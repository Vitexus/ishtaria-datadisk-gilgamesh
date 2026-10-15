"""Renders glb models of the city from a camera, for checking looks (daylight, simple sky).

    blender -b --python tools/blender/render_city.py -- out.png "cam_x,cam_y,cam_z,target_x,target_y,target_z,lens" model.glb [model.glb ...]

Coordinates are Blender's (x east, y north, z up) in the frame of the models; several models of the city share a world
frame only when they have the same origin, so give the shift of a model as `file.glb@dx,dy,dz`.
"""
import math
import sys

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
cam_spec = [float(v) for v in args[1].split(",")]
bpy.ops.wm.read_factory_settings(use_empty=True)
for spec in args[2:]:
    path, _, shift = spec.partition("@")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    if shift:
        d = [float(v) for v in shift.split(",")]
        for o in set(bpy.data.objects) - before:
            if o.parent is None:
                o.location += Vector(d)
scene = bpy.context.scene
# the terrain of the datadisk around the target, as the server's patch has it: TERRAIN=ox,oz,half[,step] (planner frame origin of the model)
import os
terrain = os.environ.get("TERRAIN")
gm = bpy.data.materials.new("sand")
gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.62, 0.52, 0.36, 1)
gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 1.0
if terrain:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "models-src", "architecture"))
    import uruk_city as C
    vals = [float(v) for v in terrain.split(",")]
    ox, oz, half = vals[:3]
    step = vals[3] if len(vals) > 3 else 4.0
    g = C.Ground()
    h0 = g.height(ox, oz)
    n = int(2 * half / step) + 1
    cx, cz = cam_spec[3], -cam_spec[4]
    verts, faces = [], []
    for j in range(n):
        for i in range(n):
            x = ox + cam_spec[3] - half + i * step
            zz = oz - cam_spec[4] - half + j * step
            verts.append((x - ox, -(zz - oz), g.height(x, zz) - h0))
    for j in range(n - 1):
        for i in range(n - 1):
            faces.append((j * n + i, j * n + i + 1, (j + 1) * n + i + 1, (j + 1) * n + i))
    me = bpy.data.meshes.new("terrain")
    me.from_pydata(verts, [], faces)
    me.update()
    ground = bpy.data.objects.new("terrain", me)
    scene.collection.objects.link(ground)
else:
    bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, -0.5))
    ground = bpy.context.active_object
ground.data.materials.append(gm)
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.use_denoising = False
scene.world = bpy.data.worlds.new("sky")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.55, 0.72, 0.95, 1)
bg.inputs[1].default_value = 1.0
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 4.5
sun.angle = math.radians(2.5)
ob = bpy.data.objects.new("sun", sun)
ob.rotation_euler = (math.radians(52), math.radians(8), math.radians(-35))
scene.collection.objects.link(ob)
cam_data = bpy.data.cameras.new("cam")
cam_data.lens = cam_spec[6]
cam_data.clip_end = 5000
cam = bpy.data.objects.new("cam", cam_data)
cam.location = Vector(cam_spec[0:3])
cam.rotation_euler = (Vector(cam_spec[3:6]) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(cam)
scene.camera = cam
scene.render.resolution_x = 1400
scene.render.resolution_y = 800
scene.render.filepath = out
scene.view_settings.view_transform = "Standard"
bpy.ops.render.render(write_still=True)
