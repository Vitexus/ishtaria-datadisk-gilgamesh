#!/usr/bin/env python3
"""
InvokeAI API Portrait Generator for Gilgamesh Datadisk
Uses the running InvokeAI REST API at localhost:9090

Requirements:
- InvokeAI running at http://localhost:9090
- requests library (pip install requests)

Usage:
    python3 invokeai_api_generate.py --single gilgamesh
    python3 invokeai_api_generate.py --all

API Documentation: https://github.com/invoke-ai/InvokeAI/blob/main/invokeai/api/openapi.yaml
"""

import argparse
import requests
import json
import os
import time
from pathlib import Path
import sys

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

# Character prompts
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
    },
    "utnapishtim": {
        "prompt": "Utnapishtim the distant, survivor of the Great Flood, wise immortal elder, simple white headband or turban, long white robes with subtle patterns, staff in right hand, clay tablets at belt, long white gray hair and beard, wrinkled wise face, wise kind expression, contemplative pose, soft peaceful lighting",
        "negative_prompt": "blurry, young, modern, cartoon, anime, photography, watermark, text, weak, foolish, short hair"
    },
    "ur_shanabi": {
        "prompt": "Ur-Shanabi the ferryman, practical working man, simple cloth turban head covering, plain linen loincloth or simple tunic, leather belt with pouch, oar or pole in hands, sandals or barefoot, practical short dark hair and beard, focused determined expression, working pose on wooden boat, soft water reflections",
        "negative_prompt": "blurry, royal, wealthy, modern, cartoon, anime, photography, watermark, text, elaborate clothing"
    },
    "scorpion_man": {
        "prompt": "Scorpion Man guardian of Mount Mashu, half-man half-scorpion hybrid creature, human upper body with muscular torso and arms, human head with focused expression, scorpion lower body with segmented exoskeleton chitin armor, large pincers, curved segmented tail with stinger, brown and black chitin plates, stone elements, guarding pose at mountain gate, dramatic lighting",
        "negative_prompt": "blurry, fully human, fully scorpion, modern, cartoon, anime, photography, watermark, text, friendly appearance"
    }
}

# For remaining characters, use simplified prompts
def get_default_prompt(character_id):
    """Generate a default prompt for characters not in the main list"""
    base = f"Mesopotamian {character_id.replace('_', ' ').title()}, "
    base += "Early Dynastic period, historically accurate costume and appearance, "
    base += "cinematic soft lighting, upper body portrait, detailed"
    
    negative = "blurry, low resolution, modern, cartoon, anime, watermark, text"
    
    return {"prompt": base, "negative_prompt": negative}


def check_invokeai_api():
    """Check if InvokeAI API is running"""
    try:
        response = requests.get(f"{INVOKEAI_URL}/api/v1/models", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Cannot connect to InvokeAI API: {e}")
        return False


def get_models():
    """Get list of available models from InvokeAI"""
    try:
        response = requests.get(f"{INVOKEAI_URL}/api/v1/models")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m.get("name") for m in models if m.get("name")]
        return []
    except Exception as e:
        print(f"⚠️  Warning: Could not fetch models: {e}")
        return []


def generate_image(prompt, negative_prompt, width=512, height=512, model="realistic_vision_v51", steps=30, cfg_scale=7):
    """Generate an image using InvokeAI API"""
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "model": model,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "scheduler": "DPMSolverMultistep",
        "seed": -1  # Random seed
    }
    
    try:
        response = requests.post(
            f"{INVOKEAI_URL}/api/v1/generation/text-to-image",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def save_image(image_data, output_path):
    """Save base64 image data to file"""
    import base64
    
    try:
        # Extract base64 data
        if isinstance(image_data, str):
            # Already base64
            binary_data = base64.b64decode(image_data)
        elif isinstance(image_data, dict) and "image" in image_data:
            binary_data = base64.b64decode(image_data["image"])
        else:
            print(f"⚠️  Unexpected image data format")
            return False
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(binary_data)
        
        return True
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return False


def generate_single_portrait(character_id, model="realistic_vision_v51", steps=50, cfg_scale=10):
    """Generate a single portrait using InvokeAI API"""
    ensure_portrait_dir()
    
    # Get prompt
    if character_id in CHARACTER_PROMPTS:
        prompt_data = CHARACTER_PROMPTS[character_id]
    else:
        prompt_data = get_default_prompt(character_id)
    
    print(f"\n🎨 Generating {character_id}...")
    print(f"   Model: {model}")
    print(f"   Steps: {steps}, CFG: {cfg_scale}")
    print(f"   Prompt: {prompt_data['prompt'][:100]}...")
    
    # Generate image
    result = generate_image(
        prompt=prompt_data["prompt"],
        negative_prompt=prompt_data["negative_prompt"],
        model=model,
        steps=steps,
        cfg_scale=cfg_scale
    )
    
    if result and "images" in result and len(result["images"]) > 0:
        image_data = result["images"][0]
        output_path = PORTRAIT_DIR / f"{character_id}.png"
        
        if save_image(image_data, output_path):
            print(f"   ✅ Success: {output_path.name}")
            file_size = output_path.stat().st_size
            print(f"   📏 Size: {file_size / 1024:.1f} KB")
            return True
        else:
            print(f"   ❌ Failed to save image")
            return False
    else:
        print(f"   ❌ No images generated")
        if result:
            print(f"   Response: {json.dumps(result, indent=2)[:200]}")
        return False


def generate_all_portraits(model="realistic_vision_v51", steps=50, cfg_scale=10):
    """Generate all character portraits"""
    ensure_portrait_dir()
    
    print("=" * 70)
    print("🏛️  Gilgamesh Datadisk - Portrait Generation via API")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Steps: {steps}, CFG Scale: {cfg_scale}")
    print(f"API: {INVOKEAI_URL}")
    print("=" * 70)
    
    # Check API
    if not check_invokeai_api():
        print("\n❌ InvokeAI API not available at", INVOKEAI_URL)
        print("   Please start InvokeAI first:")
        print("   invokeai --host 0.0.0.0 --port 9090")
        return False
    
    # Show available models
    models = get_models()
    if models:
        print(f"\n📋 Available models: {len(models)}")
        for m in models[:5]:
            print(f"   - {m}")
        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more")
    
    success_count = 0
    failed_count = 0
    total_count = len(CHARACTERS)
    
    for character_id in CHARACTERS:
        if generate_single_portrait(character_id, model, steps, cfg_scale):
            success_count += 1
            # Small delay between requests
            time.sleep(1)
        else:
            failed_count += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Generation Summary")
    print("=" * 70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📋 Total: {total_count}")
    print(f"📈 Success Rate: {success_count/total_count*100:.1f}%")
    print("=" * 70)
    
    return success_count == total_count


def ensure_portrait_dir():
    """Create portrait directory if it doesn't exist"""
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)
    return PORTRAIT_DIR


def convert_to_jpeg():
    """Convert all PNG portraits to JPEG for smaller file size"""
    ensure_portrait_dir()
    
    print("\n🔄 Converting PNG to JPEG...")
    converted = 0
    
    for png_file in sorted(PORTRAIT_DIR.glob("*.png")):
        jpeg_file = png_file.with_suffix(".jpg")
        
        # Use ImageMagick convert
        cmd = [
            "convert",
            str(png_file),
            "-quality", "90",
            "-resize", "512x512",
            str(jpeg_file)
        ]
        
        try:
            import subprocess
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            png_file.unlink()  # Remove PNG
            print(f"   ✅ {jpeg_file.name}")
            converted += 1
        except Exception as e:
            print(f"   ❌ {png_file.name}: {e}")
    
    print(f"\n📊 Converted {converted} images to JPEG")
    return converted


def main():
    parser = argparse.ArgumentParser(
        description="Generate Gilgamesh portraits using InvokeAI REST API"
    )
    parser.add_argument(
        "--model", type=str, 
        default="realistic_vision_v51",
        help="Model to use (default: realistic_vision_v51)"
    )
    parser.add_argument(
        "--steps", type=int, default=50,
        help="Number of diffusion steps (default: 50)"
    )
    parser.add_argument(
        "--cfg", type=int, default=10,
        help="CFG scale (default: 10)"
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
        "--list-models", action="store_true",
        help="List available models and exit"
    )
    parser.add_argument(
        "--api-url", type=str, 
        default="http://localhost:9090",
        help="InvokeAI API URL (default: http://localhost:9090)"
    )
    
    args = parser.parse_args()
    
    # Set API URL
    global INVOKEAI_URL
    INVOKEAI_URL = args.api_url
    
    # List models and exit
    if args.list_models:
        models = get_models()
        print("Available models:")
        for i, model in enumerate(models, 1):
            print(f"{i}. {model}")
        sys.exit(0)
    
    print("\n🚀 Starting Gilgamesh Portrait Generation via API\n")
    
    if args.single:
        # Generate only one character
        ensure_portrait_dir()
        
        if args.single not in CHARACTERS and args.single not in CHARACTER_PROMPTS:
            # Try to generate anyway with default prompt
            pass
        
        success = generate_single_portrait(
            args.single, args.model, args.steps, args.cfg
        )
        
        if success and args.convert:
            convert_to_jpeg()
        
        if success:
            print(f"\n✅ {args.single} portrait generated successfully!")
            sys.exit(0)
        else:
            print(f"\n❌ Failed to generate {args.single}")
            sys.exit(1)
    
    else:
        # Generate all characters
        success = generate_all_portraits(args.model, args.steps, args.cfg)
        
        if success and args.convert:
            convert_to_jpeg()
        
        if success:
            print("\n✅ All portraits generated successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some portraits failed to generate")
            sys.exit(1)


if __name__ == "__main__":
    main()
