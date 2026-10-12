# InvokeAI API Fix for Gilgamesh Datadisk

The error you're seeing (`405 Method Not Allowed`) indicates that the **InvokeAI REST API is not enabled** in your running instance.

## 🚨 The Problem

Your InvokeAI is running at `http://localhost:9090` but it's serving the **Web UI only**, not the REST API. This happens when:

1. You started InvokeAI **without** the `--enable-rest-api` flag
2. You're using a newer version of InvokeAI (3.x+) where REST API is disabled by default
3. The REST API is not properly configured

## ✅ Solution 1: Restart InvokeAI with REST API Enabled (Recommended)

### Stop your current InvokeAI instance:
```bash
pkill -f invokeai
# or
sudo lsof -i :9090 | grep invokeai
kill <PID>
```

### Restart with REST API enabled:
```bash
# For InvokeAI 3.x+
invokeai --host 0.0.0.0 --port 9090 --enable-rest-api

# Or with all options
invokeai --host 0.0.0.0 --port 9090 --enable-rest-api --enable-websockets
```

### Then try the generation again:
```bash
cd /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh
make portraits-all
```

---

## ✅ Solution 2: Use the Web UI Directly

Since your InvokeAI Web UI is running, you can use it manually:

### Open the Web UI:
- Go to: http://localhost:9090

### Generate each portrait:
1. Open InvokeAI Web UI in your browser
2. Select model: `sd-xl-base-1.0` or `realistic_vision_v51`
3. Paste one of these prompts (from the scripts):

**Gilgamesh:**
```
Mesopotamian king of Uruk, Early Dynastic period 2700 BCE, two-thirds god one-third man, golden diadem crown with lapis lazuli inlays, white linen tunic with gold embroidery, kaunakes sheep-fleece skirt, wide leather belt with gold buckle, gold-decorated sandals, gold necklace bracelets signet ring, short well-kept hair, short curled beard, sword at belt, regal heroic pose, proud commanding expression, cinematic soft lighting from upper left
Negative: blurry, low resolution, modern clothing, fantasy elements not in epic, cartoon, anime, realistic photography, watermark, text, extra limbs, deformities
```

4. Set parameters:
   - Width: 512
   - Height: 512
   - Steps: 60
   - CFG Scale: 12

5. Generate and save as `gilgamesh.png` to `media/portraits/`

6. Repeat for all 19 characters

### All Prompts Available:
See `tools/invokeai/generate_portraits.py` for all character prompts

---

## ✅ Solution 3: Use the InvokeAI CLI (No Web UI Needed)

If you don't want to use the Web UI, install the CLI:

### Install InvokeAI CLI:
```bash
pip install invokeai
```

### Download models:
```bash
invokeai model download sd-xl-base-1.0.safetensors
invokeai model download realistic_vision_v51.safetensors
```

### Run CLI generation:
```bash
cd /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh
make portraits-invokeai
```

This will use the CLI instead of the API.

---

## 🔍 How to Verify REST API is Working

### Test the API:
```bash
curl http://localhost:9090/api/v1/models
```

**Expected JSON response:**
```json
{
  "models": [
    {"name": "sd-xl-base-1.0.safetensors", ...},
    {"name": "realistic_vision_v51.safetensors", ...}
  ]
}
```

**If you get HTML:** REST API is NOT enabled

---

## 📋 InvokeAI Startup Commands

| Command | Purpose |
|---------|---------|
| `invokeai --host 0.0.0.0 --port 9090` | Web UI only (current issue) |
| `invokeai --host 0.0.0.0 --port 9090 --enable-rest-api` | Web UI + REST API ✅ |
| `invokeai --host 0.0.0.0 --port 9090 --enable-websockets` | Web UI + WebSocket API ✅ |
| `invokeai --host 0.0.0.0 --port 9090 --enable-rest-api --enable-websockets` | Full API support ✅ |

### For Docker:
```bash
docker run -it --gpus=all --rm -p 9090:9090 \
  -e INVOKEAI_ENABLE_REST_API=true \
  -v $HOME/.invokeai:/root/.invokeai \
  invokeai/invokeai:latest
```

---

## 🎯 Quick Fix for Your Current Situation

Since you already have InvokeAI running at `localhost:9090`, the **fastest solution** is:

### Step 1: Stop current instance
```bash
pkill -f invokeai
```

### Step 2: Restart with REST API
```bash
invokeai --host 0.0.0.0 --port 9090 --enable-rest-api
```

### Step 3: Wait for startup (~30-60 seconds)

### Step 4: Run generation
```bash
cd /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh
make portraits-all
```

---

## 📚 Available Resources

- **Full API Documentation**: https://github.com/invoke-ai/InvokeAI/blob/main/invokeai/api/openapi.yaml
- **InvokeAI GitHub**: https://github.com/invoke-ai/InvokeAI
- **REST API Guide**: https://github.com/invoke-ai/InvokeAI/wiki/REST-API
- **Configuration**: https://github.com/invoke-ai/InvokeAI/wiki/Configuration

---

## 💡 Alternative: Use Stable Diffusion WebUI

If you prefer Automatic1111's Stable Diffusion WebUI:

### Install:
```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui
pip install -r requirements.txt
```

### Start:
```bash
./webui.sh --api
```

### Use API:
```bash
# This will work with the correct endpoints
curl -X POST http://localhost:7860/sdapi/v1/txt2img \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test","negative_prompt":"","steps":20}'
```

---

## 🎨 Manual Generation via Web UI

If you want to stay with your current InvokeAI Web UI:

1. **Open**: http://localhost:9090
2. **Generate** each portrait using the prompts from `tools/invokeai/generate_portraits.py`
3. **Save** to `media/portraits/[character].jpg`

### Recommended workflow:
```bash
# Open the prompts file
less /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh/tools/invokeai/generate_portraits.py

# Copy each character's prompt and use in Web UI
```

---

## ✅ Success Criteria

After fixing:
- [ ] `curl http://localhost:9090/api/v1/models` returns **JSON** (not HTML)
- [ ] `make portraits-all` works without errors
- [ ] Portraits appear in `media/portraits/`
- [ ] `make check` passes validation

---

## 📞 Need More Help?

### Check your InvokeAI version:
```bash
invokeai --version
# or
curl http://localhost:9090/api/version
```

### Common versions:
- **InvokeAI 2.x**: REST API enabled by default
- **InvokeAI 3.x+**: REST API disabled by default (needs `--enable-rest-api`)

### View logs:
```bash
# Find InvokeAI process
ps aux | grep invokeai

# View logs (if started in terminal)
# Or check system logs
journalctl -u invokeai 2>/dev/null || echo "Not a system service"
```

---

## 🎉 Summary

**The issue:** REST API is disabled in your InvokeAI instance   
**The fix:** Restart with `--enable-rest-api` flag   
**The result:** Generation will work perfectly   

**Quick command:**
```bash
pkill -f invokeai && sleep 5 && invokeai --host 0.0.0.0 --port 9090 --enable-rest-api &
sleep 30 && cd /home/vitex/Projects/Ishtaria/ishtaria-datadisk-gilgamesh && make portraits-all
```

This will restart InvokeAI with REST API enabled and immediately start generating all 19 portraits!
