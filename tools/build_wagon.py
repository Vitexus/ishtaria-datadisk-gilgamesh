#!/usr/bin/env python3
"""Writes media/models/wagon.glb and media/models/caravan.glb: an ox cart with its carter and a camel with its driver.

    python3 tools/build_wagon.py [PUBLIC_ZIP]

0 A.D. (Wildfire Games, CC BY-SA 3.0) has no cart with its draught animals in one piece (its traders are an actor made of a
cart, a horse and a driver), so the engine's one character is put together here from parts that already have clips:

  wagon.glb   the wooden cart of 0 A.D. (props/wooden_cart, from public.zip), two oxen of 0 A.D.
              (assets/zeroad/fauna/bull.glb, Idle and Walk) yoked in front of it and facing the way it goes, and the carter
              of Uruk's crowd (media/models/crowd_caravaneer.glb) walking beside them;
  caravan.glb a camel of 0 A.D. (camel.glb) led by the same carter.

The model's front is +Z, its origin the middle of the ground under it. The clips are Idle and Walk of all the parts, joined by
tools/compose_glb.py.

The cart mesh of 0 A.D. is one piece and is turned about 21 degrees about the vertical against its own axle, so it is
straightened first (the axle along the cart's width), tilted about the hubs so that the shafts rest on the yokes, and set so
that the lowest point of the wheels touches the ground (y = 0). The two wheels are cut out of the mesh and become nodes of
their own, centred on their hubs, which turn in the Walk clip: one turn per loop of the oxen's Walk clip (about 3.7 m of road
at the carter's pace of 1.1 m/s made half as fast again by the road, against a wheel circumference of about 4 m); in Idle
they stand still.
"""
import importlib.util
import io
import os
import sys
import zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CLIENT = os.path.join(ROOT, "..", "ishtaria-client")
sys.path.insert(0, HERE)
from compose_glb import Part, accessor_array, merge, read_glb, write  # noqa: E402

PUBLIC = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/games/0ad/mods/public/public.zip"
MODELS = os.path.join(ROOT, "media", "models")
TMP = os.path.join(ROOT, "build", "wagon")
os.makedirs(TMP, exist_ok=True)

spec = importlib.util.spec_from_file_location("zeroad_structures", os.path.join(CLIENT, "tools", "zeroad-structures.py"))
structures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structures)

BULL = os.path.join(CLIENT, "assets", "zeroad", "fauna", "bull.glb")
CAMEL = os.path.join(CLIENT, "assets", "zeroad", "fauna", "camel.glb")
CARTER = os.path.join(MODELS, "crowd_caravaneer.glb")

# ---- the cart: its mesh and wood texture from 0 A.D., a Y-up model lying along X with its shafts towards -X
with zipfile.ZipFile(PUBLIC) as store:
    positions, faces, normals, uvs = structures.read_pmd(store.read("art/meshes/props/wooden_cart.dae.cached.pmd"))
    image = Image.open(io.BytesIO(store.read("art/textures/skins/props/wood_c.png.cached.dds"))).convert("RGBA")
image.thumbnail((512, 512), Image.LANCZOS)
png = io.BytesIO()
image.save(png, "PNG", optimize=True)
pos, norms, tex = structures.authored(positions, faces, normals, uvs, False)   # a triangle soup: three vertices per face
pos, norms = pos.astype(float), norms.astype(float)
triangles = pos.reshape(-1, 3, 3)

# The pieces of the mesh: triangles sharing a vertex belong together.  The two biggest are the rims of the wheels; the
# small pieces whose middle lies at a rim's middle are its hub and spokes.
parent = list(range(len(triangles)))


def find(item):
    while parent[item] != item:
        parent[item] = parent[parent[item]]
        item = parent[item]
    return item


first = {}
for number, triangle in enumerate(triangles):
    for vertex in triangle:
        key = tuple(np.round(vertex, 3))
        if key in first:
            parent[find(number)] = find(first[key])
        else:
            first[key] = number
pieces = {}
for number in range(len(triangles)):
    pieces.setdefault(find(number), []).append(number)
pieces = sorted(pieces.values(), key=len, reverse=True)
rims = pieces[:2]
hubs = [triangles[rim].reshape(-1, 3).mean(axis=0) for rim in rims]
wheel_triangles = []
for rim, hub in zip(rims, hubs):
    members = list(rim)
    for piece in pieces[2:]:
        if np.linalg.norm(triangles[piece].reshape(-1, 3).mean(axis=0) - hub) < 0.1:
            members += piece
    wheel_triangles.append(sorted(members))
assert not set(wheel_triangles[0]) & set(wheel_triangles[1])

# Straighten: turn about the vertical so that the line through the hubs lies along Z.
axle = hubs[1] - hubs[0]
if axle[2] < 0:
    axle = -axle
turn = np.arctan2(-axle[0], axle[2])
ct, st = np.cos(turn), np.sin(turn)
middle = (hubs[0] + hubs[1]) / 2


def turned(points, vectors=False):
    rel = points - (0 if vectors else middle)
    x = rel[:, 0] * ct + rel[:, 2] * st
    z = -rel[:, 0] * st + rel[:, 2] * ct
    return np.stack([x, rel[:, 1], z], axis=1) + (0 if vectors else middle)


pos, norms = turned(pos), turned(norms, True)
hubs = [turned(hub[None])[0] for hub in hubs]
if hubs[0][2] > hubs[1][2]:                      # wheel 0 is the one on the -Z side
    hubs.reverse()
    wheel_triangles.reverse()
print("cart turned %.1f degrees about the vertical; hubs at %s" % (np.degrees(turn), [h.round(3).tolist() for h in hubs]))

# Harnessed, the shafts rest on the yokes of the oxen: the cart is tilted about its hubs (the wheels do not move, being
# discs about the hubs), and then set on the ground by the lowest point of the wheels.
PITCH = np.radians(-24.0)
c, s_ = np.cos(PITCH), np.sin(PITCH)
pivot = np.array([hubs[0][0], hubs[0][1]])


def pitched(points, vectors=False):
    rel = points[:, :2] - (0 if vectors else pivot)
    out = np.stack([rel[:, 0] * c - rel[:, 1] * s_, rel[:, 0] * s_ + rel[:, 1] * c], axis=1) + (0 if vectors else pivot)
    return np.concatenate([out, points[:, 2:]], axis=1)


pos, norms = pitched(pos), pitched(norms, True)
for number in range(2):
    hubs[number] = np.concatenate([pitched(hubs[number][None, :2])[0], hubs[number][2:]])
wheel_mask = np.zeros(len(triangles), dtype=bool)
for members in wheel_triangles:
    wheel_mask[members] = True
soup = pos.reshape(-1, 3, 3)
radius = max(float(np.hypot(soup[members][:, :, 0] - hubs[n][0], soup[members][:, :, 1] - hubs[n][1]).max())
             for n, members in enumerate(wheel_triangles))
lowest = float(soup[wheel_mask][:, :, 1].min())
shift = np.array([-(pos[:, 0].min() + pos[:, 0].max()) / 2, -lowest, -(hubs[0][2] + hubs[1][2]) / 2])
pos = pos + shift
hubs = [hub + shift for hub in hubs]
soup = pos.reshape(-1, 3, 3)
print("wheel radius %.3f m, lowest point of the wheels %.3f m above the ground" % (radius, float(soup[wheel_mask][:, :, 1].min())))


def mesh_glb(path, selection, origin=np.zeros(3)):
    """Writes the triangles `selection` (indices) of the cart, with `origin` taken as the zero of their coordinates."""
    flat = np.concatenate([np.arange(3 * n, 3 * n + 3) for n in selection])
    open(path, "wb").write(structures.glb((pos[flat] - origin).astype("<f4"), norms[flat].astype("<f4"), tex[flat], png.getvalue()))


body_path = os.path.join(TMP, "cart_body.glb")
mesh_glb(body_path, [n for n in range(len(triangles)) if not wheel_mask[n]])
extent = np.ptp(pos, axis=0)
print("cart: extent %s" % extent.round(2))

DURATION = None
document, blob = read_glb(BULL)
for animation in document["animations"]:
    if animation["name"] == "Walk":
        DURATION = float(accessor_array(document, blob, animation["samplers"][0]["input"]).reshape(-1)[-1])


def spinning(path, hub):
    """Gives the one node of the wheel glb its place (the hub) and a Walk clip: one turn about the axle (+Z, which rolls the
    cart towards its shafts at -X) in DURATION seconds."""
    document, blob = read_glb(path)
    document["nodes"][0]["translation"] = [float(v) for v in hub]
    angles = np.linspace(0.0, 2 * np.pi, 5)              # every quarter turn: a quaternion cannot be interpolated over more
    times = np.linspace(0.0, DURATION, 5).astype("<f4")
    values = np.stack([np.zeros(5), np.zeros(5), np.sin(angles / 2), np.cos(angles / 2)], axis=1).astype("<f4")
    accessors = []
    for array, kind, extra in ((times, "SCALAR", {"min": [0.0], "max": [float(times[-1])]}), (values, "VEC4", {})):
        data = array.tobytes()
        document["bufferViews"].append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
        blob += data + b"\0" * (-len(data) % 4)
        document["accessors"].append({"bufferView": len(document["bufferViews"]) - 1, "componentType": 5126, "count": 5, "type": kind, **extra})
        accessors.append(len(document["accessors"]) - 1)
    document["animations"] = [{"name": "Walk", "samplers": [{"input": accessors[0], "output": accessors[1], "interpolation": "LINEAR"}],
                               "channels": [{"sampler": 0, "target": {"node": 0, "path": "rotation"}}]}]
    document["buffers"][0]["byteLength"] = len(blob)
    write(path, (document, blob))


wheel_paths = []
for number, members in enumerate(wheel_triangles):
    path = os.path.join(TMP, "cart_wheel_%d.glb" % number)
    mesh_glb(path, members, hubs[number])
    spinning(path, hubs[number])
    wheel_paths.append(path)

OX = 0.4            # a bull of 0 A.D. is 3.5 units at the shoulder: 1.4 m
CAMEL_SCALE = 0.32  # a camel is 5 units at the hump: about 1.7 m

half = float(extent[0]) / 2
# the cart turned so that its shafts (-X) point to +Z
yoke = half - 0.5               # the middle of the oxen: their necks (0.55 m ahead of the middle of the body, the bull of
                                # 0 A.D. being 2.2 m long) lie under the tips of the shafts
wagon = [
    Part(body_path, yaw_deg=90.0, name="cart", clips=False),
    Part(wheel_paths[0], yaw_deg=90.0, name="wheel", clips=True),
    Part(wheel_paths[1], yaw_deg=90.0, name="wheel", clips=True),
    # the bull of 0 A.D. faces -Z; turned half a circle it faces the way the cart goes (+Z)
    Part(BULL, translation=(-0.55, 0.0, yoke), yaw_deg=180.0, scale=OX, name="ox"),
    Part(BULL, translation=(0.55, 0.0, yoke), yaw_deg=180.0, scale=OX, name="ox"),
    Part(CARTER, translation=(-1.55, 0.0, yoke), name="carter"),
]
write(os.path.join(MODELS, "wagon.glb"), merge(wagon, name="wagon"))
caravan = [
    # like the bull, the camel of 0 A.D. faces -Z: turned half a circle it faces the way the caravan goes (+Z), towards its driver
    Part(CAMEL, translation=(0.0, 0.0, 0.0), yaw_deg=180.0, scale=CAMEL_SCALE, name="camel"),
    Part(CARTER, translation=(-1.1, 0.0, 1.5), name="driver"),
]
write(os.path.join(MODELS, "caravan.glb"), merge(caravan, name="caravan"))
for name in ("wagon", "caravan"):
    print("%s.glb: %d bytes" % (name, os.path.getsize(os.path.join(MODELS, name + ".glb"))))
