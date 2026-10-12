"""Turns a generated texture (any image) into a seamless tile: python3 make_tileable.py in.png out.jpg [size]

The image is shifted by half its size and blended with the original through a mask that is 1 in the middle and
0 at the edges, so the seams of the shifted copy are hidden under the untouched middle."""
import sys

import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
size = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
img = Image.open(src).convert("RGB").resize((size, size), Image.LANCZOS)
a = np.asarray(img).astype(np.float32)
shifted = np.roll(a, (size // 2, size // 2), axis=(0, 1))
x = np.linspace(0, 1, size)
ramp = 1 - np.abs(2 * x - 1)               # 0 at the edges, 1 in the middle
ramp = np.minimum(1.0, ramp * 2.0)         # a wider plateau
mask = np.outer(ramp, ramp)[..., None]
out = a * mask + shifted * (1 - mask)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst, quality=88)
