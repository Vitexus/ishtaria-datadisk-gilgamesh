"""Water works of Early Dynastic Sumer after research/warers.png (research/WATER_WORKS.md): the settling reservoir (nagkud),
the weir (kunzida) and the whole irrigation scheme of the drawing.

    blender -b --factory-startup -P models-src/architecture/irrigation_works.py -- media/models/architecture [preview.png]

Writes irrigation_nagkud.glb, irrigation_weir.glb and irrigation_works.glb into the directory. Metres, +Y up, origin on the
ground in the middle of the main canal at the mouth of the nagkud. The canal runs along +X (blender X east, Y north, Z up).
The water is a flat translucent plane, there is no collision. Deterministic.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = ARGS[0] if ARGS else "."
PREVIEW = ARGS[1] if len(ARGS) > 1 else None

COLOURS = {
    "mud": (0.36, 0.25, 0.15), "brick": (0.42, 0.28, 0.17), "bank": (0.30, 0.22, 0.13), "timber": (0.22, 0.14, 0.08),
    "reed": (0.55, 0.46, 0.22), "green": (0.18, 0.34, 0.10), "ripe": (0.62, 0.50, 0.20), "fallow": (0.33, 0.24, 0.14),
    "palm": (0.12, 0.28, 0.08), "trunk": (0.30, 0.20, 0.10), "roof": (0.38, 0.27, 0.16), "ground": (0.40, 0.31, 0.19),
}
_mats = {}
BRICK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "media", "textures", "well_brick.png")


def mat(name):
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    if name == "water":
        b.inputs["Base Color"].default_value = (0.10, 0.20, 0.22, 1)
        b.inputs["Alpha"].default_value = 0.72
        b.inputs["Roughness"].default_value = 0.08
        m.blend_method = "BLEND"
    elif name == "brick" and os.path.isfile(BRICK):
        # the brick of the wells of Uruk (tools/make_well_brick.py); the boxes carry the cube's UVs, so the texture is
        # stretched by their size: good enough at the distance these works are seen from
        t = m.node_tree.nodes.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(BRICK)
        m.node_tree.links.new(t.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = 0.92
    else:
        b.inputs["Base Color"].default_value = (*COLOURS[name], 1)
        b.inputs["Roughness"].default_value = 0.92
    _mats[name] = m
    return m


class Builder:
    def __init__(self):
        self.parts = {}

    def bm(self, name):
        if name not in self.parts:
            self.parts[name] = bmesh.new()
        return self.parts[name]

    def box(self, material, cx, cy, z0, sx, sy, sz, yaw=0.0):
        bm = self.bm(material)
        v = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=v)
        bmesh.ops.rotate(bm, verts=v, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(yaw, 3, "Z"))
        bmesh.ops.translate(bm, vec=(cx, cy, z0 + sz / 2), verts=v)

    def cylinder(self, material, cx, cy, z0, radius, height, n=10):
        bm = self.bm(material)
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=radius, radius2=radius, depth=height)
        bmesh.ops.translate(bm, vec=(cx, cy, z0 + height / 2), verts=r["verts"])

    def cone(self, material, cx, cy, z0, r1, r2, height, n=10):
        bm = self.bm(material)
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=height)
        bmesh.ops.translate(bm, vec=(cx, cy, z0 + height / 2), verts=r["verts"])

    def ring(self, material, cx, cy, z, r_out, r_in, n=28):
        bm = self.bm(material)
        outer = [bm.verts.new((cx + math.cos(2 * math.pi * i / n) * r_out, cy + math.sin(2 * math.pi * i / n) * r_out, z)) for i in range(n)]
        inner = [bm.verts.new((cx + math.cos(2 * math.pi * i / n) * r_in, cy + math.sin(2 * math.pi * i / n) * r_in, z)) for i in range(n)]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((outer[i], outer[j], inner[j], inner[i]))

    def flush(self, name):
        objs = []
        for key, bm in self.parts.items():
            me = bpy.data.meshes.new(f"{name}_{key}")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(mat(key))
            ob = bpy.data.objects.new(f"{name}_{key}", me)
            bpy.context.scene.collection.objects.link(ob)
            objs.append(ob)
        self.parts = {}
        return objs


def canal(b, x0, x1, y, width, bank=2.0, depth=0.0):
    """A canal along X: the water plane between two berms."""
    b.box("water", (x0 + x1) / 2, y, -0.25, x1 - x0, width, 0.02)
    for side in (-1, 1):
        b.box("bank", (x0 + x1) / 2, y + side * (width / 2 + bank / 2), 0, x1 - x0, bank, 0.7)


def canal_y(b, y0, y1, x, width, bank=2.0):
    b.box("water", x, (y0 + y1) / 2, -0.25, width, y1 - y0, 0.02)
    for side in (-1, 1):
        b.box("bank", x + side * (width / 2 + bank / 2), (y0 + y1) / 2, 0, bank, y1 - y0, 0.7)


def nagkud(b, cx, cy, w=36.0, d=24.0):
    """The settling reservoir: an embankment basin with two eddies; mouth (ka) on the west side at the canal, outlet (kun)
    in the south-east corner behind a weir."""
    wall = 4.0
    h = 1.6
    b.box("water", cx, cy, -0.35, w, d, 0.02)
    for side in (-1, 1):
        b.box("bank", cx, cy + side * (d / 2 + wall / 2), 0, w + 2 * wall, wall, h)
    b.box("bank", cx - w / 2 - wall / 2, cy, 0, wall, d, h)
    # the east bank leaves a gap of 4 m in the south-east corner: kun, the outlet of the nagkud
    b.box("bank", cx + w / 2 + wall / 2, cy + 3.0, 0, wall, d - 6.0, h)
    for k, sx in enumerate((-1, 1)):
        b.ring("reed", cx + sx * w * 0.2, cy, -0.32, d * 0.3, d * 0.3 - 0.4)
        b.ring("reed", cx + sx * w * 0.2, cy, -0.32, d * 0.18, d * 0.18 - 0.3)
    # reed fascine on the inner slope
    b.box("reed", cx, cy + d / 2 - 0.3, -0.3, w, 0.5, 1.0)
    b.box("reed", cx, cy - d / 2 + 0.3, -0.3, w, 0.5, 1.0)


def mouth(b, x, y, width=5.0):
    """ka: the gated mouth: two brick piers with timber boards between them."""
    for side in (-1, 1):
        b.box("brick", x, y + side * (width / 2 + 0.7), 0, 2.0, 1.4, 2.6)
    for i in range(4):
        b.box("timber", x, y, 0.2 + i * 0.55, 0.3, width, 0.4)
    b.box("timber", x, y, 2.6, 1.0, width + 3.2, 0.3)


def weir(b, x, y, width=10.0):
    """kunzida: a low brick sill across the canal on timber piles with a reed apron downstream."""
    b.box("brick", x, y, -0.3, 2.4, width + 2, 0.9)
    b.box("reed", x + 3.0, y, -0.3, 3.5, width, 0.25)
    for i in range(5):
        b.cylinder("timber", x - 1.5, y - width / 2 + i * width / 4, -0.3, 0.18, 1.6, 8)
    for side in (-1, 1):
        b.box("brick", x, y + side * (width / 2 + 1.8), 0, 3.0, 2.4, 1.5)


def field(b, x0, y0, sx, sy, kind, rows=9):
    b.box("ground", x0 + sx / 2, y0 + sy / 2, 0, sx, sy, 0.08)
    for i in range(rows):
        b.box(kind, x0 + sx / 2, y0 + (i + 0.5) * sy / rows, 0.08, sx - 1.0, sy / rows * 0.45, 0.35 if kind != "fallow" else 0.12)


def palm(b, x, y, rng):
    h = rng.uniform(5.0, 8.0)
    b.cone("trunk", x, y, 0, 0.35, 0.2, h, 7)
    for k in range(7):
        a = k * 2 * math.pi / 7 + rng.uniform(-0.2, 0.2)
        b.box("palm", x + math.cos(a) * 1.6, y + math.sin(a) * 1.6, h - 0.2, 3.4, 0.5, 0.18, yaw=a)


def house(b, x, y, sx, sy, sz):
    b.box("brick", x, y, 0, sx, sy, sz)
    b.box("roof", x, y, sz, sx + 0.4, sy + 0.4, 0.25)


def build_nagkud():
    b = Builder()
    canal(b, -26, 40, 0, 10)
    nagkud(b, 12, -24)
    mouth(b, 12 - 18 - 3, -8, 4.0)
    canal_y(b, -12, -5, -9, 4)
    weir(b, 30, 0)
    return b.flush("nagkud")


def build_weir():
    b = Builder()
    canal(b, -14, 18, 0, 10)
    weir(b, 0, 0)
    return b.flush("weir")


def build_works():
    rng = random.Random(7)
    b = Builder()
    canal(b, -50, 90, 0, 10)                      # id: the main canal
    nagkud(b, 12, -24)
    mouth(b, -9, -8, 4.0)                         # ka
    canal_y(b, -12, -5, -9, 4)
    weir(b, 34, 0)                                # kunzida across the main canal
    canal(b, 28, 44, -34, 4)                      # kun: the outlet of the nagkud, through the gap in its bank
    canal_y(b, -52, -34, 42, 4)
    canal(b, 42, 100, -36, 4)
    canal(b, 42, 100, -52, 3)
    # asa: furrowed fields between the branch canals
    for i, kind in enumerate(("green", "ripe", "green", "fallow")):
        field(b, 46 + i * 14, -50, 12, 12, kind)
        field(b, 46 + i * 14, -34, 12, 14, kind if i % 2 else "ripe")
    for i, kind in enumerate(("ripe", "green")):
        field(b, -44 + i * 20, -60, 18, 22, kind)
    # kiri: the orchard on the dry ground north of the canal
    for ix in range(-40, 70, 9):
        for iy in (14, 22, 30):
            palm(b, ix + rng.uniform(-1.5, 1.5), iy + rng.uniform(-1.5, 1.5), rng)
    # e and ganun: the houses and the storehouse
    for k, (x, y) in enumerate(((66, -8), (74, -18), (62, -22), (80, 6), (84, -10))):
        house(b, x, y, rng.uniform(5, 8), rng.uniform(5, 8), rng.uniform(2.8, 3.6))
    b.box("brick", 70, 18, 0, 14, 8, 4.0)          # ganun
    b.box("roof", 70, 18, 4.0, 14.6, 8.6, 0.3)
    b.box("brick", 70, 11.5, 0, 3, 5, 1.2)         # the ramp
    return b.flush("works")


def export(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True, export_yup=True)
    print("exported", path, os.path.getsize(path), "bytes")


def render(objs, path):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x, scene.render.resolution_y = 1400, 900
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("w")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.62, 0.75, 1)
    scene.world = world
    cam_data = bpy.data.cameras.new("c")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 170
    cam = bpy.data.objects.new("c", cam_data)
    scene.collection.objects.link(cam)
    cam.location = (-60, -130, 110)
    cam.rotation_euler = (Vector((20, -25, 0)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    sun = bpy.data.lights.new("s", "SUN")
    sun.energy = 3.5
    so = bpy.data.objects.new("s", sun)
    scene.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), 0, math.radians(30))
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    for name, fn in (("irrigation_nagkud", build_nagkud), ("irrigation_weir", build_weir), ("irrigation_works", build_works)):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        _mats.clear()
        objs = fn()
        export(objs, os.path.join(OUT, name + ".glb"))
        if PREVIEW and name == "irrigation_works":
            render(objs, PREVIEW)


main()
