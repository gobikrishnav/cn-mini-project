import os
import sys

# Configure writable matplotlib cache
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), 'reports', '.mplconfig')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon

def draw_campus_network_topology():
    # 16:10 widescreen high-resolution canvas
    fig, ax = plt.subplots(figsize=(16, 11), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Pure White Background for Academic Report
    bg_color = "#ffffff"
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # -------------------------------------------------------------
    # COLOR PALETTE
    # -------------------------------------------------------------
    CLR_HEADER_BG   = "#0f172a"
    CLR_ROUTER      = "#2563eb"  # Blue for Routers
    CLR_CORE_SW     = "#0284c7"  # Cyan/Blue for L3 Core Switch
    CLR_DIST_SW     = "#059669"  # Emerald for Distribution Switches
    CLR_ACCESS_SW   = "#4f46e5"  # Indigo for Access Layer Switches
    CLR_PC          = "#0f172a"  # Slate dark for workstations
    CLR_TRUNK       = "#dc2626"  # Red for 802.1Q Trunks
    CLR_ACCESS_LINK = "#2563eb"  # Blue for Access links
    CLR_TEXT_DARK   = "#0f172a"
    CLR_TEXT_MUTED  = "#475569"
    CLR_CARD_BG     = "#f8fafc"
    CLR_CARD_BORDER = "#cbd5e1"

    # -------------------------------------------------------------
    # HEADER BANNER
    # -------------------------------------------------------------
    header = FancyBboxPatch((3, 91), 94, 7, boxstyle="round,pad=0.4,rounding_size=1.2",
                            facecolor=CLR_HEADER_BG, edgecolor="none")
    ax.add_patch(header)
    ax.text(50, 95.5, "CAMPUS NETWORK PHYSICAL & LOGICAL TOPOLOGY DESIGN", 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#ffffff', fontfamily='sans-serif')
    ax.text(50, 92.6, "Course: 23AD551 - Computer Networking Laboratory | NetLab-Pro 4-Tier Hierarchical Infrastructure", 
            ha='center', va='center', fontsize=10, color='#94a3b8', fontfamily='sans-serif')

    # Helper: draw Cisco Router Cylinder
    def draw_router(cx, cy, name, ip_label=""):
        # Shadow
        ax.add_patch(Circle((cx+0.2, cy-0.2), 3.2, color="#e2e8f0"))
        # Main circle
        ax.add_patch(Circle((cx, cy), 3.2, facecolor="#eff6ff", edgecolor=CLR_ROUTER, lw=2.2))
        # 4 inward/outward arrows (Cisco Router symbol)
        arr_len = 1.6
        ax.annotate("", xy=(cx-arr_len, cy), xytext=(cx+arr_len, cy),
                    arrowprops=dict(arrowstyle="<->", color=CLR_ROUTER, lw=2, mutation_scale=12))
        ax.annotate("", xy=(cx, cy-arr_len), xytext=(cx, cy+arr_len),
                    arrowprops=dict(arrowstyle="<->", color=CLR_ROUTER, lw=2, mutation_scale=12))
        
        ax.text(cx, cy - 4.4, name, ha='center', va='top', fontsize=9.5, fontweight='bold', color=CLR_TEXT_DARK)
        if ip_label:
            ax.text(cx, cy - 6.2, ip_label, ha='center', va='top', fontsize=8, color=CLR_ROUTER, fontweight='bold')

    # Helper: draw Cisco Layer-3 Core Switch (Double square with crossed arrows)
    def draw_l3_switch(cx, cy, name, ip_label=""):
        w, h = 10, 4.8
        # Shadow
        ax.add_patch(FancyBboxPatch((cx-w/2+0.2, cy-h/2-0.2), w, h, boxstyle="round,pad=0.2,rounding_size=0.6",
                                    facecolor="#e2e8f0", edgecolor="none"))
        # Main box
        ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.2,rounding_size=0.6",
                                    facecolor="#f0f9ff", edgecolor=CLR_CORE_SW, lw=2.2))
        # Layer 3 Cross Arrows
        ax.annotate("", xy=(cx-3.2, cy), xytext=(cx+3.2, cy),
                    arrowprops=dict(arrowstyle="<->", color=CLR_CORE_SW, lw=1.8, mutation_scale=10))
        ax.annotate("", xy=(cx, cy-1.4), xytext=(cx, cy+1.4),
                    arrowprops=dict(arrowstyle="<->", color=CLR_CORE_SW, lw=1.8, mutation_scale=10))
        ax.text(cx, cy - 3.4, name, ha='center', va='top', fontsize=9.5, fontweight='bold', color=CLR_TEXT_DARK)
        if ip_label:
            ax.text(cx, cy - 5.2, ip_label, ha='center', va='top', fontsize=8, color=CLR_CORE_SW, fontweight='bold')

    # Helper: draw Layer-2 Switch
    def draw_l2_switch(cx, cy, name, label=""):
        w, h = 8.5, 3.8
        ax.add_patch(FancyBboxPatch((cx-w/2+0.2, cy-h/2-0.2), w, h, boxstyle="round,pad=0.2,rounding_size=0.5",
                                    facecolor="#e2e8f0", edgecolor="none"))
        ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h, boxstyle="round,pad=0.2,rounding_size=0.5",
                                    facecolor="#f8fafc", edgecolor=CLR_ACCESS_SW, lw=2))
        # 4 parallel switch arrows
        ax.annotate("", xy=(cx-2.2, cy+0.7), xytext=(cx+2.2, cy+0.7),
                    arrowprops=dict(arrowstyle="->", color=CLR_ACCESS_SW, lw=1.2, mutation_scale=8))
        ax.annotate("", xy=(cx+2.2, cy-0.7), xytext=(cx-2.2, cy-0.7),
                    arrowprops=dict(arrowstyle="->", color=CLR_ACCESS_SW, lw=1.2, mutation_scale=8))
        ax.text(cx, cy - 2.8, name, ha='center', va='top', fontsize=8.8, fontweight='bold', color=CLR_TEXT_DARK)
        if label:
            ax.text(cx, cy - 4.4, label, ha='center', va='top', fontsize=7.5, color=CLR_TEXT_MUTED)

    # Helper: draw PC Workstation Icon
    def draw_pc(cx, cy, name, ip=""):
        # Monitor
        ax.add_patch(FancyBboxPatch((cx-1.6, cy-0.4), 3.2, 2.2, boxstyle="round,pad=0.1,rounding_size=0.2",
                                    facecolor="#ffffff", edgecolor=CLR_PC, lw=1.2))
        ax.add_patch(Rectangle((cx-1.4, cy-0.2), 2.8, 1.8, facecolor="#0284c7"))
        # Stand & Base
        ax.plot([cx, cx], [cy-0.4, cy-0.9], color=CLR_PC, lw=1.5)
        ax.plot([cx-1.2, cx+1.2], [cy-0.9, cy-0.9], color=CLR_PC, lw=2)
        ax.text(cx, cy - 1.6, name, ha='center', va='top', fontsize=7.5, fontweight='bold', color=CLR_TEXT_DARK)
        if ip:
            ax.text(cx, cy - 2.8, ip, ha='center', va='top', fontsize=6.8, color="#2563eb", fontfamily='monospace')

    # -------------------------------------------------------------
    # TIER 1: INTERNET / WAN CLOUD & BORDER ROUTER (Top)
    # -------------------------------------------------------------
    # ISP Cloud
    cloud_w, cloud_h = 16, 7
    cloud_x, cloud_y = 15, 80
    ax.add_patch(FancyBboxPatch((cloud_x+0.3, cloud_y-0.3), cloud_w, cloud_h, boxstyle="round,pad=0.8,rounding_size=2.5",
                                facecolor="#e2e8f0", edgecolor="none"))
    ax.add_patch(FancyBboxPatch((cloud_x, cloud_y), cloud_w, cloud_h, boxstyle="round,pad=0.8,rounding_size=2.5",
                                facecolor="#f0fdf4", edgecolor="#16a34a", lw=2))
    ax.text(cloud_x + cloud_w/2, cloud_y + cloud_h/2 + 0.8, "INTERNET / ISP", ha='center', va='center',
            fontsize=11, fontweight='bold', color="#166534")
    ax.text(cloud_x + cloud_w/2, cloud_y + cloud_h/2 - 1.2, "Public Gateway (203.0.113.1)", ha='center', va='center',
            fontsize=7.5, color="#15803d")

    # Border Gateway Router
    r_x, r_y = 50, 83.5
    draw_router(r_x, r_y, "Border Gateway Router", "Cisco 2911 (WAN)")

    # Line from ISP Cloud to Border Router
    ax.plot([cloud_x + cloud_w, r_x - 3.2], [cloud_y + cloud_h/2, r_y], color="#16a34a", lw=2.2, ls="--")
    ax.text(39, 84.8, "Serial / WAN Link", ha='center', va='bottom', fontsize=7.5, fontweight='bold', color="#16a34a")

    # DHCP & Network Management Server (Top Right)
    srv_x, srv_y = 80, 83.5
    srv_box = FancyBboxPatch((srv_x-6, srv_y-3.5), 12, 6, boxstyle="round,pad=0.3,rounding_size=0.6",
                             facecolor="#fefce8", edgecolor="#ca8a04", lw=1.8)
    ax.add_patch(srv_box)
    ax.text(srv_x, srv_y + 1.2, "DHCP & DNS SERVER", ha='center', va='center', fontsize=8.5, fontweight='bold', color="#854d0e")
    ax.text(srv_x, srv_y - 0.4, "IP: 192.168.0.2 /24", ha='center', va='center', fontsize=7.8, color="#713f12", fontfamily='monospace')
    ax.text(srv_x, srv_y - 1.8, "VLAN 99 (Management)", ha='center', va='center', fontsize=7.2, color="#a16207")

    # -------------------------------------------------------------
    # TIER 2: ENTERPRISE LAYER-3 CORE SWITCH
    # -------------------------------------------------------------
    c_x, c_y = 50, 68
    draw_l3_switch(c_x, c_y, "Campus Core L3 Switch", "Cisco Catalyst 3850 (SVI Gateway)")

    # Trunk from Router to Core Switch
    ax.plot([r_x, c_x], [r_y - 3.2, c_y + 2.4], color=CLR_TRUNK, lw=2.5)
    ax.text(50.5, 75, "Gig0/0 Trunk\n(Point-to-Point)", ha='left', va='center', fontsize=7.5, fontweight='bold', color=CLR_TRUNK)

    # Link from Core Switch to Server
    ax.plot([c_x + 5, srv_x], [c_y + 1, srv_y - 3.5], color=CLR_ACCESS_LINK, lw=1.8, ls=":")
    ax.text(67, 72, "VLAN 99 Trunk", ha='center', va='center', fontsize=7.2, color=CLR_ACCESS_LINK)

    # SVI Gateways Card on Core Switch
    svi_box = FancyBboxPatch((2, 63), 32, 11, boxstyle="round,pad=0.4,rounding_size=0.8",
                             facecolor="#eff6ff", edgecolor=CLR_CORE_SW, lw=1.5)
    ax.add_patch(svi_box)
    ax.text(18, 71.5, "INTER-VLAN SVI GATEWAY INTERFACES", ha='center', va='center', 
            fontsize=8.5, fontweight='bold', color="#0369a1")
    ax.text(4, 69, "• SVI Vlan 10: 192.168.0.1/26 (Networks Lab GW)", ha='left', va='center', fontsize=7.5, fontfamily='monospace', color=CLR_TEXT_DARK)
    ax.text(4, 66.8, "• SVI Vlan 20: 192.168.0.65/26 (Web Tech Lab GW)", ha='left', va='center', fontsize=7.5, fontfamily='monospace', color=CLR_TEXT_DARK)
    ax.text(4, 64.6, "• SVI Vlan 30: 192.168.0.129/27 (IoT Systems GW)", ha='left', va='center', fontsize=7.5, fontfamily='monospace', color=CLR_TEXT_DARK)

    ax.plot([34, c_x - 5], [68, 68], color=CLR_CORE_SW, lw=1.5, ls="--")

    # -------------------------------------------------------------
    # TIER 3: DISTRIBUTION LAYER SWITCHES (Academic Blocks)
    # -------------------------------------------------------------
    d1_x, d1_y = 25, 48
    d2_x, d2_y = 50, 48
    d3_x, d3_y = 75, 48

    draw_l2_switch(d1_x, d1_y, "Distribution SW 1", "Block A (CSE Wing)")
    draw_l2_switch(d2_x, d2_y, "Distribution SW 2", "Block B (IT Wing)")
    draw_l2_switch(d3_x, d3_y, "Distribution SW 3", "Block C (AI & ECE)")

    # 802.1Q Trunks from Core Switch to Distribution Switches
    ax.plot([c_x - 4, d1_x], [c_y - 2.4, d1_y + 1.9], color=CLR_TRUNK, lw=2)
    ax.plot([c_x, d2_x], [c_y - 2.4, d2_y + 1.9], color=CLR_TRUNK, lw=2)
    ax.plot([c_x + 4, d3_x], [c_y - 2.4, d3_y + 1.9], color=CLR_TRUNK, lw=2)

    ax.text(34, 57, "802.1Q Trunk", ha='center', va='center', fontsize=7.5, fontweight='bold', color=CLR_TRUNK, rotation=35)
    ax.text(50.8, 56, "802.1Q Trunk", ha='left', va='center', fontsize=7.5, fontweight='bold', color=CLR_TRUNK)
    ax.text(66, 57, "802.1Q Trunk", ha='center', va='center', fontsize=7.5, fontweight='bold', color=CLR_TRUNK, rotation=-35)

    # -------------------------------------------------------------
    # TIER 4: ACCESS LAYER SWITCHES & CAMPUS LAB VLANs
    # -------------------------------------------------------------

    def draw_lab_vlan_box(x, y, w, h, vlan_title, subnet_info, lab_color, pcs_count, sample_pcs):
        # Card container
        shadow = FancyBboxPatch((x+0.3, y-0.3), w, h, boxstyle="round,pad=0.3,rounding_size=0.8",
                                facecolor="#e2e8f0", edgecolor="none")
        ax.add_patch(shadow)
        card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=0.8",
                              facecolor="#ffffff", edgecolor=lab_color, lw=2)
        ax.add_patch(card)

        # Header tag
        tag = FancyBboxPatch((x+1, y+h-3.2), w-2, 2.5, boxstyle="round,pad=0.1,rounding_size=0.4",
                             facecolor=lab_color, edgecolor="none")
        ax.add_patch(tag)
        ax.text(x + w/2, y + h - 1.9, vlan_title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color="#ffffff")

        # Subnet parameters inside card
        curr_y = y + h - 4.5
        for line in subnet_info:
            ax.text(x + 1.5, curr_y, line, ha='left', va='center', 
                    fontsize=7.6, color=CLR_TEXT_DARK, fontfamily='monospace')
            curr_y -= 1.8

        # Access switch icon inside card
        asw_x, asw_y = x + w/2, curr_y - 2.5
        draw_l2_switch(asw_x, asw_y, "Access SW (Cisco 2960)", f"24 Ports | {pcs_count} Active Hosts")

        # PCs at bottom of card
        pc_y = y + 5
        for i, (pc_name, pc_ip) in enumerate(sample_pcs):
            pc_x = x + 3.8 + (i * 7.5)
            draw_pc(pc_x, pc_y, pc_name, pc_ip)
            # Link line from access switch to PC
            ax.plot([asw_x, pc_x], [asw_y - 1.9, pc_y + 1.8], color="#94a3b8", lw=1.2)

        # Access link indicator
        ax.text(x + w/2, y + 1.2, f"DHCP Auto-Assigned Fleet: {pcs_count} PCs", 
                ha='center', va='center', fontsize=7.2, fontweight='bold', color=lab_color)

    # LAB 1: COMPUTER NETWORKS LAB (VLAN 10)
    lab1_w, lab1_h = 28, 35
    lab1_x, lab1_y = 4, 4
    draw_lab_vlan_box(lab1_x, lab1_y, lab1_w, lab1_h,
                      "VLAN 10: COMPUTER NETWORKS LAB",
                      [
                          "Subnet:  192.168.0.0 /26",
                          "Mask:    255.255.255.192",
                          "Gateway: 192.168.0.1 (SVI)",
                          "Range:   192.168.0.2 - .62",
                          "Hosts:   60 PCs (Capacity 62)"
                      ],
                      "#0284c7", 60,
                      [("CN-WS01", ".2"), ("CN-WS02", ".3"), ("CN-WS60", ".61")])

    # Connect Distribution 1 to Lab 1 Access Switch
    ax.plot([d1_x, lab1_x + lab1_w/2], [d1_y - 1.9, lab1_y + lab1_h], color=CLR_TRUNK, lw=2)

    # LAB 2: WEB TECHNOLOGIES LAB (VLAN 20)
    lab2_w, lab2_h = 28, 35
    lab2_x, lab2_y = 36, 4
    draw_lab_vlan_box(lab2_x, lab2_y, lab2_w, lab2_h,
                      "VLAN 20: WEB TECHNOLOGIES LAB",
                      [
                          "Subnet:  192.168.0.64 /26",
                          "Mask:    255.255.255.192",
                          "Gateway: 192.168.0.65 (SVI)",
                          "Range:   192.168.0.66 - .126",
                          "Hosts:   40 PCs (Capacity 62)"
                      ],
                      "#059669", 40,
                      [("WT-WS01", ".66"), ("WT-WS02", ".67"), ("WT-WS40", ".105")])

    # Connect Distribution 2 to Lab 2 Access Switch
    ax.plot([d2_x, lab2_x + lab2_w/2], [d2_y - 1.9, lab2_y + lab2_h], color=CLR_TRUNK, lw=2)

    # LAB 3: IOT & EMBEDDED SYSTEMS LAB (VLAN 30)
    lab3_w, lab3_h = 28, 35
    lab3_x, lab3_y = 68, 4
    draw_lab_vlan_box(lab3_x, lab3_y, lab3_w, lab3_h,
                      "VLAN 30: IOT & EMBEDDED SYSTEMS LAB",
                      [
                          "Subnet:  192.168.0.128 /27",
                          "Mask:    255.255.255.224",
                          "Gateway: 192.168.0.129 (SVI)",
                          "Range:   192.168.0.130 - .158",
                          "Hosts:   25 PCs (Capacity 30)"
                      ],
                      "#7c3aed", 25,
                      [("IOT-WS01", ".130"), ("IOT-WS02", ".131"), ("IOT-WS25", ".154")])

    # Connect Distribution 3 to Lab 3 Access Switch
    ax.plot([d3_x, lab3_x + lab3_w/2], [d3_y - 1.9, lab3_y + lab3_h], color=CLR_TRUNK, lw=2)

    # -------------------------------------------------------------
    # SUPERNET ROUTE SUMMARIZATION CALLOUT (Connecting Lab 1 & 2)
    # -------------------------------------------------------------
    sup_callout = FancyBboxPatch((18, 40), 32, 4.5, boxstyle="round,pad=0.2,rounding_size=0.5",
                                 facecolor="#fefce8", edgecolor="#ca8a04", lw=1.5, ls="--")
    ax.add_patch(sup_callout)
    ax.text(34, 42.8, "CIDR SUPERNET SUMMARIZATION", ha='center', va='center', 
            fontsize=7.8, fontweight='bold', color="#854d0e")
    ax.text(34, 41.2, "Merge VLAN 10 + 20: 192.168.0.0/25 (128 IPs, 0 Gaps)", ha='center', va='center', 
            fontsize=7, color="#713f12", fontfamily='monospace')

    # Legend / Key in bottom right of Core area
    leg_box = FancyBboxPatch((68, 62), 30, 9, boxstyle="round,pad=0.3,rounding_size=0.6",
                             facecolor="#f8fafc", edgecolor="#94a3b8", lw=1)
    ax.add_patch(leg_box)
    ax.text(83, 68.8, "TOPOLOGY LEGEND / KEY", ha='center', va='center', fontsize=8, fontweight='bold', color=CLR_TEXT_DARK)
    
    # Red line for Trunk
    ax.plot([70, 75], [66.5, 66.5], color=CLR_TRUNK, lw=2.5)
    ax.text(76, 66.5, "802.1Q VLAN Trunk Line", ha='left', va='center', fontsize=7.2, color=CLR_TEXT_DARK)

    # Green dashed for WAN
    ax.plot([70, 75], [64.2, 64.2], color="#16a34a", lw=2, ls="--")
    ax.text(76, 64.2, "WAN / Internet Uplink", ha='left', va='center', fontsize=7.2, color=CLR_TEXT_DARK)

    # Blue for Access
    ax.plot([70, 75], [62.2, 62.2], color=CLR_ACCESS_LINK, lw=1.5)
    ax.text(76, 62.2, "1000Base-T Access Link", ha='left', va='center', fontsize=7.2, color=CLR_TEXT_DARK)

    # Figure Caption at Bottom
    ax.text(50, 1.2, "Figure 2.1: Campus Network Physical & Logical 4-Tier Topology with Dynamic VLSM Subnetting", 
            ha='center', va='center', fontsize=11, fontweight='bold', color="#1e293b", fontfamily='sans-serif')

    plt.tight_layout()

    # Save to high-res PNG, JPG, and pure vector PDF / SVG
    out_png = os.path.join(os.path.dirname(__file__), "system_design_topology.png")
    out_jpg = os.path.join(os.path.dirname(__file__), "system_design_topology.jpg")
    out_svg = os.path.join(os.path.dirname(__file__), "system_design_topology.svg")
    out_pdf = os.path.join(os.path.dirname(__file__), "reports", "system_design_topology.pdf")
    out_arch_png = os.path.join(os.path.dirname(__file__), "system_design_architecture.png")
    out_arch_jpg = os.path.join(os.path.dirname(__file__), "system_design_architecture.jpg")

    plt.savefig(out_png, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(out_jpg, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(out_svg, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(out_pdf, bbox_inches='tight', facecolor=bg_color)
    # Also update system_design_architecture files directly so user's main image is updated
    plt.savefig(out_arch_png, dpi=300, bbox_inches='tight', facecolor=bg_color)
    plt.savefig(out_arch_jpg, dpi=300, bbox_inches='tight', facecolor=bg_color)

    print(f"[SUCCESS] Campus Network Topology Diagram generated successfully at 300 DPI:")
    print(f"  - PNG: {out_png}")
    print(f"  - JPG: {out_jpg}")
    print(f"  - SVG: {out_svg}")
    print(f"  - PDF: {out_pdf}")

if __name__ == "__main__":
    draw_campus_network_topology()
