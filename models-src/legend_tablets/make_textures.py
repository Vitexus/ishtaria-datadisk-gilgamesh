"""Paints the faces of the clay tablets of the legends in legends.py.

    python3 -I models-src/legend_tablets/make_textures.py

Each face carries a key sign of the legend on the first line and, on the second, as many strokes as the number of the
tablet. The signs come from Noto Sans Cuneiform (SIL Open Font License; only the rendered pixels are kept): Neo-Assyrian
forms, a stand-in like the client's clay tablet. Writes textures/<slug>_<n>_albedo.png / _normal.png (384x544) and
clay_albedo.png / clay_normal.png; the textures are not committed, this script regenerates them.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from legends import LEGENDS  # noqa: E402

OUT = HERE / "textures"
FONT = "/usr/share/fonts/truetype/noto/NotoSansCuneiform-Regular.ttf"
DISH = 0x12079
W, H = 384, 544
MARGIN, RULE = 22, 4
CLAY = np.array([176, 140, 98], dtype=np.float32)
SHADOW = np.array([88, 62, 38], dtype=np.float32)
NORMAL_STRENGTH = 4.0


def noise(shape, seed, scales=(1, 4, 16)):
    rng = np.random.default_rng(seed)
    h, w = shape
    total = np.zeros(shape, dtype=np.float32)
    weight = 0.0
    for i, s in enumerate(scales):
        small = rng.random((max(1, h // (s * 8)), max(1, w // (s * 8)))).astype(np.float32)
        tiled = np.tile(small, (3, 3))
        img = Image.fromarray((tiled * 255).astype(np.uint8)).resize(
            (tiled.shape[1] * s * 8, tiled.shape[0] * s * 8), Image.BICUBIC)
        arr = np.asarray(img, dtype=np.float32) / 255.0
        y0, x0 = small.shape[0] * s * 8, small.shape[1] * s * 8
        total += arr[y0:y0 + h, x0:x0 + w] * (1.0 / (i + 1))
        weight += 1.0 / (i + 1)
    return total / weight


def normal_map(height):
    gy, gx = np.gradient(height)
    n = np.dstack([-gx * NORMAL_STRENGTH, gy * NORMAL_STRENGTH, np.ones_like(height)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8))


def incisions(sign, n, signature=None):
    img = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(img)
    rows = 8
    row_h = (H - 2 * MARGIN) / rows
    for i in range(rows + 1):
        y = round(MARGIN + i * row_h)
        draw.rectangle([MARGIN, y - RULE // 2, W - MARGIN, y + RULE // 2], fill=255)
    for i, text in enumerate((chr(sign), "".join(chr(DISH) for _ in range(n)))):
        size = int(row_h * 0.7)
        font = ImageFont.truetype(FONT, size)
        while font.getlength(text) > W - 2 * MARGIN - 20 and size > 16:
            size -= 2
            font = ImageFont.truetype(FONT, size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        y_mid = MARGIN + (i + 0.5) * row_h
        draw.text((MARGIN + 12 - left, y_mid - (top + bottom) / 2), text, font=font, fill=255)
    if signature:
        text = "".join(chr(c) for c in signature)
        font = ImageFont.truetype(FONT, int(row_h * 0.7))
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        y_mid = MARGIN + (rows - 0.5) * row_h
        draw.text((W - MARGIN - 12 - right, y_mid - (top + bottom) / 2), text, font=font, fill=255)
    return np.asarray(img, dtype=np.float32) / 255.0


def main():
    OUT.mkdir(exist_ok=True)
    seed = 200
    for legend in LEGENDS:
        for n in range(1, legend["count"] + 1):
            seed += 1
            cut = incisions(legend["sign"], n, legend.get("signature"))
            soft = np.asarray(Image.fromarray((cut * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)),
                              dtype=np.float32) / 255.0
            grain = noise((H, W), seed)
            rgb = CLAY * (0.85 + grain * 0.3)[..., None]
            rgb = rgb * (1 - soft[..., None] * 0.7) + SHADOW * soft[..., None] * 0.7
            Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT / f"{legend['slug']}_{n}_albedo.png")
            normal_map(1.0 - soft * 0.9 + grain * 0.08).save(OUT / f"{legend['slug']}_{n}_normal.png")
    s = 256
    grain = noise((s, s), 41, (1, 2, 4))
    rgb = CLAY * (0.8 + grain * 0.4)[..., None]
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT / "clay_albedo.png")
    normal_map(grain * 0.08).save(OUT / "clay_normal.png")
    print("textures written to", OUT)


if __name__ == "__main__":
    main()
