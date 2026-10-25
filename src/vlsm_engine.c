#include "vlsm_engine.h"

static int compare_labs_desc(const void *a, const void *b) {
    const lab_spec_t *lab_a = (const lab_spec_t *)a;
    const lab_spec_t *lab_b = (const lab_spec_t *)b;
    if (lab_b->effective_hosts != lab_a->effective_hosts) {
        return lab_b->effective_hosts - lab_a->effective_hosts;
    }
    return lab_a->id - lab_b->id;
}

void campus_vlsm_init(campus_vlsm_t *campus, ipv4_t base_ip, int base_cidr) {
    if (!campus) return;
    memset(campus, 0, sizeof(campus_vlsm_t));

    campus->base_cidr = base_cidr;
    campus->base_mask = cidr_to_mask(base_cidr);
    campus->base_network_ip = base_ip & campus->base_mask;
    campus->base_broadcast = campus->base_network_ip | calculate_wildcard(campus->base_mask);

    if (base_cidr >= 32) {
        campus->total_campus_capacity = 1;
    } else {
        campus->total_campus_capacity = 1ULL << (32 - base_cidr);
    }

    campus->lab_capacity = 8;
    campus->labs = (lab_spec_t *)malloc(sizeof(lab_spec_t) * campus->lab_capacity);
    campus->lab_count = 0;
    campus->is_calculated = false;
    campus->is_valid = false;
}

bool campus_vlsm_add_lab(campus_vlsm_t *campus, const char *name, const char *dept, 
                         int workstations, int growth_percent, int vlan_id) {
    if (!campus) return false;

    if (campus->lab_count >= campus->lab_capacity) {
        int new_cap = campus->lab_capacity * 2;
        lab_spec_t *resized = (lab_spec_t *)realloc(campus->labs, sizeof(lab_spec_t) * new_cap);
        if (!resized) return false;
        campus->labs = resized;
        campus->lab_capacity = new_cap;
    }

    lab_spec_t *lab = &campus->labs[campus->lab_count];
    memset(lab, 0, sizeof(lab_spec_t));

    lab->id = campus->lab_count + 1;
    strncpy(lab->name, name ? name : "Unnamed Lab", sizeof(lab->name) - 1);
    strncpy(lab->department, dept ? dept : "Campus", sizeof(lab->department) - 1);
    lab->workstations = workstations > 0 ? workstations : 1;
    lab->growth_percent = growth_percent >= 0 ? growth_percent : 0;

    /* Add buffer percentage and minimum 2 system addresses (Gateway + Local Server) */
    double buffered = (double)lab->workstations * (1.0 + ((double)lab->growth_percent / 100.0));
    lab->effective_hosts = (int)ceil(buffered);
    if (lab->effective_hosts < 2) lab->effective_hosts = 2;

    lab->vlan_id = vlan_id > 0 ? vlan_id : (10 + campus->lab_count * 10);

    campus->lab_count++;
    campus->is_calculated = false;
    return true;
}

bool campus_vlsm_remove_lab(campus_vlsm_t *campus, int index) {
    if (!campus || index < 0 || index >= campus->lab_count) return false;

    for (int i = index; i < campus->lab_count - 1; i++) {
        campus->labs[i] = campus->labs[i + 1];
        campus->labs[i].id = i + 1;
    }
    campus->lab_count--;
    campus->is_calculated = false;
    return true;
}

void campus_vlsm_clear_labs(campus_vlsm_t *campus) {
    if (!campus) return;
    campus->lab_count = 0;
    campus->is_calculated = false;
}

void campus_vlsm_free(campus_vlsm_t *campus) {
    if (!campus) return;
    if (campus->labs) {
        free(campus->labs);
        campus->labs = NULL;
    }
    campus->lab_count = 0;
    campus->lab_capacity = 0;
}

bool campus_vlsm_calculate(campus_vlsm_t *campus) {
    if (!campus || campus->lab_count == 0) {
        if (campus) {
            campus->is_valid = false;
            snprintf(campus->error_reason, sizeof(campus->error_reason), "No labs added to design.");
        }
        return false;
    }

    /* Crucial VLSM Rule: Sort descending by effective host requirements */
    qsort(campus->labs, campus->lab_count, sizeof(lab_spec_t), compare_labs_desc);

    /* Re-index IDs neatly */
    for (int i = 0; i < campus->lab_count; i++) {
        campus->labs[i].id = i + 1;
    }

    ipv4_t current_network = campus->base_network_ip;
    campus->total_requested_hosts = 0;
    campus->total_allocated_blocks = 0;
    campus->total_usable_hosts = 0;
    campus->total_wasted_ips = 0;

    for (int i = 0; i < campus->lab_count; i++) {
        lab_spec_t *lab = &campus->labs[i];
        campus->total_requested_hosts += lab->workstations;

        /* Determine minimum host bits required: (2^h - 2) >= effective_hosts */
        int h = 2;
        while (h < 31 && ((1ULL << h) - 2) < (uint64_t)lab->effective_hosts) {
            h++;
        }

        int cidr = 32 - h;
        uint32_t block_size = 1U << h;

        /* Align to power-of-2 block boundary */
        if (current_network % block_size != 0) {
            current_network = ((current_network + block_size - 1) / block_size) * block_size;
        }

        /* Check for address exhaustion against the base campus network */
        uint64_t subnet_end = (uint64_t)current_network + block_size - 1;
        if (subnet_end > (uint64_t)campus->base_broadcast) {
            campus->is_calculated = true;
            campus->is_valid = false;
            snprintf(campus->error_reason, sizeof(campus->error_reason),
                     "IP Address Space Exhausted at Lab '%s' (Requires block size %u). Base network has only %llu addresses.",
                     lab->name, block_size, (unsigned long long)campus->total_campus_capacity);
            return false;
        }

        lab->is_allocated = true;
        lab->allocated_cidr = cidr;
        lab->subnet_mask = cidr_to_mask(cidr);
        lab->network_ip = current_network;
        lab->broadcast_ip = (ipv4_t)subnet_end;
        lab->first_usable = current_network + 1;
        lab->last_usable = lab->broadcast_ip - 1;
        lab->gateway_ip = lab->first_usable; /* First usable host is assigned as Gateway */
        lab->dns_server_ip = lab->network_ip + 2; /* Local Cache / DNS */
        lab->block_size = block_size;
        lab->usable_capacity = block_size - 2;
        lab->wasted_ips = lab->usable_capacity - lab->effective_hosts;
        lab->efficiency_pct = ((double)lab->workstations / (double)lab->usable_capacity) * 100.0;

        campus->total_allocated_blocks += block_size;
        campus->total_usable_hosts += lab->usable_capacity;
        campus->total_wasted_ips += lab->wasted_ips;

        current_network += block_size;
    }

    campus->next_free_subnet = current_network;
    if ((uint64_t)campus->base_broadcast >= (uint64_t)current_network) {
        campus->free_ips_remaining = ((uint64_t)campus->base_broadcast - (uint64_t)current_network) + 1;
    } else {
        campus->free_ips_remaining = 0;
    }

    if (campus->total_usable_hosts > 0) {
        campus->overall_efficiency = ((double)campus->total_requested_hosts / (double)campus->total_usable_hosts) * 100.0;
    } else {
        campus->overall_efficiency = 0.0;
    }

    campus->is_calculated = true;
    campus->is_valid = true;
    campus->error_reason[0] = '\0';
    return true;
}

void campus_vlsm_load_preset_college(campus_vlsm_t *campus) {
    if (!campus) return;

    /* Base Campus Network: 10.50.0.0/16 */
    ipv4_t base_ip;
    parse_ipv4("10.50.0.0", &base_ip);
    campus_vlsm_init(campus, base_ip, 16);

    /* Realistic College Labs with diverse workstation requirements */
    campus_vlsm_add_lab(campus, "Artificial Intelligence & Robotics Lab", "CSE Dept - Block A", 120, 15, 10);
    campus_vlsm_add_lab(campus, "Cloud Computing & Data Science Lab",  "CSE Dept - Block A", 90,  10, 20);
    campus_vlsm_add_lab(campus, "Cyber Security & Forensics Lab",      "IT Dept - Block B",  65,  10, 30);
    campus_vlsm_add_lab(campus, "Internet of Things (IoT) Embedded Lab","ECE Dept - Block C", 45,  10, 40);
    campus_vlsm_add_lab(campus, "Object-Oriented Programming Lab",     "CSE Dept - Block A", 60,  10, 50);
    campus_vlsm_add_lab(campus, "High-Performance Data Center Farm",    "Central IT Wing",    30,  20, 60);
    campus_vlsm_add_lab(campus, "Faculty Research & Admin Wing",       "Admin Building",     22,   5, 70);
    campus_vlsm_add_lab(campus, "Core Router Inter-Switch Backbone",   "Campus WAN Infra",    2,   0, 99);

    campus_vlsm_calculate(campus);
}
