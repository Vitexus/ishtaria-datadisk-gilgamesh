"""Assembles the lamassu (aladlammu) from two Rodin meshes: a winged bull and the bearded head of a man.

    blender -b --python models-src/rodin_lamassu_assemble.py -- lamassu/lamassu_body_rodin_source.glb \
        lamassu/lamassu_head_rodin_source.glb lamassu/lamassu_assembled.glb

A text-to-image model draws the bull body with a bull's or a horse's head, never with the head of a man, so the animal head is cut off
at the top of the neck and the bust of a bearded man in a horned tiara (a second Rodin generation) is put on. Both look along -Y,
z up. Result: metres, feet on z=0, looking along -Y, a bull of about 1.9 m height with the neck raised (scaled by the placer).
"""
import sys

import bmesh
import bpy
from mathutils import Vector

BODY, HEAD, OUT = sys.argv[sys.argv.index("--") + 1:][:3]
BODY_CUT = 0.20          # source z of the plane where the animal head is cut off (top of the neck column)
HEAD_CUT = -0.55         # source z of the plane under the man's beard where the bust is cut
HEAD_SCALE = 0.80
HEAD_DROP = 0.0          # extra lowering of the head into the neck


def load(path, name):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before and o.type == "MESH"]
    obj = max(new, key=lambda o: len(o.data.polygons))
    for o in list(bpy.data.objects):
        if o not in before and o is not obj:
            bpy.data.objects.remove(o, do_unlink=True)
    obj.parent = None
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.name = name
    return obj


def weld(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bm.to_mesh(obj.data); bm.free()


def cut(obj, z, keep_below):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, z), plane_no=(0, 0, 1),
                           clear_outer=keep_below, clear_inner=not keep_below)
    bm.to_mesh(obj.data); bm.free()


def section_centre(obj, z, eps=0.004):
    pts = [v.co for v in obj.data.vertices if abs(v.co.z - z) < eps]
    return Vector((sum(p.x for p in pts) / len(pts), sum(p.y for p in pts) / len(pts), z)), len(pts)


bpy.ops.wm.read_factory_settings(use_empty=True)
body = load(BODY, "bull")
head = load(HEAD, "head")
weld(body); weld(head)
cut(body, BODY_CUT, keep_below=True)
cut(head, HEAD_CUT, keep_below=False)
# the neck is cut, put the head on it: scale, then centre the two cross-sections
bc, nb = section_centre(body, BODY_CUT)
for v in head.data.vertices:
    v.co = v.co * HEAD_SCALE
hc, nh = section_centre(head, HEAD_CUT * HEAD_SCALE)
shift = Vector((bc.x - hc.x, bc.y - hc.y, bc.z - hc.z - HEAD_DROP))
for v in head.data.vertices:
    v.co += shift
head.data.update()
print("neck section", tuple(bc), nb, "head section", tuple(hc), nh)
# stand on z=0
zmin = min(v.co.z for v in body.data.vertices)
for o in (body, head):
    for v in o.data.vertices:
        v.co.z -= zmin
    o.data.update()
print("body faces", len(body.data.polygons), "head faces", len(head.data.polygons))
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); head.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_yup=True, export_image_format="JPEG")
print("exported", OUT)
