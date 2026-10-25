import os
import sys

# Configure writable matplotlib cache
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), 'reports', '.mplconfig')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, PathPatch
import matplotlib.path as mpath
import numpy as np

def create_netlab_pro_diagram():
    # 16:9 widescreen canvas, high resolution 300 DPI
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Dark background matching reference image
    bg_color = "#080e1a"
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # -------------------------------------------------------------
    # STYLING CONSTANTS
    # -------------------------------------------------------------
    CYAN_BORDER = "#38bdf8"
    CYAN_GLOW = "#0284c7"
    BOX_BG = "#0d1b2e"
    BOX_BG_DARK = "#091424"
    TEXT_WHITE = "#f8fafc"
    TEXT_CYAN = "#38bdf8"
    TEXT_ORANGE = "#fdba74"
    TEXT_MUTED = "#94a3b8"
    ARROW_ORANGE = "#f97316"
    DOT_CYAN = "#38bdf8"

    # -------------------------------------------------------------
    # TITLE AT TOP
    # -------------------------------------------------------------
    ax.text(32, 94.5, "#NETLAB-PRO", ha='right', va='center', fontsize=20, fontweight='bold', color=TEXT_CYAN)
    ax.text(33.5, 94.5, "—", ha='center', va='center', fontsize=20, fontweight='light', color=TEXT_MUTED)
    ax.text(35, 94.5, "SYSTEM ARCHITECTURE", ha='left', va='center', fontsize=20, fontweight='bold', color=TEXT_WHITE)

    # Helper function for drawing glowing rounded rectangular boxes
    def draw_tech_box(x, y, w, h, title, subtitle="", items=None, bg=BOX_BG, border=CYAN_BORDER, lw=1.8, round_size=1.2):
        # Outer glow effect
        glow = FancyBboxPatch((x-0.2, y-0.2), w+0.4, h+0.4, boxstyle=f"round,pad=0.2,rounding_size={round_size}",
                              facecolor="none", edgecolor=CYAN_GLOW, linewidth=2.5, alpha=0.35)
        ax.add_patch(glow)

        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.2,rounding_size={round_size}",
                             facecolor=bg, edgecolor=border, linewidth=lw)
        ax.add_patch(box)

        if title:
            lines = title.split("\n")
            if len(lines) == 1:
                ax.text(x + w/2, y + h - 2.8, lines[0], ha='center', va='center',
                        fontsize=10.5, fontweight='bold', color=TEXT_WHITE)
            else:
                ax.text(x + w/2, y + h - 2.3, lines[0], ha='center', va='center',
                        fontsize=10.5, fontweight='bold', color=TEXT_WHITE)
                ax.text(x + w/2, y + h - 4.2, lines[1], ha='center', va='center',
                        fontsize=9, color=TEXT_MUTED)

        if subtitle:
            ax.text(x + w/2, y + 2.5, subtitle, ha='center', va='center',
                    fontsize=8.5, color=TEXT_MUTED)

        return box

    def draw_port_dot(x, y):
        glow = plt.Circle((x, y), 0.7, color=CYAN_GLOW, alpha=0.45)
        dot = plt.Circle((x, y), 0.45, color=DOT_CYAN)
        core = plt.Circle((x, y), 0.2, color="#ffffff")
        ax.add_patch(glow)
        ax.add_patch(dot)
        ax.add_patch(core)

    def draw_orange_line_arrow(p1, p2, label="", label_pos=(0, 0), align='center', two_way=False):
        # p1 and p2 can be list of waypoints [(x1,y1), (x2,y2), ...]
        xs = [p[0] for p in p1]
        ys = [p[1] for p in p1]
        ax.plot(xs, ys, color=ARROW_ORANGE, lw=2, solid_capstyle='round')

        # Draw arrowheads
        if len(p1) >= 2:
            dx = p1[-1][0] - p1[-2][0]
            dy = p1[-1][1] - p1[-2][1]
            ax.annotate("", xy=p1[-1], xytext=(p1[-1][0]-dx*0.01, p1[-1][1]-dy*0.01),
                        arrowprops=dict(arrowstyle="->", color=ARROW_ORANGE, lw=2.2, mutation_scale=14))
            if two_way:
                dx0 = p1[1][0] - p1[0][0]
                dy0 = p1[1][1] - p1[0][1]
                ax.annotate("", xy=p1[0], xytext=(p1[0][0]+dx0*0.01, p1[0][1]+dy0*0.01),
                            arrowprops=dict(arrowstyle="->", color=ARROW_ORANGE, lw=2.2, mutation_scale=14))

        if label:
            ax.text(label_pos[0], label_pos[1], label, ha=align, va='center',
                    fontsize=7.8, fontweight='bold', color=TEXT_ORANGE)

    # -------------------------------------------------------------
    # LEFT COLUMN: CLIENTS & NETWORK CLOUD
    # -------------------------------------------------------------

    # Client 1 (Top Left)
    draw_tech_box(4, 69, 16, 19, "PEER CLIENT 1\n(WEB BROWSER)")
    # Draw simple laptop icon
    lap_x, lap_y = 12, 78
    ax.plot([lap_x-3, lap_x+3, lap_x+2.4, lap_x-2.4, lap_x-3], 
            [lap_y-1.5, lap_y-1.5, lap_y+2.2, lap_y+2.2, lap_y-1.5], color=TEXT_CYAN, lw=1.5)
    ax.plot([lap_x-4, lap_x+4], [lap_y-1.6, lap_y-1.6], color=TEXT_WHITE, lw=2)
    # Globe / Web icon inside laptop
    ax.add_patch(plt.Circle((lap_x, lap_y+0.4), 1.2, color="none", ec=TEXT_CYAN, lw=1))
    ax.plot([lap_x-1.2, lap_x+1.2], [lap_y+0.4, lap_y+0.4], color=TEXT_CYAN, lw=0.8)
    ax.plot([lap_x, lap_x], [lap_y-0.8, lap_y+1.6], color=TEXT_CYAN, lw=0.8)
    # Chrome browser badge
    ax.add_patch(plt.Circle((lap_x+4, lap_y+2.5), 1.3, color="#ea4335", ec="#ffffff", lw=0.5))
    ax.add_patch(plt.Circle((lap_x+4, lap_y+2.5), 0.6, color="#4285f4"))
    draw_port_dot(20, 78.5)

    # Client 2 (Bottom Left)
    draw_tech_box(4, 7, 16, 19, "PEER CLIENT 2\n(WEB BROWSER)")
    lap2_y = 16
    ax.plot([lap_x-3, lap_x+3, lap_x+2.4, lap_x-2.4, lap_x-3], 
            [lap2_y-1.5, lap2_y-1.5, lap2_y+2.2, lap2_y+2.2, lap2_y-1.5], color=TEXT_CYAN, lw=1.5)
    ax.plot([lap_x-4, lap_x+4], [lap2_y-1.6, lap2_y-1.6], color=TEXT_WHITE, lw=2)
    # Edge browser badge
    ax.add_patch(plt.Circle((lap_x-1, lap2_y+0.4), 1.2, color="#0ea5e9", ec="#ffffff", lw=0.5))
    ax.add_patch(plt.Circle((lap_x+4, lap2_y+2.5), 1.3, color="#ea4335", ec="#ffffff", lw=0.5))
    ax.add_patch(plt.Circle((lap_x+4, lap2_y+2.5), 0.6, color="#4285f4"))
    draw_port_dot(20, 16.5)

    # Center: Network Cloud Box
    cloud_w, cloud_h = 16, 9
    cloud_x, cloud_y = 20, 44
    cloud = FancyBboxPatch((cloud_x, cloud_y), cloud_w, cloud_h, boxstyle="round,pad=1.2,rounding_size=3.5",
                           facecolor="#0c203b", edgecolor=CYAN_BORDER, linewidth=2)
    ax.add_patch(cloud)
    ax.text(cloud_x + cloud_w/2, cloud_y + cloud_h/2 + 0.9, "NETWORK", ha='center', va='center',
            fontsize=11, fontweight='bold', color=TEXT_WHITE)
    ax.text(cloud_x + cloud_w/2, cloud_y + cloud_h/2 - 1.2, "(WI-FI OR INTERNET)", ha='center', va='center',
            fontsize=7.8, fontweight='bold', color=TEXT_MUTED)

    # Orange Connections from Clients to Cloud
    draw_orange_line_arrow([(20, 78.5), (25, 78.5), (25, 54)], [], 
                           "CONNECTS VIA\nBROWSER URL", (28, 81), align='left')
    draw_orange_line_arrow([(20, 16.5), (25, 16.5), (25, 43)], [], 
                           "CONNECTS VIA\nBROWSER URL", (28, 14), align='left')

    # Bidirectional client interconnections through network
    draw_orange_line_arrow([(12, 69), (12, 57), (19, 50)], [], two_way=True)
    draw_orange_line_arrow([(12, 26), (12, 40), (19, 48)], [], two_way=True)
    ax.text(12, 48, "INTERACTIVE HTTP / WEBSOCKET SESSIONS\n(VLSM SETUP, WORKSTATIONS, SUPERNETTING)",
            ha='center', va='center', fontsize=6.8, fontweight='bold', color=TEXT_ORANGE, rotation=90)

    # -------------------------------------------------------------
    # RIGHT SIDE: HOST MACHINE (WINDOWS 11)
    # -------------------------------------------------------------
    host_x, host_y, host_w, host_h = 44, 5, 53, 83
    # Main Host Machine Outer Container
    host_glow = FancyBboxPatch((host_x-0.3, host_y-0.3), host_w+0.6, host_h+0.6, boxstyle="round,pad=0.4,rounding_size=1.5",
                               facecolor="none", edgecolor=CYAN_GLOW, linewidth=3, alpha=0.35)
    ax.add_patch(host_glow)
    host_box = FancyBboxPatch((host_x, host_y), host_w, host_h, boxstyle="round,pad=0.4,rounding_size=1.5",
                              facecolor=BOX_BG_DARK, edgecolor=CYAN_BORDER, linewidth=2)
    ax.add_patch(host_box)

    # Windows 11 Logo & Header
    # Draw 4 blue squares for Windows logo
    wx, wy = host_x + 2.5, host_y + host_h - 4.5
    w_size = 1.3
    w_gap = 0.3
    w_color = "#00a4ef"
    ax.add_patch(patches.Rectangle((wx, wy), w_size, w_size, color=w_color))
    ax.add_patch(patches.Rectangle((wx+w_size+w_gap, wy), w_size, w_size, color=w_color))
    ax.add_patch(patches.Rectangle((wx, wy-w_size-w_gap), w_size, w_size, color=w_color))
    ax.add_patch(patches.Rectangle((wx+w_size+w_gap, wy-w_size-w_gap), w_size, w_size, color=w_color))

    ax.text(wx + 4.5, wy - 0.2, "HOST MACHINE (WINDOWS 11 / LINUX / RENDER)", 
            ha='left', va='center', fontsize=12, fontweight='bold', color=TEXT_WHITE)

    # Separator line under header
    ax.plot([host_x + 0.5, host_x + host_w - 0.5], [host_y + host_h - 7.5, host_y + host_h - 7.5], 
            color=CYAN_BORDER, lw=1.2)

    # -------------------------------------------------------------
    # INSIDE HOST MACHINE: LEFT INNER BOX -> FLASK BACKEND (SERVER.PY)
    # -------------------------------------------------------------
    fb_x, fb_y, fb_w, fb_h = 46.5, 27, 18, 47
    draw_tech_box(fb_x, fb_y, fb_w, fb_h, "FLASK BACKEND\n(SERVER.PY)", bg="#0a182d")

    # Sub-card 1: Core Subnetting Service
    draw_tech_box(fb_x + 1.5, fb_y + 24, fb_w - 3, 13, 
                  "CAMPUS VLSM &\nSUBNET SERVICE", bg="#0f233f", lw=1.2, round_size=0.8)
    draw_port_dot(fb_x + 1.5, fb_y + 30.5)

    # Sub-card 2: API Endpoints / Web Server
    draw_tech_box(fb_x + 1.5, fb_y + 8, fb_w - 3, 13, 
                  "API ENDPOINTS /\nWEB SERVER", bg="#0f233f", lw=1.2, round_size=0.8)
    draw_port_dot(fb_x + 1.5, fb_y + 14.5)

    # Sub-card 3: Bottom HTML Templates Box
    draw_tech_box(fb_x, 9, fb_w, 13, "HTML TEMPLATES &\nSTATIC ASSETS", bg="#0a182d")

    # Arrow from Flask to HTML Templates
    draw_orange_line_arrow([(fb_x + fb_w/2, fb_y), (fb_x + fb_w/2, 22)], [], 
                           "SERVES\nWEB PAGES", (fb_x + fb_w/2 + 2.5, 24.5), align='left')

    # Connections from Network Cloud to Flask Backend
    draw_orange_line_arrow([(37, 50), (48, 50), (48, fb_y + 30.5)], [], two_way=True)
    ax.text(42, 53, "CAMPUS SUBNET DATA\n(VLSM / SUPERNETTING / INVENTORY)", 
            ha='center', va='center', fontsize=6.8, fontweight='bold', color=TEXT_ORANGE)

    draw_orange_line_arrow([(37, 47), (48, 47), (48, fb_y + 14.5)], [], two_way=True)
    ax.text(42, 42.5, "HTTP REST API ENDPOINTS\n(/api/state, /api/supernet)", 
            ha='center', va='center', fontsize=6.8, fontweight='bold', color=TEXT_ORANGE)

    # -------------------------------------------------------------
    # INSIDE HOST MACHINE: RIGHT INNER BOX -> C NATIVE CORE ENGINE
    # -------------------------------------------------------------
    cb_x, cb_y, cb_w, cb_h = 74, 15, 21, 59
    draw_tech_box(cb_x, cb_y, cb_w, cb_h, "C NETWORK SUBNET\nENGINE (NETLAB_CORE.DLL)", bg="#0a182d")

    # Inside C Engine: Vertical Bus line with 4 glowing dots
    bus_x = cb_x + 2.5
    ax.plot([bus_x, bus_x], [cb_y + 8, cb_y + 44], color=CYAN_BORDER, lw=1.8)

    # 4 Modular Algorithmic Sub-cards
    sub_titles = [
        "DYNAMIC VLSM\nALLOCATOR",
        "CIDR SUPERNETTING\n& LCP XOR ENGINE",
        "32-BIT BOOLEAN\nBITWISE ALGEBRA",
        "L2 SWITCHING / L3\nROUTING DIAGNOSTICS"
    ]
    sub_box_h = 9
    sub_box_w = 15
    for i, title in enumerate(sub_titles):
        s_y = cb_y + 39 - (i * 10.5)
        draw_tech_box(cb_x + 4.5, s_y, sub_box_w, sub_box_h, title, bg="#0f233f", lw=1.2, round_size=0.8)
        draw_port_dot(bus_x, s_y + sub_box_h/2)
        ax.plot([bus_x, cb_x + 4.5], [s_y + sub_box_h/2, s_y + sub_box_h/2], color=CYAN_BORDER, lw=1.5)

    # -------------------------------------------------------------
    # INTER-PROCESS COMMUNICATION: FLASK <-> C ENGINE
    # -------------------------------------------------------------
    # Top connector: Flask running on port 5000 -> C Engine
    draw_port_dot(fb_x + fb_w, fb_y + 38)
    draw_orange_line_arrow([(fb_x + fb_w, fb_y + 38), (cb_x, fb_y + 38)], [])
    # Flask chilli icon / pill
    ax.text(69.2, fb_y + 42, "FLASK APPLICATION\nRUNNING ON\nPORT 5000", 
            ha='center', va='center', fontsize=7.2, fontweight='bold', color=TEXT_WHITE)
    # Draw small flame / chilli
    ax.text(64.5, fb_y + 42, "🌶️", ha='center', va='center', fontsize=11)

    # Main Bidirectional Data Bus between Python Backend & C Engine
    draw_port_dot(fb_x + fb_w, fb_y + 24)
    draw_port_dot(cb_x, fb_y + 24)
    draw_orange_line_arrow([(fb_x + fb_w, fb_y + 24), (cb_x, fb_y + 24)], [], two_way=True)
    ax.text(69.2, fb_y + 26.5, "COMMUNICATES\nCONFIG & DATA\n(CTYPES FFI)", 
            ha='center', va='center', fontsize=7.2, fontweight='bold', color=TEXT_ORANGE)

    # Bottom connector: L2/L3 Diagnostics
    draw_port_dot(fb_x + fb_w, fb_y + 10)
    draw_port_dot(cb_x, fb_y + 10)
    draw_orange_line_arrow([(fb_x + fb_w, fb_y + 10), (cb_x, fb_y + 10)], [], two_way=True)
    ax.text(69.2, fb_y + 12.5, "BITWISE RESULTS &\nDIAGNOSIS STRING", 
            ha='center', va='center', fontsize=7, color=TEXT_MUTED)

    # Bottom Right Sparkle Icon matching reference image
    ax.text(93.5, 8.5, "✦", ha='center', va='center', fontsize=18, color=CYAN_BORDER, alpha=0.6)

    plt.tight_layout()
    output_png = os.path.join(os.path.dirname(__file__), "system_design_architecture.png")
    output_jpg = os.path.join(os.path.dirname(__file__), "system_design_architecture.jpg")
    output_netconf_style = os.path.join(os.path.dirname(__file__), "reports", "system_design_netconf_style.png")

    plt.savefig(output_png, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(output_jpg, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(output_netconf_style, dpi=300, bbox_inches='tight', facecolor=bg_color)

    print(f"[SUCCESS] NetConf-style System Design diagram generated at 300 DPI:")
    print(f"  - {output_png}")
    print(f"  - {output_jpg}")
    print(f"  - {output_netconf_style}")

if __name__ == "__main__":
    create_netlab_pro_diagram()
