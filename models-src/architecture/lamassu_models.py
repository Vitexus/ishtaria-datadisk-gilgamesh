"""Builds the lamassu (aladlammu) guardians for the game: a pair of statues and its simple collision model.

    blender -b --python models-src/architecture/lamassu_models.py -- models-src/lamassu/lamassu_derived_rodin_source.glb media/models/architecture

Writes <dir>/lamassu_pair.glb (+ _collision) and <dir>/shedu_pair.glb (+ _collision). The statue is the Rodin model made from a render of the Printables model
"Persian Lamassu" by Peter Farell (CC BY-NC, see debian/copyright and models-src/lamassu/NOTES.md for the licence question): decimated,
scaled to HEIGHT_M, standing on z = 0 and looking along -Y (glTF +Z, so with yaw 0 it looks south in the game). The pair stands GAP_M apart (centre
to centre) on either side of the origin, both looking the same way, as the guardians stand at the jambs of a gate or at the foot of a stair. The small shedu pair (a metre high) guards house doors and markets.
"""
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

SRC, OUTDIR = sys.argv[sys.argv.index("--") + 1:][:2]
# the big guardians of gates, palaces and stairs (twice the first 3.8 m: owner, 2026-10-13) and the small ones at house doors and markets
KINDS = {
    "lamassu": dict(height=7.6, gap=9.5, faces=24000, tex=1024),
    "shedu": dict(height=2.2, gap=5.4, faces=8000, tex=512),   # 2.2 m: taller than a man (the first 1.1 m were smaller than one)
}


def load(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    obj = max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.polygons))
    for o in list(bpy.data.objects):
        if o is not obj:
            bpy.data.objects.remove(o, do_unlink=True)
    obj.parent = None
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def prepare(obj, HEIGHT_M, FACES, TEX):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)     # generated meshes are split along the UV seams
    bm.to_mesh(obj.data); bm.free()
    mod = obj.modifiers.new("dec", "DECIMATE")
    mod.ratio = FACES / len(obj.data.polygons)
    bpy.ops.object.modifier_apply(modifier="dec")
    co = np.array([v.co[:] for v in obj.data.vertices])
    mn, mx = co.min(axis=0), co.max(axis=0)
    s = HEIGHT_M / (mx[2] - mn[2])
    cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
    for v in obj.data.vertices:
        v.co = Vector(((v.co.x - cx) * s, (v.co.y - cy) * s, (v.co.z - mn[2]) * s))
    obj.data.update()
    for img in bpy.data.images:
        if img.size[0] > TEX:
            img.scale(TEX, TEX)
    size = (mx - mn) * s
    print("statue faces", len(obj.data.polygons), "size (x, y, z) m", size.round(2))
    return size


def export(path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_image_format="JPEG", export_jpeg_quality=85,
                              use_selection=True)


def build(kind, height, gap, faces, tex):
    obj = load(SRC)
    size = prepare(obj, height, faces, tex)
    obj.name = kind + "_L"
    twin = bpy.data.objects.new(kind + "_R", obj.data)       # same mesh: one copy in the file, two nodes
    bpy.context.collection.objects.link(twin)
    obj.location.x, twin.location.x = -gap / 2, gap / 2
    export("%s/%s_pair.glb" % (OUTDIR, kind))
    # collision: a box per statue (a little slimmer than the body, as the wings are thin)
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for x in (-gap / 2, gap / 2):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, height / 2))
        box = bpy.context.active_object
        box.scale = (size[0] * 1.1, size[1] * 0.9, height)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    export("%s/%s_pair_collision.glb" % (OUTDIR, kind))


for kind, spec in KINDS.items():
    build(kind, **spec)
print("done")
