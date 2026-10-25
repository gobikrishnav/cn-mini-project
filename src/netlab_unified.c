/**
 * ==============================================================================================
 * PROJECT TITLE: CAMPUS NETWORK SUBNET ARCHITECT & DYNAMIC VLSM SUITE (NetLab-Pro)
 * COURSE:        23AD551 - COMPUTER NETWORKING LABORATORY
 * DEPARTMENT:    DEPARTMENT OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE
 * INSTITUTION:   MEPCO SCHLENK ENGINEERING COLLEGE (AUTONOMOUS), SIVAKASI
 * 
 * MODULE:        CHAPTER 2 - SECTION 2.2: PROGRAM CODING (C - CODE)
 * DESCRIPTION:   Complete, self-contained C implementation of IPv4 Bitwise Algebra,
 *                Variable Length Subnet Masking (VLSM) Allocation, CIDR Supernetting /
 *                Route Summarization with Contiguity Checking, 32-Bit Binary Boolean ANDing,
 *                and Layer-2 / Layer-3 Reachability Diagnostics.
 * ==============================================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <ctype.h>

#define MAX_LABS 32
#define MAX_NAME_LEN 64
#define MAX_DEPT_LEN 64

/* IPv4 address represented as an unsigned 32-bit integer in host byte order */
typedef uint32_t ipv4_t;

/* Structure representing a laboratory subnet allocation */
typedef struct {
    int id;
    char name[MAX_NAME_LEN];
    char department[MAX_DEPT_LEN];
    int workstations;
    int growth_percent;
    int effective_hosts;
    int vlan_id;
    int allocated_cidr;
    uint32_t block_size;
    ipv4_t subnet_mask;
    ipv4_t network_ip;
    ipv4_t broadcast_ip;
    ipv4_t first_usable;
    ipv4_t last_usable;
    ipv4_t gateway_ip;
    uint32_t usable_capacity;
    float efficiency_pct;
    bool is_allocated;
} lab_spec_t;

/* Structure representing the overall campus network */
typedef struct {
    ipv4_t base_ip;
    int base_cidr;
    ipv4_t base_mask;
    ipv4_t base_network;
    ipv4_t base_broadcast;
    uint64_t total_capacity;
    lab_spec_t labs[MAX_LABS];
    int lab_count;
    uint64_t total_requested_hosts;
    uint64_t total_allocated_blocks;
    uint64_t total_usable_hosts;
    float overall_efficiency;
    ipv4_t next_free_subnet;
    uint64_t free_ips_remaining;
    bool is_valid;
    char error_reason[256];
} campus_network_t;

/* ==============================================================================================
 * MODULE 1: IP ADDRESS CONVERSION & BITWISE MATHEMATICS
 * ============================================================================================== */

/**
 * Converts a dotted-decimal IPv4 string (e.g. "192.168.1.1") into a 32-bit unsigned integer.
 */
bool parse_ipv4(const char *ip_str, ipv4_t *out_ip) {
    if (!ip_str || !out_ip) return false;
    unsigned int b0, b1, b2, b3;
    char extra;
    if (sscanf(ip_str, "%u.%u.%u.%u%c", &b0, &b1, &b2, &b3, &extra) != 4) {
        return false;
    }
    if (b0 > 255 || b1 > 255 || b2 > 255 || b3 > 255) {
        return false;
    }
    *out_ip = ((ipv4_t)b0 << 24) | ((ipv4_t)b1 << 16) | ((ipv4_t)b2 << 8) | (ipv4_t)b3;
    return true;
}

/**
 * Converts a 32-bit unsigned integer into a dotted-decimal IPv4 string.
 */
void ipv4_to_str(ipv4_t ip, char *buf, size_t buf_len) {
    if (!buf || buf_len < 16) return;
    snprintf(buf, buf_len, "%u.%u.%u.%u",
             (ip >> 24) & 0xFF,
             (ip >> 16) & 0xFF,
             (ip >> 8) & 0xFF,
             ip & 0xFF);
}

/**
 * Converts a CIDR prefix length (0-32) to a 32-bit subnet mask integer.
 */
ipv4_t cidr_to_mask(int cidr) {
    if (cidr <= 0) return 0;
    if (cidr >= 32) return 0xFFFFFFFF;
    return (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF;
}

/**
 * Calculates CIDR prefix length from a 32-bit subnet mask.
 */
int mask_to_cidr(ipv4_t mask) {
    int cidr = 0;
    while (mask & 0x80000000) {
        cidr++;
        mask <<= 1;
    }
    return cidr;
}

/**
 * Formats a 32-bit integer into a dot-separated binary string (e.g. "11000000.10101000.00000001.00000001")
 */
void ipv4_to_binary_str(ipv4_t ip, char *buf, size_t buf_len) {
    if (!buf || buf_len < 36) return;
    int pos = 0;
    for (int i = 31; i >= 0; i--) {
        buf[pos++] = ((ip >> i) & 1) ? '1' : '0';
        if (i == 24 || i == 16 || i == 8) {
            buf[pos++] = '.';
        }
    }
    buf[pos] = '\0';
}

/* ==============================================================================================
 * MODULE 2: DYNAMIC VLSM SUBNETTING ENGINE
 * ============================================================================================== */

/* Comparator for descending host sorting (Core VLSM Requirement) */
int compare_labs_descending(const void *a, const void *b) {
    const lab_spec_t *lab_a = (const lab_spec_t *)a;
    const lab_spec_t *lab_b = (const lab_spec_t *)b;
    return lab_b->effective_hosts - lab_a->effective_hosts;
}

/**
 * Executes Variable Length Subnet Masking (VLSM) allocation across all campus labs.
 */
bool calculate_campus_vlsm(campus_network_t *campus) {
    if (!campus || campus->lab_count == 0) return false;

    /* Step 1: Sort labs descending by host requirement */
    qsort(campus->labs, campus->lab_count, sizeof(lab_spec_t), compare_labs_descending);
    for (int i = 0; i < campus->lab_count; i++) {
        campus->labs[i].id = i + 1;
    }

    ipv4_t current_network = campus->base_network;
    campus->total_requested_hosts = 0;
    campus->total_allocated_blocks = 0;
    campus->total_usable_hosts = 0;
    campus->is_valid = true;
    campus->error_reason[0] = '\0';

    for (int i = 0; i < campus->lab_count; i++) {
        lab_spec_t *lab = &campus->labs[i];
        campus->total_requested_hosts += lab->workstations;

        /* Find minimum host bits: (2^h - 2) >= effective_hosts */
        int h = 2;
        while (h < 31 && ((1U << h) - 2) < (uint32_t)lab->effective_hosts) {
            h++;
        }

        lab->allocated_cidr = 32 - h;
        lab->block_size = (1U << h);
        lab->usable_capacity = (lab->allocated_cidr >= 31) ? lab->block_size : (lab->block_size - 2);

        /* Boundary alignment: current_network must be divisible by block_size */
        if (current_network % lab->block_size != 0) {
            current_network = ((current_network + lab->block_size - 1) / lab->block_size) * lab->block_size;
        }

        /* Check for address space exhaustion */
        ipv4_t subnet_end = current_network + lab->block_size - 1;
        if (subnet_end > campus->base_broadcast || current_network < campus->base_network) {
            campus->is_valid = false;
            lab->is_allocated = false;
            snprintf(campus->error_reason, sizeof(campus->error_reason),
                     "Address space exhausted at Lab '%s' (Needs block of %u IPs).",
                     lab->name, lab->block_size);
            return false;
        }

        lab->is_allocated = true;
        lab->subnet_mask = cidr_to_mask(lab->allocated_cidr);
        lab->network_ip = current_network;
        lab->broadcast_ip = subnet_end;
        lab->first_usable = current_network + 1;
        lab->last_usable = subnet_end - 1;
        lab->gateway_ip = lab->first_usable;
        lab->efficiency_pct = ((float)lab->workstations / (float)lab->usable_capacity) * 100.0f;

        campus->total_allocated_blocks += lab->block_size;
        campus->total_usable_hosts += lab->usable_capacity;

        current_network += lab->block_size;
    }

    campus->next_free_subnet = current_network;
    campus->free_ips_remaining = (campus->base_broadcast >= current_network) ?
                                 ((campus->base_broadcast - current_network) + 1) : 0;
    campus->overall_efficiency = (campus->total_usable_hosts > 0) ?
                                 (((float)campus->total_requested_hosts / (float)campus->total_usable_hosts) * 100.0f) : 0.0f;
    return true;
}

/* ==============================================================================================
 * MODULE 3: CIDR SUPERNETTING & CONTIGUITY VERIFICATION
 * ============================================================================================== */

typedef struct {
    ipv4_t supernet_ip;
    int supernet_cidr;
    ipv4_t supernet_mask;
    ipv4_t supernet_broadcast;
    uint64_t total_supernet_ips;
    uint64_t usable_supernet_hosts;
    uint64_t total_input_ips;
    int input_count;
    float reduction_pct;
    bool is_contiguous;
    bool is_power_of_2;
    bool is_boundary_aligned;
    bool is_valid_supernet;
} supernet_result_t;

/**
 * Calculates CIDR Supernet route summarization across multiple IPv4 blocks.
 * Verifies strict contiguity, power-of-2 alignment, and Longest Common Prefix (LCP).
 */
bool calculate_supernet(ipv4_t *networks, int *cidrs, int count, supernet_result_t *res) {
    if (!networks || !cidrs || count < 2 || !res) return false;

    memset(res, 0, sizeof(supernet_result_t));
    res->input_count = count;

    /* Sort input subnets ascending by network IP */
    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            if (networks[j] > networks[j + 1]) {
                ipv4_t tmp_n = networks[j]; networks[j] = networks[j + 1]; networks[j + 1] = tmp_n;
                int tmp_c = cidrs[j]; cidrs[j] = cidrs[j + 1]; cidrs[j + 1] = tmp_c;
            }
        }
    }

    /* Check strict contiguity: each block begins immediately after previous broadcast */
    res->is_contiguous = true;
    res->total_input_ips = 0;
    for (int i = 0; i < count; i++) {
        uint64_t sz = 1ULL << (32 - cidrs[i]);
        res->total_input_ips += sz;
        if (i > 0) {
            uint64_t prev_sz = 1ULL << (32 - cidrs[i - 1]);
            ipv4_t prev_bcast = networks[i - 1] + (ipv4_t)prev_sz - 1;
            if (networks[i] != prev_bcast + 1) {
                res->is_contiguous = false;
            }
        }
    }

    /* Longest Common Prefix (LCP) via XOR difference */
    ipv4_t min_net = networks[0];
    uint64_t last_sz = 1ULL << (32 - cidrs[count - 1]);
    ipv4_t max_bcast = networks[count - 1] + (ipv4_t)last_sz - 1;
    ipv4_t diff = min_net ^ max_bcast;

    int lcp = 32;
    if (diff != 0) {
        while (diff > 0) {
            lcp--;
            diff >>= 1;
        }
    }

    res->supernet_cidr = lcp;
    res->supernet_mask = cidr_to_mask(lcp);
    res->supernet_ip = min_net & res->supernet_mask;
    res->total_supernet_ips = 1ULL << (32 - lcp);
    res->supernet_broadcast = res->supernet_ip + (ipv4_t)res->total_supernet_ips - 1;
    res->usable_supernet_hosts = (lcp >= 31) ? res->total_supernet_ips : (res->total_supernet_ips - 2);

    /* Power-of-2 check and boundary divisibility */
    res->is_power_of_2 = (count > 0) && ((count & (count - 1)) == 0);
    res->is_boundary_aligned = (res->supernet_ip % res->total_supernet_ips == 0);
    res->reduction_pct = ((float)(count - 1) / (float)count) * 100.0f;
    res->is_valid_supernet = res->is_contiguous;

    return true;
}

/* ==============================================================================================
 * MODULE 4: LAYER-2 VS LAYER-3 REACHABILITY DIAGNOSTICS
 * ============================================================================================== */

typedef enum {
    REACH_L2_DIRECT_SWITCHED,
    REACH_L3_ROUTED_PATH,
    REACH_ASYMMETRIC_MASK_ERROR,
    REACH_INVALID_HOST_IP
} reachability_status_t;

typedef struct {
    reachability_status_t status;
    char verdict[128];
    char diagnosis[512];
    char recommendation[256];
} reachability_result_t;

/**
 * Analyzes Layer-2 switching vs Layer-3 routing path between two host IP addresses.
 */
void analyze_reachability(ipv4_t ip_a, int cidr_a, ipv4_t ip_b, int cidr_b, reachability_result_t *res) {
    if (!res) return;
    memset(res, 0, sizeof(reachability_result_t));

    ipv4_t mask_a = cidr_to_mask(cidr_a);
    ipv4_t mask_b = cidr_to_mask(cidr_b);
    ipv4_t net_a = ip_a & mask_a;
    ipv4_t net_b = ip_b & mask_b;
    ipv4_t bcast_a = net_a | (~mask_a);
    ipv4_t bcast_b = net_b | (~mask_b);

    /* Check for reserved Subnet ID or Broadcast ID */
    if (ip_a == net_a || ip_a == bcast_a || ip_b == net_b || ip_b == bcast_b) {
        res->status = REACH_INVALID_HOST_IP;
        snprintf(res->verdict, sizeof(res->verdict), "INVALID HOST IP ASSIGNED");
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "One or both endpoints are assigned a reserved Network ID or Broadcast address.");
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "Assign valid usable host IP addresses strictly inside host range.");
        return;
    }

    bool a_thinks_b_local = ((ip_b & mask_a) == net_a);
    bool b_thinks_a_local = ((ip_a & mask_b) == net_b);

    if (a_thinks_b_local && b_thinks_a_local && (cidr_a == cidr_b)) {
        res->status = REACH_L2_DIRECT_SWITCHED;
        snprintf(res->verdict, sizeof(res->verdict), "DIRECT LAYER-2 SWITCHED PATH");
        char net_s[16]; ipv4_to_str(net_a, net_s, sizeof(net_s));
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "Both hosts belong to the identical subnet (%s/%d). Host A broadcasts an ARP "
                 "request for Host B's MAC address directly over the local L2 switch. Zero router hops.",
                 net_s, cidr_a);
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "Ensure both switch ports share the identical 802.1Q VLAN ID. No default gateway required.");
    } else if (a_thinks_b_local != b_thinks_a_local) {
        res->status = REACH_ASYMMETRIC_MASK_ERROR;
        snprintf(res->verdict, sizeof(res->verdict), "ASYMMETRIC MASK MISCONFIGURATION (BLACKHOLE)");
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "Host A has mask /%d while Host B has /%d. One endpoint attempts local ARP resolution "
                 "while the peer routes to its default gateway. Creates a one-way communications blackhole.",
                 cidr_a, cidr_b);
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "Standardize subnet masks across all workstations residing on the same broadcast domain.");
    } else {
        res->status = REACH_L3_ROUTED_PATH;
        snprintf(res->verdict, sizeof(res->verdict), "LAYER-3 ROUTED PATH REQUIRED");
        char net_a_s[16], net_b_s[16];
        ipv4_to_str(net_a, net_a_s, sizeof(net_a_s));
        ipv4_to_str(net_b, net_b_s, sizeof(net_b_s));
        snprintf(res->diagnosis, sizeof(res->diagnosis),
                 "Endpoints reside on separate subnets (Host A on %s/%d, Host B on %s/%d). "
                 "Broadcast frames cannot cross subnet boundaries. Traffic must traverse a Layer-3 Router/Gateway.",
                 net_a_s, cidr_a, net_b_s, cidr_b);
        snprintf(res->recommendation, sizeof(res->recommendation),
                 "Configure valid Default Gateway IP on both nodes and enable IP routing on Core switch.");
    }
}

/* ==============================================================================================
 * MODULE 5: USER-DRIVEN CLI MENU SYSTEM
 * ============================================================================================== */

void print_separator(char c, int len) {
    for (int i = 0; i < len; i++) putchar(c);
    putchar('\n');
}

void run_vlsm_menu(void) {
    print_separator('=', 80);
    printf("         FEATURE 1: DYNAMIC CAMPUS VLSM SUBNET ARCHITECT\n");
    print_separator('=', 80);

    campus_network_t campus;
    memset(&campus, 0, sizeof(campus));

    char base_ip_str[32];
    printf("Enter Root Campus Network IP (e.g. 192.168.0.0 or 10.50.0.0): ");
    if (scanf("%31s", base_ip_str) != 1 || !parse_ipv4(base_ip_str, &campus.base_ip)) {
        printf("[ERROR] Invalid IPv4 address entered.\n");
        return;
    }

    printf("Enter Root CIDR Prefix Length (e.g. 16, 22, 24): ");
    if (scanf("%d", &campus.base_cidr) != 1 || campus.base_cidr < 8 || campus.base_cidr > 30) {
        printf("[ERROR] Invalid CIDR prefix.\n");
        return;
    }

    campus.base_mask = cidr_to_mask(campus.base_cidr);
    campus.base_network = campus.base_ip & campus.base_mask;
    campus.base_broadcast = campus.base_network | (~campus.base_mask);
    campus.total_capacity = 1ULL << (32 - campus.base_cidr);

    printf("Enter Number of Campus Laboratories to Configure: ");
    if (scanf("%d", &campus.lab_count) != 1 || campus.lab_count <= 0 || campus.lab_count > MAX_LABS) {
        printf("[ERROR] Lab count must be between 1 and %d.\n", MAX_LABS);
        return;
    }

    for (int i = 0; i < campus.lab_count; i++) {
        lab_spec_t *l = &campus.labs[i];
        l->id = i + 1;
        printf("\n--- Laboratory #%d Configuration ---\n", i + 1);
        printf("  Enter Laboratory Name (e.g. Networks_Lab): ");
        scanf("%63s", l->name);
        printf("  Enter Department / Wing (e.g. CSE_Block_A): ");
        scanf("%63s", l->department);
        printf("  Enter Number of Workstations / PCs: ");
        scanf("%d", &l->workstations);
        printf("  Enter Future Growth Buffer Percentage (e.g. 10): ");
        scanf("%d", &l->growth_percent);
        l->vlan_id = (i + 1) * 10;

        float buffered = (float)l->workstations * (1.0f + ((float)l->growth_percent / 100.0f));
        l->effective_hosts = (int)(buffered + 0.999f);
        if (l->effective_hosts < 2) l->effective_hosts = 2;
    }

    printf("\n[INFO] Executing Descending VLSM Greedy Allocation in C...\n\n");
    if (!calculate_campus_vlsm(&campus)) {
        printf("[FAILED] %s\n", campus.error_reason);
        return;
    }

    print_separator('-', 100);
    printf("%-4s %-20s %-12s %-6s %-18s %-16s %-16s %-6s\n",
           "ID", "LABORATORY NAME", "DEPARTMENT", "VLAN", "SUBNET / CIDR", "DEFAULT GATEWAY", "USABLE RANGE", "EFF%");
    print_separator('-', 100);

    for (int i = 0; i < campus.lab_count; i++) {
        lab_spec_t *l = &campus.labs[i];
        char net_s[16], gw_s[16], f_s[16], l_s[16];
        ipv4_to_str(l->network_ip, net_s, sizeof(net_s));
        ipv4_to_str(l->gateway_ip, gw_s, sizeof(gw_s));
        ipv4_to_str(l->first_usable, f_s, sizeof(f_s));
        ipv4_to_str(l->last_usable, l_s, sizeof(l_s));

        char sub_str[24], range_str[36];
        snprintf(sub_str, sizeof(sub_str), "%s/%d", net_s, l->allocated_cidr);
        snprintf(range_str, sizeof(range_str), "%s-%s", f_s, l_s);

        printf("#%-3d %-20s %-12s %-6d %-18s %-16s %-16s %5.1f%%\n",
               l->id, l->name, l->department, l->vlan_id, sub_str, gw_s, range_str, l->efficiency_pct);
    }
    print_separator('-', 100);

    char next_free_s[16];
    ipv4_to_str(campus.next_free_subnet, next_free_s, sizeof(next_free_s));
    printf("Allocation Metrics:\n");
    printf("  Total Campus Block: %llu IPs | Requested PCs: %llu | Allocated Capacity: %llu IPs\n",
           (unsigned long long)campus.total_capacity,
           (unsigned long long)campus.total_requested_hosts,
           (unsigned long long)campus.total_allocated_blocks);
    printf("  Overall Utilization Efficiency: %.1f%% | Next Free Subnet: %s | Remaining Free IPs: %llu\n",
           campus.overall_efficiency, next_free_s, (unsigned long long)campus.free_ips_remaining);
}

void run_supernet_menu(void) {
    print_separator('=', 80);
    printf("         FEATURE 2: CIDR SUPERNETTING & CONTIGUITY VERIFICATION\n");
    print_separator('=', 80);

    int count = 0;
    printf("Enter number of subnets to merge / summarize (2 to 8): ");
    if (scanf("%d", &count) != 1 || count < 2 || count > 8) {
        printf("[ERROR] Count must be between 2 and 8.\n");
        return;
    }

    ipv4_t networks[8];
    int cidrs[8];

    for (int i = 0; i < count; i++) {
        char input[32];
        printf("  Enter Subnet #%d in IP/CIDR format (e.g. 192.168.0.0/26): ", i + 1);
        scanf("%31s", input);
        char *slash = strchr(input, '/');
        if (!slash) {
            printf("[ERROR] Missing '/' in CIDR string.\n");
            return;
        }
        *slash = '\0';
        if (!parse_ipv4(input, &networks[i])) {
            printf("[ERROR] Invalid IPv4 address.\n");
            return;
        }
        cidrs[i] = atoi(slash + 1);
    }

    supernet_result_t res;
    if (calculate_supernet(networks, cidrs, count, &res)) {
        char sup_ip[16], sup_mask[16], sup_bcast[16];
        ipv4_to_str(res.supernet_ip, sup_ip, sizeof(sup_ip));
        ipv4_to_str(res.supernet_mask, sup_mask, sizeof(sup_mask));
        ipv4_to_str(res.supernet_broadcast, sup_bcast, sizeof(sup_bcast));

        printf("\n=================== CIDR SUPERNETTING RESULT ===================\n");
        printf("  Synthesized Supernet:         %s/%d\n", sup_ip, res.supernet_cidr);
        printf("  Supernet Subnet Mask:         %s\n", sup_mask);
        printf("  Supernet Broadcast IP:        %s\n", sup_bcast);
        printf("  Total Aggregated Capacity:    %llu IPs (%llu usable hosts)\n",
               (unsigned long long)res.total_supernet_ips, (unsigned long long)res.usable_supernet_hosts);
        printf("  Routing Table Reduction:      %.1f%%\n", res.reduction_pct);
        printf("  Contiguity Verification:      %s\n", res.is_contiguous ? "PASSED (Zero address gaps)" : "FAILED (Address gaps exist)");
        printf("  Power-of-2 Block Condition:   %s\n", res.is_power_of_2 ? "PASSED (2^n subnets)" : "VARIABLE CIDR");
        printf("  Boundary Alignment:           %s\n", res.is_boundary_aligned ? "PASSED" : "FAILED");
        printf("  Cisco IOS Static Route:       ip route %s %s Null0\n", sup_ip, sup_mask);
        print_separator('=', 80);
    }
}

void run_binary_menu(void) {
    print_separator('=', 80);
    printf("         FEATURE 3: 32-BIT BINARY VISUALIZER & BITWISE ANDing\n");
    print_separator('=', 80);

    char ip_str[32];
    int cidr = 24;
    printf("Enter IPv4 Address (e.g. 192.168.1.130): ");
    scanf("%31s", ip_str);
    printf("Enter CIDR Prefix Length (e.g. 26): ");
    scanf("%d", &cidr);

    ipv4_t ip;
    if (!parse_ipv4(ip_str, &ip) || cidr < 0 || cidr > 32) {
        printf("[ERROR] Invalid IP or CIDR.\n");
        return;
    }

    ipv4_t mask = cidr_to_mask(cidr);
    ipv4_t net = ip & mask;
    ipv4_t bcast = net | (~mask);

    char bin_ip[36], bin_mask[36], bin_net[36], bin_bcast[36];
    ipv4_to_binary_str(ip, bin_ip, sizeof(bin_ip));
    ipv4_to_binary_str(mask, bin_mask, sizeof(bin_mask));
    ipv4_to_binary_str(net, bin_net, sizeof(bin_net));
    ipv4_to_binary_str(bcast, bin_bcast, sizeof(bin_bcast));

    char net_s[16], bcast_s[16], mask_s[16];
    ipv4_to_str(net, net_s, sizeof(net_s));
    ipv4_to_str(bcast, bcast_s, sizeof(bcast_s));
    ipv4_to_str(mask, mask_s, sizeof(mask_s));

    printf("\n32-Bit Bitwise Boolean ANDing Breakdown:\n");
    printf("  Host IP:       %s  (%s)\n", bin_ip, ip_str);
    printf("  Subnet Mask:   %s  (%s)\n", bin_mask, mask_s);
    printf("  ------------------------------------------------------------ (Bitwise AND)\n");
    printf("  Network ID:    %s  (%s/%d)\n", bin_net, net_s, cidr);
    printf("  Broadcast ID:  %s  (%s)\n", bin_bcast, bcast_s);
    printf("\n  Bits Summary:  Network Bits = %d | Host Bits = %d | Usable Hosts = %u\n",
           cidr, 32 - cidr, (cidr >= 31) ? (1U << (32 - cidr)) : ((1U << (32 - cidr)) - 2));
}

void run_reachability_menu(void) {
    print_separator('=', 80);
    printf("         FEATURE 4: LAYER-2 VS LAYER-3 REACHABILITY DIAGNOSTICS\n");
    print_separator('=', 80);

    char ip_a_str[32], ip_b_str[32];
    int cidr_a = 24, cidr_b = 24;

    printf("Enter Host A IP Address (e.g. 192.168.1.10): ");
    scanf("%31s", ip_a_str);
    printf("Enter Host A CIDR (e.g. 24): ");
    scanf("%d", &cidr_a);

    printf("Enter Host B IP Address (e.g. 192.168.1.50 or 192.168.2.10): ");
    scanf("%31s", ip_b_str);
    printf("Enter Host B CIDR (e.g. 24): ");
    scanf("%d", &cidr_b);

    ipv4_t ip_a, ip_b;
    if (!parse_ipv4(ip_a_str, &ip_a) || !parse_ipv4(ip_b_str, &ip_b)) {
        printf("[ERROR] Invalid IP format.\n");
        return;
    }

    reachability_result_t res;
    analyze_reachability(ip_a, cidr_a, ip_b, cidr_b, &res);

    printf("\n================ PATH ANALYSIS DIAGNOSTIC RESULT ================\n");
    printf("  Verdict:        %s\n", res.verdict);
    printf("  Diagnosis:      %s\n", res.diagnosis);
    printf("  Recommendation: %s\n", res.recommendation);
    print_separator('=', 80);
}

int main(void) {
    while (1) {
        printf("\n");
        print_separator('=', 78);
        printf("    CAMPUS NETWORK SUBNET ARCHITECT & DYNAMIC VLSM SUITE (C-CORE)\n");
        printf("    23AD551 - Computer Networking Laboratory | Mepco Schlenk Engg College\n");
        print_separator('=', 78);
        printf("  [1] Dynamic Campus VLSM Laboratory Subnetting Architect\n");
        printf("  [2] CIDR Supernetting & Contiguity Verification Engine\n");
        printf("  [3] 32-Bit Binary Visualizer & Bitwise Boolean Algebra\n");
        printf("  [4] Layer-2 Switching vs Layer-3 Routing Reachability Diagnostics\n");
        printf("  [0] Exit Application\n");
        print_separator('-', 78);
        printf("Enter your choice [0-4]: ");

        int choice = -1;
        if (scanf("%d", &choice) != 1) {
            break;
        }

        if (choice == 0) {
            printf("\nExiting NetLab-Pro C Engine. Thank you!\n");
            break;
        }

        switch (choice) {
            case 1: run_vlsm_menu(); break;
            case 2: run_supernet_menu(); break;
            case 3: run_binary_menu(); break;
            case 4: run_reachability_menu(); break;
            default: printf("[!] Invalid selection. Please choose 0 to 4.\n");
        }
    }
    return 0;
}
