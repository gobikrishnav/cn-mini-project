import os
import sys

# Configure writable matplotlib cache
os.environ['MPLCONFIGDIR'] = os.path.join(os.path.dirname(__file__), 'reports', '.mplconfig')
os.makedirs(os.environ['MPLCONFIGDIR'], exist_ok=True)

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_system_design():
    # High resolution 16:10 figure
    fig, ax = plt.subplots(figsize=(16, 11), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Background
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Header Banner
    header = patches.FancyBboxPatch((3, 91), 94, 7, boxstyle="round,pad=0.5,rounding_size=1",
                                    facecolor="#0f172a", edgecolor="#1e293b", linewidth=1.5)
    ax.add_patch(header)
    ax.text(50, 95.5, "SYSTEM ARCHITECTURE & METHODOLOGY DESIGN", 
            ha='center', va='center', fontsize=16, fontweight='bold', color='#ffffff', fontfamily='sans-serif')
    ax.text(50, 92.5, "Course: 23AD551 - Computer Networking Laboratory | NetLab-Pro Dynamic Campus Subnetting Suite", 
            ha='center', va='center', fontsize=10.5, color='#94a3b8', fontfamily='sans-serif')

    def draw_box(x, y, w, h, title, subtitle, items, bg_color, border_color, title_color="#0f172a", badge=""):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
                                     facecolor=bg_color, edgecolor=border_color, linewidth=2)
        ax.add_patch(box)
        
        # Header inside box
        ax.text(x + w/2, y + h - 2.8, title, ha='center', va='center', 
                fontsize=11.5, fontweight='bold', color=title_color, fontfamily='sans-serif')
        if subtitle:
            ax.text(x + w/2, y + h - 5.2, subtitle, ha='center', va='center', 
                    fontsize=8.5, fontstyle='italic', color='#475569', fontfamily='sans-serif')
            
        if badge:
            badge_box = patches.FancyBboxPatch((x + w - 16, y + h - 3.8), 14, 2.2, boxstyle="round,pad=0.2,rounding_size=0.5",
                                               facecolor=border_color, edgecolor="none")
            ax.add_patch(badge_box)
            ax.text(x + w - 9, y + h - 2.7, badge, ha='center', va='center',
                    fontsize=7.5, fontweight='bold', color='#ffffff', fontfamily='sans-serif')

        # Items
        curr_y = y + h - 7.5
        for item in items:
            # Bullet point circle
            ax.plot(x + 2.5, curr_y, marker='o', markersize=4, color=border_color)
            ax.text(x + 4.5, curr_y, item, ha='left', va='center', 
                    fontsize=9, color='#1e293b', fontfamily='sans-serif')
            curr_y -= 3.1

    # =========================================================================
    # ROW 1: USER INPUT & PRESENTATION LAYER
    # =========================================================================
    draw_box(4, 69, 43, 20, 
             "1. USER CONFIGURATION & INPUT MODULE", 
             "User-Driven Requirements & Network Constraints",
             [
                 "Base IPv4 Network Scope (e.g., 10.50.0.0/16, 192.168.0.0/24)",
                 "Dynamic Lab Quantity (1 to 32 Laboratories Supported)",
                 "Lab Identity: Name, Department Wing, Workstation PC Count",
                 "Future Host Growth Buffer (0% to 100% capacity reservation)",
                 "Interactive Supernet Selection (Contiguous Member Labs to Merge)",
                 "Diagnostics Input: Endpoint Pair IPs for L2/L3 Path Verification"
             ],
             "#f0f9ff", "#0284c7", "#0369a1", "USER INPUT")

    draw_box(53, 69, 43, 20, 
             "2. WEB PRESENTATION & APPLICATION SERVER", 
             "Python Flask Controller & Dynamic Modern Web UI",
             [
                 "Single-Page Dashboard: Responsive Tailwind CSS & UI Panels",
                 "Interactive Setup Wizard: Multi-Lab Real-time Parameter Sizing",
                 "REST API Controllers: /api/state, /api/supernet, /api/binary",
                 "Real-time DOM Data-Binding & Dynamic Capacity Utilization Bar",
                 "Interactive Supernetting: 1-Click Lab Merge & 1-Click Split/Revert",
                 "Client-side Input Validation & Async Fetch API Communications"
             ],
             "#eef2ff", "#4f46e5", "#3730a3", "FRONT-END")

    # Arrow from Input to Presentation
    ax.annotate("", xy=(53, 79), xytext=(47, 79),
                arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2.5))
    ax.text(50, 80.5, "User Inputs", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0284c7')

    # =========================================================================
    # ROW 2: FFI INTEROPERABILITY & MIDDLEWARE BRIDGE
    # =========================================================================
    bridge_box = patches.FancyBboxPatch((15, 54), 70, 11, boxstyle="round,pad=0.5,rounding_size=1",
                                       facecolor="#fefce8", edgecolor="#ca8a04", linewidth=2)
    ax.add_patch(bridge_box)
    ax.text(50, 62.5, "3. CROSS-PLATFORM FFI INTEROPERABILITY BRIDGE (ctypes)", ha='center', va='center',
            fontsize=12, fontweight='bold', color='#854d0e')
    ax.text(50, 59.8, "Direct Memory Binding Between Python Web Layer & Native Compiled C Dynamic Library", 
            ha='center', va='center', fontsize=9, fontstyle='italic', color='#713f12')
    
    # Bridge sub-boxes
    sub_w = 20
    sub_h = 3.6
    sub_y = 55.5
    for idx, (label, subtext) in enumerate([
        ("Memory Marshaling", "C Structs <-> Python Objects"),
        ("JSON Buffer Exchange", "Fast In-Memory Serialization"),
        ("Platform Detection", "Loads .dll (Win) / .so (Linux)")
    ]):
        sx = 18 + (idx * 23)
        sb = patches.FancyBboxPatch((sx, sub_y), sub_w, sub_h, boxstyle="round,pad=0.2,rounding_size=0.5",
                                   facecolor="#ffffff", edgecolor="#eab308", linewidth=1.2)
        ax.add_patch(sb)
        ax.text(sx + sub_w/2, sub_y + 2.2, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#854d0e')
        ax.text(sx + sub_w/2, sub_y + 0.9, subtext, ha='center', va='center', fontsize=7, color='#713f12')

    # Arrows between Presentation and Bridge
    ax.annotate("", xy=(50, 65), xytext=(50, 69),
                arrowprops=dict(arrowstyle="<->", color="#4f46e5", lw=2.5))
    ax.text(52, 67, "High-Speed C Foreign Function Calls", ha='left', va='center', fontsize=8, fontweight='bold', color='#4f46e5')

    # =========================================================================
    # ROW 3: C NATIVE CORE ENGINE (CENTRAL COMPUTATIONAL KERNEL)
    # =========================================================================
    draw_box(4, 25, 92, 25, 
             "4. C NATIVE COMPUTATIONAL KERNEL (bin/netlab_core.dll | netlab_core.so)", 
             "High-Performance Bitwise Algorithms, Descending Bin-Packing & Routing Logic in Pure C (ANSI C99)",
             [],
             "#f0fdf4", "#16a34a", "#15803d", "C BACKEND")

    # 4 Inner Pillars inside C Engine
    c_sub_w = 21
    c_sub_h = 16.5
    c_sub_y = 27
    
    # Pillar A: VLSM Engine
    draw_box(6, c_sub_y, c_sub_w, c_sub_h,
             "A. VLSM Engine", "Descending Bin-Packing",
             [
                 "qsort() Descending Host Sort",
                 "Host Bit Math: (2^h - 2) >= Req",
                 "Power-of-2 Block Alignment",
                 "Prefix Sizing: CIDR = 32 - h",
                 "Subnet Boundary Clamping",
                 "Address Space Exhaustion Guard"
             ],
             "#ffffff", "#22c55e", "#166534")

    # Pillar B: CIDR Supernetting
    draw_box(29, c_sub_y, c_sub_w, c_sub_h,
             "B. Supernetting", "LCP Route Summarization",
             [
                 "Contiguity Verification (0 Gaps)",
                 "XOR LCP: (min_net ^ max_bcast)",
                 "Supernet Mask & Prefix Math",
                 "Route Reduction % Efficiency",
                 "Power-of-2 Block Condition",
                 "Cisco 'ip route' Command Gen"
             ],
             "#ffffff", "#22c55e", "#166534")

    # Pillar C: 32-Bit Binary Visualizer
    draw_box(52, c_sub_y, c_sub_w, c_sub_h,
             "C. Binary Boolean", "32-Bit Bitwise Algebra",
             [
                 "Bitwise AND: Host & Subnet Mask",
                 "Network ID & Broadcast Derivation",
                 "Usable Host Boundary Slicing",
                 "32-Bit Octet Dot Separation",
                 "Borrowed Bits Classification",
                 "RFC 1918 Scope Identification"
             ],
             "#ffffff", "#22c55e", "#166534")

    # Pillar D: L2/L3 Diagnostics
    draw_box(75, c_sub_y, c_sub_w, c_sub_h,
             "D. L2/L3 Diagnostics", "Reachability Analyzer",
             [
                 "Local Subnet Check (Direct ARP)",
                 "Inter-VLAN L3 Router Gateway",
                 "Asymmetric Mask Blackhole Check",
                 "Reserved Host IP Validation",
                 "Wire-Speed vs Hop Diagnosis",
                 "VLAN SVI Remediation Advice"
             ],
             "#ffffff", "#22c55e", "#166534")

    # Arrow from Bridge to C Kernel
    ax.annotate("", xy=(50, 50), xytext=(50, 54),
                arrowprops=dict(arrowstyle="<->", color="#16a34a", lw=2.5))
    ax.text(52, 52, "Native Binary Execution", ha='left', va='center', fontsize=8, fontweight='bold', color='#16a34a')

    # =========================================================================
    # ROW 4: OUTPUT DELIVERABLES & PHYSICAL TOPOLOGY
    # =========================================================================
    draw_box(4, 4, 92, 17, 
             "5. APPLICATION DELIVERABLES & 4-TIER CAMPUS TOPOLOGY MAPPING", 
             "Essential Deliverables Generated for Enterprise Deployment & Lab Report",
             [],
             "#faf5ff", "#9333ea", "#7e22ce", "OUTPUTS")

    # Deliverables cards
    deliv_w = 21
    deliv_h = 9.5
    deliv_y = 6

    # Deliv 1: Subnet Matrix
    draw_box(6, deliv_y, deliv_w, deliv_h,
             "Subnet Matrix Table", "",
             [
                 "Network & Broadcast IPs",
                 "First - Last Usable Hosts",
                 "VLAN IDs & SVI Gateways",
                 "Allocation Efficiency %"
             ],
             "#ffffff", "#a855f7", "#6b21a8")

    # Deliv 2: Fleet Inventory
    draw_box(29, deliv_y, deliv_w, deliv_h,
             "Workstation Fleet", "",
             [
                 "PC-by-PC Hostnames & IPs",
                 "Assigned MAC Addresses",
                 "DHCP Start / End Pools",
                 "Lease Capacity Counters"
             ],
             "#ffffff", "#a855f7", "#6b21a8")

    # Deliv 3: Cisco IOS Config
    draw_box(52, deliv_y, deliv_w, deliv_h,
             "Cisco Config (.cfg)", "",
             [
                 "VLAN 802.1Q Database",
                 "Interface SVI IP / Masks",
                 "DHCP Pool Configurations",
                 "Static Route Summaries"
             ],
             "#ffffff", "#a855f7", "#6b21a8")

    # Deliv 4: 4-Tier Topology
    draw_box(75, deliv_y, deliv_w, deliv_h,
             "Campus 4-Tier Topology", "",
             [
                 "Tier 1: Border Edge Router",
                 "Tier 2: Core L3 Switch (SVI)",
                 "Tier 3: Distribution Trunks",
                 "Tier 4: Lab Access VLANs"
             ],
             "#ffffff", "#a855f7", "#6b21a8")

    # Arrow from C Kernel to Deliverables
    ax.annotate("", xy=(50, 21), xytext=(50, 25),
                arrowprops=dict(arrowstyle="->", color="#9333ea", lw=2.5))
    ax.text(52, 23, "Deterministic Subnet Allocations & Route Summaries", ha='left', va='center', 
            fontsize=8, fontweight='bold', color='#9333ea')

    # Footer Caption
    ax.text(50, 1.2, "Figure 2.1: System Architecture and Detailed Design Workflow of NetLab-Pro Campus Subnet Suite", 
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#334155', fontfamily='sans-serif')

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), "system_design_architecture.png")
    output_rep = os.path.join(os.path.dirname(__file__), "reports", "system_design_architecture.png")
    output_pdf = os.path.join(os.path.dirname(__file__), "reports", "system_design_architecture.pdf")

    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.savefig(output_rep, dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.savefig(output_pdf, bbox_inches='tight', facecolor='#ffffff')
    print(f"[SUCCESS] System Design Diagram successfully generated at 300 DPI:")
    print(f"  - {output_path}")
    print(f"  - {output_rep}")
    print(f"  - {output_pdf}")

if __name__ == "__main__":
    draw_system_design()
