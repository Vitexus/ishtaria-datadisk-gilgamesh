# Mesopotamian Architecture Models

This directory contains 3D models of Mesopotamian architecture created for the Gilgamesh datadisk using Blender 4.3.2.

## Models

### Ziggurats
1. **ziggurat_simple.glb** (4.5 KB)
   - Simple stepped ziggurat with 4 tiers
   - Basic mud brick material
   - Size: ~10m x 10m base

2. **ziggurat_etemenanki.glb** (2.4 MB)
   - Great Ziggurat of Babylon (Etemenanki), rebuilt by `models-src/architecture/ziggurat.py`
   - 6 stages and the glazed temple of Marduk on top, three stairways, textured mud and baked brick
   - Size: ~91 m base, ~96 m high, stairs reach 33 m in front
   - `etemenanki_precinct.glb`: paved court, enclosure wall with glazed band and gate, palms (203 m)

   `ishtar_gate.glb` (2.8 MB): the Ishtar Gate of Babylon, outer gate, courtyard and the higher inner gate with the
   curtain walls, glazed blue brick with rows of aurochs and mushussu dragons (88 x 56 m, 27 m high with merlons);
   `processional_way.glb` (1.3 MB): the street, 80 m, with the walls of striding lions. See `research/ISHTAR_GATE.md`.

   `uruk_walls.glb` (3.9 MB) and `uruk_walls_collision.glb` (1 MB): the wall of Uruk on its surveyed OpenStreetMap
   outline (8.6 km, 18 m high, towers, stairs), with the Ishtar Gate and Processional Way in the south wall and
   the Anu ziggurat on its excavated terrace; built by `models-src/architecture/uruk_walls.py` from
   `tools/data/uruk_outlines.json`, see `research/LANDSCAPE.md`.

   `ziggurat_anu.glb` (1.1 MB): Early Dynastic ziggurat of Anu with the White Temple (Uruk), ~52 m

3. **ziggurat_complex.glb** (9.8 KB)
   - Complete ziggurat complex with:
     - Main ziggurat (5 tiers)
     - Temple at the top
     - Courtyard walls
   - Size: ~30m x 30m total

### Temples and Religious Structures
4. **temple.glb** (2.9 KB)
   - Mesopotamian temple building
   - Sandstone/limestone material
   - Size: ~15m x 20m

5. **shrine.glb** (7.1 KB)
   - Small religious shrine
   - Stone base with gold trim pillars
   - Size: ~5m x 5m

### Civil Buildings
6. **palace.glb** (6.1 KB)
   - Royal palace with:
     - Main hall
     - Throne room
     - 4 corner towers
   - Mud brick with wood accents
   - Size: ~30m x 20m

7. **residential.glb** (3.7 KB)
   - Typical Mesopotamian house
   - Flat roof (characteristic of the region)
   - Small courtyard wall
   - Size: ~8m x 6m

8. **grain_storage.glb** (2.9 KB)
   - Grain storage building
   - Large rectangular structure
   - Size: ~10m x 10m

### Public Structures
9. **marketplace.glb** (12 KB)
   - Marketplace with:
     - Ground plane
     - 5 market stalls with roofs
     - Central trading platform
   - Size: ~40m x 40m

10. **city_gate.glb** (3.7 KB)
    - Mesopotamian city gate (Ishtar Gate inspired)
    - Decorative towers
    - Blue lapis lazuli glaze material
    - Size: ~15m x 3m

## Technical Details

- **Format**: GLTF Binary (.glb)
- **Software**: Blender 4.3.2
- **Units**: Meters (Blender units)
- **Materials**: Included in models
- **Polygons**: Low-poly for performance
- **Textures**: None (using material colors)

## Generation

Models were created using Python scripts that leverage Blender's Python API (`bpy`).

### Scripts
- `tools/blender/create_ziggurat.py` - Creates ziggurats and temple structures
- `tools/blender/create_mesopotamian_building.py` - Creates additional buildings

### Usage

To create new models:
```bash
# Navigate to datadisk directory
cd /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh

# Create a ziggurat
blender --background --python tools/blender/create_ziggurat.py -- ziggurat_simple output.glb

# Create a palace
blender --background --python tools/blender/create_mesopotamian_building.py -- palace output.glb
```

### Available Types

**create_ziggurat.py:**
- ziggurat_simple
- ziggurat_etemenanki
- ziggurat_stairs
- temple
- city_gate
- complex

**create_mesopotamian_building.py:**
- palace
- residential
- marketplace
- grain_storage
- shrine

## Historical Accuracy

All models are inspired by archaeological evidence and historical descriptions:
- **Ziggurats**: Based on Ur ziggurat, Etemenanki descriptions
- **Temples**: Based on Sumerian and Akkadian temple designs
- **Ishtar Gate**: Based on the famous Babylonian gate with blue glazed bricks
- **Residential**: Based on excavated houses from Ur and other cities
- **Materials**: Mud brick, limestone, cedar wood (all historically accurate)

## License

All models are CC BY-SA 4.0, matching the datadisk license.
