#!/usr/bin/env python3
"""Build the terrain patch of the hunter's water-hole: a small pond on the steppe, with the spawn on its bank.

The steppe around the hunter's spawn is flat floodplain that the coarse planet map calls "river": the server
let the hunter drink there while the client drew only dry ground. The patch makes the water real, so what is
drawn is what the server walks on: the pond is water (a character that steps in swims and drowns until a dry
shore, as everywhere), the bank is dry land, and drinking is possible only within reach of the pond.

Heights are relative to the anchor (the spawn): 0x8000 is the anchor's height, one step is a decimetre; the water
mask is 0 for dry land, otherwise the surface in decimetres above the anchor. The frame is the client's local one:
+x east, +z south, row 0 of the PNGs the most northern row (see tools/build_landscape.py).

Usage: tools/build_waterhole.py      (needs Pillow and numpy; writes media/terrain/hunter_waterhole_*.png)
"""
import math
import pathlib

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
TERRAIN = ROOT / "media" / "terrain"
SIZE = 400                 # one pixel per metre, the extent_m of the place
POND_RADIUS_M = 40.0       # where the bowl meets the plain
POND_DEPTH_M = 2.2         # below the plain, in the middle
WATER_LEVEL_M = -0.4       # the surface, relative to the plain
BANK_DISTANCE_M = 4.0      # from the anchor to the water's edge
BEARING_DEG = 315.0        # the pond lies north-west of the spawn


def value_noise(size, cell, seed, amplitude):
    """Smooth, seeded value noise: the bank is not a perfect circle."""
    rng = np.random.default_rng(seed)
    lattice = rng.uniform(-1.0, 1.0, (size // cell + 3, size // cell + 3))
    yy, xx = np.mgrid[0:size, 0:size] / cell
    y0, x0 = yy.astype(int), xx.astype(int)
    fy, fx = yy - y0, xx - x0
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    top = lattice[y0, x0] * (1 - fx) + lattice[y0, x0 + 1] * fx
    bottom = lattice[y0 + 1, x0] * (1 - fx) + lattice[y0 + 1, x0 + 1] * fx
    return (top * (1 - fy) + bottom * fy) * amplitude


def write_png16(path, grid):
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(np.clip(grid, 0, 65535).astype(np.uint16), mode="I;16")
    image.save(path)
    print(f"  {path.relative_to(ROOT)}: {image.size[0]}x{image.size[1]}, {path.stat().st_size} bytes")


def build():
    # The edge of the water is where the bowl is WATER_LEVEL_M deep: radius * sqrt(1 - level / depth).
    shore = POND_RADIUS_M * math.sqrt(1.0 - WATER_LEVEL_M / -POND_DEPTH_M)
    distance = shore + BANK_DISTANCE_M
    angle = math.radians(BEARING_DEG)
    centre_x = distance * math.sin(angle)      # bearing 0 is north, 90 east
    centre_z = -distance * math.cos(angle)     # +z is south
    xx, zz = np.meshgrid(np.arange(SIZE) - (SIZE - 1) / 2.0, np.arange(SIZE) - (SIZE - 1) / 2.0)
    wobble = value_noise(SIZE, 24, 7, 0.12 * POND_RADIUS_M)
    radius = np.hypot(xx - centre_x, zz - centre_z) + wobble
    bowl = -POND_DEPTH_M * np.clip(1.0 - (radius / POND_RADIUS_M) ** 2, 0.0, 1.0)
    ground = bowl + value_noise(SIZE, 16, 11, 0.08)          # a little unevenness all over
    # The anchor itself stays at its placed height, so the spawn does not float or sink.
    ground -= ground[SIZE // 2, SIZE // 2]
    heightmap = np.round(ground * 10.0).astype(np.int32) + 32768
    water = np.zeros((SIZE, SIZE), dtype=np.int32)
    wet = ground < WATER_LEVEL_M
    water[wet] = round(WATER_LEVEL_M * 10.0) + 32768
    write_png16(TERRAIN / "hunter_waterhole_height.png", heightmap)
    write_png16(TERRAIN / "hunter_waterhole_water.png", water)
    nearest = np.hypot(xx[wet], zz[wet]).min()
    print(f"  pond centre ({centre_x:+.0f}, {centre_z:+.0f}) m, {int(wet.sum())} m2 of water, nearest {nearest:.1f} m from the spawn, "
          f"relief {ground.min():+.1f} to {ground.max():+.1f} m")


if __name__ == "__main__":
    build()
