#include "flsm_engine.h"

static bool populate_flsm(flsm_plan_t *plan, ipv4_t base_ip, int base_cidr, int new_cidr) {
    if (new_cidr > 30 || new_cidr < base_cidr) {
        return false;
    }

    plan->base_ip = base_ip & cidr_to_mask(base_cidr);
    plan->base_cidr = base_cidr;
    plan->new_cidr = new_cidr;
    plan->borrowed_bits = new_cidr - base_cidr;
    plan->total_subnets_generated = 1U << plan->borrowed_bits;
    plan->block_size = 1U << (32 - new_cidr);
    plan->usable_hosts_per_subnet = plan->block_size - 2;

    int allocate_count = plan->total_subnets_generated > 512 ? 512 : plan->total_subnets_generated;
    plan->subnets = (flsm_subnet_t *)malloc(sizeof(flsm_subnet_t) * allocate_count);
    if (!plan->subnets) return false;

    plan->displayed_count = allocate_count;

    ipv4_t current_net = plan->base_ip;
    ipv4_t mask = cidr_to_mask(new_cidr);

    for (int i = 0; i < allocate_count; i++) {
        flsm_subnet_t *s = &plan->subnets[i];
        s->subnet_index = i + 1;
        s->network_ip = current_net;
        s->cidr = new_cidr;
        s->subnet_mask = mask;
        s->broadcast_ip = current_net + plan->block_size - 1;
        s->first_usable = current_net + 1;
        s->last_usable = s->broadcast_ip - 1;
        s->usable_hosts = plan->usable_hosts_per_subnet;

        current_net += plan->block_size;
    }

    return true;
}

bool flsm_divide_by_subnets(ipv4_t base_ip, int base_cidr, int required_subnets, flsm_plan_t *out_plan) {
    if (!out_plan || required_subnets <= 0) return false;
    memset(out_plan, 0, sizeof(flsm_plan_t));

    int b = 0;
    while ((1U << b) < (unsigned int)required_subnets) {
        b++;
    }

    int new_cidr = base_cidr + b;
    return populate_flsm(out_plan, base_ip, base_cidr, new_cidr);
}

bool flsm_divide_by_hosts(ipv4_t base_ip, int base_cidr, int hosts_per_subnet, flsm_plan_t *out_plan) {
    if (!out_plan || hosts_per_subnet <= 0) return false;
    memset(out_plan, 0, sizeof(flsm_plan_t));

    int h = 2;
    while (h < 31 && ((1ULL << h) - 2) < (uint64_t)hosts_per_subnet) {
        h++;
    }

    int new_cidr = 32 - h;
    if (new_cidr < base_cidr) {
        return false;
    }

    return populate_flsm(out_plan, base_ip, base_cidr, new_cidr);
}

void flsm_free_plan(flsm_plan_t *plan) {
    if (!plan) return;
    if (plan->subnets) {
        free(plan->subnets);
        plan->subnets = NULL;
    }
    plan->displayed_count = 0;
}
