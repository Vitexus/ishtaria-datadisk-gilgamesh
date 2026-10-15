# The real planet: continents, heights and the Gulf of the Epic

A world generated with this disk is not a procedural planet: it is the Earth of the Early
Dynastic period (c. 2700 BCE, the time of the Epic of Gilgamesh). The datadisk names the
equirectangular rasters in `world.terrain` (datadisk.yaml) and `ishtaria-worldgen --earth`
projects them onto the cube-sphere, so the world's map has the real outline of every
continent, the real ocean floors and both rivers running into the Persian Gulf. This note
records what comes from where, what is a documented reconstruction and what is knowingly
simplified; `tools/build_world_map.py` builds the rasters and checks the geography.

## Sources

| What | Source | Notes |
| --- | --- | --- |
| Relief and bathymetry | ETOPO 2022, 60 arc-second **bed** grid (NOAA NCEI, public domain) | Downloaded once into `tools/cache/` (never shipped whole). The shipped rasters resample it to 0.05 degrees (7200 x 3600) by block means. The bed grid carries land heights and ocean depths in one signed field, which is exactly the `media/world/height.pgm` encoding (16-bit signed metres, 0 is sea level). |
| Coastline | The ETOPO data itself (elevation <= 0 is water) | Shallow seas and dry depressions are decided by the mask, not the quantised heights. |
| Persian Gulf shoreline, the marshes, the rivers | The reconstructions below | The palaeogeography of southern Iraq since Gilgamesh, from the published literature. |
| Dry depressions | Fixed list in the tool (Qattara, Death Valley, Turfan, Danakil, Salton Sink, Laguna del Carbon) | Land below sea level must stay land; only real water bodies may be water. |

Attribution for ETOPO is in `datadisk.yaml`. The tool prints a check for each city of the
Epic (Uruk, Eridu, Ur, Larsa, Girsu, Lagash, Nigin, Umma, Abu Tbeirah, Kissik, Nippur,
Dilmun, the Cedar Forest, Mashu) and fails when one of them lands in the sea.

## How Iraq changed since Gilgamesh

Iraq's bedrock relief barely moved in five thousand years; what changed is the water:
the shoreline of the Gulf, the courses of both great rivers, and the extent of the
marshes. The reconstruction follows the literature (each with its own simplifications):

- **The Gulf head prograded ~150-250 km.** During the mid-Holocene transgression the sea
  reached about the Nasiriyah line around 4000 BCE (Aqrawi et al. 2001; the "Ur Schatt"
  introgression); by the Early Dynastic period the delta had built out to the Eridu-Ur
  line. How quickly is debated - the authors "differ strongly" (Jotheri et al.; Hritz
  marks the ED shoreline as "unclear") - but the brackish marshes around Abu Tbeirah
  (2900-2000 BCE, 7 km south of Nasiriyah) place the water's edge at the latitude of
  Eridu and Ur, as a lagoon rather than open sea (Forti et al. 2022: a sinuous channel
  in a floodplain and marsh environment, freshwater to brackish). Geyer and Sauvage
  (2020) draw the successive coastlines of the delta for 4000, 2000-1800, 1500-800 and
  700-300 BCE; the reconstruction follows their picture: at the Epic's time both rivers
  still had **separate outlets** into the Gulf.
- **The Tigris moved east, twice.** Before ~4000 BCE it joined the Euphrates near
  Sippar; it then avulsed and ran past Adab and Larsa (Engel and Brueckner 2018), and in
  the Early Dynastic period it flowed past **Girsu, Lagash and Nigin** into the marshes
  and the Gulf - the joint channel with the Euphrates, whose levee the modern Shatt
  al-Gharraf reuses (Steinkeller 2001; Aqrawi 2001; Hritz 2021; Hammer, Stone and
  McMahon 2022 map the river past the three cities from HEXAGON imagery). Only between
  2500 and 2000 BCE did it move to its present course further east.
- **The marshes were far larger.** The delta of the Epic was a mosaic of channels,
  levees, lagoons and permanent marsh (Pournelle 2003; "much of the archaic alluvial
  landscape consisted in large part of wetlands"): the brackish lagoon in front of the
  Eridu-Ur shoreline (the environment of Abu Tbeirah and Kissik, and the ancestor of the
  later Sealand and of lake Hammar) and the marshes east of the Tigris - the remnant of
  the bay near al-Amara that the Tigris was filling (Aqrawi 2001; Hritz 2021: a "marsh
  and deltaic environment" east of the Shatt al-Gharraf). The later Chaldaicus Lacus of
  the classical authors grew from the same setting.

## What the map draws

`GULF_SHORELINE` (one latitude per longitude of the basin head) is the ED water's edge:
the sea reaches the Eridu-Ur line, today's delta on the east, today's coast everywhere
else. Everything between today's shoreline and that curve becomes shallow sea (-5 m).
`MARSHES` are the two permanent wetlands above, water in the mask at -2 m.
`SHORE_SITES` carves the tells that stood in the water back to dry land (Kissik).

- **Euphrates** (`EUPHRATES`): from Hit past Kish, Nippur and Shuruppak, east of Uruk
  (where the city's landscape patch, research/LANDSCAPE.md, has its Early Dynastic
  branch), past Larsa and Ur into the lagoon (Adams 1981, simplified). `ERIDU_BRANCH`
  is the western branch past Larsa's and Eridu's west sides: the oldest city stood on
  the shore, not in the channel.
- **Tigris** (`TIGRIS`): today's course from Nineveh through Assur and Samarra to Kut
  (ancient enough there), then past the west bank of Girsu, Lagash and Nigin into the
  marshes and the Gulf - the course it kept until ~2500-2000 BCE.
- **Joint channel** (`JOINT_CHANNEL`): the large leveed branch of both rivers past
  Umma to Girsu (Adams 1981; Pournelle 2003; Hritz 2021), the ancestor of the Shatt
  al-Gharraf.

The rivers and marshes are the base map at ~5.5 km a pixel: one line per river, two
polygons for the marshes, no canals, no side branches, no levee relief. The playable
river is the patch around Uruk. The Iranian rivers (Karun, Karkheh) that also shaped
the Gulf head are not drawn; their Early Dynastic courses are even less agreed on
(Cole and Gasche 2007; Heyvaert 2007 trace the "K1" only for later periods).

## What the base map can and cannot hold

- The strip is 8-bit: one step is 62.7 m, the range is -8000..+7998 m, so Everest rounds
  to 7998 and shallow depths to -31 m. The client's local relief, the landscape patches
  and the placement of places carry the real detail.
- Face sizes larger than 256 pay off: the rasters support up to the server's 1024 face
  size (about 10 km a pixel at the face centre). A single 5.5 km tell (Kissik) may fall
  between the coarser strip samples - the source rasters keep it land.
- Climate and vegetation are **not** from 2700 BCE: the world's biomes still come from
  latitude, elevation and the seeded moisture of the server's environment map. A wetter
  Mesopotamia with reed banks and date palms along the rivers needs a further contract
  extension (proposed, not built - see research/LANDSCAPE.md, "Climate: not done").
- Sea level: the mid-Holocene highstand was at most ~0.3 m above today's (some authors
  put the stabilization 3-4 m below present); far below the strip's resolution, ignored.

## Rebuilding

```sh
python3 tools/build_world_map.py          # rebuilds media/world/*.pgm (needs numpy, Pillow,
                                          # tifffile, imagecodecs; caches the ETOPO download)
python3 ../ishtaria-protocol/tests/validate_datadisk.py .   # validates shape, maxval, sizes
```

The rasters are committed (about 78 MB raw; the .deb compresses them). Changing
`GULF_SHORELINE`, the rivers or the marshes changes the disk's content hash and therefore
the identity of worlds generated with it - that is intended: it is a persisted contract,
like every other manifest change.
