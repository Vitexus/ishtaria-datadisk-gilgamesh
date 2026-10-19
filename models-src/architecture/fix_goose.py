"""Re-export goose.glb standing (largest dimension = +Z height 0.55 m).

Prefer re-downloading from Sketchfab via Blender MCP when the source mesh is gone.
This script only repairs an already-exported GLB whose tallest axis is not +Z.

    blender -b --python models-src/architecture/fix_goose.py
"""
import math
import sys

import bpy
from mathutils import Vector

OUT = "/home/vitex/Projects/Ishtaria/ishtaria-client/assets/hyper3d/ed/goose.glb"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=OUT)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
if not meshes:
    sys.exit("no mesh in goose.glb")
obj = meshes[0]
if obj.animation_data:
    obj.animation_data_clear()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)

bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
sizes = [max(v[i] for v in bb) - min(v[i] for v in bb) for i in range(3)]
up_axis = max(range(3), key=lambda i: sizes[i])
if up_axis == 0:
    obj.rotation_euler = (0, math.radians(-90), 0)
elif up_axis == 1:
    obj.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
h = max(v.z for v in bb) - min(v.z for v in bb)
obj.scale *= 0.55 / max(h, 1e-6)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
obj.location -= Vector(
    (
        (min(v.x for v in bb) + max(v.x for v in bb)) / 2,
        (min(v.y for v in bb) + max(v.y for v in bb)) / 2,
        min(v.z for v in bb),
    )
)
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

mat = bpy.data.materials.new("goose_mat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.72, 0.72, 0.68, 1.0)
bsdf.inputs["Roughness"].default_value = 0.7
obj.data.materials.clear()
obj.data.materials.append(mat)
obj.name = "goose"

obj.animation_data_create()
idle = bpy.data.actions.new(name="Idle")
fcz = idle.fcurves.new(data_path="location", index=2)
for frame, z in [(1, 0.0), (30, 0.012), (60, 0.0)]:
    fcz.keyframe_points.insert(frame, z).interpolation = "BEZIER"
idle.use_fake_user = True
walk = bpy.data.actions.new(name="Walk")
fcz = walk.fcurves.new(data_path="location", index=2)
for frame, z in [(1, 0.0), (10, 0.028), (20, 0.0), (30, 0.028), (40, 0.0)]:
    fcz.keyframe_points.insert(frame, z).interpolation = "BEZIER"
fcr = walk.fcurves.new(data_path="rotation_euler", index=0)
for frame, r in [(1, 0.0), (10, -0.04), (20, 0.0), (30, 0.04), (40, 0.0)]:
    fcr.keyframe_points.insert(frame, r).interpolation = "BEZIER"
walk.use_fake_user = True
t1 = obj.animation_data.nla_tracks.new()
t1.name = "Idle"
t1.strips.new("Idle", 1, idle)
t2 = obj.animation_data.nla_tracks.new()
t2.name = "Walk"
t2.strips.new("Walk", 1, walk)

bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_animation_mode="NLA_TRACKS",
    export_apply=True,
)
bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
sizes = [round(max(v[i] for v in bb) - min(v[i] for v in bb), 3) for i in range(3)]
print("wrote", OUT, "sizes xyz", sizes, "dim", [round(x, 3) for x in obj.dimensions])
if sizes[2] < max(sizes[0], sizes[1]):
    sys.exit("goose is not standing (Z should be tallest)")
