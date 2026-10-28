"""Paints the inscribed face of the foundation tablet (research/foundtion-tablet.jpg).

    python3 -I models-src/foundation_tablet/make_textures.py

The photo is a black steatite foundation tablet of Ur-Namma (Ur III, c. 2100 BCE): ruled registers of incised signs
that hold a pale deposit, so the writing reads light on dark stone. The disk is set six centuries earlier, so the
tablet does not copy Ur-Namma's text. It carries the same dedication formula without a king's name:

    d-inanna / nin-a-ni / lugal / unug{ki}-ga-ke4 / e2-a-ni / mu-na-du3
    "For Inanna, his lady, the king of Uruk built her temple."

The signs come from Noto Sans Cuneiform (SIL Open Font License; only the rendered pixels are kept, the font is not
shipped). It is the Neo-Assyrian sign form, not the Early Dynastic one: a stand-in, like the client's clay tablet.

Writes into textures/ beside this script: front_albedo.png and front_normal.png (the inscribed face, 512x1024),
stone_albedo.png and stone_normal.png (plain tileable steatite for the edges and the back, 256x256).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "textures"
FONT = "/usr/share/fonts/truetype/noto/NotoSansCuneiform-Regular.ttf"

# one register per line, read top to bottom, left to right
REGISTERS = [
    [0x1202D, 0x12239],             # AN MUŠ3          d-inanna
    [0x1238F, 0x12000, 0x1224C],    # NIN A NI         nin-a-ni
    [0x12217],                      # LUGAL            lugal
    [0x12015, 0x121A0, 0x120B5, 0x121A4],  # UNUG KI GA KID  unug{ki}-ga-ke4
    [0x1208D, 0x12000, 0x1224C],    # E2 A NI          e2-a-ni
    [0x1222C, 0x1223E, 0x12195],    # MU NA KAK        mu-na-du3
]

W, H = 512, 1024
MARGIN = 26          # uninscribed rim around the ruled field (texels)
RULE = 5             # width of an incised register line
STONE = np.array([18, 20, 18], dtype=np.float32)      # near-black steatite, faintly green
DEPOSIT = np.array([168, 150, 122], dtype=np.float32)  # pale fill of the incisions
NORMAL_STRENGTH = 3.0


def noise(shape, seed, scales=(1, 4, 16)):
    """Smooth value noise in 0..1 summed over a few octaves, tileable (wrapped upscaling)."""
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


def scratches(shape, seed, count):
    """Fine pale scratches of handling, as a 0..1 mask."""
    rng = np.random.default_rng(seed)
    img = Image.new("L", (shape[1], shape[0]), 0)
    draw = ImageDraw.Draw(img)
    for _ in range(count):
        x, y = rng.random(2) * (shape[1], shape[0])
        angle = rng.normal(0.6, 0.5)
        length = rng.uniform(10, 70)
        draw.line([(x, y), (x + np.cos(angle) * length, y + np.sin(angle) * length)],
                  fill=int(rng.uniform(40, 110)), width=1)
    return np.asarray(img.filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255.0


def normal_map(height):
    """Tangent-space normal map (OpenGL convention, as glTF expects) from a 0..1 height field."""
    gy, gx = np.gradient(height)
    n = np.dstack([-gx * NORMAL_STRENGTH, gy * NORMAL_STRENGTH, np.ones_like(height)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8))


def incisions():
    """Mask (0..1) of the ruled lines and the signs on the front face."""
    img = Image.new("L", (W, H), 0)
    draw = ImageDraw.Draw(img)
    field_top, field_bottom = MARGIN, H - MARGIN
    row_h = (field_bottom - field_top) / len(REGISTERS)
    # ruling: the frame of the field and a line under every register
    for i in range(len(REGISTERS) + 1):
        y = round(field_top + i * row_h)
        draw.rectangle([MARGIN, y - RULE // 2, W - MARGIN, y + RULE // 2], fill=255)
    for x in (MARGIN, W - MARGIN):
        draw.rectangle([x - RULE // 2, field_top, x + RULE // 2, field_bottom], fill=255)
    usable_w = W - 2 * MARGIN - 28
    for i, signs in enumerate(REGISTERS):
        text = "".join(chr(cp) for cp in signs)
        size = int(row_h * 0.62)
        font = ImageFont.truetype(FONT, size)
        while font.getlength(text) > usable_w and size > 20:
            size -= 4
            font = ImageFont.truetype(FONT, size)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        y_mid = field_top + (i + 0.5) * row_h
        # signs start at the left of the register, as on the photo
        draw.text((MARGIN + 16 - left, y_mid - (top + bottom) / 2), text, font=font, fill=255)
    return np.asarray(img, dtype=np.float32) / 255.0


def main():
    OUT.mkdir(exist_ok=True)

    cut = incisions()
    cut_soft = np.asarray(Image.fromarray((cut * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)),
                          dtype=np.float32) / 255.0
    grain = noise((H, W), 7)
    wear = scratches((H, W), 11, 160)
    # the deposit is patchy: some incisions are full, some half empty
    fill = np.clip(0.6 + (noise((H, W), 13, (4, 8)) - 0.5) * 1.2, 0.3, 1.0)
    shade = (0.8 + grain * 0.4)[..., None]
    rgb = STONE * shade
    rgb = rgb + wear[..., None] * 45.0
    rgb = rgb * (1.0 - (cut * fill)[..., None]) + DEPOSIT * (cut * fill)[..., None] * (0.85 + grain[..., None] * 0.3)
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT / "front_albedo.png")
    height = 1.0 - cut_soft * 0.9 + grain * 0.04 - wear * 0.05
    normal_map(height).save(OUT / "front_normal.png")

    s = 256
    grain = noise((s, s), 21, (1, 2, 4))
    wear = scratches((s, s), 23, 25)
    rgb = STONE * (0.8 + grain * 0.4)[..., None] + wear[..., None] * 35.0
    Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(OUT / "stone_albedo.png")
    normal_map(grain * 0.06 - wear * 0.04).save(OUT / "stone_normal.png")
    print("textures written to", OUT)


if __name__ == "__main__":
    main()
