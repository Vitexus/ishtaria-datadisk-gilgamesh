#!/usr/bin/env python3
"""Writes buildings/uruk_fields.yaml (and the field plots into media/terrain/uruk_clear.png): tilled fields on both sides of
every irrigation canal of Uruk's landscape patch.

    tools/build_landscape.py uruk        # first: carves the canals and writes tools/data/uruk_canals_used.json
    tools/build_fields.py

Along each canal (tools/data/uruk_canals_used.json: the survey canals, the channel network, the barrage and herringbone canals,
all in metres from Uruk's tell) a plot of 24-62 m along the canal and 24-40 m (a farm canal) or 34-52 m (a larger one) deep is laid one after
another on both sides (farms of 500-20 000 square metres, Jotheri et al. 2025), 14 m from the canal axis edge (the path along the canal; the water mask is 10 m a pixel), its furrows running down from the canal as water does
(research/RIVER_NETWORK.md, RTF_LOST_IN_TIME_URUK.md: furrow irrigation; basin irrigation by gravity from the levee, Jotheri et al. 2018). A plot is left out where it would
stand in water, within 120 m of the wall of the city, or on another plot; it is green barley, ripe barley or fallow by chance.
The plots are `passable` buildings (ishtaria-server: they block nothing and lie on the ground), of the place `uruk_fields` that
stands at Uruk's tell (places/uruk_fields.yaml). The cleared plots go into the clear mask so no wild trees grow in a field.
Deterministic.
"""
import json
import math
import pathlib
import random

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODELS = {"green": "media/models/architecture/field_barley_green.glb", "ripe": "media/models/architecture/field_barley_ripe.glb",
          "fallow": "media/models/architecture/field_fallow.glb"}
CHANCE = (("green", 0.5), ("ripe", 0.3), ("fallow", 0.2))
STATION_M, LENGTH_M, GAP_M = 30.0, 27.0, 14.0     # the default plot; each plot varies below
LENGTH_RANGE_M, DEPTH_RANGE_M, BETWEEN_M = (24.0, 62.0), ((24.0, 40.0), (34.0, 52.0)), 3.0   # farms of 500-20 000 m2 (Jotheri et al. 2025)
CITY_M = 120.0
RELIEF_M = 0.2                    # crest above trough
PIXEL_M = 4.0                     # raster of the checks: the clear mask's 1500 px of 6000 m
SIZE_M = 6000.0
ANCHOR_SHIFT = (0.0, 1.0)         # the place uruk_fields stands 1 m north of Uruk's tell (z south): item z = world z + 1
MAX_FIELDS = 6000


def to_pixel(x, z):
    return ((x + SIZE_M / 2.0) / PIXEL_M, (z + SIZE_M / 2.0) / PIXEL_M)


def rasterize(corners, size):
    mask = np.zeros((size, size), np.uint8)
    cv2.fillPoly(mask, [np.array([to_pixel(*c) for c in corners], np.float32).round().astype(np.int32)], 1)
    return mask > 0


def main():
    canals = json.loads((ROOT / "tools" / "data" / "uruk_canals_used.json").read_text(encoding="utf-8"))
    outlines = json.loads((ROOT / "tools" / "data" / "uruk_outlines.json").read_text(encoding="utf-8"))
    size = int(SIZE_M / PIXEL_M)
    water10 = np.array(Image.open(ROOT / "media" / "terrain" / "uruk_water.png")) > 0
    wet = cv2.resize(water10.astype(np.uint8), (size, size), interpolation=cv2.INTER_NEAREST) > 0
    wet = ndi.binary_dilation(wet, iterations=1)
    city = np.zeros((size, size), np.uint8)
    cv2.fillPoly(city, [np.array([to_pixel(x, z) for x, z, *_ in outlines["wall"]], np.float32).round().astype(np.int32)], 1)
    blocked = ndi.binary_dilation(city > 0, iterations=int(CITY_M / PIXEL_M)) | wet
    occupied = np.zeros((size, size), bool)
    rng = random.Random(2650)
    placed, items = 0, []
    plots = []
    for canal in sorted(canals, key=lambda c: -c["width_m"]):          # the larger canals take their fields first
        width = canal["width_m"]
        depth_range = DEPTH_RANGE_M[1] if width >= 14.0 else DEPTH_RANGE_M[0]
        points = canal["points"]
        # walk along the polyline by stations
        carried = 0.0
        for (x1, z1), (x2, z2) in zip(points, points[1:]):
            length = math.hypot(x2 - x1, z2 - z1)
            if length < 1.0:
                continue
            tx, tz = (x2 - x1) / length, (z2 - z1) / length
            nx, nz = -tz, tx
            at = carried
            while at <= length:
                plot_length = rng.uniform(*LENGTH_RANGE_M)
                cx, cz = x1 + tx * (at + plot_length / 2.0), z1 + tz * (at + plot_length / 2.0)
                for side in (-1.0, 1.0):
                    depth = rng.uniform(*depth_range)
                    offset = width / 2.0 + GAP_M + depth / 2.0
                    mx, mz = cx + side * nx * offset, cz + side * nz * offset
                    if abs(mx) > 2950 or abs(mz) > 2950:
                        continue
                    # the plot: depth along the normal (the furrows), LENGTH_M along the canal
                    hd, hl = depth / 2.0, plot_length / 2.0
                    corners = [(mx + nx * a + tx * b, mz + nz * a + tz * b) for a, b in ((-hd, -hl), (hd, -hl), (hd, hl), (-hd, hl))]
                    mask = rasterize(corners, size)
                    area = int(mask.sum())
                    if area == 0 or (mask & blocked).any() or (mask & occupied).sum() > 0.1 * area:
                        continue
                    occupied |= mask
                    plots.append(mask)
                    placed += 1
                    # the model's x (width, the furrows) lies along the normal: bearing of the front (+Z) from b = atan2(-az, -ax)
                    bearing = math.degrees(math.atan2(-nz * side, -nx * side)) % 360.0
                    roll = rng.random()
                    kind = "green"
                    total = 0.0
                    for name, chance in CHANCE:
                        total += chance
                        if roll <= total:
                            kind = name
                            break
                    items.append({"model": MODELS[kind], "x": round(mx - ANCHOR_SHIFT[0], 2), "z": round(mz + ANCHOR_SHIFT[1], 2),
                                  "yaw_deg": round(bearing, 1), "scale": [round(depth / 10.0, 3), RELIEF_M, round(plot_length / 10.0, 3)],
                                  "footprint": [round(depth, 2), round(plot_length, 2)], "passable": True})
                    if placed >= MAX_FIELDS:
                        break
                at += plot_length + BETWEEN_M
                if placed >= MAX_FIELDS:
                    break
            carried = at - length
            if placed >= MAX_FIELDS:
                break
    rows = ["  - {model: %s, x: %.2f, z: %.2f, yaw_deg: %.1f, scale: [%.3f, %.3f, %.3f], footprint: [%.2f, %.2f], sink_m: 0.05, passable: true}\n"
            % (i["model"], i["x"], i["z"], i["yaw_deg"], *i["scale"], *i["footprint"]) for i in items]
    (ROOT / "buildings" / "uruk_fields.yaml").write_text(
        "# Tilled fields on both sides of the irrigation canals of Uruk (written by tools/build_fields.py; do not edit).\n"
        "# Format: ishtaria-protocol schemas/datadisk.schema.json, $defs/buildings (passable: a field blocks nothing).\n"
        "place: uruk_fields\nitems:\n" + "".join(rows), encoding="utf-8")
    # no wild growth in a field: the plots go into the clear mask (1 px = 4 m)
    clear_path = ROOT / "media" / "terrain" / "uruk_clear.png"
    clear = np.array(Image.open(clear_path))
    for mask in plots:
        clear[mask] = 255
    Image.fromarray(clear).save(clear_path, optimize=True)
    print("%d fields on %.1f ha, %d canals" % (placed, occupied.sum() * PIXEL_M * PIXEL_M / 10000.0, len(canals)))


if __name__ == "__main__":
    main()
