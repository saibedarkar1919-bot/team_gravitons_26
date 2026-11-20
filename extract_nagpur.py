import csv
import json
import math
import os

DATA_DIR = r"D:\hackumbh"
OUT_DIR = os.path.join(DATA_DIR, "processed")
os.makedirs(OUT_DIR, exist_ok=True)

NGP_BOUNDS = {"min_lon": 78.20, "max_lon": 79.80, "min_lat": 20.50, "max_lat": 21.80}

CSV_TARGETS = [
    (
        "gwl_manual_quarterly_cgwb_mh_2021_2025.csv",
        "Groundwater Level Quarterly Manual (meter)",
        "nagpur_quarterly.json",
    ),
    (
        "gwl_tel_6_hourly_cgwb_mh_2021_2025.csv",
        "Groundwater Level Telemetry 6 Hourly (meter)",
        "nagpur_telemetry_6hr.json",
    ),
]


def lonlat_to_mercator(lon: float, lat: float) -> tuple[float, float]:
    x = lon * 20037508.34 / 180.0
    y = math.log(math.tan((90.0 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
    y = y * 20037508.34 / 180.0
    return x, y


def mercator_to_lonlat(x: float, y: float) -> tuple[float, float]:
    lon = (x / 20037508.34) * 180.0
    lat = (y / 20037508.34) * 180.0
    lat = 180.0 / math.pi * (2.0 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
    return round(lon, 6), round(lat, 6)


def convert_coords_to_lonlat(coords):
    if not coords:
        return coords
    if isinstance(coords[0], (int, float)):
        lon, lat = mercator_to_lonlat(coords[0], coords[1])
        return [lon, lat]
    return [convert_coords_to_lonlat(item) for item in coords]


def get_geometry_bbox(coords, bounds=None):
    if bounds is None:
        bounds = [float("inf"), float("inf"), float("-inf"), float("-inf")]
    if not coords:
        return bounds
    if isinstance(coords[0], (int, float)):
        x, y = coords[0], coords[1]
        bounds[0] = min(bounds[0], x)
        bounds[1] = min(bounds[1], y)
        bounds[2] = max(bounds[2], x)
        bounds[3] = max(bounds[3], y)
        return bounds
    for item in coords:
        get_geometry_bbox(item, bounds)
    return bounds


def filter_aquifer_geojson():
    src_path = os.path.join(DATA_DIR, "major_principal_aquifer.geojson")
    print("=== Clipping & Converting major_principal_aquifer.geojson to GPS (Lat/Lon) ===")

    # Convert Nagpur GPS bounding box into EPSG:3857 meters to match the GeoJSON
    ngp_min_x, ngp_min_y = lonlat_to_mercator(NGP_BOUNDS["min_lon"], NGP_BOUNDS["min_lat"])
    ngp_max_x, ngp_max_y = lonlat_to_mercator(NGP_BOUNDS["max_lon"], NGP_BOUNDS["max_lat"])

    with open(src_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nagpur_features = []
    aquifer_names = set()

    for feat in data.get("features", []):
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates", [])
        min_x, min_y, max_x, max_y = get_geometry_bbox(coords)

        overlaps = not (
            max_x < ngp_min_x or min_x > ngp_max_x or max_y < ngp_min_y or min_y > ngp_max_y
        )
        if overlaps:
            props = feat.get("properties") or {}
            aquifer_names.add(f"{props.get('mas_name')} ({props.get('pas_name')})")
            nagpur_features.append({
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": geom.get("type"),
                    "coordinates": convert_coords_to_lonlat(coords),
                },
            })

    out_path = os.path.join(OUT_DIR, "nagpur_aquifers.geojson")
    with open(out_path, "w", encoding="utf-8") as out_f:
        json.dump({"type": "FeatureCollection", "features": nagpur_features}, out_f)

    print(f"Saved {len(nagpur_features)} Nagpur aquifer polygons (converted to Lat/Lon) -> {out_path}")
    print("Aquifers covering Nagpur:", sorted(aquifer_names))


if __name__ == "__main__":
    # CSVs are already extracted cleanly; run aquifer projection fix now
    filter_aquifer_geojson()