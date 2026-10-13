"""Side, front and top views of a Rodin mesh in metres (for creatures), to read bone positions off a grid.

    blender -b --python models-src/rodin/views.py -- <rodin.glb> <out_prefix> <height_m> [yaw_deg]

The mesh is turned by yaw_deg about Z, scaled so that its height is height_m, centred on x/y of its bounding box and
stood on z=0. Writes <prefix>_side.png (looking along +X, front to the left = -Y), _front.png and _top.png, 400 px per
metre; grid lines each 0.5 m are drawn by views_grid.py.
"""
import math, sys
import bpy, mathutils
src, out, height = sys.argv[sys.argv.index("--")+1:][:3]
yaw = float(sys.argv[sys.argv.index("--")+4]) if len(sys.argv) > sys.argv.index("--")+4 else 0.0
height = float(height)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
body = max(ms, key=lambda o: len(o.data.polygons))
for o in list(bpy.context.scene.objects):
    if o is not body: bpy.data.objects.remove(o, do_unlink=True)
body.parent = None; bpy.context.view_layer.objects.active = body; body.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
rot = mathutils.Matrix.Rotation(math.radians(yaw), 3, "Z")
vs = [rot @ v.co for v in body.data.vertices]
zmin = min(v.z for v in vs); zmax = max(v.z for v in vs)
s = height / (zmax - zmin)
cx = (min(v.x for v in vs) + max(v.x for v in vs)) / 2; cy = (min(v.y for v in vs) + max(v.y for v in vs)) / 2
for v, p in zip(body.data.vertices, vs):
    v.co = mathutils.Vector(((p.x - cx) * s, (p.y - cy) * s, (p.z - zmin) * s))
xs = [v.co.x for v in body.data.vertices]; ys = [v.co.y for v in body.data.vertices]
print("extent x", min(xs), max(xs), "y", min(ys), max(ys), "z", 0, height)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "FLAT"; sc.display.shading.color_type = "TEXTURE"
sc.render.resolution_x = 1600; sc.render.resolution_y = 1200
cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = 4.0   # 400 px per metre
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
for name, loc, rotation in (("side", (6, 0, 1.5), (1.5708, 0, 1.5708)), ("front", (0, -6, 1.5), (1.5708, 0, 0)), ("top", (0, 0, 8), (0, 0, 0))):
    co.location = loc; co.rotation_euler = rotation
    sc.render.filepath = f"{out}_{name}.png"; bpy.ops.render.render(write_still=True)
