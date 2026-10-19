"""The three bridges of Uruk: a wooden footbridge of the poor edges, a plain baked-brick
bridge of the burgher quarters, and the stone bridge with statues of the old gods that
carries the temple way over its canal (research/CITY.md). Built world-aligned in the
planner's frame like uruk_walls.py: the origin of each model is the surveyed point on the
middle of the canal it spans, the deck runs across the flow, and the water always passes under.

Usage: blender --background --python uruk_bridges.py -- [all|wood,brick,stone] <out_dir>

Headless only. Never run this through an add-on inside a GUI session: the factory reset
between models (read_factory_settings, which finish() alone would make unnecessary) disables
every add-on and wipes their preferences, and finish() removes every object of the open scene.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import uruk_city as C
import ziggurat as Z

# Mesopotamia had no stone to speak of; what it had was carried up from far quarries and spent
# on the gods alone, so the temple bridge is the one stone thing of the city (research/CITY.md).
Z.MATERIALS.update({
    "limestone": (None, (0.78, 0.74, 0.62), 0.85, 0.0, 1.0),
    "bitumen": (None, (0.10, 0.09, 0.08), 0.7, 0.05, 1.0),
})

PLAN = C.PLAN
SITES = {
    # The main canal (width 6) on the poor west edge, beside the wall road culvert.
    "wood": {"canal": 118, "near": (-1063.8, -639.1)},
    # A burgher canal of the middle quarters behind the Eanna ward.
    "brick": {"canal": 43, "near": (483.0, 322.0)},
    # The canal by the head of the Processional Way, the approach to the sacred precinct.
    "stone": {"canal": 113, "near": (25.1, 1052.6)},
}


def canal_point_direction(canals, site):
    """The surveyed point on the canal nearest `near`, and the bearing of the flow there."""
    pts = canals[site["canal"]]["pts"]
    best, index = 1e9, None
    for i, p in enumerate(pts):
        d = math.hypot(p[0] - site["near"][0], p[1] - site["near"][1])
        if d < best:
            best, index = d, i
    a, b = pts[max(0, index - 2)], pts[min(len(pts) - 1, index + 2)]
    flow = math.degrees(math.atan2(b[0] - a[0], -(b[1] - a[1]))) % 360.0
    return tuple(pts[index]), flow, canals[site["canal"]]["width"]


def frame(axis_bearing):
    """Plan-frame unit vectors: along the deck (across the water) and across it."""
    b = math.radians(axis_bearing)
    return (math.sin(b), -math.cos(b)), (math.cos(b), math.sin(b))


def at(c, e1, e2, a, b):
    """The plan point `a` metres along the deck and `b` across it from the centre."""
    return (c[0] + e1[0] * a + e2[0] * b, c[1] + e1[1] * a + e2[1] * b)


def sloped(ctx, col, c, e1, e2, a0, a1, w, h0, h1, mat, top=None):
    """A walkable slope from (a0, h0) to (a1, h1) along the deck: visual and collision."""
    n = max(2, int(abs(a1 - a0) / 0.22) + 1)
    for i in range(n - 1):
        aa0 = a0 + (a1 - a0) * i / (n - 1)
        aa1 = a0 + (a1 - a0) * (i + 1) / (n - 1)
        hh0 = h0 + (h1 - h0) * i / (n - 1)
        hh1 = h0 + (h1 - h0) * (i + 1) / (n - 1)
        mid, length = (aa0 + aa1) / 2.0, aa1 - aa0
        if ctx is not None:
            ctx.box(mat, top, at(c, e1, e2, mid, 0.0), e1, e2, length, w, hh0 - 0.6, hh1)
        if col is not None:
            col.box(at(c, e1, e2, mid, 0.0), e1, e2, length, w, hh0 - 0.6, hh1)


def arch_height(x, clear, rise, radius):
    """Height over the springing of a segmental arch at `x` metres from the crown."""
    return rise - (radius - math.sqrt(max(0.0, radius * radius - x * x)))


def voussoirs(ctx, c, e1, e2, clear, rise, w, bank, spring, steps, mat):
    """A segmental arch of stepped boxes (the flat-shaded way of the disk's models)."""
    radius = clear * clear / (8.0 * rise) + rise / 2.0
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        x0 = clear / 2.0 - t0 * clear
        x1 = clear / 2.0 - t1 * clear
        h0, h1 = arch_height(x0, clear, rise, radius), arch_height(x1, clear, rise, radius)
        centre = (x0 + x1) / 2.0
        ctx.box(mat, None, at(c, e1, e2, -centre, 0.0), e1, e2, abs(t1 - t0) * clear + 0.05, w,
                bank + spring + min(h0, h1) - 0.30, bank + spring + max(h0, h1))
    return radius


# ---------------------------------------------------------------- the wooden footbridge

def footbridge(model, plan, ground, canals):
    """A lávka of the poor edges: three log stringers carrying split-plank decking on posts
    driven into the banks and one trestle pair in the water, a single rail, nothing else."""
    origin, flow, width = canal_point_direction(canals, SITES["wood"])
    axis = (flow + 90.0) % 360.0
    ctx = C.Ctx(model, origin, ground)
    col = C.Collision(origin, ground)
    e1, e2 = frame(axis)
    length, w = 12.0, 2.2
    bank = ctx.H(*at(origin, e1, e2, -length / 2.0, 0.0))

    def dh(a):
        # a gentle crown: high over the middle of the water, down to the banks
        return bank + 0.30 + 0.28 * (1.0 - (abs(a) / (length / 2.0)) ** 2)

    # stringers: three logs along the axis, each in two halves to follow the crown
    for b in (-0.75, 0.0, 0.75):
        for a0, a1 in ((-length / 2.0, 0.0), (0.0, length / 2.0)):
            ctx.box("wood", None, at(origin, e1, e2, (a0 + a1) / 2.0, b * w / 2.0), e1, e2,
                    a1 - a0, 0.24, dh(a0) - 0.24, dh(a1) - 0.02)
    # decking of split planks
    a = -length / 2.0
    while a < length / 2.0 - 1e-6:
        span = min(0.35, length / 2.0 - a)
        mid = a + span / 2.0
        ctx.box("wood", "wood", at(origin, e1, e2, mid, 0.0), e1, e2, span, w, dh(mid) - 0.07, dh(mid))
        a += span
    # posts: a pair on each bank and one trestle pair in the water
    ctx.m.jitter = 0.9
    for aa in (-length / 2.0 + 0.9, -1.4, 1.4, length / 2.0 - 0.9):
        bed = ctx.H(*at(origin, e1, e2, aa, 0.0)) - 0.55
        for sgn in (-1, 1):
            ctx.box("wood", None, at(origin, e1, e2, aa, sgn * (w / 2.0 - 0.16)), e1, e2,
                    0.22, 0.22, bed, dh(aa) - 0.04)
    # the one rail, upstream, in posts and two rails
    for aa in (-length / 2.0 + 0.5, -0.4, 0.6, length / 2.0 - 0.3):
        ctx.box("wood", None, at(origin, e1, e2, aa, w / 2.0 - 0.18), e1, e2,
                0.14, 0.14, dh(aa) - 0.02, dh(aa) + 0.72)
    for a0, a1 in ((-length / 2.0, 0.0), (0.0, length / 2.0)):
        for up in (0.62, 0.30):
            ctx.box("wood", None, at(origin, e1, e2, (a0 + a1) / 2.0, w / 2.0 - 0.18), e1, e2,
                    a1 - a0, 0.10, dh(a0) + up, dh(a1) + up)
    ctx.m.jitter = 1.0
    # earth landings on both banks
    for sgn in (-1, 1):
        h = dh(sgn * length / 2.0)
        ctx.box("earth", "dust", at(origin, e1, e2, sgn * (length / 2.0 + 0.55), 0.0), e1, e2,
                1.4, w + 0.6, h - 0.55, h)
    # collision: the deck and the landings - walkable from both banks
    for a0, a1 in ((-length / 2.0, 0.0), (0.0, length / 2.0)):
        n = 6
        for i in range(n):
            aa0 = a0 + (a1 - a0) * i / n
            aa1 = a0 + (a1 - a0) * (i + 1) / n
            col.box(at(origin, e1, e2, (aa0 + aa1) / 2.0, 0.0), e1, e2, aa1 - aa0, w,
                    dh(aa0) - 0.12, dh(aa1))
    return origin, axis, col


# ---------------------------------------------------------------- the brick bridge

def brick_bridge(model, plan, ground, canals):
    """The bridge of the burgher quarters: a segmental arch of baked brick set in bitumen,
    mudbrick abutments, a paved deck for the carts, low parapets. 4 m wide."""
    origin, flow, width = canal_point_direction(canals, SITES["brick"])
    axis = (flow + 90.0) % 360.0
    ctx = C.Ctx(model, origin, ground)
    col = C.Collision(origin, ground)
    e1, e2 = frame(axis)
    length, w = 8.6, 4.0
    bank = ctx.H(*at(origin, e1, e2, -length / 2.0, 0.0))
    spring, rise = 0.55, 0.95
    clear = max(width + 0.3, 3.5)
    deck = spring + rise + 0.14
    # abutments of mudbrick with a baked-brick face round the opening
    for sgn in (-1, 1):
        a0, a1 = sgn * length / 2.0, sgn * (clear / 2.0 + 0.15)
        ctx.box("mudbrick", None, at(origin, e1, e2, (a0 + a1) / 2.0, 0.0), e1, e2,
                abs(a1 - a0), w, bank - 0.55, bank + spring)
        for side in (-1, 1):
            ctx.box("bakedbrick", None, at(origin, e1, e2, sgn * (clear / 2.0 + 0.15), side * (w / 2.0 - 0.07)),
                    e1, e2, 0.14, w, bank - 0.55, bank + spring)
    voussoirs(ctx, origin, e1, e2, clear, rise, w, bank, spring, 13, "bakedbrick")
    # bitumen waterproofing over the arch, the paved deck and its ramps
    ctx.box("bitumen", None, at(origin, e1, e2, 0.0, 0.0), e1, e2, clear + 0.4, w,
            bank + spring + rise - 0.07, bank + deck - 0.07)
    ctx.box("bakedbrick", "paving", at(origin, e1, e2, 0.0, 0.0), e1, e2, clear + 0.5, w,
            bank + deck - 0.10, bank + deck)
    for sgn in (-1, 1):
        sloped(ctx, None, origin, e1, e2, sgn * (clear / 2.0 + 0.25), sgn * (length / 2.0 + 0.6),
               w, bank + deck, bank - 0.05, "bakedbrick", top="paving")
        # parapets along the whole bridge
        for side in (-1, 1):
            ctx.box("bakedbrick", "bakedbrick", at(origin, e1, e2, sgn * (length / 4.0 + 0.3), side * (w / 2.0 - 0.15)),
                    e1, e2, length / 2.0 + 1.2, 0.30, bank + deck, bank + deck + 0.72)
    # collision: the way, its ramps and parapets; the water keeps its course under the arch
    col.box(at(origin, e1, e2, 0.0, 0.0), e1, e2, clear + 0.5, w, bank + deck - 0.10, bank + deck)
    for sgn in (-1, 1):
        sloped(None, col, origin, e1, e2, sgn * (clear / 2.0 + 0.25), sgn * (length / 2.0 + 0.6),
               w, bank + deck, bank - 0.05, "bakedbrick")
        for side in (-1, 1):
            col.box(at(origin, e1, e2, sgn * (length / 4.0 + 0.3), side * (w / 2.0 - 0.15)),
                     e1, e2, length / 2.0 + 1.2, 0.30, bank + deck, bank + deck + 0.72)
    return origin, axis, col


# ---------------------------------------------------------------- the stone bridge

def deity(ctx, c, e1, e2, base):
    """A god of old Sumer: the long robe, the arms folded in blessing, the rod-and-ring of
    justice in gold at the chest and the tiered horned crown on the head. Stylised, like the
    votive figures of the Early Dynastic temples."""
    ctx.m.jitter = 0.97
    body = "limestone"
    # the long robe, tapered to the waist
    for frac, w_, d_ in ((0.00, 0.56, 0.40), (0.28, 0.50, 0.36), (0.56, 0.42, 0.30)):
        ctx.box(body, None, at(c, e1, e2, 0.0, 0.0), e1, e2, w_, d_, base + frac, base + frac + 0.30)
    # the shoulders and the folded arms
    ctx.box(body, None, at(c, e1, e2, 0.0, 0.0), e1, e2, 0.50, 0.42, base + 0.86, base + 1.12)
    ctx.box(body, None, at(c, e1, e2, 0.0, -0.12), e1, e2, 0.34, 0.24, base + 0.74, base + 0.92)
    # the rod-and-ring of justice, gold, at the chest
    ctx.box("gold", None, at(c, e1, e2, 0.14, -0.12), e1, e2, 0.16, 0.16, base + 0.82, base + 0.98)
    # the head, then the crown: a tier of horns for each rank of heaven
    ctx.box(body, None, at(c, e1, e2, 0.0, 0.0), e1, e2, 0.30, 0.28, base + 1.12, base + 1.32)
    crown = base + 1.32
    for w_, d_, hh in ((0.34, 0.32, 0.10), (0.30, 0.28, 0.09), (0.24, 0.22, 0.08)):
        ctx.box(body, None, at(c, e1, e2, 0.0, 0.0), e1, e2, w_, d_, crown, crown + hh)
        crown += hh
    ctx.m.jitter = 1.0


def stone_bridge(model, plan, ground, canals):
    """The bridge of the temple way: stone carried from far quarries and spent on the gods
    alone, a wide arch, the glazed band of the temple blue, and four gods of old Sumer
    watching the way. 5.2 m wide."""
    origin, flow, width = canal_point_direction(canals, SITES["stone"])
    axis = (flow + 90.0) % 360.0
    ctx = C.Ctx(model, origin, ground)
    col = C.Collision(origin, ground)
    e1, e2 = frame(axis)
    length, w = 10.0, 5.2
    bank = ctx.H(*at(origin, e1, e2, -length / 2.0, 0.0))
    spring, rise = 0.70, 1.05
    clear = max(width + 0.4, 3.6)
    deck = spring + rise + 0.16
    # stone abutments with cutwaters against the current
    for sgn in (-1, 1):
        a0, a1 = sgn * length / 2.0, sgn * (clear / 2.0 + 0.2)
        ctx.box("limestone", None, at(origin, e1, e2, (a0 + a1) / 2.0, 0.0), e1, e2,
                abs(a1 - a0), w, bank - 0.7, bank + spring)
        for side in (-1, 1):
            # the cutwater nose: a prism pointing into the flow from the abutment
            tip = at(origin, e1, e2, sgn * (clear / 2.0 + 0.2), side * (w / 2.0 + 0.9))
            back = at(origin, e1, e2, sgn * (clear / 2.0 + 0.2), side * w / 2.0)
            fore = at(origin, e1, e2, sgn * (clear / 2.0 - 0.5), side * w / 2.0)
            ctx.prism("limestone", "limestone", [tip, back, fore], bank - 0.7, bank + spring + 0.05)
    voussoirs(ctx, origin, e1, e2, clear, rise, w, bank, spring, 15, "limestone")
    # the deck: stone slabs with the paved way over them, and ramps to the ground
    ctx.box("limestone", None, at(origin, e1, e2, 0.0, 0.0), e1, e2, clear + 0.5, w,
            bank + deck - 0.16, bank + deck - 0.04)
    ctx.box("limestone", "paving", at(origin, e1, e2, 0.0, 0.0), e1, e2, clear + 0.5, w,
            bank + deck - 0.05, bank + deck)
    for sgn in (-1, 1):
        sloped(ctx, None, origin, e1, e2, sgn * (clear / 2.0 + 0.25), sgn * (length / 2.0 + 0.7),
               w, bank + deck, bank - 0.05, "limestone", top="paving")
        # parapets with the temple's glazed band and a coping
        for side in (-1, 1):
            centre = at(origin, e1, e2, sgn * (length / 4.0 + 0.35), side * (w / 2.0 - 0.24))
            ctx.box("limestone", None, centre, e1, e2, length / 2.0 + 1.4, 0.48, bank + deck, bank + deck + 1.02)
            ctx.box("blueglaze", None, at(origin, e1, e2, sgn * (length / 4.0 + 0.35), side * (w / 2.0 - 0.49)),
                    e1, e2, length / 2.0 + 1.4, 0.05, bank + deck + 0.12, bank + deck + 0.52)
            ctx.box("limestone", "limestone", centre, e1, e2, length / 2.0 + 1.4, 0.56,
                    bank + deck + 1.02, bank + deck + 1.14)
    # the four gods on their pedestals, watching the way
    for sgn in (-1, 1):
        for side in (-1, 1):
            base = at(origin, e1, e2, sgn * (length / 2.0 - 1.15), side * (w / 2.0 - 0.85))
            ctx.box("limestone", "limestone", base, e1, e2, 0.95, 0.95, bank + deck, bank + deck + 0.85)
            deity(ctx, base, e1, e2, bank + deck + 0.85)
    # collision: the way, its ramps and parapets; the water passes under the arch
    col.box(at(origin, e1, e2, 0.0, 0.0), e1, e2, clear + 0.5, w, bank + deck - 0.16, bank + deck)
    for sgn in (-1, 1):
        sloped(None, col, origin, e1, e2, sgn * (clear / 2.0 + 0.25), sgn * (length / 2.0 + 0.7),
               w, bank + deck, bank - 0.05, "limestone")
        for side in (-1, 1):
            col.box(at(origin, e1, e2, sgn * (length / 4.0 + 0.35), side * (w / 2.0 - 0.24)),
                    e1, e2, length / 2.0 + 1.4, 0.48, bank + deck, bank + deck + 1.02)
    return origin, axis, col


BUILDERS = {"wood": footbridge, "brick": brick_bridge, "stone": stone_bridge}


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    which, out_dir = args[0], args[1]
    with open(PLAN) as handle:
        plan = json.load(handle)
    canals = plan.get("canals", [])
    ground = C.Ground()
    todo = list(BUILDERS) if which == "all" else which.split(",")
    for name in todo:
        import bpy
        bpy.ops.wm.read_factory_settings(use_empty=True)
        model = C.CM()
        origin, axis, col = BUILDERS[name](model, plan, ground, canals)
        out = os.path.join(out_dir, "uruk_bridge_%s.glb" % name)
        C.finish(model, out)
        col.export(os.path.join(out_dir, "uruk_bridge_%s_collision.glb" % name))
        print("%s: bearing_deg %.3f distance_m %.1f (from the anchor of uruk)" % (
            name, math.degrees(math.atan2(origin[0], -origin[1])) % 360.0, math.hypot(*origin)))


if __name__ == "__main__":
    main()
