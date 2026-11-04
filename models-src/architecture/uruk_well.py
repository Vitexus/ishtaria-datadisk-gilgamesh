"""A well of the Early Dynastic kind, after the brick-lined well that still stands open at Uruk: a round shaft lined with
pale bricks laid in rings, set on edge in the upper courses, finished with a parapet of brick almost a metre high (so
that nobody falls in and it reads as a well from afar) over a stepped footing, and a timber frame of two posts, a
crossbeam and a windlass with a rope and a clay bucket (wells lined with brick are known from Ur and Abu Salabikh).

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


def cylinder(bm, a, b, radius, n=8):
    """A closed prism of n sides from point a to point b."""
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
    brick = material("well_brick", image=BRICK)
    clay = material("well_clay", colour=(0.42, 0.26, 0.16, 1.0))
    rope_m = material("well_rope", colour=(0.55, 0.45, 0.28, 1.0))
    dark = material("well_water", colour=(0.02, 0.05, 0.06, 1.0), rough=0.2)
    wood = material("well_wood", colour=(0.34, 0.21, 0.11, 1.0), rough=0.8)
    inner = 0.6                                   # the clear radius of the shaft; the lining is one brick (0.3 m) thick
    objs = [part("lining", lambda bm: ring(bm, inner + 0.3, inner, -3.0, 0.0), brick)]
    # the footing stepped out over the ground, the parapet and its cap of flat bricks
    objs.append(part("footing", lambda bm: ring(bm, inner + 0.55, inner, 0.0, 0.1), brick))
    objs.append(part("parapet", lambda bm: (ring(bm, inner + 0.3, inner, 0.1, 0.85), ring(bm, inner + 0.42, inner - 0.05, 0.85, 0.95)), brick))
    def water(bm):
        vs = [bm.verts.new((math.cos(2 * math.pi * i / 16) * inner, math.sin(2 * math.pi * i / 16) * inner, -2.4)) for i in range(16)]
        bm.faces.new(vs)
    objs.append(part("water", water, dark))
    # the frame: posts at either side, a crossbeam, and a windlass roll with a crank under it
    post_x, beam_z = 1.05, 2.15
    def frame(bm):
        for sign in (-1, 1):
            cylinder(bm, (sign * post_x, 0.0, 0.0), (sign * post_x, 0.0, beam_z + 0.12), 0.09)
            cylinder(bm, (sign * post_x, 0.0, 0.0), (sign * (post_x - 0.55), 0.0, 0.7), 0.04)   # a brace
        cylinder(bm, (-post_x - 0.15, 0.0, beam_z), (post_x + 0.15, 0.0, beam_z), 0.07)
    objs.append(part("frame", frame, wood))
    def windlass(bm):
        cylinder(bm, (-0.8, 0.0, beam_z - 0.2), (0.8, 0.0, beam_z - 0.2), 0.1)
        cylinder(bm, (post_x + 0.05, 0.0, beam_z - 0.2), (post_x + 0.4, 0.0, beam_z - 0.2), 0.03)
        cylinder(bm, (post_x + 0.4, 0.0, beam_z - 0.2), (post_x + 0.4, 0.0, beam_z - 0.6), 0.03)   # the crank handle
    objs.append(part("windlass", windlass, wood))
    bucket_top = 1.55
    def bucket(bm):
        ring(bm, 0.14, 0.11, bucket_top - 0.26, bucket_top, n=8)
    objs.append(part("bucket", bucket, clay))
    def rope(bm):
        cylinder(bm, (0.0, 0.0, bucket_top), (0.0, 0.0, beam_z - 0.2), 0.02)
    objs.append(part("rope", rope, rope_m))
    # Blender is Z-up; the glTF exporter turns it to Y-up
    for o in bpy.context.scene.objects:
        o.select_set(True)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", use_selection=True, export_yup=True)
    print("wrote", out)


main()
