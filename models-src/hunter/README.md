# Hunter (Hyper3D Rodin, player model)

The player starts as the hunter of Tablet I (`player_model` in `datadisk.yaml`). Hyper3D job
`85b93290-bfc4-4962-ac05-b44c6cdd4f30` (image-to-3D from a Hyper3D 2D concept in A-pose, arms well away from
the body: the earlier version with arms at the sides stuck its hands to the hips in the walking clip).
Not shipped in the `.deb`; only `media/models/hunter.glb` is.

| File | Role |
| --- | --- |
| `hunter_concept.png` | InvokeAI concept of the first static attempt (`models-src/rodin/make_concepts.py hunter`) |
| `hunter_rodin_raw.glb` | Full web export (`base_basic_pbr.glb`): 500 k faces, Mixamo rig, clips Walking, Dying, ForwardJump, Boxing, Kicking, ... |
| `hunter_rodin_source.glb` | Welded + decimated static mesh (~90 k faces) for `rodin_rig.py` |
| `rebuild_source.py` | Rebuilds the source from the raw export |
| `retarget_clips.py` | Bakes Jump and Die from the raw Mixamo clips onto the game armature |
| `previous/` | The chargen model that shipped before, and the earlier static Rodin attempts |

The joint positions in `models-src/rodin/hunter.json` were read from the Mixamo bones of the raw export.

    blender -b --python models-src/hunter/rebuild_source.py
    blender -b --python models-src/rodin_rig.py -- models-src/hunter/hunter_rodin_source.glb media/models/hunter.glb models-src/rodin/hunter.json
    blender -b --python models-src/hunter/retarget_clips.py -- models-src/hunter/hunter_rodin_raw.glb media/models/hunter.glb media/models/hunter.glb

The export has no running or sitting clip (only the limping `HumanInjuredRun`), so the model has `Idle`, `Walk`,
`Jump` and `Die`; the client skips the clips that are missing.

## Clips from the Mixamo export

`retarget_clips.py` and `../retarget_ambient.py` (the clips of every other Rodin figure, `../clipmaps/<npc>.json`) turn each game bone
as its Mixamo bone turns in the world (`world`, the fifth argument of `retarget_ambient.py`). The first versions copied the local
rotation of each bone, which is only right near the rest pose: the bones of the two rigs are rolled differently, so a lying
swimmer or a falling man came out as a tangle. `../audit_clips.py` measures it (0 degrees = the clip moves like its source; the old
clips were 20 to 86 degrees off on average):

    blender -b --python models-src/audit_clips.py -- models-src/<npc>/<npc>_rodin_raw.glb media/models/<npc>.glb models-src/clipmaps/<npc>.json
    blender -b --python models-src/hunter/preview_clip.py -- MODEL.glb ACTION OUT_PREFIX 0 36 72    # renders frames to look at

Re-run a figure's clips: `blender -b --python models-src/retarget_ambient.py -- models-src/<npc>/<npc>_rodin_raw.glb media/models/<npc>.glb
media/models/<npc>.glb models-src/clipmaps/<npc>.json world` (replaces the clips of the clipmap, keeps the others).
