"""The walls of Uruk along their real outline, built to match the Ishtar Gate (see ishtar_gate.py), with the gate.

    blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls media/models/architecture/uruk_walls.glb
    blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls_collision media/models/architecture/uruk_walls_collision.glb

The circuit follows the OpenStreetMap outline of the wall of Uruk (8.6 km, 520 ha), written to tools/data/uruk_outlines.json
by tools/build_landscape.py in the client's local frame: 18 m high and 7 m thick, glazed blue brick like the curtain walls of
the inner gate, with stepped battlements and a tower every ~75 m. The wall follows the relief of the terrain patch (the
outline in the JSON carries the terrain height at every point); 6 m of foundation lie below the ground. The Ishtar Gate
(outer gate, courtyard, inner gate and the 80 m Processional Way) stands in the south wall where the wall is straightest
and the terrain flattest; four flights of stairs inside climb to the wall walk. The Early Dynastic ziggurat of Anu (ziggurat.py)
is part of the same model, on its excavated terrace: a place can show only one building and the datadisk cannot put a
child place at a bearing, so the exact spot (OSM footprint, turned like the survey) is kept here.

Metres. The origin is the middle of the Ishtar Gate on the outline of the wall and z = 0 the terrain height there, so the
model stands on the terrain wherever the datadisk puts it: `offset_m` is the position of the gate from the anchor of the
place (the middle of the OSM site), printed at the end. Blender X is east and Y is north, so the glTF z axis points
south like the client's local z: x_local = X, z_local = -Y.
The collision model has no battlements, animals or textures; it is what the server walks on.
"""
import json
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

OUTLINES = os.path.join(HERE, "..", "..", "tools", "data", "uruk_outlines.json")
WALL_H = 18.0       # as the curtain walls of the inner gate
THICK = 7.0
Y_OUT = 22.0        # outer face of the gate's curtain walls in the gate's own frame
STUB = 44.0         # where the curtain walls of the gate end
TOWER = 9.0
TOWER_H = WALL_H + 4.0
FOUNDATION = 6.0    # the wall reaches this far below the terrain
TOWER_EVERY = 75.0
MERLON_EVERY = 6.0
ANU_YAW_DEG = 41.0       # the terrace is turned like the surveyed footprint; the stairs face the Eanna precinct
ROWS_NEAR_GATE = 300.0   # animal rows on the wall this far from the gate stubs, plain glaze elsewhere
PROCESSION = 80.0
PLAN = os.path.join(HERE, "..", "..", "tools", "data", "uruk_city.json")
PASS_W = 8.0             # the passage of the other gates
GATE_TOWER = 12.0        # width of a tower of the other gates
GATE_GAP = PASS_W / 2 + GATE_TOWER   # the wall is cut this far to each side of the middle of such a gate
GATE_H = 9.0             # clear height of the passage


def v3(x, y, z):
    return Vector((x, y, z))


class Ring:
    """The wall outline: points (Blender X, Y, terrain height) of a closed outline, counter-clockwise seen from above,
    so that the outside is to the right of the direction of travel."""

    def __init__(self, points):
        self.p = [Vector((x, -z)) for x, z, _ in points[:-1]]
        self.h = [h for _, _, h in points[:-1]]
        self.n = len(self.p)
        area = sum(self.p[i].x * self.p[(i + 1) % self.n].y - self.p[(i + 1) % self.n].x * self.p[i].y for i in range(self.n))
        if area < 0:
            raise SystemExit("the outline must run counter-clockwise (x east, y north)")

    def tangent(self, i, span=3):
        d = self.p[(i + span) % self.n] - self.p[(i - span) % self.n]
        return d.normalized()

    @staticmethod
    def outward(t):
        return Vector((t.y, -t.x))


def pick_gate(ring):
    """The point of the south wall that is straightest and has the flattest terrain."""
    best = None
    for i in range(ring.n):
        t = ring.tangent(i, 3)
        out = ring.outward(t)
        if out.y > -0.6:
            continue
        bend = 0.0
        flat = 0.0
        for k in range(-4, 5):
            q = ring.p[(i + k) % ring.n]
            bend += abs((q - ring.p[i]).dot(out))
            flat += abs(ring.h[(i + k) % ring.n] - ring.h[i])
        # the street leads 80 m out of the gate: the terrain there should not rise to the wall top
        score = bend + 8.0 * flat
        if best is None or score < best[0]:
            best = (score, i)
    return best[1]


def rbox(model, c, t, sl, sw, z0, z1, mat_wall, mat_top, rng=None):
    """A block without a bottom, sl long along t, sw wide across it, centred at c."""
    s = Vector((-t.y, t.x))
    corners = [c - t * sl / 2 - s * sw / 2, c + t * sl / 2 - s * sw / 2, c + t * sl / 2 + s * sw / 2, c - t * sl / 2 + s * sw / 2]
    for i in range(4):
        a, b = corners[i], corners[(i + 1) % 4]
        d = (b - a).normalized()
        model.wall([v3(a.x, a.y, z0), v3(b.x, b.y, z0), v3(b.x, b.y, z1), v3(a.x, a.y, z1)], mat_wall, d,
                   rng.random() * 8 if rng else 0.0, v3(d.y, -d.x, 0))
    model.top([v3(q.x, q.y, z1) for q in corners], mat_top)


def move_gate(model, ring, gate, datum):
    """The gate complex was built in its own frame (street along -Y, wall line at y = Y_OUT); put it into the wall."""
    t = ring.tangent(gate, 3)
    out = ring.outward(t)
    origin = ring.p[gate]
    for v in model.bm.verts:
        gx, gy = v.co.x, v.co.y
        w = origin + t * gx + out * (Y_OUT - gy)
        v.co = Vector((w.x, w.y, v.co.z))
    return t, out, origin


def chain_around_gate(ring, gate, gap):
    """Indices of the wall, going from the gate's forward stub round the whole circuit to its backward stub. The cut
    points are interpolated on the outline `gap` metres from the gate; returns [(position, height)]."""
    n = ring.n
    pts = [(ring.p[(gate + k) % n], ring.h[(gate + k) % n]) for k in range(n + 1)]
    # arc length from the gate going forward
    arc = [0.0]
    for a, b in zip(pts, pts[1:]):
        arc.append(arc[-1] + (b[0] - a[0]).length)
    total = arc[-1]

    def at(s):
        for k in range(n):
            if arc[k] <= s <= arc[k + 1]:
                f = (s - arc[k]) / (arc[k + 1] - arc[k])
                return pts[k][0].lerp(pts[k + 1][0], f), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f
        raise ValueError(s)

    chain = [at(gap)]
    chain += [pts[k] for k in range(n) if gap < arc[k] < total - gap]
    chain.append(at(total - gap))
    return chain, arc, total


def arc_chain(ring, i, j, gap_i, gap_j):
    """The wall from gate i to the next gate j (going forward), cut `gap_i` and `gap_j` metres from the gates;
    returns [(position, height)] and the length of the chain."""
    n = ring.n
    count = (j - i) % n or n
    pts = [(ring.p[(i + k) % n], ring.h[(i + k) % n]) for k in range(count + 1)]
    arc = [0.0]
    for a, b in zip(pts, pts[1:]):
        arc.append(arc[-1] + (b[0] - a[0]).length)
    total = arc[-1]

    def at(s):
        for k in range(count):
            if arc[k] <= s <= arc[k + 1]:
                f = (s - arc[k]) / (arc[k + 1] - arc[k])
                return pts[k][0].lerp(pts[k + 1][0], f), pts[k][1] + (pts[k + 1][1] - pts[k][1]) * f
        raise ValueError(s)

    chain = [at(gap_i)]
    chain += [pts[k] for k in range(count) if gap_i < arc[k] < total - gap_j]
    chain.append(at(total - gap_j))
    return chain, total - gap_i - gap_j


WATER_PASS = 5.0         # the water gate: the main canal enters under the wall here
WATER_TOWER = 8.0
WATER_GAP = WATER_PASS / 2 + WATER_TOWER
WATER_H = 4.6


def minor_gate(model, ring, idx, datum, collision, rng, water=False):
    """A plain gate of the wall: two towers of glazed brick 12 m wide with a passage of 8 m between them, a lintel bridging it at
    the height of the wall walk, stepped battlements on top. The wall is cut GATE_GAP metres to each side of the middle."""
    t = ring.tangent(idx, 3)
    out = ring.outward(t)
    origin = ring.p[idx]
    z = ring.h[idx] - datum
    centre = origin - out * (THICK / 2)
    depth = THICK + 6.0
    pass_w, tower_w, pass_h = (WATER_PASS, WATER_TOWER, WATER_H) if water else (PASS_W, GATE_TOWER, GATE_H)
    top_h = WALL_H + (3.0 if water else 8.0)
    for sx in (-1, 1):
        c = centre + t * (sx * (pass_w / 2 + tower_w / 2))
        rbox(model, c, t, tower_w, depth, z - FOUNDATION, z + top_h, "blueglaze", "bakedbrick", rng)
        if not collision:
            rbox(model, c, t, tower_w - 2.5, depth - 2.5, z + top_h, z + top_h + 1.8, "bakedbrick", "bakedbrick")
    rbox(model, centre, t, pass_w + 0.2, THICK + 1.0, z + pass_h, z + WALL_H + 2.0, "blueglaze", "bakedbrick", rng)
    if water:
        return t, out
    if not collision:
        count = 4
        for q in range(count):
            f = (q + 0.5) / count - 0.5
            cc = centre + t * (f * PASS_W) + out * (THICK / 2 - 0.5)
            rbox(model, cc, t, 1.4, 1.0, z + WALL_H + 2.0 - 0.3, z + WALL_H + 3.6, "blueglaze", "bakedbrick")
        # the roadway through the passage
        a = origin + out * 6.0
        b = origin - out * (THICK + 6.0)
        p = [a + t * (PASS_W / 2), a - t * (PASS_W / 2), b - t * (PASS_W / 2), b + t * (PASS_W / 2)]
        model.top([v3(q.x, q.y, z + 0.05) for q in p], "stonepaving")
    return t, out


def circuit(model, ring, gate, datum, gate_pos, rng, collision, chain=None, chain_len=None, rows_start=False, rows_end=False,
            stair_starts=(90.0,)):
    rows = ["bull", "dragon", "bull"]
    if chain is None:
        chain, _, total = chain_around_gate(ring, gate, STUB)
        chain_len = total - 2 * STUB
        rows_start = rows_end = True
        stair_starts = (90.0, 520.0)
    total = chain_len + 2 * STUB
    m = len(chain)
    seg_n = []
    for k in range(m - 1):
        d = (chain[k + 1][0] - chain[k][0]).normalized()
        seg_n.append(Ring.outward(d))
    # mitred outward normals at the vertices of the chain
    vert_n = [seg_n[0]]
    for k in range(1, m - 1):
        mean = (seg_n[k - 1] + seg_n[k]).normalized()
        vert_n.append(mean)
    vert_n.append(seg_n[-1])
    scale = []
    for k in range(m):
        ref = seg_n[min(k, m - 2)]
        scale.append(min(2.5, 1.0 / max(0.4, vert_n[k].dot(ref))))
    outer = [chain[k][0] for k in range(m)]
    inner = [chain[k][0] - vert_n[k] * THICK * scale[k] for k in range(m)]
    base = [chain[k][1] - datum - FOUNDATION for k in range(m)]
    top = [chain[k][1] - datum + WALL_H for k in range(m)]

    arc_from_gate = 0.0
    for k in range(m - 1):
        a, b = outer[k], outer[k + 1]
        length = (b - a).length
        t = (b - a) / length
        out = seg_n[k]
        ia, ib = inner[k], inner[k + 1]
        plain = "blueglaze"
        model.jitter = 0.92 + rng.random() * 0.08
        model.wall([v3(a.x, a.y, base[k]), v3(b.x, b.y, base[k + 1]), v3(b.x, b.y, top[k + 1]), v3(a.x, a.y, top[k])],
                   plain, t, rng.random() * 6, v3(out.x, out.y, 0))
        model.wall([v3(ib.x, ib.y, base[k + 1]), v3(ia.x, ia.y, base[k]), v3(ia.x, ia.y, top[k]), v3(ib.x, ib.y, top[k + 1])],
                   plain, -t, rng.random() * 6, v3(-out.x, -out.y, 0))
        model.jitter = 1.0
        model.top([v3(a.x, a.y, top[k]), v3(b.x, b.y, top[k + 1]), v3(ib.x, ib.y, top[k + 1]), v3(ia.x, ia.y, top[k])], "bakedbrick")
        if collision:
            continue
        # animal rows on the outer face near the gate, as on the gate itself
        near_gate = (rows_start and arc_from_gate < ROWS_NEAR_GATE) or (rows_end and chain_len - arc_from_gate < ROWS_NEAR_GATE)
        if near_gate and length > 6.0:
            mid = (chain[k][1] + chain[k + 1][1]) / 2 - datum
            G.animal_rows(model, a, t, out, length, mid + G.PLINTH + 0.4, rows, (t.x, t.y), rng, margin=1.0)
        # stepped battlements along the outer edge
        count = max(1, int(length / MERLON_EVERY))
        for q in range(count):
            f = (q + 0.5) / count
            c = a.lerp(b, f) - out * 0.5
            z = top[k] + (top[k + 1] - top[k]) * f
            rbox(model, c, t, 1.6, 1.0, z - 0.5, z + 1.6, "blueglaze", "bakedbrick")
        arc_from_gate += length

    # towers on the outer edge, every ~TOWER_EVERY metres and at the ends
    run = 0.0
    towers = 0
    for k in range(m):
        if k > 0:
            run += (chain[k][0] - chain[k - 1][0]).length
        if k == 0 or k == m - 1 or run >= TOWER_EVERY:
            run = 0.0
            ref = seg_n[min(k, m - 2)]
            t = Vector((-ref.y, ref.x))
            c = chain[k][0] - ref * 0.5
            z = chain[k][1] - datum
            rbox(model, c, t, TOWER, TOWER, z - FOUNDATION, z + TOWER_H, "blueglaze", "bakedbrick", rng)
            if not collision:
                rbox(model, c, t, TOWER - 2.5, TOWER - 2.5, z + TOWER_H, z + TOWER_H + 1.8, "bakedbrick", "bakedbrick")
            towers += 1
    print("circuit:", m - 1, "wall pieces,", towers, "towers, wall length", round(chain_len), "m")

    # stairs from the inside up to the wall walk, climbing away from the gate on both sides
    for direction in (1, -1):
        for start in stair_starts:
            s0 = start
            # find the chain position at arc s0 from the stub, either end
            arc = 0.0
            order = range(m - 1) if direction == 1 else range(m - 2, -1, -1)
            for k in order:
                a, b = (chain[k][0], chain[k + 1][0]) if direction == 1 else (chain[k + 1][0], chain[k][0])
                ha, hb = (chain[k][1], chain[k + 1][1]) if direction == 1 else (chain[k + 1][1], chain[k][1])
                length = (b - a).length
                if arc + length < s0 + 50.0 + 1e-6:
                    arc += length
                    continue
                break
            else:
                continue
            # straight run of 50 m from the cut: along the chain, flush with the inner face
            d = (b - a).normalized()
            out = Ring.outward(d)
            f = max(0.0, (s0 - arc) / length)
            origin = a.lerp(b, f) - out * (THICK + 1.5)
            z_start = (ha + (hb - ha) * f) - datum
            if f * length + 50.0 > length:
                continue
            z_end = (ha + (hb - ha) * ((f * length + 50.0) / length)) - datum
            Z.stairs(model, origin.x, origin.y, (d.x, d.y), 3.0, z_start, (z_end + WALL_H) - z_start, 50.0, rh=0.3)


def anu_ziggurat(model, rng, outlines, datum, collision=False):
    """The Anu ziggurat at the centre of its OSM footprint, on the lowest ground under it."""
    first = len(model.bm.verts)
    Z.anu(model, rng, detail=not collision)
    angle = math.radians(ANU_YAW_DEG)
    c, s = math.cos(angle), math.sin(angle)
    cx, cz = outlines["ziggurat_centre"]
    lift = outlines["ziggurat_base_h"] - datum
    for v in list(model.bm.verts)[first:]:
        x, y = v.co.x, v.co.y
        v.co = Vector((cx + x * c - y * s, -cz + x * s + y * c, v.co.z + lift))
    print("Anu ziggurat at local x=%.1f z=%.1f, %.1f m above the gate datum" % (cx, cz, lift))


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
    if which not in ("uruk_walls", "uruk_walls_collision"):
        raise SystemExit("unknown model " + which)
    collision = which == "uruk_walls_collision"
    rng = random.Random(7)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with open(OUTLINES) as handle:
        outlines = json.load(handle)
    ring = Ring(outlines["wall"])
    gate = pick_gate(ring)
    datum = ring.h[gate]
    with open(PLAN) as handle:
        plan = json.load(handle)
    gates = sorted(plan["gates"], key=lambda g: g["index"])
    ishtar = [g for g in gates if g["name"] == "ishtar"][0]
    if ishtar["index"] != gate:
        raise SystemExit("the Ishtar Gate of the plan (%d) is not the one chosen here (%d)" % (ishtar["index"], gate))
    model = Z.Model()
    G.gate_complex(model, rng)
    G.processional_way(model, rng, PROCESSION)
    t, outward, origin = move_gate(model, ring, gate, datum)
    # the wall in pieces from gate to gate
    for k, g in enumerate(gates):
        nxt = gates[(k + 1) % len(gates)]
        def gap_of(gt):
            return STUB if gt["name"] == "ishtar" else WATER_GAP if gt["name"] == "water" else GATE_GAP

        gap_i, gap_j = gap_of(g), gap_of(nxt)
        chain, chain_len = arc_chain(ring, g["index"], nxt["index"], gap_i, gap_j)
        circuit(model, ring, gate, datum, origin, rng, collision, chain, chain_len, g["name"] == "ishtar", nxt["name"] == "ishtar",
                (90.0, 520.0) if "ishtar" in (g["name"], nxt["name"]) else (60.0,))
    for g in gates:
        if g["name"] != "ishtar":
            minor_gate(model, ring, g["index"], datum, collision, rng, water=g["name"] == "water")
    anu_ziggurat(model, rng, outlines, datum, collision)
    if collision:   # no textures: the colours are all the server needs
        for name, spec in list(Z.MATERIALS.items()):
            Z.MATERIALS[name] = (None,) + spec[1:]
        for name, spec in list(G.Z.MATERIALS.items()):
            G.Z.MATERIALS[name] = (None,) + spec[1:]
    else:
        recompress()
    # re-centre on the gate: the model's origin is where its height is taken from the terrain
    for v in model.bm.verts:
        v.co.x -= origin.x
        v.co.y -= origin.y
    finish(model, out)
    print("gate at local x=%.1f z=%.1f, terrain %.2f m above the anchor" % (origin.x, -origin.y, datum))
    print("offset_m: [%.1f, %.1f]" % (origin.x, -origin.y))
    print("gate direction (outward) x=%.3f z=%.3f" % (outward.x, -outward.y))


if __name__ == "__main__":
    main()
