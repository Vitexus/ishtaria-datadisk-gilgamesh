#!/usr/bin/env python3
"""Draws the map of Sumer as it is in the game: maps/sumer.<lang>.png (written by this tool; do not edit).

    tools/build_sumer_map.py                       # both languages, the default region
    tools/build_sumer_map.py --lang cs --pixels-per-degree 400
    tools/build_sumer_map.py --bbox 30,44,34,48.5 --lang en --out /tmp/map.png

Everything on the map is read from the datadisk itself when the tool runs, so that running it again after the game has
grown (a new city, a new river, a new road) updates the map; nothing is typed in here:

  * the land, the sea and the relief: media/world/height.pgm and water.pgm, the very rasters the server turns into the
    planet (0.05 degrees, about 5.5 km a pixel: the coast and the marshes are as coarse as they are in the game);
  * the rivers and canals: rivers/*.yaml (the Euphrates and the Tigris, the HydroRIVERS tributaries, the channel networks
    of Uruk, Larsa and Eridu);
  * the cities (every place of `kind: city` inside the region) with their names from i18n/<lang>.yaml:
    places/*.yaml, pinned by `geo` or placed by a `locate` chain from another place;
  * the roads: trails/*.yaml, every place of a trail resolved to a position.

A place given by `locate` (bearing and distance from another place) is drawn at its nominal point: the server may move it
by its tolerance to suitable ground. Needs numpy, scipy, PyYAML and PIL. Deterministic: the same data give the same picture.
"""
import argparse
import glob
import math
import os

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
EARTH_M = 6371000.0
DEFAULT_BBOX = (29.4, 43.6, 34.2, 49.0)       # south, west, north, east: Sumer and its neighbours
SUPERSAMPLE = 2
EXAGGERATION = 6.0                            # of the relief, so that the flat alluvium still shows its swells

LAND_RAMP = [(-50, (205, 205, 160)), (0, (214, 207, 160)), (60, (205, 190, 140)), (300, (186, 165, 118)),
             (800, (160, 140, 102)), (1600, (134, 120, 98)), (3000, (226, 224, 218))]
SEA = (146, 188, 214)
RIVER = (38, 104, 160)
CANAL = (76, 140, 190)
ROAD = (176, 52, 36)
CITY = (60, 32, 16)
HOME = (210, 120, 20)

TEXT = {
    "en": {"title": "Sumer", "subtitle": "the world of the Epic of Gilgamesh, c. 2700 BCE, as it is in the game",
           "river": "River", "canal": "Canal or tributary", "road": "Road", "city": "City", "home": "Uruk, the city of Gilgamesh",
           "scale": "km", "credit": "Land and sea: ETOPO 2022, Early Dynastic coast (Adams 1981); rivers: Natural Earth, "
           "HydroRIVERS (Lehner and Grill 2013), Jotheri et al.; drawn from the datadisk by tools/build_sumer_map.py",
           "count": "%d cities, %d roads, %d rivers and canals", "rivers": {"euphrates": "Euphrates", "tigris": "Tigris"}},
    "cs": {"title": "Sumer", "subtitle": "svět Eposu o Gilgamešovi, asi 2700 př. n. l., tak jak je ve hře",
           "river": "Řeka", "canal": "Kanál nebo přítok", "road": "Cesta", "city": "Město", "home": "Uruk, město Gilgameše",
           "scale": "km", "credit": "Země a moře: ETOPO 2022, raně dynastické pobřeží (Adams 1981); řeky: Natural Earth, "
           "HydroRIVERS (Lehner a Grill 2013), Jotheri a kol.; nakresleno z datadisku nástrojem tools/build_sumer_map.py",
           "count": "%d měst, %d cest, %d řek a kanálů", "rivers": {"euphrates": "Eufrat", "tigris": "Tigris"}},
}


class Projection:
    """Equirectangular, true to scale in the middle of the region; (lat, lon) -> pixel of the supersampled picture."""

    def __init__(self, bbox, pixels_per_degree):
        self.south, self.west, self.north, self.east = bbox
        middle = math.radians((self.south + self.north) / 2)
        self.ky = pixels_per_degree * SUPERSAMPLE
        self.kx = self.ky * math.cos(middle)
        self.width = int(round((self.east - self.west) * self.kx))
        self.height = int(round((self.north - self.south) * self.ky))
        self.metres_per_pixel = math.pi * EARTH_M / 180.0 / pixels_per_degree

    def __call__(self, lat, lon):
        return ((lon - self.west) * self.kx, (self.north - lat) * self.ky)

    def inside(self, lat, lon, margin=0.0):
        return self.south - margin <= lat <= self.north + margin and self.west - margin <= lon <= self.east + margin


def read_pgm(path):
    """A P5 PGM as an array; 16-bit pictures are big-endian and, for the height, signed metres."""
    with open(path, "rb") as handle:
        data = handle.read()
    fields, position = [], 0
    while len(fields) < 4:
        while data[position:position + 1].isspace():
            position += 1
        if data[position:position + 1] == b"#":
            position = data.index(b"\n", position) + 1
            continue
        end = position
        while not data[end:end + 1].isspace():
            end += 1
        fields.append(data[position:end])
        position = end
    position += 1
    magic, width, height, maximum = fields[0], int(fields[1]), int(fields[2]), int(fields[3])
    assert magic == b"P5", "%s is not a P5 PGM" % path
    if maximum > 255:
        return np.frombuffer(data, dtype=">u2", count=width * height, offset=position).reshape(height, width).astype(np.uint16)
    return np.frombuffer(data, dtype=np.uint8, count=width * height, offset=position).reshape(height, width)


def land_and_sea(projection):
    """The relief (metres) and the water mask of the region at the size of the picture, from the world rasters."""
    height = read_pgm(os.path.join(ROOT, "media", "world", "height.pgm")).view(np.int16).astype(np.float64)
    water = read_pgm(os.path.join(ROOT, "media", "world", "water.pgm")).astype(np.float64) / 255.0
    rows, columns = height.shape
    pad = 3

    def window(lat, lon):
        return (90.0 - lat) / 180.0 * rows, (lon + 180.0) / 360.0 * columns

    r0, c0 = window(projection.north, projection.west)
    r1, c1 = window(projection.south, projection.east)
    r0, c0, r1, c1 = int(r0) - pad, int(c0) - pad, int(math.ceil(r1)) + pad, int(math.ceil(c1)) + pad
    height, water = height[r0:r1, c0:c1], water[r0:r1, c0:c1]
    # sample the window at the pixels of the picture (pixel centres, bicubic for the relief, linear for the mask)
    lat = projection.north - (np.arange(projection.height) + 0.5) / projection.ky
    lon = projection.west + (np.arange(projection.width) + 0.5) / projection.kx
    rr = ((90.0 - lat) / 180.0 * rows - r0 - 0.5)[:, None] * np.ones((1, projection.width))
    cc = ((lon + 180.0) / 360.0 * columns - c0 - 0.5)[None, :] * np.ones((projection.height, 1))
    relief = ndimage.map_coordinates(height, [rr, cc], order=3, mode="nearest")
    sea = ndimage.map_coordinates(water, [rr, cc], order=1, mode="nearest")
    sea = ndimage.gaussian_filter(sea, SUPERSAMPLE * 2.0) > 0.5
    # The mask marks the coarse rivers as bands of cells (5.5 km wide); the rivers are drawn from their own lines, so only
    # the wide waters stay: an opening by a little more than a cell removes the bands and keeps the Gulf and the lakes.
    cell = projection.ky * 0.05
    radius = 1.3 * cell
    eroded = ndimage.distance_transform_edt(sea) > radius
    sea = ndimage.distance_transform_edt(~eroded) <= radius
    return relief, sea


def land_colours(relief, sea, metres_per_pixel):
    """Hypsometric tint of the land with a hillshade, so the Zagros and the flat alluvium both read."""
    heights = np.array([h for h, _ in LAND_RAMP], dtype=np.float64)
    channels = [np.interp(relief, heights, [colour[k] for _, colour in LAND_RAMP]) for k in range(3)]
    picture = np.stack(channels, axis=-1)
    smooth = ndimage.gaussian_filter(relief, SUPERSAMPLE * 7.0)
    gy, gx = np.gradient(smooth)
    # slope in metres of height per metre of ground (the picture is `metres_per_pixel` a pixel, supersampled), exaggerated
    scale = EXAGGERATION / metres_per_pixel * SUPERSAMPLE
    normal = np.stack([-gx * scale, -gy * scale, np.ones_like(smooth)], axis=-1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    light = np.array([-0.55, -0.55, 0.63])          # from the north-west (y grows to the south)
    shade = np.clip(normal @ (light / np.linalg.norm(light)), 0.0, 1.0)
    flat = float(light[2] / np.linalg.norm(light))
    picture = picture * np.clip(1.0 + 0.9 * (shade - flat), 0.55, 1.25)[..., None]
    picture = np.clip(picture, 0, 255)
    picture[sea] = SEA
    return picture.astype(np.uint8)


def load_yaml(path):
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_rivers():
    """[(file stem, id, [(lat, lon, width_m)])] of every river and canal of rivers/*.yaml."""
    found = []
    for path in sorted(glob.glob(os.path.join(ROOT, "rivers", "*.yaml"))):
        data = load_yaml(path)
        for river in ([data] if isinstance(data, dict) else data or []):
            found.append((os.path.splitext(os.path.basename(path))[0], river["id"], [tuple(p) for p in river["points"]]))
    return found


def read_places():
    """id -> place of every place of places/*.yaml."""
    places = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "places", "*.yaml"))):
        for place in load_yaml(path) or []:
            if isinstance(place, dict) and "id" in place:
                places[place["id"]] = place
    return places


def position(places, ident, cache, trail=()):
    """(lat, lon) of a place: its `geo`, or the point `locate` gives from another place; None when it cannot be told."""
    if ident in cache:
        return cache[ident]
    place, result = places.get(ident), None
    if place is not None and ident not in trail:
        if place.get("geo"):
            result = (float(place["geo"]["latitude_deg"]), float(place["geo"]["longitude_deg"]))
        elif place.get("locate"):
            where = place["locate"]
            origin = position(places, where["from"], cache, trail + (ident,))
            if origin is not None:
                bearing, distance = math.radians(float(where["bearing_deg"])), float(where["distance_m"])
                lat = origin[0] + math.degrees(distance * math.cos(bearing) / EARTH_M)
                lon = origin[1] + math.degrees(distance * math.sin(bearing) / (EARTH_M * math.cos(math.radians(origin[0]))))
                result = (lat, lon)
    cache[ident] = result
    return result


def read_roads(places):
    """[(trail id, [(lat, lon)])] with every place of each trail resolved; a trail with an unknown place is reported."""
    cache, roads = {}, []
    for path in sorted(glob.glob(os.path.join(ROOT, "trails", "*.yaml"))):
        trail = load_yaml(path)
        points = [position(places, ident, cache) for ident in trail["places"]]
        if any(point is None for point in points):
            print("warning: trail %s has a place that cannot be placed, skipped" % trail["id"])
            continue
        roads.append((trail["id"], points))
    return roads, cache


def read_names(language):
    names = load_yaml(os.path.join(ROOT, "i18n", language + ".yaml")) or {}
    return {key: value for key, value in names.items() if isinstance(value, str)}


def font(size, bold=False):
    for name in ("NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        for folder in ("/usr/share/fonts/truetype/noto", "/usr/share/fonts/truetype/dejavu"):
            if os.path.exists(os.path.join(folder, name)):
                return ImageFont.truetype(os.path.join(folder, name), size * SUPERSAMPLE)
    return ImageFont.load_default()


def polyline(draw, projection, points, colour, width, sea=None):
    """A line through `points`; with `sea` (the mask of the picture) the parts that run out over open water are left out."""
    pixels = [projection(lat, lon) for lat, lon, *_ in points]
    runs, run = [], []
    for x, y in pixels:
        column, row = int(round(x)), int(round(y))
        wet = sea is not None and 0 <= row < sea.shape[0] and 0 <= column < sea.shape[1] and sea[row, column]
        if wet:
            if len(run) >= 2:
                runs.append(run)
            run = []
        else:
            run.append((x, y))
    if len(run) >= 2:
        runs.append(run)
    for part in runs:
        draw.line(part, fill=colour, width=max(1, int(round(width * SUPERSAMPLE))), joint="curve")


def draw_graticule(draw, projection, label_font):
    for lat in range(math.ceil(projection.south), math.floor(projection.north) + 1):
        y = projection(lat, projection.west)[1]
        draw.line([(0, y), (projection.width, y)], fill=(255, 255, 255, 70), width=SUPERSAMPLE)
        text = "%d°N" % lat
        width = draw.textbbox((0, 0), text, font=label_font)[2]
        draw.text((projection.width - width - 6 * SUPERSAMPLE, y - 18 * SUPERSAMPLE), text, font=label_font, fill=(60, 60, 60, 220))
    for lon in range(math.ceil(projection.west), math.floor(projection.east) + 1):
        x = projection(projection.south, lon)[0]
        draw.line([(x, 0), (x, projection.height)], fill=(255, 255, 255, 70), width=SUPERSAMPLE)
        draw.text((x + 4 * SUPERSAMPLE, projection.height - 24 * SUPERSAMPLE), "%d°E" % lon, font=label_font, fill=(60, 60, 60, 220))


def place_labels(draw, projection, markers, text_font, bold_font, keep_out=()):
    """Writes each name beside its marker at the first of eight spots that overlaps nothing written before."""
    taken = [(x - (r + 2) * SUPERSAMPLE, y - (r + 2) * SUPERSAMPLE, x + (r + 2) * SUPERSAMPLE, y + (r + 2) * SUPERSAMPLE)
             for _, x, y, r, _ in markers]
    taken += list(keep_out)
    for name, x, y, radius, home in sorted(markers, key=lambda m: (not m[4], m[0])):
        face = bold_font if home else text_font
        box = draw.textbbox((0, 0), name, font=face, stroke_width=2 * SUPERSAMPLE)
        w, h = box[2] - box[0], box[3] - box[1]
        gap = (radius + 3) * SUPERSAMPLE
        for dx, dy in ((1, -0.5), (-1, -0.5), (1, 0.6), (-1, 0.6), (0, -1.3), (0, 1.3), (1.0, -1.4), (-1.0, 1.4)):
            left = x + gap * dx + (0 if dx >= 0 else -w) - (w / 2 if dx == 0 else 0)
            top = y + gap * dy - h / 2 if dy in (-0.5, 0.6) else y + gap * dy - (h if dy < 0 else 0)
            rect = (left - 2, top - 2, left + w + 2, top + h + 2)
            if rect[0] < 0 or rect[1] < 0 or rect[2] > projection.width or rect[3] > projection.height:
                continue
            if any(not (rect[2] < o[0] or rect[0] > o[2] or rect[3] < o[1] or rect[1] > o[3]) for o in taken):
                continue
            taken.append(rect)
            draw.text((left - box[0], top - box[1]), name, font=face, fill=(40, 20, 10, 255),
                      stroke_width=2 * SUPERSAMPLE, stroke_fill=(255, 255, 255, 235))
            break


def legend_rows(labels):
    return [("line", RIVER, 4, labels["river"]), ("line", CANAL, 2, labels["canal"]), ("line", ROAD, 3, labels["road"]),
            ("dot", CITY, 5, labels["city"]), ("star", HOME, 8, labels["home"])]


def legend_box(labels):
    x0, y0, line = 18 * SUPERSAMPLE, 18 * SUPERSAMPLE, 24 * SUPERSAMPLE
    return x0, y0, x0 + 250 * SUPERSAMPLE, y0 + (len(legend_rows(labels)) + 3) * line + 10 * SUPERSAMPLE


def draw_legend(draw, projection, labels, text_font, bold_font, counts):
    x0, y0, x1, y1 = legend_box(labels)
    line = 24 * SUPERSAMPLE
    rows = legend_rows(labels)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=8 * SUPERSAMPLE, fill=(255, 255, 255, 220), outline=(120, 100, 80, 255), width=SUPERSAMPLE)
    draw.text((x0 + 12 * SUPERSAMPLE, y0 + 6 * SUPERSAMPLE), labels["title"], font=font(26, True), fill=(40, 20, 10, 255))
    y = y0 + 40 * SUPERSAMPLE
    draw.text((x0 + 12 * SUPERSAMPLE, y), labels["count"] % counts, font=font(12), fill=(70, 70, 70, 255))
    y += line
    for kind, colour, size, text in rows:
        cx, cy = x0 + 26 * SUPERSAMPLE, y + 8 * SUPERSAMPLE
        if kind == "line":
            draw.line([(x0 + 10 * SUPERSAMPLE, cy), (x0 + 42 * SUPERSAMPLE, cy)], fill=colour, width=size * SUPERSAMPLE)
        elif kind == "dot":
            r = size * SUPERSAMPLE
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=colour, outline=(255, 255, 255, 255), width=SUPERSAMPLE)
        else:
            star(draw, cx, cy, size * SUPERSAMPLE, colour)
        draw.text((x0 + 52 * SUPERSAMPLE, y), text, font=text_font, fill=(40, 40, 40, 255))
        y += line


def star(draw, x, y, radius, colour):
    points = []
    for k in range(10):
        r = radius if k % 2 == 0 else radius * 0.45
        angle = -math.pi / 2 + k * math.pi / 5
        points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
    draw.polygon(points, fill=colour, outline=(255, 255, 255, 255))


def draw_scale(draw, projection, labels, text_font):
    kilometres = 100
    length = kilometres * 1000.0 / projection.metres_per_pixel * SUPERSAMPLE
    x1, y = projection.width - 24 * SUPERSAMPLE, projection.height - 52 * SUPERSAMPLE
    x0 = x1 - length
    draw.line([(x0, y), (x1, y)], fill=(40, 40, 40, 255), width=3 * SUPERSAMPLE)
    for x in (x0, x1):
        draw.line([(x, y - 6 * SUPERSAMPLE), (x, y + 6 * SUPERSAMPLE)], fill=(40, 40, 40, 255), width=3 * SUPERSAMPLE)
    text = "%d %s" % (kilometres, labels["scale"])
    box = draw.textbbox((0, 0), text, font=text_font)
    draw.text(((x0 + x1) / 2 - (box[2] - box[0]) / 2, y - 26 * SUPERSAMPLE), text, font=text_font, fill=(40, 40, 40, 255),
              stroke_width=2 * SUPERSAMPLE, stroke_fill=(255, 255, 255, 220))
    # north arrow above the scale
    nx, ny = projection.width - 40 * SUPERSAMPLE, projection.height - 130 * SUPERSAMPLE
    draw.polygon([(nx, ny), (nx - 9 * SUPERSAMPLE, ny + 26 * SUPERSAMPLE), (nx, ny + 19 * SUPERSAMPLE), (nx + 9 * SUPERSAMPLE, ny + 26 * SUPERSAMPLE)],
                 fill=(40, 40, 40, 255))
    draw.text((nx - 5 * SUPERSAMPLE, ny - 22 * SUPERSAMPLE), "N", font=text_font, fill=(40, 40, 40, 255))


def render(language, bbox, pixels_per_degree, tributaries, out):
    labels = TEXT[language]
    names = read_names(language)
    projection = Projection(bbox, pixels_per_degree)
    relief, sea = land_and_sea(projection)
    image = Image.fromarray(land_colours(relief, sea, projection.metres_per_pixel), "RGB").convert("RGBA")
    # soften the block edges of the coarse coast a little
    image = image.filter(ImageFilter.GaussianBlur(0.6 * SUPERSAMPLE))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    text_font, bold_font, small_font = font(15), font(18, True), font(13)

    draw_graticule(draw, projection, small_font)

    rivers = read_rivers()
    main = [r for r in rivers if r[0] in ("euphrates", "tigris")]
    others = [r for r in rivers if r[0] not in ("euphrates", "tigris")]
    for stem, _, points in others:
        if not tributaries and stem.startswith("network"):
            continue
        if any(projection.inside(p[0], p[1], 0.2) for p in points):
            polyline(draw, projection, points, CANAL, 1.1 if stem.startswith("network") else 1.6, sea)
    for _, _, points in main:
        polyline(draw, projection, points, RIVER, 3.4, sea)
    river_font = font(17, True)
    for _, ident, points in main:
        name = labels["rivers"].get(ident)
        inside = [p for p in points if projection.inside(p[0], p[1])]
        if not name or not inside:
            continue
        lat0 = projection.north - (projection.north - projection.south) * 0.28
        lat, lon = min(inside, key=lambda p: abs(p[0] - lat0))[:2]
        x, y = projection(lat, lon)
        draw.text((x + 12 * SUPERSAMPLE, y - 8 * SUPERSAMPLE), name, font=river_font, fill=(20, 70, 120, 255),
                  stroke_width=2 * SUPERSAMPLE, stroke_fill=(255, 255, 255, 220))

    places = read_places()
    roads, cache = read_roads(places)
    for _, points in roads:
        polyline(draw, projection, points, (255, 255, 255, 255), 6)
    for _, points in roads:
        polyline(draw, projection, points, ROAD, 3.2)

    markers, count = [], 0
    for ident, place in sorted(places.items()):
        kind = place.get("kind")
        if kind != "city":
            continue
        spot = position(places, ident, cache)
        if spot is None or not projection.inside(*spot):
            continue
        x, y = projection(*spot)
        home = ident == "uruk"
        radius = 8 if home else 5
        count += 1
        r = radius * SUPERSAMPLE
        if home:
            star(draw, x, y, r + 2 * SUPERSAMPLE, HOME)
        else:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=CITY, outline=(255, 255, 255, 255), width=SUPERSAMPLE)
        name = names.get(place.get("name_key", ""), ident.replace("_", " ").title())
        markers.append((name, x, y, radius, home))
    place_labels(draw, projection, markers, text_font, bold_font, [legend_box(labels)])
    draw_legend(draw, projection, labels, text_font, bold_font, (count, len(roads), len(rivers)))
    draw_scale(draw, projection, labels, text_font)

    image = Image.alpha_composite(image, overlay)
    # the credit line under the picture
    footer = 26 * SUPERSAMPLE
    page = Image.new("RGBA", (image.width, image.height + footer), (245, 240, 228, 255))
    page.paste(image, (0, 0))
    ImageDraw.Draw(page).text((10 * SUPERSAMPLE, image.height + 5 * SUPERSAMPLE), labels["subtitle"][0].upper() + labels["subtitle"][1:] + ". " + labels["credit"],
                              font=font(10), fill=(70, 60, 50, 255))
    page = page.convert("RGB").resize((page.width // SUPERSAMPLE, page.height // SUPERSAMPLE), Image.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    page.save(out, optimize=True)
    print("%s: %dx%d px, %d cities, %d roads, %d rivers and canals, %d bytes" % (
        out, page.width, page.height, count, len(roads), len(rivers), os.path.getsize(out)))


def main():
    parser = argparse.ArgumentParser(description="Draw the map of Sumer from the data of the datadisk.")
    parser.add_argument("--lang", choices=["en", "cs", "all"], default="all")
    parser.add_argument("--bbox", default=",".join(str(v) for v in DEFAULT_BBOX), help="south,west,north,east in degrees")
    parser.add_argument("--pixels-per-degree", type=int, default=300)
    parser.add_argument("--no-tributaries", action="store_true", help="leave out the HydroRIVERS tributaries")
    parser.add_argument("--out", help="output file (one language only); default maps/sumer.<lang>.png")
    args = parser.parse_args()
    bbox = tuple(float(v) for v in args.bbox.split(","))
    assert len(bbox) == 4 and bbox[0] < bbox[2] and bbox[1] < bbox[3], "--bbox is south,west,north,east"
    languages = ["en", "cs"] if args.lang == "all" else [args.lang]
    assert args.out is None or len(languages) == 1, "--out needs one --lang"
    for language in languages:
        render(language, bbox, args.pixels_per_degree, not args.no_tributaries,
               args.out or os.path.join(ROOT, "maps", "sumer.%s.png" % language))


if __name__ == "__main__":
    main()
