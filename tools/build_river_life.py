#!/usr/bin/env python3
"""Writes places/uruk_river.yaml: the green banks of the Euphrates, the harbour of Uruk and the boats on the river.

    tools/build_river_life.py

Reads the landscape patch of Uruk (media/terrain/uruk_water.png, media/terrain/uruk_height.png) and follows the river's
course from it. The Sumerian texts put reed beds (gi), tamarisk, Euphrates poplar (asal) and willow, date-palm groves and
gardens along the watercourses, and Uruk had its own quay (kar) on the Euphrates (research/LANDSCAPE.md): so
  * every ~330 m of the river a small wildlife overlay with dense reeds at the water, then shrubs and trees behind them
    (the server picks the smallest overlay that covers a point, so these win over the wide one of the city);
  * a harbour on the city's bank where the river comes nearest: the 0 A.D. dock, with a merchant ship, a bireme and
    two fishing boats moored at it (they float at the water surface, `structure.on_water`);
  * fishing boats (0 A.D. fishing ship, scaled to a river boat) spread along the river.
Positions are surveyed points from the anchor of Uruk (bearing and distance), exactly where this puts them. Deterministic.
"""
import math
import os
import random

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "places", "uruk_river.yaml")
STEP = 10.0            # metres per pixel of the patch (6000 m over 600 px)
HALF = 300
ZEROAD = "media/models/architecture/zeroad/"

water = np.array(Image.open(os.path.join(ROOT, "media", "terrain", "uruk_water.png"))).astype(int)
wet = water > 0


def to_plan(col, row):
    """Pixel -> metres east and south of the anchor."""
    return ((col + 0.5 - HALF) * STEP, (row + 0.5 - HALF) * STEP)


def is_wet(x, z):
    col, row = int(x / STEP + HALF), int(z / STEP + HALF)
    return 0 <= col < 600 and 0 <= row < 600 and bool(wet[row, col])


def bearing_distance(x, z):
    return math.degrees(math.atan2(x, -z)) % 360.0, math.hypot(x, z)


def locate(x, z):
    b, d = bearing_distance(x, z)
    return "{from: uruk, bearing_deg: %.2f, distance_m: %.1f, tolerance_m: 0}" % (b, d)


# the river's centre line: the middle of the wet pixels of every row (it runs north-south through the patch)
centre = []
for row in range(600):
    cols = np.nonzero(wet[row])[0]
    if len(cols):
        centre.append(to_plan(cols.mean(), row))
width_m = float(wet.sum(axis=1).mean()) * STEP


def along(index):
    a = centre[max(index - 4, 0)]
    b = centre[min(index + 4, len(centre) - 1)]
    t = (b[0] - a[0], b[1] - a[1])
    n = math.hypot(*t)
    return (t[0] / n, t[1] / n)


def yaw_of(direction):
    """The yaw_deg that turns a model's front (+Z) to the direction (east, south)."""
    return math.degrees(math.atan2(direction[0], direction[1])) % 360.0


rng = random.Random(2700)
lines = [
    "# The green banks, the harbour and the boats of the Euphrates at Uruk (written by tools/build_river_life.py; do not edit).",
    "# Reed beds, tamarisk, poplar, willow and date palms along the river; the quay of Uruk with its dock and ships.",
    "",
]

REEDS = [("nature.reed_clump", 10), ("zeroad.reed_pond_lush", 7), ("zeroad.reed_giant", 5), ("zeroad.reed_beach_a", 5),
         ("zeroad.reed_beach_b", 5), ("zeroad.papyrus_1", 3), ("zeroad.papyrus_2", 3), ("zeroad.cattails", 5)]
SHRUBS = [("hyper3d.tamarisk", 8), ("zeroad.tamarix_a", 6), ("zeroad.bush_desert_a", 3), ("nature.plant_bushSmall", 2),
          ("nature.plant_bushLarge", 2), ("quaternius.bush_1", 2)]
TREES = [("zeroad.poplar_lombardy", 6), ("zeroad.willow_a", 6), ("zeroad.fig_a", 2), ("zeroad.fig_b", 2),
         ("nature.tree_palmTall", 4), ("nature.tree_palmDetailedTall", 3), ("nature.tree_palmShort", 3),
         ("zeroad.palm_date_a", 4), ("zeroad.palm_date_b", 4), ("zeroad.palm_date_c", 3), ("zeroad.palm_date_new_1", 3),
         ("zeroad.palm_date_new_2", 2), ("zeroad.palm_date_fruit_1", 2)]
FAUNA = [("animal.duck", 6, True), ("animal.goose", 5, True), ("animal.turtle", 3, True), ("animal.pigeon", 3, False),
         ("animal.gazelle", 2, False), ("animal.onager", 1, False), ("animal.goat", 2, False), ("animal.sheep", 2, False),
         ("animal.donkey", 1, False), ("animal.lizard", 2, False), ("zeroad.crow", 1, False)]


def flora_block():
    out = ["    flora:"]
    for ident, w in REEDS:
        out.append("      - {id: %s, weight: %d, waterside: true}" % (ident, w * 2))
    for ident, w in SHRUBS:
        out.append("      - {id: %s, weight: %d, waterside: true}" % (ident, w))
    for ident, w in TREES:
        out.append("      - {id: %s, weight: %d}" % (ident, w))
    out.append("    fauna:")
    for ident, w, side in FAUNA:
        out.append("      - {id: %s, weight: %d%s}" % (ident, w, ", waterside: true" if side else ""))
    return out


# --- the green banks: an overlay every ~330 m of the river
belts = 0
for i in range(0, len(centre), 33):
    x, z = centre[i]
    if math.hypot(x, z) < 450.0:
        continue
    belts += 1
    lines += [
        "- id: uruk_bank_%02d" % belts,
        "  kind: landmark",
        "  name_key: place.uruk_riverbank",
        "  radius_m: 20",
        "  locate: %s" % locate(x, z),
        "  wildlife:",
        "    radius_m: 230",
        "    density: 6.0",
    ] + flora_block() + ["  requires:", "    max_slope_deg: 45", ""]

# --- the harbour, on the river's bank nearest to the city
nearest = min(range(len(centre)), key=lambda k: math.hypot(*centre[k]))
cx, cz = centre[nearest]
tangent = along(nearest)
normal = (-tangent[1], tangent[0])
if normal[0] * cx + normal[1] * cz > 0:
    normal = (-normal[0], -normal[1])          # points from the river towards the city (the anchor is the origin)
# the water edge on the city's side of the channel
edge = 0.0
while is_wet(cx + normal[0] * edge, cz + normal[1] * edge):
    edge += 1.0
bank = (cx + normal[0] * edge, cz + normal[1] * edge)
to_river = (-normal[0], -normal[1])
quay_yaw = yaw_of(to_river)
dock = (bank[0] + normal[0] * 8.0, bank[1] + normal[1] * 8.0)           # the dock's front reaches the water
lines += [
    "# The quay of Uruk on the Euphrates: the 0 A.D. dock (Wildfire Games, CC BY-SA 3.0) on the bank nearest to the city,",
    "# %.0f m from the anchor, its front turned to the river." % math.hypot(*bank),
    "- id: uruk_harbour",
    "  kind: landmark",
    "  name_key: place.uruk_harbour",
    "  radius_m: 14",
    "  locate: %s" % locate(*dock),
    "  structure:",
    "    model: %spers_dock.glb" % ZEROAD,
    "    yaw_deg: %.1f" % quay_yaw,
    "    visible_m: 1400",
    "  requires:",
    "    max_slope_deg: 45",
    "",
]
moored = [("pers_merchant", 0.75, -11.0, 20.0, "merchant ship"), ("pers_bireme", 0.6, 13.0, 24.0, "bireme"),
          ("pers_fishship", 0.7, -26.0, 12.0, "fishing boat"), ("pers_fishship", 0.7, 27.0, 10.0, "fishing boat")]
boat = 0
for model, scale, lateral, out_m, label in moored:
    # lateral along the bank (the river's direction), out into the water from the water's edge
    x = bank[0] + tangent[0] * lateral + to_river[0] * out_m
    z = bank[1] + tangent[1] * lateral + to_river[1] * out_m
    if not is_wet(x, z):
        continue
    boat += 1
    lines += [
        "- id: uruk_harbour_boat_%d" % boat,
        "  kind: landmark",
        "  name_key: place.uruk_boat",
        "  radius_m: 8",
        "  locate: %s" % locate(x, z),
        "  structure:",
        "    model: %s%s.glb" % (ZEROAD, model),
        "    scale_m: %.2f" % scale,
        "    yaw_deg: %.1f" % (yaw_of(tangent) + rng.uniform(-6, 6)),
        "    visible_m: 1200",
        "    on_water: true",
        "  requires:",
        "    max_slope_deg: 45",
        "",
    ]

# --- fishing boats on the river, a few hundred metres apart
fishers = 0
for i in range(10, len(centre) - 10, 29):
    x, z = centre[i]
    t = along(i)
    n = (-t[1], t[0])
    x += n[0] * rng.uniform(-35, 35)
    z += n[1] * rng.uniform(-35, 35)
    if math.hypot(*bank) and math.hypot(x - bank[0], z - bank[1]) < 80.0:
        continue
    if not is_wet(x, z):
        continue
    fishers += 1
    lines += [
        "- id: uruk_fisher_%02d" % fishers,
        "  kind: landmark",
        "  name_key: place.uruk_fisher",
        "  radius_m: 6",
        "  locate: %s" % locate(x, z),
        "  structure:",
        "    model: %spers_fishship.glb" % ZEROAD,
        "    scale_m: 0.62",
        "    yaw_deg: %.1f" % ((yaw_of(t) + rng.choice([0.0, 180.0]) + rng.uniform(-15, 15)) % 360.0),
        "    visible_m: 1100",
        "    on_water: true",
        "  requires:",
        "    max_slope_deg: 45",
        "",
    ]

with open(OUT, "w") as handle:
    handle.write("\n".join(lines))
print(f"{OUT}: {belts} bank overlays, the harbour at {math.hypot(*bank):.0f} m ({boat} moored boats), {fishers} fishing boats; "
      f"the river is {width_m:.0f} m wide")
