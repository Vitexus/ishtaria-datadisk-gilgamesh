#!/usr/bin/env python3
"""Places the statues of Uruk: the lamassu (aladlammu) guardians and the restored Burney Relief goddess.

    python3 tools/build_statues.py [--preview statues.png]

Reads the plan of the city (tools/data/uruk_city.json) and writes `places/uruk_statues.yaml` and the names between the markers
`# >>> uruk statues` / `# <<< uruk statues` in `i18n/en.yaml` and `i18n/cs.yaml`.

Every statue place is a `structure` (ADR 0012) of the shared pair model `lamassu_pair.glb` (two guardians 9.5 m apart, both looking
south at yaw 0) turned with `yaw_deg` and scaled with `scale_m`; the place is the middle of the pair. Plan frame: x east, z south, metres from the
anchor of Uruk (as everywhere in this disk). A pair stands on both sides of the way, looking out at whoever comes:
  - at the six land gates of the wall (the water gate has no road): 6.5 m outside the wall, the Ishtar Gate 28 m outside its middle,
  - at the gate of the two palace compounds (3 m in front of the wall),
  - at the six entrances of the Eanna precinct and at the stairs of the Anu terrace and of the Ishtar ziggurat,
  - small guardians (shedu_pair.glb: 2.2 m high) at the door of the richest houses and in the middle of the four market squares.
The Burney Relief goddess stands in the court by the stairs of the Ishtar ziggurat, looking at the court.
Yaw: the client turns a model by Quaternion(UP, yaw), so a model looking along +Z (south) at yaw 0 looks along (sin yaw, cos yaw) in (x, z).
"""
import json
import math
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PLAN = os.path.join(ROOT, "tools", "data", "uruk_city.json")
PAIR = "media/models/architecture/lamassu_pair.glb"
PAIR_COLLISION = "media/models/architecture/lamassu_pair_collision.glb"
SHEDU = "media/models/architecture/shedu_pair.glb"
SHEDU_COLLISION = "media/models/architecture/shedu_pair_collision.glb"
GODDESS = "media/models/architecture/burney_relief.glb"
GODDESS_COLLISION = "media/models/architecture/burney_relief_collision.glb"
SMALL = 1.0             # (the small guardians have a model of their own, shedu_pair.glb: a pair 2.2 m high and 5.4 m apart)
HOUSES = 24             # how many of the richest houses near the centre get a pair


def unit(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n)


def left(t):
    return (-t[1], t[0])


def loc(pt):
    """Bearing (clockwise from north) and distance from the anchor of Uruk, as `locate` wants them."""
    return round(math.degrees(math.atan2(pt[0], -pt[1])) % 360.0, 3), round(math.hypot(pt[0], pt[1]), 1)


def yaw_of(face):
    return round(math.degrees(math.atan2(face[0], face[1])) % 360.0, 2)


def load_places():
    """The other places of the disk with their plan coordinates (from `locate`, recursively), radius (the server's default is 20 m) and parent."""
    import glob
    import yaml
    raw = {}
    for path in glob.glob(os.path.join(ROOT, "places", "*.yaml")):
        if path.endswith("uruk_statues.yaml"):
            continue
        for place in yaml.safe_load(open(path)) or []:
            if isinstance(place, dict) and "id" in place:
                raw[place["id"]] = place
    pos = {"uruk": (0.0, 0.0)}

    def where(pid, depth=0):
        if pid in pos:
            return pos[pid]
        place = raw.get(pid)
        loc_ = place.get("locate") if place else None
        if not loc_ or depth > 8 or loc_["from"] not in raw and loc_["from"] != "uruk":
            return None
        base = where(loc_["from"], depth + 1)
        if base is None:
            return None
        b = math.radians(loc_["bearing_deg"])
        pos[pid] = (base[0] + loc_["distance_m"] * math.sin(b), base[1] - loc_["distance_m"] * math.cos(b))
        return pos[pid]

    for pid in raw:
        where(pid)
    return raw, pos


def chain(raw, pid):
    out = []
    while pid in raw:
        pid = raw[pid].get("parent")
        if pid:
            out.append(pid)
    return out


def choose_parent(statue, raw, pos):
    """The server keeps unrelated places `radius + radius` apart; ancestors and descendants are exempt. Pick the parent that exempts every
    place the statue would stand inside of (the default parent is the city)."""
    pt = statue["pt"]
    near = [pid for pid, q in pos.items() if pid != "uruk" and math.hypot(pt[0] - q[0], pt[1] - q[1]) < raw[pid].get("radius_m", 20.0) + 1.0 + 0.5]
    if not near:
        return "uruk", []
    for cand in near:
        exempt = {cand, *chain(raw, cand)}
        if all(n in exempt for n in near):
            return cand, []
    return near[0], [n for n in near if n not in {near[0], *chain(raw, near[0])}]


def build():
    plan = json.load(open(PLAN))
    out = []       # (id, english, czech, point, facing, scale, note)

    def add(pid, en, cs, pt, face, scale=1.0, note="", model="pair"):
        out.append(dict(id=pid, en=en, cs=cs, pt=pt, face=unit(face), scale=scale, note=note, model=model))

    # gates of the wall
    cs_gate = {"ishtar": "Ištařiny brány", "river": "říční brány", "north": "severní brány", "west": "západní brány", "northwest": "severozápadní brány",
               "southwest": "jihozápadní brány"}
    for gate in plan["gates"]:
        name = gate["name"]
        if name == "water":
            continue
        o = gate["out"]
        dist = 28.0 if name == "ishtar" else 6.5
        pt = (gate["pos"][0] + o[0] * dist, gate["pos"][1] + o[1] * dist)
        add("lamassu_gate_" + name, "Lamassu of the %s gate" % name.replace("northwest", "north-west").replace("southwest", "south-west"),
            "Lamassu %s" % cs_gate[name], pt, o, note="outside the %s gate of the wall, looking out" % name)
    # the two palace compounds: the gate is in the middle of the front, the front is at v = -d/2 (the compound frame of build_city)
    for pal in plan["palaces"]:
        enc = next(i for i in pal["items"] if i["type"] == "enclosure")
        yaw = math.radians(pal["yaw"])
        t = (math.cos(yaw), math.sin(yaw))
        n = left(t)
        front = (-n[0], -n[1])
        gate = (pal["c"][0] + front[0] * enc["d"] / 2, pal["c"][1] + front[1] * enc["d"] / 2)
        pt = (gate[0] + front[0] * 3.0, gate[1] + front[1] * 3.0)
        cs = {"uruk_palace": "paláce Gilgameše", "sinkashid_palace": "paláce Sin-kašida"}[pal["name"]]
        en = {"uruk_palace": "the palace of Gilgamesh", "sinkashid_palace": "the palace of Sin-kashid"}[pal["name"]]
        add("lamassu_" + pal["name"], "Lamassu of " + en, "Lamassu " + cs, pt, front, note="before the gate of the palace compound")
    # the six entrances of the Eanna precinct, looking out of the precinct
    centre = plan["centre"]
    for i, e in enumerate(plan["precinct"]):
        o = unit((e[0] - centre[0], e[1] - centre[1]))
        pt = (e[0] + o[0] * 2.0, e[1] + o[1] * 2.0)
        add("lamassu_eanna_%d" % (i + 1), "Lamassu of the Eanna entrance %d" % (i + 1), "Lamassu u vchodu %d do Eanny" % (i + 1), pt, o,
            note="at an entrance of the sacred precinct")
    # the stairs of the Anu terrace (52 m square turned 41 degrees, stairs facing -n) and of the Ishtar ziggurat
    a = math.radians(plan["anu"]["yaw_deg"])
    front = (math.sin(a), -math.cos(a))
    c = plan["anu"]["c"]
    add("lamassu_anu", "Lamassu at the stairs of Anu", "Lamassu u schodů Anuova chrámu", (c[0] + front[0] * 44.0, c[1] + front[1] * 44.0), front,
        note="at the foot of the stairs of the Anu terrace")
    iz = plan["ishtar_ziggurat"]
    f = tuple(iz["front"])
    ic = iz["c"]
    add("lamassu_ishtar_ziggurat", "Lamassu at the stairs of Ishtar", "Lamassu u schodů Ištařina chrámu", (ic[0] + f[0] * 40.0, ic[1] + f[1] * 40.0), f,
        note="at the foot of the stairs of the Ishtar ziggurat")
    # markets: a small pair in the middle of each square
    for m in plan["markets"]:
        label = m["name"].replace("market_", "").replace("uruk_market", "great")
        add("shedu_" + m["name"], "Shedu of the %s market" % label, "Šédu na trhu (%s)" % label, tuple(m["c"]), (0.0, 1.0), SMALL,
            "small guardians in the middle of a market square", model="shedu")
    # the richest houses near the middle: a small pair at the door (the facade faces the street along `front`)
    rich = [h for h in plan["houses"] if h[6] == 2]
    rich.sort(key=lambda h: math.hypot(h[0] - centre[0], h[1] - centre[1]))
    taken = []
    for h in rich:
        if len(taken) >= HOUSES:
            break
        if all(math.hypot(h[0] - q[0], h[1] - q[1]) > 40.0 for q in taken):       # spread out
            taken.append(h)
    for i, h in enumerate(taken):
        front = (h[2], h[3])
        door = (h[0] + front[0] * (h[5] / 2 + 1.4), h[1] + front[1] * (h[5] / 2 + 1.4))
        add("shedu_house_%02d" % (i + 1), "Shedu at a house door %d" % (i + 1), "Šédu u dveří domu %d" % (i + 1), door, front, SMALL,
            "a small pair at the door of a rich house", model="shedu")
    # the goddess: in the court by the stairs of the Ishtar ziggurat, 12 m to the left of the stairs, looking at the court
    side = left(f)
    g = (ic[0] + f[0] * 28.0 + side[0] * 12.0, ic[1] + f[1] * 28.0 + side[1] * 12.0)
    add("queen_of_the_night", "The Queen of the Night", "Královna noci", g, f, note="the restored Burney Relief goddess", model="goddess")
    raw, pos = load_places()
    for st in out:
        st["parent"], st["unresolved"] = choose_parent(st, raw, pos)
        if st["unresolved"]:
            print("WARNING: %s still stands inside %s" % (st["id"], ", ".join(st["unresolved"])), file=sys.stderr)
    return out


def places_yaml(statues):
    lines = ["# Generated by tools/build_statues.py from the plan of the city (tools/data/uruk_city.json): the lamassu guardians and the goddess of",
             "# the Burney Relief. Each place is the middle of a pair (or of the goddess) at an exact spot (`locate` with a tolerance of one metre).",
             "# Do not edit; change the script and run it again.", ""]
    models = {"pair": (PAIR, PAIR_COLLISION), "shedu": (SHEDU, SHEDU_COLLISION), "goddess": (GODDESS, GODDESS_COLLISION)}
    for s in statues:
        b, d = loc(s["pt"])
        lines += ["- id: %s" % s["id"], "  kind: landmark", "  name_key: place.%s" % s["id"], "  parent: %s" % s["parent"], "  radius_m: 1",
                  "  # %s" % s["note"],
                  "  locate: {from: uruk, bearing_deg: %s, distance_m: %s, tolerance_m: 1}" % (b, d),
                  "  structure:", "    model: %s" % models[s["model"]][0],
                  "    collision: %s" % models[s["model"]][1]]
        if s["scale"] != 1.0:
            lines.append("    scale_m: %s" % s["scale"])
        lines += ["    yaw_deg: %s" % yaw_of(s["face"]), "    visible_m: %d" % (250 if s["model"] == "shedu" else 500),
                  "  requires:", "    max_slope_deg: 60", ""]
    return "\n".join(lines)


def write_names(statues):
    for lang in ("en", "cs"):
        path = os.path.join(ROOT, "i18n", lang + ".yaml")
        text = open(path, encoding="utf-8").read()
        begin, end = "# >>> uruk statues (generated by tools/build_statues.py)", "# <<< uruk statues"
        block = begin + "\n" + "\n".join("place.%s: %s" % (s["id"], s[lang]) for s in statues) + "\n" + end + "\n"
        if begin in text:
            a = text.index(begin)
            b = text.index(end) + len(end) + 1
            text = text[:a] + block + text[b:]
        else:
            text = text.rstrip("\n") + "\n\n" + block
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)


def preview(statues, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plan = json.load(open(PLAN))
    fig, ax = plt.subplots(figsize=(11, 11))
    for s in plan["streets"]:
        ax.plot([p[0] for p in s["pts"]], [p[1] for p in s["pts"]], color="#bbbbbb", lw=max(0.4, s["width"] / 12))
    pre = plan["precinct"] + [plan["precinct"][0]]
    ax.plot([p[0] for p in pre], [p[1] for p in pre], color="#7a5", lw=1.2)
    for g in plan["gates"]:
        ax.plot(*g["pos"], "ks", ms=4)
    for s in statues:
        col = {"goddess": "#d0a", "pair": "#07c", "shedu": "#c70"}[s["model"]]
        ax.plot(*s["pt"], "o", color=col, ms=2.5 if s["model"] == "shedu" else 4)
        k = 12 if s["model"] == "shedu" else 30
        ax.annotate("", xy=(s["pt"][0] + s["face"][0] * k, s["pt"][1] + s["face"][1] * k), xytext=s["pt"],
                    arrowprops=dict(arrowstyle="->", color=col, lw=0.8))
    for pal in plan["palaces"]:
        enc = next(i for i in pal["items"] if i["type"] == "enclosure")
        yaw = math.radians(pal["yaw"])
        t = (math.cos(yaw), math.sin(yaw))
        n = left(t)
        corners = [(pal["c"][0] + t[0] * u + n[0] * v, pal["c"][1] + t[1] * u + n[1] * v)
                   for u, v in ((-enc["w"] / 2, -enc["d"] / 2), (enc["w"] / 2, -enc["d"] / 2), (enc["w"] / 2, enc["d"] / 2), (-enc["w"] / 2, enc["d"] / 2), (-enc["w"] / 2, -enc["d"] / 2))]
        ax.plot([c[0] for c in corners], [c[1] for c in corners], color="#a63", lw=1.0)
    ax.plot(*plan["anu"]["c"], "k^", ms=6)
    ax.plot(*plan["ishtar_ziggurat"]["c"], "k^", ms=6)
    if os.environ.get("ZOOM"):
        x0, x1, z0, z1 = (float(v) for v in os.environ["ZOOM"].split(","))
        ax.set_xlim(x0, x1)
        ax.set_ylim(z1, z0)
    else:
        ax.invert_yaxis()
    ax.set_aspect("equal")
    ax.set_title("statues: blue pairs, orange small shedu, magenta the goddess; arrows = looking direction (north up)")
    fig.savefig(path, dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    statues = build()
    with open(os.path.join(ROOT, "places", "uruk_statues.yaml"), "w") as handle:
        handle.write(places_yaml(statues))
    write_names(statues)
    print("wrote places/uruk_statues.yaml (%d places) and the names in i18n" % len(statues))
    if "--preview" in sys.argv:
        preview(statues, sys.argv[sys.argv.index("--preview") + 1])
        print("preview", sys.argv[sys.argv.index("--preview") + 1])
