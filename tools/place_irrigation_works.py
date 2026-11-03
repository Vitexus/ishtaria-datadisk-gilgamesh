#!/usr/bin/env python3
"""Lays the irrigation scheme (media/models/architecture/irrigation_works.glb) at the best sites of tools/data/irrigation_sites.json
(tools/find_irrigation_sites.py): one on a documented canal near Uruk, one near Eridu, one near Larsa. Writes places/irrigation_works.yaml,
buildings/irrigation_works_<site>.yaml and takes the fields of buildings/uruk_fields.yaml out of the footprint of the one at Uruk. Also writes
research/IRRIGATION_SITES.md (the other sites).

    tools/place_irrigation_works.py

The model's origin is the middle of its canal at the mouth of the nagkud; the item stands there with the bearing of the model's front
(+Z, the scheme side). Deterministic.
"""
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TELL = (31.3228, 45.6389)
FOOTPRINT = (100.0, 94.0)          # the schema allows 100 m at most: the scheme itself is 150 m along the canal (passable, nothing collides)
U0, U1, V_SCHEME, V_ORCHARD = -50.0, 100.0, 62.0, 32.0
MODEL = "media/models/architecture/irrigation_works.glb"
CHOICES = (("uruk", "uruk"), ("eridu", "eridu"), ("larsa", "larsa"))     # (suffix, nearest city)


def to_geo(x, z):
    lat = TELL[0] - z / 110574.0
    return lat, TELL[1] + x / (111320.0 * math.cos(math.radians(TELL[0])))


def corners(site, margin=12.0):
    b = math.radians(site["bearing_deg"])
    sx, sz = math.sin(b), -math.cos(b)                 # to the scheme side (east, south)
    ux, uz = sz * -1.0, sx                             # along the canal: the front turned 90 degrees to the left
    # bearing of +X is bearing - 90: (sin(b-90), -cos(b-90)) = (-cos b, -sin b)
    ux, uz = -math.cos(b), -math.sin(b)
    def at(u, v):
        return (site["x"] + ux * u + sx * v, site["z"] + uz * u + sz * v)
    return [at(U0 - margin, -V_ORCHARD - margin), at(U1 + margin, -V_ORCHARD - margin), at(U1 + margin, V_SCHEME + margin), at(U0 - margin, V_SCHEME + margin)]


def inside(poly, x, z):
    sign = None
    for (x1, z1), (x2, z2) in zip(poly, poly[1:] + poly[:1]):
        c = (x2 - x1) * (z - z1) - (z2 - z1) * (x - x1)
        if abs(c) < 1e-9:
            continue
        if sign is None:
            sign = c > 0
        elif (c > 0) != sign:
            return False
    return True


def main():
    sites = json.loads((ROOT / "tools/data/irrigation_sites.json").read_text(encoding="utf-8"))
    chosen = []
    for suffix, city in CHOICES:
        near = [s for s in sites if s["nearest_city"] == city]
        if suffix == "uruk":
            near = [s for s in near if s["source"] == "jotheri2018"]       # the Uruk canal of the published network
        if near:
            chosen.append((suffix, min(near, key=lambda s: s["city_distance_m"])))
    places = ["# The irrigation scheme (media/models/architecture/irrigation_works.glb, research/WATER_WORKS.md) laid on documented canals by\n"
              "# tools/place_irrigation_works.py (do not edit): near Uruk (the channel network of Jotheri et al. 2018), near Eridu (the primary\n"
              "# canals of the Eridu region) and near Larsa (the survey canals between Uruk and Larsa). Other sites: research/IRRIGATION_SITES.md.\n"]
    for suffix, s in chosen:
        pid = f"irrigation_works_{suffix}"
        if suffix == "uruk":
            bearing = math.degrees(math.atan2(s["x"], -s["z"])) % 360.0
            locate = f"  locate: {{from: uruk, bearing_deg: {bearing:.3f}, distance_m: {math.hypot(s['x'], s['z']):.1f}, tolerance_m: 0}}\n  parent: uruk\n"
        else:
            lat, lon = to_geo(s["x"], s["z"])
            locate = f"  geo: {{latitude_deg: {lat:.5f}, longitude_deg: {lon:.5f}}}\n"
        places.append(f"\n- id: {pid}\n  kind: landmark\n  name_key: place.irrigation_works\n  radius_m: 80\n{locate}"
                      f"  # canal {s['canal']} ({s['canal_width_m']:g} m, {s['source']}), {s['city_distance_m']} m from {s['nearest_city']}; the scheme lies to the right of the\n"
                      f"  # canal as the model's +X runs, front towards bearing {s['bearing_deg']}\n")
        (ROOT / "buildings" / f"{pid}.yaml").write_text(
            "# The irrigation scheme of the place (written by tools/place_irrigation_works.py; do not edit). Format: ishtaria-protocol\n"
            "# schemas/datadisk.schema.json, $defs/buildings (passable: no collision).\n"
            f"place: {pid}\nitems:\n  - {{model: {MODEL}, x: 0.0, z: 0.0, yaw_deg: {s['bearing_deg']:.1f}, scale: [1.0, 1.0, 1.0], footprint: [{FOOTPRINT[0]:.1f}, {FOOTPRINT[1]:.1f}], sink_m: 0.3, passable: true}}\n",
            encoding="utf-8")
    (ROOT / "places" / "irrigation_works.yaml").write_text("".join(places), encoding="utf-8")
    # the fields of Uruk take no part where the scheme stands
    for suffix, s in chosen:
        if suffix != "uruk":
            continue
        poly = corners(s)
        path = ROOT / "buildings" / "uruk_fields.yaml"
        if not path.is_file():
            continue
        kept, dropped = [], 0
        for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
            m = re.search(r"x: (-?[\d.]+), z: (-?[\d.]+),", line)
            if m and line.lstrip().startswith("- {model:"):
                x, z = float(m.group(1)), float(m.group(2)) - 1.0           # the place uruk_fields stands 1 m north of the tell
                if inside(poly, x, z):
                    dropped += 1
                    continue
            kept.append(line)
        path.write_text("".join(kept), encoding="utf-8")
        print("fields taken out of the footprint at Uruk:", dropped)
    # the report
    doc = ["# Sites for the irrigation scheme\n\n",
           "Found by `tools/find_irrigation_sites.py` along the documented irrigation canals (research/RIVER_NETWORK.md): the primary canals of the Eridu region, the survey canals\n"
           "between Uruk and Larsa and the channel network of Jotheri et al. 2018, only those 10 to 14 m wide (the model's canal is 10 m). The scheme needs 150 m along the canal and 94 m\n"
           "across, no other canal or river inside, 200 m from any city, 150 m from the wall of Uruk, and where there are terrain rasters (the patch of Uruk) no water but its own\n"
           "canal and a ground within 1.5 m. Metres are east (x) and south (z) of Uruk's tell; the bearing is that of the model's front (the scheme side).\n\n",
           "Placed: " + ", ".join(f"`irrigation_works_{a}` (canal {b['canal']})" for a, b in chosen) + ".\n\n",
           f"{len(sites)} sites at least 1.5 km apart (before the selection of the three), nearest to a city first:\n\n",
           "| # | canal | width m | source | nearest city | city m | x | z | bearing |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"]
    for i, s in enumerate(sites[:40]):
        doc.append(f"| {i} | {s['canal']} | {s['canal_width_m']:g} | {s['source']} | {s['nearest_city']} | {s['city_distance_m']} | {s['x']} | {s['z']} | {s['bearing_deg']} |\n")
    (ROOT / "research" / "IRRIGATION_SITES.md").write_text("".join(doc), encoding="utf-8")
    for suffix, s in chosen:
        print(suffix, s)


if __name__ == "__main__":
    main()
