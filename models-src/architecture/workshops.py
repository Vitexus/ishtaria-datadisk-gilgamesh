"""Potter's yards for the Gilgamesh datadisk.

    blender -b --python models-src/architecture/workshops.py -- media/models/architecture

The open front of the shed faces the model's +Z (south in the plan, before yaw_deg). A yard holds a kiln,
jars and bowls drying in the sun, stacks of clay tablets and the baskets the servants carry to the temple
and the market. The smiths' yards are the workshops already standing on the smiths' street; their furnaces,
charcoal kilns and wood piles are built with the city (uruk_city.smithy).
"""
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import uruk_city as C  # noqa: E402
import ziggurat as Z  # noqa: E402

Z.MATERIALS["copper"] = (None, (0.72, 0.40, 0.22), 0.45, 0.85, 1.0)


class Flat:
    def height(self, x, z):
        return 0.0


def shed(ctx, col, w=8.5, d=6.2, h=3.6):
    """Three walls and a roof. The open front is +z."""
    corners = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    ctx.m.tint = (0.88, 0.78, 0.66)
    ctx.wall("mudbrick", corners[0], corners[1], -0.3, h, (0, -1))
    ctx.wall("mudbrick", corners[1], corners[2], -0.3, h, (1, 0), 2.4)
    ctx.wall("mudbrick", corners[3], corners[0], -0.3, h, (-1, 0), 4.8)
    ctx.top("mudbrick", corners, h)
    ctx.m.tint = (1, 1, 1)
    ctx.quad("door", [(*corners[3], 0), (*corners[2], 0), (*corners[2], h - 0.15), (*corners[3], h - 0.15)], (0, -1))
    col.prism(corners, -0.4, h * 0.55)
    return corners


def jar(ctx, c, z, scale=1.0):
    ctx.box("clay", "clay", c, (1, 0), (0, 1), 0.34 * scale, 0.34 * scale, z, z + 0.42 * scale)
    ctx.box("clay", "clay", c, (1, 0), (0, 1), 0.18 * scale, 0.18 * scale, z + 0.42 * scale, z + 0.58 * scale)


def tablet_stack(ctx, c, z, n=5):
    for k in range(n):
        ctx.box("clay", "clay", c, (1, 0), (0, 1), 0.28, 0.18, z + k * 0.035, z + (k + 1) * 0.03)


def basket(ctx, c, z):
    ctx.box("straw", "straw", c, (1, 0), (0, 1), 0.55, 0.42, z, z + 0.32)
    tablet_stack(ctx, c, z + 0.28, 3)


def pottery(ctx, col):
    """A potter's yard: the wheel and the jars under the shed, a kiln, tablets and baskets outside."""
    shed(ctx, col)
    # wheel and the vessels he is throwing
    ctx.box("wood", "wood", (0.2, -1.2), (1, 0), (0, 1), 0.7, 0.7, 0.0, 0.45)
    ctx.box("wood", "clay", (0.2, -1.2), (1, 0), (0, 1), 0.55, 0.55, 0.45, 0.52)
    jar(ctx, (0.2, -1.2), 0.52, 0.7)
    for i, x in enumerate((-2.6, -1.6, -0.7, 1.3, 2.2, 3.0)):
        jar(ctx, (x, -2.4), 0.0, 0.85 + (i % 3) * 0.12)
    for i, x in enumerate((-3.1, -2.2, -1.2, 1.6, 2.6)):
        ctx.box("clay", "clay", (x, -0.4), (1, 0), (0, 1), 0.42, 0.42, 0.0, 0.16 + (i % 2) * 0.05)
    # a bench of tablets the scribes, merchants and priests will write on
    ctx.box("wood", None, (2.4, -3.4), (1, 0), (0, 1), 2.2, 0.7, 0.0, 0.62)
    for k, x in enumerate((-0.7, -0.15, 0.4)):
        tablet_stack(ctx, (2.4 + x, -3.4), 0.62, 4 + k % 2)
    # kiln to one side of the yard, baskets of tablets waiting for the servants by the front
    kiln = (5.6, 1.4)
    ctx.m.tint = (0.95, 0.72, 0.58)
    ctx.box("bakedbrick", None, kiln, (1, 0), (0, 1), 2.2, 2.0, 0.0, 1.35)
    ctx.top("embers", [(kiln[0] - 0.45, kiln[1] - 0.4), (kiln[0] + 0.45, kiln[1] - 0.4),
                       (kiln[0] + 0.45, kiln[1] + 0.4), (kiln[0] - 0.45, kiln[1] + 0.4)], 1.37)
    ctx.box("bakedbrick", "charcoal", kiln, (1, 0), (0, 1), 0.7, 0.7, 1.35, 2.6)
    ctx.m.tint = (1, 1, 1)
    col.box(kiln, (1, 0), (0, 1), 2.2, 2.0, 0.0, 2.6)
    for i, (x, z) in enumerate(((-5.2, 2.2), (-4.2, 3.1), (-5.4, 3.4), (3.6, 2.6), (4.5, 3.3))):
        basket(ctx, (x, z), 0.0)
    # a low drying yard of bowls in front, where the potter stands
    for i in range(6):
        ctx.box("clay", "clay", (-2.2 + i * 0.7, 2.4), (1, 0), (0, 1), 0.36, 0.36, 0.0, 0.1)


def build(out_dir):
    ground = Flat()
    model = C.CM()
    ctx = C.Ctx(model, (0.0, 0.0), ground)
    col = C.Collision((0.0, 0.0), ground)
    pottery(ctx, col)
    path = os.path.join(out_dir, "uruk_pottery.glb")
    C.finish(model, path, quality=70, res=256)
    col.export(os.path.join(out_dir, "uruk_pottery_collision.glb"))


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    out = args[0] if args else os.path.join(HERE, "..", "..", "media", "models", "architecture")
    os.makedirs(out, exist_ok=True)
    build(os.path.abspath(out))


if __name__ == "__main__":
    main()
