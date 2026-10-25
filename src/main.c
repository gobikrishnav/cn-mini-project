#include "common.h"
#include "ip_calc.h"
#include "vlsm_engine.h"
#include "flsm_engine.h"
#include "host_inventory.h"
#include "reachability.h"
#include "cisco_export.h"
#include "quiz_engine.h"
#include "ui_framework.h"

static campus_vlsm_t g_campus;
static bool g_campus_active = false;
static quiz_session_t g_quiz_session;

static void handle_vlsm_export_menu(campus_vlsm_t *campus) {
    while (1) {
        printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== EXPORT & INVENTORY MENU ===" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_GREEN "[1]" ANSI_RESET " Inspect PC-by-PC Workstation IP Inventory for a Lab\n");
        printf("    " ANSI_BOLD ANSI_FG_GREEN "[2]" ANSI_RESET " Export Cisco IOS Router & Switch Config Script (reports/campus_cisco.cfg)\n");
        printf("    " ANSI_BOLD ANSI_FG_GREEN "[3]" ANSI_RESET " Export CSV Spreadsheet for Excel (reports/campus_subnets.csv)\n");
        printf("    " ANSI_BOLD ANSI_FG_GREEN "[4]" ANSI_RESET " Export Detailed Documentation Report (reports/campus_report.txt)\n");
        printf("    " ANSI_BOLD ANSI_FG_YELLOW "[0]" ANSI_RESET " Return to Main Dashboard\n\n");

        int choice = ui_read_int("Select Export/Action Option", 0, 4, 0);
        if (choice == 0) break;

        if (choice == 1) {
            printf("\n  Select a Lab by ID (1 to %d): ", campus->lab_count);
            int lab_id = ui_read_int("Lab ID", 1, campus->lab_count, 1);
            const lab_spec_t *selected_lab = &campus->labs[lab_id - 1];

            lab_inventory_t inv;
            if (generate_lab_inventory(selected_lab, &inv)) {
                int page = 1;
                int per_page = 20;
                int total_pages = (inv.total_hosts + per_page - 1) / per_page;

                while (1) {
                    display_lab_inventory_page(&inv, page, per_page);

                    /* DHCP Scope Card */
                    char gw[16], start_ip[16], end_ip[16], mask[16];
                    ipv4_to_str(inv.dhcp.default_gateway, gw, sizeof(gw));
                    ipv4_to_str(inv.dhcp.dhcp_range_start, start_ip, sizeof(start_ip));
                    ipv4_to_str(inv.dhcp.dhcp_range_end, end_ip, sizeof(end_ip));
                    ipv4_to_str(inv.dhcp.subnet_mask, mask, sizeof(mask));

                    printf("\n  " ANSI_BOLD ANSI_FG_YELLOW "DHCP POOL SCOPE:" ANSI_RESET " "
                           "Subnet: %s | Gateway: %s | Range: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s - %s" ANSI_RESET " (%u leases)\n",
                           mask, gw, start_ip, end_ip, inv.dhcp.total_dhcp_leases);

                    if (total_pages > 1) {
                        printf("\n  Page %d of %d. Enter page number (or 0 to back): ", page, total_pages);
                        int p = ui_read_int("Page", 0, total_pages, 0);
                        if (p == 0) break;
                        page = p;
                    } else {
                        ui_press_any_key();
                        break;
                    }
                }
                free_lab_inventory(&inv);
            }
        } else if (choice == 2) {
            const char *path = "reports/campus_cisco.cfg";
            if (export_cisco_ios_config(campus, path)) {
                printf("\n  " ANSI_BG_GREEN ANSI_FG_BRIGHT_WHITE " SUCCESS " ANSI_RESET
                       " Cisco IOS Configuration saved to: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s" ANSI_RESET "\n", path);
            } else {
                printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ERROR " ANSI_RESET " Failed to write file.\n");
            }
        } else if (choice == 3) {
            const char *path = "reports/campus_subnets.csv";
            if (export_csv_report(campus, path)) {
                printf("\n  " ANSI_BG_GREEN ANSI_FG_BRIGHT_WHITE " SUCCESS " ANSI_RESET
                       " CSV Spreadsheet saved to: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s" ANSI_RESET "\n", path);
            } else {
                printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ERROR " ANSI_RESET " Failed to write file.\n");
            }
        } else if (choice == 4) {
            const char *path = "reports/campus_report.txt";
            if (export_summary_text_report(campus, path)) {
                printf("\n  " ANSI_BG_GREEN ANSI_FG_BRIGHT_WHITE " SUCCESS " ANSI_RESET
                       " Summary Report saved to: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s" ANSI_RESET "\n", path);
            } else {
                printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ERROR " ANSI_RESET " Failed to write file.\n");
            }
        }
    }
}

static void handle_custom_vlsm_wizard(void) {
    ui_clear_screen();
    ui_draw_banner();
    ui_draw_header("CAMPUS VLSM LAB SUBNET WIZARD", "Any Number of Labs & Computers");

    printf("\n  " ANSI_BOLD ANSI_FG_WHITE "Step 1: Define Base Campus Network Allocation" ANSI_RESET "\n");
    printf("  " ANSI_FG_BRIGHT_BLACK "(e.g., 10.50.0.0/16 or 172.16.0.0/18 or 192.168.0.0/22)" ANSI_RESET "\n\n");

    ipv4_t base_ip;
    if (!ui_read_ipv4_prompt("Enter Base Network IP", &base_ip)) {
        return;
    }
    int base_cidr = ui_read_cidr_prompt("Enter Base CIDR Prefix", 8, 30, 16);

    campus_vlsm_init(&g_campus, base_ip, base_cidr);

    printf("\n  " ANSI_BOLD ANSI_FG_WHITE "Step 2: Enter Number of Labs in Your Campus / Department" ANSI_RESET "\n");
    int lab_count = ui_read_int("Number of Labs", 1, 100, 4);

    for (int i = 0; i < lab_count; i++) {
        printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "--- Configuring Lab #%d of %d ---" ANSI_RESET "\n", i + 1, lab_count);

        char lab_name[MAX_LAB_NAME_LEN];
        char dept_name[MAX_DEPT_NAME_LEN];
        char prompt_name[64];
        snprintf(prompt_name, sizeof(prompt_name), "Lab Name [e.g. AI Lab %d]: ", i + 1);
        if (!ui_read_line(prompt_name, lab_name, sizeof(lab_name)) || strlen(lab_name) == 0) {
            snprintf(lab_name, sizeof(lab_name), "Computer Lab %d", i + 1);
        }

        if (!ui_read_line("Department / Building [e.g. CSE Wing]: ", dept_name, sizeof(dept_name)) || strlen(dept_name) == 0) {
            strncpy(dept_name, "Main Campus", sizeof(dept_name) - 1);
        }

        int pcs = ui_read_int("Number of Workstation Computers", 1, 10000, 60);
        int growth = ui_read_int("Future Growth Buffer Percentage", 0, 100, 10);
        int vlan = 10 + (i * 10);

        campus_vlsm_add_lab(&g_campus, lab_name, dept_name, pcs, growth, vlan);
    }

    /* Run Allocation Algorithm */
    if (campus_vlsm_calculate(&g_campus)) {
        g_campus_active = true;
        ui_render_vlsm_table(&g_campus);
        handle_vlsm_export_menu(&g_campus);
    } else {
        printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ALLOCATION FAILED " ANSI_RESET " %s\n", g_campus.error_reason);
        ui_press_any_key();
    }
}

static void handle_preset_campus(void) {
    ui_clear_screen();
    ui_draw_banner();
    ui_draw_header("PRESET COLLEGE CAMPUS NETWORK", "8 Real-world Labs Pre-loaded");

    campus_vlsm_load_preset_college(&g_campus);
    g_campus_active = true;

    ui_render_vlsm_table(&g_campus);
    handle_vlsm_export_menu(&g_campus);
}

static void handle_flsm_mode(void) {
    ui_clear_screen();
    ui_draw_banner();
    ui_draw_header("FIXED-LENGTH SUBNET MASKING (FLSM)", "Equal Partition Allocator");

    ipv4_t base_ip;
    if (!ui_read_ipv4_prompt("Enter Base Network IP", &base_ip)) return;
    int base_cidr = ui_read_cidr_prompt("Enter Base CIDR Prefix", 8, 29, 24);

    printf("\n  " ANSI_BOLD "Partitioning Mode:" ANSI_RESET "\n"
           "    [1] Divide into Fixed Number of Equal Subnets (e.g. 8 Labs)\n"
           "    [2] Divide by Workstation Capacity per Subnet (e.g. 50 PCs each)\n\n");
    int mode = ui_read_int("Select Mode", 1, 2, 1);

    flsm_plan_t plan;
    bool success = false;

    if (mode == 1) {
        int subnets = ui_read_int("Number of Subnets Needed", 2, 256, 4);
        success = flsm_divide_by_subnets(base_ip, base_cidr, subnets, &plan);
    } else {
        int hosts = ui_read_int("Required Hosts per Subnet", 2, 10000, 30);
        success = flsm_divide_by_hosts(base_ip, base_cidr, hosts, &plan);
    }

    if (success) {
        ui_render_flsm_table(&plan);
        flsm_free_plan(&plan);
    } else {
        printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ERROR " ANSI_RESET " Unable to partition with given constraints.\n");
    }
    ui_press_any_key();
}

static void handle_single_calc(void) {
    ui_clear_screen();
    ui_draw_banner();
    ui_draw_header("SINGLE IP & CIDR SUBNET CALCULATOR", "Address Inspection");

    char input[64];
    printf("\n  Enter IP and CIDR prefix (e.g. 192.168.10.75/26): ");
    if (!fgets(input, sizeof(input), stdin)) return;

    ipv4_t ip;
    int cidr;
    if (parse_cidr_string(input, &ip, &cidr)) {
        ip_info_t info;
        calculate_ip_info(ip, cidr, &info);
        ui_render_single_ip_dashboard(&info);
    } else {
        printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ERROR " ANSI_RESET " Invalid format. Expected e.g. 192.168.1.50/24\n");
    }
    ui_press_any_key();
}

static void handle_binary_view(void) {
    ui_clear_screen();
    ui_draw_banner();
    ui_draw_header("BITWISE BINARY DECOMPOSITION", "32-Bit AND/OR Visualizer");

    char input[64];
    printf("\n  Enter IP and CIDR prefix (e.g. 172.16.50.100/22): ");
    if (!fgets(input, sizeof(input), stdin)) return;

    ipv4_t ip;
    int cidr;
    if (parse_cidr_string(input, &ip, &cidr)) {
        render_bitwise_breakdown(ip, cidr);
    } else {
        printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ERROR " ANSI_RESET " Invalid IP/CIDR input.\n");
    }
    ui_press_any_key();
}

static void handle_reachability(void) {
    ui_clear_screen();
    ui_draw_banner();
    ui_draw_header("INTER-HOST REACHABILITY & ROUTING ANALYZER", "L2 Switching vs L3 Routing");

    char ip_str_a[64], ip_str_b[64];
    printf("\n  " ANSI_BOLD ANSI_FG_WHITE "Enter Host A IP & CIDR (e.g. 192.168.1.15/24): " ANSI_RESET);
    if (!fgets(ip_str_a, sizeof(ip_str_a), stdin)) return;

    printf("  " ANSI_BOLD ANSI_FG_WHITE "Enter Host B IP & CIDR (e.g. 192.168.2.30/24): " ANSI_RESET);
    if (!fgets(ip_str_b, sizeof(ip_str_b), stdin)) return;

    ipv4_t ip_a, ip_b;
    int cidr_a, cidr_b;

    if (parse_cidr_string(ip_str_a, &ip_a, &cidr_a) &&
        parse_cidr_string(ip_str_b, &ip_b, &cidr_b)) {
        reachability_result_t res;
        analyze_reachability(ip_a, cidr_a, ip_b, cidr_b, &res);
        render_reachability_report(&res);
    } else {
        printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ERROR " ANSI_RESET " Invalid IP addresses provided.\n");
    }
    ui_press_any_key();
}

int main(void) {
    ui_init();
    quiz_session_init(&g_quiz_session);

    while (1) {
        ui_clear_screen();
        ui_draw_banner();

        printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== PRIMARY CAMPUS NETWORK LAB MANAGEMENT MODULES ===" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_GREEN "[1]" ANSI_RESET " " ANSI_BOLD ANSI_FG_WHITE "Campus VLSM Lab Subnet Architect" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLACK "(Custom Labs & Any PC Count)" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_GREEN "[2]" ANSI_RESET " " ANSI_BOLD ANSI_FG_WHITE "Load Preset College Campus" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLACK "(8 Realistic Pre-configured Labs)" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_GREEN "[3]" ANSI_RESET " " ANSI_BOLD ANSI_FG_WHITE "Fixed-Length Subnetting (FLSM)" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLACK "(Equal-size Lab Partitions)" ANSI_RESET "\n");

        printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== NETWORK ENGINEERING & DIAGNOSTIC UTILITIES ===" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_CYAN "[4]" ANSI_RESET " " ANSI_FG_WHITE "Single IP & CIDR Subnet Calculator" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_CYAN "[5]" ANSI_RESET " " ANSI_FG_WHITE "Deep 32-Bit Binary Visualizer & ANDing Engine" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_CYAN "[6]" ANSI_RESET " " ANSI_FG_WHITE "Inter-Host Reachability & Routing Analyzer (L2/L3)" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_CYAN "[7]" ANSI_RESET " " ANSI_FG_WHITE "IPv4 CIDR Reference Cheatsheet & RFC 1918 Scope" ANSI_RESET "\n");

        printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== EVALUATION & VIVA EXAMINATION SUITE ===" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_YELLOW "[8]" ANSI_RESET " " ANSI_BOLD ANSI_FG_YELLOW "Interactive Viva Quiz & Subnet Exam Trainer" ANSI_RESET "\n");
        printf("    " ANSI_BOLD ANSI_FG_RED "[0]" ANSI_RESET " " ANSI_FG_BRIGHT_WHITE "Exit NetLab-Pro" ANSI_RESET "\n\n");

        int choice = ui_read_int("Select Menu Option", 0, 8, 1);

        if (choice <= 0) {
            printf("\n  Exiting NetLab-Pro. Goodbye!\n\n");
            break;
        }

        switch (choice) {
            case 1: handle_custom_vlsm_wizard(); break;
            case 2: handle_preset_campus(); break;
            case 3: handle_flsm_mode(); break;
            case 4: handle_single_calc(); break;
            case 5: handle_binary_view(); break;
            case 6: handle_reachability(); break;
            case 7:
                ui_clear_screen();
                ui_draw_banner();
                ui_render_reference_sheet();
                ui_press_any_key();
                break;
            case 8:
                run_interactive_quiz(&g_quiz_session);
                break;
            default:
                break;
        }
    }

    if (g_campus_active) {
        campus_vlsm_free(&g_campus);
    }

    return 0;
}
