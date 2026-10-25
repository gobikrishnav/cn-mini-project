#ifndef CISCO_EXPORT_H
#define CISCO_EXPORT_H

#include "common.h"
#include "vlsm_engine.h"

bool export_cisco_ios_config(const campus_vlsm_t *campus, const char *filepath);
bool export_csv_report(const campus_vlsm_t *campus, const char *filepath);
bool export_summary_text_report(const campus_vlsm_t *campus, const char *filepath);

#endif /* CISCO_EXPORT_H */
