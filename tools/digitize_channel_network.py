#!/usr/bin/env python3
"""Digitises the channel networks of the Uruk region from the published figures and writes the canals the disk lacked.

Source: Jotheri, J., Altaweel, M., Tuji, A., Anma, R., Pennington, B., Rost, S., Watanabe, C.: "Holocene fluvial and anthropogenic
processes in the region of Uruk in southern Mesopotamia", Quaternary International (2018), doi:10.1016/j.quaint.2017.11.037
(research/Jotherietal2017.pdf). Two figures:

* Fig. 6 (research/Channel-networks-of-the-Uruk-region-at-different-time-intervals-A-From-the-early.webp, 850 x 579 px): the
  channel networks at four time intervals: **A** the early 4th to the late 1st millennium BCE (the time of Gilgamesh: an
  anastomosing network, channels that enclose flood basins and rejoin), **B** the late 1st millennium BCE to the middle of the
  2nd millennium CE (fewer, larger channels; its main channel from the north-west by Uruk is **dug in the Sasanian period**), **C**
  after the Islamic period to the 1980s, **D** the 1980s to now (Euphrates only). Only A is of our time. The channels are
  dated there by the occupation of the sites along them (Adams 1981) and by radiocarbon;
* Fig. 4 (research/The-identified-channels-and-archaeological-sites-in-the-present-study-see-also-Fig-1.jpeg, 850 x 634 px, 10 km =
  96 px): all the channels identified, of every period (black ribbons of several lines = the larger channels; grey and bluish
  thin lines = small ones), the active channel (blue: today's Euphrates, which has no ancient channels along it: not used), the
  sites of the 4th, 3rd-2nd and 1st millennium (purple, red, black dots) and the tells of Uruk (yellow) and Larsa (the large red
  blob). It is the more exact map but it does not say which channel is of which time: **a channel is taken from it only if panel
  A of Fig. 6 has it too**; what lies outside A is of a later interval (the Sasanian main channel, the channels of the Islamic
  period) and is kept in tools/data/uruk_region_network.json ("later") and not laid.

Georeference of A: the tells of Uruk (219.1, 115.5 px) and Larsa (325.2, 138.3 px) are the pins of both cities (the second is 20.5 km
east and 4.1 km south of the first), which gives 191 m per pixel (the scale bar of the panel, 10 km = 47 px, gives 213 m: the
panel is not exactly to scale); north is up. Of B: the bar (10 km = 69 px) gives 145 m per pixel, Uruk at (219, 407 px).

What is written:

* the lines are skeletonised, the dots and labels removed, simplified to 1.6 px (about 300 m);
* the thickness of a line says its class: thick = large channel (30 m of water), medium (20 m), thin (14 m, 10 m);
* a line that lies within 700 m of a canal already told (tools/data/uruk_larsa_canals.json, the survey's own, more exact map) is
  dropped; what is left is the network the disk lacked: rivers/uruk_region_network.yaml (carved by server and client outside
  Uruk's patch) and tools/data/uruk_region_network.json (metres from Uruk's tell, carved into the patch by build_landscape.py).

Usage: tools/digitize_channel_network.py      (needs numpy, Pillow, scipy, scikit-image, opencv)
"""
import json
import math
import pathlib

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIGURE = ROOT / "research" / "Channel-networks-of-the-Uruk-region-at-different-time-intervals-A-From-the-early.webp"
ANCHOR = (31.3228, 45.6389)
A = {"box": (3, 3, 421, 283), "origin": (219.1, 115.5), "m_per_px": 191.0,
     "texts": [(15, 5, 50, 55), (385, 0, 425, 40), (5, 252, 72, 280), (180, 100, 214, 126), (290, 125, 320, 150), (300, 252, 345, 272)],
     "tells": [(219, 115, 10), (325, 138, 9)]}
B = {"box": (4, 296, 421, 576), "origin": (219.0, 407.0), "m_per_px": 145.0,
     "texts": [(28, 295, 52, 350), (385, 292, 425, 330), (25, 526, 76, 568), (225, 400, 264, 421)],
     "tells": [(219, 407, 10)]}
DEDUP_M = 700.0


def extract(image, panel):
    x1, y1, x2, y2 = panel["box"]
    mask = np.zeros(image.shape, bool)
    mask[y1:y2, x1:x2] = image[y1:y2, x1:x2] < 110
    for a, b, c, d in panel["texts"]:
        mask[b:d, a:c] = False
    yy, xx = np.ogrid[: image.shape[0], : image.shape[1]]
    for cx, cy, radius in panel["tells"]:
        mask[(xx - cx) ** 2 + (yy - cy) ** 2 <= radius * radius] = False
    # the dots (sites) survive an opening that removes the lines
    opened = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))) > 0
    labels, count = ndi.label(opened)
    dots = np.zeros_like(mask)
    for i in range(1, count + 1):
        if (labels == i).sum() < 70:
            dots |= labels == i
    lines = ndi.binary_closing(mask & ~ndi.binary_dilation(dots, iterations=1), structure=np.ones((3, 3)), iterations=2)
    skeleton = skeletonize(lines)
    labels, count = ndi.label(skeleton, structure=np.ones((3, 3)))
    sizes = ndi.sum(skeleton, labels, range(1, count + 1))
    keep = np.zeros_like(skeleton)
    for i, size in enumerate(sizes, 1):
        if size >= 14:
            keep |= labels == i
    return keep, ndi.distance_transform_edt(mask | ndi.binary_dilation(dots, iterations=1))


def trace(skeleton, thickness, eps=1.6, min_length=6):
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
            if len(path) >= min_length:
                array = np.array([(x, y) for y, x in path], np.float32).reshape(-1, 1, 2)
                simple = cv2.approxPolyDP(array, eps, False).reshape(-1, 2)
                width_px = 2.0 * float(np.mean([thickness[y, x] for y, x in path]))
                out.append({"px": [[float(x), float(y)] for x, y in simple], "thickness_px": round(width_px, 2)})
    return out


def width_class(thickness_px):
    if thickness_px >= 4.2:
        return 30.0
    if thickness_px >= 3.0:
        return 20.0
    if thickness_px >= 2.2:
        return 14.0
    return 10.0


def local(panel, point):
    return ((point[0] - panel["origin"][0]) * panel["m_per_px"], (point[1] - panel["origin"][1]) * panel["m_per_px"])


def geo(east, south):
    return ANCHOR[0] - south / 110574.0, ANCHOR[1] + east / (111320.0 * math.cos(math.radians(ANCHOR[0])))


def near(point, polylines, limit):
    """Whether a point lies within `limit` metres of any of the polylines (lists of (x, z))."""
    for line in polylines:
        for (x1, z1), (x2, z2) in zip(line, line[1:]):
            dx, dz = x2 - x1, z2 - z1
            length2 = dx * dx + dz * dz
            t = 0.0 if length2 == 0 else max(0.0, min(1.0, ((point[0] - x1) * dx + (point[1] - z1) * dz) / length2))
            if math.hypot(point[0] - (x1 + t * dx), point[1] - (z1 + t * dz)) <= limit:
                return True
    return False


def densify(points, step=200.0):
    out = []
    for a, b in zip(points, points[1:]):
        n = max(1, int(math.dist(a, b) / step))
        out.extend((a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n))
    out.append(points[-1])
    return out


FIGURE_IDENTIFIED = ROOT / "research" / "The-identified-channels-and-archaeological-sites-in-the-present-study-see-also-Fig-1.jpeg"
# figure labels, boreholes (rings) and the scale bar, as boxes (x1, y1, x2, y2) and discs (x, y, r) to blank out
IDENTIFIED_BOXES = [(8, 420, 80, 520), (5, 540, 130, 572), (78, 160, 330, 195), (370, 185, 440, 215), (455, 155, 500, 195),
                    (570, 140, 640, 178), (95, 435, 190, 465), (240, 282, 335, 310)]
IDENTIFIED_DISCS = [(424, 193, 13), (480, 162, 13), (612, 168, 13), (311, 318, 13), (171, 447, 13)]


def tell_pixels(rgb):
    """Centres of the tell of Uruk (yellow) and of Larsa (the largest red blob) in the identified-channels figure."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    height = rgb.shape[0]
    yellow = (r > 200) & (g > 180) & (b < 120)
    yellow[540:] = False
    ys, xs = np.nonzero(yellow)
    uruk = (float(xs.mean()), float(ys.mean()))
    red = (r > 140) & (g < 110) & (b < 110)
    red[540:] = False
    labels, count = ndi.label(red)
    sizes = ndi.sum(red, labels, range(1, count + 1))
    ys, xs = np.nonzero(labels == int(np.argmax(sizes)) + 1)
    return uruk, (float(xs.mean()), float(ys.mean()))


def extract_identified(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h, w = r.shape
    valid = np.zeros((h, w), bool)
    valid[6:567, 6:845] = True
    active = (b > r + 45) & (b > g + 25) & (r < 140)
    active_near = ndi.binary_dilation(active, iterations=3)
    sites = ndi.binary_dilation(((r > 90) & (b > 90) & (g < r - 30) & (g < b - 30)) | ((r > 140) & (g < 110) & (b < 110)) | ((r > 200) & (g > 180) & (b < 120)), iterations=1)
    ground = (abs(r - 156) < 28) & (abs(g - 200) < 22) & (abs(b - 122) < 30)
    black = (r < 150) & (g < 165) & (b < 150) & ~ground
    bluish = (b > g) & (b > r + 15) & (g < 178) & ~ground      # the thin bluish-grey lines: small channels
    line = (black | bluish) & valid & ~active_near & ~sites
    for x1, y1, x2, y2 in IDENTIFIED_BOXES:
        line[y1:y2, x1:x2] = False
    yy, xx = np.ogrid[:h, :w]
    uruk, larsa = tell_pixels(rgb)
    for cx, cy, radius in IDENTIFIED_DISCS + [(uruk[0], uruk[1], 17), (larsa[0], larsa[1], 15)]:
        line[(xx - cx) ** 2 + (yy - cy) ** 2 <= radius * radius] = False
    opened = cv2.morphologyEx(line.astype(np.uint8), cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))) > 0
    labels, count = ndi.label(opened)
    dots = np.zeros_like(line)
    for i in range(1, count + 1):
        if (labels == i).sum() < 60:
            dots |= labels == i
    lines = ndi.binary_closing(line & ~ndi.binary_dilation(dots, iterations=1), structure=np.ones((3, 3)), iterations=1)
    skeleton = skeletonize(lines)
    labels, count = ndi.label(skeleton, structure=np.ones((3, 3)))
    sizes = ndi.sum(skeleton, labels, range(1, count + 1))
    keep = np.zeros_like(skeleton)
    for i, size in enumerate(sizes, 1):
        if size >= 12:
            keep |= labels == i
    return keep, ndi.distance_transform_edt(lines), uruk, larsa


def length_m(points):
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def accept(points, accepted_lines, limit):
    samples = densify(points, 120.0)
    return sum(near(sample, accepted_lines, limit) for sample in samples) < 0.7 * len(samples)


def main():
    told = json.loads((ROOT / "tools" / "data" / "uruk_larsa_canals.json").read_text(encoding="utf-8"))["polylines"]
    accepted_lines = [[tuple(p) for p in line["points"]] for line in told]
    # panel A of Fig. 6: the network of our time
    image = np.array(Image.open(FIGURE).convert("L")).astype(int)
    skeleton, thickness = extract(image, A)
    panel_a = []
    for line in trace(skeleton, thickness):
        panel_a.append(([local(A, p) for p in line["px"]], line["thickness_px"]))
    panel_a_lines = [points for points, _ in panel_a]
    # Fig. 4: the finer map; a channel counts only where panel A has one (within 700 m)
    rgb = np.array(Image.open(FIGURE_IDENTIFIED).convert("RGB")).astype(int)
    skeleton, thickness, uruk, larsa = extract_identified(rgb)
    pixel_m = 20900.0 / math.dist(uruk, larsa)      # Uruk to Larsa is 20.9 km: 96.8 m per pixel (the boreholes of the paper agree)
    panel = {"origin": uruk, "m_per_px": pixel_m}
    lines = trace(skeleton, thickness)
    lines.sort(key=lambda line: -length_m([local(panel, p) for p in line["px"]]))
    lacking, later, dropped = [], [], {"twin": 0, "told": 0, "panel A only": 0}
    for line in lines:
        points = [local(panel, p) for p in line["px"]]
        if length_m(points) < 600.0:
            continue
        record = {"class_width_m": width_class(line["thickness_px"]), "points": [[round(x, 1), round(z, 1)] for x, z in points]}
        samples = densify(points, 120.0)
        in_a = sum(near(sample, panel_a_lines, DEDUP_M) for sample in samples) >= 0.6 * len(samples)
        if not in_a:
            later.append(record)                      # a channel of a later interval (B, C or D of the figure)
            continue
        if not accept(points, accepted_lines, DEDUP_M * 0.35):
            dropped["twin"] += 1
            continue
        accepted_lines.append(points)
        lacking.append(record)
    # panel A itself: what the finer map and the survey do not have
    for points, thick in panel_a:
        if not accept(points, accepted_lines, DEDUP_M):
            dropped["told"] += 1
            continue
        dropped["panel A only"] += 1
        accepted_lines.append(points)
        lacking.append({"class_width_m": width_class(thick), "points": [[round(x, 1), round(z, 1)] for x, z in points]})
    result = {"earlier": [], "later": later}
    skeleton, thickness = extract(image, B)
    for line in trace(skeleton, thickness):
        result["earlier"].append({"class_width_m": width_class(line["thickness_px"]),
                                  "points": [[round(x, 1), round(z, 1)] for x, z in (local(B, p) for p in line["px"])]})
    result["polylines"] = lacking
    result["description"] = ("The channels of the network of the time of Gilgamesh (Fig. 6 A of Jotheri et al. 2018, in the finer drawing of "
                             "its Fig. 4) not yet told by the survey canals (tools/digitize_channel_network.py): metres east (x) and south "
                             "(z) of Uruk's tell. 'earlier' is panel B (a later interval), 'later' the channels of Fig. 4 that panel A lacks; "
                             "neither is laid.")
    (ROOT / "tools" / "data" / "uruk_region_network.json").write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
    rows = []
    for number, line in enumerate(lacking, 1):
        pts = ", ".join("[%.5f, %.5f, %.0f]" % (*geo(x, z), line["class_width_m"]) for x, z in line["points"])
        rows.append("- {id: region_%03d, points: [%s]}\n" % (number, pts))
    header = ("# The channel network of the time of Gilgamesh round Uruk and Larsa (tools/digitize_channel_network.py): "
              "[latitude, longitude, width_m]. Jotheri et al. 2018, see research/RIVER_NETWORK.md.\n")
    out = ROOT / "rivers"
    for old in out.glob("uruk_region_network*.yaml"):
        old.unlink()
    chunks, current, size = [], [], 0
    for row in rows:
        if size + len(row) > 800_000:
            chunks.append(current)
            current, size = [], 0
        current.append(row)
        size += len(row)
    chunks.append(current)
    for number, chunk in enumerate(chunks, 1):
        (out / ("uruk_region_network_%02d.yaml" % number)).write_text(header + "".join(chunk), encoding="utf-8")
    total = sum(length_m([tuple(p) for p in l["points"]]) for l in lacking) / 1000.0
    print("%d lines laid (%.0f km, %d points); %s; later-interval channels kept aside: %d; panel B: %d lines"
          % (len(lacking), total, sum(len(l["points"]) for l in lacking), dropped, len(later), len(result["earlier"])))


if __name__ == "__main__":
    main()
