#!/usr/bin/env python3
"""
Generate placeholder images for portraits and textures.

This script creates simple placeholder images for all the portraits and textures
needed by the Gilgamesh datadisk. These can be replaced with proper artwork later.

Usage:
    python3 tools/generate_placeholders.py
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Configuration
ROOT = Path(__file__).resolve().parent.parent
PORTRAIT_DIR = ROOT / "media" / "portraits"
TEXTURE_DIR = ROOT / "media" / "textures"
COVER_DIR = ROOT / "media" / "cover"
MODEL_DIR = ROOT / "media" / "models"

# Portrait specifications (name: description, color)
PORTRAITS = {
    "gilgamesh.jpg": ("Gilgamesh", "King of Uruk", (218, 165, 32, 255)),
    "enkidu.jpg": ("Enkidu", "Wild Man & Companion", (72, 61, 139, 255)),
    "ishtar.jpg": ("Ishtar", "Goddess of Love & War", (199, 21, 133, 255)),
    "shamhat.jpg": ("Shamhat", "Temple Priestess", (255, 20, 147, 255)),
    "humbaba.jpg": ("Humbaba", "Guardian of Cedar Forest", (34, 139, 34, 255)),
    "utnapishtim.jpg": ("Utnapishtim", "Flood Survivor", (70, 130, 180, 255)),
    "ur_shanabi.jpg": ("Ur-Shanabi", "Ferryman", (135, 206, 235, 255)),
    "scorpion_man.jpg": ("Scorpion Man", "Guardian of Mashu", (139, 69, 19, 255)),
    "ninsun.jpg": ("Ninsun", "Mother of Gilgamesh", (189, 183, 107, 255)),
    "anu.jpg": ("Anu", "Sky God", (255, 215, 0, 255)),
    "bull_of_heaven.jpg": ("Bull of Heaven", "Divine Beast", (165, 42, 42, 255)),
    "high_priest_anu.jpg": ("High Priest of Anu", "Temple Servant", (240, 230, 140, 255)),
    "high_priestess_ishtar.jpg": ("High Priestess of Ishtar", "Divine Voice", (220, 20, 60, 255)),
    "temple_scribe.jpg": ("Temple Scribe", "Keeper of Records", (205, 133, 63, 255)),
    "royal_guard.jpg": ("Royal Guard", "Protector of Uruk", (85, 107, 47, 255)),
    "uruk_noble.jpg": ("Uruk Noble", "Wealthy Citizen", (148, 0, 211, 255)),
    "uruk_merchant.jpg": ("Uruk Merchant", "Trader", (0, 128, 128, 255)),
    "potter.jpg": ("Potter", "Craftsman", (139, 69, 19, 255)),
    "weaver.jpg": ("Weaver", "Textile Worker", (184, 134, 11, 255)),
}

# Music track placeholders
MUSIC_TRACKS = [
    "temple.ogg",
    "ishtar_shrine.ogg",
    "cedar_forest.ogg",
    "mountain_echo.ogg",
    "waters_of_death.ogg",
    "utnapishtim.ogg",
]

def create_portrait(name, title, description, color, size=(512, 512)):
    """Create a placeholder portrait image."""
    img = Image.new('RGBA', size, color)
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fall back to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw border
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(0, 0, 0, 255), width=4)
    
    # Draw inner border
    draw.rectangle([8, 8, size[0]-9, size[1]-9], outline=(255, 255, 255, 255), width=2)
    
    # Draw name
    draw.text((20, 20), name, fill=(255, 255, 255, 255), font=font_large)
    
    # Draw title
    draw.text((20, 60), title, fill=(255, 255, 255, 255), font=font_small)
    
    # Draw description at bottom
    y_pos = size[1] - 80
    for line in textwrap.wrap(description, width=30):
        draw.text((20, y_pos), line, fill=(255, 255, 255, 255), font=font_small)
        y_pos += 20
    
    return img

def create_cover_image(size=(1024, 768)):
    """Create a placeholder cover image."""
    img = Image.new('RGBA', size, (40, 40, 80, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw gradient background
    for y in range(size[1]):
        ratio = y / size[1]
        color = (
            int(40 + 160 * ratio),
            int(40 + 120 * ratio),
            int(80 + 175 * ratio),
            255
        )
        draw.line([(0, y), (size[0], y)], fill=color)
    
    # Draw title
    title = "Epic of Gilgamesh"
    title_width = draw.textlength(title, font=font_large)
    draw.text((size[0]//2 - title_width//2, 200), title, fill=(255, 215, 0, 255), font=font_large)
    
    # Draw subtitle
    subtitle = "An Ishtaria Datadisk"
    sub_width = draw.textlength(subtitle, font=font_small)
    draw.text((size[0]//2 - sub_width//2, 280), subtitle, fill=(255, 255, 255, 255), font=font_small)
    
    # Draw decorative elements
    draw.ellipse([(size[0]//2 - 150, 350), (size[0]//2 + 150, 550)], 
                outline=(255, 215, 0, 255), width=4)
    
    # Draw features
    features = [
        "13 Epic Locations",
        "8 Main Characters",
        "Complete Questline",
        "Mesopotamian Architecture",
        "English & Czech Translations"
    ]
    
    y_pos = 400
    for feature in features:
        draw.text((size[0]//2 - 100, y_pos), feature, fill=(255, 255, 255, 255), font=font_small)
        y_pos += 40
    
    return img

def create_texture(name, color, size=(512, 512)):
    """Create a placeholder texture."""
    img = Image.new('RGBA', size, color)
    draw = ImageDraw.Draw(img)
    
    # Draw diagonal cross pattern
    draw.line([(0, 0), (size[0], size[1])], fill=(0, 0, 0, 128), width=2)
    draw.line([(0, size[1]), (size[0], 0)], fill=(0, 0, 0, 128), width=2)
    
    # Draw name in corner
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), name, fill=(255, 255, 255, 255), font=font)
    
    return img

def create_music_placeholder(name, size=(512, 512)):
    """Create a placeholder for music track (visual representation)."""
    img = Image.new('RGBA', size, (40, 40, 40, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    # Draw musical note symbol
    draw.ellipse([(200, 200), (220, 240)], fill=(255, 255, 255, 255))
    draw.line([(220, 220), (240, 180)], fill=(255, 255, 255, 255), width=3)
    
    # Draw name
    draw.text((20, 20), name.replace('.ogg', ''), fill=(255, 255, 255, 255), font=font)
    
    # Draw description
    draw.text((20, 450), "Music track placeholder", fill=(200, 200, 200, 255), font=font)
    
    return img

def main():
    print("Generating placeholder images for Gilgamesh datadisk...")
    
    # Create directories
    PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate portraits
    print(f"\nGenerating {len(PORTRAITS)} portraits...")
    for filename, (name, title, color) in PORTRAITS.items():
        img = create_portrait(name, title, "Character Portrait", color)
        # Convert RGBA to RGB for JPEG
        if filename.endswith('.jpg'):
            rgb_img = img.convert('RGB')
            rgb_img.save(PORTRAIT_DIR / filename)
        else:
            img.save(PORTRAIT_DIR / filename)
        print(f"  Created: {filename}")
    
    # Generate cover
    print("\nGenerating cover image...")
    img = create_cover_image()
    img.convert('RGB').save(COVER_DIR / "cover.jpg")
    print("  Created: cover/cover.jpg")
    
    # Generate music track placeholders (as images for documentation)
    print(f"\nGenerating {len(MUSIC_TRACKS)} music track images...")
    for filename in MUSIC_TRACKS:
        img = create_music_placeholder(filename)
        img.save(TEXTURE_DIR / f"{filename.replace('.ogg', '.png')}")
        print(f"  Created: textures/{filename.replace('.ogg', '.png')}")
    
    # Generate some texture placeholders
    print("\nGenerating texture placeholders...")
    textures = {
        "mud_brick.png": ("Mud Brick", (139, 69, 19, 255)),
        "plaster.png": ("Plaster", (240, 240, 230, 255)),
        "lapis_lazuli.png": ("Lapis Lazuli", (38, 97, 139, 255)),
        "bronze.png": ("Bronze", (205, 127, 50, 255)),
        "gold.png": ("Gold", (255, 215, 0, 255)),
        "cedar_wood.png": ("Cedar Wood", (139, 69, 19, 255)),
    }
    
    for filename, (name, color) in textures.items():
        img = create_texture(name, color)
        img.save(TEXTURE_DIR / filename)
        print(f"  Created: textures/{filename}")
    
    print("\n✅ All placeholders generated successfully!")
    print(f"\nPortraits: {PORTRAIT_DIR}")
    print(f"Textures: {TEXTURE_DIR}")
    print(f"Cover: {COVER_DIR}")
    print("\nNote: These are placeholder images. Replace them with proper artwork.")
    print("For actual music tracks, add OGG files to the music/ directory.")

if __name__ == "__main__":
    main()
