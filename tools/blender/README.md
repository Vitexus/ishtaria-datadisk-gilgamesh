# Blender Tools for Gilgamesh Datadisk

This directory contains Blender Python scripts for creating 3D models for the Gilgamesh datadisk.

## Requirements

- Blender 3.0 or later (tested with 3.6 LTS)
- Python 3.10+

## Usage

### Running Scripts

#### Method 1: From Blender GUI
1. Open Blender
2. Go to `Scripting` workspace
3. Open a new text editor
4. Paste the script content
5. Run the script with the play button or press `Alt+P`

#### Method 2: From Command Line
```bash
blender --background --python ziggurat_uruk.py
blender --background --python gilgamesh_character.py
```

#### Method 3: Export All Models
```bash
# Create models directory
mkdir -p media/models/architecture
mkdir -p media/models/characters
mkdir -p media/models/monsters

# Run all scripts
blender --background --python ziggurat_uruk.py
blender --background --python gilgamesh_character.py
# Add more scripts as needed
```

## Available Scripts

### Architecture Scripts
1. **ziggurat_uruk.py** - Creates the Ziggurat of Uruk
   - Output: `media/models/architecture/ziggurat_uruk.glb`
   - Features: 3 tiered platforms, staircase, buttresses, niches, temple
   - Size: ~60m x 50m base, ~22m height

2. **ziggurat_anu.py** - Creates the Ziggurat of Anu
   - Output: `media/models/architecture/ziggurat_anu.glb`
   - Features: 3 tiers, lapis lazuli inlays, sky motifs
   - Size: ~45m x 45m base, ~20m height

3. **ziggurat_ishtar.py** - Creates the Ziggurat of Ishtar
   - Output: `media/models/architecture/ziggurat_ishtar.glb`
   - Features: 3 tiers, red plaster, lion motifs
   - Size: ~50m x 50m base, ~22m height

4. **white_temple.py** - Creates the White Temple
   - Output: `media/models/architecture/white_temple.glb`
   - Features: Rectangular, white plaster, niche decorations
   - Size: ~30m x 20m base, ~15m height

5. **uruk_wall.py** - Creates a section of Uruk's Great Wall
   - Output: `media/models/architecture/uruk_wall_section.glb`
   - Features: Fortified towers, crenellations, gates
   - Size: 100m long section

### Character Scripts
1. **gilgamesh_character.py** - Creates Gilgamesh character
   - Output: `media/models/characters/gilgamesh.glb`
   - Features: Kaunakes skirt, linen tunic, golden crown, beard
   - Height: 2.0m (taller than normal men)

2. **enkidu_character.py** - Creates Enkidu character
   - Output: `media/models/characters/enkidu.glb`
   - Versions: Wild (animal skins) and Civilized (linen tunic)
   - Height: 1.9m

3. **ishtar_character.py** - Creates Ishtar goddess
   - Output: `media/models/characters/ishtar.glb`
   - Features: Horned headdress, red and gold robes, jewelry
   - Height: 1.8m

### Monster Scripts
1. **humbaba.py** - Creates Humbaba monster
   - Output: `media/models/monsters/humbaba.glb`
   - Features: Massive size, animal skins, bone armor
   - Height: ~3.0m

2. **scorpion_man.py** - Creates Scorpion Man guardian
   - Output: `media/models/monsters/scorpion_man.glb`
   - Features: Human upper body, scorpion lower body, pincers
   - Height: ~2.5m

## Modeling Guidelines

### Scale
- **1 Blender unit = 1 meter** in Ishtaria
- Character models: Realistic human proportions
- Architecture: Based on archaeological measurements

### Polycount
- **Characters**: 10,000-30,000 triangles
- **Architecture**: 5,000-50,000 triangles (depending on size)
- **Props**: 1,000-10,000 triangles
- **Optimization**: Use instancing for repetitive elements

### Textures
- **Format**: PNG with alpha channel
- **Size**: 1024x1024 or 2048x2048 for main textures
- **Type**: PBR (Base Color, Roughness, Metallic, Normal, AO)
- **Compression**: Use appropriate texture compression

### Materials
- Use PBR (Physically Based Rendering) materials
- Accurate historical colors and textures
- Reference: `3D_MODELS.md` for color palettes

### Export Settings
- **Format**: GLB (GLTF Binary)
- **Scale**: Apply all transforms before export
- **Options**: Include materials, textures, normals, tangents
- **Max Size**: 4 MiB per model

## Historical Accuracy

All models are based on:
- Archaeological reconstructions
- Museum artifacts (British Museum, Louvre, Pergamon Museum)
- Academic publications on Mesopotamian architecture
- Historical depictions (Standard of Ur, Stele of Naram-Sin, Statues of Gudea)

## Creating New Models

1. **Research**: Consult `research/HISTORICAL_REFERENCES.md`
2. **Blockout**: Create basic shapes and proportions
3. **Detail**: Add architectural features and costume elements
4. **Texture**: Create PBR materials
5. **Optimize**: Reduce polycount, create LODs if needed
6. **Export**: Use GLB format with proper settings

## Testing in Ishtaria

After creating models:

1. Place GLB files in appropriate `media/models/` subdirectories
2. Reference in NPC definitions:
   ```yaml
   character: {pack: protagonists, skin: warriorMaleA, model: media/models/characters/gilgamesh.glb}
   ```
3. Test in Ishtaria server with the Gilgamesh datadisk

## Troubleshooting

### Common Issues
1. **Scale Problems**: Ensure 1 unit = 1 meter
2. **Missing Materials**: Check material assignments in Blender
3. **Texture Issues**: Verify texture paths and packing
4. **Export Errors**: Make sure all transforms are applied

### Tips
- Use Blender's 3D viewport to preview models at correct scale
- Test with simple shapes first before detailed modeling
- Use reference images for accurate proportions
- Save incremental versions of your work

## Performance Optimization

1. **LODs**: Create multiple levels of detail for large objects
   - LOD0: Full detail (0-50m)
   - LOD1: Medium detail (50-100m)
   - LOD2: Low detail (100m+)

2. **Instancing**: Use for repetitive elements (columns, windows)
3. **Decimation**: Reduce polycount where not visible
4. **Texture Atlases**: Combine multiple textures into one

## Additional Resources

- [Blender Documentation](https://docs.blender.org/)
- [GLTF/GLB Export Guide](https://docs.blender.org/manual/en/latest/addons/io_scene_gltf2.html)
- [PBR Material Guide](https://polyhaven.com/pbr)
- [Mesopotamian Architecture References](https://cdli.ucla.edu/)

## License

All scripts and generated models are part of the Gilgamesh datadisk and licensed under CC BY-SA 4.0.

---

**Status**: Scripts are placeholders that create basic geometry. For production-quality models, use these as starting points and add more detail manually in Blender.
