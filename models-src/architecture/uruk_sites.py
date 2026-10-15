"""The sites of Uruk that have a model of their own: markets, the two palaces with their farm buildings, the ziggurat of
Ishtar and the paved court of the Eanna precinct. Used by uruk_city.py; see there for the frame the models are built in."""
import math
import os
import random

from mathutils import Vector

import uruk_city as C
import ziggurat as Z

PT = Z.tile("paving")     # metres of one repeat of the pavement texture (8 x 8 tiles of 30 cm)


def left(v):
    return (-v[1], v[0])


# ---------------------------------------------------------------- markets

def stall(ctx, col, s):
    rng = random.Random(s["seed"])
    f = tuple(s["front"])
    e = left(f)
    c = (s["x"], s["z"])
    g = ctx.H(*c)
    cloth = C.CLOTHS[s["awning"]]
    W, D = rng.uniform(3.0, 3.6), rng.uniform(2.4, 3.0)

    def P(a, b):
        return C.rotated(c, e, f, a, b)

    ctx.m.jitter = 1.0
    # table with a front cloth
    ctx.box("wood", "wood", P(0, 0.35), e, f, W - 0.5, 0.9, g, g + 0.85)
    for sx in (-1, 1):
        ctx.box("wood", None, P(sx * (W / 2 - 0.1), D / 2 - 0.1), e, f, 0.13, 0.13, g, g + 2.5)
    # the awning slopes down towards the back; striped cloth for one in seven
    hi, lo = g + 2.55, g + 2.05
    a0, a1, b0, b1 = -W / 2 - 0.15, W / 2 + 0.15, -D / 2 - 0.1, D / 2 + 0.25
    if s["awning"] == 6:
        strips = 6
        for k in range(strips):
            u0 = a0 + (a1 - a0) * k / strips
            u1 = a0 + (a1 - a0) * (k + 1) / strips
            mat = "cloth0" if k % 2 == 0 else "cloth4"
            ctx.quad(mat, [(*P(u0, b0), lo), (*P(u1, b0), lo), (*P(u1, b1), hi), (*P(u0, b1), hi)], (0, 0, 1))
    else:
        ctx.quad(cloth, [(*P(a0, b0), lo), (*P(a1, b0), lo), (*P(a1, b1), hi), (*P(a0, b1), hi)], (0, 0, 1))
    # the front edge hangs a little
    ctx.quad(cloth, [(*P(a0, b1), hi), (*P(a1, b1), hi), (*P(a1, b1), hi - 0.35), (*P(a0, b1), hi - 0.35)], f)
    # back and side cloth
    ctx.m.jitter = 0.8
    ctx.quad(cloth, [(*P(a0, b0), g + 0.2), (*P(a1, b0), g + 0.2), (*P(a1, b0), lo), (*P(a0, b0), lo)], (-f[0], -f[1]))
    ctx.m.jitter = 1.0
    # goods
    kind = s["goods"]
    top = g + 0.85
    for k in range(rng.randrange(3, 6)):
        a = rng.uniform(-W / 2 + 0.5, W / 2 - 0.5)
        b = 0.35 + rng.uniform(-0.25, 0.25)
        if kind == 0:
            ctx.box("clay", "clay", P(a, b), e, f, 0.32, 0.32, top, top + rng.uniform(0.3, 0.5))
        elif kind == 1:
            ctx.box("straw", "straw", P(a, b), e, f, 0.55, 0.45, top, top + 0.22)
        elif kind == 2:
            ctx.box(C.CLOTHS[rng.randrange(7)], C.CLOTHS[rng.randrange(7)], P(a, b), e, f, 0.5, 0.35, top, top + 0.28)
        elif kind == 3:
            ctx.box("hide", "hide", P(a, b), e, f, 0.45, 0.28, top, top + 0.16)
        elif kind == 4:
            ctx.box("straw", "wood", P(a, b), e, f, 0.4, 0.4, top, top + 0.3)
        else:
            ctx.box("clay", "clay", P(a, b), e, f, 0.3, 0.3, top, top + 0.4)
    if kind in (0, 5):
        for k in range(2):
            ctx.box("clay", "clay", P(rng.uniform(-W / 2, W / 2), -D / 2 + 0.3), e, f, 0.6, 0.6, g, g + 0.95)
    col.box(P(0, 0.35), e, f, W - 0.5, 0.9, g - 0.2, g + 1.0)


def well(ctx, col, c):
    g = ctx.H(*c)
    ring = [(c[0] + math.cos(a) * 1.3, c[1] + math.sin(a) * 1.3) for a in [i * math.pi / 4 for i in range(8)]]
    ctx.prism("bakedbrick", None, ring, g - 0.2, g + 1.0)
    ctx.top("water", [(c[0] + math.cos(a) * 1.0, c[1] + math.sin(a) * 1.0) for a in [i * math.pi / 4 for i in range(8)]], g + 0.55)
    for sx in (-1, 1):
        ctx.box("wood", None, (c[0] + sx * 1.1, c[1]), (1, 0), (0, 1), 0.14, 0.14, g, g + 2.1)
    ctx.box("wood", None, (c[0], c[1]), (1, 0), (0, 1), 2.4, 0.12, g + 2.0, g + 2.14)
    col.prism(ring, g - 0.4, g + 1.1)


def plaza(ctx, m, lift=0.16, cell=6.0):
    t = tuple(m["t"])
    n = left(t)
    w, d = m["w"], m["d"]
    c = tuple(m["c"])
    nu, nv = max(1, int(round(w / cell))), max(1, int(round(d / cell)))
    for i in range(nu):
        for j in range(nv):
            u0, u1 = -w / 2 + w * i / nu, -w / 2 + w * (i + 1) / nu
            v0, v1 = -d / 2 + d * j / nv, -d / 2 + d * (j + 1) / nv
            pts = [C.rotated(c, t, n, u0, v0), C.rotated(c, t, n, u1, v0), C.rotated(c, t, n, u1, v1), C.rotated(c, t, n, u0, v1)]
            pv = [ctx.V(p[0], p[1], ctx.H(*p) + lift) for p in pts]
            tile = Z.tile("paving")
            uvs = [((u0 + w / 2) / tile, (v0 + d / 2) / tile), ((u1 + w / 2) / tile, (v0 + d / 2) / tile),
                   ((u1 + w / 2) / tile, (v1 + d / 2) / tile), ((u0 + w / 2) / tile, (v1 + d / 2) / tile)]
            ctx.m.jitter = 0.93 + 0.07 * ((i * 7 + j * 13) % 5) / 4.0
            ctx.m.face(pv, "paving", uvs, (0, 0, 1))
    ctx.m.jitter = 1.0


def market(ctx, col, m, plan, small=False):
    plaza(ctx, m)
    for s in m["stalls"]:
        stall(ctx, col, s)
    well(ctx, col, tuple(m["well"]))


# ---------------------------------------------------------------- shared pieces

Z.MATERIALS["cones"] = ("cone_mosaic.jpg", (1, 1, 1), 0.9, 0.0, 2.4)
Z.MATERIALS["cone_wall"] = ("cone_wall.jpg", (1, 1, 1), 0.95, 0.0, 2.4)
Z.MATERIALS["leaf"] = (None, (0.22, 0.38, 0.14), 0.9, 0.0, 1.0)
Z.MATERIALS["limestone"] = ("plaster.jpg", (0.97, 0.95, 0.9), 0.9, 0.0, 5.0)


class Frame:
    """A site frame: u along t, v along n = left of t, both in the planner's plane."""

    def __init__(self, c, yaw_deg):
        self.c = tuple(c)
        a = math.radians(yaw_deg)
        self.t = (math.cos(a), math.sin(a))
        self.n = left(self.t)

    def W(self, u, v):
        return (self.c[0] + self.t[0] * u + self.n[0] * v, self.c[1] + self.t[1] * u + self.n[1] * v)

    def rect(self, u0, u1, v0, v1):
        return [self.W(u0, v0), self.W(u1, v0), self.W(u1, v1), self.W(u0, v1)]


def ground_range(ctx, pts):
    hs = [ctx.H(*p) for p in pts]
    return min(hs), max(hs)


def niche_run(ctx, a, b, z0, z1, out, mat, spacing=3.6, depth=0.5, ratio=0.55, off=0.0):
    """A wall edge a-b with pilasters and recessed panels (the pattern of the mud-brick walls)."""
    d = math.hypot(b[0] - a[0], b[1] - a[1])
    if d < 0.5:
        return
    n = max(1, int(round(d / spacing)))
    t = ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
    o = (out[0], out[1])
    ol = math.hypot(*o)
    o = (o[0] / ol, o[1] / ol)
    bay = d / n
    pw = bay * (1.0 - ratio)
    for k in range(n):
        s0 = k * bay
        p0 = (a[0] + t[0] * s0, a[1] + t[1] * s0)
        p1 = (a[0] + t[0] * (s0 + pw), a[1] + t[1] * (s0 + pw))
        p2 = (a[0] + t[0] * (s0 + bay), a[1] + t[1] * (s0 + bay))
        r1 = (p1[0] - o[0] * depth, p1[1] - o[1] * depth)
        r2 = (p2[0] - o[0] * depth, p2[1] - o[1] * depth)
        ctx.wall(mat, p0, p1, z0, z1, o, off + k * 0.37)
        ctx.wall(mat, p1, r1, z0, z1, (-t[0], -t[1]), 0.0)
        ctx.wall(mat, r1, r2, z0, z1, o, off + k * 0.37 + 0.2)
        ctx.wall(mat, r2, p2, z0, z1, (t[0], t[1]), 0.0)


def mass(ctx, col, fr, u0, u1, v0, v1, h, mat, tint=(1, 1, 1), top="plaster", niches=0.0, base=None, band=None, lip=0.5, extra=0.0):
    """A solid building mass of the frame: walls to the height h over the highest ground, flat roof with a lip; `niches`
    gives the spacing of the pilaster pattern on the outer walls (0: plain). Returns the roof height."""
    corners = fr.rect(u0, u1, v0, v1)
    lo, hi = ground_range(ctx, corners)
    z0 = lo - 0.5
    zr = hi + h
    ctx.m.tint = tint
    cx = sum(p[0] for p in corners) / 4
    cz = sum(p[1] for p in corners) / 4
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        out = ((a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cz)
        top_z = zr + lip
        if base:
            ctx.m.tint = (1.0, 0.9, 0.85)
            ctx.wall(base, a, b, z0, hi + 1.4, out, i * 1.7)
            ctx.m.tint = tint
            bottom = hi + 1.4
        else:
            bottom = z0
        zb = top_z - (1.3 if band else 0.0)
        if niches:
            niche_run(ctx, a, b, bottom, zb, out, mat, spacing=niches, off=i * 2.3)
        else:
            ctx.wall(mat, a, b, bottom, zb, out, i * 2.3)
        if band:
            ctx.m.tint = (1, 1, 1)
            ctx.wall(band, a, b, zb, top_z, out, i * 0.9)
            ctx.m.tint = tint
    ctx.top(top, corners, zr + extra)
    ctx.m.tint = (1, 1, 1)
    col.prism(corners, z0 - 0.3, zr + lip)
    return zr


def tree(ctx, x, z, rng, kind="fruit"):
    g = ctx.H(x, z)
    h = rng.uniform(3.4, 4.6)
    r = 0.22
    pts = [(x + math.cos(a) * r, z + math.sin(a) * r) for a in [i * math.pi / 2 for i in range(4)]]
    ctx.prism("trunk", None, pts, g, g + h * 0.55)
    # a round crown: a ring of triangles over a lower ring
    cz = g + h * 0.45
    for ring, (rad, hh) in enumerate(((2.0, 0.0), (1.5, 1.2))):
        pass
    rad = rng.uniform(1.8, 2.4)
    top = (x, z, cz + h * 0.6)
    sides = 7
    for i in range(sides):
        a0 = 2 * math.pi * i / sides
        a1 = 2 * math.pi * (i + 1) / sides
        p0 = (x + math.cos(a0) * rad, z + math.sin(a0) * rad, cz + h * 0.1)
        p1 = (x + math.cos(a1) * rad, z + math.sin(a1) * rad, cz + h * 0.1)
        mid = ((p0[0] + p1[0]) / 2 - x, (p0[1] + p1[1]) / 2 - z)
        ctx.quad("leaf", [p0, p1, top], (mid[0], mid[1], 0.6))
        ctx.quad("leaf", [p1, p0, (x, z, cz - 0.35)], (mid[0], mid[1], -0.4))


def palm(ctx, x, z, rng, height=None, base=None):
    """A light date palm: tapering trunk of two segments and seven arching fronds."""
    g = ctx.H(x, z) if base is None else base
    h = height or rng.uniform(6.5, 10.0)
    lean = (rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6))
    rings = [(g, 0.34, (0.0, 0.0)), (g + h * 0.5, 0.26, (lean[0] * 0.25, lean[1] * 0.25)), (g + h, 0.2, lean)]
    sides = 5
    prev = None
    for zz, r, (lx, lz) in rings:
        pts = [(x + lx + math.cos(a) * r, z + lz + math.sin(a) * r, zz) for a in [2 * math.pi * i / sides for i in range(sides)]]
        if prev:
            for i in range(sides):
                j = (i + 1) % sides
                mid = ((prev[i][0] + prev[j][0]) / 2 - x, (prev[i][1] + prev[j][1]) / 2 - z)
                ctx.quad("trunk", [prev[i], prev[j], pts[j], pts[i]], (mid[0], mid[1], 0.0))
        prev = pts
    top = (x + lean[0], z + lean[1], g + h)
    for i in range(7):
        a = 2 * math.pi * i / 7 + rng.uniform(-0.25, 0.25)
        d = (math.cos(a), math.sin(a))
        s = (-d[1], d[0])
        L = rng.uniform(3.6, 4.8)
        mid = (top[0] + d[0] * L * 0.5, top[1] + d[1] * L * 0.5, top[2] + 0.7)
        end = (top[0] + d[0] * L, top[1] + d[1] * L, top[2] - 0.9)
        w = 0.55
        ctx.quad("frond", [(top[0] - s[0] * 0.08, top[1] - s[1] * 0.08, top[2]), (top[0] + s[0] * 0.08, top[1] + s[1] * 0.08, top[2]),
                           (mid[0] + s[0] * w, mid[1] + s[1] * w, mid[2]), (mid[0] - s[0] * w, mid[1] - s[1] * w, mid[2])], (0, 0, 1))
        ctx.quad("frond", [(mid[0] - s[0] * w, mid[1] - s[1] * w, mid[2]), (mid[0] + s[0] * w, mid[1] + s[1] * w, mid[2]),
                           (end[0] + s[0] * 0.05, end[1] + s[1] * 0.05, end[2]), (end[0] - s[0] * 0.05, end[1] - s[1] * 0.05, end[2])], (0, 0, 1))


def cone_roof(ctx, c, r, z0, z1, mat, sides=12, tint=None):
    for i in range(sides):
        a0 = 2 * math.pi * i / sides
        a1 = 2 * math.pi * (i + 1) / sides
        p0 = (c[0] + math.cos(a0) * r, c[1] + math.sin(a0) * r, z0)
        p1 = (c[0] + math.cos(a1) * r, c[1] + math.sin(a1) * r, z0)
        mid = ((p0[0] + p1[0]) / 2 - c[0], (p0[1] + p1[1]) / 2 - c[1], 0.7)
        ctx.quad(mat, [p0, p1, (c[0], c[1], z1)], mid, ((0, 0), (1, 0), (0.5, 1)))


def round_building(ctx, col, c, r, h, mat, cap, rng, sides=12):
    g0, g1 = ground_range(ctx, [(c[0] + math.cos(a) * r, c[1] + math.sin(a) * r) for a in [i * math.pi / 2 for i in range(4)]])
    ring = [(c[0] + math.cos(2 * math.pi * i / sides) * r, c[1] + math.sin(2 * math.pi * i / sides) * r) for i in range(sides)]
    ctx.prism(mat, None, ring, g0 - 0.4, g1 + h)
    cone_roof(ctx, c, r + 0.25, g1 + h, g1 + h + rng.uniform(2.0, 2.8), cap, sides)
    ctx.quad("door", [(c[0] + r * 0.98, c[1] - 0.4, g1), (c[0] + r * 0.98, c[1] + 0.4, g1), (c[0] + r * 0.98, c[1] + 0.4, g1 + 1.7), (c[0] + r * 0.98, c[1] - 0.4, g1 + 1.7)], (1, 0))
    col.prism(ring, g0 - 0.5, g1 + h)


def fence(ctx, corners, h=1.1):
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        cx = sum(p[0] for p in corners) / 4
        cz = sum(p[1] for p in corners) / 4
        ctx.wall("wood", a, b, min(ctx.H(*a), ctx.H(*b)) - 0.1, max(ctx.H(*a), ctx.H(*b)) + h, ((a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cz), i * 1.3)


def animal(ctx, c, f, kind, rng):
    e = left(f)
    g = ctx.H(*c)
    if kind == "cattle":
        body, h, w, d, mat = (1.5, 0.55, 1.0), 0.65, 0.55, 1.5, "hide"
    elif kind == "goats":
        body, h, w, d, mat = (0.9, 0.35, 0.7), 0.45, 0.35, 0.8, "hide"
    else:
        body, h, w, d, mat = (0.9, 0.4, 0.7), 0.45, 0.4, 0.9, "wool"
    ctx.box(mat, mat, c, e, f, w, d, g + h * 0.6, g + h + 0.35)
    for sx in (-1, 1):
        for sy in (-1, 1):
            ctx.box("wood", None, C.rotated(c, e, f, sx * w * 0.35, sy * d * 0.35), e, f, 0.1, 0.1, g, g + h * 0.6)
    ctx.box(mat, mat, C.rotated(c, e, f, 0, d * 0.6), e, f, w * 0.5, 0.35, g + h * 0.8, g + h + 0.35)


def pen(ctx, col, fr, it, rng):
    c = fr.W(it["u"], it["v"])
    t, n = fr.t, fr.n
    corners = [C.rotated(c, t, n, a, b) for a, b in ((-it["w"] / 2, -it["d"] / 2), (it["w"] / 2, -it["d"] / 2), (it["w"] / 2, it["d"] / 2),
                                                   (-it["w"] / 2, it["d"] / 2))]
    fence(ctx, corners, it["h"])
    for k in range(rng.randrange(4, 8)):
        a = rng.uniform(-it["w"] / 2 + 1.5, it["w"] / 2 - 1.5)
        b = rng.uniform(-it["d"] / 2 + 1.5, it["d"] / 2 - 1.5)
        ang = rng.uniform(0, 2 * math.pi)
        animal(ctx, C.rotated(c, t, n, a, b), (math.cos(ang), math.sin(ang)), it.get("animals", "sheep"), rng)


def threshing(ctx, c, r):
    g = ctx.H(*c)
    ring = [(c[0] + math.cos(2 * math.pi * i / 14) * r, c[1] + math.sin(2 * math.pi * i / 14) * r) for i in range(14)]
    ctx.top("straw", ring, g + 0.1)


def haystack(ctx, c, r, h):
    g = ctx.H(*c)
    cone_roof(ctx, c, r, g, g + h, "straw", 8)


def shed(ctx, col, fr, it, kind, rng, pw_half):
    """Farm and working buildings of the palace: flat-roofed blocks that face the palace or the forecourt."""
    c = fr.W(it["u"], it["v"])
    if abs(it["u"]) > pw_half and kind not in ("stable", "gatehouse"):
        f = (-fr.t[0], -fr.t[1]) if it["u"] > 0 else fr.t
    else:
        f = (-fr.n[0], -fr.n[1])
    e = left(f)
    w, d, h = it["w"], it["d"], it["h"]
    if kind == "workshop":
        smith_rec = [c[0], c[1], f[0], f[1], min(w, 11.0), min(d, 10.0), 1, 1, h, it["seed"], 1]
        C.smithy(ctx, col, smith_rec)
        return
    tints = [("mudbrick", (0.9, 0.82, 0.72)), ("plaster", (1.0, 0.84, 0.62)), ("mudbrick", (0.82, 0.74, 0.64))]
    mat, tint = rng.choice(tints)
    ctx.m.tint = tint
    corners = [C.rotated(c, e, f, a, b) for a, b in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))]
    lo, hi = ground_range(ctx, corners)
    zr = hi + h
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        out = [(0, 0), (e[0], e[1]), f, (-e[0], -e[1])][i]
        out = ((-f[0], -f[1]), e, f, (-e[0], -e[1]))[i]
        ctx.wall(mat, a, b, lo - 0.4, zr + 0.5, out, i * 1.9)
    ctx.top("mudbrick", corners, zr)
    ctx.m.tint = (1, 1, 1)
    # a wide doorway; the open front of a stable is dark
    if kind == "stable":
        p0, p1 = C.rotated(c, e, f, -w * 0.35, d / 2 + 0.04), C.rotated(c, e, f, w * 0.35, d / 2 + 0.04)
        ctx.quad("door", [(*p0, hi), (*p1, hi), (*p1, hi + h * 0.75), (*p0, hi + h * 0.75)], f)
    else:
        da = rng.uniform(-w * 0.25, w * 0.25)
        p0, p1 = C.rotated(c, e, f, da - 0.8, d / 2 + 0.04), C.rotated(c, e, f, da + 0.8, d / 2 + 0.04)
        ctx.quad("door", [(*p0, hi), (*p1, hi), (*p1, hi + 2.2), (*p0, hi + 2.2)], f)
    if kind in ("kitchen", "bakery", "brewery"):
        ctx.m.tint = (0.95, 0.72, 0.6)
        cc = C.rotated(c, e, f, rng.choice((-1, 1)) * (w / 2 - 1.2), -d / 4)
        ctx.box("bakedbrick", "charcoal", cc, e, f, 1.1, 1.1, zr, zr + rng.uniform(2.2, 3.4))
        ctx.m.tint = (1, 1, 1)
    col.prism(corners, lo - 0.5, zr + 0.5)


# ---------------------------------------------------------------- the palaces

def royal_palace(ctx, col, fr, it, rng):
    """The palace of Gilgamesh: four wings round a courtyard, the throne hall on the far side with a portico of six
    columns, corner towers, whitewashed walls over a baked-brick plinth, a frieze of clay-cone mosaic under the roof."""
    pw, pd = it["w"], it["d"]
    pv = it["v"]
    cw, cd = it["court"]
    wall = ("plaster", (1.0, 0.94, 0.84))
    v0, v1 = pv - pd / 2, pv + pd / 2
    u0, u1 = -pw / 2, pw / 2
    cu0, cu1 = -cw / 2, cw / 2
    cv0, cv1 = pv - cd / 2, pv + cd / 2
    gate = 3.6
    # south wing (the front) with the gateway, east and west wings, the throne hall in the north
    mass(ctx, col, fr, u0, -gate, v0, cv0, 7.0, *wall, niches=3.4, base="bakedbrick", band="cones")
    mass(ctx, col, fr, gate, u1, v0, cv0, 7.0, *wall, niches=3.4, base="bakedbrick", band="cones")
    # the lintel over the gateway
    corners = fr.rect(-gate, gate, v0, cv0)
    lo, hi = ground_range(ctx, corners)
    ctx.m.tint = wall[1]
    ctx.prism("plaster", "plaster", corners, hi + 4.6, hi + 7.5)
    ctx.m.tint = (1, 1, 1)
    col.prism(corners, hi + 4.6, hi + 7.5)
    mass(ctx, col, fr, u0, cu0, cv0, cv1, 7.0, *wall, niches=3.4, base="bakedbrick", band="cones")
    mass(ctx, col, fr, cu1, u1, cv0, cv1, 7.0, *wall, niches=3.4, base="bakedbrick", band="cones")
    zt = mass(ctx, col, fr, u0, u1, cv1, v1, 10.0, *wall, niches=3.4, base="bakedbrick", band="cones", extra=0.0)
    # the portico: six columns in front of the throne hall, a slab on top
    g = ctx.H(*fr.W(0, cv1))
    for k in range(6):
        u = -10.0 + k * 4.0
        cc = fr.W(u, cv1 - 1.4)
        ring = [(cc[0] + math.cos(a) * 0.45, cc[1] + math.sin(a) * 0.45) for a in [i * math.pi / 3 for i in range(6)]]
        ctx.prism("plaster", None, ring, g, g + 5.6)
    ctx.m.tint = (1.0, 0.9, 0.8)
    ctx.prism("bakedbrick", "bakedbrick", fr.rect(-12.5, 12.5, cv1 - 3.0, cv1), g + 5.6, g + 6.3)
    ctx.m.tint = (1, 1, 1)
    # the courtyard floor
    cell = 6.0
    for i in range(int(cw / cell)):
        for j in range(int(cd / cell)):
            a0, a1 = cu0 + i * cell, cu0 + (i + 1) * cell
            b0, b1 = cv0 + j * cell, cv0 + (j + 1) * cell
            pts = fr.rect(a0, a1, b0, b1)
            ctx.m.face([ctx.V(p[0], p[1], ctx.H(*p) + 0.08) for p in pts], "paving",
                       [(a0 / PT, b0 / PT), (a1 / PT, b0 / PT), (a1 / PT, b1 / PT), (a0 / PT, b1 / PT)], (0, 0, 1))
    # corner towers
    for su in (-1, 1):
        for sv in (v0 + 1.0, v1 - 1.0):
            mass(ctx, col, fr, su * (pw / 2 - 1.0) - 4.5, su * (pw / 2 - 1.0) + 4.5, sv - 4.5, sv + 4.5, 12.0, "plaster", (1.0, 0.92, 0.8),
                 base="bakedbrick", band="cones")
    # an altar and a basin in the courtyard, off the middle where the people stand
    ctx.m.tint = (1, 0.95, 0.88)
    ctx.box("plaster", "plaster", fr.W(cw / 2 - 4.0, pv + 3.0), fr.t, fr.n, 2.4, 1.6, ctx.H(*fr.W(cw / 2 - 4.0, pv + 3.0)), ctx.H(*fr.W(cw / 2 - 4.0, pv + 3.0)) + 1.0)
    ctx.m.tint = (1, 1, 1)


def sinkashid_palace(ctx, col, fr, it, rng):
    """The palace of Sin-kashid after the excavation: a low mud-brick rectangle of 142 by 109 m on a baked-brick base, a
    wall with niches round it, a gate between small towers in the front, rooms in the west half and round the sides, the
    large courtyard in the east half, a hall with six columns, small blocks standing out of the flat roof."""
    pw, pd = it["w"], it["d"]
    pv = it["v"]
    cu = it.get("court_u", 18.0)
    cw, cd = it["court"]
    v0, v1 = pv - pd / 2, pv + pd / 2
    u0, u1 = -pw / 2, pw / 2
    wall = ("mudbrick", (0.95, 0.88, 0.78))
    th = 7.0                      # the thick outer walls
    H = 6.2
    # the outer ring, each side a mass (the front has the gate at u = cu)
    gate = 4.0
    mass(ctx, col, fr, u0, cu - gate, v0, v0 + th, H, *wall, top="mudbrick", niches=3.6, base="bakedbrick")
    mass(ctx, col, fr, cu + gate, u1, v0, v0 + th, H, *wall, top="mudbrick", niches=3.6, base="bakedbrick")
    mass(ctx, col, fr, u0, u1, v1 - th, v1, H, *wall, top="mudbrick", niches=3.6, base="bakedbrick")
    mass(ctx, col, fr, u0, u0 + th, v0 + th, v1 - th, H, *wall, top="mudbrick", niches=3.6, base="bakedbrick")
    mass(ctx, col, fr, u1 - th, u1, v0 + th, v1 - th, H, *wall, top="mudbrick", niches=3.6, base="bakedbrick")
    # small towers flanking the gate
    for su in (-1, 1):
        mass(ctx, col, fr, cu + su * (gate + 3.5) - 3.5, cu + su * (gate + 3.5) + 3.5, v0 - 1.5, v0 + 6.0, 9.5, *wall, top="mudbrick",
             base="bakedbrick")
    # rooms in the west half, a block along the south and north of the court, the east strip
    c0, c1 = cu - cw / 2, cu + cw / 2
    cv0, cv1 = pv - cd / 2, pv + cd / 2
    blocks = [(u0 + th, c0 - 3.0, v0 + th, v1 - th, 5.4), (c0 - 3.0, c1, v0 + th, cv0, 5.0), (c0 - 3.0, c1, cv1, v1 - th, 5.0),
              (c1, u1 - th, v0 + th, v1 - th, 5.0)]
    for (a0, a1, b0, b1, h) in blocks:
        if a1 - a0 < 4 or b1 - b0 < 4:
            continue
        if a0 == c0 - 3.0 and b1 == cv0:      # the passage from the gate to the court stays open
            mass(ctx, col, fr, a0, cu - 3.0, b0, b1, h, *wall, top="mudbrick")
            mass(ctx, col, fr, cu + 3.0, a1, b0, b1, h, *wall, top="mudbrick")
        else:
            mass(ctx, col, fr, a0, a1, b0, b1, h, *wall, top="mudbrick")
    # light wells in the flat roof of the west rooms and small blocks (roof rooms) standing out of it
    for k in range(7):
        a = rng.uniform(u0 + th + 4.0, c0 - 8.0)
        b = rng.uniform(v0 + th + 5.0, v1 - th - 5.0)
        wc = fr.W(a, b)
        g = ctx.H(*wc)
        if k % 2 == 0:
            mass(ctx, col, fr, a - 4.0, a + 4.0, b - 3.5, b + 3.5, 8.2, "mudbrick", (0.95, 0.88, 0.78), top="mudbrick")
        else:
            ctx.top("door", fr.rect(a - 1.2, a + 1.2, b - 1.2, b + 1.2), g + 5.45)
    # the courtyard: paved, a basin, the hall of six columns on its west side
    cell = 6.0
    for i in range(int(cw / cell)):
        for j in range(int(cd / cell)):
            a0, a1 = c0 + i * cell, c0 + (i + 1) * cell
            b0, b1 = cv0 + j * cell, cv0 + (j + 1) * cell
            pts = fr.rect(a0, a1, b0, b1)
            ctx.m.face([ctx.V(p[0], p[1], ctx.H(*p) + 0.08) for p in pts], "paving",
                       [(a0 / PT, b0 / PT), (a1 / PT, b0 / PT), (a1 / PT, b1 / PT), (a0 / PT, b1 / PT)], (0, 0, 1))
    g = ctx.H(*fr.W(c0, pv))
    for k in range(6):
        cc = fr.W(c0 + 1.8, pv - 7.5 + k * 3.0)
        ring = [(cc[0] + math.cos(a) * 0.5, cc[1] + math.sin(a) * 0.5) for a in [i * math.pi / 3 for i in range(6)]]
        ctx.prism("mudbrick", None, ring, g, g + 4.4)
    ctx.prism("wood", "wood", fr.rect(c0, c0 + 3.6, pv - 9.5, pv + 9.5), g + 4.4, g + 4.9)
    # a pool of water in the middle of the court
    ctx.top("water", fr.rect(cu + 6.0, cu + 10.0, pv - 2.0, pv + 2.0), ctx.H(*fr.W(cu + 8, pv)) + 0.12)
    ctx.prism("bakedbrick", None, fr.rect(cu + 5.6, cu + 10.4, pv - 2.4, pv + 2.4), ctx.H(*fr.W(cu + 8, pv)) - 0.2, ctx.H(*fr.W(cu + 8, pv)) + 0.35)


def enclosure(ctx, col, fr, it, rng):
    """The wall round the farm buildings: 1.8 m thick, a gate between two towers in the middle of the front."""
    W, D, h = it["w"], it["d"], it["h"]
    gw = it.get("gate_w", 11.0)
    th = 1.8
    u0, u1, v0, v1 = -W / 2, W / 2, -D / 2, D / 2
    segs = [(u0, -gw / 2, v0, v0 + th), (gw / 2, u1, v0, v0 + th), (u0, u1, v1 - th, v1), (u0, u0 + th, v0, v1), (u1 - th, u1, v0, v1)]
    for (a0, a1, b0, b1) in segs:
        corners = fr.rect(a0, a1, b0, b1)
        lo, hi = ground_range(ctx, corners)
        ctx.m.tint = (0.92, 0.84, 0.72)
        cx = sum(p[0] for p in corners) / 4
        cz = sum(p[1] for p in corners) / 4
        for i in range(4):
            a, b = corners[i], corners[(i + 1) % 4]
            ctx.wall("mudbrick", a, b, lo - 0.5, hi + h, ((a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cz), i * 2.1)
        ctx.top("mudbrick", corners, hi + h)
        col.prism(corners, lo - 0.6, hi + h)
        # merlons along the top of the long walls
        long_u = (a1 - a0) > (b1 - b0)
        length_ = (a1 - a0) if long_u else (b1 - b0)
        count = int(length_ / 3.4)
        for k in range(count):
            f_ = (k + 0.5) / count
            cu_, cv_ = (a0 + (a1 - a0) * f_, (b0 + b1) / 2) if long_u else ((a0 + a1) / 2, b0 + (b1 - b0) * f_)
            cc = fr.W(cu_, cv_)
            ctx.box("mudbrick", "mudbrick", cc, fr.t, fr.n, 1.2 if long_u else th * 0.7, th * 0.7 if long_u else 1.2,
                    ctx.H(*cc) + h, ctx.H(*cc) + h + 0.9)
    ctx.m.tint = (1, 1, 1)
    for su in (-1, 1):
        mass(ctx, col, fr, su * (gw / 2 + 3.2) - 3.2, su * (gw / 2 + 3.2) + 3.2, v0 - 1.0, v0 + 5.4, h + 3.5, "mudbrick", (0.95, 0.86, 0.74),
             top="mudbrick", base="bakedbrick")


def build_palace(plan, ground, pal, out_dir, finish, base_name):
    anchor = tuple(pal["anchor"])
    model = C.CM()
    ctx = C.Ctx(model, anchor, ground)
    col = C.Collision(anchor, ground)
    fr = Frame(pal["c"], pal["yaw"])
    rng = random.Random(len(pal["name"]) * 977)
    pw_half = [it for it in pal["items"] if it["type"] == "palace"][0]["w"] / 2
    for it in pal["items"]:
        r = random.Random(it["seed"])
        kind = it["type"]
        c = fr.W(it["u"], it["v"])
        if kind == "palace":
            (royal_palace if it["variant"] == "royal" else sinkashid_palace)(ctx, col, fr, it, r)
        elif kind == "enclosure":
            enclosure(ctx, col, fr, it, r)
        elif kind in ("stable", "gatehouse", "kitchen", "bakery", "brewery", "workshop", "store", "storehouse", "barn"):
            shed(ctx, col, fr, it, kind, r, pw_half + 4.0)
        elif kind == "granary":
            round_building(ctx, col, c, it["w"] / 2, it["h"], "mudbrick", "straw", r)
        elif kind == "pen":
            pen(ctx, col, fr, it, r)
        elif kind == "threshing":
            threshing(ctx, c, it["w"] / 2)
        elif kind == "haystack":
            haystack(ctx, c, it["w"] / 2, it["h"])
        elif kind == "well":
            well(ctx, col, c)
        elif kind == "palm":
            palm(ctx, c[0], c[1], r, it["h"])
        elif kind == "garden":
            # the hanging garden: a stepped terrace planted with palms
            for k, (hh, inset) in enumerate(((2.6, 0.0), (5.4, 4.0))):
                mass(ctx, col, fr, it["u"] - it["w"] / 2 + inset, it["u"] + it["w"] / 2 - inset, it["v"] - it["d"] / 2 + inset * 0.3,
                     it["v"] + it["d"] / 2 - inset * 0.3, hh, "mudbrick", (0.92, 0.84, 0.72), top="grass", base="bakedbrick")
            for k in range(9):
                uu = it["u"] - it["w"] / 2 + 6 + k * (it["w"] - 12) / 8
                cc = fr.W(uu, it["v"] + r.uniform(-3, 3))
                palm(ctx, cc[0], cc[1], r, r.uniform(4.0, 6.5), base=ctx.H(*fr.W(it["u"], it["v"])) + 5.4)
        else:
            print("palace item not built:", kind)
    print(pal["name"], len(pal["items"]), "items")
    return model, col


# ---------------------------------------------------------------- the ziggurat of Ishtar

def ishtar_ziggurat_model(model, rng):
    """A stepped tower of three stages in the local frame (centre at the origin, the stairs facing -Y), a red temple on
    top; built like the Anu ziggurat of ziggurat.py with its three flights meeting on a landing."""
    from mathutils import Vector
    spec = [(44.0, 6.5, 0.06), (32.0, 5.5, 0.05), (22.0, 5.0, 0.05)]
    z = 0.0
    tops = []
    top_front = top_w = None
    for k, (w, h, batter) in enumerate(spec):
        inset = batter * h
        y_front = -w / 2 if k == 0 else top_front + 0.75 * (top_w - w)
        cy = y_front + w / 2
        pts = Z.outline(0.0, cy, w, w, 4.2, 1.8, 0.5)
        scale = (w - 2 * inset) / w
        Z.prism(model, pts, z, z + h, Vector((0.0, cy)), scale, "mudbrick", rng, cap_mat="plaster")
        t_w = w - 2 * inset
        t_front = y_front + inset
        Z.merlons(model, 0.0, cy, t_w / 2, z + h, rng, skip_front=7.0 if k == 0 else 5.0, spacing=2.6, mat="plaster")
        tops.append((z + h, 0.0, cy, t_w, t_front))
        top_front, top_w = t_front, t_w
        z += h
    rise = spec[0][1]
    front = -spec[0][0] / 2
    landing_front, landing_half = front - 3.0, 5.5
    wall_top_y = front + 0.06 * rise
    Z.box(model, 0.0, (landing_front + wall_top_y) / 2, 2 * landing_half, wall_top_y - landing_front, 0.0, rise, "mudbrick", "plaster", rng)
    Z.stairs(model, 0.0, landing_front - rise, (0, 1), 5.5, 0.0, rise, rise, rh=0.3)
    side_y = front - 1.5
    Z.stairs(model, -15.0, side_y, (1, 0), 3.0, 0.0, rise, 15.0 - landing_half, rh=0.3)
    Z.stairs(model, 15.0, side_y, (-1, 0), 3.0, 0.0, rise, 15.0 - landing_half, rh=0.3)
    zacc = rise
    for k in range(1, 3):
        w, h = spec[k][0], spec[k][1]
        zt, cx, cy_k, t_w, t_front = tops[k]
        y_front = cy_k - w / 2
        margin = y_front - tops[k - 1][4]
        run = min(h, margin - 1.2)
        Z.stairs(model, 0.0, y_front + 0.3 - run, (0, 1), 4.5, zacc, h, run, rh=0.3)
        zacc += h
    zt, cx, cy_k, t_w, t_front = tops[2]
    back = cy_k + t_w / 2
    yf = back - 2.2 - 11.0
    Z.temple(model, 0.0, yf, zt, 14.0, 11.0, 5.5, rng, body="bakedbrick", plinth_mat="plaster", gold=True, upper=False)
    # the roof of the shrine (the concave cap of the pilastered outline is not reliable once exported)
    model.top([Vector((-6.6, yf + 0.4, zt + 5.52)), Vector((6.6, yf + 0.4, zt + 5.52)), Vector((6.6, yf + 10.6, zt + 5.52)),
               Vector((-6.6, yf + 10.6, zt + 5.52))], "plaster")


def build_ishtar_ziggurat(plan, ground, origin, out_dir, finish):
    from mathutils import Vector
    z = plan["ishtar_ziggurat"]
    model = C.CM()
    ctx = C.Ctx(model, origin, ground)
    first = len(model.bm.verts)
    ishtar_ziggurat_model(model, random.Random(11))
    fx, fz = z["front"]
    # local -Y (the stairs) turns to the planner's front vector: Blender direction (fx, -fz)
    sin_t, cos_t = fx, fz
    cx, cz = z["c"]
    half = z["size"] / 2 + 3.0
    foot = [(cx + dx, cz + dz) for dx in (-half, half) for dz in (-half, half)] + [(cx, cz)]
    lo = min(ctx.H(*p) for p in foot)
    for v in list(model.bm.verts)[first:]:
        x, y = v.co.x, v.co.y
        v.co = Vector((cx - ctx.ox + x * cos_t - y * sin_t, -(cz - ctx.oz) + x * sin_t + y * cos_t, v.co.z + lo - 0.8))
    finish(model, os.path.join(out_dir, "uruk_ishtar_ziggurat.glb"))


# ---------------------------------------------------------------- the court of the Eanna precinct

def court_paving(ctx, plan, fr_blocks):
    poly = [tuple(p) for p in plan["precinct"]]
    anu = plan["anu"]
    ac = tuple(anu["c"])
    a = math.radians(anu["yaw_deg"])
    # the Anu terrace (52 m square turned like the survey) with its stairs to the front, and the Ishtar ziggurat
    at, an = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    iz = plan["ishtar_ziggurat"]
    izc = tuple(iz["c"])
    izf = tuple(iz["front"])

    def in_anu(p):
        d = (p[0] - ac[0], p[1] - ac[1])
        u = d[0] * at[0] + d[1] * at[1]
        v = d[0] * an[0] + d[1] * an[1]
        return abs(u) < 29.0 and -29.0 < v < 29.0 or (abs(u) < 5.0 and -40.0 < v < 29.0)

    def in_iz(p):
        d = (p[0] - izc[0], p[1] - izc[1])
        u = d[0] * izf[0] + d[1] * izf[1]
        v = d[0] * -izf[1] + d[1] * izf[0]
        return abs(v) < 24.0 and -23.0 < u < 24.0 or (abs(v) < 4.0 and u > 0 and u < 40.0 and False)

    cell = 5.0
    x0 = min(p[0] for p in poly)
    x1 = max(p[0] for p in poly)
    z0 = min(p[1] for p in poly)
    z1 = max(p[1] for p in poly)

    def inside(p):
        return C.__dict__.get("in_poly", None) and False

    def in_poly(p):
        x, zz = p
        res = False
        j = len(poly) - 1
        for i in range(len(poly)):
            xi, zi = poly[i]
            xj, zj = poly[j]
            if (zi > zz) != (zj > zz) and x < (xj - xi) * (zz - zi) / (zj - zi + 1e-12) + xi:
                res = not res
            j = i
        return res

    def clip(subject, clipper):
        """Sutherland-Hodgman: the part of a polygon inside a convex polygon (either orientation)."""
        area = sum(clipper[i][0] * clipper[(i + 1) % len(clipper)][1] - clipper[(i + 1) % len(clipper)][0] * clipper[i][1] for i in range(len(clipper)))
        sign = 1.0 if area > 0 else -1.0
        out = subject
        for i in range(len(clipper)):
            a_, b_ = clipper[i], clipper[(i + 1) % len(clipper)]
            inp, out = out, []
            if not inp:
                break

            def inside_(q):
                return sign * ((b_[0] - a_[0]) * (q[1] - a_[1]) - (b_[1] - a_[1]) * (q[0] - a_[0])) >= 0

            def cross(q1, q2):
                d1 = (b_[0] - a_[0]) * (q1[1] - a_[1]) - (b_[1] - a_[1]) * (q1[0] - a_[0])
                d2 = (b_[0] - a_[0]) * (q2[1] - a_[1]) - (b_[1] - a_[1]) * (q2[0] - a_[0])
                f = d1 / (d1 - d2)
                return (q1[0] + (q2[0] - q1[0]) * f, q1[1] + (q2[1] - q1[1]) * f)

            prev = inp[-1]
            for cur in inp:
                if inside_(cur):
                    if not inside_(prev):
                        out.append(cross(prev, cur))
                    out.append(cur)
                elif inside_(prev):
                    out.append(cross(prev, cur))
                prev = cur
        return out

    x = x0
    count = 0
    while x < x1:
        zz = z0
        while zz < z1:
            cell_pts = [(x, zz), (x + cell, zz), (x + cell, zz + cell), (x, zz + cell)]
            mid = (x + cell / 2, zz + cell / 2)
            if not (in_anu(mid) or in_iz(mid)) and not any(fr["inside"](mid) for fr in fr_blocks):
                pts = cell_pts if all(in_poly(p) for p in cell_pts) else clip(cell_pts, poly)
                if len(pts) >= 3 and not any(in_anu(p) and in_anu((p[0] * 0.9 + mid[0] * 0.1, p[1] * 0.9 + mid[1] * 0.1)) for p in pts[:1]):
                    tile = PT       # the pavement of Uruk: square tiles of 30 cm (make_paving.py), like the streets
                    ctx.m.jitter = 0.9 + 0.1 * (((int(x) // 5) * 7 + (int(zz) // 5) * 13) % 5) / 4
                    ctx.m.tint = (1.0, 0.92, 0.80)
                    ctx.m.face([ctx.V(p[0], p[1], ctx.H(*p) + 0.25) for p in pts], "paving",
                               [(p[0] / tile, p[1] / tile) for p in pts], (0, 0, 1))
                    count += 1
            zz += cell
        x += cell
    ctx.m.tint = (1.0, 1.0, 1.0)
    ctx.m.jitter = 1.0
    return count


def pillar_hall(ctx, col, b, rng):
    """A long hall with close pilasters along its walls, tall doorways under triangular niches, a band of clay-cone mosaic
    and a dark band under the flat roof, as the reconstruction of the pillar hall shows it."""
    fr = Frame(b["c"], b["yaw"])
    w, d, h = b["w"], b["d"], b["h"]
    corners = fr.rect(-w / 2, w / 2, -d / 2, d / 2)
    lo, hi = ground_range(ctx, corners)
    z0 = lo - 0.5
    zr = hi + h
    cx, cz = b["c"]
    ctx.m.tint = (1.0, 0.86, 0.62)
    for i in range(4):
        a, bb = corners[i], corners[(i + 1) % 4]
        out = ((a[0] + bb[0]) / 2 - cx, (a[1] + bb[1]) / 2 - cz)
        niche_run(ctx, a, bb, hi, zr - 1.4, out, "mudbrick", spacing=1.5, depth=0.3, ratio=0.45, off=i)
        ctx.wall("mudbrick", a, bb, z0, hi, out)
        ctx.m.tint = (1, 1, 1)
        ctx.wall("cones", a, bb, zr - 1.4, zr - 0.5, out, i * 0.5)
        ctx.m.tint = (0.3, 0.25, 0.2)
        ctx.wall("mudbrick", a, bb, zr - 0.5, zr + 0.4, out)
        ctx.m.tint = (1.0, 0.86, 0.62)
    ctx.top("mudbrick", corners, zr)
    ctx.m.tint = (1, 1, 1)
    # doorways on the two long sides, a dark opening with a triangular niche above it
    for side in (-1, 1):
        for k in range(4):
            u = -w / 2 + (k + 0.5) * w / 4
            p0, p1 = fr.W(u - 1.3, side * (d / 2 + 0.34)), fr.W(u + 1.3, side * (d / 2 + 0.34))
            out = (fr.n[0] * side, fr.n[1] * side)
            ctx.quad("door", [(*p0, hi), (*p1, hi), (*p1, hi + 4.2), (*p0, hi + 4.2)], out)
            m0, m1, m2 = fr.W(u - 0.9, side * (d / 2 + 0.34)), fr.W(u + 0.9, side * (d / 2 + 0.34)), fr.W(u, side * (d / 2 + 0.34))
            ctx.quad("door", [(*m0, hi + 4.5), (*m1, hi + 4.5), (*m2, hi + 5.8)], out, ((0, 0), (1, 0), (0.5, 1)))
    col.prism(corners, z0 - 0.3, zr + 0.4)


def stone_cone_building(ctx, col, b, rng):
    """The stone-cone building on a terrace: walls covered with the mosaic of black, white and red clay cones, a water basin
    in front, reed standards (flagpoles) beside the entrance."""
    fr = Frame(b["c"], b["yaw"])
    w, d, h = b["w"], b["d"], b["h"]
    tcorners = fr.rect(-w / 2 - 3.0, w / 2 + 3.0, -d / 2 - 3.0, d / 2 + 3.0)
    lo, hi = ground_range(ctx, tcorners)
    cx, cz = b["c"]
    ctx.m.tint = (0.95, 0.86, 0.74)
    for i in range(4):
        a, bb = tcorners[i], tcorners[(i + 1) % 4]
        ctx.wall("mudbrick", a, bb, lo - 0.5, hi + 1.0, ((a[0] + bb[0]) / 2 - cx, (a[1] + bb[1]) / 2 - cz), i)
    ctx.top("mudbrick", tcorners, hi + 1.0)
    ctx.m.tint = (1, 1, 1)
    col.prism(tcorners, lo - 0.6, hi + 1.0)
    corners = fr.rect(-w / 2, w / 2, -d / 2, d / 2)
    z0 = hi + 1.0
    for i in range(4):
        a, bb = corners[i], corners[(i + 1) % 4]
        ctx.wall("cones", a, bb, z0, z0 + h, ((a[0] + bb[0]) / 2 - cx, (a[1] + bb[1]) / 2 - cz), i * 0.7)
    ctx.top("plaster", corners, z0 + h)
    col.prism(corners, z0 - 0.2, z0 + h + 0.3)
    # the doorway and the basin
    p0, p1 = fr.W(-1.5, -d / 2 - 0.05), fr.W(1.5, -d / 2 - 0.05)
    ctx.quad("door", [(*p0, z0), (*p1, z0), (*p1, z0 + 3.4), (*p0, z0 + 3.4)], (-fr.n[0], -fr.n[1]))
    ctx.prism("limestone", "water", fr.rect(-4.0, 4.0, -d / 2 - 2.8, -d / 2 - 0.4), hi, hi + 1.05)
    for k in range(3):
        cc = fr.W(-w / 2 + 3.0 + k * 3.5, -d / 2 - 2.0)
        ring = [(cc[0] + math.cos(a) * 0.18, cc[1] + math.sin(a) * 0.18) for a in [i * math.pi / 2 for i in range(4)]]
        ctx.prism("straw", None, ring, z0, z0 + 9.0)


# The plan of the Late Uruk temple of Eanna in cells of a 60 x 39 grid: walls as (c0, c1, r0, r1) of the northern half, the
# southern half is its mirror image about r = 19.5. A thick band of rooms and niches along each long side with three
# entrance passages through it, a hall across the west end and a long middle hall with chambers on both sides; the
# middle hall and the cross hall are open to the sky. Read by hand from the excavation plan (a layout, not a drawing).
TEMPLE_COLS, TEMPLE_ROWS = 60.0, 39.0
TEMPLE_NORTH = [
    # the band along the long side, notched for the entrances; the entrance passages are two cells wide
    (0, 12, 0, 8), (16, 28, 0, 8), (32, 44, 0, 8), (48, 60, 0, 8),
    (12, 13, 5, 8), (15, 16, 5, 8), (28, 29, 5, 8), (31, 32, 5, 8), (44, 45, 5, 8), (47, 48, 5, 8),
    # the west end: outer wall, the corner room and the wall of the entrance room (a doorway between them)
    (0, 2, 8, 16.5), (0, 4, 13, 15), (6, 10, 13, 15), (7, 10, 8, 13), (7, 10, 15, 16.5),
    # chambers along the middle hall: the wall towards the hall (doors at 34-36 and 48-49) and the partitions
    (18, 21, 8, 15), (22, 34, 13, 15), (36, 48, 13, 15), (23, 26, 8, 13), (37, 39, 8, 13), (31, 32.2, 9, 13), (44, 45.2, 9, 13),
    # the east end: the wall of the hall and the outer wall (a doorway in each)
    (49, 52, 8, 16.5), (58, 60, 8, 16.5),
]


def tripartite_temple(ctx, col, b, rng):
    """The Late Uruk temple of Eanna built from its plan: niched outer walls, chambers, the cross hall and the long middle hall."""
    fr = Frame(b["c"], b["yaw"])
    w, d, h = b["w"], b["d"], b["h"]
    cell = w / TEMPLE_COLS
    rects = []
    for (c0, c1, r0, r1) in TEMPLE_NORTH:
        rects.append((c0, c1, r0, r1))
        rects.append((c0, c1, TEMPLE_ROWS - r1, TEMPLE_ROWS - r0))
    lo, hi = ground_range(ctx, fr.rect(-w / 2, w / 2, -d / 2, d / 2))
    for (c0, c1, r0, r1) in rects:
        u0, u1 = (c0 - TEMPLE_COLS / 2) * cell, (c1 - TEMPLE_COLS / 2) * cell
        v0, v1 = (r0 - TEMPLE_ROWS / 2) * cell, (r1 - TEMPLE_ROWS / 2) * cell
        _, hi_i = ground_range(ctx, fr.rect(u0, u1, v0, v1))
        thick = min(c1 - c0, r1 - r0) * cell
        mass(ctx, col, fr, u0, u1, v0, v1, h + hi - hi_i, "limestone", (1, 1, 1), top="limestone", niches=2.2 if thick > 3.0 else 0.0,
             band=None, lip=0.35)


def great_court(ctx, col, b, rng):
    """A walled square orchard with rows of trees, water channels between the rows and a pool in the corner by the entrance."""
    fr = Frame(b["c"], b["yaw"])
    w = b["w"]
    th = 2.0
    hw = w / 2
    segs = [(-hw, hw, -hw, -hw + th), (-hw, hw, hw - th, hw), (-hw, -hw + th, -hw, hw), (hw - th, hw, -hw, hw)]
    for (a0, a1, b0, b1) in segs:
        corners = fr.rect(a0, a1, b0, b1)
        lo, hi = ground_range(ctx, corners)
        ctx.m.tint = (0.95, 0.86, 0.74)
        cx = sum(p[0] for p in corners) / 4
        cz = sum(p[1] for p in corners) / 4
        for i in range(4):
            a, bb = corners[i], corners[(i + 1) % 4]
            ctx.wall("mudbrick", a, bb, lo - 0.5, hi + 3.0, ((a[0] + bb[0]) / 2 - cx, (a[1] + bb[1]) / 2 - cz), i)
        ctx.top("mudbrick", corners, hi + 3.0)
        col.prism(corners, lo - 0.6, hi + 3.0)
    ctx.m.tint = (1, 1, 1)
    # the orchard floor, channels and trees in rows
    n = 6
    step = (w - 2 * th - 4.0) / n
    for i in range(n):
        for j in range(n):
            u = -hw + th + 2.0 + step * (i + 0.5)
            v = -hw + th + 2.0 + step * (j + 0.5)
            if i == 0 and j == 0:
                continue
            c = fr.W(u, v)
            tree(ctx, c[0], c[1], random.Random(i * 31 + j))
        # a channel along each row
        strip = fr.rect(-hw + th + 1.0, hw - th - 1.0, -hw + th + 2.0 + step * (i + 0.5) + 1.2, -hw + th + 2.0 + step * (i + 0.5) + 1.8)
        ctx.m.face([ctx.V(p[0], p[1], ctx.H(*p) + 0.11) for p in strip], "water", [(0, 0), (1, 0), (1, 1), (0, 1)], (0, 0, 1))
    # the pool by the entrance
    pc = fr.W(-hw + th + 3.0, -hw + th + 3.0)
    ctx.prism("bakedbrick", "water", fr.rect(-hw + th + 1.0, -hw + th + 5.0, -hw + th + 1.0, -hw + th + 5.0), ctx.H(*pc) - 0.2, ctx.H(*pc) + 0.4)


def build_eanna(plan, ground, origin, out_dir, finish):
    model = C.CM()
    ctx = C.Ctx(model, origin, ground)
    col = C.Collision(origin, ground)
    blocks = []
    for b in plan["eanna_buildings"]:
        fr = Frame(b["c"], b["yaw"])
        half_w, half_d = b["w"] / 2 + (3.0 if b["name"] == "stone_cone" else 0.0), b["d"] / 2 + (3.0 if b["name"] == "stone_cone" else 0.0)

        def inside(p, fr=fr, hw=half_w, hd=half_d):
            d = (p[0] - fr.c[0], p[1] - fr.c[1])
            return abs(d[0] * fr.t[0] + d[1] * fr.t[1]) < hw + 0.5 and abs(d[0] * fr.n[0] + d[1] * fr.n[1]) < hd + 0.5

        blocks.append({"inside": inside})
    n = court_paving(ctx, plan, blocks)
    print("court cells:", n)
    for b in plan["eanna_buildings"]:
        rng = random.Random(len(b["name"]))
        {"great_court": great_court, "pillar_hall": pillar_hall, "stone_cone": stone_cone_building, "limestone_hall": tripartite_temple}[b["name"]](
            ctx, col, b, rng)
    finish(model, os.path.join(out_dir, "uruk_eanna.glb"))
    col.export(os.path.join(out_dir, "uruk_eanna_collision.glb"))


# ---------------------------------------------------------------- the great market and the dispatch

def build_market(plan, ground, m, out_dir, finish):
    origin = tuple(m["c"])
    model = C.CM()
    ctx = C.Ctx(model, origin, ground)
    col = C.Collision(origin, ground)
    market(ctx, col, m, plan)
    for k in range(8):
        a = math.radians(45 * k + 20)
        c = (origin[0] + math.cos(a) * (m["w"] / 2 + 3), origin[1] + math.sin(a) * (m["d"] / 2 + 3))
        palm(ctx, c[0], c[1], random.Random(k))
    finish(model, os.path.join(out_dir, "uruk_market.glb"))
    col.export(os.path.join(out_dir, "uruk_market_collision.glb"))


def build_site(plan, ground, name, out_dir, finish):
    if name == "uruk_market":
        m = [x for x in plan["markets"] if x["name"] == "uruk_market"][0]
        build_market(plan, ground, m, out_dir, finish)
    elif name in ("uruk_palace", "sinkashid_palace"):
        pal = [p for p in plan["palaces"] if p["name"] == name][0]
        model, col = build_palace(plan, ground, pal, out_dir, finish, name)
        stem = "uruk_palace" if name == "uruk_palace" else "uruk_sinkashid"
        finish(model, os.path.join(out_dir, stem + ".glb"))
        col.export(os.path.join(out_dir, stem + "_collision.glb"))
    elif name == "ishtar_temple":
        build_ishtar_ziggurat(plan, ground, tuple(plan["fixed"]["ishtar_temple"]), out_dir, finish)
    elif name == "eanna_temple":
        build_eanna(plan, ground, tuple(plan["fixed"]["eanna_temple"]), out_dir, finish)
    else:
        raise SystemExit("unknown site " + name)


# ---------------------------------------------------------------- the irrigated fields

def palm_low(ctx, x, z, rng):
    """A cheap date palm for the orchards: a four-sided trunk and five fronds."""
    g = ctx.H(x, z)
    h = rng.uniform(6.0, 9.0)
    r0, r1 = 0.3, 0.2
    ring = lambda r, zz: [(x + math.cos(a) * r, z + math.sin(a) * r, zz) for a in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)]
    a, b = ring(r0, g), ring(r1, g + h)
    for i in range(4):
        j = (i + 1) % 4
        mid = ((a[i][0] + a[j][0]) / 2 - x, (a[i][1] + a[j][1]) / 2 - z)
        ctx.quad("trunk", [a[i], a[j], b[j], b[i]], (mid[0], mid[1], 0.0))
    top = (x, z, g + h)
    for i in range(5):
        ang = 2 * math.pi * i / 5 + rng.uniform(-0.3, 0.3)
        d = (math.cos(ang), math.sin(ang))
        s = (-d[1], d[0])
        L = rng.uniform(3.4, 4.4)
        end = (top[0] + d[0] * L, top[1] + d[1] * L, top[2] - 0.8)
        ctx.quad("frond", [(top[0] - s[0] * 0.5, top[1] - s[1] * 0.5, top[2] + 0.2), (top[0] + s[0] * 0.5, top[1] + s[1] * 0.5, top[2] + 0.2),
                           (end[0] + s[0] * 0.08, end[1] + s[1] * 0.08, end[2]), (end[0] - s[0] * 0.08, end[1] - s[1] * 0.08, end[2])], (0, 0, 1))


def field(ctx, f):
    """A field of the irrigated land: a grid of quads that follow the ground, textured with furrows along the long side (grain),
    bare plowed earth (fallow) or grass with rows of date palms (orchard)."""
    t = tuple(f["t"])
    n = left(t)
    c = tuple(f["c"])
    w, d = f["w"], f["d"]
    mat = {"grain": "crop", "fallow": "plowed", "orchard": "grass"}[f["kind"]]
    rng = random.Random(f["seed"])
    nu, nv = max(1, int(round(w / 10.0))), max(1, int(round(d / 10.0)))
    tile = 8.0
    tint = (rng.uniform(0.85, 1.0), rng.uniform(0.9, 1.0), rng.uniform(0.8, 1.0))
    ctx.m.tint = tint
    for i in range(nu):
        for j in range(nv):
            u0, u1 = -w / 2 + w * i / nu, -w / 2 + w * (i + 1) / nu
            v0, v1 = -d / 2 + d * j / nv, -d / 2 + d * (j + 1) / nv
            pts = [C.rotated(c, t, n, u0, v0), C.rotated(c, t, n, u1, v0), C.rotated(c, t, n, u1, v1), C.rotated(c, t, n, u0, v1)]
            # furrows run along t: the texture's stripes (constant u) follow it
            uvs = [(v0 / tile, u0 / tile), (v0 / tile, u1 / tile), (v1 / tile, u1 / tile), (v1 / tile, u0 / tile)]
            ctx.m.face([ctx.V(p[0], p[1], ctx.H(*p) + 0.12) for p in pts], mat, uvs, (0, 0, 1))
    ctx.m.tint = (1.0, 1.0, 1.0)
    if f["kind"] == "orchard":
        step = 12.0
        nu2, nv2 = int(w // step), int(d // step)
        for i in range(nu2):
            for j in range(nv2):
                a = -w / 2 + (i + 0.5) * w / nu2 + rng.uniform(-0.8, 0.8)
                b = -d / 2 + (j + 0.5) * d / nv2 + rng.uniform(-0.8, 0.8)
                p = C.rotated(c, t, n, a, b)
                palm_low(ctx, p[0], p[1], rng)
