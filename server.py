"""
NetLab-Pro: Modern Web Application Server (Flask Engine)
Essential Computer Networks Project Server:
- User-Driven Dynamic VLSM Campus Subnetting
- Workstation Fleet IP Inventory & DHCP Scope Generation
- Interactive 4-Tier Network Topology
- 32-Bit Binary Visualizer & ANDing Boolean Algebra
- L2/L3 Inter-Host Packet Reachability Diagnostics
- CIDR Route Supernetting & Route Summarization
- Cisco IOS Switch & Router Configuration (.cfg)
- Viva Defense & Exam Quiz Studio
"""

import os
import sys
import math
import webbrowser
import subprocess
from flask import Flask, render_template, request, jsonify, send_file, Response

import netlab_engine as engine

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Shared Campus VLSM State (Initial clean setup with user-ready defaults)
campus = engine.CampusVLSM("192.168.0.0", 24)
campus.add_lab("Computer Networks Lab", "CSE Dept - Block A", 60, 10, 10)
campus.add_lab("Web Technologies Lab", "IT Dept - Block B", 40, 10, 20)
campus.add_lab("IoT Systems Lab", "ECE Dept - Block C", 25, 10, 30)
campus.calculate()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/engine-status", methods=["GET"])
def get_engine_status():
    return jsonify({
        "success": True,
        "status": engine.get_engine_status()
    })


@app.route("/api/state", methods=["GET"])
def get_state():
    labs_data = [lab.to_dict() for lab in campus.labs]
    next_free_str = engine.int_to_ip(campus.next_free_subnet)
    return jsonify({
        "success": True,
        "engine_status": engine.get_engine_status(),
        "base_ip": campus.base_ip_str,
        "base_cidr": campus.base_cidr,
        "num_labs": len(campus.labs),
        "total_campus_capacity": campus.total_campus_capacity,
        "total_requested_hosts": campus.total_requested_hosts,
        "total_allocated_blocks": campus.total_allocated_blocks,
        "total_usable_hosts": campus.total_usable_hosts,
        "overall_efficiency": round(campus.overall_efficiency, 1),
        "next_free_subnet": next_free_str,
        "free_ips_remaining": campus.free_ips_remaining,
        "is_calculated": campus.is_calculated,
        "is_valid": campus.is_valid,
        "error_reason": campus.error_reason,
        "recommended_cidr": getattr(campus, "recommended_cidr", campus.base_cidr),
        "total_needed_blocks": getattr(campus, "total_needed_blocks", 0),
        "has_merge_history": len(getattr(campus, "merge_history", [])) > 0,
        "merge_history_count": len(getattr(campus, "merge_history", [])),
        "last_merge": campus.merge_history[-1] if getattr(campus, "merge_history", None) else None,
        "labs": labs_data
    })


@app.route("/api/setup", methods=["POST"])
def setup_network():
    """Batch user configuration: Root scope + N labs with names & workstation counts."""
    data = request.json or {}
    base_ip = data.get("base_ip", "192.168.0.0").strip()
    base_cidr = int(data.get("base_cidr", 24))
    labs_list = data.get("labs", [])
    auto_expand = data.get("auto_expand", True)

    if not labs_list:
        return jsonify({"success": False, "error": "At least one laboratory is required"}), 400

    try:
        # Pre-calculate total block size needed across all labs
        total_needed = 0
        for lab in labs_list:
            pcs = int(lab.get("workstations") or lab.get("hosts") or 30)
            gr = int(lab.get("growth_percent") or lab.get("growth_pct") or 10)
            eff = max(2, math.ceil(pcs * (1.0 + gr / 100.0)))
            h = 2
            while h < 31 and ((1 << h) - 2) < eff:
                h += 1
            total_needed += (1 << h)

        # Check if requested base CIDR capacity is smaller than total needed
        current_cap = 1 if base_cidr >= 32 else (1 << (32 - base_cidr))
        expanded_notice = ""
        if auto_expand and total_needed > current_cap:
            needed_cap = 1
            while needed_cap < max(4, total_needed):
                needed_cap <<= 1
            new_cidr = 32 - int(math.log2(needed_cap))
            new_cidr = max(8, min(new_cidr, base_cidr))
            base_cidr = new_cidr
            expanded_notice = f"Auto-expanded base network scope to /{base_cidr} ({needed_cap:,} IPs) to cleanly accommodate all {len(labs_list)} laboratories."

        campus.update_base(base_ip, base_cidr)
        campus.clear_labs()
        for idx, lab in enumerate(labs_list):
            name = str(lab.get("name", f"Lab {idx + 1}")).strip() or f"Lab {idx + 1}"
            dept = str(lab.get("department") or lab.get("dept") or f"Department {chr(65 + (idx % 6))}").strip()
            workstations = int(lab.get("workstations") or lab.get("hosts") or 30)
            growth = int(lab.get("growth_percent") or lab.get("growth_pct") or 10)
            vlan = int(lab.get("vlan_id") or ((idx + 1) * 10))
            campus.add_lab(name, dept, workstations, growth, vlan)

        campus.calculate()
        return jsonify({
            "success": True,
            "is_valid": campus.is_valid,
            "error_reason": campus.error_reason,
            "base_cidr": campus.base_cidr,
            "notice": expanded_notice,
            "total_allocated": campus.total_allocated_blocks
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/labs/setup-n", methods=["POST"])
def setup_n_laboratories():
    """Configure N laboratories from single number-of-labs input."""
    data = request.json or {}
    num_labs = int(data.get("num_labs", data.get("count", 3)))
    base_ip = data.get("base_ip")
    base_cidr = data.get("base_cidr")
    try:
        if base_ip and base_cidr:
            campus.update_base(base_ip, int(base_cidr))
        campus.setup_n_labs(num_labs)
        return jsonify({
            "success": True,
            "is_valid": campus.is_valid,
            "error_reason": campus.error_reason,
            "num_labs": len(campus.labs)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/base", methods=["POST"])
@app.route("/api/base/update", methods=["POST"])
def update_base():
    data = request.json or {}
    base_ip = data.get("base_ip", "192.168.0.0").strip()
    base_cidr = int(data.get("base_cidr", 24))
    try:
        campus.update_base(base_ip, base_cidr)
        campus.calculate()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/labs/add", methods=["POST"])
def add_lab():
    data = request.json or {}
    name = data.get("name", "").strip()
    dept = data.get("department", "Campus").strip()
    workstations = int(data.get("workstations", 50))
    growth = int(data.get("growth_percent", 10))
    vlan_id = int(data.get("vlan_id", 0))

    if not name:
        return jsonify({"success": False, "error": "Lab name is required"}), 400

    campus.add_lab(name, dept, workstations, growth, vlan_id)
    campus.calculate()
    return jsonify({"success": True})


@app.route("/api/labs/edit", methods=["POST"])
def edit_lab():
    data = request.json or {}
    lab_id = int(data.get("id", 0))
    name = data.get("name", "").strip()
    dept = data.get("department", "Campus").strip()
    workstations = int(data.get("workstations", 50))
    growth = int(data.get("growth_percent", 10))
    vlan_id = int(data.get("vlan_id", 0))

    if not name:
        return jsonify({"success": False, "error": "Lab name is required"}), 400

    success = campus.edit_lab(lab_id, name, dept, workstations, growth, vlan_id)
    return jsonify({"success": success})


@app.route("/api/labs/remove", methods=["POST"])
def remove_lab():
    data = request.json or {}
    index = int(data.get("index", -1))
    success = campus.remove_lab(index)
    campus.calculate()
    return jsonify({"success": success})


@app.route("/api/labs/clear", methods=["POST"])
def clear_labs():
    campus.clear_labs()
    return jsonify({"success": True})


@app.route("/api/inventory/<int:lab_id>", methods=["GET"])
def get_inventory(lab_id):
    target_lab = None
    for lab in campus.labs:
        if lab.id == lab_id:
            target_lab = lab
            break
    if not target_lab and campus.labs:
        target_lab = campus.labs[0]

    if not target_lab:
        return jsonify({"success": False, "error": "No lab found"}), 404

    inv = engine.generate_lab_inventory(target_lab)
    return jsonify({"success": True, "inventory": inv})


@app.route("/api/binary", methods=["POST"])
def run_binary():
    data = request.json or {}
    raw = data.get("input", "192.168.1.130/26").strip()
    try:
        ip_val, cidr = engine.parse_ip_cidr(raw)
        info = engine.calculate_ip_info(ip_val, cidr)
        return jsonify({"success": True, "info": info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/reachability", methods=["POST"])
def run_reachability():
    data = request.json or {}
    ip_a_raw = data.get("ip_a", "192.168.0.15/26").strip()
    ip_b_raw = data.get("ip_b", "192.168.0.70/26").strip()
    try:
        val_a, cidr_a = engine.parse_ip_cidr(ip_a_raw)
        val_b, cidr_b = engine.parse_ip_cidr(ip_b_raw)
        res = engine.analyze_reachability(
            engine.int_to_ip(val_a), cidr_a,
            engine.int_to_ip(val_b), cidr_b
        )
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/calc", methods=["POST"])
def run_calc():
    data = request.json or {}
    raw = data.get("input", "192.168.0.1/24").strip()
    try:
        ip_val, cidr = engine.parse_ip_cidr(raw)
        info = engine.calculate_ip_info(ip_val, cidr)
        return jsonify({"success": True, "info": info})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/supernet", methods=["POST"])
def run_supernet():
    data = request.json or {}
    raw_subnets = data.get("subnets", [])
    if isinstance(raw_subnets, str):
        raw_subnets = [s.strip() for s in raw_subnets.replace(",", "\n").splitlines() if s.strip()]
    try:
        res = engine.calculate_supernet(raw_subnets)
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/labs/merge", methods=["POST"])
def merge_laboratories():
    """Merge user-selected laboratories into a unified CIDR supernet."""
    data = request.json or {}
    lab_ids = data.get("lab_ids", [])

    if not lab_ids or not isinstance(lab_ids, list):
        return jsonify({"success": False, "error": "Please select at least one laboratory to merge."}), 400

    selected_labs = []
    subnets = []
    for l_id in lab_ids:
        for lab in campus.labs:
            if lab.id == int(l_id):
                d = lab.to_dict()
                if lab.is_allocated:
                    selected_labs.append({
                        "id": lab.id,
                        "name": lab.name,
                        "department": lab.department,
                        "workstations": lab.workstations,
                        "vlan_id": lab.vlan_id,
                        "subnet_str": d["subnet_str"],
                        "mask_str": d["subnet_mask_str"],
                        "range_str": d["range_str"]
                    })
                    subnets.append(d["subnet_str"])
                break

    if not subnets:
        return jsonify({"success": False, "error": "None of the selected laboratories have allocated subnets."}), 400

    try:
        res = engine.calculate_supernet(subnets)
        res["merged_labs"] = selected_labs
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/labs/merge-commit", methods=["POST"])
def commit_supernet_merge():
    """Applies the supernet merge to campus network, assigning new name and updating the subnet table."""
    data = request.json or {}
    lab_ids = data.get("lab_ids", [])
    new_name = data.get("new_name", "Consolidated Super-Lab").strip()
    new_dept = data.get("new_department", "").strip()

    if not lab_ids:
        return jsonify({"success": False, "error": "Please select laboratories to merge."}), 400
    if not new_name:
        return jsonify({"success": False, "error": "Please provide a name for the merged laboratory."}), 400

    try:
        res = campus.merge_labs_into_supernet(lab_ids, new_name, new_dept)
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/labs/split", methods=["POST"])
def split_supernet():
    """Splits the merged supernet back into the previous separate laboratories."""
    try:
        res = campus.split_supernet()
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/labs/add-systems", methods=["POST"])
def add_systems():
    data = request.json or {}
    lab_id = int(data.get("lab_id", 1))
    count = int(data.get("count", 1))
    try:
        res = campus.add_systems_to_lab(lab_id, count)
        return jsonify({"success": True, "result": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/topology", methods=["GET"])
def get_topology():
    try:
        graph = engine.generate_topology_graph(campus.labs, f"{campus.base_ip_str}/{campus.base_cidr}")
        return jsonify({
            "success": True,
            "graph": graph,
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", []),
            "metadata": graph.get("metadata", {})
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/topology/svg", methods=["GET"])
def get_topology_svg():
    try:
        os.makedirs("reports", exist_ok=True)
        graph = engine.generate_topology_graph(campus.labs, f"{campus.base_ip_str}/{campus.base_cidr}")
        svg_content = engine.export_topology_svg(graph, "reports/campus_topology.svg")
        return Response(svg_content, mimetype="image/svg+xml")
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/download/topology-svg", methods=["GET"])
def download_topology_svg():
    os.makedirs("reports", exist_ok=True)
    graph = engine.generate_topology_graph(campus.labs, f"{campus.base_ip_str}/{campus.base_cidr}")
    path = "reports/campus_topology.svg"
    engine.export_topology_svg(graph, path)
    return send_file(path, as_attachment=True, download_name="campus_topology.svg", mimetype="image/svg+xml")


@app.route("/download/topology-png", methods=["GET"])
def download_topology_png():
    os.makedirs("reports", exist_ok=True)
    graph = engine.generate_topology_graph(campus.labs, f"{campus.base_ip_str}/{campus.base_cidr}")
    path = "reports/campus_topology.png"
    engine.export_topology_image(graph, path)
    return send_file(path, as_attachment=True, download_name="campus_topology.png", mimetype="image/png")


@app.route("/download/cisco")
def download_cisco():
    os.makedirs("reports", exist_ok=True)
    path = "reports/campus_cisco.cfg"
    engine.export_cisco_ios(campus, path)
    return send_file(path, as_attachment=True, download_name="campus_cisco.cfg")


@app.route("/download/report")
def download_report():
    os.makedirs("reports", exist_ok=True)
    path = "reports/campus_report.txt"
    engine.export_report_txt(campus, path)
    return send_file(path, as_attachment=True, download_name="campus_report.txt")


def launch_browser():
    """Launch Google Chrome / Default Browser to the application URL."""
    url = "http://localhost:5000"
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path, url])
                return
            except Exception:
                pass
    webbrowser.open(url)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    if os.environ.get("RENDER") is None and sys.platform == "win32":
        import threading
        threading.Timer(1.2, launch_browser).start()
    app.run(host="0.0.0.0", port=port, debug=False)
