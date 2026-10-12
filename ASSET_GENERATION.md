# Asset Generation Guide for Gilgamesh Datadisk

This guide provides instructions for generating all artwork and 3D models needed for the Gilgamesh datadisk. Since the mcp-server-invokeai and mcp-server-blender are not available in this environment, this document provides alternative methods for creating the assets.

## 📋 Current Status

The Gilgamesh datadisk is **structurally complete** with all YAML content created, translations done, and placeholder assets generated. The following has been added:

### ✅ Completed
- **Historical Research**: `research/HISTORICAL_REFERENCES.md` - Comprehensive guide to Mesopotamian art, architecture, and costumes
- **Blender Scripts**: `tools/blender/` - Python scripts for creating 3D models
  - `ziggurat_uruk.py` - Creates Ziggurat of Uruk
  - `gilgamesh_character.py` - Creates Gilgamesh character model
  - `texgen.py` - Generates PBR textures for Mesopotamian materials
  - `README.md` - Documentation for all Blender scripts
- **Asset Generation Script**: `tools/generate_assets.py` - Generates prompts for AI image generation
- **Updated Makefile**: Added commands for asset generation
- **Music References**: Sourced in `tools/generate_assets.py`

### 🎯 Still Needed
1. **Real Character Portraits** - Replace placeholder portraits with proper artwork
2. **3D Models** - Generate or manually create the GLB models
3. **Music Tracks** - Add background music for locations
4. **Cover Image** - Create an eye-catching cover image

## 🎨 Generating Portraits

### Method 1: Using AI Image Generation (Recommended)

#### Requirements
- Stable Diffusion, Midjourney, DALL-E, or similar AI image generator
- OR InvokeAI (when available)
- OR access to online services

#### Steps

1. **Generate Prompts**
   ```bash
   make prompts
   ```
   This creates JSON files with detailed prompts in the `prompts/` directory:
   - `portrait_prompts.json` - Prompts for all 19 character portraits
   - `architecture_prompts.json` - Prompts for Mesopotamian buildings
   - `cover_prompt.json` - Prompt for the datadisk cover

2. **Use the Prompts**
   Copy the prompts from these files and use them with your preferred AI image generation service.

3. **Example Stable Diffusion Command**
   ```bash
   # Using Automatic1111 WebUI
   # Paste the positive and negative prompts into the txt2img interface
   
   # Or using command line with InvokeAI (when available)
   # invokeai --prompt "[PASTE_PROMPT_HERE]" --negative "[PASTE_NEGATIVE_PROMPT]" \
   #   --width 512 --height 512 --output media/portraits/[character].png
   ```

4. **Manual Prompt Example for Gilgamesh**
   ```
   Positive: Mesopotamian king of uruk from the epic of gilgamesh era, two-thirds god and one-third man, mighty king of Uruk, oppresses his people, taking brides and abusing his power, wearing golden diadem/crown with lapis lazuli inlays, white linen tunic with gold embroidery, kaunakes (sheep-fleece skirt), wide leather belt with gold buckle, gold-decorated sandals, gold necklace bracelets signet ring, short to medium length well-kept hair, short curled beard, sword at belt dagger, regal confident hero pose, proud commanding, historically accurate Mesopotamian royal portrait, upper body portrait, 512x512 pixels, transparent background, soft lighting from upper left, cinematic, professional illustration, character focused, no modern elements, authentic Mesopotamian art style
   
   Negative: blurry, low resolution, modern clothing, fantasy elements, cartoon, anime, realistic photography, watermark, text
   
   Settings:
   - Size: 512x512
   - Steps: 30-50
   - CFG Scale: 7-12
   - Model: Realistic or semi-realistic
   ```

5. **Save Portraits**
   Save generated images as:
   - Format: PNG or JPEG
   - Size: 512x512 pixels
   - Max size: 1 MiB per file
   - Location: `media/portraits/[character_name].jpg` or `.png`
   - Background: Transparent preferred, or simple neutral gradient

### Method 2: Manual Creation

#### Requirements
- Image editing software (GIMP, Krita, Photoshop)
- Historical reference images

#### Steps
1. Download reference images from `research/HISTORICAL_REFERENCES.md`
2. Create portraits based on historical accuracy guidelines
3. Match the style: Semi-realistic, clean lines, soft lighting
4. Use the color palette from the historical references
5. Save in the correct format and location

#### Recommended References
- British Museum: [Mesopotamia Collection](https://www.britishmuseum.org/collection/galleries/mesopotamia)
- Louvre: [Near Eastern Antiquities](https://www.louvre.fr/en/departments/near-eastern-antiquities)
- Wikimedia Commons: Search for "Sumerian statue", "Mesopotamian art", etc.

## 🏛️ Creating 3D Models

### Method 1: Using Blender Scripts (Recommended)

#### Requirements
- Blender 3.0 or later (tested with 3.6 LTS)
- Python 3.10+

#### Steps

1. **Run Blender Scripts**
   ```bash
   make models
   ```
   This will run the Blender scripts and generate models.
   
   OR run manually:
   ```bash
   blender --background --python tools/blender/ziggurat_uruk.py
   blender --background --python tools/blender/gilgamesh_character.py
   ```

2. **Manual Enhancement**
   The scripts create basic geometry. For production quality:
   - Open the generated models in Blender
   - Add more detail and refinement
   - Adjust proportions for historical accuracy
   - Add proper UV unwrapping
   - Create detailed textures

3. **Export as GLB**
   - Select all objects in the scene
   - File > Export > glTF 2.0 (.glb)
   - Settings:
     - Format: GLB (Binary)
     - Include: Selected Objects
     - Materials: EXPORT
     - Textures: True
     - Normals: True
     - Tangents: True
     - Apply Modifiers: True
   - Save to: `media/models/[category]/[model_name].glb`

### Method 2: Manual Modeling in Blender

#### Steps
1. Open Blender
2. Use the specifications from `3D_MODELS.md` and `research/HISTORICAL_REFERENCES.md`
3. Model based on archaeological reconstructions
4. Apply PBR materials
5. Export as GLB

#### Recommended Add-ons
- **MeshMachines** - For hard surface modeling
- **HardOps** - For architectural details
- **BoxCutter** - For precise cutting
- **TextureLab** - For PBR materials

## 🎵 Adding Music Tracks

### Sources for Free Music

1. **Free Music Archive**: https://freemusicarchive.org/
   - Search for: "Mesopotamian", "ancient", "middle eastern", "ambient"

2. **Incompetech** (Kevin MacLeod): https://incompetech.com/
   - Royalty-free music
   - Search for: "Ancient", "Epic", "Mystery"

3. **Tabletop Audio**: https://tabletopaudio.com/
   - 10-minute looping ambient tracks
   - Perfect for background music

### Required Tracks

| Track ID | Location | Style | Filename |
|----------|----------|-------|----------|
| temple | Temple locations | Sacred, mystical | `media/music/temple.ogg` |
| ishtar_shrine | Ishtar's Temple | Passionate, rhythmic | `media/music/ishtar_shrine.ogg` |
| cedar_forest | Cedar Forest | Dark, mysterious | `media/music/cedar_forest.ogg` |
| mountain_echo | Mount Mashu | Echoing, cavernous | `media/music/mountain_echo.ogg` |
| waters_of_death | Waters of Death | Dark, ominous | `media/music/waters_of_death.ogg` |
| utnapishtim | Utnapishtim's Dwelling | Peaceful, wise | `media/music/utnapishtim.ogg` |

### Conversion to OGG

```bash
# Install ffmpeg if not available
# sudo apt-get install ffmpeg

# Convert MP3 to OGG
ffmpeg -i input.mp3 -c:a libvorbis -q:a 6 output.ogg

# Ensure proper format
ffmpeg -i input.mp3 -c:a libvorbis -q:a 6 -f ogg output.ogg
```

### Music File Requirements
- Format: OGG Vorbis
- Channels: Mono or Stereo
- Sample Rate: Up to 48 kHz
- Maximum Size: 8 MiB per track
- Looping: Tracks should be seamless loops

## 🖼️ Creating Cover Image

### Method 1: AI Generation

Use the cover prompt from `prompts/cover_prompt.json`:

```
Positive: Epic of Gilgamesh cover art, Gilgamesh and Enkidu in foreground, Ziggurat of Uruk in background, Cedar Forest elements, Gilgamesh wearing golden crown and white robes, Enkidu in kaunakes skirt and simple tunic, both heroes in heroic poses, Uruk ziggurats towering in background, golden hour lighting with dramatic shadows, clear blue sky with subtle clouds, title text 'Gilgamesh' at top, Mesopotamian art style, historically accurate, cinematic composition, wide shot, 1024x768 pixels, highly detailed, professional fantasy art, epic atmosphere, authentic costumes and architecture

Negative: modern elements, anachronisms, fantasy creatures not in epic, cartoon, anime, low resolution, blurry, watermark, text (except title)
```

### Method 2: Manual Creation

1. **Composition**
   - Foreground: Gilgamesh (left) and Enkidu (right) in heroic poses
   - Middle: Cedar Forest trees
   - Background: Ziggurats of Uruk
   - Sky: Clear blue with subtle clouds
   - Title: "Gilgamesh" at top

2. **Style**
   - Cinematic, wide shot
   - Golden hour lighting
   - Dramatic shadows
   - Authentic Mesopotamian art style

3. **Requirements**
   - Size: 1024x768 pixels
   - Format: JPEG or PNG
   - Max size: 1 MiB
   - Save as: `media/cover/cover.jpg`

## 📁 File Organization

```
ishtaria-datadisk-gilgamesh/
├── media/
│   ├── portraits/             # 19 character portraits (512x512)
│   │   ├── gilgamesh.jpg
│   │   ├── enkidu.jpg
│   │   ├── ishtar.jpg
│   │   ├── shamhat.jpg
│   │   ├── humbaba.jpg
│   │   ├── utnapishtim.jpg
│   │   ├── ur_shanabi.jpg
│   │   ├── scorpion_man.jpg
│   │   ├── ninsun.jpg
│   │   ├── anu.jpg
│   │   ├── bull_of_heaven.jpg
│   │   ├── high_priest_anu.jpg
│   │   ├── high_priestess_ishtar.jpg
│   │   ├── temple_scribe.jpg
│   │   ├── royal_guard.jpg
│   │   ├── uruk_noble.jpg
│   │   ├── uruk_merchant.jpg
│   │   ├── potter.jpg
│   │   └── weaver.jpg
│   │
│   ├── cover/                 # Cover image
│   │   └── cover.jpg         # 1024x768
│   │
│   ├── music/                 # Music tracks
│   │   ├── temple.ogg
│   │   ├── ishtar_shrine.ogg
│   │   ├── cedar_forest.ogg
│   │   ├── mountain_echo.ogg
│   │   ├── waters_of_death.ogg
│   │   └── utnapishtim.ogg
│   │
│   └── models/                # 3D models
│       ├── architecture/      # Buildings
│       │   ├── ziggurat_uruk.glb
│       │   ├── ziggurat_anu.glb
│       │   ├── ziggurat_ishtar.glb
│       │   ├── white_temple.glb
│       │   ├── uruk_wall_section.glb
│       │   ├── uruk_gate.glb
│       │   └── royal_palace.glb
│       │
│       ├── characters/        # Character models
│       │   ├── gilgamesh.glb
│       │   ├── enkidu.glb
│       │   ├── enkidu_wild.glb
│       │   ├── ishtar.glb
│       │   ├── shamhat.glb
│       │   ├── utnapishtim.glb
│       │   └── ur_shanabi.glb
│       │
│       └── monsters/          # Monster models
│           ├── humbaba.glb
│           ├── scorpion_man.glb
│           └── bull_of_heaven.glb
│
└── tools/
    ├── blender/               # Blender scripts
    │   ├── ziggurat_uruk.py
    │   ├── gilgamesh_character.py
    │   ├── texgen.py
    │   └── README.md
    │
    └── generate_assets.py      # Asset generation script
```

## 🎯 Priority Order for Asset Creation

### Phase 1: Essential Assets (Required for full experience)
1. **Portraits** (High Priority)
   - gilgamesh.jpg
   - enkidu.jpg
   - ishtar.jpg
   - shamhat.jpg
   - humbaba.jpg
   - utnapishtim.jpg

2. **3D Models** (High Priority)
   - ziggurat_uruk.glb
   - gilgamesh.glb
   - enkidu.glb

3. **Cover Image**
   - cover.jpg

### Phase 2: Enhanced Experience (Recommended)
1. **Remaining Portraits**
   - All historical figures (13 portraits)

2. **3D Models**
   - ziggurat_anu.glb
   - ziggurat_ishtar.glb
   - white_temple.glb
   - uruk_wall_section.glb
   - ishtar.glb
   - shamhat.glb

3. **Music Tracks**
   - All 6 music tracks

### Phase 3: Complete Experience (Optional)
1. **All Remaining 3D Models**
   - All architecture models
   - All character models
   - All monster models

2. **PBR Textures**
   - High-quality textures for all models
   - Normal maps
   - Roughness maps
   - Metallic maps

## 🔧 Using the Makefile

The Makefile has been updated with asset generation commands:

```bash
# Validate the datadisk
make check

# Generate prompts for AI image generation
make prompts

# Generate 3D models (requires Blender)
make models

# Clean generated models
make clean-models

# Generate all assets (prompts + models)
make assets

# Render voices (requires Piper and ffmpeg)
make voices

# Stage for local testing
make stage

# Start local server
make server

# Stop server
make stop

# Clean everything
make clean
```

## 📚 Available Documentation

1. **Historical References**: `research/HISTORICAL_REFERENCES.md`
   - Detailed historical research on costumes and architecture
   - Museum references and academic sources
   - Color palettes and material specifications

2. **3D Model Specifications**: `3D_MODELS.md`
   - Complete specifications for all 3D models
   - Historical accuracy notes
   - Blender modeling guidelines
   - File organization

3. **Blender Scripts Documentation**: `tools/blender/README.md`
   - How to use the Blender scripts
   - Modeling guidelines
   - Historical references for each model

4. **Asset Generation Script**: `tools/generate_assets.py`
   - Generates prompts for all assets
   - Includes portrait, architecture, and cover prompts
   - Music track references

## 🎨 Style Guide

### Portraits
- **Format**: 512x512 pixels, square
- **Background**: Transparent or simple gradient
- **Pose**: Upper body or full figure, 3/4 view
- **Lighting**: Soft, directional (from upper left)
- **Style**: Semi-realistic with stylized elements
- **Line Work**: Clean, defined edges
- **Color**: Rich, earthy tones with selective bright colors

### Architecture Models
- **Scale**: 1 Blender unit = 1 meter
- **Accuracy**: Based on archaeological reconstructions
- **Materials**: Visible texture of mud brick, plaster, stone
- **Weathering**: Slight wear and aging
- **Details**: Architectural features (buttresses, niches, friezes)
- **Lighting**: Natural sunlight with shadows
- **Polycount**: 5,000-50,000 triangles (depending on size)

### Character Models
- **Scale**: Realistic human proportions (Gilgamesh: 2.0m, others: 1.7-1.9m)
- **Proportions**: Mesopotamian artistic conventions
  - Head: Large relative to body (1:6 to 1:7)
  - Eyes: Large, almond-shaped
  - Nose: Straight profile
- **Features**: Exaggerated for important characters
- **Poses**: Static, hierarchical (royalty upright, commoners slightly bent)
- **Polycount**: 10,000-30,000 triangles

## ✅ Validation

After adding new assets, validate them:

```bash
# Validate the entire datadisk
make check

# Or manually
python3 ../ishtaria-protocol/tests/validate_datadisk.py .
```

The validator will check:
- All referenced portrait files exist
- All music files exist (if referenced)
- All model files exist (if referenced)
- File sizes are within limits
- File formats are correct

## 📊 Asset Checklist

Use this checklist to track asset creation:

### Portraits
- [ ] gilgamesh.jpg
- [ ] enkidu.jpg
- [ ] ishtar.jpg
- [ ] shamhat.jpg
- [ ] humbaba.jpg
- [ ] utnapishtim.jpg
- [ ] ur_shanabi.jpg
- [ ] scorpion_man.jpg
- [ ] ninsun.jpg
- [ ] anu.jpg
- [ ] bull_of_heaven.jpg
- [ ] high_priest_anu.jpg
- [ ] high_priestess_ishtar.jpg
- [ ] temple_scribe.jpg
- [ ] royal_guard.jpg
- [ ] uruk_noble.jpg
- [ ] uruk_merchant.jpg
- [ ] potter.jpg
- [ ] weaver.jpg

### Cover Image
- [ ] cover.jpg

### Music Tracks
- [ ] temple.ogg
- [ ] ishtar_shrine.ogg
- [ ] cedar_forest.ogg
- [ ] mountain_echo.ogg
- [ ] waters_of_death.ogg
- [ ] utnapishtim.ogg

### 3D Models - Architecture
- [ ] ziggurat_uruk.glb
- [ ] ziggurat_anu.glb
- [ ] ziggurat_ishtar.glb
- [ ] white_temple.glb
- [ ] uruk_wall_section.glb
- [ ] uruk_gate.glb
- [ ] royal_palace.glb
- [ ] hanging_gardens.glb
- [ ] royal_tombs.glb
- [ ] humbaba_lair.glb
- [ ] scorpion_gate.glb
- [ ] tunnel_of_sun.glb
- [ ] ferry.glb
- [ ] utnapishtim_dwelling.glb

### 3D Models - Characters
- [ ] gilgamesh.glb
- [ ] enkidu.glb
- [ ] enkidu_wild.glb
- [ ] ishtar.glb
- [ ] shamhat.glb
- [ ] utnapishtim.glb
- [ ] ur_shanabi.glb
- [ ] high_priest_anu.glb
- [ ] high_priestess_ishtar.glb

### 3D Models - Monsters
- [ ] humbaba.glb
- [ ] scorpion_man.glb
- [ ] bull_of_heaven.glb

## 📖 Next Steps

1. **Generate Portraits**
   - Use `make prompts` to generate AI prompts
   - Use an AI image generator or create manually
   - Save to `media/portraits/`

2. **Create 3D Models**
   - Run `make models` to generate basic geometry
   - Enhance manually in Blender
   - Export as GLB files
   - Save to `media/models/[category]/`

3. **Add Music**
   - Download appropriate music tracks
   - Convert to OGG format
   - Save to `media/music/`

4. **Create Cover Image**
   - Use the cover prompt
   - Generate or create manually
   - Save to `media/cover/cover.jpg`

5. **Validate**
   - Run `make check`
   - Fix any validation errors

6. **Test**
   - Run `make stage`
   - Run `make server`
   - Test in Ishtaria client

## 🎉 Completion

Once all assets are created and validated:
- The Gilgamesh datadisk will be **production-ready**
- It can be packaged and distributed
- Players will have a fully immersive Mesopotamian experience

**Current Status**: ✅ Structurally complete with placeholders
**Target Status**: 🎯 Fully realized with custom assets

---

For questions or issues, refer to:
- `research/HISTORICAL_REFERENCES.md` - Historical accuracy
- `3D_MODELS.md` - 3D model specifications
- `tools/blender/README.md` - Blender script documentation
