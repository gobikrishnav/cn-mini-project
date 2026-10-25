#include "host_inventory.h"

static void generate_prefix(const char *name, char *prefix, size_t maxlen) {
    size_t p = 0;
    bool new_word = true;

    for (size_t i = 0; name[i] != '\0' && p < maxlen - 1; i++) {
        if (isalnum((unsigned char)name[i])) {
            if (new_word) {
                prefix[p++] = (char)toupper((unsigned char)name[i]);
                new_word = false;
            }
        } else {
            new_word = true;
        }
    }
    if (p < 2 && strlen(name) >= 2) {
        prefix[0] = (char)toupper((unsigned char)name[0]);
        prefix[1] = (char)toupper((unsigned char)name[1]);
        p = 2;
    }
    prefix[p] = '\0';
}

bool generate_lab_inventory(const lab_spec_t *lab, lab_inventory_t *out_inv) {
    if (!lab || !out_inv || lab->usable_capacity == 0) return false;

    memset(out_inv, 0, sizeof(lab_inventory_t));
    strncpy(out_inv->lab_name, lab->name, sizeof(out_inv->lab_name) - 1);

    int total_slots = lab->usable_capacity;
    out_inv->records = (host_record_t *)malloc(sizeof(host_record_t) * total_slots);
    if (!out_inv->records) return false;

    out_inv->total_hosts = total_slots;

    char prefix[16];
    generate_prefix(lab->name, prefix, sizeof(prefix));

    /* Initialize DHCP Scope */
    strncpy(out_inv->dhcp.lab_name, lab->name, sizeof(out_inv->dhcp.lab_name) - 1);
    out_inv->dhcp.vlan_id = lab->vlan_id;
    out_inv->dhcp.pool_network = lab->network_ip;
    out_inv->dhcp.subnet_mask = lab->subnet_mask;
    out_inv->dhcp.default_gateway = lab->gateway_ip;
    out_inv->dhcp.dns_server = lab->dns_server_ip;
    out_inv->dhcp.dhcp_range_start = lab->first_usable + 3;
    out_inv->dhcp.dhcp_range_end = lab->last_usable;
    out_inv->dhcp.lease_days = 7;
    out_inv->dhcp.total_dhcp_leases = (lab->last_usable >= out_inv->dhcp.dhcp_range_start)
                                        ? (lab->last_usable - out_inv->dhcp.dhcp_range_start + 1)
                                        : 0;

    ipv4_t current_ip = lab->first_usable;
    int pc_num = 1;

    for (int i = 0; i < total_slots; i++) {
        host_record_t *rec = &out_inv->records[i];
        rec->index = i + 1;
        rec->ip = current_ip;
        rec->mask = lab->subnet_mask;
        rec->gateway = lab->gateway_ip;
        rec->dns = lab->dns_server_ip;

        if (i == 0) {
            snprintf(rec->hostname, sizeof(rec->hostname), "%s-GW01", prefix);
            strncpy(rec->role_name, "Default Gateway", sizeof(rec->role_name) - 1);
            rec->role = DEVICE_GATEWAY;
        } else if (i == 1) {
            snprintf(rec->hostname, sizeof(rec->hostname), "%s-SRV01", prefix);
            strncpy(rec->role_name, "Lab Server / DNS", sizeof(rec->role_name) - 1);
            rec->role = DEVICE_LOCAL_SERVER;
        } else if (i == 2) {
            snprintf(rec->hostname, sizeof(rec->hostname), "%s-PRN01", prefix);
            strncpy(rec->role_name, "Network Printer", sizeof(rec->role_name) - 1);
            rec->role = DEVICE_NETWORK_PRINTER;
        } else if (pc_num <= lab->workstations) {
            snprintf(rec->hostname, sizeof(rec->hostname), "%s-PC-%02d", prefix, pc_num);
            strncpy(rec->role_name, "Student Station", sizeof(rec->role_name) - 1);
            rec->role = DEVICE_STUDENT_PC;
            pc_num++;
        } else {
            snprintf(rec->hostname, sizeof(rec->hostname), "%s-RESV-%02d", prefix, i - lab->workstations - 2);
            strncpy(rec->role_name, "Future Expansion", sizeof(rec->role_name) - 1);
            rec->role = DEVICE_SPARE;
        }

        current_ip++;
    }

    return true;
}

void free_lab_inventory(lab_inventory_t *inv) {
    if (!inv) return;
    if (inv->records) {
        free(inv->records);
        inv->records = NULL;
    }
    inv->total_hosts = 0;
}

void display_lab_inventory_page(const lab_inventory_t *inv, int page, int per_page) {
    if (!inv || !inv->records || inv->total_hosts == 0) {
        printf("  No host inventory records found.\n");
        return;
    }

    int total_pages = (inv->total_hosts + per_page - 1) / per_page;
    if (page < 1) page = 1;
    if (page > total_pages) page = total_pages;

    int start_idx = (page - 1) * per_page;
    int end_idx = start_idx + per_page;
    if (end_idx > inv->total_hosts) end_idx = inv->total_hosts;

    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== HOST IP ALLOCATION TABLE: %s (Page %d of %d) ===" ANSI_RESET "\n",
           inv->lab_name, page, total_pages);
    printf("  " ANSI_FG_WHITE "Total Workstations: %d | Page Showing Devices #%d to #%d" ANSI_RESET "\n\n",
           inv->total_hosts, start_idx + 1, end_idx);

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_TL);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_TR ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_WHITE "%-4s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_CYAN "%-16s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_GREEN "%-16s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_YELLOW "%-16s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
           ANSI_BOLD ANSI_FG_MAGENTA "%-14s" ANSI_RESET " "
           ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
           "No.", "Hostname", "Assigned IP", "Default Gateway", "Device Role");

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_T_RIGHT);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_T_LEFT ANSI_RESET "\n");

    for (int i = start_idx; i < end_idx; i++) {
        const host_record_t *r = &inv->records[i];
        char ip_str[16], gw_str[16];
        ipv4_to_str(r->ip, ip_str, sizeof(ip_str));
        ipv4_to_str(r->gateway, gw_str, sizeof(gw_str));

        const char *color = ANSI_FG_WHITE;
        if (r->role == DEVICE_GATEWAY) color = ANSI_FG_BRIGHT_RED;
        else if (r->role == DEVICE_LOCAL_SERVER) color = ANSI_FG_BRIGHT_MAGENTA;
        else if (r->role == DEVICE_NETWORK_PRINTER) color = ANSI_FG_BRIGHT_YELLOW;
        else if (r->role == DEVICE_STUDENT_PC) color = ANSI_FG_BRIGHT_GREEN;
        else if (r->role == DEVICE_SPARE) color = ANSI_FG_BRIGHT_BLACK;

        printf("  " ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_WHITE "%-4d" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               "%s%-16s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_BRIGHT_CYAN "%-16s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               ANSI_FG_WHITE "%-16s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET " "
               "%s%-14s" ANSI_RESET " "
               ANSI_FG_BRIGHT_BLUE BOX_V ANSI_RESET "\n",
               r->index, color, r->hostname, ip_str, gw_str, color, r->role_name);
    }

    printf("  " ANSI_FG_BRIGHT_BLUE BOX_BL);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_BR ANSI_RESET "\n");
}
