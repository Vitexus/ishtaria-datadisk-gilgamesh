#!/usr/bin/env python3
"""Writes places/uruk_wells.yaml: wells in the quarters of Uruk, two to a quarter where the city is built up.

    tools/build_uruk_wells.py

Every settlement has water to drink and to fill a waterskin from, and a city has many wells (models-src/architecture/
uruk_well.py; the server lets a character drink within reach of a disk model named *_well.glb). A well is put at an open
spot of the quarter that lies in the built-up ground (at least six houses within 45 m) and clear of houses and streets.
Positions are metres from the anchor of Uruk (the frame of tools/data/uruk_city.json). Deterministic.
"""
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
plan = json.load(open(os.path.join(HERE, "data", "uruk_city.json")))
houses = plan["houses"]            # x, z, fx, fz, w, d, ...
grid = {}
for h in houses:
    grid.setdefault((int(h[0] // 50), int(h[1] // 50)), []).append(h)


def near_houses(x, z, r):
    out = []
    for gx in range(int((x - r) // 50), int((x + r) // 50) + 1):
        for gz in range(int((z - r) // 50), int((z + r) // 50) + 1):
            for h in grid.get((gx, gz), ()):
                if math.hypot(h[0] - x, h[1] - z) <= r:
                    out.append(h)
    return out


def clear_of_streets(x, z):
    for st in plan["streets"]:
        pts = st["pts"]
        half = float(st.get("width", 4.0)) / 2.0 + 2.0
        for a, b in zip(pts, pts[1:]):
            ax, az, bx, bz = a[0], a[1], b[0], b[1]
            dx, dz = bx - ax, bz - az
            ln = dx * dx + dz * dz
            t = 0.0 if ln == 0 else max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / ln))
            if math.hypot(x - (ax + t * dx), z - (az + t * dz)) < half:
                return False
    return True


rng = random.Random(4500)
lines = ["# The wells of Uruk (written by tools/build_uruk_wells.py; do not edit). Drinking and waterskins: see uruk_well.py.", ""]
count = 0
# The well that is still open in Uruk (photographed at 31.3243503 N, 45.6388031 E), a surveyed point of the plan: no house stands on it
wx, wz = plan["real_well"]
lines += [
    "- id: uruk_great_well",
    "  kind: landmark",
    "  name_key: place.uruk_great_well",
    "  radius_m: 4",
    "  locate: {from: uruk, bearing_deg: %.2f, distance_m: %.2f, tolerance_m: 0}" % (math.degrees(math.atan2(wx, -wz)) % 360.0, math.hypot(wx, wz)),
    "  structure:",
    "    model: media/models/architecture/uruk_well.glb",
    "    visible_m: 400",
    "  requires:",
    "    max_slope_deg: 45",
    "",
]
for q in plan["districts"]:
    x0, z0, x1, z1 = q["rect"]
    placed = []
    for _ in range(4000):
        if len(placed) >= 2:
            break
        x, z = rng.uniform(x0, x1), rng.uniform(z0, z1)
        close = near_houses(x, z, 45.0)
        if len(close) < 6:
            continue
        if any(math.hypot(h[0] - x, h[1] - z) < max(h[4], h[5]) / 2.0 + 3.5 for h in near_houses(x, z, 15.0)):
            continue
        if any(math.hypot(x - px, z - pz) < 120.0 for px, pz in placed):
            continue
        if not clear_of_streets(x, z):
            continue
        placed.append((x, z))
    for x, z in placed:
        count += 1
        lines += [
            "- id: uruk_well_%02d" % count,
            "  kind: landmark",
            "  name_key: place.uruk_well",
            "  radius_m: 4",
            "  locate: {from: uruk, bearing_deg: %.2f, distance_m: %.2f, tolerance_m: 0}" % (math.degrees(math.atan2(x, -z)) % 360.0, math.hypot(x, z)),
            "  structure:",
            "    model: media/models/architecture/uruk_well.glb",
            "    visible_m: 400",
            "  requires:",
            "    max_slope_deg: 45",
            "",
        ]
with open(os.path.join(ROOT, "places", "uruk_wells.yaml"), "w") as out:
    out.write("\n".join(lines))
print(count, "wells")
