"""Render a clip of a glTF model from the side and from the front, to look at what the retargeting did.

    blender -b --python models-src/hunter/preview_clip.py -- MODEL.glb ACTION OUT_PREFIX [FRAME ...]

Cycles render (CPU, headless) of the armature's mesh at the given frames of the action (default: five frames over the clip).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

MODEL, ACTION, PREFIX = sys.argv[sys.argv.index("--") + 1 :][:3]
FRAMES = [int(f) for f in sys.argv[sys.argv.index("--") + 4 :]]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(MODEL))
arm = max((o for o in bpy.data.objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))
action = next(a for a in bpy.data.actions if a.name.split("|")[-1] == ACTION or a.name == ACTION or a.name.startswith(ACTION))
arm.animation_data_create()
arm.animation_data.action = action
for track in list(arm.animation_data.nla_tracks):
    arm.animation_data.nla_tracks.remove(track)
arm.animation_data.action = action
start, end = [int(x) for x in action.frame_range]
if not FRAMES:
    FRAMES = [start + (end - start) * i // 4 for i in range(5)]
scene = bpy.context.scene
# Cycles on the CPU: a Workbench or EEVEE render needs a display, and this runs headless.
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 16
scene.cycles.use_denoising = False
scene.render.resolution_x, scene.render.resolution_y = 600, 400
scene.world = bpy.data.worlds.new("sky")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.6, 0.7, 0.8, 1.0)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(50), 0, math.radians(30))
bpy.context.collection.objects.link(sun)
camera = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
bpy.context.collection.objects.link(camera)
camera.data.type = "ORTHO"
camera.data.ortho_scale = 2.8
scene.camera = camera
for name, location, rotation in (("side", (6, 0, 0.9), (math.pi / 2, 0, math.pi / 2)), ("front", (0, -6, 0.9), (math.pi / 2, 0, 0))):
    camera.location, camera.rotation_euler = location, rotation
    for frame in FRAMES:
        scene.frame_set(frame)
        scene.render.filepath = os.path.abspath("%s_%s_%03d.png" % (PREFIX, name, frame))
        bpy.ops.render.render(write_still=True)
print("frames", FRAMES, "of", start, end)
