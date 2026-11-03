"""The houses and streets of Uruk, built from the plan of tools/build_city.py (tools/data/uruk_city.json).

    blender -b --python models-src/architecture/uruk_city.py -- all media/models/architecture
    blender -b --python models-src/architecture/uruk_city.py -- uruk_city_03 media/models/architecture

One glb (and a lean collision twin) for every quarter of the city: its streets, the houses along them in three sizes
with their own sizes, turns, heights and wall colours, the smithies, and the small gate markets. The great market, the two
palaces with their farm buildings, the ziggurat of Ishtar and the court of the Eanna precinct are models of their own
(uruk_sites.py). Every model is built in the world frame of the plan around its own origin (the anchor of its place), so that
a place needs no offset or turn: Blender X is the client's x (east), Blender Y is -z (north), heights are metres above the
terrain at the origin (read from media/terrain/uruk_height.png, as the server's patch gives it).

The look follows the reference of the owner: flat roofs of sand-coloured mud brick, parapets (some with the pointed teeth
of the poor houses), pale plastered and red-banded houses of the rich, dark doors, light wells in the roofs, forges with
tall chimneys, coloured awnings over the market stalls.
"""
import json
import math
import os
import random
import struct
import sys
import zlib

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))

import ishtar_gate  # noqa: E402,F401  (registers the blue glaze materials)
import ziggurat as Z  # noqa: E402
from city_kinds import kind_of  # noqa: E402  (houses drawn as separate buildings, buildings/uruk.yaml, are left out)

ROOT = os.path.join(HERE, "..", "..")
PLAN = os.path.join(ROOT, "tools", "data", "uruk_city.json")
HEIGHT = os.path.join(ROOT, "media", "terrain", "uruk_height.png")
EXTENT = 6000.0

Z.MATERIALS.update({
    "cone_wall": ("cone_wall.jpg", (1, 1, 1), 0.95, 0.0, 2.4),
    "earth": (None, (0.20, 0.17, 0.11), 1.0, 0.0, 1.0),   # linear: beaten earth must match the lit steppe, whose textures are about 0.15 linear; 0.56 drew pale patches
    "dust": (None, (0.23, 0.19, 0.13), 1.0, 0.0, 1.0),
    "straw": (None, (0.76, 0.62, 0.32), 1.0, 0.0, 1.0),
    "clay": (None, (0.60, 0.33, 0.20), 0.9, 0.0, 1.0),
    "wood": (None, (0.34, 0.23, 0.13), 0.95, 0.0, 1.0),
    "charcoal": (None, (0.04, 0.04, 0.045), 1.0, 0.0, 1.0),
    "copper": (None, (0.72, 0.40, 0.22), 0.45, 0.85, 1.0),
    "iron": (None, (0.16, 0.16, 0.18), 0.5, 0.7, 1.0),
    "embers": (None, (0.95, 0.32, 0.06), 0.6, 0.0, 1.0),
    "water": (None, (0.10, 0.20, 0.25), 0.2, 0.0, 1.0),
    "wool": (None, (0.90, 0.88, 0.82), 1.0, 0.0, 1.0),
    "hide": (None, (0.42, 0.27, 0.16), 1.0, 0.0, 1.0),
    "grass": (None, (0.30, 0.42, 0.16), 1.0, 0.0, 1.0),
    "canal": (None, (0.16, 0.30, 0.34), 0.15, 0.0, 1.0),
    "crop": ("crop_rows.jpg", (1, 1, 1), 1.0, 0.0, 8.0),
    "plowed": ("plowed.jpg", (1, 1, 1), 1.0, 0.0, 8.0),
    "cloth0": (None, (0.74, 0.16, 0.11), 0.95, 0.0, 1.0),
    "cloth1": (None, (0.17, 0.42, 0.24), 0.95, 0.0, 1.0),
    "cloth2": (None, (0.13, 0.48, 0.52), 0.95, 0.0, 1.0),
    "cloth3": (None, (0.84, 0.58, 0.18), 0.95, 0.0, 1.0),
    "cloth4": (None, (0.92, 0.90, 0.84), 0.95, 0.0, 1.0),
    "cloth5": (None, (0.18, 0.28, 0.58), 0.95, 0.0, 1.0),
    "cloth6": (None, (0.80, 0.30, 0.20), 0.95, 0.0, 1.0),
})
CLOTHS = ["cloth%d" % i for i in range(7)]


# ---------------------------------------------------------------- terrain

def read_png16(path):
    """A 16-bit greyscale PNG as rows of ints (the terrain files of the datadisk)."""
    with open(path, "rb") as handle:
        data = handle.read()
    pos = 8
    idat = b""
    width = height = None
    while pos < len(data):
        n, = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 16 or colour != 0 or interlace != 0:
                raise SystemExit("only 16-bit greyscale PNG files without interlacing")
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    raw = zlib.decompress(idat)
    stride = width * 2
    rows = []
    prev = bytearray(stride)
    p = 0
    for _ in range(height):
        f = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        if f == 1:
            for i in range(2, stride):
                line[i] = (line[i] + line[i - 2]) & 255
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                left = line[i - 2] if i >= 2 else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - 2] if i >= 2 else 0
                b = prev[i]
                c = prev[i - 2] if i >= 2 else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(line)
        prev = line
    return [list(struct.unpack(">%dH" % width, bytes(r))) for r in rows]


class Ground:
    def __init__(self):
        self.h = read_png16(HEIGHT)
        self.n = len(self.h)
        self.step = EXTENT / self.n
        self.cache = {}

    def height(self, x, z):
        r = z / self.step + (self.n - 1) / 2.0
        c = x / self.step + (self.n - 1) / 2.0
        r = min(max(r, 0.0), self.n - 1.001)
        c = min(max(c, 0.0), self.n - 1.001)
        r0, c0 = int(r), int(c)
        fr, fc = r - r0, c - c0
        g = self.h
        v = (g[r0][c0] * (1 - fc) + g[r0][c0 + 1] * fc) * (1 - fr) + (g[r0 + 1][c0] * (1 - fc) + g[r0 + 1][c0 + 1] * fc) * fr
        return (v - 32768.0) / 10.0


# ---------------------------------------------------------------- model helpers

class CM(Z.Model):
    """A model whose faces can carry a colour tint (vertex colour) on top of the weathering of Z.Model."""

    def __init__(self):
        super().__init__()
        self.tint = (1.0, 1.0, 1.0)

    def face(self, pts, mat, uvs, outward=None):
        f = super().face(pts, mat, uvs, outward)
        r, g, b = self.tint
        for loop in f.loops:
            # a mild darkening at the foot of a wall, the brightness of the piece, and the tint of the colour of the wall
            v = (0.88 + 0.12 * min(1.0, max(0.0, loop.vert.co.z) / 3.0)) * self.jitter
            loop[self.col] = (min(1.0, v * r), min(1.0, v * g), min(1.0, v * b), 1.0)
        return f


class Ctx:
    """Builds in the planner's frame (x east, z south) into a model whose origin is (ox, oz)."""

    def __init__(self, model, origin, ground):
        self.m = model
        self.ox, self.oz = origin
        self.g = ground
        self.h0 = ground.height(self.ox, self.oz)

    def V(self, x, z, h):
        return Vector((x - self.ox, -(z - self.oz), h))

    def H(self, x, z):
        return self.g.height(x, z) - self.h0

    @staticmethod
    def D(dx, dz):
        return Vector((dx, -dz, 0.0))

    def wall(self, mat, a, b, z0, z1, out, off=0.0):
        pts = [self.V(a[0], a[1], z0), self.V(b[0], b[1], z0), self.V(b[0], b[1], z1), self.V(a[0], a[1], z1)]
        d = Vector((b[0] - a[0], -(b[1] - a[1])))
        if d.length < 1e-6:
            return
        self.m.wall(pts, mat, d.normalized(), off, self.D(*out))

    def top(self, mat, pts, h, off=(0.0, 0.0)):
        self.m.top([self.V(p[0], p[1], h) for p in pts], mat, off)

    def quad(self, mat, pts3, out, uvs=((0, 0), (1, 0), (1, 1), (0, 1))):
        """A free quad or triangle given as (x, z, h) points."""
        self.m.face([self.V(*p) for p in pts3], mat, list(uvs)[:len(pts3)], self.D(*out) if len(out) == 2 else Vector(out))

    def prism(self, mat_wall, mat_top, corners, z0, z1, off=0.0):
        """Walls and top of a convex polygon (planner frame points), heights relative to the model origin."""
        n = len(corners)
        for i in range(n):
            a, b = corners[i], corners[(i + 1) % n]
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            cx = sum(p[0] for p in corners) / n
            cz = sum(p[1] for p in corners) / n
            out = (mid[0] - cx, mid[1] - cz)
            self.wall(mat_wall, a, b, z0, z1, out, off + i * 3.1)
        if mat_top:
            self.top(mat_top, corners, z1)

    def box(self, mat_wall, mat_top, c, e1, e2, w, d, z0, z1, off=0.0):
        """An oriented box (w along e1, d along e2) centred at c, without a bottom."""
        corners = [(c[0] + e1[0] * a + e2[0] * b, c[1] + e1[1] * a + e2[1] * b)
                   for a, b in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
        self.prism(mat_wall, mat_top, corners, z0, z1, off)
        return corners


def rotated(c, e1, e2, a, b):
    return (c[0] + e1[0] * a + e2[0] * b, c[1] + e1[1] * a + e2[1] * b)


class Collision:
    """A lean mesh of boxes and prisms for the server: shared vertices, no materials."""

    def __init__(self, origin, ground):
        self.ox, self.oz = origin
        self.g = ground
        self.h0 = ground.height(*origin)
        self.verts = []
        self.faces = []

    def H(self, x, z):
        return self.g.height(x, z) - self.h0

    def prism(self, corners, z0, z1, top=True):
        base = len(self.verts)
        n = len(corners)
        for z in (z0, z1):
            for x, y in corners:
                self.verts.append((x - self.ox, -(y - self.oz), z))
        for i in range(n):
            j = (i + 1) % n
            self.faces.append((base + i, base + j, base + n + j, base + n + i))
        if top:
            self.faces.append(tuple(base + n + i for i in range(n)))

    def box(self, c, e1, e2, w, d, z0, z1):
        corners = [rotated(c, e1, e2, a, b) for a, b in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
        self.prism(corners, z0, z1)

    def export(self, path):
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        me = bpy.data.meshes.new("collision")
        me.from_pydata(self.verts, [], self.faces)
        me.update()
        obj = bpy.data.objects.new(os.path.splitext(os.path.basename(path))[0], me)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
                                  export_lights=False, export_cameras=False, export_animations=False, export_materials='NONE',
                                  export_normals=False)
        print("exported", path, os.path.getsize(path), "bytes", len(me.polygons), "faces")


# ---------------------------------------------------------------- houses

def unit(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n) if n > 1e-9 else (1.0, 0.0)


# wall colours: (material, tint). Mud brick is the darkest, plaster tinted with ochre gives the sand colour of the reference.
POOR = [("mudbrick", (0.95, 0.88, 0.76)), ("mudbrick", (1.0, 0.94, 0.84)), ("mudbrick", (0.82, 0.74, 0.64)),
        ("plaster", (1.0, 0.80, 0.55)), ("plaster", (0.98, 0.72, 0.50)), ("plaster", (0.90, 0.80, 0.68)), ("mudbrick", (0.9, 0.78, 0.66))]
MIDDLE = [("plaster", (1.0, 0.84, 0.60)), ("plaster", (1.0, 0.92, 0.78)), ("plaster", (1.0, 0.76, 0.62)), ("plaster", (0.95, 0.88, 0.70)),
          ("plaster", (1.0, 0.80, 0.50)), ("mudbrick", (1.0, 0.92, 0.82)), ("plaster", (0.88, 0.80, 0.72))]
RICH = [("plaster", (1.0, 0.98, 0.94)), ("plaster", (1.0, 0.94, 0.84)), ("plaster", (1.0, 0.86, 0.70)), ("bakedbrick", (1.0, 0.95, 0.9)),
        ("plaster", (0.98, 0.90, 0.80)), ("plaster", (1.0, 0.82, 0.62))]


def pick_walls(cls, rng):
    mat, tint = rng.choice((POOR, MIDDLE, RICH)[cls])
    j = rng.uniform(0.92, 1.04)
    return mat, tuple(min(1.0, c * j) for c in tint)


def teeth(ctx, mat, a, b, z, out, rng, size=0.9):
    """Pointed merlons along the edge a-b (the horned parapet of the poor houses), single triangles in the plane of the wall."""
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(2, int(d / (size * 1.2)))
    t = ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
    for k in range(n):
        s0 = (k + 0.12) / n * d
        s1 = (k + 0.88) / n * d
        sm = (k + 0.5) / n * d
        p0 = (a[0] + t[0] * s0, a[1] + t[1] * s0)
        p1 = (a[0] + t[0] * s1, a[1] + t[1] * s1)
        pm = (a[0] + t[0] * sm, a[1] + t[1] * sm)
        hgt = size * rng.uniform(0.85, 1.15)
        ctx.quad(mat, [(p0[0], p0[1], z), (p1[0], p1[1], z), (pm[0], pm[1], z + hgt)], out, ((0, 0), (1, 0), (0.5, 1)))


def house(ctx, col, rec):
    x, z, fx, fz, w, d, cls, floors, h0, seed, smith = rec
    if smith:
        return smithy(ctx, col, rec)
    rng = random.Random(seed)
    f = (fx, fz)
    e = (-fz, fx)
    c = (x, z)
    mat, tint = pick_walls(cls, rng)
    ctx.m.tint = tint
    ctx.m.jitter = rng.uniform(0.9, 1.0)

    def P(a, b):
        return rotated(c, e, f, a, b)

    corners = [P(-w / 2, -d / 2), P(w / 2, -d / 2), P(w / 2, d / 2), P(-w / 2, d / 2)]
    gs = [ctx.H(*p) for p in corners]
    zb = min(gs) - 0.4
    zf = max(gs)
    zr = zf + h0
    lip = rng.choice((0.0, 0.35, 0.5, 0.6)) if cls == 0 else rng.choice((0.4, 0.55, 0.7))
    top_mat = "mudbrick"
    sides = [(0, 1, (-f[0], -f[1])), (1, 2, e), (2, 3, f), (3, 0, (-e[0], -e[1]))]
    off = rng.random() * 6.0
    for k, (i, j, out) in enumerate(sides):
        ctx.wall(mat, corners[i], corners[j], zb, zr + lip, out, off + k * 2.7)
    if cls >= 1:
        # a plinth of clay cones laid heads out, as the surviving foundations show; it stands 4 cm proud of the wall
        ph = zf + (0.7 if cls == 1 else 1.0)
        ctx.m.tint = (1.0, 1.0, 1.0)
        for k, (i, j, out) in enumerate(sides):
            n = math.hypot(*out) or 1.0
            sh = (out[0] / n * 0.04, out[1] / n * 0.04)
            a = (corners[i][0] + sh[0], corners[i][1] + sh[1])
            b = (corners[j][0] + sh[0], corners[j][1] + sh[1])
            ctx.wall("cone_wall", a, b, zb, ph, out, off + k * 1.3)
        ctx.m.tint = tint
    ctx.top(top_mat, corners, zr)
    roof_h = zr
    clutter_at = None
    # an upper floor, set back from the front and narrower
    if floors >= 2 and cls >= 1:
        inset = rng.uniform(0.5, 1.4)
        back_setback = rng.uniform(1.5, min(3.5, d * 0.3))
        a0, a1 = -w / 2 + inset, w / 2 - rng.uniform(0.4, 1.8)
        b0, b1 = -d / 2 + rng.uniform(0.0, 0.8), d / 2 - back_setback
        h1 = rng.uniform(2.8, 3.3) + (0.4 if cls == 2 else 0.0)
        up = [P(a0, b0), P(a1, b0), P(a1, b1), P(a0, b1)]
        usides = [(0, 1, (-f[0], -f[1])), (1, 2, e), (2, 3, f), (3, 0, (-e[0], -e[1]))]
        for k, (i, j, out) in enumerate(usides):
            ctx.wall(mat, up[i], up[j], zr, zr + h1 + lip, out, off + k * 1.9)
        ctx.top(top_mat, up, zr + h1)
        roof_h = zr + h1
        # small windows on the upper floor facing the street
        for q in range(rng.choice((2, 3))):
            wa = a0 + (q + 1) * (a1 - a0) / (4 if q >= 0 else 1)
            wa = a0 + (q + 0.5) * (a1 - a0) / 3.0
            p0 = P(wa - 0.22, b1 + 0.03)
            p1 = P(wa + 0.22, b1 + 0.03)
            ctx.quad("door", [(p0[0], p0[1], zr + 1.5), (p1[0], p1[1], zr + 1.5), (p1[0], p1[1], zr + 2.2), (p0[0], p0[1], zr + 2.2)], f)
        corners_top = up
        if cls == 2 and rng.random() < 0.55:
            # a painted red band under the parapet (bakedbrick) on the facade of the upper floor
            p0, p1 = P(a0, b1 + 0.04), P(a1, b1 + 0.04)
            ctx.m.tint = (1.0, 0.82, 0.76)
            ctx.quad("bakedbrick", [(p0[0], p0[1], zr + h1 - 0.55), (p1[0], p1[1], zr + h1 - 0.55), (p1[0], p1[1], zr + h1 + 0.1),
                                    (p0[0], p0[1], zr + h1 + 0.1)], f, ((0, 0), (3, 0), (3, 0.3), (0, 0.3)))
            ctx.m.tint = tint
    # the door: a dark opening, a lintel for the better houses
    door_w = rng.uniform(0.9, 1.1) if cls == 0 else rng.uniform(1.1, 1.5)
    door_h = rng.uniform(1.8, 2.1) if cls == 0 else rng.uniform(2.1, 2.6)
    da = rng.uniform(-w / 2 + door_w / 2 + 0.5, w / 2 - door_w / 2 - 0.5) if cls < 2 else rng.uniform(-0.8, 0.8)
    p0, p1 = P(da - door_w / 2, d / 2 + 0.03), P(da + door_w / 2, d / 2 + 0.03)
    ctx.quad("door", [(p0[0], p0[1], zf), (p1[0], p1[1], zf), (p1[0], p1[1], zf + door_h), (p0[0], p0[1], zf + door_h)], f)
    if cls >= 1:
        q0, q1 = P(da - door_w / 2 - 0.35, d / 2 + 0.05), P(da + door_w / 2 + 0.35, d / 2 + 0.05)
        ctx.m.tint = (1.0, 0.97, 0.9)
        ctx.quad("plaster", [(q0[0], q0[1], zf + door_h), (q1[0], q1[1], zf + door_h), (q1[0], q1[1], zf + door_h + 0.4),
                             (q0[0], q0[1], zf + door_h + 0.4)], f)
        ctx.m.tint = tint
    if cls == 0 and rng.random() < 0.45:
        wa = rng.choice((-1, 1)) * w * 0.28
        p0, p1 = P(wa - 0.17, d / 2 + 0.03), P(wa + 0.17, d / 2 + 0.03)
        ctx.quad("door", [(p0[0], p0[1], zf + 1.9), (p1[0], p1[1], zf + 1.9), (p1[0], p1[1], zf + 2.4), (p0[0], p0[1], zf + 2.4)], f)
    if cls >= 1:
        for q in range(2 if cls == 1 else 3):
            wa = (-1 if q % 2 else 1) * (w * 0.3 + q * 0.4)
            if abs(wa - da) < door_w / 2 + 0.7:
                continue
            p0, p1 = P(wa - 0.2, d / 2 + 0.03), P(wa + 0.2, d / 2 + 0.03)
            ctx.quad("door", [(p0[0], p0[1], zf + 1.7), (p1[0], p1[1], zf + 1.7), (p1[0], p1[1], zf + 2.5), (p0[0], p0[1], zf + 2.5)], f)
    # pilasters on the facades of rich houses
    if cls == 2:
        n = max(3, int(w / 3.2))
        ctx.m.tint = tuple(min(1.0, t * 1.02) for t in tint)
        for q in range(n):
            pa = -w / 2 + 1.2 + q * (w - 2.4) / max(1, n - 1)
            if abs(pa - da) < door_w / 2 + 1.0:
                continue
            ctx.box(mat, None, P(pa, d / 2 + 0.17), e, f, 0.55, 0.34, zf + 0.0, zr + 0.0)
        ctx.m.tint = tint
    # roof: light well, a stair house, clutter, teeth of the parapet
    top_pts = corners
    if cls >= 1 and rng.random() < 0.5:
        wa, wb = rng.uniform(-w * 0.2, w * 0.2), rng.uniform(-d * 0.25, d * 0.1)
        ww, wd = rng.uniform(1.4, 2.4), rng.uniform(1.4, 2.4)
        well = [P(wa - ww / 2, wb - wd / 2), P(wa + ww / 2, wb - wd / 2), P(wa + ww / 2, wb + wd / 2), P(wa - ww / 2, wb + wd / 2)]
        if floors < 2 or cls == 0:
            ctx.top("door", well, roof_h + 0.01)
            ctx.prism(top_mat, None, well, roof_h, roof_h + 0.3)
    if rng.random() < (0.22 if cls == 0 else 0.3):
        sa, sb = rng.choice((-1, 1)) * (w / 2 - 1.3), rng.choice((-1, 1)) * (d / 2 - 1.3)
        if floors < 2 or cls == 0:
            ctx.box(mat, top_mat, P(sa, sb), e, f, 1.8, 2.0, roof_h, roof_h + 2.1)
    if cls == 0 and rng.random() < 0.28:
        for k, (i, j, out) in enumerate(sides):
            teeth(ctx, mat, corners[i], corners[j], zr + lip, out, rng, size=rng.uniform(0.7, 1.0))
    if cls == 1 and rng.random() < 0.18:
        for k, (i, j, out) in enumerate(sides[:3:2]):
            teeth(ctx, mat, corners[i], corners[j], zr + lip, out, rng, size=0.8)
    ctx.m.tint = (1.0, 1.0, 1.0)
    ctx.m.jitter = 1.0
    top = zr + (h1 if floors >= 2 and cls >= 1 else 0.0) if False else None
    ceiling = (roof_h + lip + 2.2)
    col.prism(corners, zb - 0.3, ceiling)


def mound(ctx, centre, radius, z0, z1, mat, sides=8):
    """A cone, used for a charcoal kiln: the base sits on the ground, the tip is the flue."""
    for i in range(sides):
        a0 = 2 * math.pi * i / sides
        a1 = 2 * math.pi * (i + 1) / sides
        p0 = (centre[0] + math.cos(a0) * radius, centre[1] + math.sin(a0) * radius, z0)
        p1 = (centre[0] + math.cos(a1) * radius, centre[1] + math.sin(a1) * radius, z0)
        outward = ((p0[0] + p1[0]) / 2 - centre[0], (p0[1] + p1[1]) / 2 - centre[1])
        ctx.quad(mat, [p0, p1, (centre[0], centre[1], z1)], outward, ((0, 0), (1, 0), (0.5, 1)))


def smithy(ctx, col, rec):
    """A smith's workshop: three walls and a roof over the open front, a furnace for smelting copper, an anvil,
    sword moulds, a trough, a heap of charcoal, a charcoal kiln and a pile of wood."""
    x, z, fx, fz, w, d, cls, floors, h0, seed, smith = rec
    rng = random.Random(seed)
    f = (fx, fz)
    e = (-fz, fx)
    c = (x, z)
    mat, tint = rng.choice([("mudbrick", (0.85, 0.76, 0.66)), ("mudbrick", (0.78, 0.7, 0.62)), ("plaster", (0.9, 0.78, 0.62))])
    ctx.m.tint = tint
    ctx.m.jitter = rng.uniform(0.85, 0.95)

    def P(a, b):
        return rotated(c, e, f, a, b)

    corners = [P(-w / 2, -d / 2), P(w / 2, -d / 2), P(w / 2, d / 2), P(-w / 2, d / 2)]
    gs = [ctx.H(*p) for p in corners]
    zb, zf = min(gs) - 0.4, max(gs)
    hh = rng.uniform(3.4, 4.0)
    zr = zf + hh
    # back and side walls, the open front is dark inside
    ctx.wall(mat, corners[0], corners[1], zb, zr + 0.4, (-f[0], -f[1]))
    ctx.wall(mat, corners[1], corners[2], zb, zr + 0.4, e, 2.7)
    ctx.wall(mat, corners[3], corners[0], zb, zr + 0.4, (-e[0], -e[1]), 5.1)
    ctx.top("mudbrick", corners, zr)
    over = [P(-w / 2 - 0.3, d / 2), P(w / 2 + 0.3, d / 2), P(w / 2 + 0.3, d / 2 + 1.4), P(-w / 2 - 0.3, d / 2 + 1.4)]
    ctx.top("wood", over, zr - 0.1)
    for sx in (-1, 1):
        ctx.box("wood", None, P(sx * (w / 2 - 0.1), d / 2 + 1.2), e, f, 0.22, 0.22, zf, zr - 0.1)
    ctx.m.tint = (1.0, 1.0, 1.0)
    ctx.quad("door", [(*corners[3], zf), (*corners[2], zf), (*corners[2], zr - 0.1), (*corners[3], zr - 0.1)], (-f[0], -f[1]))
    # forge: a brick hearth under a chimney that stands out of the roof
    fa = rng.choice((-1, 1)) * (w / 2 - 1.5)
    hearth = P(fa, -d / 2 + 1.3)
    ctx.m.tint = (0.95, 0.7, 0.6)
    ctx.box("bakedbrick", None, hearth, e, f, 1.7, 1.5, zf, zf + 1.0)
    ctx.top("embers", [P(fa - 0.5, -d / 2 + 0.9), P(fa + 0.5, -d / 2 + 0.9), P(fa + 0.5, -d / 2 + 1.7), P(fa - 0.5, -d / 2 + 1.7)], zf + 1.02)
    ctx.box("bakedbrick", None, P(fa, -d / 2 + 0.7), e, f, 1.1, 1.0, zr, zr + 3.0)
    ctx.box("bakedbrick", "charcoal", P(fa, -d / 2 + 0.7), e, f, 1.5, 1.4, zr + 3.0, zr + 3.6)
    ctx.m.tint = (1.0, 1.0, 1.0)
    ctx.box("iron", None, P(-fa * 0.3, 0.2), e, f, 0.5, 0.35, zf + 0.5, zf + 0.78)
    ctx.box("wood", None, P(-fa * 0.3, 0.2), e, f, 0.45, 0.4, zf, zf + 0.5)
    ctx.box("wood", "water", P(-fa * 0.6, 1.5), e, f, 1.4, 0.7, zf, zf + 0.55)
    # crucible of copper on the hearth, and blades cooling in open moulds
    ctx.m.tint = (1.0, 0.85, 0.7)
    ctx.box("copper", "embers", P(fa, -d / 2 + 1.35), e, f, 0.55, 0.42, zf + 1.02, zf + 1.32)
    ctx.m.tint = (1.0, 1.0, 1.0)
    ctx.box("wood", None, P(0.2, 0.9), e, f, 1.8, 0.55, zf, zf + 0.7)
    for along in (-0.5, 0.05, 0.55):
        ctx.box("clay", None, P(along, 0.9), e, f, 0.22, 0.7, zf + 0.7, zf + 0.78)
        ctx.box("copper", None, P(along, 0.9), e, f, 0.06, 0.62, zf + 0.78, zf + 0.86)
    # charcoal heap and a yard in front
    hp = P(rng.uniform(-w / 2, w / 2) * 0.7, d / 2 + 2.6)
    r = rng.uniform(0.9, 1.4)
    ring = [(hp[0] + math.cos(a) * r, hp[1] + math.sin(a) * r) for a in (0, math.pi / 2, math.pi, 3 * math.pi / 2)]
    zg = ctx.H(*hp)
    for i in range(4):
        a, b = ring[i], ring[(i + 1) % 4]
        ctx.quad("charcoal", [(a[0], a[1], zg), (b[0], b[1], zg), (hp[0], hp[1], zg + 0.9)], ((a[0] + b[0]) / 2 - hp[0], (a[1] + b[1]) / 2 - hp[1]))
    # a charcoal kiln (a turf mound with a flue) and a stack of cordwood, in the yard in front of the open side
    side = 1 if fa < 0 else -1
    kiln = P(side * (w / 2 - 1.7), d / 2 + 2.3)
    kg = ctx.H(*kiln)
    ctx.m.tint = (0.85, 0.75, 0.6)
    mound(ctx, kiln, 1.15, kg, kg + 1.55, "earth")
    ctx.m.tint = (1.0, 1.0, 1.0)
    ctx.box("bakedbrick", "charcoal", kiln, e, f, 0.32, 0.32, kg + 1.4, kg + 1.95)
    woodp = P(-side * (w / 2 - 1.7), d / 2 + 2.1)
    wg = ctx.H(*woodp)
    for layer in range(4):
        ctx.box("wood", "wood", woodp, e, f, 2.1 - layer * 0.15, 0.85, wg + layer * 0.28, wg + (layer + 1) * 0.28)
    ctx.m.jitter = 1.0
    col.prism(corners, zb - 0.3, zr + 3.7 if False else zr + 0.5)
    col.box(P(fa, -d / 2 + 0.7), e, f, 1.1, 1.0, zr, zr + 3.2)


# ---------------------------------------------------------------- streets

def simplify(pts, tol):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    ab = (b[0] - a[0], b[1] - a[1])
    n = math.hypot(*ab)
    best, idx = -1.0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        if n < 1e-9:
            dd = math.hypot(p[0] - a[0], p[1] - a[1])
        else:
            dd = abs((p[0] - a[0]) * ab[1] - (p[1] - a[1]) * ab[0]) / n
        if dd > best:
            best, idx = dd, i
    if best <= tol:
        return [a, b]
    return simplify(pts[:idx + 1], tol)[:-1] + simplify(pts[idx:], tol)


def subdivide(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(math.ceil(d / step)))
        for k in range(1, n + 1):
            out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    return out


# Ribbons lie this far over the ground. It was 7-16 cm, which buried the ankles of every walker on a street (the server walks
# characters on the ground itself); the drawn ground follows the same height map within a centimetre or two.
LIFT = {"canalbank": 0.03, "canal": 0.06, "avenue": 0.06, "ring": 0.05, "way": 0.06, "street": 0.04, "wallroad": 0.04, "road": 0.035, "lane": 0.03, "alley": 0.025}
PAVED = {"avenue", "ring", "way"}


def ribbon(ctx, street, inside=None, rng=None):
    kind, width = street["kind"], street["width"]
    pts = simplify([tuple(p) for p in street["pts"]], 0.4)
    pts = subdivide(pts, 12.0)
    n = len(pts)
    if n < 2:
        return 0
    half = width / 2.0
    norm = []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        t = unit((b[0] - a[0], b[1] - a[1]))
        s0 = unit((pts[i][0] - a[0], pts[i][1] - a[1])) if i > 0 else t
        k = max(0.55, abs(t[0] * s0[0] + t[1] * s0[1]))
        norm.append(((-t[1], t[0]), 1.0 / k))
    left_pts, right_pts = [], []
    for p, (nr, k) in zip(pts, norm):
        left_pts.append((p[0] + nr[0] * half * k, p[1] + nr[1] * half * k))
        right_pts.append((p[0] - nr[0] * half * k, p[1] - nr[1] * half * k))
    lift = LIFT.get(kind, 0.08)
    mat = "paving" if kind in PAVED else {"canal": "canal", "canalbank": "grass"}.get(kind, "earth")
    tile = Z.tile("paving") if mat == "paving" else 1.0
    s = 0.0
    count = 0
    for i in range(n - 1):
        seg = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        mid = ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
        if inside is None or inside(mid):
            quad = [left_pts[i], left_pts[i + 1], right_pts[i + 1], right_pts[i]]
            hs = [ctx.H(*q) + lift for q in quad]
            pv = [ctx.V(q[0], q[1], h) for q, h in zip(quad, hs)]
            if mat == "paving":
                uvs = [(0, s / tile), (0, (s + seg) / tile), (width / tile, (s + seg) / tile), (width / tile, s / tile)]
            else:
                uvs = [(0, 0), (0, 1), (1, 1), (1, 0)]
            ctx.m.jitter = 0.86 + 0.14 * (hash((round(mid[0] / 7), round(mid[1] / 7))) % 100) / 100.0
            if mat == "paving":
                ctx.m.tint = (1.0, 0.92, 0.80)
            ctx.m.face(pv, mat, uvs, (0, 0, 1))
            ctx.m.tint = (1.0, 1.0, 1.0)
            ctx.m.jitter = 1.0
            count += 1
        s += seg
    return count


# ---------------------------------------------------------------- canals

CANAL_WATER_H = 0.30     # the water stands this far over the ground
CANAL_BANK_H = 0.62      # the crests of the banks
CANAL_STEP_M = 5.0


def street_grid(plan, cell=10.0):
    """Points along every street with the half width of the street, in a hash grid: where a canal passes under a street."""
    grid = {}
    for st in plan["streets"]:
        pts = subdivide([tuple(q) for q in st["pts"]], 3.0)
        for q in pts:
            grid.setdefault((int(q[0] // cell), int(q[1] // cell)), []).append((q[0], q[1], st["width"] / 2.0))
    return grid, cell


def under_street(grid_cell, p, reach=3.0):
    grid, cell = grid_cell
    cx, cz = int(p[0] // cell), int(p[1] // cell)
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            for x, z, hw in grid.get((cx + dx, cz + dz), ()):
                if math.hypot(p[0] - x, p[1] - z) < hw + reach:
                    return True
    return False


def canal(ctx, cn, grid_cell):
    """A water channel in 3D: banks of earth on both sides (flat crest, sloping sides) and the water between them, a little over the
    ground, so that the channel has a bed that can be seen from the side. Where a street crosses, the canal goes under it (culvert): no
    banks and no water there. Visual only, like the canals always were (the server's terrain has no water for them)."""
    pts = subdivide(simplify([tuple(p) for p in cn["pts"]], 0.4), CANAL_STEP_M)
    n = len(pts)
    if n < 2:
        return 0
    half = cn["width"] / 2.0
    # the cross-sections: lateral offset from the middle of the canal, height over the ground of the middle, outer toe on the ground
    profile = [(-(half + 1.9), None), (-(half + 0.95), CANAL_BANK_H), (-(half + 0.45), CANAL_BANK_H), (-half, CANAL_WATER_H),
               (half, CANAL_WATER_H), (half + 0.45, CANAL_BANK_H), (half + 0.95, CANAL_BANK_H), (half + 1.9, None)]
    rows = []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        t = unit((b[0] - a[0], b[1] - a[1]))
        nr = (-t[1], t[0])
        centre = ctx.H(*pts[i])
        row = []
        for u, h in profile:
            q = (pts[i][0] + nr[0] * u, pts[i][1] + nr[1] * u)
            z = ctx.H(*q) + 0.04 if h is None else centre + h
            row.append(ctx.V(q[0], q[1], z))
        rows.append(row)
    count = 0
    for i in range(n - 1):
        mid = ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
        if under_street(grid_cell, mid) or under_street(grid_cell, pts[i]) and under_street(grid_cell, pts[i + 1]):
            continue
        seg = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        ctx.m.jitter = 0.86 + 0.14 * (hash((round(mid[0] / 7), round(mid[1] / 7))) % 100) / 100.0
        for j in range(len(profile) - 1):
            mat = "canal" if j == 3 else ("dust" if j in (1, 5) else "earth")
            quad = [rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]]
            uvs = [(0, 0), (1, 0), (1, seg / 3.0), (0, seg / 3.0)]
            ctx.m.face(quad, mat, uvs, (0, 0, 1))
            count += 1
    ctx.m.jitter = 1.0
    return count


# ---------------------------------------------------------------- textures and export

GAIN = {"mudbrick": 1.5, "plaster": 1.25, "paving": 1.3, "bakedbrick": 1.2, "stonepaving": 1.3, "crop_rows": 1.2, "plowed": 1.2}


def recompress(res=512, quality=65):
    """Smaller textures for the city models: every quarter carries its own copy."""
    import tempfile
    folder = tempfile.mkdtemp(prefix="uruk_city_textures_")
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = quality
    for name in sorted(os.listdir(Z.TEXTURES)):
        if name.endswith(".jpg"):
            image = bpy.data.images.load(os.path.join(Z.TEXTURES, name))
            image.scale(res, res)
            gain = GAIN.get(name[:-4], 1.0)
            if gain != 1.0:
                # the walls of the city are lit by the game's sun with little ambient light: brighter albedo than the gate's
                import numpy as np
                px = np.empty(len(image.pixels), dtype=np.float32)
                image.pixels.foreach_get(px)
                px = px.reshape(-1, 4)
                px[:, :3] = np.clip(px[:, :3] * gain, 0.0, 1.0)
                image.pixels.foreach_set(px.ravel())
            image.save_render(os.path.join(folder, name), scene=scene)
            bpy.data.images.remove(image)
    return folder


_TEX = {}


def finish(model, path, quality=65, res=512):
    if "dir" not in _TEX:
        _TEX["dir"] = recompress(res, quality)
    Z.TEXTURES = _TEX["dir"]
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    me = bpy.data.meshes.new(os.path.splitext(os.path.basename(path))[0])
    model.bm.to_mesh(me)
    model.bm.free()
    for m in Z.materials_for(model):
        me.materials.append(m)
    if me.color_attributes:
        me.color_attributes.active_color = me.color_attributes[0]
        me.color_attributes.render_color_index = 0
    obj = bpy.data.objects.new(os.path.splitext(os.path.basename(path))[0], me)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_image_format="JPEG",
                              export_jpeg_quality=quality, export_yup=True, export_apply=False, export_lights=False,
                              export_cameras=False, export_animations=False, export_vertex_color='ACTIVE', export_all_vertex_colors=False)
    print("exported", path, os.path.getsize(path), "bytes", len(me.polygons), "faces", len(me.vertices), "vertices")
    # the images stay loaded: remove the materials so that the next model starts clean
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for img in list(bpy.data.images):
        bpy.data.images.remove(img)


# ---------------------------------------------------------------- one quarter

def build_district(plan, ground, dist, out_dir):
    a, b, c, d = dist["rect"]
    origin = tuple(dist["anchor"])
    model = CM()
    ctx = Ctx(model, origin, ground)
    col = Collision(origin, ground)

    def inside(p):
        return a <= p[0] < b and c <= p[1] < d

    count = {"houses": 0, "smithies": 0, "ribbons": 0, "stalls": 0}
    for s in plan["streets"]:
        count["ribbons"] += ribbon(ctx, s, inside)
    import uruk_sites as S
    grid_cell = street_grid(plan)
    count["canal_faces"] = 0
    for cn in plan.get("canals", []):
        mid = cn["pts"][len(cn["pts"]) // 2]
        if inside(mid):
            count["canal_faces"] += canal(ctx, cn, grid_cell)
    for fl in plan.get("fields", []):
        if inside(tuple(fl["c"])):
            S.field(ctx, fl)
            count["stalls"] += 0
    for rec in plan["houses"]:
        if kind_of(rec) != "orig":
            continue
        if inside((rec[0], rec[1])):
            house(ctx, col, rec)
            count["smithies" if rec[10] else "houses"] += 1
    for m in plan["markets"]:
        if m["name"] != "uruk_market" and inside(tuple(m["c"])):
            S.market(ctx, col, m, plan, small=True)
            count["stalls"] += len(m["stalls"])
    print(dist["id"], count)
    finish(model, os.path.join(out_dir, dist["id"] + ".glb"))
    col.export(os.path.join(out_dir, dist["id"] + "_collision.glb"))


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    which, out_dir = args[0], args[1]
    with open(PLAN) as handle:
        plan = json.load(handle)
    ground = Ground()
    import uruk_sites as S
    names = {d["id"]: d for d in plan["districts"]}
    todo = list(names) if which == "all" else which.split(",")
    sites = ["uruk_market", "uruk_palace", "sinkashid_palace", "ishtar_temple", "eanna_temple"]
    if which == "all":
        todo += sites
    for name in todo:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if name in names:
            build_district(plan, ground, names[name], out_dir)
        elif name in sites:
            S.build_site(plan, ground, name, out_dir, finish)
        else:
            raise SystemExit("unknown model " + name)


if __name__ == "__main__":
    main()
