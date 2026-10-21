# Ziggurats of the datadisk (research notes)

Policy (owner, 2026-10): every **city on the disk** that has a ziggurat attested in texts or excavation
gets one in the world. Where plans or reconstructions give usable dimensions, the model is **distinct**.
Where only the existence of a tower is known, the place **reuses** an existing glb (a clone). Later
towers on Early Dynastic pins are the same class of deliberate anachronism as the Ishtar Gate and
Etemenanki (see `GAREUS_TEMPLE.md`).

Models are built by `models-src/architecture/ziggurat.py` (and Ishtar's stepped tower by
`uruk_sites.py`). Places: `places/ziggurats.yaml` (Uruk precinct), `places/babylon.yaml` (Etemenanki),
`places/city_ziggurats.yaml` (other cities). The Anu terrace is also baked into `uruk_walls.glb`.

Uruk's Anu ziggurat is **not** the Great Ziggurat of Ur (Nanna / Etemenniguru, Ur-Nammu, ~2100 BCE).
Early tools (`tools/blender/ziggurat_uruk.py`) mixed those names; Anu is a single terrace, Ur is three
rectangular stages. See the catalog below.

## Catalog: disk cities and attestation

Only Mesopotamian / Elamite cities on the disk are candidates. Levantine, Egyptian and other pins do
not get Mesopotamian ziggurats.

| City (place id) | Ziggurat / temple tower | Attestation | Appearance | Disk model |
| --- | --- | --- | --- | --- |
| `uruk` | Anu + White Temple | Excavated (Warka) | Known (single terrace ~12 m) | `ziggurat_anu.glb` (in walls) |
| `uruk` | Eanna / Inanna (game: Ishtar tower) | Precinct excavated; stepped form is a story addition | Partial | `uruk_ishtar_ziggurat.glb` (**distinct** stepped, not a copy of Ur) |
| `ur` | Etemenniguru (Nanna/Sîn) | Excavated (Woolley); best-preserved Neo-Sumerian | Known: 64 × 45 m, 3 stages, ~30 m original | `ziggurat_ur.glb` (**distinct**) |
| Babylon (`etemenanki`) | Etemenanki (Marduk) | Koldewey + Esagila tablet | Known (usual reconstr. ~91 m / 7 stages) | `ziggurat_etemenanki.glb` (**distinct**) |
| `eridu` | Enki / Ea temple mound → later ziggurat | Long temple sequence on a raised platform; later ziggurat mound | Partial (early platform better known than upper stages) | `ziggurat_eridu.glb` (**distinct**, low Anu-like terrace) |
| `nippur` | Ekur (Enlil) | Excavated; UNESCO notes ~25 m high ziggurat | Partial (height known; stage plan approximate) | `ziggurat_nippur.glb` (**distinct**, ~25 m stepped) |
| `kish` | Ziggurat at Tell Ingharra | Excavated remains | Poor | clone of `ziggurat_ur.glb` |
| `larsa` | Ebabbar (Šamaš) ziggurat | Excavated with temple | Poor | clone of `ziggurat_ur.glb` |
| `girsu` | Ningirsu temple tower / Eninnu platform | Texts (Gudea) + excavated temple mound | Poor | clone of `ziggurat_ur.glb` |
| `adab` | Ninmah / Ninhursag temple on a platform | Texts + ED temple | Poor | clone of `ziggurat_anu.glb` |
| `susa` | Inšušinak ziggurat | Texts + scant remains (Iran Safar: gone) | Poor | clone of `ziggurat_ur.glb` |
| `nineveh` | Ištar / Nabû temple towers (later Assyrian) | Excavation / texts | Poor | clone of `ziggurat_ur.glb` |

**Not placed (on disk but no secure ziggurat):** Shuruppak, Umma, Lagash (main tower at Girsu), Nigin,
Abu Tbeirah, Kissik, Eshnunna (Square Temple is not a ziggurat), Mari, Tell Brak, and all non-Mesopotamian
cities.

**Off disk (attested elsewhere, not pinned):** Borsippa (Eurmeiminanki), Dur-Kurigalzu / Aqar Quf,
Assur, Sippar, Chogha Zanbil, Sialk, Konar Sandal. Documented under Sources if a later pin is added.

Clone policy: one glb path, several places; `structure.yaw_deg` differs so copies do not share one
compass heading. Platform-style unknowns (Adab) clone Anu; stepped Neo-Sumerian / later unknowns clone Ur.

## Etemenanki, the tower of Babylon

What the sources agree on (searched 2026-10, see the links below):

- A square base of about 91 m a side, found in the excavations of Koldewey; the Esagila tablet (a Seleucid copy, 229 BC of
  older texts) gives base measurements that match it.
- Seven stages with the temple of Marduk (Ekarzagina) on the seventh; about 90 m in all in the usual reconstruction
  (a dissenting proposal by Montero Fenollós and colleagues reaches only 66 m, with other accesses and another
  temple layout). Popular travel summaries sometimes quote ~54 m (177 ft); that figure is speculative and is not used
  here — the model follows Schmid/George (~90 m).
- Baked brick and bitumen outside, mud brick inside (inscriptions of Nabopolassar and Nebuchadnezzar II); the temple
  was probably clad in glazed blue brick and the upper stages are thought to have been painted.
- The stairways: three, meeting at a gate before the first stage, as at the ziggurat of Ur and as in the
  reconstruction pictures that were shown by the project owner.
- Solid mass (no interior chambers); the spaces around a ziggurat were often planted with trees.

What the model assumes and could not be confirmed here (check Schmid, *Der Tempelturm Etemenanki in Babylon*, 1995,
and George, *Babylonian Topographical Texts*, before relying on it):

- the stage heights 33, 18, 6, 6, 6, 6 and 15 m (temple) and the stage widths 91.5, 72, 58, 49, 41 and 33 m. They give
  the usual 90 m; the finials and the upper chamber of the temple add a few metres above it;
- the position of the stairs (a steep central flight on every stage, two ramps on the first), the pairs of glazed
  portals and the palms are artistic choices following the reconstruction pictures, not evidence.

## The ziggurat of Anu and the White Temple (Uruk)

Early Dynastic Uruk, the world of Gilgamesh (c. 2700 BCE): the Anu ziggurat is a high mud-brick terrace with sloping,
buttressed sides and the whitewashed White Temple on top (a tripartite plan of about 22 x 17 m with niched walls).

What the sources agree on (searched 2026-10, see the links below and the notes from the Sebek thesis in `CITY.md`):

- One massive terrace, not a tower of stages: about 12 m (40 ft) high, raised over many building phases
  (artefacts-berlin.de, the Sebek thesis, Iran Safar summary). The excavated mound body is 56 x 49 m, the surveyed
  footprint 49 x 63 m (see `LANDSCAPE.md`).
- Built of rammed earth and sun-dried mud brick; the court on top had a waterproof bitumen layer under the
  whitewashed temple (Iran Safar; bitumen waterproofing is the usual Mesopotamian treatment).
- A court of about 50 x 45 m on top, behind sloped outer walls (artefacts-berlin.de: a surface of about 45 x 50 m at a
  height of about 12 m; the Sebek thesis: 12 m high, the court on top about 50 x 45 m).
- The White Temple on the court: 22 x 17 m / about 55 x 72 ft (the model: 22.3 x 17.5 m), built 3517-3358 BCE,
  whitewashed, tripartite, plan aligned with the cardinal axes of the terrace; three entrances and none faces the
  access ramp (a visitor has to walk round it), pits for sacrifices in the big middle room; its roof about 21 m
  above the plain. A small terrace north of the temple with a 3 x 2 m fire pit.
- Staircases climb to the temple court. The terrace was a landmark of Uruk, visible beyond the city's walls.

What the model assumes (`ziggurat_anu.glb`, rebuilt 2026-10):

- The base 57 x 52 m with a 3.5 m batter on every side (the court 50 x 45 m) reconciles the surveyed footprint with the
  published court; the walls are smoothed and grooved, the weep holes decorative. The remaining proportions are
  approximate. In `uruk_walls.glb` the terrace is turned 41° like the OSM footprint (stairs toward Eanna), not to
  true north — the temple stays axis-aligned to that terrace.
- The court and landing tops are dark bitumen (waterproof layer); the White Temple itself remains whitewashed plaster.
- The access keeps the layout of the reconstruction drawing of the ziggurat of Ur shown by the owner: three flights
  meeting on a solid landing against the front of the terrace — a steep central flight at 43 degrees (0.3 m risers,
  0.316 m treads, the slope the server's walking tests climb) between parapets, and two ramps running along the front
  from the sides — with a gate house on the landing at the head of the central flight. The drawing is a reference for
  the layout only, not a source of geometry or texture.

## The Great Ziggurat of Ur (Etemenniguru)

What the sources agree on (Woolley; Wikipedia / Britannica summaries checked 2026-10):

- Rectangular base **64 × 45 m** (length × width), original height about **30 m** (foundations of the Sumerian
  mass survive; height is reconstructive). Three solid stages of mud brick faced with baked brick in bitumen.
- Built by **Ur-Nammu** (completed under Šulgi), dedicated to **Nanna/Sîn**; Nabonidus later restored it
  (reportedly as seven stages — the model keeps the Neo-Sumerian three-stage form).
- Three stairways on the front (northeast face in the restored monument), meeting on a landing; temple of Nanna
  on the summit (destroyed; blue glazed bricks from the shrine are reported).
- Coordinates of the pin match Tell el-Muqayyar (`ur` in `ancient_cities.yaml`: 30.9626 N, 46.1030 E).

What the model assumes (`ziggurat_ur.glb`):

- Stage footprints about 64×45, 46×33 and 33×22 m; heights 11.5, 8.0 and 5.5 m; a whitewashed shrine ~15×10×5 m
  on top (~30 m overall). Three flights on the long front (central + two side), bitumen caps on the terraces,
  baked-brick parapets. Stage heights and shrine size are reconstruction choices within the published envelope.

## Eridu (Enki) and Nippur (Ekur)

**Eridu** (`ziggurat_eridu.glb`): the Ubaid–ED temple sequence sits on a raised platform that later carried a
ziggurat mound. No Woolley-quality stage plan for the Epic's century. The model is a **smaller single terrace**
(about 40 × 36 m, 8 m high, bitumen court, modest shrine) so it reads as an early platform, not a copy of Anu's
White Temple mass.

**Nippur** (`ziggurat_nippur.glb`): the Ekur ziggurat is excavated; published summaries give about **25 m**
surviving / reconstructed height. Stage plan is not used as a measured drawing here. The model is a **square
three-stage tower** (~52 m base, stages 12 / 7 / 4 m + shrine) totalling ~25 m, visually distinct from Ur's
rectangle and from Etemenanki's seven stages.

## Sources

- <https://en.wikipedia.org/wiki/Etemenanki>, <https://en.wikipedia.org/wiki/Ziggurat>
- <https://en.wikipedia.org/wiki/Great_Ziggurat_of_Ur>
- <https://www.globalsecurity.org/military/world/iraq/etemenanki.htm>
- <https://www.ancient-history-sites.com/?p=133381>
- Montero Fenollós et al., Etemenanki: <https://revistas.uam.es/isimu/article/download/3374/3591/6748>
- <https://archeologie.culture.gouv.fr/orient-cuneiforme/en/architecture-ziggurat>
- <https://worldhistory.org/image/11755> (recreation of the Etemenanki)
- <https://www.worldhistory.org/collection/248/a-gallery-of-ziggurats-of-ancient-mesopotamia/>
- <https://www.iransafar.co/what-is-a-ziggurat/> (overview; Anu height, bitumen, Uruk≠Ur; Susa lost; Etemenanki ~54 m
  estimate not followed)
- Anu ziggurat and White Temple, Uruk (Warka): artefacts-berlin.de (reconstructions; looked at for dimensions only,
  nothing is copied from them), <https://en.wikipedia.org/wiki/White_Temple_(Uruk)>, <https://en.wikipedia.org/wiki/Anu_Ziggurat>
- Nippur / Ekur: <https://whc.unesco.org/en/tentativelists/6173/> (~25 m ziggurat)
- Petr Sebek, *Uruk and its hinterland* (bachelor thesis, Plzen 2021), `Sebek_BP.pdf` in this directory; the notes are in
  `CITY.md`. The surveyed footprint: OSM ways 1311535414, 1311535415, see `LANDSCAPE.md`.
- Older compiled notes (partly outdated on Ur vs Uruk naming): `HISTORICAL_REFERENCES.md` § Ziggurats — prefer this file.
