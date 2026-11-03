"""A well of the Early Dynastic kind, after the brick-lined well that still stands open at Uruk: a round shaft lined with
pale bricks laid in rings, set on edge in the upper courses, finished with a low rim of flat bricks stepped out over the
ground, a rope and a clay bucket (wells lined with brick are known from Ur and Abu Salabikh; a bucket on a rope is all
they needed).

    blender -b --factory-startup -P models-src/architecture/uruk_well.py -- media/models/architecture/uruk_well.glb

Metres, +Y up, origin in the middle of the curb on the ground. Fresh water for `structure` drinking is recognised by the
model name `*_well.glb` (ishtaria-server survival.rs). Deterministic.
"""
import math
import os
import sys

import bmesh
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
BRICK = os.path.join(HERE, "..", "..", "media", "textures", "well_brick.png")  # tools/make_well_brick.py


def material(name, colour=None, image=None, rough=0.9):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    if image:
        t = m.node_tree.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(image)
        m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
    else:
        b.inputs["Base Color"].default_value = colour
    return m


def part(name, bm_builder, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bm_builder(bm)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(mat)
    return ob


TILES_W, TILE_H = 0.6, 0.32          # one tile of the brick texture in metres


def ring(bm, r_out, r_in, z0, z1, n=16):
    """A tube of brick (outer wall, inner wall, top, bottom). The courses run level round it: the u of the side walls is
    the arc length in whole tiles, so the pattern closes at the seam."""
    uv = bm.loops.layers.uv.verify()
    tiles_out = max(1, round(2 * math.pi * r_out / TILES_W))
    tiles_in = max(1, round(2 * math.pi * r_in / TILES_W))
    def pts(r): return [(math.cos(2 * math.pi * i / n) * r, math.sin(2 * math.pi * i / n) * r) for i in range(n)]
    ov, iv = pts(r_out), pts(r_in)
    def v(p, z): return bm.verts.new((p[0], p[1], z))
    bo0 = [v(p, z0) for p in ov]; bo1 = [v(p, z1) for p in ov]
    bi0 = [v(p, z0) for p in iv]; bi1 = [v(p, z1) for p in iv]
    for i in range(n):
        j = (i + 1) % n
        for quad, kind in (((bo0[i], bo0[j], bo1[j], bo1[i]), "out"), ((bi0[j], bi0[i], bi1[i], bi1[j]), "in"),
                           ((bo1[i], bo1[j], bi1[j], bi1[i]), "top"), ((bi0[i], bi0[j], bo0[j], bo0[i]), "top")):
            f = bm.faces.new(quad)
            for lp in f.loops:
                c = lp.vert.co
                if kind == "top":
                    lp[uv].uv = (c.x / TILES_W, c.y / TILE_H)
                else:
                    k = i if lp.vert in (quad[0], quad[3]) else i + 1
                    lp[uv].uv = (k / n * (tiles_out if kind == "out" else tiles_in), c.z / TILE_H)


def main():
    out = sys.argv[sys.argv.index("--") + 1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    brick = material("well_brick", image=BRICK)
    clay = material("well_clay", colour=(0.42, 0.26, 0.16, 1.0))
    rope_m = material("well_rope", colour=(0.55, 0.45, 0.28, 1.0))
    dark = material("well_water", colour=(0.02, 0.05, 0.06, 1.0), rough=0.2)
    inner = 0.6                                   # the clear radius of the shaft; the lining is one brick (0.3 m) thick
    objs = [part("lining", lambda bm: ring(bm, inner + 0.3, inner, -3.0, 0.0), brick)]
    # the rim: two courses of flat bricks stepped out over the ground, as the top of the excavated shaft is
    objs.append(part("rim", lambda bm: (ring(bm, inner + 0.5, inner, 0.0, 0.1), ring(bm, inner + 0.3, inner, 0.1, 0.2)), brick))
    def water(bm):
        vs = [bm.verts.new((math.cos(2 * math.pi * i / 16) * inner, math.sin(2 * math.pi * i / 16) * inner, -2.4)) for i in range(16)]
        bm.faces.new(vs)
    objs.append(part("water", water, dark))
    def bucket(bm):
        ring(bm, 0.14, 0.11, 0.2, 0.46, n=8)
    objs.append(part("bucket", bucket, clay))
    def rope(bm):
        ring(bm, 0.02, 0.0, 0.46, 0.50, n=4)
    objs.append(part("rope", rope, rope_m))
    # Blender is Z-up; the glTF exporter turns it to Y-up
    for o in bpy.context.scene.objects:
        o.select_set(True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True)
    print("wrote", out)


main()
