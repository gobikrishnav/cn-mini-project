# 🌐 NetLab-Pro: Campus Network Subnet Architect & Dynamic VLSM Suite

**NetLab-Pro** is an interactive, production-grade IPv4 Subnetting and Campus Network Planning Suite. Built specifically for Computer Networks (CN) mini-projects, enterprise network design, and college viva demonstrations.

It runs **natively on your Windows device** as an interactive desktop GUI application:
* 🚀 **One-Click Native Windows Desktop App** (`run.bat` or `run_gui.bat`) - Built with a clean, modern white sidebar dashboard interface, real-time dynamic recalculations, interactive diagnostic tools, and in-place export generators.
* 📊 **PowerPoint Presentation Deck Generator** (`generate_ppt.py`) - Automatically creates a 12-slide widescreen presentation deck (`reports/NetLab_Pro_Project_Presentation.pptx`).

---

## 🌟 Key Features & Capabilities

### 1. 🏢 Dynamic Campus VLSM Subnet Architect (Direct Number of Labs Input)
* **Direct Number of Labs Input:** Enter the total number of laboratories to provision via spinbox or quick-sizing chips (`4 Labs`, `6 Labs`, `8 Labs`, `12 Labs`, `16 Labs`).
* **Configure N Labs Wizard:** Open an interactive modal table to define exact names, departments, and workstation counts for all $N$ laboratories with instant VLSM recalculation.
* **Zero Constraints:** Subnet for **any number of computer labs** ($1$ to $32+$) and **any number of computers per lab** ($2$ to $10,000+$).
* **Intelligent VLSM Allocation:**
  * Computes minimum host bits required: $(2^h - 2) \ge \text{workstations} + \text{buffer}$.
  * Sorts all labs descending by capacity demand to eliminate address fragmentation and prevent subnet overlaps.
  * Automatically calculates power-of-2 boundary alignments (`current_network % block_size == 0`).
  * Real-time address exhaustion detection against the base campus network.
* **Buffer & Growth Expansion:** Configurable percentage expansion buffer per lab (e.g., 10% or 20% future capacity).
* **Efficiency Analysis:** Reports total IP wastage, allocated blocks, and percentage efficiency.

### 2. 🌐 CIDR Supernetting & Multi-Subnet Route Summarization Engine
* **Multi-Subnet Aggregation:** Aggregate multiple contiguous or disparate subnets into a single supernet prefix (e.g. four `/24` subnets $\to$ one `/22` supernet).
* **Longest Common Prefix (LCP) Proof:** Performs 32-bit bitwise XOR analysis (`min_net ^ max_bcast`) to find the exact bit boundary separating common prefix bits from host bits.
* **Contiguity & Boundary Analysis:** Validates power-of-2 subnet count, starting boundary alignment, and detects unallocated IP address leakage.
* **Route Table Reduction:** Automatically computes percentage routing table reduction: $((N - 1) / N) \times 100\%$.
* **Multi-Protocol Cisco IOS CLI Generator:** Instantly outputs Cisco commands:
  * Anti-Routing-Loop Discard Static Route: `ip route <net> <mask> Null0`
  * OSPF Area Border Router (ABR) Summary: `area 0 range <net> <mask>`
  * BGP Border Gateway Aggregation: `aggregate-address <net> <mask> summary-only`
  * EIGRP Interface Route Summarization: `ip summary-address eigrp 100 <net> <mask>`
* **Import Active Campus Labs:** One-click button imports all active campus laboratories into the Supernetting engine.

### 3. 🖥️ PC-by-PC Workstation Inventory & DHCP Scope Generator
* **Dynamic System Addition & Expansion:** Add 1, 5, or any $N$ new systems directly to any laboratory on the fly via the **`➕ Add System to Lab...`** wizard or inline **`+1 PC` / `+5 PCs`** quick-add buttons. Automatically scales up the subnet block (e.g., from `/26` to `/25`) if capacity threshold is reached.
* For any configured lab, inspect the complete workstation-by-workstation inventory table:
  * Gateway IP (`<Lab>-GW01`)
  * Local Cache / DNS Server (`<Lab>-SRV01`)
  * Network Printer (`<Lab>-PRN01`)
  * Student Workstations (`<Lab>-PC-01`, `<Lab>-PC-02`, ...)
  * Spare / Expansion reserved addresses
* Computes exact DHCP pool scopes (Lease range start, range end, excluded gateway/server addresses, DNS).

### 3. 🔬 Deep 32-Bit Binary Visualizer & ANDing Engine
* Visualizes the complete 32-bit binary decomposition of an IPv4 address:
  * Network Bits (Cyan)
  * Subnet Borrowed Bits (Yellow)
  * Host Bits (Green)
* Step-by-step bitwise ANDing demonstration: `IP & MASK = Network ID`.
* Wildcard calculation: `~MASK = Wildcard Mask`.
* Broadcast calculation: `Network ID | Wildcard = Broadcast ID`.

### 4. 🔍 Inter-Host Reachability & Routing Diagnostic Tool
* Test communication between any two endpoints (`IP_A/CIDR_A` and `IP_B/CIDR_B`).
* Diagnoses:
  * **Direct Layer-2 Switched Path:** Same subnet; resolves MAC via ARP; no router hop.
  * **Layer-3 Routed Path:** Distinct subnets/VLANs; packet forwarded via Default Gateway and Inter-VLAN router.
  * **Asymmetric Mask Misconfiguration:** Detects mismatched masks causing one-way blackholes.

### 5. 📜 Multi-Format Export & PowerPoint Presentation Engine
* **12-Slide PowerPoint Presentation Deck (`reports/NetLab_Pro_Project_Presentation.pptx`):** Professional 16:9 widescreen presentation deck explaining problem statements, 4-tier system architecture, VLSM math, 8-lab case study, Cisco CLI, and viva defense Q&A.
* **Cisco IOS Switch & Router Config (`reports/campus_cisco.cfg`):** Ready to paste into Cisco Packet Tracer or a physical Cisco Catalyst L3 Switch/Router. Generates VLANs, SVIs (`interface VlanX`), DHCP pools, and default routes.
* **CSV Spreadsheet (`reports/campus_subnets.csv`):** Import directly into Microsoft Excel or Google Sheets.
* **Engineering Report (`reports/campus_report.txt`):** Complete formatted text report.

---

## 🏗️ Architecture & File Structure

```text
D:\cn mini project\
├── server.py             # Flask Web Server launching the Chrome Web Application
├── templates\
│   └── index.html        # Modern Chrome Web Interface (Tailwind CSS, Glassmorphic UI)
├── generate_ppt.py       # Human-designed 12-slide PowerPoint presentation generator
├── gui_app.py            # High-DPI Python Desktop GUI Application (Tkinter Dark Theme)
├── netlab_engine.py      # Core Python IPv4/VLSM math, diagnostics, DHCP & export engine
├── app.py                # Python Master Entry Point
├── run_chrome_app.bat    # 1-Click launcher to run Web App in Google Chrome
├── run_python_gui.bat    # 1-Click launcher for Desktop GUI Studio
├── reports\              # Generated Cisco scripts, CSVs, reports, and PPTX presentation
│   ├── NetLab_Pro_Project_Presentation.pptx
│   ├── campus_cisco.cfg
│   ├── campus_subnets.csv
│   └── campus_report.txt
├── include\              # C header files
├── src\                  # C source files
├── build.bat             # Auto-detects GCC or MSVC cl.exe and compiles C editions
├── run_gui.bat           # 1-Click launcher for Chrome Web App
└── run.bat               # 1-Click launcher for Terminal TUI
```

---

## ⚡ How to Run On Your Device

### 1. Master Launcher (All Modes)
Double-click `run.bat` or run:
```cmd
run.bat
```
This presents a clean menu to launch:
1. **Modern Web Application (Recommended)**: Runs on `http://localhost:5000` with interactive 4-tier network topology, live search, CIDR supernetting, 32-bit binary visualizer, reachability diagnostics, and viva defense quiz.
2. **Native Desktop GUI Studio**: High-DPI Windows Tkinter application with live recalculations.
3. **Interactive Terminal CLI**: Command-line prompt wizard.
4. **PowerPoint Presentation Deck Generator**: Generates `reports/NetLab_Pro_Project_Presentation.pptx`.

### 2. Direct Web Application Launcher
Double-click `run_chrome_app.bat` or run:
```cmd
python server.py
```
* Opens automatically in Google Chrome / your default browser at `http://localhost:5000`.
* Full suite of 8 interactive tabs, real-time live search, dynamic subnet scale buttons (`+1 PC`, `+5 PCs`), edit modal, address utilization bar, interactive Vis.js 4-tier topology, multi-protocol Cisco CLI generation, and instant downloads.

### 3. Direct Native Desktop GUI Launcher
Double-click `run_gui.bat` (or `run_python_gui.bat`) or run:
```cmd
python gui_app.py
```

### 4. Interactive Terminal Wizard (CLI Input Mode)
Double-click `run_cli.bat` or run:
```cmd
python interactive_cli.py
```

### 5. Generate 12-Slide PowerPoint Presentation Deck
Run:
```cmd
python generate_ppt.py
```
