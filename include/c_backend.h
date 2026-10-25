#ifndef C_BACKEND_H
#define C_BACKEND_H

#include "common.h"
#include "ip_calc.h"
#include "vlsm_engine.h"
#include "supernet_engine.h"
#include "reachability.h"
#include "cisco_export.h"

#ifdef _WIN32
    #define EXPORT_API __declspec(dllexport)
#else
    #define EXPORT_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

EXPORT_API const char* c_get_backend_version(void);
EXPORT_API uint32_t c_ip_to_int(const char *ip_str);
EXPORT_API void c_int_to_ip(uint32_t ip, char *buf);
EXPORT_API int c_calculate_ip_info_fast(const char *ip_cidr, char *out_json, int max_len);
EXPORT_API int c_calculate_supernet_fast(const char *subnets_newline_delimited, char *out_json, int max_len);
EXPORT_API int c_calculate_vlsm_fast(const char *base_ip, int base_cidr, const char *labs_csv, char *out_json, int max_len);
EXPORT_API int c_analyze_reachability_fast(const char *ip_a, int cidr_a, const char *ip_b, int cidr_b, char *out_json, int max_len);

#ifdef __cplusplus
}
#endif

#endif /* C_BACKEND_H */
