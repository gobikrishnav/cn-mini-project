#include "reachability.h"

void analyze_reachability(ipv4_t ip_a, int cidr_a, ipv4_t ip_b, int cidr_b, reachability_result_t *res) {
    if (!res) return;
    memset(res, 0, sizeof(reachability_result_t));

    res->host_a = ip_a;
    res->cidr_a = cidr_a;
    res->host_b = ip_b;
    res->cidr_b = cidr_b;

    ipv4_t mask_a = cidr_to_mask(cidr_a);
    ipv4_t mask_b = cidr_to_mask(cidr_b);

    res->net_a = ip_a & mask_a;
    res->net_b = ip_b & mask_b;

    ipv4_t bcast_a = res->net_a | calculate_wildcard(mask_a);
    ipv4_t bcast_b = res->net_b | calculate_wildcard(mask_b);

    if (ip_a == res->net_a || ip_a == bcast_a || ip_b == res->net_b || ip_b == bcast_b) {
        res->status = REACH_INVALID_HOST_IP;
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "Warning: One or both assigned IP addresses are reserved Network or Broadcast identifiers.");
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "Assign valid usable host IP addresses within the range.");
        return;
    }

    bool a_thinks_b_local = ((ip_b & mask_a) == res->net_a);
    bool b_thinks_a_local = ((ip_a & mask_b) == res->net_b);

    if (a_thinks_b_local && b_thinks_a_local && (cidr_a == cidr_b)) {
        res->status = REACH_SAME_SUBNET_L2;
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "DIRECT LAYER-2 SWITCHED PATH: Both hosts share the identical subnet (%u.%u.%u.%u/%d). "
                 "They can communicate directly through a Layer-2 switch. Host A will broadcast an ARP request "
                 "for Host B's MAC address, and frames will be exchanged with zero router hops.",
                 (res->net_a >> 24) & 0xFF, (res->net_a >> 16) & 0xFF,
                 (res->net_a >> 8) & 0xFF, res->net_a & 0xFF, cidr_a);
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "No routing configuration needed. Verify switch VLAN membership is identical.");
    } else if (a_thinks_b_local != b_thinks_a_local) {
        res->status = REACH_ASYMMETRIC_MASK_ERROR;
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "ASYMMETRIC MASK MISCONFIGURATION: Host A has /%d while Host B has /%d. "
                 "Host %s considers the destination local (will ARP), while Host %s considers "
                 "the destination remote (will send to gateway). This creates a blackhole communication failure!",
                 cidr_a, cidr_b,
                 a_thinks_b_local ? "A" : "B",
                 b_thinks_a_local ? "A" : "B");
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "Ensure consistent subnet masks across all hosts on the same physical broadcast domain.");
    } else {
        res->status = REACH_DIFFERENT_SUBNET_L3;
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "ROUTED LAYER-3 PATH REQUIRED: Hosts reside on different subnets (Host A on %u.%u.%u.%u/%d, "
                 "Host B on %u.%u.%u.%u/%d). Direct Layer-2 frames will NOT reach each other. "
                 "Host A must send packets to its Default Gateway via ARP; a Layer-3 Router or L3 Switch "
                 "must perform Inter-VLAN routing (802.1Q trunking).",
                 (res->net_a >> 24) & 0xFF, (res->net_a >> 16) & 0xFF,
                 (res->net_a >> 8) & 0xFF, res->net_a & 0xFF, cidr_a,
                 (res->net_b >> 24) & 0xFF, (res->net_b >> 16) & 0xFF,
                 (res->net_b >> 8) & 0xFF, res->net_b & 0xFF, cidr_b);
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "Configure default gateways on both endpoints and enable IP routing on intermediate router/L3 switch.");
    }
}

void render_reachability_report(const reachability_result_t *res) {
    if (!res) return;

    char ip_a_str[16], ip_b_str[16], net_a_str[16], net_b_str[16];
    ipv4_to_str(res->host_a, ip_a_str, sizeof(ip_a_str));
    ipv4_to_str(res->host_b, ip_b_str, sizeof(ip_b_str));
    ipv4_to_str(res->net_a, net_a_str, sizeof(net_a_str));
    ipv4_to_str(res->net_b, net_b_str, sizeof(net_b_str));

    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== INTER-HOST COMMUNICATION & ROUTING ANALYSIS ===" ANSI_RESET "\n\n");
    printf("  " ANSI_FG_WHITE "Endpoint A : " ANSI_BOLD ANSI_FG_BRIGHT_GREEN "%s/%d" ANSI_RESET
           "  (Network: %s)\n", ip_a_str, res->cidr_a, net_a_str);
    printf("  " ANSI_FG_WHITE "Endpoint B : " ANSI_BOLD ANSI_FG_BRIGHT_YELLOW "%s/%d" ANSI_RESET
           "  (Network: %s)\n\n", ip_b_str, res->cidr_b, net_b_str);

    const char *status_badge = "";
    if (res->status == REACH_SAME_SUBNET_L2) {
        status_badge = ANSI_BG_GREEN ANSI_FG_BRIGHT_WHITE " DIRECT L2 SWITCHING POSSIBLE " ANSI_RESET;
    } else if (res->status == REACH_DIFFERENT_SUBNET_L3) {
        status_badge = ANSI_BG_BLUE ANSI_FG_BRIGHT_WHITE " LAYER-3 ROUTER / GATEWAY REQUIRED " ANSI_RESET;
    } else if (res->status == REACH_ASYMMETRIC_MASK_ERROR) {
        status_badge = ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " CONFIGURATION ERROR: ASYMMETRIC MASK " ANSI_RESET;
    } else {
        status_badge = ANSI_BG_RED ANSI_FG_BRIGHT_WHITE " INVALID HOST ADDRESS " ANSI_RESET;
    }

    printf("  " ANSI_BOLD "Connectivity Status:" ANSI_RESET " %s\n\n", status_badge);

    printf("  " ANSI_FG_BRIGHT_CYAN BOX_TL);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_TR ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET " "
           ANSI_BOLD "Technical Analysis:" ANSI_RESET "\n");
    printf("  " ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET " "
           "%-74.74s" ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET "\n", res->diagnosis);
    if (strlen(res->diagnosis) > 74) {
        printf("  " ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET " "
               "%-74.74s" ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET "\n", res->diagnosis + 74);
    }
    if (strlen(res->diagnosis) > 148) {
        printf("  " ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET " "
               "%-74.74s" ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET "\n", res->diagnosis + 148);
    }

    printf("  " ANSI_FG_BRIGHT_CYAN BOX_T_RIGHT);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_T_LEFT ANSI_RESET "\n");

    printf("  " ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET " "
           ANSI_BOLD "Engineering Recommendation:" ANSI_RESET "\n");
    printf("  " ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET " "
           "%-74.74s" ANSI_FG_BRIGHT_CYAN BOX_V ANSI_RESET "\n", res->recommendation);

    printf("  " ANSI_FG_BRIGHT_CYAN BOX_BL);
    for (int i = 0; i < 76; i++) printf(BOX_H);
    printf(BOX_BR ANSI_RESET "\n");
}
