"""
NetLab-Pro: Modern Desktop Application (Dynamic GUI)
Campus Network Subnet Architect & Dynamic VLSM Suite
Designed with Clean White Sidebar Dashboard Layout,
Real-Time Dynamic Recalculation, and User-Driven Input Configuration.
"""

import os
import sys
import math
import tkinter as tk
from tkinter import ttk, messagebox

# Enable High-DPI awareness on Windows if available
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import netlab_engine as engine

# =============================================================================
# COLOR PALETTE (Clean White SaaS Dashboard Design)
# =============================================================================
BG_CANVAS = "#f1f5f9"      # Slate 100 soft canvas
BG_CARD = "#ffffff"        # Pure White Card
BG_SIDEBAR = "#ffffff"     # Pure White Sidebar
BG_INPUT = "#f8fafc"       # Soft input canvas
BORDER_COLOR = "#e2e8f0"   # Light subtle border
BORDER_ACTIVE = "#3b82f6"  # Active focus border

TEXT_MAIN = "#0f172a"      # Slate 900
TEXT_MUTED = "#64748b"     # Slate 500
TEXT_DIM = "#94a3b8"       # Slate 400

COLOR_BLUE = "#2563eb"     # Royal Blue (Primary active)
COLOR_BLUE_HOVER = "#1d4ed8"
COLOR_BLUE_SOFT = "#eff6ff"
COLOR_GREEN = "#00c076"    # Vibrant Mint / Emerald Green for numbers
COLOR_GREEN_SOFT = "#e6f9f1"
COLOR_ROSE = "#ef4444"     # Rose red
COLOR_AMBER = "#f59e0b"    # Warning amber
COLOR_INDIGO = "#6366f1"   # Indigo

FONT_TITLE = ("Segoe UI", 13, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_MAIN = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI", 9, "bold")
FONT_SMALL = ("Segoe UI", 8)
FONT_SMALL_BOLD = ("Segoe UI", 8, "bold")
FONT_MONO = ("Consolas", 9)
FONT_MONO_BOLD = ("Consolas", 9, "bold")
FONT_NUM_BIG = ("Segoe UI", 18, "bold")


class NetLabDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NetLab-Pro :: Campus Network Subnet Architect & Dynamic VLSM Suite")
        
        # Auto-fit window to screen dimensions
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        win_w = min(1240, max(960, screen_w - 30))
        win_h = min(740, max(580, screen_h - 60))
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(960, 560)
        self.configure(bg=BG_CANVAS)

        # Core Engine Instance (User-driven, starts clean)
        self.campus = engine.CampusVLSM("192.168.0.0", 24)

        # TTK Style Config
        self._setup_ttk_styles()

        # Layout containers
        self.active_page = "vlsm"
        self.nav_buttons = {}
        self.page_frames = {}

        self._build_main_layout()

        # Initial UI render
        self._refresh_all_ui()
        self.show_page("vlsm")

        # Automatically open input wizard for user to specify labs if empty
        self.after(250, self._check_first_run_input)

    def _check_first_run_input(self):
        if not self.campus.labs:
            self._cmd_configure_n_labs_dialog(default_n=8)

    def _setup_ttk_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Treeview styling (Clean white table with soft headers)
        style.configure("Treeview",
                        background="#ffffff",
                        foreground=TEXT_MAIN,
                        fieldbackground="#ffffff",
                        rowheight=28,
                        font=FONT_MONO,
                        borderwidth=1,
                        relief="flat")
        style.configure("Treeview.Heading",
                        background="#f8fafc",
                        foreground=TEXT_MUTED,
                        font=FONT_BOLD,
                        padding=[8, 6],
                        borderwidth=1,
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", "#dbeafe")],
                  foreground=[("selected", "#1e3a8a")])
        style.map("Treeview.Heading",
                  background=[("active", "#f1f5f9")])

        # Combobox
        style.configure("TCombobox", fieldbackground="#f8fafc", background="#ffffff",
                        foreground=TEXT_MAIN, arrowcolor=COLOR_BLUE)
        style.map("TCombobox", fieldbackground=[("readonly", "#f8fafc")])

        # Scrollbars
        style.configure("Vertical.TScrollbar", background="#cbd5e1", troughcolor=BG_CANVAS, borderwidth=0)
        style.configure("Horizontal.TScrollbar", background="#cbd5e1", troughcolor=BG_CANVAS, borderwidth=0)

    def _build_main_layout(self):
        # 1. Left Sidebar (Fixed 220px)
        self.sidebar = tk.Frame(self, bg=BG_SIDEBAR, width=224, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 2. Right Body Container
        self.right_container = tk.Frame(self, bg=BG_CANVAS)
        self.right_container.pack(side="right", fill="both", expand=True)

        # Build Sidebar
        self._build_sidebar_contents()

        # Build Top Header (Clean, zero export buttons)
        self._build_top_header()

        # Build Main Content Area for Pages
        self.main_content = tk.Frame(self.right_container, bg=BG_CANVAS, padx=20, pady=16)
        self.main_content.pack(fill="both", expand=True)

        # Instantiate Essential Pages Only
        self._build_page_vlsm()
        self._build_page_inventory()
        self._build_page_supernetting()

        # Build Bottom Status Bar
        self._build_status_bar()

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    def _build_sidebar_contents(self):
        # Top Brand Logo
        brand_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR, height=64, padx=16)
        brand_frame.pack(fill="x", side="top")
        brand_frame.pack_propagate(False)

        logo_icon = tk.Label(brand_frame, text="NL", bg=COLOR_ROSE, fg="#ffffff",
                             font=("Segoe UI", 10, "bold"), width=3, height=1, relief="flat")
        logo_icon.pack(side="left", padx=(0, 8), pady=16)

        title_box = tk.Frame(brand_frame, bg=BG_SIDEBAR)
        title_box.pack(side="left", pady=16)

        lbl_b1 = tk.Label(title_box, text="NetLab", bg=BG_SIDEBAR, fg=TEXT_MAIN, font=("Segoe UI", 12, "bold"))
        lbl_b1.pack(side="left")
        lbl_b2 = tk.Label(title_box, text=".pro", bg=BG_SIDEBAR, fg=COLOR_BLUE, font=("Segoe UI", 12, "bold"))
        lbl_b2.pack(side="left")

        # Divider
        tk.Frame(self.sidebar, bg=BORDER_COLOR, height=1).pack(fill="x", side="top")

        # Navigation Menu
        nav_container = tk.Frame(self.sidebar, bg=BG_SIDEBAR, padx=12, pady=16)
        nav_container.pack(fill="both", expand=True, side="top")

        lbl_section = tk.Label(nav_container, text="PAGES", bg=BG_SIDEBAR, fg=TEXT_DIM,
                               font=("Segoe UI", 8, "bold"))
        lbl_section.pack(anchor="w", padx=4, pady=(0, 8))

        nav_items = [
            ("vlsm", "🏢  Subnet Matrix"),
            ("inventory", "🖥️  Workstations"),
            ("supernetting", "🌐  Supernetting / CIDR")
        ]

        for key, text in nav_items:
            btn = tk.Button(nav_container, text=text, anchor="w", padx=12, pady=8,
                            font=FONT_BOLD, relief="flat", bd=0, cursor="hand2",
                            command=lambda k=key: self.show_page(k))
            btn.pack(fill="x", pady=3)
            self.nav_buttons[key] = btn

        # Bottom Active Engine Status Box
        bottom_box = tk.Frame(self.sidebar, bg="#f8fafc", padx=12, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        bottom_box.pack(fill="x", side="bottom", padx=8, pady=8)

        lbl_status_icon = tk.Label(bottom_box, text="● VLSM Engine Ready", bg="#f8fafc", fg=COLOR_GREEN,
                                   font=("Segoe UI", 8, "bold"))
        lbl_status_icon.pack(anchor="w")

        lbl_status_desc = tk.Label(bottom_box, text="User-Driven Input Mode", bg="#f8fafc", fg=TEXT_MUTED,
                                   font=FONT_SMALL)
        lbl_status_desc.pack(anchor="w", pady=(2, 0))

    def show_page(self, page_key):
        self.active_page = page_key

        # Update button visual states
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.configure(bg=COLOR_BLUE, fg="#ffffff", activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff")
            else:
                btn.configure(bg=BG_SIDEBAR, fg=TEXT_MUTED, activebackground="#f1f5f9", activeforeground=TEXT_MAIN)

        # Show selected frame, hide others
        for key, frame in self.page_frames.items():
            if key == page_key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        # Update header subtitle
        subtitles = {
            "vlsm": "Dynamic Campus VLSM Planning & Subnet Allocation",
            "inventory": "Deterministic Workstation IP Allocation & DHCP Scopes",
            "supernetting": "CIDR Route Summarization & Multi-Subnet Aggregation Engine"
        }
        self.lbl_page_subtitle.configure(text=subtitles.get(page_key, "Campus Network Subnet Architect"))

    # =========================================================================
    # TOP HEADER (Clean, zero export buttons)
    # =========================================================================
    def _build_top_header(self):
        header_frame = tk.Frame(self.right_container, bg=BG_CARD, height=64, padx=20,
                                highlightbackground=BORDER_COLOR, highlightthickness=1)
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)

        # Title & Subtitle on left
        left_box = tk.Frame(header_frame, bg=BG_CARD)
        left_box.pack(side="left", fill="y", pady=10)

        lbl_title = tk.Label(left_box, text="Subnet Architect", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE)
        lbl_title.pack(anchor="w")

        self.lbl_page_subtitle = tk.Label(left_box, text="Dynamic Campus VLSM Planning & Subnet Allocation",
                                          bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL)
        self.lbl_page_subtitle.pack(anchor="w")

        # Action Buttons on right (User-driven actions only, zero file generation buttons)
        right_box = tk.Frame(header_frame, bg=BG_CARD)
        right_box.pack(side="right", fill="y", pady=12)

        btn_input_labs = tk.Button(right_box, text="📝 Input Lab Details...", bg=COLOR_BLUE, fg="#ffffff",
                                   activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                                   font=FONT_BOLD, relief="flat", padx=12, pady=4, cursor="hand2",
                                   command=self._cmd_configure_n_labs_dialog)
        btn_input_labs.pack(side="left", padx=4)

        btn_clear = tk.Button(right_box, text="🗑️ Clear All Labs", bg="#ffffff", fg=COLOR_ROSE,
                              activebackground="#fef2f2", activeforeground=COLOR_ROSE,
                              font=FONT_BOLD, relief="solid", bd=1, padx=10, pady=4, cursor="hand2",
                              command=self._cmd_clear_labs)
        btn_clear.pack(side="left", padx=4)

    # =========================================================================
    # PAGE 1: SUBNET MATRIX (Full Width Dashboard Layout)
    # =========================================================================
    def _build_page_vlsm(self):
        page = tk.Frame(self.main_content, bg=BG_CANVAS)
        self.page_frames["vlsm"] = page

        # Scrollable container for page 1
        canvas = tk.Canvas(page, bg=BG_CANVAS, highlightthickness=0)
        v_scroll = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg=BG_CANVAS)

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # Mousewheel scroll support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 1. Target Scope Header Bar (Dynamic IPv4 & CIDR Input)
        scope_card = tk.Frame(scroll_content, bg=BG_CARD, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        scope_card.pack(fill="x", pady=(0, 10))

        scope_top = tk.Frame(scope_card, bg=BG_CARD)
        scope_top.pack(fill="x", pady=(0, 8))

        globe_badge = tk.Label(scope_top, text="🌐", bg=COLOR_BLUE, fg="#ffffff", font=("Segoe UI", 11, "bold"),
                               width=3, height=1, relief="flat")
        globe_badge.pack(side="left", padx=(0, 10))

        scope_title_box = tk.Frame(scope_top, bg=BG_CARD)
        scope_title_box.pack(side="left", fill="y")

        lbl_scope_head = tk.Label(scope_title_box, text="Target Network Scope (Root IPv4 Prefix)", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD)
        lbl_scope_head.pack(anchor="w")

        lbl_scope_sub = tk.Label(scope_title_box, text="Specify the root IPv4 address and CIDR prefix for your campus network",
                                 bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL)
        lbl_scope_sub.pack(anchor="w")

        # Scope Input Controls
        input_row = tk.Frame(scope_card, bg="#f8fafc", padx=12, pady=8, highlightbackground=BORDER_COLOR, highlightthickness=1)
        input_row.pack(fill="x")

        tk.Label(input_row, text="Base IP Address:", bg="#f8fafc", fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left", padx=(0, 6))
        self.ent_base_ip = tk.Entry(input_row, bg="#ffffff", fg=TEXT_MAIN, font=FONT_MONO_BOLD, width=16, relief="solid", bd=1)
        self.ent_base_ip.insert(0, "192.168.0.0")
        self.ent_base_ip.pack(side="left", padx=(0, 10))
        self.ent_base_ip.bind("<Return>", lambda e: self._cmd_apply_base())

        tk.Label(input_row, text="Prefix Length:", bg="#f8fafc", fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left", padx=(0, 6))
        self.cbo_base_cidr = ttk.Combobox(input_row, values=[f"/{c}" for c in range(8, 31)], width=6, state="readonly")
        self.cbo_base_cidr.set("/24")
        self.cbo_base_cidr.pack(side="left", padx=(0, 10))
        self.cbo_base_cidr.bind("<<ComboboxSelected>>", lambda e: self._cmd_apply_base())

        btn_apply_scope = tk.Button(input_row, text="⚡ Apply Scope", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                                    activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                                    relief="flat", padx=12, pady=3, cursor="hand2", command=self._cmd_apply_base)
        btn_apply_scope.pack(side="left", padx=(0, 14))

        self.lbl_scope_summary = tk.Label(input_row, text="Root Scope: 256 Total IP Addresses", bg="#f8fafc", fg=TEXT_MUTED, font=FONT_SMALL)
        self.lbl_scope_summary.pack(side="left")

        # 2. 4 Quick Subnet Cards (Dynamically Linked to Top Provisioned Subnets)
        cards_row = tk.Frame(scroll_content, bg=BG_CANVAS)
        cards_row.pack(fill="x", pady=(0, 10))

        self.quick_cards = []
        for i in range(4):
            border_c = BORDER_ACTIVE if i == 1 else BORDER_COLOR
            c_frame = tk.Frame(cards_row, bg=BG_CARD, padx=14, pady=12, highlightbackground=border_c, highlightthickness=1)
            c_frame.pack(side="left", fill="both", expand=True, padx=4)

            lbl_badge = tk.Label(c_frame, text="ALLOCATED" if i == 0 else "AVAILABLE",
                                 bg=COLOR_BLUE_SOFT if i == 0 else "#f1f5f9",
                                 fg=COLOR_BLUE if i == 0 else TEXT_MUTED, font=("Segoe UI", 7, "bold"))
            lbl_badge.pack(anchor="e")

            lbl_t = tk.Label(c_frame, text=f"LAB #{i+1}", bg=BG_CARD, fg=TEXT_MUTED, font=("Segoe UI", 7, "bold"))
            lbl_t.pack(anchor="w")

            lbl_v = tk.Label(c_frame, text="-- PCs", bg=BG_CARD, fg=COLOR_GREEN, font=FONT_NUM_BIG)
            lbl_v.pack(anchor="w", pady=(2, 0))

            lbl_s = tk.Label(c_frame, text="Subnet: --", bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL)
            lbl_s.pack(anchor="w")

            self.quick_cards.append({
                "frame": c_frame,
                "badge": lbl_badge,
                "title": lbl_t,
                "val": lbl_v,
                "sub": lbl_s
            })

        # 3. 5 Mathematical Breakdown Metric Strip
        metric_row = tk.Frame(scroll_content, bg=BG_CANVAS)
        metric_row.pack(fill="x", pady=(0, 10))

        self.stat_labels = {}
        metrics_meta = [
            ("workstations", "PLANNED DEMAND", "0 PCs", TEXT_MAIN),
            ("allocated", "ALLOCATED SPACE", "0 IPs", TEXT_MAIN),
            ("usable", "USABLE CAPACITY", "0 Slots", COLOR_GREEN),
            ("next_free", "NEXT FREE SUBNET", "192.168.0.0", TEXT_MAIN),
            ("efficiency", "VLSM EFFICIENCY", "0.0 %", COLOR_GREEN),
        ]

        for key, title, default_val, fg_color in metrics_meta:
            m_box = tk.Frame(metric_row, bg=BG_CARD, padx=12, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
            m_box.pack(side="left", fill="both", expand=True, padx=4)

            lbl_t = tk.Label(m_box, text=title, bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI", 7, "bold"))
            lbl_t.pack(anchor="w")

            lbl_val = tk.Label(m_box, text=default_val, bg=BG_CARD, fg=fg_color, font=("Segoe UI", 12, "bold"))
            lbl_val.pack(anchor="w", pady=(2, 0))

            self.stat_labels[key] = lbl_val

        # 4. Laboratory Fleet Input & Sizing Section
        fleet_card = tk.Frame(scroll_content, bg=BG_CARD, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        fleet_card.pack(fill="x", pady=(0, 10))

        fleet_head = tk.Frame(fleet_card, bg=BG_CARD)
        fleet_head.pack(fill="x", pady=(0, 8))

        lbl_f_icon = tk.Label(fleet_head, text="🏫", font=("Segoe UI", 11))
        lbl_f_icon.pack(side="left", padx=(0, 6))

        tk.Label(fleet_head, text="Laboratory Fleet Configuration (User Input):", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left")

        # Quick sizing chips on the right
        fleet_presets = tk.Frame(fleet_head, bg=BG_CARD)
        fleet_presets.pack(side="right")
        tk.Label(fleet_presets, text="Quick Sizing:", bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left", padx=(0, 4))
        for cnt in [4, 6, 8, 10, 12]:
            btn_cnt = tk.Button(fleet_presets, text=f"{cnt} Labs", bg="#ffffff", fg=TEXT_MAIN, font=FONT_SMALL, relief="solid", bd=1,
                                padx=6, pady=1, cursor="hand2", command=lambda c=cnt: self._cmd_quick_preset_labs(c))
            btn_cnt.pack(side="left", padx=2)

        fleet_row = tk.Frame(fleet_card, bg="#f8fafc", padx=12, pady=8, highlightbackground=BORDER_COLOR, highlightthickness=1)
        fleet_row.pack(fill="x", pady=(0, 10))

        tk.Label(fleet_row, text="Number of Laboratories:", bg="#f8fafc", fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left", padx=(0, 8))
        self.spn_num_labs = tk.Spinbox(fleet_row, from_=1, to=32, width=5, font=FONT_MONO_BOLD, relief="solid", bd=1, justify="center")
        self.spn_num_labs.delete(0, tk.END)
        self.spn_num_labs.insert(0, "8")
        self.spn_num_labs.pack(side="left", padx=(0, 10))
        self.spn_num_labs.bind("<Return>", lambda e: self._cmd_configure_n_labs_dialog())

        btn_wizard_n = tk.Button(fleet_row, text="📝 Input Details for Labs...", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                                 activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                                 relief="flat", padx=14, pady=3, cursor="hand2", command=self._cmd_configure_n_labs_dialog)
        btn_wizard_n.pack(side="left", padx=(0, 12))

        self.lbl_fleet_hint = tk.Label(fleet_row, text="Input your exact laboratory names and workstation PC counts to compute VLSM",
                                       bg="#f8fafc", fg=TEXT_MUTED, font=FONT_SMALL)
        self.lbl_fleet_hint.pack(side="left")

        # Single Lab Quick Add Bar
        prov_sub = tk.Frame(fleet_card, bg=BG_CARD)
        prov_sub.pack(fill="x")

        tk.Label(prov_sub, text="Or Quickly Add a Single Laboratory:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL_BOLD).grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 6))

        tk.Label(prov_sub, text="Lab Name:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_MAIN).grid(row=1, column=0, sticky="w")
        self.ent_lab_name = tk.Entry(prov_sub, bg=BG_INPUT, fg=TEXT_MAIN, width=22, font=FONT_MAIN, relief="solid", bd=1)
        self.ent_lab_name.insert(0, "Computer Lab")
        self.ent_lab_name.grid(row=1, column=1, padx=(4, 10))
        self.ent_lab_name.bind("<Return>", lambda e: self._cmd_add_lab())

        tk.Label(prov_sub, text="Department:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_MAIN).grid(row=1, column=2, sticky="w")
        self.ent_lab_dept = tk.Entry(prov_sub, bg=BG_INPUT, fg=TEXT_MAIN, width=15, font=FONT_MAIN, relief="solid", bd=1)
        self.ent_lab_dept.insert(0, "Campus Wing")
        self.ent_lab_dept.grid(row=1, column=3, padx=(4, 10))

        tk.Label(prov_sub, text="PCs:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_MAIN).grid(row=1, column=4, sticky="w")
        self.ent_lab_pcs = tk.Entry(prov_sub, bg=BG_INPUT, fg=TEXT_MAIN, width=6, font=FONT_MONO, relief="solid", bd=1)
        self.ent_lab_pcs.insert(0, "50")
        self.ent_lab_pcs.grid(row=1, column=5, padx=(4, 10))
        self.ent_lab_pcs.bind("<Return>", lambda e: self._cmd_add_lab())

        tk.Label(prov_sub, text="Growth %:", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_MAIN).grid(row=1, column=6, sticky="w")
        self.ent_lab_growth = tk.Entry(prov_sub, bg=BG_INPUT, fg=TEXT_MAIN, width=5, font=FONT_MONO, relief="solid", bd=1)
        self.ent_lab_growth.insert(0, "10")
        self.ent_lab_growth.grid(row=1, column=7, padx=(4, 10))
        self.ent_lab_growth.bind("<Return>", lambda e: self._cmd_add_lab())

        btn_add = tk.Button(prov_sub, text="+ Add Lab", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                            activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                            relief="flat", padx=10, pady=3, cursor="hand2", command=self._cmd_add_lab)
        btn_add.grid(row=1, column=8, padx=4)

        btn_clear = tk.Button(prov_sub, text="Clear All", bg="#ffffff", fg=COLOR_ROSE, font=FONT_MAIN,
                              relief="solid", bd=1, padx=8, pady=3, cursor="hand2", command=self._cmd_clear_labs)
        btn_clear.grid(row=1, column=9, padx=4)

        # 5. Main Campus Subnet Allocations Table
        table_card = tk.Frame(scroll_content, bg=BG_CARD, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        t_head = tk.Frame(table_card, bg=BG_CARD)
        t_head.pack(fill="x", pady=(0, 8))

        self.lbl_table_title = tk.Label(t_head, text="Campus Subnet Allocation Matrix", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_HEADING)
        self.lbl_table_title.pack(side="left")

        btn_box = tk.Frame(t_head, bg=BG_CARD)
        btn_box.pack(side="right")

        btn_add_sys = tk.Button(btn_box, text="➕ Add System to Lab...", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                                activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                                relief="flat", padx=10, pady=2, cursor="hand2", command=self._cmd_add_systems_dialog)
        btn_add_sys.pack(side="left", padx=4)

        btn_edit_selected = tk.Button(btn_box, text="✏️ Edit Selected Lab", bg="#ffffff", fg=COLOR_BLUE, font=FONT_MAIN,
                                      relief="solid", bd=1, padx=8, pady=2, cursor="hand2", command=self._cmd_edit_lab)
        btn_edit_selected.pack(side="left", padx=4)

        btn_del_selected = tk.Button(btn_box, text="🗑️ Remove Selected Lab", bg="#ffffff", fg=COLOR_ROSE, font=FONT_MAIN,
                                     relief="solid", bd=1, padx=8, pady=2, cursor="hand2", command=self._cmd_remove_lab)
        btn_del_selected.pack(side="left", padx=4)

        cols = ("id", "name", "dept", "pcs", "vlan", "subnet", "mask", "range", "gateway", "capacity", "eff")
        self.tree_vlsm = ttk.Treeview(table_card, columns=cols, show="headings", height=10, selectmode="browse")

        col_heads = [
            ("id", "Lab #", 50, "center"),
            ("name", "Laboratory Name", 180, "w"),
            ("dept", "Department", 130, "w"),
            ("pcs", "Workstations", 90, "center"),
            ("vlan", "VLAN", 60, "center"),
            ("subnet", "Subnet Prefix", 120, "w"),
            ("mask", "Subnet Mask", 110, "w"),
            ("range", "Usable Host Range", 170, "w"),
            ("gateway", "Gateway (SVI)", 100, "w"),
            ("capacity", "Capacity", 70, "center"),
            ("eff", "Efficiency", 80, "center"),
        ]

        for col_id, title, w, align in col_heads:
            self.tree_vlsm.heading(col_id, text=title)
            self.tree_vlsm.column(col_id, width=w, anchor=align)

        self.tree_vlsm.bind("<Double-1>", lambda e: self._cmd_edit_lab())

        tree_scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.tree_vlsm.yview)
        self.tree_vlsm.configure(yscrollcommand=tree_scroll.set)

        self.tree_vlsm.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

    # =========================================================================
    # PAGE 2: WORKSTATION INVENTORY & SYSTEMS
    # =========================================================================
    def _build_page_inventory(self):
        page = tk.Frame(self.main_content, bg=BG_CANVAS)
        self.page_frames["inventory"] = page

        # Top Control Bar (Clean, zero export buttons)
        top_bar = tk.Frame(page, bg=BG_CARD, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="Select Laboratory Subnet:", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left", padx=(0, 8))
        self.cbo_inv_lab = ttk.Combobox(top_bar, width=32, state="readonly")
        self.cbo_inv_lab.pack(side="left", padx=(0, 10))
        self.cbo_inv_lab.bind("<<ComboboxSelected>>", self._on_inv_lab_selected)

        # Inline Add System to Selected Lab Controls
        sep_vl = tk.Frame(top_bar, bg=BORDER_COLOR, width=1, height=22)
        sep_vl.pack(side="left", padx=(4, 12))

        tk.Label(top_bar, text="Add New System(s):", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left", padx=(0, 6))
        self.spn_add_sys_count = tk.Spinbox(top_bar, from_=1, to=200, width=4, font=FONT_MONO_BOLD, relief="solid", bd=1, justify="center")
        self.spn_add_sys_count.delete(0, tk.END)
        self.spn_add_sys_count.insert(0, "1")
        self.spn_add_sys_count.pack(side="left", padx=(0, 6))
        self.spn_add_sys_count.bind("<Return>", lambda e: self._cmd_add_systems_to_current_lab())

        btn_add_one_pc = tk.Button(top_bar, text="+1 PC", bg="#ffffff", fg=COLOR_BLUE, font=FONT_SMALL_BOLD,
                                   relief="solid", bd=1, padx=6, pady=2, cursor="hand2", command=lambda: self._cmd_add_systems_to_current_lab(1))
        btn_add_one_pc.pack(side="left", padx=2)

        btn_add_five_pc = tk.Button(top_bar, text="+5 PCs", bg="#ffffff", fg=COLOR_BLUE, font=FONT_SMALL_BOLD,
                                    relief="solid", bd=1, padx=6, pady=2, cursor="hand2", command=lambda: self._cmd_add_systems_to_current_lab(5))
        btn_add_five_pc.pack(side="left", padx=2)

        btn_add_sys_inv = tk.Button(top_bar, text="➕ Add to Lab", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                                    activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                                    relief="flat", padx=10, pady=2, cursor="hand2", command=self._cmd_add_systems_to_current_lab)
        btn_add_sys_inv.pack(side="left", padx=(4, 0))

        # 4 Scope Cards (Subnet Pool, Mask/VLAN, Gateway, DHCP Range)
        self.scope_cards_frame = tk.Frame(page, bg=BG_CANVAS)
        self.scope_cards_frame.pack(fill="x", pady=(0, 10))

        self.inv_scope_labels = {}
        for key, title in [("pool", "SUBNET POOL"), ("mask", "MASK & VLAN"), ("gateway", "DEFAULT GATEWAY (SVI)"), ("range", "DHCP LEASE RANGE")]:
            c = tk.Frame(self.scope_cards_frame, bg=BG_CARD, padx=12, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
            c.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(c, text=title, bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI", 7, "bold")).pack(anchor="w")
            lbl_v = tk.Label(c, text="--", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_MONO_BOLD)
            lbl_v.pack(anchor="w", pady=(2, 0))
            self.inv_scope_labels[key] = lbl_v

        # Bottom Split: Cisco DHCP Pool on left, Device Inventory on right
        split_frame = tk.Frame(page, bg=BG_CANVAS)
        split_frame.pack(fill="both", expand=True)

        # Left: Cisco DHCP Script
        dhcp_box = tk.LabelFrame(split_frame, text=" Cisco IOS DHCP Configuration Script ", bg=BG_CARD, fg=COLOR_BLUE, font=FONT_BOLD, padx=10, pady=8)
        dhcp_box.pack(side="left", fill="both", expand=False, padx=(0, 8))
        dhcp_box.configure(width=420)
        dhcp_box.pack_propagate(False)

        btn_copy_dhcp = tk.Button(dhcp_box, text="📋 Copy CLI", bg=COLOR_BLUE, fg="#ffffff", font=FONT_SMALL_BOLD,
                                  relief="flat", padx=6, pady=2, cursor="hand2", command=self._copy_dhcp_cli)
        btn_copy_dhcp.pack(anchor="e", pady=(0, 4))

        self.txt_dhcp_cli = tk.Text(dhcp_box, bg="#0f172a", fg="#34d399", font=FONT_MONO, relief="flat", padx=8, pady=8)
        self.txt_dhcp_cli.pack(fill="both", expand=True)

        # Right: Device Inventory Table
        inv_box = tk.LabelFrame(split_frame, text=" Workstation Device Inventory ", bg=BG_CARD, fg=COLOR_GREEN, font=FONT_BOLD, padx=10, pady=8)
        inv_box.pack(side="right", fill="both", expand=True)

        cols_inv = ("idx", "host", "role", "ip", "mask", "gw", "dns")
        self.tree_inv = ttk.Treeview(inv_box, columns=cols_inv, show="headings", height=12)

        for cid, t, w in [("idx", "#", 40), ("host", "Hostname", 120), ("role", "Role", 110),
                          ("ip", "IP Address", 110), ("mask", "Subnet Mask", 100),
                          ("gw", "Gateway", 100), ("dns", "DNS", 90)]:
            self.tree_inv.heading(cid, text=t)
            self.tree_inv.column(cid, width=w, anchor="w" if cid != "idx" else "center")

        inv_scroll = ttk.Scrollbar(inv_box, orient="vertical", command=self.tree_inv.yview)
        self.tree_inv.configure(yscrollcommand=inv_scroll.set)
        self.tree_inv.pack(side="left", fill="both", expand=True)
        inv_scroll.pack(side="right", fill="y")

    # =========================================================================
    # PAGE 3: CIDR SUPERNETTING & ROUTE SUMMARIZATION
    # =========================================================================
    def _build_page_supernetting(self):
        page = tk.Frame(self.main_content, bg=BG_CANVAS)
        self.page_frames["supernetting"] = page

        # Scrollable container for Supernetting page
        canvas = tk.Canvas(page, bg=BG_CANVAS, highlightthickness=0)
        v_scroll = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scroll_content = tk.Frame(canvas, bg=BG_CANVAS)

        scroll_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_content, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        v_scroll.pack(side="right", fill="y")

        # 1. Top Card: Header & Presets
        top_card = tk.Frame(scroll_content, bg=BG_CARD, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        top_card.pack(fill="x", pady=(0, 10))

        head_row = tk.Frame(top_card, bg=BG_CARD)
        head_row.pack(fill="x", pady=(0, 8))

        icon_lbl = tk.Label(head_row, text="🌐", bg=COLOR_BLUE, fg="#ffffff", font=("Segoe UI", 11, "bold"), width=3, height=1)
        icon_lbl.pack(side="left", padx=(0, 10))

        title_box = tk.Frame(head_row, bg=BG_CARD)
        title_box.pack(side="left")
        tk.Label(title_box, text="CIDR Supernetting & Route Summarization Engine", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(anchor="w")
        tk.Label(title_box, text="Aggregate contiguous subnets into a single prefix, compute LCP binary proof, and reduce routing tables", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w")

        # Presets on the right
        super_presets = tk.Frame(head_row, bg=BG_CARD)
        super_presets.pack(side="right")
        tk.Label(super_presets, text="Presets:", bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL).pack(side="left", padx=(0, 4))
        for p_name, p_list in [
            ("4 Class C", ["192.168.0.0/24", "192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"]),
            ("8 Class C", [f"192.168.{i}.0/24" for i in range(8)]),
            ("ISP Core (/22)", ["198.51.100.0/24", "198.51.101.0/24", "198.51.102.0/24", "198.51.103.0/24"]),
            ("Campus WAN", ["10.50.254.0/30", "10.50.254.4/30", "10.50.254.8/30", "10.50.254.12/30"]),
        ]:
            btn_p = tk.Button(super_presets, text=p_name, bg="#ffffff", fg=TEXT_MAIN, font=FONT_SMALL, relief="solid", bd=1,
                              padx=5, pady=1, cursor="hand2", command=lambda pl=p_list: self._set_super_preset(pl))
            btn_p.pack(side="left", padx=2)

        # 2. Input Box & Action Buttons
        input_card = tk.Frame(scroll_content, bg=BG_CARD, padx=16, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        input_card.pack(fill="x", pady=(0, 10))

        in_head = tk.Frame(input_card, bg=BG_CARD)
        in_head.pack(fill="x", pady=(0, 6))
        tk.Label(in_head, text="Target Subnets to Summarize (One prefix per line or comma-separated):", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left")

        btn_import_campus = tk.Button(in_head, text="🏫 Import Active Campus Labs", bg="#ffffff", fg=COLOR_BLUE, font=FONT_SMALL_BOLD,
                                      relief="solid", bd=1, padx=8, pady=2, cursor="hand2", command=self._cmd_import_campus_supernet)
        btn_import_campus.pack(side="right")

        in_body = tk.Frame(input_card, bg=BG_CARD)
        in_body.pack(fill="x")

        self.txt_super_input = tk.Text(in_body, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MONO, height=4, relief="solid", bd=1, padx=8, pady=6)
        self.txt_super_input.pack(side="left", fill="x", expand=True, padx=(0, 12))
        default_super = "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24\n192.168.3.0/24"
        self.txt_super_input.insert("1.0", default_super)

        btn_act_box = tk.Frame(in_body, bg=BG_CARD)
        btn_act_box.pack(side="right", fill="y")

        btn_calc_super = tk.Button(btn_act_box, text="⚡ Calculate Supernet", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                                   activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                                   relief="flat", padx=16, pady=8, cursor="hand2", command=self._cmd_run_supernet)
        btn_calc_super.pack(fill="x", pady=(0, 6))

        btn_clear_super = tk.Button(btn_act_box, text="Clear Input", bg="#ffffff", fg=TEXT_MUTED, font=FONT_MAIN,
                                    relief="solid", bd=1, padx=12, pady=4, cursor="hand2", command=lambda: self.txt_super_input.delete("1.0", tk.END))
        btn_clear_super.pack(fill="x")

        # 3. 4 Dynamic Supernet Metrics Strip
        metrics_row = tk.Frame(scroll_content, bg=BG_CANVAS)
        metrics_row.pack(fill="x", pady=(0, 10))

        self.super_stat_labels = {}
        super_meta = [
            ("supernet_id", "SUPERNET NETWORK ID", "192.168.0.0 /22", COLOR_BLUE),
            ("supernet_mask", "AGGREGATE MASK", "255.255.252.0", COLOR_GREEN),
            ("total_ips", "TOTAL AGGREGATE CAPACITY", "1,024 IPs (1,022 Hosts)", TEXT_MAIN),
            ("reduction", "ROUTE TABLE REDUCTION", "75.0 % (4 routes → 1)", COLOR_GREEN),
        ]
        for key, title, def_val, color in super_meta:
            m_box = tk.Frame(metrics_row, bg=BG_CARD, padx=12, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
            m_box.pack(side="left", fill="both", expand=True, padx=4)
            tk.Label(m_box, text=title, bg=BG_CARD, fg=TEXT_DIM, font=("Segoe UI", 7, "bold")).pack(anchor="w")
            lbl_v = tk.Label(m_box, text=def_val, bg=BG_CARD, fg=color, font=("Segoe UI", 12, "bold"))
            lbl_v.pack(anchor="w", pady=(2, 0))
            self.super_stat_labels[key] = lbl_v

        # 4. Verdict / Contiguity Status Banner
        status_banner = tk.Frame(scroll_content, bg=BG_CARD, padx=16, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        status_banner.pack(fill="x", pady=(0, 10))

        self.lbl_super_badge = tk.Label(status_banner, text="✅ Optimal Exact Supernet (Zero Address Leakage)", bg=COLOR_GREEN_SOFT, fg=COLOR_GREEN, font=FONT_BOLD, padx=10, pady=4)
        self.lbl_super_badge.pack(side="left", padx=(0, 12))

        self.lbl_super_desc = tk.Label(status_banner, text="All input subnets are strictly contiguous and power-of-2 aligned.", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_MAIN, wraplength=700, justify="left")
        self.lbl_super_desc.pack(side="left", fill="x", expand=True)

        # 5. Split Bottom Area: Binary LCP Proof on Left, Cisco IOS on Right
        split_bot = tk.Frame(scroll_content, bg=BG_CANVAS)
        split_bot.pack(fill="both", expand=True, pady=(0, 10))

        # Left: Binary Longest Common Prefix (LCP) Proof
        bin_box = tk.LabelFrame(split_bot, text=" 32-Bit Longest Common Prefix (LCP) Mathematical Proof ", bg=BG_CARD, fg=COLOR_BLUE, font=FONT_BOLD, padx=12, pady=10)
        bin_box.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.txt_super_bin = tk.Text(bin_box, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MONO, height=12, relief="flat", padx=10, pady=8)
        self.txt_super_bin.pack(fill="both", expand=True)

        # Right: Cisco Route Summarization CLI
        cisco_box = tk.LabelFrame(split_bot, text=" Cisco IOS Multi-Protocol Route Summarization CLI ", bg=BG_CARD, fg=COLOR_GREEN, font=FONT_BOLD, padx=12, pady=10)
        cisco_box.pack(side="right", fill="both", expand=True, padx=(6, 0))

        cisco_top = tk.Frame(cisco_box, bg=BG_CARD)
        cisco_top.pack(fill="x", pady=(0, 4))
        tk.Label(cisco_top, text="Static Discard, OSPF ABR, BGP & EIGRP Configs", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(side="left")
        btn_copy_super_cisco = tk.Button(cisco_top, text="📋 Copy CLI", bg=COLOR_BLUE, fg="#ffffff", font=FONT_SMALL_BOLD,
                                         relief="flat", padx=6, pady=2, cursor="hand2", command=self._copy_super_cisco)
        btn_copy_super_cisco.pack(side="right")

        self.txt_super_cisco = tk.Text(cisco_box, bg="#0f172a", fg="#34d399", font=FONT_MONO, height=12, relief="flat", padx=10, pady=8)
        self.txt_super_cisco.pack(fill="both", expand=True)

        # 6. Aggregated Subnets Matrix Table
        tbl_card = tk.LabelFrame(scroll_content, text=" Aggregated Subnets Breakdown Matrix ", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD, padx=12, pady=10)
        tbl_card.pack(fill="both", expand=True)

        cols_s = ("idx", "net", "mask", "range", "bcast", "capacity", "lcp")
        self.tree_super = ttk.Treeview(tbl_card, columns=cols_s, show="headings", height=5)
        for cid, chead, cw, calign in [
            ("idx", "#", 40, "center"),
            ("net", "Input Subnet", 140, "w"),
            ("mask", "Subnet Mask", 130, "w"),
            ("range", "Usable Host Range", 200, "w"),
            ("bcast", "Broadcast ID", 130, "w"),
            ("capacity", "Block Size", 90, "center"),
            ("lcp", "LCP Bit Status", 130, "center"),
        ]:
            self.tree_super.heading(cid, text=chead)
            self.tree_super.column(cid, width=cw, anchor=calign)

        self.tree_super.pack(fill="both", expand=True)

        # Run initial calculation
        self._cmd_run_supernet()

    # =========================================================================
    # STATUS BAR
    # =========================================================================
    def _build_status_bar(self):
        status_frame = tk.Frame(self.right_container, bg=BG_CARD, height=26, padx=16,
                                highlightbackground=BORDER_COLOR, highlightthickness=1)
        status_frame.pack(fill="x", side="bottom")

        self.lbl_status = tk.Label(status_frame, text="Ready. User-driven input mode.",
                                   bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL)
        self.lbl_status.pack(side="left", pady=3)

        lbl_credits = tk.Label(status_frame, text="Computer Networks Mini Project • Native Desktop GUI",
                               bg=BG_CARD, fg=TEXT_DIM, font=FONT_SMALL)
        lbl_credits.pack(side="right", pady=3)

    # =========================================================================
    # DYNAMIC DATA LOGIC & COMMANDS
    # =========================================================================
    def _refresh_all_ui(self):
        # 1. Refresh Subnet Matrix table
        for row in self.tree_vlsm.get_children():
            self.tree_vlsm.delete(row)

        for lab in self.campus.labs:
            d = lab.to_dict()
            self.tree_vlsm.insert("", "end", values=(
                f"#{d['id']}",
                d['name'],
                d['department'],
                f"{d['workstations']} PCs",
                f"VLAN {d['vlan_id']}",
                d['subnet_str'],
                d['subnet_mask_str'],
                d['range_str'],
                d['gateway_ip_str'],
                f"{d['usable_capacity']}",
                f"{d['efficiency_pct']}%"
            ))

        # 2. Refresh 4 Quick Subnet Cards Dynamically
        if hasattr(self, "quick_cards") and self.quick_cards:
            for i in range(4):
                card = self.quick_cards[i]
                if i < len(self.campus.labs):
                    d = self.campus.labs[i].to_dict()
                    card["title"].configure(text=d["name"].upper())
                    card["val"].configure(text=f"{d['workstations']} PCs")
                    card["sub"].configure(text=f"Subnet: {d['subnet_str']} ({d['usable_capacity']} Hosts)")
                    card["badge"].configure(text="ALLOCATED", bg=COLOR_BLUE_SOFT, fg=COLOR_BLUE)
                else:
                    card["title"].configure(text=f"UNALLOCATED SLOT #{i+1}")
                    card["val"].configure(text="-- PCs")
                    card["sub"].configure(text="Ready for allocation")
                    card["badge"].configure(text="AVAILABLE", bg="#f1f5f9", fg=TEXT_MUTED)

        # 3. Refresh Metrics Strip
        self.stat_labels["workstations"].configure(text=f"{self.campus.total_requested_hosts} PCs")
        self.stat_labels["allocated"].configure(text=f"{self.campus.total_allocated_blocks:,} IPs")
        self.stat_labels["usable"].configure(text=f"{self.campus.total_usable_hosts:,} Slots")
        next_free_str = engine.int_to_ip(self.campus.next_free_subnet) if self.campus.labs else self.campus.base_ip_str
        self.stat_labels["next_free"].configure(text=next_free_str)
        eff = round(self.campus.overall_efficiency, 1)
        self.stat_labels["efficiency"].configure(text=f"{eff} %")

        # 4. Refresh Scope Summary Label
        base_end = engine.int_to_ip(self.campus.base_broadcast)
        self.lbl_scope_summary.configure(
            text=f"Scope: {self.campus.base_ip_str} - {base_end} • {self.campus.total_campus_capacity:,} Total IPs ({self.campus.free_ips_remaining:,} Free)"
        )
        if self.campus.labs:
            self.lbl_table_title.configure(text=f"Campus Subnet Allocation Matrix ({len(self.campus.labs)} Subnets Provisioned)")
            self.lbl_status.configure(text=f"Calculated {len(self.campus.labs)} subnets on {self.campus.base_ip_str}/{self.campus.base_cidr}. VLSM efficiency: {eff}%.")
        else:
            self.lbl_table_title.configure(text="Campus Subnet Allocation Matrix (Awaiting User Input)")
            self.lbl_status.configure(text=f"Scope set to {self.campus.base_ip_str}/{self.campus.base_cidr}. Click 'Input Lab Details' to configure your laboratories.")

        # 5. Update Inventory Lab Combobox
        opts = [f"{l.id}. {l.name} ({l.workstations} PCs, VLAN {l.vlan_id})" for l in self.campus.labs]
        self.cbo_inv_lab["values"] = opts
        if opts:
            self.cbo_inv_lab.current(0)
            self._on_inv_lab_selected()
        else:
            self.cbo_inv_lab.set("")
            for k in self.inv_scope_labels:
                self.inv_scope_labels[k].configure(text="--")
            self.txt_dhcp_cli.delete("1.0", tk.END)
            for r in self.tree_inv.get_children():
                self.tree_inv.delete(r)

        # Update Number of Labs spinbox if present
        if hasattr(self, "spn_num_labs"):
            try:
                cnt = len(self.campus.labs) if self.campus.labs else 8
                self.spn_num_labs.delete(0, tk.END)
                self.spn_num_labs.insert(0, str(cnt))
            except Exception:
                pass

    def _cmd_apply_base(self):
        raw_ip = self.ent_base_ip.get().strip()
        raw_cidr = self.cbo_base_cidr.get().replace("/", "").strip()

        if "/" in raw_ip:
            parts = raw_ip.split("/")
            ip_str = parts[0].strip()
            cidr_str = parts[1].strip()
            self.ent_base_ip.delete(0, tk.END)
            self.ent_base_ip.insert(0, ip_str)
            self.cbo_base_cidr.set(f"/{cidr_str}")
        else:
            ip_str = raw_ip
            cidr_str = raw_cidr

        try:
            cidr = int(cidr_str)
            if not (8 <= cidr <= 30):
                messagebox.showwarning("Invalid CIDR", "CIDR prefix must be between /8 and /30.")
                return
            self.campus.update_base(ip_str, cidr)
            if self.campus.labs:
                success = self.campus.calculate()
                self._refresh_all_ui()
                if not success:
                    messagebox.showwarning(
                        "Scope Capacity Warning",
                        f"Warning: {self.campus.error_reason}\n\n"
                        f"Base scope {ip_str}/{cidr} provides {self.campus.total_campus_capacity:,} total addresses, "
                        f"which cannot fit all {len(self.campus.labs)} laboratories ({self.campus.total_requested_hosts} PCs)."
                    )
            else:
                self._refresh_all_ui()
            self.lbl_status.configure(text=f"✓ Network scope set: {ip_str}/{cidr}.")
        except Exception as e:
            messagebox.showerror("Scope Error", str(e))

    def _cmd_quick_preset_labs(self, count):
        self.spn_num_labs.delete(0, tk.END)
        self.spn_num_labs.insert(0, str(count))
        self._cmd_configure_n_labs_dialog(default_n=count)

    def _cmd_configure_n_labs_dialog(self, default_n=None):
        dlg = tk.Toplevel(self)
        dlg.title("Configure Laboratory Fleet (User Input)")
        dlg.geometry("740x580")
        dlg.configure(bg=BG_CARD)
        dlg.transient(self)
        dlg.grab_set()

        head = tk.Frame(dlg, bg=BG_CARD, padx=20, pady=14, highlightbackground=BORDER_COLOR, highlightthickness=1)
        head.pack(fill="x")

        tk.Label(head, text="Laboratory Fleet Configuration (User Input)", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w")
        tk.Label(head, text="Enter the Name, Department, and Number of PCs for each laboratory. Allocations are computed directly from your input.", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w")

        # Top control: Lab Count Input & Rows Update
        ctrl_card = tk.Frame(dlg, bg="#f8fafc", padx=16, pady=10, highlightbackground=BORDER_COLOR, highlightthickness=1)
        ctrl_card.pack(fill="x", padx=16, pady=10)

        tk.Label(ctrl_card, text="Total Number of Labs (1-32):", bg="#f8fafc", fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left", padx=(0, 6))
        spn_dlg_n = tk.Spinbox(ctrl_card, from_=1, to=32, width=4, font=FONT_MONO_BOLD, relief="solid", bd=1, justify="center")
        
        if default_n is not None:
            current_n = default_n
        elif self.campus.labs:
            current_n = len(self.campus.labs)
        else:
            try:
                current_n = int(self.spn_num_labs.get().strip())
            except Exception:
                current_n = 8
        
        spn_dlg_n.delete(0, tk.END)
        spn_dlg_n.insert(0, str(current_n))
        spn_dlg_n.pack(side="left", padx=(0, 10))

        # Dynamic Rows container (Scrollable Frame)
        container = tk.Frame(dlg, bg=BG_CARD, padx=16)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_CARD)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Table header
        header_row = tk.Frame(scrollable_frame, bg="#f1f5f9", padx=8, pady=4)
        header_row.pack(fill="x", pady=(0, 4))
        tk.Label(header_row, text="Lab #", width=6, bg="#f1f5f9", fg=TEXT_MUTED, font=FONT_BOLD).pack(side="left")
        tk.Label(header_row, text="Laboratory Name", width=26, bg="#f1f5f9", fg=TEXT_MUTED, font=FONT_BOLD).pack(side="left", padx=4)
        tk.Label(header_row, text="Department / Wing", width=18, bg="#f1f5f9", fg=TEXT_MUTED, font=FONT_BOLD).pack(side="left", padx=4)
        tk.Label(header_row, text="Workstations (PCs)", width=16, bg="#f1f5f9", fg=TEXT_MUTED, font=FONT_BOLD).pack(side="left", padx=4)
        tk.Label(header_row, text="Growth %", width=10, bg="#f1f5f9", fg=TEXT_MUTED, font=FONT_BOLD).pack(side="left", padx=4)

        row_entries = []

        def render_rows(n_val):
            for row in row_entries:
                row["frame"].destroy()
            row_entries.clear()

            existing = list(self.campus.labs)
            for i in range(n_val):
                r_frame = tk.Frame(scrollable_frame, bg=BG_CARD, padx=8, pady=2)
                r_frame.pack(fill="x")

                tk.Label(r_frame, text=f"#{i+1}", width=6, bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(side="left")

                ent_n = tk.Entry(r_frame, width=28, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MAIN, relief="solid", bd=1)
                if i < len(existing):
                    ent_n.insert(0, existing[i].name)
                else:
                    ent_n.insert(0, f"Lab {i+1}")
                ent_n.pack(side="left", padx=4)

                ent_d = tk.Entry(r_frame, width=20, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MAIN, relief="solid", bd=1)
                if i < len(existing):
                    ent_d.insert(0, existing[i].department)
                else:
                    ent_d.insert(0, f"Department {chr(65 + (i % 6))}")
                ent_d.pack(side="left", padx=4)

                ent_p = tk.Entry(r_frame, width=16, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MONO_BOLD, relief="solid", bd=1)
                if i < len(existing):
                    ent_p.insert(0, str(existing[i].workstations))
                else:
                    # Provide default stepped values that user can easily modify
                    default_pcs = max(15, 60 - (i * 5)) if n_val >= 8 else (60 if i == 0 else 30)
                    ent_p.insert(0, str(default_pcs))
                ent_p.pack(side="left", padx=4)

                ent_g = tk.Entry(r_frame, width=10, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MONO, relief="solid", bd=1)
                if i < len(existing):
                    ent_g.insert(0, str(existing[i].growth_percent))
                else:
                    ent_g.insert(0, "10")
                ent_g.pack(side="left", padx=4)

                row_entries.append({
                    "frame": r_frame,
                    "name": ent_n,
                    "dept": ent_d,
                    "pcs": ent_p,
                    "growth": ent_g
                })

        def on_update_rows():
            try:
                n = int(spn_dlg_n.get().strip())
                if n < 1 or n > 32:
                    messagebox.showerror("Invalid Count", "Number of labs must be between 1 and 32.", parent=dlg)
                    return
                render_rows(n)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid integer.", parent=dlg)

        btn_update_rows = tk.Button(ctrl_card, text="🔄 Update Row Count", bg="#ffffff", fg=TEXT_MAIN, font=FONT_BOLD,
                                    relief="solid", bd=1, padx=8, pady=2, cursor="hand2", command=on_update_rows)
        btn_update_rows.pack(side="left", padx=(0, 10))

        # Initial render of rows
        render_rows(current_n)

        # Bottom Button Row
        btn_bar = tk.Frame(dlg, bg=BG_CARD, padx=20, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        btn_bar.pack(fill="x", side="bottom")

        def apply_fleet():
            try:
                new_labs_data = []
                for idx, r in enumerate(row_entries, 1):
                    nm = r["name"].get().strip()
                    dp = r["dept"].get().strip() or "Campus Wing"
                    pcs_str = r["pcs"].get().strip()
                    g_str = r["growth"].get().strip() or "0"
                    if not nm:
                        messagebox.showwarning("Validation Error", f"Lab #{idx} name cannot be empty.", parent=dlg)
                        return
                    pcs = int(pcs_str)
                    if pcs <= 0:
                        messagebox.showwarning("Validation Error", f"Lab #{idx} workstations must be at least 1.", parent=dlg)
                        return
                    growth = int(g_str)
                    new_labs_data.append((nm, dp, pcs, growth))

                self.campus.clear_labs()
                for nm, dp, pcs, growth in new_labs_data:
                    self.campus.add_lab(nm, dp, pcs, growth)

                self.campus.calculate()
                self._refresh_all_ui()
                self.spn_num_labs.delete(0, tk.END)
                self.spn_num_labs.insert(0, str(len(new_labs_data)))
                dlg.destroy()
                self.lbl_status.configure(text=f"✓ Successfully allocated subnets for {len(new_labs_data)} laboratories based on your input.")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)

        btn_apply = tk.Button(btn_bar, text="🚀 Allocate Subnets for these Laboratories", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                              activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                              relief="flat", padx=16, pady=6, cursor="hand2", command=apply_fleet)
        btn_apply.pack(side="right", padx=6)

        btn_cancel = tk.Button(btn_bar, text="Cancel", bg="#ffffff", fg=TEXT_MUTED, font=FONT_MAIN,
                               relief="solid", bd=1, padx=12, pady=6, cursor="hand2", command=dlg.destroy)
        btn_cancel.pack(side="right")

    def _cmd_add_lab(self):
        name = self.ent_lab_name.get().strip()
        dept = self.ent_lab_dept.get().strip()
        pcs_str = self.ent_lab_pcs.get().strip()
        growth_str = self.ent_lab_growth.get().strip()

        if not name:
            messagebox.showwarning("Input Required", "Please enter a laboratory name.")
            return

        try:
            pcs = int(pcs_str)
            if pcs <= 0:
                messagebox.showwarning("Input Required", "PCs must be at least 1.")
                return
            growth = int(growth_str) if growth_str else 0
            self.campus.add_lab(name, dept if dept else "Campus Wing", pcs, growth)
            self.campus.calculate()
            self._refresh_all_ui()
            self.ent_lab_name.delete(0, tk.END)
            self.ent_lab_name.insert(0, f"Lab {len(self.campus.labs) + 1}")
        except Exception as e:
            messagebox.showerror("Allocation Error", str(e))

    def _cmd_edit_lab(self):
        selected = self.tree_vlsm.selection()
        if not selected:
            messagebox.showinfo("Select Row", "Please select a laboratory from the table to edit.")
            return

        item = self.tree_vlsm.item(selected[0])
        val_id = item["values"][0]
        try:
            lab_idx = int(str(val_id).replace("#", "")) - 1
            lab = self.campus.labs[lab_idx]
        except Exception:
            return

        dlg = tk.Toplevel(self)
        dlg.title(f"Edit Lab #{lab.id} - {lab.name}")
        dlg.geometry("440x300")
        dlg.configure(bg=BG_CARD)
        dlg.transient(self)
        dlg.grab_set()

        head = tk.Frame(dlg, bg=BG_CARD, padx=20, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        head.pack(fill="x")
        tk.Label(head, text=f"Edit Lab #{lab.id} Specifications", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w")

        body = tk.Frame(dlg, bg=BG_CARD, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Laboratory Name:", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_MAIN).grid(row=0, column=0, sticky="w", pady=4)
        ent_name = tk.Entry(body, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MAIN, width=24, relief="solid", bd=1)
        ent_name.insert(0, lab.name)
        ent_name.grid(row=0, column=1, pady=4, sticky="w")

        tk.Label(body, text="Department / Wing:", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_MAIN).grid(row=1, column=0, sticky="w", pady=4)
        ent_dept = tk.Entry(body, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MAIN, width=24, relief="solid", bd=1)
        ent_dept.insert(0, lab.department)
        ent_dept.grid(row=1, column=1, pady=4, sticky="w")

        tk.Label(body, text="Workstations (PCs):", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_MAIN).grid(row=2, column=0, sticky="w", pady=4)
        ent_pcs = tk.Entry(body, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MONO_BOLD, width=10, relief="solid", bd=1)
        ent_pcs.insert(0, str(lab.workstations))
        ent_pcs.grid(row=2, column=1, pady=4, sticky="w")

        tk.Label(body, text="Growth Buffer %:", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_MAIN).grid(row=3, column=0, sticky="w", pady=4)
        ent_growth = tk.Entry(body, bg=BG_INPUT, fg=TEXT_MAIN, font=FONT_MONO, width=10, relief="solid", bd=1)
        ent_growth.insert(0, str(lab.growth_percent))
        ent_growth.grid(row=3, column=1, pady=4, sticky="w")

        def _save_changes():
            n = ent_name.get().strip()
            d = ent_dept.get().strip()
            p_str = ent_pcs.get().strip()
            g_str = ent_growth.get().strip()
            if not n:
                messagebox.showwarning("Input Required", "Laboratory name cannot be empty.", parent=dlg)
                return
            try:
                p = int(p_str)
                g = int(g_str) if g_str else 0
                lab.name = n
                lab.department = d if d else "Campus Wing"
                lab.workstations = p
                lab.growth_percent = g
                self.campus.calculate()
                self._refresh_all_ui()
                dlg.destroy()
                self.lbl_status.configure(text=f"✓ Updated Lab #{lab.id} ({n}) to {p} PCs. Subnets recomputed.")
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=dlg)

        btn_row = tk.Frame(dlg, bg=BG_CARD, padx=20, pady=12)
        btn_row.pack(fill="x", side="bottom")

        btn_save = tk.Button(btn_row, text="💾 Save Changes", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                             activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                             relief="flat", padx=14, pady=4, cursor="hand2", command=_save_changes)
        btn_save.pack(side="right", padx=4)

        btn_cancel = tk.Button(btn_row, text="Cancel", bg="#ffffff", fg=TEXT_MUTED, font=FONT_MAIN,
                               relief="solid", bd=1, padx=10, pady=4, cursor="hand2", command=dlg.destroy)
        btn_cancel.pack(side="right", padx=4)

        ent_name.focus_set()
        ent_pcs.bind("<Return>", lambda e: _save_changes())

    def _cmd_remove_lab(self):
        selected = self.tree_vlsm.selection()
        if not selected:
            messagebox.showinfo("Select Row", "Please select a laboratory from the table to remove.")
            return

        item = self.tree_vlsm.item(selected[0])
        val_id = item["values"][0]
        try:
            idx = int(str(val_id).replace("#", "")) - 1
            if 0 <= idx < len(self.campus.labs):
                self.campus.remove_lab(idx)
                self.campus.calculate()
                self._refresh_all_ui()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _cmd_clear_labs(self):
        if messagebox.askyesno("Confirm Clear", "Clear all configured laboratory subnets?"):
            self.campus.clear_labs()
            self.campus.calculate()
            self._refresh_all_ui()

    def _on_inv_lab_selected(self, event=None):
        sel_idx = self.cbo_inv_lab.current()
        if sel_idx < 0 or sel_idx >= len(self.campus.labs):
            return

        lab = self.campus.labs[sel_idx]
        inv = engine.generate_lab_inventory(lab)
        dhcp = inv["dhcp"]

        self.inv_scope_labels["pool"].configure(text=f"{dhcp['pool_network']}/{lab.allocated_cidr}")
        self.inv_scope_labels["mask"].configure(text=f"{dhcp['subnet_mask']} (VLAN {dhcp['vlan_id']})")
        self.inv_scope_labels["gateway"].configure(text=dhcp['default_gateway'])
        self.inv_scope_labels["range"].configure(text=f"{dhcp['dhcp_range_start']} - {dhcp['dhcp_range_end']}")

        # Cisco DHCP Script
        clean_name = lab.name.replace(" ", "_").replace("-", "_")
        script = f"""ip dhcp excluded-address {dhcp['default_gateway']} {dhcp['dns_server']}
!
ip dhcp pool POOL_{clean_name}
 network {dhcp['pool_network']} {dhcp['subnet_mask']}
 default-router {dhcp['default_gateway']}
 dns-server {dhcp['dns_server']} 8.8.8.8
 domain-name campus.netlab.internal
 lease 7 0 0
!
interface Vlan{dhcp['vlan_id']}
 description Gateway for {lab.name}
 ip address {dhcp['default_gateway']} {dhcp['subnet_mask']}
 no shutdown"""

        self.txt_dhcp_cli.delete("1.0", tk.END)
        self.txt_dhcp_cli.insert(tk.END, script)

        # Device inventory table
        for r in self.tree_inv.get_children():
            self.tree_inv.delete(r)

        for rec in inv["records"]:
            self.tree_inv.insert("", "end", values=(
                rec["index"],
                rec["hostname"],
                rec["role"],
                rec["ip_str"],
                rec["mask_str"],
                rec["gateway_str"],
                rec["dns_str"]
            ))

    def _copy_dhcp_cli(self):
        content = self.txt_dhcp_cli.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copied", "Cisco IOS DHCP script copied to clipboard.")

    def _cmd_add_systems_to_current_lab(self, count=None):
        sel_idx = self.cbo_inv_lab.current()
        if sel_idx < 0 or sel_idx >= len(self.campus.labs):
            messagebox.showinfo("Select Lab", "Please select a laboratory first.")
            return

        lab = self.campus.labs[sel_idx]
        if count is None:
            try:
                cnt_str = self.spn_add_sys_count.get().strip()
                count = int(cnt_str)
                if count <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Invalid Input", "Please enter a valid positive integer for number of systems.")
                return

        try:
            res = self.campus.add_systems_to_lab(lab.id, count)
            self._refresh_all_ui()
            # Reselect the same lab in combobox
            for idx, l in enumerate(self.campus.labs):
                if l.id == lab.id:
                    self.cbo_inv_lab.current(idx)
                    self._on_inv_lab_selected()
                    break

            msg = f"✓ Added {count} new system(s) to '{lab.name}'.\n\nTotal Workstations: {res['old_workstations']} → {res['new_workstations']} PCs.\nSubnet: {res['new_subnet']} (Usable Capacity: {res['usable_capacity']} hosts, {res['spare_slots']} spare slots remaining)."
            if res["expanded"]:
                msg += f"\n\n⚡ Subnet auto-expanded from /{res['old_cidr']} to /{res['new_cidr']} to accommodate the new systems!"

            messagebox.showinfo("System Added Successfully", msg)
            self.lbl_status.configure(text=f"✓ Added {count} system(s) to Lab #{lab.id} ({lab.name}). Total PCs: {res['new_workstations']}.")
        except Exception as e:
            messagebox.showerror("Error Adding System", str(e))

    def _cmd_add_systems_dialog(self):
        if not self.campus.labs:
            messagebox.showinfo("No Laboratories", "No laboratories configured to add systems to.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Add New Systems to Laboratory")
        dlg.geometry("540x480")
        dlg.configure(bg=BG_CARD)
        dlg.transient(self)
        dlg.grab_set()

        head = tk.Frame(dlg, bg=BG_CARD, padx=20, pady=14, highlightbackground=BORDER_COLOR, highlightthickness=1)
        head.pack(fill="x")

        tk.Label(head, text="Add New System(s) to Laboratory", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_TITLE).pack(anchor="w")
        tk.Label(head, text="Specify additional workstation computers or hosts to allocate to a laboratory subnet.", bg=BG_CARD, fg=TEXT_MUTED, font=FONT_SMALL).pack(anchor="w")

        body = tk.Frame(dlg, bg=BG_CARD, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        # 1. Target Laboratory Selection
        tk.Label(body, text="Select Target Laboratory:", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(anchor="w", pady=(0, 4))
        cbo_lab = ttk.Combobox(body, width=48, state="readonly")
        lab_opts = [f"#{l.id} - {l.name} ({l.workstations} PCs, Subnet: {l.to_dict()['subnet_str']})" for l in self.campus.labs]
        cbo_lab["values"] = lab_opts

        pre_sel = 0
        tree_sel = self.tree_vlsm.selection()
        if tree_sel:
            try:
                item = self.tree_vlsm.item(tree_sel[0])
                val_id = int(str(item["values"][0]).replace("#", ""))
                for idx, l in enumerate(self.campus.labs):
                    if l.id == val_id:
                        pre_sel = idx
                        break
            except Exception:
                pass
        cbo_lab.current(pre_sel)
        cbo_lab.pack(fill="x", pady=(0, 14))

        # 2. Number of Systems to Add
        tk.Label(body, text="Number of New Systems to Add:", bg=BG_CARD, fg=TEXT_MAIN, font=FONT_BOLD).pack(anchor="w", pady=(0, 4))
        count_frame = tk.Frame(body, bg=BG_CARD)
        count_frame.pack(fill="x", pady=(0, 14))

        spn_count = tk.Spinbox(count_frame, from_=1, to=254, width=6, font=FONT_MONO_BOLD, relief="solid", bd=1, justify="center")
        spn_count.delete(0, tk.END)
        spn_count.insert(0, "1")
        spn_count.pack(side="left", padx=(0, 10))

        # 3. Live Capacity Preview Box
        preview_box = tk.LabelFrame(body, text=" Subnet Capacity & Resizing Preview ", bg="#f8fafc", fg=COLOR_BLUE, font=FONT_BOLD, padx=12, pady=10)
        preview_box.pack(fill="x", pady=(0, 10))

        lbl_curr_info = tk.Label(preview_box, text="Current: --", bg="#f8fafc", fg=TEXT_MAIN, font=FONT_MAIN, anchor="w", justify="left")
        lbl_curr_info.pack(fill="x")

        lbl_after_info = tk.Label(preview_box, text="After Addition: --", bg="#f8fafc", fg=COLOR_GREEN, font=FONT_BOLD, anchor="w", justify="left")
        lbl_after_info.pack(fill="x", pady=(4, 0))

        def _update_preview(*args):
            sel_i = cbo_lab.current()
            if sel_i < 0 or sel_i >= len(self.campus.labs):
                return
            t_lab = self.campus.labs[sel_i]
            try:
                c = int(spn_count.get().strip())
                if c <= 0:
                    c = 1
            except Exception:
                c = 1

            new_pcs = t_lab.workstations + c
            cur_cap = t_lab.usable_capacity
            spare = max(0, cur_cap - t_lab.workstations)

            lbl_curr_info.configure(
                text=f"Current: {t_lab.workstations} PCs in Subnet {t_lab.to_dict()['subnet_str']} (Capacity: {cur_cap} hosts, {spare} spare slots left)"
            )

            # Check if fits without resizing
            buf_new = new_pcs * (1.0 + (t_lab.growth_percent / 100.0))
            eff_new = max(2, math.ceil(buf_new))
            h = 2
            while h < 31 and ((1 << h) - 2) < eff_new:
                h += 1
            needed_cidr = 32 - h
            needed_cap = (1 << h) - 2

            if needed_cidr == t_lab.allocated_cidr:
                lbl_after_info.configure(
                    text=f"After Addition: {new_pcs} PCs (+{c}) • Fits in current /{needed_cidr} subnet ({needed_cap - new_pcs} spare remaining).",
                    fg=COLOR_GREEN
                )
            else:
                lbl_after_info.configure(
                    text=f"After Addition: {new_pcs} PCs (+{c}) • Subnet will AUTO-EXPAND from /{t_lab.allocated_cidr} to /{needed_cidr} ({needed_cap} capacity)!",
                    fg=COLOR_INDIGO
                )

        def _set_add_val(v):
            spn_count.delete(0, tk.END)
            spn_count.insert(0, str(v))
            _update_preview()

        for inc_label, inc_val in [("+1 PC", 1), ("+5 PCs", 5), ("+10 PCs", 10), ("+20 PCs", 20)]:
            btn_inc = tk.Button(count_frame, text=inc_label, bg="#ffffff", fg=COLOR_BLUE, font=FONT_SMALL_BOLD,
                                relief="solid", bd=1, padx=6, pady=2, cursor="hand2", command=lambda v=inc_val: _set_add_val(v))
            btn_inc.pack(side="left", padx=2)

        cbo_lab.bind("<<ComboboxSelected>>", _update_preview)
        spn_count.bind("<KeyRelease>", _update_preview)
        _update_preview()

        # Bottom Buttons
        btn_bar = tk.Frame(dlg, bg=BG_CARD, padx=20, pady=12, highlightbackground=BORDER_COLOR, highlightthickness=1)
        btn_bar.pack(fill="x", side="bottom")

        def _confirm_add():
            sel_i = cbo_lab.current()
            if sel_i < 0 or sel_i >= len(self.campus.labs):
                return
            t_lab = self.campus.labs[sel_i]
            try:
                cnt = int(spn_count.get().strip())
                if cnt <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Invalid Count", "Please enter a positive integer.", parent=dlg)
                return

            try:
                res = self.campus.add_systems_to_lab(t_lab.id, cnt)
                self._refresh_all_ui()
                dlg.destroy()

                info_txt = f"✓ Successfully added {cnt} system(s) to '{res['lab_name']}'.\n\n" \
                           f"Total Workstations : {res['old_workstations']} → {res['new_workstations']} PCs\n" \
                           f"Allocated Subnet   : {res['new_subnet']} (Usable Hosts: {res['usable_capacity']})\n" \
                           f"Remaining Spares   : {res['spare_slots']} free IP addresses in subnet pool"
                if res["expanded"]:
                    info_txt += f"\n\n⚡ Automated VLSM Scaling: Subnet prefix expanded from /{res['old_cidr']} to /{res['new_cidr']}!"

                messagebox.showinfo("Systems Added Successfully", info_txt)
                self.lbl_status.configure(text=f"✓ Added {cnt} system(s) to Lab #{t_lab.id} ({res['lab_name']}). Total: {res['new_workstations']} PCs.")
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=dlg)

        btn_ok = tk.Button(btn_bar, text="➕ Add System(s) & Recompute", bg=COLOR_BLUE, fg="#ffffff", font=FONT_BOLD,
                           activebackground=COLOR_BLUE_HOVER, activeforeground="#ffffff",
                           relief="flat", padx=16, pady=5, cursor="hand2", command=_confirm_add)
        btn_ok.pack(side="right", padx=4)

        btn_cancel = tk.Button(btn_bar, text="Cancel", bg="#ffffff", fg=TEXT_MUTED, font=FONT_MAIN,
                               relief="solid", bd=1, padx=12, pady=5, cursor="hand2", command=dlg.destroy)
        btn_cancel.pack(side="right")

    def _set_super_preset(self, prefix_list):
        self.txt_super_input.delete("1.0", tk.END)
        self.txt_super_input.insert("1.0", "\n".join(prefix_list))
        self._cmd_run_supernet()

    def _cmd_import_campus_supernet(self):
        if not self.campus.labs:
            messagebox.showinfo("No Subnets", "No active campus laboratory subnets to import.")
            return
        subnets = [f"{engine.int_to_ip(lab.network_ip)}/{lab.allocated_cidr}" for lab in self.campus.labs]
        self.txt_super_input.delete("1.0", tk.END)
        self.txt_super_input.insert("1.0", "\n".join(subnets))
        self._cmd_run_supernet()
        self.lbl_status.configure(text=f"✓ Imported {len(subnets)} campus laboratory subnets into Supernetting Engine.")

    def _copy_super_cisco(self):
        content = self.txt_super_cisco.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copied", "Cisco IOS route summarization commands copied to clipboard.")

    def _cmd_run_supernet(self):
        raw_text = self.txt_super_input.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Input Required", "Please enter one or more IPv4 subnets.")
            return

        lines = [line.strip() for line in raw_text.replace(",", "\n").splitlines() if line.strip()]
        try:
            res = engine.calculate_supernet(lines)
        except Exception as e:
            messagebox.showerror("Supernet Error", str(e))
            return

        # 1. Update Metrics
        self.super_stat_labels["supernet_id"].configure(text=res["supernet_str"])
        self.super_stat_labels["supernet_mask"].configure(text=res["supernet_mask_str"])
        self.super_stat_labels["total_ips"].configure(text=f"{res['total_supernet_ips']:,} IPs ({res['usable_supernet_hosts']:,} Hosts)")
        self.super_stat_labels["reduction"].configure(text=f"{res['reduction_pct']}% ({res['input_count']} routes → 1)")

        # 2. Update Badge & Verdict
        self.lbl_super_badge.configure(text=res["verdict_badge"])
        if res["is_optimal"]:
            self.lbl_super_badge.configure(bg=COLOR_GREEN_SOFT, fg=COLOR_GREEN)
        elif res["is_contiguous"]:
            self.lbl_super_badge.configure(bg=COLOR_BLUE_SOFT, fg=COLOR_BLUE)
        else:
            self.lbl_super_badge.configure(bg="#fef3c7", fg=COLOR_AMBER)
        self.lbl_super_desc.configure(text=res["verdict_desc"])

        # 3. Update Binary LCP Proof
        s_cidr = res["supernet_cidr"]
        bin_net_str = res.get("supernet_binary") or res.get("supernet_bin_str", "")
        bin_mask_str = res.get("supernet_mask_binary") or res.get("supernet_mask_bin_str", "")
        proof_lines = [
            f"SUPERNET SUMMARY ID : {res['supernet_str']:<18} -> {bin_net_str}",
            f"SUPERNET MASK        : {res['supernet_mask_str']:<18} -> {bin_mask_str}",
            f"LONGEST COMMON PREFIX: /{s_cidr} (First {s_cidr} bits identical across all inputs)",
            "-" * 80
        ]
        for b_item in res["binary_analysis"]:
            proof_lines.append(f"{b_item['network_str']:<21}: [{b_item['common_bits']}] | {b_item['divergent_bits']}")
        proof_lines.append("-" * 80)
        proof_lines.append(f"Usable Host Scope    : {res['supernet_first_usable']} TO {res['supernet_last_usable']}")
        proof_lines.append(f"Contiguity Check     : {'PASS (Contiguous)' if res['is_contiguous'] else 'FAIL (Address Gaps Detected)'}")
        proof_lines.append(f"Power-of-2 Check     : {'PASS (' + str(res['input_count']) + ' subnets)' if res['is_power_of_2'] else 'FAIL (Non power-of-2)'}")
        if res['extra_covered_ips'] > 0:
            proof_lines.append(f"Address Leakage      : Covers {res['extra_covered_ips']:,} extra unassigned IP addresses")

        self.txt_super_bin.delete("1.0", tk.END)
        self.txt_super_bin.insert(tk.END, "\n".join(proof_lines))

        # 4. Update Cisco Commands
        cisco_text = f"""! -------------------------------------------------------------
! Cisco IOS Multi-Protocol Route Summarization Commands
! Generated for Aggregate Prefix: {res['supernet_str']}
! -------------------------------------------------------------

! 1. Anti-Routing-Loop Discard Static Route (RFC 1812)
{res['cisco_static']}

! 2. OSPF Area Border Router (ABR) Route Aggregation
{res['cisco_ospf']}

! 3. BGP Border Gateway Route Aggregation
{res['cisco_bgp']}

! 4. EIGRP Interface Level Route Summarization
{res['cisco_eigrp']}
"""
        self.txt_super_cisco.delete("1.0", tk.END)
        self.txt_super_cisco.insert(tk.END, cisco_text)

        # 5. Update Table
        for r in self.tree_super.get_children():
            self.tree_super.delete(r)

        for idx, item in enumerate(res["input_networks"], 1):
            self.tree_super.insert("", "end", values=(
                f"#{idx}",
                item["network_str"],
                item["mask_str"],
                f"{item['first_usable']} - {item['last_usable']}",
                item["broadcast_str"],
                f"{item['block_size']:,} IPs",
                f"Prefix /{s_cidr} Match"
            ))


def main():
    app = NetLabDesktopApp()
    app.mainloop()


if __name__ == "__main__":
    main()
