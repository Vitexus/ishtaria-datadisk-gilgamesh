#!/usr/bin/env python3
"""Build the real planet of the world: equirectangular relief and water mask.

A world generated with this disk is the Early Dynastic Earth (c. 2700 BCE), not a
procedural planet: the real outline of every continent and real heights, with the
documented Mesopotamian reconstruction of the Epic's time (research/WORLD.md).
The two rasters this tool writes are what `world.terrain` in datadisk.yaml names
and `ishtaria-worldgen --earth` strips onto the cube-sphere.

Sources:

| What | Source | Notes |
| --- | --- | --- |
| Relief and bathymetry | ETOPO 2022, 60 arc-second bed grid (NOAA NCEI, public domain) | Downloaded once into tools/cache/ and never shipped whole; the shipped rasters derive from it and datadisk.yaml carries the attribution. |
| Coastline | The ETOPO data itself (elevation <= 0 is water) | Shallow seas and dry depressions are decided by the mask, not the quantised heights. |
| Persian Gulf shoreline, the marshes, Euphrates, Tigris | Documented reconstruction (see research/WORLD.md) | The palaeogeography of southern Iraq since Gilgamesh: Aqrawi (2001), Steinkeller (2001), Pournelle (2003), Hritz (2021), Forti et al. (2022, the Abu Tbeirah excavations), Hammer et al. (2022), Geyer and Sauvage (2020). The Gulf reached the Eridu-Ur line in the Early Dynastic period with a brackish lagoon in front of it; the Tigris ran past Girsu, Lagash and Nigin until ~2500-2000 BCE; both rivers had separate mouths into the Gulf. |

Output: media/world/height.pgm (16-bit signed metres, big-endian) and
media/world/water.pgm (0 land, 255 water), both 7200 x 3600 (0.05 degrees a pixel,
twice as wide as tall, row 0 at +90). The water mask wins over the heights at the
coastline, so the shallow Gulf stays sea and the dry Qattara depression stays land
however the 8-bit world strip quantises them.

Usage: tools/build_world_map.py [--degrees 0.05]
Requires: numpy, Pillow, tifffile and imagecodecs (the ETOPO GeoTIFF predictor);
caches the ETOPO download in tools/cache/.
"""
import argparse
import math
import pathlib
import sys
import urllib.request

import numpy as np
import tifffile
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "cache"
WORLD = ROOT / "media" / "world"
ETOPO = "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/60s/60s_bed_elev_gtif/ETOPO_2022_v1_60s_N90W180_bed.tif"
USER_AGENT = "IshtariaDatadisk/0.2 (research; https://git.vitexsoftware.com/Ishtaria)"

# The Early Dynastic (c. 2700 BCE) reconstruction, see research/WORLD.md.
#
# The shoreline of the Gulf and the rivers follow the published reconstructions of
# southern Iraq's palaeogeography, simplified to one line or one polygon each:
# Aqrawi (2001); Steinkeller (2001); Pournelle (2003); Adams (1981); Engel &
# Brueckner (2018); Hritz (2021) - the Umma-Lagash landscape; Forti et al. (2022)
# - the Abu Tbeirah excavations; Hammer, Stone and McMahon (2022) - the river past
# Girsu, Lagash and Nigin; Geyer and Sauvage (2020) - the prograding coastlines.
#
# Gulf shoreline: latitude of the water's edge for each longitude of the basin's
# head. The mid-Holocene transgression reached the Nasiriyah line around 4000 BCE;
# by the Early Dynastic period the delta had prograded to the Eridu-Ur line, with
# a brackish lagoon and marsh belt (Abu Tbeirah: freshwater to brackish marsh)
# rather than open sea in front of it. The rest of the shoreline is today's.
GULF_SHORELINE = [
    (42.8, 29.4),
    (43.4, 29.7),
    (44.0, 30.0),
    (44.6, 30.2),
    (45.2, 30.35),
    (45.6, 30.55),
    (45.9, 30.65),
    (46.2, 30.70),
    (46.5, 30.60),
    (46.8, 30.65),
    (47.2, 30.55),
    (47.6, 30.30),
    (48.0, 30.00),
    (48.4, 29.75),
    (48.6, 29.55),
]
GULF_BASIN = (42.5, 28.0, 48.7, 31.3)  # west, south, east, north: where the shoreline applies
# The Euphrates of the Epic: Hit through Kish, Nippur and Shuruppak, past Uruk
# (east of the tell, as the city's patch has it), Larsa and Ur to the lagoon of
# the Gulf (Adams 1981 course, simplified; Ur stands on the bank, not in the channel).
EUPHRATES = [
    (42.82, 33.64),
    (43.40, 33.20),
    (44.00, 32.80),
    (44.60, 32.55),
    (45.06, 32.05),
    (45.50, 31.80),
    (45.68, 31.35),
    (45.95, 31.05),   # just east of Larsa
    (46.18, 30.88),   # just east of Ur
    (46.15, 30.50),   # into the lagoon south of Ur
]
# The western branch to Eridu: the oldest city of Sumer stood on the shore of the
# lagoon, on its own branch west of the main channel, which ran past Larsa's west
# side (Adams 1981; Larsa's pixel must stay land, and so must Eridu's).
ERIDU_BRANCH = [
    (45.80, 31.15),
    (45.74, 30.95),   # just west of Larsa
    (45.50, 30.82),   # just west of Eridu
    (45.60, 30.50),   # into the lagoon
]
# The Tigris of that time: it avulsed from the Euphrates near Sippar around
# 4000 BCE, ran to Adab and Larsa, and in the Early Dynastic period turned past
# Girsu, Lagash and Nigin into the marshes and the Gulf (Steinkeller 2001;
# Hritz 2021; Hammer et al. 2022); it moved to today's more eastern course only
# between 2500 and 2000 BCE (Aqrawi 2001). The cities sit on its west bank.
TIGRIS = [
    (43.15, 36.35),
    (43.50, 35.45),
    (43.87, 34.20),
    (44.40, 33.60),
    (45.20, 32.95),
    (45.82, 32.50),   # Kut
    (46.10, 31.95),
    (46.58, 31.60),   # just east of Girsu
    (46.70, 31.00),   # just east of Lagash and Nigin
    (46.85, 30.55),
    (47.05, 30.35),   # into the marshes and the Gulf
]
# The great leveed joint channel of the Tigris and the Euphrates (Adams 1981;
# Pournelle 2003): it passed Umma and Girsu, and its levee is reused by the
# modern Shatt al-Gharraf (Hritz 2021). Umma stands on its west bank.
JOINT_CHANNEL = [
    (45.30, 31.95),
    (45.95, 31.68),   # just east of Umma
    (46.35, 31.65),
    (46.58, 31.60),   # joins the Tigris by Girsu
]
# Tells that stood in the marshes and the lagoon, on the water but never in it:
# their pixels are carved back to land (Forti et al. 2022: cities of the delta on
# "turtlebacks"; Kissik is a port of the lagoon, 33 km SE of Ur). The same list
# keeps the coastal and riverside tells of the wider world (places/ancient_cities.yaml,
# research/ANCIENT_CITIES.md) dry: at 0.05 degrees one block can be half sea though
# the tell itself stood on dry ground (Ugarit, Sidon, Liman Tepe), and the one-line
# rivers of the reconstruction can cross the block of a city that stood on their
# bank (Kish, Shuruppak).
SHORE_SITES = [
    ("Kissik (Tell al-Lahm)", 30.61, 46.36),
    ("Kish (Tell al-Uhaymir)", 32.5403, 44.6047),
    ("Shuruppak (Tell Fara)", 31.7775, 45.5097),
    ("Ugarit (Ras Shamra)", 35.6019, 35.7856),
    ("Sidon", 33.5607, 35.3683),
    ("Liman Tepe", 38.3633, 26.7758),
]
# The permanent marshes of Early Dynastic Sumer, water in the mask: the brackish
# lagoon in front of the Eridu-Ur shoreline (the environment of Abu Tbeirah and
# of the later Sealand) and the marshes east of the Tigris, remnant of the bay
# near al-Amara that the Tigris was filling (Aqrawi 2001; Hritz 2021).
MARSHES = [
    ("the Eridu-Ur lagoon", [
        (45.25, 30.45),
        (45.90, 30.75),
        (46.15, 30.78),
        (46.35, 30.55),   # the shore bends around Kissik (Tell al-Lahm)
        (47.00, 30.50),
        (47.35, 30.15),
        (46.50, 29.60),
        (45.50, 29.95),
    ]),
    ("the marshes east of the Tigris", [
        (46.55, 30.90),
        (47.30, 31.55),
        (48.05, 31.25),
        (47.90, 30.40),
        (47.00, 30.25),
    ]),
]
# Dry depressions below sea level that must stay land (the mask decides, not the
# heights): the sea stopped at their sills in 2700 BCE too.
DRY_DEPRESSIONS = [
    ("Qattara", 28.5, 30.2, 26.5, 28.7),      # Egypt, -134 m
    ("Death Valley", 35.8, 37.0, -117.5, -116.3),
    ("Turfan", 42.4, 43.1, 88.4, 90.0),
    ("Danakil", 12.9, 14.3, 40.1, 41.2),      # salt pans, dry in the Bronze Age
    ("Salton Sink", 33.1, 33.6, -116.1, -115.5),
    ("Laguna del Carbon", -49.6, -49.1, -68.5, -68.2),
    # The floor of the Jordan valley between the Dead Sea and the Sea of Galilee is
    # dry land far below sea level (Jericho stands at about -250 m; the two seas
    # themselves stay water - their blocks lie outside this rectangle).
    ("Jordan Valley", 31.82, 32.62, 35.30, 35.60),
]


def fetch_etopo(target):
    if target.is_file() and target.stat().st_size > 400_000_000:
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading ETOPO 2022 60s bed grid ({ETOPO.rsplit('/', 1)[1]}, about 480 MiB)...")
    request = urllib.request.Request(ETOPO, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=280) as response, open(target, "wb") as out:
        while True:
            block = response.read(1 << 20)
            if not block:
                break
            out.write(block)
    return target


def shoreline_latitude(longitude):
    """Interpolated Early Dynastic Gulf shoreline latitude at `longitude`."""
    for (west, south), (east, north) in zip(GULF_SHORELINE, GULF_SHORELINE[1:]):
        if west <= longitude <= east:
            span = east - west
            return south + (north - south) * ((longitude - west) / span if span else 1.0)
    return None


def draw_polyline(draw, points, size, width=1):
    scaled = [((lon + 180.0) / 360.0 * size[0], (90.0 - lat) / 180.0 * size[1]) for lon, lat in points]
    draw.line(scaled, fill=255, width=width, joint="curve")


def build(degrees):
    etopo = fetch_etopo(CACHE / "ETOPO_2022_v1_60s_N90W180_bed.tif")
    grid = tifffile.TiffFile(etopo).pages[0].asarray()  # 10800 x 21600, row 0 at 90N, column 0 at 180W
    if grid.shape != (10800, 21600):
        raise SystemExit(f"unexpected ETOPO shape {grid.shape}")
    width, height = round(360.0 / degrees), round(180.0 / degrees)
    if grid.shape[1] % width or grid.shape[0] % height:
        raise SystemExit(f"{degrees} degrees does not divide the ETOPO grid")
    step_lon, step_lat = grid.shape[1] // width, grid.shape[0] // height
    print(f"ETOPO {grid.shape[0]}x{grid.shape[1]} -> {width}x{height} ({degrees} degrees, "
          f"block {step_lat}x{step_lon} cells)")

    # Block means for the relief, majority for the water: the block is water when at
    # least half of its cells lies at or below sea level.
    blocks = grid.reshape(height, step_lat, width, step_lon)
    metres = np.clip(np.round(blocks.mean(axis=(1, 3))), -32768, 32767).astype(np.int16)
    water = ((blocks <= 0).mean(axis=(1, 3)) >= 0.5).astype(np.uint8) * 255
    del grid, blocks
    print("  resampled the relief and the water mask")

    # Dry depressions stay land even below sea level.
    for name, south, north, west, east in DRY_DEPRESSIONS:
        first = int((90.0 - north) / 180.0 * height)
        last = int((90.0 - south) / 180.0 * height) + 1
        left = int((west + 180.0) / 360.0 * width)
        right = int((east + 180.0) / 360.0 * width) + 1
        before = int((water[first:last, left:right] == 255).sum())
        water[first:last, left:right] = 0
        print(f"  {name}: {before} sea pixels turned back into land")

    # The Early Dynastic Gulf: everything between today's shoreline and the
    # reconstructed one becomes shallow sea. The pre-floodplain relief is kept
    # for the tells that stood in the water.
    plain = metres.copy()
    west, south, east, north = GULF_BASIN
    lons = (np.arange(width) + 0.5) / width * 360.0 - 180.0
    lats = 90.0 - (np.arange(height) + 0.5) / height * 180.0
    shore = np.array([shoreline_latitude(lon) for lon in lons], dtype=np.float64)
    inside_columns = (lons >= west) & (lons <= east)
    flooded = 0
    for column in np.flatnonzero(inside_columns & ~np.isnan(shore)):
        rows = np.flatnonzero((lats < shore[column]) & (lats > south))
        was_land = water[rows, column] == 0
        metres[rows[was_land], column] = np.minimum(metres[rows[was_land], column], -5)
        flooded += int(was_land.sum())
        water[rows, column] = 255
    print(f"  Persian Gulf extended to its Early Dynastic shoreline: {flooded} land pixels became sea")

    # The rivers of the Epic: marked as water in the mask, so the world strip keeps
    # them below sea level and the world's map shows both rivers running into the Gulf.
    rivers = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(rivers)
    draw_polyline(draw, EUPHRATES, (width, height))
    draw_polyline(draw, ERIDU_BRANCH, (width, height))
    draw_polyline(draw, TIGRIS, (width, height))
    draw_polyline(draw, JOINT_CHANNEL, (width, height))
    print(f"  Euphrates, its Eridu branch, Tigris and the joint channel drawn: "
          f"{int((np.asarray(rivers) == 255).sum())} water pixels")

    # The permanent marshes of the delta: water in the mask, the surface just
    # below the plain (Forti et al. 2022: freshwater to brackish marsh around
    # Abu Tbeirah; Hritz 2021: marsh and deltaic environment east of the Tigris).
    for name, outline in MARSHES:
        marsh = Image.new("L", (width, height), 0)
        marsh_draw = ImageDraw.Draw(marsh)
        scaled = [((lon + 180.0) / 360.0 * width, (90.0 - lat) / 180.0 * height) for lon, lat in outline]
        marsh_draw.polygon(scaled, fill=255)
        inside = np.asarray(marsh) == 255
        metres[inside] = np.minimum(metres[inside], -2)
        water[inside] = 255
        print(f"  {name}: {int(inside.sum())} water pixels")
    water[np.asarray(rivers) == 255] = 255

    # The tells of the lagoon: dry land carved back out of the marshes.
    for name, lat, lon in SHORE_SITES:
        row = min(int((90.0 - lat) / 180.0 * height), height - 1)
        column = int((lon + 180.0) / 360.0 * width) % width
        metres[row, column] = plain[row, column]
        water[row, column] = 0
        print(f"  {name}: carved back into land ({plain[row, column]:+d} m)")

    return width, height, metres, water


def write_pgm(path, raster, maximum):
    if raster.dtype == np.int16:
        raster = raster.astype(">u2")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as out:
        out.write(f"P5\n{raster.shape[1]} {raster.shape[0]}\n{maximum}\n".encode("ascii"))
        raster.tofile(out)
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")


def sample(lat, lon, height, width, metres, water):
    row = min(int((90.0 - lat) / 180.0 * height), height - 1)
    column = int((lon + 180.0) / 360.0 * width) % width
    return metres[row, column], water[row, column]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--degrees", type=float, default=0.05, help="raster resolution (default 0.05)")
    args = parser.parse_args()
    width, height, metres, water = build(args.degrees)
    write_pgm(WORLD / "height.pgm", metres, 65535)
    write_pgm(WORLD / "water.pgm", water, 255)

    # Checks: the world the Epic plays in must match its geography.
    print()
    for name, lat, lon, expect in [
        ("Uruk (Warka)", 31.3228, 45.6389, "land"),
        ("Eridu", 30.82, 45.61, "land"),
        ("Ur", 30.96, 46.10, "land"),
        ("Larsa", 31.05, 45.85, "land"),
        ("Lagash (Tell al-Hiba)", 31.00, 46.40, "land"),
        ("Girsu (Tello)", 31.55, 46.48, "land"),
        ("Nigin (Tell Zurghul)", 30.95, 46.53, "land"),
        ("Umma (Tell Jokha)", 31.66, 45.87, "land"),
        ("Abu Tbeirah", 31.22, 46.29, "land"),
        ("Kissik (Tell al-Lahm)", 30.61, 46.36, "land"),
        ("Nippur", 32.03, 45.13, "land"),
        # The archaeologically attested cities of the Epic's time, worldwide (c. 2700 BCE):
        # places/ancient_cities.yaml, research/ANCIENT_CITIES.md.
        ("Eridu (Tell Abu Shahrain)", 30.8261, 45.9947, "land"),
        ("Ur (Tell el-Muqayyar)", 30.9626, 46.1030, "land"),
        ("Kish (Tell al-Uhaymir)", 32.5403, 44.6047, "land"),
        ("Nippur (Tell Nuffar)", 32.1261, 45.2308, "land"),
        ("Shuruppak (Tell Fara)", 31.7775, 45.5097, "land"),
        ("Larsa (Tell Senkereh)", 31.2858, 45.8536, "land"),
        ("Umma (Tell Jokha)", 31.6672, 45.8875, "land"),
        ("Lagash (Tell al-Hiba)", 31.4111, 46.4111, "land"),
        ("Girsu (Tello)", 31.5653, 46.1896, "land"),
        ("Nigin (Tell Zurghul)", 31.3768, 46.4957, "land"),
        ("Abu Tbeirah", 30.9700, 46.2680, "land"),
        ("Adab (Tell Bismaya)", 31.9473, 45.6263, "land"),
        ("Eshnunna (Tell Asmar)", 33.8106, 44.7667, "land"),
        ("Nineveh (Kuyunjik)", 36.3586, 43.1539, "land"),
        ("Tell Brak (Nagar)", 36.6700, 41.0600, "land"),
        ("Mari (Tell Hariri)", 34.5494, 40.8900, "land"),
        ("Susa (Shush)", 32.1894, 48.2561, "land"),
        ("Shahr-e Sukhteh", 30.6500, 61.4000, "land"),
        ("Ebla (Tell Mardikh)", 35.7981, 36.7986, "land"),
        ("Byblos", 34.1167, 35.6500, "land"),
        ("Ugarit (Ras Shamra)", 35.6019, 35.7856, "land"),
        ("Sidon", 33.5607, 35.3683, "land"),
        ("Megiddo (Tell el-Mutesellim)", 32.5833, 35.1833, "land"),
        ("Jericho (Tell es-Sultan)", 31.8717, 35.4446, "land"),
        ("Arad (Tel Arad)", 31.2808, 35.1250, "land"),
        ("Hazor (Tell el-Qedah)", 33.0182, 35.5691, "land"),
        ("Memphis (Mit Rahina)", 29.8447, 31.2509, "land"),
        ("Heliopolis", 30.1294, 31.2889, "land"),
        ("Abydos", 26.1852, 31.9189, "land"),
        ("Hierakonpolis (Nekhen)", 25.0972, 32.7794, "land"),
        ("Naqada", 25.9017, 32.7242, "land"),
        ("Koptos (Qift)", 25.9951, 32.8197, "land"),
        ("Elephantine", 24.0867, 32.8792, "land"),
        ("Buto (Tell el-Fara'in)", 31.1912, 30.7402, "land"),
        ("Kerma", 19.6008, 30.4097, "land"),
        ("Altyn-Depe", 36.8547, 60.4261, "land"),
        ("Namazga-Depe", 37.3703, 59.5542, "land"),
        ("Sarazm", 39.5167, 67.5667, "land"),
        ("Harappa", 30.6333, 72.8667, "land"),
        ("Kot Diji", 27.3416, 68.7000, "land"),
        ("Kalibangan", 29.4700, 74.1300, "land"),
        ("Rehman Dheri", 31.9678, 70.7969, "land"),
        ("Dholavira", 23.8861, 70.2167, "land"),
        ("Liangzhu", 30.3967, 119.9853, "land"),
        ("Troy (Hisarlik)", 39.9575, 26.2389, "land"),
        ("Poliochni", 39.8537, 25.3430, "land"),
        ("Kultepe (Kanesh)", 38.8500, 35.6333, "land"),
        ("Liman Tepe", 38.3633, 26.7758, "land"),
        ("Alaca Hoyuk", 40.2340, 34.6907, "land"),
        ("Arslantepe", 38.3819, 38.3611, "land"),
        ("Knossos", 35.2981, 25.1631, "land"),
        ("Lerna", 37.5512, 22.7182, "land"),
        ("Los Millares", 36.9644, -2.4597, "land"),
        ("Zambujal", 39.0744, -9.2858, "land"),
        ("Caral", -10.8895, -77.5188, "land"),
        ("Aspero", -10.8156, -77.7410, "land"),
        ("the Euphrates east of Uruk", 31.33, 45.68, "water"),
        ("the Euphrates east of Larsa", 31.05, 45.95, "water"),
        ("the Euphrates east of Ur", 30.87, 46.18, "water"),
        ("the Eridu branch west of Eridu", 30.82, 45.50, "water"),
        ("the Euphrates mouth into the lagoon", 30.50, 46.15, "water"),
        ("the Tigris east of Girsu", 31.55, 46.58, "water"),
        ("the Tigris east of Nigin", 31.00, 46.70, "water"),
        ("the Tigris mouth into the marshes", 30.35, 47.05, "water"),
        ("the joint channel east of Umma", 31.68, 45.95, "water"),
        ("the lagoon south of Eridu (ED shoreline)", 30.40, 45.65, "water"),
        ("the lagoon off Abu Tbeirah", 30.60, 46.30, "water"),
        ("the marshes east of the Tigris", 30.90, 47.30, "water"),
        ("the Gulf between Kuwait and Iran", 28.5, 48.6, "water"),
        ("the Cedar Forest (Lebanon)", 34.4, 36.1, "land"),
        ("Dilmun (Bahrain)", 26.07, 50.55, "land"),
        ("Mashu (Zagros pass)", 36.4, 45.0, "land"),
        ("the Caspian", 41.5, 50.5, "water"),
        ("the Qattara depression", 29.7, 27.2, "land"),
        ("the Nile delta", 31.0, 31.2, "land"),
        ("the Mediterranean off Ugarit", 35.5, 35.8, "water"),
        ("the Persian Gulf today's head (Basra)", 29.95, 48.6, "water"),
        ("Everest", 27.99, 86.92, "land"),
        ("the Atlantic mid-ocean", 0.0, -140.0, "water"),
    ]:
        metres_at, water_at = sample(lat, lon, height, width, metres, water)
        is_water = water_at == 255
        ok = is_water if expect == "water" else not is_water
        print(f"  {'ok ' if ok else 'BAD'} {name}: {'water' if is_water else 'land'} "
              f"{metres_at:+d} m at ({lat}, {lon})")
        if not ok:
            raise SystemExit(f"{name} is not {expect}")


if __name__ == "__main__":
    main()
