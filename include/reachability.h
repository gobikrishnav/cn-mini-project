#ifndef REACHABILITY_H
#define REACHABILITY_H

#include "common.h"
#include "ip_calc.h"

typedef enum {
    REACH_SAME_SUBNET_L2,          /* Direct L2 Switch Delivery */
    REACH_DIFFERENT_SUBNET_L3,     /* L3 Router / Gateway Required */
    REACH_ASYMMETRIC_MASK_ERROR,   /* Subnet Mask Mismatch Configuration Bug */
    REACH_INVALID_HOST_IP          /* One of the IPs is network or broadcast */
} reachability_status_t;

typedef struct {
    ipv4_t host_a;
    int cidr_a;
    ipv4_t host_b;
    int cidr_b;

    ipv4_t net_a;
    ipv4_t net_b;

    reachability_status_t status;
    char diagnosis[512];
    char recommendation[256];
} reachability_result_t;

void analyze_reachability(ipv4_t ip_a, int cidr_a, ipv4_t ip_b, int cidr_b, reachability_result_t *res);
void render_reachability_report(const reachability_result_t *res);

#endif /* REACHABILITY_H */
