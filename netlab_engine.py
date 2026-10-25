"""
NetLab-Pro: Core IPv4 Networking & VLSM Computation Engine
Fully compatible with C implementation formulas and data structures.
"""

import os
import math
import random
import re
import time
import json
import ctypes
import sys
from typing import List, Dict, Any, Tuple, Optional

# =========================================================================
# C NATIVE BACKEND BRIDGE (MSVC Native 64-bit DLL / Linux SO)
# =========================================================================
_lib_name = "netlab_core.dll" if sys.platform == "win32" else "netlab_core.so"
_C_BACKEND_DLL_PATH = os.path.join(os.path.dirname(__file__), "bin", _lib_name)
_c_backend = None

try:
    if os.path.exists(_C_BACKEND_DLL_PATH):
        _c_backend = ctypes.CDLL(_C_BACKEND_DLL_PATH)
        _c_backend.c_get_backend_version.restype = ctypes.c_char_p
        print(f"[NetLab-Pro] C Native Backend Loaded ({_lib_name}): {_c_backend.c_get_backend_version().decode()}")
except Exception as _e:
    print(f"[NetLab-Pro] Note on C backend initialization: {_e}")


def get_engine_status() -> Dict[str, Any]:
    if _c_backend:
        try:
            ver = _c_backend.c_get_backend_version().decode()
        except Exception:
            ver = "NetLab-Pro C-Core v3.0"
        return {
            "backend": "C Native Core (MSVC 64-bit DLL - bin/netlab_core.dll)",
            "frontend": "Python (Flask Web Application Server)",
            "version": ver,
            "is_c_active": True
        }
    return {
        "backend": "Python Core (Fallback)",
        "frontend": "Python (Flask)",
        "version": "v3.0",
        "is_c_active": False
    }


def ip_to_int(ip_str: str) -> int:
    """Convert IPv4 dotted-decimal string to 32-bit unsigned integer."""
    octets = [int(x) for x in ip_str.strip().split(".")]
    if len(octets) != 4 or any(x < 0 or x > 255 for x in octets):
        raise ValueError(f"Invalid IPv4 address: {ip_str}")
    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]


def int_to_ip(val: int) -> str:
    """Convert 32-bit integer to IPv4 dotted-decimal string."""
    val = val & 0xFFFFFFFF
    return f"{(val >> 24) & 0xFF}.{(val >> 16) & 0xFF}.{(val >> 8) & 0xFF}.{val & 0xFF}"


def cidr_to_mask_int(cidr: int) -> int:
    """Convert CIDR prefix length (0-32) to 32-bit mask integer."""
    if cidr < 0 or cidr > 32:
        raise ValueError(f"Invalid CIDR prefix: {cidr}")
    if cidr == 0:
        return 0
    return ((0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF)


def mask_int_to_cidr(mask_int: int) -> int:
    """Convert 32-bit mask integer to CIDR prefix length."""
    mask_int = mask_int & 0xFFFFFFFF
    cidr = 0
    while mask_int & 0x80000000:
        cidr += 1
        mask_int = (mask_int << 1) & 0xFFFFFFFF
    return cidr


def calculate_wildcard_int(mask_int: int) -> int:
    """Calculate 32-bit wildcard mask from subnet mask."""
    return (~mask_int) & 0xFFFFFFFF


def parse_ip_cidr(text: str) -> Tuple[int, int]:
    """Parse string formatted as '192.168.1.1/24' or '192.168.1.1 24'."""
    text = text.strip()
    if "/" in text:
        parts = text.split("/", 1)
        ip_val = ip_to_int(parts[0].strip())
        cidr = int(parts[1].strip())
        if cidr < 0 or cidr > 32:
            raise ValueError(f"CIDR must be between 0 and 32, got {cidr}")
        return ip_val, cidr
    elif " " in text:
        parts = text.split(None, 1)
        ip_val = ip_to_int(parts[0].strip())
        cidr = int(parts[1].strip())
        return ip_val, cidr
    else:
        # Default to /24 if only IP provided
        return ip_to_int(text), 24


def int_to_binary_str(val: int) -> str:
    """Return 32-bit binary string separated into 4 octets by dots."""
    val = val & 0xFFFFFFFF
    b = f"{val:032b}"
    return f"{b[0:8]}.{b[8:16]}.{b[16:24]}.{b[24:32]}"


def get_ip_class(ip_int: int) -> str:
    """Determine Class A, B, C, D, or E."""
    first_octet = (ip_int >> 24) & 0xFF
    if first_octet < 128:
        return "Class A"
    elif first_octet < 192:
        return "Class B"
    elif first_octet < 224:
        return "Class C"
    elif first_octet < 240:
        return "Class D (Multicast)"
    else:
        return "Class E (Experimental / Reserved)"


def get_ip_scope(ip_int: int) -> str:
    """Determine RFC 1918 Private, Loopback, APIPA, or Public."""
    first = (ip_int >> 24) & 0xFF
    second = (ip_int >> 16) & 0xFF

    if first == 10:
        return "Private (RFC 1918 - Class A)"
    elif first == 172 and (16 <= second <= 31):
        return "Private (RFC 1918 - Class B)"
    elif first == 192 and second == 168:
        return "Private (RFC 1918 - Class C)"
    elif first == 127:
        return "Loopback Address"
    elif first == 169 and second == 254:
        return "Link-Local / APIPA (RFC 3927)"
    elif first >= 224 and first <= 239:
        return "Multicast Scope (RFC 5771)"
    elif first >= 240:
        return "Reserved / Experimental"
    elif first == 0:
        return "This Network (RFC 1122)"
    else:
        return "Public Internet Routable"


def calculate_ip_info(ip_int: int, cidr: int) -> Dict[str, Any]:
    """Calculate complete IPv4 subnet parameters (computed via C Native Core DLL if loaded)."""
    # Prefer C Native Core DLL calculation
    if _c_backend:
        try:
            ip_str = int_to_ip(ip_int)
            ip_cidr_bytes = f"{ip_str}/{cidr}".encode("utf-8")
            buf = ctypes.create_string_buffer(4096)
            if _c_backend.c_calculate_ip_info_fast(ip_cidr_bytes, buf, 4096) == 1:
                c_res = json.loads(buf.value.decode("utf-8"))
                if c_res.get("success"):
                    mask_int = cidr_to_mask_int(cidr)
                    wildcard_int = calculate_wildcard_int(mask_int)
                    network_int = (ip_int & mask_int) & 0xFFFFFFFF
                    broadcast_int = (network_int | wildcard_int) & 0xFFFFFFFF
                    total_ips = c_res.get("total_hosts", 1 if cidr == 32 else (1 << (32 - cidr)))
                    usable_hosts = c_res.get("usable_hosts", max(0, total_ips - 2) if cidr < 31 else total_ips)
                    first_usable = network_int if cidr >= 31 else network_int + 1
                    last_usable = broadcast_int if cidr >= 31 else broadcast_int - 1
                    default_net_bits = 24 if ip_int >= 0xC0000000 else (16 if ip_int >= 0x80000000 else 8)
                    borrowed_bits = max(0, cidr - default_net_bits)

                    return {
                        "ip_int": ip_int,
                        "cidr": cidr,
                        "ip_str": c_res.get("ip_address_str", ip_str),
                        "ip_address": c_res.get("ip_address_str", ip_str),
                        "mask_int": mask_int,
                        "mask_str": c_res.get("subnet_mask_str", int_to_ip(mask_int)),
                        "subnet_mask": c_res.get("subnet_mask_str", int_to_ip(mask_int)),
                        "subnet_mask_str": c_res.get("subnet_mask_str", int_to_ip(mask_int)),
                        "wildcard_int": wildcard_int,
                        "wildcard_str": c_res.get("wildcard_mask_str", int_to_ip(wildcard_int)),
                        "wildcard_mask": c_res.get("wildcard_mask_str", int_to_ip(wildcard_int)),
                        "network_int": network_int,
                        "network_str": c_res.get("network_ip_str", int_to_ip(network_int)),
                        "network_ip": c_res.get("network_ip_str", int_to_ip(network_int)),
                        "broadcast_int": broadcast_int,
                        "broadcast_str": c_res.get("broadcast_ip_str", int_to_ip(broadcast_int)),
                        "broadcast_ip": c_res.get("broadcast_ip_str", int_to_ip(broadcast_int)),
                        "first_usable_int": first_usable,
                        "first_usable_str": c_res.get("first_usable_str", int_to_ip(first_usable)),
                        "first_usable_ip": c_res.get("first_usable_str", int_to_ip(first_usable)),
                        "last_usable_int": last_usable,
                        "last_usable_str": c_res.get("last_usable_str", int_to_ip(last_usable)),
                        "last_usable_ip": c_res.get("last_usable_str", int_to_ip(last_usable)),
                        "total_ips": total_ips,
                        "total_hosts": total_ips,
                        "usable_hosts": usable_hosts,
                        "ip_class": c_res.get("ip_class", get_ip_class(ip_int)),
                        "scope": c_res.get("scope", get_ip_scope(ip_int)),
                        "ip_scope": c_res.get("scope", get_ip_scope(ip_int)),
                        "binary_ip": c_res.get("binary_ip", int_to_binary_str(ip_int)),
                        "ip_binary": c_res.get("binary_ip", int_to_binary_str(ip_int)),
                        "binary_mask": c_res.get("binary_mask", int_to_binary_str(mask_int)),
                        "mask_binary": c_res.get("binary_mask", int_to_binary_str(mask_int)),
                        "binary_network": c_res.get("binary_network", int_to_binary_str(network_int)),
                        "network_binary": c_res.get("binary_network", int_to_binary_str(network_int)),
                        "binary_broadcast": c_res.get("binary_broadcast", int_to_binary_str(broadcast_int)),
                        "broadcast_binary": c_res.get("binary_broadcast", int_to_binary_str(broadcast_int)),
                        "network_bits": default_net_bits,
                        "borrowed_bits": borrowed_bits,
                        "host_bits": 32 - cidr,
                        "engine": "C Native Core (MSVC 64-bit)"
                    }
        except Exception:
            pass

    mask_int = cidr_to_mask_int(cidr)
    wildcard_int = calculate_wildcard_int(mask_int)
    network_int = (ip_int & mask_int) & 0xFFFFFFFF
    broadcast_int = (network_int | wildcard_int) & 0xFFFFFFFF

    total_ips = 1 if cidr == 32 else (1 << (32 - cidr))
    if cidr >= 31:
        usable_hosts = total_ips
        first_usable = network_int
        last_usable = broadcast_int
    else:
        usable_hosts = total_ips - 2
        first_usable = network_int + 1
        last_usable = broadcast_int - 1

    default_net_bits = 24 if ip_int >= 0xC0000000 else (16 if ip_int >= 0x80000000 else 8)
    borrowed_bits = max(0, cidr - default_net_bits)

    ip_str = int_to_ip(ip_int)
    mask_str = int_to_ip(mask_int)
    wildcard_str = int_to_ip(wildcard_int)
    network_str = int_to_ip(network_int)
    broadcast_str = int_to_ip(broadcast_int)
    first_usable_str = int_to_ip(first_usable)
    last_usable_str = int_to_ip(last_usable)
    binary_ip = int_to_binary_str(ip_int)
    binary_mask = int_to_binary_str(mask_int)
    binary_network = int_to_binary_str(network_int)
    binary_broadcast = int_to_binary_str(broadcast_int)
    scope = get_ip_scope(ip_int)
    ip_class = get_ip_class(ip_int)

    return {
        "ip_int": ip_int,
        "cidr": cidr,
        "ip_str": ip_str,
        "ip_address": ip_str,
        "mask_int": mask_int,
        "mask_str": mask_str,
        "subnet_mask": mask_str,
        "subnet_mask_str": mask_str,
        "wildcard_int": wildcard_int,
        "wildcard_str": wildcard_str,
        "wildcard_mask": wildcard_str,
        "network_int": network_int,
        "network_str": network_str,
        "network_ip": network_str,
        "broadcast_int": broadcast_int,
        "broadcast_str": broadcast_str,
        "broadcast_ip": broadcast_str,
        "first_usable_int": first_usable,
        "first_usable_str": first_usable_str,
        "first_usable_ip": first_usable_str,
        "last_usable_int": last_usable,
        "last_usable_str": last_usable_str,
        "last_usable_ip": last_usable_str,
        "total_ips": total_ips,
        "total_hosts": total_ips,
        "usable_hosts": usable_hosts,
        "ip_class": ip_class,
        "scope": scope,
        "ip_scope": scope,
        "binary_ip": binary_ip,
        "ip_binary": binary_ip,
        "binary_mask": binary_mask,
        "mask_binary": binary_mask,
        "binary_network": binary_network,
        "network_binary": binary_network,
        "binary_broadcast": binary_broadcast,
        "broadcast_binary": binary_broadcast,
        "network_bits": default_net_bits,
        "borrowed_bits": borrowed_bits,
        "host_bits": 32 - cidr,
    }


class LabSpec:
    """Represents a laboratory specification in VLSM calculation."""

    def __init__(self, name: str, department: str, workstations: int, growth_percent: int = 10, vlan_id: int = 10):
        self.id: int = 0
        self.name: str = name.strip() or "Unnamed Lab"
        self.department: str = department.strip() or "Campus"
        self.workstations: int = max(1, int(workstations))
        self.growth_percent: int = max(0, int(growth_percent))
        self.vlan_id: int = max(1, int(vlan_id))

        buffered = self.workstations * (1.0 + (self.growth_percent / 100.0))
        self.effective_hosts: int = max(2, math.ceil(buffered))

        # Computed fields
        self.allocated_cidr: int = 24
        self.is_allocated: bool = False
        self.is_supernet: bool = False
        self.component_labs_count: int = 0
        self.component_names: List[str] = []
        self.subnet_mask: int = 0
        self.network_ip: int = 0
        self.broadcast_ip: int = 0
        self.first_usable: int = 0
        self.last_usable: int = 0
        self.gateway_ip: int = 0
        self.dns_server_ip: int = 0
        self.block_size: int = 0
        self.usable_capacity: int = 0
        self.wasted_ips: int = 0
        self.efficiency_pct: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        if self.is_allocated:
            sub_mask_str = int_to_ip(self.subnet_mask)
            net_ip_str = int_to_ip(self.network_ip)
            bcast_str = int_to_ip(self.broadcast_ip)
            f_usable_str = int_to_ip(self.first_usable)
            l_usable_str = int_to_ip(self.last_usable)
            gw_str = int_to_ip(self.gateway_ip)
            dns_str = int_to_ip(self.dns_server_ip)
            sub_str = f"{net_ip_str}/{self.allocated_cidr}"
            rng_str = f"{f_usable_str} -> {l_usable_str}"
        else:
            sub_mask_str = int_to_ip(cidr_to_mask_int(self.allocated_cidr))
            net_ip_str = "--"
            bcast_str = "--"
            f_usable_str = "--"
            l_usable_str = "--"
            gw_str = "--"
            dns_str = "--"
            sub_str = f"⚠️ Unallocated (Needs /{self.allocated_cidr})"
            rng_str = f"Needs {self.block_size} IPs (Base Exhausted)"

        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "workstations": self.workstations,
            "growth_percent": self.growth_percent,
            "effective_hosts": self.effective_hosts,
            "vlan_id": self.vlan_id,
            "allocated_cidr": self.allocated_cidr,
            "is_allocated": self.is_allocated,
            "subnet_mask_str": sub_mask_str,
            "network_ip_str": net_ip_str,
            "broadcast_ip_str": bcast_str,
            "first_usable_str": f_usable_str,
            "last_usable_str": l_usable_str,
            "gateway_ip_str": gw_str,
            "dns_server_ip_str": dns_str,
            "block_size": self.block_size,
            "usable_capacity": self.usable_capacity,
            "wasted_ips": self.wasted_ips,
            "efficiency_pct": round(self.efficiency_pct, 1),
            "subnet_str": sub_str,
            "range_str": rng_str,
            "is_supernet": getattr(self, "is_supernet", False),
            "component_labs_count": getattr(self, "component_labs_count", 0),
            "component_names": getattr(self, "component_names", []),
        }


class CampusVLSM:
    """Manages multi-lab VLSM calculation, address alignment, and metrics."""

    def __init__(self, base_ip_str: str = "10.50.0.0", base_cidr: int = 16):
        self.base_ip_str: str = base_ip_str
        self.base_cidr: int = base_cidr
        self.base_ip: int = ip_to_int(base_ip_str)
        self.base_mask: int = cidr_to_mask_int(base_cidr)
        self.base_network_ip: int = self.base_ip & self.base_mask
        self.base_broadcast: int = self.base_network_ip | calculate_wildcard_int(self.base_mask)
        self.total_campus_capacity: int = 1 if base_cidr >= 32 else (1 << (32 - base_cidr))

        self.labs: List[LabSpec] = []
        self.is_calculated: bool = False
        self.is_valid: bool = False
        self.error_reason: str = ""

        # Summary Metrics
        self.total_requested_hosts: int = 0
        self.total_allocated_blocks: int = 0
        self.total_usable_hosts: int = 0
        self.total_wasted_ips: int = 0
        self.overall_efficiency: float = 0.0
        self.next_free_subnet: int = self.base_network_ip
        self.free_ips_remaining: int = self.total_campus_capacity
        self.recommended_cidr: int = base_cidr
        self.total_needed_blocks: int = 0
        self.merge_history: List[Dict[str, Any]] = []

    def update_base(self, base_ip_str: str, base_cidr: int):
        self.base_ip_str = base_ip_str.strip()
        self.base_cidr = base_cidr
        self.base_ip = ip_to_int(self.base_ip_str)
        self.base_mask = cidr_to_mask_int(base_cidr)
        self.base_network_ip = self.base_ip & self.base_mask
        self.base_broadcast = self.base_network_ip | calculate_wildcard_int(self.base_mask)
        self.total_campus_capacity = 1 if base_cidr >= 32 else (1 << (32 - base_cidr))
        self.is_calculated = False

    def add_lab(self, name: str, dept: str, workstations: int, growth_percent: int = 10, vlan_id: int = 0) -> LabSpec:
        if vlan_id <= 0:
            vlan_id = 10 + len(self.labs) * 10
        lab = LabSpec(name, dept, workstations, growth_percent, vlan_id)
        lab.id = len(self.labs) + 1
        self.labs.append(lab)
        self.is_calculated = False
        return lab

    def edit_lab(self, lab_id: int, name: str, dept: str, workstations: int, growth_percent: int = 10, vlan_id: int = 0) -> bool:
        for lab in self.labs:
            if lab.id == lab_id:
                lab.name = name.strip() if name else lab.name
                lab.department = dept.strip() if dept else lab.department
                lab.workstations = max(1, int(workstations))
                lab.growth_percent = max(0, int(growth_percent))
                if vlan_id > 0:
                    lab.vlan_id = int(vlan_id)
                buffered = lab.workstations * (1.0 + (lab.growth_percent / 100.0))
                lab.effective_hosts = max(2, math.ceil(buffered))
                self.is_calculated = False
                return self.calculate()
        return False

    def remove_lab(self, index: int) -> bool:
        if 0 <= index < len(self.labs):
            del self.labs[index]
            for i, lab in enumerate(self.labs):
                lab.id = i + 1
            self.is_calculated = False
            return True
        return False

    def clear_labs(self):
        self.labs.clear()
        self.is_calculated = False

    def load_college_preset(self):
        self.update_base("10.50.0.0", 16)
        self.clear_labs()
        preset_data = [
            ("Artificial Intelligence & Robotics Lab", "CSE Dept - Block A", 120, 15, 10),
            ("Cloud Computing & Data Science Lab", "CSE Dept - Block A", 90, 10, 20),
            ("Cyber Security & Forensics Lab", "IT Dept - Block B", 65, 10, 30),
            ("Internet of Things (IoT) Embedded Lab", "ECE Dept - Block C", 45, 10, 40),
            ("Object-Oriented Programming Lab", "CSE Dept - Block A", 60, 10, 50),
            ("High-Performance Data Center Farm", "Central IT Wing", 30, 20, 60),
            ("Faculty Research & Admin Wing", "Admin Building", 22, 5, 70),
            ("Core Router Inter-Switch Backbone", "Campus WAN Infra", 2, 0, 99),
        ]
        for name, dept, pc, gr, vlan in preset_data:
            self.add_lab(name, dept, pc, gr, vlan)
        self.calculate()

    def setup_n_labs(self, num_labs: int, base_pc: int = 120, step: int = 15) -> bool:
        """Dynamically configure N laboratories with realistic host demands scaled to campus capacity."""
        self.clear_labs()
        num_labs = max(1, min(num_labs, 32))

        lab_names = [
            ("Computer Networks Lab", "CSE Dept - Block A"),
            ("Web Technologies Lab", "IT Dept - Block B"),
            ("IoT Systems Lab", "ECE Dept - Block C"),
            ("Data Science & Big Data Lab", "AI Dept - Block D"),
            ("Cyber Security Lab", "IT Dept - Block B"),
            ("Artificial Intelligence Lab", "CSE Dept - Block A"),
            ("Software Engineering Studio", "IT Dept - Block B"),
            ("Database Systems Lab", "CSE Dept - Block A"),
            ("Cloud Infrastructure Lab", "Central IT Wing"),
            ("Embedded Systems Lab", "ECE Dept - Block C"),
            ("Mobile Applications Lab", "IT Dept - Block B"),
            ("High-Performance Computing Lab", "Admin Building")
        ]

        cap = self.total_campus_capacity
        if cap <= 256:
            # /24 scope (256 IPs) -> scale hosts safely so N labs fit cleanly
            if num_labs == 1:
                pcs_pool = [100]
            elif num_labs == 2:
                pcs_pool = [60, 40]
            elif num_labs == 3:
                pcs_pool = [50, 35, 20]
            elif num_labs == 4:
                pcs_pool = [45, 30, 20, 15]
            elif num_labs == 5:
                pcs_pool = [35, 25, 20, 15, 10]
            else:
                pcs_pool = [max(8, int(180 / num_labs))] * num_labs
        elif cap <= 1024:
            # /22 to /23 (512 - 1024 IPs)
            base = [90, 75, 55, 45, 35, 30, 25, 20]
            pcs_pool = [base[i % len(base)] for i in range(num_labs)]
        else:
            # /16 to /20 (4,096 to 65,536 IPs)
            base = [120, 90, 65, 45, 60, 50, 40, 35, 30]
            pcs_pool = [base[i % len(base)] for i in range(num_labs)]

        for i in range(num_labs):
            if i < len(lab_names):
                name, dept = lab_names[i]
            else:
                name = f"Computer Laboratory {i + 1}"
                dept = f"Department Wing {chr(65 + (i % 6))}"

            pcs = pcs_pool[i] if i < len(pcs_pool) else max(10, 50 - (i * 5))
            growth = 10
            vlan = (i + 1) * 10
            self.add_lab(name, dept, pcs, growth, vlan)

        return self.calculate()

    def add_systems_to_lab(self, lab_id: int, count: int = 1) -> Dict[str, Any]:
        """
        Dynamically add one or more new systems (PCs/workstations) to an existing lab.
        Recalculates VLSM allocations, detecting if subnet expansion occurs.
        """
        target_lab = None
        for lab in self.labs:
            if lab.id == lab_id:
                target_lab = lab
                break
        if not target_lab:
            raise ValueError(f"Laboratory #{lab_id} not found.")

        if count <= 0:
            raise ValueError("Number of systems to add must be at least 1.")

        old_pcs = target_lab.workstations
        old_cidr = target_lab.allocated_cidr
        old_subnet = target_lab.to_dict().get("subnet_str", "")

        target_lab.workstations += count
        buffered = target_lab.workstations * (1.0 + (target_lab.growth_percent / 100.0))
        target_lab.effective_hosts = max(2, math.ceil(buffered))

        # Recalculate campus allocations
        success = self.calculate()
        new_cidr = target_lab.allocated_cidr
        new_subnet = target_lab.to_dict().get("subnet_str", "")
        expanded = (new_cidr != old_cidr)

        return {
            "success": success,
            "lab_id": target_lab.id,
            "lab_name": target_lab.name,
            "old_workstations": old_pcs,
            "new_workstations": target_lab.workstations,
            "added_count": count,
            "old_cidr": old_cidr,
            "new_cidr": new_cidr,
            "old_subnet": old_subnet,
            "new_subnet": new_subnet,
            "expanded": expanded,
            "usable_capacity": target_lab.usable_capacity,
            "spare_slots": max(0, target_lab.usable_capacity - target_lab.workstations),
        }

    def calculate(self) -> bool:
        if not self.labs:
            self.is_valid = False
            self.is_calculated = False
            self.error_reason = "No labs added to design."
            return False

        # Reset all lab allocation flags
        for lab in self.labs:
            lab.is_allocated = False

        # Sort labs descending by effective_hosts (VLSM fundamental constraint)
        self.labs.sort(key=lambda lab: lab.effective_hosts, reverse=True)
        for i, lab in enumerate(self.labs):
            lab.id = i + 1

        current_network = self.base_network_ip
        self.total_requested_hosts = 0
        self.total_allocated_blocks = 0
        self.total_usable_hosts = 0
        self.total_wasted_ips = 0

        exhausted_at = None
        total_needed_sum = 0

        for lab in self.labs:
            self.total_requested_hosts += lab.workstations

            # Determine minimum host bits required: (2^h - 2) >= effective_hosts
            h = 2
            while h < 31 and ((1 << h) - 2) < lab.effective_hosts:
                h += 1

            cidr = 32 - h
            block_size = 1 << h
            lab.allocated_cidr = cidr
            lab.block_size = block_size
            lab.usable_capacity = max(0, block_size - 2)
            total_needed_sum += block_size

            # If already exhausted in a prior lab, mark unallocated and continue
            if exhausted_at is not None:
                lab.is_allocated = False
                continue

            # Align to power-of-2 block boundary
            if current_network % block_size != 0:
                current_network = ((current_network + block_size - 1) // block_size) * block_size

            # Check address exhaustion
            subnet_end = current_network + block_size - 1
            if subnet_end > self.base_broadcast:
                exhausted_at = lab
                lab.is_allocated = False
                continue

            lab.is_allocated = True
            lab.subnet_mask = cidr_to_mask_int(cidr)
            lab.network_ip = current_network
            lab.broadcast_ip = subnet_end
            lab.first_usable = current_network + 1
            lab.last_usable = lab.broadcast_ip - 1
            lab.gateway_ip = lab.first_usable
            lab.dns_server_ip = current_network + 2
            lab.wasted_ips = lab.usable_capacity - lab.effective_hosts
            lab.efficiency_pct = (lab.workstations / lab.usable_capacity) * 100.0

            self.total_allocated_blocks += block_size
            self.total_usable_hosts += lab.usable_capacity
            self.total_wasted_ips += lab.wasted_ips

            current_network += block_size

        self.total_needed_blocks = total_needed_sum
        needed_cap = 1
        while needed_cap < max(4, total_needed_sum):
            needed_cap <<= 1
        self.recommended_cidr = 32 - int(math.log2(needed_cap))

        if exhausted_at is not None:
            self.is_calculated = True
            self.is_valid = False
            self.error_reason = (
                f"IP address space exhausted at '{exhausted_at.name}' (needs block size {exhausted_at.block_size} IPs). "
                f"Base scope has {self.total_campus_capacity} IPs, but your labs require {self.total_needed_blocks} IPs. "
                f"Please expand base scope to /{self.recommended_cidr} ({needed_cap:,} IPs) or reduce workstations."
            )
            self.next_free_subnet = current_network
            self.free_ips_remaining = 0
            return False

        self.next_free_subnet = current_network
        if self.base_broadcast >= current_network:
            self.free_ips_remaining = (self.base_broadcast - current_network) + 1
        else:
            self.free_ips_remaining = 0

        if self.total_usable_hosts > 0:
            self.overall_efficiency = (self.total_requested_hosts / self.total_usable_hosts) * 100.0
        else:
            self.overall_efficiency = 0.0

        self.is_calculated = True
        self.is_valid = True
        self.error_reason = ""
        return True

    def merge_labs_into_supernet(self, lab_ids: List[int], new_name: str, new_dept: str = "") -> Dict[str, Any]:
        """
        Consolidates selected laboratories into a single supernet laboratory with a user-given name.
        Saves full campus state snapshot into merge_history for one-click splitting/reversion.
        """
        int_ids = [int(x) for x in lab_ids]
        selected_labs = [l for l in self.labs if l.id in int_ids and l.is_allocated]
        if len(selected_labs) < 2:
            raise ValueError("Supernetting requires at least 2 allocated laboratories to merge.")

        subnets = [l.to_dict()["subnet_str"] for l in selected_labs]
        sup_res = calculate_supernet(subnets)

        # Snapshot for full faithful restoration
        snapshot = {
            "timestamp": time.time(),
            "base_ip_str": self.base_ip_str,
            "base_cidr": self.base_cidr,
            "merged_name": new_name.strip(),
            "supernet_str": sup_res["supernet_str"],
            "merged_ids": int_ids,
            "original_labs": [
                {
                    "name": l.name,
                    "department": l.department,
                    "workstations": l.workstations,
                    "growth_percent": l.growth_percent,
                    "vlan_id": l.vlan_id,
                    "is_supernet": getattr(l, "is_supernet", False)
                }
                for l in self.labs
            ]
        }
        self.merge_history.append(snapshot)

        # Merged lab specifications
        total_ws = sum(l.workstations for l in selected_labs)
        combined_dept = new_dept.strip() or selected_labs[0].department
        combined_vlan = min(l.vlan_id for l in selected_labs)

        merged_lab = LabSpec(
            name=new_name.strip() or f"Consolidated Super-Lab ({len(selected_labs)} Labs)",
            department=combined_dept,
            workstations=total_ws,
            growth_percent=0,
            vlan_id=combined_vlan
        )
        merged_lab.is_supernet = True
        merged_lab.component_labs_count = len(selected_labs)
        merged_lab.component_names = [l.name for l in selected_labs]

        # Filter out merged member labs and add the unified supernet lab
        remaining = [l for l in self.labs if l.id not in int_ids]
        self.labs = remaining + [merged_lab]

        # Check if base network capacity needs expansion for the consolidated block
        total_needed = 0
        for l in self.labs:
            h = 2
            while h < 31 and ((1 << h) - 2) < l.effective_hosts:
                h += 1
            total_needed += (1 << h)

        if total_needed > self.total_campus_capacity:
            needed_cap = 1
            while needed_cap < max(4, total_needed):
                needed_cap <<= 1
            new_cidr = 32 - int(math.log2(needed_cap))
            self.update_base(self.base_ip_str, min(self.base_cidr, new_cidr))

        self.calculate()
        return {
            "success": True,
            "supernet": sup_res,
            "merged_name": merged_lab.name,
            "component_count": len(selected_labs),
            "total_workstations": total_ws
        }

    def split_supernet(self, snapshot_idx: int = -1) -> Dict[str, Any]:
        """
        Splits the consolidated supernet and restores the exact original separate laboratories.
        """
        if not self.merge_history:
            raise ValueError("No supernet merge history found to split or revert.")

        snapshot = self.merge_history.pop(snapshot_idx)

        # Restore original base scope
        self.update_base(snapshot["base_ip_str"], snapshot["base_cidr"])
        self.clear_labs()

        # Reconstruct all original laboratories
        for d in snapshot["original_labs"]:
            lab = self.add_lab(
                name=d["name"],
                dept=d["department"],
                workstations=d["workstations"],
                growth_percent=d["growth_percent"],
                vlan_id=d["vlan_id"]
            )
            lab.is_supernet = d.get("is_supernet", False)

        self.calculate()
        return {
            "success": True,
            "restored_count": len(self.labs),
            "restored_names": [l.name for l in self.labs]
        }


def generate_lab_prefix(name: str) -> str:
    """Generate 2-4 uppercase acronym from lab name."""
    words = re.findall(r"[A-Za-z0-9]+", name)
    prefix = "".join(w[0].upper() for w in words if w)
    if len(prefix) < 2 and words:
        prefix = words[0][:3].upper()
    return prefix or "LAB"


def generate_lab_inventory(lab: LabSpec) -> Dict[str, Any]:
    """Generate workstation-by-workstation inventory and DHCP scope."""
    prefix = generate_lab_prefix(lab.name)
    total_slots = lab.usable_capacity

    records = []
    # Index 1: Gateway
    records.append({
        "index": 1,
        "hostname": f"{prefix}-GW01",
        "role": "Default Gateway",
        "ip_str": int_to_ip(lab.gateway_ip),
        "mask_str": int_to_ip(lab.subnet_mask),
        "gateway_str": "Self (L3 Interface)",
        "dns_str": int_to_ip(lab.dns_server_ip),
    })

    # Index 2: Local Server / DNS Cache
    records.append({
        "index": 2,
        "hostname": f"{prefix}-SRV01",
        "role": "Local Cache / DNS Server",
        "ip_str": int_to_ip(lab.dns_server_ip),
        "mask_str": int_to_ip(lab.subnet_mask),
        "gateway_str": int_to_ip(lab.gateway_ip),
        "dns_str": "127.0.0.1 (Local)",
    })

    # Index 3: Network Printer
    prn_ip = lab.network_ip + 3
    records.append({
        "index": 3,
        "hostname": f"{prefix}-PRN01",
        "role": "Network Laser Printer",
        "ip_str": int_to_ip(prn_ip),
        "mask_str": int_to_ip(lab.subnet_mask),
        "gateway_str": int_to_ip(lab.gateway_ip),
        "dns_str": int_to_ip(lab.dns_server_ip),
    })

    # Student Workstations
    dhcp_start_ip = lab.network_ip + 4
    for pc_idx in range(1, lab.workstations + 1):
        ip_val = dhcp_start_ip + (pc_idx - 1)
        if ip_val > lab.last_usable:
            break
        records.append({
            "index": len(records) + 1,
            "hostname": f"{prefix}-PC-{pc_idx:02d}",
            "role": "Student Workstation",
            "ip_str": int_to_ip(ip_val),
            "mask_str": int_to_ip(lab.subnet_mask),
            "gateway_str": int_to_ip(lab.gateway_ip),
            "dns_str": int_to_ip(lab.dns_server_ip),
        })

    # Spare / Expansion addresses
    spare_idx = 1
    current_ip = dhcp_start_ip + lab.workstations
    while current_ip <= lab.last_usable:
        records.append({
            "index": len(records) + 1,
            "hostname": f"{prefix}-SPARE-{spare_idx:02d}",
            "role": "Expansion / Spare Pool",
            "ip_str": int_to_ip(current_ip),
            "mask_str": int_to_ip(lab.subnet_mask),
            "gateway_str": int_to_ip(lab.gateway_ip),
            "dns_str": int_to_ip(lab.dns_server_ip),
        })
        current_ip += 1
        spare_idx += 1

    dhcp_leases = max(0, (lab.last_usable - dhcp_start_ip) + 1)

    def_gw = int_to_ip(lab.gateway_ip)
    sub_mask = int_to_ip(lab.subnet_mask)
    dns_srv = int_to_ip(lab.dns_server_ip)
    pool_start = int_to_ip(dhcp_start_ip)
    pool_end = int_to_ip(lab.last_usable)

    # Add normalized aliases to records for frontend table compatibility
    for r in records:
        r["number"] = r["index"]
        r["ip_address"] = r["ip_str"]
        r["subnet_mask"] = r["mask_str"]
        r["default_gateway"] = r["gateway_str"]
        r["dns_server"] = r["dns_str"]

    cisco_cli = f"""! Cisco IOS DHCP Pool: {lab.name} (VLAN {lab.vlan_id})
ip dhcp excluded-address {int_to_ip(lab.network_ip)} {int_to_ip(dhcp_start_ip - 1)}
ip dhcp pool VLAN_{lab.vlan_id}_{prefix}
 network {int_to_ip(lab.network_ip)} {sub_mask}
 default-router {def_gw}
 dns-server {dns_srv} 8.8.8.8
 domain-name campus.netlab.edu
 lease 7 0 0
exit"""

    dhcp_scope = {
        "lab_name": lab.name,
        "vlan_id": lab.vlan_id,
        "pool_network": int_to_ip(lab.network_ip),
        "subnet_mask": sub_mask,
        "default_gateway": def_gw,
        "dns_server": dns_srv,
        "dhcp_range_start": pool_start,
        "dhcp_range_end": pool_end,
        "total_leases": dhcp_leases,
        "lease_days": 7,
    }

    return {
        "lab_name": lab.name,
        "total_hosts": len(records),
        "records": records,
        "inventory": records,
        "workstations": records,
        "default_gateway": def_gw,
        "subnet_mask": sub_mask,
        "dns_server": dns_srv,
        "dhcp_pool_start": pool_start,
        "dhcp_pool_end": pool_end,
        "dhcp_range_start": pool_start,
        "dhcp_range_end": pool_end,
        "cisco_dhcp_cli": cisco_cli,
        "dhcp": dhcp_scope,
    }


def analyze_reachability(ip_a_str: str, cidr_a: int, ip_b_str: str, cidr_b: int) -> Dict[str, Any]:
    """Diagnose L2 vs L3 routing, asymmetric mask, or invalid IPs (accelerated via C Native Core DLL)."""
    ip_a = ip_to_int(ip_a_str)
    ip_b = ip_to_int(ip_b_str)
    mask_a = cidr_to_mask_int(cidr_a)
    mask_b = cidr_to_mask_int(cidr_b)

    net_a = (ip_a & mask_a) & 0xFFFFFFFF
    net_b = (ip_b & mask_b) & 0xFFFFFFFF

    bcast_a = (net_a | calculate_wildcard_int(mask_a)) & 0xFFFFFFFF
    bcast_b = (net_b | calculate_wildcard_int(mask_b)) & 0xFFFFFFFF

    engine_tag = "C Native Core (MSVC 64-bit)" if _c_backend else "Python Core"

    # Call C Native Core DLL if loaded
    c_diag = None
    c_rec = None
    if _c_backend:
        try:
            buf = ctypes.create_string_buffer(4096)
            if _c_backend.c_analyze_reachability_fast(ip_a_str.encode("utf-8"), cidr_a, ip_b_str.encode("utf-8"), cidr_b, buf, 4096) == 1:
                c_res = json.loads(buf.value.decode("utf-8"))
                if c_res.get("success"):
                    c_diag = c_res.get("diagnosis")
                    c_rec = c_res.get("recommendation")
        except Exception:
            pass

    if ip_a in (net_a, bcast_a) or ip_b in (net_b, bcast_b):
        return {
            "status": "INVALID_HOST",
            "path_type": "INVALID_HOST",
            "badge": "⚠️ Reserved IP",
            "summary_badge": "⚠️ Reserved IP",
            "badge_color": "yellow",
            "headline": "Invalid Host IP Address Assigned",
            "verdict": "Invalid Host IP Address Assigned",
            "net_a": f"{int_to_ip(net_a)}/{cidr_a}",
            "net_b": f"{int_to_ip(net_b)}/{cidr_b}",
            "host_a": {"network": f"{int_to_ip(net_a)}/{cidr_a}"},
            "host_b": {"network": f"{int_to_ip(net_b)}/{cidr_b}"},
            "diagnosis": c_diag or "One or both configured IP addresses match the reserved Subnet ID or Broadcast ID for their respective network.",
            "detailed_explanation": c_diag or "One or both configured IP addresses match the reserved Subnet ID or Broadcast ID for their respective network.",
            "recommendation": c_rec or "Assign a valid host IP strictly within the usable range (First Usable -> Last Usable).",
            "next_hop_recommendation": "Assign valid host IP inside usable subnet boundaries.",
            "engine": engine_tag
        }

    a_thinks_b_local = ((ip_b & mask_a) & 0xFFFFFFFF) == net_a
    b_thinks_a_local = ((ip_a & mask_b) & 0xFFFFFFFF) == net_b

    if a_thinks_b_local and b_thinks_a_local and (cidr_a == cidr_b):
        diag_msg = c_diag or (
            f"Both hosts belong to the identical subnet ({int_to_ip(net_a)}/{cidr_a}). "
            "Host A broadcasts an ARP Request for Host B's MAC address directly over the local L2 switch. "
            "Frames are switched at wire speed with 0 router hops."
        )
        return {
            "status": "SAME_SUBNET_L2",
            "path_type": "SAME_SUBNET_L2",
            "badge": "🟢 Direct Layer-2 Switched Path",
            "summary_badge": "🟢 Direct Layer-2 Switched Path",
            "badge_color": "green",
            "headline": f"Direct Layer-2 Switched Delivery (Subnet: {int_to_ip(net_a)}/{cidr_a})",
            "verdict": f"Direct Layer-2 Switched Delivery ({int_to_ip(net_a)}/{cidr_a})",
            "net_a": f"{int_to_ip(net_a)}/{cidr_a}",
            "net_b": f"{int_to_ip(net_b)}/{cidr_b}",
            "host_a": {"network": f"{int_to_ip(net_a)}/{cidr_a}"},
            "host_b": {"network": f"{int_to_ip(net_b)}/{cidr_b}"},
            "diagnosis": diag_msg,
            "detailed_explanation": diag_msg,
            "recommendation": c_rec or "No IP router or default gateway needed. Ensure both switch ports share the same 802.1Q VLAN ID.",
            "next_hop_recommendation": "Direct ARP Resolution (Local Layer-2 Switch)",
            "engine": engine_tag
        }
    elif a_thinks_b_local != b_thinks_a_local:
        diag_msg = c_diag or (
            f"Host A has mask /{cidr_a} while Host B has /{cidr_b}. "
            f"Host {'A' if a_thinks_b_local else 'B'} considers the peer local (will ARP), "
            f"while Host {'B' if a_thinks_b_local else 'A'} considers the peer remote (will send to gateway). "
            "This creates an asymmetric blackhole where packets cannot be returned."
        )
        return {
            "status": "ASYMMETRIC_MASK_ERROR",
            "path_type": "ASYMMETRIC",
            "badge": "🔴 Asymmetric Mask Misconfiguration",
            "summary_badge": "🔴 Asymmetric Mask Misconfiguration",
            "badge_color": "red",
            "headline": "Asymmetric Subnet Mask Warning (One-Way Blackhole)",
            "verdict": "Asymmetric Subnet Mask Warning (One-Way Blackhole)",
            "net_a": f"{int_to_ip(net_a)}/{cidr_a}",
            "net_b": f"{int_to_ip(net_b)}/{cidr_b}",
            "host_a": {"network": f"{int_to_ip(net_a)}/{cidr_a}"},
            "host_b": {"network": f"{int_to_ip(net_b)}/{cidr_b}"},
            "diagnosis": diag_msg,
            "detailed_explanation": diag_msg,
            "recommendation": c_rec or "Standardize the subnet mask across all nodes within the same physical broadcast segment.",
            "next_hop_recommendation": "Fix Subnet Mask Misconfiguration",
            "engine": engine_tag
        }
    else:
        diag_msg = c_diag or (
            f"Endpoints reside in distinct subnets (Host A on {int_to_ip(net_a)}/{cidr_a}, "
            f"Host B on {int_to_ip(net_b)}/{cidr_b}). Direct L2 broadcast frames cannot cross subnet boundaries. "
            "Host A forwards packets to its Default Gateway via ARP; an Inter-VLAN Layer-3 Router or L3 Core Switch forwards the packet."
        )
        return {
            "status": "DIFFERENT_SUBNET_L3",
            "path_type": "ROUTED",
            "badge": "🔵 Layer-3 Routed Path Required",
            "summary_badge": "🔵 Layer-3 Routed Path Required",
            "badge_color": "blue",
            "headline": "Inter-Subnet Layer-3 Routing Required",
            "verdict": "Inter-Subnet Layer-3 Routing Required",
            "net_a": f"{int_to_ip(net_a)}/{cidr_a}",
            "net_b": f"{int_to_ip(net_b)}/{cidr_b}",
            "host_a": {"network": f"{int_to_ip(net_a)}/{cidr_a}"},
            "host_b": {"network": f"{int_to_ip(net_b)}/{cidr_b}"},
            "diagnosis": diag_msg,
            "detailed_explanation": diag_msg,
            "recommendation": c_rec or "Configure valid Default Gateways on both endpoints and enable IP routing (802.1Q trunking / SVI) on the Core switch.",
            "next_hop_recommendation": f"Default Gateway SVI Router -> Inter-VLAN L3 Forwarding",
            "engine": engine_tag
        }


def calculate_supernet(networks_input: List[str]) -> Dict[str, Any]:
    """
    Calculate CIDR Supernet / Route Summarization across multiple IPv4 networks.
    Determines Longest Common Prefix (LCP), boundary alignment, contiguity,
    supernet mask, route table reduction percentage, and Cisco IOS summary commands.
    """
    if not networks_input:
        raise ValueError("No networks provided for supernet calculation.")

    # Parse and clean each input
    parsed_items = []
    for raw in networks_input:
        raw_clean = raw.strip()
        if not raw_clean:
            continue
        try:
            ip_val, cidr = parse_ip_cidr(raw_clean)
            mask_val = cidr_to_mask_int(cidr)
            net_val = (ip_val & mask_val) & 0xFFFFFFFF
            bcast_val = (net_val | calculate_wildcard_int(mask_val)) & 0xFFFFFFFF
            block_sz = 1 if cidr == 32 else (1 << (32 - cidr))
            parsed_items.append({
                "network_ip": net_val,
                "cidr": cidr,
                "mask_ip": mask_val,
                "broadcast_ip": bcast_val,
                "block_size": block_sz,
                "network_str": f"{int_to_ip(net_val)}/{cidr}",
                "mask_str": int_to_ip(mask_val),
                "broadcast_str": int_to_ip(bcast_val),
                "first_usable": int_to_ip(net_val + 1) if cidr < 31 else int_to_ip(net_val),
                "last_usable": int_to_ip(bcast_val - 1) if cidr < 31 else int_to_ip(bcast_val),
                "binary_net": int_to_binary_str(net_val),
            })
        except Exception as e:
            raise ValueError(f"Invalid network '{raw_clean}': {e}")

    if not parsed_items:
        raise ValueError("Please provide at least one valid IPv4 network.")

    # Deduplicate and sort by network IP ascending
    unique_nets = {}
    for item in parsed_items:
        key = (item["network_ip"], item["cidr"])
        if key not in unique_nets:
            unique_nets[key] = item
    sorted_nets = sorted(unique_nets.values(), key=lambda x: x["network_ip"])

    num_inputs = len(sorted_nets)
    total_input_ips = sum(item["block_size"] for item in sorted_nets)

    min_net = sorted_nets[0]["network_ip"]
    max_bcast = max(item["broadcast_ip"] for item in sorted_nets)

    # Check contiguity
    is_contiguous = True
    for i in range(1, num_inputs):
        prev_end = sorted_nets[i - 1]["broadcast_ip"]
        curr_start = sorted_nets[i]["network_ip"]
        if curr_start != prev_end + 1:
            is_contiguous = False
            break

    # Find Longest Common Prefix (LCP) between min_net and max_bcast
    diff = (min_net ^ max_bcast) & 0xFFFFFFFF
    if diff == 0:
        supernet_cidr = sorted_nets[0]["cidr"]
    else:
        supernet_cidr = 32 - diff.bit_length()

    supernet_mask = cidr_to_mask_int(supernet_cidr)
    supernet_net = (min_net & supernet_mask) & 0xFFFFFFFF
    supernet_bcast = (supernet_net | calculate_wildcard_int(supernet_mask)) & 0xFFFFFFFF
    supernet_total_ips = 1 if supernet_cidr == 32 else (1 << (32 - supernet_cidr))
    supernet_usable = max(0, supernet_total_ips - 2) if supernet_cidr < 31 else supernet_total_ips

    # Check power-of-2 count and boundary alignment
    is_power_of_2 = (num_inputs > 0) and ((num_inputs & (num_inputs - 1)) == 0)
    is_aligned = (min_net % supernet_total_ips) == 0
    is_optimal = (supernet_total_ips == total_input_ips) and is_contiguous

    # Unallocated / leaked addresses covered by supernet
    extra_covered_ips = max(0, supernet_total_ips - total_input_ips)

    reduction_pct = round(((num_inputs - 1) / num_inputs) * 100.0, 1) if num_inputs > 1 else 0.0

    # Binary representations with LCP split
    supernet_bin_str = int_to_binary_str(supernet_net)
    supernet_mask_bin_str = int_to_binary_str(supernet_mask)

    binary_analysis = []
    for item in sorted_nets:
        b_clean = item["binary_net"].replace(".", "")
        common_bits = b_clean[:supernet_cidr]
        divergent_bits = b_clean[supernet_cidr:]
        binary_analysis.append({
            "network_str": item["network_str"],
            "binary_raw": item["binary_net"],
            "common_bits": common_bits,
            "divergent_bits": divergent_bits,
        })

    # Cisco CLI summary configurations
    cisco_static = f"ip route {int_to_ip(supernet_net)} {int_to_ip(supernet_mask)} Null0"
    cisco_ospf = f"router ospf 1\n area 0 range {int_to_ip(supernet_net)} {int_to_ip(supernet_mask)}"
    cisco_bgp = f"router bgp 65001\n aggregate-address {int_to_ip(supernet_net)} {int_to_ip(supernet_mask)} summary-only"
    cisco_eigrp = f"interface GigabitEthernet0/0/0\n ip summary-address eigrp 100 {int_to_ip(supernet_net)} {int_to_ip(supernet_mask)}"

    # Member masks uniform?
    member_cidrs = [x["cidr"] for x in sorted_nets]
    is_uniform_mask = (len(set(member_cidrs)) == 1) if member_cidrs else True
    base_member_cidr = member_cidrs[0] if member_cidrs else supernet_cidr
    borrowed_bits = max(0, base_member_cidr - supernet_cidr) if is_uniform_mask else 0
    is_valid_supernet = is_contiguous

    rules_checklist = [
        {
            "id": "rule_contiguous",
            "name": "1. Strict Contiguity Rule",
            "passed": is_contiguous,
            "status": "PASS" if is_contiguous else "FAIL",
            "description": "All selected member laboratories are sequentially adjacent with zero address gaps." if is_contiguous else "Address gap detected between selected laboratories (Non-contiguous)."
        },
        {
            "id": "rule_power_of_2",
            "name": "2. Power-of-2 Block Rule (2^n)",
            "passed": is_power_of_2 or is_contiguous,
            "status": "PASS" if (is_power_of_2 or is_contiguous) else "FAIL",
            "description": f"{num_inputs} subnets (2^{int(math.log2(num_inputs))}) satisfies power-of-2 condition." if is_power_of_2 else f"{num_inputs} contiguous laboratories aggregated into a {supernet_total_ips}-IP power-of-2 CIDR block."
        },
        {
            "id": "rule_boundary",
            "name": "3. Base Boundary Divisibility Rule",
            "passed": is_aligned,
            "status": "PASS" if is_aligned else "FAIL",
            "description": f"Base network {int_to_ip(supernet_net)} is evenly divisible by combined block size ({supernet_total_ips} IPs)." if is_aligned else f"Base network {int_to_ip(min_net)} aligned to CIDR boundary."
        },
        {
            "id": "rule_uniform_mask",
            "name": "4. CIDR Prefix Aggregation Rule",
            "passed": is_uniform_mask or is_contiguous,
            "status": "PASS" if (is_uniform_mask or is_contiguous) else "FAIL",
            "description": f"All {num_inputs} subnets have identical /{base_member_cidr} prefix length ({borrowed_bits} bits borrowed back)." if is_uniform_mask else f"CIDR variable-length aggregation consolidates contiguous subnets into common /{supernet_cidr} prefix."
        }
    ]

    # Status assessment
    if is_optimal:
        verdict = "OPTIMAL_SUPERNET"
        verdict_badge = "✅ Optimal Contiguous Supernet"
        verdict_desc = f"All {num_inputs} selected laboratories are strictly contiguous and power-of-2 aligned, consolidated into {int_to_ip(supernet_net)}/{supernet_cidr} with 0 unallocated address leakage."
    elif is_contiguous:
        verdict = "CONTIGUOUS_SUMMARIZATION"
        verdict_badge = "✅ Valid CIDR Contiguous Supernet"
        verdict_desc = f"All {num_inputs} selected laboratories are strictly contiguous with zero address gaps, successfully consolidated into {int_to_ip(supernet_net)}/{supernet_cidr}."
    else:
        verdict = "NON_CONTIGUOUS_SUMMARY"
        verdict_badge = "⚠️ Non-Contiguous Aggregation (Address Gaps Detected)"
        verdict_desc = f"Non-contiguous selection: Unassigned address gaps exist between input subnets. Route summarization aggregates to {int_to_ip(supernet_net)}/{supernet_cidr} with {extra_covered_ips:,} unassigned IP addresses."

    engine_tag = "C Native Core (MSVC 64-bit)" if _c_backend else "Python Core"

    # Execute computation through C Native Core DLL when available
    if _c_backend:
        try:
            subnets_newline = "\n".join(networks_input).encode("utf-8")
            buf = ctypes.create_string_buffer(16384)
            if _c_backend.c_calculate_supernet_fast(subnets_newline, buf, 16384) == 1:
                c_json = json.loads(buf.value.decode("utf-8"))
                if c_json.get("success"):
                    # Use C-engine verified CIDR prefix, reduction %, contiguity and cisco command
                    supernet_cidr = c_json["supernet_cidr"]
                    reduction_pct = c_json["reduction_pct"]
                    is_contiguous = c_json["is_contiguous"]
                    is_power_of_2 = c_json["is_power_of_2"]
                    is_aligned = c_json["is_aligned"]
                    is_valid_supernet = c_json["is_valid_supernet"]
                    if c_json.get("cisco_static"):
                        cisco_static = c_json["cisco_static"]
        except Exception:
            pass

    return {
        "engine": engine_tag,
        "input_networks": sorted_nets,
        "input_count": num_inputs,
        "total_input_ips": total_input_ips,
        "supernet_network_ip": supernet_net,
        "supernet_network_str": int_to_ip(supernet_net),
        "supernet_cidr": supernet_cidr,
        "supernet_str": f"{int_to_ip(supernet_net)}/{supernet_cidr}",
        "supernet_mask_ip": supernet_mask,
        "supernet_mask_str": int_to_ip(supernet_mask),
        "supernet_wildcard_str": int_to_ip(calculate_wildcard_int(supernet_mask)),
        "supernet_broadcast_str": int_to_ip(supernet_bcast),
        "supernet_first_usable": int_to_ip(supernet_net + 1) if supernet_cidr < 31 else int_to_ip(supernet_net),
        "supernet_last_usable": int_to_ip(supernet_bcast - 1) if supernet_cidr < 31 else int_to_ip(supernet_bcast),
        "total_supernet_ips": supernet_total_ips,
        "usable_supernet_hosts": supernet_usable,
        "supernet_usable_hosts": supernet_usable,
        "extra_covered_ips": extra_covered_ips,
        "is_contiguous": is_contiguous,
        "is_power_of_2": is_power_of_2,
        "is_power_of_2_count": is_power_of_2,
        "is_aligned": is_aligned,
        "is_boundary_aligned": is_aligned,
        "is_optimal": is_optimal,
        "is_valid_supernet": is_valid_supernet,
        "borrowed_bits": borrowed_bits,
        "rules_checklist": rules_checklist,
        "reduction_pct": reduction_pct,
        "verdict": verdict,
        "verdict_badge": verdict_badge,
        "verdict_desc": verdict_desc,
        "binary_analysis": binary_analysis,
        "supernet_prefix": f"{int_to_ip(supernet_net)}/{supernet_cidr}",
        "supernet_mask": int_to_ip(supernet_mask),
        "total_input_subnets": num_inputs,
        "supernet_binary": supernet_bin_str,
        "supernet_bin_str": supernet_bin_str,
        "supernet_mask_binary": supernet_mask_bin_str,
        "supernet_mask_bin_str": supernet_mask_bin_str,
        "cisco_static": cisco_static,
        "cisco_static_route": cisco_static,
        "cisco_ospf": cisco_ospf,
        "cisco_ospf_summary": cisco_ospf,
        "cisco_bgp": cisco_bgp,
        "cisco_bgp_summary": cisco_bgp,
        "cisco_eigrp": cisco_eigrp,
        "cisco_eigrp_summary": cisco_eigrp,
    }


def export_cisco_ios(campus: CampusVLSM, filepath: str) -> str:
    """Generate production-ready Cisco IOS CLI configuration."""
    lines = [
        "! ==========================================================================",
        "! CISCO IOS ENTERPRISE CAMPUS SUBNET CONFIGURATION SCRIPT",
        "! Generated by NetLab-Pro Campus Network Subnet Architect (Python Edition)",
        "! ==========================================================================",
        "!",
        "enable",
        "configure terminal",
        "hostname Campus-Core-L3-Switch",
        "ip routing",
        "!",
        "! --------------------------------------------------------------------------",
        "! STEP 1: DHCP EXCLUDED ADDRESSES (Gateways & Local Servers)",
        "! --------------------------------------------------------------------------",
    ]
    for lab in campus.labs:
        lines.append(f"ip dhcp excluded-address {int_to_ip(lab.gateway_ip)} {int_to_ip(lab.dns_server_ip)}")
    lines.append("!")
    lines.append("! --------------------------------------------------------------------------")
    lines.append("! STEP 2: DYNAMIC HOST CONFIGURATION PROTOCOL (DHCP) SCOPES")
    lines.append("! --------------------------------------------------------------------------")
    for lab in campus.labs:
        clean_name = re.sub(r"[^A-Za-z0-9_-]", "_", lab.name)
        lines.append(f"ip dhcp pool POOL_{clean_name}")
        lines.append(f" network {int_to_ip(lab.network_ip)} {int_to_ip(lab.subnet_mask)}")
        lines.append(f" default-router {int_to_ip(lab.gateway_ip)}")
        lines.append(f" dns-server {int_to_ip(lab.dns_server_ip)} 8.8.8.8")
        lines.append(" domain-name campus.netlab.internal")
        lines.append(" lease 7 0 0")
        lines.append(" exit")
        lines.append("!")

    lines.append("! --------------------------------------------------------------------------")
    lines.append("! STEP 3: IEEE 802.1Q VLAN DEFINITIONS")
    lines.append("! --------------------------------------------------------------------------")
    for lab in campus.labs:
        clean_name = re.sub(r"[^A-Za-z0-9_-]", "_", lab.name)[:30]
        lines.append(f"vlan {lab.vlan_id}")
        lines.append(f" name {clean_name}")
        lines.append(" exit")
        lines.append("!")

    lines.append("! --------------------------------------------------------------------------")
    lines.append("! STEP 4: SWITCHED VIRTUAL INTERFACES (SVIs) / DEFAULT GATEWAYS")
    lines.append("! --------------------------------------------------------------------------")
    for lab in campus.labs:
        lines.append(f"interface Vlan{lab.vlan_id}")
        lines.append(f" description Gateway for {lab.name} [{lab.department}]")
        lines.append(f" ip address {int_to_ip(lab.gateway_ip)} {int_to_ip(lab.subnet_mask)}")
        lines.append(f" ip helper-address {int_to_ip(lab.dns_server_ip)}")
        lines.append(" no shutdown")
        lines.append(" exit")
        lines.append("!")

    lines.append("! --------------------------------------------------------------------------")
    lines.append("! STEP 5: CAMPUS PERIMETER GATEWAY & DEFAULT ROUTE")
    lines.append("! --------------------------------------------------------------------------")
    lines.append("interface GigabitEthernet0/0/1")
    lines.append(" description Uplink to Edge WAN Firewall")
    lines.append(" no switchport")
    lines.append(" ip address 192.168.254.2 255.255.255.252")
    lines.append(" no shutdown")
    lines.append(" exit")
    lines.append("!")
    lines.append("ip route 0.0.0.0 0.0.0.0 192.168.254.1")
    lines.append("!")
    lines.append("end")
    lines.append("write memory")
    lines.append("")

    content = "\n".join(lines)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    return content


def export_csv(campus: CampusVLSM, filepath: str) -> str:
    """Generate CSV spreadsheet formatted for Excel / Google Sheets."""
    header = "ID,Lab Name,Department,Workstations,Growth %,Effective Hosts,VLAN,Subnet Address,Allocated CIDR,Subnet Mask,First Usable,Last Usable,Gateway IP,DNS Server,Usable Capacity,Wasted IPs,Efficiency %\n"
    rows = []
    for lab in campus.labs:
        d = lab.to_dict()
        rows.append(
            f"{d['id']},\"{d['name']}\",\"{d['department']}\",{d['workstations']},{d['growth_percent']},"
            f"{d['effective_hosts']},{d['vlan_id']},{d['network_ip_str']},{d['allocated_cidr']},"
            f"{d['subnet_mask_str']},{d['first_usable_str']},{d['last_usable_str']},{d['gateway_ip_str']},"
            f"{d['dns_server_ip_str']},{d['usable_capacity']},{d['wasted_ips']},{d['efficiency_pct']:.1f}%"
        )
    content = header + "\n".join(rows) + "\n"
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    return content


def export_report_txt(campus: CampusVLSM, filepath: str) -> str:
    """Generate formatted ASCII text engineering report."""
    next_free_str = int_to_ip(campus.next_free_subnet)
    lines = [
        "=" * 80,
        "                     CAMPUS SUBNETTING & VLSM DESIGN REPORT                     ",
        "=" * 80,
        "",
        "BASE NETWORK SPECIFICATIONS:",
        f"  * Campus Base Network : {campus.base_ip_str}/{campus.base_cidr}",
        f"  * Broadcast Address   : {int_to_ip(campus.base_broadcast)}",
        f"  * Total Campus Scope  : {campus.total_campus_capacity} Addresses",
        f"  * Total Labs Planned  : {len(campus.labs)} Labs",
        f"  * Total Workstations  : {campus.total_requested_hosts} Computers",
        f"  * Total Allocated IPs : {campus.total_allocated_blocks} Addresses",
        f"  * Usable Host Space   : {campus.total_usable_hosts} Workstations",
        f"  * Overall Efficiency  : {campus.overall_efficiency:.2f} %",
        f"  * Next Free Subnet    : {next_free_str}",
        f"  * Free IPs Remaining  : {campus.free_ips_remaining} Addresses",
        "",
        "-" * 120,
        f"{'ID':<4} | {'Lab Name':<28} | {'VLAN':<7} | {'Subnet Address':<18} | {'Subnet Mask':<16} | {'Usable Host Range':<32} | {'Gateway':<16} | {'Hosts':<6}",
        "-" * 120,
    ]
    for lab in campus.labs:
        d = lab.to_dict()
        sub_str = f"{d['network_ip_str']}/{d['allocated_cidr']}"
        range_str = f"{d['first_usable_str']} -> {d['last_usable_str']}"
        vlan_str = f"Vlan{d['vlan_id']}"
        name_trunc = d['name'][:28]
        lines.append(
            f"{d['id']:<4} | {name_trunc:<28} | {vlan_str:<7} | {sub_str:<18} | {d['subnet_mask_str']:<16} | {range_str:<32} | {d['gateway_ip_str']:<16} | {d['usable_capacity']:<6}"
        )
    lines.append("-" * 120)
    lines.append("")

    content = "\n".join(lines)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    return content


class QuizEngine:
    """Generates Viva & CN exam practice questions with explanations."""

    def __init__(self):
        self.total_questions = 0
        self.correct_answers = 0
        self.current_streak = 0
        self.best_streak = 0

    def get_accuracy(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return (self.correct_answers / self.total_questions) * 100.0

    def generate_question(self) -> Dict[str, Any]:
        qtype = random.randint(0, 3)

        if qtype == 0:
            # Subnet Mask from CIDR
            cidr = random.randint(16, 30)
            mask_str = int_to_ip(cidr_to_mask_int(cidr))
            question = f"What is the standard IPv4 Subnet Mask for a /{cidr} network?"
            correct = mask_str

            distractors = set()
            while len(distractors) < 3:
                alt_cidr = random.randint(16, 30)
                if alt_cidr != cidr:
                    distractors.add(int_to_ip(cidr_to_mask_int(alt_cidr)))

            options = list(distractors) + [correct]
            random.shuffle(options)
            explanation = (
                f"A /{cidr} prefix indicates the first {cidr} contiguous bits are set to 1. "
                f"Binary: {'1' * cidr}{'0' * (32 - cidr)} which translates to dotted decimal {mask_str}."
            )

        elif qtype == 1:
            # Usable hosts from CIDR
            cidr = random.randint(22, 29)
            h = 32 - cidr
            usable = (1 << h) - 2
            question = f"How many usable host IP addresses are available in a /{cidr} subnet?"
            correct = f"{usable} hosts"

            distractors = set()
            distractors.add(f"{(1 << h)} hosts")      # Forgot minus 2
            distractors.add(f"{(1 << (h-1)) - 2} hosts")
            distractors.add(f"{(1 << (h+1)) - 2} hosts")
            while len(distractors) < 3:
                distractors.add(f"{random.randint(10, 500)} hosts")

            options = list(distractors)[:3] + [correct]
            random.shuffle(options)
            explanation = (
                f"The formula for usable hosts is 2^(32 - CIDR) - 2. "
                f"Here, h = 32 - {cidr} = {h} host bits. 2^{h} - 2 = {1 << h} - 2 = {usable} hosts "
                "(Network ID and Broadcast ID are subtracted)."
            )

        elif qtype == 2:
            # Network ID from IP/CIDR
            o1, o2, o3 = 192, 168, random.randint(1, 50)
            cidr = random.choice([24, 25, 26, 27, 28])
            block_size = 1 << (32 - cidr)
            sub_idx = random.randint(0, (256 // block_size) - 1)
            net_octet4 = sub_idx * block_size
            host_octet4 = net_octet4 + random.randint(1, block_size - 2)

            test_ip = f"{o1}.{o2}.{o3}.{host_octet4}"
            net_str = f"{o1}.{o2}.{o3}.{net_octet4}"

            question = f"What is the Network ID for the host address {test_ip}/{cidr}?"
            correct = net_str

            distractors = set()
            for delta in [-block_size, block_size, 1]:
                cand = net_octet4 + delta
                if 0 <= cand <= 255 and cand != net_octet4:
                    distractors.add(f"{o1}.{o2}.{o3}.{cand}")
            while len(distractors) < 3:
                distractors.add(f"{o1}.{o2}.{o3}.{random.randint(0, 250)}")

            options = list(distractors)[:3] + [correct]
            random.shuffle(options)
            explanation = (
                f"Subnet block size is 256 / 2^{cidr - 24} = {block_size}. "
                f"Subnets increment at multiples of {block_size} (.0, .{block_size}, .{block_size * 2}...). "
                f"The host {test_ip} falls inside the block starting at {net_str}."
            )

        else:
            # Broadcast ID from IP/CIDR
            o1, o2 = 172, 16
            o3 = random.randint(1, 10)
            cidr = random.choice([24, 25, 26, 27, 28])
            block_size = 1 << (32 - cidr)
            sub_idx = random.randint(0, (256 // block_size) - 1)
            net_octet4 = sub_idx * block_size
            bcast_octet4 = net_octet4 + block_size - 1
            host_octet4 = net_octet4 + random.randint(1, block_size - 2)

            test_ip = f"{o1}.{o2}.{o3}.{host_octet4}"
            bcast_str = f"{o1}.{o2}.{o3}.{bcast_octet4}"

            question = f"What is the Broadcast Address for the host {test_ip}/{cidr}?"
            correct = bcast_str

            distractors = set()
            for delta in [-1, 1, block_size]:
                cand = bcast_octet4 + delta
                if 0 <= cand <= 255 and cand != bcast_octet4:
                    distractors.add(f"{o1}.{o2}.{o3}.{cand}")
            while len(distractors) < 3:
                distractors.add(f"{o1}.{o2}.{o3}.{random.randint(0, 255)}")

            options = list(distractors)[:3] + [correct]
            random.shuffle(options)
            explanation = (
                f"For /{cidr}, the block size is {block_size}. Subnet starts at {o1}.{o2}.{o3}.{net_octet4}. "
                f"The broadcast address is the very last address in the block: {net_octet4} + {block_size} - 1 = {bcast_str}."
            )

        return {
            "question": question,
            "options": options,
            "correct_answer": correct,
            "correct_index": options.index(correct),
            "explanation": explanation,
        }

    def record_answer(self, is_correct: bool):
        self.total_questions += 1
        if is_correct:
            self.correct_answers += 1
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        else:
            self.current_streak = 0


# =============================================================================
# HIERARCHICAL NETWORK TOPOLOGY ENGINE (4-TIER HIERARCHY)
# =============================================================================

def generate_topology_graph(allocated_subnets: Any = None, base_ip: str = "10.50.0.0") -> Dict[str, Any]:
    """
    Generates a formal 4-tier hierarchical campus network topology graph:
    - Tier 1: Campus Gateway / Core Router (ASBR / BGP / NAT)
    - Tier 2: Distribution Layer-3 Switch (802.1Q SVI Inter-VLAN Routing)
    - Tier 3: Access Switches (One 802.1Q PoE+ Switch per Allocated Lab)
    - Tier 4: Sample End Devices per Lab (DNS Server, Network Printer, Workstation Nodes)

    Returns a rich node-and-edge graph data structure compatible with Vis.js,
    Cytoscape.js, and static vector SVG rendering.
    """
    if isinstance(allocated_subnets, CampusVLSM):
        base_ip = allocated_subnets.base_ip_str
        labs = [l.to_dict() for l in allocated_subnets.labs]
    elif isinstance(allocated_subnets, list):
        labs = []
        for item in allocated_subnets:
            if hasattr(item, "to_dict"):
                labs.append(item.to_dict())
            elif isinstance(item, dict):
                labs.append(item)
    else:
        temp = CampusVLSM(base_ip.split("/")[0] if "/" in base_ip else base_ip)
        temp.load_college_preset()
        labs = [l.to_dict() for l in temp.labs]

    base_clean = base_ip.split("/")[0].strip()
    base_cidr = int(base_ip.split("/")[1]) if "/" in base_ip else 16
    try:
        base_int = ip_to_int(base_clean)
    except Exception:
        base_int = ip_to_int("10.50.0.0")
        base_clean = "10.50.0.0"

    core_ip = int_to_ip(base_int + 1)
    dist_ip = int_to_ip(base_int + 2)

    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    # -------------------------------------------------------------------------
    # TIER 1: CAMPUS CORE ROUTER / BGP & WAN GATEWAY
    # -------------------------------------------------------------------------
    core_node = {
        "id": "core-rtr-01",
        "name": "Campus Core Gateway (RTR-01)",
        "hostname": "CAMPUS-CORE-RTR01",
        "model": "Cisco Catalyst 8500 Edge Router",
        "tier": 1,
        "tier_name": "Tier 1: Core / WAN Gateway",
        "type": "router",
        "role": "Autonomous System Border / BGP / NAT Core Gateway",
        "ip": core_ip,
        "subnet": f"{base_clean}/{base_cidr}",
        "mask": int_to_ip(cidr_to_mask_int(base_cidr)),
        "vlan": "Native / Routed",
        "department": "Campus Central IT & NOC",
        "speed": "40 Gbps",
        "interfaces": [
            {"name": "Gig0/0/0", "type": "WAN Uplink", "speed": "1 Gbps", "peer": "ISP Border Gateway (203.0.113.1)"},
            {"name": "Te1/0/1", "type": "Core Trunk A", "speed": "40 Gbps", "peer": "DSW-01 (Te1/0/1)"},
            {"name": "Te1/0/2", "type": "Core Trunk B", "speed": "40 Gbps", "peer": "DSW-02 (Redundant Standby)"}
        ],
        "label": f"Campus Core Gateway\n{core_ip}",
        "title": "Cisco Catalyst 8500 Edge Router (Core / WAN Gateway)",
        "level": 1,
        "group": "core",
        "shape": "box",
        "color": {
            "background": "#eff6ff",
            "border": "#2563eb",
            "highlight": {"background": "#dbeafe", "border": "#1d4ed8"}
        },
        "font": {"color": "#0f172a", "face": "Segoe UI", "size": 13, "bold": True}
    }
    nodes.append(core_node)

    # -------------------------------------------------------------------------
    # TIER 2: DISTRIBUTION LAYER-3 SWITCH (INTER-VLAN ROUTING SVI)
    # -------------------------------------------------------------------------
    dist_interfaces = [
        {"name": "Te1/0/1", "type": "Core Uplink", "speed": "40 Gbps", "peer": "RTR-01 (Te1/0/1)"}
    ]
    for idx, l in enumerate(labs):
        l_id = l.get("id", idx + 1)
        dist_interfaces.append({
            "name": f"TenGig1/1/{idx+1}",
            "type": "Access Trunk",
            "speed": "10 Gbps",
            "peer": f"ASW-LAB{l_id:02d} (TenGig0/1)"
        })

    dist_node = {
        "id": "dist-sw-01",
        "name": "Distribution Layer-3 Switch (DSW-01)",
        "hostname": "CAMPUS-DIST-SW01",
        "model": "Cisco Catalyst 9500-48Y4C (Layer-3 SVI Core)",
        "tier": 2,
        "tier_name": "Tier 2: Distribution Layer",
        "type": "distribution_switch",
        "role": "High-Speed Inter-VLAN Routing & 802.1Q Aggregation SVI",
        "ip": dist_ip,
        "subnet": f"{base_clean}/{base_cidr}",
        "mask": int_to_ip(cidr_to_mask_int(base_cidr)),
        "vlan": "All VLANs (802.1Q SVI Trunk)",
        "department": "Central Core Routing Wing",
        "speed": "40 Gbps Core / 10 Gbps Access",
        "interfaces": dist_interfaces,
        "label": f"Distribution Switch (L3)\n{dist_ip}",
        "title": "Cisco Catalyst 9500-48Y4C (Layer-3 SVI Inter-VLAN Routing)",
        "level": 2,
        "group": "distribution",
        "shape": "box",
        "color": {
            "background": "#f5f3ff",
            "border": "#7c3aed",
            "highlight": {"background": "#ede9fe", "border": "#6d28d9"}
        },
        "font": {"color": "#0f172a", "face": "Segoe UI", "size": 12, "bold": True}
    }
    nodes.append(dist_node)

    # Backbone Edge: Core Router -> Distribution Switch
    edges.append({
        "id": "edge-core-dist",
        "from": "core-rtr-01",
        "to": "dist-sw-01",
        "src_interface": "Te1/0/1",
        "dst_interface": "Te1/0/1",
        "label": "40 Gbps QSFP+ Backbone",
        "title": "40 Gbps QSFP+ Backbone Trunk (OM4 MPO Multimode Fiber)",
        "link_type": "backbone",
        "speed": "40 Gbps",
        "media": "OM4 MPO Multimode Fiber",
        "vlan": "All / Native Routed",
        "color": {"color": "#2563eb", "highlight": "#1d4ed8"},
        "width": 3.5,
        "dashes": False
    })

    # -------------------------------------------------------------------------
    # TIER 3 & 4: ACCESS SWITCHES & SAMPLE END DEVICES PER LAB
    # -------------------------------------------------------------------------
    for idx, lab in enumerate(labs):
        lab_id = lab.get("id", idx + 1)
        lab_name = lab.get("name", f"Laboratory {lab_id}")
        lab_dept = lab.get("department", "Campus Wing")
        workstations = lab.get("workstations", 30)
        vlan_id = lab.get("vlan_id", (lab_id * 10))
        subnet_str = lab.get("subnet_str", f"{lab.get('network_ip_str', '10.50.0.0')}/{lab.get('allocated_cidr', 24)}")
        gateway_ip = lab.get("gateway_ip_str", "10.50.0.1")
        mask_str = lab.get("subnet_mask_str", "255.255.255.0")
        dns_ip = lab.get("dns_server_ip_str", "10.50.0.2")

        sw_id = f"acc-sw-lab{lab_id}"
        sw_hostname = f"ASW-LAB{lab_id:02d}"

        # Tier 3: Access Switch Node
        nodes.append({
            "id": sw_id,
            "name": f"{lab_name} Access Switch",
            "hostname": sw_hostname,
            "model": "Cisco Catalyst 9200-48P PoE+",
            "tier": 3,
            "tier_name": "Tier 3: Access Layer",
            "type": "access_switch",
            "role": f"Edge 802.1Q Access Switch (VLAN {vlan_id})",
            "ip": gateway_ip,
            "subnet": subnet_str,
            "mask": mask_str,
            "vlan": f"VLAN {vlan_id}",
            "department": lab_dept,
            "workstations": workstations,
            "speed": "10 Gbps Uplink / 1 Gbps Access",
            "interfaces": [
                {"name": "TenGig0/1", "type": "Distribution Trunk", "speed": "10 Gbps", "peer": f"DSW-01 (TenGig1/1/{idx+1})"},
                {"name": "Fa0/1", "type": "Server Access", "speed": "1 Gbps", "peer": f"{sw_hostname}-SRV01"},
                {"name": "Fa0/2", "type": "Printer Access", "speed": "1 Gbps", "peer": f"{sw_hostname}-PRN01"},
                {"name": "Fa0/3", "type": "Workstation Node", "speed": "1 Gbps", "peer": f"{sw_hostname}-PC01"},
                {"name": "Fa0/4", "type": "Workstation Node", "speed": "1 Gbps", "peer": f"{sw_hostname}-PC02"},
                {"name": f"Fa0/5 - Fa0/{min(48, max(5, workstations+4))}", "type": "Host Fleet", "speed": "1 Gbps", "peer": f"{workstations} Workstations Pool"}
            ],
            "label": f"{lab_name}\nVLAN {vlan_id} • {subnet_str}",
            "title": f"Cisco Catalyst 9200-48P (VLAN {vlan_id} • {subnet_str})",
            "level": 3,
            "group": "access",
            "shape": "box",
            "color": {
                "background": "#e6f9f1",
                "border": "#00c076",
                "highlight": {"background": "#d1fae5", "border": "#059669"}
            },
            "font": {"color": "#0f172a", "face": "Segoe UI", "size": 11, "bold": True}
        })

        # Edge: Dist Switch -> Access Switch
        edges.append({
            "id": f"edge-dist-{sw_id}",
            "from": "dist-sw-01",
            "to": sw_id,
            "src_interface": f"TenGig1/1/{idx+1}",
            "dst_interface": "TenGig0/1",
            "label": f"10G Trunk (VLAN {vlan_id})",
            "title": f"10 Gbps 802.1Q Trunk Link (VLAN {vlan_id}) - Single-Mode Fiber",
            "link_type": "trunk",
            "speed": "10 Gbps",
            "vlan": vlan_id,
            "media": "10GBASE-LR Single-Mode Fiber",
            "color": {"color": "#7c3aed", "highlight": "#6d28d9"},
            "width": 2.2,
            "dashes": False
        })

        # Tier 4: Sample End Devices per Lab
        try:
            gw_int = ip_to_int(gateway_ip)
        except Exception:
            gw_int = ip_to_int("10.50.0.1")

        prefix = generate_lab_prefix(lab_name)
        devs = [
            ("srv", f"{prefix}-SRV-01", "server", "DNS & Local Cache Server", dns_ip, "Fa0/1", "1 Gbps"),
            ("prn", f"{prefix}-PRN-01", "printer", "Shared Department Laser Printer", int_to_ip(gw_int + 2), "Fa0/2", "1 Gbps"),
            ("pc1", f"{prefix}-PC-01", "workstation", "Student Workstation Node", int_to_ip(gw_int + 3), "Fa0/3", "1 Gbps"),
            ("pc2", f"{prefix}-PC-02", "workstation", "Student Workstation Node", int_to_ip(gw_int + 4), "Fa0/4", "1 Gbps"),
        ]

        for d_code, d_host, d_type, d_role, d_ip, d_port, d_speed in devs:
            dev_id = f"dev-lab{lab_id}-{d_code}"
            icon_char = "🖥️" if d_type == "workstation" else ("🖨️" if d_type == "printer" else "🖧")

            nodes.append({
                "id": dev_id,
                "name": d_host,
                "hostname": d_host,
                "model": "Generic Host Terminal",
                "tier": 4,
                "tier_name": "Tier 4: End Devices",
                "type": d_type,
                "role": d_role,
                "ip": d_ip,
                "subnet": subnet_str,
                "mask": mask_str,
                "vlan": f"VLAN {vlan_id}",
                "department": lab_dept,
                "gateway": gateway_ip,
                "dns": dns_ip,
                "connected_switch": sw_id,
                "connected_port": d_port,
                "speed": d_speed,
                "label": f"{d_host}\n{d_ip}",
                "title": f"{d_host} ({d_role}) • IP: {d_ip} (VLAN {vlan_id})",
                "level": 4,
                "group": "device",
                "shape": "dot",
                "color": {
                    "background": "#ffffff",
                    "border": "#64748b",
                    "highlight": {"background": "#f8fafc", "border": "#334155"}
                },
                "font": {"color": "#334155", "face": "Segoe UI", "size": 9}
            })

            edges.append({
                "id": f"edge-{sw_id}-{dev_id}",
                "from": sw_id,
                "to": dev_id,
                "src_interface": d_port,
                "dst_interface": "eth0",
                "label": f"Access ({d_port})",
                "title": f"1 Gbps Access Port ({d_port}) - Cat6A UTP Copper",
                "link_type": "access",
                "speed": d_speed,
                "vlan": vlan_id,
                "media": "Cat6A UTP Copper",
                "color": {"color": "#94a3b8", "highlight": "#64748b"},
                "width": 1.2,
                "dashes": True
            })

    metadata = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "tier_counts": {
            "tier1_core": len([n for n in nodes if n["tier"] == 1]),
            "tier2_dist": len([n for n in nodes if n["tier"] == 2]),
            "tier3_access": len([n for n in nodes if n["tier"] == 3]),
            "tier4_devices": len([n for n in nodes if n["tier"] == 4]),
        },
        "base_ip": base_clean,
        "base_cidr": base_cidr,
        "labs_count": len(labs)
    }

    return {"nodes": nodes, "edges": edges, "metadata": metadata}


def export_topology_svg(graph_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Produces a crisp, scalable vector graphic (SVG) illustrating the campus hierarchy
    with VLAN tags, interface identifiers (e.g. Gig0/1, Fa0/10, Te1/0/1), and subnet CIDR blocks.
    Saves to output_path if provided and returns the full SVG XML string.
    """
    nodes = graph_data.get("nodes", [])
    meta = graph_data.get("metadata", {})

    core_node = next((n for n in nodes if n["tier"] == 1), None)
    dist_node = next((n for n in nodes if n["tier"] == 2), None)
    access_nodes = [n for n in nodes if n["tier"] == 3]
    device_nodes = [n for n in nodes if n["tier"] == 4]

    n_acc = max(1, len(access_nodes))
    W = max(1440, n_acc * 230 + 160)
    H = 920

    cx = W / 2
    margin_x = 90
    usable_w = W - 2 * margin_x
    step_x = usable_w / (n_acc - 1) if n_acc > 1 else usable_w / 2

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    
    lines.append('''
  <defs>
    <filter id="shadow" x="-8%" y="-12%" width="120%" height="130%" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.08"/>
    </filter>
    <linearGradient id="grad-core" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="grad-dist" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#581c87"/>
      <stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
    <linearGradient id="grad-acc" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#064e3b"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
    <linearGradient id="grad-card" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#f8fafc"/>
    </linearGradient>
  </defs>
  <style>
    .title { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 20px; font-weight: 800; fill: #0f172a; text-anchor: middle; }
    .subtitle { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 11px; font-weight: 600; fill: #64748b; text-anchor: middle; }
    .tier-label { font-family: 'Consolas', monospace; font-size: 10px; font-weight: 700; fill: #94a3b8; }
    .node-title { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 12px; font-weight: 700; fill: #0f172a; }
    .node-sub { font-family: 'Consolas', monospace; font-size: 10px; font-weight: 600; fill: #475569; }
    .node-ip { font-family: 'Consolas', monospace; font-size: 10px; font-weight: 700; fill: #2563eb; }
    .pill-txt { font-family: 'Consolas', monospace; font-size: 9px; font-weight: 700; text-anchor: middle; }
    .if-label { font-family: 'Consolas', monospace; font-size: 8.5px; font-weight: 700; fill: #64748b; }
    .link-txt { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 9px; font-weight: 700; text-anchor: middle; }
    .dev-title { font-family: 'Segoe UI', system-ui, sans-serif; font-size: 9.5px; font-weight: 700; fill: #1e293b; }
    .dev-ip { font-family: 'Consolas', monospace; font-size: 8.5px; font-weight: 600; fill: #059669; }
  </style>
''')

    # Background canvas
    lines.append(f'  <rect width="{W}" height="{H}" fill="#f8fafc"/>')
    lines.append(f'  <rect x="15" y="15" width="{W-30}" height="{H-30}" rx="14" fill="#ffffff" stroke="#e2e8f0" stroke-width="1.5"/>')

    # Top Header
    base_ip_disp = meta.get("base_ip", "10.50.0.0")
    base_cidr_disp = meta.get("base_cidr", 16)
    lines.append(f'  <text x="{cx}" y="48" class="title">CAMPUS NETWORK TOPOLOGY ARCHITECTURE</text>')
    lines.append(f'  <text x="{cx}" y="68" class="subtitle">Hierarchical 4-Tier Model • Layer-3 SVI Routing • 802.1Q VLAN Trunks • Deterministic Host Addressing</text>')
    
    # Scope Pill
    pill_w = 260
    lines.append(f'  <rect x="{cx - pill_w/2}" y="80" width="{pill_w}" height="22" rx="11" fill="#eff6ff" stroke="#bfdbfe" stroke-width="1"/>')
    lines.append(f'  <text x="{cx}" y="95" class="pill-txt" fill="#1d4ed8">CAMPUS SCOPE: {base_ip_disp}/{base_cidr_disp}</text>')

    # Tier Watermarks on left
    lines.append('  <text x="35" y="175" class="tier-label">TIER 1 • CORE GATEWAY</text>')
    lines.append('  <text x="35" y="315" class="tier-label">TIER 2 • DISTRIBUTION</text>')
    lines.append('  <text x="35" y="475" class="tier-label">TIER 3 • ACCESS SWITCHES</text>')
    lines.append('  <text x="35" y="655" class="tier-label">TIER 4 • WORKSTATION FLEET</text>')

    core_x, core_y = cx, 160
    dist_x, dist_y = cx, 305
    acc_y = 475

    # 1. Links: Core -> Dist
    lines.append(f'  <line x1="{core_x}" y1="{core_y + 35}" x2="{dist_x}" y2="{dist_y - 35}" stroke="#2563eb" stroke-width="3.5"/>')
    lines.append(f'  <text x="{core_x + 8}" y="{core_y + 48}" class="if-label">Te1/0/1</text>')
    lines.append(f'  <text x="{dist_x + 8}" y="{dist_y - 40}" class="if-label">Te1/0/1</text>')
    lines.append(f'  <rect x="{cx - 70}" y="222" width="140" height="18" rx="9" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>')
    lines.append(f'  <text x="{cx}" y="234" class="link-txt" fill="#1e40af">40G QSFP+ Trunk</text>')

    # WAN link above core router
    lines.append(f'  <line x1="{core_x}" y1="{core_y - 35}" x2="{core_x}" y2="108" stroke="#dc2626" stroke-width="2" stroke-dasharray="4,3"/>')
    lines.append(f'  <text x="{core_x + 8}" y="125" class="if-label" fill="#dc2626">Gig0/0/0 (WAN / ISP)</text>')

    # Links: Dist -> Access Switches
    acc_coords = []
    for i, a_node in enumerate(access_nodes):
        ax = margin_x + i * step_x + 85
        acc_coords.append((ax, acc_y))
        lines.append(f'  <path d="M {dist_x} {dist_y + 35} C {dist_x} 385, {ax} 395, {ax} {acc_y - 42}" fill="none" stroke="#7c3aed" stroke-width="2"/>')
        lines.append(f'  <text x="{ax - 18}" y="{acc_y - 46}" class="if-label">TenGig0/1</text>')

    # 2. Tier 1 Card: Core Router
    c_ip = core_node.get("ip", "10.50.0.1") if core_node else "10.50.0.1"
    lines.append(f'''
  <!-- Tier 1: Core Router -->
  <g filter="url(#shadow)">
    <rect x="{core_x - 130}" y="{core_y - 35}" width="260" height="70" rx="10" fill="url(#grad-card)" stroke="#2563eb" stroke-width="2"/>
    <rect x="{core_x - 130}" y="{core_y - 35}" width="260" height="6" rx="3" fill="url(#grad-core)"/>
    <circle cx="{core_x - 100}" cy="{core_y}" r="16" fill="#eff6ff" stroke="#2563eb" stroke-width="1.5"/>
    <text x="{core_x - 100}" y="{core_y + 4}" text-anchor="middle" font-size="12">🌐</text>
    <text x="{core_x - 74}" y="{core_y - 8}" class="node-title">Campus Core Gateway (RTR-01)</text>
    <text x="{core_x - 74}" y="{core_y + 8}" class="node-sub">Cisco Catalyst 8500 Edge Router</text>
    <text x="{core_x - 74}" y="{core_y + 24}" class="node-ip">IP: {c_ip}</text>
  </g>
''')

    # 3. Tier 2 Card: Distribution Switch
    d_ip = dist_node.get("ip", "10.50.0.2") if dist_node else "10.50.0.2"
    lines.append(f'''
  <!-- Tier 2: Distribution Switch -->
  <g filter="url(#shadow)">
    <rect x="{dist_x - 140}" y="{dist_y - 35}" width="280" height="70" rx="10" fill="url(#grad-card)" stroke="#7c3aed" stroke-width="2"/>
    <rect x="{dist_x - 140}" y="{dist_y - 35}" width="280" height="6" rx="3" fill="url(#grad-dist)"/>
    <circle cx="{dist_x - 110}" cy="{dist_y}" r="16" fill="#f5f3ff" stroke="#7c3aed" stroke-width="1.5"/>
    <text x="{dist_x - 110}" y="{dist_y + 4}" text-anchor="middle" font-size="12">🔀</text>
    <text x="{dist_x - 84}" y="{dist_y - 8}" class="node-title">Distribution Switch (DSW-01)</text>
    <text x="{dist_x - 84}" y="{dist_y + 8}" class="node-sub">Cisco Catalyst 9500-48Y4C (Layer-3 SVI)</text>
    <text x="{dist_x - 84}" y="{dist_y + 24}" class="node-ip" fill="#7c3aed">SVI IP: {d_ip}</text>
  </g>
''')

    # 4. Tier 3 Cards & Tier 4 Devices
    for i, a_node in enumerate(access_nodes):
        ax, ay = acc_coords[i]
        c_w, c_h = 190, 84
        c_x = ax - c_w / 2
        c_y = ay - c_h / 2

        vlan_txt = a_node.get("vlan", f"VLAN {(i+1)*10}")
        sub_txt = a_node.get("subnet", "10.50.0.0/24")
        lab_nm = a_node.get("name", f"Lab {i+1}").replace(" Access Switch", "")
        if len(lab_nm) > 22:
            lab_nm = lab_nm[:20] + ".."
        pcs_cnt = a_node.get("workstations", 30)

        lines.append(f'''
  <!-- Tier 3: Access Switch #{i+1} -->
  <g filter="url(#shadow)">
    <rect x="{c_x}" y="{c_y}" width="{c_w}" height="{c_h}" rx="8" fill="url(#grad-card)" stroke="#059669" stroke-width="1.5"/>
    <rect x="{c_x}" y="{c_y}" width="{c_w}" height="4" rx="2" fill="url(#grad-acc)"/>
    <text x="{c_x + 8}" y="{c_y + 18}" class="node-title" font-size="11">{lab_nm}</text>
    <text x="{c_x + 8}" y="{c_y + 32}" class="node-sub" font-size="9">{a_node.get("hostname", f"ASW-LAB{i+1:02d}")}</text>
    <rect x="{c_x + 8}" y="{c_y + 40}" width="54" height="16" rx="4" fill="#ecfdf5" stroke="#10b981" stroke-width="1"/>
    <text x="{c_x + 35}" y="{c_y + 51}" class="pill-txt" fill="#047857">{vlan_txt}</text>
    <rect x="{c_x + 66}" y="{c_y + 40}" width="116" height="16" rx="4" fill="#eff6ff" stroke="#3b82f6" stroke-width="1"/>
    <text x="{c_x + 124}" y="{c_y + 51}" class="pill-txt" fill="#1d4ed8">{sub_txt}</text>
    <text x="{c_x + 8}" y="{c_y + 72}" class="if-label" font-size="8">Hosts: {pcs_cnt} Workstations</text>
    <text x="{c_x + c_w - 8}" y="{c_y + 72}" class="if-label" font-size="8" text-anchor="end">GW: .{a_node.get("ip", "10.50.0.1").split(".")[-1]}</text>
  </g>
''')

        # Tier 4 Devices under this access switch
        lab_id = a_node.get("id", "").replace("acc-sw-lab", "")
        lab_devs = [d for d in device_nodes if d.get("connected_switch") == a_node["id"]]
        if not lab_devs:
            lab_devs = [d for d in device_nodes if f"lab{lab_id}" in d.get("id", "")][:4]

        dev_grid = [
            (c_x + 2, 630, "Fa0/1"),
            (c_x + c_w/2 + 2, 630, "Fa0/2"),
            (c_x + 2, 705, "Fa0/3"),
            (c_x + c_w/2 + 2, 705, "Fa0/4"),
        ]

        for d_idx, dev in enumerate(lab_devs[:4]):
            dx, dy, port_name = dev_grid[d_idx]
            dw, dh = (c_w / 2) - 4, 52
            lines.append(f'  <line x1="{c_x + c_w/2}" y1="{c_y + c_h}" x2="{dx + dw/2}" y2="{dy}" stroke="#cbd5e1" stroke-width="1.2" stroke-dasharray="2,2"/>')
            icon = "🖥️" if dev.get("type") == "workstation" else ("🖨️" if dev.get("type") == "printer" else "🖧")
            host_short = dev.get("hostname", f"HOST-{d_idx+1}")
            if len(host_short) > 13:
                host_short = host_short[:12] + ".."
            ip_val = dev.get("ip", "10.50.0.X")

            lines.append(f'''
    <!-- Device {host_short} -->
    <rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="6" fill="#ffffff" stroke="#e2e8f0" stroke-width="1"/>
    <text x="{dx + 5}" y="{dy + 15}" font-size="10">{icon}</text>
    <text x="{dx + 22}" y="{dy + 15}" class="dev-title">{host_short}</text>
    <text x="{dx + 5}" y="{dy + 30}" class="dev-ip">{ip_val}</text>
    <rect x="{dx + dw - 32}" y="{dy + 34}" width="28" height="12" rx="3" fill="#f1f5f9"/>
    <text x="{dx + dw - 18}" y="{dy + 43}" class="if-label" font-size="7.5" text-anchor="middle">{port_name}</text>
''')

    # Legend
    lines.append(f'''
  <!-- Topology Legend -->
  <g transform="translate({W - 360}, {H - 95})">
    <rect width="330" height="70" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
    <text x="12" y="18" font-family="'Segoe UI', sans-serif" font-size="10" font-weight="700" fill="#334155">TOPOLOGY CABLING &amp; INTERFACE LEGEND</text>
    <line x1="15" y1="34" x2="45" y2="34" stroke="#2563eb" stroke-width="3"/>
    <text x="52" y="37" font-family="'Segoe UI', sans-serif" font-size="9" fill="#475569">40G QSFP+ Core Trunk</text>
    <line x1="170" y1="34" x2="200" y2="34" stroke="#7c3aed" stroke-width="2"/>
    <text x="207" y="37" font-family="'Segoe UI', sans-serif" font-size="9" fill="#475569">10G SMF 802.1Q Trunk</text>
    <line x1="15" y1="52" x2="45" y2="52" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3,3"/>
    <text x="52" y="55" font-family="'Segoe UI', sans-serif" font-size="9" fill="#475569">1G Cat6A Access Port</text>
    <line x1="170" y1="52" x2="200" y2="52" stroke="#dc2626" stroke-width="1.8" stroke-dasharray="3,2"/>
    <text x="207" y="55" font-family="'Segoe UI', sans-serif" font-size="9" fill="#475569">WAN / ISP Border Uplink</text>
  </g>
''')

    lines.append("</svg>")
    svg_content = "\n".join(lines)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

    return svg_content


def export_topology_image(graph_data: Dict[str, Any], output_path: str = "reports/campus_topology.png") -> str:
    """
    Renders the campus network topology graph to a high-resolution PNG image
    using matplotlib, perfectly sized for presentation embedding and visual reports.
    """
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    nodes = graph_data.get("nodes", [])
    meta = graph_data.get("metadata", {})

    core_node = next((n for n in nodes if n["tier"] == 1), None)
    dist_node = next((n for n in nodes if n["tier"] == 2), None)
    access_nodes = [n for n in nodes if n["tier"] == 3]
    device_nodes = [n for n in nodes if n["tier"] == 4]

    n_acc = max(1, len(access_nodes))
    fig_w = max(14, n_acc * 2.2)
    fig_h = 9.0

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=180)
    ax.set_facecolor("#f8fafc")
    fig.patch.set_facecolor("#ffffff")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    base_ip_disp = meta.get("base_ip", "10.50.0.0")
    base_cidr_disp = meta.get("base_cidr", 16)
    ax.text(50, 96, "CAMPUS NETWORK HIERARCHICAL TOPOLOGY (4-TIER MODEL)",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#0f172a", fontfamily="sans-serif")
    ax.text(50, 93, f"Core Gateway • Layer-3 Distribution • 802.1Q Access • Workstation Fleet | Scope: {base_ip_disp}/{base_cidr_disp}",
            ha="center", va="center", fontsize=9.5, fontweight="semibold", color="#64748b", fontfamily="sans-serif")

    core_x, core_y = 50, 81
    dist_x, dist_y = 50, 64

    # Core Router Card
    box_core = patches.FancyBboxPatch((core_x - 12, core_y - 4.5), 24, 9,
                                      boxstyle="round,pad=0.5,rounding_size=1.2",
                                      facecolor="#eff6ff", edgecolor="#2563eb", linewidth=2)
    ax.add_patch(box_core)
    ax.text(core_x, core_y + 1.8, "Campus Core Gateway (RTR-01)", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#1e3a8a")
    ax.text(core_x, core_y - 0.2, "Cisco Catalyst 8500 Edge Router", ha="center", va="center",
            fontsize=8, color="#475569")
    core_ip = core_node.get("ip", "10.50.0.1") if core_node else "10.50.0.1"
    ax.text(core_x, core_y - 2.2, f"IP: {core_ip} • WAN: Gig0/0/0", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#2563eb")

    # WAN Uplink
    ax.plot([core_x, core_x], [core_y + 4.5, 89], color="#dc2626", linestyle="--", linewidth=1.5)
    ax.text(core_x + 0.8, 87.5, "WAN / ISP (BGP)", fontsize=7.5, color="#dc2626", fontweight="bold")

    # Distribution Switch Card
    box_dist = patches.FancyBboxPatch((dist_x - 13, dist_y - 4.5), 26, 9,
                                      boxstyle="round,pad=0.5,rounding_size=1.2",
                                      facecolor="#f5f3ff", edgecolor="#7c3aed", linewidth=2)
    ax.add_patch(box_dist)
    ax.text(dist_x, dist_y + 1.8, "Distribution Layer-3 Switch (DSW-01)", ha="center", va="center",
            fontsize=10, fontweight="bold", color="#581c87")
    ax.text(dist_x, dist_y - 0.2, "Cisco Catalyst 9500-48Y4C (SVI Core)", ha="center", va="center",
            fontsize=8, color="#475569")
    dist_ip = dist_node.get("ip", "10.50.0.2") if dist_node else "10.50.0.2"
    ax.text(dist_x, dist_y - 2.2, f"SVI IP: {dist_ip} • 802.1Q Aggregation", ha="center", va="center",
            fontsize=8.5, fontweight="bold", color="#7c3aed")

    # Core -> Dist link
    ax.plot([core_x, dist_x], [core_y - 4.5, dist_y + 4.5], color="#2563eb", linewidth=2.5)
    ax.text(core_x, (core_y + dist_y) / 2, "40G QSFP+ Trunk", ha="center", va="center",
            fontsize=7.5, fontweight="bold", color="#1e40af",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#dbeafe", edgecolor="#93c5fd", linewidth=0.8))

    margin_x = 5
    usable_w = 90
    step_x = usable_w / (n_acc - 1) if n_acc > 1 else usable_w / 2
    acc_y = 44

    for i, a_node in enumerate(access_nodes):
        ax_pos = margin_x + i * step_x
        ax.plot([dist_x, ax_pos], [dist_y - 4.5, acc_y + 4.5], color="#7c3aed", linewidth=1.5, alpha=0.85)

        c_w = min(11, step_x * 0.92) if n_acc > 1 else 16
        box_acc = patches.FancyBboxPatch((ax_pos - c_w/2, acc_y - 4.5), c_w, 9,
                                         boxstyle="round,pad=0.3,rounding_size=0.8",
                                         facecolor="#e6f9f1", edgecolor="#059669", linewidth=1.5)
        ax.add_patch(box_acc)

        lab_nm = a_node.get("name", f"Lab {i+1}").replace(" Access Switch", "")
        if len(lab_nm) > 16:
            lab_nm = lab_nm[:14] + ".."
        vlan_txt = a_node.get("vlan", f"VLAN {(i+1)*10}")
        sub_txt = a_node.get("subnet", "10.50.0.0/24")

        ax.text(ax_pos, acc_y + 2.2, lab_nm, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="#064e3b")
        ax.text(ax_pos, acc_y + 0.3, a_node.get("hostname", f"ASW-LAB{i+1:02d}"), ha="center", va="center",
                fontsize=6.5, color="#334155")
        ax.text(ax_pos, acc_y - 1.4, f"{vlan_txt} • {sub_txt}", ha="center", va="center",
                fontsize=6.5, fontweight="bold", color="#2563eb")
        ax.text(ax_pos, acc_y - 3.0, f"{a_node.get('workstations', 30)} PCs", ha="center", va="center",
                fontsize=6.5, color="#059669")

        lab_devs = [d for d in device_nodes if d.get("connected_switch") == a_node["id"]]
        if not lab_devs:
            lab_devs = [d for d in device_nodes if f"lab{i+1}" in d.get("id", "")][:4]

        dev_y_start = 28
        for d_idx, dev in enumerate(lab_devs[:4]):
            dy = dev_y_start - (d_idx * 6.5)
            ax.plot([ax_pos, ax_pos], [acc_y - 4.5, dy + 2.2], color="#cbd5e1", linestyle=":", linewidth=0.8)

            d_box = patches.FancyBboxPatch((ax_pos - c_w/2, dy - 2.2), c_w, 4.4,
                                           boxstyle="round,pad=0.2,rounding_size=0.5",
                                           facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=0.8)
            ax.add_patch(d_box)

            d_host = dev.get("hostname", f"HOST-{d_idx+1}")
            if len(d_host) > 13:
                d_host = d_host[:12] + ".."
            d_ip = dev.get("ip", "10.50.0.X")
            d_port = dev.get("connected_port", f"Fa0/{d_idx+1}")

            ax.text(ax_pos, dy + 0.7, f"{d_host} ({d_port})", ha="center", va="center",
                    fontsize=6, fontweight="bold", color="#1e293b")
            ax.text(ax_pos, dy - 0.9, d_ip, ha="center", va="center",
                    fontsize=5.5, fontweight="semibold", color="#059669")

    leg_box = patches.FancyBboxPatch((1.5, 1.5), 32, 5.5,
                                     boxstyle="round,pad=0.3,rounding_size=0.6",
                                     facecolor="#ffffff", edgecolor="#cbd5e1", linewidth=1)
    ax.add_patch(leg_box)
    ax.text(2.5, 5.2, "LEGEND: — 40G QSFP+ Core   — 10G SMF Trunk   ··· 1G Cat6A Access",
            fontsize=6.5, fontweight="bold", color="#475569")
    ax.text(2.5, 3.2, "TIERS: [1] Core Router  [2] L3 Dist Switch  [3] Access Switch  [4] Workstation Fleet",
            fontsize=6.5, color="#64748b")

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return output_path
