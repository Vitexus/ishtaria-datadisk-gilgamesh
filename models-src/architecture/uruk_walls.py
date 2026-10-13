"""The walls of Uruk, built to match the Ishtar Gate (see ishtar_gate.py), in one model with the gate.

    blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls media/models/architecture/uruk_walls.glb

A rectangular circuit of glazed blue brick, 18 m high and 7 m thick like the curtain walls of the inner gate, closes the
city: the outer face carries the rows of aurochs and mushussu dragons and the stepped battlements of the gate, the inner
face is plain glaze, and the passage of the Ishtar Gate (with its outer gate, courtyard and 80 m Processional Way) is the
only entrance. Towers stand at the corners and every ~85 m; four flights of stairs inside climb to the wall walk.

Metres, ground at z = 0, the street runs along -Y into the gate, the city lies on the +Y side.
The origin is the middle of the gate, so a datadisk places the model with `offset_m: [0, CENTRE_Y]` (the middle of the
walled area, in the model's -Z direction in glTF) to put the middle of the city at the anchor of its place.
Walls are 14 m deep below the ground so that they do not float on uneven terrain.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ishtar_gate as G  # noqa: E402
import ziggurat as Z  # noqa: E402

WALL_H = 18.0       # as the curtain walls of the inner gate
THICK = 7.0
Y_OUT = 22.0        # outer face of the south wall: the line of the inner gate's curtain walls
HALF_W = 200.0      # half of the width of the circuit, to the outer faces
LENGTH = 420.0      # depth of the circuit, to the outer faces
STUB = 44.0         # where the curtain walls of the gate end
TOWER = 11.0
TOWER_H = WALL_H + 5.0
DEPTH = 14.0        # the foundation below the ground
CENTRE_Y = Y_OUT + LENGTH / 2   # the middle of the city, seen from the middle of the gate


def v3(x, y, z):
    return Vector((x, y, z))


def segment(model, a, b, rng, rows):
    """A wall from a to b along its outer face (the outer side is to the right of the direction a -> b)."""
    d = b - a
    length = d.length
    t = d / length
    out = Vector((t.y, -t.x))
    inn = -out
    a_in = a + inn * THICK
    b_in = b + inn * THICK
    # outer and inner faces, from the foundation up
    model.jitter = 0.94 + rng.random() * 0.06
    model.wall([v3(a.x, a.y, -DEPTH), v3(b.x, b.y, -DEPTH), v3(b.x, b.y, WALL_H), v3(a.x, a.y, WALL_H)], "blueglaze", t, rng.random() * 6, v3(out.x, out.y, 0))
    model.wall([v3(b_in.x, b_in.y, -DEPTH), v3(a_in.x, a_in.y, -DEPTH), v3(a_in.x, a_in.y, WALL_H), v3(b_in.x, b_in.y, WALL_H)], "blueglaze", -t, rng.random() * 6, v3(inn.x, inn.y, 0))
    model.jitter = 1.0
    model.top([v3(a.x, a.y, WALL_H), v3(b.x, b.y, WALL_H), v3(b_in.x, b_in.y, WALL_H), v3(a_in.x, a_in.y, WALL_H)], "bakedbrick")
    # plinth and the rows of animals on the outer face, as on the gate
    model.wall([v3(a.x + out.x * 0.04, a.y + out.y * 0.04, 0), v3(b.x + out.x * 0.04, b.y + out.y * 0.04, 0),
                v3(b.x + out.x * 0.04, b.y + out.y * 0.04, G.PLINTH), v3(a.x + out.x * 0.04, a.y + out.y * 0.04, G.PLINTH)],
               "bakedbrick", t, 0.0, v3(out.x, out.y, 0))
    G.animal_rows(model, a, t, out, length, G.PLINTH + 0.4, rows, (t.x, t.y), rng, margin=1.2)
    # stepped battlements along the outer edge only; the inner edge stays open for the wall walk
    merlons(model, a + out * -0.5 + t * 0.5, b + out * -0.5 - t * 0.5, WALL_H, rng)


def merlons(model, a, b, z, rng):
    """Battlements of the long walls: one block every 3.4 m (the gate keeps its two-step merlons), to save size."""
    d = b - a
    t = d / d.length
    n = max(1, int(d.length / 3.4))
    for k in range(n):
        c = a + d * ((k + 0.5) / n)
        sx, sy = (1.5, 1.0) if abs(t.x) > 0.5 else (1.0, 1.5)
        Z.box(model, c.x, c.y, sx, sy, z, z + 1.6, "blueglaze", "bakedbrick", rng=rng)


def tower(model, cx, cy, rng):
    Z.box(model, cx, cy, TOWER, TOWER, -DEPTH, TOWER_H, "blueglaze", "bakedbrick", rng)
    G.crenellations(model, Vector((cx - TOWER / 2 + 0.5, cy - TOWER / 2 + 0.5)), Vector((cx + TOWER / 2 - 0.5, cy - TOWER / 2 + 0.5)), TOWER_H, rng)
    G.crenellations(model, Vector((cx - TOWER / 2 + 0.5, cy + TOWER / 2 - 0.5)), Vector((cx + TOWER / 2 - 0.5, cy + TOWER / 2 - 0.5)), TOWER_H, rng)
    for sx in (-1, 1):
        G.crenellations(model, Vector((cx + sx * (TOWER / 2 - 0.5), cy - TOWER / 2 + 0.5)), Vector((cx + sx * (TOWER / 2 - 0.5), cy + TOWER / 2 - 0.5)), TOWER_H, rng)


def circuit(model, rng):
    rows = ["bull", "dragon", "bull"]
    x = HALF_W
    y0, y1 = Y_OUT, Y_OUT + LENGTH
    corners = [Vector((-x, y0)), Vector((x, y0)), Vector((x, y1)), Vector((-x, y1))]
    # The outer side is to the right of the direction a -> b. South: east-wards, outer face towards -Y; the gate's own
    # curtain walls reach STUB. Then east (+Y), north (-X) and west (-Y), the circuit seen from above, clockwise.
    segment(model, Vector((-x, y0)), Vector((-STUB, y0)), rng, rows)
    segment(model, Vector((STUB, y0)), Vector((x, y0)), rng, rows)
    segment(model, Vector((x, y0)), Vector((x, y1)), rng, rows)
    segment(model, Vector((x, y1)), Vector((-x, y1)), rng, rows)
    segment(model, Vector((-x, y1)), Vector((-x, y0)), rng, rows)
    # towers at the corners and along the walls
    for c in corners:
        tower(model, c.x - math.copysign(3.5, c.x), c.y + (3.5 if c.y == y0 else -3.5), rng)
    for k in range(1, 4):
        tower(model, x - THICK / 2, y0 + LENGTH * k / 4, rng)
        tower(model, -x + THICK / 2, y0 + LENGTH * k / 4, rng)
        tower(model, -x + 2 * x * k / 4, y1 - THICK / 2, rng)
    for sx in (-1, 1):
        tower(model, sx * (STUB + 40.0), y0 + THICK / 2, rng)
        tower(model, sx * (STUB + 90.0), y0 + THICK / 2, rng)
    # stairs from the inside up to the wall walk: flush with the inner face, the top meets the wall top
    inner = x - THICK
    z0 = 0.0
    Z.stairs(model, inner - 1.5, y0 + 112.0, (0, 1), 3.0, z0, WALL_H, 50.0, rh=0.3)
    Z.stairs(model, -inner + 1.5, y0 + 112.0, (0, 1), 3.0, z0, WALL_H, 50.0, rh=0.3)
    Z.stairs(model, -76.0, y1 - THICK - 1.5, (1, 0), 3.0, z0, WALL_H, 50.0, rh=0.3)
    Z.stairs(model, -72.0, y0 + THICK + 1.5, (1, 0), 3.0, z0, WALL_H, 50.0, rh=0.3)


def recompress(quality=70):
    """Blender copies JPEG files into the glb as they are, so the textures are saved again at a lower quality (into
    a temporary folder that Z.TEXTURES then points to): the walls must stay below the 4 MiB a datadisk model may have."""
    import tempfile
    folder = tempfile.mkdtemp(prefix="uruk_textures_")
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = quality
    for name in sorted(os.listdir(Z.TEXTURES)):
        if name.endswith(".jpg"):
            image = bpy.data.images.load(os.path.join(Z.TEXTURES, name))
            image.save_render(os.path.join(folder, name), scene=scene)
            bpy.data.images.remove(image)
    Z.TEXTURES = folder


def finish(model, path, quality=70):
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    me = bpy.data.meshes.new("uruk_walls")
    model.bm.to_mesh(me)
    model.bm.free()
    for m in Z.materials_for(model):
        me.materials.append(m)
    obj = bpy.data.objects.new(os.path.splitext(os.path.basename(path))[0], me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_image_format="JPEG",
                              export_jpeg_quality=quality, export_yup=True, export_apply=False, export_lights=False,
                              export_cameras=False, export_animations=False, export_vertex_color='ACTIVE')
    print("exported", path, os.path.getsize(path), "bytes", len(me.polygons), "faces")


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    which, out = args[0], args[1]
    rng = random.Random(7)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    model = Z.Model()
    if which != "uruk_walls":
        raise SystemExit("unknown model " + which)
    G.gate_complex(model, rng)
    G.processional_way(model, rng)
    circuit(model, rng)
    recompress()
    finish(model, out)
    print("centre_y", CENTRE_Y)


if __name__ == "__main__":
    main()
