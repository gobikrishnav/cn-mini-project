"""
NetLab-Pro: Interactive Terminal Subnet Architect (CLI Input Mode)
Directly prompts the user for all network parameters:
- Root IPv4 Base Address & CIDR Prefix
- Total Number of Computer Laboratories
- Laboratory Names, Departments, Number of Systems/Workstations, Growth %, and VLAN IDs
Exports essential Cisco IOS configuration (.cfg) and Engineering Report (.txt).
"""

import sys
import os

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
except Exception:
    pass

import netlab_engine as engine


def print_banner():
    print("=" * 82)
    print("   NETLAB-PRO :: CAMPUS NETWORK SUBNET ARCHITECT & DYNAMIC VLSM ENGINE")
    print("   User-Driven Input Mode - Essential Computer Networks Project Suite")
    print("=" * 82)


def get_target_scope_input():
    print("\n[STEP 1/2] ROOT CAMPUS NETWORK SCOPE INPUT")
    print("-" * 55)
    print("Enter the root IPv4 network address and prefix for your campus.")
    print("Examples: 192.168.0.0 /24 | 172.16.0.0 /20 | 10.0.0.0 /16")

    while True:
        raw_ip = input("\n>> Enter Base IPv4 Network [192.168.0.0]: ").strip()
        if not raw_ip:
            raw_ip = "192.168.0.0"

        if "/" in raw_ip:
            parts = raw_ip.split("/")
            ip_str = parts[0].strip()
            cidr_default = parts[1].strip()
        else:
            ip_str = raw_ip
            cidr_default = "24"

        try:
            engine.ip_to_int(ip_str)
            break
        except Exception as e:
            print(f"[!] Invalid IPv4 address '{ip_str}': {e}. Please try again.")

    while True:
        raw_cidr = input(f">> Enter CIDR Prefix Length (8-30) [{cidr_default}]: ").strip()
        if not raw_cidr:
            raw_cidr = cidr_default

        raw_cidr = raw_cidr.replace("/", "").strip()
        try:
            cidr = int(raw_cidr)
            if 8 <= cidr <= 30:
                break
            print("[!] CIDR prefix must be between 8 and 30. Please try again.")
        except ValueError:
            print("[!] Please enter a valid integer for CIDR prefix.")

    return ip_str, cidr


def get_laboratories_input(campus: engine.CampusVLSM):
    print("\n[STEP 2/2] CAMPUS LABORATORIES & SYSTEMS INPUT")
    print("-" * 55)

    campus.clear_labs()
    while True:
        try:
            num_labs_str = input(">> Enter Total Number of Computer Laboratories to configure [3]: ").strip()
            num_labs = int(num_labs_str) if num_labs_str else 3
            if 1 <= num_labs <= 32:
                break
            print("[!] Please enter a number between 1 and 32.")
        except ValueError:
            print("[!] Please enter a valid integer.")

    print(f"\nEntering details for all {num_labs} laboratories:")
    default_names = ["Computer Networks Lab", "Web Technologies Lab", "IoT Systems Lab", "Data Science Lab", "AI & Robotics Lab", "Systems Programming Lab"]
    
    for i in range(1, num_labs + 1):
        def_name = default_names[i - 1] if (i - 1) < len(default_names) else f"Computer Lab {i}"
        def_dept = f"Department Wing {chr(65 + ((i - 1) % 6))}"
        def_pcs = max(20, 80 - ((i - 1) * 20))
        def_vlan = i * 10

        print(f"\n--- Laboratory #{i} Specification ---")
        name = input(f"  >> Lab #{i} Name [{def_name}]: ").strip()
        if not name:
            name = def_name

        dept = input(f"  >> Department / Campus Wing [{def_dept}]: ").strip()
        if not dept:
            dept = def_dept

        while True:
            try:
                pcs_str = input(f"  >> Number of Systems / PCs in {name} [{def_pcs}]: ").strip()
                workstations = int(pcs_str) if pcs_str else def_pcs
                if workstations >= 1:
                    break
                print("     [!] Number of systems must be at least 1.")
            except ValueError:
                print("     [!] Please enter a valid number.")

        while True:
            try:
                gr_str = input(f"  >> Future Growth Expansion Buffer % (0-100) [10]: ").strip()
                growth = int(gr_str) if gr_str else 10
                if 0 <= growth <= 100:
                    break
                print("     [!] Growth buffer must be between 0 and 100%.")
            except ValueError:
                print("     [!] Please enter a valid number.")

        while True:
            try:
                vlan_str = input(f"  >> 802.1Q VLAN ID (1-4094) [{def_vlan}]: ").strip()
                vlan_id = int(vlan_id_str := vlan_str) if vlan_str else def_vlan
                if 1 <= vlan_id <= 4094:
                    break
                print("     [!] VLAN ID must be between 1 and 4094.")
            except ValueError:
                print("     [!] Please enter a valid integer.")

        campus.add_lab(name, dept, workstations, growth, vlan_id)

    print(f"\n[+] Running VLSM Subnet Calculation for {len(campus.labs)} laboratories...")
    success = campus.calculate()
    if not success:
        print(f"\n[!] WARNING: Address exhaustion detected!")
        print(f"    Reason: {campus.error_reason}")
    else:
        print("[+] VLSM allocations computed successfully!")


def display_results(campus: engine.CampusVLSM):
    print("\n" + "=" * 115)
    print("                    NETLAB-PRO :: CAMPUS VLSM SUBNET MATRIX RESULTS")
    print("=" * 115)
    print(f"Base Scope: {campus.base_ip_str}/{campus.base_cidr}  |  Total Capacity: {campus.total_campus_capacity:,} IPs  |  Planned Systems: {campus.total_requested_hosts} PCs")
    print(f"Allocated Blocks: {campus.total_allocated_blocks:,} IPs  |  Usable Capacity: {campus.total_usable_hosts:,} slots  |  Overall Efficiency: {campus.overall_efficiency:.1f}%")
    print("-" * 115)
    print(f"{'#':<3} {'Laboratory Name':<26} {'Department Wing':<16} {'PCs':<6} {'VLAN':<6} {'Subnet Prefix':<18} {'Subnet Mask':<16} {'Usable Host Range':<28}")
    print("-" * 115)

    for lab in campus.labs:
        d = lab.to_dict()
        print(f"#{d['id']:<2} {d['name'][:25]:<26} {d['department'][:15]:<16} {d['workstations']:<6} {d['vlan_id']:<6} {d['subnet_str']:<18} {d['subnet_mask_str']:<16} {d['range_str']:<28}")
    print("-" * 115)


def post_calculation_menu(campus: engine.CampusVLSM):
    while True:
        print("\n" + "=" * 50)
        print("          ESSENTIAL PROJECT ACTIONS")
        print("=" * 50)
        print("  1. Export Cisco IOS Switch & Router Config (.cfg)")
        print("  2. Export Engineering Architecture Report (.txt)")
        print("  3. Run CIDR Supernetting & Route Summarization")
        print("  4. Add Systems / PCs to a Laboratory on the fly")
        print("  5. Re-run Calculation with New User Inputs")
        print("  6. Exit")
        print("-" * 50)

        choice = input(">> Select Option (1-6) [1]: ").strip()
        if not choice:
            choice = "1"

        if choice == "1":
            os.makedirs("reports", exist_ok=True)
            out_file = "reports/campus_cisco.cfg"
            engine.export_cisco_ios(campus, out_file)
            print(f"[+] Cisco IOS configuration saved to: {os.path.abspath(out_file)}")

        elif choice == "2":
            os.makedirs("reports", exist_ok=True)
            out_file = "reports/campus_report.txt"
            engine.export_report_txt(campus, out_file)
            print(f"[+] Engineering report saved to: {os.path.abspath(out_file)}")

        elif choice == "3":
            run_cli_supernet(campus)

        elif choice == "4":
            run_cli_add_systems(campus)
            display_results(campus)

        elif choice == "5":
            return True

        elif choice == "6":
            print("\nExiting NetLab-Pro. Goodbye!\n")
            return False


def run_cli_add_systems(campus: engine.CampusVLSM):
    print("\n" + "=" * 60)
    print("      ADD NEW SYSTEMS / WORKSTATIONS TO LABORATORY")
    print("=" * 60)
    if not campus.labs:
        print("[!] No active laboratories configured.")
        return

    for lab in campus.labs:
        print(f"  #{lab.id}: {lab.name} ({lab.workstations} PCs, Subnet: {lab.to_dict()['subnet_str']})")

    while True:
        try:
            raw_id = input(f"\n>> Enter Lab # (1-{len(campus.labs)}) [1]: ").strip()
            lab_id = int(raw_id) if raw_id else 1
            if 1 <= lab_id <= len(campus.labs):
                break
            print(f"[!] Please enter a number between 1 and {len(campus.labs)}.")
        except ValueError:
            print("[!] Please enter a valid integer.")

    while True:
        try:
            raw_cnt = input(">> How many new systems to add to this lab? [5]: ").strip()
            cnt = int(raw_cnt) if raw_cnt else 5
            if cnt >= 1:
                break
            print("[!] Count must be at least 1.")
        except ValueError:
            print("[!] Please enter a valid integer.")

    try:
        res = campus.add_systems_to_lab(lab_id, cnt)
        print("\n" + "-" * 60)
        print("             SYSTEMS ALLOCATION RESULTS")
        print("-" * 60)
        print(f"  Target Lab         : #{res['lab_id']} - {res['lab_name']}")
        print(f"  Added Systems      : +{res['added_count']} PCs")
        print(f"  Total Workstations : {res['old_workstations']} -> {res['new_workstations']} PCs")
        print(f"  Subnet Allocation  : {res['new_subnet']} (Usable Capacity: {res['usable_capacity']} hosts)")
        print(f"  Spare IP Slots     : {res['spare_slots']} free host slots remaining")
        if res["expanded"]:
            print(f"  ⚡ Subnet Scaling  : Auto-expanded from /{res['old_cidr']} to /{res['new_cidr']}!")
        print("-" * 60)
    except Exception as e:
        print(f"[!] Error adding systems: {e}")


def run_cli_supernet(campus: engine.CampusVLSM):
    print("\n" + "=" * 60)
    print("      CIDR SUPERNETTING & ROUTE SUMMARIZATION CALCULATOR")
    print("=" * 60)
    if not campus.labs:
        print("[!] No active campus labs to summarize.")
        return
    nets = [f"{engine.int_to_ip(l.network_ip)}/{l.allocated_cidr}" for l in campus.labs]

    try:
        res = engine.calculate_supernet(nets)
        print("\n" + "-" * 60)
        print("                 SUPERNETTING RESULTS")
        print("-" * 60)
        print(f"  Summary Network ID : {res['supernet_str']}")
        print(f"  Aggregate Mask     : {res['supernet_mask_str']}")
        print(f"  Total Capacity     : {res['total_supernet_ips']:,} IPs ({res['usable_supernet_hosts']:,} usable hosts)")
        print(f"  Route Reduction    : {res['reduction_pct']}% ({res['input_count']} routes -> 1 summary route)")
        print(f"  Verdict            : {res['verdict_badge']}")
        print(f"  Description        : {res['verdict_desc']}")
        print("-" * 60)
        print("  Cisco IOS Route Summarization:")
        print(f"    Static Discard   : {res['cisco_static']}")
        print(f"    OSPF ABR Range   : {res['cisco_ospf']}")
        print(f"    BGP Summary      : {res['cisco_bgp']}")
        print("-" * 60)
    except Exception as e:
        print(f"[!] Supernet calculation error: {e}")


def main():
    print_banner()
    while True:
        base_ip, cidr = get_target_scope_input()
        campus = engine.CampusVLSM(base_ip, cidr)
        get_laboratories_input(campus)
        display_results(campus)
        should_rerun = post_calculation_menu(campus)
        if not should_rerun:
            break


if __name__ == "__main__":
    main()
