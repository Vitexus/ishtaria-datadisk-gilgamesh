# 3D Models for Gilgamesh Datadisk
# Mesopotamian Architecture and Character Costumes

This document provides specifications and guidance for creating 3D models for the Gilgamesh datadisk.

> **Status:** the 20 NPC character models exist (rigged, `Idle`/`Walk`): see `models-src/README.md` and
> `research/CHARACTER_DESIGN.md`. They live directly in `media/models/<npc_id>.glb` (the schema forbids subdirectories
> for NPC models). The costume notes below are the older, partly Late Bronze Age wishlist; the research file supersedes
> them. `tools/blender/gilgamesh_character.py` is an obsolete stub.

## 🏛️ Architectural Models Required

### Ziggurats

#### 1. Ziggurat of Uruk (Main Ziggurat)
- **Scale**: Large (approximately 60m x 60m base, 25m height)
- **Structure**: 3-4 tiered levels
- **Materials**: 
  - Mud brick texture (light brown/tan)
  - White plaster finish on upper levels
  - Recessed panels and buttresses
- **Details**: 
  - Staircase leading to summit
  - Temple structure at top
  - Small windows/slits for ventilation
  - Decorative friezes near entrance
- **Texture Reference**: Historical Mesopotamian ziggurat reconstructions
- **Output**: `media/models/ziggurat_uruk.glb`

#### 2. Ziggurat of Anu
- **Scale**: Medium (45m x 45m base, 20m height)
- **Structure**: 3 tiered levels
- **Materials**: 
  - Darker mud brick
  - Lapis lazuli inlays (blue decorative elements)
  - White plaster accents
- **Details**:
  - Single central staircase
  - Smaller temple at summit
  - Sky/star motifs in decoration
- **Output**: `media/models/ziggurat_anu.glb`

#### 3. Ziggurat of Ishtar
- **Scale**: Medium (50m x 50m base, 22m height)
- **Structure**: 3 tiered levels
- **Materials**:
  - Red and pink plaster
  - Carnelian inlays (red-orange decorative stones)
  - Gold accents
- **Details**:
  - Multiple staircases
  - Lion and star motifs
  - Larger temple complex at top
- **Output**: `media/models/ziggurat_ishtar.glb`

#### 4. White Temple
- **Scale**: Small (30m x 20m base, 15m height)
- **Structure**: Single level on platform
- **Materials**:
  - Whitewashed exterior
  - Clean geometric lines
  - Mud brick core
- **Details**:
  - Rectangular shape
  - Niche decorations
  - Flat roof with parapet
- **Output**: `media/models/white_temple.glb`

### City Structures

#### 5. Great Wall of Uruk
- **Scale**: Massive (sections of 100m)
- **Structure**: 
  - Outer wall: 8m height, 5m thickness
  - Inner wall: 6m height, 4m thickness
  - Distance between walls: 15m
- **Materials**:
  - Mud brick with white plaster
  - Fortified towers every 50m
  - Crenelations at top
- **Details**:
  - Main gates with guardhouses
  - Arrow slits
  - Buttresses for reinforcement
- **Output**: `media/models/uruk_wall_section.glb`

#### 6. City Gate of Uruk
- **Scale**: Large (25m wide, 12m height)
- **Structure**: 
  - Massive stone and brick construction
  - Twin towers flanking entrance
  - Wooden doors with bronze reinforcement
- **Materials**:
  - Stone base
  - Mud brick upper sections
  - Bronze door fittings
- **Details**:
  - Decorative stone carvings
  - Guard platforms
  - Portcullis mechanism
- **Output**: `media/models/uruk_gate.glb`

#### 7. Royal Palace of Uruk
- **Scale**: Large complex (80m x 60m)
- **Structure**: Multiple buildings around courtyards
- **Materials**:
  - Mud brick with colorful plaster
  - Cedar wood beams
  - Stone foundations
- **Details**:
  - Throne room with raised dais
  - Private quarters
  - Audience halls
  - Gardens and pools
- **Output**: `media/models/royal_palace.glb`

#### 8. Hanging Gardens
- **Scale**: Medium (50m x 40m)
- **Structure**: Terraced garden on stone platform
- **Materials**:
  - Stone retaining walls
  - Soil and plants
  - Irrigation channels
- **Details**:
  - Multiple levels of planting
  - Water features
  - Shaded walkways
  - Exotic trees and flowers
- **Output**: `media/models/hanging_gardens.glb`

#### 9. Royal Tombs
- **Scale**: Small (20m x 20m)
- **Structure**: Underground or above-ground mausoleums
- **Materials**:
  - Stone blocks
  - Mud brick
  - Decorative carvings
- **Details**:
  - Multiple tomb chambers
  - Offering niches
  - Sealed entrances
- **Output**: `media/models/royal_tombs.glb`

### Special Locations

#### 10. Humbaba's Lair
- **Scale**: Medium (30m diameter)
- **Structure**: Cave-like with forest integration
- **Materials**:
  - Stone and earth
  - Cedar wood debris
  - Monster nest elements
- **Details**:
  - Carved stone throne
  - Bone decorations
  - Cedar tree roots integrated
  - Scattered weapons of defeated warriors
- **Output**: `media/models/humbaba_lair.glb`

#### 11. Scorpion Gate
- **Scale**: Medium (20m wide, 10m height)
- **Structure**: Mountain pass gateway
- **Materials**:
  - Natural stone
  - Carved scorpion motifs
  - Bronze reinforcements
- **Details**:
  - Massive scorpion statues
  - Gate mechanism
  - Warning inscriptions
- **Output**: `media/models/scorpion_gate.glb`

#### 12. Tunnel of the Sun
- **Scale**: Long tunnel (100m length, 5m height)
- **Structure**: Mountain tunnel
- **Materials**:
  - Natural stone walls
  - Carved reliefs
  - Torch holders
- **Details**:
  - Sun disk motifs
  - Light shafts from above
  - Ancient carvings
- **Output**: `media/models/tunnel_of_sun.glb`

#### 13. Ferry Across Waters of Death
- **Scale**: Small (10m long boat)
- **Structure**: Simple flat boat
- **Materials**:
  - Wooden construction
  - Stone ballast
- **Details**:
  - Oar or pole for propulsion
  - Simple seating
  - Ur-Shanabi's personal items
- **Output**: `media/models/ferry.glb`

#### 14. Utnapishtim's Dwelling
- **Scale**: Medium (35m x 25m)
- **Structure**: House with garden
- **Materials**:
  - Mud brick
  - Wooden beams
  - Reed thatch roof
- **Details**:
  - Modest but well-built
  - Garden with various plants
  - Water feature
- **Output**: `media/models/utnapishtim_dwelling.glb`

## 👗 Character Costumes

### Main Characters

#### Gilgamesh
- **Outfit**: Royal king's attire
- **Elements**:
  - Golden diadem/crown
  - White linen tunic with gold embroidery
  - Leather belt with gold buckle
  - Sandals
  - Amulets and jewelry
  - Short beard (character model feature)
- **Textures**: 
  - Gold metallic
  - Fine linen
  - Leather
- **Note**: Two-thirds god appearance - more magnificent than mortal men

#### Enkidu (Civilized)
- **Outfit**: Former wild man now civilized
- **Elements**:
  - Simple linen tunic
  - Leather belt
  - Sandals
  - Still some wild hair (long tresses)
  - Minimal jewelry
- **Textures**:
  - Rough linen
  - Leather
  - Body hair texture
- **Note**: Less refined than Gilgamesh, still showing wild origins

#### Enkidu (Wild)
- **Outfit**: Wild man appearance
- **Elements**:
  - Animal skin loincloth
  - Long, matted hair covering body
  - Long beard
  - No footwear
- **Textures**:
  - Animal fur
  - Body hair
  - Dirt and mud
- **Note**: Before meeting Shamhat

#### Ishtar
- **Outfit**: Goddess of love and war
- **Elements**:
  - Red and gold ceremonial robes
  - Lapis lazuli jewelry
  - Headdress with star motifs
  - Sandals
  - Weapon (mace or bow) at side
- **Textures**:
  - Fine silk/linen
  - Gold and lapis lazuli
  - Gemstones
- **Note**: Both beautiful and terrifying

#### Shamhat
- **Outfit**: Temple priestess
- **Elements**:
  - White ceremonial robes
  - Gold jewelry
  - Headdress
  - Sandals
  - Small ceremonial knife
- **Textures**:
  - Fine linen
  - Gold
  - Gemstones
- **Note**: Elegant but approachable

#### Humbaba
- **Outfit**: Monster/ogre
- **Elements**:
  - Animal skins and furs
  - Bone armor
  - Stone jewelry
  - Massive weapon (club or axe)
- **Textures**:
  - Rough skin
  - Fur
  - Bone
  - Stone
- **Note**: Terrifying appearance, sevenfold terrors

#### Utnapishtim
- **Outfit**: Wise elder
- **Elements**:
  - Simple white robes
  - Staff
  - Minimal jewelry
- **Textures**:
  - Linen
  - Wood
- **Note**: Ancient, wise, immortal appearance

#### Ur-Shanabi
- **Outfit**: Ferryman
- **Elements**:
  - Simple loincloth or tunic
  - Oar/pole
  - Pouch at belt
- **Textures**:
  - Rough linen
  - Wood
  - Leather
- **Note**: Practical working attire

#### Scorpion Man
- **Outfit**: Monster guardian
- **Elements**:
  - Human upper body with scorpion lower body
  - Chitin armor plates
  - Massive pincers
  - Scorpion tail
- **Textures**:
  - Chitin/armor
  - Human skin
  - Stone/rock elements
- **Note**: Half-man, half-scorpion

### Historical Figures

#### High Priest of Anu
- **Outfit**: Traditional priestly robes
- **Elements**:
  - White linen tunic and robe
  - Lapis lazuli bead necklace
  - White headdress
  - Ceremonial dagger
  - Clay tablet at belt
- **Textures**:
  - Fine linen
  - Lapis lazuli
  - Clay
  - Gold
- **Note**: Pure and divine appearance

#### High Priestess of Ishtar
- **Outfit**: Ceremonial robes of love and war
- **Elements**:
  - Red and gold robes
  - Gold jewelry
  - Star headdress
  - Ceremonial mace
- **Textures**:
  - Silk/linen
  - Gold
  - Gemstones
- **Note**: Regal and powerful

#### Temple Scribe
- **Outfit**: Scholar's attire
- **Elements**:
  - Simple white tunic
  - Clay tablets in satchel
  - Reed stylus at belt
  - Minimal jewelry
- **Textures**:
  - Linen
  - Clay
  - Reed/wood
- **Note**: Practical scholar appearance

#### Royal Guard
- **Outfit**: Elite soldier
- **Elements**:
  - Bronze scale armor
  - Plumed helmet
  - Bronze greaves
  - Sword and spear
  - Leather belt
- **Textures**:
  - Bronze metal
  - Leather
  - Feather plumes
- **Note**: Formidable protector

#### Uruk Noble
- **Outfit**: Wealthy citizen
- **Elements**:
  - Fine linen tunic with embroidery
  - Gold jewelry (necklace, bracelets, rings)
  - Leather sandals
  - Staff or walking stick
- **Textures**:
  - Fine linen
  - Gold
  - Leather
- **Note**: Wealthy and refined

#### Uruk Merchant
- **Outfit**: Trader's attire
- **Elements**:
  - Colorful tunic
  - Balance scale
  - Money pouch
  - Turban or head covering
- **Textures**:
  - Various colored fabrics
  - Metal (balance)
  - Leather
- **Note**: Practical but colorful

#### Potter
- **Outfit**: Craftsman's attire
- **Elements**:
  - Simple tunic
  - Clay-covered apron
  - Wooden tools at belt
  - Clay on hands and clothes
- **Textures**:
  - Linen
  - Clay
  - Wood
- **Note**: Working craftsman

#### Weaver
- **Outfit**: Textile worker's attire
- **Elements**:
  - Simple dress
  - Shuttle at belt
  - Fabric samples
  - Head covering
- **Textures**:
  - Linen
  - Various fabrics
  - Wood (shuttle)
- **Note**: Practical working woman

## 🎨 Blender Modeling Guidelines

### General Specifications

1. **File Format**: Export as `.glb` (GLTF Binary)
2. **Scale**: 1 unit = 1 meter in Ishtaria
3. **Polycount**: 
   - Architecture: 5,000-50,000 triangles (depending on size)
   - Characters: 10,000-30,000 triangles
   - Props: 1,000-10,000 triangles
4. **Textures**: 
   - Maximum size: 2048x2048 for main textures
   - Use PBR materials where possible
   - Compress textures for performance
5. **LODs**: Create Level of Detail versions for large structures
   - LOD0: Full detail (up to 50m)
   - LOD1: Medium detail (50m-100m)
   - LOD2: Low detail (100m+)

### Modeling Workflow

#### 1. Reference Gathering
- Study historical reconstructions of Mesopotamian architecture
- Use museum references for accurate details
- Review academic sources on Sumerian/Akkadian/Babylonian art

#### 2. Blockout Phase
```python
# Blender Python for quick blockout
import bpy

# Create ziggurat base
bpy.ops.mesh.primitive_cube_add(size=60, location=(0,0,0))
base = bpy.context.active_object
base.name = "Ziggurat_Base"

# Create second level (smaller)
bpy.ops.mesh.primitive_cube_add(size=40, location=(0,0,10))
level2 = bpy.context.active_object
level2.name = "Ziggurat_Level2"

# Create third level (smallest)
bpy.ops.mesh.primitive_cube_add(size=20, location=(0,0,25))
level3 = bpy.context.active_object
level3.name = "Ziggurat_Level3"
```

#### 3. Detailing Phase
- Add architectural details (buttresses, niches, friezes)
- Create accurate textures (mud brick, plaster, stone)
- Add wear and aging effects
- Model stairs, doorways, and windows

#### 4. Optimization
- Use bevel for hard edges
- Apply subsurface division for smooth curves
- Use instancing for repetitive elements (columns, windows)
- Optimize geometry for performance

#### 5. Texturing
- Create PBR materials
- Use historical color references
- Add dirt, wear, and aging
- Bake lighting where appropriate

#### 6. Export
- Select all objects
- File > Export > glTF 2.0 (.glb)
- Enable: Include > Selected Objects
- Transform: Apply
- Geometry: Include Normals, Include Tangents

### Historical Accuracy Notes

#### Materials Reference

**Mud Brick**:
- Color: #8B4513 to #A0522D (tan to brown)
- Texture: Rough, irregular
- Variations: Different firing temperatures create color variations

**Plaster**:
- Color: #F5F5DC to #FFFFFF (cream to white)
- Texture: Smooth with slight irregularities
- Often painted with geometric patterns

**Stone**:
- Color: #696969 to #A9A9A9 (gray)
- Types: Limestone, basalt, alabaster
- Texture: Smooth for carved, rough for natural

**Lapis Lazuli**:
- Color: #38618B to #0047AB (deep blue)
- Used for: Decorative inlays, jewelry, temple ornaments
- Texture: Smooth, polished

**Carnelian**:
- Color: #B31B1B to #CD5C5C (red-orange)
- Used for: Decorative inlays, jewelry
- Texture: Smooth, polished

**Gold**:
- Color: #FFD700 (standard gold)
- Used for: Temple ornaments, jewelry, royal items
- Texture: Highly polished, reflective

**Cedar Wood**:
- Color: #8B4513 to #A0522D (rich brown)
- Grain: Visible growth rings
- Used for: Doors, beams, furniture

**Bronze**:
- Color: #CD7F32 (metallic bronze)
- Texture: Slightly tarnished
- Used for: Weapons, armor, tools, fittings

### MesPotamian Architectural Features

1. **Buttresses**: Reinforcing projections on walls
2. **Niches**: Recessed rectangular spaces in walls
3. **Friezes**: Decorative bands with geometric or figurative designs
4. **Crenellations**: Battlements at wall tops
5. **Drainage**: Systems for water management
6. **Plaster**: White coating on mud brick
7. **Glazed Brick**: Colored bricks for decoration

### Character Proportions Reference

Based on historical depictions and the epic:

- **Gilgamesh**: Tall, muscular, heroic proportions
  - Height: ~2.0m (taller than normal men)
  - Build: Athletic, broad-shouldered
  - Hair: Short to medium, well-kept beard

- **Enkidu**: Strong, slightly shorter than Gilgamesh, broader
  - Height: ~1.9m
  - Build: Very muscular, stocky
  - Hair: Long, wild, matted when uncivilized

- **Ishtar**: Tall, regal, commanding presence
  - Height: ~1.8m
  - Build: Slender but strong
  - Features: Beautiful, proud

- **Humbaba**: Massive, monstrous
  - Height: ~3.0m
  - Build: Massive, distorted
  - Features: Terrible, with exaggerated facial features

- **Scorpion Man**: Hybrid creature
  - Human upper body: Normal proportions
  - Scorpion lower body: Large pincers, segmented tail
  - Height: ~2.5m total

## 📁 File Organization

```
media/models/
├── architecture/
│   ├── ziggurat_uruk.glb
│   ├── ziggurat_anu.glb
│   ├── ziggurat_ishtar.glb
│   ├── white_temple.glb
│   ├── uruk_wall_section.glb
│   ├── uruk_gate.glb
│   ├── royal_palace.glb
│   ├── hanging_gardens.glb
│   ├── royal_tombs.glb
│   ├── humbaba_lair.glb
│   ├── scorpion_gate.glb
│   ├── tunnel_of_sun.glb
│   └── ferry.glb
│
├── monsters/
│   ├── humbaba.glb
│   ├── scorpion_man.glb
│   └── bull_of_heaven.glb
│
└── characters/
    ├── gilgamesh.glb
    ├── enkidu.glb
    ├── enkidu_wild.glb
    ├── ishtar.glb
    ├── shamhat.glb
    ├── utnapishtim.glb
    ├── ur_shanabi.glb
    ├── high_priest_anu.glb
    └── high_priestess_ishtar.glb
```

## 🔧 Scripts for Automation

### Batch Export Script (Blender Python)

Save as `tools/export_models.py`:

```python
#!/usr/bin/env blender --background --python

import bpy
import os
import sys

# Configuration
MODEL_DIR = "//media/models"
EXPORT_FORMAT = 'GLB'

# Ensure output directory exists
os.makedirs(bpy.path.abspath(MODEL_DIR), exist_ok=True)

# Select all objects in the scene
bpy.ops.object.select_all(action='SELECT')

# Export each object/group as separate GLB
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        # Deselect all
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select only this object and its children
        obj.select_set(True)
        for child in obj.children:
            child.select_set(True)
        
        # Export
        export_path = os.path.join(bpy.path.abspath(MODEL_DIR), f"{obj.name}.glb")
        bpy.ops.export_scene.gltf(
            filepath=export_path,
            export_format=EXPORT_FORMAT,
            use_selection=True,
            export_materials='EXPORT',
            export_textures=True,
            export_normals=True,
            export_tangents=True
        )
        
        print(f"Exported: {export_path}")

print("Export complete!")
```

### Material Setup Script

```python
#!/usr/bin/env blender --background --python

import bpy

# Create standard Mesopotamian materials
def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    # Create Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    links = mat.node_tree.links
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create standard materials
mud_brick = create_material("MudBrick", (0.55, 0.27, 0.07, 1))
plaster = create_material("Plaster", (0.96, 0.96, 0.92, 1), roughness=0.6)
limestone = create_material("Limestone", (0.7, 0.7, 0.7, 1), roughness=0.7)
lapis = create_material("LapisLazuli", (0.22, 0.38, 0.55, 1), roughness=0.1, metallic=0.3)
gold = create_material("Gold", (0.83, 0.69, 0.22, 1), roughness=0.1, metallic=1.0)
bronze = create_material("Bronze", (0.8, 0.5, 0.2, 1), roughness=0.3, metallic=0.8)
cedar = create_material("CedarWood", (0.55, 0.27, 0.07, 1), roughness=0.7)

print("Materials created!")
```

## 📚 Historical References

### Ziggurat Architecture
- **Ziggurat of Ur** (2100 BCE): 3 levels, 21m height
- **Ziggurat of Nanna**: White temple on platform
- **Ziggurat of Aqar Quf**: Parthian era, well-preserved

### Mesopotamian Materials
- **Mud Brick**: 90% of construction, sun-dried
- **Fired Brick**: For important structures
- **Stone**: Rare, used for foundations and special elements
- **Wood**: Cedar from Lebanon, for beams and doors
- **Plaster**: White gypsum or lime
- **Glazed Brick**: Colored, for decorative facades

### Color Symbolism
- **White**: Purity, divinity, Anu
- **Red**: Life, vitality, Ishtar
- **Blue**: Heaven, divinity, lapis lazuli
- **Gold**: Royalty, divinity, wealth
- **Black**: Earth, underworld

### Architectural Details
- **Buttresses**: Every 2-3 meters
- **Niches**: For statues and offerings
- **Stairs**: Central or multiple, straight
- **Doors**: Wooden with stone thresholds
- **Roofs**: Flat, sometimes with parapets

## ✅ Next Steps

1. **Model the ziggurats first** (most iconic Mesopotamian structures)
2. **Create character models** with period-appropriate costumes
3. **Test in Ishtaria** by adding model references to NPCs
4. **Create LOD versions** for performance
5. **Add collision meshes** for interactive structures

## 🎯 Priorities

### High Priority (Essential for immersion)
- Ziggurat of Uruk
- Ziggurat of Anu
- Ziggurat of Ishtar
- Great Wall of Uruk
- Gilgamesh character model
- Enkidu character models (wild and civilized)
- Ishtar character model

### Medium Priority (Enhances experience)
- White Temple
- City Gate
- Royal Palace
- Humbaba character model
- Scorpion Man character model
- Historical NPC models

### Low Priority (Nice to have)
- Hanging Gardens
- Royal Tombs
- Tunnel of the Sun
- Ferry
- Utnapishtim's Dwelling
- Other monsters

---

**Note**: While 3D models greatly enhance the visual experience, the datadisk is fully functional without them. The existing character packs (protagonists, retro, survivors) provide placeholder appearances for all NPCs, and the places will be generated using the scenery system.