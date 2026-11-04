#!/usr/bin/env python3
"""Writes media/models/architecture/field_barley_green.glb, field_barley_ripe.glb and field_fallow.glb: a tilled field of ten metres
square (scaled to the plot by the buildings file), rows of crop running along the model's x.

    tools/build_field_models.py

A corrugated surface: 60 rows over the depth of the plot (z), a crest and a trough each, one unit of relief from trough to crest (the
buildings file scales it to about 0.2 m), painted with a small repeating texture (soil in the trough, barley or stubble on the crest,
the blades and the soil varying along the row). The three differ in the colour of the crop: green, ripe and none (fallow with weeds).
Pure Python with numpy and Pillow; deterministic.
"""
import io
import json
import struct

import numpy as np
from PIL import Image

OUT = "media/models/architecture/field_%s.glb"
ROWS = 60                 # rows over the depth of the plot
STEPS = 6                 # samples per row
TEX_W, TEX_H = 128, 32    # texels: along the row and across one row's period

PALETTES = {
    "barley_green": {"soil": (112, 84, 58), "crop": [(88, 138, 52), (104, 154, 60), (76, 120, 46)]},
    "barley_ripe": {"soil": (118, 88, 60), "crop": [(196, 160, 72), (212, 178, 88), (178, 142, 62)]},
    "fallow": {"soil": (126, 96, 66), "crop": [(132, 112, 78), (112, 126, 70), (140, 116, 84)]},
}


def texture(palette, seed):
    rng = np.random.default_rng(seed)
    image = np.zeros((TEX_H, TEX_W, 3), np.float32)
    soil = np.array(palette["soil"], np.float32)
    for y in range(TEX_H):
        # 0 at the trough, 1 at the crest of the row
        crest = 0.5 - 0.5 * np.cos(2 * np.pi * (y + 0.5) / TEX_H)
        for x in range(TEX_W):
            crop = np.array(palette["crop"][int(rng.integers(len(palette["crop"])))], np.float32)
            blend = np.clip((crest - 0.35) / 0.35, 0.0, 1.0)
            if palette is PALETTES["fallow"]:
                blend *= 0.45 * rng.random()          # a few weeds on bare ridges
            colour = soil * (0.82 + 0.18 * crest) * (1 - blend) + crop * blend
            image[y, x] = colour * rng.uniform(0.93, 1.07)
    out = io.BytesIO()
    Image.fromarray(np.clip(image, 0, 255).astype(np.uint8)).save(out, format="PNG")
    return out.getvalue()


def pad(data, fill=b"\0"):
    return data + fill * (-len(data) % 4)


def build(name, seed):
    zs = np.linspace(-5.0, 5.0, ROWS * STEPS + 1)
    positions, normals, uvs = [], [], []
    for index, z in enumerate(zs):
        phase = index / STEPS                          # rows so far
        height = 0.5 - 0.5 * np.cos(2 * np.pi * phase)
        slope = 0.5 * 2 * np.pi * np.sin(2 * np.pi * phase) * ROWS / 10.0     # d height / d z
        normal = np.array([0.0, 1.0, -slope * 0.2])
        normal /= np.linalg.norm(normal)
        for x in (-5.0, 5.0):
            positions.append([x, height, z])
            normals.append(normal)
            uvs.append([x / 10.0 + 0.5, phase])
    positions = np.array(positions, np.float32)
    normals = np.array(normals, np.float32)
    uvs = np.array(uvs, np.float32)
    indices = []
    for i in range(len(zs) - 1):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3
        indices += [a, c, b, b, c, d]
    indices = np.array(indices, np.uint16)
    image = texture(PALETTES[name], seed)
    blob, views, accessors = b"", [], []
    for data, target, kind, count, ctype, extra in [
        (positions.tobytes(), 34962, "VEC3", len(positions), 5126, {"min": positions.min(0).tolist(), "max": positions.max(0).tolist()}),
        (normals.tobytes(), 34962, "VEC3", len(normals), 5126, {}),
        (uvs.tobytes(), 34962, "VEC2", len(uvs), 5126, {}),
        (indices.tobytes(), 34963, "SCALAR", len(indices), 5123, {}),
    ]:
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data), "target": target})
        accessors.append({"bufferView": len(views) - 1, "componentType": ctype, "count": count, "type": kind, **extra})
        blob += pad(data)
    views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(image)})
    blob += pad(image)
    doc = {
        "asset": {"version": "2.0", "generator": "tools/build_field_models.py"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": "field_" + name}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2}, "indices": 3, "material": 0}]}],
        "materials": [{"name": name, "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 1.0}, "doubleSided": True}],
        "textures": [{"source": 0, "sampler": 0}],
        "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}],
        "images": [{"bufferView": len(views) - 1, "mimeType": "image/png"}],
        "buffers": [{"byteLength": len(blob)}], "bufferViews": views, "accessors": accessors,
    }
    text = pad(json.dumps(doc, separators=(",", ":")).encode(), b" ")
    glb = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(text) + 8 + len(blob))
    glb += struct.pack("<I4s", len(text), b"JSON") + text + struct.pack("<I4s", len(blob), b"BIN\0") + blob
    with open(OUT % name, "wb") as handle:
        handle.write(glb)
    print("%s: %d bytes" % (OUT % name, len(glb)))


if __name__ == "__main__":
    for number, name in enumerate(PALETTES):
        build(name, 2650 + number)
