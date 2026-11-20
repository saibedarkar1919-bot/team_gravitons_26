# 💧 JalSetu Nagpur — Community Groundwater, Tanker & Recharge Portal

> **🎥 DEMO VIDEO LINK:** [Watch 3-Minute Prototype Demo on Google Drive](https://drive.google.com/file/d/11uLzC5UrTz2J1VFUseN4vIlEhoYGk5pT/view?usp=sharing)  
> **🔗 Direct URL:** `https://drive.google.com/file/d/11uLzC5UrTz2J1VFUseN4vIlEhoYGk5pT/view?usp=sharing`

---

## 📖 About JalSetu Nagpur

**JalSetu Nagpur** (built by **Team Gravitons** for **YCCE HackKumbh 2026**) is a zero-hardware, community-driven water resource monitoring and conservation portal designed for drought-prone and rapidly urbanizing residential layouts across **Nagpur District**.

Instead of installing expensive Internet of Things (IoT) sensors in every borewell, JalSetu calibrates periodic manual well measurements against continuous 6-hourly Central Ground Water Board (CGWB) telemetry and live 48-hour rainfall data—connecting **Residents**, **Field Verifiers**, and **Municipal Tanker Dispatchers** on one unified platform.

### Key Capabilities
* **91 Monitored Nagpur Locations:** Covers **87 Central Ground Water Board (CGWB)** monitoring stations plus **4 residential pilot layouts** (*Wanadongri*, *Hingna*, *Wadi*, and *Nagpur Rural*).
* **Zero-Hardware Calibration & Pump Runway:** Computes offset-calibrated groundwater depth, weekly depletion rate, and **Borewell Pump Runway** (remaining days before water drops below submersible pump intake).
* **3-Signal Scarcity & Anti-Cheat Engine:** Evaluates aquifer stress, rapid depletion velocity, and resident dry-borewell reports while cross-checking entries against **live 48-hour Open-Meteo rainfall**.
* **End-to-End Tanker Lifecycle (55 LPCD Norm):** Field Verifiers raise verified emergency tanker indents; Utility Dispatchers auto-route the nearest depot with available water stock and trucks via Haversine distance; Residents confirm water receipt on a live map.
* **14-Taluka Rainwater Harvesting (RWH) Calculator:** Estimates gross runoff, first-flush diversion, and net harvest across all 14 talukas of Nagpur District, paired with trilingual (**English / हिंदी / मराठी**) monsoon readiness checklists.

---

## 🛠️ Tech Stack & Prerequisites

To run and view the JalSetu Nagpur web application locally on your device, you only need:

1. **Python 3.10 or higher** (uses Python's built-in `http.server`, `json`, `math`, `hashlib`, `urllib`, and `datetime` standard libraries—**no heavy third-party `pip` packages required**).
2. **A Modern Web Browser** (Google Chrome, Microsoft Edge, Brave, or Firefox) with internet access to load map tiles (`OpenStreetMap` / `Leaflet.js`) and live 48-hour rainfall (`Open-Meteo API`).
3. **Git** (optional, for cloning the repository).

---

## 🚀 Installation & Quick Start Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/saibedarkar1919-bot/team_gravitons_26.git
cd team_gravitons_26
```

### Step 2: Verify Python Installation
```bash
python --version
```
*(Ensure Python 3.10+ is installed.)*

### Step 3: Start the Application Server
Run the main unified server (`unifed2.py`):
```bash
python -u unifed2.py
```
You will see:
```text
=======================================================
 Nagpur Unified Multi-Role Prototype (91 locations)
 Open Login Page: http://127.0.0.1:8000/login
 Press Ctrl+C to stop.
=======================================================
```

### Step 4: Open in Your Browser
Visit **[http://127.0.0.1:8000/login](http://127.0.0.1:8000/login)** and sign in using any of the three role portals (credentials auto-fill when you click a role tab):

| Portal Role | Default Name | Default Password | What You Can Do |
| :--- | :--- | :--- | :--- |
| **1. Citizen Portal** (`/citizen`) | `Aarav Deshmukh` | `citizen123` | View colony Red/Yellow/Green supply status & pump runway, log 1-tap daily water availability, track live incoming tankers & confirm delivery, report pipeline leaks, and calculate 14-taluka Rainwater Harvesting. |
| **2. Field Verifier Portal** (`/verifier`) | `Rajesh Kulkarni` | `verifier123` | Log reference well depth with 48h rainfall anti-cheat validation, inspect 7-day 6-hourly calibrated hydrographs, and raise verified 55 LPCD tanker indents. |
| **3. Utility & Tanker Console** (`/utility`) | `NMC Dispatch Desk` | `utility123` | View district-wide scarcity & fleet map, auto-dispatch tankers from nearest depots with stock, refill depots, and resolve resident leak tickets. |

---

## 📂 Project Architecture & File Overview

```text
team_gravitons_26/
├── unifed2.py                     # Main entry point: Multi-role HTTP server, REST APIs, and complete UI for Citizen, Verifier & Utility portals
├── stage2_scarcity_engine.py      # Core groundwater calibration, pump runway calculator, and 3-signal scarcity & anti-cheat engine
├── weather_service.py             # Live 48-hour rainfall fetcher using Open-Meteo API
├── extract_nagpur.py              # Offline ETL script that filters raw Maharashtra CGWB CSVs for Nagpur District
├── probe_aquifer.py               # Utility script for inspecting aquifer GeoJSON boundaries
├── stage1_groundwater.py          # Stage 1 modular prototype for groundwater calibration and validation
├── app.py / unified.py            # Earlier development iterations of the web server
└── processed/
    ├── nagpur_quarterly.json      # Cleaned quarterly groundwater levels across 87 CGWB Nagpur stations
    ├── nagpur_telemetry_6hr.json  # Cleaned 6-hourly telemetry readings across 11 Nagpur stations
    ├── nagpur_aquifers.geojson    # Processed Nagpur aquifer boundary polygons
    └── unified_state.json         # Live shared database for check-ins, well readings, tanker orders & leak tickets
```

### How Everything Connects
1. **Offline Data Preparation (`extract_nagpur.py`):** Filters raw Central Ground Water Board datasets for Nagpur District and outputs normalized JSON files into `processed/`.
2. **Main Application (`unifed2.py`):** Launches the web portal on port `8000` and serves all three role interfaces. Every user action updates `processed/unified_state.json` in real time.
3. **Scarcity & Weather Engine (`unifed2.py` → `stage2_scarcity_engine.py` → `weather_service.py`):** Matches any selected colony to its nearest CGWB station, applies offset calibration, checks live 48-hour rainfall via Open-Meteo, and outputs Red/Yellow/Green scarcity alerts and tanker recommendations.

---

## 👥 Team Gravitons — YCCE HackKumbh 2026
* **Team Leader:** Yash Mukesh Batra
* **Data & API Acknowledgements:** Central Ground Water Board (CGWB) Nagpur Groundwater Dataset, Open-Meteo Weather API, OpenStreetMap & Leaflet.js, and Jal Jeevan Mission (55 LPCD) norms.