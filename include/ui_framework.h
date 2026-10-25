#ifndef UI_FRAMEWORK_H
#define UI_FRAMEWORK_H

#include "common.h"
#include "ip_calc.h"
#include "vlsm_engine.h"
#include "flsm_engine.h"

void ui_init(void);
void ui_clear_screen(void);
void ui_draw_banner(void);
void ui_draw_header(const char *title, const char *subtitle);
void ui_draw_divider(int width);
void ui_press_any_key(void);

/* Input Prompts */
bool ui_read_line(const char *prompt, char *buf, size_t maxlen);
int ui_read_int(const char *prompt, int min_val, int max_val, int default_val);
bool ui_read_ipv4_prompt(const char *prompt, ipv4_t *out_ip);
int ui_read_cidr_prompt(const char *prompt, int min_cidr, int max_cidr, int default_cidr);

/* Complex Presentation Views */
void ui_render_single_ip_dashboard(const ip_info_t *info);
void ui_render_vlsm_table(const campus_vlsm_t *campus);
void ui_render_flsm_table(const flsm_plan_t *plan);
void ui_render_reference_sheet(void);

#endif /* UI_FRAMEWORK_H */
