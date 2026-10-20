# ishtaria-datadisk-gilgamesh

Epic story datadisk for [Ishtaria](https://git.vitexsoftware.com/Ishtaria/ishtaria-docs) based on
the ancient **Epic of Gilgamesh**, the world's oldest surviving work of literature.

**Open source content** - CC BY-SA 4.0 license. This datadisk brings the epic tale of
Gilgamesh, king of Uruk, and his companion Enkidu to life in the Ishtaria world.

A datadisk is data, not code: places, characters, dialogue trees and scenarios that the Ishtaria
server evaluates. This disk can be combined with other datadisks in one world.

```
datadisk.yaml          manifest (id, version, requires/conflicts, license, rating)
places/                places the world generator finds sites for (Uruk, Cedar Forest...)
npcs/                  characters standing at places (Gilgamesh, Enkidu, Ishtar...)
dialogues/             decision trees: character dialogues and story branches
quests/                the epic questline as stage machines
lore/                  codex entries for the epic characters and events
i18n/en.yaml cs.yaml   English and Czech translations
voice/voices.yaml      voice synthesizer settings for NPC speech
tools/                 helper scripts (render_voices.py, build_landscape.py: terrain patch of Uruk, see research/LANDSCAPE.md;
                       build_city.py: plan of the streets, houses, markets, palaces and fields of Uruk, see research/CITY.md;
                       build_world_map.py: the real planet of the world, see research/WORLD.md)
media/                 portraits, character models (media/models/*.glb), architecture models, cover,
                       world rasters (media/world/: the Early Dynastic Earth with the Persian Gulf of the Epic)
models-src/            Blender builder of the character models (not installed)
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


Format: `ishtaria-protocol/schemas/datadisk.schema.json`. Check the disk (schema, references, media):

```sh
python3 ../ishtaria-protocol/tests/validate_datadisk.py .
```

Install (`dpkg-buildpackage -us -uc -b`, then `dpkg -i`) to `/usr/share/ishtaria/datadisks/gilgamesh/`.
In `ishtaria-admin`, *World maps → Generate map* then shows a checkbox for this disk; or
`ishtaria-server-init <seed> <size> gilgamesh`.

## Content Overview

### The Epic Storyline

A **finite indie narrative** for players interested in ancient Iraq: live the Epic of
Gilgamesh in a short playable arc (not dozens of hours of grind). You begin as the
hunter, then Šamḫat, Enkidu and finally Gilgameš. Long journeys (Cedar Forest, Dilmun)
use story travel, not real-distance walking. If you die or a quest fails (for example
Šamḫat on the road), the active quest **restarts at its checkpoint** instead of ending
in a permanent memorial.

Story beats:

1. **Hunter and the wild man**: snares at the water-hole, father, Gilgameš, Šamḫat
2. **Civilization of Enkidu**: Šamḫat teaches love, bread, ale and clothing
3. **Meeting of equals**: Enkidu wrestles Gilgameš; they become brothers; you become the king
4. **Cedar Forest**: prepare in Uruk, travel, face Humbaba
5. **Ishtar and the Bull of Heaven**: rejection, divine punishment
6. **Death of Enkidu**: grief and the decision to seek eternal life
7. **Journey to Utnapishtim**: Mashu, the Tunnel of the Sun, the Waters of Death
8. **Eternal life**: unlike the epic, you **can** win immortality (epilogue ends the game);
   losing the plant / accepting mortality is the secondary ending

### Main Locations

- **Uruk**: The great city with its mighty walls, temples, and palace
- **Cedar Forest**: Vast forest stretching ten thousand leagues, home of Humbaba
- **Mount Mashu**: Mountain through which the sun passes, with the Scorpion Gate
- **Tunnel of the Sun**: Dark passage through Mount Mashu
- **Waters of Death**: Deadly waters that must be crossed to reach Utnapishtim
- **Utnapishtim's Dwelling**: Home of the flood survivor across the Waters of Death

### Main Characters

- **Gilgamesh**: King of Uruk, two-thirds god and one-third man
- **Enkidu**: Wild man created from clay, Gilgamesh's loyal companion
- **Ishtar**: Goddess of love and war, patron of Uruk
- **Shamhat**: Temple priestess who civilizes Enkidu
- **Humbaba**: Guardian of the Cedar Forest
- **Utnapishtim**: Survivor of the Great Flood, granted eternal life
- **Ur-Shanabi**: Ferryman across the Waters of Death
- **Scorpion Man**: Guardian of the gate to Mount Mashu
- **Ninsun**: Gilgamesh's mother, wise goddess
- **Anu**: Sky god, father of Ishtar
- **Bull of Heaven**: Divine beast sent to punish Gilgamesh

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
```

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
Hyper3D Mixamo export onto the game armature (see `models-src/gilgamesh/README.md`). The source meshes
are under `models-src/ishtar/` and `models-src/gilgamesh/`. Rebuild Ishtar with

    blender -b --python models-src/rodin_rig.py -- models-src/ishtar/ishtar_rodin_source.glb media/models/ishtar.glb models-src/rodin/ishtar.json

The client plays `Idle` on NPC models. Player Gilgamesh also uses `Walk` / `Run` / `Jump` / `Sit` / `Die`
when those clips exist. Other NPCs do not move yet (the server has no NPC paths), so `Walk` is ready
for when they do.

## Notes

This datadisk demonstrates how the Ishtaria engine can be extended to support full-featured
story-driven experiences. The epic questline provides a comprehensive gameplay experience
from character creation through the hero's journey and eventual acceptance of mortality.

Music tracks live in `media/music/` (synthesized by `tools/compose_music.py` as gish-gudi lute and
zurna-style reed with drone, a shared Gilgamesh leitmotif, sectioned verse/rest timelines and
heterophony — inspired by public descriptions of Sumerian instruments, not a sample of any
commercial recording; CC0 loops in `tools/music-samples/`). Regenerate with
`python3 tools/compose_music.py`. A cover image should be added to `media/cover/cover.jpg`
(1024x768 recommended).
