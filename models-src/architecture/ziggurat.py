"""Mesopotamian ziggurats, built procedurally in Blender with textures from textures/*.jpg.

    blender -b --python models-src/architecture/ziggurat.py -- <model> <out.glb>

models:  etemenanki          the great tower of Babylon (seven stages), tower only
         etemenanki_precinct courtyard, enclosure wall with a glazed gate, palms
         etemenanki_complete both in one file
         anu                 the Early Dynastic ziggurat of Anu in Uruk with the White Temple on top

Metres, ground at z = 0, the front (stairs) faces -Y like the character models. Every wall is a prism with the
sloping sides ("batter") and the pilaster and recess pattern of Mesopotamian mud-brick architecture; the stairs are
single sawtooth prisms. Texture coordinates are in metres per texture tile, so the brick courses keep one size on
every wall.

Proportions of the Etemenanki follow the Esagila tablet as reconstructed by Schmid and George: a square base of about
91.5 m, a first stage 33 m high, a second 18 m, four of 6 m and the temple of Marduk 15 m on top, 90 m in all.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTURES = os.path.join(HERE, "textures")

# name: (texture file or None, colour, roughness, metallic, tile size in metres)
MATERIALS = {
    "mudbrick": ("mudbrick.jpg", (1, 1, 1), 0.95, 0.0, 4.0),
    "bakedbrick": ("bakedbrick.jpg", (1, 1, 1), 0.9, 0.0, 3.0),
    "glazed": ("glazed.jpg", (1, 1, 1), 0.3, 0.0, 3.0),
    "plaster": ("plaster.jpg", (1, 1, 1), 0.9, 0.0, 5.0),
    "paving": ("paving.jpg", (1, 1, 1), 0.95, 0.0, 4.0),
    "gold": (None, (0.9, 0.62, 0.12), 0.3, 0.9, 1.0),
    "door": (None, (0.035, 0.028, 0.022), 1.0, 0.0, 1.0),
    "trunk": (None, (0.30, 0.21, 0.12), 0.95, 0.0, 1.0),
    "frond": (None, (0.17, 0.33, 0.10), 0.8, 0.0, 1.0),
}


def tile(name):
    return MATERIALS[name][4]


class Model:
    """One bmesh with a material per face; faces are not shared, so every surface is flat shaded."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.col = self.bm.loops.layers.color.new("Col")
        self.order = []
        self.jitter = 1.0  # brightness of the surface being built; walls vary a little from piece to piece

    def index(self, name):
        if name not in self.order:
            self.order.append(name)
        return self.order.index(name)

    def face(self, pts, mat, uvs, outward=None):
        pts = [Vector(p) for p in pts]
        uvs = list(uvs)
        if outward is not None:
            normal = Vector((0, 0, 0))
            for i, p in enumerate(pts):  # Newell's method
                q = pts[(i + 1) % len(pts)]
                normal += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
            if normal.dot(Vector(outward)) < 0:
                pts.reverse()
                uvs.reverse()
        verts = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(verts)
        f.material_index = self.index(mat)
        for loop, (u, v) in zip(f.loops, uvs):
            loop[self.uv].uv = (u, v)
            # weathering: the foot of a wall is darker, the rest differs slightly from piece to piece
            fade = 0.72 + 0.28 * min(1.0, max(0.0, loop.vert.co.z) / 7.0)
            value = min(1.0, fade * self.jitter)
            loop[self.col] = (value, value, value, 1.0)
        return f

    # surfaces with world-scale texture coordinates
    def wall(self, pts, mat, along, offset=0.0, outward=None):
        t = tile(mat)
        self.face(pts, mat, [((p.x * along.x + p.y * along.y) / t + offset, p.z / t) for p in pts], outward)

    def top(self, pts, mat, offset=(0.0, 0.0)):
        t = tile(mat)
        self.face(pts, mat, [(p.x / t + offset[0], p.y / t + offset[1]) for p in pts], (0, 0, 1))


def box(model, cx, cy, sx, sy, z0, z1, mat_wall, mat_top=None, rng=None, front_only=False):
    """An axis-aligned block without a bottom."""
    hx, hy = sx / 2, sy / 2
    p = [Vector((cx - hx, cy - hy)), Vector((cx + hx, cy - hy)), Vector((cx + hx, cy + hy)), Vector((cx - hx, cy + hy))]
    for i in range(4):
        a, b = p[i], p[(i + 1) % 4]
        t = (b - a).normalized()
        out = Vector((t.y, -t.x, 0))
        off = rng.random() * 8 if rng else 0.0
        model.wall([Vector((a.x, a.y, z0)), Vector((b.x, b.y, z0)), Vector((b.x, b.y, z1)), Vector((a.x, a.y, z1))],
                   mat_wall, t, off, out)
    model.top([Vector((q.x, q.y, z1)) for q in p], mat_top or mat_wall)


def outline(cx, cy, w, d, spacing, corner, recess, panel_ratio=0.62):
    """Counter-clockwise outline of a w x d rectangle whose walls have pilasters and recessed panels between them."""
    hw, hd = w / 2, d / 2
    corners = [Vector((cx - hw, cy - hd)), Vector((cx + hw, cy - hd)), Vector((cx + hw, cy + hd)), Vector((cx - hw, cy + hd))]
    pts = []
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        t = b - a
        length = t.length
        t /= length
        inward = Vector((-t.y, t.x))
        bays = max(1, round((length - 2 * corner) / spacing))
        unit = (length - 2 * corner) / bays
        panel = unit * panel_ratio
        pts.append(a)
        for k in range(bays):
            s0 = corner + k * unit + (unit - panel) / 2 - 0.0
            pts += [a + t * s0, a + t * s0 + inward * recess, a + t * (s0 + panel) + inward * recess, a + t * (s0 + panel)]
    return pts


def prism(model, pts, z0, z1, centre, scale, mat, rng, cap_mat=None):
    """Walls of a polygon prism whose top is the polygon scaled about `centre`; returns the top polygon."""
    top = [Vector((centre.x + (p.x - centre.x) * scale, centre.y + (p.y - centre.y) * scale)) for p in pts]
    run = 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        ta, tb = top[i], top[(i + 1) % len(pts)]
        t = b - a
        length = t.length
        if length < 1e-6:
            continue
        t /= length
        out = Vector((t.y, -t.x, 0))
        model.jitter = 0.9 + rng.random() * 0.1
        model.wall([Vector((a.x, a.y, z0)), Vector((b.x, b.y, z0)), Vector((tb.x, tb.y, z1)), Vector((ta.x, ta.y, z1))],
                   mat, t, rng.random() * 9, out)
        model.jitter = 1.0
        run += length
    if cap_mat:
        model.top([Vector((p.x, p.y, z1)) for p in top], cap_mat)
    return top


def merlons(model, cx, cy, half, z, rng, skip_front=0.0, spacing=2.4, mat="mudbrick"):
    """Battlements along the edge of a terrace; `skip_front` leaves a gap of that width in front for the stairs."""
    inset = 0.45
    h = half - inset
    corners = [(-h, -h), (h, -h), (h, h), (-h, h)]
    for i in range(4):
        a = Vector((cx + corners[i][0], cy + corners[i][1]))
        b = Vector((cx + corners[(i + 1) % 4][0], cy + corners[(i + 1) % 4][1]))
        length = (b - a).length
        n = int(length / spacing)
        for k in range(n):
            c = a + (b - a) * ((k + 0.5) / n)
            if skip_front and i == 0 and abs(c.x - cx) < skip_front / 2:
                continue
            t = (b - a).normalized()
            if abs(t.x) > 0.5:
                box(model, c.x, c.y, 1.0, 0.6, z, z + 1.15, mat, rng=rng)
            else:
                box(model, c.x, c.y, 0.6, 1.0, z, z + 1.15, mat, rng=rng)


def stairs(model, ox, oy, direction, width, z0, rise, run, rh=0.3, wall_mat="bakedbrick", tread_mat="bakedbrick", slab=None):
    """A flight of steps as a sawtooth prism, climbing from (ox, oy) along `direction` (a unit 2D vector)."""
    n = max(1, round(rise / rh))
    rh = rise / n
    td = run / n
    d = Vector((direction[0], direction[1]))
    left = Vector((-d.y, d.x))

    def P(s, lat, z):
        return Vector((ox + d.x * s + left.x * lat, oy + d.y * s + left.y * lat, z))

    hw = width / 2
    away = Vector((-d.x, -d.y, 0))
    for k in range(n):
        zb, zt = z0 + k * rh, z0 + (k + 1) * rh
        model.wall([P(k * td, -hw, zb), P(k * td, hw, zb), P(k * td, hw, zt), P(k * td, -hw, zt)], wall_mat, left, 0.0, away)
        pts = [P(k * td, -hw, zt), P((k + 1) * td, -hw, zt), P((k + 1) * td, hw, zt), P(k * td, hw, zt)]
        model.top(pts, tread_mat)
    # `slab`: a flight leaning on a wall is a thin inclined slab of that thickness instead of a solid wedge
    s0 = slab * run / rise if slab else 0.0
    for lat, out in ((-hw, -left), (hw, left)):
        pts = [P(0, lat, z0)]
        for k in range(n):
            zt = z0 + (k + 1) * rh
            pts += [P(k * td, lat, zt), P((k + 1) * td, lat, zt)]
        if slab:
            pts += [P(run, lat, z0 + rise - slab), P(s0, lat, z0)]
        else:
            pts.append(P(run, lat, z0))
        model.wall(pts, wall_mat, d, 0.0, Vector((out.x, out.y, 0)))
    if slab:
        model.wall([P(s0, -hw, z0), P(s0, hw, z0), P(run, hw, z0 + rise - slab), P(run, -hw, z0 + rise - slab)],
                   wall_mat, left, 0.0, Vector((d.y * 0, 0, -1)) + Vector((-d.x, -d.y, 0)) * 0.0)
        model.wall([P(run, -hw, z0 + rise - slab), P(run, hw, z0 + rise - slab), P(run, hw, z0 + rise), P(run, -hw, z0 + rise)],
                   wall_mat, left, 0.0, Vector((d.x, d.y, 0)))


def portal(model, cx, y_front, z0, width, depth, height, door_w, door_h, rng, mat="glazed", trim="plaster", gold=True):
    """A gate block against a wall, facing -Y: piers, lintel, a dark doorway and a gold cornice."""
    hx = width / 2
    yb = y_front + depth  # the wall behind
    # side and top faces
    for sx in (-1, 1):
        model.wall([Vector((cx + sx * hx, y_front, z0)), Vector((cx + sx * hx, yb, z0)), Vector((cx + sx * hx, yb, z0 + height)),
                    Vector((cx + sx * hx, y_front, z0 + height))], mat, Vector((0, 1, 0)), 0.0, Vector((sx, 0, 0)))
    model.top([Vector((cx - hx, y_front, z0 + height)), Vector((cx + hx, y_front, z0 + height)),
               Vector((cx + hx, yb, z0 + height)), Vector((cx - hx, yb, z0 + height))], trim)
    # front: piers and lintel around the opening
    dw = door_w / 2
    out = Vector((0, -1, 0))
    x = Vector((1, 0, 0))
    plinth = 0.9
    for (xa, xb) in ((cx - hx, cx - dw), (cx + dw, cx + hx)):
        model.wall([Vector((xa, y_front, z0 + plinth)), Vector((xb, y_front, z0 + plinth)), Vector((xb, y_front, z0 + height)),
                    Vector((xa, y_front, z0 + height))], mat, x, rng.random() * 5, out)
        model.wall([Vector((xa, y_front, z0)), Vector((xb, y_front, z0)), Vector((xb, y_front, z0 + plinth)),
                    Vector((xa, y_front, z0 + plinth))], trim, x, 0.0, out)
    model.wall([Vector((cx - dw, y_front, z0 + door_h)), Vector((cx + dw, y_front, z0 + door_h)),
                Vector((cx + dw, y_front, z0 + height)), Vector((cx - dw, y_front, z0 + height))], mat, x, 0.0, out)
    # the doorway: reveals and a dark back wall
    rev = min(depth * 0.8, 1.6)
    for sx in (-1, 1):
        model.wall([Vector((cx + sx * dw, y_front, z0)), Vector((cx + sx * dw, y_front + rev, z0)),
                    Vector((cx + sx * dw, y_front + rev, z0 + door_h)), Vector((cx + sx * dw, y_front, z0 + door_h))],
                   trim, Vector((0, 1, 0)), 0.0, Vector((-sx, 0, 0)))
    model.face([Vector((cx - dw, y_front, z0 + door_h)), Vector((cx + dw, y_front, z0 + door_h)),
                Vector((cx + dw, y_front + rev, z0 + door_h)), Vector((cx - dw, y_front + rev, z0 + door_h))],
               trim, [(0, 0), (1, 0), (1, 1), (0, 1)], (0, 0, -1))
    model.face([Vector((cx - dw, y_front + rev, z0)), Vector((cx + dw, y_front + rev, z0)),
                Vector((cx + dw, y_front + rev, z0 + door_h)), Vector((cx - dw, y_front + rev, z0 + door_h))],
               "door", [(0, 0), (1, 0), (1, 1), (0, 1)], out)
    if not gold:
        return
    # gold cornice
    model.wall([Vector((cx - hx - 0.1, y_front - 0.15, z0 + height)), Vector((cx + hx + 0.1, y_front - 0.15, z0 + height)),
                Vector((cx + hx + 0.1, y_front - 0.15, z0 + height + 0.45)), Vector((cx - hx - 0.1, y_front - 0.15, z0 + height + 0.45))],
               "gold", x, 0.0, out)


def temple(model, cx, y_front, z0, w, d, h, rng, body="glazed", plinth_mat="plaster", gold=True, upper=True):
    """The shrine on top: pilastered walls on a plaster plinth, a doorway in the middle of the front, a stepped
    parapet, and (for the temple of Marduk) a smaller upper chamber under a gold roof."""
    cy = y_front + d / 2
    plinth_h = 1.6
    base = outline(cx, cy, w + 1.0, d + 1.0, 4.0, 1.0, 0.0)
    prism(model, base, z0, z0 + plinth_h, Vector((cx, cy)), 1.0, plinth_mat, rng, cap_mat=plinth_mat)
    walls = outline(cx, cy, w, d, 3.2, 1.1, 0.45)
    prism(model, walls, z0 + plinth_h, z0 + h, Vector((cx, cy)), 0.985, body, rng, cap_mat=plinth_mat)
    # gold cornice under the roof edge and a stepped (horned) parapet
    if gold:
        box(model, cx, cy, w + 0.5, d + 0.5, z0 + h - 0.9, z0 + h, "gold", None, rng)
    step = 1.7
    for side in range(4):
        n = int((w if side % 2 == 0 else d) / step)
        for k in range(n):
            off = -((w if side % 2 == 0 else d) / 2) + (k + 0.5) * (w if side % 2 == 0 else d) / n
            px = cx + off if side % 2 == 0 else cx + (w / 2 - 0.3) * (1 if side == 1 else -1)
            py = (y_front + 0.3 if side == 0 else y_front + d - 0.3) if side % 2 == 0 else cy + off
            if side == 0 and abs(px - cx) < 3.0:
                continue
            box(model, px, py, 0.9, 0.9, z0 + h, z0 + h + 1.2, body, plinth_mat, rng)
            box(model, px, py, 0.5, 0.5, z0 + h + 1.2, z0 + h + 1.9, body, plinth_mat, rng)
    if upper:
        uw, ud = w * 0.62, d * 0.55
        uy = y_front + d * 0.5
        box(model, cx, uy, uw, ud, z0 + h, z0 + h + 4.2, body, plinth_mat, rng)
        box(model, cx, uy, uw + 0.8, ud + 0.8, z0 + h + 4.2, z0 + h + 4.9, "gold" if gold else plinth_mat, None, rng)
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(model, cx + sx * (uw / 2 - 0.2), uy + sy * (ud / 2 - 0.2), 0.9, 0.9, z0 + h + 4.9, z0 + h + 6.4,
                    "gold" if gold else plinth_mat)
    # horned corner towers
    for sx in (-1, 1):
        for sy in (0, 1):
            tx, ty = cx + sx * (w / 2 - 0.5), y_front + 0.5 + sy * (d - 1.0)
            box(model, tx, ty, 1.7, 1.7, z0 + h, z0 + h + 2.4, body, plinth_mat, rng)
            if gold:
                box(model, tx, ty, 1.0, 1.0, z0 + h + 2.4, z0 + h + 3.8, "gold")
    # doorway on the front face
    portal(model, cx, y_front - 0.55, z0 + plinth_h - 0.1, 6.2, 1.0, h - plinth_h * 0.8, 3.6, 7.2, rng, mat=body, trim=plinth_mat, gold=gold)


def etemenanki(model, rng):
    widths = [91.5, 72.0, 58.0, 49.0, 41.0, 33.0]
    heights = [33.0, 18.0, 6.0, 6.0, 6.0, 6.0]
    z = 0.0
    top_front = None
    top_w = None
    cy = 0.0
    tops = []
    foundation = outline(0.0, 0.0, widths[0] + 3.0, widths[0] + 3.0, 14.0, 3.0, 0.0)
    prism(model, foundation, 0.0, 1.5, Vector((0.0, 0.0)), 1.0, "bakedbrick", rng, cap_mat="bakedbrick")
    for k, (w, h) in enumerate(zip(widths, heights)):
        inset = 0.035 * h
        if k == 0:
            y_front = -w / 2
        else:
            y_front = top_front + 0.75 * (top_w - w)
        cy = y_front + w / 2
        spacing = 7.6 if k == 0 else max(3.4, w / 11)
        pts = outline(0.0, cy, w, w, spacing, 3.0 if k == 0 else 1.8, 0.9 if k == 0 else 0.45, 0.30 if k == 0 else 0.5)
        scale = (w - 2 * inset) / w
        prism(model, pts, z, z + h, Vector((0.0, cy)), scale, "mudbrick", rng, cap_mat="paving")
        t_w = w - 2 * inset
        t_front = y_front + inset
        merlons(model, 0.0, cy, t_w / 2, z + h, rng, skip_front=7.5 if k < 5 else 9.5, spacing=2.5)
        tops.append((z + h, 0.0, cy, t_w, t_front))
        top_front, top_w = t_front, t_w
        z += h

    # the three stairways of the first stage, and a central flight up each higher stage
    y1 = -widths[0] / 2
    inset1 = 0.035 * heights[0]
    stairs(model, 0.0, y1 - heights[0] + inset1 * 0.0, (0, 1), 7.0, 0.0, heights[0], heights[0] + inset1, rh=0.3)
    run_side = 31.0
    stairs(model, -(widths[0] / 2 - 4.2), y1 - 1.7, (1, 0), 3.4, 0.0, heights[0] - 2.5, run_side, rh=0.3, slab=2.4)
    stairs(model, (widths[0] / 2 - 4.2), y1 - 1.7, (-1, 0), 3.4, 0.0, heights[0] - 2.5, run_side, rh=0.3, slab=2.4)
    z = heights[0]
    for k in range(1, 6):
        w, h = widths[k], heights[k]
        zt, cx, cy_k, t_w, t_front = tops[k]
        y_front = cy_k - w / 2
        margin = y_front - tops[k - 1][4]
        inset = 0.035 * h
        run = min(h, margin - 1.4)
        y_end = y_front + inset
        stairs(model, 0.0, y_end - run, (0, 1), 5.5 if k < 3 else 4.2, z, h, run + inset * 0.0, rh=0.3)
        for sx in (-1, 1):
            gx = sx * min(w * 0.30, 17.0)
            portal(model, gx, y_front - 2.4, z, 5.4, 2.4, min(5.0, h - 0.8), 2.2, min(3.6, h - 2.0), rng)
        z += h

    # the temple of Marduk on the last terrace
    zt, cx, cy_k, t_w, t_front = tops[5]
    back = cy_k + t_w / 2
    temple(model, 0.0, back - 3.0 - 14.0, zt, 24.0, 15.0, 15.0, rng)
    return model


def anu(model, rng):
    """The Anu ziggurat of Early Dynastic Uruk: a high terrace of mud brick with the whitewashed White Temple on it."""
    z = 0.0
    spec = [(52.0, 7.5, 0.06), (38.0, 6.0, 0.05)]
    top_front = None
    top_w = None
    tops = []
    for k, (w, h, batter) in enumerate(spec):
        inset = batter * h
        y_front = -w / 2 if k == 0 else top_front + 0.6 * (top_w - w)
        cy = y_front + w / 2
        pts = outline(0.0, cy, w, w, 4.4, 1.8, 0.5)
        scale = (w - 2 * inset) / w
        prism(model, pts, z, z + h, Vector((0.0, cy)), scale, "mudbrick", rng, cap_mat="plaster")
        t_w = w - 2 * inset
        t_front = y_front + inset
        merlons(model, 0.0, cy, t_w / 2, z + h, rng, skip_front=7.0 if k == 0 else 5.0, spacing=2.6, mat="plaster")
        tops.append((z + h, 0.0, cy, t_w, t_front))
        top_front, top_w = t_front, t_w
        z += h
    stairs(model, 0.0, -26.0 + 0.45 - 7.9, (0, 1), 6.0, 0.0, 7.5, 7.9, rh=0.3)
    stairs(model, -19.0, -27.5, (1, 0), 3.0, 0.0, 6.0, 12.0, rh=0.3, slab=1.6)
    stairs(model, 19.0, -27.5, (-1, 0), 3.0, 0.0, 6.0, 12.0, rh=0.3, slab=1.6)
    zt, cx, cy_k, t_w, t_front = tops[1]
    y_front = cy_k - 19.0
    margin = y_front - tops[0][4]
    run = min(6.0, margin - 1.2)
    stairs(model, 0.0, y_front + 0.3 - run, (0, 1), 4.5, tops[0][0], 6.0, run, rh=0.3)
    back = cy_k + t_w / 2
    temple(model, 0.0, back - 2.5 - 17.5, zt, 22.0, 17.5, 6.5, rng, body="plaster", plinth_mat="plaster", gold=False, upper=False)
    return model


def precinct(model, rng):
    """Paved court, enclosure wall with pilasters and a glazed band, a gatehouse and date palms."""
    half = 100.0
    slab = [Vector((-half, -half)), Vector((half, -half)), Vector((half, half)), Vector((-half, half))]
    model.top([Vector((p.x, p.y, 0.0)) for p in slab], "paving")
    # the road in front of the gate
    road = [Vector((-14.0, -half - 30.0)), Vector((14.0, -half - 30.0)), Vector((14.0, -half)), Vector((-14.0, -half))]
    model.top([Vector((p.x, p.y, 0.0)) for p in road], "paving", (0.31, 0.17))
    wall_h, thick = 6.0, 3.2
    gate_w = 16.0
    # side and back walls, front wall in two parts
    segments = [(-half, half, half, half), (-half, -half, -half, half), (half, -half, half, half)]
    for (x0, y0, x1, y1) in segments:
        a, b = Vector((x0, y0)), Vector((x1, y1))
        wall_run(model, a, b, wall_h, thick, rng)
    wall_run(model, Vector((-half, -half)), Vector((-gate_w / 2 - 10.0, -half)), wall_h, thick, rng)
    wall_run(model, Vector((gate_w / 2 + 10.0, -half)), Vector((half, -half)), wall_h, thick, rng)
    # the gatehouse: two towers around the entrance
    for sx in (-1, 1):
        cx = sx * (gate_w / 2 + 5.0)
        tower_block(model, cx, -half, 10.0, 10.0, 17.0, rng)
    # lintel block above the gate
    box(model, 0.0, -half, gate_w, 8.0, 10.5, 14.0, "glazed", "plaster", rng)
    box(model, 0.0, -half - 0.2, gate_w + 0.4, 8.4, 14.0, 14.7, "gold", None, rng)
    # palms inside the court
    for (px, py) in palm_positions(rng, half - 12.0):
        palm(model, px, py, rng)
    return model


def wall_run(model, a, b, h, thick, rng):
    d = b - a
    length = d.length
    t = d / length
    n = Vector((-t.y, t.x))
    # core: a long box rotated onto the axis (the walls are axis aligned)
    cx, cy = (a.x + b.x) / 2, (a.y + b.y) / 2
    if abs(t.x) > 0.5:
        sx, sy = length, thick
    else:
        sx, sy = thick, length
    glaze = 1.7
    # lower part mud brick, glazed band on top
    box(model, cx, cy, sx, sy, 0.0, h - glaze, "mudbrick", None, rng)
    box(model, cx, cy, sx + 0.2, sy + 0.2, h - glaze, h, "glazed", "plaster", rng)
    # battlements
    count = int(length / 2.4)
    for k in range(count):
        c = a + d * ((k + 0.5) / count)
        if abs(t.x) > 0.5:
            box(model, c.x, c.y, 1.0, thick * 0.7, h, h + 1.1, "mudbrick", rng=rng)
        else:
            box(model, c.x, c.y, thick * 0.7, 1.0, h, h + 1.1, "mudbrick", rng=rng)


def tower_block(model, cx, cy, sx, sy, h, rng):
    box(model, cx, cy, sx, sy, 0.0, h - 2.2, "mudbrick", None, rng)
    box(model, cx, cy, sx + 0.3, sy + 0.3, h - 2.2, h, "glazed", "plaster", rng)
    for dx in (-1, 1):
        for dy in (-1, 1):
            box(model, cx + dx * (sx / 2 - 0.5), cy + dy * (sy / 2 - 0.5), 1.0, 1.0, h, h + 1.2, "mudbrick", rng=rng)
    # glazed band mid-height
    box(model, cx, cy, sx + 0.25, sy + 0.25, 5.0, 6.4, "glazed", "plaster", rng)


def palm_positions(rng, extent):
    pts = []
    for k in range(60):
        side = k % 4
        s = rng.uniform(-extent, extent)
        off = rng.uniform(0, 9)
        if side == 0:
            pts.append((s, extent - off))
        elif side == 1:
            pts.append((-extent + off, s))
        elif side == 2:
            pts.append((extent - off, s))
        else:
            pts.append((s, -extent + off * 0.7))
    # keep the avenue to the tower free
    return [p for p in pts if not (abs(p[0]) < 12 and p[1] < 0)]


def palm(model, x, y, rng):
    """A low-poly date palm: a tapering trunk and a crown of curved fronds."""
    height = rng.uniform(9.0, 13.5)
    r0, r1 = 0.38, 0.22
    lean = Vector((rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8)))
    segs = 8
    prev = None
    rings = 3
    for ring in range(rings + 1):
        t = ring / rings
        c = Vector((x + lean.x * t * t, y + lean.y * t * t, height * t))
        r = r0 + (r1 - r0) * t
        pts = [Vector((c.x + math.cos(2 * math.pi * i / segs) * r, c.y + math.sin(2 * math.pi * i / segs) * r, c.z)) for i in range(segs)]
        if prev is not None:
            for i in range(segs):
                j = (i + 1) % segs
                model.face([prev[i], prev[j], pts[j], pts[i]], "trunk", [(0, 0), (1, 0), (1, 1), (0, 1)],
                           Vector(((prev[i].x + prev[j].x) / 2 - x, (prev[i].y + prev[j].y) / 2 - y, 0)))
        prev = pts
    top = Vector((x + lean.x, y + lean.y, height))
    n = 11
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        d = Vector((math.cos(a), math.sin(a), 0))
        side = Vector((-d.y, d.x, 0))
        length = rng.uniform(4.6, 5.8)
        pts = []
        for s in range(5):
            t = s / 4
            width = 0.7 * math.sin(math.pi * (0.15 + 0.85 * t) ) * (1 - 0.3 * t) + 0.04
            c = top + d * (length * t) + Vector((0, 0, 1.15 * math.sin(math.pi * t * 0.85) - 1.4 * t * t))
            pts.append((c + side * width, c - side * width))
        for s in range(4):
            a0, b0 = pts[s]
            a1, b1 = pts[s + 1]
            model.face([a0, a1, b1, b0], "frond", [(0, 0), (1, 0), (1, 1), (0, 1)], (0, 0, 1))
            model.face([b0, b1, a1, a0], "frond", [(0, 0), (1, 0), (1, 1), (0, 1)], (0, 0, -1))


def materials_for(model):
    out = []
    for name in model.order:
        tex, colour, rough, metal, _ = MATERIALS[name]
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bsdf = nodes["Principled BSDF"]
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if tex:
            image = bpy.data.images.load(os.path.join(TEXTURES, tex))
            node = nodes.new("ShaderNodeTexImage")
            node.image = image
            if tuple(colour) != (1, 1, 1):  # a tint multiplies the texture (exported as the base colour factor)
                mix = nodes.new("ShaderNodeMix")
                mix.data_type = "RGBA"
                mix.blend_type = "MULTIPLY"
                mix.inputs[0].default_value = 1.0
                mix.inputs[7].default_value = (*colour, 1.0)
                links.new(node.outputs["Color"], mix.inputs[6])
                links.new(mix.outputs[2], bsdf.inputs["Base Color"])
            else:
                links.new(node.outputs["Color"], bsdf.inputs["Base Color"])
        else:
            bsdf.inputs["Base Color"].default_value = (*colour, 1.0)
        out.append(mat)
    return out


def finish(model, path):
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    me = bpy.data.meshes.new("ziggurat")
    model.bm.to_mesh(me)
    model.bm.free()
    for m in materials_for(model):
        me.materials.append(m)
    obj = bpy.data.objects.new(os.path.splitext(os.path.basename(path))[0], me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_image_format="JPEG",
                              export_jpeg_quality=85, export_yup=True, export_apply=False, export_lights=False,
                              export_cameras=False, export_animations=False, export_vertex_color='ACTIVE')
    print("exported", path, os.path.getsize(path), "bytes", len(me.polygons), "faces")


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    which, out = args[0], args[1]
    rng = random.Random(7)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    model = Model()
    if which == "etemenanki":
        etemenanki(model, rng)
    elif which == "etemenanki_precinct":
        precinct(model, rng)
    elif which == "etemenanki_complete":
        etemenanki(model, rng)
        precinct(model, rng)
    elif which == "anu":
        anu(model, rng)
    else:
        raise SystemExit("unknown model " + which)
    finish(model, out)


if __name__ == "__main__":
    main()
