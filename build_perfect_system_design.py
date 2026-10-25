import os
import sys

# Configure writable matplotlib cache
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), 'reports', '.mplconfig')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, PathPatch
import matplotlib.path as mpath

def create_perfect_diagram():
    # 16:9 widescreen canvas, high resolution 300 DPI
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Pure Solid White Background
    bg_color = "#ffffff"
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # -------------------------------------------------------------
    # COLOR PALETTE (Clean Academic White Theme)
    # -------------------------------------------------------------
    CLR_TITLE_BLUE   = "#1d4ed8"  # Royal blue for '#NETLAB-PRO'
    CLR_TITLE_DARK   = "#0f172a"  # Slate 900 for 'SYSTEM ARCHITECTURE'
    CLR_BORDER_BLUE  = "#2563eb"  # Vibrant blue 600 for card borders
    CLR_BORDER_LIGHT = "#93c5fd"  # Soft blue 300 for sub-cards
    CLR_CARD_BG      = "#f8fafc"  # Slate 50 for primary cards
    CLR_CARD_WHITE   = "#ffffff"  # Pure white for inner cards
    CLR_CARD_BLUE    = "#eff6ff"  # Soft blue 50 for clients
    CLR_TEXT_DARK    = "#0f172a"  # Crisp primary text
    CLR_TEXT_MUTED   = "#475569"  # Secondary text
    CLR_TEXT_LIGHT   = "#64748b"  # Subtitle text
    CLR_ARROW        = "#ea580c"  # High-visibility orange for all connections
    CLR_ARROW_TEXT   = "#c2410c"  # Dark orange for legible text on white
    CLR_DOT          = "#0284c7"  # Connection junction dots
    CLR_DOT_RING     = "#bae6fd"  # Outer ring for junction dots

    # -------------------------------------------------------------
    # HEADER TITLE
    # -------------------------------------------------------------
    ax.text(33, 94.5, "#NETLAB-PRO", ha='right', va='center', 
            fontsize=21, fontweight='bold', color=CLR_TITLE_BLUE, fontfamily='sans-serif')
    ax.text(34.8, 94.5, "—", ha='center', va='center', 
            fontsize=21, fontweight='light', color=CLR_TEXT_LIGHT, fontfamily='sans-serif')
    ax.text(36.6, 94.5, "SYSTEM ARCHITECTURE", ha='left', va='center', 
            fontsize=21, fontweight='bold', color=CLR_TITLE_DARK, fontfamily='sans-serif')

    # Helper: draw box with shadow
    def draw_card(x, y, w, h, title="", subtitle="", bg=CLR_CARD_BG, border=CLR_BORDER_BLUE, lw=1.8, round_size=1.2):
        # Subtle drop shadow
        shadow = FancyBboxPatch((x+0.25, y-0.25), w, h, boxstyle=f"round,pad=0.2,rounding_size={round_size}",
                                facecolor="#e2e8f0", edgecolor="none", alpha=0.6)
        ax.add_patch(shadow)

        box = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.2,rounding_size={round_size}",
                             facecolor=bg, edgecolor=border, linewidth=lw)
        ax.add_patch(box)

        if title:
            lines = title.split("\n")
            if len(lines) == 1:
                ax.text(x + w/2, y + h - 2.8, lines[0], ha='center', va='center',
                        fontsize=10.5, fontweight='bold', color=CLR_TEXT_DARK, fontfamily='sans-serif')
            else:
                ax.text(x + w/2, y + h - 2.2, lines[0], ha='center', va='center',
                        fontsize=10.5, fontweight='bold', color=CLR_TEXT_DARK, fontfamily='sans-serif')
                ax.text(x + w/2, y + h - 4.4, lines[1], ha='center', va='center',
                        fontsize=8.5, fontweight='bold', color=CLR_TEXT_MUTED, fontfamily='sans-serif')

        if subtitle:
            ax.text(x + w/2, y + 2.4, subtitle, ha='center', va='center',
                    fontsize=8, color=CLR_TEXT_LIGHT, fontfamily='sans-serif')
        return box

    # Helper: draw junction dot
    def draw_dot(x, y):
        ax.add_patch(Circle((x, y), 0.65, color=CLR_DOT_RING))
        ax.add_patch(Circle((x, y), 0.42, color=CLR_DOT))
        ax.add_patch(Circle((x, y), 0.18, color="#ffffff"))

    # Helper: draw orange arrow
    def draw_arrow(points, label="", label_pos=(0, 0), align='center', two_way=False):
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        ax.plot(xs, ys, color=CLR_ARROW, lw=2.2, solid_capstyle='round')

        if len(points) >= 2:
            dx = points[-1][0] - points[-2][0]
            dy = points[-1][1] - points[-2][1]
            ax.annotate("", xy=points[-1], xytext=(points[-1][0]-dx*0.01, points[-1][1]-dy*0.01),
                        arrowprops=dict(arrowstyle="->", color=CLR_ARROW, lw=2.2, mutation_scale=14))
            if two_way:
                dx0 = points[1][0] - points[0][0]
                dy0 = points[1][1] - points[0][1]
                ax.annotate("", xy=points[0], xytext=(points[0][0]+dx0*0.01, points[0][1]+dy0*0.01),
                            arrowprops=dict(arrowstyle="->", color=CLR_ARROW, lw=2.2, mutation_scale=14))

        if label:
            lines = label.split("\n")
            if len(lines) == 1:
                ax.text(label_pos[0], label_pos[1], label, ha=align, va='center',
                        fontsize=7.8, fontweight='bold', color=CLR_ARROW_TEXT, fontfamily='sans-serif')
            else:
                ax.text(label_pos[0], label_pos[1] + 0.9, lines[0], ha=align, va='center',
                        fontsize=7.8, fontweight='bold', color=CLR_ARROW_TEXT, fontfamily='sans-serif')
                ax.text(label_pos[0], label_pos[1] - 0.9, lines[1], ha=align, va='center',
                        fontsize=7.8, fontweight='bold', color=CLR_ARROW_TEXT, fontfamily='sans-serif')

    # Helper: draw clean laptop vector icon
    def draw_laptop(cx, cy, has_globe=True):
        # Base
        ax.add_patch(FancyBboxPatch((cx-4.2, cy-1.8), 8.4, 0.7, boxstyle="round,pad=0.1,rounding_size=0.2",
                                   facecolor="#334155", edgecolor="#1e293b", lw=1))
        # Screen frame
        ax.add_patch(FancyBboxPatch((cx-3.2, cy-1.1), 6.4, 4.4, boxstyle="round,pad=0.1,rounding_size=0.3",
                                   facecolor="#0f172a", edgecolor="#1e293b", lw=1))
        # Inner screen display
        ax.add_patch(Rectangle((cx-2.8, cy-0.7), 5.6, 3.6, facecolor="#0284c7"))
        
        if has_globe:
            # Clean globe graphic inside screen
            ax.add_patch(Circle((cx, cy+1.1), 1.2, color="none", ec="#ffffff", lw=1))
            ax.plot([cx-1.2, cx+1.2], [cy+1.1, cy+1.1], color="#ffffff", lw=0.8)
            ax.plot([cx, cx], [cy-0.1, cy+2.3], color="#ffffff", lw=0.8)
        else:
            # Terminal / prompt lines inside screen
            ax.plot([cx-2.2, cx-0.8], [cy+2.1, cy+2.1], color="#ffffff", lw=1.2)
            ax.plot([cx-2.2, cx+1.8], [cy+1.3, cy+1.3], color="#7dd3fc", lw=1)
            ax.plot([cx-2.2, cx+0.5], [cy+0.5, cy+0.5], color="#7dd3fc", lw=1)

    # -------------------------------------------------------------
    # 1. LEFT SIDE: CLIENTS & NETWORK CLOUD
    # -------------------------------------------------------------

    # Peer Client 1 (Top Left)
    draw_card(4, 69, 16, 19, "PEER CLIENT 1\n(WEB BROWSER)", bg=CLR_CARD_BLUE)
    draw_laptop(12, 78, has_globe=True)
    # Chrome browser icon on top-right of laptop
    ax.add_patch(Circle((16, 81), 1.2, color="#ea4335", ec="#ffffff", lw=0.8))
    ax.add_patch(Circle((16, 81), 0.55, color="#4285f4"))
    draw_dot(20, 78.5)

    # Peer Client 2 (Bottom Left)
    draw_card(4, 7, 16, 19, "PEER CLIENT 2\n(WEB BROWSER)", bg=CLR_CARD_BLUE)
    draw_laptop(12, 16, has_globe=False)
    # Edge + Chrome icons
    ax.add_patch(Circle((14.5, 19), 1.1, color="#0284c7", ec="#ffffff", lw=0.8))
    ax.add_patch(Circle((16.8, 19), 1.1, color="#ea4335", ec="#ffffff", lw=0.8))
    ax.add_patch(Circle((16.8, 19), 0.5, color="#4285f4"))
    draw_dot(20, 16.5)

    # Network Cloud (Center Left)
    cloud_w, cloud_h = 16, 9
    cloud_x, cloud_y = 20.5, 44
    c_shadow = FancyBboxPatch((cloud_x+0.3, cloud_y-0.3), cloud_w, cloud_h, boxstyle="round,pad=1.2,rounding_size=3.5",
                              facecolor="#e2e8f0", edgecolor="none", alpha=0.6)
    ax.add_patch(c_shadow)
    cloud = FancyBboxPatch((cloud_x, cloud_y), cloud_w, cloud_h, boxstyle="round,pad=1.2,rounding_size=3.5",
                           facecolor="#f0f9ff", edgecolor=CLR_BORDER_BLUE, linewidth=2.2)
    ax.add_patch(cloud)
    ax.text(cloud_x + cloud_w/2, cloud_y + cloud_h/2 + 1.1, "NETWORK", ha='center', va='center',
            fontsize=12, fontweight='bold', color=CLR_TEXT_DARK, fontfamily='sans-serif')
    ax.text(cloud_x + cloud_w/2, cloud_y + cloud_h/2 - 1.2, "(WI-FI OR INTERNET)", ha='center', va='center',
            fontsize=7.8, fontweight='bold', color=CLR_TEXT_MUTED, fontfamily='sans-serif')

    # Connection Arrows from Clients to Network Cloud
    draw_arrow([(20, 78.5), (25.5, 78.5), (25.5, 54)], 
               label="CONNECTS VIA\nBROWSER URL", label_pos=(28.5, 81), align='left')
    draw_arrow([(20, 16.5), (25.5, 16.5), (25.5, 43)], 
               label="CONNECTS VIA\nBROWSER URL", label_pos=(28.5, 14), align='left')

    # Bidirectional client interactions through network
    draw_arrow([(12, 69), (12, 57), (19.5, 50)], two_way=True)
    draw_arrow([(12, 26), (12, 40), (19.5, 48)], two_way=True)
    ax.text(12, 48, "INTERACTIVE HTTP SESSIONS (VLSM, SUPERNETTING, INVENTORY)",
            ha='center', va='center', fontsize=6.8, fontweight='bold', color=CLR_ARROW_TEXT, rotation=90)

    # -------------------------------------------------------------
    # 2. RIGHT SIDE: HOST MACHINE (WINDOWS 11 / LINUX / RENDER)
    # -------------------------------------------------------------
    host_x, host_y, host_w, host_h = 44, 5, 53, 83

    # Main Host Machine Outer Container
    host_shadow = FancyBboxPatch((host_x+0.35, host_y-0.35), host_w, host_h, boxstyle="round,pad=0.4,rounding_size=1.5",
                                 facecolor="#cbd5e1", edgecolor="none", alpha=0.4)
    ax.add_patch(host_shadow)
    host_box = FancyBboxPatch((host_x, host_y), host_w, host_h, boxstyle="round,pad=0.4,rounding_size=1.5",
                              facecolor="#fcfdfd", edgecolor=CLR_BORDER_BLUE, linewidth=2.2)
    ax.add_patch(host_box)

    # Windows 11 Logo & Header
    wx, wy = host_x + 2.5, host_y + host_h - 4.5
    w_size = 1.3
    w_gap = 0.3
    w_color = "#0284c7"
    ax.add_patch(Rectangle((wx, wy), w_size, w_size, color=w_color))
    ax.add_patch(Rectangle((wx+w_size+w_gap, wy), w_size, w_size, color=w_color))
    ax.add_patch(Rectangle((wx, wy-w_size-w_gap), w_size, w_size, color=w_color))
    ax.add_patch(Rectangle((wx+w_size+w_gap, wy-w_size-w_gap), w_size, w_size, color=w_color))

    ax.text(wx + 4.5, wy - 0.2, "HOST MACHINE (WINDOWS 11 / LINUX / RENDER)", 
            ha='left', va='center', fontsize=12, fontweight='bold', color=CLR_TEXT_DARK, fontfamily='sans-serif')

    # Separator line under header
    ax.plot([host_x + 0.5, host_x + host_w - 0.5], [host_y + host_h - 7.5, host_y + host_h - 7.5], 
            color=CLR_BORDER_LIGHT, lw=1.5)

    # -------------------------------------------------------------
    # 3. INSIDE HOST MACHINE: LEFT BOX -> FLASK BACKEND (SERVER.PY)
    # -------------------------------------------------------------
    fb_x, fb_y, fb_w, fb_h = 46.5, 27, 18, 47
    draw_card(fb_x, fb_y, fb_w, fb_h, "FLASK BACKEND\n(SERVER.PY)", bg=CLR_CARD_BG, border=CLR_BORDER_BLUE)

    # Sub-card 1: Core VLSM Subnetting Service
    draw_card(fb_x + 1.5, fb_y + 24, fb_w - 3, 13, 
              "CAMPUS VLSM &\nSUBNET SERVICE", bg=CLR_CARD_WHITE, border=CLR_BORDER_LIGHT, lw=1.2, round_size=0.8)
    draw_dot(fb_x + 1.5, fb_y + 30.5)

    # Sub-card 2: API Endpoints / Web Server
    draw_card(fb_x + 1.5, fb_y + 8, fb_w - 3, 13, 
              "API ENDPOINTS /\nWEB SERVER", bg=CLR_CARD_WHITE, border=CLR_BORDER_LIGHT, lw=1.2, round_size=0.8)
    draw_dot(fb_x + 1.5, fb_y + 14.5)

    # Sub-card 3: Bottom HTML Templates Box
    draw_card(fb_x, 9, fb_w, 13, "HTML TEMPLATES &\nSTATIC ASSETS", bg=CLR_CARD_BG, border=CLR_BORDER_BLUE)

    # Arrow from Flask to HTML Templates
    draw_arrow([(fb_x + fb_w/2, fb_y), (fb_x + fb_w/2, 22)], 
               label="SERVES\nWEB PAGES", label_pos=(fb_x + fb_w/2 + 2.8, 24.5), align='left')

    # Connections from Network Cloud to Flask Backend
    draw_arrow([(37.5, 50), (48, 50), (48, fb_y + 30.5)], two_way=True)
    ax.text(42, 53, "CAMPUS SUBNET DATA\n(VLSM / SUPERNET / INVENTORY)", 
            ha='center', va='center', fontsize=6.8, fontweight='bold', color=CLR_ARROW_TEXT, fontfamily='sans-serif')

    draw_arrow([(37.5, 47), (48, 47), (48, fb_y + 14.5)], two_way=True)
    ax.text(42, 42.5, "HTTP REST API ENDPOINTS\n(/api/state, /api/supernet)", 
            ha='center', va='center', fontsize=6.8, fontweight='bold', color=CLR_ARROW_TEXT, fontfamily='sans-serif')

    # -------------------------------------------------------------
    # 4. INSIDE HOST MACHINE: RIGHT BOX -> C NETWORK SUBNET ENGINE
    # -------------------------------------------------------------
    cb_x, cb_y, cb_w, cb_h = 74, 15, 21, 59
    draw_card(cb_x, cb_y, cb_w, cb_h, "C NETWORK SIMULATION\nENGINE (NETLAB_CORE.DLL)", bg=CLR_CARD_BG, border=CLR_BORDER_BLUE)

    # Inside C Engine: Vertical Bus line with 4 connection dots
    bus_x = cb_x + 2.5
    ax.plot([bus_x, bus_x], [cb_y + 8, cb_y + 44], color=CLR_BORDER_BLUE, lw=2)

    # 4 Modular Algorithmic Sub-cards
    sub_modules = [
        ("DYNAMIC VLSM\nALLOCATOR", "Greedy Descending Bin-Packing"),
        ("CIDR SUPERNETTING\n& LCP XOR ENGINE", "Contiguity & Prefix Math"),
        ("32-BIT BOOLEAN\nBITWISE ALGEBRA", "Bitwise ANDing & Scope"),
        ("L2 SWITCHING / L3\nROUTING DIAGNOSTICS", "ARP vs Default Gateway")
    ]
    sub_box_h = 9
    sub_box_w = 15
    for i, (title, subtitle) in enumerate(sub_modules):
        s_y = cb_y + 39 - (i * 10.5)
        draw_card(cb_x + 4.5, s_y, sub_box_w, sub_box_h, title, bg=CLR_CARD_WHITE, border=CLR_BORDER_LIGHT, lw=1.2, round_size=0.8)
        draw_dot(bus_x, s_y + sub_box_h/2)
        ax.plot([bus_x, cb_x + 4.5], [s_y + sub_box_h/2, s_y + sub_box_h/2], color=CLR_BORDER_BLUE, lw=1.5)

    # -------------------------------------------------------------
    # 5. INTER-PROCESS COMMUNICATION: FLASK <-> C ENGINE
    # -------------------------------------------------------------
    # Top connector: Flask running on port 5000 -> C Engine
    draw_dot(fb_x + fb_w, fb_y + 38)
    draw_arrow([(fb_x + fb_w, fb_y + 38), (cb_x, fb_y + 38)])
    
    # Pill box for Flask port 5000 with clean red chilli
    pill = FancyBboxPatch((64.2, fb_y + 39.5), 10.2, 5, boxstyle="round,pad=0.2,rounding_size=0.8",
                          facecolor="#fef2f2", edgecolor="#ef4444", linewidth=1.2)
    ax.add_patch(pill)
    ax.text(69.3, fb_y + 42, "FLASK APP ON\nPORT 5000", 
            ha='center', va='center', fontsize=7.2, fontweight='bold', color="#b91c1c", fontfamily='sans-serif')

    # Main Bidirectional Data Bus between Python Backend & C Engine
    draw_dot(fb_x + fb_w, fb_y + 24)
    draw_dot(cb_x, fb_y + 24)
    draw_arrow([(fb_x + fb_w, fb_y + 24), (cb_x, fb_y + 24)], two_way=True)
    ax.text(69.2, fb_y + 26.5, "COMMUNICATES\nCONFIG & DATA\n(CTYPES FFI)", 
            ha='center', va='center', fontsize=7.2, fontweight='bold', color=CLR_ARROW_TEXT, fontfamily='sans-serif')

    # Bottom connector: L2/L3 Diagnostics
    draw_dot(fb_x + fb_w, fb_y + 10)
    draw_dot(cb_x, fb_y + 10)
    draw_arrow([(fb_x + fb_w, fb_y + 10), (cb_x, fb_y + 10)], two_way=True)
    ax.text(69.2, fb_y + 12.5, "BITWISE RESULTS &\nDIAGNOSIS STRING", 
            ha='center', va='center', fontsize=7, color=CLR_TEXT_MUTED, fontfamily='sans-serif')

    plt.tight_layout()

    # Save to high-res PNG, JPG, and pure vector SVG
    output_png = os.path.join(os.path.dirname(__file__), "system_design_architecture.png")
    output_jpg = os.path.join(os.path.dirname(__file__), "system_design_architecture.jpg")
    output_svg = os.path.join(os.path.dirname(__file__), "system_design_architecture.svg")
    output_rep = os.path.join(os.path.dirname(__file__), "reports", "system_design_architecture.png")
    output_pdf = os.path.join(os.path.dirname(__file__), "reports", "system_design_architecture.pdf")

    plt.savefig(output_png, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(output_jpg, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(output_svg, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(output_rep, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(output_pdf, bbox_inches='tight', facecolor=bg_color)

    print(f"[SUCCESS] High-resolution perfect diagram generated:")
    print(f"  - PNG (300 DPI): {output_png}")
    print(f"  - JPG:           {output_jpg}")
    print(f"  - SVG (Vector):  {output_svg}")
    print(f"  - PDF (Vector):  {output_pdf}")

if __name__ == "__main__":
    create_perfect_diagram()
