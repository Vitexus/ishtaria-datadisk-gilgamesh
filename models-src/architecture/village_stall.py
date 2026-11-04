"""A market stall of the old father's village: a timber frame with a striped cloth awning, a counter with fruit, pots
and loaves, crates and sacks behind it. About 3.2 m wide and 2.2 m deep, 2.7 m high at the back; the front (where the
trader stands) is glTF +Z.

    blender -b --factory-startup -P models-src/architecture/village_stall.py -- media/models/architecture/village_stall.glb

Metres, +Y up, origin in the middle of the floor. Deterministic.
"""
import math
import os
import sys

import bmesh
import bpy


def material(name, colour, rough=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = colour
    b.inputs["Roughness"].default_value = rough
    return m


def part(name, builder, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    builder(bm)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    return ob


def box(bm, x0, x1, y0, y1, z0, z1):
    v = [bm.verts.new((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    for quad in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([v[i] for i in quad])


def cylinder(bm, a, b, radius, n=10):
    ax = [b[i] - a[i] for i in range(3)]
    length = math.sqrt(sum(c * c for c in ax))
    d = [c / length for c in ax]
    ref = (1.0, 0.0, 0.0) if abs(d[0]) < 0.9 else (0.0, 1.0, 0.0)
    u = [d[1] * ref[2] - d[2] * ref[1], d[2] * ref[0] - d[0] * ref[2], d[0] * ref[1] - d[1] * ref[0]]
    ul = math.sqrt(sum(c * c for c in u))
    u = [c / ul for c in u]
    w = [d[1] * u[2] - d[2] * u[1], d[2] * u[0] - d[0] * u[2], d[0] * u[1] - d[1] * u[0]]

    def circle(p):
        return [bm.verts.new(tuple(p[k] + radius * (math.cos(2 * math.pi * i / n) * u[k] + math.sin(2 * math.pi * i / n) * w[k]) for k in range(3))) for i in range(n)]

    c0, c1 = circle(a), circle(b)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((c0[i], c0[j], c1[j], c1[i]))
    bm.faces.new(c0[::-1])
    bm.faces.new(c1)


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    wood = material("stall_wood", (0.36, 0.23, 0.12, 1.0), 0.8)
    plank = material("stall_plank", (0.5, 0.36, 0.2, 1.0), 0.85)
    red = material("stall_cloth_red", (0.62, 0.22, 0.12, 1.0))
    cream = material("stall_cloth_cream", (0.88, 0.8, 0.62, 1.0))
    clay = material("stall_clay", (0.55, 0.32, 0.18, 1.0))
    orange = material("stall_orange", (0.9, 0.5, 0.1, 1.0), 0.6)
    green = material("stall_green", (0.35, 0.55, 0.18, 1.0), 0.6)
    bread = material("stall_bread", (0.72, 0.5, 0.26, 1.0))
    sack = material("stall_sack", (0.7, 0.62, 0.45, 1.0))
    # Blender -Y becomes glTF +Z: the front (the customer's side) is at -Y
    FRONT, BACK = -1.0, 0.9
    objs = []
    def frame(bm):
        for x in (-1.5, 1.5):
            cylinder(bm, (x, FRONT, 0.0), (x, FRONT, 2.2), 0.05)
            cylinder(bm, (x, BACK, 0.0), (x, BACK, 2.65), 0.05)
        for y in (FRONT, BACK):
            top = 2.2 if y == FRONT else 2.65
            cylinder(bm, (-1.55, y, top), (1.55, y, top), 0.04)
    objs.append(part("frame", frame, wood))
    # the awning: stripes of two cloths, sloping down to the front and hanging a little over it
    def stripes(colour_a):
        def build(bm):
            count = 8
            for i in range(count):
                if (i % 2 == 0) != colour_a:
                    continue
                x0 = -1.75 + 3.5 * i / count
                x1 = -1.75 + 3.5 * (i + 1) / count
                back = (BACK + 0.1, 2.7)
                front = (FRONT - 0.45, 2.12)
                corners = [(x0, back[0], back[1]), (x1, back[0], back[1]), (x1, front[0], front[1]), (x0, front[0], front[1])]
                bm.faces.new([bm.verts.new(c) for c in corners])
                bm.faces.new([bm.verts.new(c) for c in corners[::-1]])        # the underside: cloth is seen from both sides
        return build
    objs.append(part("awning_red", stripes(True), red))
    objs.append(part("awning_cream", stripes(False), cream))
    def counter(bm):
        box(bm, -1.4, 1.4, FRONT + 0.1, FRONT + 0.7, 0.0, 0.9)
        box(bm, -1.5, 1.5, FRONT + 0.05, FRONT + 0.8, 0.9, 0.96)
    objs.append(part("counter", counter, plank))
    def shelf(bm):
        box(bm, -1.4, 1.4, BACK - 0.5, BACK, 0.0, 0.9)
        box(bm, -1.4, 1.4, BACK - 0.45, BACK - 0.05, 1.25, 1.3)       # a shelf above the back table
    objs.append(part("back_table", shelf, wood))
    def pots(bm):
        for x, z in ((-1.05, 0.96), (0.9, 0.96), (-0.4, 1.3), (0.5, 1.3)):
            y = FRONT + 0.45 if z < 1.0 else BACK - 0.25
            cylinder(bm, (x, y, z), (x, y, z + 0.32), 0.13)
            cylinder(bm, (x, y, z + 0.32), (x, y, z + 0.4), 0.07)
    objs.append(part("pots", pots, clay))
    def oranges(bm):
        for i in range(6):
            x = -0.3 + 0.17 * (i % 3) + 0.0
            y = FRONT + 0.4 + 0.17 * (i // 3)
            cylinder(bm, (x, y, 0.96), (x, y, 1.1), 0.08, 8)
    objs.append(part("oranges", oranges, orange))
    def greens(bm):
        for i in range(6):
            x = 0.2 + 0.17 * (i % 3)
            y = FRONT + 0.4 + 0.17 * (i // 3)
            cylinder(bm, (x, y, 0.96), (x, y, 1.08), 0.08, 8)
    objs.append(part("greens", greens, green))
    def loaves(bm):
        for i in range(4):
            x = -1.25 + 0.22 * i
            cylinder(bm, (x, FRONT + 0.4, 1.02), (x, FRONT + 0.4 + 0.3, 1.02), 0.07, 8)
    objs.append(part("loaves", loaves, bread))
    def crates(bm):
        box(bm, 1.7, 2.3, BACK - 0.6, BACK, 0.0, 0.45)
        box(bm, 1.75, 2.25, BACK - 0.55, BACK - 0.05, 0.45, 0.9)
    objs.append(part("crates", crates, plank))
    def sacks(bm):
        for x, y in ((-1.9, -0.3), (-2.2, 0.2)):
            box(bm, x - 0.22, x + 0.22, y - 0.2, y + 0.2, 0.0, 0.55)
    objs.append(part("sacks", sacks, sack))
    for o in bpy.context.scene.objects:
        o.select_set(True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True)
    print("wrote", out)


main()
