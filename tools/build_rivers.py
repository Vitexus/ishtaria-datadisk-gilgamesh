#!/usr/bin/env python3
"""Writes rivers/euphrates.yaml and rivers/tigris.yaml: the two great rivers from their sources to the Gulf of the Epic.

The server carves and draws a course wherever no landscape patch replaces the ground (ishtaria-server `rivers/*.yaml`,
ishtaria-protocol `schemas/datadisk.schema.json` `river`). Each is joined from pieces of `[latitude, longitude, width_m]`:

* from the source to the point where the Early Dynastic course takes over: today's course (Natural Earth 1:10m rivers,
  public domain), which the rivers have kept above the alluvial plain; widening from a mountain stream to a great river;
* from there to the lagoon or the marshes of the Gulf: the Early Dynastic course of tools/build_world_map.py (EUPHRATES,
  TIGRIS), simplified from Adams (1981), Steinkeller (2001) and Hritz (2021), smoothed;
* the Euphrates through the landscape patch of Uruk: the centre line of the patch's water mask
  (media/terrain/uruk_water.png), so the river leaves the patch exactly where the patch river ends and goes on from there.

Usage: tools/build_rivers.py      (needs numpy, Pillow; downloads the Natural Earth file once into tools/cache/)
"""
import json
import math
import pathlib
import urllib.request

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "cache"
NATURAL_EARTH = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
                 "ne_10m_rivers_lake_centerlines.geojson")
USER_AGENT = "IshtariaDatadisk/0.3 (research; https://git.vitexsoftware.com/Ishtaria)"

# The Early Dynastic course below Hit and the end of it (tools/build_world_map.py EUPHRATES, past the patch of Uruk).
HIT = (42.82, 33.64)                       # (longitude, latitude): where the Early Dynastic Euphrates takes over
ED_ABOVE_URUK = [(43.40, 33.20), (44.00, 32.80), (44.60, 32.55), (45.06, 32.05), (45.50, 31.80)]
ED_BELOW_URUK = [(45.95, 31.05), (46.18, 30.88), (46.15, 30.50)]
# The Early Dynastic Tigris (tools/build_world_map.py TIGRIS): past Girsu, Lagash and Nigin into the marshes.
TIGRIS_FIRST = (43.15, 36.35)
ED_TIGRIS = [(43.50, 35.45), (43.87, 34.20), (44.40, 33.60), (45.20, 32.95), (45.82, 32.50), (46.10, 31.95),
             (46.58, 31.60), (46.70, 31.00), (46.85, 30.55), (47.05, 30.35)]
URUK = (31.3228, 45.6389)                  # latitude, longitude of the patch's anchor
PATCH_M, PATCH_STEP_M = 6000.0, 10.0
METRES_PER_DEGREE_LAT = 110574.0

SOURCE_WIDTH_M = 25.0
WIDENING_M_PER_KM = 0.3                    # a mountain stream becomes a great river over some 450 km
SPACING_KM = 4.0                           # points of the smoothed Early Dynastic stretches


def fetch_rivers():
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "ne_10m_rivers_lake_centerlines.geojson"
    if not path.exists():
        request = urllib.request.Request(NATURAL_EARTH, headers={"User-Agent": USER_AGENT})
        path.write_bytes(urllib.request.urlopen(request, timeout=120).read())
    return json.loads(path.read_text(encoding="utf-8"))


def upstream(names, source_near, goal_near):
    """The modern course from the vertex nearest to `source_near` down to the one nearest to `goal_near` (lon, lat), the
    shortest way through the pieces of the Natural Earth line, joined where their ends meet."""
    import heapq
    pieces = []
    for feature in fetch_rivers()["features"]:
        if feature["properties"].get("name") not in names:
            continue
        geometry = feature["geometry"]
        parts = geometry["coordinates"] if geometry["type"] == "MultiLineString" else [geometry["coordinates"]]
        pieces.extend([tuple(p[:2]) for p in part] for part in parts)
    vertices = [point for piece in pieces for point in piece]
    edges = {i: [] for i in range(len(vertices))}
    offset = 0
    ends = []
    for piece in pieces:
        for i in range(len(piece) - 1):
            edges[offset + i].append(offset + i + 1)
            edges[offset + i + 1].append(offset + i)
        ends += [offset, offset + len(piece) - 1]
        offset += len(piece)
    for a in ends:                       # pieces that meet end to end are one river
        for b in ends:
            if a < b and math.hypot(vertices[a][0] - vertices[b][0], vertices[a][1] - vertices[b][1]) < 0.06:
                edges[a].append(b)
                edges[b].append(a)
    nearest = lambda wanted: min(range(len(vertices)), key=lambda i: math.hypot(vertices[i][0] - wanted[0], vertices[i][1] - wanted[1]))
    source, goal = nearest(source_near), nearest(goal_near)
    best, previous, queue = {source: 0.0}, {}, [(0.0, source)]
    while queue:
        cost, node = heapq.heappop(queue)
        if node == goal:
            break
        if cost > best.get(node, 1e18):
            continue
        for other in edges[node]:
            step = cost + math.hypot(vertices[other][0] - vertices[node][0], vertices[other][1] - vertices[node][1])
            if step < best.get(other, 1e18):
                best[other], previous[other] = step, node
                heapq.heappush(queue, (step, other))
    path, node = [goal], goal
    while node != source:
        node = previous[node]
        path.append(node)
    return [vertices[i] for i in reversed(path)]


def km(a, b):
    """Great-circle distance of two (lon, lat) points in kilometres."""
    (lon1, lat1), (lon2, lat2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 12742.0 * math.asin(math.sqrt(h))


def thin(points, tolerance_deg=0.004):
    """Douglas-Peucker: the dense modern line keeps its meanders but not every vertex."""
    if len(points) < 3:
        return points
    (x1, y1), (x2, y2) = points[0], points[-1]
    length = math.hypot(x2 - x1, y2 - y1) or 1e-12
    index, far = 0, 0.0
    for i, (x, y) in enumerate(points[1:-1], 1):
        distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / length
        if distance > far:
            index, far = i, distance
    if far <= tolerance_deg:
        return [points[0], points[-1]]
    return thin(points[: index + 1], tolerance_deg)[:-1] + thin(points[index:], tolerance_deg)


def chaikin(points, rounds=3):
    """Corner cutting: a few waypoints of a reconstruction become a calm, bending course (the ends stay)."""
    for _ in range(rounds):
        cut = [points[0]]
        for a, b in zip(points, points[1:]):
            cut.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            cut.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        cut.append(points[-1])
        points = cut
    return points


def patch_course():
    """The centre of the patch's water per row (north to south), as (lon, lat) points every 200 m."""
    mask = np.array(Image.open(ROOT / "media" / "terrain" / "uruk_water.png"))
    size = mask.shape[0]
    points = []
    for row in range(0, size, 20):
        columns = np.nonzero(mask[row])[0]
        if not len(columns):
            continue
        x = (columns.mean() - (size - 1) / 2.0) * PATCH_STEP_M
        z = (row - (size - 1) / 2.0) * PATCH_STEP_M          # +z is south
        latitude = URUK[0] - z / METRES_PER_DEGREE_LAT
        longitude = URUK[1] + x / (111320.0 * math.cos(math.radians(URUK[0])))
        points.append((longitude, latitude))
    return points


def widths(course, mouth_width):
    along = [0.0]
    for a, b in zip(course, course[1:]):
        along.append(along[-1] + km(a, b))
    return [min(mouth_width, SOURCE_WIDTH_M + WIDENING_M_PER_KM * distance) for distance in along], along[-1]


def join(parts):
    course = []
    for part in parts:
        for point in part:
            if not course or km(course[-1], point) > 0.05:
                course.append(point)
    return course


def write(name, comment, course, mouth_width):
    sizes, length = widths(course, mouth_width)
    rows = ["  - [%.5f, %.5f, %.0f]" % (lat, lon, width) for (lon, lat), width in zip(course, sizes)]
    out = ROOT / "rivers"
    out.mkdir(exist_ok=True)
    (out / (name + ".yaml")).write_text(
        "# %s (tools/build_rivers.py): [latitude, longitude, width_m].\n%sid: %s\npoints:\n%s\n"
        % (comment, "", name, "\n".join(rows)),
        encoding="utf-8",
    )
    print("rivers/%s.yaml: %d points, %.0f km, source %s, mouth %s" % (name, len(course), length, course[0], course[-1]))


def main():
    source = (41.455, 40.180)                                       # the Karasu
    patch = patch_course()
    euphrates = join([
        thin(upstream(("Firat", "Al Furat", "Euphrates"), source, HIT)),
        chaikin([HIT] + ED_ABOVE_URUK + [patch[0]]),
        patch,
        chaikin([patch[-1]] + ED_BELOW_URUK),
    ])
    write("euphrates", "The Euphrates from its sources to the Gulf of the Epic: today's course to Hit (Natural Earth, public "
          "domain),\n# the Early Dynastic course below it (Adams 1981, as the world map has it) and through the landscape "
          "patch of Uruk the\n# course of the patch's own river", euphrates, 160.0)
    tigris = join([
        thin(upstream(("Dicle", "Tigris"), (39.17, 38.42), TIGRIS_FIRST)),
        chaikin([TIGRIS_FIRST] + ED_TIGRIS),
    ])
    write("tigris", "The Tigris from the Armenian highland to the marshes of the Gulf: today's course to Mosul (Natural Earth, "
          "public domain),\n# the Early Dynastic course below it past Girsu, Lagash and Nigin (Steinkeller 2001, Hritz 2021)",
          tigris, 180.0)


if __name__ == "__main__":
    main()
