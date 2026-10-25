#ifndef SUPERNET_ENGINE_H
#define SUPERNET_ENGINE_H

#include "common.h"
#include "ip_calc.h"
#include "vlsm_engine.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    ipv4_t network_ip;
    int cidr;
    ipv4_t mask_ip;
    ipv4_t broadcast_ip;
    uint32_t block_size;
    char network_str[32];
    char mask_str[32];
    char broadcast_str[32];
    char first_usable[32];
    char last_usable[32];
} supernet_member_t;

typedef struct {
    ipv4_t supernet_net;
    int supernet_cidr;
    ipv4_t supernet_mask;
    ipv4_t supernet_broadcast;
    uint64_t total_supernet_ips;
    uint64_t usable_supernet_hosts;
    uint64_t total_input_ips;
    int input_count;
    bool is_contiguous;
    bool is_power_of_2;
    bool is_aligned;
    bool is_valid_supernet;
    double reduction_pct;
    char supernet_str[32];
    char supernet_mask_str[32];
    char supernet_broadcast_str[32];
    char supernet_first_usable[32];
    char supernet_last_usable[32];
    char verdict[64];
    char verdict_badge[128];
    char verdict_desc[256];
    char cisco_static[128];
    char cisco_ospf[128];
    char cisco_bgp[128];
    char cisco_eigrp[128];
} supernet_calc_result_t;

/* Pure C CIDR Supernetting Engine */
bool calculate_supernet_c(const char **subnets, int count, supernet_calc_result_t *out_res);

#ifdef __cplusplus
}
#endif

#endif /* SUPERNET_ENGINE_H */
