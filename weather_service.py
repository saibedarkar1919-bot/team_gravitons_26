from datetime import datetime, timedelta
import json
import urllib.parse
import urllib.request

# In-memory cache: {(rounded_lat, rounded_lon): (expires_at, rain_48h_mm, source_label)}
_RAIN_CACHE: dict[tuple[float, float], tuple[datetime, float, str]] = {}
CACHE_TTL_MINUTES = 30


def get_48h_rainfall_mm(lat: float, lon: float, timeout_sec: float = 3.0) -> dict:
    """
    Fetches real 48-hour precipitation sum (mm) for a Nagpur GPS coordinate using Open-Meteo.
    Falls back cleanly to 0.0 mm if offline so the dashboard never blocks.
    """
    key = (round(float(lat), 3), round(float(lon), 3))
    now = datetime.now()

    if key in _RAIN_CACHE:
        expires_at, cached_mm, cached_src = _RAIN_CACHE[key]
        if now < expires_at:
            return {"rain_48h_mm": cached_mm, "source": cached_src}

    params = urllib.parse.urlencode({
        "latitude": key[0],
        "longitude": key[1],
        "daily": "precipitation_sum",
        "past_days": 2,
        "forecast_days": 1,
        "timezone": "Asia/Kolkata",
    })
    url = f"https://api.open-meteo.com/v1/forecast?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NagpurGroundwaterMonitor/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            payload = json.loads(resp.read().decode("utf-8"))

        daily_rain = (payload.get("daily") or {}).get("precipitation_sum") or []
        # past_days=2 + forecast_days=1 returns [2 days ago, yesterday, today]
        valid_vals = [float(v) for v in daily_rain if v is not None]
        rain_48h = round(sum(valid_vals[-3:]), 1)
        source = f"Open-Meteo Live ({now.strftime('%H:%M')} IST)"

        _RAIN_CACHE[key] = (now + timedelta(minutes=CACHE_TTL_MINUTES), rain_48h, source)
        return {"rain_48h_mm": rain_48h, "source": source}
    except Exception:
        return {"rain_48h_mm": 0.0, "source": "Offline Fallback (0.0 mm)"}