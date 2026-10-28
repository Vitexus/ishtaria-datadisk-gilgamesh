"""Builds the lamassu (aladlammu) guardians for the game: a pair of statues and its simple collision model.

    blender -b --python models-src/architecture/lamassu_models.py -- media/models/architecture

Writes <dir>/lamassu_pair.glb (+ _collision) and <dir>/shedu_pair.glb (+ _collision). The statues are the 0 A.D.
models `pers_lamassu` and `pers_lamassu_small` (Wildfire Games, CC BY-SA 3.0; mirrored on this disk under
media/models/architecture/zeroad/, converted from 0 A.D.'s public.zip by ishtaria-client/tools/zeroad-structures.py,
see media/models/architecture/zeroad/License.txt and models-src/lamassu/NOTES.md): decimated, scaled to HEIGHT_M,
standing on z = 0 and looking along -Y (glTF +Z, so with yaw 0 it looks south in the game). The 0 A.D. source faces
the same way as the previous, licence-problematic Rodin model did, so the places written by tools/build_statues.py
keep their yaw; the script checks the head side and refuses to write a pair that looks the wrong way. The pair
stands GAP_M apart (centre to centre) on either side of the origin, both looking the same way, as the guardians stand
at the jambs of a gate or at the foot of a stair. The small shedu pair (a metre high) guards house doors and markets.
"""
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector

OUTDIR = sys.argv[sys.argv.index("--") + 1]
ZEROAD = "media/models/architecture/zeroad"
# the big guardians of gates, palaces and stairs (twice the first 3.8 m: owner, 2026-10-13) and the small ones at house doors and markets
KINDS = {
    "lamassu": dict(src=ZEROAD + "/pers_lamassu.glb", height=7.6, gap=9.5, faces=24000, tex=1024),
    "shedu": dict(src=ZEROAD + "/pers_lamassu_small.glb", height=2.2, gap=5.4, faces=8000, tex=512),   # 2.2 m: taller than a man (the first 1.1 m were smaller than one)
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
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)     # the 0 A.D. conversion splits every triangle corner
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
    # the head (the tiara is the highest part) must be at -Y: the game turns a model by yaw about UP, and a model
    # looking along +Z (south) at yaw 0 must look along (sin yaw, cos yaw) in (x, z) — the places of build_statues.py
    # were laid out for that convention
    top = co[co[:, 2] > mn[2] + 0.9 * (mx[2] - mn[2])]
    head_y = float(top[:, 1].mean()) if len(top) else 0.0
    if head_y > 0:
        raise SystemExit("the source model faces +Y (head at +Y); turn it to face -Y before building the pair")
    print("statue faces", len(obj.data.polygons), "size (x, y, z) m", size.round(2), "head y %.2f (must be < 0)" % head_y)
    return size


def export(path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True, export_image_format="JPEG", export_jpeg_quality=85,
                              use_selection=True)


def build(kind, src, height, gap, faces, tex):
    obj = load(src)
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
