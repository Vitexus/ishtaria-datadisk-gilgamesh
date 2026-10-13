#!/usr/bin/env python3
"""Build the terrain patch of a place from open elevation data (ADR 0013).

The relief around the site is real: the Copernicus DEM (GLO-30, 30 m), downloaded from the
public AWS bucket. OpenStreetMap (Overpass `api/map`) supplies the modern hydrography and the
archaeological footprints, kept in the cache and reported against the historical course.

The river is carved back to its Early Dynastic course (c. 2700 BCE, see research/LANDSCAPE.md): it
runs along the outside of the east city wall, whose outline is the OSM way of the wall. The channel has
moved away since, but the relief of the floodplain stayed. Heights are written
relative to the anchor: 0x8000 is the anchor's height, one step is a decimetre. The water mask
is 0 for dry land, otherwise the surface in decimetres above the anchor.

The patch uses the client's local frame: +x east and +z SOUTH (Godot is right-handed with +y up, so
a map with +x east has -z north; row 0 of the PNGs is the most northern row). The outline of the city wall
and of the Eanna precinct is also written in that frame to tools/data/ for the wall model
(models-src/architecture/uruk_walls.py), so both come from one source.

Usage: tools/build_landscape.py [SITE]      (default: uruk)
Requires: Pillow and numpy (system packages); writes media/terrain/ and caches sources
in tools/cache/ (never shipped: the DEM is ESA data, OSM is ODbL, see datadisk.yaml).
"""
import json
import math
import pathlib
import sys
import urllib.request

from PIL import Image
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "cache"
TERRAIN = ROOT / "media" / "terrain"
DEMO = "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_%s/%s.tif"
OVERPASS = "https://overpass-api.de/api/map?bbox=%.4f,%.4f,%.4f,%.4f"
USER_AGENT = "IshtariaDatadisk/0.2 (research; https://git.vitexsoftware.com/Ishtaria)"

SITES = {
    "uruk": {
        # Centre of the OSM archaeological-site polygon of Uruk (Warka), the disk's anchor.
        "anchor": (31.3228, 45.6389),
        "extent_m": 6000.0,
        "resolution_m": 10.0,
        # The Early Dynastic Euphrates branch runs along the outside of the east wall (derived from the OSM
        # wall way, see river_course); the exact course is a reconstruction, see research/LANDSCAPE.md.
        "river_offset_m": 140.0,
        "river_width_m": 160.0,
        "river_bed_m": 3.8,
        "river_water_m": 3.2,
    },
}

METRES_PER_DEGREE_LAT = 110574.0
OUTLINES = {                     # OSM ways whose outline the wall model and the places need
    "wall": "1046022672",        # historic=citywalls
    "eanna": "1311535414",
    "ziggurat": "1311535415",
}


def metres_per_degree_lon(latitude):
    return 111320.0 * math.cos(math.radians(latitude))


def fetch(url, target):
    if target.is_file():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=280) as response, open(target, "wb") as out:
        out.write(response.read())
    return target


def dem_tiles(anchor, extent):
    """The Copernicus GLO-30 tiles covering the patch, keyed by tile bounds."""
    half_lat = extent / 2.0 / METRES_PER_DEGREE_LAT
    half_lon = extent / 2.0 / metres_per_degree_lon(anchor[0])
    west = int(math.floor(anchor[1] - half_lon))
    east = int(math.floor(anchor[1] + half_lon))
    south = int(math.floor(anchor[0] - half_lat))
    north = int(math.floor(anchor[0] + half_lat))
    tiles = []
    for lat in range(south, north + 1):
        for lon in range(west, east + 1):
            name = "N%02d_00_E%03d_00_DEM" % (lat, lon) if lat >= 0 else "S%02d_00_W%03d_00_DEM" % (-lat, -lon)
            folder = "Copernicus_DSM_COG_10_" + name
            file = fetch(DEMO % (folder, folder + "/" + name), CACHE / (name + ".tif"))
            image = Image.open(file)
            if image.mode != "F":
                raise SystemExit(f"{name}: unexpected DEM mode {image.mode}")
            data = np.asarray(image, dtype=np.float64)
            tiles.append((lon, lat, lon + 1, lat + 1, data))
    return tiles


def sample_dem(tiles, longitude, latitude):
    """Bilinear DEM sample in metres; tiles cover [lon, lon+1) x [lat, lat+1)."""
    for west, south, east, north, data in tiles:
        if west <= longitude < east and south <= latitude < north:
            x = (longitude - west) * data.shape[1]
            y = (north - latitude) * data.shape[0]
            return bilinear(data, x, y)
    raise SystemExit(f"DEM does not cover {latitude}, {longitude}")


def bilinear(grid, x, y):
    columns = grid.shape[1] - 1
    rows = grid.shape[0] - 1
    x = min(max(x, 0.0), columns)
    y = min(max(y, 0.0), rows)
    column = min(int(x), columns - 1)
    row = min(int(y), rows - 1)
    fx, fy = x - column, y - row
    upper = grid[row, column] * (1 - fx) + grid[row, column + 1] * fx
    lower = grid[row + 1, column] * (1 - fx) + grid[row + 1, column + 1] * fx
    return float(upper * (1 - fy) + lower * fy)


def box_blur(grid, radius_px):
    """A flat smoothing of the DEM: the local plain the river carves its bed into."""
    padded = np.pad(grid, radius_px, mode="edge")
    cumulative = padded.cumsum(0).cumsum(1)
    cumulative = np.pad(cumulative, ((1, 0), (1, 0)))
    size = 2 * radius_px + 1
    inner = (
        cumulative[size:, size:]
        - cumulative[:-size, size:]
        - cumulative[size:, :-size]
        + cumulative[:-size, :-size]
    )
    return inner / (size * size)


def window_extreme(grid, radius_px, func):
    """Separable running maximum/minimum over a (2r+1) square."""
    out = grid
    for axis in (0, 1):
        padded = np.pad(out, [(radius_px, radius_px) if a == axis else (0, 0) for a in (0, 1)], mode="edge")
        stack = [np.take(padded, range(k, k + out.shape[axis]), axis=axis) for k in range(2 * radius_px + 1)]
        out = func.reduce(stack)
    return out


def fill_trenches(grid, width_m, step):
    """A grey closing: the modern canals, drains and road cuts of the DEM (narrow trenches) are filled, since
    they did not exist in the Early Dynastic landscape; the broad relief and the tell are untouched."""
    radius = int(round(width_m / 2.0 / step))
    return window_extreme(window_extreme(grid, radius, np.maximum), radius, np.minimum)


def smoothstep(value):
    return value * value * (3.0 - 2.0 * value)


def distance_to_polyline(points, x, z):
    """Distance of every grid position to the polyline, in metres: rows are z, columns are x."""
    xx = x[None, :]
    zz = z[:, None]
    best = np.full((len(z), len(x)), math.inf)
    for (x1, z1), (x2, z2) in zip(points, points[1:]):
        length_sq = (x2 - x1) ** 2 + (z2 - z1) ** 2
        if length_sq == 0:
            continue
        t = np.clip(((xx - x1) * (x2 - x1) + (zz - z1) * (z2 - z1)) / length_sq, 0.0, 1.0)
        dx = xx - (x1 + t * (x2 - x1))
        dz = zz - (z1 + t * (z2 - z1))
        best = np.minimum(best, np.sqrt(dx * dx + dz * dz))
    return best


def write_png16(path, grid):
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(np.clip(grid, 0, 65535).astype(np.uint16), mode="I;16")
    image.save(path)
    print(f"  {path.relative_to(ROOT)}: {image.size[0]}x{image.size[1]}, {path.stat().st_size} bytes")


def local_xz(anchor, lat, lon):
    """Client local frame of a coordinate: x east, z south, in metres from the anchor."""
    return ((lon - anchor[1]) * metres_per_degree_lon(anchor[0]), -(lat - anchor[0]) * METRES_PER_DEGREE_LAT)


def outlines(site, anchor, extent):
    """The OSM outlines of the wall, the Eanna precinct and the Anu ziggurat in the local frame."""
    import xml.etree.ElementTree as ET

    half_lat = extent / 2.0 / METRES_PER_DEGREE_LAT * 1.4
    half_lon = extent / 2.0 / metres_per_degree_lon(anchor[0]) * 1.4
    bbox = (anchor[1] - half_lon, anchor[0] - half_lat, anchor[1] + half_lon, anchor[0] + half_lat)
    root = ET.parse(fetch(OVERPASS % bbox, CACHE / f"osm_{site}.osm")).getroot()
    nodes = {node.get("id"): (float(node.get("lat")), float(node.get("lon"))) for node in root.findall("node")}
    result = {}
    for way in root.findall("way"):
        for name, way_id in OUTLINES.items():
            if way.get("id") == way_id:
                points = [nodes[ref.get("ref")] for ref in way.findall("nd") if ref.get("ref") in nodes]
                result[name] = [[round(v, 1) for v in local_xz(anchor, lat, lon)] for lat, lon in points]
    missing = sorted(set(OUTLINES) - set(result))
    if missing:
        raise SystemExit(f"OSM ways missing from the extract: {', '.join(missing)}")
    return result


def densify(points, spacing):
    """A closed outline cut into pieces of at most `spacing` metres (the corners stay)."""
    result = []
    for (x1, z1), (x2, z2) in zip(points, points[1:]):
        pieces = max(1, int(math.ceil(math.hypot(x2 - x1, z2 - z1) / spacing)))
        result += [(x1 + (x2 - x1) * k / pieces, z1 + (z2 - z1) * k / pieces) for k in range(pieces)]
    return result + [result[0]]


def write_outlines(site, shapes, ground, anchor_height, step):
    """tools/data/<site>_outlines.json: the outlines in the local frame, the wall densified with the height of the
    final terrain (metres above the anchor) at every point, so that the wall model can follow the relief."""
    size = ground.shape[0]

    def height(x, z):
        column = x / step + (size - 1) / 2.0
        row = z / step + (size - 1) / 2.0
        return bilinear(ground, column, row) - anchor_height

    result = {name: [list(p) for p in points] for name, points in shapes.items()}
    # the Anu ziggurat stands on the lowest ground under its footprint, so that its terrace never floats
    zig = shapes["ziggurat"]
    cx = sum(p[0] for p in zig[:-1]) / (len(zig) - 1)
    cz = sum(p[1] for p in zig[:-1]) / (len(zig) - 1)
    result["ziggurat_centre"] = [round(cx, 1), round(cz, 1)]
    result["ziggurat_base_h"] = round(min(height(x, z) for x, z in densify(zig, 8.0)) - 0.3, 2)
    result["wall"] = [[round(x, 1), round(z, 1), round(height(x, z), 2)] for x, z in densify(shapes["wall"], 30.0)]
    target = ROOT / "tools" / "data" / f"{site}_outlines.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    print(f"  {target.relative_to(ROOT)}: " + ", ".join(f"{name} {len(points)} points" for name, points in result.items() if name in OUTLINES))


def river_course(wall, offset, extent):
    """The channel along the outside of the east wall: the east edge of the wall outline per row of z,
    plus `offset`, smoothed; straight on beyond the wall. Points are (x, z) in the local frame."""
    rows = list(np.arange(-extent / 2.0, extent / 2.0 + 1.0, 100.0))
    east = []
    for z in rows:
        crossings = []
        for (x1, z1), (x2, z2) in zip(wall, wall[1:]):
            if (z1 - z) * (z2 - z) <= 0 and z1 != z2:
                crossings.append(x1 + (x2 - x1) * (z - z1) / (z2 - z1))
        east.append(max(crossings) if crossings else None)
    inside = [i for i, value in enumerate(east) if value is not None]
    for i, value in enumerate(east):          # beyond the wall: keep the nearest edge
        if value is None:
            east[i] = east[inside[0]] if i < inside[0] else east[inside[-1]]
    kernel = 5
    smooth = [sum(east[max(0, i - kernel):i + kernel + 1]) / len(east[max(0, i - kernel):i + kernel + 1]) for i in range(len(east))]
    # never let the smoothing pull the channel into the wall
    return [(max(s, e) + offset, z) for s, e, z in zip(smooth, east, rows)]


def osm_summary(site, anchor, extent):
    """Distance from the anchor to today's mapped waterways: how far the river has moved."""
    half_lat = extent / 2.0 / METRES_PER_DEGREE_LAT * 1.4
    half_lon = extent / 2.0 / metres_per_degree_lon(anchor[0]) * 1.4
    bbox = (anchor[1] - half_lon, anchor[0] - half_lat, anchor[1] + half_lon, anchor[0] + half_lat)
    file = fetch(OVERPASS % bbox, CACHE / f"osm_{site}.osm")
    import xml.etree.ElementTree as ET

    root = ET.parse(file).getroot()
    nodes = {node.get("id"): (float(node.get("lat")), float(node.get("lon"))) for node in root.findall("node")}
    nearest = math.inf
    waterways = 0
    for way in root.findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        if tags.get("waterway") is None and tags.get("natural") != "water":
            continue
        waterways += 1
        for ref in way.findall("nd"):
            point = nodes.get(ref.get("ref"))
            if point is None:
                continue
            north = (point[0] - anchor[0]) * METRES_PER_DEGREE_LAT
            east = (point[1] - anchor[1]) * metres_per_degree_lon(anchor[0])
            nearest = min(nearest, math.hypot(east, north))
    if nearest is math.inf:
        print(f"  OSM: no mapped water within {half_lat * METRES_PER_DEGREE_LAT:.0f} m of the site")
    else:
        print(f"  OSM: {waterways} mapped water features, nearest {nearest:.0f} m from the anchor today")


def build(site_name):
    site = SITES[site_name]
    anchor = site["anchor"]
    extent = site["extent_m"]
    step = site["resolution_m"]
    size = int(round(extent / step))
    print(f"Building the terrain patch of {site_name} "
          f"({extent:.0f} x {extent:.0f} m at {step} m, anchor {anchor[0]:.4f}N {anchor[1]:.4f}E)")
    shapes = outlines(site_name, anchor, extent)
    tiles = dem_tiles(anchor, extent)
    print(f"  DEM: {len(tiles)} Copernicus GLO-30 tile(s)")
    osm_summary(site_name, anchor, extent)

    # Local frame: +x east, +z south (see the header), the anchor at the centre of the patch.
    x = (np.arange(size) - (size - 1) / 2.0) * step
    z = (np.arange(size) - (size - 1) / 2.0) * step
    lon = anchor[1] + x / metres_per_degree_lon(anchor[0])
    lat = anchor[0] - z / METRES_PER_DEGREE_LAT
    ground = np.empty((size, size))
    for row in range(size):
        for column in range(size):
            ground[row, column] = sample_dem(tiles, lon[column], lat[row])
    anchor_height = sample_dem(tiles, anchor[1], anchor[0])
    ground = fill_trenches(ground, 120.0, step)
    plain = box_blur(ground, int(round(150.0 / step)))

    # The river at its historical course: carve the bed, keep the relief everywhere else.
    river = river_course(shapes["wall"], site["river_offset_m"], extent)
    distance = distance_to_polyline(river, x, z)
    half = site["river_width_m"] / 2.0
    bank = 60.0
    carved = np.where(
        distance <= half,
        plain - site["river_bed_m"],
        plain - site["river_bed_m"] * (1.0 - smoothstep(np.clip((distance - half) / bank, 0.0, 1.0))),
    )
    ground = np.minimum(ground, carved)
    ground[size // 2, size // 2] = anchor_height

    heightmap = np.round((ground - anchor_height) * 10.0).astype(np.int32) + 32768
    surface = plain - site["river_bed_m"] + site["river_water_m"] - anchor_height
    water = np.zeros((size, size), dtype=np.int32)
    riverbed = (distance <= half) & (surface > ground - anchor_height)
    water[riverbed] = np.round(surface * 10.0).astype(np.int32)[riverbed] + 32768

    write_outlines(site_name, shapes, ground, anchor_height, step)
    write_png16(TERRAIN / f"{site_name}_height.png", heightmap)
    write_png16(TERRAIN / f"{site_name}_water.png", water)
    print(f"  relief: {ground.min() - anchor_height:+.1f} to {ground.max() - anchor_height:+.1f} m "
          f"around the anchor ({anchor_height:.1f} m above sea level)")
    print(f"  river: {site['river_width_m']:.0f} m wide, {int(riverbed.sum() * step * step / 10000)} ha of water")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "uruk")
