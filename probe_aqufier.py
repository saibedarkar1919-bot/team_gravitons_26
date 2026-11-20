import json
import os

SRC = r"D:\hackumbh\major_principal_aquifer.geojson"


def walk_coords(coords, out):
    if not coords:
        return
    if isinstance(coords[0], (int, float)):
        out.append((coords[0], coords[1]))
        return
    for item in coords:
        walk_coords(item, out)


with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

features = data.get("features", [])
print("Total features:", len(features))

mas_values = set()
pas_values = set()
sample_pts = []

for feat in features:
    props = feat.get("properties") or {}
    mas_values.add(str(props.get("mas_name")))
    pas_values.add(str(props.get("pas_name")))
    if len(sample_pts) < 5:
        walk_coords((feat.get("geometry") or {}).get("coordinates", []), sample_pts)

print("Unique mas_name:", sorted(mas_values))
print("Unique pas_name:", sorted(pas_values))
print("First 5 coordinate pairs:", sample_pts)
