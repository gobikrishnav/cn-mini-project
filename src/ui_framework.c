#include "ui_framework.h"

void ui_init(void) {
#ifdef _WIN32
    /* Set console code page to UTF-8 for box drawing */
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);

    /* Enable Virtual Terminal Processing for ANSI colors */
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    if (hOut != INVALID_HANDLE_VALUE) {
        DWORD dwMode = 0;
        if (GetConsoleMode(hOut, &dwMode)) {
            dwMode |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
            SetConsoleMode(hOut, dwMode);
        }
    }
#endif
}

void ui_clear_screen(void) {
    printf("\033[2J\033[H");
}

void ui_draw_banner(void) {
    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN DBOX_TL);
    for (int i = 0; i < 76; i++) printf(DBOX_H);
    printf(DBOX_TR ANSI_RESET "\n");

    printf("  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN DBOX_V ANSI_RESET
           "  " ANSI_BOLD ANSI_FG_BRIGHT_WHITE "NetLab-Pro" ANSI_RESET " "
           ANSI_FG_WHITE ":: Campus Network Subnet Architect & VLSM Lab Suite" ANSI_RESET
           "  " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "[v2.5 PRO]" ANSI_RESET "  "
           ANSI_BOLD ANSI_FG_BRIGHT_CYAN DBOX_V ANSI_RESET "\n");

    printf("  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN DBOX_BL);
    for (int i = 0; i < 76; i++) printf(DBOX_H);
    printf(DBOX_BR ANSI_RESET "\n");
}

void ui_draw_header(const char *title, const char *subtitle) {
    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_BLUE "┌─" ANSI_RESET " "
           ANSI_BOLD ANSI_FG_BRIGHT_WHITE "%s" ANSI_RESET, title);
    if (subtitle) {
        printf(" " ANSI_FG_BRIGHT_BLACK "(%s)" ANSI_RESET, subtitle);
    }
    printf("\n");
}

void ui_draw_divider(int width) {
    printf("  " ANSI_FG_BRIGHT_BLACK);
    for (int i = 0; i < width; i++) printf("─");
    printf(ANSI_RESET "\n");
}

void ui_press_any_key(void) {
    printf("\n  " ANSI_FG_BRIGHT_BLACK "Press ENTER to return to menu..." ANSI_RESET);
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

bool ui_read_line(const char *prompt, char *buf, size_t maxlen) {
    if (!buf || maxlen == 0) return false;
    printf("  " ANSI_FG_WHITE "%s" ANSI_RESET, prompt);

    if (!fgets(buf, (int)maxlen, stdin)) return false;

    /* Remove trailing newline */
    size_t len = strlen(buf);
    if (len > 0 && buf[len - 1] == '\n') {
        buf[len - 1] = '\0';
    }
    return true;
}

int ui_read_int(const char *prompt, int min_val, int max_val, int default_val) {
    char buf[64];
    while (1) {
        printf("  " ANSI_FG_WHITE "%s [%d-%d, default %d]: " ANSI_RESET, prompt, min_val, max_val, default_val);
        if (!fgets(buf, sizeof(buf), stdin)) {
            if (feof(stdin)) return -1;
            return default_val;
        }

        /* Strip whitespace */
        char *p = buf;
        while (isspace((unsigned char)*p)) p++;
        if (*p == '\0') return default_val;

        char *endptr;
        long val = strtol(p, &endptr, 10);
        while (isspace((unsigned char)*endptr)) endptr++;
        if (*endptr == '\0' && val >= min_val && val <= max_val) {
            return (int)val;
        }
        printf("  " ANSI_FG_BRIGHT_RED "Invalid input! Please enter a number between %d and %d." ANSI_RESET "\n", min_val, max_val);
    }
}

bool ui_read_ipv4_prompt(const char *prompt, ipv4_t *out_ip) {
    char buf[64];
    while (1) {
        printf("  " ANSI_FG_WHITE "%s: " ANSI_RESET, prompt);
        if (!fgets(buf, sizeof(buf), stdin)) return false;

        /* Strip newline */
        size_t len = strlen(buf);
        if (len > 0 && buf[len - 1] == '\n') buf[len - 1] = '\0';

        char *p = buf;
        while (isspace((unsigned char)*p)) p++;
        if (strlen(p) == 0) return false;

        if (parse_ipv4(p, out_ip)) {
            return true;
        }
        printf("  " ANSI_FG_BRIGHT_RED "Invalid IPv4 format! Expected e.g. 192.168.1.0 or 10.0.0.0" ANSI_RESET "\n");
    }
}

int ui_read_cidr_prompt(const char *prompt, int min_cidr, int max_cidr, int default_cidr) {
    return ui_read_int(prompt, min_cidr, max_cidr, default_cidr);
}

void ui_render_single_ip_dashboard(const ip_info_t *info) {
    if (!info) return;

    printf("\n  " ANSI_FG_BRIGHT_BLUE BOX_TL);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_TR ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_BRIGHT_CYAN "NETWORK IDENTITY SPECIFICATION" ANSI_RESET
           "%*s" ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n", 45, "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_T_RIGHT);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_T_LEFT ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_BRIGHT_WHITE "%s/%d" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Input IP / Prefix", info->ip_str, info->cidr,
           (int)(51 - strlen(info->ip_str) - (info->cidr >= 10 ? 3 : 2)), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Subnet Mask", info->mask_str, (int)(52 - strlen(info->mask_str)), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_FG_WHITE "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Wildcard Mask", info->wildcard_str, (int)(52 - strlen(info->wildcard_str)), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Network Address", info->network_str, (int)(52 - strlen(info->network_str)), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "%s" ANSI_RESET " " SYM_ARROW " "
           ANSI_BOLD ANSI_FG_BRIGHT_CYAN "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Usable Host Range", info->first_usable_str, info->last_usable_str,
           (int)(49 - strlen(info->first_usable_str) - strlen(info->last_usable_str)), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_BRIGHT_MAGENTA "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Broadcast Address", info->broadcast_str, (int)(52 - strlen(info->broadcast_str)), "");

    char hosts_buf[64];
    snprintf(hosts_buf, sizeof(hosts_buf), "%llu addresses (%llu usable)",
             (unsigned long long)info->total_ips, (unsigned long long)info->usable_hosts);

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_WHITE "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Capacity", hosts_buf, (int)(52 - strlen(hosts_buf)), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_BRIGHT_BLUE "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "Classification", class_to_string(info->ip_class),
           (int)(52 - strlen(class_to_string(info->ip_class))), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "  "
           "%-20s: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s" ANSI_RESET "%*s"
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "RFC Scope", scope_to_string(info->scope),
           (int)(52 - strlen(scope_to_string(info->scope))), "");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_BL);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_BR ANSI_RESET "\n");
}

void ui_render_vlsm_table(const campus_vlsm_t *campus) {
    if (!campus) return;

    if (!campus->is_valid) {
        printf("\n  " ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " ALLOCATION FAILED " ANSI_RESET " %s\n\n",
               campus->error_reason);
        return;
    }

    char base_net[16], next_free[16];
    ipv4_to_str(campus->base_network_ip, base_net, sizeof(base_net));
    ipv4_to_str(campus->next_free_subnet, next_free, sizeof(next_free));

    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_WHITE "CAMPUS VLSM SUBNET MATRIX" ANSI_RESET
           "  Base: " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "%s/%d" ANSI_RESET
           "  Total Scope: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%llu IPs" ANSI_RESET
           "  Efficiency: " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "%.1f%%" ANSI_RESET "\n\n",
           base_net, campus->base_cidr, (unsigned long long)campus->total_campus_capacity,
           campus->overall_efficiency);

    /* Render Box Header */
    printf("  " ANSI_FG_BRIGHT_BLUE BOX_TL);
    for (int i = 0; i < 118; i++) printf(BOX_H);
    printf(BOX_TR ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_WHITE "%-3s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_CYAN "%-26s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_YELLOW "%-6s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_WHITE "%-18s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_GREEN "%-27s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_MAGENTA "%-15s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_WHITE "%-7s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "ID", "Lab / Department Name", "VLAN", "Subnet Address", "Usable Host Range", "Default Gateway", "Hosts");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_T_RIGHT);
    for (int i = 0; i < 118; i++) printf(BOX_H);
    printf(BOX_T_LEFT ANSI_RESET "\n");

    for (int i = 0; i < campus->lab_count; i++) {
        const lab_spec_t *lab = &campus->labs[i];
        char net_cidr[24], range_str[36], gw_str[16];
        char net[16], first[16], last[16];
        ipv4_to_str(lab->network_ip, net, sizeof(net));
        ipv4_to_str(lab->first_usable, first, sizeof(first));
        ipv4_to_str(lab->last_usable, last, sizeof(last));
        ipv4_to_str(lab->gateway_ip, gw_str, sizeof(gw_str));

        snprintf(net_cidr, sizeof(net_cidr), "%s/%d", net, lab->allocated_cidr);
        snprintf(range_str, sizeof(range_str), "%s " SYM_ARROW " %s", first, last);

        printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_WHITE "%-3d" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_BOLD ANSI_FG_BRIGHT_WHITE "%-26.26s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_YELLOW "VLAN%-2d" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_BRIGHT_CYAN "%-18s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_BRIGHT_GREEN "%-27.27s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_BRIGHT_MAGENTA "%-15s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_BOLD ANSI_FG_WHITE "%-3d" ANSI_RESET ANSI_FG_BRIGHT_BLACK "/%-3u" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
               lab->id, lab->name, lab->vlan_id, net_cidr, range_str, gw_str,
               lab->workstations, lab->usable_capacity);
    }

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_BL);
    for (int i = 0; i < 118; i++) printf(BOX_H);
    printf(BOX_BR ANSI_RESET "\n");

    printf("\n  " ANSI_BOLD "Campus Capacity Summary:" ANSI_RESET "\n"
           "    - Total PCs Requested     : " ANSI_BOLD ANSI_FG_BRIGHT_WHITE "%llu" ANSI_RESET "\n"
           "    - Total Block Space Used  : " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "%llu" ANSI_RESET " addresses\n"
           "    - Next Available Unused IP: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s" ANSI_RESET "\n"
           "    - Free Addresses Left     : " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "%llu" ANSI_RESET " addresses\n",
           (unsigned long long)campus->total_requested_hosts,
           (unsigned long long)campus->total_allocated_blocks,
           next_free, (unsigned long long)campus->free_ips_remaining);
}

void ui_render_flsm_table(const flsm_plan_t *plan) {
    if (!plan || !plan->subnets || plan->displayed_count == 0) return;

    char base[16];
    ipv4_to_str(plan->base_ip, base, sizeof(base));

    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_WHITE "FLSM EQUAL PARTITION BREAKDOWN" ANSI_RESET
           "  Base: " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "%s/%d" ANSI_RESET
           "  Subnets: " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%u" ANSI_RESET
           "  Hosts/Subnet: " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "%u" ANSI_RESET "\n\n",
           base, plan->base_cidr, plan->total_subnets_generated, plan->usable_hosts_per_subnet);

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_TL);
    for (int i = 0; i < 94; i++) printf(BOX_H);
    printf(BOX_TR ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_WHITE "%-4s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_CYAN "%-18s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_YELLOW "%-16s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_GREEN "%-31s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_MAGENTA "%-15s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "No.", "Subnet Address", "Subnet Mask", "Usable Host Range", "Broadcast ID");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_T_RIGHT);
    for (int i = 0; i < 94; i++) printf(BOX_H);
    printf(BOX_T_LEFT ANSI_RESET "\n");

    for (int i = 0; i < plan->displayed_count; i++) {
        const flsm_subnet_t *s = &plan->subnets[i];
        char net_cidr[24], mask[16], range_str[36], bcast[16];
        char net[16], first[16], last[16];
        ipv4_to_str(s->network_ip, net, sizeof(net));
        ipv4_to_str(s->subnet_mask, mask, sizeof(mask));
        ipv4_to_str(s->first_usable, first, sizeof(first));
        ipv4_to_str(s->last_usable, last, sizeof(last));
        ipv4_to_str(s->broadcast_ip, bcast, sizeof(bcast));

        snprintf(net_cidr, sizeof(net_cidr), "%s/%d", net, s->cidr);
        snprintf(range_str, sizeof(range_str), "%s " SYM_ARROW " %s", first, last);

        printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_WHITE "%-4d" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_BRIGHT_CYAN "%-18s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_YELLOW "%-16s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_BRIGHT_GREEN "%-31.31s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_BRIGHT_MAGENTA "%-15s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
               s->subnet_index, net_cidr, mask, range_str, bcast);
    }

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_BL);
    for (int i = 0; i < 94; i++) printf(BOX_H);
    printf(BOX_BR ANSI_RESET "\n");
}

void ui_render_reference_sheet(void) {
    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== IPv4 CIDR SUBNET MASK QUICK REFERENCE CHEATSHEET ===" ANSI_RESET "\n\n");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_TL);
    for (int i = 0; i < 84; i++) printf(BOX_H);
    printf(BOX_TR ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_WHITE "%-6s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_CYAN "%-17s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_YELLOW "%-17s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_GREEN "%-16s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_MAGENTA "%-18s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "CIDR", "Subnet Mask", "Wildcard Mask", "Total IPs", "Usable Workstations");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_T_RIGHT);
    for (int i = 0; i < 84; i++) printf(BOX_H);
    printf(BOX_T_LEFT ANSI_RESET "\n");

    for (int cidr = 16; cidr <= 30; cidr++) {
        ipv4_t mask = cidr_to_mask(cidr);
        ipv4_t wildcard = calculate_wildcard(mask);
        char mask_str[16], wild_str[16];
        ipv4_to_str(mask, mask_str, sizeof(mask_str));
        ipv4_to_str(wildcard, wild_str, sizeof(wild_str));

        uint64_t total = 1ULL << (32 - cidr);
        uint64_t usable = total - 2;

        printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_BOLD ANSI_FG_BRIGHT_WHITE "/%-5d" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_CYAN "%-17s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_YELLOW "%-17s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_WHITE "%-16llu" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%-18llu" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
               cidr, mask_str, wild_str, (unsigned long long)total, (unsigned long long)usable);
    }

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_BL);
    for (int i = 0; i < 84; i++) printf(BOX_H);
    printf(BOX_BR ANSI_RESET "\n");

    printf("\n  " ANSI_BOLD ANSI_FG_WHITE "RFC 1918 Private Address Ranges:" ANSI_RESET "\n"
           "    * " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "10.0.0.0/8" ANSI_RESET "       (10.0.0.0 - 10.255.255.255)       -> 16,777,216 addresses (Class A)\n"
           "    * " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "172.16.0.0/12" ANSI_RESET "    (172.16.0.0 - 172.31.255.255)     -> 1,048,576 addresses (Class B)\n"
           "    * " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "192.168.0.0/16" ANSI_RESET "   (192.168.0.0 - 192.168.255.255)   -> 65,536 addresses (Class C)\n");
}
