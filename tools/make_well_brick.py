#!/usr/bin/env python3
"""Render media/textures/well_brick.png: pale buff Uruk brick in a running bond (original work, deterministic).

One tile is 0.6 m wide and 0.32 m high: four courses of 8 cm, bricks 30 cm long with a 1 cm mortar joint.
"""
import os
import random

from PIL import Image, ImageDraw, ImageFilter

W, H = 512, 512
COURSES, PER_COURSE = 4, 2
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "media", "textures", "well_brick.png")

rng = random.Random(2700)
img = Image.new("RGB", (W, H), (150, 140, 122))  # mud mortar
d = ImageDraw.Draw(img)
ch, bw, joint = H // COURSES, W // PER_COURSE, 5
for c in range(COURSES):
    shift = bw // 2 if c % 2 else 0
    for b in range(-1, PER_COURSE + 1):
        x0 = b * bw + shift
        t = rng.uniform(-1, 1)
        col = (int(206 + 18 * t), int(188 + 16 * t), int(150 + 14 * t))  # pale buff brick as in the well of Uruk, each a little different
        d.rectangle([x0 + joint // 2, c * ch + joint // 2, x0 + bw - joint // 2 - 1, (c + 1) * ch - joint // 2 - 1], fill=col)
        for _ in range(60):  # speckle
            x, y = rng.randrange(x0, x0 + bw), rng.randrange(c * ch, (c + 1) * ch)
            s = rng.randint(-18, 18)
            d.point((x, y), fill=(min(255, max(0, col[0] + s)), min(255, max(0, col[1] + s)), min(255, max(0, col[2] + s))))
# the courses wrap sideways: draw the bricks that run over the right edge again on the left
img = img.filter(ImageFilter.GaussianBlur(0.6))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT)
print("wrote", OUT)
