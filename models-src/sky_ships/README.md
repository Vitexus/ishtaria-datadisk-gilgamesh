# Sky ships (easter egg)

`sky_ships.blend` builds both models (Blender 4.3, via the Blender MCP); exports are `media/models/sky_disc.glb`
(winged disc Sham-a: disc, dome, rim, glowing underside, two feathered wings, tail fan) and `media/models/sky_gir.glb`
(GIR / MU rocket with conical capsule, four fins, bands, flame). Front is +Z in glTF, origin in the middle.

Textures (InvokeAI, RealVisXL_V4.0, 30 steps, in `textures/`):

| File | Seed | Prompt (abridged) |
| --- | --- | --- |
| `hull_bronze.png` 1024x1024 | 2700 | hammered bronze plate, engraved cuneiform, lapis lazuli inlay bands, weathered patina |
| `wing_feathers.png` 1024x512 | 2701 | Assyrian winged sun disc feathers in layered rows, gold, lapis blue, carnelian red |

Flights are scheduled by `sky_flyers.yaml` at the disk root. The lore is "ancient astronauts" folklore told in character
(`dialogues/*`): in the game it is what the people of Uruk say, not a claim about history.
