#!/usr/bin/env python3
"""The roads of Uruk: from its gates to the places around, and the waypoints they need (written by this tool; do not edit).

    tools/build_roads.py

A road leaves the wall by a gate, never by a field. The gates are those of the plan of the city (tools/data/uruk_city.json,
the water gate, where a canal runs under the wall, has no road):

  * the hunter's village: the road ends at the gate of the wall that lies nearest to it (the north-west gate), not at a landing
    on the river far from the city;
  * the harbour: the quay stands where the Euphrates comes nearest to a gate (tools/build_river_life.py); a short road leads
    from that gate to the quay;
  * the other cities (`JOIN_CITIES`): a road leaves one of the other gates for each city within `NEAR_CITY_M`. Cities
    farther away are not joined (a long road needs a waypoint every 3 km, the server's limit of one leg).

Writes places/uruk_roads.yaml (a landmark outside each gate that a road uses and the waypoints of the long roads),
trails/*.yaml of the roads and moves the two waypoints of the hunter's road (places/hunter_road.yaml) onto the new line. The
legs of a trail are at most `LEG_M` long. Positions are metres east and south of the anchor of Uruk (the frame of the
plan), told as bearing and distance from it. Pure Python; deterministic.
"""
import glob
import json
import math
import os
import re

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
LEG_M = 2600.0              # the server's limit is 3000 m a leg
NEAR_CITY_M = 25000.0
# Off: the one city within reach, Larsa, lies beyond the Euphrates (250 to 300 m wide at Uruk) and beyond a coarse river of the
# world map, and the server bridges 36 m at most (`trails::MAX_SPAN_M`): its legs have no way, so no road is laid
# that would end in the middle of the plain. Roads to cities on this side of the river are 45 km and more away.
JOIN_CITIES = False
OUT_M = 30.0                # a gate's landmark stands this far outside the wall
EARTH_M = 6371000.0
TRACK = "media/models/architecture/cart_track.glb"

plan = json.load(open(os.path.join(HERE, "data", "uruk_city.json")))
GATES = {g["name"]: g for g in plan["gates"]}
ANCHOR = yaml.safe_load(open(os.path.join(ROOT, "places", "uruk.yaml")))[0]["geo"]


def offset(latitude, longitude):
    """Metres east and south of the anchor of Uruk of a point given by its coordinates."""
    lat0, lon0 = math.radians(ANCHOR["latitude_deg"]), math.radians(ANCHOR["longitude_deg"])
    east = (math.radians(longitude) - lon0) * math.cos(lat0) * EARTH_M
    south = -(math.radians(latitude) - lat0) * EARTH_M
    return east, south


def bearing_distance(x, z):
    return math.degrees(math.atan2(x, -z)) % 360.0, math.hypot(x, z)


def locate(x, z, tolerance=0):
    bearing, distance = bearing_distance(x, z)
    return "{from: uruk, bearing_deg: %.2f, distance_m: %.1f, tolerance_m: %g}" % (bearing, distance, tolerance)


def outside(name):
    gate = GATES[name]
    return gate["pos"][0] + gate["out"][0] * OUT_M, gate["pos"][1] + gate["out"][1] * OUT_M


def hunter_village():
    """The hunter's village by the chain of its `locate`s (the water-hole 12 km north-west of Uruk, the village 3.5 km on)."""
    waterhole = (12000.0 * math.sin(math.radians(310.0)), -12000.0 * math.cos(math.radians(310.0)))
    return (waterhole[0] + 3500.0 * math.sin(math.radians(130.0)), waterhole[1] - 3500.0 * math.cos(math.radians(130.0)))


def road_gates():
    return [name for name in GATES if name != "water"]


def nearest_gate(point, taken=()):
    return min((n for n in road_gates() if n not in taken), key=lambda n: math.hypot(point[0] - GATES[n]["pos"][0], point[1] - GATES[n]["pos"][1]))


def waypoints(start, end, legs):
    """The points between start and end that divide the way into `legs` legs of the same length."""
    return [(start[0] + (end[0] - start[0]) * k / legs, start[1] + (end[1] - start[1]) * k / legs) for k in range(1, legs)]


NAMES = {
    "northwest": ("North-west gate of Uruk", "Severozápadní brána Uruku"),
    "ishtar": ("Ishtar Gate of Uruk", "Ištařina brána Uruku"),
    "river": ("River gate of Uruk", "Říční brána Uruku"),
    "north": ("North gate of Uruk", "Severní brána Uruku"),
    "west": ("West gate of Uruk", "Západní brána Uruku"),
    "southwest": ("South-west gate of Uruk", "Jihozápadní brána Uruku"),
}


def main():
    places = []            # (id, name_key or None, locate, requires)
    trails = {}            # id -> (places, start clearance, end clearance)
    names = {}             # i18n keys written to the block of this tool
    used = []

    def gate_place(name):
        if name not in used:
            used.append(name)
        return "uruk_gate_" + name

    # 1. the hunter's village to the nearest gate
    village = hunter_village()
    gate = nearest_gate(village)
    end = outside(gate)
    length = math.hypot(end[0] - village[0], end[1] - village[1])
    legs = math.ceil(length / LEG_M)
    heading = math.degrees(math.atan2(end[0] - village[0], -(end[1] - village[1]))) % 360.0
    hunter_points = [(village[0] + (end[0] - village[0]) * k / legs, village[1] + (end[1] - village[1]) * k / legs) for k in range(1, legs)]
    hunter = {"gate": gate, "heading": heading, "length": length, "legs": legs,
              "distances": [length * k / legs for k in range(1, legs)]}
    trails["hunter_road"] = (["hunter_village"] + ["hunter_road_%d" % (k + 1) for k in range(len(hunter_points))] + [gate_place(gate)], 45, 10)

    # 2. the harbour, at the gate the river comes nearest to
    river = open(os.path.join(ROOT, "places", "uruk_river.yaml")).read()
    harbour = re.search(r"- id: uruk_harbour\n(?:.*\n)*?  locate: \{from: uruk, bearing_deg: ([\d.]+), distance_m: ([\d.]+)", river)
    hx = float(harbour.group(2)) * math.sin(math.radians(float(harbour.group(1))))
    hz = -float(harbour.group(2)) * math.cos(math.radians(float(harbour.group(1))))
    harbour_gate = nearest_gate((hx, hz))
    trails["uruk_harbour_road"] = ([gate_place(harbour_gate), "uruk_harbour"], 5, 6)

    # 3. the cities within reach, each by a gate of its own that no other road uses
    cities = []
    for place in yaml.safe_load(open(os.path.join(ROOT, "places", "ancient_cities.yaml"))):
        geo = place.get("geo") if isinstance(place, dict) else None
        if not geo or place.get("kind") != "city":
            continue
        point = offset(geo["latitude_deg"], geo["longitude_deg"])
        if JOIN_CITIES and math.hypot(*point) <= NEAR_CITY_M:
            cities.append((math.hypot(*point), place["id"], point))
    taken = {gate, harbour_gate}
    roads = []
    for _, city, point in sorted(cities):
        origin = nearest_gate(point, taken)
        taken.add(origin)
        start = outside(origin)
        legs_to = math.ceil(math.hypot(point[0] - start[0], point[1] - start[1]) / LEG_M)
        way = waypoints(start, point, legs_to)
        ids = ["%s_road_%d" % (city, k + 1) for k in range(len(way))]
        for ident, spot in zip(ids, way):
            places.append((ident, "place.%s_road" % city, locate(*spot, tolerance=300),
                           "    biome: [grassland, lowland]\n    height_m: {min: -10, max: 250}\n    max_slope_deg: 15"))
        trails["%s_road" % city] = ([gate_place(origin)] + ids + [city], 10, 60)
        roads.append((city, origin, math.hypot(point[0] - start[0], point[1] - start[1])))

    # the landmarks outside the gates the roads use
    gate_entries = []
    for name in used:
        gate_entries.append(("uruk_gate_" + name, "place.uruk_gate_" + name, locate(*outside(name)), "    max_slope_deg: 45"))
    out = ["# The gates of Uruk that roads leave by, and the waypoints of the long roads (written by tools/build_roads.py; do not edit).", ""]
    for ident, name_key, where, requires in gate_entries + places:
        out += ["- id: %s" % ident, "  kind: landmark", "  name_key: %s" % name_key, "  radius_m: 6", "  locate: %s" % where,
                "  requires:", requires, ""]
    open(os.path.join(ROOT, "places", "uruk_roads.yaml"), "w").write("\n".join(out))

    for ident, (route, start_clear, end_clear) in trails.items():
        what = {"hunter_road": "The road from the hunter's village to the nearest gate of Uruk",
                "uruk_harbour_road": "The road from the gate nearest to the river to the quay of Uruk"}.get(ident, "The road from a gate of Uruk to " + ident[:-5].title())
        with open(os.path.join(ROOT, "trails", ident + ".yaml"), "w") as handle:
            handle.write("# %s (written by tools/build_roads.py; do not edit), laid leg by leg by the server.\n" % what)
            handle.write("id: %s\nplaces: [%s]\nstart_clearance_m: %g\nend_clearance_m: %g\n" % (ident, ", ".join(route), start_clear, end_clear))
            handle.write("# A worn field track of ox carts (tools/build_cart_track.py), 4 m of it at every step, instead of stepping stones.\n")
            handle.write("model: %s\n" % TRACK)

    # a road of an earlier run that is not told any more goes
    for stale in glob.glob(os.path.join(ROOT, "trails", "*_road.yaml")):
        if os.path.basename(stale)[:-5] not in trails:
            os.remove(stale)

    # the two waypoints of the hunter's road move onto the new line
    path = os.path.join(ROOT, "places", "hunter_road.yaml")
    text = open(path).read()
    for k, distance in enumerate(hunter["distances"], 1):
        pattern = r"(- id: hunter_road_%d\n(?:.*\n)*?  locate: )\{[^}]*\}" % k
        text, count = re.subn(pattern, r"\g<1>{from: hunter_village, bearing_deg: %.1f, distance_m: %d, tolerance_m: 250}" % (heading, round(distance)), text, count=1)
        assert count == 1, "hunter_road_%d is missing" % k
    open(path, "w").write(text)

    # names
    entries = {}
    for name in used:
        entries["place.uruk_gate_" + name] = NAMES[name]
    for city, _, _ in roads:
        entries["place.%s_road" % city] = ("Road to %s" % city.replace("_", " ").title(), "Cesta do města %s" % city.replace("_", " ").title())
    write_names(entries)
    print("hunter road: %s gate, %.0f m in %d legs (heading %.1f); harbour road from the %s gate; roads to cities: %s; gates used: %s" % (
        hunter["gate"], hunter["length"], hunter["legs"], hunter["heading"], harbour_gate,
        ", ".join("%s by the %s gate (%.0f m)" % r for r in roads) or "none", ", ".join(used)))


BEGIN, END = "# BEGIN roads (written by tools/build_roads.py; do not edit)", "# END roads"


def write_names(entries):
    for index, language in ((0, "en"), (1, "cs")):
        path = os.path.join(ROOT, "i18n", language + ".yaml")
        text = open(path, encoding="utf-8").read()
        start, end = text.find(BEGIN), text.find(END)
        if start >= 0 and end > start:
            text = text[:start].rstrip("\n") + "\n" + text[end + len(END):].lstrip("\n")
        block = [BEGIN] + ["%s: %s" % (key, json.dumps(entries[key][index], ensure_ascii=False)) for key in sorted(entries)] + [END]
        open(path, "w", encoding="utf-8").write(text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n")


if __name__ == "__main__":
    main()
