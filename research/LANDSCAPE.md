# Landscape of Uruk: real relief, real wall, ancient river

The datadisk anchors a **terrain patch** (ADR 0013) at the `uruk` place: six kilometres of the
real Mesopotamian floodplain around the tell of Warka, the city wall on its surveyed outline and the
Euphrates returned to its Early Dynastic course (c. 2700 BCE, the time of Gilgamesh). Everything is built
by `tools/build_landscape.py` (terrain, river, outlines) and `models-src/architecture/uruk_walls.py`
(wall, gate, Anu ziggurat) from open data; this note records what comes from where, what is a documented
reconstruction, and what is still knowingly simplified.

## Sources

| What | Source | Notes |
| --- | --- | --- |
| Relief (heights) | Copernicus DEM, GLO-30 (30 m), public AWS bucket | The alluvial plain around Warka spans roughly 3–25 m above sea level; the tell rises about 15 m above it. The patch stores heights **relative to the anchor** so it can land on any generated world. |
| Wall of the city | OSM way 1046022672 (`historic=citywalls`) | 63 nodes, 8.6 km, 520 ha: the surveyed circuit of the Early Dynastic wall (the literature gives about 9.5 km and 600 ha). |
| Eanna precinct, Anu ziggurat | OSM ways 1311535414, 1311535415 | The ziggurat footprint is 49 × 63 m, its centre 137 m east and 201 m north of the anchor. |
| Anchor | Centre of the OSM site polygon (wikidata Q168518), 31.3228 N, 45.6389 E | |
| Modern hydrography | OSM (Overpass `api/map`) | Documentation only: today **no mapped water exists within about 4 km** of the tell. |

Attribution for both is in `datadisk.yaml`: Copernicus data under the ESA terms, OSM under ODbL.

## Frame and orientation

The patch lives in the client's local frame: **+x east, +z south** (Godot is right-handed with +y up, so a
map with +x east has −z north). Row 0 of the PNGs is therefore the most northern row. An earlier build
wrote the rows the other way round, which mirrored the whole landscape; the check that settled it: with
the right frame the raised mound of the DEM (the tell and the city) exactly fills the OSM wall outline.
`tools/build_landscape.py` writes the outlines in this frame to `tools/data/uruk_outlines.json`
(wall densified to 30 m, with the terrain height at every point), the single source for the wall model.
The orientation of the planet itself is arbitrary (a generated world), so only the handedness is real,
not the compass.

## The river has moved; the relief stayed

Five thousand years changed the hydrography but barely touched the relief:

- **Early Dynastic (c. 2700 BCE):** Uruk stood on a branch of the Euphrates that watered its fields and
  carried its trade (Adams, *Heartland of Cities*, 1981: the settlement pattern of the Uruk and Jemdet Nasr
  periods hugs a channel; levee and canal traces east of Warka are legible in imagery).
- **Today:** the tell lies in the desert, the nearest permanent water tens of kilometres away; the OSM
  extract contains **no waterway at all** — the tool prints this as a check.

The patch keeps the Copernicus relief and **carves the channel along the outside of the east wall**:
the course is the east edge of the wall outline plus 140 m (a 160 m wide channel, so the near bank lies
60 m from the wall), smoothed, running straight on beyond the wall to the north and south edges of the
patch. The bed lies 3.8 m below the local plain, the water 0.6 m below it: up to 3.2 m deep in the middle,
shallow towards the banks (fish need at least 3 m). That the branch lay east of the city is common ground in
palaeochannel studies (Jotheri, Altaweel et al. on the Holocene avulsions of the Euphrates near Uruk); its
exact position within a few hundred metres is beyond what public data can prove, so this is a
reconstruction. The offset is `river_offset_m` at the top of the script.

Modern **canals, drains and road cuts** of the DEM (a four-metre trench crosses the south-west corner
of the patch) did not exist then; the script fills trenches narrower than 120 m with a grey closing
before the river is carved, the broad relief and the tell are untouched.

## The wall and the gate

`uruk_walls.glb` follows the OSM outline: 18 m high, 7 m thick, glazed blue brick (the owner's decision:
walls that match the Ishtar Gate, a deliberate fantasy — the real Early Dynastic wall was plano-convex
mud brick with semicircular towers), a tower every ~75 m and stepped battlements. The wall follows the
relief (the base lies 6 m below the terrain height at every point, the top 18 m above it) and 316 pieces and
103 towers make up its 8.5 km. The Ishtar Gate with its Processional Way stands in the south wall where
the wall is straightest and the terrain flattest (about 41 m east and 1263 m south of the anchor, facing
south-south-west). Animal rows decorate the wall within 300 m of the gate only; four flights of stairs
climb to the wall walk. `uruk_walls_collision.glb` is the lean twin the server walks on.

The **Anu ziggurat** is part of the same glb: a place can show one building, and a child place cannot be put
at a bearing from its parent (see below), so the building stands in the wall model exactly on its
excavated terrace (OSM footprint centre, turned 41° like the survey, stairs towards the Eanna precinct, on
the lowest ground under the footprint).

## Climate: not done

Mesopotamia of the fourth and third millennia BCE was greener than today (wetter climate, marshes and
date palms along the channels, fields and orchards watered by canals). The disk can only demand
`biome: [grassland]` for the anchor; trees, grass, flowers and animals of the scene come from the world's
biome map, not from the datadisk, and the patch carries height and water only. A lusher, ancient
vegetation along the river and the canals needs a contract extension (a `terrain` option for vegetation
and reed/palm banks); it is proposed, not built.

## Known simplifications (alpha)

- **Places lie where the excavations and the geography put them** (`locate`, ADR 0016): the Eanna precinct and the
  Anu ziggurat from the OSM outlines, the White Temple on the ziggurat, the Ishtar temple in Eanna, and far away the
  Cedar Forest (Lebanon, 953 km WNW), Mashu, Babylon, the Gulf and Dilmun. The market, the palace, the tombs and the
  other places of the city are still placed at random within the walls: no excavation plan is used for them.
- **New players appear just inside the Ishtar Gate** (`city_gate` is located at the gate).
- **The channel is one line, not a braided system.** The ED floodplain had side branches, canals, levees and
  marshes; no field systems are raised or lowered around the channel.
- The DEM is 30 m data upsampled to a 10 m grid; the tell's outline is smoothed by that.
- Wall tops follow the terrain in 30 m steps; the gate complex itself is flat.
- Not yet looked at in the client: the geometry and the server behaviour were checked (see below), the look of
  the scene was not.

## Checked on the server

With a local demo world (seed 7): the server announces the patch and the wall (model height at the gate
equals the patched terrain, 9.7 m below the base height of the anchor — before the server loaded patches
ahead of building structures the walls floated 11 m up), scenery and animals no longer stand in the river
(0 of about 1200 objects around the channel), and fish swim in the deepest part. Server changes for this are in the
working tree of `ishtaria-server` (`src/story/world.rs`, `src/movement.rs`).

## Building

```sh
tools/build_landscape.py            # downloads Copernicus tiles + OSM into tools/cache/
                                    # (git-ignored, never shipped), writes media/terrain/ and tools/data/
blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls media/models/architecture/uruk_walls.glb
blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls_collision media/models/architecture/uruk_walls_collision.glb
```

The builder prints `offset_m` (the gate from the anchor), which belongs into `places/uruk.yaml`. Blender's
glTF exporter prints "Draco mesh compression is not available": harmless, no Draco is used.

Values: 16-bit greyscale PNG, `0x8000` = the anchor's height, one step = a decimetre; the water
mask is 0 for dry land, otherwise the surface in decimetres above the anchor
(`media/terrain/uruk_height.png`, `media/terrain/uruk_water.png`).
