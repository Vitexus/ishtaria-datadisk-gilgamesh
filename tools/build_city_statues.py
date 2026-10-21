#!/usr/bin/env python3
"""Places a statue of Gilgamesh holding the lion in every city of the disk (and at Etemenanki in Babylon).

    python3 tools/build_city_statues.py

Reads the cities of the disk (places/*.yaml: `kind: city` places with their `geo`) and writes `places/city_statues.yaml` and the
names between the markers `# >>> city statues` / `# <<< city statues` in `i18n/en.yaml` and `i18n/cs.yaml`.

Every city of the Epic's world (every `kind: city` place but Uruk, whose statues tools/build_statues.py places inside the city plan)
gets one statue of Gilgamesh holding the adult lion (models-src/architecture/gilgamesh_statue.py): 25 m from the middle of the
historical site towards Uruk, facing Uruk - the king's statue stands in every city of his realm, looking at his own. The cities
are pinned to their sites and carry no generated town, so the statue stands on the bare ground of the tell; the world's own
settlements keep their distance by the places' radii. Babylon (the Etemenanki ziggurat, places/babylon.yaml) gets its statue 118 m
in front of the foot of the ziggurat's stairs, facing the tower.

`bearing_deg` in `locate` and `yaw_deg` of a structure are both in the map frame of the place (0 is up the map, 90 is to its
right; a model faces +Z of its own file at yaw 0, so a model facing map bearing b stands at yaw 180 - b). The way towards Uruk is
a geographic direction, so the script turns it into the map frame of every city: the tangent towards Uruk (the great-circle initial
bearing at the city) is read in the client's local axes at the site (ishtaria-server's `scenery::client_axes`, ported below), which
is the frame `locate` and `yaw_deg` live in.
"""
import glob
import math
import os
import sys

import yaml

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
URUK = (31.3228, 45.6389)   # the anchor of the city of the king (places/uruk.yaml)
MODEL = "media/models/architecture/gilgamesh_statue.glb"
COLLISION = "media/models/architecture/gilgamesh_statue_collision.glb"
OFFSET_M = 25.0             # the statue stands this far from the middle of the city, towards Uruk


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def unit(v):
    n = math.sqrt(dot(v, v))
    return tuple(c / n for c in v)


def up_vector(lat, lon):
    """The unit direction of a point of the planet (latitude = asin(y), longitude = atan2(-z, x))."""
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.cos(lo), math.sin(la), -math.cos(la) * math.sin(lo))


def client_axes(up):
    """The client's local +X and +Z axes at a site: the rotation that carries +Y to the site's up by the shortest arc, applied to
    +X and +Z (ishtaria-server's `scenery::client_axes`)."""
    cos = max(-1.0, min(1.0, up[1]))
    axis = (up[2], 0.0, -up[0])
    norm = math.hypot(axis[0], axis[2])
    if norm < 1e-12:
        return ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)) if cos > 0 else ((1.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    k = (axis[0] / norm, 0.0, axis[2] / norm)
    sin = math.sqrt(1.0 - cos * cos)

    def rotate(v):
        cr = cross(k, v)
        return tuple(v[i] * cos + cr[i] * sin + k[i] * dot(k, v) * (1.0 - cos) for i in range(3))

    return rotate((1.0, 0.0, 0.0)), rotate((0.0, 0.0, 1.0))


def bearing_to_uruk(lat, lon):
    """The great-circle initial bearing from a point to Uruk, in degrees clockwise from the north there."""
    p1, p2 = math.radians(lat), math.radians(URUK[0])
    dl = math.radians(URUK[1] - lon)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(x, y)) % 360.0


def map_frame_towards(lat, lon, target):
    """The map bearing (as `locate` wants it) and the model's yaw (as `structure` wants it) that face `target` (a lat/lon) from a
    site at (lat, lon): the tangent towards the target read in the client's local axes at the site."""
    up = up_vector(lat, lon)
    b = math.radians(bearing_to_uruk(lat, lon) if target == "uruk" else great_circle(lat, lon, target))
    east = unit(cross((0.0, 1.0, 0.0), up))
    north = unit(cross(up, east))
    tangent = tuple(math.cos(b) * north[i] + math.sin(b) * east[i] for i in range(3))
    axis_x, axis_z = client_axes(up)
    lx, lz = dot(tangent, axis_x), dot(tangent, axis_z)
    bearing = math.degrees(math.atan2(lx, -lz)) % 360.0     # 0 is up the map (local -Z), 90 to its right (local +X)
    yaw = math.degrees(math.atan2(lx, lz)) % 360.0          # the model faces local (sin yaw, cos yaw)
    return bearing, yaw


def great_circle(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(x, y)) % 360.0


def load_cities():
    """The cities of the disk with their geo coordinates, in the order of the files."""
    cities = []
    for path in sorted(glob.glob(os.path.join(ROOT, "places", "*.yaml"))):
        if path.endswith("city_statues.yaml"):
            continue
        for place in yaml.safe_load(open(path)) or []:
            if isinstance(place, dict) and place.get("kind") == "city" and place["id"] != "uruk" and place.get("geo"):
                cities.append((place["id"], place["geo"]["latitude_deg"], place["geo"]["longitude_deg"]))
    return cities


def build():
    out = []       # (id, english, czech, parent, bearing, yaw, note)
    for cid, lat, lon in load_cities():
        bearing, yaw = map_frame_towards(lat, lon, "uruk")
        out.append(dict(id="gilgamesh_statue_" + cid, en="Statue of Gilgamesh", cs="Socha Gilgameše", parent=cid,
                        bearing=round(bearing, 3), yaw=round(yaw, 2),
                        note="the king holding the lion, %g m from the middle of the city towards Uruk, facing Uruk" % OFFSET_M))
    # Babylon: in front of the foot of the Etemenanki ziggurat's stairs (78 m south of its place), facing the tower
    out.append(dict(id="gilgamesh_statue_babylon", en="Statue of Gilgamesh in Babylon", cs="Socha Gilgameše v Babylonu",
                    parent="etemenanki", bearing=180.0, yaw=180.0, distance=118.0,
                    note="the king holding the lion, in front of the Etemenanki ziggurat, facing the tower"))
    return out


def places_yaml(statues):
    lines = ["# Generated by tools/build_city_statues.py from the cities of the disk (places/*.yaml): a statue of Gilgamesh holding",
             "# the lion in every city of the Epic's world (and at the Etemenanki ziggurat in Babylon), %g m from the middle of the site" % OFFSET_M,
             "# towards Uruk and facing Uruk. Do not edit; change the script and run it again.", ""]
    for s in statues:
        distance = s.get("distance", OFFSET_M)
        lines += ["- id: %s" % s["id"], "  kind: landmark", "  name_key: place.%s" % s["id"], "  parent: %s" % s["parent"], "  radius_m: 1",
                  "  # %s" % s["note"],
                  "  locate: {from: %s, bearing_deg: %s, distance_m: %s, tolerance_m: 0}" % (s["parent"], s["bearing"], distance),
                  "  structure:", "    model: %s" % MODEL, "    collision: %s" % COLLISION,
                  "    yaw_deg: %s" % s["yaw"], "    visible_m: 500",
                  "  requires:", "    max_slope_deg: 60", ""]
    return "\n".join(lines)


def write_names(statues):
    for lang in ("en", "cs"):
        path = os.path.join(ROOT, "i18n", lang + ".yaml")
        text = open(path, encoding="utf-8").read()
        begin, end = "# >>> city statues (generated by tools/build_city_statues.py)", "# <<< city statues"
        block = begin + "\n" + "\n".join("place.%s: %s" % (s["id"], s[lang]) for s in statues) + "\n" + end + "\n"
        if begin in text:
            a = text.index(begin)
            b = text.index(end) + len(end) + 1
            text = text[:a] + block + text[b:]
        else:
            anchor = "# <<< uruk statues"   # keep the names of all the statues together
            if anchor in text:
                b = text.index(anchor) + len(anchor) + 1
                text = text[:b] + "\n" + block + text[b:]
            else:
                text = text.rstrip("\n") + "\n\n" + block
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)


def check(statues):
    """Reads every statue's yaw back in world vectors and prints how far it faces from Uruk (a self-check of the frame math)."""
    worst = 0.0
    for s in statues:
        if s["parent"] == "etemenanki":
            continue
        city = next(c for c in load_cities() if c[0] == s["parent"])
        lat, lon = city[1], city[2]
        up = up_vector(lat, lon)
        axis_x, axis_z = client_axes(up)
        yaw = math.radians(s["yaw"])
        forward = tuple(math.sin(yaw) * axis_x[i] + math.cos(yaw) * axis_z[i] for i in range(3))
        east = unit(cross((0.0, 1.0, 0.0), up))
        north = unit(cross(up, east))
        faced = math.degrees(math.atan2(dot(forward, east), dot(forward, north))) % 360.0
        wanted = bearing_to_uruk(lat, lon)
        error = abs((faced - wanted + 180.0) % 360.0 - 180.0)
        worst = max(worst, error)
    print("worst facing error towards Uruk: %.3f deg" % worst)
    return worst < 0.01


if __name__ == "__main__":
    statues = build()
    with open(os.path.join(ROOT, "places", "city_statues.yaml"), "w") as handle:
        handle.write(places_yaml(statues))
    write_names(statues)
    ok = check(statues)
    print("wrote places/city_statues.yaml (%d places) and the names in i18n" % len(statues))
    sys.exit(0 if ok else 1)
