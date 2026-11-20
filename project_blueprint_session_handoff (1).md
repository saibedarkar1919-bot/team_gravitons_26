# YCCE HackKumbh — Theme 03, Problem Statement 04

## Community Water Scarcity & Groundwater Monitoring Dashboard

**Workspace Path:** `D:\hackumbh`

**Target Pilot Region:** Nagpur District (Urbanizing & Semi-Urban Layouts: Hingna, Wanadongri, Wadi, Nagpur Rural)

## 1. Core Value Proposition & USP

Unlike fragmented existing platforms (**India-WRIS**, **Jaldoot App**, **Swachhata**, **MyGate**), this platform creates a **zero-hardware, closed-loop "Supply-to-Recharge" utility** for residential layouts and semi-urban Gram Panchayats:

1. **Zero-Hardware Hyper-Local Groundwater Tracking:** Pairs open-source 6-hourly CGWB/India-WRIS telemetry stations with weekly manual readings from verified neighborhood leads using **Offset Calibration**, eliminating the need for costly IoT sensors.

2. **Real-World Governance & Anti-Abuse Guardrails:** Mirrors actual Maharashtra local water administration (Residents $\rightarrow$ Local Verifier $\rightarrow$ Utility/Tanker Cell) so unmoderated resident calls never spam tanker queues.

3. **Two-Way Tanker Accountability:** Stops fake tanker trips and water theft by requiring both a **Tanker Driver GPS Unloading Photo** and **Resident "Water Received" Check-ins** at community tanks.

4. **Actionable Conservation Loop:** Links local aquifer depth trends with a **Rainwater Harvesting (RWH) Maintenance Checklist & Effectiveness Calculator** ($\text{Volume} = \text{Rainfall} \times \text{Roof Area} \times 0.85$) and direct civic pipe-leak reporting.

## 2. Three-Tier Role-Based Access Control (RBAC)

| User Role | Real-World Counterpart | What They See | What They Do | Strict Guardrails (Cannot Touch) | 
| ----- | ----- | ----- | ----- | ----- | 
| **1. Local Residents** | Everyday households in residential layouts & semi-urban wards | Live 6-hr calibrated groundwater chart, official tanker ETA schedule, RWH calculator, water-saving tips. | Tap **"Tanker Arrived"** to confirm unloading, report daily tap/borewell shortages, log geo-tagged pipe leaks. | **Cannot** order/dispatch tankers directly; **cannot** edit groundwater depth records. | 
| **2. Local Verifiers** | Gram Panchayat (`Gramsevak`), Municipal Ward Officer, GSDA Staff, or Housing Society Secretary | Aggregated household shortage alerts in their ward/layout, reference-well depth history, open leak pins. | Log **weekly reference-well depth** (+ photo proof), submit **1 verified tanker indent** (20–40 LPCD norm), audit RWH checklists. | **Cannot** manage tanker fleet routing, assign drivers, or clear contractor bills. | 
| **3. Tanker & Utility Dispatchers** | BDO / Tehsildar / Municipal Water Cell + Contracted Tanker Drivers | Verified tanker demands, assigned filling points, delivery routes, and open leak repair tickets. | Approve daily tanker trip quotas, upload **GPS arrival & unloading photos** at community tanks, close leak tickets. | **Zero exposure** to raw India-WRIS telemetry graphs, aquifer maps, or RWH calculators. | 

## 3. End-to-End 5-Tier System Architecture

```
[TIER 1: DATA INPUTS]
 • Open Gov Data: India-WRIS/NWDP 6-Hr Telemetry + 5-Yr Quarterly Avg + Aquifer GeoJSON + IMD/Open-Meteo Rain
 • Local Verifier: Weekly reference well depth (+ photo) + RWH maintenance checklist + verified tanker indent
 • Resident Crowd: Daily dry-borewell/no-water check-ins + GPS pipe-leak reports + tanker arrival confirmations
        │
        ▼
[TIER 2: BACKEND DATA FUSION & VALIDATION ENGINE]
 • Spatial Matcher: Pairs layout GPS to nearest 1–3 gov stations on the SAME underground aquifer polygon
 • Outlier & Rain Filter: Flags manual jumps > ±2.0m unless IMD rainfall confirms genuine aquifer recharge
 • Offset Calibration: Saves gap (Local Well - Gov Sensor) and shifts 6-hourly gov wave for a live colony graph
        │
        ▼
[TIER 3: 3-SIGNAL SCARCITY & ANALYTICS ENGINE]
 • RED Alert Triggers: (1) >2.5m deeper than 5-yr avg  (2) Drop >0.5m/week  (3) >=30% households report dry pumps
 • Parallel Analytics: RWH Harvest Calculator (Rain_mm × Roof_sqm × 0.85 × Checklist_Score) & Leak Ticket Router
        │
        ▼
[TIER 4 & 5: ROLE PORTALS & CLOSED-LOOP ACCOUNTABILITY]
 • Resident Portal <──> Verifier Portal <──> Tanker & Utility Dispatcher
 • Two-Way Delivery Proof (Driver GPS Photo + Resident Arrival Tap) + Long-Term Aquifer Recharge Tracking
```

## 4. Datasets Downloaded in `D:\hackumbh` & Preprocessing Findings

Three raw files from `nwdp.nwic.gov.in` (India-WRIS open data portal) are stored in `D:\hackumbh`:

1. `gwl_manual_quarterly_cgwb_mh_2021_2025.csv` (\~1.7 MB) — 5-year seasonal baseline (`Groundwater Level Quarterly Manual (meter)`).
   * **Verified Nagpur Extraction:** Filtering strictly on `District == 'Nagpur'` yields **671 clean rows across 87 stations** (saved to `D:\hackumbh\processed\nagpur_quarterly.json`).

2. `gwl_tel_6_hourly_cgwb_mh_2021_2025.csv` (\~54.2 MB) — Live 6-hourly regional sensor wave (`Groundwater Level Telemetry 6 Hourly (meter)`).
   * **Verified Nagpur Extraction:** Filtering strictly on `District == 'Nagpur'` yields **27,767 clean rows across 11 stations** (`Bela_5`, `Bokhara_1`, `Fetri_2`, `Gumthala_1`, `IMD Nagpur_1`, `Kanholibara_2`, `Khandala_2`, `Makardhokra`, `Nara_3`, `Narkhed_1`, `Rohna_1`) saved to `D:\hackumbh\processed\nagpur_telemetry_6hr.json`.
   * **Sign Normalization Rule:** Telemetry depth values in the CSV can be negative (e.g., `-1.2`), whereas quarterly values are positive (e.g., `8.63`). Always normalize depth to positive meters below ground level (`m bgl`) using `abs(float(val))` before computing offsets or deficits.
   * **District Column Trap:** `'District LGD Code'` appears before `'District'` in the CSV header list—always match exact `'District'` rather than substring/prefix matching so neighboring districts like Wardha or Bhandara do not leak in.

3. `major_principal_aquifer.geojson` (\~131 MB) — National underground rock/aquifer boundary polygons (43 features; aquifer types include `Basalt`, `Alluvium`, `Gneiss`, `Banded Gneissic Complex`, etc.).
   * **Projection Note:** Coordinates in this file are projected in meters (India Albers Equal Area Conic, e.g., `~5546318, ~2227560`) rather than standard GPS degrees (`Lat/Lon`), and `CRS` is `None` at top-level. For the fast prototype, use GPS haversine distance to the nearest Nagpur CGWB station + seasonal quarterly baseline + layout aquifer label (`Basalt` / `Alluvium` / `Gneiss`), while keeping `probe_aquifer.py` / `nagpur_aquifers.geojson` available if needed.

4. **Rainfall Feed:** Use **Open-Meteo API** (`https://api.open-meteo.com/v1/forecast?latitude=21.10&longitude=78.98&daily=precipitation_sum`) as a zero-API-key live daily rainfall feed (or IMD Maharashtra CSV).

### Verified CSV Headers

`['SlNo', 'Station', 'Agency', 'State LGD Code', 'State', 'District LGD Code', 'District', 'Tehsil', 'Block', 'Village', 'River', 'Basin', 'Tributary', 'Subtributary', 'SubSubtributary', 'Local River', 'Latitude', 'Longitude', 'RL_MSL', 'Data Acquisition Time', 'Groundwater Level ... (meter)']`

## 5. Step-by-Step Build Roadmap (Pick Up Here)

### Step 1: Clean Nagpur Data Extraction (`D:\hackumbh\extract_nagpur.py`) — **Completed for CSVs**
* Filters strictly on `row["District"].strip().lower() == "nagpur"`, normalizes `depth_m = round(abs(float(raw_val)), 2)`, and outputs `nagpur_quarterly.json` and `nagpur_telemetry_6hr.json` in `D:\hackumbh\processed\`.

### Step 2: Build & Test Stage 1 Groundwater Engine (`D:\hackumbh\stage1_groundwater.py`) — **Current Step**
Combines **Gov 6-Hr Telemetry + 5-Yr Quarterly Avg + Rainfall (`rain_48h_mm`) + Weekly Verifier Depth** to output 5 core metrics per layout:
1. `live_calibrated_depth_m` (`gov_depth + local_offset`)
2. `seasonal_deficit_m` (`calibrated_depth - 5yr_monthly_avg`)
3. `depletion_velocity_m_per_week`
4. `estimated_pump_runway_days` (`(avg_pump_depth - calibrated_depth) / daily_drop`)
5. `verifier_validation` (`VERIFIED` vs `FLAGGED` if depth $\le 0$, sudden drop $> 2.5\text{m}$, or rise $> 2.0\text{m}$ with `< 15mm` 48h rain)

### Step 3: Fuse Stage 2 Resident Crowd Signals (`3-Signal Scarcity Engine`)
Combine Stage 1 outputs with resident `NO_WATER` / `BOREWELL_DRY` check-ins to compute **GREEN / YELLOW / RED** layout scarcity status, unlock verified tanker indents for the Local Verifier, and activate two-way tanker delivery confirmation.

### Step 4: Build FastAPI Backend + Role-Switched Web Dashboard
* **Backend (`FastAPI` + `SQLite`):** Endpoints for `/layouts`, `/verifier/log-depth`, `/resident/signal`, `/verifier/request-tanker`, `/utility/approve-tanker`, `/driver/confirm-delivery`, `/leaks`, and `/rwh-calculator`.
* **Frontend (`Next.js` or `React + Vite + Tailwind CSS`):** Single clean web portal with a top-bar **Role Switcher** (`Resident View` | `Local Verifier View` | `Tanker & Utility View`) so hackathon judges can test the entire end-to-end workflow live on one screen.

## 6. Prompt to Paste Into Your Next Session

> "I am building a hackathon project for **Water Scarcity & Groundwater Monitoring** (YCCE HackKumbh, Theme 03 PS 04) in `D:\hackumbh`. Always explain **why** and **what the code will do** before generating any code. I have pasted my updated `PROJECT_BLUEPRINT.md` above. We already extracted 671 Nagpur quarterly rows (87 stations) and 27,767 Nagpur 6-hourly telemetry rows (11 stations) into `D:\hackumbh\processed\`, and created `stage1_groundwater.py`. Let's review/test **Stage 1** and then fuse it with **Resident Crowd Inputs** for the **3-Signal Scarcity Engine**."