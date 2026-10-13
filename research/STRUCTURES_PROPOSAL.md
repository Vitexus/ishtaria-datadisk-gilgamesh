# Custom building models in datadisk places (implemented)

Status: **implemented in the working trees of ishtaria-protocol, ishtaria-server, ishtaria-client and this disk on
2026-10-13; not committed.** Decision record: `ishtaria-docs/source/decisions/0012-datadisk-structures.rst`.
The owner chose walkable stairs (not only a solid footprint) and to include the Babylonian buildings as a fantasy element.

## Contract (see `datadisk.schema.json`, `places[].structure`)

```yaml
structure:
  model: media/models/architecture/ziggurat_anu.glb   # required; <= 4 MiB; metres; +Y up; self-contained glb
  collision: media/models/...                         # optional simpler mesh for collision
  scale_m: 1.0  yaw_deg: 0  offset_m: [east, north]    # placement relative to the place's anchor
  ground_m: [x, z]    # the point of the model that stands on the terrain (the foot of its stairs); default the origin
  visible_m: 600      # how far away the server announces it
```

## How it works

- Server: `story/disk.rs` validates and ships the files; `story/settlements.rs::build_structure` reads the glb with
  `src/glb.rs` (no new dependency), registers the collision mesh (`movement.rs::register_structure`) and emits
  a prop `disk:<disk>:<path>` plus a collider; towns leave room for buildings.
- Walking: near a building the character is moved by the swept capsule against the mesh (`movement.rs`), with a step of
  0.7 m and a walkable contact normal of 0.4 for building meshes (stairs of 45 degrees meet a round capsule on their edges).
- Client: `surface_environment.gd` fetches `disk:` models through the story media cache and fills the waiting placement.

## Verified

- Server unit tests: synthetic stairs (0.3 m risers, also 43 degrees), a wall that is too high, glb reader, validation.
- Live: a bot logged in to a generated world, walked to the Anu ziggurat and climbed 13.5 m up its stairs.
- Not verified: how it looks in the client (no screenshot was taken), performance on weak GPUs, other worlds' seeds.

## Limits

- Models float or sink on uneven ground; give them a foundation (the walls go 14 m below the ground plane).
- No doors, interiors, destruction; animals are not walked by the mesh.
- Etemenanki and the Ishtar Gate are Babylon (c. 575 BCE), not Uruk of Gilgamesh (c. 2700 BCE): a fantasy element.
