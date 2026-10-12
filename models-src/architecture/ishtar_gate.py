"""The Ishtar Gate of Babylon and its Processional Way, built procedurally in Blender.

    blender -b --python models-src/architecture/ishtar_gate.py -- <model> <out.glb>

models:  ishtar_gate       the double gate: outer gate, courtyard, taller inner gate, and stubs of the city walls
         processional_way  the street with the walls of striding lions, 80 m long, ending at the outer gate
         ishtar_gate_complete  both in one file

Metres, ground at z = 0, the street runs along +Y and the front of the gate faces -Y like the other models.
Sizes follow Koldewey's excavation as quoted in research/ISHTAR_GATE.md: the outer gate is 28 m wide and 11 m deep,
the passage 4.5 m wide, the walls 7 m thick, gate rooms and courtyard 48 m in all. The face is deep blue glazed brick with
alternating rows of aurochs (Adad) and mushussu dragons (Marduk); the street walls carry lions (Ishtar).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ziggurat as Z  # noqa: E402

Z.MATERIALS.update({
    "blueglaze": ("blueglaze.jpg", (0.62, 0.72, 1.0), 0.42, 0.0, 3.0),
    "border": ("border.jpg", (1, 1, 1), 0.3, 0.0, 1.0),
    "bull": ("bull.jpg", (0.85, 0.9, 1.0), 0.32, 0.0, 1.0),
    "dragon": ("dragon.jpg", (0.85, 0.9, 1.0), 0.32, 0.0, 1.0),
    "bull2": ("bull2.jpg", (0.85, 0.9, 1.0), 0.32, 0.0, 1.0),
    "dragon2": ("dragon2.jpg", (0.85, 0.9, 1.0), 0.32, 0.0, 1.0),
    "lion": ("lion.jpg", (0.85, 0.9, 1.0), 0.32, 0.0, 1.0),
    "stonepaving": ("stonepaving.jpg", (1, 1, 1), 0.9, 0.0, 5.0),
    "cedar": ("cedar.jpg", (1, 1, 1), 0.6, 0.0, 2.0),
})

PASS_W = 4.5        # passage width
GATE_W = 28.0       # width of a gate with its flanking towers
CELL_H = 2.1        # an animal panel: height ...
CELL_W = 3.07       # ... and width (the relief images are 1216 x 832)
BORDER_H = 0.38     # rosette border between two rows of animals
PLINTH = 1.4        # baked brick plinth under the glazed face
FRAME = 0.06        # reliefs stand this far off the wall


def v3(x, y, z):
    return Vector((x, y, z))


def quad_uv(model, mat, pts, flip=False, repeat=(1.0, 1.0), out=None):
    uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
    if flip:
        uvs = [(1, 0), (0, 0), (0, 1), (1, 1)]
    uvs = [(u * repeat[0], v * repeat[1]) for u, v in uvs]
    model.face(pts, mat, uvs, out)


def animal_rows(model, a, t, out, length, z0, rows, face_dir, rng, margin=0.5):
    """Rows of animal panels on a wall. `a` is the left end of the wall seen from outside, `t` the unit vector to the
    right (2D), `out` the outward normal (2D); rows run top to bottom as given ('bull' or 'dragon'); the animals face
    along `face_dir` (2D)."""
    n = max(1, int((length - 2 * margin) / (CELL_W + 0.3)))
    gap = (length - 2 * margin - n * CELL_W) / max(1, n)
    flip = (Vector(face_dir).dot(t) < 0)
    out3 = v3(out.x, out.y, 0)
    pitch = CELL_H + BORDER_H
    top = z0 + len(rows) * pitch
    for r, kind in enumerate(rows):
        zr = top - (r + 1) * pitch
        for c in range(n):
            s0 = margin + gap / 2 + c * (CELL_W + gap)
            p0 = a + t * s0 + out * FRAME
            p1 = a + t * (s0 + CELL_W) + out * FRAME
            variant = kind + "2" if (r + c) % 2 == 1 else kind   # two drawings of each animal, so the rows do not repeat
            quad_uv(model, variant, [v3(p0.x, p0.y, zr), v3(p1.x, p1.y, zr), v3(p1.x, p1.y, zr + CELL_H), v3(p0.x, p0.y, zr + CELL_H)],
                    flip, out=out3)
    # rosette borders above, between and below the rows
    for r in range(len(rows) + 1):
        zb = top - r * pitch - BORDER_H
        p0 = a + out * FRAME
        p1 = a + t * length + out * FRAME
        model.face([v3(p0.x, p0.y, zb), v3(p1.x, p1.y, zb), v3(p1.x, p1.y, zb + BORDER_H), v3(p0.x, p0.y, zb + BORDER_H)],
                   "border", [(0, 0), (length / (BORDER_H * 3), 0), (length / (BORDER_H * 3), 1), (0, 1)], out3)
    return top


def plain_wall(model, a, b, z0, z1, mat, rng):
    t = (b - a).normalized()
    out = Vector((t.y, -t.x, 0))
    model.jitter = 0.92 + rng.random() * 0.08
    model.wall([v3(a.x, a.y, z0), v3(b.x, b.y, z0), v3(b.x, b.y, z1), v3(a.x, a.y, z1)], mat, t, rng.random() * 6, out)
    model.jitter = 1.0


def crenellations(model, a, b, z, rng, mat="blueglaze", thick=1.0):
    """Stepped merlons along the top edge from a to b."""
    d = b - a
    length = d.length
    t = d / length
    n = max(1, int(length / 1.9))
    for k in range(n):
        c = a + d * ((k + 0.5) / n)
        sx, sy = (1.1, thick) if abs(t.x) > 0.5 else (thick, 1.1)
        Z.box(model, c.x, c.y, sx, sy, z, z + 1.1, mat, rng=rng)
        sx, sy = (0.6, thick) if abs(t.x) > 0.5 else (thick, 0.6)
        Z.box(model, c.x, c.y, sx, sy, z + 1.1, z + 1.9, "bakedbrick", rng=rng)


def arch_points(cx, spring, r, n=14):
    return [(cx + r * math.cos(math.pi - math.pi * i / n), spring + r * math.sin(math.pi * i / n)) for i in range(n + 1)]


def gate(model, y0, depth, height, rows, rng, spring, wall_h, towers_proj=3.0, wall_len=30.0, face_front=True):
    """One gate: a block with an arched passage, animal rows on the towers, battlements, and the curtain walls to
    both sides, set back so that the towers project."""
    hw = GATE_W / 2
    y1 = y0 + depth
    arch = arch_points(0.0, spring, PASS_W / 2)
    # front (-Y) and back (+Y) faces: pier faces and the part above the arch
    for yy, out, front in ((y0, v3(0, -1, 0), True), (y1, v3(0, 1, 0), False)):
        for sx in (-1, 1):
            xa, xb = (sx * hw, sx * PASS_W / 2) if sx < 0 else (sx * PASS_W / 2, sx * hw)
            pts = [v3(xa, yy, 0), v3(xb, yy, 0), v3(xb, yy, height), v3(xa, yy, height)]
            model.wall(pts, "blueglaze", Vector((1, 0)), rng.random() * 5, out)
        strip = [v3(x, yy, z) for x, z in arch] + [v3(PASS_W / 2, yy, height), v3(-PASS_W / 2, yy, height)]
        model.wall(strip, "blueglaze", Vector((1, 0)), rng.random() * 5, out)
        # a ring of baked brick around the opening
        for i in range(len(arch) - 1):
            (xa, za), (xb, zb) = arch[i], arch[i + 1]
            ra = (PASS_W / 2 + 0.55) / (PASS_W / 2)
            model.wall([v3(xa, yy + out.y * 0.05, za), v3(xb, yy + out.y * 0.05, zb),
                        v3(xb * ra, yy + out.y * 0.05, spring + (zb - spring) * ra), v3(xa * ra, yy + out.y * 0.05, spring + (za - spring) * ra)],
                       "bakedbrick", Vector((1, 0)), 0.0, out)
        for sx in (-1, 1):
            model.wall([v3(sx * PASS_W / 2, yy + out.y * 0.05, 0), v3(sx * (PASS_W / 2 + 0.55), yy + out.y * 0.05, 0),
                        v3(sx * (PASS_W / 2 + 0.55), yy + out.y * 0.05, spring), v3(sx * PASS_W / 2, yy + out.y * 0.05, spring)],
                       "bakedbrick", Vector((1, 0)), 0.0, out)
        # plinth and animal rows on the pier faces of the front only
        if front:
            for sx in (-1, 1):
                xa, xb = (sx * hw, sx * PASS_W / 2) if sx < 0 else (sx * PASS_W / 2, sx * hw)
                model.wall([v3(xa, yy - 0.04, 0), v3(xb, yy - 0.04, 0), v3(xb, yy - 0.04, PLINTH), v3(xa, yy - 0.04, PLINTH)],
                           "bakedbrick", Vector((1, 0)), 0.0, out)
                a = Vector((xa + (0.0 if sx < 0 else 0.55), yy))
                length = (xb - xa) - 0.55
                animal_rows(model, a, Vector((1, 0)), Vector((0, -1)), length, PLINTH + 0.4, rows, (-sx * 1.0, 0), rng, margin=1.1)
    # sides of the towers (the part that projects in front of the curtain walls)
    for sx in (-1, 1):
        x = sx * hw
        out = v3(sx, 0, 0)
        model.wall([v3(x, y0, 0), v3(x, y1, 0), v3(x, y1, height), v3(x, y0, height)], "blueglaze", Vector((0, 1)), 0.0, out)
    # top and a battlement ring
    model.top([v3(-hw, y0, height), v3(hw, y0, height), v3(hw, y1, height), v3(-hw, y1, height)], "bakedbrick")
    crenellations(model, Vector((-hw + 0.5, y0 + 0.5)), Vector((hw - 0.5, y0 + 0.5)), height, rng)
    crenellations(model, Vector((-hw + 0.5, y1 - 0.5)), Vector((hw - 0.5, y1 - 0.5)), height, rng)
    for sx in (-1, 1):
        crenellations(model, Vector((sx * (hw - 0.5), y0 + 0.5)), Vector((sx * (hw - 0.5), y1 - 0.5)), height, rng)
    # the passage: floor, walls, vault
    for z0, z1, mat in ((0.0, spring, "bakedbrick"),):
        for sx in (-1, 1):
            model.wall([v3(sx * PASS_W / 2, y0, z0), v3(sx * PASS_W / 2, y1, z0), v3(sx * PASS_W / 2, y1, z1), v3(sx * PASS_W / 2, y0, z1)],
                       mat, Vector((0, 1)), 0.0, v3(-sx, 0, 0))
    for i in range(len(arch) - 1):
        (xa, za), (xb, zb) = arch[i], arch[i + 1]
        model.wall([v3(xa, y0, za), v3(xb, y0, zb), v3(xb, y1, zb), v3(xa, y1, za)], "bakedbrick", Vector((1, 0)), 0.0,
                   v3(-(xa + xb) / 2, 0, -(((za + zb) / 2) - spring)))
    model.top([v3(-PASS_W / 2, y0, 0.02), v3(PASS_W / 2, y0, 0.02), v3(PASS_W / 2, y1, 0.02), v3(-PASS_W / 2, y1, 0.02)], "stonepaving")
    # door leaves, open against the passage walls (cedar clad in bronze)
    for yy in (y0 + 1.3, y1 - 1.3 - 2.2):
        for sx in (-1, 1):
            Z.box(model, sx * (PASS_W / 2 - 0.2), yy + 1.1, 0.35, 2.2, 0.0, spring + 0.5, "cedar", "cedar", rng)
    # curtain walls to both sides, set back so that the towers project
    for sx in (-1, 1):
        xa, xb = sx * hw, sx * (hw + wall_len)
        yf, yb = y0 + towers_proj, y1 - (depth - towers_proj - 7.0) if depth > towers_proj + 7.0 else y1
        yb = yf + 7.0
        lo, hi = (xa, xb) if sx > 0 else (xb, xa)
        model.wall([v3(lo, yf, 0), v3(hi, yf, 0), v3(hi, yf, wall_h), v3(lo, yf, wall_h)], "blueglaze", Vector((1, 0)), 0.0, v3(0, -1, 0))
        model.wall([v3(lo, yb, 0), v3(hi, yb, 0), v3(hi, yb, wall_h), v3(lo, yb, wall_h)], "blueglaze", Vector((1, 0)), 0.0, v3(0, 1, 0))
        model.wall([v3(xb, yf, 0), v3(xb, yb, 0), v3(xb, yb, wall_h), v3(xb, yf, wall_h)], "bakedbrick", Vector((0, 1)), 0.0, v3(sx, 0, 0))
        model.top([v3(lo, yf, wall_h), v3(hi, yf, wall_h), v3(hi, yb, wall_h), v3(lo, yb, wall_h)], "bakedbrick")
        # animal rows along the front of the wall
        a = Vector((lo, yf))
        nrows = max(2, int((wall_h - PLINTH - 2.2) / (CELL_H + BORDER_H)))
        kinds = [("bull" if (nrows - 1 - r) % 2 == 0 else "dragon") for r in range(nrows)]
        animal_rows(model, a, Vector((1, 0)), Vector((0, -1)), hi - lo, PLINTH + 0.3, kinds, (-sx, 0), rng)
        crenellations(model, Vector((lo + 0.5, yf + 0.5)), Vector((hi - 0.5, yf + 0.5)), wall_h, rng)


def ground(model, x0, x1, y0, y1, mat="stonepaving"):
    model.top([v3(x0, y0, 0.0), v3(x1, y0, 0.0), v3(x1, y1, 0.0), v3(x0, y1, 0.0)], mat)


def gate_complex(model, rng):
    outer_rows = ["bull", "dragon", "bull", "dragon", "bull"]
    inner_rows = [("bull" if r % 2 == 0 else "dragon") for r in range(9)]
    gate(model, 0.0, 11.0, 15.0, outer_rows, rng, spring=7.0, wall_h=12.0)
    # the courtyard between the gates
    ground(model, -14.0, 14.0, 11.0, 19.0)
    for sx in (-1, 1):
        a = Vector((sx * 14.0, 11.0))
        b = Vector((sx * 14.0, 19.0))
        model.wall([v3(sx * 14.0, 11.0, 0), v3(sx * 14.0, 19.0, 0), v3(sx * 14.0, 19.0, 12.0), v3(sx * 14.0, 11.0, 12.0)],
                   "blueglaze", Vector((0, 1)), 0.0, v3(-sx, 0, 0))
    gate(model, 19.0, 29.0, 25.0, inner_rows, rng, spring=8.3, wall_h=18.0)
    ground(model, -44.0, 44.0, -2.0, 0.0)
    ground(model, -44.0, 44.0, 48.0, 54.0)
    return model


def processional_way(model, rng, length=80.0):
    half = 10.0
    y_start = -length
    ground(model, -half, half, y_start, -2.0, "stonepaving")  # the last 2 m belong to the apron of the gate
    wall_h = 10.0
    for sx in (-1, 1):
        xi = sx * half            # inner face of the wall
        xo = sx * (half + 3.0)
        lo, hi = (min(xi, xo), max(xi, xo))
        out_in = v3(-sx, 0, 0)    # the street side faces the street
        # the street face: blue glaze above, lions on the plinth row
        model.wall([v3(xi, y_start, 0), v3(xi, 0, 0), v3(xi, 0, wall_h), v3(xi, y_start, wall_h)], "blueglaze", Vector((0, 1)), 0.0, out_in)
        model.wall([v3(xo, y_start, 0), v3(xo, 0, 0), v3(xo, 0, wall_h), v3(xo, y_start, wall_h)], "bakedbrick", Vector((0, 1)), 0.0, v3(sx, 0, 0))
        model.top([v3(xi, y_start, wall_h), v3(xo, y_start, wall_h), v3(xo, 0, wall_h), v3(xi, 0, wall_h)], "bakedbrick")
        model.wall([v3(xi, y_start, 0), v3(xo, y_start, 0), v3(xo, y_start, wall_h), v3(xi, y_start, wall_h)], "bakedbrick", Vector((1, 0)), 0.0, v3(0, -1, 0))
        # lions: the viewer on the street looks at the wall; a is the left end of the wall seen from the street
        if sx > 0:      # east wall, looking +X: right is -Y
            a = Vector((xi, 0.0))
            t = Vector((0, -1))
        else:           # west wall, looking -X: right is +Y
            a = Vector((xi, y_start))
            t = Vector((0, 1))
        out2 = Vector((-sx, 0))
        L = length
        n = int(L / (CELL_W + 0.35))
        gap = (L - n * CELL_W) / n
        flip = Vector((0, 1)).dot(t) < 0   # the lions walk towards the gate (+Y)
        for c in range(n):
            s0 = gap / 2 + c * (CELL_W + gap)
            p0 = a + t * s0 + out2 * FRAME
            p1 = a + t * (s0 + CELL_W) + out2 * FRAME
            z0 = 1.6
            quad_uv(model, "lion", [v3(p0.x, p0.y, z0), v3(p1.x, p1.y, z0), v3(p1.x, p1.y, z0 + CELL_H), v3(p0.x, p0.y, z0 + CELL_H)], flip,
                    out=v3(out2.x, out2.y, 0))
        # rosette borders above and below the lions and under the top
        for zb in (1.6 - BORDER_H, 1.6 + CELL_H, wall_h - 1.4):
            p0 = a + out2 * FRAME
            p1 = a + t * L + out2 * FRAME
            model.face([v3(p0.x, p0.y, zb), v3(p1.x, p1.y, zb), v3(p1.x, p1.y, zb + BORDER_H), v3(p0.x, p0.y, zb + BORDER_H)],
                       "border", [(0, 0), (L / (BORDER_H * 3), 0), (L / (BORDER_H * 3), 1), (0, 1)], v3(out2.x, out2.y, 0))
    return model


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    which, out = args[0], args[1]
    rng = random.Random(11)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    model = Z.Model()
    if which == "ishtar_gate":
        gate_complex(model, rng)
    elif which == "processional_way":
        processional_way(model, rng)
    elif which == "ishtar_gate_complete":
        gate_complex(model, rng)
        processional_way(model, rng)
        # the street meets the gate: shift is zero, the way ends at y = 0 where the outer gate begins
    else:
        raise SystemExit("unknown model " + which)
    Z.finish(model, out)


if __name__ == "__main__":
    main()
