"""Houses of Uruk that are still being built: four building-site models for buildings/uruk.yaml.

    blender -b --factory-startup -P models-src/architecture/uruk_building_sites.py -- media/models/architecture

Writes uruk_site_a.glb .. uruk_site_d.glb: a 10 x 10 m plot (x = width, z = depth, +Z the front with the door gap,
+Y up, origin in the middle of the plot on the ground) with a mud-brick platform, walls laid up to different heights
in steps (a bricklayer builds a corner first), brick stacks and a mud heap at the front, scaffold poles with rails.
build_buildings.py scales a model in x and z to the plot of the house it stands for. Everything is plain boxes, the
walls use media/textures/mud_brick.png, the poles a flat wood colour. Deterministic.
"""
import math
import os
import random
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
BRICK = os.path.join(HERE, "..", "..", "media", "textures", "mud_brick.png")
SIZE = 10.0
VARIANTS = {
    # name: (seed, how far the work has got, height of a full wall in metres)
    "a": (101, 0.30, 4.0),
    "b": (202, 0.50, 4.4),
    "c": (303, 0.70, 4.0),
    "d": (404, 0.90, 6.6),
}


def make_materials():
    brick = bpy.data.materials.new("site_brick")
    brick.use_nodes = True
    nodes = brick.node_tree.nodes
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.95
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(BRICK)
    brick.node_tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    wood = bpy.data.materials.new("site_wood")
    wood.use_nodes = True
    wb = wood.node_tree.nodes["Principled BSDF"]
    wb.inputs["Base Color"].default_value = (0.30, 0.19, 0.10, 1.0)
    wb.inputs["Roughness"].default_value = 0.9
    return brick, wood


def build(name, seed, stage, full):
    rng = random.Random(seed)
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")

    def box(cx, cy, z0, z1, hx, hy, mat):
        """Axis-aligned box centred at (cx, cy) with half-extents hx, hy; planar UVs of 1 m per tile."""
        v = [bm.verts.new(p) for p in (
            (cx - hx, cy - hy, z0), (cx + hx, cy - hy, z0), (cx + hx, cy + hy, z0), (cx - hx, cy + hy, z0),
            (cx - hx, cy - hy, z1), (cx + hx, cy - hy, z1), (cx + hx, cy + hy, z1), (cx - hx, cy + hy, z1))]
        for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            f = bm.faces.new([v[i] for i in q])
            f.material_index = mat
            n = f.normal
            for loop in f.loops:
                p = loop.vert.co
                if abs(n.z) > 0.7:
                    loop[uv].uv = (p.x, p.y)
                elif abs(n.x) > abs(n.y):
                    loop[uv].uv = (p.y, p.z)
                else:
                    loop[uv].uv = (p.x, p.z)

    half = SIZE / 2.0
    # model frame here is Blender's (x width, y depth, z up); the glTF export turns it into +Y up and +Z = -y,
    # so the front (door side) of the plot is at -y
    box(0.0, 0.0, -0.8, 0.25, half, half, 0)
    th = 0.45
    lead = rng.uniform(0.6, 1.0) * stage
    for side in range(4):
        if side == 0:
            (px, py, ax, ay, ln) = (0.0, half - th / 2, 1.0, 0.0, SIZE)       # back
        elif side == 1:
            (px, py, ax, ay, ln) = (0.0, -half + th / 2, 1.0, 0.0, SIZE)      # front, door gap
        elif side == 2:
            (px, py, ax, ay, ln) = (-half + th / 2, 0.0, 0.0, 1.0, SIZE)
        else:
            (px, py, ax, ay, ln) = (half - th / 2, 0.0, 0.0, 1.0, SIZE)
        nseg = int(ln)
        for i in range(nseg):
            t = (i + 0.5) - ln / 2.0
            if side == 1 and abs(t) < 0.8:
                continue
            prof = 0.5 + 0.5 * math.cos((i / (nseg - 1.0) - rng.random() * 0.3) * math.pi * 1.3)
            hgt = max(0.25, min(full, full * lead * (0.35 + 0.65 * prof)) + rng.uniform(-0.1, 0.1))
            hgt = round(hgt / 0.3) * 0.3 + 0.1
            hx = 0.5 if ay == 0.0 else th / 2
            hy = th / 2 if ay == 0.0 else 0.5
            box(px + ax * t, py + ay * t, 0.2, 0.25 + hgt, hx, hy, 0)
    # brick stacks and a mud heap in front of the door
    for _ in range(rng.randint(2, 4)):
        box(rng.uniform(-half, half), -half - rng.uniform(1.2, 2.8), -0.1, rng.uniform(0.4, 0.9), 0.55, 0.3, 0)
    # scaffold: poles and two rails along the front
    top = 0.25 + full * stage
    for j in range(4):
        box((j + 0.5) / 4 * SIZE - half, -half - 0.9, -0.2, max(top + 1.2, 2.0), 0.08, 0.08, 1)
    for lvl in (0.45, 0.9):
        zr = 0.25 + (top) * lvl
        box(0.0, -half - 0.9, zr, zr + 0.1, half, 0.07, 1)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for m in make_materials():
        mesh.materials.append(m)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    os.makedirs(out, exist_ok=True)
    for key, (seed, stage, full) in VARIANTS.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        obj = build("uruk_site_" + key, seed, stage, full)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        path = os.path.join(out, "uruk_site_%s.glb" % key)
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_yup=True,
                                  export_image_format="JPEG", export_jpeg_quality=75, export_apply=False,
                                  export_lights=False, export_cameras=False, export_animations=False)
        print("exported", path, os.path.getsize(path), "bytes")


main()
