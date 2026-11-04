#!/usr/bin/env python3
"""Writes buildings/hunter_village.yaml: the village of the hunter's old father from 0 A.D. Persian buildings.

    tools/build_village.py

The village used to be a generated medieval town (Kenney Fantasy Town). This lays old-Persian houses (the 0 A.D. set
the city of Uruk uses, CC BY-SA 3.0) in two loose rings round the open square where the old father stands, every house
turned to face the square, with a smithy (the forge of the story), a storehouse, a farmstead and a corral at the edge.
Positions are metres from the anchor of the place (x east, z south); the server stands each building on the lowest
ground under its plot. Deterministic.
"""
import json
import math
import os
import random
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_sink import sink_field  # noqa: E402
from build_elders import MAN as ELDER_MAN, WOMAN as ELDER_WOMAN, dialogue_id  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
ZEROAD = "media/models/architecture/zeroad/"
OUT = os.path.join(ROOT, "buildings", "hunter_village.yaml")


def extent(name):
    with open(os.path.join(ROOT, ZEROAD + name + ".glb"), "rb") as handle:
        data = handle.read()
    doc = json.loads(data[20:20 + struct.unpack("<I", data[12:16])[0]])
    box = [a for a in doc["accessors"] if "max" in a][0]
    return [hi - lo for lo, hi in zip(box["min"], box["max"])]   # width, height, depth


# The houses are 20 % larger than the 0 A.D. proportions the village first used, so that a standing character walks
# through the gate of a house without stooping: footprints, heights and the rings they stand on grow by this factor.
HOUSE_SCALE = 1.2

rng = random.Random(2650)
rows = []


def put(name, x, z, footprint, height, jitter=8.0):
    dx, dy, dz = extent(name)
    # the front (+Z of the model) faces the square at the middle
    face = math.atan2(-x, z)                                       # bearing of the direction towards the origin
    bearing = (math.degrees(math.atan2(-x, z)) + rng.uniform(-jitter, jitter)) % 360.0
    w, d = footprint
    if name != "pers_corral":
        w, d, height = w * HOUSE_SCALE, d * HOUSE_SCALE, height * HOUSE_SCALE
        x, z = x * HOUSE_SCALE, z * HOUSE_SCALE
    s_all = math.sqrt((w / dx) * (d / dz))
    scale = [w / dx, min(max(height / dy, 0.85 * s_all), 1.15 * s_all), d / dz]
    rows.append((x, z, ZEROAD + name + ".glb", bearing, scale, (w, d)))


# an inner ring of homes round the square, an outer ring of larger houses and the yards
for k in range(9):
    angle = math.radians(k * 40.0 + rng.uniform(-6, 6))
    radius = 38.0 + rng.uniform(-3, 4)
    name = rng.choice(["pers_house_c", "pers_house_d", "pers_house_d", "pers_house_c"])
    put(name, radius * math.sin(angle), -radius * math.cos(angle), (rng.uniform(9.5, 12.0), rng.uniform(9.5, 12.0)), rng.uniform(6.5, 8.0))
for k in range(8):
    angle = math.radians(k * 45.0 + 20.0 + rng.uniform(-8, 8))
    radius = 66.0 + rng.uniform(-4, 5)
    name = rng.choice(["pers_house_a", "pers_house_b", "pers_house_c"])
    put(name, radius * math.sin(angle), -radius * math.cos(angle), (rng.uniform(12.0, 15.0), rng.uniform(12.5, 15.5)), rng.uniform(8.0, 10.0))
# the smithy of the story, a storehouse, a farmstead and a corral at the edge, away from the square
put("pers_workshop", -56.0, 42.0, (15.0, 12.0), 8.0, 3.0)
put("pers_storehouse", 58.0, 40.0, (10.0, 12.0), 7.0, 3.0)
put("pers_farmstead", 8.0, 92.0, (16.0, 16.0), 8.0, 3.0)
put("pers_corral", -80.0, -30.0, (15.0, 8.0), 3.5, 3.0)

# the trader stands in front of one of the inner-ring houses, between it and the square; the well is on the square
trader_house = rows[2]
tx, tz = trader_house[0], trader_house[1]
length = math.hypot(tx, tz)
step = trader_house[5][1] / 2.0 + 2.4
trader = (tx - tx / length * step, tz - tz / length * step)
well = (9.0, 6.0)
# the trader's stall (tools/../models-src/architecture/village_stall.py) stands beside him, its front towards the square
tangent = (-trader[1] / math.hypot(*trader), trader[0] / math.hypot(*trader))
stall = (trader[0] + tangent[0] * 2.8, trader[1] + tangent[1] * 2.8)
stall_yaw = math.degrees(math.atan2(-stall[0], stall[1])) % 360.0


def locate(x, z):
    return "{from: hunter_village, bearing_deg: %.2f, distance_m: %.2f, tolerance_m: 0}" % (
        math.degrees(math.atan2(x, -z)) % 360.0, math.hypot(x, z))


with open(os.path.join(ROOT, "places", "hunter_village_extras.yaml"), "w") as extra:
    extra.write("# The trader's spot and the well of the old father's village (written by tools/build_village.py; do not edit).\n\n")
    extra.write("- id: hunter_village_trader\n  kind: landmark\n  name_key: place.hunter_village_trader\n  radius_m: 4\n")
    extra.write("  locate: %s\n  requires:\n    max_slope_deg: 45\n\n" % locate(*trader))
    extra.write("- id: hunter_village_well\n  kind: landmark\n  name_key: place.hunter_village_well\n  radius_m: 4\n")
    extra.write("  locate: %s\n  structure:\n    model: media/models/architecture/uruk_well.glb\n    visible_m: 500\n" % locate(*well))
    extra.write("  requires:\n    max_slope_deg: 45\n\n")
    extra.write("- id: hunter_village_stall\n  kind: landmark\n  name_key: place.hunter_village_stall\n  radius_m: 4\n")
    extra.write("  locate: %s\n  structure:\n    model: media/models/architecture/village_stall.glb\n    yaw_deg: %.1f\n    visible_m: 500\n" % (locate(*stall), stall_yaw))
    extra.write("  requires:\n    max_slope_deg: 45\n")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as out:
    out.write("# The village of the hunter's old father: 0 A.D. Persian houses round the square (written by tools/build_village.py;\n")
    out.write("# do not edit). Format: ishtaria-protocol schemas/datadisk.schema.json, $defs/buildings.\n")
    out.write("place: hunter_village\nitems:\n")
    for x, z, model, bearing, scale, (w, d) in rows:
        out.write(f"  - {{model: {model}, x: {x:.2f}, z: {z:.2f}, yaw_deg: {bearing:.1f}, "
                  f"scale: [{scale[0]:.3f}, {scale[1]:.3f}, {scale[2]:.3f}], footprint: [{w:.2f}, {d:.2f}]{sink_field(model, 1.0 if model.endswith("pers_corral.glb") else HOUSE_SCALE)}}}\n")
print(f"{OUT}: {len(rows)} buildings")

# --- the families of the houses: a man, a woman, an old man, an old woman and two children at each of the homes
# (the houses a-d; the smithy, storehouse, farmstead and corral are not homes). Each home is a landmark in front of the
# door, towards the square, where its people stand and wander about.
FOLK = [  # role, model, pack, skin, radius, speed, pause, tags
    ("man", "crowd_fisherman", "survivors", "survivorMaleB", 14, 1.0, 4, "[crowd, villager]"),
    ("woman", "crowd_young_woman", "retro", "humanFemaleA", 14, 0.95, 4, "[crowd, villager]"),
    ("old_man", "crowd_old_man", "retro", "humanMaleA", 8, 0.48, 6, "[crowd, villager, elder]"),
    ("old_woman", "crowd_grandmother", "retro", "humanFemaleA", 8, 0.42, 8, "[crowd, villager, elder]"),
    ("boy", "crowd_boy_8", "protagonists", "criminalMaleA", 20, 2.2, 1.5, "[crowd, villager, child]"),
    ("girl", "crowd_girl_8", "retro", "humanFemaleA", 20, 2.0, 2, "[crowd, villager, child]"),
]
mothers = random.Random(2651)     # about one woman in three of the village is with child
homes = [r for r in rows if os.path.basename(r[2]).startswith("pers_house_")]
with open(os.path.join(ROOT, "places", "hunter_village_homes.yaml"), "w") as places, \
        open(os.path.join(ROOT, "npcs", "hunter_village_folk.yaml"), "w") as folk:
    places.write("# The doorsteps of the homes of the old father's village (written by tools/build_village.py; do not edit).\n\n")
    folk.write("# The families of the village: a man, a woman, an old man, an old woman and two children at every home\n"
               "# (written by tools/build_village.py; do not edit). Looks and portraits are those of the crowd of Uruk.\n\n")
    for number, (x, z, model, bearing, scale, (w, d)) in enumerate(homes, 1):
        length = math.hypot(x, z)
        step = d / 2.0 + 2.5
        door = (x - x / length * step, z - z / length * step)      # in front of the door, towards the square
        home = "hunter_home_%02d" % number
        places.write("- id: %s\n  kind: landmark\n  name_key: place.hunter_home\n  radius_m: 3\n  locate: %s\n\n" % (home, locate(*door)))
        expecting = mothers.random() < 0.34
        for role, glb, pack, skin, radius, speed, pause, tags in FOLK:
            bio = "village_" + role
            if role == "woman" and expecting:
                glb, bio = "crowd_pregnant_woman", "village_pregnant_woman"
            # The old ones are the elders of the world: each tells one tale and says where one tablet lies (tools/build_elders.py).
            dialogue = {"old_man": dialogue_id(ELDER_MAN, number), "old_woman": dialogue_id(ELDER_WOMAN, number)}.get(role, "crowd_passersby")
            folk.write(
                "- id: hv_h%02d_%s\n  name_key: npc.village_%s\n  place: %s\n"
                "  character: {pack: %s, skin: %s, model: media/models/%s.glb}\n"
                "  portrait: media/portraits/%s.jpg\n  dialogue: %s\n  bio_key: npc.%s.bio\n"
                "  movement: {kind: wander, radius_m: %g, speed_m_s: %g, pause_s: %g}\n  tags: %s\n\n"
                % (number, role, role, home, pack, skin, glb, glb, dialogue, bio, radius, speed, pause, tags))
print("%d homes, %d villagers" % (len(homes), len(homes) * len(FOLK)))
