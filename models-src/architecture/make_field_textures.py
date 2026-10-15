#!/usr/bin/env python3
"""Draws textures/crop_rows.jpg and textures/plowed.jpg: tileable (8 m) furrowed fields for the irrigated land inside the
wall of Uruk (the magnetogram of the excavation shows the furrows). Our own drawing. Run with system Python (Pillow, numpy):

    python3 models-src/architecture/make_field_textures.py
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
N = 512


def rows(path, soil, crop, ridge, seed):
    rng = np.random.default_rng(seed)
    x = np.arange(N)[None, :].repeat(N, 0)
    period = 64
    phase = (x % period) / period
    # a furrow is a darker trough, a ridge (with the crop) a lighter band
    band = np.clip(np.cos(phase * 2 * np.pi) * 0.5 + 0.5, 0, 1)
    img = np.zeros((N, N, 3))
    for c in range(3):
        img[:, :, c] = soil[c] * (1 - band) + (crop[c] if ridge else soil[c] * 1.25) * band
    noise = rng.normal(0, 7, (N, N, 1))
    # broad blotches, tileable by construction (period divides N)
    big = np.kron(rng.normal(0, 9, (16, 16, 1)), np.ones((32, 32, 1)))
    img = np.clip(img + noise + big, 0, 255).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(HERE, "textures", path), quality=85)
    print("wrote", path)


if __name__ == "__main__":
    rows("crop_rows.jpg", (108, 84, 52), (92, 128, 56), True, 1)
    rows("plowed.jpg", (96, 72, 46), (140, 106, 70), False, 2)
