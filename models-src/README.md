# Character model sources

Sources of the NPC models in `media/models/`. They are not installed by the package; only the exported `.glb` ships.

- `build_models.py`: entry point, `blender -b --python models-src/build_models.py -- <npc_id|all> media/models`.
- `chargen/core.py`: primitives (sphere, cylinder, tube), materials and the texture tinting.
- `chargen/humanoid.py`: body, hair, beards, garments, jewellery, props, skeleton, `Idle`/`Walk` animations, glTF export.
  The skin parts are fused into one seamless mesh (voxel remesh, smoothed) and take over the weights of the parts.
- `chargen/npcs.py`: look of the 18 humanoids (heights, dress, attributes) after `research/CHARACTER_DESIGN.md`.
- `chargen/creatures.py`: the old procedural Scorpion Man and Bull of Heaven (replaced by the Rodin models below; kept as a fallback).
- `rodin_rig.py` rigs humanoid Rodin meshes from `rodin/<id>.json`. With `"skirt": true` the lower legs keep half their
  weight on the hips so a long robe does not tear between the legs; a short skirt or tunic sets `skirt_hem` (metres)
  so bare shins below the hem follow the legs alone, and `ankle_blend` (metres above the ankle, default [0.02, 0.13])
  narrows where the foot's weight fades into the shin. The hunter and Gilgamesh use both; their shins bent mid-length before.
- `rodin_rig_creature.py` rigs non-humanoid Rodin meshes (bones, legs and tail from `rodin/<id>.json`, weights by distance to the bones, Idle and Walk); `rodin_scorpion_assemble.py` joins the Rodin scorpion and the Rodin upper body of a man into the Scorpion Man; `rodin/views.py` + `views_grid.py` give metre grids to read the bones off.
- `textures/*.jpg`: 256 px fabric, fur, leather and skin textures generated with InvokeAI (RealVisXL_V4.0).

The models are authored in metres, face -Y in Blender (+Z in glTF), stand with the feet at the origin and keep a
`Head_end` bone at the top for the client's name plate. A model must stay below 4 MiB (they are about 1 MiB).
`Idle` loops in 3 s, `Walk` in 1 s. Check a model in Godot (skeleton, clips, blend shapes) or render it with
`tools/blender/render_preview.py`.

## Architecture

`architecture/ziggurat.py` builds the buildings in `media/models/architecture/` procedurally (no rig): the Etemenanki
(`etemenanki`, `etemenanki_precinct`, `etemenanki_complete`), Anu (`anu`), Ur / Etemenniguru (`ur`), Eridu (`eridu`)
and Nippur / Ekur (`nippur`). Catalog and clone policy: `research/ZIGGURATS.md`.

    blender -b --python models-src/architecture/ziggurat.py -- ur media/models/architecture/ziggurat_ur.glb

Walls are battered prisms with pilasters and recessed panels, the stairs are sawtooth prisms, the UVs are in metres per
texture tile (one brick size on every wall), vertex colours add weathering. `architecture/textures/*.jpg` are
InvokeAI textures (Juggernaut XL v9) made seamless by `architecture/make_tileable.py`. Renders are in
`architecture/renders/`. The datadisk format cannot place such a model yet: see `research/ZIGGURATS.md`.

`architecture/ishtar_gate.py` builds the Ishtar Gate (`ishtar_gate`, `processional_way`, `ishtar_gate_complete`) with the same
helpers: `blender -b --python models-src/architecture/ishtar_gate.py -- ishtar_gate media/models/architecture/ishtar_gate.glb`.
The relief panels (aurochs, mushussu dragon, lion, two drawings of each animal, the rosette border) and the blue glaze, stone
paving and cedar door textures are InvokeAI images (Juggernaut XL v9); the panels are placed on the walls by explicit
UVs, the glaze is tiled.

`architecture/uruk_walls.py` builds the walls of Uruk in the style of the Ishtar Gate, in one model with the gate and the
Processional Way: `blender -b --python models-src/architecture/uruk_walls.py -- uruk_walls media/models/architecture/uruk_walls.glb`.
A rectangular circuit (400 x 420 m, 18 m high, 7 m thick) of glazed blue brick with the rows of aurochs and dragons of the gate on
its outer face, corner and wall towers, four flights of stairs to the wall walk, and the passage of the Ishtar Gate as the
only entrance. The JPEG textures are saved again at a lower quality so that the model stays below the 4 MiB of a datadisk
model. `places/uruk.yaml` places it as the `structure` of the city (`offset_m: [0, 232]`: the model's origin is the gate,
the middle of the city lies 232 m behind it).

`architecture/gilgamesh_statue.py` composes the statue of Gilgamesh holding the lion, after the Neo-Assyrian "king
mastering a lion" statues (`research/gilgamesh-lion-statue.jpg`): the rigged king `media/models/gilgamesh.glb` scaled to
4.5 m (Gilgamesh was a demigod giant) on a limestone pedestal, with the rigged adult male lion
`media/models/mountain_lion.glb` rearing upright in his arms - an adult lion, not a cub; the size difference is the
king's. The poses are baked from the `Idle` clips (the king's left arm into a cradle, the lion on its hind legs) and
the painted character textures are kept, as the ancient statues were polychrome.
One static mesh:

    blender -b --python models-src/architecture/gilgamesh_statue.py -- media/models media/models/architecture

writes `gilgamesh_statue.glb` (1.5 MiB) and `gilgamesh_statue_collision.glb` (three boxes) into
`media/models/architecture/`; `--preview` renders `architecture/renders/gilgamesh_statue_*.png`. `tools/build_statues.py`
places the statue three times in Uruk (palace courtyard, court of Eanna, royal tombs) and `tools/build_city_statues.py`
in every city of the disk and in front of the Etemenanki ziggurat.

`architecture/lamassu_models.py` builds the lamassu (aladlammu) guardians of Uruk from the 0 A.D. statues
`pers_lamassu` and `pers_lamassu_small` (Wildfire Games, CC BY-SA 3.0; mirrored under `media/models/architecture/zeroad/`):
welded, decimated, scaled to 7.6 m and 2.2 m, standing on the ground and looking south at yaw 0, as pairs 9.5 m and
5.4 m apart, with simple collision boxes:

    blender -b --python models-src/architecture/lamassu_models.py -- media/models/architecture

writes `lamassu_pair.glb`, `lamassu_pair_collision.glb`, `shedu_pair.glb` and `shedu_pair_collision.glb`.
`tools/build_statues.py` places the pairs at the gates, palaces, precinct entrances and stairs of Uruk and the small
shedu at house doors and markets (`places/uruk_statues.yaml`); `places/lamassu_guardians.yaml` stands the raw 0 A.D.
statues at Susa. Provenance and the licence history: `models-src/lamassu/NOTES.md`.

`rodin/make_concepts.py` and `rodin/img2img_concept.py` make the concept images for Hyper3D Rodin on the remote InvokeAI
server; the sources of the Rodin models of the citizens of Uruk are in `uruk_*/` and the images in `concepts/`.
Gilgamesh's Hyper3D export (concept, raw GLB with combat clips, welded source) lives in `gilgamesh/`.
The clips in the raw Hyper3D exports (`*_rodin_raw.glb`) come from Hyper3D's own animation library (Humanoid), not
from Mixamo; Hyper3D only names the bones of its auto-rig the Mixamo way (`LeftHandThumb3`, ...), which is what
"Mixamo-style" and "Mixamo bone" mean in these sources and scripts.
After `rodin_rig.py`, `gilgamesh/retarget_clips.py` bakes Run, Jump, Sit and Die from the raw Hyper3D
clips onto `media/models/gilgamesh.glb` for the client's pose contract.

## Files kept compressed in git

`models-src/gilgamesh/gilgamesh_rodin_raw.glb` (128 MB, the raw Hyper3D Rodin export of Gilgameš) is larger than GitHub accepts
(100 MB a file), so git holds it as `gilgamesh_rodin_raw.glb.xz` (36 MB, `xz -9e`). Unpack it before use with `make raw-models`
(or `xz -dk models-src/gilgamesh/gilgamesh_rodin_raw.glb.xz`); the unpacked file is git-ignored. The Gilgameš model in
`media/models/` is built from it by `models-src/gilgamesh/retarget_clips.py`. If you change the export, pack it again with
`xz -9e -k models-src/gilgamesh/gilgamesh_rodin_raw.glb`. Blender's `*.blend1` backups are ignored.
