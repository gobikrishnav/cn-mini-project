#ifndef VLSM_ENGINE_H
#define VLSM_ENGINE_H

#include "common.h"
#include "ip_calc.h"

#define MAX_LAB_NAME_LEN 64
#define MAX_DEPT_NAME_LEN 64

typedef struct {
    int id;
    char name[MAX_LAB_NAME_LEN];
    char department[MAX_DEPT_NAME_LEN];
    int workstations;
    int growth_percent;
    int effective_hosts;
    int vlan_id;

    /* Computed Subnet Parameters */
    bool is_allocated;
    int allocated_cidr;
    ipv4_t subnet_mask;
    ipv4_t network_ip;
    ipv4_t broadcast_ip;
    ipv4_t first_usable;
    ipv4_t last_usable;
    ipv4_t gateway_ip;
    ipv4_t dns_server_ip;
    uint32_t block_size;
    uint32_t usable_capacity;
    uint32_t wasted_ips;
    double efficiency_pct;
} lab_spec_t;

typedef struct {
    ipv4_t base_network_ip;
    int base_cidr;
    ipv4_t base_mask;
    ipv4_t base_broadcast;
    uint64_t total_campus_capacity;

    int lab_count;
    int lab_capacity;
    lab_spec_t *labs;

    bool is_calculated;
    bool is_valid;
    char error_reason[256];

    /* Overall Summary Metrics */
    uint64_t total_requested_hosts;
    uint64_t total_allocated_blocks;
    uint64_t total_usable_hosts;
    uint64_t total_wasted_ips;
    double overall_efficiency;
    ipv4_t next_free_subnet;
    uint64_t free_ips_remaining;
} campus_vlsm_t;

/* Lifecycle */
void campus_vlsm_init(campus_vlsm_t *campus, ipv4_t base_ip, int base_cidr);
bool campus_vlsm_add_lab(campus_vlsm_t *campus, const char *name, const char *dept, 
                         int workstations, int growth_percent, int vlan_id);
bool campus_vlsm_remove_lab(campus_vlsm_t *campus, int index);
void campus_vlsm_clear_labs(campus_vlsm_t *campus);
void campus_vlsm_free(campus_vlsm_t *campus);

/* Core Allocation Algorithm */
bool campus_vlsm_calculate(campus_vlsm_t *campus);

/* Presets & Samples */
void campus_vlsm_load_preset_college(campus_vlsm_t *campus);

#endif /* VLSM_ENGINE_H */
