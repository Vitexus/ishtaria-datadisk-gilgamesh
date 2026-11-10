#!/usr/bin/env python3
"""Writes media/models/architecture/zeroad/palisade_gate_open.glb: the gate of the 0 A.D. wooden palisade with its doors taken out.

    tools/build_palisade_gate.py

The 0 A.D. gate (props/palisade_rocks_gate, converted into the same folder by ishtaria-client/tools/zeroad-structures.py as
palisade_gate.glb, CC BY-SA 3.0, Wildfire Games) is drawn with its two leaves shut; a character walks through a gate, so the
triangles of the leaves are dropped and the two posts with their rocks stay. Deterministic.
"""
import importlib.util
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CLIENT = os.path.join(ROOT, "..", "ishtaria-client")
sys.path.insert(0, HERE)
from compose_glb import accessor_array, read_glb  # noqa: E402

spec = importlib.util.spec_from_file_location("zeroad_structures", os.path.join(CLIENT, "tools", "zeroad-structures.py"))
structures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structures)

FOLDER = os.path.join(ROOT, "media", "models", "architecture", "zeroad")
LEAVES_X = (-5.3, 5.5)       # the doors fill the gap between the posts
LEAVES_MIN_Y = 1.0           # model metres; the rocks of the posts lie lower and farther out


def main():
    document, blob = read_glb(os.path.join(FOLDER, "palisade_gate.glb"))
    attributes = document["meshes"][0]["primitives"][0]["attributes"]
    positions = accessor_array(document, blob, attributes["POSITION"]).astype("<f4")
    normals = accessor_array(document, blob, attributes["NORMAL"]).astype("<f4")
    uvs = accessor_array(document, blob, attributes["TEXCOORD_0"]).astype("<f4")
    view = document["bufferViews"][document["images"][0]["bufferView"]]
    png = bytes(blob[view["byteOffset"]: view["byteOffset"] + view["byteLength"]])
    middle = positions.reshape(-1, 3, 3).mean(axis=1)
    leaf = (middle[:, 0] > LEAVES_X[0]) & (middle[:, 0] < LEAVES_X[1]) & (middle[:, 1] > LEAVES_MIN_Y)
    keep = np.repeat(~leaf, 3)
    out = os.path.join(FOLDER, "palisade_gate_open.glb")
    with open(out, "wb") as handle:
        handle.write(structures.glb(positions[keep], normals[keep], uvs[keep], png))
    print("%s: %d of %d triangles kept, %d bytes" % (os.path.relpath(out, ROOT), keep.sum() // 3, len(keep) // 3, os.path.getsize(out)))


if __name__ == "__main__":
    main()
