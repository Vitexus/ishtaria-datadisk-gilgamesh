#!/usr/bin/env python3
"""Lists the houses of Uruk that are drawn as separate buildings and writes buildings/uruk.yaml.

    tools/build_buildings.py

Reads the plan of tools/build_city.py (tools/data/uruk_city.json) and, for every house that tools/city_kinds.py does not
leave to the quarter models, writes one building: a finished house of the 0 A.D. Persian set or a building site
(models-src/architecture/uruk_building_sites.py). Positions are in the plan's frame, metres from the anchor of the place
`uruk` (x east, z south), as `structure.offset_m` is. The model is turned so that its front (+Z) points the way the house
faces; its footprint is the plot of the house; it stands on the lowest ground under that footprint, which the server
and the client decide from the terrain. Pure Python; deterministic.
"""
import json
import math
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from building_sink import sink_field  # noqa: E402
from city_kinds import kind_of  # noqa: E402

PLAN = os.path.join(HERE, "data", "uruk_city.json")
OUT = os.path.join(ROOT, "buildings", "uruk.yaml")
MODELS = "media/models/architecture/"
ZEROAD = MODELS + "zeroad/"
HOUSE_MODELS = {
    0: ["pers_house_d", "pers_house_c", "pers_house_d"],
    1: ["pers_house_c", "pers_house_b", "pers_house_d", "pers_house_c"],
    2: ["pers_house_a", "pers_house_b"],
}
SITE_MODELS = ["uruk_site_a", "uruk_site_b", "uruk_site_c", "uruk_site_d"]
SITE_SIZE = 10.0


def glb_extent(path):
    """(width, height, depth) of a glTF binary from its POSITION accessors (no node transforms in these models)."""
    with open(path, "rb") as handle:
        data = handle.read()
    length = struct.unpack("<I", data[12:16])[0]
    doc = json.loads(data[20:20 + length])
    lo = [1e18] * 3
    hi = [-1e18] * 3
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            acc = doc["accessors"][prim["attributes"]["POSITION"]]
            for i in range(3):
                lo[i] = min(lo[i], acc["min"][i])
                hi[i] = max(hi[i], acc["max"][i])
    return tuple(hi[i] - lo[i] for i in range(3))


def main():
    with open(PLAN) as handle:
        plan = json.load(handle)
    extents = {}
    for name in sum(HOUSE_MODELS.values(), []):
        extents[name] = glb_extent(os.path.join(ROOT, ZEROAD + name + ".glb"))
    rows = []
    for rec in plan["houses"]:
        kind = kind_of(rec)
        if kind == "orig":
            continue
        x, z, fx, fz, w, d, cls, floors, h0, seed, _smithy = rec
        rng = random.Random(seed)
        yaw = math.degrees(math.atan2(fx, -fz)) % 360.0
        if kind == "site":
            model = MODELS + rng.choice(SITE_MODELS) + ".glb"
            scale = [w / SITE_SIZE, 1.0, d / SITE_SIZE]
        else:
            name = rng.choice(HOUSE_MODELS[cls])
            model = ZEROAD + name + ".glb"
            dx, dy, dz = extents[name]
            sx, sz = w / dx, d / dz
            # the house keeps its own proportions (door, storeys and beams stay the size of a man's world): one scale for the
            # footprint (the geometric mean of the two), the height only a little off it for a lower or taller house
            s_all = math.sqrt(sx * sz)
            wanted = max(h0, 3.0) * max(floors, 1) + 0.8
            scale = [sx, min(max(wanted / dy, 0.85 * s_all), 1.15 * s_all), sz]
        rows.append((x, z, model, yaw, scale, (w, d)))
    rows.sort(key=lambda r: (round(r[1]), r[0]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as out:
        out.write("# Houses of Uruk drawn as separate buildings (written by tools/build_buildings.py from the city plan;\n")
        out.write("# do not edit). Format: ishtaria-protocol schemas/datadisk.schema.json, $defs/buildings.\n")
        out.write("place: uruk\nitems:\n")
        for x, z, model, yaw, scale, (w, d) in rows:
            out.write(
                f"  - {{model: {model}, x: {x:.2f}, z: {z:.2f}, yaw_deg: {yaw:.1f}, "
                f"scale: [{scale[0]:.3f}, {scale[1]:.3f}, {scale[2]:.3f}], footprint: [{w:.2f}, {d:.2f}]{sink_field(model)}}}\n"
            )
    sites = sum(1 for r in rows if "uruk_site_" in r[2])
    print(f"{OUT}: {len(rows)} buildings ({len(rows) - sites} finished 0 A.D. houses, {sites} building sites)")


if __name__ == "__main__":
    main()
