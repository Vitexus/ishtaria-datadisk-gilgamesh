#!/usr/bin/env python3
"""Digitises the irrigation canals and the ancient Euphrates of the Eridu region from Fig. 5 of Jotheri et al. 2025.

Source: Jotheri, J., Rokan, M., Al-Ghanim, A., Rayne, L., de Gruchy, M., Alabdan, R.: "Identifying the preserved network of irrigation
canals in the Eridu region, southern Mesopotamia", Antiquity 99 (2025), doi:10.15184/aqy.2025.19 (research/identifying-the-preserved-
network-...pdf; open access, CC BY 4.0: the figure is reproduced here with that attribution). Fig. 5 (research/images/eridu-canals-fig5.png,
1583 x 684 px): "The reconstructed irrigation canal network in context with the ancient Euphrates riverbed and the archaeological sites of
the Eridu region" on a Corona image: canals in red, the ancient Euphrates in light blue, sites in black, 2 km = 120 px, north up.

What the paper says (all dates: the network of all periods of the region's occupation, Ubaid to the early 1st millennium BCE, never all
at once): more than 200 primary canals joined to the Euphrates, 1-9 km long and 2-5 m wide; more than 4000 minor and branch canals 10-200 m
long and 1-2 m wide, around the edges of more than 700 farms of 500-20 000 square metres; both banks canalised, the north one more.

Georeference: the tell of Eridu (619, 258 px) is the pin of the city (30.8261 N, 45.9947 E); 1 px = 16.67 m.

What is written (rivers/eridu_canals.yaml): the **primary canals** only: red lines of 800 m and more (the lines are 2-5 m wide in fact; the
disk's narrowest water is 10 m, so a primary canal is told 10 m wide, one of 3 km or more 14 m), and the centre line of the ancient
Euphrates (120 m of water). The dense net of minor canals (thousands of lines of under 200 m, the farm edges) is not laid: at the narrowest
water of the disk it would drown the farmland it irrigates.

Usage: tools/digitize_eridu_canals.py      (needs numpy, Pillow, scipy, scikit-image, opencv)
"""
import math
import pathlib

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGURE = ROOT / "research" / "images" / "eridu-canals-fig5.png"
ORIGIN_PX, ORIGIN_GEO, M_PER_PX = (619.0, 258.0), (30.8261, 45.9947), 2000.0 / 120.0
MIN_PRIMARY_M, LONG_M = 700.0, 3000.0
RIVER_WIDTH_M = 120.0
OVERLAY = None          # a path: writes a picture of what was taken, for a check


def geo(point):
    east = (point[0] - ORIGIN_PX[0]) * M_PER_PX
    south = (point[1] - ORIGIN_PX[1]) * M_PER_PX
    return (ORIGIN_GEO[0] - south / 110574.0, ORIGIN_GEO[1] + east / (111320.0 * math.cos(math.radians(ORIGIN_GEO[0]))))


def length_m(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:])) * M_PER_PX


def trace(skeleton, eps=2.0):
    points = set(zip(*np.nonzero(skeleton)))

    def neighbours(p):
        y, x = p
        return [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and (y + dy, x + dx) in points]

    nodes = {p for p in points if len(neighbours(p)) != 2}
    seen, out = set(), []
    for start in nodes:
        for first in neighbours(start):
            if frozenset((start, first)) in seen:
                continue
            path, previous, current = [start, first], start, first
            while current not in nodes:
                candidates = [c for c in neighbours(current) if c != previous]
                if not candidates:
                    break
                previous, current = current, candidates[0]
                path.append(current)
            for a, b in zip(path, path[1:]):
                seen.add(frozenset((a, b)))
            array = np.array([(x, y) for y, x in path], np.float32).reshape(-1, 1, 2)
            out.append([(float(x), float(y)) for x, y in cv2.approxPolyDP(array, eps, False).reshape(-1, 2)])
    return out


def longest_path(skeleton, eps):
    """The longest path of a skeleton (two breadth-first searches: the farthest pixel from any, then the farthest from that)."""
    from collections import deque
    points = set(zip(*np.nonzero(skeleton)))

    def bfs(start):
        previous, queue, last = {start: None}, deque([start]), start
        while queue:
            last = queue.popleft()
            y, x = last
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (y + dy, x + dx)
                    if (dy or dx) and q in points and q not in previous:
                        previous[q] = last
                        queue.append(q)
        return last, previous

    end, _ = bfs(next(iter(points)))
    other, previous = bfs(end)
    path = []
    while other is not None:
        path.append(other)
        other = previous[other]
    array = np.array([(x, y) for y, x in path], np.float32).reshape(-1, 1, 2)
    return [(float(x), float(y)) for x, y in cv2.approxPolyDP(array, eps, False).reshape(-1, 2)]


def straight_canals(skeleton, min_px):
    """The long straight canals of the net: probabilistic Hough lines on the skeleton, the ones that lie on one line (same angle, within
    4 px) and overlap or nearly touch joined into one. Returns lines of two points."""
    mask = skeleton.astype(np.uint8) * 255
    found = cv2.HoughLinesP(mask, 1, np.pi / 360.0, threshold=14, minLineLength=min_px, maxLineGap=8)
    segments = [] if found is None else [tuple(map(float, l[0])) for l in found]
    items = []
    for x1, y1, x2, y2 in segments:
        angle = math.atan2(y2 - y1, x2 - x1) % math.pi
        items.append({"angle": angle, "pts": [(x1, y1), (x2, y2)]})
    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                da = abs(a["angle"] - b["angle"])
                if min(da, math.pi - da) > math.radians(3.0):
                    continue
                ux, uy = math.cos(a["angle"]), math.sin(a["angle"])
                ox, oy = a["pts"][0]
                off = lambda p: (p[0] - ox) * -uy + (p[1] - oy) * ux
                tt = lambda p: (p[0] - ox) * ux + (p[1] - oy) * uy
                if max(abs(off(p)) for p in b["pts"]) > 4.0:
                    continue
                ta = sorted(tt(p) for p in a["pts"])
                tb = sorted(tt(p) for p in b["pts"])
                if tb[0] > ta[1] + 8.0 or ta[0] > tb[1] + 8.0:
                    continue
                lo, hi = min(ta[0], tb[0]), max(ta[1], tb[1])
                a["pts"] = [(ox + ux * lo, oy + uy * lo), (ox + ux * hi, oy + uy * hi)]
                del items[j]
                changed = True
                break
            if changed:
                break
    return [item["pts"] for item in items]


def merge(lines, join=3.0):
    """Chains the lines of the tracer (it cuts at every junction) into canals: at a junction two lines that continue
    straight on (within about 30 degrees) are one canal. One pass over the junctions, no search."""
    ends = {}
    for index, line in enumerate(lines):
        for which in (0, -1):
            node = (round(line[which][0] / join), round(line[which][1] / join))
            ends.setdefault(node, []).append((index, which))

    def direction(index, which):
        line = lines[index]
        a, b = (line[0], line[min(2, len(line) - 1)]) if which == 0 else (line[-1], line[max(-3, -len(line))])
        v = (b[0] - a[0], b[1] - a[1])
        n = math.hypot(*v) or 1.0
        return (v[0] / n, v[1] / n)

    link = {}                                  # (line, end) -> (line, end) it continues into
    for node, members in ends.items():
        candidates = []
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                (a, ea), (b, eb) = members[i], members[j]
                if a == b:
                    continue
                da, db = direction(a, ea), direction(b, eb)
                cosine = da[0] * db[0] + da[1] * db[1]
                if cosine < -0.86:
                    candidates.append((cosine, members[i], members[j]))
        used = set()
        for cosine, m1, m2 in sorted(candidates):
            if m1 in used or m2 in used:
                continue
            used.update((m1, m2))
            link[m1], link[m2] = m2, m1
    seen, chains = set(), []
    for start in range(len(lines)):
        if start in seen:
            continue
        # walk to one end of the chain, then along it
        index, which = start, 0
        while (index, which) in link:
            nxt, nwhich = link[(index, which)]
            if nxt in seen or nxt == start:
                break
            index, which = nxt, -1 if nwhich == 0 else 0
            if index == start:
                break
        chain, cursor, enter = [], index, which          # `which` is the free end we start from
        line_pts = lines[cursor] if enter == 0 else lines[cursor][::-1]
        while True:
            seen.add(cursor)
            chain.extend(line_pts if not chain else line_pts[1:])
            exit_end = -1 if enter == 0 else 0
            target = link.get((cursor, exit_end))
            if target is None or target[0] in seen:
                break
            cursor, enter = target[0], target[1]
            line_pts = lines[cursor] if enter == 0 else lines[cursor][::-1]
        chains.append(chain)
    return chains


def main():
    rgb = np.array(Image.open(FIGURE).convert("RGB")).astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h, w = r.shape
    keep_area = np.ones((h, w), bool)
    keep_area[512:, :400] = False                 # the legend
    keep_area[:6, :] = False
    red = (r > 140) & (r - g > 55) & (r - b > 45) & keep_area      # thin lines are paler than the thick ones
    red = ndi.binary_closing(red, structure=np.ones((3, 3)), iterations=2)
    skeleton = skeletonize(red)
    labels, count = ndi.label(skeleton, structure=np.ones((3, 3)))
    sizes = ndi.sum(skeleton, labels, range(1, count + 1))
    clean = np.zeros_like(skeleton)
    for i, size in enumerate(sizes, 1):
        if size >= 10:
            clean |= labels == i
    # the tracer cuts at every junction: the stubs of side canals shorter than 100 m are removed (twice), then two lines that
    # continue straight on through a junction are one canal
    for _ in range(2):
        edges = trace(clean, eps=1.0)
        ends = {}
        for line in edges:
            for end in (line[0], line[-1]):
                ends[(round(end[0]), round(end[1]))] = ends.get((round(end[0]), round(end[1])), 0) + 1
        pruned = np.zeros(clean.shape, np.uint8)
        for line in edges:
            leaf = ends[(round(line[0][0]), round(line[0][1]))] == 1 or ends[(round(line[-1][0]), round(line[-1][1]))] == 1
            if leaf and length_m(line) < 100.0:
                continue
            cv2.polylines(pruned, [np.array(line, np.int32)], False, 1, 1)
        clean = skeletonize(pruned > 0)
    lines = merge(trace(clean))
    primary = [line for line in lines if length_m(line) >= MIN_PRIMARY_M]
    # the ancient Euphrates: the light-blue region; its centre line = the longest path of its skeleton
    blue = (b > r + 20) & (b > g + 5) & (r > 130) & (r < 215) & keep_area
    blue = ndi.binary_opening(blue, iterations=2)
    labels, count = ndi.label(blue)
    big = int(np.argmax(ndi.sum(blue, labels, range(1, count + 1)))) + 1
    river = longest_path(skeletonize(labels == big), eps=6.0)
    rows = []
    for number, line in enumerate(sorted(primary, key=lambda l: -length_m(l)), 1):
        width = 14 if length_m(line) >= LONG_M else 10
        rows.append("- {id: eridu_canal_%03d, points: [%s]}\n" % (number, ", ".join("[%.5f, %.5f, %d]" % (*geo(p), width) for p in line)))
    header = ("# The primary irrigation canals of the Eridu region and the ancient Euphrates there (tools/digitize_eridu_canals.py): "
              "[latitude, longitude, width_m]. Jotheri et al. 2025, Antiquity, CC BY 4.0, see research/RIVER_NETWORK.md.\n")
    river_row = "- {id: eridu_euphrates, points: [%s]}\n" % ", ".join("[%.5f, %.5f, %d]" % (*geo(p), RIVER_WIDTH_M) for p in river)
    (ROOT / "rivers" / "eridu_canals.yaml").write_text(header + river_row + "".join(rows), encoding="utf-8")
    if OVERLAY:
        picture = cv2.cvtColor(np.array(Image.open(FIGURE).convert("L")).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        for line in primary:
            cv2.polylines(picture, [np.array(line, np.int32)], False, (255, 0, 0), 3)
        cv2.polylines(picture, [np.array(river, np.int32)], False, (0, 160, 0), 4)
        cv2.imwrite(OVERLAY, picture)
    total = sum(length_m(l) for l in primary) / 1000.0
    print("%d lines in all, %d primary canals (%.0f km), river %.1f km"
          % (len(lines), len(primary), total, length_m(river) / 1000.0))


if __name__ == "__main__":
    main()
