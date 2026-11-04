# ishtaria-datadisk-gilgamesh

<!-- source-notice -->
> **Primary source:** <https://git.vitexsoftware.com/Ishtaria/ishtaria-datadisk-gilgamesh> (development happens there). **GitHub** (<https://github.com/Vitexus/ishtaria-datadisk-gilgamesh>) is a secondary mirror; packages and binaries are **not built from GitHub**.
<!-- /source-notice -->

Epic story datadisk for [Ishtaria](https://git.vitexsoftware.com/Ishtaria/ishtaria-docs) based on
the ancient **Epic of Gilgamesh**, the world's oldest surviving work of literature.

**Open source content** - CC BY-SA 4.0 license. This datadisk brings the epic tale of
Gilgamesh, king of Uruk, and his companion Enkidu to life in the Ishtaria world.

A datadisk is data, not code: places, characters, dialogue trees and scenarios that the Ishtaria
server evaluates. This disk can be combined with other datadisks in one world.

```
datadisk.yaml          manifest (id, version, requires/conflicts, license, rating, cover)
places/                places the world generator finds sites for (Uruk and its districts, Cedar Forest, the cities of
                       the Early Dynastic world, the clay tablets of the legends, ...)
npcs/                  characters standing at places (Gilgamesh, Enkidu, Ishtar, the crowd of Uruk, the elders, ...)
dialogues/             decision trees: character dialogues and story branches
quests/                the epic questline as stage machines
buildings/             the houses of Uruk, of the hunter's village and of ancient villages, and the fields (generated)
trails/                the roads (generated)
rivers/                the Euphrates, the Tigris and the canals between the cities
knowledge.yaml         knowledge cards: the clay tablets and inscriptions a player can read
achievements.yaml      the disk's achievements
lore/                  codex entries for the epic characters and events
i18n/en.yaml cs.yaml   English and Czech translations
voice/voices.yaml      voice synthesizer settings for NPC speech
tools/                 generators and helper scripts (see "How the world is made" below)
media/                 portraits, character models (media/models/*.glb), architecture models, terrain rasters and the
                       map of Uruk (media/terrain/), music, the cover, world rasters (media/world/: the Early Dynastic
                       Earth with the Persian Gulf of the Epic)
models-src/            Blender builders of the character and architecture models (not installed)
research/              the sources behind the story, the city and the landscape (notes, not installed)
```

The world this disk generates is the real Early Dynastic Earth, not a procedural
planet: real continent outlines and heights (ETOPO 2022), with the Persian Gulf
extended to its 2700 BCE shoreline and both rivers running into it. The rasters
below `media/world/` are what `ishtaria-server-init` and `ishtaria-admin` render the
world heightmap from; `make world` rebuilds them and `research/WORLD.md` documents
what is real data and what is a documented reconstruction.

Epic text research (eBL Standard Babylonian I–XII + OB/MB witnesses, Thompson 1928 PD,
planned multi-protagonist questline Hunter → Šamḫat → Enkidu → Gilgameš): see
[`research/EPIC.md`](research/EPIC.md) and [`research/QUESTLINE.md`](research/QUESTLINE.md).


**Contributing:** you do not need to program. Scholars and students of Assyriology are especially welcome,
see [CONTRIBUTING.md](CONTRIBUTING.md) (Czech and English) and [CONTRIBUTORS](CONTRIBUTORS).

Format: `ishtaria-protocol/schemas/datadisk.schema.json`. Check the disk (schema, references, media):

```sh
python3 ../ishtaria-protocol/tests/validate_datadisk.py .
```

Install (`dpkg-buildpackage -us -uc -b`, then `dpkg -i`) to `/usr/share/ishtaria/datadisks/gilgamesh/`.
In `ishtaria-admin`, *World maps → Generate map* then shows a checkbox for this disk; or
`ishtaria-server-init <seed> <size> gilgamesh`.

## Content Overview

### At a glance

- **1,362 houses**, modelled one by one: 1,278 in Uruk, 21 in the hunter's village and 63 in the villages of nine ancient cities
- **11 quests** following the Epic, from the hunter's snares to the search for immortality
- **189 NPCs**: **56 named characters** (heroes of the Epic, rulers, historical figures, craftsmen, village mayors) and the townspeople and villagers of the crowd
- **12 achievements**
- 71 dialogues, in English and Czech, with spoken lines

The numbers are counted from the data of the disk: run `make stats` to refresh them after the game has grown.

### The Epic Storyline

A **finite indie narrative** for players interested in ancient Iraq: live the Epic of
Gilgamesh in a short playable arc (not dozens of hours of grind). You begin as the
hunter, then Šamḫat, Enkidu and finally Gilgameš. Long journeys (Cedar Forest, Dilmun)
use story travel, not real-distance walking. If you die or a quest fails (for example
Šamḫat on the road), the active quest **restarts at its checkpoint** instead of ending
in a permanent memorial.

Story beats:

1. **Hunter and the wild man**: snares at the water-hole, the old father, the market of Uruk (where you ask the way to the king), Gilgameš in his palace, Šamḫat
2. **Civilization of Enkidu**: Šamḫat teaches love, bread, ale and clothing
3. **Meeting of equals**: Enkidu wrestles Gilgameš; they become brothers; you become the king
4. **Cedar Forest**: prepare in Uruk, travel, face Humbaba
5. **Ishtar and the Bull of Heaven**: rejection, divine punishment
6. **Death of Enkidu**: grief and the decision to seek eternal life
7. **Journey to Utnapishtim**: Mashu, the Tunnel of the Sun, the Waters of Death
8. **Eternal life**: unlike the epic, you **can** win immortality (epilogue ends the game);
   losing the plant / accepting mortality is the secondary ending

### Main Locations

- **Uruk**: the great city, drawn from a plan of the real one: a wall of 8.6 km with its gates, the sacred precinct with the
  stepped tower of Ishtar and the terrace of Anu, the palace of Gilgamesh, markets, streets and thousands of houses, canals and
  fields, and the quay on the Euphrates. The city has a map of its own on the minimap (walls, streets, houses, canals).
- **The hunter's village and the water-hole**: the old father's village and the pond where the hunter's story begins, a few
  hours' walk north-west of Uruk
- **The cities of the world**: Eridu, Nippur, Kish, Ur, Larsa, Babylon, Assur and many more, each at its historical site; their
  ziggurats and the clay tablets of the legends
- **Cedar Forest**: Vast forest stretching ten thousand leagues, home of Humbaba
- **Mount Mashu**: Mountain through which the sun passes, with the Scorpion Gate
- **Tunnel of the Sun**: Dark passage through Mount Mashu
- **Waters of Death**: Deadly waters that must be crossed to reach Utnapishtim
- **Utnapishtim's Dwelling**: Home of the flood survivor across the Waters of Death

### Main Characters

- **Gilgamesh**: King of Uruk, two-thirds god and one-third man; he holds court in his palace
- **Enkidu**: Wild man created from clay, Gilgamesh's loyal companion (in Uruk only once Šamḫat has brought him there)
- **Ishtar**: Goddess of love and war, patron of Uruk; she stands with her priests on the top platform of her stepped tower
- **Shamhat**: Temple priestess who civilizes Enkidu
- **Humbaba**: Guardian of the Cedar Forest
- **Utnapishtim**: Survivor of the Great Flood, granted eternal life
- **Ur-Shanabi**: Ferryman across the Waters of Death
- **Scorpion Man**: Guardian of the gate to Mount Mashu
- **Ninsun**: Gilgamesh's mother, wise goddess
- **Anu**: Sky god, father of Ishtar
- **Bull of Heaven**: Divine beast sent to punish Gilgamesh; it grazes on the pasture outside the walls

### What a character knows

The story is told in order, and so is what the people of Uruk say of it. A character speaks of an event only once the player has
got there (a branch on the quest stages), and before that gives an answer that leaves it out; the civilized Enkidu does not stand
in Uruk before Šamḫat has brought him (`visible_if` of the character). Nobody tells how Enkidu was made a man before it has
happened, nor of the Cedar Forest, the Bull of Heaven or the death of Enkidu before the player has lived them.

The people of the world are not all alike. Every **elder** (one at the market of Uruk and two at each home of the hunter's
village) knows ONE tale (men: Atra-Hasis, Etana, Adapa, the New Year song; women: Ishtar's descent, the New Year song, Dilmun,
Nergal) and, as a separate choice of the dialogue, says where ONE clay tablet of it lies. To learn the other tales, or where the
other tablets lie, the player asks other elders. The tablets stand where the legends were kept: in the courts of the temples and
at the ziggurats of the old cities.

### How the world is made

Most of the content below the line is **generated** by scripts in `tools/` from sources in `tools/data/` and `research/`; the
generated files say so in their first lines and are rewritten by the script, not edited.

| Script | Writes | What it does |
| --- | --- | --- |
| `build_world_map.py` | `media/world/` | the Early Dynastic Earth: relief, shores, the Persian Gulf of 2700 BCE |
| `build_landscape.py` | `media/terrain/uruk_*.png` | the landscape patch of Uruk: relief, the Euphrates, where the city stands |
| `build_city.py` | `tools/data/uruk_city.json` | the plan of Uruk: gates, streets, houses, markets, palaces, canals, fields |
| `build_buildings.py` | `buildings/uruk.yaml` | the houses of the plan that are separate buildings, each fitted to its plot (the buried part of a 0 A.D. house is scaled with the house) |
| `build_map.py` | `media/terrain/uruk_map.png` | the map of Uruk the minimap draws: wall and gates, streets, houses, canals, fields, the river |
| `build_river_life.py` | `places/uruk_river.yaml` | the green banks, the quay at the gate where the Euphrates comes nearest to the wall, the boats (the hunter rows the first fishing boat) |
| `build_roads.py` | `places/uruk_roads.yaml`, `trails/` | the roads leave by the gates: the hunter's road ends at the gate nearest to his village (north-west), a short road leads from the river gate to the quay. Roads to other cities are not laid: Larsa, the only city within 25 km, lies beyond the Euphrates (250 to 300 m wide) and the server bridges 36 m at most (`JOIN_CITIES`) |
| `build_village.py`, `build_ancient_villages.py` | `buildings/`, `places/`, `npcs/` | the hunter's village and the villages of other cities |
| `build_elders.py` | `dialogues/elder_*.yaml`, `i18n/` | one tale and one tablet for every elder |
| `build_waterhole.py` | `media/terrain/hunter_waterhole_*.png` | the pond beside the hunter's spawn |
| `compose_music.py`, `render_voices.py` | `media/music/`, `media/voice/` | the music and the spoken lines |

## Spoken Lines

`dpkg-buildpackage` runs `tools/render_voices.py`: every NPC line is synthesized with Piper
and encoded to OGG Vorbis in `media/voice/<language>/<text_key>.ogg`.

`dpkg-buildpackage -P pkg.ishtaria-datadisk-gilgamesh.novoice` skips the rendering.

### Voice Configuration

Each NPC has a unique voice profile in `voice/voices.yaml` with:
- Piper text-to-speech model
- Pitch adjustment
- Tempo (speech rate)
- Noise and echo effects for character

The Epic of Gilgamesh features distinct voices for each major character to enhance immersion.

## Development

```sh
make check     # validate the datadisk
make voices    # render all spoken lines (requires Piper and ffmpeg)
make stage     # stage for local testing
make server    # start local server with this datadisk
make stop      # stop the server
make logs      # follow server logs
make clean     # clean build artifacts
make sumer-map # redraw maps/sumer.<lang>.png from the data of the disk
```

### The map of Sumer

`maps/sumer.en.png` and `maps/sumer.cs.png` show Sumer as it is in the game: the coast and relief of the world rasters,
the Euphrates, the Tigris and their canals and tributaries, every city with its name and the roads. The picture is
drawn from the data of the disk (`rivers/`, `places/`, `trails/`, `media/world/`, `i18n/`) by `tools/build_sumer_map.py`, so
run `make sumer-map` after the game has grown (a new city, river or road) to bring it up to date. `--lang`, `--bbox` and
`--pixels-per-degree` change the language, the region and the size.

## Requirements

- **Piper**: `python3-piper-tts` for text-to-speech
- **Voice models**: `piper-voice-cs-cz-jirka-medium`, `piper-voice-en-us-libritts-r-medium`
  (installed under `/usr/share/piper/voices/`)
- **ffmpeg**: For audio conversion to OGG Vorbis
- **Python 3**: With PyYAML installed
- **Ishtaria Server**: For local testing

## Source Material

The dialogue and story content is based on the public domain translation of the Epic of Gilgamesh
by N. K. Sanders (Assyrian International News Agency, www.aina.org). The original text
is available at: https://archive.org/stream/TheEpicofGilgamesh_201606/eog_djvu.txt

## License

CC BY-SA 4.0. All original content in this datadisk is licensed under Creative Commons
Attribution-ShareAlike 4.0 International. The Epic of Gilgamesh text is in the public domain.

## Credits

- **Epic of Gilgamesh**: Public domain translation by N. K. Sanders
- **Datadisk Design**: Based on the ancient Mesopotamian epic
- **Characters**: Faithful to the original epic descriptions
- **Quests**: Following the narrative structure of the epic

## Character models

Every NPC has a rigged glTF model in `media/models/<npc_id>.glb` (skeleton, `Idle` and `Walk` clips, blink and
mouth blend shapes; the three non-humans, Humbaba, the Scorpion Man and the Bull of Heaven, have their own rigs).
Their look follows Early Dynastic Uruk, see `research/CHARACTER_DESIGN.md`. `pack`/`skin` in `npcs/*.yaml` stay as the
fallback while a model loads. Rebuild and re-render:

    blender -b --python models-src/build_models.py -- all media/models      # or one id, e.g. gilgamesh
    python3 tools/render_portraits.py                                       # media/portraits/*.jpg from the models
    blender -b --python tools/blender/render_preview.py -- media/models/gilgamesh.glb /tmp/g.png full Walk 7

Ishtar is the exception: her model is a Hyper3D Rodin mesh (concept image from InvokeAI), made game-ready by
`models-src/rodin_rig.py`. Her settings are in `models-src/rodin/ishtar.json`. Gilgamesh uses the same
pipeline plus `models-src/gilgamesh/retarget_clips.py`, which bakes Run, Jump, Sit and Die from the
Hyper3D export (clips of Hyper3D's own animation library) onto the game armature (see `models-src/gilgamesh/README.md`). The source meshes
are under `models-src/ishtar/` and `models-src/gilgamesh/`. Rebuild Ishtar with

    blender -b --python models-src/rodin_rig.py -- models-src/ishtar/ishtar_rodin_source.glb media/models/ishtar.glb models-src/rodin/ishtar.json

The client plays `Idle` on NPC models and `Walk` while a character walks (the crowd, the shepherds, the road traffic and the
companion who follows the player). Player Gilgamesh also uses `Run` / `Jump` / `Sit` / `Die` when those clips exist.

## Notes

This datadisk demonstrates how the Ishtaria engine can be extended to support full-featured
story-driven experiences. The epic questline provides a comprehensive gameplay experience
from character creation through the hero's journey and eventual acceptance of mortality.

Music tracks live in `media/music/`. The core Gilgamesh themes (logo, plains, city, temple,
cedar forest, marsh waters) are synthesized by `tools/compose_music.py` (gish-gudi lute and
zurna-style reed; CC0 loops in `tools/music-samples/`). Regenerate with
`python3 tools/compose_music.py`. Place-specific colour (Sumerian rivers, Nile, harbours,
Susa, Indus, Mashu, Waters of Death, Dilmun) comes from 0 A.D. (Wildfire Games, CC BY-SA 3.0;
see `media/music/License-zeroad.txt`) and is selected on each place via `music` /
`music_radius_m`. A cover image should be added to `media/cover/cover.jpg`
(1024x768 recommended).
