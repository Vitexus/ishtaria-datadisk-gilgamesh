"""Assembles the Scorpion Man from two Rodin meshes: a giant scorpion and the upper body of a bearded man.

    blender -b --python models-src/rodin_scorpion_assemble.py -- scorpion_man/scorpion_body_rodin_source.glb \
        scorpion_man/scorpion_torso_rodin_source.glb scorpion_man/scorpion_man_assembled.glb

(a text-to-image model cannot draw the hybrid in one picture). The scorpion already looks along -Y (head and claws at the front,
the tail rising from the rear end of the abdomen); the man is cut at the belt and stands on the carapace with his waist inside it. Textures stay separate (two materials).
Metres, the creature looks along -Y, z up, feet on z=0; the rig script (rodin_rig_creature.py) takes the result.
"""
import math
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

BODY, TORSO, OUT = sys.argv[sys.argv.index("--") + 1:][:3]
BODY_HEIGHT = 0.9         # the scorpion with the tail up, metres (carapace top then at 0.7 m)
TORSO_HEIGHT = 2.7       # the whole standing man, of whom the upper half is kept
CUT = 0.96 / 2.0          # fraction of the man's height where he is cut (just under the belt)
WAIST = (0.0, -0.45, 0.62)  # where the cut of the man is put, in the scorpion frame (just inside the top of the carapace)


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


def fit(obj, height, yaw_deg, put):
    """Scale to `height`, stand on z=0, centre x/y on the bounding box, turn about Z, then move by put (x, y, z-offset)."""
    rot = Matrix.Rotation(math.radians(yaw_deg), 3, "Z")
    co = [rot @ v.co for v in obj.data.vertices]
    zmin, zmax = min(c.z for c in co), max(c.z for c in co)
    s = height / (zmax - zmin)
    cx = (min(c.x for c in co) + max(c.x for c in co)) / 2
    cy = (min(c.y for c in co) + max(c.y for c in co)) / 2
    for v, c in zip(obj.data.vertices, co):
        v.co = Vector(((c.x - cx) * s + put[0], (c.y - cy) * s + put[1], (c.z - zmin) * s + put[2]))
    obj.data.update()


def weld(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bm.to_mesh(obj.data); bm.free()


bpy.ops.wm.read_factory_settings(use_empty=True)
body = load(BODY, "scorpion")
torso = load(TORSO, "man")
fit(body, BODY_HEIGHT, 0.0, (0, 0, 0))
fit(torso, TORSO_HEIGHT, 0.0, (0, 0, 0))
# the man: cut off everything under the belt, then lower the cut to the waist position
weld(torso)
bm = bmesh.new(); bm.from_mesh(torso.data)
cut_z = TORSO_HEIGHT * CUT
bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, cut_z), plane_no=(0, 0, 1), clear_inner=True)
bm.to_mesh(torso.data); bm.free()
for v in torso.data.vertices:
    v.co += Vector((WAIST[0], WAIST[1], WAIST[2] - cut_z))
torso.data.update()
print("man faces", len(torso.data.polygons), "scorpion faces", len(body.data.polygons))
# join, keeping the two materials
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True); torso.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", export_yup=True, export_image_format="JPEG")
print("exported", OUT)
