"""
NetLab-Pro: Modern Python Web Dashboard (Streamlit Edition)
Campus Network Subnet Architect & VLSM Lab Planning Suite
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import netlab_engine as engine
import os

st.set_page_config(
    page_title="NetLab-Pro :: Campus VLSM Subnet Suite",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #0b1120; }
    .kpi-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .kpi-title { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-val { font-size: 24px; font-weight: 800; margin-top: 4px; }
    .kpi-sub { font-size: 11px; color: #64748b; margin-top: 2px; }
    .metric-cyan { color: #06b6d4; }
    .metric-green { color: #10b981; }
    .metric-yellow { color: #f59e0b; }
    .metric-blue { color: #3b82f6; }
    .metric-purple { color: #a855f7; }
    .badge-l2 { background-color: #064e3b; color: #10b981; padding: 6px 12px; border-radius: 6px; font-weight: 700; display: inline-block; }
    .badge-l3 { background-color: #1e3a5f; color: #3b82f6; padding: 6px 12px; border-radius: 6px; font-weight: 700; display: inline-block; }
    .badge-err { background-color: #7f1d1d; color: #ef4444; padding: 6px 12px; border-radius: 6px; font-weight: 700; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "campus" not in st.session_state:
    c = engine.CampusVLSM("10.50.0.0", 16)
    c.load_college_preset()
    st.session_state.campus = c

campus: engine.CampusVLSM = st.session_state.campus

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🌐 NetLab-Pro")
    st.caption("Campus Network Subnet Architect & VLSM Suite")
    st.markdown("---")

    st.subheader("Base Campus Network")
    base_ip_in = st.text_input("Base Network IP", value=campus.base_ip_str)
    base_cidr_in = st.selectbox("Base Prefix (CIDR)", options=list(range(8, 31)), index=campus.base_cidr - 8)

    if st.button("Apply Base Network", use_container_width=True):
        try:
            campus.update_base(base_ip_in, base_cidr_in)
            campus.calculate()
            st.success(f"Base updated to {base_ip_in}/{base_cidr_in}")
            st.rerun()
        except Exception as e:
            st.error(str(e))

    st.markdown("---")
    st.subheader("Preset Configurations")
    if st.button("🏫 Load College Preset (8 Labs)", use_container_width=True):
        campus.load_college_preset()
        st.success("Loaded 8 standard engineering college labs!")
        st.rerun()

    st.markdown("---")
    st.subheader("Add Lab to Design")
    with st.form("add_lab_form", clear_on_submit=True):
        new_name = st.text_input("Lab Name", placeholder="e.g. AI & Robotics Lab")
        new_dept = st.text_input("Department / Wing", placeholder="e.g. CSE Dept - Block A")
        c1, c2 = st.columns(2)
        with c1:
            new_pcs = st.number_input("Workstations", min_value=1, max_value=5000, value=60)
            new_vlan = st.number_input("VLAN ID", min_value=1, max_value=4094, value=80)
        with c2:
            new_growth = st.number_input("Growth Buffer %", min_value=0, max_value=100, value=10)

        submitted = st.form_submit_button("➕ Add Lab to Design", use_container_width=True)
        if submitted:
            if not new_name:
                st.error("Please provide a lab name.")
            else:
                campus.add_lab(new_name, new_dept, int(new_pcs), int(new_growth), int(new_vlan))
                campus.calculate()
                st.rerun()

    if st.button("🧹 Clear All Labs", use_container_width=True):
        campus.clear_labs()
        st.rerun()

# -----------------------------------------------------------------------------
# TOP METRICS DASHBOARD
# -----------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Base Network Scope</div>
        <div class="kpi-val metric-cyan">{campus.base_ip_str}/{campus.base_cidr}</div>
        <div class="kpi-sub">{campus.total_campus_capacity:,} Total IP Addresses</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Workstations</div>
        <div class="kpi-val metric-green">{campus.total_requested_hosts} PCs</div>
        <div class="kpi-sub">Across {len(campus.labs)} Planned Labs</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Allocated Space</div>
        <div class="kpi-val metric-yellow">{campus.total_allocated_blocks:,} IPs</div>
        <div class="kpi-sub">Subnet Blocks Reserved</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    next_free_str = engine.int_to_ip(campus.next_free_subnet)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Next Free Subnet</div>
        <div class="kpi-val metric-blue">{next_free_str}</div>
        <div class="kpi-sub">{campus.free_ips_remaining:,} Free IPs Remaining</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Overall Efficiency</div>
        <div class="kpi-val metric-purple">{campus.overall_efficiency:.1f} %</div>
        <div class="kpi-sub">Address Utilization</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN APP TABS
# -----------------------------------------------------------------------------
tab_vlsm, tab_inv, tab_bin, tab_reach, tab_calc, tab_arch = st.tabs([
    "🏢 VLSM Lab Matrix",
    "🖥️ Workstation Inventory & DHCP",
    "🔬 32-Bit Binary Visualizer",
    "🔄 Reachability Diagnostics (L2 vs L3)",
    "📐 Single Subnet Calculator",
    "🏗️ Architecture & PPT Generator"
])

# -----------------------------------------------------------------------------
# TAB 1: VLSM LAB MATRIX
# -----------------------------------------------------------------------------
with tab_vlsm:
    st.subheader("Campus VLSM Subnet Allocation Table")

    if not campus.labs:
        st.info("No labs configured. Use the sidebar to add labs or load the College Preset.")
    else:
        rows = []
        for lab in campus.labs:
            d = lab.to_dict()
            rows.append({
                "ID": d["id"],
                "Lab Name": d["name"],
                "Department": d["department"],
                "Demand": f"{d['workstations']} PCs (+{d['growth_percent']}%)",
                "VLAN": f"VLAN{d['vlan_id']}",
                "Subnet Address": d["subnet_str"] if campus.is_calculated else "[Uncalculated]",
                "Subnet Mask": d["subnet_mask_str"] if campus.is_calculated else "-",
                "Usable Host Range": d["range_str"] if campus.is_calculated else "-",
                "Default Gateway": d["gateway_ip_str"] if campus.is_calculated else "-",
                "DNS Server": d["dns_server_ip_str"] if campus.is_calculated else "-",
                "Capacity": f"{d['usable_capacity']} hosts" if campus.is_calculated else "-",
                "Efficiency": f"{d['efficiency_pct']}%" if campus.is_calculated else "-"
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Quick Actions & Downloads
        st.markdown("### 📥 Export Configurations & Engineering Reports")
        c1, c2, c3 = st.columns(3)

        cisco_cfg = engine.export_cisco_ios(campus, "")
        csv_data = engine.export_csv(campus, "")
        txt_rep = engine.export_report_txt(campus, "")

        with c1:
            st.download_button(
                "📄 Download Cisco IOS Script (.cfg)",
                data=cisco_cfg,
                file_name="campus_cisco.cfg",
                mime="text/plain",
                use_container_width=True
            )
        with c2:
            st.download_button(
                "📊 Download CSV Spreadsheet (.csv)",
                data=csv_data,
                file_name="campus_subnets.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c3:
            st.download_button(
                "📝 Download Engineering Report (.txt)",
                data=txt_rep,
                file_name="campus_report.txt",
                mime="text/plain",
                use_container_width=True
            )

        # Visual Chart of Address Allocation
        st.markdown("### 📊 IP Address Allocation by Laboratory")
        chart_data = []
        for lab in campus.labs:
            chart_data.append({
                "Lab": lab.name,
                "Workstations": lab.workstations,
                "Usable Capacity": lab.usable_capacity,
                "Wasted IPs": lab.wasted_ips
            })
        df_chart = pd.DataFrame(chart_data)
        fig = px.bar(
            df_chart,
            x="Lab",
            y=["Workstations", "Wasted IPs"],
            title="Workstations Demand vs Address Block Overhead",
            barmode="stack",
            color_discrete_map={"Workstations": "#06b6d4", "Wasted IPs": "#f59e0b"}
        )
        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font_color="#f8fafc",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: INVENTORY & DHCP
# -----------------------------------------------------------------------------
with tab_inv:
    st.subheader("Workstation-by-Workstation Device Inventory & DHCP Scope")

    if not campus.labs:
        st.info("Please configure labs first.")
    else:
        lab_opts = [f"{lab.id}. {lab.name} ({lab.workstations} PCs, VLAN {lab.vlan_id})" for lab in campus.labs]
        sel_idx = st.selectbox("Select Laboratory", range(len(lab_opts)), format_func=lambda i: lab_opts[i])

        chosen_lab = campus.labs[sel_idx]
        inv = engine.generate_lab_inventory(chosen_lab)
        dhcp = inv["dhcp"]

        st.markdown(f"""
        <div style="background-color: #1e293b; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 6px; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #f59e0b; font-size: 16px; margin-bottom: 6px;">DHCP Pool Scope & Gateway Specification</div>
            <div style="font-family: monospace; font-size: 13px; color: #f8fafc; line-height: 1.6;">
                <b>Network:</b> {dhcp['pool_network']} &nbsp;|&nbsp; <b>Subnet Mask:</b> {dhcp['subnet_mask']} &nbsp;|&nbsp; <b>VLAN ID:</b> {dhcp['vlan_id']}<br>
                <b>Default Gateway:</b> {dhcp['default_gateway']} &nbsp;|&nbsp; <b>Local DNS Server:</b> {dhcp['dns_server']}<br>
                <b>DHCP Dynamic Lease Range:</b> {dhcp['dhcp_range_start']} ➔ {dhcp['dhcp_range_end']} ({dhcp['total_leases']} Total Client Leases, {dhcp['lease_days']} Days)
            </div>
        </div>
        """, unsafe_allow_html=True)

        inv_df = pd.DataFrame(inv["records"])
        inv_df.columns = ["#", "Device Hostname", "Device Role", "Assigned IP", "Subnet Mask", "Default Gateway", "DNS Server"]
        st.dataframe(inv_df, use_container_width=True, hide_index=True)

        # CSV Download for this lab inventory
        inv_csv = inv_df.to_csv(index=False)
        st.download_button(
            f"💾 Download Workstation Inventory CSV ({chosen_lab.name})",
            data=inv_csv,
            file_name=f"inventory_{chosen_lab.name.replace(' ', '_')}.csv",
            mime="text/csv"
        )

# -----------------------------------------------------------------------------
# TAB 3: BINARY VISUALIZER
# -----------------------------------------------------------------------------
with tab_bin:
    st.subheader("32-Bit Binary IPv4 Decomposition & Bitwise ANDing Engine")

    c1, c2 = st.columns([3, 1])
    with c1:
        bin_in = st.text_input("Enter IPv4 Address & Prefix (CIDR)", value="192.168.1.130/26")
    with c2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        run_bin = st.button("⚡ Decompose & Calculate", use_container_width=True)

    try:
        ip_val, cidr = engine.parse_ip_cidr(bin_in)
        info = engine.calculate_ip_info(ip_val, cidr)

        # Bit breakdown display
        b_ip = f"{ip_val:032b}"
        b_html = []
        for i, bit in enumerate(b_ip):
            if i > 0 and i % 8 == 0:
                b_html.append("<span style='color: #64748b;'> • </span>")
            if i < 8:
                col = "#06b6d4"  # Net
            elif i < cidr:
                col = "#f59e0b"  # Subnet
            else:
                col = "#10b981"  # Host
            b_html.append(f"<span style='color: {col}; font-weight: bold;'>{bit}</span>")

        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 18px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 20px;">
            <div style="font-size: 13px; font-weight: 700; color: #94a3b8; margin-bottom: 8px;">
                COLOR-CODED 32-BIT REPRESENTATION &nbsp;&nbsp;
                <span style="color: #06b6d4;">■ Network Bits</span> &nbsp;&nbsp;
                <span style="color: #f59e0b;">■ Subnet Borrowed Bits</span> &nbsp;&nbsp;
                <span style="color: #10b981;">■ Host Bits</span>
            </div>
            <div style="font-family: monospace; font-size: 20px; letter-spacing: 2px;">
                {''.join(b_html)}
            </div>
            <div style="font-size: 12px; color: #64748b; margin-top: 6px;">
                Prefix /{cidr}: {cidr} Network/Subnet Bits | {32 - cidr} Host Bits
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background-color: #0f172a; padding: 20px; border-radius: 8px; font-family: monospace; font-size: 13px; line-height: 1.8; color: #f8fafc; border: 1px solid #334155;">
            <b style="color: #06b6d4;">1. IP ADDRESS SPECIFICATION:</b><br>
            &nbsp;&nbsp;* Decimal Notation    : {info['ip_str']}/{cidr}<br>
            &nbsp;&nbsp;* 32-Bit Binary       : {info['binary_ip']}<br>
            &nbsp;&nbsp;* Hexadecimal         : 0x{info['ip_int']:08X}<br>
            &nbsp;&nbsp;* Classification       : {info['ip_class']} ({info['scope']})<br><br>

            <b style="color: #10b981;">2. BITWISE AND OPERATION (IP & MASK = NETWORK ID):</b><br>
            &nbsp;&nbsp;&nbsp;&nbsp;IP Address        : {info['binary_ip']}<br>
            &nbsp;&nbsp;&amp; Subnet Mask       : {info['binary_mask']}<br>
            &nbsp;&nbsp;------------------------------------------------------------------------<br>
            &nbsp;&nbsp;= <span style="color: #06b6d4; font-weight: bold;">Network ID</span>        : {info['binary_network']}  ➔  <b>{info['network_str']}/{cidr}</b><br><br>

            <b style="color: #f59e0b;">3. BITWISE INVERT &amp; OR (NETWORK ID | WILDCARD = BROADCAST ID):</b><br>
            &nbsp;&nbsp;&nbsp;&nbsp;Network ID        : {info['binary_network']}<br>
            &nbsp;&nbsp;| Wildcard Mask     : {engine.int_to_binary_str(info['wildcard_int'])}<br>
            &nbsp;&nbsp;------------------------------------------------------------------------<br>
            &nbsp;&nbsp;= <span style="color: #f59e0b; font-weight: bold;">Broadcast ID</span>      : {info['binary_broadcast']}  ➔  <b>{info['broadcast_str']}</b><br><br>

            <b style="color: #a855f7;">4. USABLE HOST CAPACITY:</b><br>
            &nbsp;&nbsp;* First Usable Host   : <b>{info['first_usable_str']}</b><br>
            &nbsp;&nbsp;* Last Usable Host    : <b>{info['last_usable_str']}</b><br>
            &nbsp;&nbsp;* Usable Capacity     : <b>{info['usable_hosts']:,} Hosts</b> (Formula: 2^{32 - cidr} - 2)
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error parsing address: {e}")

# -----------------------------------------------------------------------------
# TAB 4: REACHABILITY DIAGNOSTICS
# -----------------------------------------------------------------------------
with tab_reach:
    st.subheader("Inter-Host Reachability & Routing Diagnostic Tool")
    st.caption("Determines whether two endpoints communicate via direct Layer-2 switching or require Layer-3 Inter-VLAN routing.")

    c1, c2 = st.columns(2)
    with c1:
        ip_a = st.text_input("Endpoint A (IP/CIDR)", value="10.50.0.15/24")
    with c2:
        ip_b = st.text_input("Endpoint B (IP/CIDR)", value="10.50.1.20/25")

    # Preset Quick Buttons
    qb1, qb2, qb3 = st.columns(3)
    with qb1:
        if st.button("🟢 Scenario 1: Same Subnet (L2)"):
            st.session_state["reach_a"] = "10.50.0.15/24"
            st.session_state["reach_b"] = "10.50.0.88/24"
            st.rerun()
    with qb2:
        if st.button("🔵 Scenario 2: Routed Subnets (L3)"):
            st.session_state["reach_a"] = "10.50.0.15/24"
            st.session_state["reach_b"] = "10.50.1.20/25"
            st.rerun()
    with qb3:
        if st.button("🔴 Scenario 3: Asymmetric Mask Bug"):
            st.session_state["reach_a"] = "192.168.1.10/24"
            st.session_state["reach_b"] = "192.168.1.130/25"
            st.rerun()

    if "reach_a" in st.session_state:
        ip_a = st.session_state["reach_a"]
        ip_b = st.session_state["reach_b"]

    try:
        val_a, cidr_a = engine.parse_ip_cidr(ip_a)
        val_b, cidr_b = engine.parse_ip_cidr(ip_b)

        res = engine.analyze_reachability(engine.int_to_ip(val_a), cidr_a,
                                          engine.int_to_ip(val_b), cidr_b)

        badge_cls = "badge-l2" if res["badge_color"] == "green" else ("badge-l3" if res["badge_color"] == "blue" else "badge-err")

        st.markdown(f"""
        <div style="background-color: #1e293b; padding: 20px; border-radius: 10px; border: 1px solid #334155; margin-top: 16px;">
            <div class="{badge_cls}">{res['badge']}</div>
            <h3 style="margin-top: 12px; color: #f8fafc;">{res['headline']}</h3>
            <p style="color: #94a3b8; font-size: 14px; line-height: 1.6;">{res['diagnosis']}</p>
            <div style="background-color: #0f172a; padding: 12px; border-radius: 6px; margin-top: 12px; border-left: 3px solid #06b6d4;">
                <b style="color: #06b6d4;">Network Engineer Recommendation:</b>
                <div style="color: #cbd5e1; font-size: 13px; margin-top: 4px;">{res['recommendation']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Diagnostic error: {e}")

# -----------------------------------------------------------------------------
# TAB 5: SINGLE CALCULATOR
# -----------------------------------------------------------------------------
with tab_calc:
    st.subheader("Single IPv4 Subnet Calculator")
    calc_in = st.text_input("Enter IP Address and Mask or CIDR", value="172.16.42.105/20")

    try:
        c_ip, c_cidr = engine.parse_ip_cidr(calc_in)
        c_info = engine.calculate_ip_info(c_ip, c_cidr)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-weight: 700; color: #06b6d4; font-size: 16px; margin-bottom: 12px;">Network Boundaries</div>
                <table style="width: 100%; color: #f8fafc; font-size: 13px;">
                    <tr><td style="color: #94a3b8;">Host IP:</td><td><b>{c_info['ip_str']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">CIDR Prefix:</td><td><b>/{c_info['cidr']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Subnet Mask:</td><td><b>{c_info['mask_str']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Wildcard Mask:</td><td><b>{c_info['wildcard_str']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Network ID:</td><td><b>{c_info['network_str']}/{c_info['cidr']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Broadcast ID:</td><td><b>{c_info['broadcast_str']}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="kpi-card">
                <div style="font-weight: 700; color: #10b981; font-size: 16px; margin-bottom: 12px;">Host Capacity & Scope</div>
                <table style="width: 100%; color: #f8fafc; font-size: 13px;">
                    <tr><td style="color: #94a3b8;">First Usable Host:</td><td><b>{c_info['first_usable_str']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Last Usable Host:</td><td><b>{c_info['last_usable_str']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Total Addresses:</td><td><b>{c_info['total_ips']:,}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Usable Hosts:</td><td><b>{c_info['usable_hosts']:,} PCs</b></td></tr>
                    <tr><td style="color: #94a3b8;">Address Class:</td><td><b>{c_info['ip_class']}</b></td></tr>
                    <tr><td style="color: #94a3b8;">Address Scope:</td><td><b>{c_info['scope']}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(str(e))

# -----------------------------------------------------------------------------
# TAB 6: ARCHITECTURE & PPT GENERATOR
# -----------------------------------------------------------------------------
with tab_arch:
    st.subheader("System Architecture & 12-Slide PowerPoint Presentation Deck")

    # PPT Generation Banner
    import generate_ppt
    os.makedirs("reports", exist_ok=True)
    ppt_path = "reports/NetLab_Pro_Project_Presentation.pptx"

    c_p1, c_p2 = st.columns([3, 1])
    with c_p1:
        st.markdown("""
        <div style="background-color: #1e293b; border-left: 4px solid #06b6d4; padding: 18px; border-radius: 8px;">
            <h4 style="color: #f8fafc; margin: 0 0 6px 0;">12-Slide Human-Designed PowerPoint Presentation</h4>
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">
                Comprehensive capstone presentation deck covering problem statements, 4-tier system architecture,
                VLSM algorithmic formulas, 8-lab college deployment topology, and technical viva defense.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_p2:
        if st.button("⚡ Generate PowerPoint Deck", use_container_width=True):
            generate_ppt.create_presentation(ppt_path)
            st.success("Presentation generated successfully!")

        if os.path.exists(ppt_path):
            with open(ppt_path, "rb") as f:
                st.download_button(
                    "📥 Download Presentation (.pptx)",
                    data=f.read(),
                    file_name="NetLab_Pro_Project_Presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )

    st.markdown("---")
    st.markdown("### 🏗️ 4-Tier Software Architecture Pipeline")

    st.markdown("""
    <div style="display: grid; gap: 14px; margin-top: 10px;">
        <div style="background-color: #1e293b; border-left: 4px solid #06b6d4; padding: 14px; border-radius: 6px;">
            <b style="color: #06b6d4;">Tier 1: Presentation & Client Layer</b>
            <p style="color: #cbd5e1; font-size: 13px; margin: 4px 0 0 0;">
                Chrome Web Dashboard (Tailwind CSS, glassmorphism), Python Desktop GUI (High-DPI Segoe UI), and ANSI 24-bit Terminal TUI.
            </p>
        </div>
        <div style="background-color: #1e293b; border-left: 4px solid #3b82f6; padding: 14px; border-radius: 6px;">
            <b style="color: #3b82f6;">Tier 2: Business Logic & Network Planning Engine</b>
            <p style="color: #cbd5e1; font-size: 13px; margin: 4px 0 0 0;">
                Campus VLSM Allocator (descending capacity sort, power-of-2 boundary alignment, collision detection) and Workstation Inventory & DHCP Scope Generator.
            </p>
        </div>
        <div style="background-color: #1e293b; border-left: 4px solid #a855f7; padding: 14px; border-radius: 6px;">
            <b style="color: #a855f7;">Tier 3: 32-Bit Bitwise Mathematics & Diagnostic Layer</b>
            <p style="color: #cbd5e1; font-size: 13px; margin: 4px 0 0 0;">
                32-Bit unsigned bitwise ANDing (IP & MASK = Network ID), wildcard inversion, and L2 vs L3 inter-host reachability analyzer with asymmetric mask detection.
            </p>
        </div>
        <div style="background-color: #1e293b; border-left: 4px solid #10b981; padding: 14px; border-radius: 6px;">
            <b style="color: #10b981;">Tier 4: Hardware Compilation & Multi-Format Exporters</b>
            <p style="color: #cbd5e1; font-size: 13px; margin: 4px 0 0 0;">
                Automated Cisco IOS Catalyst L3 switch/router CLI configurations, CSV spreadsheets for Excel, ASCII technical reports, and 12-slide PowerPoint presentation deck.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
