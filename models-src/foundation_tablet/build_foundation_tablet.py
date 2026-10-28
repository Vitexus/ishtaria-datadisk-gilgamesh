"""Builds the foundation tablet of the Temple of Ishtar (Inanna) and its foundation deposit.

    python3 -I models-src/foundation_tablet/make_textures.py
    blender -b --python models-src/foundation_tablet/build_foundation_tablet.py -- [icon.png]

After the steatite foundation tablets of the Eanna (research/foundtion-tablet.jpg): a small slab of black stone,
10 x 5.2 x 1.6 cm with rounded edges, its face ruled into registers of incised signs (textures from
make_textures.py). Writes

* media/models/foundation_tablet.glb - the tablet alone, lying face up, origin under its middle (the item);
* media/models/architecture/foundation_deposit.glb - the tablet in its open box of baked bricks, as foundation
  deposits were laid under the corners of a temple, opened and the brick lid set aside (the `foundation_deposit`
  place at the north-east corner of the stepped tower); origin at ground level in the middle of the box;
* media/knowledge/foundation_tablet.jpg - the picture of the tablet's knowledge card;
* the 128 px inventory icon when a path is given (ishtaria-client/assets/icons/items/foundation_tablet.png).

Blender: X east, Y north, Z up.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
DISK = os.path.normpath(os.path.join(HERE, "..", ".."))
TEX = os.path.join(HERE, "textures")
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ICON = ARGS[0] if ARGS else None

TW, TL, TT = 0.052, 0.100, 0.016  # tablet width (x), length (y), thickness (z)
BEVEL = 0.004


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
    if normal:
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


def tablet(name="foundation_tablet"):
    """The tablet lying face up on z=0; the face (+Z) carries the inscription, read from +Y down."""
    front = image_material("tablet_inscribed", os.path.join(TEX, "front_albedo.png"),
                           os.path.join(TEX, "front_normal.png"), 0.42)
    stone = image_material("steatite", os.path.join(TEX, "stone_albedo.png"),
                           os.path.join(TEX, "stone_normal.png"), 0.5)
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(TW, TL, TT), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, TT / 2), verts=bm.verts)
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=BEVEL, segments=3, affect="EDGES", profile=0.5)
    obj.data.materials.append(front)
    obj.data.materials.append(stone)
    uv = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        n = face.normal
        if n.z > 0.99:
            face.material_index = 0
            for loop in face.loops:
                p = loop.vert.co
                loop[uv].uv = ((p.x + TW / 2) / TW, (p.y + TL / 2) / TL)
            continue
        face.material_index = 1
        axis = max(range(3), key=lambda i: abs(n[i]))
        for loop in face.loops:
            p = loop.vert.co
            a, b = [p[i] for i in range(3) if i != axis]
            loop[uv].uv = (a * 8.0, b * 8.0)  # 256 px of stone per 12.5 cm
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    return obj


def brick_box(rng):
    """An open box of baked bricks 60 cm square: a floor course bedded with sand, three courses of walls, the lid aside.

    It stands on the ground as an excavated deposit: sunk into the ground, terrain would cover the tablet."""
    tones = [flat_material("bakedbrick_%d" % i, c, 0.88) for i, c in
             enumerate([(0.30, 0.10, 0.045), (0.36, 0.13, 0.06), (0.25, 0.09, 0.045)])]  # linear, as glTF expects
    floor_mat = flat_material("sand", (0.42, 0.31, 0.17), 0.95)
    mesh = bpy.data.meshes.new("foundation_box")
    obj = bpy.data.objects.new("foundation_box", mesh)
    bpy.context.collection.objects.link(obj)
    for mat in tones + [floor_mat]:
        obj.data.materials.append(mat)
    sand = len(tones)
    bm = bmesh.new()

    def block(cx, cy, sx, sy, z0, z1, mat=None, tilt=0.0):
        new = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=(sx, sy, z1 - z0), verts=new)
        if tilt:
            bmesh.ops.rotate(bm, verts=new, cent=(0, 0, 0), matrix=Matrix.Rotation(tilt, 3, "X"))
        bmesh.ops.translate(bm, vec=(cx, cy, (z0 + z1) / 2), verts=new)
        index = rng.randrange(len(tones)) if mat is None else mat
        for f in {f for v in new for f in v.link_faces}:
            f.material_index = index

    course, g = 0.07, 0.006  # brick course and mortar joint
    # the floor course, with a bedding of clean sand inside the box under the tablet
    block(0, 0, 0.60, 0.60, 0.0, course - g)
    floor = course - g
    block(0, 0, 0.30, 0.30, floor, floor + 0.004, sand)
    # three courses of a pinwheel of four bricks round a 30 cm square, the joints turning each course
    for k in range(3):
        z0, z1 = floor + k * course, floor + (k + 1) * course - g
        if k % 2 == 0:
            block(-0.075, 0.225, 0.45 - g, 0.15 - g, z0, z1)
            block(0.225, 0.075, 0.15 - g, 0.45 - g, z0, z1)
            block(0.075, -0.225, 0.45 - g, 0.15 - g, z0, z1)
            block(-0.225, -0.075, 0.15 - g, 0.45 - g, z0, z1)
        else:
            block(0.075, 0.225, 0.45 - g, 0.15 - g, z0, z1)
            block(0.225, -0.075, 0.15 - g, 0.45 - g, z0, z1)
            block(-0.075, -0.225, 0.45 - g, 0.15 - g, z0, z1)
            block(-0.225, 0.075, 0.15 - g, 0.45 - g, z0, z1)
    # the lid, a square brick, lifted off and leaning on the south wall
    tilt = math.radians(14)
    block(0.0, -0.47, 0.34, 0.34, 0.17 * math.sin(tilt) - 0.03, 0.17 * math.sin(tilt) + 0.03, tilt=tilt)
    bm.to_mesh(mesh)
    bm.free()
    return obj, floor + 0.004


def export(path, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_image_format="AUTO")
    print("exported", path, os.path.getsize(path), "bytes")


def render_icon(path, card=False):
    """The tablet standing, three-quarter view from the front left: the 128 px icon on a transparent background, or
    (`card`) the 640x1100 picture of the knowledge card, nearly frontal on a dark cloth, written as JPEG."""
    reset()
    obj = tablet()
    obj.rotation_euler = (math.radians(90), 0, math.radians(-14 if card else -38))
    obj.location = (0, 0, TL / 2)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = (640, 1100) if card else (128, 128)
    scene.render.film_transparent = not card
    scene.render.image_settings.file_format = "JPEG" if card else "PNG"
    scene.render.image_settings.color_mode = "RGB" if card else "RGBA"
    if card:
        scene.render.image_settings.quality = 88
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("icon")
    world.use_nodes = True
    background = (0.012, 0.011, 0.01, 1.0) if card else (0.55, 0.55, 0.6, 1.0)
    world.node_tree.nodes["Background"].inputs["Color"].default_value = background
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    scene.world = world
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = TL * (1.25 if card else 1.0)
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (-0.15, -0.7, 0.2) if card else (-0.3, -0.6, 0.3)
    direction = Vector((0, 0, TL / 2)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    for loc, energy in (((-0.4, -0.5, 0.6), 2.5), ((0.5, -0.3, 0.2), 0.8)):
        light_data = bpy.data.lights.new("l", "SUN")
        light_data.energy = energy
        light = bpy.data.objects.new("l", light_data)
        scene.collection.objects.link(light)
        light.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("card" if card else "icon", path)


def main():
    reset()
    item = tablet()
    export(os.path.join(DISK, "media", "models", "foundation_tablet.glb"), [item])

    reset()
    rng = random.Random(5)
    box, floor = brick_box(rng)
    laid = tablet("deposit_tablet")
    laid.location = (0.02, -0.01, floor)
    laid.rotation_euler = (0, 0, math.radians(7))
    export(os.path.join(DISK, "media", "models", "architecture", "foundation_deposit.glb"), [box, laid])

    render_icon(os.path.join(DISK, "media", "knowledge", "foundation_tablet.jpg"), card=True)
    if ICON:
        render_icon(ICON)


main()
