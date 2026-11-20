from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import urllib.parse
from stage2_scarcity_engine import Stage2ScarcityEngine

PORT = 8000
PROCESSED_DIR = r"D:\hackumbh\processed"
QUARTERLY_PATH = os.path.join(PROCESSED_DIR, "nagpur_quarterly.json")
CUSTOM_LAYOUTS_PATH = os.path.join(PROCESSED_DIR, "custom_layouts.json")
COMMUNITY_STATE_PATH = os.path.join(PROCESSED_DIR, "community_state.json")

engine = Stage2ScarcityEngine()

FEATURED_LAYOUTS = [
    {
        "id": "wanadongri",
        "name": "Shanti Vihar Layout, Wanadongri",
        "tehsil": "HINGNA",
        "category": "Featured Pilot",
        "lat": 21.1020,
        "lon": 78.9850,
        "aquifer_type": "Basalt",
        "avg_pump_depth_m": 22.0,
        "total_households": 120,
        "default_verifier_depth": 16.5,
        "default_last_recorded_depth": 15.8,
        "default_crowd": {"NORMAL": 65, "LOW_PRESSURE": 10, "BOREWELL_DRY": 45},
    },
    {
        "id": "hingna",
        "name": "Samarth Nagar, Hingna",
        "tehsil": "HINGNA",
        "category": "Featured Pilot",
        "lat": 21.0650,
        "lon": 78.9620,
        "aquifer_type": "Basalt",
        "avg_pump_depth_m": 20.0,
        "total_households": 80,
        "default_verifier_depth": 15.2,
        "default_last_recorded_depth": 14.6,
        "default_crowd": {"NORMAL": 65, "LOW_PRESSURE": 6, "BOREWELL_DRY": 9},
    },
    {
        "id": "wadi",
        "name": "Amravati Road Layout, Wadi",
        "tehsil": "NAGPUR RURAL",
        "category": "Featured Pilot",
        "lat": 21.1480,
        "lon": 79.0150,
        "aquifer_type": "Basalt",
        "avg_pump_depth_m": 24.0,
        "total_households": 150,
        "default_verifier_depth": 5.2,
        "default_last_recorded_depth": 5.1,
        "default_crowd": {"NORMAL": 145, "LOW_PRESSURE": 3, "BOREWELL_DRY": 2},
    },
    {
        "id": "nagpur_rural",
        "name": "Gramsevak Ward 4, Nagpur Rural",
        "tehsil": "NAGPUR RURAL",
        "category": "Featured Pilot",
        "lat": 21.1200,
        "lon": 79.0500,
        "aquifer_type": "Basalt",
        "avg_pump_depth_m": 25.0,
        "total_households": 100,
        "default_verifier_depth": 4.8,
        "default_last_recorded_depth": 4.8,
        "default_crowd": {"NORMAL": 45, "LOW_PRESSURE": 15, "BOREWELL_DRY": 40},
    },
]


def parse_ts(ts: str) -> datetime:
    for fmt in ("%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y"):
        try:
            return datetime.strptime(ts.strip(), fmt)
        except ValueError:
            continue
    return datetime.min


def clean_station_label(raw_station: str, tehsil: str) -> str:
    label = raw_station.replace("_Pz", "").replace("_pz_1", " (Zone 1)").replace("_pz_2", " (Zone 2)")
    label = label.replace("_1", "").replace("-1", "").replace("-2", "").replace("_", " - ").strip()
    if tehsil and tehsil != "-" and tehsil.lower() not in label.lower():
        return f"{label} ({tehsil.title()})"
    return label


def load_all_nagpur_layouts() -> list[dict]:
    layouts = list(FEATURED_LAYOUTS)
    seen_ids = {item["id"] for item in layouts}

    if os.path.exists(CUSTOM_LAYOUTS_PATH):
        try:
            with open(CUSTOM_LAYOUTS_PATH, "r", encoding="utf-8") as f:
                custom_items = json.load(f)
                for item in custom_items:
                    if item.get("id") not in seen_ids:
                        if "default_last_recorded_depth" not in item:
                            item["default_last_recorded_depth"] = item.get("default_last_verifier_depth", 10.2)
                        layouts.append(item)
                        seen_ids.add(item["id"])
        except Exception:
            pass

    if os.path.exists(QUARTERLY_PATH):
        with open(QUARTERLY_PATH, "r", encoding="utf-8") as f:
            q_rows = json.load(f)

        by_station = {}
        for row in q_rows:
            st = row.get("station", "").strip()
            if not st:
                continue
            dt = parse_ts(row.get("timestamp", ""))
            if st not in by_station or dt > by_station[st]["dt"]:
                by_station[st] = {
                    "dt": dt,
                    "station": st,
                    "tehsil": (row.get("tehsil") or "NAGPUR").strip().upper(),
                    "lat": float(row["lat"]),
                    "lon": float(row["lon"]),
                    "depth_m": float(row["depth_m"]),
                }

        for st_key in sorted(by_station.keys()):
            info = by_station[st_key]
            slug = "ngp_" + "".join(ch.lower() if ch.isalnum() else "_" for ch in st_key).strip("_")
            if slug in seen_ids:
                continue
            seen_ids.add(slug)

            base_d = round(max(2.5, min(23.5, info["depth_m"])), 1)
            last_d = round(max(2.2, base_d - 0.3), 1)
            pump_d = round(max(20.0, base_d + 6.5), 1)
            homes = 80 + (sum(ord(c) for c in st_key) % 100)

            if base_d >= 13.5:
                dry = round(homes * 0.34)
                low_p = round(homes * 0.14)
            elif base_d >= 9.5:
                dry = round(homes * 0.12)
                low_p = round(homes * 0.16)
            else:
                dry = max(1, round(homes * 0.02))
                low_p = max(2, round(homes * 0.04))

            norm = max(0, homes - dry - low_p)
            tehsil_clean = info["tehsil"] if info["tehsil"] and info["tehsil"] != "-" else "NAGPUR"

            layouts.append({
                "id": slug,
                "name": clean_station_label(st_key, tehsil_clean),
                "tehsil": tehsil_clean,
                "category": "CGWB Nagpur Network",
                "lat": info["lat"],
                "lon": info["lon"],
                "aquifer_type": "Basalt",
                "avg_pump_depth_m": pump_d,
                "total_households": homes,
                "default_verifier_depth": base_d,
                "default_last_recorded_depth": last_d,
                "default_crowd": {"NORMAL": norm, "LOW_PRESSURE": low_p, "BOREWELL_DRY": dry},
            })

    return layouts


ALL_LAYOUTS = load_all_nagpur_layouts()
LAYOUT_INDEX = {item["id"]: item for item in ALL_LAYOUTS}


def load_community_state() -> dict:
    if os.path.exists(COMMUNITY_STATE_PATH):
        try:
            with open(COMMUNITY_STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_community_state(state: dict):
    with open(COMMUNITY_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


COMMUNITY_STATE = load_community_state()


def get_layout_crowd_state(layout_id: str) -> dict:
    layout = LAYOUT_INDEX[layout_id]
    if layout_id not in COMMUNITY_STATE:
        COMMUNITY_STATE[layout_id] = {
            "counts": dict(layout["default_crowd"]),
            "recent_logs": [
                {
                    "time": "08:15 AM",
                    "unit": "Plot 14 / B-201",
                    "status": "BOREWELL_DRY" if layout["default_crowd"]["BOREWELL_DRY"] >= 15 else "NORMAL",
                    "note": "Morning overhead tank check-in",
                },
                {
                    "time": "07:45 AM",
                    "unit": "Plot 09 / A-104",
                    "status": "LOW_PRESSURE" if layout["default_crowd"]["LOW_PRESSURE"] >= 5 else "NORMAL",
                    "note": "Municipal sump supply check",
                },
            ],
        }
    return COMMUNITY_STATE[layout_id]


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nagpur Groundwater & Community Water Availability Monitor</title>
  <style>
    :root {
      --bg: #0f172a;
      --card: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --green: #10b981;
      --yellow: #f59e0b;
      --red: #ef4444;
      --blue: #38bdf8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 24px; min-height: 100vh; }
    header { margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 16px; display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; }
    h1 { font-size: 20px; font-weight: 700; color: var(--blue); }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
    .grid { display: grid; grid-template-columns: 440px 1fr; gap: 24px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    .card h2 { font-size: 15px; margin-bottom: 14px; color: #e2e8f0; display: flex; align-items: center; justify-content: space-between; }
    label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 6px; font-weight: 500; }
    .field { margin-bottom: 12px; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .three-col { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
    input, select { width: 100%; background: #0b1120; border: 1px solid var(--border); color: var(--text); padding: 8px 10px; border-radius: 6px; font-size: 13px; outline: none; }
    input:focus, select:focus { border-color: var(--blue); }
    .slider-row { display: flex; align-items: center; gap: 12px; }
    .slider-row input[type="range"] { flex: 1; }
    .slider-row span { min-width: 46px; text-align: right; font-weight: 600; font-size: 14px; color: var(--blue); }
    .btn-group { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
    button.btn { background: #334155; border: 1px solid var(--border); color: var(--text); padding: 7px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.15s ease; }
    button.btn:hover { background: #475569; }
    button.btn-primary { background: #0284c7; border-color: #38bdf8; color: white; font-weight: 600; padding: 9px 14px; width: 100%; }
    button.btn-primary:hover { background: #0369a1; }

    /* 1-Tap Resident Check-in Buttons */
    .tap-btn { padding: 10px 8px; border-radius: 8px; font-size: 12px; font-weight: 700; cursor: pointer; border: 1px solid; text-align: center; transition: transform 0.1s ease; }
    .tap-btn:active { transform: scale(0.97); }
    .tap-normal { background: rgba(16, 185, 129, 0.14); border-color: var(--green); color: #6ee7b7; }
    .tap-low { background: rgba(245, 158, 11, 0.14); border-color: var(--yellow); color: #fcd34d; }
    .tap-dry { background: rgba(239, 68, 68, 0.16); border-color: var(--red); color: #fca5a5; }

    .add-box { background: #0b1120; border: 1px dashed #475569; border-radius: 8px; padding: 12px; margin-top: 12px; display: none; }
    .add-box.open { display: block; }

    /* Stacked Community Availability Bar */
    .avail-bar { height: 10px; border-radius: 999px; background: #0b1120; overflow: hidden; display: flex; margin: 8px 0; border: 1px solid var(--border); }
    .bar-norm { background: var(--green); height: 100%; transition: width 0.25s ease; }
    .bar-low { background: var(--yellow); height: 100%; transition: width 0.25s ease; }
    .bar-dry { background: var(--red); height: 100%; transition: width 0.25s ease; }

    .checkin-feed { max-height: 125px; overflow-y: auto; margin-top: 10px; border-top: 1px solid var(--border); padding-top: 8px; }
    .checkin-item { display: flex; justify-content: space-between; align-items: center; font-size: 11px; padding: 5px 8px; background: #0b1120; border-radius: 5px; margin-bottom: 5px; color: #cbd5e1; }

    /* Status banner */
    .status-banner { border-radius: 10px; padding: 18px; margin-bottom: 20px; border-left: 6px solid; }
    .status-banner.RED { background: rgba(239, 68, 68, 0.12); border-color: var(--red); color: #fca5a5; }
    .status-banner.YELLOW { background: rgba(245, 158, 11, 0.12); border-color: var(--yellow); color: #fde68a; }
    .status-banner.GREEN { background: rgba(16, 185, 129, 0.12); border-color: var(--green); color: #a7f3d0; }
    .status-title { font-size: 21px; font-weight: 800; display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
    .status-desc { font-size: 13px; line-height: 1.5; opacity: 0.95; }

    /* Metrics row */
    .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
    .metric-box { background: #0b1120; border: 1px solid var(--border); border-radius: 8px; padding: 14px; }
    .metric-label { font-size: 11px; color: var(--muted); margin-bottom: 6px; text-transform: uppercase; font-weight: 600; }
    .metric-val { font-size: 20px; font-weight: 700; color: var(--text); }
    .metric-sub { font-size: 11px; color: var(--muted); margin-top: 4px; }

    /* Signal triggers list */
    .signals-list { list-style: none; margin-top: 8px; }
    .signals-list li { padding: 8px 12px; margin-bottom: 6px; border-radius: 6px; font-size: 12px; display: flex; align-items: center; justify-content: space-between; }
    .signal-active { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; font-weight: 600; }
    .signal-inactive { background: #0b1120; border: 1px solid var(--border); color: var(--muted); }

    /* Hydrograph SVG */
    .chart-box { background: #0b1120; border: 1px solid var(--border); border-radius: 8px; padding: 14px; margin-top: 14px; }
    svg { width: 100%; height: 210px; overflow: visible; }
    .legend { display: flex; gap: 16px; font-size: 11px; margin-top: 10px; color: var(--muted); justify-content: center; }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 2px; }
  </style>
</head>
<body>

  <header>
    <div>
      <h1>Nagpur Community Water Scarcity & Groundwater Monitor</h1>
      <p style="font-size: 12px; color: var(--muted); margin-top: 4px;">
        YCCE HackKumbh 2026 · Theme 03 PS 04 · Live Open-Meteo Rainfall + Daily Household Water Availability Log
      </p>
    </div>
    <div style="display: flex; gap: 8px; align-items: center;">
      <span id="liveRainBadge" class="badge" style="background: rgba(16, 185, 129, 0.14); color: #6ee7b7; border: 1px solid var(--green);">
        48h Rain: -- mm
      </span>
      <span id="colonyCountBadge" class="badge" style="background: rgba(56, 189, 248, 0.15); color: var(--blue); border: 1px solid var(--blue);">
        Loading...
      </span>
    </div>
  </header>

  <div class="grid">
    <!-- Left Column -->
    <div>
      <!-- Card 1: Colony Selector -->
      <div class="card">
        <h2>
          <span>1. Select Nagpur Colony / Ward</span>
          <button class="btn" style="font-size: 11px; padding: 3px 8px;" onclick="toggleAddColony()">+ Add Colony</button>
        </h2>

        <div class="two-col field">
          <div>
            <label>Filter by Tehsil / Zone</label>
            <select id="tehsilFilter" onchange="filterColonies()">
              <option value="ALL">All Nagpur District</option>
            </select>
          </div>
          <div>
            <label>Search Area Name</label>
            <input type="text" id="colonySearch" placeholder="e.g. Hingna, Wadi, Ramdaspeth..." oninput="filterColonies()">
          </div>
        </div>

        <div class="field">
          <label>Colony / Village / Ward (<span id="filteredCountText">0</span> matching)</label>
          <select id="layoutSelect" onchange="onLayoutChange()"></select>
        </div>

        <div style="font-size: 11px; color: var(--muted); margin-bottom: 6px;">Quick Judge Demo Presets:</div>
        <div class="btn-group">
          <button class="btn" onclick="setPreset('drought')">🔥 Peak Drought</button>
          <button class="btn" onclick="setPreset('warning')">⚠️ Fast Drop</button>
          <button class="btn" onclick="setPreset('safe')">💧 Safe Baseline</button>
          <button class="btn" onclick="setPreset('pipe_burst')">🚨 Pipe/Motor Fault</button>
        </div>

        <div id="addColonyBox" class="add-box">
          <div style="font-size: 12px; font-weight: 700; color: var(--blue); margin-bottom: 8px;">Register New Nagpur Residential Layout</div>
          <div class="field">
            <label>Layout / Colony Name</label>
            <input type="text" id="newColonyName" placeholder="e.g. Gajanan Nagar, Hingna Road">
          </div>
          <div class="two-col field">
            <div>
              <label>Tehsil / Zone</label>
              <input type="text" id="newColonyTehsil" value="HINGNA">
            </div>
            <div>
              <label>Registered Homes</label>
              <input type="number" id="newColonyHomes" value="110" min="10" max="2000">
            </div>
          </div>
          <div class="two-col field">
            <div>
              <label>Latitude</label>
              <input type="number" id="newColonyLat" value="21.1150" step="0.0001">
            </div>
            <div>
              <label>Longitude</label>
              <input type="number" id="newColonyLon" value="78.9920" step="0.0001">
            </div>
          </div>
          <div class="field">
            <label>Average Borewell Pump Depth (m)</label>
            <input type="number" id="newColonyPump" value="22.0" step="0.5">
          </div>
          <button class="btn btn-primary" onclick="saveNewColony()">Save & Load Colony</button>
        </div>
      </div>

      <!-- Card 2: Local Verifier Periodic Well Depth -->
      <div class="card">
        <h2>
          <span>2. Local Verifier Well Depth Log</span>
          <span style="font-size: 11px; font-weight: normal; color: var(--muted);">Auto-Checked vs Live Rain</span>
        </h2>
        <div class="field">
          <label>Reference Well Depth Measured Today (m bgl)</label>
          <div class="slider-row">
            <input type="range" id="verifierDepth" min="1.5" max="26.0" step="0.1" value="15.2" oninput="updateVal('verifierDepthVal', this.value); evaluate()">
            <span id="verifierDepthVal">15.2m</span>
          </div>
        </div>
        <div class="two-col field">
          <div>
            <label>Last Recorded Depth (m bgl)</label>
            <div class="slider-row">
              <input type="range" id="lastRecordedDepth" min="1.5" max="26.0" step="0.1" value="14.6" oninput="updateVal('lastRecordedDepthVal', this.value); evaluate()">
              <span id="lastRecordedDepthVal">14.6m</span>
            </div>
          </div>
          <div>
            <label>Days Since Last Record</label>
            <select id="daysSinceRecord" onchange="evaluate()">
              <option value="7" selected>7 days (Summer Weekly)</option>
              <option value="14">14 days (Fortnightly)</option>
              <option value="30">30 days (Winter Monthly)</option>
            </select>
          </div>
        </div>
        <div style="font-size: 11px; color: var(--muted); margin-bottom: 8px;">
          48h Rainfall Feed: <b id="rainFeedDetail" style="color: var(--blue);">Fetching Open-Meteo...</b>
        </div>
        <div id="validationStatus" style="font-size: 11px; padding: 6px 10px; border-radius: 6px; background: #0b1120; border: 1px solid var(--border); color: var(--muted);">
          Validation: Pending
        </div>
      </div>

      <!-- Card 3: Real Community Daily Water Availability Logging -->
      <div class="card">
        <h2>
          <span>3. Daily Water Availability Check-in</span>
          <span style="font-size: 11px; font-weight: normal; color: var(--muted);">Resident 1-Tap Log</span>
        </h2>

        <div class="two-col field">
          <div>
            <label>Flat / Plot / House No.</label>
            <input type="text" id="residentUnitInput" placeholder="e.g. B-304 or Plot 22" value="B-304">
          </div>
          <div>
            <label>Registered Homes in Colony</label>
            <input type="text" id="totalHomesDisplay" value="80 homes" readonly style="opacity: 0.75;">
          </div>
        </div>

        <label>Tap Today's Tap & Borewell Status:</label>
        <div class="three-col field">
          <button class="tap-btn tap-normal" onclick="submitDailyCheckin('NORMAL')">🟢 Normal Supply</button>
          <button class="tap-btn tap-low" onclick="submitDailyCheckin('LOW_PRESSURE')">🟡 Low Pressure</button>
          <button class="tap-btn tap-dry" onclick="submitDailyCheckin('BOREWELL_DRY')">🔴 Borewell Dry</button>
        </div>

        <div class="avail-bar">
          <div id="barNorm" class="bar-norm" style="width: 80%;"></div>
          <div id="barLow" class="bar-low" style="width: 8%;"></div>
          <div id="barDry" class="bar-dry" style="width: 12%;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 11px; color: var(--muted);">
          <span style="color: #6ee7b7;">🟢 Normal: <b id="countNormText">0</b></span>
          <span style="color: #fcd34d;">🟡 Low: <b id="countLowText">0</b></span>
          <span style="color: #fca5a5;">🔴 Dry: <b id="countDryText">0</b> (<b id="pctDryText">0%</b>)</span>
        </div>

        <div class="checkin-feed" id="checkinFeed"></div>
      </div>
    </div>

    <!-- Output Dashboard -->
    <div>
      <div id="statusBanner" class="status-banner YELLOW">
        <div class="status-title" id="statusTitle">Connecting to Nagpur Engine...</div>
        <div class="status-desc" id="statusDesc">Evaluating combined physical groundwater & crowd signals...</div>
      </div>

      <div class="metrics-grid">
        <div class="metric-box">
          <div class="metric-label">Live Calibrated Depth</div>
          <div class="metric-val" id="metricLiveDepth">-- m</div>
          <div class="metric-sub" id="metricOffset">Offset: -- m vs Gov Sensor</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">Depletion Velocity</div>
          <div class="metric-val" id="metricVelocity">-- m/wk</div>
          <div class="metric-sub" id="metricDeficit">True Deficit: -- m</div>
        </div>
        <div class="metric-box">
          <div class="metric-label">Pump Runway</div>
          <div class="metric-val" id="metricRunway">-- days</div>
          <div class="metric-sub" id="metricRunwayLabel">--</div>
        </div>
      </div>

      <div class="card">
        <h2>
          <span>3-Signal Scarcity Breakdown</span>
          <span id="activeSignalsBadge" class="badge" style="background: rgba(56,189,248,0.15); color: var(--blue);">0/3 Active</span>
        </h2>
        <ul class="signals-list" id="signalsList"></ul>
      </div>

      <div class="card">
        <h2>
          <span>7-Day 6-Hourly Calibrated Hydrograph (Zero-Hardware Offset Wave)</span>
          <span id="stationDistanceBadge" style="font-size: 11px; color: var(--blue);">Matched: --</span>
        </h2>
        <div class="chart-box">
          <svg id="chartSvg" viewBox="0 0 600 180"></svg>
          <div class="legend">
            <div class="legend-item"><div class="legend-dot" style="background: var(--blue);"></div> CGWB Gov Telemetry Wave (Raw)</div>
            <div class="legend-item"><div class="legend-dot" style="background: #e11d48;"></div> Colony Live Calibrated Depth (Shifted)</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let allLayouts = [];
    let layoutMap = {};
    let currentCrowdState = { counts: { NORMAL: 65, LOW_PRESSURE: 6, BOREWELL_DRY: 9 }, recent_logs: [] };

    async function loadLayouts(selectId = null) {
      const res = await fetch('/api/layouts');
      allLayouts = await res.json();
      layoutMap = {};
      allLayouts.forEach(l => { layoutMap[l.id] = l; });

      document.getElementById('colonyCountBadge').innerText = `${allLayouts.length} Nagpur Colonies`;

      const tehsils = Array.from(new Set(allLayouts.map(l => l.tehsil || 'NAGPUR'))).sort();
      const tf = document.getElementById('tehsilFilter');
      const prevTehsil = tf.value || 'ALL';
      tf.innerHTML = `<option value="ALL">All Nagpur District (${allLayouts.length})</option>` +
                     `<option value="FEATURED">Featured Pilot Colonies (4)</option>`;
      tehsils.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = `Tehsil: ${t}`;
        tf.appendChild(opt);
      });
      tf.value = prevTehsil;

      filterColonies(selectId);
    }

    function filterColonies(preferredId = null) {
      const tehsilVal = document.getElementById('tehsilFilter').value;
      const query = document.getElementById('colonySearch').value.trim().toLowerCase();
      const sel = document.getElementById('layoutSelect');
      const currentSelected = preferredId || sel.value;

      const filtered = allLayouts.filter(l => {
        if (tehsilVal === 'FEATURED' && l.category !== 'Featured Pilot') return false;
        if (tehsilVal !== 'ALL' && tehsilVal !== 'FEATURED' && (l.tehsil || 'NAGPUR') !== tehsilVal) return false;
        if (query && !l.name.toLowerCase().includes(query) && !(l.tehsil || '').toLowerCase().includes(query)) return false;
        return true;
      });

      document.getElementById('filteredCountText').innerText = filtered.length;
      sel.innerHTML = '';

      filtered.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l.id;
        opt.textContent = l.category === 'Featured Pilot' ? `★ ${l.name}` : l.name;
        sel.appendChild(opt);
      });

      if (filtered.some(l => l.id === currentSelected)) {
        sel.value = currentSelected;
      }
      if (filtered.length > 0) {
        onLayoutChange();
      }
    }

    function toggleAddColony() {
      document.getElementById('addColonyBox').classList.toggle('open');
    }

    async function saveNewColony() {
      const name = document.getElementById('newColonyName').value.trim();
      if (!name) {
        alert('Please enter a Nagpur colony or layout name.');
        return;
      }
      const payload = {
        name: name,
        tehsil: document.getElementById('newColonyTehsil').value.trim().toUpperCase() || 'NAGPUR',
        total_households: parseInt(document.getElementById('newColonyHomes').value) || 100,
        lat: parseFloat(document.getElementById('newColonyLat').value) || 21.1150,
        lon: parseFloat(document.getElementById('newColonyLon').value) || 78.9920,
        avg_pump_depth_m: parseFloat(document.getElementById('newColonyPump').value) || 22.0
      };

      const res = await fetch('/api/layouts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const created = await res.json();
      document.getElementById('newColonyName').value = '';
      document.getElementById('addColonyBox').classList.remove('open');
      document.getElementById('tehsilFilter').value = 'ALL';
      document.getElementById('colonySearch').value = '';
      await loadLayouts(created.id);
    }

    function updateVal(id, val) {
      document.getElementById(id).innerText = val + (id.includes('Depth') ? 'm' : '');
    }

    function renderCrowdUI(totalHomes) {
      const c = currentCrowdState.counts;
      const n = c.NORMAL || 0;
      const l = c.LOW_PRESSURE || 0;
      const d = c.BOREWELL_DRY || 0;
      const denom = Math.max(totalHomes, n + l + d, 1);

      document.getElementById('barNorm').style.width = ((n / denom) * 100).toFixed(1) + '%';
      document.getElementById('barLow').style.width = ((l / denom) * 100).toFixed(1) + '%';
      document.getElementById('barDry').style.width = ((d / denom) * 100).toFixed(1) + '%';

      document.getElementById('countNormText').innerText = n;
      document.getElementById('countLowText').innerText = l;
      document.getElementById('countDryText').innerText = d;
      document.getElementById('pctDryText').innerText = ((d / denom) * 100).toFixed(1) + '%';

      const feed = document.getElementById('checkinFeed');
      feed.innerHTML = '';
      const badgeMap = {
        NORMAL: '🟢 Normal',
        LOW_PRESSURE: '🟡 Low Pressure',
        BOREWELL_DRY: '🔴 Borewell Dry'
      };
      (currentCrowdState.recent_logs || []).slice(0, 6).forEach(item => {
        const div = document.createElement('div');
        div.className = 'checkin-item';
        div.innerHTML = `<span><b>${item.unit}</b> · ${item.note || 'Daily check-in'}</span><span>${badgeMap[item.status] || item.status} (${item.time})</span>`;
        feed.appendChild(div);
      });
    }

    async function onLayoutChange() {
      const id = document.getElementById('layoutSelect').value;
      const l = layoutMap[id];
      if (!l) return;
      const lastRec = l.default_last_recorded_depth ?? 10.0;
      document.getElementById('totalHomesDisplay').value = `${l.total_households} homes`;
      document.getElementById('verifierDepth').value = l.default_verifier_depth;
      document.getElementById('lastRecordedDepth').value = lastRec;
      document.getElementById('verifierDepthVal').innerText = l.default_verifier_depth + 'm';
      document.getElementById('lastRecordedDepthVal').innerText = lastRec + 'm';
      document.getElementById('daysSinceRecord').value = '7';

      const crowdRes = await fetch(`/api/community-state?layout_id=${encodeURIComponent(id)}`);
      currentCrowdState = await crowdRes.json();
      renderCrowdUI(l.total_households);
      evaluate();
    }

    async function submitDailyCheckin(status) {
      const id = document.getElementById('layoutSelect').value;
      const l = layoutMap[id];
      if (!l) return;
      const unit = document.getElementById('residentUnitInput').value.trim() || 'Resident';

      const res = await fetch('/api/community-checkin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ layout_id: id, unit: unit, status: status })
      });
      currentCrowdState = await res.json();
      renderCrowdUI(l.total_households);
      evaluate();
    }

    async function setPreset(type) {
      const id = document.getElementById('layoutSelect').value;
      const l = layoutMap[id];
      if (!l) return;
      const homes = l.total_households;
      document.getElementById('daysSinceRecord').value = '7';

      let counts = { NORMAL: homes - 3, LOW_PRESSURE: 2, BOREWELL_DRY: 1 };
      let label = 'Safe Baseline Preset';

      if (type === 'drought') {
        document.getElementById('verifierDepth').value = 18.8;
        document.getElementById('lastRecordedDepth').value = 16.5;
        const dry = Math.round(homes * 0.42);
        const low = Math.round(homes * 0.15);
        counts = { NORMAL: Math.max(0, homes - dry - low), LOW_PRESSURE: low, BOREWELL_DRY: dry };
        label = 'Peak Summer Drought Preset';
      } else if (type === 'warning') {
        document.getElementById('verifierDepth').value = 15.2;
        document.getElementById('lastRecordedDepth').value = 14.6;
        const dry = Math.round(homes * 0.11);
        const low = Math.round(homes * 0.08);
        counts = { NORMAL: Math.max(0, homes - dry - low), LOW_PRESSURE: low, BOREWELL_DRY: dry };
        label = 'Rapid Depletion Warning Preset';
      } else if (type === 'safe') {
        document.getElementById('verifierDepth').value = 5.0;
        document.getElementById('lastRecordedDepth').value = 4.9;
        counts = { NORMAL: Math.max(0, homes - 3), LOW_PRESSURE: 2, BOREWELL_DRY: 1 };
        label = 'Healthy Supply Preset';
      } else if (type === 'pipe_burst') {
        document.getElementById('verifierDepth').value = 4.8;
        document.getElementById('lastRecordedDepth').value = 4.8;
        const dry = Math.round(homes * 0.45);
        const low = Math.round(homes * 0.10);
        counts = { NORMAL: Math.max(0, homes - dry - low), LOW_PRESSURE: low, BOREWELL_DRY: dry };
        label = 'Pipe / Motor Fault Anomaly Preset';
      }

      document.getElementById('verifierDepthVal').innerText = document.getElementById('verifierDepth').value + 'm';
      document.getElementById('lastRecordedDepthVal').innerText = document.getElementById('lastRecordedDepth').value + 'm';

      const res = await fetch('/api/community-preset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ layout_id: id, counts: counts, preset_label: label })
      });
      currentCrowdState = await res.json();
      renderCrowdUI(homes);
      evaluate();
    }

    async function evaluate() {
      const curId = document.getElementById('layoutSelect').value;
      const l = layoutMap[curId];
      if (!l) return;
      const payload = {
        layout_name: l.name,
        lat: l.lat,
        lon: l.lon,
        aquifer_type: l.aquifer_type,
        avg_pump_depth_m: l.avg_pump_depth_m,
        total_households: l.total_households,
        verifier_manual_depth_m: parseFloat(document.getElementById('verifierDepth').value),
        last_recorded_depth_m: parseFloat(document.getElementById('lastRecordedDepth').value),
        days_since_last_record: parseInt(document.getElementById('daysSinceRecord').value) || 7,
        crowd_checkins: currentCrowdState.counts
      };

      try {
        const res = await fetch('/api/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok || data.error) {
          document.getElementById('statusBanner').className = 'status-banner RED';
          document.getElementById('statusTitle').innerText = 'Backend Evaluation Error';
          document.getElementById('statusDesc').innerText = data.error || 'Server returned HTTP ' + res.status;
          return;
        }
        renderResults(data);
      } catch (err) {
        document.getElementById('statusBanner').className = 'status-banner RED';
        document.getElementById('statusTitle').innerText = 'Connection Error';
        document.getElementById('statusDesc').innerText = 'Could not reach Python server on port 8000: ' + err.message;
      }
    }

    function renderResults(d) {
      const banner = document.getElementById('statusBanner');
      banner.className = 'status-banner ' + d.scarcity_status;
      const icons = { RED: '🔴', YELLOW: '🟡', GREEN: '🟢' };
      document.getElementById('statusTitle').innerText = `${icons[d.scarcity_status]} ${d.scarcity_status} STATUS: ${d.scarcity_status === 'RED' ? 'CRITICAL SCARCITY' : (d.scarcity_status === 'YELLOW' ? 'MODERATE WARNING' : 'NORMAL SUPPLY')}`;
      document.getElementById('statusDesc').innerText = d.diagnosis;

      const rainMm = d.raw_stage1.rain_48h_mm ?? 0;
      const rainSrc = d.raw_stage1.rainfall_source || 'Open-Meteo';
      document.getElementById('liveRainBadge').innerText = `48h Rain: ${rainMm} mm`;
      document.getElementById('rainFeedDetail').innerText = `${rainMm} mm (${rainSrc})`;

      document.getElementById('metricLiveDepth').innerText = d.groundwater_summary.live_calibrated_depth_m + ' m';
      const offVal = d.raw_stage1.local_offset_m || 0;
      document.getElementById('metricOffset').innerText = `Offset: ${offVal >= 0 ? '+' : ''}${offVal}m vs ${d.groundwater_summary.matched_gov_station}`;
      document.getElementById('metricVelocity').innerText = (d.raw_stage1.depletion_velocity_m_per_week > 0 ? '+' : '') + d.raw_stage1.depletion_velocity_m_per_week + ' m/wk';
      const defVal = d.signals.signal_1_aquifer_stress.deficit_m;
      document.getElementById('metricDeficit').innerText = `True Deficit: ${defVal >= 0 ? '+' : ''}${defVal} m`;

      const pr = d.groundwater_summary.pump_runway;
      document.getElementById('metricRunway').innerText = pr.days !== null ? pr.days + ' days' : 'Stable';
      document.getElementById('metricRunwayLabel').innerText = pr.label;

      const vv = d.groundwater_summary.verifier_validation;
      const vvElem = document.getElementById('validationStatus');
      if (vv) {
        vvElem.innerText = `Validation: ${vv.status} — ${vv.reason}`;
        vvElem.style.borderColor = vv.status === 'VERIFIED' ? 'var(--green)' : 'var(--red)';
        vvElem.style.color = vv.status === 'VERIFIED' ? '#a7f3d0' : '#fca5a5';
      }

      const sigList = document.getElementById('signalsList');
      sigList.innerHTML = '';
      const items = [
        { name: `Signal 1: Aquifer Stress (>2.5m Deficit or ≤1.5m Col)`, active: d.signals.signal_1_aquifer_stress.active, detail: `True Deficit: ${defVal >= 0 ? '+' : ''}${defVal}m` },
        { name: `Signal 2: Rapid Depletion (>0.5m/week drop)`, active: d.signals.signal_2_rapid_depletion.active, detail: `Current: ${d.signals.signal_2_rapid_depletion.velocity_m_per_week}m/wk` },
        { name: `Signal 3: Community Shortage (≥30% Dry)`, active: d.signals.signal_3_community_shortage.active, detail: `Current: ${d.signals.signal_3_community_shortage.dry_percentage}% (${d.crowd_summary.dry_reports_count} homes)` }
      ];
      items.forEach(it => {
        const li = document.createElement('li');
        li.className = it.active ? 'signal-active' : 'signal-inactive';
        li.innerHTML = `<span>${it.active ? '⚠️' : '✓'} ${it.name}</span><span style="font-size: 11px; opacity: 0.85;">${it.detail}</span>`;
        sigList.appendChild(li);
      });
      document.getElementById('activeSignalsBadge').innerText = `${d.signals.active_signals_count}/3 Active`;
      document.getElementById('stationDistanceBadge').innerText = `Nearest Sensor: ${d.groundwater_summary.matched_gov_station} (${d.groundwater_summary.station_distance_km} km away)`;

      drawHydrograph(d.raw_stage1.calibrated_series);
    }

    function drawHydrograph(series) {
      if (!series || series.length < 2) return;
      const svg = document.getElementById('chartSvg');
      svg.innerHTML = '';
      const w = 600, h = 180, padL = 40, padR = 20, padT = 20, padB = 30;

      const govDepths = series.map(p => p.gov_depth_m);
      const calDepths = series.map(p => p.calibrated_layout_depth_m);
      const allDepths = govDepths.concat(calDepths);
      const minD = Math.floor(Math.min(...allDepths) - 0.5);
      const maxD = Math.ceil(Math.max(...allDepths) + 0.5);

      const xScale = i => padL + (i / (series.length - 1)) * (w - padL - padR);
      const yScale = d => padT + ((d - minD) / (maxD - minD)) * (h - padT - padB);

      for (let yVal = minD; yVal <= maxD; yVal += Math.max(1, Math.round((maxD - minD) / 4))) {
        const y = yScale(yVal);
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', padL); line.setAttribute('x2', w - padR);
        line.setAttribute('y1', y); line.setAttribute('y2', y);
        line.setAttribute('stroke', '#334155'); line.setAttribute('stroke-dasharray', '3 3');
        svg.appendChild(line);

        const txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        txt.setAttribute('x', padL - 8); txt.setAttribute('y', y + 4);
        txt.setAttribute('text-anchor', 'end'); txt.setAttribute('fill', '#94a3b8');
        txt.setAttribute('font-size', '10px'); txt.textContent = yVal + 'm';
        svg.appendChild(txt);
      }

      function buildPath(pts, key) {
        return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(i).toFixed(1)} ${yScale(p[key]).toFixed(1)}`).join(' ');
      }

      const pathGov = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      pathGov.setAttribute('d', buildPath(series, 'gov_depth_m'));
      pathGov.setAttribute('fill', 'none'); pathGov.setAttribute('stroke', '#38bdf8');
      pathGov.setAttribute('stroke-width', '2'); svg.appendChild(pathGov);

      const pathCal = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      pathCal.setAttribute('d', buildPath(series, 'calibrated_layout_depth_m'));
      pathCal.setAttribute('fill', 'none'); pathCal.setAttribute('stroke', '#e11d48');
      pathCal.setAttribute('stroke-width', '2.5'); svg.appendChild(pathCal);

      [0, series.length - 1].forEach(idx => {
        const t = series[idx].timestamp.split(' ')[0];
        const lbl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        lbl.setAttribute('x', xScale(idx)); lbl.setAttribute('y', h - 8);
        lbl.setAttribute('text-anchor', idx === 0 ? 'start' : 'end');
        lbl.setAttribute('fill', '#94a3b8'); lbl.setAttribute('font-size', '10px');
        lbl.textContent = t;
        svg.appendChild(lbl);
      });
    }

    window.addEventListener('DOMContentLoaded', () => loadLayouts('hingna'));
  </script>
</body>
</html>
"""


class DashboardRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def _send_json(self, code: int, payload):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif url.path == "/api/layouts":
            self._send_json(200, ALL_LAYOUTS)
        elif url.path == "/api/community-state":
            qs = urllib.parse.parse_qs(url.query)
            layout_id = (qs.get("layout_id") or ["hingna"])[0]
            if layout_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown layout"})
                return
            self._send_json(200, get_layout_crowd_state(layout_id))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if url.path == "/api/layouts":
            name = str(data.get("name", "")).strip()
            tehsil = str(data.get("tehsil", "NAGPUR")).strip().upper()
            homes = max(10, int(data.get("total_households", 100)))
            lat = float(data.get("lat", 21.1150))
            lon = float(data.get("lon", 78.9920))
            pump_d = float(data.get("avg_pump_depth_m", 22.0))

            slug = "custom_" + "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")
            slug = f"{slug}_{int(datetime.now().timestamp())}"

            new_item = {
                "id": slug,
                "name": f"{name} ({tehsil.title()})",
                "tehsil": tehsil,
                "category": "Custom Registered Layout",
                "lat": lat,
                "lon": lon,
                "aquifer_type": "Basalt",
                "avg_pump_depth_m": pump_d,
                "total_households": homes,
                "default_verifier_depth": 10.5,
                "default_last_recorded_depth": 10.2,
                "default_crowd": {"NORMAL": homes - 4, "LOW_PRESSURE": 3, "BOREWELL_DRY": 1},
            }
            ALL_LAYOUTS.insert(len(FEATURED_LAYOUTS), new_item)
            LAYOUT_INDEX[slug] = new_item

            custom_only = [l for l in ALL_LAYOUTS if l.get("category") == "Custom Registered Layout"]
            with open(CUSTOM_LAYOUTS_PATH, "w", encoding="utf-8") as f:
                json.dump(custom_only, f, indent=2)

            self._send_json(201, new_item)

        elif url.path == "/api/community-checkin":
            layout_id = data.get("layout_id")
            status = data.get("status", "NORMAL")
            unit = str(data.get("unit", "Resident")).strip() or "Resident"
            if layout_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown layout"})
                return

            state = get_layout_crowd_state(layout_id)
            counts = state["counts"]
            if status in counts:
                counts[status] = counts.get(status, 0) + 1
                if status != "NORMAL" and counts.get("NORMAL", 0) > 0:
                    counts["NORMAL"] -= 1

            state["recent_logs"].insert(0, {
                "time": datetime.now().strftime("%I:%M %p"),
                "unit": unit,
                "status": status,
                "note": "Daily household availability log",
            })
            state["recent_logs"] = state["recent_logs"][:15]
            save_community_state(COMMUNITY_STATE)
            self._send_json(200, state)

        elif url.path == "/api/community-preset":
            layout_id = data.get("layout_id")
            if layout_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown layout"})
                return
            state = get_layout_crowd_state(layout_id)
            state["counts"] = data.get("counts", state["counts"])
            state["recent_logs"].insert(0, {
                "time": datetime.now().strftime("%I:%M %p"),
                "unit": "Society Summary",
                "status": "BOREWELL_DRY" if state["counts"].get("BOREWELL_DRY", 0) >= 15 else "NORMAL",
                "note": data.get("preset_label", "Scenario loaded"),
            })
            state["recent_logs"] = state["recent_logs"][:15]
            save_community_state(COMMUNITY_STATE)
            self._send_json(200, state)

        elif url.path == "/api/evaluate":
            try:
                result = engine.evaluate_layout_scarcity(
                    layout_name=data.get("layout_name", "Demo Layout"),
                    lat=float(data.get("lat", 21.1020)),
                    lon=float(data.get("lon", 78.9850)),
                    aquifer_type=data.get("aquifer_type", "Basalt"),
                    avg_pump_depth_m=float(data.get("avg_pump_depth_m", 22.0)),
                    total_households=int(data.get("total_households", 100)),
                    crowd_checkins=data.get("crowd_checkins", {}),
                    verifier_manual_depth_m=data.get("verifier_manual_depth_m"),
                    last_recorded_depth_m=data.get("last_recorded_depth_m"),
                    days_since_last_record=int(data.get("days_since_last_record", 7)),
                    rain_48h_mm=None,  # Always fetch live Open-Meteo 48h rainfall
                )
                self._send_json(200, result)
            except Exception as e:
                self._send_json(500, {"error": str(e)})
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = ThreadingHTTPServer(server_address, DashboardRequestHandler)
    print("\n=======================================================")
    print(f" Nagpur Groundwater Monitor LIVE ({len(ALL_LAYOUTS)} locations loaded)")
    print(f" Open your browser: http://localhost:{PORT}")
    print(" Press Ctrl+C to stop the server.")
    print("=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()