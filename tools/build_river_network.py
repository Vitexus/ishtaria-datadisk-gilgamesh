#!/usr/bin/env python3
"""Writes rivers/network_NN.yaml: the tributaries and streams of the Tigris-Euphrates-Karun drainage.

The two great rivers are told by tools/build_rivers.py (rivers/euphrates.yaml, rivers/tigris.yaml). Everything that runs into
them, down to the brooks, comes from HydroRIVERS v1.0 (Lehner and Grill 2013, https://www.hydrosheds.org/products/hydrorivers,
CC BY 4.0 with the HydroSHEDS licence: attribution required; see datadisk.yaml and debian/copyright), derived from the 15 arc
second SRTM relief: every reach of the Middle East ("eu" tile) that drains to the Shatt al-Arab, with its average discharge.

What is kept:

* streams of flow order 6 and above (`ORD_FLOW` <= 6: from the main stems down to streams of about a cubic metre a second);
* nothing on the alluvial plain below 33.6 N and west of 47 E: there the DEM-derived lines of HydroRIVERS follow today's
  canals and levees, not rivers of 2700 BCE (the plain's waterways are the Euphrates, the Tigris and the canals);
* nothing within a kilometre of the courses of euphrates.yaml and tigris.yaml (the stems are theirs).

Reaches are merged into polylines from each headwater to the confluence (or to a stem), simplified to 150 m, and given the
width of the water at each reach from its discharge (width = 3.4 * Q^0.5 metres, 10 to 400 m). The output is split in
files of under a megabyte each, a list of rivers in each.

Usage: tools/build_river_network.py      (needs GDAL's python bindings (osgeo), PyYAML; downloads the HydroRIVERS "eu" tile
(about 67 MB) once into tools/cache/)
"""
import json
import math
import pathlib
import urllib.request
import zipfile

import yaml
from osgeo import ogr

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "cache"
URL = "https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_eu_shp.zip"
BASIN = 20791150                    # MAIN_RIV of the Shatt al-Arab: the drainage that reaches the Gulf at its head
BOX = (36.0, 28.5, 50.0, 40.5)      # west, south, east, north
MAX_ORDER = 6
PLAIN = (33.6, 47.0)                # below this latitude and west of this longitude: no tributaries
STEM_DISTANCE_KM = 1.0
SIMPLIFY_DEG = 0.0015
MAX_FILE_BYTES = 880_000


def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)
    shp = CACHE / "HydroRIVERS_v10_eu_shp" / "HydroRIVERS_v10_eu.shp"
    if not shp.exists():
        archive = CACHE / "HydroRIVERS_v10_eu_shp.zip"
        if not archive.exists():
            request = urllib.request.Request(URL, headers={"User-Agent": "IshtariaDatadisk/0.3 (research)"})
            archive.write_bytes(urllib.request.urlopen(request, timeout=900).read())
        zipfile.ZipFile(archive).extractall(CACHE / "HydroRIVERS_v10_eu_shp")
        shp = next((CACHE / "HydroRIVERS_v10_eu_shp").rglob("*.shp"))
    return shp


def stems():
    """The points of the two great rivers, to keep the network off them."""
    points = []
    for name in ("euphrates", "tigris"):
        document = yaml.safe_load((ROOT / "rivers" / (name + ".yaml")).read_text(encoding="utf-8"))
        points.extend((lon, lat) for lat, lon, _ in document["points"])
    return points


def near_stem(grid, lon, lat):
    key = (int(lon * 10), int(lat * 10))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for slon, slat in grid.get((key[0] + dx, key[1] + dy), ()):
                if math.hypot((lon - slon) * 95.0, (lat - slat) * 111.0) < STEM_DISTANCE_KM:
                    return True
    return False


def densify(points, step_deg=0.01):
    out = []
    for a, b in zip(points, points[1:]):
        n = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step_deg))
        out.extend((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n))
    out.append(points[-1])
    return out


def thin(points, keep, tolerance=SIMPLIFY_DEG):
    """Douglas-Peucker on indices; `keep` are indices that must stay (changes of width)."""
    marked = {0, len(points) - 1} | set(keep)
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        (x1, y1), (x2, y2) = points[first], points[last]
        length = math.hypot(x2 - x1, y2 - y1) or 1e-12
        index, far = None, 0.0
        for i in range(first + 1, last):
            x, y = points[i]
            distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / length
            if distance > far:
                index, far = i, distance
        if index is not None and far > tolerance:
            marked.add(index)
            stack += [(first, index), (index, last)]
    return sorted(marked)


def main():
    ogr.UseExceptions()
    dataset = ogr.Open(str(fetch()))
    layer = dataset.GetLayer(0)
    layer.SetSpatialFilterRect(*BOX)
    grid = {}
    for lon, lat in densify(stems()):
        grid.setdefault((int(lon * 10), int(lat * 10)), []).append((lon, lat))
    reaches = {}
    for feature in layer:
        if feature["MAIN_RIV"] != BASIN or feature["ORD_FLOW"] > MAX_ORDER:
            continue
        geometry = feature.GetGeometryRef()
        points = [(geometry.GetX(i), geometry.GetY(i)) for i in range(geometry.GetPointCount())]
        mid_lon = sum(p[0] for p in points) / len(points)
        mid_lat = sum(p[1] for p in points) / len(points)
        if mid_lat < PLAIN[0] and mid_lon < PLAIN[1]:
            continue
        if all(near_stem(grid, lon, lat) for lon, lat in points):
            continue
        reaches[feature["HYRIV_ID"]] = (feature["NEXT_DOWN"], points, float(feature["DIS_AV_CMS"]))
    upstream = {}
    for identity, (down, _, _) in reaches.items():
        upstream.setdefault(down, []).append(identity)
    heads = [identity for identity in reaches if identity not in upstream]
    visited = set()
    rivers = []
    for head in sorted(heads):
        path, widths, node = [], [], head
        while node in reaches and node not in visited:
            visited.add(node)
            down, points, discharge = reaches[node]
            width = min(400.0, max(10.0, 3.4 * math.sqrt(discharge)))
            for point in points if not path else points[1:]:
                path.append(point)
                widths.append(width)
            node = down
        if node in reaches:                       # joins a stream already laid: end on its first point
            path.append(reaches[node][1][0])
            widths.append(max(widths[-1], min(400.0, max(10.0, 3.4 * math.sqrt(reaches[node][2])))))
        if len(path) < 2:
            continue
        changes = [i for i in range(1, len(widths)) if abs(widths[i] - widths[i - 1]) > 0.35 * widths[i - 1] + 3]
        kept = thin(path, changes)
        rivers.append((head, [(path[i][1], path[i][0], widths[i]) for i in kept]))
    # headwater first: the long streams first, so a file is a whole drainage rather than scraps
    rivers.sort(key=lambda river: -len(river[1]))
    out = ROOT / "rivers"
    for old in out.glob("network_*.yaml"):
        old.unlink()
    files, current, size = 0, [], 0
    header = ("# Tributaries and streams of the Tigris-Euphrates-Karun drainage (tools/build_river_network.py): HydroRIVERS v1.0, "
              "Lehner and Grill (2013), CC BY 4.0.\n# Each river: [latitude, longitude, width_m] from the headwater to the "
              "confluence.\n")

    def flush():
        nonlocal files, current, size
        if not current:
            return
        files += 1
        (out / ("network_%02d.yaml" % files)).write_text(header + "".join(current), encoding="utf-8")
        current, size = [], 0

    for head, points in rivers:
        line = "- {id: net_%d, points: [%s]}\n" % (head, ", ".join("[%.4f, %.4f, %.0f]" % p for p in points))
        if size + len(line) > MAX_FILE_BYTES:
            flush()
        current.append(line)
        size += len(line)
    flush()
    total = sum(len(points) for _, points in rivers)
    print("%d reaches -> %d rivers, %d points, %d files" % (len(reaches), len(rivers), total, files))


if __name__ == "__main__":
    main()
