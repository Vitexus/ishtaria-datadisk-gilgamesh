"""Writes models-src/rodin/<id>.json from joints read off front_view/front_grid sheets (fractions of the height).

Imported by the batch scripts; see the dictionaries at the bottom of each batch file for the numbers per character.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent


def std(shoulder, elbow, wrist, hand, hip, knee, ankle, toe):
    return {"shoulder": shoulder, "elbow": elbow, "wrist": wrist, "hand": hand, "hip": hip, "knee": knee, "ankle": ankle, "toe": toe}


def write(name, height, joints, eyes, mouth, skirt, side=None, extra=None):
    config = {
        "name": name, "height": height, "tris": 30000, "tex": 2048, "centre": "bbox", "skirt": skirt,
        "stride": 0.3 if skirt else 0.45, "arm_swing": 0.5 if skirt else 0.8, "influences": 6 if skirt else 4,
        "face": {"eyes": [[round(e[0] * height, 3), round(e[1] * height, 3)] for e in eyes],
                 "mouth": [round(mouth[0] * height, 3), round(mouth[1] * height, 3)]},
        "joints": {k: [round(v[0], 3), round(v[1], 3)] for k, v in joints.items()},
    }
    if skirt:
        config["spatial_smooth"] = [0.05, 0.015]
    if side:
        config["side_x"] = {k: [round(a * height, 3), round(b * height, 3)] for k, (a, b) in side.items()}
    if extra:
        config.update(extra)
    (HERE / f"{name}.json").write_text(json.dumps(config, indent=1))
