#!/usr/bin/env python3
"""Writes media/models/wagon.glb and media/models/caravan.glb: an ox cart with its carter and a camel with its driver.

    python3 tools/build_wagon.py [PUBLIC_ZIP]

0 A.D. (Wildfire Games, CC BY-SA 3.0) has no cart with its draught animals in one piece (its traders are an actor made of a
cart, a horse and a driver), so the engine's one character is put together here from parts that already have clips:

  wagon.glb   the wooden cart of 0 A.D. (props/wooden_cart, from public.zip) drawn at rest, two oxen of 0 A.D.
              (assets/zeroad/fauna/bull.glb, Idle and Walk) yoked in front of it, and the carter of Uruk's crowd
              (media/models/crowd_caravaneer.glb) walking beside them;
  caravan.glb a camel of 0 A.D. (camel.glb) led by the same carter.

The model's front is +Z, its origin the middle of the ground under it. The clips are Idle and Walk of all the parts, joined by
tools/compose_glb.py. The wheels of the cart do not turn.
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
from compose_glb import Part, merge, write  # noqa: E402

PUBLIC = sys.argv[1] if len(sys.argv) > 1 else "/usr/share/games/0ad/mods/public/public.zip"
MODELS = os.path.join(ROOT, "media", "models")
TMP = os.path.join(ROOT, "build", "wagon")
os.makedirs(TMP, exist_ok=True)

spec = importlib.util.spec_from_file_location("zeroad_structures", os.path.join(CLIENT, "tools", "zeroad-structures.py"))
structures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(structures)

# ---- the cart: its mesh and wood texture from 0 A.D., a Y-up model lying along X with its shafts towards -X
with zipfile.ZipFile(PUBLIC) as store:
    positions, faces, normals, uvs = structures.read_pmd(store.read("art/meshes/props/wooden_cart.dae.cached.pmd"))
    image = Image.open(io.BytesIO(store.read("art/textures/skins/props/wood_c.png.cached.dds"))).convert("RGBA")
image.thumbnail((512, 512), Image.LANCZOS)
png = io.BytesIO()
image.save(png, "PNG", optimize=True)
pos, norms, tex = structures.authored(positions, faces, normals, uvs, False)
# The cart as it is stands with its shafts on the ground; harnessed, they rest on the yokes of the oxen. It is turned about
# its axle (the middle of its wheels) so that the shafts rise to the height of the yoke, the wheels staying on the ground.
AXLE = np.array([-0.02, 0.8])
PITCH = np.radians(-24.0)
c, s_ = np.cos(PITCH), np.sin(PITCH)


def pitched(points, vectors=False):
    rel = points[:, :2] - (0 if vectors else AXLE)
    turned = np.stack([rel[:, 0] * c - rel[:, 1] * s_, rel[:, 0] * s_ + rel[:, 1] * c], axis=1)
    return np.concatenate([turned + (0 if vectors else AXLE), points[:, 2:]], axis=1).astype("<f4")


pos, norms = pitched(pos), pitched(norms, True)
cart_path = os.path.join(TMP, "cart.glb")
open(cart_path, "wb").write(structures.glb(pos, norms, tex, png.getvalue()))
extent = np.ptp(pos, axis=0)
print("cart: extent %s" % extent.round(2))

BULL = os.path.join(CLIENT, "assets", "zeroad", "fauna", "bull.glb")
CAMEL = os.path.join(CLIENT, "assets", "zeroad", "fauna", "camel.glb")
CARTER = os.path.join(MODELS, "crowd_caravaneer.glb")
OX = 0.4            # a bull of 0 A.D. is 3.5 units at the shoulder: 1.4 m
CAMEL_SCALE = 0.32  # a camel is 5 units at the hump: about 1.7 m

half = float(extent[0]) / 2
# the cart turned so that its shafts (-X) point to +Z
cart = Part(cart_path, translation=(0.0, 0.19, 0.0), yaw_deg=90.0, name="cart", clips=False)
yoke = half + 0.9               # the middle of the oxen: their rear is just behind where the shafts end
wagon = [
    cart,
    Part(BULL, translation=(-0.55, 0.0, yoke), scale=OX, name="ox"),
    Part(BULL, translation=(0.55, 0.0, yoke), scale=OX, name="ox"),
    Part(CARTER, translation=(-1.55, 0.0, yoke), name="carter"),
]
write(os.path.join(MODELS, "wagon.glb"), merge(wagon, name="wagon"))
caravan = [
    Part(CAMEL, translation=(0.0, 0.0, 0.0), scale=CAMEL_SCALE, name="camel"),
    Part(CARTER, translation=(-1.1, 0.0, 1.5), name="driver"),
]
write(os.path.join(MODELS, "caravan.glb"), merge(caravan, name="caravan"))
for name in ("wagon", "caravan"):
    print("%s.glb: %d bytes" % (name, os.path.getsize(os.path.join(MODELS, name + ".glb"))))
