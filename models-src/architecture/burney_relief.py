"""Prepares the photogrammetry scan of the Burney Relief (Queen of the Night, British Museum) for the game.

    blender -b --python models-src/architecture/burney_relief.py -- models-src/burney_relief/scene.gltf media/models/architecture/burney_relief.glb

Source: "The Burney Relief" by danielpett (https://sketchfab.com/3d-models/the-burney-relief-217a01bf2d324ad19a05e54256b2824e),
CC BY 4.0 (models-src/burney_relief/license.txt). Changes: the six pieces are joined and welded, decimated to about TARGET faces, the
textures are scaled down to TEX px, the model is scaled so that it is HEIGHT_M high and put with its lower edge at z=0, centred in x, the
back of the plaque at y=0 and the face looking along -Y. The damage is then repaired (broken neck, the crack on the right). Exported with glTF +Y up as the other models.
"""
import sys

import bmesh
import bpy
import cv2
import numpy as np
from scipy.spatial import cKDTree
from mathutils import Vector

SRC, OUT = sys.argv[sys.argv.index("--") + 1:][:2]
TARGET = 45000
TEX = 2048
HEIGHT_M = 2.4
RESTORE = False   # patching depth and texture in place crumples the neck and leaves a smudge on the crack (tried 2026-10-13): off

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:  # the glTF root empties carry the scene's rotation and scale: bake them into the meshes
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bm = bmesh.new(); bm.from_mesh(obj.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.00005)
bm.to_mesh(obj.data); bm.free()
n0 = len(obj.data.polygons)
mod = obj.modifiers.new("dec", "DECIMATE")
mod.ratio = TARGET / n0
bpy.ops.object.modifier_apply(modifier="dec")
print("faces", n0, "->", len(obj.data.polygons))
co = [v.co for v in obj.data.vertices]
mn = Vector([min(c[i] for c in co) for i in range(3)]); mx = Vector([max(c[i] for c in co) for i in range(3)])
s = HEIGHT_M / (mx.z - mn.z)
cx = (mn.x + mx.x) / 2
for v in obj.data.vertices:
    v.co = Vector(((v.co.x - cx) * s, (v.co.y - mx.y) * s, (v.co.z - mn.z) * s))
obj.data.update()
print("size m", (mx.x - mn.x) * s, (mx.y - mn.y) * s, HEIGHT_M)
# ---- restoration (the owner asked for the relief as it left the workshop): the broken-off piece of the neck and the crack on the right
# Front-view coordinates (x right, z up, metres, read from orthographic renders with a grid).
CRACKS = [  # polyline (x, z), half width in metres
    ([(0.36, 1.47), (0.41, 1.45), (0.47, 1.42), (0.55, 1.38), (0.63, 1.34), (0.72, 1.31), (0.80, 1.30), (0.89, 1.30)], 0.030),
    ([(0.64, 1.32), (0.72, 1.25), (0.80, 1.19), (0.84, 1.15)], 0.025),
]
BLOBS = [  # (cx, cz, rx, rz): the pit in the crack, the chipped neck
    (0.475, 1.395, 0.045, 0.045),
    (0.02, 1.89, 0.10, 0.045),
]
FEATHER = 1.8


def seg_dist(px, pz, a, b):
    ax, az, bx, bz = a[0], a[1], b[0], b[1]
    dx, dz = bx - ax, bz - az
    t = np.clip(((px - ax) * dx + (pz - az) * dz) / (dx * dx + dz * dz), 0, 1)
    return np.hypot(px - (ax + t * dx), pz - (az + t * dz))


def restoration_weight(x, z):
    """0 outside, 1 inside the damaged places, smooth in between (also the units of the feather)."""
    d = np.full(len(x), 9.0)
    for pts, hw in CRACKS:
        for a, b in zip(pts, pts[1:]):
            d = np.minimum(d, seg_dist(x, z, a, b) / hw)
    for cx, cz, rx, rz in BLOBS:
        d = np.minimum(d, np.hypot((x - cx) / rx, (z - cz) / rz))
    t = np.clip((FEATHER - d) / (FEATHER - 1.0), 0, 1)
    return t * t * (3 - 2 * t)


P = np.array([v.co[:] for v in obj.data.vertices])
W = restoration_weight(P[:, 0], P[:, 2]) if RESTORE else np.zeros(len(P))
src = np.where(W == 0)[0]
dst = np.where(W > 0)[0]
tree = cKDTree(P[src][:, [0, 2]])
R = 0.07
newy = P[:, 1].copy()
for i in dst:
    idx = tree.query_ball_point(P[i, [0, 2]], R)
    if len(idx) < 3:
        continue
    q = P[src[idx]]
    w = np.exp(-(np.hypot(q[:, 0] - P[i, 0], q[:, 2] - P[i, 2]) / (R / 2)) ** 2)
    newy[i] = P[i, 1] * (1 - W[i]) + (q[:, 1] * w).sum() / w.sum() * W[i]
for i in dst:
    obj.data.vertices[i].co.y = newy[i]
obj.data.update()
print("restored vertices", len(dst))

# texture: paint the same places over with the surrounding stone (OpenCV inpainting), per material image
uv = obj.data.uv_layers.active.data
by_mat = {}
for poly in obj.data.polygons:
    by_mat.setdefault(poly.material_index, []).append(poly)
for mi, polys in by_mat.items():
    mat = obj.data.materials[mi]
    img = next(n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE")
    us = [uv[l].uv[0] for poly in polys for l in poly.loop_indices]
    vs = [uv[l].uv[1] for poly in polys for l in poly.loop_indices]
    u0, v0 = np.floor(min(us)), np.floor(min(vs))
    print("material", mat.name, "uv range", min(us), max(us), min(vs), max(vs), img.size[:])
    if img.size[0] > TEX:
        img.scale(TEX, int(TEX * img.size[1] / img.size[0]))
    w_, h_ = img.size
    arr = np.array(img.pixels[:], dtype=np.float32).reshape(h_, w_, 4)
    mask = np.zeros((h_, w_), np.uint8)
    for poly in polys:
        vi = poly.vertices
        if max(W[v] for v in vi) <= 0.0:
            continue
        pts = np.array([[(uv[l].uv[0] - u0) * w_, (uv[l].uv[1] - v0) * h_] for l in poly.loop_indices], np.int32)
        cv2.fillPoly(mask, [pts], 255)
    if mask.any():
        mask = cv2.dilate(mask, np.ones((7, 7), np.uint8))
        rgb8 = (np.clip(arr[:, :, :3], 0, 1) * 255).astype(np.uint8)
        filled = cv2.inpaint(rgb8, mask, 9, cv2.INPAINT_TELEA)
        # grain: the inpainting is smooth, stone is not
        noise = np.random.default_rng(3).normal(0, 4, filled.shape[:2])[..., None]
        filled = np.clip(filled.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        m = mask > 0
        rgb8[m] = filled[m]
        arr[:, :, :3] = rgb8 / 255.0
        img.pixels[:] = arr.ravel()
        img.update()
        print("  inpainted pixels", int(m.sum()))
for img in bpy.data.images:
    if img.size[0] > TEX:
        img.scale(TEX, int(TEX * img.size[1] / img.size[0]))
for m in obj.data.materials:
    print("material", m.name)
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_yup=True, export_image_format="JPEG", export_jpeg_quality=85)
print("exported", OUT)
