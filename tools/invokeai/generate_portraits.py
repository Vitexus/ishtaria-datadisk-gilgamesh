#!/usr/bin/env python3
"""
InvokeAI Portrait Generator for Gilgamesh Datadisk
Generates all character portraits using InvokeAI

Requirements:
- InvokeAI installed and configured
- invokeai CLI command available in PATH
- Models downloaded (e.g., realistic_vision_v51.safetensors)

Usage:
    python3 generate_portraits.py --model <model_name> --steps 50 --cfg 10

Example:
    python3 generate_portraits.py --model realistic_vision_v51.safetensors --steps 50 --cfg 10
    python3 generate_portraits.py --single gilgamesh --model sd-xl-base-1.0.safetensors
"""

import argparse
import os
import json
import sys
import subprocess
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
PORTRAIT_DIR = BASE_DIR / "media" / "portraits"

# All characters that need portraits
CHARACTERS = [
    "gilgamesh", "enkidu", "ishtar", "shamhat", "humbaba", "utnapishtim",
    "ur_shanabi", "scorpion_man", "ninsun", "anu", "bull_of_heaven",
    "high_priest_anu", "high_priestess_ishtar", "temple_scribe", "royal_guard",
    "uruk_noble", "uruk_merchant", "potter", "weaver"
]

# Historically accurate prompts for each character
CHARACTER_PROMPTS = {
    "gilgamesh": {
        "positive": "Mesopotamian king of Uruk, Early Dynastic period 2700 BCE, two-thirds god one-third man, golden diadem crown with lapis lazuli inlays, white linen tunic with gold embroidery, kaunakes sheep-fleece skirt, wide leather belt with gold buckle, gold-decorated sandals, gold necklace bracelets signet ring, short well-kept hair, short curled beard, sword at belt, regal heroic pose, proud commanding expression, cinematic soft lighting from upper left, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, low resolution, modern clothing, fantasy elements, cartoon, anime, realistic photography, watermark, text, extra limbs, deformities, low detail"
    },
    "enkidu": {
        "positive": "Enkidu wild man from Epic of Gilgamesh, Early Dynastic period, strong muscular build, long matted hair covering shoulders and back, animal skin loincloth made from lion or deer, bare chest, long unkempt beard, intense focused expression, powerful primal pose standing on the steppe, natural lighting, upper body portrait, historically accurate Mesopotamian wild man, high detail, 512x512",
        "negative": "blurry, modern elements, cartoon, anime, photography, watermark, text, clothing, clean groomed hair, civilization, human appearance"
    },
    "enkidu_civilized": {
        "positive": "Enkidu after civilization by Shamhat, Early Dynastic period, strong muscular build, simple headband, simple linen tunic, kaunakes or plain skirt, leather belt, sandals, one gold bracelet from Shamhat, long but cleaner hair, trimmed beard, noble expression, refined pose, soft temple lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, wild appearance, animal skins, unkempt hair, cartoon, anime, photography, watermark, text"
    },
    "ishtar": {
        "positive": "Mesopotamian goddess Ishtar, goddess of love and war, horned headdress with multiple tiers and star motifs, lappets hanging down, red and gold ceremonial robes with intricate embroidery, lapis lazuli jewelry, carnelian inlays, gold sandals, heavy kohl eye makeup, red lips, long elaborately styled hair with braids, multiple gold necklaces bracelets armlets anklets earrings, ceremonial mace at side, beautiful yet terrifying expression, divine regal pose, ethereal lighting, upper body portrait, historically accurate Babylonian, high detail, 512x512",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, mortal appearance, humble, simple clothing, no makeup"
    },
    "shamhat": {
        "positive": "Temple priestess Shamhat of Ishtar, Early Dynastic period Uruk, gold headdress with lappets, white ceremonial robes with gold embroidery and patterns, long pleated linen dress, gold belt with precious stones, gold sandals, gold necklace with lapis lazuli, gold bracelets and earrings, small ceremonial bronze knife at belt, long elaborately styled black hair, subtle kohl eye makeup, elegant wise pose with hands clasped, kind noble expression, soft temple lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, servant appearance, commoner clothing, messy hair"
    },
    "humbaba": {
        "positive": "Humbaba monster guardian of the Sacred Cedar Forest, sevenfold terrors, monstrous face with exaggerated features, large nose wide mouth, animal skins and furs draped over body, bone armor plates, massive stone club weapon, terrifying appearance, fierce intense expression with glowing eyes, menacing pose standing among cedar trees, dark forest lighting, full body portrait, Mesopotamian monster from epic, high detail, 512x512",
        "negative": "blurry, human, beautiful, modern, cartoon, anime, photography, watermark, text, small, weak, friendly, civilized"
    },
    "utnapishtim": {
        "positive": "Utnapishtim the distant, survivor of the Great Flood, wise immortal elder, simple white headband or turban, long white robes with subtle patterns, staff in right hand, clay tablets at belt, long white gray hair and beard, wrinkled wise face, wise kind expression, contemplative pose, soft peaceful lighting, upper body portrait, historically accurate ancient Mesopotamian, high detail, 512x512",
        "negative": "blurry, young, modern, cartoon, anime, photography, watermark, text, weak, foolish, short hair, colorful clothing"
    },
    "ur_shanabi": {
        "positive": "Ur-Shanabi the ferryman, practical working man, simple cloth turban head covering, plain linen loincloth or simple tunic, leather belt with pouch, oar or pole in hands, sandals or barefoot, practical short dark hair and beard, focused determined expression, working pose on wooden boat, soft water reflections, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, royal, wealthy, modern, cartoon, anime, photography, watermark, text, elaborate clothing, jewelry"
    },
    "scorpion_man": {
        "positive": "Scorpion Man guardian of Mount Mashu, half-man half-scorpion hybrid creature, human upper body with muscular torso and arms, human head with focused expression, scorpion lower body with segmented exoskeleton chitin armor, large pincers, curved segmented tail with stinger, brown and black chitin plates, stone elements, guarding pose at mountain gate, dramatic lighting, full body portrait, Mesopotamian guardian from Gilgamesh epic, high detail, 512x512",
        "negative": "blurry, fully human, fully scorpion, modern, cartoon, anime, photography, watermark, text, friendly appearance, small size"
    },
    "ninsun": {
        "positive": "Ninsun mother of Gilgamesh, wise goddess, goddess headdress with divine symbols, white robes with gold embroidery, long flowing white skirt, gold belt, gold sandals, multiple gold jewelry pieces, long elaborately styled hair, heavy kohl eye makeup, wise divine expression, maternal pose, soft divine lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, young, commoner, modern, cartoon, anime, photography, watermark, text, simple appearance, mortal"
    },
    "anu": {
        "positive": "Anu sky god father of Ishtar, supreme deity, horned headdress with multiple tiers representing heavens, white or blue robes with gold and lapis lazuli decorations, long flowing skirt, wide gold belt, gold sandals, extensive gold jewelry with lapis lazuli, scepter in hand, symbols of the sky, long white gray hair and beard elaborately curled, divine authority expression, regal pose on throne, ethereal heavenly lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, mortal, modern, cartoon, anime, photography, watermark, text, earthly appearance, simple"
    },
    "bull_of_heaven": {
        "positive": "Bull of Heaven divine beast sent by Ishtar, massive divine bull with exaggerated features, powerful muscular body, large curved horns, red and black coloring as described in epic, terrifying appearance, fierce expression, smoke and fire effects around mouth and nostrils, charging pose, dramatic divine lighting, full body portrait, Mesopotamian divine creature, high detail, 512x512",
        "negative": "blurry, normal bull, small, weak, modern, cartoon, anime, photography, watermark, text, friendly, mortal appearance"
    },
    "high_priest_anu": {
        "positive": "High Priest of Anu, traditional Mesopotamian priest, white headdress with lappets, white linen tunic and ceremonial robe, long skirt, lapis lazuli bead necklace worn as belt, white sandals, ceremonial bronze dagger at belt, clay tablet in hand, long well-kept black hair and beard, pious divine expression, prayer pose with hands raised, soft temple lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, warrior, commoner, simple clothing, messy appearance"
    },
    "high_priestess_ishtar": {
        "positive": "High Priestess of Ishtar, ceremonial robes of love and war, star headdress with Ishtar symbols, red and gold robes with intricate embroidery, long skirt, gold belt, gold sandals, multiple gold jewelry pieces, ceremonial mace in hand, long elaborately styled hair, heavy makeup with kohl and red, regal powerful expression, divine pose, soft temple lighting with red accents, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, simple appearance, commoner, humble"
    },
    "temple_scribe": {
        "positive": "Mesopotamian temple scribe, scholar appearance, simple white headband, plain white linen tunic, plain skirt, clay tablets in leather satchel over shoulder, reed stylus at belt, sandals, practical short black hair and beard, focused scholarly expression, reading pose with stylus in hand, soft library lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, modern, cartoon, anime, photography, watermark, text, warrior, noble, elaborate clothing"
    },
    "royal_guard": {
        "positive": "Royal Guard of Uruk, elite soldier, plumed bronze helmet with horsehair crest, bronze scale armor cuirass, leather skirt over armor, bronze greaves on legs, leather boots, sword at belt and spear in hand, short practical hair and beard, formidable guarding expression, alert pose, soft palace lighting, full body portrait, historically accurate Akkadian period, high detail, 512x512",
        "negative": "blurry, commoner, modern, cartoon, anime, photography, watermark, text, simple clothing, no armor"
    },
    "uruk_noble": {
        "positive": "Uruk Noble wealthy citizen, turban or cylinder hat, fine linen tunic with gold embroidery at edges, long skirt, gold belt, gold sandals, gold jewelry necklace bracelets rings, staff or walking stick in hand, well-kept black hair and beard, refined noble expression, elegant pose, soft palace lighting, upper body portrait, historically accurate Early Dynastic, high detail, 512x512",
        "negative": "blurry, poor, modern, cartoon, anime, photography, watermark, text, simple clothing, messy appearance"
    },
    "uruk_merchant": {
        "positive": "Uruk Merchant trader, colorful turban head covering, colorful tunic with patterns, plain skirt, balance scale hanging from belt, leather money pouch at waist, practical sandals, short practical hair and beard, shrewd trading expression, offering pose with hands extended, bustling market lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, noble, modern, cartoon, anime, photography, watermark, text, simple clothing, wealthy appearance"
    },
    "potter": {
        "positive": "Mesopotamian potter craftsman, simple cloth head covering, plain linen tunic stained with clay, plain skirt, clay-covered leather apron, wooden tools at belt, barefoot or simple sandals, clay dust on hands and clothes, short practical hair, focused working expression, shaping clay pose with hands on pottery, workshop lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, noble, modern, cartoon, anime, photography, watermark, text, clean appearance, no clay"
    },
    "weaver": {
        "positive": "Mesopotamian weaver textile worker, simple head covering shawl, plain dress with woven patterns, long skirt, shuttle at belt, fabric samples in hand, barefoot or simple sandals, practical covered hair, focused working expression, weaving pose with hands busy, soft home lighting, upper body portrait, historically accurate, high detail, 512x512",
        "negative": "blurry, noble, modern, cartoon, anime, photography, watermark, text, elaborate clothing, idle pose"
    }
}


def ensure_portrait_dir():
    """Create portrait directory if it doesn't exist"""
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)
    return PORTRAIT_DIR


def check_invokeai():
    """Check if InvokeAI is installed and available"""
    try:
        result = subprocess.run(
            ["invokeai", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def generate_single_portrait(character_id, model, steps=50, cfg_scale=10, width=512, height=512):
    """Generate a single portrait using InvokeAI CLI"""
    ensure_portrait_dir()
    
    if character_id not in CHARACTER_PROMPTS:
        print(f"⚠️  Warning: No built-in prompt for {character_id}, skipping...")
        return False
    
    prompt_data = CHARACTER_PROMPTS[character_id]
    positive = prompt_data["positive"]
    negative = prompt_data["negative"]
    
    output_file = PORTRAIT_DIR / f"{character_id}.png"
    
    # Build InvokeAI command
    cmd = [
        "invokeai",
        "--prompt", positive,
        "--negative-prompt", negative,
        "--width", str(width),
        "--height", str(height),
        "--model", model,
        "--steps", str(steps),
        "--cfg-scale", str(cfg_scale),
        "--output", str(output_file),
        "--seed", "42",  # For reproducibility
        "--precision", "float16" if "xl" in model.lower() else "float32"
    ]
    
    print(f"\n🎨 Generating {character_id}...")
    print(f"   Model: {model}")
    print(f"   Steps: {steps}, CFG: {cfg_scale}")
    print(f"   Output: {output_file.name}")
    print(f"   Positive: {positive[:100]}...")
    print(f"   Negative: {negative[:80]}...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180  # 3 minutes per image
        )
        
        if result.returncode == 0:
            print(f"   ✅ Success: {output_file.name}")
            
            # Check if file was created
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"   📏 Size: {file_size / 1024:.1f} KB")
                return True
            else:
                print(f"   ⚠️  Command succeeded but no output file created")
                print(f"   stdout: {result.stdout[:200]}")
                print(f"   stderr: {result.stderr[:200]}")
                return False
        else:
            print(f"   ❌ Error (code {result.returncode}):")
            if result.stderr:
                print(f"      {result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout after 180 seconds")
        return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


def generate_all_portraits(model="realistic_vision_v51.safetensors", steps=50, cfg_scale=10):
    """Generate all character portraits"""
    ensure_portrait_dir()
    
    print("=" * 70)
    print("🏛️  Gilgamesh Datadisk - Portrait Generation")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Steps: {steps}, CFG Scale: {cfg_scale}")
    print(f"Output: {PORTRAIT_DIR}")
    print(f"Characters: {len(CHARACTERS)}")
    print("=" * 70)
    
    # Check InvokeAI
    if not check_invokeai():
        print("\n❌ InvokeAI not found!")
        print("   Please install InvokeAI first:")
        print("   https://github.com/invoke-ai/InvokeAI")
        print("\n   Or use pip:")
        print("   pip install invokeai")
        return False
    
    success_count = 0
    failed_count = 0
    total_count = len(CHARACTERS)
    
    for character_id in CHARACTERS:
        if generate_single_portrait(character_id, model, steps, cfg_scale):
            success_count += 1
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
        description="Generate Gilgamesh character portraits using InvokeAI"
    )
    parser.add_argument(
        "--model", type=str, 
        default="realistic_vision_v51.safetensors",
        help="InvokeAI model (default: realistic_vision_v51.safetensors)"
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
        help="Generate only a single character (e.g., 'gilgamesh')"
    )
    parser.add_argument(
        "--convert", action="store_true",
        help="Convert PNG to JPEG after generation"
    )
    parser.add_argument(
        "--width", type=int, default=512,
        help="Image width (default: 512)"
    )
    parser.add_argument(
        "--height", type=int, default=512,
        help="Image height (default: 512)"
    )
    
    args = parser.parse_args()
    
    print("\n🚀 Starting Gilgamesh Portrait Generation\n")
    
    if args.single:
        # Generate only one character
        ensure_portrait_dir()
        
        if args.single not in CHARACTER_PROMPTS:
            print(f"❌ Character '{args.single}' not found in prompts")
            print(f"   Available: {', '.join(CHARACTER_PROMPTS.keys())}")
            sys.exit(1)
        
        success = generate_single_portrait(
            args.single, args.model, args.steps, args.cfg, 
            args.width, args.height
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
