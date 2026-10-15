#!/usr/bin/env python3
"""Plans the streets and buildings of Uruk inside its wall and writes tools/data/uruk_city.json.

    tools/build_city.py [--preview out.png]

Pure Python (numpy, Pillow, matplotlib for the preview). The plan is deterministic: the same inputs give the same city.
Coordinates are the client's local frame in metres from the anchor of Uruk: x east, z south (as in uruk_outlines.json).

What it plans (see research/CITY.md):
  * the gates of the wall (the Ishtar Gate stays where uruk_walls.py puts it) and the avenues from every gate to the
    sacred precinct of Eanna, where the ziggurats stand; a ring road round the precinct, a middle ring and the road
    inside the wall; lanes branching off, some of them dead ends;
  * houses along every street in three sizes (poor, middling, rich) with random sizes, turns, heights and wall colours;
  * markets (plazas with stalls), a smiths' quarter and single smithies, two palaces with farm buildings round them.
The Blender builder models/architecture/uruk_city.py turns the plan into models; tools/build_city_places.py is not
needed: the districts are written into places/uruk_city.yaml by this script.
"""
import argparse
import json
import math
import os
import random

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTLINES = os.path.join(HERE, "data", "uruk_outlines.json")
OUT = os.path.join(HERE, "data", "uruk_city.json")
HEIGHT = os.path.join(ROOT, "media", "terrain", "uruk_height.png")
WATER = os.path.join(ROOT, "media", "terrain", "uruk_water.png")
EXTENT = 6000.0

SEED = 2700
INSET_ROAD = 15.0        # the road inside the wall, from the wall's inner face
WALL_CLEAR = 24.0        # no houses closer to the wall than this
AVENUE_W, RING_W, STREET_W, LANE_W = 14.0, 10.0, 6.5, 4.0


# ---------------------------------------------------------------- terrain

class Ground:
    def __init__(self):
        self.h = np.array(Image.open(HEIGHT)).astype(float)
        self.w = np.array(Image.open(WATER)).astype(float)
        self.n = self.h.shape[0]
        self.step = EXTENT / self.n

    def _rc(self, x, z):
        return z / self.step + (self.n - 1) / 2.0, x / self.step + (self.n - 1) / 2.0

    def height(self, x, z):
        """Terrain height in metres above the anchor (bilinear), as the server's patch gives it."""
        r, c = self._rc(x, z)
        r = min(max(r, 0.0), self.n - 1.001)
        c = min(max(c, 0.0), self.n - 1.001)
        r0, c0 = int(r), int(c)
        fr, fc = r - r0, c - c0
        g = self.h
        v = (g[r0, c0] * (1 - fc) + g[r0, c0 + 1] * fc) * (1 - fr) + (g[r0 + 1, c0] * (1 - fc) + g[r0 + 1, c0 + 1] * fc) * fr
        return (v - 32768.0) / 10.0

    def wet(self, x, z):
        r, c = self._rc(x, z)
        r, c = int(round(r)), int(round(c))
        if not (0 <= r < self.n and 0 <= c < self.n):
            return False
        return self.w[r, c] > 0


# ---------------------------------------------------------------- geometry

def sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, k):
    return (a[0] * k, a[1] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def length(a):
    return math.hypot(a[0], a[1])


def unit(a):
    n = length(a)
    return (a[0] / n, a[1] / n) if n > 1e-9 else (1.0, 0.0)


def left(a):
    return (-a[1], a[0])


def lerp(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def seg_dist(p, a, b):
    ab = sub(b, a)
    t = max(0.0, min(1.0, dot(sub(p, a), ab) / max(1e-9, dot(ab, ab))))
    return length(sub(p, add(a, mul(ab, t)))), t


def in_poly(p, poly):
    x, z = p
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def poly_dist(p, poly):
    return min(seg_dist(p, poly[i], poly[(i + 1) % len(poly)])[0] for i in range(len(poly)))


def poly_area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def resample(pts, step):
    """A polyline with points about `step` apart (the ends stay)."""
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        d = length(sub(b, a))
        n = max(1, int(round(d / step)))
        for k in range(1, n + 1):
            out.append(lerp(a, b, k / n))
    return out


def smooth(pts, passes=2):
    for _ in range(passes):
        out = [pts[0]]
        for i in range(1, len(pts) - 1):
            out.append(((pts[i - 1][0] + 2 * pts[i][0] + pts[i + 1][0]) / 4, (pts[i - 1][1] + 2 * pts[i][1] + pts[i + 1][1]) / 4))
        out.append(pts[-1])
        pts = out
    return pts


def arc_lengths(pts):
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + length(sub(b, a)))
    return s


def point_at(pts, s_list, s):
    """Position and unit tangent at arc length s of a polyline."""
    s = max(0.0, min(s_list[-1], s))
    lo, hi = 0, len(pts) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if s_list[mid] <= s:
            lo = mid
        else:
            hi = mid
    seg = s_list[hi] - s_list[lo]
    f = (s - s_list[lo]) / seg if seg > 1e-9 else 0.0
    # tangent smoothed over neighbouring segments
    a = pts[max(0, lo - 1)]
    b = pts[min(len(pts) - 1, hi + 1)]
    return lerp(pts[lo], pts[hi], f), unit(sub(b, a))


def rect_corners(c, t, w, d):
    """Corners of a w (along t) by d (across) rectangle centred at c."""
    n = left(t)
    hw, hd = w / 2, d / 2
    return [add(add(c, mul(t, -hw)), mul(n, -hd)), add(add(c, mul(t, hw)), mul(n, -hd)),
            add(add(c, mul(t, hw)), mul(n, hd)), add(add(c, mul(t, -hw)), mul(n, hd))]


def rects_overlap(a, b, margin=0.0):
    """Separating axis test of two convex quadrilaterals, `a` grown by `margin`."""
    for poly in (a, b):
        for i in range(4):
            e = sub(poly[(i + 1) % 4], poly[i])
            axis = unit(left(e))
            pa = [dot(p, axis) for p in a]
            pb = [dot(p, axis) for p in b]
            if max(pa) + margin < min(pb) or max(pb) + margin < min(pa):
                return False
    return True


class Hash:
    """A spatial hash of shapes with a bounding radius."""

    def __init__(self, cell=40.0):
        self.cell = cell
        self.cells = {}

    def _keys(self, c, r):
        x0, x1 = int((c[0] - r) // self.cell), int((c[0] + r) // self.cell)
        z0, z1 = int((c[1] - r) // self.cell), int((c[1] + r) // self.cell)
        return [(x, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)]

    def add(self, item, c, r):
        for k in self._keys(c, r):
            self.cells.setdefault(k, []).append(item)

    def near(self, c, r):
        seen = set()
        for k in self._keys(c, r):
            for item in self.cells.get(k, ()):
                if id(item) not in seen:
                    seen.add(id(item))
                    yield item


# ---------------------------------------------------------------- the plan

class City:
    def __init__(self):
        self.rng = random.Random(SEED)
        self.ground = Ground()
        with open(OUTLINES) as handle:
            self.outlines = json.load(handle)
        raw = self.outlines["wall"][:-1]
        self.wall = [(x, z) for x, z, _ in raw]
        self.wall_h = [h for _, _, h in raw]
        if poly_area(self.wall) < 0:     # make it clockwise on the map (x east, z south): the outside is to the left
            pass
        self.eanna = [tuple(p) for p in self.outlines["eanna"][:-1]]
        self.anu = tuple(self.outlines["ziggurat_centre"])
        self.streets = []        # dicts: id, kind, width, pts
        self.houses = []
        self.hash = Hash(30.0)   # house rectangles and reserved shapes
        self.street_hash = Hash(30.0)
        self.zones = []          # reserved shapes: dict(kind, poly, name)
        self.markers = {}
        self.gates = []
        self.palaces = []
        self.markets = []
        self.smithies = []
        self.farm = []
        self.centre = (130.0, -170.0)   # the sacred precinct

    # ---- wall helpers
    def wall_outward(self, i, span=3):
        """Outward unit normal of the wall at vertex i (towards the outside of the polygon)."""
        n = len(self.wall)
        t = unit(sub(self.wall[(i + span) % n], self.wall[(i - span) % n]))
        for sign in (1, -1):
            nrm = mul(left(t), sign)
            probe = add(self.wall[i], mul(nrm, 6.0))
            if not in_poly(probe, self.wall):
                return nrm
        return left(t)

    def _field(self):
        """Signed distance to the wall (positive inside) on a 5 m grid over the city, so that clearance tests are lookups."""
        from matplotlib.path import Path
        self.f0 = (-1500.0, -1700.0)
        self.fstep = 5.0
        nx, nz = int(3000 / 5), int(3300 / 5)
        xs = self.f0[0] + (np.arange(nx) + 0.5) * 5.0
        zs = self.f0[1] + (np.arange(nz) + 0.5) * 5.0
        gx, gz = np.meshgrid(xs, zs)
        pts = np.stack([gx.ravel(), gz.ravel()], 1)
        inside = Path(np.array(self.wall)).contains_points(pts)
        best = np.full(len(pts), 1e9)
        w = np.array(self.wall)
        for i in range(len(w)):
            a, b = w[i], w[(i + 1) % len(w)]
            ab = b - a
            t = np.clip(((pts - a) @ ab) / max(1e-9, ab @ ab), 0, 1)
            d = np.hypot(*(pts - (a + t[:, None] * ab)).T)
            best = np.minimum(best, d)
        self.sd = np.where(inside, best, -best).reshape(nz, nx)

    def inside(self, p, clear=0.0):
        if not hasattr(self, "sd"):
            self._field()
        c = int((p[0] - self.f0[0]) / self.fstep)
        r = int((p[1] - self.f0[1]) / self.fstep)
        if not (0 <= r < self.sd.shape[0] and 0 <= c < self.sd.shape[1]):
            return False
        return self.sd[r, c] >= max(clear, 0.0) if clear > 0 else self.sd[r, c] > 0

    # ---- gates
    def plan_gates(self):
        """Six gates: the Ishtar Gate in the south wall (chosen exactly as uruk_walls.py chooses it) and five more."""
        n = len(self.wall)
        ring = self.wall

        def straight(i):
            nrm = self.wall_outward(i)
            bend = 0.0
            flat = 0.0
            for k in range(-4, 5):
                q = ring[(i + k) % n]
                bend += abs(dot(sub(q, ring[i]), nrm))
                flat += abs(self.wall_h[(i + k) % n] - self.wall_h[i])
            return bend + 8.0 * flat

        # the Ishtar Gate: uruk_walls.py works with Blender's y = -z, the outward normal there has y < -0.6, that is z > 0.6
        best = None
        for i in range(n):
            nrm = self.wall_outward(i)
            if -nrm[1] > -0.6:
                continue
            sc = straight(i)
            if best is None or sc < best[0]:
                best = (sc, i)
        picks = [("ishtar", best[1])]
        # others by the direction of the outward normal (bearing clockwise from north: x east, z south)
        wanted = [("river", 90.0), ("north", 0.0), ("west", 270.0), ("northwest", 315.0), ("southwest", 225.0)]
        for name, bearing in wanted:
            want = (math.sin(math.radians(bearing)), -math.cos(math.radians(bearing)))
            cand = None
            for i in range(n):
                if any(self.arc_between(i, j) < 450.0 for _, j in picks):
                    continue
                nrm = self.wall_outward(i)
                if dot(nrm, want) < 0.82:
                    continue
                sc = straight(i) - 120.0 * dot(nrm, want)
                if cand is None or sc < cand[0]:
                    cand = (sc, i)
            if cand is None:
                raise SystemExit("no place for the %s gate" % name)
            picks.append((name, cand[1]))
        for name, i in picks:
            nrm = self.wall_outward(i)
            tan = unit(left(nrm))
            self.gates.append({"name": name, "index": i, "pos": [round(self.wall[i][0], 2), round(self.wall[i][1], 2)],
                               "out": [round(nrm[0], 4), round(nrm[1], 4)], "tangent": [round(tan[0], 4), round(tan[1], 4)],
                               "height": round(self.wall_h[i], 2)})
        print("gates:", [(g["name"], g["pos"]) for g in self.gates])

    def arc_between(self, i, j):
        if not hasattr(self, "_cum"):
            self._cum = [0.0]
            n = len(self.wall)
            for k in range(n):
                self._cum.append(self._cum[-1] + length(sub(self.wall[(k + 1) % n], self.wall[k])))
        total = self._cum[-1]
        d = abs(self._cum[i] - self._cum[j])
        return min(d, total - d)


# ---------------------------------------------------------------- streets

def chaikin(pts, closed=True, rounds=2):
    for _ in range(rounds):
        out = []
        n = len(pts)
        rng_ = range(n) if closed else range(n - 1)
        for i in rng_:
            a, b = pts[i], pts[(i + 1) % n]
            out += [lerp(a, b, 0.25), lerp(a, b, 0.75)]
        pts = out
    return pts


def inflate_convex(poly, dist):
    """A convex polygon grown by `dist` (vertex normals of the mitre)."""
    n = len(poly)
    cen = (sum(p[0] for p in poly) / n, sum(p[1] for p in poly) / n)
    out = []
    for i in range(n):
        a, b, c = poly[i - 1], poly[i], poly[(i + 1) % n]
        n1 = unit(left(sub(b, a)))
        n2 = unit(left(sub(c, b)))
        if dot(n1, sub(b, cen)) < 0:
            n1, n2 = mul(n1, -1), mul(n2, -1)
        m = unit(add(n1, n2))
        k = dist / max(0.4, dot(m, n1))
        out.append(add(b, mul(m, k)))
    return out


class Planner(City):
    # ---- registry
    def add_street(self, kind, width, pts, step=5.0, name=None):
        pts = resample(pts, step)
        sid = len(self.streets)
        street = {"id": sid, "kind": kind, "width": width, "pts": pts, "name": name}
        self.streets.append(street)
        half = width / 2.0
        for a, b in zip(pts, pts[1:]):
            item = (a, b, half, sid)
            self.street_hash.add(item, lerp(a, b, 0.5), length(sub(a, b)) / 2 + half + 2)
        return street

    def street_gap(self, p, ignore=(), reach=40.0):
        """Distance from p to the nearest street edge (negative inside a street) and that street's id."""
        best = (1e9, None)
        for a, b, half, sid in self.street_hash.near(p, reach):
            if sid in ignore:
                continue
            d = seg_dist(p, a, b)[0] - half
            if d < best[0]:
                best = (d, sid)
        return best

    def zone_hit(self, p, margin=0.0):
        for z in self.zones:
            if z["kind"] == "circle":
                if length(sub(p, z["c"])) < z["r"] + margin:
                    return z
            else:
                if in_poly(p, z["poly"]) or (margin > 0 and poly_dist(p, z["poly"]) < margin):
                    return z
        return None

    def reserve_poly(self, kind, poly, name):
        self.zones.append({"kind": "poly", "poly": poly, "name": name, "what": kind})

    def reserve_circle(self, c, r, name):
        self.zones.append({"kind": "circle", "c": c, "r": r, "name": name, "what": "marker"})

    # ---- the sacred precinct, avenues and rings
    def plan_precinct(self):
        self.precinct = self.eanna
        self.centre = (sum(p[0] for p in self.eanna) / len(self.eanna), sum(p[1] for p in self.eanna) / len(self.eanna))
        self.reserve_poly("precinct", self.precinct, "Eanna")
        ring = chaikin(inflate_convex(self.precinct, 34.0), True, 2)
        self.precinct_ring = ring
        self.add_street("ring", RING_W, ring + [ring[0]], name="sacred_ring")
        # the six entrances: corners of the precinct
        self.entrances = [p for p in self.precinct]

    def inward(self, g, d):
        out = tuple(g["out"])
        return add(tuple(g["pos"]), mul(out, -d))

    def plan_avenues(self):
        free = list(range(len(self.entrances)))
        order = sorted(range(len(self.gates)), key=lambda k: 0 if self.gates[k]["name"] == "ishtar" else 1)
        for k in order:
            g = self.gates[k]
            start = self.inward(g, 36.0 if g["name"] == "ishtar" else 18.0)
            gdir = unit(sub(start, self.centre))
            best = None
            for e in free:
                ed = unit(sub(self.entrances[e], self.centre))
                sc = dot(gdir, ed)
                if best is None or sc > best[0]:
                    best = (sc, e)
            e = best[1]
            free.remove(e)
            # land on the precinct ring beside the entrance
            ent = self.entrances[e]
            target = add(ent, mul(unit(sub(ent, self.centre)), 34.0))
            g["entrance"] = e
            pts = self.curved_path(start, target, amp_max=45.0, seed=k)
            # the way goes on into the court to the entrance corner
            pts = pts + [add(ent, mul(unit(sub(ent, self.centre)), 4.0))]
            street = self.add_street("avenue", AVENUE_W, pts, name="avenue_" + g["name"])
            g["avenue"] = street["id"]
            # the road leading away from the gate
            outer = add(tuple(g["pos"]), mul(tuple(g["out"]), 150.0 if g["name"] != "ishtar" else 5.0))
            if g["name"] != "ishtar":
                self.add_street("road", STREET_W, [add(tuple(g["pos"]), mul(tuple(g["out"]), 4.0)), outer], name="road_" + g["name"])
            # the stretch between the gate's inner end and the street, so that the two meet
            self.add_street("avenue", AVENUE_W, [tuple(g["pos"]), start], name="gatestreet_" + g["name"])

    def curved_path(self, a, b, amp_max, seed):
        r = random.Random(SEED * 31 + seed)
        d = length(sub(b, a))
        t = unit(sub(b, a))
        nrm = left(t)
        amp = min(amp_max, 0.04 * d) * (1 if r.random() < 0.5 else -1)
        phase = r.random() * 2
        pts = []
        n = max(6, int(d / 60))
        for i in range(n + 1):
            u = i / n
            lateral = amp * math.sin(math.pi * (u * 1.4 + phase * 0.2)) * math.sin(math.pi * u) ** 0.8
            pts.append(add(lerp(a, b, u), mul(nrm, lateral)))
        return smooth(pts, 2)

    def scaled_ring(self, f, wobble=0.0, name="ring"):
        pts = []
        for i, p in enumerate(self.wall):
            if i % 5:
                continue
            pts.append(add(self.centre, mul(sub(p, self.centre), f)))
        pts = chaikin(pts, True, 2)
        return pts

    def plan_rings(self):
        for f, nm in ((0.42, "middle_ring"), (0.70, "outer_ring")):
            pts = self.scaled_ring(f)
            # cut the ring where it would run through the precinct or the water
            run = []
            runs = []
            for p in pts + [pts[0]]:
                bad = self.zone_hit(p, 20.0) is not None or self.ground.wet(*p)
                if bad:
                    if len(run) > 3:
                        runs.append(run)
                    run = []
                else:
                    run.append(p)
            if len(run) > 3:
                runs.append(run)
            for k, r in enumerate(runs):
                self.add_street("ring", RING_W, r, name="%s_%d" % (nm, k))
        # the road inside the wall
        n = len(self.wall)
        pts = []
        for i in range(n):
            nrm = self.wall_outward(i, 2)
            pts.append(add(self.wall[i], mul(nrm, -(INSET_ROAD + 3.5))))
        pts = smooth(pts + pts[:2], 1)[:-1]
        pts = chaikin(pts, True, 1)
        runs, run = [], []
        for p in pts + [pts[0]]:
            if self.ground.wet(*p):
                if len(run) > 3:
                    runs.append(run)
                run = []
            else:
                run.append(p)
        if len(run) > 3:
            runs.append(run)
        for k, r in enumerate(runs):
            self.add_street("wallroad", STREET_W, r, name="wallroad_%d" % k)


# ---------------------------------------------------------------- preview

def preview(city, path, window=None, dpi=110, size=14):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    fig, ax = plt.subplots(figsize=(size, size * (1.0 if window is None else (window[3] - window[2]) / (window[1] - window[0]))))
    h = city.ground.h
    ax.imshow((h - 32768) / 10, extent=[-3000, 3000, 3000, -3000], cmap="terrain", alpha=0.35)
    wat = city.ground.w > 0
    ax.imshow(np.ma.masked_where(~wat, wat), extent=[-3000, 3000, 3000, -3000], cmap="Blues", alpha=0.8)
    w = city.wall + [city.wall[0]]
    ax.plot([p[0] for p in w], [p[1] for p in w], "k-", lw=2)
    colours = {"ring": "#b08040", "avenue": "#a06020", "road": "#c0a070", "wallroad": "#c0a070", "street": "#d0a060", "lane": "#d8b890",
               "alley": "#e0c8a0", "way": "#b08040"}
    for s in city.streets:
        xs = [p[0] for p in s["pts"]]
        zs = [p[1] for p in s["pts"]]
        ax.plot(xs, zs, "-", color=colours.get(s["kind"], "r"), lw=max(0.5, s["width"] * 0.6 * size / 14 / 3.2 * (3000 / ((window[1] - window[0]) / 2) if window else 1) / 3.0), solid_capstyle="butt")
    cls = {"S": "#9a7050", "M": "#c89860", "L": "#e0d0b0"}
    for hs in city.houses:
        colour = "#d04020" if hs.get("smith") else cls.get(hs["cls"], "#808080")
        ax.add_patch(Polygon(hs["corners"], closed=True, fc=colour, ec="none"))
    for m in city.markets:
        ax.add_patch(Polygon(m["poly"], closed=True, fc="#d04040", alpha=0.5))
    for p in city.palaces:
        ax.add_patch(Polygon(p["poly"], closed=True, fc="#4040d0", alpha=0.4))
    for z in city.zones:
        if z["kind"] == "poly":
            ax.add_patch(Polygon(z["poly"], closed=True, fc="none", ec="m", lw=1))
    mc = getattr(city, "main_canal", None)
    if mc:
        ax.plot([q[0] for q in mc["pts"]], [q[1] for q in mc["pts"]], "-", color="#0040ff", lw=2.5)
    for c in getattr(city, "canals", []):
        ax.plot([q[0] for q in c["pts"]], [q[1] for q in c["pts"]], "-", color="#3080c0", lw=0.8)
    for f in getattr(city, "fields", []):
        tt = f["t"]
        col_ = {"grain": "#70a040", "orchard": "#206020", "fallow": "#b09060"}[f["kind"]]
        ax.add_patch(Polygon(rect_corners(f["c"], tt, f["w"], f["d"]), closed=True, fc=col_, alpha=0.6, ec="none"))
    for b in getattr(city, "eanna_buildings", []):
        ax.add_patch(Polygon(b["corners"], closed=True, fc="#40a040", alpha=0.6))
    if hasattr(city, "ishtar_ziggurat"):
        z = city.ishtar_ziggurat
        ax.add_patch(Polygon(rect_corners(z["c"], left(z["front"]), 44.0, 44.0), closed=True, fc="#c04080", alpha=0.7))
    for k, p in getattr(city, "marker_places", {}).items():
        ax.plot(*p, "b^", ms=6)
    for k, p in getattr(city, "fixed", {}).items():
        ax.plot(*p, "r^", ms=7)
    for g in city.gates:
        ax.plot(*g["pos"], "go", ms=8)
    ax.plot(*city.centre, "m*", ms=12)
    if window:
        ax.set_xlim(window[0], window[1])
        ax.set_ylim(window[3], window[2])
    else:
        ax.set_xlim(-1500, 1400)
        ax.set_ylim(1500, -1650)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- sites: markets, smithies, palaces, markers

def offset_bearing(origin, bearing_deg, dist):
    b = math.radians(bearing_deg)
    return (origin[0] + dist * math.sin(b), origin[1] - dist * math.cos(b))


def frame_to_world(c, yaw_deg, u, v):
    """Compound frame: u along the front (t), v from the front into the compound (n = left of t, flipped so that +v goes
    away from the street, see Site)."""
    t = (math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg)))
    n = left(t)
    return add(c, add(mul(t, u), mul(n, v)))


class Sites(Planner):
    def rect_ok(self, corners, margin=10.0, streets=True, flat=0.5):
        c = (sum(p[0] for p in corners) / 4, sum(p[1] for p in corners) / 4)
        pts = list(corners) + [lerp(corners[i], corners[(i + 1) % 4], 0.5) for i in range(4)] + [c]
        for p in pts:
            if not self.inside(p, WALL_CLEAR + 30):
                return False
            if self.ground.wet(*p):
                return False
            if self.zone_hit(p, margin) is not None:
                return False
            if streets and self.street_gap(p)[0] < margin:
                return False
        hs = [self.ground.height(*p) for p in pts]
        return max(hs) - min(hs) <= flat * 8.0 and self.slope(corners) < 0.12

    def slope(self, corners):
        c = (sum(p[0] for p in corners) / 4, sum(p[1] for p in corners) / 4)
        hc = self.ground.height(*c)
        r = max(length(sub(p, c)) for p in corners)
        return max(abs(self.ground.height(*p) - hc) for p in corners) / max(1.0, r)

    def nearest_street_point(self, p, kinds=("avenue", "ring", "wallroad", "street", "lane")):
        best = None
        for s in self.streets:
            if s["kind"] not in kinds:
                continue
            for a, b in zip(s["pts"], s["pts"][1:]):
                d, t = seg_dist(p, a, b)
                if best is None or d < best[0]:
                    best = (d, add(a, mul(sub(b, a), t)), unit(sub(b, a)), s["id"])
        return best

    def connect_street(self, p, name, width=STREET_W, kinds=("avenue", "ring", "wallroad", "street")):
        d, q, t, sid = self.nearest_street_point(p, kinds)
        if d > 4:
            self.add_street("street", width, [p, q], name=name)
        return d

    # ---- markets
    def plan_markets(self):
        r = random.Random(SEED + 1)
        ishtar = self.streets[self.gates[0]["avenue"]]
        s_arc = arc_lengths(ishtar["pts"])
        # the great market beside the Ishtar avenue, towards the precinct
        spec = [("uruk_market", self.gates[0]["avenue"], arc_lengths(self.streets[self.gates[0]["avenue"]]["pts"])[-1] - 330.0, -1, 92.0, 62.0, "great"),
                ("market_ishtar", self.gates[0]["avenue"], 200.0, 1, 54.0, 36.0, "gate"),
                ("market_river", [g for g in self.gates if g["name"] == "river"][0]["avenue"], 190.0, 1, 54.0, 36.0, "gate"),
                ("market_west", [g for g in self.gates if g["name"] == "west"][0]["avenue"], 230.0, -1, 54.0, 36.0, "gate")]
        for name, sid, at, side, w, d, kind in spec:
            st = self.streets[sid]
            sl = arc_lengths(st["pts"])
            placed = False
            for dx in (0, 40, -40, 80, -80, 120, -120):
                p, t = point_at(st["pts"], sl, at + dx)
                n = left(t)
                for sd in (side, -side):
                    c = add(p, mul(n, sd * (AVENUE_W / 2 + d / 2 + 2.0)))
                    corners = rect_corners(c, t, w, d)
                    if self.rect_ok(corners, 3.0, streets=False) and all(
                            self.street_gap(q, ignore=(sid,))[0] > 6 for q in corners):
                        yaw = math.degrees(math.atan2(t[1], t[0]))
                        self.markets.append({"name": name, "kind": kind, "c": c, "t": t, "w": w, "d": d, "poly": corners,
                                             "avenue": sid, "side": sd, "yaw": yaw})
                        self.reserve_poly("market", corners, name)
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                print("market %s: no room" % name)
        print("markets:", [(m["name"], [round(v) for v in m["c"]]) for m in self.markets])

    # ---- palaces and their farm buildings
    def plan_palaces(self):
        specs = [("uruk_palace", (10.0, 100.0), 600.0, 190.0, 150.0), ("sinkashid_palace", (225.0, 300.0), 600.0, 230.0, 175.0)]
        for name, (b0, b1), rmax, W, D in specs:
            best = None
            for rad in range(190, int(rmax), 30):
                for b in range(int(b0), int(b1) + 1, 5):
                    ang = math.radians(b)
                    c = add(self.centre, (math.sin(ang) * rad, -math.cos(ang) * rad))
                    near = self.nearest_street_point(c, ("avenue", "ring"))
                    if near is None:
                        continue
                    for yaw in range(0, 180, 15):
                        t = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
                        corners = rect_corners(c, t, W, D)
                        if not self.rect_ok(corners, 18.0):
                            continue
                        # the front (-n side) should look at the nearest street
                        n = left(t)
                        score = rad + 0.5 * near[0]
                        if best is None or score < best[0]:
                            best = (score, c, yaw, corners)
                if best:
                    break
            if best is None:
                raise SystemExit("no room for " + name)
            score, c, yaw, corners = best
            t = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
            n = left(t)
            # which long side is the front: the one nearer to a street
            fa = add(c, mul(n, -D / 2 - 8))
            fb = add(c, mul(n, D / 2 + 8))
            da = self.nearest_street_point(fa)[0]
            db = self.nearest_street_point(fb)[0]
            if db < da:           # flip so that the front is -n
                yaw = (yaw + 180) % 360
                t = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
                n = left(t)
                fa = add(c, mul(n, -D / 2 - 8))
            self.palaces.append({"name": name, "c": c, "yaw": yaw, "W": W, "D": D, "poly": corners})
            self.reserve_poly("palace", corners, name)
            self.connect_street(add(c, mul(n, -D / 2)), "road_" + name, 9.0)
        print("palaces:", [(p["name"], [round(v) for v in p["c"]], p["yaw"]) for p in self.palaces])

    # ---- smithies: a street of workshops off the south-west avenue
    def plan_smith_street(self):
        sw = [g for g in self.gates if g["name"] == "southwest"][0]
        st = self.streets[sw["avenue"]]
        sl = arc_lengths(st["pts"])
        for at in (520.0, 470.0, 570.0, 420.0, 620.0):
            p, t = point_at(st["pts"], sl, at)
            n = left(t)
            for sd in (1, -1):
                # away from the sacred centre is outwards; try both sides
                d_dir = mul(n, sd)
                pts = [add(p, mul(d_dir, k * 6.0 + AVENUE_W / 2)) for k in range(0, 36)]
                ok = all(self.inside(q, WALL_CLEAR + 20) and not self.ground.wet(*q) and self.zone_hit(q, 6.0) is None
                         and (k < 4 or self.street_gap(q, ignore=(st["id"],))[0] > 22) for k, q in enumerate(pts))
                if ok:
                    s = self.add_street("street", STREET_W, pts, name="smiths_street")
                    self.smith_street = s["id"]
                    print("smiths' street from", [round(v) for v in pts[0]], "to", [round(v) for v in pts[-1]])
                    return
        print("no room for the smiths' street")
        self.smith_street = None

    # ---- markers of places that are not buildings of the plan
    def plan_markers(self):
        # anchors of the existing places (fixed by the datadisk): the middle of the site and the precinct
        self.markers["uruk"] = (0.0, 0.0)
        self.reserve_circle((0.0, 0.0), 26.0, "uruk")
        self.connect_street((0.0, 0.0), "square_uruk", STREET_W, ("avenue", "ring", "wallroad", "street"))


# ---------------------------------------------------------------- lanes and houses

SIZES = {  # class: (w range, d range, floors, ground-floor height range)
    "S": ((5.0, 7.4), (5.5, 8.5), (1,), (3.0, 3.6)),
    "M": ((7.8, 11.0), (8.5, 12.0), (1, 1, 2), (3.4, 4.0)),
    "L": ((11.5, 16.5), (12.5, 18.0), (2, 2, 3), (3.8, 4.4)),
}


class Builder(Sites):
    def setup_radial(self):
        self.R = []
        for k in range(180):
            ang = math.radians(k * 2.0)
            d = (math.sin(ang), -math.cos(ang))
            r = 0.0
            lo, hi = 0.0, 3000.0
            for _ in range(30):
                mid = (lo + hi) / 2
                if in_poly(add(self.centre, mul(d, mid)), self.wall):
                    lo = mid
                else:
                    hi = mid
            self.R.append(lo)

    def radial(self, p):
        v = sub(p, self.centre)
        r = length(v)
        ang = math.degrees(math.atan2(v[0], -v[1])) % 360.0
        k = int(ang / 2.0) % 180
        return min(1.5, r / max(100.0, self.R[k]))

    def keep_prob(self, u, kind):
        base = 1.0 if u < 0.42 else max(0.03, 1.0 - (u - 0.42) * 2.6)
        if kind in ("avenue", "ring"):
            base = min(1.0, base + 0.15)
        return base

    # ---- lanes
    def trace_lane(self, p, d, width, maxlen, parent, r, umax, kind):
        pts = [p]
        q = p
        heading = d
        travelled = 0.0
        step = 5.0
        end_snap = None
        while travelled < maxlen:
            turn = math.radians(r.uniform(-4.0, 4.0))
            heading = unit((heading[0] * math.cos(turn) - heading[1] * math.sin(turn),
                            heading[0] * math.sin(turn) + heading[1] * math.cos(turn)))
            nq = add(q, mul(heading, step))
            if not self.inside(nq, INSET_ROAD + 22) or self.ground.wet(*nq) or self.zone_hit(nq, 9.0) is not None:
                break
            if self.radial(nq) > umax:
                break
            gap, sid = self.street_gap(nq, ignore=(parent,) if travelled < 18 else ())
            if gap < 14.0 and sid is not None:
                if travelled >= 18.0:
                    st = self.streets[sid]
                    best = None
                    for a, b in zip(st["pts"], st["pts"][1:]):
                        dd, t = seg_dist(nq, a, b)
                        if best is None or dd < best[0]:
                            best = (dd, add(a, mul(sub(b, a), t)), unit(sub(b, a)))
                    if best is not None and abs(dot(heading, best[2])) < 0.8:
                        end_snap = best[1]
                break
            pts.append(nq)
            q = nq
            travelled += step
        if end_snap is not None:
            pts.append(end_snap)
        if travelled < 24.0:
            return None
        return pts

    def grow_lanes(self):
        r = random.Random(SEED + 2)
        generation = [[s["id"] for s in self.streets if s["kind"] in ("avenue", "ring", "street", "wallroad")
                       and s["name"] and not str(s["name"]).startswith(("gatestreet", "road", "wallroad", "square", "sacred"))]]
        for gen in (1, 2):
            fresh = []
            for sid in generation[-1]:
                st = self.streets[sid]
                sl = arc_lengths(st["pts"])
                total = sl[-1]
                if total < 60:
                    continue
                spacing = r.uniform(80.0, 110.0) if gen == 1 else r.uniform(60.0, 85.0)
                s = r.uniform(25.0, spacing)
                side = 1 if r.random() < 0.5 else -1
                while s < total - 20.0:
                    p, t = point_at(st["pts"], sl, s)
                    n = left(t)
                    heading = unit(add(mul(n, side), mul(t, r.uniform(-0.25, 0.25))))
                    umax = (0.40 + 0.22 * r.random()) if gen == 1 else (0.30 + 0.22 * r.random())
                    width = LANE_W + 0.5 if gen == 1 else LANE_W - 0.6
                    maxlen = r.uniform(90.0, 230.0) if gen == 1 else r.uniform(36.0, 110.0)
                    if gen == 3:
                        maxlen = r.uniform(30.0, 70.0)
                    start = add(p, mul(heading, st["width"] / 2.0))
                    if self.radial(p) <= umax and self.zone_hit(start, 8.0) is None:
                        pts = self.trace_lane(start, heading, width, maxlen, sid, r, umax, "lane")
                        if pts is not None:
                            new = self.add_street("lane" if gen == 1 else "alley", width, [p] + pts, name="lane%d" % len(self.streets))
                            fresh.append(new["id"])
                    side = -side
                    s += spacing * r.uniform(0.5, 0.75)
            generation.append(fresh)
        print("streets:", len(self.streets), "lanes:", sum(1 for s in self.streets if s["kind"] in ("lane", "alley")))

    # ---- houses
    def wealth(self, p, kind, r):
        d = length(sub(p, self.centre))
        w = 0.12 + 0.85 * math.exp(-d / 520.0)
        w += {"avenue": 0.12, "ring": 0.08, "street": 0.0, "lane": -0.08, "alley": -0.16, "wallroad": -0.15}.get(kind, 0.0)
        for pal in self.palaces:
            if length(sub(p, pal["c"])) < 160:
                w += 0.2
        return max(0.0, min(1.0, w + r.uniform(-0.14, 0.14)))

    def choose_class(self, w, r):
        pl = max(0.0, (w - 0.45)) * 1.5
        pm = 0.18 + 0.5 * w
        x = r.random()
        if x < pl:
            return "L"
        if x < pl + pm:
            return "M"
        return "S"

    def house_ok(self, corners, c, rad):
        for q in corners + [c]:
            if not self.inside(q, WALL_CLEAR) or self.ground.wet(*q):
                return False
            if self.zone_hit(q, 1.5) is not None:
                return False
        for hs in self.hash.near(c, rad + 2):
            if rects_overlap(corners, hs["corners"], 0.45):
                return False
        for q in corners + [lerp(corners[i], corners[(i + 1) % 4], 0.5) for i in range(4)]:
            gap, sid = self.street_gap(q)
            if gap < 0.35:
                return False
        return self.slope(corners) < 0.2

    def fill_street(self, st, r):
        kind = st["kind"]
        if kind in ("road",) or str(st["name"]).startswith(("gatestreet", "square")):
            return
        pts = st["pts"]
        sl = arc_lengths(pts)
        total = sl[-1]
        half = st["width"] / 2.0
        smith = st["name"] == "smiths_street"
        for side in (1, -1):
            if kind == "wallroad" and side == 1:
                pass
            s = r.uniform(1.0, 6.0)
            fails = 0
            while s < total - 3.0:
                p0, t = point_at(pts, sl, s)
                n = left(t)
                out_n = mul(n, side)
                if kind == "wallroad":
                    # only the side that faces the city
                    if in_poly(add(p0, mul(out_n, 30.0)), self.wall) is False or self.wall_dist(add(p0, mul(out_n, 4.0))) < self.wall_dist(p0):
                        s += 12.0
                        continue
                u = self.radial(p0)
                wl = self.wealth(p0, kind, r)
                cls = "S" if smith else self.choose_class(wl, r)
                if smith:
                    cls = "M" if r.random() < 0.8 else "S"
                (w0, w1), (d0, d1), fl, (h0, h1) = SIZES[cls]
                w = r.uniform(w0, w1)
                d = r.uniform(d0, d1)
                if smith:
                    w, d = r.uniform(8.5, 11.0), r.uniform(8.0, 10.5)
                # a block narrower than the plot: the depth shrinks when the next street is close (see house_ok retries)
                placed = False
                for attempt in range(3):
                    sc = s + w / 2.0
                    pc, tc = point_at(pts, sl, sc)
                    nc = mul(left(tc), side)
                    setback = r.uniform(0.5, 1.6)
                    c = add(pc, mul(nc, half + setback + d / 2.0))
                    yaw_jit = math.radians(r.uniform(-2.5, 2.5))
                    tt = (tc[0] * math.cos(yaw_jit) - tc[1] * math.sin(yaw_jit), tc[0] * math.sin(yaw_jit) + tc[1] * math.cos(yaw_jit))
                    corners = rect_corners(c, tt, w, d)
                    if self.house_ok(corners, c, max(w, d)):
                        if r.random() < self.keep_prob(u, kind) or smith:
                            front = mul(left(tt), -side)    # the facade looks at the street
                            rec = {"c": c, "corners": corners, "w": w, "d": d, "cls": cls, "front": front,
                                   "floors": r.choice(fl), "h0": r.uniform(h1 * 0.0 + h0, h1), "seed": r.randrange(1 << 30),
                                   "smith": smith}
                            if not smith and u > 0.3 and r.random() < 0.0035:
                                rec["smith"] = True
                                rec["w"], rec["d"] = max(w, 8.5), max(d, 8.0)
                            self.hash.add(rec, c, max(w, d))
                            self.houses.append(rec)
                        placed = True
                        break
                    w *= 0.82
                    d *= 0.85
                    if w < 4.6 or d < 4.6:
                        break
                if placed:
                    s += w + r.uniform(0.2, 1.4) + (r.uniform(2.5, 4.0) if r.random() < 0.06 else 0.0)
                else:
                    s += 3.5

    def wall_dist(self, p):
        if not hasattr(self, "sd"):
            self._field()
        c = int((p[0] - self.f0[0]) / self.fstep)
        r = int((p[1] - self.f0[1]) / self.fstep)
        if not (0 <= r < self.sd.shape[0] and 0 <= c < self.sd.shape[1]):
            return -1.0
        return abs(self.sd[r, c])

    def plan_houses(self):
        r = random.Random(SEED + 3)
        order = sorted(self.streets, key=lambda s: {"avenue": 0, "ring": 1, "street": 2, "lane": 3, "alley": 4, "wallroad": 5}.get(s["kind"], 6))
        for st in order:
            self.fill_street(st, r)
        n = len(self.houses)
        counts = {c: sum(1 for h in self.houses if h["cls"] == c) for c in "SML"}
        print("houses:", n, counts, "smithies:", sum(1 for h in self.houses if h["smith"]))

    def run(self):
        self.plan_gates()
        self.plan_precinct()
        self.setup_radial()
        self.plan_avenues()
        self.plan_rings()
        self.plan_markers()
        self.plan_markets()
        self.plan_palaces()
        self.plan_smith_street()
        self.grow_lanes()
        self.plan_houses()



# ---------------------------------------------------------------- stalls, compounds, districts, output

AWNINGS = 7   # colours of the cloth, the builder knows them: red, green, teal, ochre, white, blue, striped red/white


class Finish(Builder):
    def plan_stalls(self):
        r = random.Random(SEED + 4)
        for m in self.markets:
            t, n, c = m["t"], left(m["t"]), m["c"]
            w, d = m["w"], m["d"]
            stalls = []
            row_gap, col_gap = 6.2, 4.4
            nrows = int((d - 6.0) // row_gap)
            ncols = int((w - 6.0) // col_gap)
            for i in range(nrows):
                v = (i - (nrows - 1) / 2.0) * row_gap
                for j in range(ncols):
                    u = (j - (ncols - 1) / 2.0) * col_gap
                    if m["kind"] == "great" and u * u + v * v < 15.0 * 15.0:
                        continue          # the open square where the people of the market stand
                    if r.random() < 0.12:
                        continue
                    p = add(add(c, mul(t, u + r.uniform(-0.4, 0.4))), mul(n, v + r.uniform(-0.4, 0.4)))
                    face = 1 if v < 0 else -1
                    stalls.append({"x": round(p[0], 2), "z": round(p[1], 2),
                                   "front": [round(n[0] * face, 3), round(n[1] * face, 3)],
                                   "awning": r.randrange(AWNINGS), "goods": r.randrange(6), "seed": r.randrange(1 << 30)})
            m["stalls"] = stalls
            # a well on one side of the square
            wp = add(c, mul(t, w / 2 - 6.0))
            m["well"] = [round(wp[0], 2), round(wp[1], 2)]
            print("market", m["name"], len(stalls), "stalls")

    def plan_compounds(self):
        """The farm and working buildings round each palace, in the palace's frame: u along the front, v from the front
        (v = -D/2, towards the street) into the compound."""
        for pal in self.palaces:
            r = random.Random(SEED + 5 + len(pal["name"]))
            W, D = pal["W"], pal["D"]
            items = []

            def put(kind, u, v, w, d, h, ang=0.0, **kw):
                rec = {"type": kind, "u": round(u, 2), "v": round(v, 2), "w": round(w, 2), "d": round(d, 2), "h": round(h, 2),
                       "ang": round(ang, 3), "seed": r.randrange(1 << 30)}
                rec.update(kw)
                items.append(rec)

            royal = pal["name"] == "uruk_palace"
            if royal:
                pw, pd = 78.0, 58.0         # the palace proper
                pv = 6.0                    # its centre (v)
                put("palace", 0.0, pv, pw, pd, 9.0, variant="royal", court=[30.0, 24.0])
                pal["anchor_uv"] = [0.0, pv]
            else:
                pw, pd = 142.0, 109.0       # Sin-kashid: 142 m long, 102-116 m wide, big courtyard on the east side
                pv = 8.0
                put("palace", 0.0, pv, pw, pd, 8.0, variant="sinkashid", court=[52.0, 40.0], court_u=18.0)
                pal["anchor_uv"] = [18.0, pv]
            # enclosure wall with the gate in the middle of the front
            put("enclosure", 0.0, 0.0, W - 4.0, D - 4.0, 5.0, gate_w=11.0)
            # the forecourt: guards' houses and stables along the front
            front_v = -D / 2 + 14.0
            for side in (-1, 1):
                for k in range(3):
                    put("stable" if k < 2 else "gatehouse", side * (22.0 + k * 20.0), front_v, 16.0, 9.0, 4.2, 0.0)
            # kitchens, bakeries, breweries and workshops on the west flank, granaries on the east flank
            west0 = -W / 2 + 12.0
            west1 = -pw / 2 - 12.0
            east0 = pw / 2 + 12.0
            east1 = W / 2 - 10.0
            vv = -D / 2 + 34.0
            row = 0
            while vv < D / 2 - 30.0:
                for (u0, u1, kind_pool) in ((west0, west1, ("kitchen", "bakery", "brewery", "workshop", "store")),):
                    if u1 - u0 > 14.0:
                        k = r.choice(kind_pool)
                        wd = r.uniform(14.0, 20.0)
                        put(k, (u0 + u1) / 2 + r.uniform(-3, 3), vv, wd, r.uniform(9.0, 13.0), r.uniform(3.8, 4.8), 0.0)
                vv += 17.0
                row += 1
            # round granaries and long storehouses on the east flank
            vv = -D / 2 + 30.0
            while vv < D / 2 - 26.0:
                u = east0 + 5.0
                n_silos = int((east1 - east0) // 11.0)
                for k in range(max(1, n_silos)):
                    put("granary", u + k * 11.0, vv, 7.0, 7.0, r.uniform(6.2, 7.4))
                vv += 14.0
            put("storehouse", (east0 + east1) / 2, D / 2 - 36.0, east1 - east0 - 2.0, 11.0, 4.6)
            # the back: pens, a threshing floor, haystacks, the garden terrace and palms
            back = D / 2 - 14.0
            for k in range(4):
                put("pen", -W / 2 + 22.0 + k * 26.0, back, 20.0, 14.0, 1.1, 0.0, animals=r.choice(["sheep", "cattle", "goats"]))
            put("threshing", pw / 2 + 30.0 if royal else -W / 2 + 40.0, back - 40.0, 20.0, 20.0, 0.12)
            for k in range(5):
                put("haystack", (-W / 2 + 90.0 if royal else 60.0) + k * 9.0, back - 28.0 + r.uniform(-2, 2), 5.0, 5.0, 4.0)
            if royal:
                put("garden", 0.0, D / 2 - 12.0, 64.0, 16.0, 6.0)      # the hanging garden: a stepped terrace of palms
            put("well", -W / 2 + 30.0, -4.0, 2.4, 2.4, 1.0)
            for k in range(14):
                u = r.uniform(-W / 2 + 10.0, W / 2 - 10.0)
                v = r.uniform(-D / 2 + 30.0, D / 2 - 10.0)
                if abs(u) < pw / 2 + 2.0 and abs(v - pv) < pd / 2 + 2.0:
                    continue
                put("palm", u, v, 1.0, 1.0, r.uniform(7.0, 10.0))
            pal["items"] = items
            t = (math.cos(math.radians(pal["yaw"])), math.sin(math.radians(pal["yaw"])))
            a = frame_to_world(pal["c"], pal["yaw"], *pal["anchor_uv"])
            pal["anchor"] = [round(a[0], 2), round(a[1], 2)]
            print("palace", pal["name"], len(items), "items, anchor", pal["anchor"])

    # ---- the court of the precinct and the places that are fixed by the datadisk
    def plan_fixed_places(self):
        self.fixed = {
            "uruk": (0.0, 0.0),
            "eanna_temple": offset_bearing((0, 0), 43.0, 217.0),
            "ziggurat_of_anu": offset_bearing((0, 0), 34.0, 244.0),
        }
        self.fixed["ishtar_temple"] = offset_bearing(self.fixed["eanna_temple"], 225.0, 45.0)

    # ---- districts
    def partition(self, max_houses=700):
        x0, x1, z0, z1 = -1500.0, 1400.0, -1700.0, 1500.0
        leaves = []

        def count(rect):
            a, b, c, d = rect
            n = sum(1 for h in self.houses if a <= h["c"][0] < b and c <= h["c"][1] < d)
            n += sum(f["weight"] for f in getattr(self, "fields", []) if a <= f["c"][0] < b and c <= f["c"][1] < d)
            return n

        stack = [(x0, x1, z0, z1)]
        while stack:
            rect = stack.pop()
            a, b, c, d = rect
            n = count(rect)
            if n == 0:
                leaves.append(rect)
                continue
            if n > max_houses and min(b - a, d - c) > 260.0:
                if (b - a) >= (d - c):
                    mid = (a + b) / 2
                    stack += [(a, mid, c, d), (mid, b, c, d)]
                else:
                    mid = (c + d) / 2
                    stack += [(a, b, c, mid), (a, b, mid, d)]
            else:
                leaves.append(rect)
        self.leaves = sorted(leaves)


    # ---- the places that only mark a spot
    def plan_marker_places(self):
        fixed = self.fixed
        avenue_ishtar = self.streets[self.gates[0]["avenue"]]
        sl = arc_lengths(avenue_ishtar["pts"])
        p, t = point_at(avenue_ishtar["pts"], sl, 150.0)
        wall_marker = add(p, mul(left(t), -(AVENUE_W / 2 + 12.0)))
        west = [g for g in self.gates if g["name"] == "west"][0]
        wr = None
        for s in self.streets:
            if s["name"] and str(s["name"]).startswith("wallroad"):
                for q in s["pts"]:
                    if length(sub(q, tuple(west["pos"]))) < 90.0 and 50.0 < length(sub(q, tuple(west["pos"]))):
                        wr = q
                        break
            if wr:
                break
        gw = add(wr, mul(unit(sub(self.centre, wr)), 14.0)) if wr else add(tuple(west["pos"]), mul(tuple(west["out"]), -60.0))
        royal = [p_ for p_ in self.palaces if p_["name"] == "uruk_palace"][0]
        tn = left((math.cos(math.radians(royal["yaw"])), math.sin(math.radians(royal["yaw"]))))
        tomb = add(royal["c"], mul(tn, royal["D"] / 2 + 44.0))
        # new characters appear here, on the avenue 80 m inside the Ishtar Gate, clear of the walls of the gate (the avenue is 14 m wide)
        gp, gt = point_at(avenue_ishtar["pts"], sl, 44.0)
        ishtar = self.gates[0]
        # New characters appear in the open 125 m before the Ishtar Gate, 23 m beyond the end of the Processional Way, in
        # sight of the gate and well away from its walls; the avenue square inside the gate stays free of houses.
        outside = add(tuple(ishtar["pos"]), mul(tuple(ishtar["out"]), 125.0))
        self.marker_places = {
            "city_gate": outside,
            "uruk_wall": wall_marker,
            "great_wall_uruk": gw,
            "royal_tombs": tomb,
            "ziggurat_of_uruk": (80.0, -215.0),
            "ziggurat_of_ishtar": (30.0, -170.0),
        }
        for k, v in self.marker_places.items():
            self.reserve_circle(v, 16.0, k)
        self.reserve_circle(gp, 16.0, "gate_square")
        tt = tuple(ishtar["out"])
        nn = left(tt)
        self.guard_patrol = [[round(tt[0] * a + nn[0] * l, 1), round(tt[1] * a + nn[1] * l, 1)] for a, l in ((-35, 4), (10, 4), (10, -4), (-35, -4))]
        print("city_gate", [round(v, 1) for v in outside], "guard patrol", self.guard_patrol)
        # the Ishtar ziggurat stands west of the Ishtar temple's anchor, its stairs facing it
        anchor = fixed["ishtar_temple"]
        centre = (62.0, -112.0)
        face = unit(sub(anchor, centre))
        self.ishtar_ziggurat = {"c": centre, "front": face, "size": 44.0}
        self.reserve_poly("ziggurat", rect_corners(centre, left(face), 52.0, 52.0), "ziggurat_ishtar")

    def plan_court_ways(self):
        """Paved ways inside the precinct from the entrances to the feet of the ziggurats."""
        ent = self.entrances
        anu_foot = (161.0, -171.0)
        ish_foot = add(self.ishtar_ziggurat["c"], mul(self.ishtar_ziggurat["front"], 22.0 + 12.0))
        # entrance nearest to the south: the Ishtar avenue's
        south = max(range(len(ent)), key=lambda i: ent[i][1])
        west = min(range(len(ent)), key=lambda i: ent[i][0])
        self.add_street("way", 9.0, smooth([ent[south], (112.0, -62.0), (118.0, -100.0), (146.0, -140.0), anu_foot], 2), name="way_anu")
        self.add_street("way", 8.0, smooth([ent[west], (10.0, -138.0), ish_foot], 1), name="way_ishtar")
        self.add_street("way", 6.0, [ish_foot, (118.0, -118.0), (118.0, -100.0)], name="way_link")

    def plan_eanna_buildings(self):
        """The Great Court (an orchard with its pool) and the large halls of the precinct, as the excavations show them,
        turned like the Anu terrace and set in the free ground of the court."""
        yaw = 41.0
        t = (math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
        n = left(t)
        specs = [("great_court", 34.0, 34.0, 0.0), ("pillar_hall", 40.0, 17.0, 6.5), ("stone_cone", 30.0, 24.0, 5.0),
                 ("limestone_hall", 42.0, 27.3, 6.2)]
        self.eanna_buildings = []
        anu_c = tuple(self.outlines["ziggurat_centre"])
        for name, w, d, h in specs:
            best = None
            for gx in range(-120, 260, 6):
                for gz in range(-300, 0, 6):
                    c = (float(gx), float(gz))
                    corners = rect_corners(c, t, w, d)
                    if not all(in_poly(q, self.precinct) and poly_dist(q, self.precinct) > 4.0 for q in corners):
                        continue
                    if length(sub(c, anu_c)) < 46.0 + max(w, d) * 0.4 or length(sub(c, self.ishtar_ziggurat["c"])) < 34.0 + max(w, d) * 0.4:
                        continue
                    if any(rects_overlap(corners, b["corners"], 6.0) for b in self.eanna_buildings):
                        continue
                    ok = True
                    for q in corners + [c] + [lerp(corners[i], corners[(i + 1) % 4], 0.5) for i in range(4)]:
                        if self.street_gap(q)[0] < 7.0 and any(sx["kind"] == "way" for sx in self.streets if sx["id"] == self.street_gap(q)[1]):
                            ok = False
                            break
                        if length(sub(q, (147.0, -159.0))) < 12.0 or length(sub(q, self.fixed["ishtar_temple"])) < 12.0:
                            ok = False
                            break
                    if not ok:
                        continue
                    score = length(sub(c, self.centre))
                    if best is None or score < best[0]:
                        best = (score, c, corners)
            if best is None:
                print("no room in the court for", name)
                continue
            self.eanna_buildings.append({"name": name, "c": best[1], "yaw": yaw, "w": w, "d": d, "h": h, "corners": best[2]})
        print("eanna:", [(b["name"], [round(v) for v in b["c"]]) for b in self.eanna_buildings])


    # ---- the irrigated fields and canals of the outskirts (the magnetogram of the excavation shows a rectilinear net of
    #      canals and furrows inside the wall): a grid of canals turned like the survey, fields in the cells that are free
    def free_ground(self, p, house_margin=14.0):
        if not self.inside(p, WALL_CLEAR + 16.0) or self.ground.wet(*p):
            return False
        if self.radial(p) < 0.40:
            return False
        if self.zone_hit(p, 12.0) is not None:
            return False
        if self.street_gap(p)[0] < 11.0:
            return False
        for h in self.hash.near(p, 40.0):
            if length(sub(p, h["c"])) < 0.5 * max(h["w"], h["d"]) + house_margin:
                return False
        return True

    def plan_fields(self):
        r = random.Random(SEED + 6)
        theta = math.radians(-20.0)    # the net of the magnetogram: one family runs NNW-SSE, the way the water flows
        t = (math.cos(theta), math.sin(theta))
        n = left(t)
        xs = [p[0] for p in self.wall]
        zs = [p[1] for p in self.wall]
        corners = [(x, z) for x in (min(xs), max(xs)) for z in (min(zs), max(zs))]
        ab = [(dot(c_, t), dot(c_, n)) for c_ in corners]
        a0, a1 = min(q[0] for q in ab), max(q[0] for q in ab)
        b0, b1 = min(q[1] for q in ab), max(q[1] for q in ab)

        def lines(lo, hi):
            v = lo + r.uniform(0, 60)
            out = []
            while v < hi:
                out.append(v)
                v += r.uniform(130.0, 210.0)
            return out

        al, bl = lines(a0, a1), lines(b0, b1)
        self.canals = []
        step = 6.0

        def run_line(fixed, lo, hi, along_a):
            run = []
            v = lo
            while v <= hi:
                p = add(mul(t, fixed), mul(n, v)) if along_a else add(mul(t, v), mul(n, fixed))
                if self.free_ground(p, 10.0):
                    run.append(p)
                else:
                    if len(run) >= 6:
                        self.canals.append({"pts": run, "width": 3.2})
                    run = []
                v += step
            if len(run) >= 6:
                self.canals.append({"pts": run, "width": 3.2})

        for a in al:
            run_line(a, b0, b1, True)
        for b in bl:
            run_line(b, a0, a1, False)
        # the water comes from the north-west (the Middle Babylonian watercourses run from there to the south-east, past Uruk):
        # the main canal is the line of the net that enters the wall furthest to the north-west, with a water gate in the wall
        best = None
        for a in al:
            v = b0
            prev_in = False
            while v <= b1:
                p = add(mul(t, a), mul(n, v))
                ins = self.inside(p, 0.0)
                if ins and not prev_in:
                    score = dot(sub(p, self.centre), (-0.7, -0.7))      # towards the north-west
                    if best is None or score > best[0]:
                        best = (score, a, v, p)
                    break
                prev_in = ins
                v += 4.0
        self.main_canal = None
        if best is not None:
            _, a_main, v_in, p_in = best
            # outside: 260 m from the wall; inside: down the line to the first obstacle (a house, the sacred precinct, a street)
            pts = []
            v = v_in - 260.0
            while v < v_in + 4.0:
                pts.append(add(mul(t, a_main), mul(n, v)))
                v += 6.0
            v = v_in + 4.0
            while v < b1:
                q = add(mul(t, a_main), mul(n, v))
                if not self.inside(q, 0.0) or self.ground.wet(*q):
                    break
                if v - v_in > 80.0 and (self.zone_hit(q, 10.0) is not None or self.street_gap(q)[0] < 8.0
                                         or any(length(sub(q, h["c"])) < 0.5 * max(h["w"], h["d"]) + 8.0 for h in self.hash.near(q, 40.0))):
                    break
                pts.append(q)
                v += 6.0
            self.main_canal = {"pts": pts, "width": 6.0, "entry": p_in}
            idx = min(range(len(self.wall)), key=lambda i: length(sub(self.wall[i], p_in)))
            nrm = self.wall_outward(idx)
            tan = unit(left(nrm))
            self.gates.append({"name": "water", "index": idx, "pos": [round(self.wall[idx][0], 2), round(self.wall[idx][1], 2)],
                               "out": [round(nrm[0], 4), round(nrm[1], 4)], "tangent": [round(tan[0], 4), round(tan[1], 4)],
                               "height": round(self.wall_h[idx], 2)})
            # the main canal must cross the wall at the water gate: bend its first stretch onto the gate
            print("water gate at", self.gates[-1]["pos"], "main canal", len(pts), "points")
        # thin the canals out on the dry north-east side
        self.canals = [c for c in self.canals if not (dot(sub(c["pts"][len(c["pts"]) // 2], self.centre), (0.7, -0.7)) > 500.0 and r.random() < 0.6)]
        # fields in the cells between neighbouring canal lines
        self.fields = []
        kinds = ["grain"] * 62 + ["orchard"] * 22 + ["fallow"] * 16
        for i in range(len(al) - 1):
            for j in range(len(bl) - 1):
                inset = 4.0
                wa, wb = al[i + 1] - al[i] - 2 * inset, bl[j + 1] - bl[j] - 2 * inset
                if wa < 30 or wb < 30:
                    continue
                ca, cb = (al[i] + al[i + 1]) / 2, (bl[j] + bl[j + 1]) / 2
                ok = True
                for u in range(-1, 2):
                    for v in range(-1, 2):
                        q = add(mul(t, ca + u * wa / 2.2), mul(n, cb + v * wb / 2.2))
                        if not self.free_ground(q, 6.0):
                            ok = False
                            break
                    if not ok:
                        break
                if not ok:
                    continue
                fc = add(mul(t, ca), mul(n, cb))
                ne = dot(sub(fc, self.centre), (0.7, -0.7))      # the north-east was dry; the irrigated land lay to the south-west
                sw = dot(sub(fc, self.centre), (-0.7, 0.7))
                if ne > 400.0 and r.random() < 0.55:
                    continue
                kind = "fallow" if (ne > 300.0 and r.random() < 0.6) else r.choice(kinds if sw < 600.0 else ["grain"] * 70 + ["orchard"] * 30)
                self.fields.append({"c": fc, "t": t, "w": wa, "d": wb, "kind": kind, "seed": r.randrange(1 << 30),
                                    "weight": 6 if kind == "orchard" else 1})
        print("canals:", len(self.canals), "runs,", round(sum(arc_lengths(c["pts"])[-1] for c in self.canals)), "m; fields:",
              len(self.fields), {k: sum(1 for f in self.fields if f["kind"] == k) for k in ("grain", "orchard", "fallow")})

    def finalize(self):
        self.plan_fields()
        self.plan_stalls()
        self.plan_compounds()
        self.partition()
        self.assign_districts()

    def run(self):
        self.plan_gates()
        self.plan_precinct()
        self.plan_fixed_places()
        self.setup_radial()
        self.plan_avenues()
        self.plan_rings()
        self.plan_markers()
        self.plan_markets()
        self.plan_palaces()
        self.plan_marker_places()
        self.plan_court_ways()
        self.plan_eanna_buildings()
        self.plan_smith_street()
        self.grow_lanes()
        self.plan_houses()
        self.finalize()

    # ---- districts: a model and a place for each leaf that has something in it
    def assign_districts(self):
        marks = list(self.fixed.values()) + list(self.marker_places.values()) + [m["c"] for m in self.markets] \
            + [p["anchor"] for p in self.palaces]

        def leaf_of(p):
            for k, (a, b, c, d) in enumerate(self.leaves):
                if a <= p[0] < b and c <= p[1] < d:
                    return k
            return None

        content = {k: 0 for k in range(len(self.leaves))}
        for h in self.houses:
            content[leaf_of(h["c"])] += 1
        for s in self.streets:
            for a, b in zip(s["pts"], s["pts"][1:]):
                k = leaf_of(lerp(a, b, 0.5))
                if k is not None:
                    content[k] += 0.05
        for f in self.fields:
            k = leaf_of(f["c"])
            if k is not None:
                content[k] += f["weight"]
        for m in self.markets:
            if m["name"] != "uruk_market":
                k = leaf_of(m["c"])
                if k is not None:
                    content[k] += len(m["stalls"]) * 0.2
        self.districts = []
        for k, (a, b, c, d) in enumerate(self.leaves):
            if content[k] < 1.0:
                continue
            anchor = ((a + b) / 2, (c + d) / 2)
            for ring_ in range(0, 40):
                moved = False
                for m in marks:
                    if length(sub(anchor, m)) < 70.0:
                        anchor = add(m, mul(unit(sub(anchor, m)) if length(sub(anchor, m)) > 1 else (1.0, 0.0), 75.0))
                        moved = True
                if not moved:
                    break
            for other in self.districts:
                if length(sub(anchor, other["anchor"])) < 20.0:
                    anchor = add(anchor, (25.0, 25.0))
            self.districts.append({"leaf": k, "rect": [a, b, c, d], "anchor": [round(anchor[0], 1), round(anchor[1], 1)]})
        # names by the quarter of the city they lie in
        names = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]
        seen = {}
        for dist in self.districts:
            v = sub(((dist["rect"][0] + dist["rect"][1]) / 2, (dist["rect"][2] + dist["rect"][3]) / 2), self.centre)
            ang = math.degrees(math.atan2(v[0], -v[1])) % 360.0
            if length(v) < 260.0:
                sector = "centre"
            else:
                sector = names[int((ang + 22.5) // 45) % 8]
            seen[sector] = seen.get(sector, 0) + 1
            dist["sector"] = sector
            dist["number"] = seen[sector]
        for k, dist in enumerate(self.districts):
            dist["id"] = "uruk_quarter_%02d" % (k + 1)
        print("districts:", len(self.districts), [(d["id"], d["sector"], d["number"]) for d in self.districts])

    def write(self, path=OUT):
        def r1(p):
            return [round(p[0], 1), round(p[1], 1)]
        plan = {
            "version": 1, "seed": SEED, "anchor_note": "client local frame, metres from the anchor of Uruk: x east, z south",
            "gates": self.gates,
            "precinct": [r1(p) for p in self.precinct],
            "centre": r1(self.centre),
            "anu": {"c": self.anu and [round(self.anu[0], 1), round(self.anu[1], 1)], "yaw_deg": 41.0},
            "ishtar_ziggurat": {"c": r1(self.ishtar_ziggurat["c"]),
                                "front": [round(self.ishtar_ziggurat["front"][0], 4), round(self.ishtar_ziggurat["front"][1], 4)],
                                "size": self.ishtar_ziggurat["size"]},
            "fixed": {k: r1(v) for k, v in self.fixed.items()},
            "marker_places": {k: r1(v) for k, v in self.marker_places.items()},
            "streets": [{"kind": s["kind"], "width": s["width"], "name": s["name"], "pts": [r1(p) for p in s["pts"]]} for s in self.streets],
            "house_fields": ["x", "z", "front_x", "front_z", "w", "d", "class(0 poor,1 middle,2 rich)", "floors", "h0", "seed", "smithy"],
            "houses": [[round(h["c"][0], 2), round(h["c"][1], 2), round(h["front"][0], 3), round(h["front"][1], 3), round(h["w"], 2),
                        round(h["d"], 2), "SML".index(h["cls"]), h["floors"], round(h["h0"], 2), h["seed"], 1 if h["smith"] else 0]
                       for h in self.houses],
            "canals": [{"width": c["width"], "pts": [r1(q) for q in c["pts"]]} for c in self.canals]
            + ([{"width": self.main_canal["width"], "main": True, "pts": [r1(q) for q in self.main_canal["pts"]]}] if self.main_canal else []),
            "fields": [{"c": r1(f["c"]), "t": [round(f["t"][0], 4), round(f["t"][1], 4)], "w": round(f["w"], 1), "d": round(f["d"], 1),
                        "kind": f["kind"], "seed": f["seed"]} for f in self.fields],
            "eanna_buildings": [{"name": b["name"], "c": r1(b["c"]), "yaw": b["yaw"], "w": b["w"], "d": b["d"], "h": b["h"]}
                                for b in self.eanna_buildings],
            "markets": [{"name": m["name"], "kind": m["kind"], "c": r1(m["c"]), "t": [round(m["t"][0], 4), round(m["t"][1], 4)],
                         "w": m["w"], "d": m["d"], "stalls": m["stalls"], "well": m["well"]} for m in self.markets],
            "palaces": [{"name": p["name"], "c": r1(p["c"]), "yaw": p["yaw"], "W": p["W"], "D": p["D"], "anchor": p["anchor"],
                         "items": p["items"]} for p in self.palaces],
            "districts": self.districts,
        }
        with open(path, "w") as handle:
            json.dump(plan, handle, separators=(",", ":"))
        print("wrote", path, os.path.getsize(path) // 1024, "KiB")


    # ---- the places of the datadisk that carry the models, and their names
    def write_places(self):
        def loc(pt):
            return round(math.degrees(math.atan2(pt[0], -pt[1])) % 360.0, 3), round(math.hypot(pt[0], pt[1]), 1)

        sector_cs = {"north": "severní", "northeast": "severovýchodní", "east": "východní", "southeast": "jihovýchodní", "south": "jižní",
                     "southwest": "jihozápadní", "west": "západní", "northwest": "severozápadní", "centre": "střední"}
        en, cs = [], []
        lines = ["# Generated by tools/build_city.py from the plan of the city (tools/data/uruk_city.json): the palace of Sin-kashid and the",
                 "# quarters of Uruk, each a place at an exact spot (`locate` with a tolerance of one metre) whose model holds the streets",
                 "# and houses of that quarter. Do not edit; change the plan and run the script again (see research/CITY.md).", ""]
        pal = [p for p in self.palaces if p["name"] == "sinkashid_palace"][0]
        b, d = loc(pal["anchor"])
        lines += ["- id: sinkashid_palace", "  kind: building", "  name_key: place.sinkashid_palace", "  parent: uruk", "  radius_m: 30",
                  "  # The palace of Sin-kashid, king of Uruk (about 1865-1833 BC), west of the sacred precinct, as the excavation shows it:",
                  "  # 142 by 109 m, a low mud-brick building on a base of baked brick, rooms in the west half and round the sides, the great",
                  "  # courtyard in the east half (the place is its middle) and a hall with six columns; farm buildings stand round it.",
                  "  locate: {from: uruk, bearing_deg: %s, distance_m: %s, tolerance_m: 2}" % (b, d),
                  "  structure:", "    model: media/models/architecture/uruk_sinkashid.glb",
                  "    collision: media/models/architecture/uruk_sinkashid_collision.glb", "    visible_m: 3300",
                  "  requires:", "    max_slope_deg: 30", ""]
        en.append("place.sinkashid_palace: Palace of Sin-kashid")
        cs.append("place.sinkashid_palace: Palác Sin-kašida")
        for dist in self.districts:
            ax, az = dist["anchor"]
            b, dd = loc((ax, az))
            a, bb, c, e = dist["rect"]
            far = max(math.hypot(x - ax, z - az) for x in (a, bb) for z in (c, e))
            vis = 3300      # the whole city can be seen from its gate (and from the approach from orbit)
            lines += ["- id: %s" % dist["id"], "  kind: landmark", "  name_key: place.%s" % dist["id"], "  parent: uruk", "  radius_m: 1",
                      "  locate: {from: uruk, bearing_deg: %s, distance_m: %s, tolerance_m: 1}" % (b, dd),
                      "  structure:", "    model: media/models/architecture/%s.glb" % dist["id"],
                      "    collision: media/models/architecture/%s_collision.glb" % dist["id"], "    visible_m: %d" % vis,
                      "  requires:", "    max_slope_deg: 60", ""]
            nm = {"centre": "central"}.get(dist["sector"], dist["sector"])
            en.append("place.%s: Uruk, %s quarter%s" % (dist["id"], nm, "" if dist["number"] == 1 else " %d" % dist["number"]))
            cs.append("place.%s: Uruk, %s čtvrť%s" % (dist["id"], sector_cs[dist["sector"]], "" if dist["number"] == 1 else " %d" % dist["number"]))
        with open(os.path.join(ROOT, "places", "uruk_city.yaml"), "w") as handle:
            handle.write("\n".join(lines))
        for lang, entries in (("en", en), ("cs", cs)):
            path = os.path.join(ROOT, "i18n", lang + ".yaml")
            text = open(path, encoding="utf-8").read()
            begin, end = "# >>> uruk city (generated by tools/build_city.py)", "# <<< uruk city"
            block = begin + "\n" + "\n".join(entries) + "\n" + end + "\n"
            if begin in text:
                a = text.index(begin)
                b2 = text.index(end) + len(end) + 1
                text = text[:a] + block + text[b2:]
            else:
                text = text.rstrip("\n") + "\n\n" + block
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
        print("wrote places/uruk_city.yaml and the names in i18n")


    # ---- the mask of built and tilled ground: no wild trees, rocks, flowers or animals stand there (server: terrain.clear)
    def write_clear_mask(self, path=None, step=4.0, margin=2.5):
        from PIL import ImageDraw
        size = int(EXTENT / step)
        img = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(img)

        def px(p):
            return ((p[0] + EXTENT / 2) / step, (p[1] + EXTENT / 2) / step)

        def line(pts, width):
            q = [px(p) for p in pts]
            w = max(1, int(round((width + 2 * margin) / step)))
            draw.line(q, fill=255, width=w, joint="curve")
            for a in (q[0], q[-1]):
                draw.ellipse((a[0] - w / 2, a[1] - w / 2, a[0] + w / 2, a[1] + w / 2), fill=255)

        def poly(corners, grow=0.0):
            c = (sum(p[0] for p in corners) / len(corners), sum(p[1] for p in corners) / len(corners))
            grown = [add(p, mul(unit(sub(p, c)), grow + margin)) for p in corners]
            draw.polygon([px(p) for p in grown], fill=255)

        for st in self.streets:
            line(st["pts"], st["width"])
        for h in self.houses:
            poly(h["corners"], 0.0)
        for c in self.canals:
            line(c["pts"], c["width"] + 3.6)
        if self.main_canal:
            line(self.main_canal["pts"], self.main_canal["width"] + 3.6)
        for f in self.fields:
            poly(rect_corners(f["c"], f["t"], f["w"], f["d"]), 0.0)
        for m in self.markets:
            poly(m["poly"], 2.0)
        for pal in self.palaces:
            poly(pal["poly"], 4.0)
        poly(self.precinct, 2.0)
        # the wall and the gates: the people walk there, wild growth is not wanted at the foot either
        line(self.wall + [self.wall[0]], 7.0 + 6.0)
        for g in self.gates:
            line([tuple(g["pos"]), add(tuple(g["pos"]), mul(tuple(g["out"]), 40.0)), add(tuple(g["pos"]), mul(tuple(g["out"]), -40.0))], 12.0)
        from PIL import ImageFilter
        img = img.filter(ImageFilter.MaxFilter(7))        # the yards between the houses too (12 m)
        # the way to the Ishtar Gate and the place where new characters appear: nothing grows there
        draw = ImageDraw.Draw(img)
        ishtar = self.gates[0]
        spawn = self.marker_places["city_gate"]
        q0, q1 = px(tuple(ishtar["pos"])), px(spawn)
        draw.line([q0, q1], fill=255, width=int(30 / step))
        r = 45.0 / step
        draw.ellipse((q1[0] - r, q1[1] - r, q1[0] + r, q1[1] + r), fill=255)
        path = path or os.path.join(ROOT, "media", "terrain", "uruk_clear.png")
        img.save(path, optimize=True)
        cleared = sum(1 for v in img.getdata() if v) * step * step / 10000.0
        print("wrote", os.path.relpath(path, ROOT), os.path.getsize(path) // 1024, "KiB,", round(cleared), "ha cleared")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    ap.add_argument("--window", nargs=4, type=float)
    args = ap.parse_args()
    city = Finish()
    city.run()
    city.write()
    city.write_places()
    city.write_clear_mask()
    if args.preview:
        preview(city, args.preview, window=args.window, dpi=70, size=12)


if __name__ == "__main__":
    main()
