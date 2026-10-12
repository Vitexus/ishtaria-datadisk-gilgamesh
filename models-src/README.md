# Character model sources

Sources of the NPC models in `media/models/`. They are not installed by the package; only the exported `.glb` ships.

- `build_models.py`: entry point, `blender -b --python models-src/build_models.py -- <npc_id|all> media/models`.
- `chargen/core.py`: primitives (sphere, cylinder, tube), materials and the texture tinting.
- `chargen/humanoid.py`: body, hair, beards, garments, jewellery, props, skeleton, `Idle`/`Walk` animations, glTF export.
  The skin parts are fused into one seamless mesh (voxel remesh, smoothed) and take over the weights of the parts.
- `chargen/npcs.py`: look of the 18 humanoids (heights, dress, attributes) after `research/CHARACTER_DESIGN.md`.
- `chargen/creatures.py`: Scorpion Man (human torso, eight legs, jointed tail) and the Bull of Heaven.
- `textures/*.jpg`: 256 px fabric, fur, leather and skin textures generated with InvokeAI (RealVisXL_V4.0).

The models are authored in metres, face -Y in Blender (+Z in glTF), stand with the feet at the origin and keep a
`Head_end` bone at the top for the client's name plate. A model must stay below 4 MiB (they are about 1 MiB).
`Idle` loops in 3 s, `Walk` in 1 s. Check a model in Godot (skeleton, clips, blend shapes) or render it with
`tools/blender/render_preview.py`.
