#!/usr/bin/env python3
"""Draws textures/cone_mosaic.jpg: the clay-cone mosaic of the Eanna precinct. Thousands of cone heads of buff, red-brown
and dark brown clay are pressed into the wall in close hexagonal packing and form bands of three pattern families, as the
reconstructed wall panels of the Uruk temples show them: a broad zigzag, a lattice of diamonds and nested diamonds.
Our own drawing from the pattern families: it does not copy any picture. Run with system Python (Pillow):

    python3 models-src/architecture/make_cone_mosaic.py
"""
import os
import random

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SIZE = 2048
SS = 2                      # supersampling
COLS, ROWS = 150, 174       # cones across and down (a 2.4 m tile: heads of 1.6 cm, as found 1.2-1.8 cm); 58 rows per band
K = 2.5                     # the patterns are drawn 2.5 times larger than a few cones so that they read from a distance
BUFF, RED, DARK = (192, 178, 132), (130, 86, 82), (66, 56, 54)
EDGE = (74, 62, 48)
ROW_H = 0.8660254           # row spacing in cone diameters (hexagonal packing)
BAND = ROWS // 3
Y_BAND = BAND * ROW_H


def tri(x, period):
    """Triangle wave 0..1..0 with the given period."""
    t = (x % period) / period
    return 1 - abs(2 * t - 1)


def colour(band, x, y):
    if band == 0:       # broad zigzag: a red band with a dark edge line, rising and falling every 6 cones
        phase = y + tri(x, 12.0 * K) * 7.0 * K
        m = phase % (9.0 * K)
        if 0.0 <= m < 3.2 * K:
            return RED
        if 4.2 * K <= m < 5.4 * K:
            return DARK
        return BUFF
    if band == 1:       # lattice of diamonds: red lines along both hexagonal axes, a dark diamond in the middle of each
        d1 = x + y / 1.7320508
        d2 = x - y / 1.7320508
        if d1 % (10.0 * K) < 1.9 * K or d2 % (10.0 * K) < 1.9 * K:
            return RED
        u, v = (d1 % (10.0 * K)) - 5.0 * K, (d2 % (10.0 * K)) - 5.0 * K
        if abs(u) + abs(v) < 2.2 * K:
            return DARK
        return BUFF
    # nested diamonds, 20 cones wide: red outline, dark ring, red heart
    yy = y - 2 * Y_BAND
    dx = (x % (20.0 * K)) - 10.0 * K
    dy = yy - Y_BAND / 2
    n = abs(dx) / (10.0 * K) + abs(dy) / (Y_BAND / 2)
    if 0.80 <= n < 1.0:
        return RED
    if 0.5 <= n < 0.64:
        return DARK
    if n < 0.2:
        return RED
    return BUFF


def main():
    rng = random.Random(3)
    px = SIZE * SS
    img = Image.new("RGB", (px, px), EDGE)
    draw = ImageDraw.Draw(img)
    pitch = px / COLS
    dy = px / ROWS
    r = pitch * 0.47
    for row in range(ROWS):
        band = row // BAND
        for col in range(COLS):
            x = col + 0.5 * (row % 2)
            y = row * ROW_H
            base = colour(band, x, y)
            k = 0.88 + 0.2 * rng.random()
            c = tuple(min(255, int(v * k)) for v in base)
            cx, cy = (x + 0.5) * pitch, (row + 0.5) * dy
            for ox in (-px, 0, px):      # wrap horizontally so the texture tiles
                draw.ellipse((cx + ox - r, cy - r, cx + ox + r, cy + r), fill=c)
                draw.ellipse((cx + ox - r * 0.55, cy - r * 0.6, cx + ox + r * 0.35, cy + r * 0.3),
                             fill=tuple(min(255, v + 10) for v in c))
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    img.save(os.path.join(HERE, "textures", "cone_mosaic.jpg"), quality=88)
    print("wrote textures/cone_mosaic.jpg")


if __name__ == "__main__":
    main()
