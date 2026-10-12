"""Turns a generated texture (any image) into a seamless tile: python3 make_tileable.py in.png out.jpg [size]

The image is shifted by half its size and blended with the original through a mask that is 1 in the middle and
0 at the edges, so the seams of the shifted copy are hidden under the untouched middle."""
import sys

import numpy as np
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
size = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
horizontal = len(sys.argv) > 4 and sys.argv[4] == "x"   # tile along x only (border strips); the image keeps its shape
img = Image.open(src).convert("RGB")
img = img.resize((size, int(size * img.height / img.width)) if horizontal else (size, size), Image.LANCZOS)
a = np.asarray(img).astype(np.float32)
h, w = a.shape[:2]
shifted = np.roll(a, (0, w // 2) if horizontal else (h // 2, w // 2), axis=(0, 1) if not horizontal else (0, 1))
x = np.linspace(0, 1, w)
ramp = np.minimum(1.0, (1 - np.abs(2 * x - 1)) * 2.0)   # 0 at the edges, 1 in the middle, a wide plateau
if horizontal:
    mask = np.tile(ramp[None, :, None], (h, 1, 1))
else:
    y = np.linspace(0, 1, h)
    ramp_y = np.minimum(1.0, (1 - np.abs(2 * y - 1)) * 2.0)
    mask = np.outer(ramp_y, ramp)[..., None]
out = a * mask + shifted * (1 - mask)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(dst, quality=88)
