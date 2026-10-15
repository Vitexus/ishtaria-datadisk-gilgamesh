#!/usr/bin/env python3
"""Draws textures/cone_wall.jpg: a seamless wall of clay cones laid in mud mortar, heads outwards (grey, olive, ochre and
brown cone heads in staggered rows, as the surviving Uruk cone walls look). Our own drawing: the palette and the way
the heads sit were taken from looking at a photograph, none of its pixels are used. Run with system Python
(numpy, scipy, Pillow):

    python3 models-src/architecture/make_cone_wall.py [seed]
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 1024
COLS, ROWS = 24, 24            # cones per tile: 2.4 m tile -> a head about 9 cm across
# (weight, colour) of a cone head: slate and grey stone-like clay, olive, ochre, brown, a few pale ones
DARK = [(52, 52, 52), (70, 70, 68), (88, 88, 84)]          # grey and black clay
BROWN = [(148, 108, 74), (132, 96, 66), (160, 120, 82)]
LIGHT = [(178, 150, 92), (198, 170, 118), (190, 162, 104), (206, 188, 148)]   # ochre and tan
STRAY = 0.05                   # share of cones laid in the wrong colour: the pattern was set by hand
MORTAR = np.array((142, 116, 84), np.float32)


def noise(rng, sigma, shape=(SIZE, SIZE)):
    """Seamless noise of one feature size, scaled to roughly -1..1."""
    n = gaussian_filter(rng.standard_normal(shape), sigma, mode="wrap")
    return (n / (np.abs(n).max() + 1e-9)).astype(np.float32)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    rng = np.random.default_rng(seed)
    px, py = SIZE / COLS, SIZE / ROWS
    aspect = px / py                                     # squares the rows so the heads stay round

    centres, radius = [], []
    for r in range(ROWS):
        for c in range(COLS):
            x = (c + (0.5 if r % 2 else 0.0) + 0.5) * px + rng.normal(0, px * 0.07)
            y = (r + 0.5) * py + rng.normal(0, py * 0.07)
            centres.append((x % SIZE, (y % SIZE) * aspect))
            radius.append(px * rng.uniform(0.50, 0.58))
    centres, radius = np.array(centres), np.array(radius)
    tree = cKDTree(centres, boxsize=(SIZE, SIZE * aspect))

    # pixels, bent by slow noise so the heads are not perfect circles
    yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    wx = xx + noise(rng, 16) * 5.0 + noise(rng, 6) * 2.0
    wy = yy + noise(rng, 16) * 5.0 + noise(rng, 6) * 2.0
    pts = np.stack([(wx % SIZE).ravel(), ((wy % SIZE) * aspect).ravel()], axis=1)
    dist, idx = tree.query(pts)
    dist, idx = dist.reshape(SIZE, SIZE), idx.reshape(SIZE, SIZE)
    rad = radius[idx]
    t = dist / rad                                        # 0 in the middle of a head, 1 at its rim

    # colour per cone: dark zigzag bands (like the back of an adder) cross a lighter field; cone (r, c) is index r*COLS+c
    period = COLS // 3
    cone = np.zeros((len(centres), 3), np.float32)
    for r in range(ROWS):
        zig = abs((r % 8) - 4)                               # triangle wave: the bands turn every four rows
        for c in range(COLS):
            m = (c + 0.5 * (r % 2) + zig) % period            # staggered rows keep the band continuous
            kind = DARK if m < 2.5 else BROWN if m < 3.5 else LIGHT
            if rng.random() < STRAY:
                kind = (DARK, BROWN, LIGHT, LIGHT)[rng.integers(4)]
            cone[r * COLS + c] = kind[rng.integers(len(kind))]
    head = cone[idx] * (1 + rng.normal(0, 0.06, len(centres)).astype(np.float32)[idx])[..., None]

    # a cone head is a slightly domed disc: lit from the upper left, dark at the rim, grainy clay
    dx = (wx - centres[idx, 0]); dy = (wy * aspect - centres[idx, 1])
    dx = (dx + SIZE / 2) % SIZE - SIZE / 2
    dy = (dy + SIZE * aspect / 2) % (SIZE * aspect) - SIZE * aspect / 2
    light = 1.0 + 0.10 * (-(dx + dy) / (rad * 1.4)) - 0.16 * np.clip(t, 0, 1) ** 3
    grain = 1 + 0.10 * noise(rng, 1.2) + 0.07 * noise(rng, 3.5)
    rings = 1 + 0.012 * np.sin(t * 15 + noise(rng, 6) * 4)
    shade = (light * grain * rings)[..., None]
    grey = head.mean(axis=2, keepdims=True)
    head = (grey + (head - grey) * 0.8) * shade      # duller than the palette: the real clay is dusty

    # mud between the heads: darker where it is wedged between cones
    ao = np.clip((t - 0.90) / 0.30, 0, 1)
    mortar = MORTAR * (0.62 + 0.38 * ao)[..., None] * (1 + 0.16 * noise(rng, 1.5) + 0.12 * noise(rng, 6))[..., None]
    mortar = mortar * (1 + 0.05 * rng.standard_normal((SIZE, SIZE, 1)))

    edge = np.clip((1.0 - t) * 9.0 + 0.5, 0, 1)[..., None]   # soft edge of the head, about 2 px
    img = head * edge + mortar * (1 - edge)
    img *= 1 + 0.05 * noise(rng, 60)[..., None]               # slow patches of dirt over the whole tile
    out = os.path.join(HERE, "textures", "cone_wall.jpg")
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(out, quality=88)
    print("wrote textures/cone_wall.jpg")


if __name__ == "__main__":
    main()
