#!/usr/bin/env python3
"""Writes places/outer_fields.yaml and buildings/outer_fields_*.yaml: barley fields and date-palm orchards on both sides of the
irrigation canals OUTSIDE the landscape patch of Uruk (the canals of the Eridu region, the survey canals between Uruk and Larsa
and the channel network of Uruk's region, rivers/*.yaml), where tools/build_fields.py does not reach because it needs the 10 m
rasters of the patch.

    tools/build_outer_fields.py [--dry]

The canals are the lines of rivers/eridu_canals.yaml (not the Euphrates), rivers/uruk_larsa_canals.yaml and
rivers/uruk_region_network_01.yaml of at most 20 m of water (wider ones are rivers). Plots are laid as build_fields.py does: a
plot every 24-62 m along each side of a canal, 14 m from the axis, furrows running away from the canal, green barley, ripe barley
or fallow by chance, and now and then a date-palm orchard (kiri) of 40 x 30 m, never two in a row on one side. A plot is left out
where it would stand on any water (the canals, the rivers, the water mask of the world), within reach of a place of the disk, in the
square of Uruk's patch (tools/build_fields.py fills that) or on another plot.

A place of the buildings schema holds at most 6000 buildings within 4 km of its anchor, so the plots are filed under places of
their own, one for each square of 6 km, pinned (`geo`) to its middle. They are plain landmarks with no model of their own; the
plots are `passable` buildings and the server keeps wild growth out of them. Deterministic.
"""
import glob
import math
import pathlib
import random
import sys

import cv2
import numpy as np
import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_fields as base  # noqa: E402  (the constants and the models of the fields of Uruk)

R = 6371000.0
URUK = (31.3228, 45.6389)
COS0 = math.cos(math.radians(URUK[0]))
CELL_M = 6000.0                      # one place for each square of this side
GRID_M = 6.0                         # raster of the checks
MAX_WATER_M = 20.0                   # a canal; wider lines are rivers
URUK_SQUARE_M = 3050.0               # the patch of Uruk, filled by build_fields.py
PLACE_CLEAR_M = 250.0                # beyond the radius of a place of the disk
MAX_PER_PLACE = 6000


def to_xz(lat, lon):
    """The one flat frame of the whole job: metres east and south of Uruk."""
    return ((lon - URUK[1]) * COS0 * math.pi / 180.0 * R, -(lat - URUK[0]) * math.pi / 180.0 * R)


def to_geo(x, z):
    return (URUK[0] - z / R * 180.0 / math.pi, URUK[1] + x / (R * COS0) * 180.0 / math.pi)


def load_lines(name, keep):
    data = yaml.safe_load((ROOT / "rivers" / name).read_text(encoding="utf-8"))
    return [line for line in (data if isinstance(data, list) else [data]) if keep(line)]


def cells_of(corners):
    """The raster cells a polygon (frame metres) covers."""
    pts = np.array([(x / GRID_M, z / GRID_M) for x, z in corners])
    low = np.floor(pts.min(axis=0)).astype(int) - 1
    high = np.ceil(pts.max(axis=0)).astype(int) + 1
    mask = np.zeros((high[1] - low[1] + 1, high[0] - low[0] + 1), np.uint8)
    cv2.fillPoly(mask, [np.round(pts - low).astype(np.int32)], 1)
    ys, xs = np.nonzero(mask)
    return {(int(x + low[0]), int(y + low[1])) for x, y in zip(xs, ys)}


def disc(cx, cz, radius):
    steps = int(radius / GRID_M) + 1
    ci, cj = int(cx // GRID_M), int(cz // GRID_M)
    return {(ci + i, cj + j) for i in range(-steps, steps + 1) for j in range(-steps, steps + 1)
            if math.hypot(i * GRID_M, j * GRID_M) <= radius + GRID_M * 0.5}


def along(points, step):
    """Points every `step` metres along a polyline of frame points."""
    out = []
    for (x1, z1), (x2, z2) in zip(points, points[1:]):
        length = math.hypot(x2 - x1, z2 - z1)
        for k in range(int(length / step) + 1):
            t = k * step / length if length else 0.0
            out.append((x1 + (x2 - x1) * t, z1 + (z2 - z1) * t))
    out.append(points[-1])
    return out


def main():
    dry = "--dry" in sys.argv
    canals = []
    for line in load_lines("eridu_canals.yaml", lambda r: str(r["id"]).startswith("eridu_canal")) \
            + load_lines("uruk_larsa_canals.yaml", lambda r: True) \
            + load_lines("uruk_region_network_01.yaml", lambda r: r["points"][0][2] <= MAX_WATER_M):
        width = float(line["points"][0][2])
        canals.append({"id": line["id"], "width": width, "points": [to_xz(p[0], p[1]) for p in line["points"]]})
    # water: the canals themselves and the rivers near them, as cells that no plot may touch
    blocked = set()
    for canal in canals:
        for x, z in along(canal["points"], 3.0):
            blocked |= disc(x, z, canal["width"] / 2.0 + base.GAP_M * 0.5)
    low = min(x for c in canals for x, _ in c["points"]) - 20000, min(z for c in canals for _, z in c["points"]) - 20000
    high = max(x for c in canals for x, _ in c["points"]) + 20000, max(z for c in canals for _, z in c["points"]) + 20000
    for name in ("euphrates.yaml", "tigris.yaml", "eridu_canals.yaml"):
        for line in load_lines(name, lambda r: True):
            if name == "eridu_canals.yaml" and not str(line["id"]).startswith("eridu_euphrates"):
                continue
            pts = [to_xz(p[0], p[1]) for p in line["points"]]
            for x, z in along(pts, 8.0):
                if low[0] <= x <= high[0] and low[1] <= z <= high[1]:
                    blocked |= disc(x, z, float(line["points"][0][2]) / 2.0 + base.GAP_M)
    # places of the disk with a pinned site: no fields on the cities and their walls
    keep_out = []
    for path in glob.glob(str(ROOT / "places" / "*.yaml")):
        for place in yaml.safe_load(open(path, encoding="utf-8")) or []:
            if isinstance(place, dict) and place.get("geo"):
                x, z = to_xz(place["geo"]["latitude_deg"], place["geo"]["longitude_deg"])
                keep_out.append((x, z, max(float(place.get("radius_m", 0)), 150.0) + PLACE_CLEAR_M))
    water = np.array(Image.open(ROOT / "media" / "world" / "water.pgm"))

    def on_world_water(x, z):
        lat, lon = to_geo(x, z)
        return water[min(3599, max(0, int((90.0 - lat) / 0.05))), min(7199, max(0, int((lon + 180.0) / 0.05)))] > 127

    rng = random.Random(2660)
    orchard_rng = random.Random(2661)
    occupied = set()
    placed, orchards, items = 0, 0, []
    for canal in sorted(canals, key=lambda c: -c["width"]):
        width = canal["width"]
        depth_range = base.DEPTH_RANGE_M[1] if width >= 14.0 else base.DEPTH_RANGE_M[0]
        after_orchard = {-1.0: False, 1.0: False}
        carried = 0.0
        for (x1, z1), (x2, z2) in zip(canal["points"], canal["points"][1:]):
            length = math.hypot(x2 - x1, z2 - z1)
            if length < 1.0:
                continue
            tx, tz = (x2 - x1) / length, (z2 - z1) / length
            nx, nz = -tz, tx
            at = carried
            while at <= length:
                plot_length = rng.uniform(*base.LENGTH_RANGE_M)
                cx, cz = x1 + tx * (at + plot_length / 2.0), z1 + tz * (at + plot_length / 2.0)
                for side in (-1.0, 1.0):
                    depth = rng.uniform(*depth_range)
                    orchard = not after_orchard[side] and orchard_rng.random() < base.ORCHARD_CHANCE
                    if orchard:
                        depth = base.ORCHARD_DEPTH_M
                    offset = width / 2.0 + base.GAP_M + depth / 2.0
                    mx, mz = cx + side * nx * offset, cz + side * nz * offset
                    hd, hl = depth / 2.0, (base.ORCHARD_LENGTH_M if orchard else plot_length) / 2.0
                    corners = [(mx + nx * a + tx * b, mz + nz * a + tz * b) for a, b in ((-hd, -hl), (hd, -hl), (hd, hl), (-hd, hl))]
                    skip = (abs(mx) < URUK_SQUARE_M and abs(mz) < URUK_SQUARE_M) \
                        or any(math.hypot(mx - kx, mz - kz) < kr for kx, kz, kr in keep_out) \
                        or on_world_water(mx, mz)
                    covered = set() if skip else cells_of(corners)
                    if skip or not covered or covered & blocked or len(covered & occupied) > 0.1 * len(covered):
                        after_orchard[side] = False
                        continue
                    after_orchard[side] = orchard
                    occupied |= covered
                    placed += 1
                    bearing = math.degrees(math.atan2(-nz * side, -nx * side)) % 360.0
                    if orchard:
                        orchards += 1
                        model, scale, footprint, sink = base.ORCHARDS[orchard_rng.randrange(len(base.ORCHARDS))], [1.0, 1.0, 1.0], \
                            [base.ORCHARD_DEPTH_M, base.ORCHARD_LENGTH_M], 0.0
                    else:
                        roll, kind, total = rng.random(), "green", 0.0
                        for name, chance in base.CHANCE:
                            total += chance
                            if roll <= total:
                                kind = name
                                break
                        model, scale, footprint, sink = base.MODELS[kind], [round(depth / 10.0, 3), base.RELIEF_M, round(plot_length / 10.0, 3)], \
                            [round(depth, 2), round(plot_length, 2)], 0.05
                    items.append((mx, mz, model, bearing, scale, footprint, sink))
                at += plot_length + base.BETWEEN_M
            carried = at - length
    print("%d plots (%d date orchards) along %d canals, %.0f km" % (
        placed, orchards, len(canals), sum(math.hypot(b[0] - a[0], b[1] - a[1]) for c in canals for a, b in zip(c["points"], c["points"][1:])) / 1000.0))
    # filed under the square of CELL_M each, pinned at its middle
    squares = {}
    for item in items:
        squares.setdefault((int(item[0] // CELL_M), int(item[1] // CELL_M)), []).append(item)
    print("%d squares, the fullest has %d plots" % (len(squares), max(len(v) for v in squares.values())))
    if dry:
        return
    for old in glob.glob(str(ROOT / "buildings" / "outer_fields_*.yaml")):
        pathlib.Path(old).unlink()
    places = ["# Anchors of the fields and orchards along the canals outside the patch of Uruk (written by tools/build_outer_fields.py; do not edit).\n"
              "# One landmark for each square of 6 km, because a place has one buildings file of at most 6000 plots within 4 km of its anchor.\n"]
    for (i, j), plots in sorted(squares.items()):
        assert len(plots) <= MAX_PER_PLACE, (i, j, len(plots))
        pid = "outer_fields_%s%02d_%s%02d" % ("w" if i < 0 else "e", abs(i), "n" if j < 0 else "s", abs(j))
        ax, az = (i + 0.5) * CELL_M, (j + 0.5) * CELL_M
        lat, lon = to_geo(ax, az)
        places.append("- {id: %s, kind: landmark, name_key: place.outer_fields, radius_m: 8, geo: {latitude_deg: %.6f, longitude_deg: %.6f}}\n" % (pid, lat, lon))
        cos_lat = math.cos(math.radians(lat))
        rows = []
        for mx, mz, model, bearing, scale, footprint, sink in plots:
            plat, plon = to_geo(mx, mz)
            x = (plon - lon) * cos_lat * math.pi / 180.0 * R
            z = -(plat - lat) * math.pi / 180.0 * R
            rows.append("  - {model: %s, x: %.2f, z: %.2f, yaw_deg: %.1f, scale: [%.3f, %.3f, %.3f], footprint: [%.2f, %.2f], sink_m: %.2f, passable: true}\n"
                        % (model, x, z, bearing, *scale, *footprint, sink))
        (ROOT / "buildings" / (pid + ".yaml")).write_text(
            "# Fields and orchards along the canals of one square of 6 km (written by tools/build_outer_fields.py; do not edit).\n"
            "place: %s\nitems:\n" % pid + "".join(rows), encoding="utf-8")
    (ROOT / "places" / "outer_fields.yaml").write_text("".join(places), encoding="utf-8")
    print("wrote places/outer_fields.yaml and %d buildings files" % len(squares))


if __name__ == "__main__":
    main()
