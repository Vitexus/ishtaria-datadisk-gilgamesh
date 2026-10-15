#!/usr/bin/env python3
"""Draws textures/paving.jpg: the baked-brick pavement of Uruk, tileable (2.4 m = 8 x 8 tiles). Our own drawing, from the owner's two photographs of the
excavated pavement of Early Dynastic Uruk (not shipped, not copied): square tiles, 30 cm on a side and about 5 cm thick, laid in a plain grid with narrow joints of dark
soil, pale grey-beige to sandy tops with reddish stains and hairline cracks, and the orange-brown side of the tile showing along one edge (that is how the 5 cm of height
are suggested; the pavement is a flat texture). Run with system Python (Pillow, numpy):

    python3 models-src/architecture/make_paving.py

`ziggurat.py` has the size of one repeat (PAVING_TILE_M of the material "paving") and every paved surface takes its UV scale from it, so a tile is 30 cm wherever it lies.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
N = 1024
TILES = 8
CELL = N // TILES             # 128 px = 30 cm (2.34 mm per pixel)
JOINT = 8                     # px: about 2 cm of dark soil between the tiles
SIDE = 4                      # px: the visible side of a 5 cm tile on its lower and right edge
PALETTE = [                   # tops: weight, colour (dusty, as the excavated pavement is)
    (0.40, (170, 164, 152)),    # grey-beige
    (0.28, (186, 170, 140)),    # sandy
    (0.14, (190, 188, 180)),    # pale grey
    (0.10, (178, 156, 130)),    # a little warmer
    (0.06, (150, 143, 132)),    # darker, dirty
    (0.02, (168, 140, 118)),    # reddish
]
SOIL = np.array([88, 80, 70], np.float32)
SIDE_COLOUR = np.array([196, 148, 100], np.float32)


def periodic_noise(rng, scale, amplitude):
    """Noise that wraps round the texture: white noise filtered in the frequency domain (`scale` = the wavelength in pixels)."""
    white = rng.normal(0, 1, (N, N))
    freq = np.fft.fftfreq(N)[:, None] ** 2 + np.fft.fftfreq(N)[None, :] ** 2
    kernel = np.exp(-freq * (scale ** 2) * 2.0)
    field = np.real(np.fft.ifft2(np.fft.fft2(white) * kernel))
    return field / field.std() * amplitude


def rounded_mask(h, w, radius, rng):
    """A tile top: a rectangle with rounded, slightly uneven corners (inside coordinates 0..h, 0..w)."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    inside_x = np.minimum(xx + 0.5, w - xx - 0.5)
    inside_y = np.minimum(yy + 0.5, h - yy - 0.5)
    d = np.minimum(inside_x, inside_y)
    corner = np.hypot(np.maximum(radius - inside_x, 0), np.maximum(radius - inside_y, 0))
    return (d > 0) & (corner < radius * (0.8 + 0.4 * rng.random()))


def main():
    rng = np.random.default_rng(2700)
    weights = np.array([w for w, _ in PALETTE])
    colours = np.array([c for _, c in PALETTE], np.float32)
    img = np.zeros((N, N, 3), np.float32)
    img[:] = SOIL
    img += periodic_noise(rng, 6, 5.0)[..., None]
    # a few light pebbles in the joints
    for _ in range(900):
        y, x = rng.integers(0, N, 2)
        img[y, x] += rng.uniform(20, 55)
    broad = periodic_noise(rng, 90, 7.0)
    fine = periodic_noise(rng, 3, 4.0)
    for i in range(TILES):
        for j in range(TILES):
            colour = colours[rng.choice(len(colours), p=weights / weights.sum())] * rng.uniform(0.93, 1.05)
            # the tile does not fill its cell exactly: a few pixels more or less on each side
            x0 = i * CELL + JOINT // 2 + int(rng.integers(-2, 3))
            x1 = (i + 1) * CELL - JOINT // 2 + int(rng.integers(-2, 3))
            y0 = j * CELL + JOINT // 2 + int(rng.integers(-2, 3))
            y1 = (j + 1) * CELL - JOINT // 2 + int(rng.integers(-2, 3))
            h, w = y1 - y0, x1 - x0
            mask = rounded_mask(h, w, 9, rng)
            tile = np.broadcast_to(colour, (h, w, 3)).copy()
            ys = (np.arange(y0, y1) % N)[:, None]
            xs = (np.arange(x0, x1) % N)[None, :]
            tile += (broad[ys, xs] + fine[ys, xs])[..., None]
            # the lower and the right edge show the side of the tile, the upper and the left one catch the light
            tile[h - SIDE:, :, :] = tile[h - SIDE:, :, :] * 0.35 + SIDE_COLOUR * 0.65 * rng.uniform(0.85, 1.05)
            tile[:, w - SIDE:, :] = tile[:, w - SIDE:, :] * 0.35 + SIDE_COLOUR * 0.65 * rng.uniform(0.85, 1.05)
            tile[:2, :, :] += 14
            tile[:, :2, :] += 10
            # stains of reddish soil and darker patches
            for _ in range(int(rng.integers(0, 4))):
                cy, cx = rng.integers(8, h - 8), rng.integers(8, w - 8)
                r = int(rng.integers(3, 9))
                yy, xx = np.mgrid[0:h, 0:w]
                blob = np.exp(-(((yy - cy) ** 2 + (xx - cx) ** 2) / (2.0 * r * r)))[..., None]
                stain = np.array([176, 118, 84], np.float32) if rng.random() < 0.6 else np.array([112, 104, 96], np.float32)
                tile = tile * (1 - 0.28 * blob) + stain * 0.28 * blob
            # dust and small pits on the top, a crazing of hairline cracks in some tiles
            tile += rng.normal(0, 3.5, (h, w, 1))
            for _ in range(int(rng.integers(6, 22))):
                py, px = int(rng.integers(4, h - 4)), int(rng.integers(4, w - 4))
                tile[py:py + 2, px:px + 2] *= 0.82
            if rng.random() < 0.45:
                y, x = float(rng.integers(10, h - 10)), float(rng.integers(10, w - 10))
                angle = rng.uniform(0, np.pi)
                for _ in range(int(rng.integers(30, 90))):
                    angle += rng.normal(0, 0.28)
                    x = float(np.clip(x + np.cos(angle) * 1.3, 1, w - 3))
                    y = float(np.clip(y + np.sin(angle) * 1.3, 1, h - 3))
                    tile[int(y):int(y) + 1, int(x):int(x) + 2] *= 0.8
            region = img[np.ix_(ys[:, 0], xs[0])]
            region[mask] = tile[mask]
            img[np.ix_(ys[:, 0], xs[0])] = region
    img += rng.normal(0, 3.0, img.shape)
    out = np.clip(img, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(os.path.join(HERE, "textures", "paving.jpg"), quality=88)
    print("wrote textures/paving.jpg (%d x %d tiles of 30 cm)" % (TILES, TILES))


if __name__ == "__main__":
    main()
