"""Builds the six clay tablets of Ishtar's Descent as places, and the pictures of their knowledge cards.

    python3 -I models-src/ishtar_descent_tablets/make_textures.py
    blender -b --python models-src/ishtar_descent_tablets/build_ishtar_descent_tablets.py

A pillow-shaped Old Babylonian clay tablet, 34 x 48 x 7 cm, leaning on a mudbrick bench the way a scribe's school set
its tablets out to dry. Tablet n carries its own face (textures/tablet_n_*.png). Writes

* media/models/architecture/ishtar_descent_tablet_<n>.glb - bench and tablet, origin at ground level in the middle of the
  bench (places/ishtar_descent_tablets.yaml);
* media/knowledge/ishtar_descent_tablet_<n>.jpg - the 640x1100 picture of the tablet's knowledge card.

Blender: X east, Y north, Z up.
"""
import math
import os

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
DISK = os.path.normpath(os.path.join(HERE, "..", ".."))
TEX = os.path.join(HERE, "textures")

TW, TL, TT = 0.34, 0.48, 0.07


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def image_material(name, albedo, normal, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = roughness
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(albedo, check_existing=True)
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    ntex = nodes.new("ShaderNodeTexImage")
    ntex.image = bpy.data.images.load(normal, check_existing=True)
    ntex.image.colorspace_settings.name = "Non-Color"
    nmap = nodes.new("ShaderNodeNormalMap")
    links.new(ntex.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def flat_material(name, color, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def tablet(n):
    """The tablet lying face up on z=0; the face (+Z) is inscribed, read from +Y down."""
    face = image_material(f"tablet_{n}", os.path.join(TEX, f"tablet_{n}_albedo.png"),
                          os.path.join(TEX, f"tablet_{n}_normal.png"), 0.85)
    clay = image_material("clay", os.path.join(TEX, "clay_albedo.png"), os.path.join(TEX, "clay_normal.png"), 0.9)
    mesh = bpy.data.meshes.new(f"tablet_{n}")
    obj = bpy.data.objects.new(f"tablet_{n}", mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(TW, TL, TT), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, TT / 2), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.022, segments=4, affect="EDGES", profile=0.5)
    obj.data.materials.append(face)
    obj.data.materials.append(clay)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        top = f.normal.z > 0.9
        f.material_index = 0 if top else 1
        for loop in f.loops:
            p = loop.vert.co
            loop[uv].uv = ((p.x + TW / 2) / TW, (p.y + TL / 2) / TL) if top else (p.x * 4 + p.z * 3, p.y * 4 + p.z * 3)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def bench():
    """A bench of sun-dried bricks, 70 x 40 cm and two courses high, with a back course the tablet leans on."""
    mud = [flat_material(f"mudbrick_{i}", c, 0.95) for i, c in
           enumerate([(0.30, 0.19, 0.10), (0.34, 0.22, 0.12), (0.27, 0.17, 0.09)])]
    mesh = bpy.data.meshes.new("bench")
    obj = bpy.data.objects.new("bench", mesh)
    bpy.context.collection.objects.link(obj)
    for m in mud:
        obj.data.materials.append(m)
    bm = bmesh.new()
    k = 0

    def block(cx, cy, sx, sy, z0, z1):
        nonlocal k
        new = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=(sx, sy, z1 - z0), verts=new)
        bmesh.ops.translate(bm, vec=(cx, cy, (z0 + z1) / 2), verts=new)
        for f in {f for v in new for f in v.link_faces}:
            f.material_index = k % len(mud)
        k += 1

    g = 0.01
    for course, z0 in enumerate((0.0, 0.11)):
        z1 = z0 + 0.10
        if course == 0:
            block(-0.17, 0, 0.34 - g, 0.40, z0, z1)
            block(0.17, 0, 0.34 - g, 0.40, z0, z1)
        else:
            block(0, -0.10, 0.70, 0.19, z0, z1)
            block(0, 0.10, 0.70, 0.19, z0, z1)
    block(0, 0.20, 0.70, 0.10, 0.21, 0.32)  # the back course
    bm.to_mesh(mesh)
    bm.free()
    return obj


def export(path, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_image_format="AUTO")
    print("exported", path, os.path.getsize(path), "bytes")


def render_card(n, path):
    reset()
    obj = tablet(n)
    obj.rotation_euler = (math.radians(90), 0, 0)
    obj.location = (0, 0, TL / 2)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = 640, 1100
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 88
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("card")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.016, 0.012, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    scene.world = world
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = TL * 1.6
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (0.0, -0.7, 0.3)
    cam.rotation_euler = (Vector((0, 0, TL / 2)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    for loc, energy in (((-0.4, -0.5, 0.6), 2.5), ((0.5, -0.3, 0.2), 0.8)):
        data = bpy.data.lights.new("l", "SUN")
        data.energy = energy
        light = bpy.data.objects.new("l", data)
        scene.collection.objects.link(light)
        light.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("card", path)


def main():
    for n in range(1, 7):
        reset()
        base = bench()
        t = tablet(n)
        # face towards -Y, leaning back on the back course
        t.rotation_euler = (-(math.radians(90) - math.radians(22)), 0, 0)
        t.location = (0, 0.04, 0.215 + 0.02)
        export(os.path.join(DISK, "media", "models", "architecture", f"ishtar_descent_tablet_{n}.glb"), [base, t])
        render_card(n, os.path.join(DISK, "media", "knowledge", f"ishtar_descent_tablet_{n}.jpg"))


main()
