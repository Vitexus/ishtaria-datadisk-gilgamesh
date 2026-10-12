#!/usr/bin/env python3
"""Renders the NPC portraits (media/portraits/<id>.jpg) from the character models in media/models/.

    python3 tools/render_portraits.py [npc_id ...]

Needs Blender (`blender` on the PATH) and Pillow. Each portrait is a 512x512 bust of the model in its
Idle pose in front of a backdrop in the colours of the NPC's place.
"""
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
# npc id -> (backdrop colour, framing multiplier); a third item "x,y,z,dist,lens" places the camera by hand
BACKDROPS = {
    "gilgamesh": ("0.42,0.30,0.18", 1.6), "enkidu": ("0.20,0.26,0.14", 1.6), "enkidu_civilized": ("0.45,0.34,0.22", 1.6),
    "ishtar": ("0.48,0.14,0.12", 1.6, "0.09,0.0,1.67,1.62,70"), "shamhat": ("0.50,0.36,0.30", 1.6), "humbaba": ("0.10,0.18,0.10", 1.6),
    "utnapishtim": ("0.20,0.30,0.38", 1.6), "ur_shanabi": ("0.12,0.20,0.30", 1.6), "scorpion_man": ("0.32,0.20,0.10", 2.0),
    "ninsun": ("0.20,0.24,0.44", 1.6), "anu": ("0.14,0.20,0.40", 1.6), "bull_of_heaven": ("0.22,0.16,0.30", 2.1),
    "high_priest_anu": ("0.30,0.34,0.44", 1.6), "high_priestess_ishtar": ("0.44,0.16,0.16", 1.6),
    "temple_scribe": ("0.46,0.40,0.28", 1.6), "royal_guard": ("0.36,0.24,0.14", 1.6), "uruk_noble": ("0.34,0.26,0.40", 1.6),
    "uruk_merchant": ("0.44,0.28,0.14", 1.6), "potter": ("0.42,0.26,0.16", 1.6), "weaver": ("0.40,0.32,0.20", 1.6),
}


def main():
    ids = sys.argv[1:] or list(BACKDROPS)
    out_dir = ROOT / "media" / "portraits"
    out_dir.mkdir(exist_ok=True)
    for npc in ids:
        colour, mult, *camera = BACKDROPS[npc]
        with tempfile.TemporaryDirectory() as tmp:
            png = pathlib.Path(tmp) / (npc + ".png")
            subprocess.run(["blender", "-b", "--python", str(ROOT / "tools/blender/render_preview.py"), "--",
                            str(ROOT / "media/models" / (npc + ".glb")), str(png), "bust", "Idle", "14", "512", colour, str(mult), *camera],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            quality = 90
            while True:
                Image.open(png).convert("RGB").save(out_dir / (npc + ".jpg"), quality=quality)
                if (out_dir / (npc + ".jpg")).stat().st_size < 900_000 or quality < 50:
                    break
                quality -= 10
        print("portrait", npc)


if __name__ == "__main__":
    main()
