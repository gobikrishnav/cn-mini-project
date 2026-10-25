#ifndef IP_CALC_H
#define IP_CALC_H

#include "common.h"

typedef uint32_t ipv4_t;

typedef enum {
    IP_CLASS_A,
    IP_CLASS_B,
    IP_CLASS_C,
    IP_CLASS_D, /* Multicast */
    IP_CLASS_E  /* Experimental */
} ip_class_t;

typedef enum {
    IP_SCOPE_PUBLIC,
    IP_SCOPE_PRIVATE_RFC1918,
    IP_SCOPE_LOOPBACK,
    IP_SCOPE_APIPA,
    IP_SCOPE_MULTICAST,
    IP_SCOPE_BROADCAST,
    IP_SCOPE_RESERVED
} ip_scope_t;

typedef struct {
    ipv4_t ip;
    int cidr;
    ipv4_t mask;
    ipv4_t wildcard;
    ipv4_t network;
    ipv4_t broadcast;
    ipv4_t first_usable;
    ipv4_t last_usable;
    uint64_t total_ips;
    uint64_t usable_hosts;
    ip_class_t ip_class;
    ip_scope_t scope;
    char ip_str[16];
    char mask_str[16];
    char wildcard_str[16];
    char network_str[16];
    char broadcast_str[16];
    char first_usable_str[16];
    char last_usable_str[16];
} ip_info_t;

/* Parsing & String Conversion */
bool parse_ipv4(const char *str, ipv4_t *out_ip);
bool parse_cidr_string(const char *str, ipv4_t *out_ip, int *out_cidr);
void ipv4_to_str(ipv4_t ip, char *buf, size_t buflen);

/* Bitwise Mask Operations */
ipv4_t cidr_to_mask(int cidr);
int mask_to_cidr(ipv4_t mask);
ipv4_t calculate_wildcard(ipv4_t mask);

/* Network Math */
void calculate_ip_info(ipv4_t ip, int cidr, ip_info_t *info);
ip_class_t get_ip_class(ipv4_t ip);
ip_scope_t get_ip_scope(ipv4_t ip);
const char* class_to_string(ip_class_t c);
const char* scope_to_string(ip_scope_t s);

/* Binary Helpers */
void ip_to_binary_str(ipv4_t ip, char *buf, size_t buflen);
void render_bitwise_breakdown(ipv4_t ip, int cidr);

#endif /* IP_CALC_H */
