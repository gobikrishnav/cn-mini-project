#ifndef HOST_INVENTORY_H
#define HOST_INVENTORY_H

#include "common.h"
#include "vlsm_engine.h"

typedef enum {
    DEVICE_GATEWAY,
    DEVICE_LOCAL_SERVER,
    DEVICE_NETWORK_PRINTER,
    DEVICE_STUDENT_PC,
    DEVICE_SPARE
} device_role_t;

typedef struct {
    int index;
    char hostname[32];
    char role_name[24];
    device_role_t role;
    ipv4_t ip;
    ipv4_t mask;
    ipv4_t gateway;
    ipv4_t dns;
} host_record_t;

typedef struct {
    char lab_name[MAX_LAB_NAME_LEN];
    int vlan_id;
    ipv4_t pool_network;
    ipv4_t subnet_mask;
    ipv4_t default_gateway;
    ipv4_t dns_server;
    ipv4_t dhcp_range_start;
    ipv4_t dhcp_range_end;
    uint32_t total_dhcp_leases;
    int lease_days;
} dhcp_scope_t;

typedef struct {
    char lab_name[MAX_LAB_NAME_LEN];
    int total_hosts;
    host_record_t *records;
    dhcp_scope_t dhcp;
} lab_inventory_t;

bool generate_lab_inventory(const lab_spec_t *lab, lab_inventory_t *out_inv);
void free_lab_inventory(lab_inventory_t *inv);
void display_lab_inventory_page(const lab_inventory_t *inv, int page, int per_page);

#endif /* HOST_INVENTORY_H */
