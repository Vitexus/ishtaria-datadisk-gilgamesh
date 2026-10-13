"""Front view of a Rodin mesh scaled to height 1 and centred on its bounding box, to read the joints off a grid.

    blender -b --python models-src/rodin/front_view.py -- <rodin.glb> <out.png>
    python3 models-src/rodin/front_grid.py <out.png> ...   (draws the grid: z every 0.05 of the height, x every 0.05)

x of a joint in the JSON is the fraction of the height from the centre line, z the fraction of the height; the face
coordinates are the same fractions times the height in metres.
"""
import bpy, sys, mathutils
src, out = sys.argv[sys.argv.index("--")+1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
ms=[o for o in bpy.context.scene.objects if o.type=="MESH"]
body=max(ms,key=lambda o:len(o.data.polygons))
for o in list(bpy.context.scene.objects):
    if o is not body: bpy.data.objects.remove(o,do_unlink=True)
body.parent=None; bpy.context.view_layer.objects.active=body; body.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
vs=[v.co.copy() for v in body.data.vertices]
zmin=min(v.z for v in vs); zmax=max(v.z for v in vs); xmin=min(v.x for v in vs); xmax=max(v.x for v in vs)
H=zmax-zmin; s=1.0/H
xs=sorted(v.x for v in vs); cx=(xmin+xmax)/2
print("size", H, xmax-xmin, "ydepth", max(v.y for v in vs)-min(v.y for v in vs))
for v in body.data.vertices:
    v.co=(v.co-mathutils.Vector((cx,0,zmin)))*s
sc=bpy.context.scene
sc.render.engine="BLENDER_WORKBENCH"; sc.display.shading.light="FLAT"; sc.display.shading.color_type="TEXTURE"
sc.render.resolution_x=800; sc.render.resolution_y=1000
cam=bpy.data.cameras.new("c"); cam.type="ORTHO"; cam.ortho_scale=1.25
co=bpy.data.objects.new("c",cam); sc.collection.objects.link(co); sc.camera=co
co.location=(0,-5,0.5); co.rotation_euler=(1.5708,0,0)
sc.render.filepath=out; bpy.ops.render.render(write_still=True)
