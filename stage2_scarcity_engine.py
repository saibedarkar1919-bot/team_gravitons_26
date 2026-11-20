from datetime import datetime
from stage1_groundwater import Stage1GroundwaterEngine


class ResidentCrowdAggregator:
    """Aggregates daily household crowd check-ins for a residential layout."""

    @staticmethod
    def aggregate_checkins(total_households: int, checkins: dict[str, int]) -> dict:
        normal_count = checkins.get("NORMAL", 0)
        low_p_count = checkins.get("LOW_PRESSURE", 0)
        dry_count = checkins.get("BOREWELL_DRY", 0)

        total_reported = normal_count + low_p_count + dry_count
        effective_total = max(total_households, total_reported, 1)

        dry_pct = round((dry_count / effective_total) * 100.0, 1)
        low_p_pct = round((low_p_count / effective_total) * 100.0, 1)

        return {
            "total_registered_households": total_households,
            "total_reporting_today": total_reported,
            "dry_reports_count": dry_count,
            "dry_percentage": dry_pct,
            "low_pressure_percentage": low_p_pct,
            "is_community_shortage_critical": dry_pct >= 30.0,
        }


class Stage2ScarcityEngine:
    """Fuses Stage 1 physical groundwater metrics with Stage 2 resident crowd inputs."""

    def __init__(self, gw_engine: Stage1GroundwaterEngine | None = None):
        self.gw_engine = gw_engine or Stage1GroundwaterEngine()

    def evaluate_layout_scarcity(
        self,
        layout_name: str,
        lat: float,
        lon: float,
        aquifer_type: str,
        avg_pump_depth_m: float,
        total_households: int,
        crowd_checkins: dict[str, int],
        verifier_manual_depth_m: float | None = None,
        last_recorded_depth_m: float | None = None,
        days_since_last_record: int = 7,
        current_offset_m: float = 0.0,
        rain_48h_mm: float = 0.0,
        target_month: int | None = None,
    ) -> dict:
        gw_metrics = self.gw_engine.run_stage1_for_layout(
            layout_name=layout_name,
            lat=lat,
            lon=lon,
            aquifer_type=aquifer_type,
            avg_pump_depth_m=avg_pump_depth_m,
            verifier_manual_depth_m=verifier_manual_depth_m,
            last_recorded_depth_m=last_recorded_depth_m,
            days_since_last_record=days_since_last_record,
            current_offset_m=current_offset_m,
            rain_48h_mm=rain_48h_mm,
            target_month=target_month,
        )

        crowd_metrics = ResidentCrowdAggregator.aggregate_checkins(
            total_households=total_households, checkins=crowd_checkins
        )

        deficit_m = gw_metrics["seasonal_deficit_m"]
        velocity_m = gw_metrics["depletion_velocity_m_per_week"]
        remaining_col_m = gw_metrics["pump_runway"]["remaining_water_column_m"]
        dry_pct = crowd_metrics["dry_percentage"]

        # Signal 1 triggers on true offset-adjusted seasonal deficit > 2.5m OR critically low water column above pump (<= 1.5m)
        signal_1_stress = (deficit_m > 2.5) or (remaining_col_m <= 1.5)
        signal_2_velocity = velocity_m > 0.5
        signal_3_crowd = dry_pct >= 30.0

        active_signals = []
        if signal_1_stress:
            if remaining_col_m <= 1.5:
                active_signals.append(
                    f"Pump Intake Critical (Only {remaining_col_m:.1f}m water column above pump)"
                )
            else:
                active_signals.append(
                    f"Aquifer Deficit Critical ({deficit_m:+.2f}m vs offset-adjusted 5-yr seasonal normal)"
                )
        if signal_2_velocity:
            active_signals.append(
                f"Depletion Velocity High ({velocity_m:.2f}m/week drop rate)"
            )
        if signal_3_crowd:
            active_signals.append(
                f"Community Shortage Critical ({dry_pct:.1f}% households report dry borewells)"
            )

        active_signal_count = len(active_signals)
        anomaly_detected = False

        if signal_3_crowd and not signal_1_stress and not signal_2_velocity:
            scarcity_status = "YELLOW"
            diagnosis = (
                "SURFACE_DISTRIBUTION_FAILURE: High dry-tap reports despite healthy local aquifer. "
                "Inspect local municipal feeder line, pump motor power, or society valves."
            )
            anomaly_detected = True
        elif active_signal_count >= 2 or signal_3_crowd:
            scarcity_status = "RED"
            if signal_3_crowd:
                diagnosis = (
                    "CRITICAL_COMMUNITY_WATER_SCARCITY: Severe aquifer depletion aligns with widespread "
                    "dry-borewell reports. Emergency tanker allocation unlocked."
                )
            else:
                diagnosis = (
                    "PROACTIVE_AQUIFER_DEPLETION_ALERT: Both underground signals (5-yr deficit + rapid weekly drop) "
                    "are critical. Initiate water rationing and pre-stage tanker support before pumps run dry."
                )
        elif active_signal_count == 1 or crowd_metrics["low_pressure_percentage"] >= 25.0:
            scarcity_status = "YELLOW"
            diagnosis = (
                "MODERATE_SCARCITY_WARNING: Early aquifer stress or emerging pressure drop detected. "
                "Issue voluntary conservation advisory."
            )
        else:
            scarcity_status = "GREEN"
            diagnosis = "NORMAL_WATER_SUPPLY: Aquifer levels and community reports are within safe thresholds."

        return {
            "layout_name": layout_name,
            "evaluated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scarcity_status": scarcity_status,
            "diagnosis": diagnosis,
            "signals": {
                "signal_1_aquifer_stress": {
                    "active": signal_1_stress,
                    "deficit_m": deficit_m,
                    "threshold_m": 2.5,
                },
                "signal_2_rapid_depletion": {
                    "active": signal_2_velocity,
                    "velocity_m_per_week": velocity_m,
                    "threshold_m_per_week": 0.5,
                },
                "signal_3_community_shortage": {
                    "active": signal_3_crowd,
                    "dry_percentage": dry_pct,
                    "threshold_percentage": 30.0,
                },
                "active_signals_count": active_signal_count,
                "active_signal_details": active_signals,
            },
            "groundwater_summary": {
                "live_calibrated_depth_m": gw_metrics["live_calibrated_depth_m"],
                "historical_normal_depth_m": gw_metrics["seasonal_historical_avg_m"],
                "pump_runway": gw_metrics["pump_runway"],
                "matched_gov_station": gw_metrics["matched_gov_station"],
                "station_distance_km": gw_metrics["station_distance_km"],
                "verifier_validation": gw_metrics["verifier_validation"],
            },
            "crowd_summary": crowd_metrics,
            "anomaly_detected": anomaly_detected,
            "raw_stage1": gw_metrics,
        }