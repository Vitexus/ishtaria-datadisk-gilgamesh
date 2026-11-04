#!/usr/bin/env python3
"""Draws the map of Uruk that the client's minimap shows: media/terrain/uruk_map.png (written by this tool; do not edit).

    tools/build_map.py

The minimap used to colour the whole built-up ground of the city with one tint (the clear mask only says where something is
built), so the streets, houses and canals could not be told apart. This is the map itself, drawn from the plan of the city
(tools/data/uruk_city.json, tools/data/uruk_outlines.json) and the river of the landscape patch (media/terrain/uruk_water.png):
the wall with its gates, streets, the houses, the great buildings, fields, canals and the Euphrates. It is an RGBA picture over
the rectangle of the landscape patch (`terrain.map` of places/uruk.yaml), transparent where nothing is drawn. Row 0 is the
north edge, column 0 the west edge, as the other rasters of the patch.

The colours are those of the minimap's legend. Needs PIL and numpy. Deterministic.
"""
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(ROOT, "media", "terrain", "uruk_map.png")
EXTENT_M = 6000.0            # the rectangle of the landscape patch (places/uruk.yaml, terrain.extent_m)
METRES_PER_PIXEL = 3.0
SUPERSAMPLE = 2              # drawn this much larger and reduced, for smooth edges

WATER = (46, 115, 166, 235)
ROAD = (158, 140, 107, 245)
BUILDING = (140, 158, 153, 245)
GREAT = (176, 190, 184, 250)
FIELD = (116, 128, 76, 120)
WALL = (205, 158, 98, 255)
GATE = (240, 215, 130, 255)

SIDE = int(EXTENT_M / METRES_PER_PIXEL)
SCALE = SUPERSAMPLE / METRES_PER_PIXEL


def px(x, z):
    """Plan metres (x east, z south of the anchor) -> pixel of the supersampled picture."""
    return ((x + EXTENT_M / 2) * SCALE, (z + EXTENT_M / 2) * SCALE)


def rectangle(centre, right, forward, width, depth):
    """The corners of a rectangle `width` across (along `right`) and `depth` deep (along `forward`)."""
    corners = []
    for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        corners.append(px(centre[0] + right[0] * a * width / 2 + forward[0] * b * depth / 2,
                          centre[1] + right[1] * a * width / 2 + forward[1] * b * depth / 2))
    return corners


def main():
    plan = json.load(open(os.path.join(HERE, "data", "uruk_city.json")))
    outlines = json.load(open(os.path.join(HERE, "data", "uruk_outlines.json")))
    size = SIDE * SUPERSAMPLE
    layers = {name: Image.new("RGBA", (size, size), (0, 0, 0, 0)) for name in ("fields", "water", "roads", "buildings", "walls")}
    draw = {name: ImageDraw.Draw(image) for name, image in layers.items()}

    for field in plan["fields"]:
        t = field["t"]
        draw["fields"].polygon(rectangle(field["c"], t, (-t[1], t[0]), field["w"], field["d"]), fill=FIELD)

    # the Euphrates and the wet ground of the patch's own raster (10 m a pixel), smoothed
    wet = np.array(Image.open(os.path.join(ROOT, "media", "terrain", "uruk_water.png"))) > 0
    mask = Image.fromarray((wet * 255).astype(np.uint8)).resize((size, size), Image.BICUBIC).filter(ImageFilter.GaussianBlur(SUPERSAMPLE * 2))
    layers["water"].paste(Image.new("RGBA", (size, size), WATER), (0, 0), mask.point(lambda v: 255 if v > 110 else 0))
    for canal in plan["canals"]:
        points = [px(*p) for p in canal["pts"]]
        draw["water"].line(points, fill=WATER, width=max(2, int(max(canal["width"], 4.5) * SCALE)), joint="curve")

    for street in plan["streets"]:
        points = [px(*p) for p in street["pts"]]
        if len(points) >= 2:
            draw["roads"].line(points, fill=ROAD, width=max(2, int(max(street["width"], 6.0) * SCALE)), joint="curve")

    for x, z, fx, fz, w, d, *_ in plan["houses"]:
        length = math.hypot(fx, fz) or 1.0
        forward = (fx / length, fz / length)
        draw["buildings"].polygon(rectangle((x, z), (-forward[1], forward[0]), forward, w, d), fill=BUILDING)
    for market in plan["markets"]:
        t = market["t"]
        draw["buildings"].polygon(rectangle(market["c"], t, (-t[1], t[0]), market["w"], market["d"]), fill=GREAT)
    for palace in plan["palaces"]:
        yaw = math.radians(palace["yaw"])
        right, forward = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        draw["buildings"].polygon(rectangle(palace["c"] if "c" in palace else palace["anchor"], right, forward, palace["W"], palace["D"]), fill=GREAT)
    for building in plan["eanna_buildings"]:
        yaw = math.radians(building["yaw"])
        right, forward = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))
        draw["buildings"].polygon(rectangle(building["c"], right, forward, building["w"], building["d"]), fill=GREAT)
    for polygon in (outlines["ziggurat"], outlines["eanna"]):
        draw["buildings"].polygon([px(p[0], p[1]) for p in polygon], fill=GREAT)

    wall = [px(p[0], p[1]) for p in outlines["wall"]]
    draw["walls"].line(wall + [wall[0]], fill=WALL, width=int(15 * SCALE), joint="curve")
    for gate in plan["gates"]:
        x, z = px(*gate["pos"])
        r = (16 if gate["name"] != "water" else 9) * SCALE
        draw["walls"].ellipse((x - r, z - r, x + r, z + r), fill=GATE if gate["name"] != "water" else WATER)

    picture = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for name in ("fields", "water", "roads", "buildings", "walls"):
        picture = Image.alpha_composite(picture, layers[name])
    picture = picture.resize((SIDE, SIDE), Image.LANCZOS)
    picture.save(OUT, optimize=True)
    print("%s: %dx%d px, %.0f m a pixel, %d bytes" % (OUT, SIDE, SIDE, METRES_PER_PIXEL, os.path.getsize(OUT)))


if __name__ == "__main__":
    main()
