#include "supernet_engine.h"

static int compare_subnets_asc(const void *a, const void *b) {
    const supernet_member_t *sa = (const supernet_member_t *)a;
    const supernet_member_t *sb = (const supernet_member_t *)b;
    if (sa->network_ip < sb->network_ip) return -1;
    if (sa->network_ip > sb->network_ip) return 1;
    return sa->cidr - sb->cidr;
}

static int get_bit_length(uint32_t val) {
    int bits = 0;
    while (val > 0) {
        bits++;
        val >>= 1;
    }
    return bits;
}

bool calculate_supernet_c(const char **subnets, int count, supernet_calc_result_t *out_res) {
    if (!subnets || count <= 0 || !out_res) return false;
    memset(out_res, 0, sizeof(supernet_calc_result_t));

    supernet_member_t *members = (supernet_member_t *)malloc(sizeof(supernet_member_t) * count);
    if (!members) return false;

    int valid_count = 0;
    for (int i = 0; i < count; i++) {
        if (!subnets[i] || strlen(subnets[i]) == 0) continue;
        ipv4_t ip;
        int cidr = 24;
        if (!parse_cidr_string(subnets[i], &ip, &cidr)) continue;

        ipv4_t mask = cidr_to_mask(cidr);
        ipv4_t net = ip & mask;
        ipv4_t bcast = net | calculate_wildcard(mask);
        uint32_t bsz = (cidr >= 32) ? 1 : (1U << (32 - cidr));

        members[valid_count].network_ip = net;
        members[valid_count].cidr = cidr;
        members[valid_count].mask_ip = mask;
        members[valid_count].broadcast_ip = bcast;
        members[valid_count].block_size = bsz;

        ipv4_to_str(net, members[valid_count].network_str, sizeof(members[valid_count].network_str));
        ipv4_to_str(mask, members[valid_count].mask_str, sizeof(members[valid_count].mask_str));
        ipv4_to_str(bcast, members[valid_count].broadcast_str, sizeof(members[valid_count].broadcast_str));
        ipv4_to_str(net + 1, members[valid_count].first_usable, sizeof(members[valid_count].first_usable));
        ipv4_to_str(bcast - 1, members[valid_count].last_usable, sizeof(members[valid_count].last_usable));

        valid_count++;
    }

    if (valid_count == 0) {
        free(members);
        return false;
    }

    /* Sort subnets ascending by network IP */
    qsort(members, valid_count, sizeof(supernet_member_t), compare_subnets_asc);

    out_res->input_count = valid_count;
    uint64_t total_input_ips = 0;
    for (int i = 0; i < valid_count; i++) {
        total_input_ips += members[i].block_size;
    }
    out_res->total_input_ips = total_input_ips;

    ipv4_t min_net = members[0].network_ip;
    ipv4_t max_bcast = members[0].broadcast_ip;
    for (int i = 1; i < valid_count; i++) {
        if (members[i].broadcast_ip > max_bcast) {
            max_bcast = members[i].broadcast_ip;
        }
    }

    /* Check strict contiguity in C */
    bool is_contiguous = true;
    for (int i = 1; i < valid_count; i++) {
        if (members[i].network_ip != members[i - 1].broadcast_ip + 1) {
            is_contiguous = false;
            break;
        }
    }
    out_res->is_contiguous = is_contiguous;

    /* Longest Common Prefix (LCP) calculation in C */
    uint32_t diff = min_net ^ max_bcast;
    int sup_cidr = 32;
    if (diff == 0) {
        sup_cidr = members[0].cidr;
    } else {
        int diff_bits = get_bit_length(diff);
        sup_cidr = 32 - diff_bits;
    }
    out_res->supernet_cidr = sup_cidr;

    ipv4_t sup_mask = cidr_to_mask(sup_cidr);
    ipv4_t sup_net = min_net & sup_mask;
    ipv4_t sup_bcast = sup_net | calculate_wildcard(sup_mask);
    uint64_t sup_total_ips = (sup_cidr >= 32) ? 1 : (1ULL << (32 - sup_cidr));
    uint64_t sup_usable = (sup_cidr < 31 && sup_total_ips >= 2) ? (sup_total_ips - 2) : sup_total_ips;

    out_res->supernet_net = sup_net;
    out_res->supernet_mask = sup_mask;
    out_res->supernet_broadcast = sup_bcast;
    out_res->total_supernet_ips = sup_total_ips;
    out_res->usable_supernet_hosts = sup_usable;

    /* Power-of-2 and alignment checks */
    out_res->is_power_of_2 = (valid_count > 0) && ((valid_count & (valid_count - 1)) == 0);
    out_res->is_aligned = (min_net % sup_total_ips) == 0;
    out_res->is_valid_supernet = is_contiguous;

    if (valid_count > 1) {
        out_res->reduction_pct = (((double)(valid_count - 1)) / (double)valid_count) * 100.0;
    } else {
        out_res->reduction_pct = 0.0;
    }

    /* Formatted strings */
    char net_s[32], mask_s[32], bcast_s[32], first_s[32], last_s[32];
    ipv4_to_str(sup_net, net_s, sizeof(net_s));
    ipv4_to_str(sup_mask, mask_s, sizeof(mask_s));
    ipv4_to_str(sup_bcast, bcast_s, sizeof(bcast_s));
    ipv4_to_str(sup_net + 1, first_s, sizeof(first_s));
    ipv4_to_str(sup_bcast - 1, last_s, sizeof(last_s));

    snprintf(out_res->supernet_str, sizeof(out_res->supernet_str), "%s/%d", net_s, sup_cidr);
    strncpy(out_res->supernet_mask_str, mask_s, sizeof(out_res->supernet_mask_str) - 1);
    strncpy(out_res->supernet_broadcast_str, bcast_s, sizeof(out_res->supernet_broadcast_str) - 1);
    strncpy(out_res->supernet_first_usable, first_s, sizeof(out_res->supernet_first_usable) - 1);
    strncpy(out_res->supernet_last_usable, last_s, sizeof(out_res->supernet_last_usable) - 1);

    /* Cisco IOS CLI Commands generated in C */
    snprintf(out_res->cisco_static, sizeof(out_res->cisco_static), "ip route %s %s Null0", net_s, mask_s);
    snprintf(out_res->cisco_ospf, sizeof(out_res->cisco_ospf), "router ospf 1\n area 0 range %s %s", net_s, mask_s);
    snprintf(out_res->cisco_bgp, sizeof(out_res->cisco_bgp), "router bgp 65001\n aggregate-address %s %s summary-only", net_s, mask_s);
    snprintf(out_res->cisco_eigrp, sizeof(out_res->cisco_eigrp), "interface GigabitEthernet0/0/0\n ip summary-address eigrp 100 %s %s", net_s, mask_s);

    /* Verdicts */
    if (is_contiguous) {
        strncpy(out_res->verdict, "CONTIGUOUS_SUPERNET", sizeof(out_res->verdict) - 1);
        strncpy(out_res->verdict_badge, "Valid CIDR Contiguous Supernet", sizeof(out_res->verdict_badge) - 1);
        snprintf(out_res->verdict_desc, sizeof(out_res->verdict_desc), 
                 "All %d laboratories are strictly contiguous in memory with zero address gaps.", valid_count);
    } else {
        strncpy(out_res->verdict, "NON_CONTIGUOUS_SUMMARY", sizeof(out_res->verdict) - 1);
        strncpy(out_res->verdict_badge, "Non-Contiguous Route Summary", sizeof(out_res->verdict_badge) - 1);
        snprintf(out_res->verdict_desc, sizeof(out_res->verdict_desc), 
                 "Gaps detected between member subnets.");
    }

    free(members);
    return true;
}
