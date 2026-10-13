#!/usr/bin/env python3
"""Draws the grid of front_view.py on the rendered views and puts up to six side by side: front_grid.py out.png in1.png ..."""
import sys

from PIL import Image, ImageDraw


def grid(path):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    for i in range(21):
        y = 900 - i * 0.05 * 800
        d.line([(0, y), (800, y)], fill=(255, 0, 0) if i % 2 == 0 else (255, 170, 170), width=1)
        if i % 2 == 0:
            d.text((2, y - 11), f"{i * 0.05:.2f}", fill=(255, 0, 0))
    for i in range(-8, 9):
        x = 400 + i * 40
        d.line([(x, 0), (x, 1000)], fill=(0, 0, 255) if i % 2 == 0 else (170, 170, 255), width=1)
        if i % 2 == 0:
            d.text((x + 2, 985), f"{i * 0.05:+.2f}", fill=(0, 0, 255))
    return im


out, *inputs = sys.argv[1:]
images = [grid(path).crop((60, 80, 740, 920)) for path in inputs]
sheet = Image.new("RGB", (680 * len(images), 840))
for k, image in enumerate(images):
    sheet.paste(image, (680 * k, 0))
sheet.save(out)
