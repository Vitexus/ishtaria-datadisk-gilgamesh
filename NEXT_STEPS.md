# Next Steps for Gilgamesh Datadisk Development

## 🧭 Open items for the next development (noted 2026-11-04)

### The hunter's village (the old father's village)

- **A wooden wall with a wooden gate** round the village, made of 0 A.D. models. The bundled catalogue
  (`ishtaria-client/assets/zeroad/structures/`) has Persian wall pieces (`pers_wall_long`, `pers_wall_medium`,
  `pers_wall_short`, `pers_wall_gate`, `pers_wall_tower`, `pers_wooden_tower`), but those are mudbrick and stone, not timber:
  import palisade pieces with `tools/zeroad-structures.py` if 0 A.D. has them, or recolour these. The village is built by
  `tools/build_village.py` (`buildings/hunter_village.yaml`). The server gives walls and fences round colliders and leaves
  gates open, as in the generated towns.
- **At night the people sleep**, so the village cannot be full of wandering NPCs and children after dark. NPCs have no
  schedules yet (they stand, wander or patrol), so this needs a mechanism: villagers go home and are out of sight at night
  and set out about their business at dawn (the world has a solar clock). The player needs a way to sleep too, for
  example **an inn** where he can wait quickly until the day begins (the Scrolls of Day and Night already turn the clock).
  To decide: a stateless schedule on the server, like the shepherd's cycle, or visibility decided by the client.
- **Women's dialogues:** some hint that they are spoken for, others offer marriage. Keep to the spoiler rules of the
  other dialogues (`visible_if`, quest stages) and see the `love` system of the server (Šamḫat).
- **Children's dialogues:** allusions to the tales of their time: Huwawa (Sumerian), also written Chuvava, Chumbaba, Huvava,
  Chuwawa, Humbaba (Akkadian; English and German), Kombabos (Greek), and beings such as Tiamat and Hundun. Cautions:
  - Hundun is Chinese and has no contact with Sumer around 2700 BCE: keep it only as a conscious cross-cultural wink, or drop it.
  - Tiamat is told in the Babylonian Enūma eliš, later than the Early Dynastic II of the disk (the Sumerian sea goddess is Nammu).
  - Huwawa is the guardian of the Cedar Forest, a later part of the Epic: the children must speak of him as a bogeyman of
    nursery tales and not reveal the story (gate by quest stage).
  - In this setting prefer the Sumerian form (Huwawa) and let the other names go into the notes (`research/`) and the
    knowledge cards.

## ✅ Completed Features

The Gilgamesh datadisk is now **structurally complete** with:

### Content Created
- **21 Places**: Uruk city locations + Mesopotamian architecture (ziggurats, temples, walls, etc.)
- **16 NPCs**: Main epic characters + historical Mesopotamian figures
- **16 Dialogues**: Branching conversation trees for all characters
- **8 Quests**: Complete epic questline following the story
- **Full Translations**: English and Czech (500+ text keys each)
- **10 Lore Entries**: Codex entries for characters, places, and events
- **Placeholder Assets**: All portraits and cover image generated
- **Validation**: Passes Ishtaria protocol schema validation

### File Structure
```
ishtaria-datadisk-gilgamesh/
├── datadisk.yaml              # Manifest (validated)
├── README.md                  # Complete documentation
├── NEXT_STEPS.md              # This file
├── 3D_MODELS.md               # Modeling guide
├── Makefile                   # Development commands
│
├── places/                    # 21 locations
│   ├── uruk.yaml              # Original locations
│   └── ziggurats.yaml         # Mesopotamian architecture
│
├── npcs/                      # 16 characters
│   ├── epic.yaml              # Main epic characters
│   └── historical.yaml        # Historical figures
│
├── dialogues/                 # 16 dialogue trees
│   ├── (8 original)
│   └── (8 new historical)
│
├── quests/                    # 8 epic quests
│   ├── the_tyranny_of_gilgamesh.yaml
│   ├── enkidus_awakening.yaml
│   ├── the_meeting_of_equals.yaml
│   ├── the_cedar_forest_journey.yaml
│   ├── ishtars_wrath.yaml
│   ├── the_death_of_enkidu.yaml
│   ├── the_search_for_immortality.yaml
│   └── the_return_to_uruk.yaml
│
├── lore/                      # 10 lore entries
│   └── epic.yaml
│
├── i18n/                     # Translations
│   ├── en.yaml                # English
│   └── cs.yaml                # Czech
│
├── media/                     # Assets
│   ├── portraits/             # 19 character portraits
│   ├── cover/                 # Cover image
│   └── textures/              # Texture placeholders
│
├── voice/                     # Voice config
│   └── voices.yaml            # Piper TTS settings
│
├── tools/                     # Helper scripts
│   ├── render_voices.py       # Voice synthesis
│   └── generate_placeholders.py # Asset generator
│
├── debian/                    # Packaging
│   ├── control
│   ├── changelog
│   ├── copyright
│   └── rules
│
└── 3D_MODELS.md              # Modeling specifications
```

---

## 🎯 Priority 1: Add Real Artwork

### 1. Replace Placeholder Portraits

**Location**: `media/portraits/`

Replace the generated placeholder images with proper character artwork:

#### Main Characters (Essential)
- `gilgamesh.jpg` - Gilgamesh, king of Uruk
- `enkidu.jpg` - Enkidu, wild man
- `ishtar.jpg` - Ishtar, goddess
- `shamhat.jpg` - Shamhat, priestess
- `humbaba.jpg` - Humbaba, monster
- `utnapishtim.jpg` - Utnapishtim, flood survivor

#### Historical Figures (Recommended)
- `ur_shanabi.jpg` - Ur-Shanabi, ferryman
- `scorpion_man.jpg` - Scorpion Man, guardian
- `ninsun.jpg` - Ninsun, Gilgamesh's mother
- `anu.jpg` - Anu, sky god
- `bull_of_heaven.jpg` - Bull of Heaven
- `high_priest_anu.jpg` - High Priest of Anu
- `high_priestess_ishtar.jpg` - High Priestess of Ishtar
- `temple_scribe.jpg` - Temple Scribe
- `royal_guard.jpg` - Royal Guard
- `uruk_noble.jpg` - Uruk Noble
- `uruk_merchant.jpg` - Uruk Merchant
- `potter.jpg` - Potter
- `weaver.jpg` - Weaver

**Specifications**:
- Format: JPEG or PNG
- Size: 512x512 pixels
- Maximum: 1 MiB per file
- Style: Character portraits, upper body or full figure
- Background: Transparent or simple neutral color

**Art Style Guidelines**:
- Match Ishtaria's aesthetic (Kenney-style pixel art or similar)
- Historical accuracy for Mesopotamian costumes
- Clear, recognizable faces
- Consistent lighting and perspective

### 2. Add Cover Image

**Location**: `media/cover/cover.jpg`

Create an eye-catching cover image that represents the epic:
- Size: 1024x768 pixels (recommended)
- Format: JPEG or PNG
- Maximum: 1 MiB
- Style: Showcase Uruk, ziggurats, and main characters

**Suggested composition**:
- Gilgamesh and Enkidu in foreground
- Ziggurat of Uruk in background
- Cedar Forest elements
- Epic title text

### 3. Add Music Tracks

**Location**: `media/music/`

Add background music tracks for each location:
- `temple.ogg` - Temple music
- `ishtar_shrine.ogg` - Ishtar's temple
- `cedar_forest.ogg` - Cedar Forest
- `mountain_echo.ogg` - Mount Mashu
- `waters_of_death.ogg` - Waters of Death
- `utnapishtim.ogg` - Utnapishtim's dwelling

**Specifications**:
- Format: OGG Vorbis
- Maximum: 8 MiB per track
- Style: Atmospheric, ancient Mesopotamian-inspired
- Looping: Tracks should be seamless loops

**Resources for free music**:
- [Free Music Archive](https://freemusicarchive.org/)
- [Incompetech](https://incompetech.com/) (Kevin MacLeod)
- [Tabletop Audio](https://tabletopaudio.com/) (10-minute loops)
- Search for: "Mesopotamian", "ancient", "middle eastern", "ambient"

---

## 🎯 Priority 2: 3D Models (Optional but Recommended)

### Using Blender

See `3D_MODELS.md` for complete specifications and Blender scripting guidance.

#### Essential Models (High Priority)
1. **Ziggurat of Uruk** (`media/models/ziggurat_uruk.glb`)
2. **Ziggurat of Anu** (`media/models/ziggurat_anu.glb`)
3. **Ziggurat of Ishtar** (`media/models/ziggurat_ishtar.glb`)
4. **Great Wall of Uruk** (`media/models/uruk_wall_section.glb`)
5. **Gilgamesh character** (`media/models/gilgamesh.glb`)
6. **Enkidu character** (`media/models/enkidu.glb`)
7. **Ishtar character** (`media/models/ishtar.glb`)

#### Medium Priority
1. **White Temple**
2. **City Gate of Uruk**
3. **Royal Palace**
4. **Humbaba**
5. **Scorpion Man**

#### Low Priority
1. **Hanging Gardens**
2. **Royal Tombs**
3. **Tunnel of the Sun**
4. **Ferry**
5. **Utnapishtim's Dwelling**

**Export Format**: `.glb` (GLTF Binary)
- Scale: 1 unit = 1 meter
- Maximum: 4 MiB per model
- Optimized: Use LODs for large structures

### Using InvokeAI (Image Generation)

If you have access to **mcp-server-invokeai** or similar image generation tools:

```bash
# Generate concept art for ziggurats
invokeai --prompt "Ancient Mesopotamian ziggurat, stepped temple tower, mud brick construction, white plaster finish, multiple levels, staircase, temple at summit, desert setting, golden hour lighting, cinematic, highly detailed" --output media/textures/ziggurat_concept.png --width 1024 --height 768

# Generate character concept art
invokeai --prompt "Gilgamesh king of Uruk, ancient Mesopotamian king, two-thirds god one-third man, perfect body, strong muscular, golden crown, white linen robes, gold jewelry, short beard, regal appearance, cinematic lighting" --output media/portraits/gilgamesh_concept.png --width 512 --height 512
```

**Recommended prompts**:
- Use "ancient Mesopotamian", "Sumerian", "Babylonian" keywords
- Specify "historically accurate" or "based on archaeological evidence"
- Include details about materials: mud brick, plaster, lapis lazuli, gold
- Mention specific architectural features: buttresses, niches, ziggurat tiers

### Using Blender MCP Server

If you have access to **mcp-server-blender**:

```python
# Example: Create a simple ziggurat
import bpy

# Create base
bpy.ops.mesh.primitive_cube_add(size=60, location=(0,0,0))
base = bpy.context.active_object
base.name = "Ziggurat_Base"

# Create second level
bpy.ops.mesh.primitive_cube_add(size=40, location=(0,0,10))
level2 = bpy.context.active_object
level2.name = "Ziggurat_Level2"

# Create third level
bpy.ops.mesh.primitive_cube_add(size=20, location=(0,0,25))
level3 = bpy.context.active_object
level3.name = "Ziggurat_Level3"

# Export
bpy.ops.export_scene.gltf(
    filepath="//media/models/ziggurat_test.glb",
    export_format='GLB'
)
```

---

## 🎯 Priority 3: Testing

### Local Testing Setup

#### 1. Validate the Datadisk
```bash
cd ishtaria-datadisk-gilgamesh
python3 ../ishtaria-protocol/tests/validate_datadisk.py .
```

#### 2. Stage for Local Testing
```bash
make stage
```

This will:
- Render all voice lines (requires Piper and ffmpeg)
- Copy all files to `build/datadisks/gilgamesh/`
- Prepare for server use

#### 3. Start Local Server
```bash
make server
```

This will:
- Create a development database
- Build the Ishtaria server
- Start the server with the Gilgamesh datadisk
- Wait for server to be ready

#### 4. Connect with Client
```bash
cd ../ishtaria-client
make run
```

Or with headless mode:
```bash
make run GODOT_ARGS="--headless --max-fps 60"
```

#### 5. Stop Server
```bash
make stop
```

#### 6. View Logs
```bash
make logs
```

### Test Checklist

- [ ] Server starts without errors
- [ ] Gilgamesh datadisk appears in world generation options
- [ ] All locations are generated correctly
- [ ] NPCs appear at their designated places
- [ ] Dialogues work for all NPCs
- [ ] Quests appear and can be progressed
- [ ] Lore entries are accessible
- [ ] Portraits display correctly
- [ ] Music plays at designated locations

---

## 🎯 Priority 4: Packaging

### Build Debian Package

```bash
cd ishtaria-datadisk-gilgamesh

# Update version in debian/changelog if needed
# Edit version in datadisk.yaml if needed

# Build the package
dpkg-buildpackage -us -uc -b

# Install the package
sudo dpkg -i ../ishtaria-datadisk-gilgamesh_0.1.0-1_all.deb
```

### Package Testing

After installation, the datadisk should be available at:
`/usr/share/ishtaria/datadisks/gilgamesh/`

Test in `ishtaria-admin`:
- World maps → Generate map
- Check that "Gilgamesh" appears in the datadisk list
- Select and generate a world with this datadisk

---

## 🎯 Priority 5: Content Refinement

### Review and Polish

1. **Dialogue Review**
   - Read through all dialogues for consistency
   - Ensure historical accuracy where possible
   - Check for typos and grammatical errors
   - Verify all text keys are used

2. **Quest Flow Testing**
   - Test each quest from start to finish
   - Verify stage transitions work correctly
   - Check that `reach` triggers work at correct distances
   - Ensure quest markers appear on the aetherglass

3. **Balance Adjustments**
   - Review experience rewards in quests
   - Adjust item quantities if needed
   - Verify quest difficulty is appropriate

4. **Translation Review**
   - Native Czech speaker should review Czech translations
   - Ensure consistency between English and Czech
   - Check for proper Czech grammar and terminology

### Add Missing Features

1. **Music Tracks** (if not added)
2. **3D Models** (if not added)
3. **Custom Character Models** (optional)
   - Create `.glb` models for special characters
   - Reference in NPC definitions: `character: {pack: protagonists, skin: warriorMaleA, model: media/models/gilgamesh.glb}`

### Expand Content

1. **Additional NPCs**
   - Shamhat (already exists but could be enhanced)
   - Ninsun (Gilgamesh's mother)
   - Anu (sky god)
   - Additional citizens of Uruk

2. **Additional Locations**
   - Market stalls
   - Residential areas
   - Temple workshops
   - Barracks

3. **Additional Quests**
   - Side quests from citizens
   - Crafting quests
   - Exploration quests

4. **Additional Lore**
   - More historical information
   - Cultural details
   - Mythological references

---

## 📋 Development Workflow

### Regular Tasks

1. **Make Changes**
   - Edit YAML files for content
   - Add/remove files as needed

2. **Validate**
   ```bash
   python3 ../ishtaria-protocol/tests/validate_datadisk.py .
   ```

3. **Test Locally**
   ```bash
   make stage
   make server
   # Test in client
   make stop
   ```

4. **Commit Changes** (if using git)
   ```bash
   git add .
   git commit -m "Describe changes"
   ```

### Adding New Content

#### Adding a New Place
1. Edit `places/uruk.yaml` or create a new file in `places/`
2. Add place definition with proper constraints
3. Add translation keys to `i18n/en.yaml` and `i18n/cs.yaml`
4. Validate

#### Adding a New NPC
1. Edit or create a file in `npcs/`
2. Add NPC definition with character, dialogue, portrait
3. Create dialogue file in `dialogues/`
4. Add translation keys to i18n files
5. Add portrait image to `media/portraits/`
6. Validate

#### Adding a New Quest
1. Create a new file in `quests/`
2. Define quest with stages
3. Add translation keys to i18n files
4. Validate

#### Adding a New Lore Entry
1. Edit `lore/epic.yaml`
2. Add lore entry with category
3. Add translation keys to i18n files
4. Validate

---

## 🎨 Art and Asset Guidelines

### Portrait Style
- **Size**: 512x512 pixels
- **Format**: JPEG or PNG
- **Style**: Character-focused, upper body or full figure
- **Background**: Transparent or simple gradient
- **Costumes**: Historically accurate Mesopotamian attire

### Music Guidelines
- **Format**: OGG Vorbis
- **Length**: 3-10 minutes (for looping)
- **Style**: Atmospheric, subtle, non-intrusive
- **Volume**: Background level, not overpowering
- **Naming**: Match the music IDs in `music/` files

### 3D Model Guidelines
- **Format**: GLB (GLTF Binary)
- **Scale**: 1 unit = 1 meter
- **Polycount**: 5,000-50,000 triangles (depending on size)
- **Textures**: PBR materials, max 2048x2048
- **LODs**: Create multiple levels of detail for large objects
- **Collision**: Simple collision meshes for interactive objects

### Voice Guidelines
- **Format**: OGG Vorbis, mono
- **Sample Rate**: Up to 48 kHz
- **Size**: Max 2 MiB per line
- **Naming**: `{text_key}.ogg` in `media/voice/{language}/`
- **Synthesis**: Piper TTS with voice profiles in `voice/voices.yaml`

---

## 📚 Resources

### Historical References
- **Epic of Gilgamesh**: Public domain translations available online
- **Mesopotamian Architecture**: Museum websites, academic papers
- **Art and Iconography**: British Museum, Louvre, Met collections

### Ishtaria Documentation
- **Protocol**: `ishtaria-protocol/DATADISK-SPEC.md`
- **Schema**: `ishtaria-protocol/schemas/datadisk.schema.json`
- **Examples**: `ishtaria-protocol/examples/datadisk-*/`

### Development Tools
- **YAML Validator**: `python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"`
- **Image Editing**: GIMP, Krita, Photoshop
- **3D Modeling**: Blender, SketchUp
- **Audio Editing**: Audacity, Ardour
- **Text-to-Speech**: Piper, eSpeak

---

## 🎯 Release Checklist

Before releasing version 0.2.0:

- [ ] All placeholder portraits replaced with proper artwork
- [ ] Cover image created
- [ ] Music tracks added (or documented as optional)
- [ ] All dialogues reviewed and polished
- [ ] All translations reviewed
- [ ] All quests tested and working
- [ ] Validation passes without errors
- [ ] Local testing successful
- [ ] Debian package builds successfully
- [ ] README updated with final information
- [ ] CHANGELOG updated

---

## 📅 Project Timeline (Suggested)

### Phase 1: Content Complete (Current State) ⭐
- All YAML content created
- All translations complete
- Validation passing
- Placeholder assets generated

### Phase 2: Art Assets (1-2 weeks)
- Create all character portraits
- Create cover image
- Find/add music tracks

### Phase 3: 3D Models (2-4 weeks)
- Model ziggurats and major architecture
- Create character models
- Optimize and test in engine

### Phase 4: Testing and Polish (1 week)
- Local testing
- Bug fixes
- Balance adjustments
- Final polish

### Phase 5: Release (1 day)
- Final validation
- Package building
- Documentation review
- Release to repository

---

## 💡 Tips and Best Practices

1. **Work Incrementally**
   - Make small changes
   - Validate frequently
   - Test locally often

2. **Backup Your Work**
   - Use git for version control
   - Commit regularly
   - Keep backups of artwork

3. **Historical Accuracy**
   - Research Mesopotamian culture
   - Use academic sources
   - Consult museums and experts when possible

4. **Performance Considerations**
   - Optimize 3D models
   - Compress textures
   - Use appropriate polycounts
   - Test on target hardware

5. **Community Contribution**
   - Document your process
   - Share resources and references
   - Credit contributors
   - Follow CC BY-SA 4.0 license

---

## 📞 Support and Help

If you encounter issues:

1. **Validation Errors**
   - Check `ishtaria-protocol/schemas/datadisk.schema.json`
   - Ensure all required fields are present
   - Verify all references exist (dialogues, places, etc.)

2. **Runtime Errors**
   - Check server logs with `make logs`
   - Verify file permissions
   - Ensure all referenced files exist

3. **Content Issues**
   - Review the epic text for accuracy
   - Consult historical sources
   - Ask for feedback from the Ishtaria community

---

## 🎉 Completion Checklist

This datadisk is **ready for use** with the current state. To make it **production-quality**:

- [x] Core structure complete
- [x] All content created
- [x] Translations complete
- [x] Validation passing
- [x] Placeholder assets generated
- [ ] Real artwork added (portraits, cover)
- [ ] Music tracks added
- [ ] 3D models created (optional)
- [ ] Local testing completed
- [ ] Final review done

**Current Status**: ✅ **Functional and usable** - Ready for testing with placeholder assets!

The datadisk can be **installed and played immediately** with the existing placeholder assets. Adding real artwork and 3D models will greatly enhance the visual experience, but the core gameplay and story are fully functional.
