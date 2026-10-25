#define _WIN32_WINNT 0x0600
#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <windows.h>
#include <commctrl.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "ip_calc.h"
#include "vlsm_engine.h"
#include "cisco_export.h"
#include "reachability.h"

#pragma comment(lib, "comctl32.lib")
#pragma comment(lib, "user32.lib")
#pragma comment(lib, "gdi32.lib")

#define ID_TAB_CONTROL          1001

/* VLSM Tab Controls */
#define ID_EDIT_BASE_IP         1101
#define ID_EDIT_BASE_CIDR       1102
#define ID_EDIT_LAB_NAME        1103
#define ID_EDIT_LAB_DEPT        1104
#define ID_EDIT_LAB_HOSTS       1105
#define ID_EDIT_LAB_GROWTH      1106
#define ID_BTN_ADD_LAB          1107
#define ID_BTN_REMOVE_LAB       1108
#define ID_BTN_CLEAR_ALL        1109
#define ID_BTN_LOAD_PRESET      1110
#define ID_BTN_CALCULATE_VLSM   1111
#define ID_BTN_EXPORT_CISCO     1112
#define ID_BTN_EXPORT_CSV       1113
#define ID_BTN_EXPORT_TXT       1114
#define ID_LIST_VLSM            1115
#define ID_STATIC_METRICS       1116

/* Single Calc Tab Controls */
#define ID_EDIT_CALC_INPUT      1201
#define ID_BTN_CALC_RUN         1202
#define ID_EDIT_CALC_OUTPUT     1203

/* Binary Visualizer Controls */
#define ID_EDIT_BIN_INPUT       1301
#define ID_BTN_BIN_RUN          1302
#define ID_EDIT_BIN_OUTPUT      1303

/* Reachability Controls */
#define ID_EDIT_REACH_A         1401
#define ID_EDIT_REACH_B         1402
#define ID_BTN_REACH_RUN        1403
#define ID_EDIT_REACH_OUTPUT    1404

/* Global State */
static HINSTANCE g_hInstance;
static HWND g_hMainWindow;
static HWND g_hTab;
static HFONT g_hFontNormal;
static HFONT g_hFontBold;
static HFONT g_hFontMono;

static campus_vlsm_t g_campus;
static bool g_has_campus = false;

/* Control Handles for Tab 0: VLSM */
static HWND g_hBaseIp, g_hBaseCidr;
static HWND g_hLabName, g_hLabDept, g_hLabHosts, g_hLabGrowth;
static HWND g_hBtnAddLab, g_hBtnRemoveLab, g_hBtnClearAll, g_hBtnLoadPreset;
static HWND g_hBtnCalculateVlsm, g_hBtnExportCisco, g_hBtnExportCsv, g_hBtnExportTxt;
static HWND g_hListVlsm, g_hStaticMetrics;
static HWND g_hLblBaseIp, g_hLblBaseCidr, g_hLblLabName, g_hLblLabDept, g_hLblLabHosts, g_hLblLabGrowth;
static HWND g_hGrpBase, g_hGrpLab;

/* Control Handles for Tab 1: Single Calc */
static HWND g_hLblCalcInput, g_hCalcInput, g_hBtnCalcRun, g_hCalcOutput;

/* Control Handles for Tab 2: Binary View */
static HWND g_hLblBinInput, g_hBinInput, g_hBtnBinRun, g_hBinOutput;

/* Control Handles for Tab 3: Reachability */
static HWND g_hLblReachA, g_hReachA, g_hLblReachB, g_hReachB, g_hBtnReachRun, g_hReachOutput;

/* Helper: Apply Segoe UI Font */
static void SetControlFont(HWND hWnd, HFONT hFont) {
    SendMessage(hWnd, WM_SETFONT, (WPARAM)hFont, TRUE);
}

/* Helper to refresh the VLSM ListView */
static void RefreshListView(void) {
    ListView_DeleteAllItems(g_hListVlsm);

    if (!g_campus.is_calculated || !g_campus.is_valid) {
        /* If not yet calculated, show current entered labs */
        for (int i = 0; i < g_campus.lab_count; i++) {
            const lab_spec_t *lab = &g_campus.labs[i];
            char buf[64];

            LVITEMA lvi = {0};
            lvi.mask = LVIF_TEXT;
            lvi.iItem = i;
            lvi.iSubItem = 0;
            snprintf(buf, sizeof(buf), "%d", i + 1);
            lvi.pszText = buf;
            ListView_InsertItem(g_hListVlsm, &lvi);

            ListView_SetItemText(g_hListVlsm, i, 1, (LPSTR)lab->name);
            ListView_SetItemText(g_hListVlsm, i, 2, (LPSTR)lab->department);
            snprintf(buf, sizeof(buf), "%d PCs (+%d%%)", lab->workstations, lab->growth_percent);
            ListView_SetItemText(g_hListVlsm, i, 3, buf);
            snprintf(buf, sizeof(buf), "VLAN%d", lab->vlan_id);
            ListView_SetItemText(g_hListVlsm, i, 4, buf);
            ListView_SetItemText(g_hListVlsm, i, 5, "[Click Calculate]");
            ListView_SetItemText(g_hListVlsm, i, 6, "-");
            ListView_SetItemText(g_hListVlsm, i, 7, "-");
            ListView_SetItemText(g_hListVlsm, i, 8, "-");
            ListView_SetItemText(g_hListVlsm, i, 9, "-");
            ListView_SetItemText(g_hListVlsm, i, 10, "-");
        }
        SetWindowTextA(g_hStaticMetrics, "Status: Labs added. Click [ CALCULATE VLSM SUBNET ALLOCATION ] to assign IP addresses.");
        return;
    }

    for (int i = 0; i < g_campus.lab_count; i++) {
        const lab_spec_t *lab = &g_campus.labs[i];
        char buf[64], net[16], mask[16], first[16], last[16], gw[16], range_str[48];

        ipv4_to_str(lab->network_ip, net, sizeof(net));
        ipv4_to_str(lab->subnet_mask, mask, sizeof(mask));
        ipv4_to_str(lab->first_usable, first, sizeof(first));
        ipv4_to_str(lab->last_usable, last, sizeof(last));
        ipv4_to_str(lab->gateway_ip, gw, sizeof(gw));
        snprintf(range_str, sizeof(range_str), "%s -> %s", first, last);

        LVITEMA lvi = {0};
        lvi.mask = LVIF_TEXT;
        lvi.iItem = i;
        lvi.iSubItem = 0;
        snprintf(buf, sizeof(buf), "%d", lab->id);
        lvi.pszText = buf;
        ListView_InsertItem(g_hListVlsm, &lvi);

        ListView_SetItemText(g_hListVlsm, i, 1, (LPSTR)lab->name);
        ListView_SetItemText(g_hListVlsm, i, 2, (LPSTR)lab->department);

        snprintf(buf, sizeof(buf), "%d PCs", lab->workstations);
        ListView_SetItemText(g_hListVlsm, i, 3, buf);

        snprintf(buf, sizeof(buf), "VLAN%d", lab->vlan_id);
        ListView_SetItemText(g_hListVlsm, i, 4, buf);

        snprintf(buf, sizeof(buf), "%s/%d", net, lab->allocated_cidr);
        ListView_SetItemText(g_hListVlsm, i, 5, buf);

        ListView_SetItemText(g_hListVlsm, i, 6, mask);
        ListView_SetItemText(g_hListVlsm, i, 7, range_str);
        ListView_SetItemText(g_hListVlsm, i, 8, gw);

        snprintf(buf, sizeof(buf), "%u hosts", lab->usable_capacity);
        ListView_SetItemText(g_hListVlsm, i, 9, buf);

        snprintf(buf, sizeof(buf), "%.1f%%", lab->efficiency_pct);
        ListView_SetItemText(g_hListVlsm, i, 10, buf);
    }

    char next_free[16];
    ipv4_to_str(g_campus.next_free_subnet, next_free, sizeof(next_free));

    char metric_text[512];
    snprintf(metric_text, sizeof(metric_text),
             "METRICS: Total Workstations: %llu PCs | Block Allocated: %llu IPs | Next Free IP: %s | Free Pool: %llu IPs | Overall Efficiency: %.1f%%",
             (unsigned long long)g_campus.total_requested_hosts,
             (unsigned long long)g_campus.total_allocated_blocks,
             next_free,
             (unsigned long long)g_campus.free_ips_remaining,
             g_campus.overall_efficiency);
    SetWindowTextA(g_hStaticMetrics, metric_text);
}

static void ShowTabControls(int tabIndex) {
    int showVlsm = (tabIndex == 0) ? SW_SHOW : SW_HIDE;
    int showCalc = (tabIndex == 1) ? SW_SHOW : SW_HIDE;
    int showBin  = (tabIndex == 2) ? SW_SHOW : SW_HIDE;
    int showReach= (tabIndex == 3) ? SW_SHOW : SW_HIDE;

    /* VLSM controls */
    ShowWindow(g_hGrpBase, showVlsm);
    ShowWindow(g_hLblBaseIp, showVlsm);
    ShowWindow(g_hBaseIp, showVlsm);
    ShowWindow(g_hLblBaseCidr, showVlsm);
    ShowWindow(g_hBaseCidr, showVlsm);
    ShowWindow(g_hGrpLab, showVlsm);
    ShowWindow(g_hLblLabName, showVlsm);
    ShowWindow(g_hLabName, showVlsm);
    ShowWindow(g_hLblLabDept, showVlsm);
    ShowWindow(g_hLabDept, showVlsm);
    ShowWindow(g_hLblLabHosts, showVlsm);
    ShowWindow(g_hLabHosts, showVlsm);
    ShowWindow(g_hLblLabGrowth, showVlsm);
    ShowWindow(g_hLabGrowth, showVlsm);
    ShowWindow(g_hBtnAddLab, showVlsm);
    ShowWindow(g_hBtnRemoveLab, showVlsm);
    ShowWindow(g_hBtnClearAll, showVlsm);
    ShowWindow(g_hBtnLoadPreset, showVlsm);
    ShowWindow(g_hBtnCalculateVlsm, showVlsm);
    ShowWindow(g_hBtnExportCisco, showVlsm);
    ShowWindow(g_hBtnExportCsv, showVlsm);
    ShowWindow(g_hBtnExportTxt, showVlsm);
    ShowWindow(g_hListVlsm, showVlsm);
    ShowWindow(g_hStaticMetrics, showVlsm);

    /* Calc controls */
    ShowWindow(g_hLblCalcInput, showCalc);
    ShowWindow(g_hCalcInput, showCalc);
    ShowWindow(g_hBtnCalcRun, showCalc);
    ShowWindow(g_hCalcOutput, showCalc);

    /* Binary controls */
    ShowWindow(g_hLblBinInput, showBin);
    ShowWindow(g_hBinInput, showBin);
    ShowWindow(g_hBtnBinRun, showBin);
    ShowWindow(g_hBinOutput, showBin);

    /* Reachability controls */
    ShowWindow(g_hLblReachA, showReach);
    ShowWindow(g_hReachA, showReach);
    ShowWindow(g_hLblReachB, showReach);
    ShowWindow(g_hReachB, showReach);
    ShowWindow(g_hBtnReachRun, showReach);
    ShowWindow(g_hReachOutput, showReach);
}

static void SetupVLSMListView(void) {
    ListView_SetExtendedListViewStyle(g_hListVlsm, LVS_EX_FULLROWSELECT | LVS_EX_GRIDLINES);

    LVCOLUMNA lvc = {0};
    lvc.mask = LVCF_TEXT | LVCF_WIDTH | LVCF_SUBITEM;

    struct {
        const char *name;
        int width;
    } cols[] = {
        {"#", 35},
        {"Lab Name", 190},
        {"Department / Wing", 120},
        {"Workstations", 100},
        {"VLAN", 65},
        {"Subnet Address", 125},
        {"Subnet Mask", 115},
        {"Usable Host Range", 210},
        {"Default Gateway", 115},
        {"Capacity", 90},
        {"Efficiency", 75}
    };

    for (int i = 0; i < 11; i++) {
        lvc.iSubItem = i;
        lvc.pszText = (LPSTR)cols[i].name;
        lvc.cx = cols[i].width;
        ListView_InsertColumn(g_hListVlsm, i, &lvc);
    }
}

static void OnCalculateVLSM(HWND hWnd) {
    char base_ip_str[64], base_cidr_str[32];
    GetWindowTextA(g_hBaseIp, base_ip_str, sizeof(base_ip_str));
    GetWindowTextA(g_hBaseCidr, base_cidr_str, sizeof(base_cidr_str));

    ipv4_t base_ip;
    if (!parse_ipv4(base_ip_str, &base_ip)) {
        MessageBoxA(hWnd, "Invalid Base Network IP Address! Example: 10.50.0.0 or 172.16.0.0", "Validation Error", MB_ICONERROR);
        return;
    }

    int base_cidr = atoi(base_cidr_str);
    if (base_cidr < 8 || base_cidr > 30) {
        MessageBoxA(hWnd, "Base CIDR prefix must be between /8 and /30.", "Validation Error", MB_ICONERROR);
        return;
    }

    if (g_campus.lab_count == 0) {
        MessageBoxA(hWnd, "Please add at least one computer lab or click [Load College Preset].", "No Labs Added", MB_ICONWARNING);
        return;
    }

    /* Reinitialize base specs and keep current labs */
    g_campus.base_cidr = base_cidr;
    g_campus.base_mask = cidr_to_mask(base_cidr);
    g_campus.base_network_ip = base_ip & g_campus.base_mask;
    g_campus.base_broadcast = g_campus.base_network_ip | calculate_wildcard(g_campus.base_mask);
    g_campus.total_campus_capacity = 1ULL << (32 - base_cidr);

    if (campus_vlsm_calculate(&g_campus)) {
        RefreshListView();
        MessageBoxA(hWnd, "VLSM Subnet Allocation Calculated Successfully! Non-overlapping contiguous blocks assigned.", "Calculation Success", MB_ICONINFORMATION);
    } else {
        MessageBoxA(hWnd, g_campus.error_reason, "IP Address Allocation Error", MB_ICONERROR);
    }
}

static void OnAddLab(HWND hWnd) {
    char name[64], dept[64], hosts_str[32], growth_str[32];
    GetWindowTextA(g_hLabName, name, sizeof(name));
    GetWindowTextA(g_hLabDept, dept, sizeof(dept));
    GetWindowTextA(g_hLabHosts, hosts_str, sizeof(hosts_str));
    GetWindowTextA(g_hLabGrowth, growth_str, sizeof(growth_str));

    if (strlen(name) == 0) strncpy(name, "New Computer Lab", sizeof(name) - 1);
    if (strlen(dept) == 0) strncpy(dept, "Main Campus", sizeof(dept) - 1);

    int hosts = atoi(hosts_str);
    if (hosts <= 0) hosts = 30;
    int growth = atoi(growth_str);
    if (growth < 0) growth = 10;

    int vlan = 10 + (g_campus.lab_count * 10);
    campus_vlsm_add_lab(&g_campus, name, dept, hosts, growth, vlan);

    /* Reset input fields */
    char next_lab_name[64];
    snprintf(next_lab_name, sizeof(next_lab_name), "Computer Lab %d", g_campus.lab_count + 1);
    SetWindowTextA(g_hLabName, next_lab_name);
    SetWindowTextA(g_hLabHosts, "60");

    RefreshListView();
}

static void OnRemoveSelectedLab(HWND hWnd) {
    int sel = ListView_GetNextItem(g_hListVlsm, -1, LVNI_SELECTED);
    if (sel >= 0 && sel < g_campus.lab_count) {
        campus_vlsm_remove_lab(&g_campus, sel);
        if (g_campus.lab_count > 0 && g_campus.is_calculated) {
            campus_vlsm_calculate(&g_campus);
        }
        RefreshListView();
    } else {
        MessageBoxA(hWnd, "Please click on a lab in the list to select it for removal.", "Selection Needed", MB_ICONINFORMATION);
    }
}

static void OnLoadPreset(HWND hWnd) {
    (void)hWnd;
    if (g_has_campus) {
        campus_vlsm_free(&g_campus);
    }
    campus_vlsm_load_preset_college(&g_campus);
    g_has_campus = true;

    char base_ip_str[16];
    ipv4_to_str(g_campus.base_network_ip, base_ip_str, sizeof(base_ip_str));
    SetWindowTextA(g_hBaseIp, base_ip_str);
    SetWindowTextA(g_hBaseCidr, "16");

    RefreshListView();
}

static void OnRunSingleCalc(HWND hWnd) {
    (void)hWnd;
    char input[64];
    GetWindowTextA(g_hCalcInput, input, sizeof(input));

    ipv4_t ip;
    int cidr;
    if (!parse_cidr_string(input, &ip, &cidr)) {
        SetWindowTextA(g_hCalcOutput, "Error: Invalid IPv4 CIDR string! Example: 192.168.10.75/26 or 10.0.0.1/16");
        return;
    }

    ip_info_t info;
    calculate_ip_info(ip, cidr, &info);

    char out[2048];
    snprintf(out, sizeof(out),
             "=====================================================================\r\n"
             "                 IPv4 ADDRESS & SUBNET DECOMPOSITION                 \r\n"
             "=====================================================================\r\n\r\n"
             "  * Input IP / CIDR     : %s / %d\r\n"
             "  * Subnet Mask         : %s\r\n"
             "  * Wildcard Mask       : %s\r\n"
             "  * Network Address     : %s\r\n"
             "  * Directed Broadcast  : %s\r\n"
             "  * Usable Host Range   : %s  ->  %s\r\n"
             "  * Total Addresses     : %llu\r\n"
             "  * Usable Host Count   : %llu Workstations\r\n"
             "  * Class               : %s\r\n"
             "  * Scope               : %s\r\n\r\n"
             "=====================================================================\r\n"
             "  Default Gateway Recommended : %s\r\n"
             "  Local Broadcast Address     : 255.255.255.255\r\n"
             "=====================================================================\r\n",
             info.ip_str, info.cidr, info.mask_str, info.wildcard_str,
             info.network_str, info.broadcast_str, info.first_usable_str, info.last_usable_str,
             (unsigned long long)info.total_ips, (unsigned long long)info.usable_hosts,
             class_to_string(info.ip_class), scope_to_string(info.scope),
             info.first_usable_str);

    SetWindowTextA(g_hCalcOutput, out);
}

static void OnRunBinaryVisualizer(HWND hWnd) {
    (void)hWnd;
    char input[64];
    GetWindowTextA(g_hBinInput, input, sizeof(input));

    ipv4_t ip;
    int cidr;
    if (!parse_cidr_string(input, &ip, &cidr)) {
        SetWindowTextA(g_hBinOutput, "Error: Invalid IPv4 CIDR string! Example: 172.16.50.100/22");
        return;
    }

    ipv4_t mask = cidr_to_mask(cidr);
    ipv4_t wildcard = calculate_wildcard(mask);
    ipv4_t net = ip & mask;
    ipv4_t bcast = net | wildcard;

    char ip_bin[40], mask_bin[40], net_bin[40], bcast_bin[40];
    ip_to_binary_str(ip, ip_bin, sizeof(ip_bin));
    ip_to_binary_str(mask, mask_bin, sizeof(mask_bin));
    ip_to_binary_str(net, net_bin, sizeof(net_bin));
    ip_to_binary_str(bcast, bcast_bin, sizeof(bcast_bin));

    char ip_str[16], mask_str[16], net_str[16], bcast_str[16];
    ipv4_to_str(ip, ip_str, sizeof(ip_str));
    ipv4_to_str(mask, mask_str, sizeof(mask_str));
    ipv4_to_str(net, net_str, sizeof(net_str));
    ipv4_to_str(bcast, bcast_str, sizeof(bcast_str));

    char out[2048];
    snprintf(out, sizeof(out),
             "========================================================================================\r\n"
             "                      32-BIT BINARY LOGICAL DECOMPOSITION & BIT SPLIT                   \r\n"
             "========================================================================================\r\n\r\n"
             "  IP Address   :  %s    (%s)\r\n"
             "  Subnet Mask  :  %s    (%s)\r\n"
             "                  -----------------------------------    (Bitwise AND : IP & MASK)\r\n"
             "  Network ID   :  %s    (%s)\r\n"
             "  Broadcast ID :  %s    (%s)\r\n\r\n"
             "----------------------------------------------------------------------------------------\r\n"
             "  BIT BOUNDARY DIVISION:\r\n"
             "    * Network Bits     : %d bits (Contiguous '1's in subnet mask)\r\n"
             "    * Host Bits        : %d bits (Zeroes available for endpoint addressing)\r\n"
             "    * Total Subnet IPs : 2^%d = %llu addresses\r\n"
             "    * Usable PCs       : 2^%d - 2 = %llu workstations\r\n"
             "========================================================================================\r\n",
             ip_bin, ip_str, mask_bin, mask_str,
             net_bin, net_str, bcast_bin, bcast_str,
             cidr, 32 - cidr,
             32 - cidr, 1ULL << (32 - cidr),
             32 - cidr, (1ULL << (32 - cidr)) - 2);

    SetWindowTextA(g_hBinOutput, out);
}

static void OnRunReachability(HWND hWnd) {
    (void)hWnd;
    char str_a[64], str_b[64];
    GetWindowTextA(g_hReachA, str_a, sizeof(str_a));
    GetWindowTextA(g_hReachB, str_b, sizeof(str_b));

    ipv4_t ip_a, ip_b;
    int cidr_a, cidr_b;

    if (!parse_cidr_string(str_a, &ip_a, &cidr_a) || !parse_cidr_string(str_b, &ip_b, &cidr_b)) {
        SetWindowTextA(g_hReachOutput, "Error: Invalid IP/CIDR in Endpoint A or Endpoint B.");
        return;
    }

    reachability_result_t res;
    analyze_reachability(ip_a, cidr_a, ip_b, cidr_b, &res);

    char out[2048];
    const char *status_str = (res.status == REACH_SAME_SUBNET_L2) ? "DIRECT LAYER-2 SWITCHING POSSIBLE (Same Subnet)" :
                             (res.status == REACH_DIFFERENT_SUBNET_L3) ? "LAYER-3 ROUTING REQUIRED (Inter-VLAN Gateway)" :
                             (res.status == REACH_ASYMMETRIC_MASK_ERROR) ? "CRITICAL ERROR: ASYMMETRIC MASK MISCONFIGURATION" :
                             "INVALID ENDPOINT IDENTIFIER";

    snprintf(out, sizeof(out),
             "========================================================================================\r\n"
             "                     INTER-HOST REACHABILITY & ROUTING DIAGNOSTIC                       \r\n"
             "========================================================================================\r\n\r\n"
             "  STATUS: [%s]\r\n\r\n"
             "  TECHNICAL ANALYSIS:\r\n"
             "    %s\r\n\r\n"
             "  ENGINEERING RECOMMENDATION:\r\n"
             "    %s\r\n\r\n"
             "========================================================================================\r\n",
             status_str, res.diagnosis, res.recommendation);

    SetWindowTextA(g_hReachOutput, out);
}

/* Window Procedure */
LRESULT CALLBACK WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch (msg) {
        case WM_CREATE: {

            g_hFontNormal = CreateFontA(15, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                                        DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                                        CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE, "Segoe UI");
            g_hFontBold = CreateFontA(15, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
                                      DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                                      CLEARTYPE_QUALITY, DEFAULT_PITCH | FF_DONTCARE, "Segoe UI");
            g_hFontMono = CreateFontA(14, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
                                      DEFAULT_CHARSET, OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS,
                                      CLEARTYPE_QUALITY, FIXED_PITCH | FF_MODERN, "Consolas");

            /* Create Main Tab Control */
            g_hTab = CreateWindowExA(0, WC_TABCONTROLA, "",
                                     WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS,
                                     10, 10, 1160, 680, hWnd, (HMENU)ID_TAB_CONTROL, g_hInstance, NULL);
            SetControlFont(g_hTab, g_hFontBold);

            TCITEMA tie = {0};
            tie.mask = TCIF_TEXT;
            tie.pszText = "  Campus VLSM Lab Planner  ";
            TabCtrl_InsertItem(g_hTab, 0, &tie);
            tie.pszText = "  Single Subnet Calculator  ";
            TabCtrl_InsertItem(g_hTab, 1, &tie);
            tie.pszText = "  32-Bit Binary Visualizer  ";
            TabCtrl_InsertItem(g_hTab, 2, &tie);
            tie.pszText = "  Inter-Host Reachability & Routing  ";
            TabCtrl_InsertItem(g_hTab, 3, &tie);

            /* ========================================================== */
            /* TAB 0: Campus VLSM Controls                                */
            /* ========================================================== */
            g_hGrpBase = CreateWindowExA(0, "BUTTON", " 1. Base Campus Network ",
                                         WS_CHILD | WS_VISIBLE | BS_GROUPBOX,
                                         25, 45, 1130, 65, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hGrpBase, g_hFontBold);

            g_hLblBaseIp = CreateWindowExA(0, "STATIC", "Base Network IP:", WS_CHILD | WS_VISIBLE,
                                           45, 72, 110, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblBaseIp, g_hFontNormal);

            g_hBaseIp = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "10.50.0.0",
                                        WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                        160, 70, 140, 24, hWnd, (HMENU)ID_EDIT_BASE_IP, g_hInstance, NULL);
            SetControlFont(g_hBaseIp, g_hFontNormal);

            g_hLblBaseCidr = CreateWindowExA(0, "STATIC", "CIDR Prefix / :", WS_CHILD | WS_VISIBLE,
                                             320, 72, 95, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblBaseCidr, g_hFontNormal);

            g_hBaseCidr = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "16",
                                          WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                          420, 70, 60, 24, hWnd, (HMENU)ID_EDIT_BASE_CIDR, g_hInstance, NULL);
            SetControlFont(g_hBaseCidr, g_hFontNormal);

            g_hBtnLoadPreset = CreateWindowExA(0, "BUTTON", "Load College Preset (8 Realistic Labs)",
                                               WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                               510, 68, 250, 28, hWnd, (HMENU)ID_BTN_LOAD_PRESET, g_hInstance, NULL);
            SetControlFont(g_hBtnLoadPreset, g_hFontBold);

            g_hBtnClearAll = CreateWindowExA(0, "BUTTON", "Clear All Labs",
                                             WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                             775, 68, 120, 28, hWnd, (HMENU)ID_BTN_CLEAR_ALL, g_hInstance, NULL);
            SetControlFont(g_hBtnClearAll, g_hFontNormal);

            /* Group 2: Add Lab Box */
            g_hGrpLab = CreateWindowExA(0, "BUTTON", " 2. Add Computer Lab Workstation Requirements ",
                                        WS_CHILD | WS_VISIBLE | BS_GROUPBOX,
                                        25, 115, 1130, 75, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hGrpLab, g_hFontBold);

            g_hLblLabName = CreateWindowExA(0, "STATIC", "Lab Name:", WS_CHILD | WS_VISIBLE,
                                            45, 145, 75, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblLabName, g_hFontNormal);

            g_hLabName = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "Cyber Security & Forensics Lab",
                                         WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                         125, 142, 220, 24, hWnd, (HMENU)ID_EDIT_LAB_NAME, g_hInstance, NULL);
            SetControlFont(g_hLabName, g_hFontNormal);

            g_hLblLabDept = CreateWindowExA(0, "STATIC", "Dept / Wing:", WS_CHILD | WS_VISIBLE,
                                            360, 145, 80, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblLabDept, g_hFontNormal);

            g_hLabDept = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "IT Dept Block B",
                                         WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                         445, 142, 140, 24, hWnd, (HMENU)ID_EDIT_LAB_DEPT, g_hInstance, NULL);
            SetControlFont(g_hLabDept, g_hFontNormal);

            g_hLblLabHosts = CreateWindowExA(0, "STATIC", "Workstation PCs:", WS_CHILD | WS_VISIBLE,
                                             600, 145, 105, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblLabHosts, g_hFontNormal);

            g_hLabHosts = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "65",
                                          WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                          710, 142, 60, 24, hWnd, (HMENU)ID_EDIT_LAB_HOSTS, g_hInstance, NULL);
            SetControlFont(g_hLabHosts, g_hFontNormal);

            g_hLblLabGrowth = CreateWindowExA(0, "STATIC", "Buffer %:", WS_CHILD | WS_VISIBLE,
                                              785, 145, 60, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblLabGrowth, g_hFontNormal);

            g_hLabGrowth = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "10",
                                           WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL,
                                           850, 142, 45, 24, hWnd, (HMENU)ID_EDIT_LAB_GROWTH, g_hInstance, NULL);
            SetControlFont(g_hLabGrowth, g_hFontNormal);

            g_hBtnAddLab = CreateWindowExA(0, "BUTTON", "+ Add Lab",
                                           WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
                                           910, 140, 100, 28, hWnd, (HMENU)ID_BTN_ADD_LAB, g_hInstance, NULL);
            SetControlFont(g_hBtnAddLab, g_hFontBold);

            g_hBtnRemoveLab = CreateWindowExA(0, "BUTTON", "- Delete Lab",
                                              WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                              1020, 140, 110, 28, hWnd, (HMENU)ID_BTN_REMOVE_LAB, g_hInstance, NULL);
            SetControlFont(g_hBtnRemoveLab, g_hFontNormal);

            /* Action Buttons */
            g_hBtnCalculateVlsm = CreateWindowExA(0, "BUTTON", "CALCULATE VLSM ALLOCATION",
                                                  WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON,
                                                  25, 200, 310, 34, hWnd, (HMENU)ID_BTN_CALCULATE_VLSM, g_hInstance, NULL);
            SetControlFont(g_hBtnCalculateVlsm, g_hFontBold);

            g_hBtnExportCisco = CreateWindowExA(0, "BUTTON", "Export Cisco IOS Config (.cfg)",
                                                WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                                350, 200, 240, 34, hWnd, (HMENU)ID_BTN_EXPORT_CISCO, g_hInstance, NULL);
            SetControlFont(g_hBtnExportCisco, g_hFontBold);

            g_hBtnExportCsv = CreateWindowExA(0, "BUTTON", "Export Excel Spreadsheet (.csv)",
                                              WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                              605, 200, 240, 34, hWnd, (HMENU)ID_BTN_EXPORT_CSV, g_hInstance, NULL);
            SetControlFont(g_hBtnExportCsv, g_hFontBold);

            g_hBtnExportTxt = CreateWindowExA(0, "BUTTON", "Export Documentation Report (.txt)",
                                              WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
                                              860, 200, 290, 34, hWnd, (HMENU)ID_BTN_EXPORT_TXT, g_hInstance, NULL);
            SetControlFont(g_hBtnExportTxt, g_hFontBold);

            /* VLSM List View Table */
            g_hListVlsm = CreateWindowExA(WS_EX_CLIENTEDGE, WC_LISTVIEWA, "",
                                          WS_CHILD | WS_VISIBLE | LVS_REPORT | LVS_SINGLESEL | WS_BORDER | WS_VSCROLL,
                                          25, 245, 1130, 385, hWnd, (HMENU)ID_LIST_VLSM, g_hInstance, NULL);
            SetControlFont(g_hListVlsm, g_hFontNormal);
            SetupVLSMListView();

            /* Metrics Bar */
            g_hStaticMetrics = CreateWindowExA(0, "STATIC",
                                               "Status: Ready. Load a campus or add labs, then click Calculate.",
                                               WS_CHILD | WS_VISIBLE,
                                               25, 640, 1130, 25, hWnd, (HMENU)ID_STATIC_METRICS, g_hInstance, NULL);
            SetControlFont(g_hStaticMetrics, g_hFontBold);

            /* ========================================================== */
            /* TAB 1: Single Subnet Calculator Controls                   */
            /* ========================================================== */
            g_hLblCalcInput = CreateWindowExA(0, "STATIC", "Enter IPv4 Address & Prefix Length (e.g., 192.168.10.75/26):",
                                              WS_CHILD, 45, 60, 480, 22, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblCalcInput, g_hFontBold);

            g_hCalcInput = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "192.168.10.75/26",
                                           WS_CHILD | ES_AUTOHSCROLL,
                                           45, 90, 320, 28, hWnd, (HMENU)ID_EDIT_CALC_INPUT, g_hInstance, NULL);
            SetControlFont(g_hCalcInput, g_hFontNormal);

            g_hBtnCalcRun = CreateWindowExA(0, "BUTTON", "Inspect Address",
                                            WS_CHILD | BS_DEFPUSHBUTTON,
                                            380, 88, 160, 30, hWnd, (HMENU)ID_BTN_CALC_RUN, g_hInstance, NULL);
            SetControlFont(g_hBtnCalcRun, g_hFontBold);

            g_hCalcOutput = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "",
                                            WS_CHILD | ES_MULTILINE | ES_READONLY | WS_VSCROLL,
                                            45, 135, 1090, 520, hWnd, (HMENU)ID_EDIT_CALC_OUTPUT, g_hInstance, NULL);
            SetControlFont(g_hCalcOutput, g_hFontMono);

            /* ========================================================== */
            /* TAB 2: 32-Bit Binary Visualizer Controls                   */
            /* ========================================================== */
            g_hLblBinInput = CreateWindowExA(0, "STATIC", "Enter IP and CIDR prefix for 32-bit decomposition (e.g. 172.16.50.100/22):",
                                             WS_CHILD, 45, 60, 560, 22, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblBinInput, g_hFontBold);

            g_hBinInput = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "172.16.50.100/22",
                                          WS_CHILD | ES_AUTOHSCROLL,
                                          45, 90, 320, 28, hWnd, (HMENU)ID_EDIT_BIN_INPUT, g_hInstance, NULL);
            SetControlFont(g_hBinInput, g_hFontNormal);

            g_hBtnBinRun = CreateWindowExA(0, "BUTTON", "Decompose 32-Bits",
                                           WS_CHILD | BS_DEFPUSHBUTTON,
                                           380, 88, 160, 30, hWnd, (HMENU)ID_BTN_BIN_RUN, g_hInstance, NULL);
            SetControlFont(g_hBtnBinRun, g_hFontBold);

            g_hBinOutput = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "",
                                           WS_CHILD | ES_MULTILINE | ES_READONLY | WS_VSCROLL,
                                           45, 135, 1090, 520, hWnd, (HMENU)ID_EDIT_BIN_OUTPUT, g_hInstance, NULL);
            SetControlFont(g_hBinOutput, g_hFontMono);

            /* ========================================================== */
            /* TAB 3: Reachability Controls                               */
            /* ========================================================== */
            g_hLblReachA = CreateWindowExA(0, "STATIC", "Endpoint A (IP / CIDR):",
                                           WS_CHILD, 45, 65, 180, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblReachA, g_hFontBold);

            g_hReachA = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "192.168.1.50/24",
                                        WS_CHILD | ES_AUTOHSCROLL,
                                        230, 62, 220, 26, hWnd, (HMENU)ID_EDIT_REACH_A, g_hInstance, NULL);
            SetControlFont(g_hReachA, g_hFontNormal);

            g_hLblReachB = CreateWindowExA(0, "STATIC", "Endpoint B (IP / CIDR):",
                                           WS_CHILD, 480, 65, 180, 20, hWnd, NULL, g_hInstance, NULL);
            SetControlFont(g_hLblReachB, g_hFontBold);

            g_hReachB = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "192.168.2.100/24",
                                        WS_CHILD | ES_AUTOHSCROLL,
                                        665, 62, 220, 26, hWnd, (HMENU)ID_EDIT_REACH_B, g_hInstance, NULL);
            SetControlFont(g_hReachB, g_hFontNormal);

            g_hBtnReachRun = CreateWindowExA(0, "BUTTON", "Analyze Route",
                                             WS_CHILD | BS_DEFPUSHBUTTON,
                                             910, 60, 160, 30, hWnd, (HMENU)ID_BTN_REACH_RUN, g_hInstance, NULL);
            SetControlFont(g_hBtnReachRun, g_hFontBold);

            g_hReachOutput = CreateWindowExA(WS_EX_CLIENTEDGE, "EDIT", "",
                                             WS_CHILD | ES_MULTILINE | ES_READONLY | WS_VSCROLL,
                                             45, 110, 1090, 545, hWnd, (HMENU)ID_EDIT_REACH_OUTPUT, g_hInstance, NULL);
            SetControlFont(g_hReachOutput, g_hFontMono);

            /* Auto-load preset on start */
            OnLoadPreset(hWnd);

            /* Ensure Tab 0 is shown initially */
            ShowTabControls(0);
            break;
        }

        case WM_NOTIFY: {
            NMHDR *pnm = (NMHDR *)lParam;
            if (pnm->idFrom == ID_TAB_CONTROL && pnm->code == TCN_SELCHANGE) {
                int sel = TabCtrl_GetCurSel(g_hTab);
                ShowTabControls(sel);
                if (sel == 1) OnRunSingleCalc(hWnd);
                if (sel == 2) OnRunBinaryVisualizer(hWnd);
                if (sel == 3) OnRunReachability(hWnd);
            }
            break;
        }

        case WM_COMMAND: {
            int wmId = LOWORD(wParam);
            switch (wmId) {
                case ID_BTN_ADD_LAB:
                    OnAddLab(hWnd);
                    break;
                case ID_BTN_REMOVE_LAB:
                    OnRemoveSelectedLab(hWnd);
                    break;
                case ID_BTN_CLEAR_ALL:
                    campus_vlsm_clear_labs(&g_campus);
                    RefreshListView();
                    break;
                case ID_BTN_LOAD_PRESET:
                    OnLoadPreset(hWnd);
                    break;
                case ID_BTN_CALCULATE_VLSM:
                    OnCalculateVLSM(hWnd);
                    break;
                case ID_BTN_EXPORT_CISCO: {
                    if (!g_campus.is_valid) {
                        MessageBoxA(hWnd, "Please calculate the VLSM plan first!", "Notice", MB_ICONWARNING);
                        break;
                    }
                    if (export_cisco_ios_config(&g_campus, "reports/campus_cisco.cfg")) {
                        MessageBoxA(hWnd, "Cisco IOS Switch/Router script saved to:\nreports/campus_cisco.cfg\n\nReady for Cisco Packet Tracer!", "Export Success", MB_ICONINFORMATION);
                    }
                    break;
                }
                case ID_BTN_EXPORT_CSV: {
                    if (!g_campus.is_valid) {
                        MessageBoxA(hWnd, "Please calculate the VLSM plan first!", "Notice", MB_ICONWARNING);
                        break;
                    }
                    if (export_csv_report(&g_campus, "reports/campus_subnets.csv")) {
                        MessageBoxA(hWnd, "CSV Spreadsheet saved to:\nreports/campus_subnets.csv\n\nReady to open in Microsoft Excel or Google Sheets!", "Export Success", MB_ICONINFORMATION);
                    }
                    break;
                }
                case ID_BTN_EXPORT_TXT: {
                    if (!g_campus.is_valid) {
                        MessageBoxA(hWnd, "Please calculate the VLSM plan first!", "Notice", MB_ICONWARNING);
                        break;
                    }
                    if (export_summary_text_report(&g_campus, "reports/campus_report.txt")) {
                        MessageBoxA(hWnd, "Technical Report saved to:\nreports/campus_report.txt", "Export Success", MB_ICONINFORMATION);
                    }
                    break;
                }
                case ID_BTN_CALC_RUN:
                    OnRunSingleCalc(hWnd);
                    break;
                case ID_BTN_BIN_RUN:
                    OnRunBinaryVisualizer(hWnd);
                    break;
                case ID_BTN_REACH_RUN:
                    OnRunReachability(hWnd);
                    break;
            }
            break;
        }

        case WM_DESTROY:
            if (g_has_campus) {
                campus_vlsm_free(&g_campus);
            }
            if (g_hFontNormal) DeleteObject(g_hFontNormal);
            if (g_hFontBold) DeleteObject(g_hFontBold);
            if (g_hFontMono) DeleteObject(g_hFontMono);
            PostQuitMessage(0);
            break;

        default:
            return DefWindowProcA(hWnd, msg, wParam, lParam);
    }
    return 0;
}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
    (void)hPrevInstance; (void)lpCmdLine;
    g_hInstance = hInstance;

    INITCOMMONCONTROLSEX icex;
    icex.dwSize = sizeof(INITCOMMONCONTROLSEX);
    icex.dwICC = ICC_TAB_CLASSES | ICC_LISTVIEW_CLASSES | ICC_STANDARD_CLASSES;
    InitCommonControlsEx(&icex);

    WNDCLASSEXA wc = {0};
    wc.cbSize = sizeof(WNDCLASSEXA);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = WndProc;
    wc.hInstance = hInstance;
    wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE + 1);
    wc.lpszClassName = "NetLabPro_GUI_Class";

    if (!RegisterClassExA(&wc)) {
        MessageBoxA(NULL, "Window Registration Failed!", "Error", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    g_hMainWindow = CreateWindowExA(
        0,
        "NetLabPro_GUI_Class",
        "NetLab-Pro :: Campus Network Subnet Architect & VLSM Lab Suite [GUI Edition]",
        WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX,
        CW_USEDEFAULT, CW_USEDEFAULT, 1200, 740,
        NULL, NULL, hInstance, NULL
    );

    if (!g_hMainWindow) {
        MessageBoxA(NULL, "Window Creation Failed!", "Error", MB_ICONEXCLAMATION | MB_OK);
        return 0;
    }

    int showMode = (nCmdShow <= 0 || nCmdShow == SW_HIDE) ? SW_SHOWNORMAL : nCmdShow;
    ShowWindow(g_hMainWindow, showMode);
    UpdateWindow(g_hMainWindow);

    MSG msg;
    while (GetMessageA(&msg, NULL, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageA(&msg);
    }

    return (int)msg.wParam;
}
