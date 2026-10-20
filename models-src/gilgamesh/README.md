# Gilgamesh (Hyper3D Rodin)

Hyper3D job `faf4343a-6e21-477b-83d9-dd9bbd37e5cd` (2026-10-19). Concept from Hyper3D Image
Generator (A-pose, ED dress + Assyrian Master-of-Animals beard). Not shipped in the `.deb`;
only `media/models/gilgamesh.glb` is.

| File | Role |
| --- | --- |
| `gilgamesh_concept.jpg` | Image-to-3D prompt result |
| `gilgamesh_rodin_raw.glb` | Full web export (`base_basic_pbr.glb`): ~1 M faces, PBR, Mixamo-style clips (Walk, Run, Boxing, Kicking, Dying, …) for later cedar-forest combat |
| `gilgamesh_rodin_source.glb` | Welded + decimated static mesh for `rodin_rig.py` (~90 k faces) |
| `gilgamesh_shipped_before_rodin.glb` | Previous game mesh (chargen/Rodin pilot) |
| `rebuild_source.py` | Rebuilds `gilgamesh_rodin_source.glb` from the raw export |
| `renders/` | Idle / Walk checks |

Rebuild the pipeline source (keeps UVs and paint; welds UV-seam doubles before Decimate):

```sh
blender -b --python models-src/gilgamesh/rebuild_source.py
```

Game model (Idle / Walk via `rodin_rig`, then Run / Jump / Sit / Die retargeted from the raw
Mixamo clips):

```sh
blender -b --python models-src/rodin_rig.py -- \
  models-src/gilgamesh/gilgamesh_rodin_source.glb \
  media/models/gilgamesh.glb \
  models-src/rodin/gilgamesh.json
blender -b --python models-src/gilgamesh/retarget_clips.py -- \
  models-src/gilgamesh/gilgamesh_rodin_raw.glb \
  media/models/gilgamesh.glb \
  media/models/gilgamesh.glb
```

`retarget_clips.py` maps `HumanRunning` → `Run`, `HumanForwardJump` → `Jump`,
`HumanSitting2` → `Sit`, `HumanDying` → `Die` onto the chargen armature (local
`matrix_basis` copy; hip height on Jump/Sit/Die) and keeps Idle/Walk from `rodin_rig`.
`HumanSitting2` is a high crouch-sit from Hyper3D, not a deep chair pose — enough for a
rock rest. Preview frames: `renders/{Idle,Run,Jump,Sit,Die}.png`. Boxing / Kicking stay
in the raw export for a later cedar-forest milestone.

Statue with the lion (rebuild after the game GLB changes):

```sh
blender -b --python models-src/architecture/gilgamesh_statue.py -- \
  media/models media/models/architecture --preview
python3 tools/render_portraits.py gilgamesh
```

The raw GLB is large (~128 MiB) on purpose: it keeps the web skeleton and combat clips that
`rodin_rig.py` does not use. Original download zip (three GLB variants) lived at
`~/Downloads/rodin3D-gilgamesh-faf4343a-6e21-477b-83d9-dd9bbd37e5cd.zip`.
