from datetime import datetime
import hashlib
import http.cookies
import json
import math
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.parse

from stage2_scarcity_engine import Stage2ScarcityEngine

PORT = 8000
PROCESSED_DIR = r"D:\hackumbh\processed"
QUARTERLY_PATH = os.path.join(PROCESSED_DIR, "nagpur_quarterly.json")
CUSTOM_LAYOUTS_PATH = os.path.join(PROCESSED_DIR, "custom_layouts.json")
UNIFIED_STATE_PATH = os.path.join(PROCESSED_DIR, "unified_state.json")

engine = Stage2ScarcityEngine()

# Active in-memory login sessions: {token: {"name": str, "role": str}}
SESSIONS: dict[str, dict] = {}

ROLE_META = {
    "citizen": {
        "title": "Citizen Portal",
        "home": "/citizen",
        "badge": "Resident View",
        "default_name": "Aarav Deshmukh",
        "default_pass": "citizen123",
    },
    "verifier": {
        "title": "Field Verifier Portal",
        "home": "/verifier",
        "badge": "Society / Gramsevak Verifier",
        "default_name": "Rajesh Kulkarni",
        "default_pass": "verifier123",
    },
    "utility": {
        "title": "Utility & Tanker Portal",
        "home": "/utility",
        "badge": "Water & Fleet Operations",
        "default_name": "NMC Dispatch Desk",
        "default_pass": "utility123",
    },
}

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
        "default_verifier_depth": 18.6,
        "default_last_recorded_depth": 16.8,
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

# All 14 Talukas of Nagpur District (from teammate's RWH portal)
NAGPUR_TALUKAS = [
    {"id": "nagpur_urban", "name": "Nagpur (Urban)", "rainfall_mm": 1100, "rain_events": 52},
    {"id": "nagpur_rural", "name": "Nagpur (Rural)", "rainfall_mm": 1080, "rain_events": 51},
    {"id": "kamptee", "name": "Kamptee", "rainfall_mm": 1120, "rain_events": 53},
    {"id": "hingna", "name": "Hingna", "rainfall_mm": 1050, "rain_events": 50},
    {"id": "kalmeshwar", "name": "Kalmeshwar", "rainfall_mm": 980, "rain_events": 47},
    {"id": "katol", "name": "Katol", "rainfall_mm": 900, "rain_events": 44},
    {"id": "narkhed", "name": "Narkhed", "rainfall_mm": 880, "rain_events": 43},
    {"id": "savner", "name": "Savner", "rainfall_mm": 990, "rain_events": 48},
    {"id": "parseoni", "name": "Parseoni", "rainfall_mm": 1160, "rain_events": 54},
    {"id": "ramtek", "name": "Ramtek", "rainfall_mm": 1220, "rain_events": 57},
    {"id": "mauda", "name": "Mauda", "rainfall_mm": 1150, "rain_events": 54},
    {"id": "kuhi", "name": "Kuhi", "rainfall_mm": 1180, "rain_events": 55},
    {"id": "umred", "name": "Umred", "rainfall_mm": 1140, "rain_events": 53},
    {"id": "bhiwapur", "name": "Bhiwapur", "rainfall_mm": 1210, "rain_events": 56},
]

ROOF_SURFACES = {
    "concrete": {"label": "Concrete / RCC Terrace", "coeff": 0.85},
    "metal": {"label": "Metal / GI Sheet Roof", "coeff": 0.90},
    "tiled": {"label": "Tiled / Sloped Roof", "coeff": 0.75},
}

DEFAULT_DEPOTS = [
    {
        "id": "depot-1",
        "name": "Zone 1 Depot — Dharampeth",
        "lat": 21.1420,
        "lon": 79.0640,
        "max_capacity_l": 40000,
        "current_stock_l": 30000,
        "trucks_ready": 4,
        "trucks_total": 5,
    },
    {
        "id": "depot-2",
        "name": "Zone 2 Depot — Sitabuldi",
        "lat": 21.1500,
        "lon": 79.0870,
        "max_capacity_l": 35000,
        "current_stock_l": 25000,
        "trucks_ready": 3,
        "trucks_total": 4,
    },
    {
        "id": "depot-3",
        "name": "Zone 3 Depot — Hingna Road",
        "lat": 21.0920,
        "lon": 78.9720,
        "max_capacity_l": 50000,
        "current_stock_l": 40000,
        "trucks_ready": 5,
        "trucks_total": 6,
    },
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


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
                for item in json.load(f):
                    if item.get("id") not in seen_ids:
                        if "default_last_recorded_depth" not in item:
                            item["default_last_recorded_depth"] = item.get("default_verifier_depth", 10.2)
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


def default_unified_state() -> dict:
    return {
        "users": {
            "citizen:aarav deshmukh": {"name": "Aarav Deshmukh", "role": "citizen", "pw_hash": hashlib.sha256(b"citizen123").hexdigest()},
            "verifier:rajesh kulkarni": {"name": "Rajesh Kulkarni", "role": "verifier", "pw_hash": hashlib.sha256(b"verifier123").hexdigest()},
            "utility:nmc dispatch desk": {"name": "NMC Dispatch Desk", "role": "utility", "pw_hash": hashlib.sha256(b"utility123").hexdigest()},
        },
        "crowd_by_layout": {},
        "verifier_by_layout": {},
        "rwh_checks_by_layout": {},
        "depots": [dict(d) for d in DEFAULT_DEPOTS],
        "tanker_orders": [
            {
                "id": "IND-101",
                "layout_id": "wanadongri",
                "layout_name": "Shanti Vihar Layout, Wanadongri",
                "volume_l": 10000,
                "trips": 1,
                "lpcd_norm": 55,
                "verified_by": "Rajesh Kulkarni",
                "status": "DISPATCHED",
                "depot_id": "depot-3",
                "depot_name": "Zone 3 Depot — Hingna Road",
                "vehicle_no": "MH-31-TK-412",
                "distance_km": 1.75,
                "created_at": "08:30 AM",
                "updated_at": "08:45 AM",
            }
        ],
        "tickets": [
            {
                "id": "W1042",
                "layout_id": "hingna",
                "layout_name": "Samarth Nagar, Hingna",
                "issue_type": "Leaking pipeline",
                "severity": "Moderate",
                "description": "Main feeder valve weeping near Gate 2",
                "reported_by": "Aarav Deshmukh",
                "status": "OPEN",
                "created_at": "09:05 AM",
            }
        ],
    }


def load_unified_state() -> dict:
    if os.path.exists(UNIFIED_STATE_PATH):
        try:
            with open(UNIFIED_STATE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                base = default_unified_state()
                for k, v in base.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    st = default_unified_state()
    save_unified_state(st)
    return st


def save_unified_state(state: dict):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(UNIFIED_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


STATE = load_unified_state()


def get_crowd_record(layout_id: str) -> dict:
    layout = LAYOUT_INDEX[layout_id]
    if layout_id not in STATE["crowd_by_layout"]:
        STATE["crowd_by_layout"][layout_id] = {
            "counts": dict(layout["default_crowd"]),
            "recent_logs": [
                {
                    "time": "08:15 AM",
                    "unit": "B-201",
                    "by": "Resident Log",
                    "status": "BOREWELL_DRY" if layout["default_crowd"]["BOREWELL_DRY"] >= 15 else "NORMAL",
                    "note": "Morning overhead tank check",
                }
            ],
        }
    return STATE["crowd_by_layout"][layout_id]


def get_verifier_record(layout_id: str) -> dict:
    layout = LAYOUT_INDEX[layout_id]
    if layout_id not in STATE["verifier_by_layout"]:
        STATE["verifier_by_layout"][layout_id] = {
            "verifier_depth_m": layout["default_verifier_depth"],
            "last_recorded_depth_m": layout["default_last_recorded_depth"],
            "days_since_last": 7,
            "verified_by": "Baseline Record",
            "updated_at": "Today",
        }
    return STATE["verifier_by_layout"][layout_id]


def evaluate_layout_full(layout_id: str) -> dict:
    layout = LAYOUT_INDEX[layout_id]
    crowd = get_crowd_record(layout_id)
    vrec = get_verifier_record(layout_id)

    eval_out = engine.evaluate_layout_scarcity(
        layout_name=layout["name"],
        lat=layout["lat"],
        lon=layout["lon"],
        aquifer_type=layout["aquifer_type"],
        avg_pump_depth_m=layout["avg_pump_depth_m"],
        total_households=layout["total_households"],
        crowd_checkins=crowd["counts"],
        verifier_manual_depth_m=float(vrec["verifier_depth_m"]),
        last_recorded_depth_m=float(vrec["last_recorded_depth_m"]),
        days_since_last_record=int(vrec["days_since_last"]),
        rain_48h_mm=None,  # Live Open-Meteo 48h rainfall
    )

    # Calculate recommended emergency water requirement (55 LPCD Jal Jeevan Mission norm, ~5 persons/household)
    dry_homes = crowd["counts"].get("BOREWELL_DRY", 0)
    affected_homes = max(dry_homes, int(round(layout["total_households"] * 0.25))) if eval_out["scarcity_status"] == "RED" else dry_homes
    recommended_litres = affected_homes * 5 * 55
    recommended_trips = max(1, math.ceil(recommended_litres / 10000)) if recommended_litres > 0 else 0

    return {
        "layout": layout,
        "crowd": crowd,
        "verifier_record": vrec,
        "evaluation": eval_out,
        "recommended_tanker": {
            "affected_homes": affected_homes,
            "litres_per_day": recommended_litres,
            "trips_10k": recommended_trips,
        },
    }


def calculate_rwh(taluka_id: str, area: float, unit: str, surface_id: str) -> dict:
    taluka = next((t for t in NAGPUR_TALUKAS if t["id"] == taluka_id), NAGPUR_TALUKAS[0])
    surf = ROOF_SURFACES.get(surface_id, ROOF_SURFACES["concrete"])
    clean_area = max(0.0, float(area or 0.0))
    area_sqm = clean_area * 0.092903 if unit == "sqft" else clean_area
    gross_l = area_sqm * taluka["rainfall_mm"] * surf["coeff"]
    first_flush_l = area_sqm * 0.8 * taluka["rain_events"]
    net_l = max(0.0, gross_l - first_flush_l)
    return {
        "taluka": taluka["name"],
        "rainfall_mm": taluka["rainfall_mm"],
        "rain_events": taluka["rain_events"],
        "surface_label": surf["label"],
        "area_sqm": round(area_sqm, 2),
        "gross_l": int(round(gross_l)),
        "first_flush_l": int(round(first_flush_l)),
        "net_l": int(round(net_l)),
    }


# ---------------------------------------------------------------------------
# SHARED HTML / CSS SHELL
# ---------------------------------------------------------------------------
SHARED_HEAD = r"""
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
<style>
  :root {
    --bg: #0b1220;
    --panel: #131c2e;
    --panel2: #0e1625;
    --border: #26354d;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --green: #10b981;
    --yellow: #f59e0b;
    --red: #ef4444;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: var(--bg); color: var(--text); min-height: 100vh; }
  .topbar {
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 12px 22px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px;
  }
  .brand { font-weight: 800; font-size: 16px; color: var(--accent); display: flex; align-items: center; gap: 10px; }
  .pill { font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 999px; border: 1px solid var(--border); background: var(--panel2); color: #cbd5e1; }
  .pill.green { border-color: var(--green); color: #6ee7b7; background: rgba(16,185,129,0.12); }
  .pill.blue { border-color: var(--accent); color: #7dd3fc; background: rgba(56,189,248,0.12); }
  .nav-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  a.btn-link, button {
    background: #1e293b; color: var(--text); border: 1px solid var(--border);
    padding: 7px 12px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; text-decoration: none;
  }
  button.primary { background: #0284c7; border-color: #38bdf8; color: #fff; }
  button.success { background: #059669; border-color: #34d399; color: #fff; }
  button.danger { background: #dc2626; border-color: #f87171; color: #fff; }
  button:hover, a.btn-link:hover { filter: brightness(1.1); }
  .container { max-width: 1280px; margin: 0 auto; padding: 20px; }
  .grid-2 { display: grid; grid-template-columns: 420px 1fr; gap: 20px; }
  .grid-even { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  @media (max-width: 980px) { .grid-2, .grid-even, .grid-3 { grid-template-columns: 1fr; } }
  .card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 18px; margin-bottom: 18px; }
  .card h2 { font-size: 15px; margin-bottom: 12px; color: #e2e8f0; display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 5px; font-weight: 600; }
  input, select, textarea {
    width: 100%; background: var(--panel2); border: 1px solid var(--border); color: var(--text);
    padding: 8px 10px; border-radius: 8px; font-size: 13px; outline: none; margin-bottom: 10px;
  }
  input:focus, select:focus, textarea:focus { border-color: var(--accent); }
  .metric { background: var(--panel2); border: 1px solid var(--border); border-radius: 10px; padding: 12px; }
  .metric small { display: block; font-size: 11px; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
  .metric strong { font-size: 20px; color: var(--text); }
  .metric span { display: block; font-size: 11px; color: var(--muted); margin-top: 3px; }
  .banner { border-radius: 10px; padding: 15px; margin-bottom: 16px; border-left: 5px solid; }
  .banner.RED { background: rgba(239,68,68,0.13); border-color: var(--red); color: #fecaca; }
  .banner.YELLOW { background: rgba(245,158,11,0.13); border-color: var(--yellow); color: #fde68a; }
  .banner.GREEN { background: rgba(16,185,129,0.13); border-color: var(--green); color: #a7f3d0; }
  .map-box { height: 290px; border-radius: 10px; border: 1px solid var(--border); overflow: hidden; background: #09111e; }
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--border); }
  th { color: var(--muted); font-size: 11px; text-transform: uppercase; }
  .status-tag { padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
  .status-tag.RED, .status-tag.OPEN, .status-tag.FLAGGED { background: rgba(239,68,68,0.18); color: #fca5a5; }
  .status-tag.YELLOW, .status-tag.DISPATCHED, .status-tag.UNLOADED, .status-tag.IN_PROGRESS { background: rgba(245,158,11,0.18); color: #fcd34d; }
  .status-tag.GREEN, .status-tag.CONFIRMED, .status-tag.RESOLVED, .status-tag.VERIFIED { background: rgba(16,185,129,0.18); color: #6ee7b7; }
  .list-item { background: var(--panel2); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; font-size: 12px; display: flex; justify-content: space-between; align-items: center; gap: 10px; }
  .avail-bar { height: 10px; border-radius: 999px; background: var(--panel2); overflow: hidden; display: flex; margin: 8px 0; border: 1px solid var(--border); }
</style>
"""

MAP_HELPER_JS = r"""
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
  function createNagpurMap(divId, center = [21.125, 79.025], zoom = 11) {
    const el = document.getElementById(divId);
    if (!el || typeof L === 'undefined') return null;
    const map = L.map(divId).setView(center, zoom);
    const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap'
    });
    osm.on('tileerror', () => {
      el.style.backgroundImage = 'radial-gradient(#26364b 1px, transparent 1px)';
      el.style.backgroundSize = '20px 20px';
    });
    osm.addTo(map);
    return map;
  }
</script>
"""


# ---------------------------------------------------------------------------
# PAGE 0: MULTI-ROLE LOGIN PAGE (/login)
# ---------------------------------------------------------------------------
LOGIN_HTML = rf"""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Nagpur Water Network — Portal Sign In</title>
  {SHARED_HEAD}
  <style>
    .login-wrap {{ max-width: 520px; margin: 48px auto; padding: 0 16px; }}
    .role-tabs {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 16px; }}
    .role-tab {{
      padding: 10px 8px; border-radius: 10px; border: 1px solid var(--border); background: var(--panel2);
      color: var(--muted); font-size: 12px; font-weight: 700; text-align: center; cursor: pointer;
    }}
    .role-tab.active {{ border-color: var(--accent); color: #fff; background: rgba(56,189,248,0.16); }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="brand">Nagpur Water Scarcity & Recharge Network <span class="pill blue">91 Nagpur Locations</span></div>
    <span class="pill green">Stage 1/2 Engine + Live 48h Rain Connected</span>
  </div>

  <div class="login-wrap">
    <div class="card">
      <h1 style="font-size:20px; margin-bottom:6px;">Select Portal & Sign In</h1>
      <p style="font-size:13px; color:var(--muted); margin-bottom:16px;">
        Choose your role below and sign in with your Name and Password. Each portal displays only the tools and data meant for that role.
      </p>

      <div class="role-tabs">
        <div class="role-tab active" data-role="citizen" onclick="selectRole('citizen')">1. Citizen Portal</div>
        <div class="role-tab" data-role="verifier" onclick="selectRole('verifier')">2. Field Verifier</div>
        <div class="role-tab" data-role="utility" onclick="selectRole('utility')">3. Utility & Tanker</div>
      </div>

      <div id="roleHint" style="font-size:12px; color:#7dd3fc; background:var(--panel2); border:1px solid var(--border); padding:10px; border-radius:8px; margin-bottom:14px;"></div>

      <label>Full Name / Username</label>
      <input type="text" id="loginName" placeholder="Enter your name" />

      <label>Password</label>
      <input type="password" id="loginPass" placeholder="Enter password" />

      <div id="loginErr" style="color:#fca5a5; font-size:12px; margin-bottom:10px; display:none;"></div>

      <div style="display:flex; gap:10px;">
        <button class="primary" style="flex:1;" onclick="submitLogin('/api/login')">Sign In to Portal</button>
        <button style="flex:1;" onclick="submitLogin('/api/register')">Register & Sign In</button>
      </div>
    </div>
  </div>

  <script>
    const ROLE_DEFAULTS = __ROLE_DEFAULTS_JSON__;
    const ROLE_HINTS = {{
      citizen: "Citizen Portal: Daily household water check-in, live incoming tanker map & delivery confirmation, leak reporting, and 14-taluka RWH calculator.",
      verifier: "Field Verifier Portal: Reference well-depth entry with live 48h rainfall anti-cheat validation, 6-hourly calibrated hydrograph, and verified tanker indents.",
      utility: "Utility & Tanker Portal: Nagpur scarcity & fleet map, verified tanker dispatch from nearest depot, depot stock management, and leak ticket closure."
    }};
    let currentRole = "__PRESELECT_ROLE__";

    function selectRole(role) {{
      currentRole = role;
      document.querySelectorAll('.role-tab').forEach(el => el.classList.toggle('active', el.dataset.role === role));
      const d = ROLE_DEFAULTS[role];
      document.getElementById('loginName').value = d.default_name;
      document.getElementById('loginPass').value = d.default_pass;
      document.getElementById('roleHint').textContent = ROLE_HINTS[role];
      document.getElementById('loginErr').style.display = 'none';
    }}

    async function submitLogin(endpoint) {{
      const name = document.getElementById('loginName').value.trim();
      const password = document.getElementById('loginPass').value;
      const res = await fetch(endpoint, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ role: currentRole, name, password }})
      }});
      const data = await res.json();
      if (!res.ok) {{
        const err = document.getElementById('loginErr');
        err.textContent = data.error || 'Authentication failed';
        err.style.display = 'block';
        return;
      }}
      window.location.href = data.redirect;
    }}

    selectRole(currentRole);
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# PAGE 1: CITIZEN PORTAL (/citizen)
# ---------------------------------------------------------------------------
CITIZEN_HTML = rf"""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Citizen Portal — Nagpur Water Network</title>
  {SHARED_HEAD}
</head>
<body>
  <div class="topbar">
    <div class="brand">Citizen Water Portal <span class="pill green" id="rainBadge">48h Rain: -- mm</span></div>
    <div class="nav-actions">
      <span class="pill blue">Signed in: __USER_NAME__</span>
      <a class="btn-link" href="/login?role=verifier">Switch Role</a>
      <a class="btn-link" href="/logout">Logout</a>
    </div>
  </div>

  <div class="container">
    <div class="grid-2">
      <!-- Left Column: Colony Picker + 1-Tap Check-in + Leak Report -->
      <div>
        <div class="card">
          <h2>1. Your Colony / Layout</h2>
          <label>Filter by Tehsil</label>
          <select id="tehsilSel" onchange="filterLayouts()"><option value="ALL">All Nagpur District (91)</option></select>
          <label>Search Colony / Ward</label>
          <input type="text" id="searchBox" placeholder="Type Hingna, Wanadongri, Wadi..." oninput="filterLayouts()" />
          <label>Select Location</label>
          <select id="layoutSel" onchange="refreshColony()"></select>
        </div>

        <div class="card">
          <h2>2. Daily Water Availability Check-in</h2>
          <label>Flat / Plot / House Number</label>
          <input type="text" id="unitInput" value="B-304" />
          <label>Tap Today's Water Supply Status:</label>
          <div class="grid-3" style="margin-bottom:10px;">
            <button class="success" onclick="sendCheckin('NORMAL')">🟢 Normal</button>
            <button style="border-color:var(--yellow); color:#fcd34d;" onclick="sendCheckin('LOW_PRESSURE')">🟡 Low Pressure</button>
            <button class="danger" onclick="sendCheckin('BOREWELL_DRY')">🔴 No Water / Dry</button>
          </div>
          <div class="avail-bar">
            <div id="barN" style="background:var(--green); width:70%;"></div>
            <div id="barL" style="background:var(--yellow); width:15%;"></div>
            <div id="barD" style="background:var(--red); width:15%;"></div>
          </div>
          <div id="crowdSummaryText" style="font-size:11px; color:var(--muted);"></div>
        </div>

        <div class="card">
          <h2>3. Report Pipeline Leak / Pump Fault</h2>
          <label>Issue Type</label>
          <select id="leakType">
            <option>Leaking pipeline</option>
            <option>Overflowing storage tank</option>
            <option>Public tap wastage</option>
            <option>Submersible pump fault</option>
            <option>Broken RWH unit</option>
          </select>
          <label>Severity</label>
          <select id="leakSev">
            <option>Minor</option>
            <option selected>Moderate</option>
            <option>Severe</option>
          </select>
          <label>Location Landmark & Details</label>
          <textarea id="leakDesc" rows="2" placeholder="e.g. Near Lane 3 corner valve leaking since morning"></textarea>
          <button class="primary" style="width:100%;" onclick="submitTicket()">Submit Utility Ticket</button>
        </div>
      </div>

      <!-- Right Column: Supply Status + Live Tanker Map & Confirmation + RWH Calculator -->
      <div>
        <div id="statusBanner" class="banner GREEN">
          <div id="bannerTitle" style="font-size:18px; font-weight:800; margin-bottom:4px;">Loading...</div>
          <div id="bannerDesc" style="font-size:13px;"></div>
        </div>

        <div class="grid-3" style="margin-bottom:18px;">
          <div class="metric">
            <small>Borewell Pump Runway</small>
            <strong id="mRunway">--</strong>
            <span id="mRunwaySub">--</span>
          </div>
          <div class="metric">
            <small>Colony Dry Reports</small>
            <strong id="mDryPct">--%</strong>
            <span id="mDryCount">-- homes</span>
          </div>
          <div class="metric">
            <small>Live 48h Rainfall</small>
            <strong id="mRain">-- mm</strong>
            <span id="mRainSrc">Open-Meteo</span>
          </div>
        </div>

        <div class="card">
          <h2>
            <span>4. Live Tanker Tracker & Delivery Confirmation</span>
            <span class="pill blue" id="tankerCountPill">0 Active</span>
          </h2>
          <div id="citizenMap" class="map-box" style="margin-bottom:12px;"></div>
          <div id="tankerOrdersList"></div>
        </div>

        <div class="card">
          <h2>
            <span>5. Rainwater Harvesting (RWH) Calculator & Checklist</span>
            <select id="rwhLang" style="width:auto; margin:0;" onchange="renderRwhChecklist()">
              <option value="en">English</option>
              <option value="hi">हिंदी</option>
              <option value="mr">मराठी</option>
            </select>
          </h2>
          <div class="grid-3">
            <div>
              <label>Nagpur Taluka (14)</label>
              <select id="rwhTaluka" onchange="calcRwh()"></select>
            </div>
            <div>
              <label>Roof Area</label>
              <div style="display:flex; gap:6px;">
                <input type="number" id="rwhArea" value="1200" min="0" oninput="calcRwh()" />
                <select id="rwhUnit" style="width:95px;" onchange="calcRwh()">
                  <option value="sqft">Sq.Ft</option>
                  <option value="sqm">Sq.M</option>
                </select>
              </div>
            </div>
            <div>
              <label>Roof Surface</label>
              <select id="rwhSurface" onchange="calcRwh()">
                <option value="concrete">Concrete / RCC (0.85)</option>
                <option value="metal">Metal / GI Sheet (0.90)</option>
                <option value="tiled">Tiled / Sloped (0.75)</option>
              </select>
            </div>
          </div>
          <div class="grid-3" style="margin-bottom:12px;">
            <div class="metric"><small>Gross Captured</small><strong id="rwhGross">0 L</strong><span>Annual potential</span></div>
            <div class="metric"><small>First-Flush Diverted</small><strong id="rwhFlush">0 L</strong><span>0.8 L/m² × rainy days</span></div>
            <div class="metric"><small>Net Effective Harvest</small><strong id="rwhNet" style="color:#34d399;">0 L</strong><span>Clean recharge/storage</span></div>
          </div>
          <div id="rwhChecklistBox"></div>
        </div>

        <div class="card">
          <h2>6. Colony Leak & Fault Tickets</h2>
          <div id="citizenTicketsList"></div>
        </div>
      </div>
    </div>
  </div>

  {MAP_HELPER_JS}
  <script>
    const ALL_LAYOUTS = __LAYOUTS_JSON__;
    const TALUKAS = __TALUKAS_JSON__;
    const DEPOTS = __DEPOTS_JSON__;

    const RWH_RULES = {{
      en: [
        "Sweep terrace & clear drain outlets before monsoon",
        "Divert first rain & dry-spell flush before recharge",
        "Keep terrace free of detergents & chemical cleaners",
        "Inspect filter mesh, sand/gravel media & recharge pit lid"
      ],
      hi: [
        "मानसून से पहले छत और नालियों की सफाई करें",
        "पहली बारिश और सूखे अंतराल का फर्स्ट-फ्लश बाहर निकालें",
        "छत को डिटर्जेंट और रसायनों से मुक्त रखें",
        "फिल्टर जाली, रेत/बजरी परत और पिट ढक्कन की जांच करें"
      ],
      mr: [
        "पावसाळ्यापूर्वी छत आणि पाण्याचे निचरे स्वच्छ करा",
        "पहिल्या पावसाचा व कोरड्या काळानंतरचा फर्स्ट-फ्लश बाहेर सोडा",
        "छत डिटर्जंट आणि रसायनांपासून मुक्त ठेवा",
        "फिल्टर जाळी, वाळू/खडीचा थर आणि पिट झाकण तपासा"
      ]
    }};

    let map = null;
    let mapLayers = null;

    function initSelectors() {{
      const tehsils = Array.from(new Set(ALL_LAYOUTS.map(x => x.tehsil))).sort();
      const tSel = document.getElementById('tehsilSel');
      tehsils.forEach(t => {{
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = `Tehsil: ${{t}}`;
        tSel.appendChild(opt);
      }});

      const rSel = document.getElementById('rwhTaluka');
      TALUKAS.forEach(t => {{
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = `${{t.name}} (${{t.rainfall_mm}} mm)`;
        rSel.appendChild(opt);
      }});
      rSel.value = 'hingna';

      filterLayouts('wanadongri');
    }}

    function filterLayouts(preferId = null) {{
      const tehsil = document.getElementById('tehsilSel').value;
      const q = document.getElementById('searchBox').value.trim().toLowerCase();
      const sel = document.getElementById('layoutSel');
      const cur = preferId || sel.value;

      const list = ALL_LAYOUTS.filter(l => {{
        if (tehsil !== 'ALL' && l.tehsil !== tehsil) return false;
        if (q && !l.name.toLowerCase().includes(q)) return false;
        return true;
      }});
      sel.innerHTML = list.map(l => `<option value="${{l.id}}">${{l.category === 'Featured Pilot' ? '★ ' : ''}}${{l.name}}</option>`).join('');
      if (list.some(l => l.id === cur)) sel.value = cur;
      if (list.length) refreshColony();
    }}

    async function refreshColony() {{
      const id = document.getElementById('layoutSel').value;
      const res = await fetch(`/api/colony?id=${{encodeURIComponent(id)}}`);
      const data = await res.json();
      const ev = data.evaluation;
      const l = data.layout;
      const c = data.crowd.counts;

      const banner = document.getElementById('statusBanner');
      banner.className = 'banner ' + ev.scarcity_status;
      document.getElementById('bannerTitle').textContent = `${{ev.scarcity_status}} SUPPLY STATUS — ${{l.name}}`;
      document.getElementById('bannerDesc').textContent = ev.diagnosis;

      const pr = ev.groundwater_summary.pump_runway;
      document.getElementById('mRunway').textContent = pr.days !== null ? `${{pr.days}} days` : 'Stable';
      document.getElementById('mRunwaySub').textContent = pr.label;
      document.getElementById('mDryPct').textContent = `${{ev.signals.signal_3_community_shortage.dry_percentage}}%`;
      document.getElementById('mDryCount').textContent = `${{c.BOREWELL_DRY || 0}} of ${{l.total_households}} homes`;
      document.getElementById('mRain').textContent = `${{ev.raw_stage1.rain_48h_mm}} mm`;
      document.getElementById('mRainSrc').textContent = ev.raw_stage1.rainfall_source;
      document.getElementById('rainBadge').textContent = `48h Rain: ${{ev.raw_stage1.rain_48h_mm}} mm`;

      const total = Math.max(l.total_households, (c.NORMAL||0) + (c.LOW_PRESSURE||0) + (c.BOREWELL_DRY||0), 1);
      document.getElementById('barN').style.width = ((c.NORMAL||0)/total*100).toFixed(1) + '%';
      document.getElementById('barL').style.width = ((c.LOW_PRESSURE||0)/total*100).toFixed(1) + '%';
      document.getElementById('barD').style.width = ((c.BOREWELL_DRY||0)/total*100).toFixed(1) + '%';
      document.getElementById('crowdSummaryText').textContent =
        `Normal: ${{c.NORMAL||0}} · Low Pressure: ${{c.LOW_PRESSURE||0}} · Borewell Dry: ${{c.BOREWELL_DRY||0}}`;

      renderTankerMapAndOrders(l, data.tanker_orders || []);
      renderTickets(data.tickets || []);
      renderRwhChecklist(data.rwh_checks || {{}});
      calcRwh();
    }}

    function renderTankerMapAndOrders(layout, orders) {{
      if (!map) {{
        map = createNagpurMap('citizenMap', [layout.lat, layout.lon], 12);
        if (map) mapLayers = L.layerGroup().addTo(map);
      }}
      if (map && mapLayers) {{
        mapLayers.clearLayers();
        L.circleMarker([layout.lat, layout.lon], {{ radius: 9, color: '#38bdf8', fillColor: '#38bdf8', fillOpacity: 0.85 }})
          .bindPopup(`<b>${{layout.name}}</b><br>Your Colony`).addTo(mapLayers);

        DEPOTS.forEach(d => {{
          L.marker([d.lat, d.lon]).bindPopup(`<b>${{d.name}}</b><br>Tanker Depot`).addTo(mapLayers);
        }});

        orders.forEach(o => {{
          const dep = DEPOTS.find(d => d.id === o.depot_id);
          if (dep && (o.status === 'DISPATCHED' || o.status === 'UNLOADED')) {{
            const line = L.polyline([[dep.lat, dep.lon], [layout.lat, layout.lon]], {{
              color: '#34d399', weight: 4, dashArray: '8, 8'
            }}).addTo(mapLayers);
            const midLat = (dep.lat + layout.lat) / 2;
            const midLon = (dep.lon + layout.lon) / 2;
            L.circleMarker([midLat, midLon], {{ radius: 7, color: '#f59e0b', fillColor: '#f59e0b', fillOpacity: 1 }})
              .bindPopup(`<b>🚛 ${{o.vehicle_no}}</b><br>${{o.volume_l.toLocaleString()}} L (${{o.status}})`).addTo(mapLayers);
            map.fitBounds(line.getBounds(), {{ padding: [40, 40] }});
          }}
        }});
        if (!orders.some(o => o.status === 'DISPATCHED' || o.status === 'UNLOADED')) {{
          map.setView([layout.lat, layout.lon], 13);
        }}
      }}

      document.getElementById('tankerCountPill').textContent = `${{orders.length}} Orders`;
      const box = document.getElementById('tankerOrdersList');
      if (!orders.length) {{
        box.innerHTML = `<div style="font-size:12px; color:var(--muted);">No active tanker orders for this colony yet.</div>`;
        return;
      }}
      box.innerHTML = orders.map(o => `
        <div class="list-item">
          <div>
            <b>${{o.id}} · ${{o.volume_l.toLocaleString()}} L</b> (${{o.vehicle_no || 'Awaiting Dispatch'}})<br>
            <span style="color:var(--muted);">From: ${{o.depot_name || 'Pending assignment'}} · ${{o.distance_km || '--'}} km</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="status-tag ${{o.status}}">${{o.status}}</span>
            ${{(o.status === 'DISPATCHED' || o.status === 'UNLOADED') ? `<button class="success" onclick="confirmDelivery('${{o.id}}')">Confirm Water Received</button>` : ''}}
          </div>
        </div>
      `).join('');
    }}

    function renderTickets(tickets) {{
      const box = document.getElementById('citizenTicketsList');
      if (!tickets.length) {{
        box.innerHTML = `<div style="font-size:12px; color:var(--muted);">No open leak or pump tickets in this colony.</div>`;
        return;
      }}
      box.innerHTML = tickets.map(t => `
        <div class="list-item">
          <div><b>#${{t.id}} · ${{t.issue_type}}</b> (${{t.severity}})<br><span style="color:var(--muted);">${{t.description}} · ${{t.created_at}}</span></div>
          <span class="status-tag ${{t.status}}">${{t.status}}</span>
        </div>
      `).join('');
    }}

    let savedChecks = {{}};
    function renderRwhChecklist(checksObj = null) {{
      if (checksObj) savedChecks = checksObj;
      const lang = document.getElementById('rwhLang').value;
      const rules = RWH_RULES[lang] || RWH_RULES.en;
      document.getElementById('rwhChecklistBox').innerHTML = rules.map((txt, idx) => {{
        const key = 'r_' + idx;
        const checked = !!savedChecks[key];
        return `<label style="display:flex; align-items:center; gap:8px; margin-bottom:6px; cursor:pointer; color:var(--text);">
          <input type="checkbox" style="width:auto; margin:0;" ${{checked ? 'checked' : ''}} onchange="toggleRwhCheck('${{key}}', this.checked)" />
          <span>${{txt}}</span>
        </label>`;
      }}).join('');
    }}

    async function toggleRwhCheck(key, val) {{
      savedChecks[key] = val;
      await fetch('/api/rwh-check', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ layout_id: document.getElementById('layoutSel').value, key, checked: val }})
      }});
    }}

    async function calcRwh() {{
      const res = await fetch('/api/rwh-calc', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          taluka_id: document.getElementById('rwhTaluka').value,
          area: parseFloat(document.getElementById('rwhArea').value) || 0,
          unit: document.getElementById('rwhUnit').value,
          surface_id: document.getElementById('rwhSurface').value
        }})
      }});
      const r = await res.json();
      document.getElementById('rwhGross').textContent = r.gross_l.toLocaleString('en-IN') + ' L';
      document.getElementById('rwhFlush').textContent = r.first_flush_l.toLocaleString('en-IN') + ' L';
      document.getElementById('rwhNet').textContent = r.net_l.toLocaleString('en-IN') + ' L';
    }}

    async function sendCheckin(status) {{
      await fetch('/api/checkin', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          layout_id: document.getElementById('layoutSel').value,
          unit: document.getElementById('unitInput').value.trim() || 'Resident',
          status
        }})
      }});
      refreshColony();
    }}

    async function submitTicket() {{
      const desc = document.getElementById('leakDesc').value.trim();
      if (!desc) return alert('Please describe the leak or fault location.');
      await fetch('/api/ticket', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          layout_id: document.getElementById('layoutSel').value,
          issue_type: document.getElementById('leakType').value,
          severity: document.getElementById('leakSev').value,
          description: desc
        }})
      }});
      document.getElementById('leakDesc').value = '';
      refreshColony();
    }}

    async function confirmDelivery(orderId) {{
      await fetch('/api/tanker-status', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ order_id: orderId, status: 'CONFIRMED' }})
      }});
      refreshColony();
    }}

    initSelectors();
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# PAGE 2: FIELD VERIFIER PORTAL (/verifier)
# ---------------------------------------------------------------------------
VERIFIER_HTML = rf"""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Field Verifier Portal — Nagpur Water Network</title>
  {SHARED_HEAD}
</head>
<body>
  <div class="topbar">
    <div class="brand">Field Verifier Portal <span class="pill green" id="rainBadge">48h Rain: -- mm</span></div>
    <div class="nav-actions">
      <span class="pill blue">Signed in: __USER_NAME__</span>
      <a class="btn-link" href="/login?role=utility">Switch Role</a>
      <a class="btn-link" href="/logout">Logout</a>
    </div>
  </div>

  <div class="container">
    <div class="grid-2">
      <!-- Left: Colony Selector + Well Depth Entry + Verified Tanker Indent -->
      <div>
        <div class="card">
          <h2>1. Assigned Colony / Ward</h2>
          <label>Search Nagpur Location (91)</label>
          <input type="text" id="searchBox" placeholder="Search Hingna, Wanadongri, Ramdaspeth..." oninput="filterLayouts()" />
          <select id="layoutSel" onchange="refreshVerifier()"></select>
        </div>

        <div class="card">
          <h2>2. Log Reference Well Depth (Anti-Cheat Checked)</h2>
          <label>Today's Measured Well Depth (m bgl)</label>
          <input type="number" id="vDepth" step="0.1" min="0.5" max="80" />
          <div class="grid-even">
            <div>
              <label>Previous Recorded Depth (m)</label>
              <input type="number" id="vLastDepth" step="0.1" min="0.5" max="80" />
            </div>
            <div>
              <label>Days Since Last Record</label>
              <select id="vDays">
                <option value="7">7 days (Weekly)</option>
                <option value="14">14 days (Fortnightly)</option>
                <option value="30">30 days (Monthly)</option>
              </select>
            </div>
          </div>
          <div id="valBox" style="font-size:12px; padding:9px; border-radius:8px; background:var(--panel2); border:1px solid var(--border); margin-bottom:10px;">
            Validation: Pending
          </div>
          <button class="primary" style="width:100%;" onclick="saveVerifierReading()">Verify & Update Calibration</button>
        </div>

        <div class="card">
          <h2>3. Submit Verified Tanker Indent (55 LPCD Norm)</h2>
          <p style="font-size:12px; color:var(--muted); margin-bottom:10px;">
            Only Field Verifiers can raise official tanker indents to prevent unverified resident spam.
          </p>
          <div id="indentCalcText" style="font-size:12px; color:#7dd3fc; margin-bottom:10px;"></div>
          <label>Indent Volume (Litres)</label>
          <select id="indentVol">
            <option value="10000">10,000 L (1 Tanker Trip)</option>
            <option value="20000">20,000 L (2 Tanker Trips)</option>
            <option value="30000">30,000 L (3 Tanker Trips)</option>
          </select>
          <button class="success" style="width:100%;" onclick="submitIndent()">Send Verified Indent to Utility Desk</button>
        </div>
      </div>

      <!-- Right: Calibrated Depth + 3 Signals + 7-Day 6-Hourly Hydrograph + Society RWH Roles -->
      <div>
        <div id="statusBanner" class="banner YELLOW">
          <div id="bannerTitle" style="font-size:18px; font-weight:800; margin-bottom:4px;">Loading...</div>
          <div id="bannerDesc" style="font-size:13px;"></div>
        </div>

        <div class="grid-3" style="margin-bottom:18px;">
          <div class="metric">
            <small>Live Calibrated Depth</small>
            <strong id="mCalDepth">-- m</strong>
            <span id="mOffset">Offset vs CGWB</span>
          </div>
          <div class="metric">
            <small>Depletion Velocity</small>
            <strong id="mVel">-- m/wk</strong>
            <span id="mDeficit">True Deficit: -- m</span>
          </div>
          <div class="metric">
            <small>Pump Runway</small>
            <strong id="mRunway">-- days</strong>
            <span id="mRunwayLbl">--</span>
          </div>
        </div>

        <div class="card">
          <h2>4. 3-Signal Scarcity & Fault Diagnostic</h2>
          <div id="signalsBox"></div>
        </div>

        <div class="card">
          <h2>
            <span>5. 7-Day 6-Hourly Calibrated Hydrograph</span>
            <span id="stationSpan" style="font-size:11px; color:var(--accent);">--</span>
          </h2>
          <svg id="hydroSvg" viewBox="0 0 600 185" style="width:100%; height:195px; background:var(--panel2); border-radius:8px; border:1px solid var(--border);"></svg>
          <div style="font-size:11px; color:var(--muted); margin-top:6px; text-align:center;">
            Blue: Raw CGWB 6-Hourly Sensor · Red: Offset-Calibrated Colony Depth
          </div>
        </div>

        <div class="card">
          <h2>
            <span>6. Housing Society RWH Audit (Role Guidelines)</span>
            <select id="socRoleSel" style="width:auto; margin:0;" onchange="renderSocietyAudit()">
              <option value="residents">Residents</option>
              <option value="plumber">Plumber & Guard</option>
              <option value="secretary">Secretary / Leader</option>
            </select>
          </h2>
          <div id="socAuditBox"></div>
        </div>
      </div>
    </div>
  </div>

  <script>
    const ALL_LAYOUTS = __LAYOUTS_JSON__;
    const SOC_GUIDELINES = {{
      residents: [
        "Keep shared terraces & outlets free of plastic wrappers and chemical cleaners",
        "Report terrace waterlogging or recharge overflow promptly",
        "Alert staff before heavy showers following dry spells for first-flush diversion"
      ],
      plumber: [
        "Clean roof gutters, leaf strainers & silt traps pre-monsoon",
        "Operate first-flush diversion valves & verify recharge pit percolation",
        "Inspect filter media beds & secure chamber covers post-monsoon"
      ],
      secretary: [
        "Sanction pre-monsoon desilting & upkeep materials ahead of June",
        "Audit maintenance logs & resident overflow alerts",
        "Maintain annual RWH compliance records for municipal inspection"
      ]
    }};

    function filterLayouts(preferId = 'wanadongri') {{
      const q = document.getElementById('searchBox').value.trim().toLowerCase();
      const sel = document.getElementById('layoutSel');
      const cur = preferId || sel.value;
      const list = ALL_LAYOUTS.filter(l => !q || l.name.toLowerCase().includes(q) || l.tehsil.toLowerCase().includes(q));
      sel.innerHTML = list.map(l => `<option value="${{l.id}}">${{l.category === 'Featured Pilot' ? '★ ' : ''}}${{l.name}}</option>`).join('');
      if (list.some(l => l.id === cur)) sel.value = cur;
      if (list.length) refreshVerifier();
    }}

    async function refreshVerifier() {{
      const id = document.getElementById('layoutSel').value;
      const res = await fetch(`/api/colony?id=${{encodeURIComponent(id)}}`);
      const data = await res.json();
      const ev = data.evaluation;
      const vr = data.verifier_record;

      document.getElementById('vDepth').value = vr.verifier_depth_m;
      document.getElementById('vLastDepth').value = vr.last_recorded_depth_m;
      document.getElementById('vDays').value = String(vr.days_since_last || 7);

      const banner = document.getElementById('statusBanner');
      banner.className = 'banner ' + ev.scarcity_status;
      document.getElementById('bannerTitle').textContent = `${{ev.scarcity_status}} — ${{data.layout.name}}`;
      document.getElementById('bannerDesc').textContent = ev.diagnosis;

      document.getElementById('rainBadge').textContent = `48h Rain: ${{ev.raw_stage1.rain_48h_mm}} mm`;
      document.getElementById('mCalDepth').textContent = `${{ev.groundwater_summary.live_calibrated_depth_m}} m`;
      const off = ev.raw_stage1.local_offset_m || 0;
      document.getElementById('mOffset').textContent = `Offset: ${{off >= 0 ? '+' : ''}}${{off}}m vs ${{ev.groundwater_summary.matched_gov_station}}`;
      document.getElementById('mVel').textContent = `${{ev.raw_stage1.depletion_velocity_m_per_week}} m/wk`;
      document.getElementById('mDeficit').textContent = `True Deficit: ${{ev.signals.signal_1_aquifer_stress.deficit_m}} m`;

      const pr = ev.groundwater_summary.pump_runway;
      document.getElementById('mRunway').textContent = pr.days !== null ? `${{pr.days}} days` : 'Stable';
      document.getElementById('mRunwayLbl').textContent = pr.label;

      const vv = ev.groundwater_summary.verifier_validation;
      if (vv) {{
        const vb = document.getElementById('valBox');
        vb.textContent = `Validation: ${{vv.status}} — ${{vv.reason}}`;
        vb.style.borderColor = vv.status === 'VERIFIED' ? 'var(--green)' : 'var(--red)';
        vb.style.color = vv.status === 'VERIFIED' ? '#6ee7b7' : '#fca5a5';
      }}

      const rec = data.recommended_tanker;
      document.getElementById('indentCalcText').textContent =
        `Recommended Indent: ${{rec.litres_per_day.toLocaleString()}} L/day (${{rec.trips_10k}} × 10,000L tankers) for ${{rec.affected_homes}} affected households @ 55 LPCD.`;

      const s1 = ev.signals.signal_1_aquifer_stress;
      const s2 = ev.signals.signal_2_rapid_depletion;
      const s3 = ev.signals.signal_3_community_shortage;
      document.getElementById('signalsBox').innerHTML = [
        {{ title: 'Signal 1: Aquifer Stress (>2.5m Deficit or ≤1.5m Col)', active: s1.active, info: `Deficit: ${{s1.deficit_m}} m` }},
        {{ title: 'Signal 2: Rapid Depletion (>0.5m/week)', active: s2.active, info: `Rate: ${{s2.velocity_m_per_week}} m/wk` }},
        {{ title: 'Signal 3: Resident Shortage (≥30% Dry Homes)', active: s3.active, info: `Dry: ${{s3.dry_percentage}}% (${{ev.crowd_summary.dry_reports_count}} homes)` }}
      ].map(s => `
        <div class="list-item" style="border-color:${{s.active ? 'var(--red)' : 'var(--border)'}};">
          <span>${{s.active ? '⚠️' : '✓'}} <b>${{s.title}}</b></span>
          <span class="status-tag ${{s.active ? 'RED' : 'GREEN'}}">${{s.info}}</span>
        </div>
      `).join('');

      document.getElementById('stationSpan').textContent =
        `Nearest CGWB: ${{ev.groundwater_summary.matched_gov_station}} (${{ev.groundwater_summary.station_distance_km}} km)`;
      drawHydrograph(ev.raw_stage1.calibrated_series || []);
      renderSocietyAudit();
    }}

    function drawHydrograph(series) {{
      const svg = document.getElementById('hydroSvg');
      svg.innerHTML = '';
      if (series.length < 2) return;
      const w = 600, h = 185, padL = 42, padR = 16, padT = 18, padB = 26;
      const all = series.map(p => p.gov_depth_m).concat(series.map(p => p.calibrated_layout_depth_m));
      const minD = Math.floor(Math.min(...all) - 0.5);
      const maxD = Math.ceil(Math.max(...all) + 0.5);
      const xS = i => padL + (i / (series.length - 1)) * (w - padL - padR);
      const yS = d => padT + ((d - minD) / Math.max(maxD - minD, 0.5)) * (h - padT - padB);

      const mkPath = key => series.map((p, i) => `${{i===0?'M':'L'}} ${{xS(i).toFixed(1)}} ${{yS(p[key]).toFixed(1)}}`).join(' ');
      const p1 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p1.setAttribute('d', mkPath('gov_depth_m')); p1.setAttribute('fill', 'none'); p1.setAttribute('stroke', '#38bdf8'); p1.setAttribute('stroke-width', '2');
      svg.appendChild(p1);

      const p2 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      p2.setAttribute('d', mkPath('calibrated_layout_depth_m')); p2.setAttribute('fill', 'none'); p2.setAttribute('stroke', '#ef4444'); p2.setAttribute('stroke-width', '2.5');
      svg.appendChild(p2);
    }}

    function renderSocietyAudit() {{
      const role = document.getElementById('socRoleSel').value;
      const list = SOC_GUIDELINES[role] || [];
      document.getElementById('socAuditBox').innerHTML = list.map(item => `
        <label style="display:flex; align-items:center; gap:8px; margin-bottom:6px; cursor:pointer; color:var(--text);">
          <input type="checkbox" style="width:auto; margin:0;" />
          <span>${{item}}</span>
        </label>
      `).join('');
    }}

    async function saveVerifierReading() {{
      await fetch('/api/verifier-update', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          layout_id: document.getElementById('layoutSel').value,
          verifier_depth_m: parseFloat(document.getElementById('vDepth').value),
          last_recorded_depth_m: parseFloat(document.getElementById('vLastDepth').value),
          days_since_last: parseInt(document.getElementById('vDays').value)
        }})
      }});
      refreshVerifier();
    }}

    async function submitIndent() {{
      const res = await fetch('/api/tanker-indent', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          layout_id: document.getElementById('layoutSel').value,
          volume_l: parseInt(document.getElementById('indentVol').value)
        }})
      }});
      const d = await res.json();
      alert(`Verified Tanker Indent ${{d.order.id}} queued for Utility Dispatch!`);
    }}

    filterLayouts('wanadongri');
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# PAGE 3: UTILITY & TANKER PORTAL (/utility)
# ---------------------------------------------------------------------------
UTILITY_HTML = rf"""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Utility & Tanker Operations Portal — Nagpur Water Network</title>
  {SHARED_HEAD}
</head>
<body>
  <div class="topbar">
    <div class="brand">Utility & Tanker Operations Console <span class="pill blue" id="fleetPill">Fleet: --</span></div>
    <div class="nav-actions">
      <span class="pill green">Signed in: __USER_NAME__</span>
      <a class="btn-link" href="/login?role=citizen">Switch Role</a>
      <a class="btn-link" href="/logout">Logout</a>
    </div>
  </div>

  <div class="container">
    <div class="grid-2">
      <!-- Left: Dispatch Console + Depot Stock + Leak Ticket Queue -->
      <div>
        <div class="card">
          <h2>1. Tanker Dispatch Console (Nearest-Depot Auto-Routing)</h2>
          <label>Destination Colony / Verified Indent</label>
          <select id="dispLayoutSel"></select>
          <label>Source Depot (Leave Auto for Nearest with Stock)</label>
          <select id="dispDepotSel">
            <option value="AUTO">Auto-Select Nearest Depot with Stock</option>
          </select>
          <label>Tanker Capacity</label>
          <select id="dispVolSel">
            <option value="5000">5,000 L Tanker</option>
            <option value="10000" selected>10,000 L Tanker</option>
            <option value="15000">15,000 L Tanker</option>
          </select>
          <button class="primary" style="width:100%;" onclick="dispatchNow()">Assign & Dispatch Tanker</button>
        </div>

        <div class="card">
          <h2>2. Nagpur Tanker Depots & Fleet Stock</h2>
          <div id="depotsBox"></div>
        </div>

        <div class="card">
          <h2>3. Field Leak & Fault Ticket Queue</h2>
          <div id="utilityTicketsBox"></div>
        </div>
      </div>

      <!-- Right: Nagpur Scarcity & Fleet Map + Verified Indents & Active Tankers + Priority Scarcity Table -->
      <div>
        <div class="card">
          <h2>
            <span>4. Nagpur Scarcity & Live Tanker Route Map</span>
            <span style="font-size:11px; color:var(--muted);">Red/Yellow/Green Colonies · 🚛 Depots · Dashed Routes</span>
          </h2>
          <div id="utilityMap" class="map-box"></div>
        </div>

        <div class="card">
          <h2>5. Verified Tanker Indents & Active Deliveries</h2>
          <div id="utilityOrdersBox"></div>
        </div>

        <div class="card">
          <h2>6. Priority Scarcity Triage Table (Featured & Stressed Colonies)</h2>
          <table>
            <thead>
              <tr>
                <th>Colony</th>
                <th>Calibrated Depth</th>
                <th>Pump Runway</th>
                <th>Dry %</th>
                <th>48h Rain</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody id="priorityTbody"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  {MAP_HELPER_JS}
  <script>
    let map = null;
    let mapLayers = null;

    async function loadUtilityOverview() {{
      const res = await fetch('/api/utility-overview');
      const data = await res.json();

      // Populate destination selector
      const lSel = document.getElementById('dispLayoutSel');
      const prevL = lSel.value;
      lSel.innerHTML = data.priority_colonies.map(c =>
        `<option value="${{c.layout.id}}">${{c.layout.name}} [${{c.evaluation.scarcity_status}} · Runway ${{c.evaluation.groundwater_summary.pump_runway.days ?? 'Stable'}}d]</option>`
      ).join('');
      if (prevL) lSel.value = prevL;

      // Depots
      const dSel = document.getElementById('dispDepotSel');
      const prevD = dSel.value;
      dSel.innerHTML = `<option value="AUTO">Auto-Select Nearest Depot with Stock</option>` +
        data.depots.map(d => `<option value="${{d.id}}">${{d.name}} (${{d.current_stock_l.toLocaleString()}} L · ${{d.trucks_ready}} trucks)</option>`).join('');
      if (prevD) dSel.value = prevD;

      let ready = 0, total = 0;
      document.getElementById('depotsBox').innerHTML = data.depots.map(d => {{
        ready += d.trucks_ready; total += d.trucks_total;
        return `<div class="list-item">
          <div><b>${{d.name}}</b><br><span style="color:var(--muted);">Stock: ${{d.current_stock_l.toLocaleString()}} / ${{d.max_capacity_l.toLocaleString()}} L · Ready Trucks: ${{d.trucks_ready}}/${{d.trucks_total}}</span></div>
          <button onclick="refillDepot('${{d.id}}')">+ Refill</button>
        </div>`;
      }}).join('');
      document.getElementById('fleetPill').textContent = `Fleet Ready: ${{ready}}/${{total}}`;

      // Orders
      document.getElementById('utilityOrdersBox').innerHTML = data.tanker_orders.map(o => `
        <div class="list-item">
          <div>
            <b>${{o.id}} · ${{o.layout_name}}</b> (${{o.volume_l.toLocaleString()}} L)<br>
            <span style="color:var(--muted);">Verified by ${{o.verified_by}} · ${{o.vehicle_no || 'Pending Truck'}} (${{o.depot_name || 'Unassigned'}})</span>
          </div>
          <div style="display:flex; gap:6px; align-items:center;">
            <span class="status-tag ${{o.status}}">${{o.status}}</span>
            ${{o.status === 'PENDING_DISPATCH' ? `<button class="primary" onclick="dispatchOrder('${{o.id}}')">Dispatch</button>` : ''}}
            ${{o.status === 'DISPATCHED' ? `<button class="success" onclick="markUnloaded('${{o.id}}')">Mark Unloaded</button>` : ''}}
          </div>
        </div>
      `).join('');

      // Tickets
      document.getElementById('utilityTicketsBox').innerHTML = data.tickets.map(t => `
        <div class="list-item">
          <div><b>#${{t.id}} · ${{t.issue_type}}</b> @ ${{t.layout_name}}<br><span style="color:var(--muted);">${{t.description}}</span></div>
          <div style="display:flex; gap:6px; align-items:center;">
            <span class="status-tag ${{t.status}}">${{t.status}}</span>
            ${{t.status !== 'RESOLVED' ? `<button class="success" onclick="resolveTicket('${{t.id}}')">Resolve</button>` : ''}}
          </div>
        </div>
      `).join('');

      // Priority table & Map
      if (!map) {{
        map = createNagpurMap('utilityMap', [21.125, 79.025], 11);
        if (map) mapLayers = L.layerGroup().addTo(map);
      }}
      if (mapLayers) mapLayers.clearLayers();

      document.getElementById('priorityTbody').innerHTML = data.priority_colonies.map(c => {{
        const ev = c.evaluation;
        const st = ev.scarcity_status;
        const col = st === 'RED' ? '#ef4444' : (st === 'YELLOW' ? '#f59e0b' : '#10b981');
        if (mapLayers) {{
          L.circleMarker([c.layout.lat, c.layout.lon], {{ radius: 8, color: col, fillColor: col, fillOpacity: 0.85 }})
            .bindPopup(`<b>${{c.layout.name}}</b><br>Status: ${{st}}<br>Depth: ${{ev.groundwater_summary.live_calibrated_depth_m}} m`).addTo(mapLayers);
        }}
        return `<tr>
          <td><b>${{c.layout.name}}</b></td>
          <td>${{ev.groundwater_summary.live_calibrated_depth_m}} m</td>
          <td>${{ev.groundwater_summary.pump_runway.days ?? 'Stable'}} d</td>
          <td>${{ev.signals.signal_3_community_shortage.dry_percentage}}%</td>
          <td>${{ev.raw_stage1.rain_48h_mm}} mm</td>
          <td><span class="status-tag ${{st}}">${{st}}</span></td>
        </tr>`;
      }}).join('');

      if (mapLayers) {{
        data.depots.forEach(d => {{
          L.marker([d.lat, d.lon]).bindPopup(`<b>🚛 ${{d.name}}</b><br>Stock: ${{d.current_stock_l.toLocaleString()}} L`).addTo(mapLayers);
        }});
        data.tanker_orders.forEach(o => {{
          if (o.status === 'DISPATCHED' || o.status === 'UNLOADED') {{
            const dep = data.depots.find(d => d.id === o.depot_id);
            const dest = data.priority_colonies.find(c => c.layout.id === o.layout_id);
            if (dep && dest) {{
              L.polyline([[dep.lat, dep.lon], [dest.layout.lat, dest.layout.lon]], {{
                color: '#38bdf8', weight: 3, dashArray: '7, 7'
              }}).addTo(mapLayers);
            }}
          }}
        }});
      }}
    }}

    async function dispatchNow() {{
      const res = await fetch('/api/tanker-dispatch', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          layout_id: document.getElementById('dispLayoutSel').value,
          depot_id: document.getElementById('dispDepotSel').value,
          volume_l: parseInt(document.getElementById('dispVolSel').value)
        }})
      }});
      const d = await res.json();
      if (!res.ok) return alert(d.error || 'Dispatch failed');
      loadUtilityOverview();
    }}

    async function dispatchOrder(orderId) {{
      const res = await fetch('/api/tanker-dispatch', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ order_id: orderId, depot_id: 'AUTO' }})
      }});
      const d = await res.json();
      if (!res.ok) return alert(d.error || 'Dispatch failed');
      loadUtilityOverview();
    }}

    async function markUnloaded(orderId) {{
      await fetch('/api/tanker-status', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ order_id: orderId, status: 'UNLOADED' }})
      }});
      loadUtilityOverview();
    }}

    async function refillDepot(depotId) {{
      await fetch('/api/depot-refill', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ depot_id: depotId }})
      }});
      loadUtilityOverview();
    }}

    async function resolveTicket(ticketId) {{
      await fetch('/api/ticket-resolve', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ ticket_id: ticketId }})
      }});
      loadUtilityOverview();
    }}

    loadUtilityOverview();
  </script>
</body>
</html>
"""


class UnifiedRequestHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def _get_session(self) -> dict | None:
        raw_cookie = self.headers.get("Cookie", "")
        if not raw_cookie:
            return None
        c = http.cookies.SimpleCookie()
        c.load(raw_cookie)
        morsel = c.get("nagpur_session")
        if not morsel:
            return None
        return SESSIONS.get(morsel.value)

    def _send_html(self, html: str, cookie_header: str | None = None):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _send_json(self, code: int, payload, cookie_header: str | None = None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _redirect(self, location: str, cookie_header: str | None = None):
        self.send_response(302)
        self.send_header("Location", location)
        if cookie_header:
            self.send_header("Set-Cookie", cookie_header)
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(url.query)
        sess = self._get_session()

        if url.path in ("/", "/login"):
            pre_role = (qs.get("role") or ["citizen"])[0]
            if pre_role not in ROLE_META:
                pre_role = "citizen"
            page = (
                LOGIN_HTML.replace("__ROLE_DEFAULTS_JSON__", json.dumps(ROLE_META))
                .replace("__PRESELECT_ROLE__", pre_role)
            )
            self._send_html(page)
            return

        if url.path == "/logout":
            raw_cookie = self.headers.get("Cookie", "")
            c = http.cookies.SimpleCookie()
            c.load(raw_cookie)
            if "nagpur_session" in c:
                SESSIONS.pop(c["nagpur_session"].value, None)
            self._redirect("/login", "nagpur_session=; Path=/; Max-Age=0")
            return

        if url.path == "/citizen":
            if not sess or sess["role"] != "citizen":
                self._redirect("/login?role=citizen")
                return
            page = (
                CITIZEN_HTML.replace("__USER_NAME__", sess["name"])
                .replace("__LAYOUTS_JSON__", json.dumps(ALL_LAYOUTS))
                .replace("__TALUKAS_JSON__", json.dumps(NAGPUR_TALUKAS))
                .replace("__DEPOTS_JSON__", json.dumps(STATE["depots"]))
            )
            self._send_html(page)
            return

        if url.path == "/verifier":
            if not sess or sess["role"] != "verifier":
                self._redirect("/login?role=verifier")
                return
            page = (
                VERIFIER_HTML.replace("__USER_NAME__", sess["name"])
                .replace("__LAYOUTS_JSON__", json.dumps(ALL_LAYOUTS))
            )
            self._send_html(page)
            return

        if url.path == "/utility":
            if not sess or sess["role"] != "utility":
                self._redirect("/login?role=utility")
                return
            page = UTILITY_HTML.replace("__USER_NAME__", sess["name"])
            self._send_html(page)
            return

        if url.path == "/api/colony":
            col_id = (qs.get("id") or ["wanadongri"])[0]
            if col_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown colony"})
                return
            full = evaluate_layout_full(col_id)
            full["tanker_orders"] = [o for o in STATE["tanker_orders"] if o["layout_id"] == col_id]
            full["tickets"] = [t for t in STATE["tickets"] if t["layout_id"] == col_id]
            full["rwh_checks"] = STATE["rwh_checks_by_layout"].get(col_id, {})
            self._send_json(200, full)
            return

        if url.path == "/api/utility-overview":
            # Evaluate featured pilot colonies + any colony with active orders/tickets
            ids_to_eval = [x["id"] for x in FEATURED_LAYOUTS]
            for o in STATE["tanker_orders"]:
                if o["layout_id"] not in ids_to_eval and o["layout_id"] in LAYOUT_INDEX:
                    ids_to_eval.append(o["layout_id"])
            for t in STATE["tickets"]:
                if t["layout_id"] not in ids_to_eval and t["layout_id"] in LAYOUT_INDEX:
                    ids_to_eval.append(t["layout_id"])

            priority = [evaluate_layout_full(cid) for cid in ids_to_eval]
            self._send_json(200, {
                "priority_colonies": priority,
                "depots": STATE["depots"],
                "tanker_orders": STATE["tanker_orders"],
                "tickets": STATE["tickets"],
            })
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if url.path in ("/api/login", "/api/register"):
            role = data.get("role", "citizen")
            name = str(data.get("name", "")).strip()
            password = str(data.get("password", ""))
            if role not in ROLE_META or not name or not password:
                self._send_json(400, {"error": "Name, password, and role are required."})
                return

            user_key = f"{role}:{name.lower()}"
            pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

            if url.path == "/api/register":
                STATE["users"][user_key] = {"name": name, "role": role, "pw_hash": pw_hash}
                save_unified_state(STATE)
            else:
                rec = STATE["users"].get(user_key)
                if not rec or rec["pw_hash"] != pw_hash:
                    self._send_json(401, {"error": "Invalid name or password for selected portal."})
                    return

            token = secrets.token_hex(24)
            SESSIONS[token] = {"name": name, "role": role}
            self._send_json(
                200,
                {"ok": True, "redirect": ROLE_META[role]["home"]},
                f"nagpur_session={token}; Path=/; HttpOnly",
            )
            return

        sess = self._get_session()

        if url.path == "/api/checkin":
            col_id = data.get("layout_id")
            if col_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown colony"})
                return
            status = data.get("status", "NORMAL")
            unit = str(data.get("unit", "Resident")).strip()
            crowd = get_crowd_record(col_id)
            if status in crowd["counts"]:
                crowd["counts"][status] += 1
                if status != "NORMAL" and crowd["counts"].get("NORMAL", 0) > 0:
                    crowd["counts"]["NORMAL"] -= 1
            crowd["recent_logs"].insert(0, {
                "time": datetime.now().strftime("%I:%M %p"),
                "unit": unit,
                "by": sess["name"] if sess else "Citizen",
                "status": status,
                "note": "Citizen daily check-in",
            })
            save_unified_state(STATE)
            self._send_json(200, {"ok": True})
            return

        if url.path == "/api/ticket":
            col_id = data.get("layout_id")
            if col_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown colony"})
                return
            tid = f"W{int(datetime.now().timestamp()) % 9000 + 1000}"
            STATE["tickets"].insert(0, {
                "id": tid,
                "layout_id": col_id,
                "layout_name": LAYOUT_INDEX[col_id]["name"],
                "issue_type": data.get("issue_type", "Leaking pipeline"),
                "severity": data.get("severity", "Moderate"),
                "description": str(data.get("description", "")).strip(),
                "reported_by": sess["name"] if sess else "Citizen",
                "status": "OPEN",
                "created_at": datetime.now().strftime("%I:%M %p"),
            })
            save_unified_state(STATE)
            self._send_json(200, {"ok": True, "ticket_id": tid})
            return

        if url.path == "/api/ticket-resolve":
            tid = data.get("ticket_id")
            for t in STATE["tickets"]:
                if t["id"] == tid:
                    t["status"] = "RESOLVED"
            save_unified_state(STATE)
            self._send_json(200, {"ok": True})
            return

        if url.path == "/api/rwh-check":
            col_id = data.get("layout_id")
            key = data.get("key")
            if col_id and key:
                STATE["rwh_checks_by_layout"].setdefault(col_id, {})[key] = bool(data.get("checked"))
                save_unified_state(STATE)
            self._send_json(200, {"ok": True})
            return

        if url.path == "/api/rwh-calc":
            out = calculate_rwh(
                taluka_id=data.get("taluka_id", "hingna"),
                area=float(data.get("area", 0)),
                unit=data.get("unit", "sqft"),
                surface_id=data.get("surface_id", "concrete"),
            )
            self._send_json(200, out)
            return

        if url.path == "/api/verifier-update":
            col_id = data.get("layout_id")
            if col_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown colony"})
                return
            vrec = get_verifier_record(col_id)
            vrec["verifier_depth_m"] = float(data.get("verifier_depth_m", vrec["verifier_depth_m"]))
            vrec["last_recorded_depth_m"] = float(data.get("last_recorded_depth_m", vrec["last_recorded_depth_m"]))
            vrec["days_since_last"] = int(data.get("days_since_last", 7))
            vrec["verified_by"] = sess["name"] if sess else "Verifier"
            vrec["updated_at"] = datetime.now().strftime("%I:%M %p")
            save_unified_state(STATE)
            self._send_json(200, {"ok": True})
            return

        if url.path == "/api/tanker-indent":
            col_id = data.get("layout_id")
            if col_id not in LAYOUT_INDEX:
                self._send_json(404, {"error": "Unknown colony"})
                return
            vol = int(data.get("volume_l", 10000))
            oid = f"IND-{int(datetime.now().timestamp()) % 900 + 100}"
            order = {
                "id": oid,
                "layout_id": col_id,
                "layout_name": LAYOUT_INDEX[col_id]["name"],
                "volume_l": vol,
                "trips": max(1, math.ceil(vol / 10000)),
                "lpcd_norm": 55,
                "verified_by": sess["name"] if sess else "Field Verifier",
                "status": "PENDING_DISPATCH",
                "depot_id": None,
                "depot_name": None,
                "vehicle_no": None,
                "distance_km": None,
                "created_at": datetime.now().strftime("%I:%M %p"),
                "updated_at": datetime.now().strftime("%I:%M %p"),
            }
            STATE["tanker_orders"].insert(0, order)
            save_unified_state(STATE)
            self._send_json(200, {"ok": True, "order": order})
            return

        if url.path == "/api/tanker-dispatch":
            order_id = data.get("order_id")
            depot_choice = data.get("depot_id", "AUTO")
            target_order = next((o for o in STATE["tanker_orders"] if o["id"] == order_id), None)

            if target_order is None:
                col_id = data.get("layout_id")
                if col_id not in LAYOUT_INDEX:
                    self._send_json(404, {"error": "Unknown colony"})
                    return
                vol = int(data.get("volume_l", 10000))
                target_order = {
                    "id": f"IND-{int(datetime.now().timestamp()) % 900 + 100}",
                    "layout_id": col_id,
                    "layout_name": LAYOUT_INDEX[col_id]["name"],
                    "volume_l": vol,
                    "trips": max(1, math.ceil(vol / 10000)),
                    "lpcd_norm": 55,
                    "verified_by": sess["name"] if sess else "Utility Duty Officer",
                    "status": "PENDING_DISPATCH",
                    "depot_id": None,
                    "depot_name": None,
                    "vehicle_no": None,
                    "distance_km": None,
                    "created_at": datetime.now().strftime("%I:%M %p"),
                    "updated_at": datetime.now().strftime("%I:%M %p"),
                }
                STATE["tanker_orders"].insert(0, target_order)

            dest = LAYOUT_INDEX[target_order["layout_id"]]
            vol = target_order["volume_l"]

            if depot_choice == "AUTO":
                eligible = [
                    d for d in STATE["depots"]
                    if d["current_stock_l"] >= vol and d["trucks_ready"] > 0
                ]
                eligible.sort(key=lambda d: haversine_km(dest["lat"], dest["lon"], d["lat"], d["lon"]))
                depot = eligible[0] if eligible else None
            else:
                depot = next((d for d in STATE["depots"] if d["id"] == depot_choice), None)

            if not depot or depot["current_stock_l"] < vol or depot["trucks_ready"] <= 0:
                self._send_json(400, {"error": "No depot has sufficient water stock and an idle tanker."})
                return

            depot["current_stock_l"] -= vol
            depot["trucks_ready"] -= 1
            target_order["status"] = "DISPATCHED"
            target_order["depot_id"] = depot["id"]
            target_order["depot_name"] = depot["name"]
            target_order["distance_km"] = haversine_km(dest["lat"], dest["lon"], depot["lat"], depot["lon"])
            target_order["vehicle_no"] = f"MH-31-TK-{100 + (int(datetime.now().timestamp()) % 899)}"
            target_order["updated_at"] = datetime.now().strftime("%I:%M %p")
            save_unified_state(STATE)
            self._send_json(200, {"ok": True, "order": target_order})
            return

        if url.path == "/api/tanker-status":
            order_id = data.get("order_id")
            new_status = data.get("status", "CONFIRMED")
            for o in STATE["tanker_orders"]:
                if o["id"] == order_id:
                    o["status"] = new_status
                    o["updated_at"] = datetime.now().strftime("%I:%M %p")
                    if new_status == "CONFIRMED" and o.get("depot_id"):
                        dep = next((d for d in STATE["depots"] if d["id"] == o["depot_id"]), None)
                        if dep and dep["trucks_ready"] < dep["trucks_total"]:
                            dep["trucks_ready"] += 1
            save_unified_state(STATE)
            self._send_json(200, {"ok": True})
            return

        if url.path == "/api/depot-refill":
            dep_id = data.get("depot_id")
            for d in STATE["depots"]:
                if d["id"] == dep_id:
                    d["current_stock_l"] = d["max_capacity_l"]
                    d["trucks_ready"] = d["trucks_total"]
            save_unified_state(STATE)
            self._send_json(200, {"ok": True})
            return

        self.send_response(404)
        self.end_headers()


def run_server():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), UnifiedRequestHandler)
    print("\n=======================================================")
    print(f" Nagpur Unified Multi-Role Prototype ({len(ALL_LAYOUTS)} locations)")
    print(f" Open Login Page: http://127.0.0.1:{PORT}/login")
    print(" Press Ctrl+C to stop.")
    print("=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    run_server()