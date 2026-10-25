#include "c_backend.h"

EXPORT_API const char* c_get_backend_version(void) {
    return "NetLab-Pro C-Core Engine v3.0 (MSVC Native 64-bit)";
}

EXPORT_API uint32_t c_ip_to_int(const char *ip_str) {
    ipv4_t ip = 0;
    if (parse_ipv4(ip_str, &ip)) {
        return (uint32_t)ip;
    }
    return 0;
}

EXPORT_API void c_int_to_ip(uint32_t ip, char *buf) {
    if (!buf) return;
    ipv4_to_str((ipv4_t)ip, buf, 32);
}

EXPORT_API int c_calculate_ip_info_fast(const char *ip_cidr, char *out_json, int max_len) {
    if (!ip_cidr || !out_json || max_len < 128) return 0;

    ipv4_t ip;
    int cidr = 24;
    if (!parse_cidr_string(ip_cidr, &ip, &cidr)) {
        snprintf(out_json, max_len, "{\"success\":false,\"error\":\"Invalid IP/CIDR input\"}");
        return 0;
    }

    ip_info_t info;
    calculate_ip_info(ip, cidr, &info);

    char bin_ip[64], bin_mask[64], bin_net[64], bin_bcast[64];
    ip_to_binary_str(info.ip, bin_ip, sizeof(bin_ip));
    ip_to_binary_str(info.mask, bin_mask, sizeof(bin_mask));
    ip_to_binary_str(info.network, bin_net, sizeof(bin_net));
    ip_to_binary_str(info.broadcast, bin_bcast, sizeof(bin_bcast));

    snprintf(out_json, max_len,
        "{\"success\":true,\"engine\":\"C-Core\","
        "\"ip_address_str\":\"%s\",\"cidr\":%d,\"subnet_mask_str\":\"%s\","
        "\"network_ip_str\":\"%s\",\"broadcast_ip_str\":\"%s\","
        "\"first_usable_str\":\"%s\",\"last_usable_str\":\"%s\","
        "\"wildcard_mask_str\":\"%s\",\"total_hosts\":%llu,\"usable_hosts\":%llu,"
        "\"ip_class\":\"%s\",\"scope\":\"%s\","
        "\"binary_ip\":\"%s\",\"binary_mask\":\"%s\",\"binary_network\":\"%s\",\"binary_broadcast\":\"%s\"}",
        info.ip_str, info.cidr, info.mask_str, info.network_str, info.broadcast_str,
        info.first_usable_str, info.last_usable_str, info.wildcard_str,
        (unsigned long long)info.total_ips, (unsigned long long)info.usable_hosts,
        class_to_string(info.ip_class), scope_to_string(info.scope),
        bin_ip, bin_mask, bin_net, bin_bcast);

    return 1;
}

EXPORT_API int c_calculate_supernet_fast(const char *subnets_newline_delimited, char *out_json, int max_len) {
    if (!subnets_newline_delimited || !out_json || max_len < 256) return 0;

    char copy[4096];
    strncpy(copy, subnets_newline_delimited, sizeof(copy) - 1);
    copy[sizeof(copy) - 1] = '\0';

    const char *sub_ptrs[64];
    int count = 0;

    char *token = strtok(copy, "\r\n,");
    while (token && count < 64) {
        while (isspace((unsigned char)*token)) token++;
        if (strlen(token) > 0) {
            sub_ptrs[count++] = token;
        }
        token = strtok(NULL, "\r\n,");
    }

    if (count == 0) {
        snprintf(out_json, max_len, "{\"success\":false,\"error\":\"No valid subnets provided\"}");
        return 0;
    }

    supernet_calc_result_t res;
    if (!calculate_supernet_c(sub_ptrs, count, &res)) {
        snprintf(out_json, max_len, "{\"success\":false,\"error\":\"Supernet calculation failed\"}");
        return 0;
    }

    snprintf(out_json, max_len,
        "{\"success\":true,\"engine\":\"C-Core\","
        "\"supernet_str\":\"%s\",\"supernet_mask_str\":\"%s\",\"supernet_broadcast_str\":\"%s\","
        "\"supernet_first_usable\":\"%s\",\"supernet_last_usable\":\"%s\","
        "\"supernet_cidr\":%d,\"total_supernet_ips\":%llu,\"usable_supernet_hosts\":%llu,"
        "\"total_input_ips\":%llu,\"input_count\":%d,\"reduction_pct\":%.1f,"
        "\"is_contiguous\":%s,\"is_power_of_2\":%s,\"is_aligned\":%s,\"is_valid_supernet\":%s,"
        "\"verdict\":\"%s\",\"verdict_badge\":\"%s\",\"verdict_desc\":\"%s\","
        "\"cisco_static\":\"%s\"}",
        res.supernet_str, res.supernet_mask_str, res.supernet_broadcast_str,
        res.supernet_first_usable, res.supernet_last_usable,
        res.supernet_cidr, (unsigned long long)res.total_supernet_ips, (unsigned long long)res.usable_supernet_hosts,
        (unsigned long long)res.total_input_ips, res.input_count, res.reduction_pct,
        res.is_contiguous ? "true" : "false",
        res.is_power_of_2 ? "true" : "false",
        res.is_aligned ? "true" : "false",
        res.is_valid_supernet ? "true" : "false",
        res.verdict, res.verdict_badge, res.verdict_desc,
        res.cisco_static);

    return 1;
}

EXPORT_API int c_calculate_vlsm_fast(const char *base_ip, int base_cidr, const char *labs_csv, char *out_json, int max_len) {
    if (!base_ip || !out_json || max_len < 256) return 0;

    ipv4_t base_ip_val;
    if (!parse_ipv4(base_ip, &base_ip_val)) {
        snprintf(out_json, max_len, "{\"success\":false,\"error\":\"Invalid base IP\"}");
        return 0;
    }

    campus_vlsm_t campus;
    campus_vlsm_init(&campus, base_ip_val, base_cidr);

    if (labs_csv && strlen(labs_csv) > 0) {
        char copy[8192];
        strncpy(copy, labs_csv, sizeof(copy) - 1);
        copy[sizeof(copy) - 1] = '\0';

        char *line = strtok(copy, "\n|");
        while (line) {
            char name[64] = "Lab", dept[64] = "Campus";
            int ws = 30, growth = 10, vlan = 10;
            char *p1 = strchr(line, ';');
            if (p1) {
                *p1 = '\0';
                strncpy(name, line, sizeof(name) - 1);
                char *p2 = strchr(p1 + 1, ';');
                if (p2) {
                    *p2 = '\0';
                    strncpy(dept, p1 + 1, sizeof(dept) - 1);
                    char *p3 = strchr(p2 + 1, ';');
                    if (p3) {
                        *p3 = '\0';
                        ws = atoi(p2 + 1);
                        char *p4 = strchr(p3 + 1, ';');
                        if (p4) {
                            *p4 = '\0';
                            growth = atoi(p3 + 1);
                            vlan = atoi(p4 + 1);
                        } else {
                            growth = atoi(p3 + 1);
                        }
                    } else {
                        ws = atoi(p2 + 1);
                    }
                }
            }
            campus_vlsm_add_lab(&campus, name, dept, ws, growth, vlan);
            line = strtok(NULL, "\n|");
        }
    }

    bool calc_ok = campus_vlsm_calculate(&campus);

    char next_free_s[32];
    ipv4_to_str(campus.next_free_subnet, next_free_s, sizeof(next_free_s));

    int pos = snprintf(out_json, max_len,
        "{\"success\":true,\"engine\":\"C-Core\","
        "\"base_ip\":\"%s\",\"base_cidr\":%d,\"is_valid\":%s,\"is_calculated\":%s,"
        "\"total_requested_hosts\":%llu,\"total_allocated_blocks\":%llu,\"total_usable_hosts\":%llu,"
        "\"overall_efficiency\":%.1f,\"next_free_subnet\":\"%s\",\"free_ips_remaining\":%llu,\"labs\":[",
        base_ip, base_cidr, calc_ok ? "true" : "false", campus.is_calculated ? "true" : "false",
        (unsigned long long)campus.total_requested_hosts,
        (unsigned long long)campus.total_allocated_blocks,
        (unsigned long long)campus.total_usable_hosts,
        campus.overall_efficiency, next_free_s,
        (unsigned long long)campus.free_ips_remaining);

    for (int i = 0; i < campus.lab_count; i++) {
        lab_spec_t *l = &campus.labs[i];
        char net_s[32], mask_s[32], gw_s[32], first_s[32], last_s[32];
        ipv4_to_str(l->network_ip, net_s, sizeof(net_s));
        ipv4_to_str(l->subnet_mask, mask_s, sizeof(mask_s));
        ipv4_to_str(l->gateway_ip, gw_s, sizeof(gw_s));
        ipv4_to_str(l->first_usable, first_s, sizeof(first_s));
        ipv4_to_str(l->last_usable, last_s, sizeof(last_s));

        int written = snprintf(out_json + pos, max_len - pos,
            "%s{\"id\":%d,\"name\":\"%s\",\"department\":\"%s\",\"workstations\":%d,\"vlan_id\":%d,"
            "\"allocated_cidr\":%d,\"subnet_str\":\"%s/%d\",\"subnet_mask_str\":\"%s\","
            "\"network_ip_str\":\"%s\",\"gateway_ip_str\":\"%s\",\"first_usable_str\":\"%s\",\"last_usable_str\":\"%s\","
            "\"usable_capacity\":%u,\"efficiency_pct\":%.1f,\"is_allocated\":%s}",
            (i > 0 ? "," : ""),
            l->id, l->name, l->department, l->workstations, l->vlan_id,
            l->allocated_cidr, net_s, l->allocated_cidr, mask_s,
            net_s, gw_s, first_s, last_s,
            l->usable_capacity, l->efficiency_pct, l->is_allocated ? "true" : "false");
        pos += written;
        if (pos >= max_len - 32) break;
    }

    snprintf(out_json + pos, max_len - pos, "]}");
    campus_vlsm_free(&campus);
    return 1;
}

EXPORT_API int c_analyze_reachability_fast(const char *ip_a_str, int cidr_a, const char *ip_b_str, int cidr_b, char *out_json, int max_len) {
    if (!ip_a_str || !ip_b_str || !out_json || max_len < 128) return 0;

    ipv4_t ip_a, ip_b;
    if (!parse_ipv4(ip_a_str, &ip_a) || !parse_ipv4(ip_b_str, &ip_b)) {
        snprintf(out_json, max_len, "{\"success\":false,\"error\":\"Invalid IP addresses\"}");
        return 0;
    }

    reachability_result_t res;
    analyze_reachability(ip_a, cidr_a, ip_b, cidr_b, &res);

    const char *badge = "Path Analyzed";
    const char *badge_color = "blue";
    if (res.status == REACH_SAME_SUBNET_L2) {
        badge = "Direct Layer-2 Switched Path";
        badge_color = "green";
    } else if (res.status == REACH_DIFFERENT_SUBNET_L3) {
        badge = "Layer-3 Routed Path (Gateway)";
        badge_color = "blue";
    } else if (res.status == REACH_ASYMMETRIC_MASK_ERROR) {
        badge = "Asymmetric Mask Misconfiguration";
        badge_color = "red";
    } else {
        badge = "Invalid Host IP Assigned";
        badge_color = "yellow";
    }

    snprintf(out_json, max_len,
        "{\"success\":true,\"engine\":\"C-Core\","
        "\"status\":%d,\"badge\":\"%s\",\"badge_color\":\"%s\","
        "\"diagnosis\":\"%s\",\"recommendation\":\"%s\"}",
        (int)res.status, badge, badge_color,
        res.diagnosis, res.recommendation);

    return 1;
}
