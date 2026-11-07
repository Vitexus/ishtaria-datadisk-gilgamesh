# Gilgamesh Datadisk - Progress Summary

> **Stale (checked 7 November 2026).** The counts below are far behind the disk: it holds
> 402 places, 189 characters, 71 dialogues with 809 player choices, and 11 quests in 69 stages,
> and its portraits are rendered from the real character models rather than placeholders.
> `README.md` and `debian/control` carry the current figures; treat this file as a historical
> note, not as a description of the disk.

## Overview

This document summarizes the progress made on the Gilgamesh datadisk for Ishtaria, including portrait generation, 3D architecture models, and infrastructure setup.

## Completed Tasks

### ✅ Character Portraits (20/20)

**All 20 character portraits have been successfully generated** using InvokeAI with SDXL model.

**Characters:**
1. Gilgamesh - King of Uruk, two-thirds god, one-third man
2. Enkidu - Wild man of the steppe
3. Enkidu (civilized) - After meeting Shamhat
4. Ishtar - Goddess of love and war
5. Shamhat - Temple priestess
6. Humbaba - Guardian of the Cedar Forest
7. Utnapishtim - Survivor of the Great Flood
8. Ur-Shanabi - The ferryman
9. Scorpion Man - Guardian of Mount Mashu
10. Ninsun - Mother of Gilgamesh
11. Anu - Sky god
12. Bull of Heaven - Divine beast
13. High Priest of Anu
14. High Priestess of Ishtar
15. Temple Scribe
16. Royal Guard of Uruk
17. Uruk Noble
18. Uruk Merchant
19. Potter
20. Weaver

**Technical Details:**
- Format: JPEG (512x512, quality 90)
- File sizes: 64-110 KB each
- Model: RealVisXL_V4.0 (SDXL)
- Steps: 20-50
- CFG Scale: 7-10
- Prompts: Historically accurate Mesopotamian descriptions

**Location:** `media/portraits/*.jpg`

**Generation Script:** `tools/invokeai/generate_with_api.py`

---

### ✅ 3D Architecture Models (10/10)

**All 10 Mesopotamian architecture models have been created** using Blender 4.3.2.

**Ziggurats:**
1. ziggurat_simple.glb - Basic 4-tier stepped ziggurat
2. ziggurat_etemenanki.glb - Great Ziggurat of Babylon (7 tiers)
3. ziggurat_complex.glb - Complete complex with temple and courtyard

**Temples & Religious:**
4. temple.glb - Mesopotamian temple building
5. shrine.glb - Small religious shrine with decorative pillars

**Civil Buildings:**
6. palace.glb - Royal palace with throne room and towers
7. residential.glb - Typical Mesopotamian house with courtyard
8. grain_storage.glb - Large grain storage building

**Public Structures:**
9. marketplace.glb - Market with 5 stalls and trading platform
10. city_gate.glb - Ishtar Gate style city gate with towers

**Technical Details:**
- Format: GLTF Binary (.glb)
- Polygons: Low-poly for performance
- Materials: Included (mud brick, limestone, cedar wood, lapis lazuli glaze)
- Sizes: 5m - 40m in dimensions

**Location:** `media/models/architecture/*.glb`

**Generation Scripts:**
- `tools/blender/create_ziggurat.py` - Ziggurats and gates
- `tools/blender/create_mesopotamian_building.py` - Civil buildings

**Documentation:** `media/models/architecture/README.md`

---

### ✅ Infrastructure Setup

1. **InvokeAI REST API**
   - Version: 6.14.0
   - Status: Running at `http://localhost:9090`
   - REST API: Functional
   - Models installed:
     - RealVisXL_V4.0 (SDXL, main model)
     - SDXL_VAE (for VAE encoding/decoding)

2. **Blender MCP Addon**
   - Version: 1.9.1
   - Status: Installed in Blender 4.3.2
   - Location: `/home/vitex/.config/blender/4.3/scripts/addons/mcp_for_blender_addon.py`
   - Note: Requires Blender GUI to run MCP server

3. **Existing Datadisk Structure**
   - Dialogues: 19 character dialogue files
   - NPCs: Historical and epic character definitions
   - Places: Uruk, ziggurats
   - Quests: Epic of Gilgamesh quests
   - Lore: Historical background
   - i18n: English and Czech translations

---

### ✅ Documentation

1. **datadisk.yaml** - Updated with portrait and model references
2. **media/models/architecture/README.md** - Complete model documentation
3. **tools/invokeai/generate_with_api.py** - Production-ready generation script
4. **tools/blender/*.py** - Blender automation scripts

---

## Technical Solutions Implemented

### InvokeAI REST API Integration

The InvokeAI 6.x API uses a node-based workflow system instead of the traditional `/api/v1/generation/text-to-image` endpoint. The solution creates workflow graphs programmatically:

```python
# Workflow includes:
- Model loader (sdxl_model_loader)
- Positive prompt encoding (sdxl_compel_prompt)
- Negative prompt encoding (sdxl_compel_prompt)
- Noise generation
- Latent denoising (denoise_latents)
- Latent-to-image conversion (l2i)
- VAE loader (for SDXL)
- Image saving (save_image)
```

### Blender Automation

Models are created using Blender's Python API (`bpy`) in background mode:

```bash
blender --background --python create_ziggurat.py -- ziggurat_simple output.glb
```

This allows for:
- Programmatic model generation
- Historical accuracy through code
- Reproducible results
- Easy modification and extension

---

## Pending Tasks

### Medium Priority

1. **Additional 3D Models**
   - More variations of ziggurats
   - Other Mesopotamian structures (wells, canals, etc.)
   - Furniture and props
   - Vehicles (chariots, boats)

2. **Model Optimization**
   - Add textures for higher visual quality
   - Create LOD (Level of Detail) versions
   - Optimize polygon counts
   - Add collision meshes

3. **Portrait Enhancement**
   - Generate at higher resolution (1024x1024)
   - Use more diffusion steps (50-100)
   - Experiment with different models
   - Add background transparency

4. **Datadisk Integration**
   - Reference models in place definitions
   - Create scenes using the models
   - Test in-game loading

### Low Priority

1. **Additional Characters**
   - More NPCs (craftsmen, farmers, priests)
   - Animals (lions, bulls, deer)
   - Mythical creatures

2. **Environment Models**
   - Cedar Forest vegetation
   - River models (Euphrates, Tigris)
   - Desert landscape

---

## Files Modified/Created

### Modified
- `datadisk.yaml` - Updated version, description, added model references

### Created
- `media/portraits/*.jpg` (20 files) - Character portraits
- `media/models/architecture/*.glb` (10 files) - 3D architecture models
- `media/models/architecture/README.md` - Model documentation
- `tools/invokeai/generate_with_api.py` - Portrait generation script
- `tools/blender/create_ziggurat.py` - Ziggurat creation script
- `tools/blender/create_mesopotamian_building.py` - Building creation script

---

## Usage Examples

### Generate Portraits

```bash
# Single character
python3 tools/invokeai/generate_with_api.py --single gilgamesh

# All characters
python3 tools/invokeai/generate_with_api.py

# Custom settings
python3 tools/invokeai/generate_with_api.py --single gilgamesh --steps 50 --cfg 10
```

### Create 3D Models

```bash
# Ziggurats
blender --background --python tools/blender/create_ziggurat.py -- ziggurat_simple output.glb
blender --background --python tools/blender/create_ziggurat.py -- ziggurat_etemenanki output.glb

# Buildings
blender --background --python tools/blender/create_mesopotamian_building.py -- palace output.glb
blender --background --python tools/blender/create_mesopotamian_building.py -- marketplace output.glb
```

---

## Validation

All generated assets have been validated:

- ✅ **Portraits**: All 20 files are valid JPEG images, 512x512, 64-110 KB
- ✅ **3D Models**: All 10 files are valid GLB format
- ✅ **Scripts**: All generation scripts work correctly
- ✅ **API**: InvokeAI REST API is functional
- ✅ **Blender**: Blender 4.3.2 with MCP addon installed

---

## Next Steps

1. Test the datadisk in Ishtaria server
2. Create additional 3D models for more variety
3. Enhance portraits with higher quality settings
4. Add textures to 3D models
5. Create scenes and integrate models into gameplay
6. Generate more NPC portraits as needed

---

## References

- **InvokeAI**: https://github.com/invoke-ai/InvokeAI
- **Blender**: https://www.blender.org/
- **Blender MCP**: https://github.com/ahujasid/blender-mcp
- **Epic of Gilgamesh**: Public domain translation by N. K. Sanders
- **Mesopotamian Architecture**: Based on archaeological evidence from Ur, Babylon, Uruk

---

*Last updated: 2026-10-10*
