# The streets and buildings of Uruk (research notes)

Plan: `tools/build_city.py` (writes `tools/data/uruk_city.json`, `places/uruk_city.yaml` and the names in `i18n/*.yaml`).
Models: `models-src/architecture/uruk_city.py` (quarters), `uruk_sites.py` (sites), `uruk_walls.py` (wall and gates).
Rebuild everything with `make city` (needs Blender 4.3, Pillow, numpy, matplotlib). Previews: `tools/build_city.py --preview x.png`
(map of the plan) and `tools/blender/render_city.py` (renders of the models on the real terrain, `TERRAIN=ox,oz,half`).

## What the plan follows

Sources: the story map *Uruk, the "first" city* (F. Moerwijk, 2021, after *Uruk: First City of the Ancient World*, 2019), saved with
its figures in `research/Uruk.html` and `research/Uruk_files/` (reference only: **do not ship or commit these pictures**, they are
not ours), and the owner's reference illustration of Babylon. Nothing was copied from them; layouts and pattern families were read.

- **The wall**: the OSM outline (8.6 km) is the one marked on the story map's satellite picture (overlay checked 2026-10-13: same
  shape and proportions). The story map gives 9 km and 5-9 m thickness with bastions; ours is 7 m with towers.
- **The centre**: the Eanna precinct and the Anu district form the religious and administrative heart, in the topographical middle
  of the city. All avenues run from the gates to the sacred ring road round the precinct and on into the court to the feet of
  the ziggurats (Anu, exact in the wall model; the stepped tower of Ishtar is an addition for the place `ishtar_temple`).
- **Eanna**: a walled square orchard (the Great Court) with rows of trees, channels and a pool; the pillar hall with close
  pilasters, tall doorways under triangular niches and a band of clay-cone mosaic (black, white and red cones, 8-10 cm long);
  the stone-cone building on a terrace with a basin and reed standards (flagpoles); the temple of Eanna of the Late Uruk period
  (`limestone_hall` in the plan, 42 x 27 m) built from its excavation plan: a thick band of niches and rooms along each long
  side with three entrance passages, a cross hall at the west end and a long middle hall open to the sky with chambers on both
  sides (`TEMPLE_NORTH` in uruk_sites.py, read by hand from the plan, southern half mirrored). Places and sizes in the court are
  chosen by the planner, only the kinds of building are from the excavation. Reference reconstructions of the central area (DAI,
  artefacts-berlin, copyrighted) were looked at for layout only: nothing is copied from them.
- **The palace of Sin-kashid** (Old Babylonian, 1865-1833 BC) lay west of Eanna and Anu: 142 m by 109 m (102-116 m short sides),
  about 15,500 m2, mud brick on a base of baked brick, a large courtyard in the east, a hall with six columns, narrow corridors,
  a scribal school in the north; the reconstruction shows a low building with a niched outer wall and a gate between small
  towers. We place it west of the precinct with this plan simplified. It is an anachronism for Gilgamesh (c. 2700 BC), like the
  Ishtar Gate: fantasy by the owner's decision.
- **The palace of Gilgamesh** (`uruk_palace`) is invented in form: four wings round a courtyard, a throne hall with a
  portico of six columns, towers, and a frieze of clay cones. Farm buildings round both palaces (granaries, storehouses,
  stables, kitchens, bakeries, breweries, a smithy, pens, a threshing floor, haystacks, palms; the hanging garden) are
  the owner's request; their kinds are plausible, their placing is ours.
- **Canals and fields**: the magnetogram shows field furrows and canals inside the wall in a rectilinear net; the story map
  says the irrigated farming lay to the south-west and the north-east was dry, and the Middle Babylonian watercourses (Adams)
  run from the north-west to the south-east past Uruk. So the net is turned (-20 degrees) to run NNW-SSE, the main canal enters
  the wall in the north-west through a water gate, fields are thinner and fallow in the north-east and richer in the south-west.
  The brook/river itself of the patch lies east of the wall (ADR 0013), so the supply from the north-west is not yet joined to it.
- **Houses**: three sizes (poor 5-7 x 6-8 m, middling 8-11 x 9-12 m, rich 12-17 x 13-18 m), flat roofs with parapets, some with
  pointed teeth (as in the reference illustration), light wells, upper floors set back from the front, door and window slits;
  the wall colour varies (mud brick, plaster with ochre, pink, cream, red baked brick on the rich ones). They are laid along the
  streets with random size, turn (+-2.5 deg), height, setback and colour. Size follows the wealth, which falls with the distance
  from the centre and is lower in lanes.
- **Markets**: a great market (92 x 62 m, 100+ stalls with coloured awnings, a well) beside the avenue from the Ishtar Gate, and
  smaller markets inside three gates. **Smithies**: a street of workshops in the south-west and a few single ones (open front,
  a furnace for smelting copper, tall chimney, anvil, sword moulds, a charcoal heap, a turf charcoal kiln and a pile of
  wood). **Potters' yards** stand beside that street (`places/workshops.yaml`, `uruk_pottery.glb`): a kiln, jars, stacks of
  clay tablets and baskets. Servants patrol from the yards to Eanna and to the great market; scribes, a merchant and a priest
  write on the tablets.
- **Density**: the built city covers the middle (up to about 0.4 of the way to the wall) and thins out; the outskirts are fields
  and orchards, as the epic says (a third city, a third orchards, a third clay pits; the clay pits are not made).

## Not verified / simplified

- The number of houses (about 4,500) and their sizes are choices, not data; the houses of Early Dynastic Uruk are not known in this detail.
- The positions of the markets, palaces, smithies, gates (except the Ishtar Gate) and the street net are ours; the net is not an
  excavated plan. The Anu ziggurat stands, by the OSM outline, within about 30 m of the Eanna precinct, while the story map's
  marker lies roughly 400 m west of Eanna: not decided, see the report.
- Canals are only drawn: no water in the game (the server's terrain has no water there) and a player walks through them.
- Houses have no doors that open and no interiors; stalls have a table collider only.
- **Natural scenery** (trees, rocks, flowers of the world's own object grid) is not cleared inside the city: it stands in lanes and
  between houses and blocks walking like anywhere else. Clearing it needs a server and protocol change (a structure option that
  suppresses natural objects within its footprint): proposed, not done.
- **Placement**: every quarter and site is a located place with a tolerance of 1-2 m (the model is built around its anchor in the
  frame of the plan). A world whose coast, or whose base terrain, makes the exact point unusable would widen the search and
  misalign the model; a failing point aborts the placing of the whole disk. Seeds 42 and 1234 already failed for other places; seed 7 works.

## Checked

- Datadisk validator passes (40 places). Server (seed 7 demo world): all 28 city places stand within 0.1 m of their planned
  distance from Uruk; the server announces the models (`disk:` props) and walks the characters by their collision meshes.
- Walking bot (real HTTP, `POST /players/me/move`): from the spawn inside the Ishtar Gate along the avenue to the foot of the Anu
  stairs (2,300 steps), through the gate of the palace of Gilgamesh into its courtyard, through the gate of the palace of Sin-kashid
  into its courtyard, and into the middle of the great market: all arrived, none stuck.
- Real client (Godot 4.5, `tests/world_view.gd`-style screenshots after standing the player at viewpoints): the city, markets, palace,
  precinct with both ziggurats and the Great Court, smithies and canals render. The look in the client is darker on the shaded
  sides than in Blender (the client's ambient light), so the city textures carry a gain (`GAIN` in uruk_city.py).
- Not checked: other seeds, performance on weak GPUs (about 16 MB of quarter models and 4 MB of walls are fetched as the player
  walks), the Czech names in the game, interior of the Great Court trees up close.

## Notes from the bachelor thesis Sebek_BP.pdf (Petr Sebek, Uruk and its hinterland, Plzen 2021)

Secondary source (cites Charvat, Crusemann, Leick, Crawford); figures to check against the models:

- **Anu**: the ziggurat is 12 m high (mud brick with a bitumen-like binding), the court on top about 50 x 45 m. The White Temple on
  top is 22 x 17 m, built 3517-3358 BCE, whitewashed, tripartite, three entrances and none faces the access ramp (a visitor has to walk
  round it), pits for sacrifices in the big middle room, two small rooms with a stair; a small terrace north of the temple with a
  3 x 2 m fire pit. A lower stone temple (layer VI) lay under the north-west part of the ziggurat. The current model follows
  this: a single terrace of 57 x 52 m at the base, 12 m high with a 3.5 m batter, the court 50 x 45 m on top, the White
  Temple 22.3 x 17.5 m with its roof about 21 m above the plain, and the fire-pit terrace north of it
  (`ziggurat_anu.glb`, dimensions and sources in `ZIGGURATS.md`).
- **Eanna**: rebuilt several times. The first stone temple (layer VI, about 3500 BCE, south-west part) had a T-shaped plan, a limestone
  plinth with buttresses and clay-cone mosaic (the plan used for `limestone_hall`). In layer V a limestone temple of 62 x 11 m stood in
  the north-east part about 100 m from it, same plan, with a ramp at the back to the roof, on the site of the old Ubaid temple. In layer
  IV the "Riemchen" building (bricks of 16 x 16 cm) stood on the site of the stone temple. Almost 20 temples in layer IV. Temple E is a
  palace-like square building (orange plaster stairs to the central court); temple D has rooms plastered with asphalt (cisterns or
  baths); the Great Court is a wide yard with rain-water channels, perhaps a shaded oasis with trees.
- **Clay cones**: 8-10 cm long, heads 1.2-1.8 cm wide, white (fired hot) and red (fired low) and dark; set into wet plaster; found on 12
  round columns of the south-east temple of Inanna, more than 70 patterns (stripes, diamonds, lattices, like reed matting).
  `make_cone_mosaic.py` draws 1.6 cm heads (150 across a 2.4 m tile), patterns enlarged 2.5 times to be readable.
