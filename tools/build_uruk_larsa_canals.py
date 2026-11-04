#!/usr/bin/env python3
"""Writes tools/data/uruk_larsa_canals.json and rivers/uruk_larsa_canals.yaml: the canals between Uruk and Larsa.

Source: the map of the canal survey of the Uruk-Larsa region (research/canals-uruk-larsa.jpg, 799 x 526 px; canals known from
earlier publications in magenta, canals found by that survey in green; scale bar 3 km = 55 px). The publication is not named
on the copy we have: **cite it in research/RIVER_NETWORK.md**. Only the named and the long canals are digitised, by eye, from
that small image, so a position is good to about half a kilometre; the many fine canals of the survey (Map 1 and Map 2 of the
figure) are not here: they need the figure at its full resolution.

Georeference: Uruk's tell (198, 183 px) is the anchor of Uruk's landscape patch (31.3228 N, 45.6389 E) and 1 px is 53.7 m, which
puts Larsa's tell (580, 264 px) 20.5 km east and 4.4 km south of it (Larsa's pin: 20.5 km, 4.1 km).

The canals are told twice: as rivers (`rivers/uruk_larsa_canals.yaml`), carved and drawn by the server and the client outside
Uruk's patch, and as polylines in metres that tools/build_landscape.py carves into the patch where it covers them.

Usage: tools/build_uruk_larsa_canals.py
"""
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANCHOR = (31.3228, 45.6389)      # latitude, longitude of Uruk's tell
ORIGIN_PX = (198.0, 183.0)
M_PER_PX = 53.7
WIDTH = {"large": 20.0, "medium": 14.0, "fine": 10.0}

# name, class, points in pixels of the figure (x east, y south), digitised by eye
CANALS = [
    ("W3", "large", [(210, 210), (250, 193), (317, 163), (410, 131)]),
    ("W5", "large", [(210, 211), (235, 240), (260, 263), (285, 296), (309, 325), (342, 372), (357, 387)]),
    ("W-north", "large", [(211, 150), (238, 118), (277, 40)]),
    ("W4", "large", [(170, 275), (217, 260), (267, 252), (323, 244), (400, 237), (460, 232), (557, 225)]),
    ("W1", "medium", [(425, 292), (472, 286), (515, 284), (550, 277)]),
    ("W2", "medium", [(437, 307), (500, 284), (527, 282), (550, 277)]),
    ("C6", "medium", [(277, 223), (323, 257), (367, 278), (410, 300), (437, 307)]),
    ("C7", "medium", [(335, 294), (375, 336), (405, 365)]),
    ("Larsa-NE", "large", [(603, 248), (617, 232), (640, 215), (700, 177), (750, 152), (790, 118)]),
]


def local(px):
    """Metres east and south of Uruk's tell."""
    return ((px[0] - ORIGIN_PX[0]) * M_PER_PX, (px[1] - ORIGIN_PX[1]) * M_PER_PX)


def geo(east, south):
    latitude = ANCHOR[0] - south / 110574.0
    longitude = ANCHOR[1] + east / (111320.0 * math.cos(math.radians(ANCHOR[0])))
    return latitude, longitude


def main():
    polylines, rivers = [], []
    for name, size, pixels in CANALS:
        points = [local(p) for p in pixels]
        polylines.append({"name": name, "class": size, "width_m": WIDTH[size], "points": [[round(x, 1), round(z, 1)] for x, z in points]})
        rows = ", ".join("[%.5f, %.5f, %.0f]" % (*geo(x, z), WIDTH[size]) for x, z in points)
        rivers.append("- {id: canal_%s, points: [%s]}\n" % (name.lower().replace("-", "_"), rows))
    (ROOT / "tools" / "data" / "uruk_larsa_canals.json").write_text(
        json.dumps({"description": "Canals between Uruk and Larsa (tools/build_uruk_larsa_canals.py): metres east (x) and south (z) of Uruk's tell.", "polylines": polylines}, separators=(",", ":")),
        encoding="utf-8")
    (ROOT / "rivers" / "uruk_larsa_canals.yaml").write_text(
        "# Canals between Uruk and Larsa (tools/build_uruk_larsa_canals.py, research/canals-uruk-larsa.jpg): [latitude, longitude, width_m].\n"
        + "".join(rivers), encoding="utf-8")
    print("%d canals, %.1f km" % (len(CANALS), sum(math.dist(local(a), local(b)) for _, _, p in CANALS for a, b in zip(p, p[1:])) / 1000.0))


if __name__ == "__main__":
    main()
