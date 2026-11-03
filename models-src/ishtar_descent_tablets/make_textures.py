"""Paints the faces of the six clay tablets of Ishtar's Descent to the Netherworld.

    python3 -I models-src/ishtar_descent_tablets/make_textures.py

The legend is not numbered in the sources (the Akkadian version is one tablet from Nineveh, the Sumerian poem
survives on many), so the disk cuts it into six episodes, one tablet each (places/ishtar_descent_tablets.yaml). Each
face carries a title line, the Sumerian name of the place the story goes to, KUR.NU.GI4 "Land of No Return", and
a row of strokes, the number of the episode:

    KUR NU GI4                   "Land of No Return"
    1..6 strokes                 the episode (an invention of the disk, not a scribal number)

The signs come from Noto Sans Cuneiform (SIL Open Font License; only the rendered pixels are kept). They are
Neo-Assyrian sign forms, not Old Babylonian ones: a stand-in, like the client's clay tablet. The writing is
impressed in damp clay, so it reads as shadow in a warm tan, with ruled lines between the registers.

Writes tablet_<n>_albedo.png / tablet_<n>_normal.png (n = 1..6) (384x544) and clay_albedo.png / clay_normal.png (tileable) into
textures/ beside this script.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "textures"
FONT = "/usr/share/fonts/truetype/noto/NotoSansCuneiform-Regular.ttf"

INCIPIT = [0x121B3, 0x12261, 0x12104]  # KUR NU GI4
DISH, DUB, KAM = 0x12079, 0x1207E, 0x12130

W, H = 384, 544
MARGIN = 22
RULE = 4
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


def registers(n):
    return [
        "".join(chr(c) for c in INCIPIT),
        "".join(chr(DISH) for _ in range(n)),
    ]


def incisions(n):
    img = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(img)
    lines = registers(n)
    rows = 8  # the text sits in the upper registers; the rest of the face is ruled and left for the scribe's text
    row_h = (H - 2 * MARGIN) / rows
    for i in range(rows + 1):
        y = round(MARGIN + i * row_h)
        draw.rectangle([MARGIN, y - RULE // 2, W - MARGIN, y + RULE // 2], fill=255)
    for i, text in enumerate(lines):
        size = int(row_h * 0.7)
        font = ImageFont.truetype(FONT, size)
        while font.getlength(text) > W - 2 * MARGIN - 20 and size > 16:
            size -= 2
            font = ImageFont.truetype(FONT, size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        y_mid = MARGIN + (i + 0.5) * row_h
        draw.text((MARGIN + 12 - left, y_mid - (top + bottom) / 2), text, font=font, fill=255)
    return np.asarray(img, dtype=np.float32) / 255.0


def main():
    OUT.mkdir(exist_ok=True)
    for n in range(1, 7):
        cut = incisions(n)
        soft = np.asarray(Image.fromarray((cut * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0)),
                          dtype=np.float32) / 255.0
        grain = noise((H, W), 90 + n)
        shade = (0.85 + grain * 0.3)[..., None]
        rgb = CLAY * shade
        rgb = rgb * (1 - soft[..., None] * 0.7) + SHADOW * soft[..., None] * 0.7
        Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT / f"tablet_{n}_albedo.png")
        normal_map(1.0 - soft * 0.9 + grain * 0.08).save(OUT / f"tablet_{n}_normal.png")
    s = 256
    grain = noise((s, s), 41, (1, 2, 4))
    rgb = CLAY * (0.8 + grain * 0.4)[..., None]
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT / "clay_albedo.png")
    normal_map(grain * 0.08).save(OUT / "clay_normal.png")
    print("textures written to", OUT)


if __name__ == "__main__":
    main()
