"""Renders a character GLB: full body views for checking a model, or a bust for a portrait.

    blender -b --python tools/blender/render_preview.py -- model.glb out.png [full|bust] [action] [frame] [size] [bg]

`full` renders front, three-quarter and side views side by side. `bust` renders one head-and-shoulders
view (the portrait). `action` is Idle or Walk, `frame` the frame of that action.
"""
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
glb, out = args[0], args[1]
mode = args[2] if len(args) > 2 else "full"
action_name = args[3] if len(args) > 3 else "Idle"
frame = float(args[4]) if len(args) > 4 else 1
size = int(args[5]) if len(args) > 5 else 512
bg = tuple(float(x) for x in args[6].split(",")) if len(args) > 6 else (0.55, 0.5, 0.42)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
scene = bpy.context.scene
arm = next((o for o in scene.objects if o.type == "ARMATURE"), None)
if arm is not None:
    action = bpy.data.actions.get(action_name)
    if action is None:
        action = next((a for a in bpy.data.actions if a.name.startswith(action_name)), None)
    if action is not None:
        arm.animation_data_create()
        arm.animation_data.action = action
        scene.frame_set(int(frame))

meshes = [o for o in scene.objects if o.type == "MESH"]
depsgraph = bpy.context.evaluated_depsgraph_get()
lo = Vector((1e9,) * 3)
hi = Vector((-1e9,) * 3)
for o in meshes:
    ev = o.evaluated_get(depsgraph)
    for corner in ev.bound_box:
        w = ev.matrix_world @ Vector(corner)
        lo = Vector(map(min, lo, w))
        hi = Vector(map(max, hi, w))
height = hi.z - lo.z
center = (lo + hi) / 2

# world and light
scene.world = bpy.data.worlds.new("w")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (bg[0], bg[1], bg[2], 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
for name, loc, energy, color in (("key", (2.5, -3.5, 3.0), 700, (1.0, 0.92, 0.8)), ("fill", (-3.0, -2.5, 1.5), 250, (0.8, 0.88, 1.0)), ("rim", (0, 3.5, 3.0), 400, (1.0, 0.9, 0.7))):
    light = bpy.data.lights.new(name, "AREA")
    light.energy = energy * max(1.0, height / 1.8) ** 2
    light.color = color
    light.size = 3
    ob = bpy.data.objects.new(name, light)
    ob.location = (loc[0] * height / 1.8, loc[1] * height / 1.8, loc[2] * height / 1.8)
    scene.collection.objects.link(ob)
    direction = Vector((center.x, center.y, center.z)) - ob.location
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = "CYCLES"
scene.cycles.samples = 64
scene.cycles.use_denoising = False
scene.render.image_settings.file_format = "PNG" if out.endswith(".png") else "JPEG"


def aim(position, target, lens, shift_y=0.0):
    cam.location = position
    cam_data.lens = lens
    direction = target - position
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_data.shift_y = shift_y


def render(path, w, h):
    scene.render.resolution_x = w
    scene.render.resolution_y = h
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


if mode == "bust":
    # Aim at the head bone of the posed rig, from the front (the character faces -Y).
    head_bone = arm.pose.bones.get("Head") if arm is not None else None
    if head_bone is not None:
        head_a = arm.matrix_world @ head_bone.head
        head_b = arm.matrix_world @ head_bone.tail
        size_h = (head_b - head_a).length
        mid = (head_a + head_b) / 2
        mult = float(args[7]) if len(args) > 7 else 1.0
        dist = size_h * 4.1 * mult
        target = Vector((mid.x, mid.y, mid.z - size_h * 0.10 * mult))
        aim(Vector((mid.x, mid.y - dist, mid.z - size_h * 0.02 * mult)), target, 70)
    else:
        head = Vector((center.x, center.y, lo.z + height * 0.9))
        dist = height * 0.62
        aim(Vector((0.0, -dist, head.z - height * 0.01)), Vector((0, 0, head.z - height * 0.045)), 70)
    scene.cycles.samples = 192
    render(out, size, size)
else:
    import os
    tmp = os.path.splitext(out)[0]
    views = []
    for i, ang in enumerate((0, 40, 90)):
        a = math.radians(ang)
        dist = max(height, hi.y - lo.y, hi.x - lo.x) * 1.7
        aim(Vector((math.sin(a) * dist, -math.cos(a) * dist, lo.z + height * 0.5)), Vector((0, 0, lo.z + height * 0.5)), 50)
        path = "%s_%d.png" % (tmp, i)
        render(path, size, int(size * 1.4))
        views.append(path)
    # stitch with PIL-free approach: load and compose through Blender images
    imgs = [bpy.data.images.load(p) for p in views]
    w, h = imgs[0].size
    result = bpy.data.images.new("sheet", w * len(imgs), h)
    px = [0.0] * (w * len(imgs) * h * 4)
    for n, im in enumerate(imgs):
        data = list(im.pixels)
        for row in range(h):
            dst = (row * w * len(imgs) + n * w) * 4
            px[dst:dst + w * 4] = data[row * w * 4:(row + 1) * w * 4]
    result.pixels = px
    result.filepath_raw = out
    result.file_format = "PNG"
    result.save()
    for p in views:
        os.remove(p)
