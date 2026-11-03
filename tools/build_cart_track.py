#!/usr/bin/env python3
"""Writes media/models/architecture/cart_track.glb: one 4 m stretch of a field track worn by ox-drawn carts.

    tools/build_cart_track.py [preview.png]

A flat 3 x 4 m quad lying along +Z with a painted texture (128 px per metre, embedded): packed dirt with two ruts worn by the
wheels of carts (a gauge of 1.5 m), the ridge of earth thrown up outside each, a hoof-trodden strip between them with a few tufts of
grass, and a ragged edge (alpha mask) that melts into the ground. Every row of the texture repeats at the ends, so stretches laid
one after another (the engine puts them 4 m apart along the path) run on without a seam. Pure Python with numpy and Pillow; deterministic.
"""
import io
import json
import struct
import sys

import numpy as np
from PIL import Image

PX_PER_M = 128
WIDTH_M, LENGTH_M = 3.0, 4.0
W, H = int(WIDTH_M * PX_PER_M), int(LENGTH_M * PX_PER_M)
OUT = "media/models/architecture/cart_track.glb"
rng = np.random.default_rng(2650)

u = (np.arange(W) + 0.5) / PX_PER_M - WIDTH_M / 2           # metres across the track
y = (np.arange(H) + 0.5) / PX_PER_M                          # metres along it
U, Y = np.meshgrid(u, y)
phase_y = 2 * np.pi * Y / LENGTH_M


def periodic(seed, waves, amplitude):
    """A smooth function of the position along the track that repeats every LENGTH_M."""
    r = np.random.default_rng(seed)
    total = np.zeros_like(Y)
    for k in range(1, waves + 1):
        total += r.uniform(0.4, 1.0) / k * np.sin(k * phase_y + r.uniform(0, 2 * np.pi))
    return total / total.std() * amplitude


def smooth(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)


def blotches(seed, scale, waves=6):
    """Soft blotchy noise in 0..1 that repeats along the track (sums of waves across it and along it)."""
    r = np.random.default_rng(seed)
    total = np.zeros_like(Y)
    for _ in range(waves):
        ky = r.integers(1, 7)
        ku = r.uniform(0.5, 1.0) / scale * 2 * np.pi
        total += np.sin(ky * phase_y + ku * U * r.choice([-1, 1]) + r.uniform(0, 2 * np.pi))
    total = (total - total.min()) / (total.max() - total.min())
    return total


# the wheel ruts weave a little; the two ruts of a pair stay one gauge apart
gauge = 1.5
weave = periodic(11, 3, 0.04)
left = np.abs(U - (-gauge / 2 + weave))
right = np.abs(U - (gauge / 2 + weave))
rut = np.exp(-(np.minimum(left, right) / 0.17) ** 2)                      # the groove
ridge = np.exp(-((np.minimum(left, right) - 0.31) / 0.12) ** 2)           # the earth thrown up beside it
centre = smooth(0.55, 0.15, np.abs(U - weave))                           # the strip trodden by the oxen

# the edge of the worn ground: ragged, wider where the track is well used
edge = 1.28 + periodic(5, 5, 0.09) + 0.07 * (blotches(8, 0.35) - 0.5)
coverage = (np.abs(U) < edge)

fine = rng.normal(0, 1, (H, W))
pebbles = (rng.random((H, W)) > 0.994).astype(float)
dust = blotches(21, 0.6)
tufts = (blotches(33, 0.18, 9) > 0.78) & (centre > 0.4) & (rut < 0.2)

dirt = np.array([150, 121, 86], float)
dark = np.array([82, 61, 41], float)
dry = np.array([176, 148, 108], float)
grass = np.array([96, 104, 58], float)
verge = np.array([118, 112, 70], float)

colour = dirt + (dust[..., None] - 0.5) * np.array([26, 24, 20])
colour = colour * (1 - 0.55 * rut[..., None]) + dark * 0.55 * rut[..., None]
colour = colour + ridge[..., None] * (dry - dirt) * 0.7
colour = colour * (1 - 0.35 * centre[..., None]) + dry * 0.35 * centre[..., None]
colour = np.where(tufts[..., None], colour * 0.25 + grass * 0.75, colour)
# towards the edge the dirt takes the colour of the dry steppe grass round it
toward_edge = smooth(edge - 0.45, edge, np.abs(U))
colour = colour * (1 - 0.6 * toward_edge[..., None]) + verge * 0.6 * toward_edge[..., None]
colour += fine[..., None] * 5.5
colour = np.where(pebbles[..., None] > 0, colour * 0.6 + 70, colour)
rgba = np.zeros((H, W, 4), np.uint8)
rgba[..., :3] = np.clip(colour, 0, 255).astype(np.uint8)
rgba[..., 3] = np.where(coverage, 255, 0)

png = io.BytesIO()
Image.fromarray(rgba, "RGBA").save(png, "PNG", optimize=True)
image = png.getvalue()
if len(sys.argv) > 1:
    Image.fromarray(np.concatenate([rgba, rgba], axis=0), "RGBA").save(sys.argv[1])

# ---- the glTF binary: a quad on the ground, lying along +Z, its front at +Z
half_w, half_l = WIDTH_M / 2, LENGTH_M / 2
positions = np.array([[-half_w, 0, -half_l], [half_w, 0, -half_l], [half_w, 0, half_l], [-half_w, 0, half_l]], np.float32)
normals = np.tile(np.array([0, 1, 0], np.float32), (4, 1))
uvs = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], np.float32)
indices = np.array([0, 2, 1, 0, 3, 2], np.uint16)


def pad(data, fill=b"\0"):
    return data + fill * (-len(data) % 4)


blob = b""
views, accessors = [], []
for data, target, kind, count, ctype, extra in [
    (positions.tobytes(), 34962, "VEC3", 4, 5126, {"min": positions.min(0).tolist(), "max": positions.max(0).tolist()}),
    (normals.tobytes(), 34962, "VEC3", 4, 5126, {}),
    (uvs.tobytes(), 34962, "VEC2", 4, 5126, {}),
    (indices.tobytes(), 34963, "SCALAR", 6, 5123, {}),
]:
    views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data), "target": target})
    accessors.append({"bufferView": len(views) - 1, "componentType": ctype, "count": count, "type": kind, **extra})
    blob += pad(data)
views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(image)})
blob += pad(image)

doc = {
    "asset": {"version": "2.0", "generator": "tools/build_cart_track.py"},
    "scene": 0,
    "scenes": [{"nodes": [0]}],
    "nodes": [{"mesh": 0, "name": "cart_track"}],
    "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2}, "indices": 3, "material": 0}]}],
    "materials": [{
        "name": "worn_dirt",
        "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}, "metallicFactor": 0.0, "roughnessFactor": 1.0},
        "alphaMode": "MASK", "alphaCutoff": 0.5, "doubleSided": True,
    }],
    "textures": [{"source": 0, "sampler": 0}],
    "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 10497}],
    "images": [{"bufferView": len(views) - 1, "mimeType": "image/png"}],
    "buffers": [{"byteLength": len(blob)}],
    "bufferViews": views,
    "accessors": accessors,
}
text = pad(json.dumps(doc, separators=(",", ":")).encode(), b" ")
glb = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(text) + 8 + len(blob))
glb += struct.pack("<I4s", len(text), b"JSON") + text + struct.pack("<I4s", len(blob), b"BIN\0") + blob
with open(OUT, "wb") as handle:
    handle.write(glb)
print("%s: %d bytes" % (OUT, len(glb)))
