"""Draws a metre grid on the views of views.py: python3 views_grid.py <prefix>   (side: horizontal = y, front: x, top: x/y)."""
import sys
from PIL import Image, ImageDraw
prefix = sys.argv[1]
for name, centre in (("side", (0.0, 1.5)), ("front", (0.0, 1.5)), ("top", (0.0, 0.0))):
    im = Image.open(f"{prefix}_{name}.png").convert("RGB"); d = ImageDraw.Draw(im)
    W, H = im.size
    for k in range(-8, 9):
        a = k * 0.25
        px = W / 2 + (a - centre[0]) * 400
        d.line([(px, 0), (px, H)], fill=(255, 0, 0) if k % 4 == 0 else (255, 160, 160), width=1)
        d.text((px + 2, 2), f"{a:.2f}", fill=(255, 0, 0))
        py = H / 2 - (a - (centre[1] - 1.5 if name != "top" else 0) - (1.5 if name != "top" else 0) + (1.5 if name != "top" else 0)) * 400 if False else None
    for k in range(-6, 13):
        a = k * 0.25
        base = centre[1]
        py = H / 2 - (a - base) * 400
        d.line([(0, py), (W, py)], fill=(0, 0, 255) if k % 4 == 0 else (160, 160, 255), width=1)
        d.text((2, py + 2), f"{a:.2f}", fill=(0, 0, 255))
    im.save(f"{prefix}_{name}_grid.png")
