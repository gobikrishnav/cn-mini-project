#ifndef FLSM_ENGINE_H
#define FLSM_ENGINE_H

#include "common.h"
#include "ip_calc.h"

typedef struct {
    int subnet_index;
    ipv4_t network_ip;
    int cidr;
    ipv4_t subnet_mask;
    ipv4_t first_usable;
    ipv4_t last_usable;
    ipv4_t broadcast_ip;
    uint32_t usable_hosts;
} flsm_subnet_t;

typedef struct {
    ipv4_t base_ip;
    int base_cidr;
    int borrowed_bits;
    int new_cidr;
    uint32_t total_subnets_generated;
    uint32_t usable_hosts_per_subnet;
    uint32_t block_size;
    flsm_subnet_t *subnets;
    int displayed_count;
} flsm_plan_t;

bool flsm_divide_by_subnets(ipv4_t base_ip, int base_cidr, int required_subnets, flsm_plan_t *out_plan);
bool flsm_divide_by_hosts(ipv4_t base_ip, int base_cidr, int hosts_per_subnet, flsm_plan_t *out_plan);
void flsm_free_plan(flsm_plan_t *plan);

#endif /* FLSM_ENGINE_H */
