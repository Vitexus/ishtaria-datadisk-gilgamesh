#!/usr/bin/env python3
"""Verification of the three Gilgamesh statue spots in Uruk against the plan (scratch check, not part of the build)."""
import glob
import json
import math
import os

import yaml

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
plan = json.load(open(os.path.join(ROOT, "tools", "data", "uruk_city.json")))


def unit(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n)


def left(t):
    return (-t[1], t[0])


# ---- places and their plan positions (as in tools/build_statues.py)
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
    if not loc_ or depth > 8 or (loc_["from"] not in raw and loc_["from"] != "uruk"):
        return None
    base = where(loc_["from"], depth + 1)
    if base is None:
        return None
    b = math.radians(loc_["bearing_deg"])
    pos[pid] = (base[0] + loc_["distance_m"] * math.sin(b), base[1] - loc_["distance_m"] * math.cos(b))
    return pos[pid]


for pid in raw:
    where(pid)

# ---- the palace frame
pal = [p for p in plan["palaces"] if p["name"] == "uruk_palace"][0]
yaw = math.radians(pal["yaw"])
t = (math.cos(yaw), math.sin(yaw))
n = left(t)
front = (-n[0], -n[1])


def W(u, v):
    return (pal["c"][0] + u * t[0] + v * n[0], pal["c"][1] + u * t[1] + v * n[1])


pit = [i for i in pal["items"] if i["type"] == "palace"][0]
pv, cw, cd = pit["v"], pit["court"][0], pit["court"][1]
print("palace: c", pal["c"], "anchor(courtyard middle)", tuple(round(x, 1) for x in W(0, pv)),
      "front", tuple(round(x, 3) for x in front))
print("  courtyard u -%.0f..%.0f v %.0f..%.0f (frame); gateway passage v %.0f..%.0f u -3.6..3.6"
      % (cw / 2, cw / 2, pv - cd / 2, pv + cd / 2, pv - pit["d"] / 2, pv - cd / 2))
print("  altar at frame (%.0f, %.0f) = plan %s" % (cw / 2 - 4, pv + 3, tuple(round(x, 1) for x in W(cw / 2 - 4, pv + 3))))

# ---- candidate spots (frame coords for the palace, plan coords else)
spots = {}
# palace: in the courtyard, on the gateway axis, 8 m in front of the middle (the NPC stands there)
spots["gilgamesh_statue_palace"] = ("uruk_palace", W(0, pv - 8.0), front)
# eanna: in the precinct court, facing the south entrance
south = plan["precinct"][0]
ept = (110.0, -70.0)
spots["gilgamesh_statue_eanna"] = ("eanna_temple", ept, unit((south[0] - ept[0], south[1] - ept[1])))
# royal tombs: 15 m from the tombs place towards the palace
tp = pos["royal_tombs"]
pc = pos["uruk_palace"]
tow = unit((pc[0] - tp[0], pc[1] - tp[1]))
spots["gilgamesh_statue_royal_tombs"] = ("royal_tombs", (tp[0] + tow[0] * 15.0, tp[1] + tow[1] * 15.0), tow)

# ---- helpers
def in_poly(pt, poly):
    x, z = pt
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi:
            inside = not inside
        j = i
    return inside


def chain(pid):
    out = []
    while pid in raw:
        pid = raw[pid].get("parent")
        if pid:
            out.append(pid)
    return out


houses = plan["houses"]
print("\nhouses: %d entries, first: %s" % (len(houses), houses[0]))

for sid, (parent, pt, face) in spots.items():
    print("\n== %s at plan %s (parent %s), faces %s" % (sid, tuple(round(x, 1) for x in pt), parent, tuple(round(x, 3) for x in face)))
    b = math.degrees(math.atan2(pt[0], -pt[1])) % 360
    print("   locate: bearing %.3f distance %.1f" % (b, math.hypot(pt[0], pt[1])))
    print("   yaw_deg: %.2f" % (math.degrees(math.atan2(face[0], face[1])) % 360))
    exempt = {parent, *chain(parent)}
    bad = []
    for pid, q in pos.items():
        if pid == "uruk" or pid in exempt:
            continue
        r = raw[pid].get("radius_m", 20.0)
        d = math.hypot(pt[0] - q[0], pt[1] - q[1])
        if d < r + 1.0 + 0.5:
            bad.append((pid, round(d, 1), r))
    print("   places too close (need >= radius+1.5):", bad if bad else "none")
    near_h = []
    for h in houses:
        d = math.hypot(pt[0] - h[0], pt[1] - h[1])
        if d < 30.0:
            near_h.append((round(d, 1), h[0], h[1], h[5], h[6]))
    near_h.sort()
    print("   houses within 30 m:", near_h[:6] if near_h else "none")
    if sid == "gilgamesh_statue_eanna":
        print("   inside precinct polygon:", in_poly(pt, plan["precinct"]))
        eb = plan.get("eanna_buildings", [])
        print("   eanna_buildings:", len(eb), "entries; first:", eb[0] if eb else None)
        for e in eb:
            c = e.get("c") or (e.get("u"), e.get("v"))
            print("     ", e.get("name"), c)
    if sid == "gilgamesh_statue_palace":
        # frame coords of the spot
        rel = (pt[0] - pal["c"][0], pt[1] - pal["c"][1])
        u = rel[0] * t[0] + rel[1] * t[1]
        v = rel[0] * n[0] + rel[1] * n[1]
        print("   frame coords: u %.1f v %.1f (courtyard u +-%.0f v %.0f..%.0f; gateway v %.0f..%.0f)"
              % (u, v, cw / 2, pv - cd / 2, pv + cd / 2, pv - pit["d"] / 2, pv - cd / 2))
