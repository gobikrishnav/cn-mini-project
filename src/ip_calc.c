#include "ip_calc.h"

bool parse_ipv4(const char *str, ipv4_t *out_ip) {
    if (!str || !out_ip) return false;

    while (isspace((unsigned char)*str)) str++;

    unsigned int a, b, c, d;
    int n = 0;
    if (sscanf(str, "%u.%u.%u.%u%n", &a, &b, &c, &d, &n) != 4 || n == 0) {
        return false;
    }

    const char *p = str + n;
    while (*p) {
        if (!isspace((unsigned char)*p)) return false;
        p++;
    }

    if (a > 255 || b > 255 || c > 255 || d > 255) {
        return false;
    }

    *out_ip = ((ipv4_t)a << 24) | ((ipv4_t)b << 16) | ((ipv4_t)c << 8) | (ipv4_t)d;
    return true;
}

bool parse_cidr_string(const char *str, ipv4_t *out_ip, int *out_cidr) {
    if (!str || !out_ip || !out_cidr) return false;

    while (isspace((unsigned char)*str)) str++;

    char ip_part[64];
    int cidr_val = -1;

    const char *slash = strchr(str, '/');
    if (slash) {
        size_t ip_len = slash - str;
        if (ip_len >= sizeof(ip_part)) return false;
        strncpy(ip_part, str, ip_len);
        ip_part[ip_len] = '\0';

        char *endptr;
        long val = strtol(slash + 1, &endptr, 10);
        while (isspace((unsigned char)*endptr)) endptr++;
        if (*endptr != '\0' || val < 0 || val > 32) {
            return false;
        }
        cidr_val = (int)val;
    } else {
        strncpy(ip_part, str, sizeof(ip_part) - 1);
        ip_part[sizeof(ip_part) - 1] = '\0';
        /* Remove trailing whitespace */
        char *end = ip_part + strlen(ip_part) - 1;
        while (end >= ip_part && isspace((unsigned char)*end)) {
            *end = '\0';
            end--;
        }
    }

    if (!parse_ipv4(ip_part, out_ip)) {
        return false;
    }

    if (cidr_val == -1) {
        /* Default to Classful CIDR if no slash provided */
        ip_class_t cls = get_ip_class(*out_ip);
        switch (cls) {
            case IP_CLASS_A: cidr_val = 8; break;
            case IP_CLASS_B: cidr_val = 16; break;
            case IP_CLASS_C: cidr_val = 24; break;
            default: cidr_val = 24; break;
        }
    }

    *out_cidr = cidr_val;
    return true;
}

void ipv4_to_str(ipv4_t ip, char *buf, size_t buflen) {
    if (!buf || buflen == 0) return;
    snprintf(buf, buflen, "%u.%u.%u.%u",
             (ip >> 24) & 0xFF,
             (ip >> 16) & 0xFF,
             (ip >> 8)  & 0xFF,
             ip & 0xFF);
}

ipv4_t cidr_to_mask(int cidr) {
    if (cidr <= 0) return 0;
    if (cidr >= 32) return 0xFFFFFFFFU;
    return (0xFFFFFFFFU << (32 - cidr)) & 0xFFFFFFFFU;
}

int mask_to_cidr(ipv4_t mask) {
    int count = 0;
    for (int i = 31; i >= 0; i--) {
        if ((mask >> i) & 1) {
            count++;
        } else {
            break;
        }
    }
    return count;
}

ipv4_t calculate_wildcard(ipv4_t mask) {
    return (~mask) & 0xFFFFFFFFU;
}

ip_class_t get_ip_class(ipv4_t ip) {
    unsigned int first_octet = (ip >> 24) & 0xFF;
    if (first_octet <= 127) return IP_CLASS_A;
    if (first_octet <= 191) return IP_CLASS_B;
    if (first_octet <= 223) return IP_CLASS_C;
    if (first_octet <= 239) return IP_CLASS_D;
    return IP_CLASS_E;
}

ip_scope_t get_ip_scope(ipv4_t ip) {
    unsigned int o1 = (ip >> 24) & 0xFF;
    unsigned int o2 = (ip >> 16) & 0xFF;

    if (ip == 0xFFFFFFFFU) return IP_SCOPE_BROADCAST;
    if (o1 == 127) return IP_SCOPE_LOOPBACK;
    if (o1 == 169 && o2 == 254) return IP_SCOPE_APIPA;
    if (o1 >= 224 && o1 <= 239) return IP_SCOPE_MULTICAST;
    if (o1 >= 240) return IP_SCOPE_RESERVED;

    /* RFC 1918 Private Ranges */
    if (o1 == 10) return IP_SCOPE_PRIVATE_RFC1918;
    if (o1 == 172 && (o2 >= 16 && o2 <= 31)) return IP_SCOPE_PRIVATE_RFC1918;
    if (o1 == 192 && o2 == 168) return IP_SCOPE_PRIVATE_RFC1918;

    return IP_SCOPE_PUBLIC;
}

const char* class_to_string(ip_class_t c) {
    switch (c) {
        case IP_CLASS_A: return "Class A (Large Networks)";
        case IP_CLASS_B: return "Class B (Medium Networks)";
        case IP_CLASS_C: return "Class C (Small LANs)";
        case IP_CLASS_D: return "Class D (Multicast Group)";
        case IP_CLASS_E: return "Class E (Experimental/Research)";
        default: return "Unknown";
    }
}

const char* scope_to_string(ip_scope_t s) {
    switch (s) {
        case IP_SCOPE_PUBLIC: return "Public Internet (Routable)";
        case IP_SCOPE_PRIVATE_RFC1918: return "Private (RFC 1918 Non-Routable)";
        case IP_SCOPE_LOOPBACK: return "Loopback / Localhost (RFC 1122)";
        case IP_SCOPE_APIPA: return "APIPA / Link-Local (RFC 3927)";
        case IP_SCOPE_MULTICAST: return "Multicast Address Space (RFC 5771)";
        case IP_SCOPE_BROADCAST: return "Limited Broadcast";
        case IP_SCOPE_RESERVED: return "Reserved / Experimental";
        default: return "Unspecified";
    }
}

void calculate_ip_info(ipv4_t ip, int cidr, ip_info_t *info) {
    if (!info) return;

    memset(info, 0, sizeof(ip_info_t));
    info->ip = ip;
    info->cidr = cidr;
    info->mask = cidr_to_mask(cidr);
    info->wildcard = calculate_wildcard(info->mask);
    info->network = ip & info->mask;
    info->broadcast = info->network | info->wildcard;

    if (cidr == 32) {
        info->first_usable = ip;
        info->last_usable = ip;
        info->total_ips = 1;
        info->usable_hosts = 1;
    } else if (cidr == 31) {
        /* RFC 3021 Point-to-Point Links */
        info->first_usable = info->network;
        info->last_usable = info->broadcast;
        info->total_ips = 2;
        info->usable_hosts = 2;
    } else {
        info->first_usable = info->network + 1;
        info->last_usable = info->broadcast - 1;
        info->total_ips = 1ULL << (32 - cidr);
        info->usable_hosts = info->total_ips - 2;
    }

    info->ip_class = get_ip_class(ip);
    info->scope = get_ip_scope(ip);

    ipv4_to_str(info->ip, info->ip_str, sizeof(info->ip_str));
    ipv4_to_str(info->mask, info->mask_str, sizeof(info->mask_str));
    ipv4_to_str(info->wildcard, info->wildcard_str, sizeof(info->wildcard_str));
    ipv4_to_str(info->network, info->network_str, sizeof(info->network_str));
    ipv4_to_str(info->broadcast, info->broadcast_str, sizeof(info->broadcast_str));
    ipv4_to_str(info->first_usable, info->first_usable_str, sizeof(info->first_usable_str));
    ipv4_to_str(info->last_usable, info->last_usable_str, sizeof(info->last_usable_str));
}

void ip_to_binary_str(ipv4_t ip, char *buf, size_t buflen) {
    if (!buf || buflen < 36) return;
    int pos = 0;
    for (int i = 31; i >= 0; i--) {
        buf[pos++] = ((ip >> i) & 1) ? '1' : '0';
        if (i % 8 == 0 && i != 0) {
            buf[pos++] = '.';
        }
    }
    buf[pos] = '\0';
}

void render_bitwise_breakdown(ipv4_t ip, int cidr) {
    ipv4_t mask = cidr_to_mask(cidr);
    ipv4_t wildcard = calculate_wildcard(mask);
    ipv4_t net = ip & mask;
    ipv4_t bcast = net | wildcard;

    printf("\n  " ANSI_BOLD ANSI_FG_BRIGHT_CYAN "=== 32-BIT BINARY LOGICAL DECOMPOSITION ===" ANSI_RESET "\n\n");
    printf("  " ANSI_FG_WHITE "IP Address  : " ANSI_RESET);
    for (int i = 31; i >= 0; i--) {
        int bit = (ip >> i) & 1;
        if (31 - i < cidr) {
            printf(ANSI_FG_BRIGHT_CYAN "%d" ANSI_RESET, bit);
        } else {
            printf(ANSI_FG_BRIGHT_GREEN "%d" ANSI_RESET, bit);
        }
        if (i % 8 == 0 && i != 0) printf(ANSI_FG_BRIGHT_BLACK "." ANSI_RESET);
    }
    printf("  (" ANSI_FG_BRIGHT_CYAN "%u.%u.%u.%u" ANSI_RESET ")\n",
           (ip >> 24) & 0xFF, (ip >> 16) & 0xFF, (ip >> 8) & 0xFF, ip & 0xFF);

    printf("  " ANSI_FG_WHITE "Subnet Mask : " ANSI_RESET);
    for (int i = 31; i >= 0; i--) {
        int bit = (mask >> i) & 1;
        if (bit) {
            printf(ANSI_FG_BRIGHT_YELLOW "%d" ANSI_RESET, bit);
        } else {
            printf(ANSI_FG_BRIGHT_BLACK "%d" ANSI_RESET, bit);
        }
        if (i % 8 == 0 && i != 0) printf(ANSI_FG_BRIGHT_BLACK "." ANSI_RESET);
    }
    printf("  (" ANSI_FG_BRIGHT_YELLOW "%u.%u.%u.%u" ANSI_RESET ")\n",
           (mask >> 24) & 0xFF, (mask >> 16) & 0xFF, (mask >> 8) & 0xFF, mask & 0xFF);

    printf("                " ANSI_FG_BRIGHT_BLACK "───────────────────────────────────  (Bitwise AND : IP & MASK)" ANSI_RESET "\n");

    printf("  " ANSI_FG_WHITE "Network ID  : " ANSI_RESET);
    for (int i = 31; i >= 0; i--) {
        int bit = (net >> i) & 1;
        if (31 - i < cidr) {
            printf(ANSI_FG_BRIGHT_CYAN "%d" ANSI_RESET, bit);
        } else {
            printf(ANSI_FG_BRIGHT_BLACK "%d" ANSI_RESET, bit);
        }
        if (i % 8 == 0 && i != 0) printf(ANSI_FG_BRIGHT_BLACK "." ANSI_RESET);
    }
    printf("  (" ANSI_FG_BRIGHT_CYAN "%u.%u.%u.%u" ANSI_RESET ")\n",
           (net >> 24) & 0xFF, (net >> 16) & 0xFF, (net >> 8) & 0xFF, net & 0xFF);

    printf("  " ANSI_FG_WHITE "Broadcast ID: " ANSI_RESET);
    for (int i = 31; i >= 0; i--) {
        int bit = (bcast >> i) & 1;
        if (31 - i < cidr) {
            printf(ANSI_FG_BRIGHT_CYAN "%d" ANSI_RESET, bit);
        } else {
            printf(ANSI_FG_BRIGHT_MAGENTA "%d" ANSI_RESET, bit);
        }
        if (i % 8 == 0 && i != 0) printf(ANSI_FG_BRIGHT_BLACK "." ANSI_RESET);
    }
    printf("  (" ANSI_FG_BRIGHT_MAGENTA "%u.%u.%u.%u" ANSI_RESET ")\n\n",
           (bcast >> 24) & 0xFF, (bcast >> 16) & 0xFF, (bcast >> 8) & 0xFF, bcast & 0xFF);

    printf("  " ANSI_FG_BRIGHT_BLACK "Legend:" ANSI_RESET " ");
    printf(ANSI_FG_BRIGHT_CYAN "■" ANSI_RESET " Network Bits (%d)  ", cidr);
    printf(ANSI_FG_BRIGHT_GREEN "■" ANSI_RESET " Usable Host Bits (%d)  ", 32 - cidr);
    printf(ANSI_FG_BRIGHT_YELLOW "■" ANSI_RESET " Mask '1's  ");
    printf(ANSI_FG_BRIGHT_MAGENTA "■" ANSI_RESET " Broadcast '1's\n");
}
