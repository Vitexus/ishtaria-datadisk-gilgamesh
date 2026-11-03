#!/usr/bin/env python3
"""Finds the places where the irrigation scheme of the disk (media/models/architecture/irrigation_works.glb, research/WATER_WORKS.md)
can stand along the DOCUMENTED irrigation canals, and writes tools/data/irrigation_sites.json.

    tools/find_irrigation_sites.py            # list the best sites
    tools/find_irrigation_sites.py --write    # also write tools/data/irrigation_sites.json

Documented canals (research/RIVER_NETWORK.md; not the canals of the splay template, a modern analogue):
  * the primary canals of the Eridu region (rivers/eridu_canals.yaml; Jotheri et al., from the preserved relict channels),
  * the canals of the survey between Uruk and Larsa (tools/data/uruk_larsa_canals.json; Adams and Nissen 1972, Jotheri 2016),
  * the channel network of Jotheri et al. 2018 (tools/data/uruk_region_network.json), both its intervals.
Only canals 10 to 14 m wide qualify: the model's canal is 10 m wide. The Euphrates and Tigris (rivers/euphrates.yaml, tigris.yaml,
the Eridu Euphrates), the cities of the disk and the wall of Uruk are obstacles.

The model's canal runs along its +X; the nagkud, the fields and the houses lie to its south (the +Z side, to the right of the
direction of the canal), the orchard to its north: a rectangle of 150 m along the canal and 94 m across (62 m on the scheme side,
32 m on the orchard side). A site is a point of a canal, a direction and a side, where that rectangle (a) crosses no other canal
and no river (a 12 m strip along its own canal is its own), (b) keeps 200 m from every city and 150 m from the wall of Uruk,
(c) inside the terrain patch of Uruk (where there are rasters) has no water but the canal and a ground that varies by less than
1.5 m. Sites are ranked by their distance from the nearest city (the nearest is seen most and walked to soonest), kept at
least 1500 m apart. Frame: metres from Uruk's tell, x east, z south. Deterministic.
"""
import json
import math
import pathlib
import sys

import cv2
import numpy as np
import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
TELL = (31.3228, 45.6389)
U0, U1 = -50.0, 100.0
V_SCHEME, V_ORCHARD = 62.0, 32.0
CITY_M, WALL_M = 200.0, 150.0
HEIGHT_RANGE_M = 1.5
APART_M = 1500.0
RES = 2.0                      # m per pixel of the local window
HALF = 260.0                   # half the window (m)
PATCH_M, PATCH_PX = 6000.0, 4.0


def to_m(lat, lon):
    """Metres east (x) and south (z) of Uruk's tell."""
    return ((lon - TELL[1]) * 111320.0 * math.cos(math.radians(TELL[0])), -(lat - TELL[0]) * 110574.0)


def load():
    canals, rivers, cities = [], [], []
    for c in yaml.safe_load(open(ROOT / "rivers/eridu_canals.yaml", encoding="utf-8")):
        pts = [to_m(la, lo) for la, lo, w in c["points"]]
        width = c["points"][0][2]
        (rivers if c["id"] == "eridu_euphrates" else canals).append({"id": c["id"], "w": width, "pts": pts, "src": "eridu"})
    for c in yaml.safe_load(open(ROOT / "rivers/uruk_larsa_canals.yaml", encoding="utf-8")):
        canals.append({"id": c["id"], "w": c["points"][0][2], "pts": [to_m(la, lo) for la, lo, w in c["points"]], "src": "survey"})
    net = json.loads((ROOT / "tools/data/uruk_region_network.json").read_text(encoding="utf-8"))
    for i, line in enumerate(net["polylines"]):
        canals.append({"id": f"jotheri_{i:03d}", "w": float(line["class_width_m"]), "pts": [tuple(p) for p in line["points"]], "src": "jotheri2018"})
    for name in ("euphrates", "tigris"):
        d = yaml.safe_load(open(ROOT / f"rivers/{name}.yaml", encoding="utf-8"))
        rivers.append({"id": name, "w": max(p[2] for p in d["points"]), "pts": [to_m(p[0], p[1]) for p in d["points"]], "src": "river"})
    for p in yaml.safe_load(open(ROOT / "places/ancient_cities.yaml", encoding="utf-8")):
        g = p.get("geo")
        if g:
            cities.append((p["id"], *to_m(g["latitude_deg"], g["longitude_deg"])))
    cities.append(("uruk", 0.0, 0.0))
    return canals, rivers, cities


def chains(canals):
    """Joins the segments of the Jotheri network that share an end into polylines; the others stay as they are."""
    out, rest = [], []
    for c in canals:
        (rest if c["src"] == "jotheri2018" else out).append(c)
    segs = [c for c in rest]
    used = [False] * len(segs)
    for i, s in enumerate(segs):
        if used[i]:
            continue
        used[i] = True
        line = list(s["pts"])
        grew = True
        while grew:
            grew = False
            for j, t in enumerate(segs):
                if used[j] or t["w"] != s["w"]:
                    continue
                tp = list(t["pts"])
                if math.dist(line[-1], tp[0]) < 3:
                    line += tp[1:]
                elif math.dist(line[-1], tp[-1]) < 3:
                    line += tp[::-1][1:]
                elif math.dist(line[0], tp[-1]) < 3:
                    line = tp[:-1] + line
                elif math.dist(line[0], tp[0]) < 3:
                    line = tp[::-1][:-1] + line
                else:
                    continue
                used[j] = True
                grew = True
                break
        out.append({"id": s["id"], "w": s["w"], "pts": line, "src": s["src"]})
    return out


def walk(line, step=50.0):
    out, carried = [], 0.0
    for (x1, z1), (x2, z2) in zip(line, line[1:]):
        length = math.hypot(x2 - x1, z2 - z1)
        if length < 0.5:
            continue
        tx, tz = (x2 - x1) / length, (z2 - z1) / length
        at = carried
        while at <= length:
            out.append(((x1 + tx * at, z1 + tz * at), (tx, tz)))
            at += step
        carried = at - length
    return out


class Patch:
    """The rasters of Uruk's terrain patch, for the sites inside it."""

    def __init__(self):
        n = int(PATCH_M / PATCH_PX)
        self.n = n
        water = np.array(Image.open(ROOT / "media/terrain/uruk_water.png")) > 0
        self.wet = cv2.resize(water.astype(np.uint8), (n, n), interpolation=cv2.INTER_NEAREST) > 0
        h = np.array(Image.open(ROOT / "media/terrain/uruk_height.png")).astype(np.float64)
        self.h = cv2.resize(h, (n, n), interpolation=cv2.INTER_LINEAR) - 32768.0
        o = json.loads((ROOT / "tools/data/uruk_outlines.json").read_text(encoding="utf-8"))
        self.wall = [(x, z) for x, z, *_ in o["wall"]]

    def px(self, x, z):
        return ((x + PATCH_M / 2) / PATCH_PX, (z + PATCH_M / 2) / PATCH_PX)

    def inside(self, corners):
        return all(abs(x) < PATCH_M / 2 - 100 and abs(z) < PATCH_M / 2 - 100 for x, z in corners)

    def check(self, corners, strip):
        rect = np.zeros((self.n, self.n), np.uint8)
        cv2.fillPoly(rect, [np.array([self.px(*c) for c in corners], np.float32).round().astype(np.int32)], 1)
        sm = np.zeros((self.n, self.n), np.uint8)
        cv2.fillPoly(sm, [np.array([self.px(*c) for c in strip], np.float32).round().astype(np.int32)], 1)
        rect, sm = rect > 0, sm > 0
        if (rect & self.wet & ~sm).any():
            return "wet"
        hv = self.h[rect]
        if (hv.max() - hv.min()) / 10.0 > HEIGHT_RANGE_M:
            return "relief"
        return None


def find():
    canals, rivers, cities = load()
    patch = Patch()
    wall = np.array(patch.wall, np.float32)
    hosts = [c for c in chains(canals) if 10.0 <= c["w"] <= 14.0]
    allcurves = [(c["pts"], c["w"], c["id"]) for c in canals] + [(r["pts"], r["w"] + 40.0, r["id"]) for r in rivers]
    boxes = [(min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts), pts, w, i) for pts, w, i in allcurves]
    found = []
    why = {}
    for host in hosts:
        for (px, pz), (tx, tz) in walk(host["pts"]):
            near = min(cities, key=lambda c: math.hypot(c[1] - px, c[2] - pz))
            d_city = math.hypot(near[1] - px, near[2] - pz)
            if d_city < CITY_M + 100:
                continue
            for flip in (1.0, -1.0):
                ux, uz = tx * flip, tz * flip
                sx, sz = -uz, ux
                bearing = math.degrees(math.atan2(sx, -sz)) % 360.0
                def at(u, v):
                    return (px + ux * u + sx * v, pz + uz * u + sz * v)
                corners = [at(U0, -V_ORCHARD), at(U1, -V_ORCHARD), at(U1, V_SCHEME), at(U0, V_SCHEME)]
                strip = [at(U0, -12), at(U1, -12), at(U1, 12), at(U0, 12)]
                cx = [c[0] for c in corners]; cz = [c[1] for c in corners]
                lo_x, hi_x, lo_z, hi_z = min(cx) - 30, max(cx) + 30, min(cz) - 30, max(cz) + 30
                # the local raster window (2 m a pixel) with the other canals and the rivers
                w = int((hi_x - lo_x) / RES) + 1
                h = int((hi_z - lo_z) / RES) + 1
                if w > 600 or h > 600:
                    continue
                def lp(x, z):
                    return ((x - lo_x) / RES, (z - lo_z) / RES)
                rect = np.zeros((h, w), np.uint8)
                cv2.fillPoly(rect, [np.array([lp(*c) for c in corners], np.float32).round().astype(np.int32)], 1)
                own = np.zeros((h, w), np.uint8)
                cv2.fillPoly(own, [np.array([lp(*c) for c in strip], np.float32).round().astype(np.int32)], 1)
                other = np.zeros((h, w), np.uint8)
                for bx0, bx1, bz0, bz1, pts, wd, cid in boxes:
                    if bx1 < lo_x or bx0 > hi_x or bz1 < lo_z or bz0 > hi_z:
                        continue
                    cv2.polylines(other, [np.array([lp(*p) for p in pts], np.float32).round().astype(np.int32)], False, 1, thickness=max(1, int((wd + 6) / RES)))
                if (rect.astype(bool) & other.astype(bool) & ~own.astype(bool)).any():
                    why["crossing"] = why.get("crossing", 0) + 1
                    continue
                if any(math.hypot(c[1] - x, c[2] - z) < CITY_M + 90 for c in cities for x, z in corners):
                    why["city"] = why.get("city", 0) + 1
                    continue
                relief = None
                if patch.inside(corners):
                    inside = cv2.pointPolygonTest(wall, (px, pz), True)
                    if inside > -WALL_M:
                        why["wall"] = why.get("wall", 0) + 1
                        continue
                    bad = patch.check(corners, strip)
                    if bad:
                        why[bad] = why.get(bad, 0) + 1
                        continue
                found.append({"x": round(px, 1), "z": round(pz, 1), "bearing_deg": round(bearing, 1), "canal": host["id"], "canal_width_m": host["w"],
                              "source": host["src"], "nearest_city": near[0], "city_distance_m": round(d_city), "distance_from_uruk_m": round(math.hypot(px, pz))})
    found.sort(key=lambda s: (s["city_distance_m"], s["canal"]))
    picked = []
    for s in found:
        if all(math.dist((s["x"], s["z"]), (p["x"], p["z"])) >= APART_M for p in picked):
            picked.append(s)
    return picked, len(found), why


if __name__ == "__main__":
    sites, total, why = find()
    for i, s in enumerate(sites[:25]):
        print(i, s)
    print(len(sites), "sites of", total, "candidates; rejected:", why)
    if "--write" in sys.argv:
        (ROOT / "tools/data/irrigation_sites.json").write_text(json.dumps(sites, indent=1), encoding="utf-8")
