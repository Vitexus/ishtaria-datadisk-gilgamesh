#!/usr/bin/env python3
"""
InvokeAI API v2 Portrait Generator for Gilgamesh Datadisk
Uses the running InvokeAI REST API with correct endpoints

InvokeAI API Endpoints:
- GET /api/v1/models - List models
- POST /api/v1/generation - Text to image (some versions)
- POST /api/v1/generation/text-to-image - Text to image (some versions)
- POST /api/v1/image - Image to image
- GET /api/v1/queue - Queue status

This script tries multiple endpoints and auto-detects the correct API.

Requirements:
- InvokeAI running at http://localhost:9090
- requests library (pip install requests)

Usage:
    python3 invokeai_api_v2.py --single gilgamesh
    python3 invokeai_api_v2.py --all
"""

import argparse
import requests
import json
import os
import time
import sys
import base64
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
PORTRAIT_DIR = BASE_DIR / "media" / "portraits"
INVOKEAI_URL = "http://localhost:9090"

# All characters that need portraits
CHARACTERS = [
    "gilgamesh", "enkidu", "ishtar", "shamhat", "humbaba", "utnapishtim",
    "ur_shanabi", "scorpion_man", "ninsun", "anu", "bull_of_heaven",
    "high_priest_anu", "high_priestess_ishtar", "temple_scribe", "royal_guard",
    "uruk_noble", "uruk_merchant", "potter", "weaver"
]

# Character prompts (same as before)
CHARACTER_PROMPTS = {
    "gilgamesh": {
        "prompt": "Mesopotamian king of Uruk, Early Dynastic period 2700 BCE, two-thirds god one-third man, golden diadem crown with lapis lazuli inlays, white linen tunic with gold embroidery, kaunakes sheep-fleece skirt, wide leather belt with gold buckle, gold-decorated sandals, gold necklace bracelets signet ring, short well-kept hair, short curled beard, sword at belt, regal heroic pose, proud commanding expression, cinematic soft lighting from upper left",
        "negative_prompt": "blurry, low resolution, modern clothing, fantasy elements not in epic, cartoon, anime, realistic photography, watermark, text, extra limbs, deformities"
    },
    "enkidu": {
        "prompt": "Enkidu wild man from Epic of Gilgamesh, Early Dynastic period, strong muscular build, long matted hair covering shoulders and back, animal skin loincloth, bare chest, long unkempt beard, intense focused expression, powerful primal pose standing on the steppe, natural lighting",
        "negative_prompt": "blurry, modern elements, cartoon, anime, photography, watermark, text, clothing, clean groomed hair, civilization"
    },
    "ishtar": {
        "prompt": "Mesopotamian goddess Ishtar, goddess of love and war, horned headdress with multiple tiers and star motifs, lappets hanging down, red and gold ceremonial robes with intricate embroidery, lapis lazuli jewelry, carnelian inlays, gold sandals, heavy kohl eye makeup, red lips, long elaborately styled hair with braids, multiple gold necklaces bracelets armlets anklets earrings, ceremonial mace at side, beautiful yet terrifying expression, divine regal pose",
        "negative_prompt": "blurry, modern, cartoon, anime, photography, watermark, text, mortal appearance, humble, simple clothing"
    },
    "shamhat": {
        "prompt": "Temple priestess Shamhat of Ishtar, Early Dynastic period Uruk, gold headdress with lappets, white ceremonial robes with gold embroidery, long pleated linen dress, gold belt with precious stones, gold sandals, gold necklace with lapis lazuli, gold bracelets and earrings, small ceremonial bronze knife at belt, long elaborately styled black hair, subtle kohl eye makeup, elegant wise pose with hands clasped, kind noble expression",
        "negative_prompt": "blurry, modern, cartoon, anime, photography, watermark, text, servant appearance, commoner clothing"
    },
    "humbaba": {
        "prompt": "Humbaba monster guardian of the Sacred Cedar Forest, sevenfold terrors, monstrous face with exaggerated features, large nose wide mouth, animal skins and furs draped over body, bone armor plates, massive stone club weapon, terrifying appearance, fierce intense expression with glowing eyes, menacing pose standing among cedar trees, dark forest lighting",
        "negative_prompt": "blurry, human, beautiful, modern, cartoon, anime, photography, watermark, text, small, weak, friendly, civilized"
    }
}

# Default prompts for other characters
def get_default_prompt(character_id):
    """Generate a default prompt for characters not in the main list"""
    base = f"Mesopotamian {character_id.replace('_', ' ').title()}, "
    base += "Early Dynastic period, historically accurate costume and appearance, "
    base += "cinematic soft lighting, upper body portrait, detailed"
    return {"prompt": base, "negative_prompt": "blurry, low resolution, modern, cartoon, anime, watermark, text"}


def ensure_portrait_dir():
    """Create portrait directory if it doesn't exist"""
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)
    return PORTRAIT_DIR


def check_invokeai_api(base_url=INVOKEAI_URL):
    """Check if InvokeAI API is running and discover correct endpoints"""
    try:
        # Try health check
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            return True, base_url
        
        # Try different endpoints
        for endpoint in ["/api/v1/models", "/api/models", "/api/v1/health"]:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    return True, base_url
            except:
                pass
        
        return False, None
    except Exception as e:
        return False, None


def discover_api_endpoint(base_url=INVOKEAI_URL):
    """Discover the correct text-to-image endpoint"""
    # Known endpoints to try
    endpoints = [
        "/api/v1/generation",
        "/api/v1/generation/text-to-image", 
        "/api/v1/text2img",
        "/api/text2img",
        "/api/v1/images",
        "/api/images"
    ]
    
    for endpoint in endpoints:
        try:
            # Try to get the endpoint info
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            # If it doesn't 404 or 405, it might exist
            if response.status_code not in [404, 405]:
                return endpoint
        except:
            pass
    
    # Default to most common
    return "/api/v1/generation"


def get_models(base_url=INVOKEAI_URL):
    """Get list of available models from InvokeAI"""
    try:
        response = requests.get(f"{base_url}/api/v1/models", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m.get("name") for m in models if m.get("name")]
        return []
    except Exception:
        return []


def generate_image_v2(prompt, negative_prompt, width=512, height=512, 
                    model="sd-xl-base-1.0", steps=30, cfg_scale=7,
                    base_url=INVOKEAI_URL):
    """Generate an image using InvokeAI API v2 with discovered endpoint"""
    
    # Discover endpoint
    endpoint = discover_api_endpoint(base_url)
    
    # Payload for newer InvokeAI versions
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "model": model,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "scheduler": "DPMSolverMultistep",
        "seed": -1
    }
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            json=payload,
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text[:300]}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None


def generate_image_websocket(prompt, negative_prompt, width=512, height=512,
                            model="sd-xl-base-1.0", steps=30, cfg_scale=7,
                            base_url=INVOKEAI_URL):
    """Generate image using InvokeAI WebSocket API (for newer versions)"""
    import websocket
    import uuid
    import threading
    
    try:
        # Generate unique ID
        task_id = str(uuid.uuid4())
        
        # WebSocket URL
        ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = ws_url.replace(":9090", ":9090/ws/api/v1/generation")
        
        # This is complex, try simpler approach first
        return None
    except Exception:
        return None


def generate_image_form(prompt, negative_prompt, width=512, height=512,
                      model="sd-xl-base-1.0", steps=30, cfg_scale=7,
                      base_url=INVOKEAI_URL):
    """Try generating using form data instead of JSON"""
    
    endpoint = discover_api_endpoint(base_url)
    
    data = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": str(width),
        "height": str(height),
        "model": model,
        "steps": str(steps),
        "cfg_scale": str(cfg_scale),
        "scheduler": "DPMSolverMultistep",
        "seed": "-1"
    }
    
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            data=data,
            timeout=180
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text[:300]}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None


def save_image(image_data, output_path):
    """Save base64 image data to file"""
    try:
        # Handle different response formats
        if isinstance(image_data, str):
            # Base64 encoded string
            binary_data = base64.b64decode(image_data)
        elif isinstance(image_data, dict):
            if "image" in image_data:
                img_str = image_data["image"]
                if isinstance(img_str, str):
                    binary_data = base64.b64decode(img_str)
                else:
                    binary_data = img_str
            elif "images" in image_data and len(image_data["images"]) > 0:
                img_str = image_data["images"][0]
                if isinstance(img_str, str):
                    binary_data = base64.b64decode(img_str)
                elif isinstance(img_str, dict) and "image" in img_str:
                    binary_data = base64.b64decode(img_str["image"])
                else:
                    binary_data = img_str
            else:
                print(f"    Unexpected format: {type(image_data)}")
                return False
        else:
            binary_data = image_data
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(binary_data)
        
        return True
    except Exception as e:
        print(f"    Save error: {e}")
        return False


def try_all_methods(prompt, negative_prompt, width=512, height=512,
                   model="sd-xl-base-1.0", steps=30, cfg_scale=7,
                   base_url=INVOKEAI_URL):
    """Try all generation methods until one works"""
    
    print("    Trying JSON POST...")
    result = generate_image_v2(prompt, negative_prompt, width, height, 
                            model, steps, cfg_scale, base_url)
    if result:
        return result
    
    print("    Trying form POST...")
    result = generate_image_form(prompt, negative_prompt, width, height,
                               model, steps, cfg_scale, base_url)
    if result:
        return result
    
    # Try without explicit endpoint
    print("    Trying common endpoints...")
    for endpoint in ["/api/v1/generation", "/api/generation", "/api/v1/images"]:
        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "model": model,
                "steps": steps,
                "cfg_scale": cfg_scale
            }
            response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=120)
            if response.status_code == 200:
                return response.json()
        except:
            pass
    
    return None


def generate_single_portrait(character_id, model="sd-xl-base-1.0", steps=60, cfg_scale=12, base_url=INVOKEAI_URL):
    """Generate a single portrait using InvokeAI API"""
    ensure_portrait_dir()
    
    if character_id in CHARACTER_PROMPTS:
        prompt_data = CHARACTER_PROMPTS[character_id]
    else:
        prompt_data = get_default_prompt(character_id)
    
    print(f"\n🎨 Generating {character_id}...")
    print(f"   Model: {model}, Steps: {steps}, CFG: {cfg_scale}")
    
    result = try_all_methods(
        prompt_data["prompt"],
        prompt_data["negative_prompt"],
        512, 512,
        model, steps, cfg_scale,
        base_url
    )
    
    if result:
        # Try to extract image from result
        image_data = None
        
        # Check various possible response formats
        if isinstance(result, dict):
            if "image" in result:
                image_data = result["image"]
            elif "images" in result and len(result.get("images", [])) > 0:
                image_data = result["images"][0]
            elif "output" in result:
                image_data = result["output"]
            elif "result" in result:
                image_data = result["result"]
            else:
                print(f"    Response keys: {list(result.keys())}")
                print(f"    Full response: {json.dumps(result)[:500]}")
        
        if image_data:
            output_path = PORTRAIT_DIR / f"{character_id}.png"
            if save_image(image_data, output_path):
                print(f"   ✅ Success: {output_path.name}")
                file_size = output_path.stat().st_size
                print(f"   📏 Size: {file_size / 1024:.1f} KB")
                return True
        else:
            print(f"    No image data in response")
    
    print(f"   ❌ Failed to generate")
    return False


def generate_all_portraits(model="sd-xl-base-1.0", steps=60, cfg_scale=12, base_url=INVOKEAI_URL):
    """Generate all character portraits"""
    ensure_portrait_dir()
    
    print("=" * 70)
    print("🏛️  Gilgamesh Datadisk - Portrait Generation via InvokeAI API")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Steps: {steps}, CFG Scale: {cfg_scale}")
    print(f"API: {base_url}")
    print("=" * 70)
    
    # Check API
    api_ok, api_url = check_invokeai_api(base_url)
    if not api_ok:
        print("\n❌ InvokeAI API not available")
        print(f"   Checked: {base_url}")
        print("\n   Please ensure InvokeAI is running:")
        print("   - InvokeAI should be running at:", base_url)
        print("   - Check with: curl", base_url)
        print("\n   Or start it with:")
        print("   invokeai --host 0.0.0.0 --port 9090")
        return False
    
    # Try to get models
    models = get_models(api_url)
    if models:
        print(f"\n📋 Available models: {len(models)}")
        for m in models[:3]:
            print(f"   - {m}")
        if len(models) > 3:
            print(f"   ... and {len(models) - 3} more")
    
    # Adjust model if needed
    if model not in models:
        print(f"\n⚠️  Model '{model}' not found, using first available")
        if models:
            model = models[0]
            print(f"   Using: {model}")
    
    success_count = 0
    failed_count = 0
    total_count = len(CHARACTERS)
    
    for character_id in CHARACTERS:
        if generate_single_portrait(character_id, model, steps, cfg_scale, api_url):
            success_count += 1
        else:
            failed_count += 1
        time.sleep(0.5)  # Small delay
    
    print("\n" + "=" * 70)
    print(f"📊 Generation Summary")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📋 Total: {total_count}")
    if total_count > 0:
        print(f"📈 Success Rate: {success_count/total_count*100:.1f}%")
    print("=" * 70)
    
    return success_count == total_count


def convert_to_jpeg():
    """Convert all PNG portraits to JPEG"""
    ensure_portrait_dir()
    
    print("\n🔄 Converting PNG to JPEG...")
    converted = 0
    
    for png_file in sorted(PORTRAIT_DIR.glob("*.png")):
        jpeg_file = png_file.with_suffix(".jpg")
        
        try:
            import subprocess
            subprocess.run(
                ["convert", str(png_file), "-quality", "90", "-resize", "512x512", str(jpeg_file)],
                check=True,
                capture_output=True,
                timeout=30
            )
            png_file.unlink()
            print(f"   ✅ {jpeg_file.name}")
            converted += 1
        except Exception as e:
            print(f"   ❌ {png_file.name}: {e}")
    
    print(f"\n📊 Converted {converted} images to JPEG")
    return converted


def main():
    parser = argparse.ArgumentParser(
        description="Generate Gilgamesh portraits using InvokeAI REST API v2"
    )
    parser.add_argument(
        "--model", type=str, 
        default="sd-xl-base-1.0",
        help="Model to use"
    )
    parser.add_argument(
        "--steps", type=int, default=60,
        help="Number of diffusion steps"
    )
    parser.add_argument(
        "--cfg", type=int, default=12,
        help="CFG scale"
    )
    parser.add_argument(
        "--single", type=str, default=None,
        help="Generate only a single character"
    )
    parser.add_argument(
        "--convert", action="store_true",
        help="Convert PNG to JPEG after generation"
    )
    parser.add_argument(
        "--api-url", type=str, 
        default="http://localhost:9090",
        help="InvokeAI API URL"
    )
    parser.add_argument(
        "--list-models", action="store_true",
        help="List available models and exit"
    )
    
    args = parser.parse_args()
    
    # List models and exit
    if args.list_models:
        api_ok, api_url = check_invokeai_api(args.api_url)
        if api_ok:
            models = get_models(api_url)
            print("Available models:")
            for i, model in enumerate(models, 1):
                print(f"{i}. {model}")
        else:
            print("InvokeAI API not available")
        sys.exit(0)
    
    print("\n🚀 Starting Gilgamesh Portrait Generation\n")
    
    if args.single:
        ensure_portrait_dir()
        success = generate_single_portrait(
            args.single, args.model, args.steps, args.cfg, args.api_url
        )
        if success and args.convert:
            convert_to_jpeg()
        sys.exit(0 if success else 1)
    else:
        success = generate_all_portraits(
            args.model, args.steps, args.cfg, args.api_url
        )
        if success and args.convert:
            convert_to_jpeg()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
