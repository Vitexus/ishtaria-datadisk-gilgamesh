#!/usr/bin/env python3
"""Writes media/models/architecture/orchard_date_a.glb, orchard_date_b.glb and orchard_date_c.glb: a date-palm orchard (kiri) of
40 x 30 metres, twelve palms in four rows of three about ten metres apart, each a little off its place, turned and of its own kind.

    tools/build_orchard_models.py

The palms are the 0 A.D. date palms of the client (ishtaria-client/assets/zeroad/flora/palm_date_*.glb, CC BY-SA 3.0, Wildfire Games),
at the scale and ground offset of their catalog entries (etc/world_objects.json), joined with tools/compose_glb.py into one still model
whose x runs along the plot's depth (like the fields) and z along the canal. The buildings file of tools/build_fields.py lays them
beside the barley fields, as the drawing of research/WATER_WORKS.md has orchards (kiri) beside fields (asa). Deterministic.
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
FLORA = os.path.join(ROOT, "..", "ishtaria-client", "assets", "zeroad", "flora")
sys.path.insert(0, HERE)
from compose_glb import Part, merge, write  # noqa: E402

KINDS = ("a", "b", "c", "d", "e")
SPACING_M = 10.0
COLUMNS, ROWS = 4, 3              # along x (the depth of the plot) and z (along the canal)
SINK_M = -0.9                     # the ground offset of the catalog entries
OUT = os.path.join(ROOT, "media", "models", "architecture", "orchard_date_%s.glb")
WIDTH_M, LENGTH_M = COLUMNS * SPACING_M, ROWS * SPACING_M


def main():
    for variant, seed in (("a", 2701), ("b", 2702), ("c", 2703)):
        rng = random.Random(seed)
        parts = []
        for column in range(COLUMNS):
            for row in range(ROWS):
                x = (column + 0.5) * SPACING_M - WIDTH_M / 2.0 + rng.uniform(-1.5, 1.5)
                z = (row + 0.5) * SPACING_M - LENGTH_M / 2.0 + rng.uniform(-1.5, 1.5)
                kind = rng.choices(KINDS, weights=(3, 3, 2, 2, 1))[0]
                path = os.path.join(FLORA, "palm_date_%s.glb" % kind)
                parts.append(Part(path, translation=(x, SINK_M, z), yaw_deg=rng.uniform(0, 360), name="palm", clips=False))
        path = OUT % variant
        write(path, merge(parts, clips=(), name="orchard_date_" + variant))
        print("%s: %d palms, %d bytes" % (os.path.relpath(path, ROOT), len(parts), os.path.getsize(path)))


if __name__ == "__main__":
    main()
