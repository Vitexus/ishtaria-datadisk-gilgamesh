# Ziggurats of the datadisk (research notes)

Models: `media/models/architecture/ziggurat_etemenanki.glb`, `etemenanki_precinct.glb`, `ziggurat_anu.glb`.
Built by `models-src/architecture/ziggurat.py` (see `models-src/README.md`).

## Etemenanki, the tower of Babylon

What the sources agree on (searched 2026-10, see the links below):

- A square base of about 91 m a side, found in the excavations of Koldewey; the Esagila tablet (a Seleucid copy, 229 BC of
  older texts) gives base measurements that match it.
- Seven stages with the temple of Marduk (Ekarzagina) on the seventh; about 90 m in all in the usual reconstruction
  (a dissenting proposal by Montero Fenollós and colleagues reaches only 66 m, with other accesses and another
  temple layout).
- Baked brick and bitumen outside, mud brick inside (inscriptions of Nabopolassar and Nebuchadnezzar II); the temple
  was probably clad in glazed blue brick and the upper stages are thought to have been painted.
- The stairways: three, meeting at a gate before the first stage, as at the ziggurat of Ur and as in the
  reconstruction pictures that were shown by the project owner.

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

- One massive terrace, not a tower of stages: about 12 m high, raised over many building phases (artefacts-berlin.de,
  the Sebek thesis). The excavated mound body is 56 x 49 m, the surveyed footprint 49 x 63 m (see `LANDSCAPE.md`).
- A court of about 50 x 45 m on top, behind sloped outer walls (artefacts-berlin.de: a surface of about 45 x 50 m at a
  height of about 12 m; the Sebek thesis: 12 m high, the court on top about 50 x 45 m).
- The White Temple on the court: 22 x 17 m (the model: 22.3 x 17.5 m), built 3517-3358 BCE, whitewashed, tripartite,
  three entrances and none faces the access ramp (a visitor has to walk round it), pits for sacrifices in the big
  middle room; its roof about 21 m above the plain. A small terrace north of the temple with a 3 x 2 m fire pit.

What the model assumes (`ziggurat_anu.glb`, rebuilt 2026-10):

- The base 57 x 52 m with a 3.5 m batter on every side (the court 50 x 45 m) reconciles the surveyed footprint with the
  published court; the walls are smoothed and grooved, the weep holes decorative. The remaining proportions are
  approximate.
- The access keeps the layout of the reconstruction drawing of the ziggurat of Ur shown by the owner: three flights
  meeting on a solid landing against the front of the terrace — a steep central flight at 43 degrees (0.3 m risers,
  0.316 m treads, the slope the server's walking tests climb) between parapets, and two ramps running along the front
  from the sides — with a gate house on the landing at the head of the central flight. The drawing is a reference for
  the layout only, not a source of geometry or texture.

## Sources

- <https://en.wikipedia.org/wiki/Etemenanki>, <https://en.wikipedia.org/wiki/Ziggurat>
- <https://www.globalsecurity.org/military/world/iraq/etemenanki.htm>
- <https://www.ancient-history-sites.com/?p=133381>
- Montero Fenollós et al., Etemenanki: <https://revistas.uam.es/isimu/article/download/3374/3591/6748>
- <https://archeologie.culture.gouv.fr/orient-cuneiforme/en/architecture-ziggurat>
- <https://worldhistory.org/image/11755> (recreation of the Etemenanki)
- Anu ziggurat and White Temple, Uruk (Warka): artefacts-berlin.de (reconstructions; looked at for dimensions only,
  nothing is copied from them), <https://en.wikipedia.org/wiki/White_Temple_(Uruk)>, <https://en.wikipedia.org/wiki/Anu_Ziggurat>
- Petr Sebek, *Uruk and its hinterland* (bachelor thesis, Plzen 2021), `Sebek_BP.pdf` in this directory; the notes are in
  `CITY.md`. The surveyed footprint: OSM ways 1311535414, 1311535415, see `LANDSCAPE.md`.
