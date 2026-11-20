from datetime import datetime
import json
import math
import os
from weather_service import get_48h_rainfall_mm

PROCESSED_DIR = r"D:\hackumbh\processed"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = (
        math.sin(dp / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    )
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_timestamp(ts: str) -> datetime | None:
    for fmt in ("%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M", "%d-%m-%Y"):
        try:
            return datetime.strptime(ts.strip(), fmt)
        except ValueError:
            continue
    return None


class Stage1GroundwaterEngine:

    def __init__(self, processed_dir: str = PROCESSED_DIR):
        tel_path = os.path.join(processed_dir, "nagpur_telemetry_6hr.json")
        qtr_path = os.path.join(processed_dir, "nagpur_quarterly.json")

        with open(tel_path, "r", encoding="utf-8") as f:
            raw_telemetry = json.load(f)

        with open(qtr_path, "r", encoding="utf-8") as f:
            raw_quarterly = json.load(f)

        self.quarterly_rows = []
        for row in raw_quarterly:
            self.quarterly_rows.append({
                "station": row.get("station", ""),
                "lat": row["lat"],
                "lon": row["lon"],
                "depth_m": row["depth_m"],
                "dt": parse_timestamp(row.get("timestamp", "")),
            })

        self.telemetry_by_station: dict[str, list[dict]] = {}
        for row in raw_telemetry:
            st = row["station"]
            if st not in self.telemetry_by_station:
                self.telemetry_by_station[st] = []
            dt = parse_timestamp(row.get("timestamp", ""))
            self.telemetry_by_station[st].append({
                "dt": dt or datetime.min,
                "timestamp": row.get("timestamp", ""),
                "depth_m": row["depth_m"],
                "lat": row["lat"],
                "lon": row["lon"],
            })

        self.station_summaries: list[dict] = []
        for name, series in self.telemetry_by_station.items():
            series.sort(key=lambda x: x["dt"])
            latest = series[-1]
            self.station_summaries.append({
                "station": name,
                "lat": latest["lat"],
                "lon": latest["lon"],
                "latest_depth_m": latest["depth_m"],
                "latest_timestamp": latest["timestamp"],
                "total_points": len(series),
            })

    def list_telemetry_stations(self) -> list[dict]:
        return self.station_summaries

    def find_nearest_station(self, lat: float, lon: float) -> dict:
        nearest = min(
            self.station_summaries,
            key=lambda s: haversine_km(lat, lon, s["lat"], s["lon"]),
        )
        dist = round(haversine_km(lat, lon, nearest["lat"], nearest["lon"]), 2)
        return {**nearest, "distance_km": dist}

    def get_seasonal_baseline_m(
        self, lat: float, lon: float, target_month: int, radius_km: float = 25.0
    ) -> float:
        nearby_depths = []
        fallback_depths = []

        for row in self.quarterly_rows:
            dist = haversine_km(lat, lon, row["lat"], row["lon"])
            if dist <= radius_km:
                fallback_depths.append(row["depth_m"])
                if row["dt"]:
                    m_diff = min(
                        abs(row["dt"].month - target_month),
                        12 - abs(row["dt"].month - target_month),
                    )
                    if m_diff <= 1:
                        nearby_depths.append(row["depth_m"])

        pool = nearby_depths if nearby_depths else fallback_depths
        if not pool:
            return 12.0
        return round(sum(pool) / len(pool), 2)

    def get_station_recent_series(
        self, station_name: str, limit: int = 28
    ) -> list[dict]:
        series = self.telemetry_by_station.get(station_name, [])
        recent = series[-limit:]
        return [
            {
                "timestamp": pt["timestamp"],
                "gov_depth_m": pt["depth_m"],
                "dt": pt["dt"],
            }
            for pt in recent
        ]

    def validate_verifier_reading(
        self,
        new_depth_m: float,
        last_recorded_depth_m: float | None,
        rain_48h_mm: float,
        days_since_last_record: int = 7,
    ) -> dict:
        if new_depth_m <= 0:
            return {
                "status": "FLAGGED",
                "reason": "Depth below ground level must be positive (m bgl).",
            }

        if last_recorded_depth_m is None:
            return {
                "status": "VERIFIED",
                "reason": "Initial layout well baseline recorded.",
            }

        delta = new_depth_m - last_recorded_depth_m
        weeks_elapsed = max(days_since_last_record / 7.0, 1.0)
        max_allowed_drop = round(2.5 * weeks_elapsed, 2)

        if delta < -2.0 and rain_48h_mm < 15.0:
            return {
                "status": "FLAGGED",
                "reason": (
                    f"Well rose {abs(delta):.2f}m with only {rain_48h_mm}mm live 48h rain."
                ),
            }

        if delta > max_allowed_drop:
            return {
                "status": "FLAGGED",
                "reason": (
                    f"Sudden {delta:.2f}m drop over {days_since_last_record}d exceeds threshold ({max_allowed_drop}m); re-check tape."
                ),
            }

        return {
            "status": "VERIFIED",
            "reason": f"Passed drift ({days_since_last_record}d) & live 48h rain ({rain_48h_mm}mm) check.",
        }

    def run_stage1_for_layout(
        self,
        layout_name: str,
        lat: float,
        lon: float,
        aquifer_type: str,
        avg_pump_depth_m: float,
        verifier_manual_depth_m: float | None = None,
        last_recorded_depth_m: float | None = None,
        days_since_last_record: int = 7,
        current_offset_m: float = 0.0,
        rain_48h_mm: float | None = None,
        target_month: int | None = None,
        telemetry_window_points: int = 28,
    ) -> dict:
        # Automatically fetch live 48-hour rainfall from Open-Meteo if not overridden
        if rain_48h_mm is None:
            weather = get_48h_rainfall_mm(lat, lon)
            effective_rain_mm = weather["rain_48h_mm"]
            rainfall_source = weather["source"]
        else:
            effective_rain_mm = float(rain_48h_mm)
            rainfall_source = "Manual Override"

        month_to_use = target_month or datetime.now().month
        station = self.find_nearest_station(lat, lon)
        series = self.get_station_recent_series(station["station"], limit=telemetry_window_points)
        latest_gov_depth = series[-1]["gov_depth_m"] if series else station["latest_depth_m"]
        regional_historical_avg_m = self.get_seasonal_baseline_m(lat, lon, month_to_use)

        validation = None
        offset_m = current_offset_m

        if verifier_manual_depth_m is not None:
            validation = self.validate_verifier_reading(
                new_depth_m=verifier_manual_depth_m,
                last_recorded_depth_m=last_recorded_depth_m,
                rain_48h_mm=effective_rain_mm,
                days_since_last_record=days_since_last_record,
            )
            if validation["status"] == "VERIFIED":
                offset_m = round(verifier_manual_depth_m - latest_gov_depth, 2)
            elif last_recorded_depth_m is not None:
                offset_m = round(last_recorded_depth_m - latest_gov_depth, 2)

        calibrated_series = [
            {
                "timestamp": pt["timestamp"],
                "gov_depth_m": pt["gov_depth_m"],
                "calibrated_layout_depth_m": round(pt["gov_depth_m"] + offset_m, 2),
            }
            for pt in series
        ]

        live_depth = (
            calibrated_series[-1]["calibrated_layout_depth_m"]
            if calibrated_series
            else round(latest_gov_depth + offset_m, 2)
        )

        telemetry_drop = (
            round(series[-1]["gov_depth_m"] - series[0]["gov_depth_m"], 2)
            if len(series) >= 2
            else 0.0
        )

        local_extra_drawdown_m = 0.0
        if (
            verifier_manual_depth_m is not None
            and last_recorded_depth_m is not None
            and validation
            and validation["status"] == "VERIFIED"
        ):
            days_gap = max(int(days_since_last_record), 1)
            total_change = verifier_manual_depth_m - last_recorded_depth_m
            weekly_velocity_m = round((total_change / days_gap) * 7.0, 2)
            local_extra_drawdown_m = round(max(0.0, total_change - max(0.0, telemetry_drop)), 2)
        elif len(series) >= 2:
            dt_start = series[0]["dt"]
            dt_end = series[-1]["dt"]
            span_days = (dt_end - dt_start).total_seconds() / 86400.0 if dt_end > dt_start else 7.0
            span_days = max(span_days, 1.0)
            weekly_velocity_m = round((telemetry_drop / span_days) * 7.0, 2)
        else:
            weekly_velocity_m = 0.0

        regional_anomaly_m = round(latest_gov_depth - regional_historical_avg_m, 2)
        true_seasonal_deficit_m = round(regional_anomaly_m + local_extra_drawdown_m, 2)
        local_expected_normal_m = round(live_depth - true_seasonal_deficit_m, 2)

        daily_drop_m = weekly_velocity_m / 7.0
        remaining_column_m = round(avg_pump_depth_m - live_depth, 2)

        if remaining_column_m <= 0:
            est_runway_days = 0
            runway_status = "DRY"
            runway_label = "Pump Dry / Below Intake (0 days)"
        elif daily_drop_m > 0.01:
            est_runway_days = int(round(remaining_column_m / daily_drop_m))
            runway_status = "CRITICAL" if est_runway_days < 30 else "DEPLETING"
            runway_label = f"{est_runway_days} days remaining ({daily_drop_m * 100:.1f} cm/day drop)"
        else:
            est_runway_days = None
            runway_status = "STABLE"
            runway_label = "Stable / Recharging (> 180 days)"

        return {
            "layout_name": layout_name,
            "aquifer_type": aquifer_type,
            "matched_gov_station": station["station"],
            "station_distance_km": station["distance_km"],
            "rain_48h_mm": effective_rain_mm,
            "rainfall_source": rainfall_source,
            "verifier_validation": validation,
            "local_offset_m": offset_m,
            "live_calibrated_depth_m": live_depth,
            "regional_historical_avg_m": regional_historical_avg_m,
            "seasonal_historical_avg_m": local_expected_normal_m,
            "regional_anomaly_m": regional_anomaly_m,
            "local_drawdown_anomaly_m": local_extra_drawdown_m,
            "seasonal_deficit_m": true_seasonal_deficit_m,
            "depletion_velocity_m_per_week": weekly_velocity_m,
            "estimated_pump_runway_days": est_runway_days if est_runway_days is not None else 999,
            "pump_runway": {
                "remaining_water_column_m": remaining_column_m,
                "days": est_runway_days,
                "status": runway_status,
                "label": runway_label,
            },
            "calibrated_series": calibrated_series,
        }