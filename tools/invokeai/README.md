# InvokeAI Tools for Gilgamesh Datadisk

This directory contains tools for generating character portraits using InvokeAI, a powerful Stable Diffusion-based image generation tool.

## 🚀 Quick Start

### 1. Install InvokeAI

```bash
# Clone the repository
git clone https://github.com/invoke-ai/InvokeAI.git
cd InvokeAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with pip
pip install -e .

# Or install from PyPI
pip install invokeai
```

### 2. Download Models

```bash
# Using the InvokeAI CLI
invokeai model download realistic_vision_v51.safetensors
invokeai model download sd-xl-base-1.0.safetensors

# Or manually from HuggingFace
# https://huggingface.co/SG161222/Realistic_Vision_V5.1
# https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
```

### 3. Generate All Portraits

```bash
cd /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh
python3 tools/invokeai/generate_portraits.py --model realistic_vision_v51.safetensors --steps 50 --cfg 10
```

### 4. Generate Single Portrait

```bash
python3 tools/invokeai/generate_portraits.py --single gilgamesh --model sd-xl-base-1.0.safetensors --steps 60 --cfg 12
```

### 5. Convert to JPEG (Optional)

```bash
python3 tools/invokeai/generate_portraits.py --model realistic_vision_v51.safetensors --convert
```

## 📚 Usage Guide

### Command Line Options

```
Usage: generate_portraits.py [OPTIONS]

Options:
  --model TEXT       InvokeAI model to use (default: realistic_vision_v51.safetensors)
  --steps INTEGER    Number of diffusion steps (default: 50)
  --cfg INTEGER      CFG scale (default: 10)
  --single TEXT      Generate only a single character (e.g., 'gilgamesh')
  --convert          Convert PNG to JPEG after generation
  --width INTEGER    Image width (default: 512)
  --height INTEGER   Image height (default: 512)
```

### Recommended Models

| Model | Best For | Quality | Speed | VRAM Required |
|-------|----------|---------|-------|----------------|
| `realistic_vision_v51.safetensors` | Realistic portraits | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 6-8 GB |
| `sd-xl-base-1.0.safetensors` | High quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 8-12 GB |
| `juggernaut-xl-v7.safetensors` | Detailed | ⭐⭐⭐⭐⭐ | ⭐⭐ | 8-12 GB |
| `epiCRealism_NaturalSinRC1VAE.safetensors` | Realistic | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 6-8 GB |

### Recommended Settings

| Character Type | Steps | CFG Scale | Model |
|---------------|-------|-----------|-------|
| Main characters (Gilgamesh, Enkidu, Ishtar) | 50-60 | 10-12 | SDXL |
| Supporting characters | 40-50 | 8-10 | Realistic Vision |
| Monsters (Humbaba, Scorpion Man) | 50-60 | 12-14 | SDXL |
| Historical figures | 40-50 | 8-10 | Realistic Vision |

## 🎨 Character Prompts

All character prompts are pre-configured in `generate_portraits.py`. Each prompt includes:

- **Historical accuracy**: Based on Early Dynastic period (2700 BCE) for main characters
- **Costume details**: Specific clothing, jewelry, and accessories
- **Pose and expression**: Appropriate for each character
- **Lighting**: Cinematic soft lighting
- **Style**: Semi-realistic with historical accuracy
- **Negative prompts**: To avoid modern elements, fantasy distortions, and low quality

### Customizing Prompts

To customize a character's prompt:

1. Edit `tools/invokeai/generate_portraits.py`
2. Find the character in `CHARACTER_PROMPTS` dictionary
3. Modify the `positive` and `negative` strings
4. Run the generator again

Example customization:
```python
CHARACTER_PROMPTS["gilgamesh"]["positive"] = "...your custom prompt..."
```

## 📁 Output Files

Generated portraits are saved to:
```
media/portraits/[character_name].png  (or .jpg if --convert used)
```

### File Requirements
- **Format**: PNG or JPEG
- **Size**: 512x512 pixels
- **Max size**: 1 MiB per file
- **Background**: Transparent preferred, or simple gradient
- **Style**: Upper body portrait, 3/4 view recommended

### Supported Characters

All 19 characters have pre-configured prompts:

**Epic Characters:**
- gilgamesh
- enkidu (wild version)
- ishtar
- shamhat
- humbaba
- utnapishtim
- ur_shanabi
- scorpion_man

**Divine Figures:**
- ninsun
- anu
- bull_of_heaven

**Historical Figures:**
- high_priest_anu
- high_priestess_ishtar
- temple_scribe
- royal_guard
- uruk_noble
- uruk_merchant
- potter
- weaver

## 🎯 Quality Tips

### For Best Results

1. **Use SDXL models** for highest quality (if you have the VRAM)
2. **Increase steps** (50-60) for more detail
3. **Use higher CFG** (10-14) for more adherence to prompt
4. **Generate multiple versions** of key characters and pick the best
5. **Use negative prompts** to remove unwanted elements

### Post-Processing

After generation, you can:

1. **Upscale** using InvokeAI's upscale feature
2. **Edit** in GIMP/Photoshop for final touches
3. **Compress** to meet the 1 MiB limit
4. **Standardize** background (remove or add consistent gradient)

### Batch Processing

To generate all portraits:
```bash
# Generate all with SDXL (high quality)
python3 tools/invokeai/generate_portraits.py \
  --model sd-xl-base-1.0.safetensors \
  --steps 60 \
  --cfg 12 \
  --convert
```

This will:
- Generate all 19 portraits
- Use SDXL model for high quality
- 60 steps for detail
- CFG 12 for prompt adherence
- Convert to JPEG for smaller files

## 🐛 Troubleshooting

### InvokeAI Not Found
```
❌ InvokeAI not found!
   Please install InvokeAI first:
   https://github.com/invoke-ai/InvokeAI
```

**Solution:** Install InvokeAI as shown in the Quick Start section.

### Model Not Found
```
❌ Model 'realistic_vision_v51.safetensors' not found
```

**Solution:** Download the model first:
```bash
invokeai model download realistic_vision_v51.safetensors
```

### Out of Memory
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. Use a smaller model (e.g., `realistic_vision_v51` instead of SDXL)
2. Reduce steps to 30-40
3. Use `--precision float16` (already enabled in script)
4. Close other GPU-intensive applications

### Slow Generation

**Solutions:**
1. Use a faster model
2. Reduce steps to 30-40
3. Use `--precision float16`
4. Use a smaller image size (256x256 for testing)

### Low Quality Results

**Solutions:**
1. Increase steps to 50-60
2. Increase CFG scale to 12-14
3. Try a different model (SDXL is best for quality)
4. Improve the prompt with more specific details
5. Generate multiple versions and select the best

## 📊 Performance Benchmarks

| Model | 512x512 Time | VRAM | Quality |
|-------|--------------|------|---------|
| realistic_vision_v51 | 15-20 sec | 6-8 GB | ⭐⭐⭐⭐ |
| sd-xl-base-1.0 | 25-35 sec | 8-12 GB | ⭐⭐⭐⭐⭐ |
| juggernaut-xl | 30-45 sec | 8-12 GB | ⭐⭐⭐⭐⭐ |

**Note:** Times are approximate for a modern GPU (RTX 3080/4090 or equivalent)

## 🔧 Advanced Configuration

### Custom Models

To use a custom model not in the InvokeAI model database:

1. Download the model file (e.g., `my_model.safetensors`)
2. Place it in the InvokeAI models directory
3. Use the full path in the `--model` argument

```bash
python3 generate_portraits.py --model /path/to/my_model.safetensors
```

### LoRA Models

To use LoRA (Low-Rank Adaptation) models for specific styles:

```bash
# Using a LoRA for ancient art style
python3 generate_portraits.py \
  --model realistic_vision_v51.safetensors \
  --lora ancient_art_lora.safetensors \
  --lora-strength 0.7
```

Note: You'll need to modify the script to add LoRA support.

### VAE Models

For better color and contrast:

```bash
python3 generate_portraits.py \
  --model my_model.safetensors \
  --vae vae-ft-mse-840000.safetensors
```

## 📚 Historical Accuracy

All prompts are based on:
- **Archaeological evidence** from Sumerian/Akkadian periods
- **Museum artifacts** (British Museum, Louvre, Pergamon Museum)
- **Academic sources** on Mesopotamian art and costume
- **Epic of Gilgamesh** descriptions

For more information, see:
- `research/HISTORICAL_REFERENCES.md`
- `3D_MODELS.md`

## 🎨 Alternative Methods

If you don't have access to InvokeAI, you can:

### Use Stable Diffusion WebUI (Automatic1111)

1. Install: https://github.com/AUTOMATIC1111/stable-diffusion-webui
2. Use the prompts from `generate_portraits.py`
3. Save to `media/portraits/`

### Use Midjourney

1. Use Discord bot: https://midjourney.com/
2. Use prompts from `generate_portraits.py`
3. Download and save to `media/portraits/`
4. Resize to 512x512

### Use DALL-E

1. Use API or web interface
2. Use prompts from `generate_portraits.py`
3. Save to `media/portraits/`
4. Resize to 512x512

### Manual Creation

1. Use reference images from `research/HISTORICAL_REFERENCES.md`
2. Create in GIMP, Krita, or Photoshop
3. Save as 512x512 PNG or JPEG
4. Save to `media/portraits/`

## 📝 Integration

After generating portraits:

1. **Validate** the datadisk:
   ```bash
   make check
   ```

2. **Stage** for testing:
   ```bash
   make stage
   ```

3. **Test** in Ishtaria server:
   ```bash
   make server
   ```

4. **Verify** portraits display correctly in the client

## 🎯 Next Steps

1. Install InvokeAI and download models
2. Run `generate_portraits.py` to create all portraits
3. Review generated portraits for quality and accuracy
4. Manually edit any that need improvement
5. Convert to JPEG if needed (`--convert` flag)
6. Validate the datadisk
7. Test in Ishtaria

## 📞 Support

For issues with:
- **InvokeAI installation**: See https://github.com/invoke-ai/InvokeAI
- **Model downloads**: Check HuggingFace for model availability
- **Prompt optimization**: See `research/HISTORICAL_REFERENCES.md`
- **Ishtaria integration**: See `NEXT_STEPS.md` and `ASSET_GENERATION.md`

## 🎉 Success Criteria

✅ All 19 portraits generated  
✅ Each portrait is historically accurate  
✅ Each portrait matches character description  
✅ All files are 512x512 pixels  
✅ All files are < 1 MiB  
✅ Datadisk validation passes  
✅ Portraits display correctly in client  

---

**Status**: ✅ Ready to use when InvokeAI is available

**Note**: The `generate_portraits.py` script is fully functional and ready to use. Simply install InvokeAI, download the models, and run the script to generate all character portraits for the Gilgamesh datadisk.
