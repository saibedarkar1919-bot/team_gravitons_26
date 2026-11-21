"""
jalsetu_backend.py
------------------
Backend business logic, Nagpur CGWB dataset loader, persistent JSON state,
3-signal scarcity evaluation wrapper, 14-taluka RWH calculator, and tanker dispatch engine.
Separated cleanly from the Watermelon UI frontend (`watermelon_ui.py`).
"""

from datetime import datetime
import hashlib
import json
import math
import os
import secrets
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from stage2_scarcity_engine import Stage2ScarcityEngine

PORT = 8000
PROCESSED_DIR = (
    os.path.join(BASE_DIR, "processed")
    if os.path.exists(os.path.join(BASE_DIR, "processed"))
    else r"D:\hackumbh\processed"
)
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
            "citizen:aarav deshmukh": {
                "name": "Aarav Deshmukh",
                "role": "citizen",
                "pw_hash": hashlib.sha256(b"citizen123").hexdigest(),
            },
            "verifier:rajesh kulkarni": {
                "name": "Rajesh Kulkarni",
                "role": "verifier",
                "pw_hash": hashlib.sha256(b"verifier123").hexdigest(),
            },
            "utility:nmc dispatch desk": {
                "name": "NMC Dispatch Desk",
                "role": "utility",
                "pw_hash": hashlib.sha256(b"utility123").hexdigest(),
            },
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


def save_unified_state(state: dict):
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    with open(UNIFIED_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


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
    affected_homes = (
        max(dry_homes, int(round(layout["total_households"] * 0.25)))
        if eval_out["scarcity_status"] == "RED"
        else dry_homes
    )
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
# CLEAN API SERVICE LAYER (Called by HTTP router in watermelon_ui.py)
# ---------------------------------------------------------------------------
def api_public_summary() -> tuple[int, dict]:
    featured_evals = [evaluate_layout_full(x["id"]) for x in FEATURED_LAYOUTS]
    stressed = sum(1 for x in featured_evals if x["evaluation"]["scarcity_status"] in ("RED", "YELLOW"))
    dry_total = sum(x["crowd"]["counts"].get("BOREWELL_DRY", 0) for x in featured_evals)
    trucks_ready = sum(d["trucks_ready"] for d in STATE["depots"])
    rain_sample = featured_evals[0]["evaluation"]["raw_stage1"]["rain_48h_mm"] if featured_evals else 0
    return 200, {
        "total_locations": len(ALL_LAYOUTS),
        "stressed_zones": stressed,
        "dry_households": dry_total,
        "trucks_ready": trucks_ready,
        "total_orders": len(STATE["tanker_orders"]),
        "rain_48h_mm": rain_sample,
    }


def api_colony_detail(col_id: str) -> tuple[int, dict]:
    if col_id not in LAYOUT_INDEX:
        return 404, {"error": "Unknown colony"}
    full = evaluate_layout_full(col_id)
    full["tanker_orders"] = [o for o in STATE["tanker_orders"] if o["layout_id"] == col_id]
    full["tickets"] = [t for t in STATE["tickets"] if t["layout_id"] == col_id]
    full["rwh_checks"] = STATE["rwh_checks_by_layout"].get(col_id, {})
    return 200, full


def api_utility_overview() -> tuple[int, dict]:
    ids_to_eval = [x["id"] for x in FEATURED_LAYOUTS]
    for o in STATE["tanker_orders"]:
        if o["layout_id"] not in ids_to_eval and o["layout_id"] in LAYOUT_INDEX:
            ids_to_eval.append(o["layout_id"])
    for t in STATE["tickets"]:
        if t["layout_id"] not in ids_to_eval and t["layout_id"] in LAYOUT_INDEX:
            ids_to_eval.append(t["layout_id"])

    priority = [evaluate_layout_full(cid) for cid in ids_to_eval]
    return 200, {
        "priority_colonies": priority,
        "depots": STATE["depots"],
        "tanker_orders": STATE["tanker_orders"],
        "tickets": STATE["tickets"],
    }


def api_auth(is_register: bool, data: dict) -> tuple[int, dict, str | None]:
    role = data.get("role", "citizen")
    name = str(data.get("name", "")).strip()
    password = str(data.get("password", ""))
    if role not in ROLE_META or not name or not password:
        return 400, {"error": "Name, password, and role are required."}, None

    user_key = f"{role}:{name.lower()}"
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    if is_register:
        STATE["users"][user_key] = {"name": name, "role": role, "pw_hash": pw_hash}
        save_unified_state(STATE)
    else:
        rec = STATE["users"].get(user_key)
        if not rec or rec["pw_hash"] != pw_hash:
            return 401, {"error": "Invalid name or password for selected portal."}, None

    token = secrets.token_hex(24)
    SESSIONS[token] = {"name": name, "role": role}
    return (
        200,
        {"ok": True, "redirect": ROLE_META[role]["home"]},
        f"nagpur_session={token}; Path=/; HttpOnly",
    )


def api_checkin(data: dict, sess: dict | None) -> tuple[int, dict]:
    col_id = data.get("layout_id")
    if col_id not in LAYOUT_INDEX:
        return 404, {"error": "Unknown colony"}
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
    return 200, {"ok": True}


def api_create_ticket(data: dict, sess: dict | None) -> tuple[int, dict]:
    col_id = data.get("layout_id")
    if col_id not in LAYOUT_INDEX:
        return 404, {"error": "Unknown colony"}
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
    return 200, {"ok": True, "ticket_id": tid}


def api_resolve_ticket(data: dict) -> tuple[int, dict]:
    tid = data.get("ticket_id")
    for t in STATE["tickets"]:
        if t["id"] == tid:
            t["status"] = "RESOLVED"
    save_unified_state(STATE)
    return 200, {"ok": True}


def api_rwh_check(data: dict) -> tuple[int, dict]:
    col_id = data.get("layout_id")
    key = data.get("key")
    if col_id and key:
        STATE["rwh_checks_by_layout"].setdefault(col_id, {})[key] = bool(data.get("checked"))
        save_unified_state(STATE)
    return 200, {"ok": True}


def api_verifier_update(data: dict, sess: dict | None) -> tuple[int, dict]:
    col_id = data.get("layout_id")
    if col_id not in LAYOUT_INDEX:
        return 404, {"error": "Unknown colony"}
    vrec = get_verifier_record(col_id)
    vrec["verifier_depth_m"] = float(data.get("verifier_depth_m", vrec["verifier_depth_m"]))
    vrec["last_recorded_depth_m"] = float(data.get("last_recorded_depth_m", vrec["last_recorded_depth_m"]))
    vrec["days_since_last"] = int(data.get("days_since_last", 7))
    vrec["verified_by"] = sess["name"] if sess else "Verifier"
    vrec["updated_at"] = datetime.now().strftime("%I:%M %p")
    save_unified_state(STATE)
    return 200, {"ok": True}


def api_tanker_indent(data: dict, sess: dict | None) -> tuple[int, dict]:
    col_id = data.get("layout_id")
    if col_id not in LAYOUT_INDEX:
        return 404, {"error": "Unknown colony"}
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
    return 200, {"ok": True, "order": order}


def api_tanker_dispatch(data: dict, sess: dict | None) -> tuple[int, dict]:
    order_id = data.get("order_id")
    depot_choice = data.get("depot_id", "AUTO")
    target_order = next((o for o in STATE["tanker_orders"] if o["id"] == order_id), None)

    if target_order is None:
        col_id = data.get("layout_id")
        if col_id not in LAYOUT_INDEX:
            return 404, {"error": "Unknown colony"}
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
        return 400, {"error": "No depot has sufficient water stock and an idle tanker."}

    depot["current_stock_l"] -= vol
    depot["trucks_ready"] -= 1
    target_order["status"] = "DISPATCHED"
    target_order["depot_id"] = depot["id"]
    target_order["depot_name"] = depot["name"]
    target_order["distance_km"] = haversine_km(dest["lat"], dest["lon"], depot["lat"], depot["lon"])
    target_order["vehicle_no"] = f"MH-31-TK-{100 + (int(datetime.now().timestamp()) % 899)}"
    target_order["updated_at"] = datetime.now().strftime("%I:%M %p")
    save_unified_state(STATE)
    return 200, {"ok": True, "order": target_order}


def api_tanker_status(data: dict) -> tuple[int, dict]:
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
    return 200, {"ok": True}


def api_depot_refill(data: dict) -> tuple[int, dict]:
    dep_id = data.get("depot_id")
    for d in STATE["depots"]:
        if d["id"] == dep_id:
            d["current_stock_l"] = d["max_capacity_l"]
            d["trucks_ready"] = d["trucks_total"]
    save_unified_state(STATE)
    return 200, {"ok": True}
