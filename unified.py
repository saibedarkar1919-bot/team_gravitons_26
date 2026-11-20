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
        rain_48h_mm=None,
    )

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
# WATERMELON UI + REACT SPRING SHELL
# ---------------------------------------------------------------------------
def build_react_page(title: str, page_mode: str, bootstrap_json: str) -> str:
    html = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
 <title>__PAGE_TITLE__</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
 <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react/18.3.1/umd/react.production.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.3.1/umd/react-dom.production.min.js"></script>
  <script crossorigin src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.24.7/babel.min.js"></script>
  <style>
    :root {{
      /* Watermelon UI Fresh Daylight Palette */
      --wm-bg: #F3F8FC;
      --wm-surface: #FFFFFF;
      --wm-surface-soft: #F8FBFF;
      --wm-border: #E2ECF5;
      --wm-text: #0F172A;
      --wm-muted: #52647A;
      --wm-aqua: #0284C7;
      --wm-aqua-bright: #0EA5E9;
      --wm-aqua-soft: #E0F2FE;
      --wm-melon: #F43F5E;
      --wm-melon-soft: #FFE4E6;
      --wm-mint: #10B981;
      --wm-mint-soft: #D1FAE5;
      --wm-amber: #F59E0B;
      --wm-amber-soft: #FEF3C7;
      --wm-shadow: 0 12px 32px -12px rgba(15, 23, 42, 0.08);
      --wm-shadow-hover: 0 18px 38px -12px rgba(2, 132, 199, 0.16);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }}
    body {{
      background:
        radial-gradient(circle at 8% 0%, rgba(14, 165, 233, 0.09), transparent 36%),
        radial-gradient(circle at 92% 6%, rgba(244, 63, 94, 0.06), transparent 32%),
        var(--wm-bg);
      color: var(--wm-text);
      min-height: 100vh;
    }}
    .wm-nav {{
      position: sticky; top: 0; z-index: 40;
      background: rgba(255, 255, 255, 0.88);
      backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--wm-border);
      padding: 13px 26px;
      display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px;
    }}
    .wm-brand {{
      display: flex; align-items: center; gap: 11px;
      font-weight: 800; font-size: 17px; color: var(--wm-text); letter-spacing: -0.02em;
    }}
    .wm-logo-drop {{
      width: 36px; height: 36px; border-radius: 12px;
      background: linear-gradient(135deg, #0284C7 0%, #38BDF8 65%, #34D399 100%);
      display: grid; place-items: center; color: #fff; font-size: 18px;
      box-shadow: 0 8px 18px -6px rgba(2, 132, 199, 0.55);
    }}
    .wm-container {{ max-width: 1280px; margin: 0 auto; padding: 24px 20px 44px; }}
    .wm-card {{
      background: var(--wm-surface);
      border: 1px solid var(--wm-border);
      border-radius: 20px;
      padding: 20px;
      box-shadow: var(--wm-shadow);
    }}
    .wm-pill {{
      display: inline-flex; align-items: center; gap: 6px;
      padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 700;
    }}
    .wm-pill.aqua {{ background: var(--wm-aqua-soft); color: #0369A1; }}
    .wm-pill.mint {{ background: var(--wm-mint-soft); color: #047857; }}
    .wm-pill.melon {{ background: var(--wm-melon-soft); color: #BE123C; }}
    .wm-pill.amber {{ background: var(--wm-amber-soft); color: #B45309; }}
    .wm-btn {{
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      padding: 10px 16px; border-radius: 13px; border: 1px solid var(--wm-border);
      background: #fff; color: var(--wm-text); font-size: 13px; font-weight: 700;
      cursor: pointer; text-decoration: none; transition: border-color 0.15s, background 0.15s;
    }}
    .wm-btn:hover {{ border-color: #BAE6FD; background: #F8FBFF; }}
    .wm-btn.primary {{
      background: linear-gradient(135deg, #0284C7, #0EA5E9);
      color: #fff; border: none;
      box-shadow: 0 10px 20px -8px rgba(2, 132, 199, 0.55);
    }}
    .wm-btn.mint {{
      background: linear-gradient(135deg, #059669, #10B981);
      color: #fff; border: none;
      box-shadow: 0 10px 20px -8px rgba(16, 185, 129, 0.45);
    }}
    .wm-btn.melon {{
      background: linear-gradient(135deg, #E11D48, #F43F5E);
      color: #fff; border: none;
      box-shadow: 0 10px 20px -8px rgba(244, 63, 94, 0.45);
    }}
    .wm-input, .wm-select, .wm-textarea {{
      width: 100%; background: var(--wm-surface-soft);
      border: 1.5px solid var(--wm-border); color: var(--wm-text);
      padding: 10px 13px; border-radius: 12px; font-size: 13.5px; font-weight: 500;
      outline: none; transition: border-color 0.15s, box-shadow 0.15s;
    }}
    .wm-input:focus, .wm-select:focus, .wm-textarea:focus {{
      border-color: var(--wm-aqua-bright); background: #fff;
      box-shadow: 0 0 0 4px rgba(14, 165, 233, 0.12);
    }}
    .wm-label {{ display: block; font-size: 12px; font-weight: 700; color: var(--wm-muted); margin-bottom: 6px; }}
    .wm-grid-hero {{ display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 22px; align-items: stretch; }}
    .wm-grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }}
    .wm-grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
    .wm-grid-main {{ display: grid; grid-template-columns: 390px 1fr; gap: 22px; align-items: start; }}
    @media (max-width: 1024px) {{
      .wm-grid-hero, .wm-grid-main {{ grid-template-columns: 1fr; }}
      .wm-grid-4 {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 640px) {{
      .wm-grid-3, .wm-grid-4 {{ grid-template-columns: 1fr; }}
    }}
    .wm-map {{ height: 310px; border-radius: 16px; border: 1px solid var(--wm-border); overflow: hidden; background: #E8F1F8; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th {{ text-align: left; padding: 10px 8px; color: var(--wm-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; border-bottom: 1px solid var(--wm-border); }}
    td {{ padding: 11px 8px; border-bottom: 1px solid #EEF4FA; }}
  </style>
</head>
<body>
  <div id="root" style="padding:24px;font-family:sans-serif;color:#52647A;">Loading JalSetu Nagpur...</div>

  <script>
    window.__PAGE_MODE__ = "__PAGE_MODE__";
    window.__BOOTSTRAP__ = __BOOTSTRAP_JSON__;
    window.addEventListener('error', function (e) {
      var el = document.getElementById('root');
      if (el && el.innerText.indexOf('Loading') !== -1) {
        el.innerHTML = '<pre style="color:#BE123C;background:#FFE4E6;padding:16px;border-radius:12px;white-space:pre-wrap;">UI Load Error: ' + (e.message || e.error) + '</pre>';
      }
    });
  </script>

  <script type="text/babel">
    const { useState, useEffect, useRef } = React;
    const { createRoot } = ReactDOM;

    // Self-contained Hooke's-law spring runtime (tension/friction)
    function makeSpringVal(v) {
      return {
        __sv: true,
        _v: v,
        get() { return this._v; },
        to(fn) { return makeSpringVal(fn(this._v)); },
      };
    }

    function useSpring(spec) {
      const { from = {}, to, delay = 0, config = {}, ...direct } = spec;
      const targets = to || direct;
      const tension = config.tension || 260;
      const friction = config.friction || 24;

      const stateRef = useRef(null);
      if (!stateRef.current) {
        const init = {};
        const vel = {};
        Object.keys(targets).forEach((k) => {
          init[k] = from[k] !== undefined ? from[k] : targets[k];
          vel[k] = 0;
        });
        stateRef.current = { cur: init, vel };
      }

      const [, setTick] = useState(0);
      const targetSig = JSON.stringify(targets);

      useEffect(() => {
        let rafId = null;
        let lastTime = performance.now();
        const timer = setTimeout(() => {
          const step = (now) => {
            const dt = Math.min(0.032, (now - lastTime) / 1000);
            lastTime = now;
            let moving = false;
            const { cur, vel } = stateRef.current;

            Object.keys(targets).forEach((k) => {
              const tgt = targets[k];
              if (typeof tgt !== 'number') {
                cur[k] = tgt;
                return;
              }
              const c = typeof cur[k] === 'number' ? cur[k] : tgt;
              const v = vel[k] || 0;
              const force = -tension * (c - tgt);
              const damp = -friction * v;
              const nextV = v + (force + damp) * dt;
              const nextC = c + nextV * dt;

              if (Math.abs(tgt - nextC) < 0.01 && Math.abs(nextV) < 0.01) {
                cur[k] = tgt;
                vel[k] = 0;
              } else {
                cur[k] = nextC;
                vel[k] = nextV;
                moving = true;
              }
            });

            setTick((t) => t + 1);
            if (moving) rafId = requestAnimationFrame(step);
          };
          rafId = requestAnimationFrame(step);
        }, delay);

        return () => {
          clearTimeout(timer);
          if (rafId) cancelAnimationFrame(rafId);
        };
      }, [targetSig]);

      const out = {};
      Object.keys(targets).forEach((k) => {
        out[k] = makeSpringVal(stateRef.current.cur[k]);
      });
      return out;
    }

    function useTransition(item, spec) {
      const s = useSpring({
        from: spec.from || { opacity: 0, y: 10 },
        to: spec.enter || { opacity: 1, y: 0 },
        config: spec.config,
      });
      return (renderFn) =>
        renderFn(
          {
            opacity: s.opacity,
            transform: s.y ? s.y.to((v) => `translate3d(0, ${v}px, 0)`) : undefined,
          },
          item
        );
    }

    function wrapAnimated(Tag) {
      return function AnimatedTag({ style, children, ...rest }) {
        const cleanStyle = style ? { ...style } : undefined;
        if (cleanStyle) {
          Object.keys(cleanStyle).forEach((k) => {
            if (cleanStyle[k] && cleanStyle[k].__sv) cleanStyle[k] = cleanStyle[k].get();
          });
        }
        const cleanChildren = children && children.__sv ? children.get() : children;
        return <Tag style={cleanStyle} {...rest}>{cleanChildren}</Tag>;
      };
    }

    const animated = {
      div: wrapAnimated('div'),
      button: wrapAnimated('button'),
      span: wrapAnimated('span'),
    };

    const MODE = window.__PAGE_MODE__;
    const BOOT = window.__BOOTSTRAP__;

   // -----------------------------------------------------------------------
    // WATERMELON UI + REACT SPRING PRIMITIVES
    // -----------------------------------------------------------------------
    function SpringCard({ children, style = {}, delay = 0, hoverLift = false, onClick }) {
      const [hovered, setHovered] = useState(false);
      const [pressed, setPressed] = useState(false);

      const enter = useSpring({
        from: { opacity: 0, y: 16 },
        to: { opacity: 1, y: 0 },
        delay,
        config: { tension: 260, friction: 24 },
      });

      const interact = useSpring({
        scale: pressed ? 0.985 : (hoverLift && hovered ? 1.015 : 1),
        y: hoverLift && hovered ? -3 : 0,
        boxShadow: hoverLift && hovered
          ? '0 18px 38px -12px rgba(2, 132, 199, 0.18)'
          : '0 12px 32px -12px rgba(15, 23, 42, 0.08)',
        config: { tension: 340, friction: 22 },
      });

      return (
        <animated.div
          className="wm-card"
          onClick={onClick}
          onMouseEnter={() => setHovered(true)}
          onMouseLeave={() => { setHovered(false); setPressed(false); }}
          onMouseDown={() => setPressed(true)}
          onMouseUp={() => setPressed(false)}
          style={{
            ...style,
            opacity: enter.opacity,
            transform: enter.y.to((ey) => `translate3d(0, ${ey + interact.y.get()}px, 0) scale(${interact.scale.get()})`),
            boxShadow: interact.boxShadow,
            cursor: onClick ? 'pointer' : style.cursor,
          }}
        >
          {children}
        </animated.div>
      );
    }

    function SpringButton({ children, variant = '', onClick, style = {}, type = 'button' }) {
      const [pressed, setPressed] = useState(false);
      const spring = useSpring({
        scale: pressed ? 0.96 : 1,
        config: { tension: 420, friction: 20 },
      });
      return (
        <animated.button
          type={type}
          className={`wm-btn ${variant}`}
          onClick={onClick}
          onMouseDown={() => setPressed(true)}
          onMouseUp={() => setPressed(false)}
          onMouseLeave={() => setPressed(false)}
          style={{ ...style, transform: spring.scale.to((s) => `scale(${s})`) }}
        >
          {children}
        </animated.button>
      );
    }

    function AnimatedNumber({ value, suffix = '' }) {
      const num = Number(value) || 0;
      const spring = useSpring({
        val: num,
        from: { val: 0 },
        config: { tension: 120, friction: 20 },
      });
      return (
        <animated.span>
          {spring.val.to((v) => `${Math.round(v).toLocaleString('en-IN')}${suffix}`)}
        </animated.span>
      );
    }

    function StatusBadge({ status }) {
      const s = String(status || '').toUpperCase();
      if (['RED', 'OPEN', 'FLAGGED'].includes(s)) return <span className="wm-pill melon">● {s}</span>;
      if (['YELLOW', 'DISPATCHED', 'UNLOADED', 'PENDING_DISPATCH'].includes(s)) return <span className="wm-pill amber">● {s.replace('_', ' ')}</span>;
      return <span className="wm-pill mint">● {s || 'HEALTHY'}</span>;
    }

    function NagpurMap({ center = [21.125, 79.025], zoom = 11, renderLayers, deps = [] }) {
      const divRef = useRef(null);
      const mapRef = useRef(null);
      const layerRef = useRef(null);

      useEffect(() => {
        if (!divRef.current || typeof L === 'undefined') return;
        if (!mapRef.current) {
          const m = L.map(divRef.current).setView(center, zoom);
          const tiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap © CARTO',
          });
          tiles.on('tileerror', () => {
            if (divRef.current) {
              divRef.current.style.backgroundImage = 'radial-gradient(#CBD5E1 1.2px, transparent 1.2px)';
              divRef.current.style.backgroundSize = '18px 18px';
            }
          });
          tiles.addTo(m);
          mapRef.current = m;
          layerRef.current = L.layerGroup().addTo(m);
        }
        if (renderLayers && mapRef.current && layerRef.current) {
          layerRef.current.clearLayers();
          renderLayers(mapRef.current, layerRef.current);
        }
      }, deps);

      return <div ref={divRef} className="wm-map" />;
    }

    // -----------------------------------------------------------------------
    // VIEW 0: PUBLIC OVERVIEW + PORTAL SIGN-IN (/login)
    // -----------------------------------------------------------------------
    function LandingLoginApp() {{
      const [role, setRole] = useState(BOOT.preselect_role || 'citizen');
      const [name, setName] = useState(BOOT.role_defaults[BOOT.preselect_role || 'citizen'].default_name);
      const [password, setPassword] = useState(BOOT.role_defaults[BOOT.preselect_role || 'citizen'].default_pass);
      const [err, setErr] = useState('');
      const [summary, setSummary] = useState(null);
      const loginBoxRef = useRef(null);

      useEffect(() => {{
        fetch('/api/public-summary').then((r) => r.json()).then(setSummary).catch(() => {{}});
      }}, []);

      const chooseRole = (r, scrollToLogin = false) => {{
        setRole(r);
        setName(BOOT.role_defaults[r].default_name);
        setPassword(BOOT.role_defaults[r].default_pass);
        setErr('');
        if (scrollToLogin && loginBoxRef.current) {{
          loginBoxRef.current.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
        }}
      }};

      const handleAuth = async (endpoint) => {{
        setErr('');
        const res = await fetch(endpoint, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ role, name: name.trim(), password }}),
        }});
        const data = await res.json();
        if (!res.ok) {{
          setErr(data.error || 'Sign-in failed');
          return;
        }}
        window.location.href = data.redirect;
      }};

      const roleDescriptions = {{
        citizen: 'Check daily colony water status & pump runway, log 1-tap household availability, track live incoming tankers on map, report leaks, and calculate 14-taluka rainwater harvesting.',
        verifier: 'Log weekly/fortnightly reference well depths with live 48h Open-Meteo rainfall anti-cheat validation, inspect 6-hourly calibrated hydrographs, and raise verified 55 LPCD tanker indents.',
        utility: 'Monitor Nagpur scarcity & live tanker routes, auto-dispatch nearest depot tankers with stock tracking, and resolve resident leak & valve fault tickets.',
      }};

      const kpis = [
        {{ label: 'Monitored Nagpur Locations', val: summary ? summary.total_locations : 91, sub: '87 CGWB stations + pilot colonies', tone: 'aqua', icon: '📍' }},
        {{ label: 'Active Scarcity Zones', val: summary ? summary.stressed_zones : 3, sub: 'RED & YELLOW alert colonies', tone: 'melon', icon: '⚠️' }},
        {{ label: 'Dry Borewell Households', val: summary ? summary.dry_households : 96, sub: 'Live resident check-in reports', tone: 'amber', icon: '🏠' }},
        {{ label: 'Tankers Ready at Depots', val: summary ? summary.trucks_ready : 12, sub: 'Across 3 Nagpur filling zones', tone: 'mint', icon: '🚛' }},
        {{ label: 'Active / Completed Deliveries', val: summary ? summary.total_orders : 1, sub: 'Verified end-to-end trips', tone: 'aqua', icon: '💧' }},
        {{ label: 'Live 48h Nagpur Rainfall', val: summary ? summary.rain_48h_mm : 0, suffix: ' mm', sub: 'Open-Meteo live precipitation', tone: 'mint', icon: '🌧️' }},
      ];

      const quickActions = [
        {{ title: 'Daily Water Check-In', desc: 'Report normal supply, low pressure, or dry borewell in 1 tap.', role: 'citizen', icon: '💧', accent: '#0284C7' }},
        {{ title: 'Track Live Tanker', desc: 'See incoming tanker route from depot & confirm delivery.', role: 'citizen', icon: '🗺️', accent: '#10B981' }},
        {{ title: 'Report Leak / Pump Fault', desc: 'Log leaking valves or pump breakdowns directly to utility desk.', role: 'citizen', icon: '🔧', accent: '#F43F5E' }},
        {{ title: '14-Taluka RWH Calculator', desc: 'Estimate roof runoff, first-flush & recharge in EN / हिं / म.', role: 'citizen', icon: '🌦️', accent: '#F59E0B' }},
      ];

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">💧</div>
              <div>
                <div>JalSetu Nagpur</div>
                <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--wm-muted)' }}>Community Groundwater, Tanker & Recharge Intelligence</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <SpringButton onClick={() => chooseRole('citizen', true)}>Citizen Login</SpringButton>
              <SpringButton onClick={() => chooseRole('verifier', true)}>Field Verifier</SpringButton>
              <SpringButton variant="primary" onClick={() => chooseRole('utility', true)}>Utility & Tanker Ops</SpringButton>
            </div>
          </nav>

          <div className="wm-container">
            {/* Hero + Role Sign-In Split */}
            <div className="wm-grid-hero" style={{ marginBottom: '26px' }}>
              <SpringCard style={{ background: 'linear-gradient(145deg, #FFFFFF 0%, #F0F9FF 100%)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '14px' }}>
                    <span className="wm-pill aqua">Nagpur District · 91 Locations</span>
                    <span className="wm-pill mint">Zero-Hardware Calibration + Live 48h Rain</span>
                  </div>
                  <h1 style={{ fontSize: '32px', fontWeight: 800, lineHeight: 1.18, letterSpacing: '-0.03em', marginBottom: '12px', color: '#0F172A' }}>
                    Real-Time Water Scarcity, Tanker Tracking & Rainwater Recharge
                  </h1>
                  <p style={{ fontSize: '14.5px', lineHeight: 1.6, color: 'var(--wm-muted)', marginBottom: '20px' }}>
                    Connecting Nagpur residents, field verifiers, and tanker dispatchers on one live workflow—calibrating local borewells against CGWB telemetry, verifying scarcity with 48-hour rainfall, and tracking every tanker drop.
                  </p>
                </div>

                {/* Custom Civic Watershed & Tanker Route Vector Illustration */}
                <div style={{ background: '#fff', border: '1px solid var(--wm-border)', borderRadius: '16px', padding: '14px' }}>
                  <svg viewBox="0 0 540 135" style={{ width: '100%', height: '125px', display: 'block' }}>
                    <defs>
                      <linearGradient id="skyGrad" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#E0F2FE" />
                        <stop offset="50%" stopColor="#F0FDF4" />
                        <stop offset="100%" stopColor="#FFE4E6" />
                      </linearGradient>
                    </defs>
                    <rect x="0" y="0" width="540" height="135" rx="12" fill="url(#skyGrad)" />
                    <path d="M 55 95 C 160 35, 290 115, 465 55" fill="none" stroke="#0284C7" strokeWidth="4" strokeDasharray="8 6" strokeLinecap="round" />
                    {/* Depot Node */}
                    <circle cx="55" cy="95" r="18" fill="#0284C7" />
                    <text x="55" y="100" textAnchor="middle" fill="#fff" fontSize="14">🚛</text>
                    <text x="55" y="125" textAnchor="middle" fill="#0F172A" fontSize="10" fontWeight="700">Tanker Depot</text>
                    {/* Calibrated Borewell Node */}
                    <circle cx="260" cy="76" r="18" fill="#10B981" />
                    <text x="260" y="81" textAnchor="middle" fill="#fff" fontSize="14">📡</text>
                    <text x="260" y="108" textAnchor="middle" fill="#0F172A" fontSize="10" fontWeight="700">CGWB + Rain Check</text>
                    {/* Colony Destination Node */}
                    <circle cx="465" cy="55" r="18" fill="#F43F5E" />
                    <text x="465" y="60" textAnchor="middle" fill="#fff" fontSize="14">🏘️</text>
                    <text x="465" y="87" textAnchor="middle" fill="#0F172A" fontSize="10" fontWeight="700">Colony Delivery</text>
                  </svg>
                </div>
              </SpringCard>

              {/* Portal Sign-In Card */}
              <div ref={loginBoxRef}>
                <SpringCard delay={80} style={{ height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <h2 style={{ fontSize: '18px', fontWeight: 800 }}>Sign In to Your Portal</h2>
                    <span className="wm-pill aqua">Role-Based Access</span>
                  </div>

                  {/* Role Switcher Pills */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', marginBottom: '14px' }}>
                    {[
                      {{ id: 'citizen', label: 'Citizen' }},
                      {{ id: 'verifier', label: 'Field Verifier' }},
                      {{ id: 'utility', label: 'Utility Ops' }},
                    ].map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => chooseRole(t.id)}
                        style={{
                          padding: '10px 8px',
                          borderRadius: '12px',
                          border: role === t.id ? '2px solid #0284C7' : '1px solid var(--wm-border)',
                          background: role === t.id ? '#E0F2FE' : '#F8FBFF',
                          color: role === t.id ? '#0369A1' : 'var(--wm-muted)',
                          fontWeight: 800,
                          fontSize: '12.5px',
                          cursor: 'pointer',
                        }}
                      >
                        {{t.label}}
                      </button>
                    ))}
                  </div>

                  <div style={{ background: '#F8FBFF', border: '1px solid var(--wm-border)', borderRadius: '12px', padding: '10px 12px', fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5, marginBottom: '14px' }}>
                    {{roleDescriptions[role]}}
                  </div>

                  <label className="wm-label">Full Name / Username</label>
                  <input className="wm-input" style={{ marginBottom: '10px' }} value={name} onChange={(e) => setName(e.target.value)} placeholder="Enter your name" />

                  <label className="wm-label">Password</label>
                  <input className="wm-input" type="password" style={{ marginBottom: '12px' }} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" />

                  {err && (
                    <div style={{ background: 'var(--wm-melon-soft)', color: '#BE123C', padding: '8px 12px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, marginBottom: '10px' }}>
                      {{err}}
                    </div>
                  )}

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <SpringButton variant="primary" style={{ flex: 1 }} onClick={() => handleAuth('/api/login')}>
                      Enter {{BOOT.role_defaults[role].title}} →
                    </SpringButton>
                    <SpringButton onClick={() => handleAuth('/api/register')}>
                      Register
                    </SpringButton>
                  </div>
                </SpringCard>
              </div>
            </div>

            {/* 6 Live District KPI Cards */}
            <div className="wm-grid-3" style={{ marginBottom: '26px' }}>
              {kpis.map((k, idx) => (
                <SpringCard key={k.label} delay={idx * 45} hoverLift style={{ display: 'flex', alignItems: 'center', gap: '14px', padding: '16px 18px' }}>
                  <div style={{
                    width: '46px', height: '46px', borderRadius: '14px', flexShrink: 0,
                    background: `var(--wm-${{k.tone}}-soft)`, display: 'grid', placeItems: 'center', fontSize: '21px'
                  }}>
                    {{k.icon}}
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--wm-muted)' }}>{{k.label}}</div>
                    <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--wm-text)', lineHeight: 1.15 }}>
                      <AnimatedNumber value={k.val} suffix={k.suffix || ''} />
                    </div>
                    <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)', marginTop: '2px' }}>{{k.sub}}</div>
                  </div>
                </SpringCard>
              ))}
            </div>

            {/* Quick Actions Strip (Citizen-First) */}
            <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2 style={{ fontSize: '18px', fontWeight: 800 }}>Citizen Quick Actions</h2>
              <span style={{ fontSize: '12px', color: 'var(--wm-muted)', fontWeight: 600 }}>Click any action to jump into Citizen Portal</span>
            </div>
            <div className="wm-grid-4">
              {quickActions.map((qa, idx) => (
                <SpringCard
                  key={qa.title}
                  delay={120 + idx * 50}
                  hoverLift
                  onClick={() => chooseRole(qa.role, true)}
                  style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}
                >
                  <div>
                    <div style={{
                      width: '40px', height: '40px', borderRadius: '12px', marginBottom: '12px',
                      background: '#F0F9FF', display: 'grid', placeItems: 'center', fontSize: '20px'
                    }}>
                      {{qa.icon}}
                    </div>
                    <div style={{ fontSize: '15px', fontWeight: 800, marginBottom: '6px' }}>{{qa.title}}</div>
                    <p style={{ fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5 }}>{{qa.desc}}</p>
                  </div>
                  <div style={{ marginTop: '14px', fontSize: '12px', fontWeight: 800, color: qa.accent }}>
                    Open Action →
                  </div>
                </SpringCard>
              ))}
            </div>
          </div>
        </div>
      );
    }}

    // -----------------------------------------------------------------------
    // VIEW 1: CITIZEN PORTAL (/citizen)
    // -----------------------------------------------------------------------
    const RWH_RULES = {{
      en: [
        'Sweep terrace & clear drain outlets before monsoon showers',
        'Divert first rain & dry-spell flush before recharge pit entry',
        'Keep terrace free of detergents & chemical cleaners',
        'Inspect filter mesh, sand/gravel bed & recharge pit lid',
      ],
      hi: [
        'मानसून से पहले छत और नालियों की सफाई करें',
        'पहली बारिश और सूखे अंतराल का फर्स्ट-फ्लश बाहर निकालें',
        'छत को डिटर्जेंट और रसायनों से मुक्त रखें',
        'फिल्टर जाली, रेत/बजरी परत और पिट ढक्कन की जांच करें',
      ],
      mr: [
        'पावसाळ्यापूर्वी छत आणि पाण्याचे निचरे स्वच्छ करा',
        'पहिल्या पावसाचा व कोरड्या काळानंतरचा फर्स्ट-फ्लश बाहेर सोडा',
        'छत डिटर्जंट आणि रसायनांपासून मुक्त ठेवा',
        'फिल्टर जाळी, वाळू/खडीचा थर आणि पिट झाकण तपासा',
      ],
    }};

    function CitizenApp() {{
      const [tehsil, setTehsil] = useState('ALL');
      const [query, setQuery] = useState('');
      const [layoutId, setLayoutId] = useState('wanadongri');
      const [data, setData] = useState(null);
      const [tab, setTab] = useState('checkin');
      const [unit, setUnit] = useState('B-304');
      const [toast, setToast] = useState('');

      // Leak Ticket state
      const [issueType, setIssueType] = useState('Leaking pipeline');
      const [severity, setSeverity] = useState('Moderate');
      const [desc, setDesc] = useState('');

      // RWH Calculator state
      const [rwhLang, setRwhLang] = useState('en');
      const [rwhTaluka, setRwhTaluka] = useState('hingna');
      const [rwhArea, setRwhArea] = useState(1200);
      const [rwhUnit, setRwhUnit] = useState('sqft');
      const [rwhSurface, setRwhSurface] = useState('concrete');
      const [rwhOut, setRwhOut] = useState(null);

      const tehsils = Array.from(new Set(BOOT.layouts.map((x) => x.tehsil))).sort();
      const filteredLayouts = BOOT.layouts.filter((l) => {{
        if (tehsil !== 'ALL' && l.tehsil !== tehsil) return false;
        if (query && !l.name.toLowerCase().includes(query.toLowerCase())) return false;
        return true;
      }});

      const showToast = (msg) => {{
        setToast(msg);
        setTimeout(() => setToast(''), 3200);
      }};

      const loadColony = async (id = layoutId) => {{
        const res = await fetch(`/api/colony?id=${{encodeURIComponent(id)}}`);
        const d = await res.json();
        setData(d);
      }};

      useEffect(() => {{ loadColony(layoutId); }}, [layoutId]);

      useEffect(() => {{
        fetch('/api/rwh-calc', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ taluka_id: rwhTaluka, area: Number(rwhArea) || 0, unit: rwhUnit, surface_id: rwhSurface }}),
        }}).then((r) => r.json()).then(setRwhOut);
      }}, [rwhTaluka, rwhArea, rwhUnit, rwhSurface]);

      const tabTransition = useTransition(tab, {{
        from: {{ opacity: 0, y: 10 }},
        enter: {{ opacity: 1, y: 0 }},
        leave: {{ opacity: 0, y: -8 }},
        config: {{ tension: 300, friction: 26 }},
      }});

      const sendCheckin = async (status) => {{
        await fetch('/api/checkin', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ layout_id: layoutId, unit, status }}),
        }});
        showToast('Daily water check-in recorded!');
        loadColony(layoutId);
      }};

      const submitTicket = async () => {{
        if (!desc.trim()) return showToast('Please describe the leak location first.');
        const res = await fetch('/api/ticket', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ layout_id: layoutId, issue_type: issueType, severity, description: desc }}),
        }});
        const d = await res.json();
        setDesc('');
        showToast(`Ticket #${{d.ticket_id}} sent to Utility Desk!`);
        loadColony(layoutId);
      }};

      const confirmTanker = async (orderId) => {{
        await fetch('/api/tanker-status', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ order_id: orderId, status: 'CONFIRMED' }}),
        }});
        showToast('Thank you! Tanker delivery confirmed.');
        loadColony(layoutId);
      }};

      const toggleRwh = async (key, checked) => {{
        await fetch('/api/rwh-check', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ layout_id: layoutId, key, checked }}),
        }});
        loadColony(layoutId);
      }};

      const ev = data?.evaluation;
      const counts = data?.crowd?.counts || {{}};
      const totalHomes = Math.max(data?.layout?.total_households || 1, (counts.NORMAL || 0) + (counts.LOW_PRESSURE || 0) + (counts.BOREWELL_DRY || 0));

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">💧</div>
              <div>
                <div>Citizen Water Portal</div>
                <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Welcome, {{BOOT.user_name}}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              {ev && <span className="wm-pill aqua">48h Rain: {{ev.raw_stage1.rain_48h_mm}} mm</span>}
              <a className="wm-btn" href="/login?role=verifier">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          {toast && (
            <div style={{ position: 'fixed', bottom: '22px', right: '22px', zIndex: 60, background: '#0F172A', color: '#fff', padding: '12px 18px', borderRadius: '14px', fontSize: '13px', fontWeight: 700, boxShadow: '0 14px 30px rgba(15,23,42,0.25)' }}>
              ✓ {{toast}}
            </div>
          )}

          <div className="wm-container">
            <div className="wm-grid-main">
              {/* Left Sidebar: Colony Picker + Quick Status Summary */}
              <div>
                <SpringCard style={{ marginBottom: '18px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '12px' }}>Select Your Colony / Ward</h3>
                  <label className="wm-label">Filter by Tehsil</label>
                  <select className="wm-select" style={{ marginBottom: '10px' }} value={tehsil} onChange={(e) => setTehsil(e.target.value)}>
                    <option value="ALL">All Nagpur District (91 Locations)</option>
                    {tehsils.map((t) => <option key={t} value={t}>{{t}}</option>)}
                  </select>

                  <label className="wm-label">Search Location</label>
                  <input className="wm-input" style={{ marginBottom: '10px' }} placeholder="Hingna, Wanadongri, Wadi..." value={query} onChange={(e) => setQuery(e.target.value)} />

                  <label className="wm-label">Colony / Station</label>
                  <select className="wm-select" value={layoutId} onChange={(e) => setLayoutId(e.target.value)}>
                    {filteredLayouts.map((l) => (
                      <option key={l.id} value={l.id}>{{l.category === 'Featured Pilot' ? '★ ' : ''}}{{l.name}}</option>
                    ))}
                  </select>
                </SpringCard>

                {ev && (
                  <SpringCard delay={70}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{ fontSize: '12px', fontWeight: 800, color: 'var(--wm-muted)' }}>COLONY SUPPLY HEALTH</span>
                      <StatusBadge status={ev.scarcity_status} />
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: 800, marginBottom: '6px' }}>{{data.layout.name}}</div>
                    <p style={{ fontSize: '12.5px', color: 'var(--wm-muted)', lineHeight: 1.5, marginBottom: '14px' }}>{{ev.diagnosis}}</p>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                      <div style={{ background: 'var(--wm-surface-soft)', padding: '11px', borderRadius: '12px', border: '1px solid var(--wm-border)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>PUMP RUNWAY</div>
                        <div style={{ fontSize: '19px', fontWeight: 800, color: ev.groundwater_summary.pump_runway.days !== null && ev.groundwater_summary.pump_runway.days <= 20 ? '#E11D48' : '#0284C7' }}>
                          {{ev.groundwater_summary.pump_runway.days !== null ? `${{ev.groundwater_summary.pump_runway.days}} days` : 'Stable'}}
                        </div>
                      </div>
                      <div style={{ background: 'var(--wm-surface-soft)', padding: '11px', borderRadius: '12px', border: '1px solid var(--wm-border)' }}>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>DRY HOMES</div>
                        <div style={{ fontSize: '19px', fontWeight: 800 }}>
                          {{ev.signals.signal_3_community_shortage.dry_percentage}}%
                        </div>
                      </div>
                    </div>
                  </SpringCard>
                )}
              </div>

              {/* Right Main Area: Spring-Animated Pill Tabs */}
              <div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                  {[
                    {{ id: 'checkin', label: '1. Daily Water Check-In' }},
                    {{ id: 'tanker', label: `2. Live Tanker Tracker (${{data?.tanker_orders?.length || 0}})` }},
                    {{ id: 'leak', label: `3. Report Leak (${{data?.tickets?.length || 0}})` }},
                    {{ id: 'rwh', label: '4. Rainwater Harvesting (14 Talukas)' }},
                  ].map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setTab(t.id)}
                      style={{
                        padding: '10px 15px',
                        borderRadius: '999px',
                        border: tab === t.id ? 'none' : '1px solid var(--wm-border)',
                        background: tab === t.id ? 'linear-gradient(135deg, #0284C7, #0EA5E9)' : '#fff',
                        color: tab === t.id ? '#fff' : 'var(--wm-text)',
                        fontSize: '13px',
                        fontWeight: 700,
                        cursor: 'pointer',
                        boxShadow: tab === t.id ? '0 8px 18px -6px rgba(2,132,199,0.5)' : 'none',
                      }}
                    >
                      {{t.label}}
                    </button>
                  ))}
                </div>

                {tabTransition((style, activeTab) => (
                  <animated.div style={style}>
                    {activeTab === 'checkin' && (
                      <SpringCard>
                        <h2 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '6px' }}>How is your tap / borewell water supply today?</h2>
                        <p style={{ fontSize: '13px', color: 'var(--wm-muted)', marginBottom: '16px' }}>
                          Your 1-tap check-in updates colony scarcity signals in real time for verifiers and tanker dispatchers.
                        </p>

                        <div style={{ maxWidth: '280px', marginBottom: '14px' }}>
                          <label className="wm-label">Your Flat / Plot / House No.</label>
                          <input className="wm-input" value={unit} onChange={(e) => setUnit(e.target.value)} />
                        </div>

                        <div className="wm-grid-3" style={{ marginBottom: '18px' }}>
                          <SpringButton variant="mint" style={{ padding: '14px' }} onClick={() => sendCheckin('NORMAL')}>
                            🟢 Normal Supply
                          </SpringButton>
                          <SpringButton style={{ padding: '14px', borderColor: '#F59E0B', color: '#B45309', background: '#FFFBEB' }} onClick={() => sendCheckin('LOW_PRESSURE')}>
                            🟡 Low Pressure
                          </SpringButton>
                          <SpringButton variant="melon" style={{ padding: '14px' }} onClick={() => sendCheckin('BOREWELL_DRY')}>
                            🔴 Borewell Dry
                          </SpringButton>
                        </div>

                        {/* Visual Stacked Availability Bar */}
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '14px', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
                          <div style={{ fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>Live Colony Household Breakdown</div>
                          <div style={{ height: '12px', borderRadius: '999px', overflow: 'hidden', display: 'flex', background: '#E2E8F0', marginBottom: '8px' }}>
                            <div style={{ width: `${{((counts.NORMAL || 0) / totalHomes) * 100}}%`, background: '#10B981' }} />
                            <div style={{ width: `${{((counts.LOW_PRESSURE || 0) / totalHomes) * 100}}%`, background: '#F59E0B' }} />
                            <div style={{ width: `${{((counts.BOREWELL_DRY || 0) / totalHomes) * 100}}%`, background: '#F43F5E' }} />
                          </div>
                          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', fontSize: '12px', fontWeight: 600, color: 'var(--wm-muted)' }}>
                            <span>🟢 Normal: <b>{{counts.NORMAL || 0}}</b></span>
                            <span>🟡 Low Pressure: <b>{{counts.LOW_PRESSURE || 0}}</b></span>
                            <span>🔴 Dry Borewell: <b>{{counts.BOREWELL_DRY || 0}}</b></span>
                          </div>
                        </div>
                      </SpringCard>
                    )}

                    {activeTab === 'tanker' && data && (
                      <SpringCard>
                        <h2 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '12px' }}>Live Incoming Tanker Map & Delivery Proof</h2>
                        <NagpurMap
                          center={[data.layout.lat, data.layout.lon]}
                          zoom={12}
                          deps={[data]}
                          renderLayers={(map, group) => {{
                            L.circleMarker([data.layout.lat, data.layout.lon], {{ radius: 9, color: '#0284C7', fillColor: '#0EA5E9', fillOpacity: 0.9 }})
                              .bindPopup(`<b>${{data.layout.name}}</b><br>Your Colony`).addTo(group);

                            BOOT.depots.forEach((d) => {{
                              L.marker([d.lat, d.lon]).bindPopup(`<b>${{d.name}}</b>`).addTo(group);
                            }});

                            (data.tanker_orders || []).forEach((o) => {{
                              const dep = BOOT.depots.find((d) => d.id === o.depot_id);
                              if (dep && (o.status === 'DISPATCHED' || o.status === 'UNLOADED')) {{
                                const line = L.polyline([[dep.lat, dep.lon], [data.layout.lat, data.layout.lon]], {{ color: '#10B981', weight: 4, dashArray: '8,8' }}).addTo(group);
                                L.circleMarker([(dep.lat + data.layout.lat) / 2, (dep.lon + data.layout.lon) / 2], {{ radius: 7, color: '#F43F5E', fillColor: '#F43F5E', fillOpacity: 1 }})
                                  .bindPopup(`<b>🚛 ${{o.vehicle_no}}</b><br>${{o.volume_l.toLocaleString()}} L`).addTo(group);
                                map.fitBounds(line.getBounds(), {{ padding: [45, 45] }});
                              }}
                            }});
                          }}
                        />

                        <div style={{ marginTop: '14px', display: 'grid', gap: '10px' }}>
                          {(data.tanker_orders || []).length === 0 && (
                            <div style={{ fontSize: '13px', color: 'var(--wm-muted)' }}>No active tanker orders for this colony right now.</div>
                          )}
                          {(data.tanker_orders || []).map((o) => (
                            <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', padding: '12px 14px', borderRadius: '14px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)' }}>
                              <div>
                                <div style={{ fontWeight: 800, fontSize: '14px' }}>{{o.id}} · {{o.volume_l.toLocaleString()}} L ({{o.vehicle_no || 'Awaiting Truck'}})</div>
                                <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>From {{o.depot_name || 'Pending Depot'}} · {{o.distance_km || '--'}} km</div>
                              </div>
                              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                                <StatusBadge status={o.status} />
                                {(o.status === 'DISPATCHED' || o.status === 'UNLOADED') && (
                                  <SpringButton variant="mint" onClick={() => confirmTanker(o.id)}>✓ Confirm Water Received</SpringButton>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </SpringCard>
                    )}

                    {activeTab === 'leak' && (
                      <SpringCard>
                        <h2 style={{ fontSize: '17px', fontWeight: 800, marginBottom: '12px' }}>Report Pipeline Leak / Pump Breakdown</h2>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '10px' }}>
                          <div>
                            <label className="wm-label">Issue Type</label>
                            <select className="wm-select" value={issueType} onChange={(e) => setIssueType(e.target.value)}>
                              <option>Leaking pipeline</option>
                              <option>Overflowing storage tank</option>
                              <option>Public tap wastage</option>
                              <option>Submersible pump fault</option>
                              <option>Broken RWH unit</option>
                            </select>
                          </div>
                          <div>
                            <label className="wm-label">Severity</label>
                            <select className="wm-select" value={severity} onChange={(e) => setSeverity(e.target.value)}>
                              <option>Minor</option>
                              <option>Moderate</option>
                              <option>Severe</option>
                            </select>
                          </div>
                        </div>
                        <label className="wm-label">Landmark & Issue Details</label>
                        <textarea className="wm-textarea" rows="2" style={{ marginBottom: '12px' }} placeholder="e.g. Gate 2 feeder valve leaking heavily..." value={desc} onChange={(e) => setDesc(e.target.value)} />
                        <SpringButton variant="primary" onClick={submitTicket}>Submit Ticket to Utility Desk</SpringButton>

                        <h3 style={{ fontSize: '14px', fontWeight: 800, marginTop: '20px', marginBottom: '10px' }}>Colony Tickets</h3>
                        <div style={{ display: 'grid', gap: '8px' }}>
                          {(data?.tickets || []).map((t) => (
                            <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '11px 14px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)' }}>
                              <div>
                                <div style={{ fontWeight: 700, fontSize: '13px' }}>#{{t.id}} · {{t.issue_type}} ({{t.severity}})</div>
                                <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>{{t.description}} · {{t.created_at}}</div>
                              </div>
                              <StatusBadge status={t.status} />
                            </div>
                          ))}
                        </div>
                      </SpringCard>
                    )}

                    {activeTab === 'rwh' && (
                      <SpringCard>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '14px' }}>
                          <h2 style={{ fontSize: '17px', fontWeight: 800 }}>Nagpur District Rainwater Harvesting Calculator</h2>
                          <select className="wm-select" style={{ width: 'auto' }} value={rwhLang} onChange={(e) => setRwhLang(e.target.value)}>
                            <option value="en">English</option>
                            <option value="hi">हिंदी</option>
                            <option value="mr">मराठी</option>
                          </select>
                        </div>

                        <div className="wm-grid-3" style={{ marginBottom: '14px' }}>
                          <div>
                            <label className="wm-label">Nagpur Taluka (14)</label>
                            <select className="wm-select" value={rwhTaluka} onChange={(e) => setRwhTaluka(e.target.value)}>
                              {BOOT.talukas.map((t) => <option key={t.id} value={t.id}>{{t.name}} ({{t.rainfall_mm}} mm)</option>)}
                            </select>
                          </div>
                          <div>
                            <label className="wm-label">Roof Area</label>
                            <div style={{ display: 'flex', gap: '6px' }}>
                              <input className="wm-input" type="number" value={rwhArea} onChange={(e) => setRwhArea(e.target.value)} />
                              <select className="wm-select" style={{ width: '95px' }} value={rwhUnit} onChange={(e) => setRwhUnit(e.target.value)}>
                                <option value="sqft">Sq.Ft</option>
                                <option value="sqm">Sq.M</option>
                              </select>
                            </div>
                          </div>
                          <div>
                            <label className="wm-label">Roof Surface</label>
                            <select className="wm-select" value={rwhSurface} onChange={(e) => setRwhSurface(e.target.value)}>
                              <option value="concrete">Concrete / RCC (0.85)</option>
                              <option value="metal">Metal / GI Sheet (0.90)</option>
                              <option value="tiled">Tiled / Sloped (0.75)</option>
                            </select>
                          </div>
                        </div>

                        {rwhOut && (
                          <div className="wm-grid-3" style={{ marginBottom: '16px' }}>
                            <div style={{ background: 'var(--wm-aqua-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: '#0369A1' }}>GROSS CAPTURED</div>
                              <div style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A' }}>{{rwhOut.gross_l.toLocaleString('en-IN')}} L</div>
                            </div>
                            <div style={{ background: 'var(--wm-amber-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: '#B45309' }}>FIRST-FLUSH DIVERTED</div>
                              <div style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A' }}>{{rwhOut.first_flush_l.toLocaleString('en-IN')}} L</div>
                            </div>
                            <div style={{ background: 'var(--wm-mint-soft)', padding: '13px', borderRadius: '14px' }}>
                              <div style={{ fontSize: '11px', fontWeight: 700, color: '#047857' }}>NET EFFECTIVE HARVEST</div>
                              <div style={{ fontSize: '20px', fontWeight: 800, color: '#047857' }}>{{rwhOut.net_l.toLocaleString('en-IN')}} L</div>
                            </div>
                          </div>
                        )}

                        <div style={{ fontSize: '13px', fontWeight: 800, marginBottom: '8px' }}>Monsoon Readiness Checklist</div>
                        {(RWH_RULES[rwhLang] || RWH_RULES.en).map((rule, idx) => {{
                          const key = `r_${{idx}}`;
                          const checked = !!(data?.rwh_checks || {{}})[key];
                          return (
                            <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 10px', borderRadius: '10px', background: 'var(--wm-surface-soft)', marginBottom: '6px', cursor: 'pointer', fontSize: '13px' }}>
                              <input type="checkbox" checked={checked} onChange={(e) => toggleRwh(key, e.target.checked)} />
                              <span>{{rule}}</span>
                            </label>
                          );
                        }})}
                      </SpringCard>
                    )}
                  </animated.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    }}

    // -----------------------------------------------------------------------
    // VIEW 2: FIELD VERIFIER PORTAL (/verifier)
    // -----------------------------------------------------------------------
    function VerifierApp() {{
      const [query, setQuery] = useState('');
      const [layoutId, setLayoutId] = useState('wanadongri');
      const [data, setData] = useState(null);
      const [vDepth, setVDepth] = useState(18.6);
      const [vLast, setVLast] = useState(16.8);
      const [vDays, setVDays] = useState(7);
      const [indentVol, setIndentVol] = useState(10000);
      const [toast, setToast] = useState('');

      const list = BOOT.layouts.filter((l) => !query || l.name.toLowerCase().includes(query.toLowerCase()) || l.tehsil.toLowerCase().includes(query.toLowerCase()));

      const showToast = (msg) => {{
        setToast(msg);
        setTimeout(() => setToast(''), 3200);
      }};

      const loadColony = async (id = layoutId) => {{
        const res = await fetch(`/api/colony?id=${{encodeURIComponent(id)}}`);
        const d = await res.json();
        setData(d);
        setVDepth(d.verifier_record.verifier_depth_m);
        setVLast(d.verifier_record.last_recorded_depth_m);
        setVDays(d.verifier_record.days_since_last || 7);
      }};

      useEffect(() => {{ loadColony(layoutId); }}, [layoutId]);

      const saveReading = async () => {{
        await fetch('/api/verifier-update', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            layout_id: layoutId,
            verifier_depth_m: Number(vDepth),
            last_recorded_depth_m: Number(vLast),
            days_since_last: Number(vDays),
          }}),
        }});
        showToast('Well depth verified & calibrated!');
        loadColony(layoutId);
      }};

      const raiseIndent = async () => {{
        const res = await fetch('/api/tanker-indent', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ layout_id: layoutId, volume_l: Number(indentVol) }}),
        }});
        const d = await res.json();
        showToast(`Verified Tanker Indent ${{d.order.id}} sent to Utility!`);
      }};

      const ev = data?.evaluation;
      const series = ev?.raw_stage1?.calibrated_series || [];

      const renderHydrograph = () => {{
        if (series.length < 2) return null;
        const w = 600, h = 185, padL = 42, padR = 16, padT = 18, padB = 24;
        const all = series.map((p) => p.gov_depth_m).concat(series.map((p) => p.calibrated_layout_depth_m));
        const minD = Math.floor(Math.min(...all) - 0.5);
        const maxD = Math.ceil(Math.max(...all) + 0.5);
        const xS = (i) => padL + (i / (series.length - 1)) * (w - padL - padR);
        const yS = (d) => padT + ((d - minD) / Math.max(maxD - minD, 0.5)) * (h - padT - padB);
        const pGov = series.map((p, i) => `${{i === 0 ? 'M' : 'L'}} ${{xS(i).toFixed(1)}} ${{yS(p.gov_depth_m).toFixed(1)}}`).join(' ');
        const pCal = series.map((p, i) => `${{i === 0 ? 'M' : 'L'}} ${{xS(i).toFixed(1)}} ${{yS(p.calibrated_layout_depth_m).toFixed(1)}}`).join(' ');

        return (
          <svg viewBox="0 0 600 185" style={{ width: '100%', height: '190px', background: 'var(--wm-surface-soft)', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
            <path d={pGov} fill="none" stroke="#0EA5E9" strokeWidth="2.5" />
            <path d={pCal} fill="none" stroke="#F43F5E" strokeWidth="3" />
          </svg>
        );
      }};

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">📡</div>
              <div>
                <div>Field Verifier Portal</div>
                <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Verifier: {{BOOT.user_name}}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              {ev && <span className="wm-pill mint">48h Rain: {{ev.raw_stage1.rain_48h_mm}} mm</span>}
              <a className="wm-btn" href="/login?role=utility">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          {toast && (
            <div style={{ position: 'fixed', bottom: '22px', right: '22px', zIndex: 60, background: '#0F172A', color: '#fff', padding: '12px 18px', borderRadius: '14px', fontSize: '13px', fontWeight: 700 }}>
              ✓ {{toast}}
            </div>
          )}

          <div className="wm-container">
            <div className="wm-grid-main">
              <div>
                <SpringCard style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>1. Assigned Colony / Ward</h3>
                  <input className="wm-input" style={{ marginBottom: '8px' }} placeholder="Search 91 locations..." value={query} onChange={(e) => setQuery(e.target.value)} />
                  <select className="wm-select" value={layoutId} onChange={(e) => setLayoutId(e.target.value)}>
                    {list.map((l) => <option key={l.id} value={l.id}>{{l.category === 'Featured Pilot' ? '★ ' : ''}}{{l.name}}</option>)}
                  </select>
                </SpringCard>

                <SpringCard delay={60} style={{ marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>2. Reference Well Depth Entry</h3>
                  <label className="wm-label">Today's Measured Depth (m bgl)</label>
                  <input className="wm-input" type="number" step="0.1" style={{ marginBottom: '8px' }} value={vDepth} onChange={(e) => setVDepth(e.target.value)} />
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '10px' }}>
                    <div>
                      <label className="wm-label">Previous Depth (m)</label>
                      <input className="wm-input" type="number" step="0.1" value={vLast} onChange={(e) => setVLast(e.target.value)} />
                    </div>
                    <div>
                      <label className="wm-label">Elapsed Days</label>
                      <select className="wm-select" value={vDays} onChange={(e) => setVDays(e.target.value)}>
                        <option value="7">7 days</option>
                        <option value="14">14 days</option>
                        <option value="30">30 days</option>
                      </select>
                    </div>
                  </div>
                  {ev?.groundwater_summary?.verifier_validation && (
                    <div style={{
                      padding: '9px 11px', borderRadius: '10px', fontSize: '12px', fontWeight: 600, marginBottom: '10px',
                      background: ev.groundwater_summary.verifier_validation.status === 'VERIFIED' ? 'var(--wm-mint-soft)' : 'var(--wm-melon-soft)',
                      color: ev.groundwater_summary.verifier_validation.status === 'VERIFIED' ? '#047857' : '#BE123C',
                    }}>
                      {{ev.groundwater_summary.verifier_validation.status}}: {{ev.groundwater_summary.verifier_validation.reason}}
                    </div>
                  )}
                  <SpringButton variant="primary" style={{ width: '100%' }} onClick={saveReading}>Verify & Update Calibration</SpringButton>
                </SpringCard>

                <SpringCard delay={110}>
                  <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '6px' }}>3. Verified Tanker Indent (55 LPCD)</h3>
                  {data && (
                    <div style={{ fontSize: '12px', color: '#0369A1', background: 'var(--wm-aqua-soft)', padding: '9px 11px', borderRadius: '10px', marginBottom: '10px', fontWeight: 600 }}>
                      Recommended: {{data.recommended_tanker.litres_per_day.toLocaleString()}} L/day ({{data.recommended_tanker.trips_10k}} trips) for {{data.recommended_tanker.affected_homes}} homes.
                    </div>
                  )}
                  <select className="wm-select" style={{ marginBottom: '10px' }} value={indentVol} onChange={(e) => setIndentVol(e.target.value)}>
                    <option value="10000">10,000 L (1 Tanker Trip)</option>
                    <option value="20000">20,000 L (2 Tanker Trips)</option>
                    <option value="30000">30,000 L (3 Tanker Trips)</option>
                  </select>
                  <SpringButton variant="mint" style={{ width: '100%' }} onClick={raiseIndent}>Send Verified Indent to Utility</SpringButton>
                </SpringCard>
              </div>

              <div>
                {ev && (
                  <>
                    <SpringCard style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <h2 style={{ fontSize: '18px', fontWeight: 800 }}>{{data.layout.name}}</h2>
                        <StatusBadge status={ev.scarcity_status} />
                      </div>
                      <p style={{ fontSize: '13px', color: 'var(--wm-muted)', marginBottom: '14px' }}>{{ev.diagnosis}}</p>

                      <div className="wm-grid-3">
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>LIVE CALIBRATED DEPTH</div>
                          <div style={{ fontSize: '21px', fontWeight: 800 }}>{{ev.groundwater_summary.live_calibrated_depth_m}} m</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Offset {{ev.raw_stage1.local_offset_m >= 0 ? '+' : ''}}{{ev.raw_stage1.local_offset_m}}m vs CGWB</div>
                        </div>
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>DEPLETION VELOCITY</div>
                          <div style={{ fontSize: '21px', fontWeight: 800 }}>{{ev.raw_stage1.depletion_velocity_m_per_week}} m/wk</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Deficit: {{ev.signals.signal_1_aquifer_stress.deficit_m}} m</div>
                        </div>
                        <div style={{ background: 'var(--wm-surface-soft)', padding: '12px', borderRadius: '14px', border: '1px solid var(--wm-border)' }}>
                          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--wm-muted)' }}>PUMP RUNWAY</div>
                          <div style={{ fontSize: '21px', fontWeight: 800 }}>{{ev.groundwater_summary.pump_runway.days !== null ? `${{ev.groundwater_summary.pump_runway.days}} d` : 'Stable'}}</div>
                          <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>{{ev.groundwater_summary.pump_runway.label}}</div>
                        </div>
                      </div>
                    </SpringCard>

                    <SpringCard delay={80} style={{ marginBottom: '16px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <h3 style={{ fontSize: '15px', fontWeight: 800 }}>7-Day 6-Hourly Calibrated Hydrograph</h3>
                        <span className="wm-pill aqua">CGWB: {{ev.groundwater_summary.matched_gov_station}} ({{ev.groundwater_summary.station_distance_km}} km)</span>
                      </div>
                      {renderHydrograph()}
                      <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)', marginTop: '6px', textAlign: 'center', fontWeight: 600 }}>
                        Blue: Raw CGWB 6-Hourly Sensor · Coral: Offset-Calibrated Colony Depth
                      </div>
                    </SpringCard>

                    <SpringCard delay={120}>
                      <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>3-Signal Scarcity & Fault Breakdown</h3>
                      {[
                        {{ title: 'Signal 1: Aquifer Stress (>2.5m Deficit or ≤1.5m Col)', active: ev.signals.signal_1_aquifer_stress.active, val: `Deficit: ${{ev.signals.signal_1_aquifer_stress.deficit_m}} m` }},
                        {{ title: 'Signal 2: Rapid Depletion (>0.5m/week)', active: ev.signals.signal_2_rapid_depletion.active, val: `Rate: ${{ev.signals.signal_2_rapid_depletion.velocity_m_per_week}} m/wk` }},
                        {{ title: 'Signal 3: Resident Shortage (≥30% Dry Homes)', active: ev.signals.signal_3_community_shortage.active, val: `Dry: ${{ev.signals.signal_3_community_shortage.dry_percentage}}%` }},
                      ].map((s) => (
                        <div key={s.title} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px', fontSize: '13px' }}>
                          <span style={{ fontWeight: 700 }}>{{s.active ? '⚠️' : '✓'}} {{s.title}}</span>
                          <StatusBadge status={s.active ? 'RED' : 'GREEN'} />
                        </div>
                      ))}
                    </SpringCard>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }}

    // -----------------------------------------------------------------------
    // VIEW 3: UTILITY & TANKER PORTAL (/utility)
    // -----------------------------------------------------------------------
    function UtilityApp() {{
      const [ov, setOv] = useState(null);
      const [destId, setDestId] = useState('wanadongri');
      const [depotId, setDepotId] = useState('AUTO');
      const [vol, setVol] = useState(10000);
      const [toast, setToast] = useState('');

      const showToast = (msg) => {{
        setToast(msg);
        setTimeout(() => setToast(''), 3200);
      }};

      const refresh = async () => {{
        const res = await fetch('/api/utility-overview');
        const d = await res.json();
        setOv(d);
      }};

      useEffect(() => {{ refresh(); }}, []);

      const dispatchNow = async () => {{
        const res = await fetch('/api/tanker-dispatch', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ layout_id: destId, depot_id: depotId, volume_l: Number(vol) }}),
        }});
        const d = await res.json();
        if (!res.ok) return showToast(d.error || 'Dispatch failed');
        showToast(`Dispatched ${{d.order.vehicle_no}} from ${{d.order.depot_name}}`);
        refresh();
      }};

      const dispatchExisting = async (orderId) => {{
        const res = await fetch('/api/tanker-dispatch', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ order_id: orderId, depot_id: 'AUTO' }}),
        }});
        const d = await res.json();
        if (!res.ok) return showToast(d.error || 'Dispatch failed');
        showToast(`Order ${{orderId}} dispatched!`);
        refresh();
      }};

      const markUnloaded = async (orderId) => {{
        await fetch('/api/tanker-status', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ order_id: orderId, status: 'UNLOADED' }}),
        }});
        showToast(`Order ${{orderId}} marked unloaded.`);
        refresh();
      }};

      const refillDepot = async (id) => {{
        await fetch('/api/depot-refill', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ depot_id: id }}),
        }});
        showToast('Depot stock & fleet refilled.');
        refresh();
      }};

      const resolveTicket = async (id) => {{
        await fetch('/api/ticket-resolve', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ ticket_id: id }}),
        }});
        showToast(`Ticket #${{id}} resolved.`);
        refresh();
      }};

      const selectedColony = ov?.priority_colonies?.find((c) => c.layout.id === destId);
      const isGreenZone = selectedColony?.evaluation?.scarcity_status === 'GREEN';

      return (
        <div>
          <nav className="wm-nav">
            <div className="wm-brand">
              <div className="wm-logo-drop">🚛</div>
              <div>
                <div>Utility & Tanker Operations</div>
                <div style={{ fontSize: '11px', color: 'var(--wm-muted)' }}>Operator: {{BOOT.user_name}}</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <a className="wm-btn" href="/login?role=citizen">Switch Role</a>
              <a className="wm-btn" href="/logout">Logout</a>
            </div>
          </nav>

          {toast && (
            <div style={{ position: 'fixed', bottom: '22px', right: '22px', zIndex: 60, background: '#0F172A', color: '#fff', padding: '12px 18px', borderRadius: '14px', fontSize: '13px', fontWeight: 700 }}>
              ✓ {{toast}}
            </div>
          )}

          {ov && (
            <div className="wm-container">
              <div className="wm-grid-main">
                <div>
                  <SpringCard style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>1. Tanker Dispatch Console</h3>
                    <label className="wm-label">Destination Colony</label>
                    <select className="wm-select" style={{ marginBottom: '8px' }} value={destId} onChange={(e) => setDestId(e.target.value)}>
                      {ov.priority_colonies.map((c) => (
                        <option key={c.layout.id} value={c.layout.id}>
                          {{c.layout.name}} [{{c.evaluation.scarcity_status}} · Runway {{c.evaluation.groundwater_summary.pump_runway.days ?? 'Stable'}}d]
                        </option>
                      ))}
                    </select>

                    {isGreenZone && (
                      <div style={{ background: 'var(--wm-amber-soft)', color: '#B45309', padding: '8px 11px', borderRadius: '10px', fontSize: '12px', fontWeight: 700, marginBottom: '8px' }}>
                        ⚠️ Note: Aquifer status is GREEN here. Check Surface Leak Tickets before sending emergency tankers.
                      </div>
                    )}

                    <label className="wm-label">Source Depot</label>
                    <select className="wm-select" style={{ marginBottom: '8px' }} value={depotId} onChange={(e) => setDepotId(e.target.value)}>
                      <option value="AUTO">Auto-Select Nearest Depot with Stock</option>
                      {ov.depots.map((d) => <option key={d.id} value={d.id}>{{d.name}} ({{d.current_stock_l.toLocaleString()}} L)</option>)}
                    </select>

                    <label className="wm-label">Tanker Volume</label>
                    <select className="wm-select" style={{ marginBottom: '12px' }} value={vol} onChange={(e) => setVol(e.target.value)}>
                      <option value="5000">5,000 L Tanker</option>
                      <option value="10000">10,000 L Tanker</option>
                      <option value="15000">15,000 L Tanker</option>
                    </select>

                    <SpringButton variant="primary" style={{ width: '100%' }} onClick={dispatchNow}>Assign & Dispatch Tanker</SpringButton>
                  </SpringCard>

                  <SpringCard delay={60} style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>2. Tanker Depots & Fleet Stock</h3>
                    {ov.depots.map((d) => (
                      <div key={d.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '13px' }}>{{d.name}}</div>
                          <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)' }}>Stock: {{d.current_stock_l.toLocaleString()}} / {{d.max_capacity_l.toLocaleString()}} L · Trucks: {{d.trucks_ready}}/{{d.trucks_total}}</div>
                        </div>
                        <SpringButton onClick={() => refillDepot(d.id)}>+ Refill</SpringButton>
                      </div>
                    ))}
                  </SpringCard>

                  <SpringCard delay={110}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>3. Surface Leak & Valve Maintenance Queue</h3>
                    {ov.tickets.map((t) => (
                      <div key={t.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px', padding: '10px 12px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '12.5px' }}>#{{t.id}} · {{t.issue_type}} @ {{t.layout_name}}</div>
                          <div style={{ fontSize: '11.5px', color: 'var(--wm-muted)' }}>{{t.description}}</div>
                        </div>
                        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          <StatusBadge status={t.status} />
                          {t.status !== 'RESOLVED' && <SpringButton variant="mint" onClick={() => resolveTicket(t.id)}>Resolve</SpringButton>}
                        </div>
                      </div>
                    ))}
                  </SpringCard>
                </div>

                <div>
                  <SpringCard style={{ marginBottom: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <h3 style={{ fontSize: '16px', fontWeight: 800 }}>4. Nagpur Scarcity & Live Tanker Route Map</h3>
                      <span className="wm-pill aqua">Live Fleet & Colony Stress</span>
                    </div>
                    <NagpurMap
                      deps={[ov]}
                      renderLayers={(map, group) => {{
                        ov.priority_colonies.forEach((c) => {{
                          const st = c.evaluation.scarcity_status;
                          const col = st === 'RED' ? '#F43F5E' : (st === 'YELLOW' ? '#F59E0B' : '#10B981');
                          L.circleMarker([c.layout.lat, c.layout.lon], {{ radius: 9, color: col, fillColor: col, fillOpacity: 0.85 }})
                            .bindPopup(`<b>${{c.layout.name}}</b><br>Status: ${{st}}<br>Depth: ${{c.evaluation.groundwater_summary.live_calibrated_depth_m}} m`).addTo(group);
                        }});
                        ov.depots.forEach((d) => {{
                          L.marker([d.lat, d.lon]).bindPopup(`<b>🚛 ${{d.name}}</b><br>Stock: ${{d.current_stock_l.toLocaleString()}} L`).addTo(group);
                        }});
                        ov.tanker_orders.forEach((o) => {{
                          if (o.status === 'DISPATCHED' || o.status === 'UNLOADED') {{
                            const dep = ov.depots.find((d) => d.id === o.depot_id);
                            const dest = ov.priority_colonies.find((c) => c.layout.id === o.layout_id);
                            if (dep && dest) {{
                              L.polyline([[dep.lat, dep.lon], [dest.layout.lat, dest.layout.lon]], {{ color: '#0284C7', weight: 4, dashArray: '8,8' }}).addTo(group);
                            }}
                          }}
                        }});
                      }}
                    />
                  </SpringCard>

                  <SpringCard delay={70} style={{ marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>5. Verified Tanker Indents & Active Deliveries</h3>
                    {ov.tanker_orders.map((o) => (
                      <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', padding: '11px 13px', borderRadius: '12px', background: 'var(--wm-surface-soft)', border: '1px solid var(--wm-border)', marginBottom: '8px' }}>
                        <div>
                          <div style={{ fontWeight: 800, fontSize: '13.5px' }}>{{o.id}} · {{o.layout_name}} ({{o.volume_l.toLocaleString()}} L)</div>
                          <div style={{ fontSize: '12px', color: 'var(--wm-muted)' }}>Verified by {{o.verified_by}} · {{o.vehicle_no || 'Pending Truck'}} ({{o.depot_name || 'Unassigned'}})</div>
                        </div>
                        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          <StatusBadge status={o.status} />
                          {o.status === 'PENDING_DISPATCH' && <SpringButton variant="primary" onClick={() => dispatchExisting(o.id)}>Dispatch</SpringButton>}
                          {o.status === 'DISPATCHED' && <SpringButton variant="mint" onClick={() => markUnloaded(o.id)}>Mark Unloaded</SpringButton>}
                        </div>
                      </div>
                    ))}
                  </SpringCard>

                  <SpringCard delay={120}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, marginBottom: '10px' }}>6. Priority Scarcity Triage Table</h3>
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
                      <tbody>
                        {ov.priority_colonies.map((c) => {{
                          const e = c.evaluation;
                          return (
                            <tr key={c.layout.id}>
                              <td style={{ fontWeight: 700 }}>{{c.layout.name}}</td>
                              <td>{{e.groundwater_summary.live_calibrated_depth_m}} m</td>
                              <td>{{e.groundwater_summary.pump_runway.days ?? 'Stable'}} d</td>
                              <td>{{e.signals.signal_3_community_shortage.dry_percentage}}%</td>
                              <td>{{e.raw_stage1.rain_48h_mm}} mm</td>
                              <td><StatusBadge status={e.scarcity_status} /></td>
                            </tr>
                          );
                        }})}
                      </tbody>
                    </table>
                  </SpringCard>
                </div>
              </div>
            </div>
          )}
        </div>
      );
    }}

    const root = createRoot(document.getElementById('root'));
    if (MODE === 'citizen') root.render(<CitizenApp />);
    else if (MODE === 'verifier') root.render(<VerifierApp />);
    else if (MODE === 'utility') root.render(<UtilityApp />);
    else root.render(<LandingLoginApp />);
  </script>
</body>
</html>"""
    def _normalize_section(text: str) -> str:
        text = text.replace("{{", "{").replace("}}", "}")
        out, i, n = [], 0, len(text)
        while i < n:
            idx = text.find("style={", i)
            if idx == -1:
                out.append(text[i:])
                break
            out.append(text[i:idx])
            j = idx + 7
            depth = 1
            while j < n and depth > 0:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                j += 1
            out.append("style={{" + text[idx + 7 : j - 1] + "}}")
            i = j
        return "".join(out)

    head, sep1, rest = html.partition("// WATERMELON UI")
    mid, sep2, tail = rest.partition("// VIEW 0: PUBLIC OVERVIEW")
    html = (
        head.replace("{{", "{").replace("}}", "}")
        + sep1
        + mid
        + sep2
        + _normalize_section(tail)
    )
    return (
        html
        .replace("__PAGE_TITLE__", title)
        .replace("__PAGE_MODE__", page_mode)
        .replace("__BOOTSTRAP_JSON__", bootstrap_json)
    )
    


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
            boot = json.dumps({"preselect_role": pre_role, "role_defaults": ROLE_META})
            self._send_html(build_react_page("JalSetu Nagpur — Water Scarcity & Recharge Network", "login", boot))
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
            boot = json.dumps({
                "user_name": sess["name"],
                "layouts": ALL_LAYOUTS,
                "talukas": NAGPUR_TALUKAS,
                "depots": STATE["depots"],
            })
            self._send_html(build_react_page("Citizen Portal — JalSetu Nagpur", "citizen", boot))
            return

        if url.path == "/verifier":
            if not sess or sess["role"] != "verifier":
                self._redirect("/login?role=verifier")
                return
            boot = json.dumps({
                "user_name": sess["name"],
                "layouts": ALL_LAYOUTS,
            })
            self._send_html(build_react_page("Field Verifier Portal — JalSetu Nagpur", "verifier", boot))
            return

        if url.path == "/utility":
            if not sess or sess["role"] != "utility":
                self._redirect("/login?role=utility")
                return
            boot = json.dumps({"user_name": sess["name"]})
            self._send_html(build_react_page("Utility & Tanker Operations — JalSetu Nagpur", "utility", boot))
            return

        if url.path == "/api/public-summary":
            featured_evals = [evaluate_layout_full(x["id"]) for x in FEATURED_LAYOUTS]
            stressed = sum(1 for x in featured_evals if x["evaluation"]["scarcity_status"] in ("RED", "YELLOW"))
            dry_total = sum(x["crowd"]["counts"].get("BOREWELL_DRY", 0) for x in featured_evals)
            trucks_ready = sum(d["trucks_ready"] for d in STATE["depots"])
            rain_sample = featured_evals[0]["evaluation"]["raw_stage1"]["rain_48h_mm"] if featured_evals else 0
            self._send_json(200, {
                "total_locations": len(ALL_LAYOUTS),
                "stressed_zones": stressed,
                "dry_households": dry_total,
                "trucks_ready": trucks_ready,
                "total_orders": len(STATE["tanker_orders"]),
                "rain_48h_mm": rain_sample,
            })
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
    print(f" JalSetu Nagpur — Watermelon UI + React Spring ({len(ALL_LAYOUTS)} locations)")
    print(f" Open Portal: http://127.0.0.1:{PORT}/login")
    print(" Press Ctrl+C to stop.")
    print("=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    run_server()