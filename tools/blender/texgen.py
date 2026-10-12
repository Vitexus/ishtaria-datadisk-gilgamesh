#!/usr/bin/env blender --background --python
"""
Texture Generator for Mesopotamian Materials
Creates PBR texture materials for use in Blender models

This script generates texture nodes and saves them as images
for use in Ishtaria 3D models.

Materials included:
- Mud Brick
- Plaster
- Stone (Limestone, Basalt)
- Lapis Lazuli
- Carnelian
- Gold
- Bronze
- Cedar Wood
- Leather
- Wool/Kaunakes
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Color

# Output directory
OUTPUT_DIR = "//media/textures"
TEXTURE_SIZE = 1024  # 1024x1024 textures

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    path = bpy.path.abspath(OUTPUT_DIR)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def create_mud_brick_texture(name="mud_brick", size=TEXTURE_SIZE):
    """Create mud brick PBR texture"""
    # Create a new image
    image = bpy.data.images.new(name=f"{name}_albedo", width=size, height=size, alpha=True)
    image.generated_type = 'CLOUDS'
    image.generated_width = size
    image.generated_height = size
    
    # Fill with brick pattern (simplified)
    pixels = [0.0] * (size * size * 4)
    
    # Base color: tan/brown
    base_color = (0.55, 0.27, 0.07, 1.0)
    
    # Create brick pattern
    brick_height = 20
    brick_width = 40
    mortar_color = (0.4, 0.2, 0.05, 1.0)
    
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            
            # Calculate brick position
            brick_y = y % (brick_height + 2)
            brick_x_start = (x // brick_width) * brick_width
            offset = (y // brick_height) * (brick_width // 2)
            brick_x = (x - brick_x_start - offset) % brick_width
            
            # Check if in mortar
            if brick_y < 2 or brick_y >= brick_height:
                pixels[i:i+4] = list(mortar_color)
            elif brick_x < 2:
                pixels[i:i+4] = list(mortar_color)
            else:
                # Brick with slight variation
                variation = 0.1 * (math.sin(x * 0.1) + math.cos(y * 0.1))
                brick_color = (
                    max(0, min(1, base_color[0] + variation)),
                    max(0, min(1, base_color[1] + variation)),
                    max(0, min(1, base_color[2] + variation)),
                    1.0
                )
                pixels[i:i+4] = list(brick_color)
    
    image.pixels = pixels
    image.pack()
    
    # Save to file
    ensure_output_dir()
    image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}_albedo.png")
    image.save()
    
    return image

def create_plaster_texture(name="plaster", size=TEXTURE_SIZE):
    """Create white plaster PBR texture"""
    image = bpy.data.images.new(name=f"{name}_albedo", width=size, height=size, alpha=True)
    
    # Create smooth plaster with slight variations
    pixels = [0.0] * (size * size * 4)
    base_color = (0.96, 0.96, 0.92, 1.0)
    
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            
            # Slight variation for realism
            variation = 0.05 * (math.sin(x * 0.05) + math.cos(y * 0.05))
            color = (
                max(0, min(1, base_color[0] + variation)),
                max(0, min(1, base_color[1] + variation)),
                max(0, min(1, base_color[2] + variation)),
                1.0
            )
            pixels[i:i+4] = list(color)
    
    image.pixels = pixels
    image.pack()
    image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}_albedo.png")
    image.save()
    
    return image

def create_stone_texture(name="stone", size=TEXTURE_SIZE):
    """Create stone PBR texture"""
    image = bpy.data.images.new(name=f"{name}_albedo", width=size, height=size, alpha=True)
    
    # Create stone pattern
    pixels = [0.0] * (size * size * 4)
    base_color = (0.7, 0.7, 0.7, 1.0)
    
    # Use noise for stone variation
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            
            # Stone color variation
            variation = 0.2 * (math.sin(x * 0.1) + math.cos(y * 0.1) + 
                         math.sin(x * 0.05 + y * 0.05))
            color = (
                max(0, min(1, base_color[0] + variation)),
                max(0, min(1, base_color[1] + variation)),
                max(0, min(1, base_color[2] + variation)),
                1.0
            )
            pixels[i:i+4] = list(color)
    
    image.pixels = pixels
    image.pack()
    image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}_albedo.png")
    image.save()
    
    return image

def create_lapis_lazuli_texture(name="lapis_lazuli", size=TEXTURE_SIZE):
    """Create lapis lazuli PBR texture"""
    image = bpy.data.images.new(name=f"{name}_albedo", width=size, height=size, alpha=True)
    
    pixels = [0.0] * (size * size * 4)
    base_color = (0.22, 0.38, 0.55, 1.0)
    
    # Deep blue with gold flecks
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            
            # Random gold flecks (pyrite)
            if (x + y) % 100 < 3 and (x * y) % 1000 < 10:
                pixels[i:i+4] = [0.83, 0.69, 0.22, 1.0]  # Gold
            else:
                variation = 0.05 * (math.sin(x * 0.05) + math.cos(y * 0.05))
                color = (
                    max(0, min(1, base_color[0] + variation)),
                    max(0, min(1, base_color[1] + variation)),
                    max(0, min(1, base_color[2] + variation)),
                    1.0
                )
                pixels[i:i+4] = list(color)
    
    image.pixels = pixels
    image.pack()
    image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}_albedo.png")
    image.save()
    
    return image

def create_gold_texture(name="gold", size=TEXTURE_SIZE):
    """Create gold PBR texture"""
    image = bpy.data.images.new(name=f"{name}_albedo", width=size, height=size, alpha=True)
    
    pixels = [0.0] * (size * size * 4)
    base_color = (0.83, 0.69, 0.22, 1.0)
    
    # Gold with slight variation and shine
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            
            # Metallic shine effect
            shine = 0.1 * (1 - abs((x - size/2) / (size/2)) * (1 - abs((y - size/2) / (size/2))))
            color = (
                max(0, min(1, base_color[0] + shine)),
                max(0, min(1, base_color[1] + shine)),
                max(0, min(1, base_color[2] + shine)),
                1.0
            )
            pixels[i:i+4] = list(color)
    
    image.pixels = pixels
    image.pack()
    image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}_albedo.png")
    image.save()
    
    return image

def create_cedar_wood_texture(name="cedar_wood", size=TEXTURE_SIZE):
    """Create cedar wood PBR texture"""
    image = bpy.data.images.new(name=f"{name}_albedo", width=size, height=size, alpha=True)
    
    pixels = [0.0] * (size * size * 4)
    base_color = (0.55, 0.27, 0.07, 1.0)
    
    # Wood grain pattern
    for y in range(size):
        for x in range(size):
            i = (y * size + x) * 4
            
            # Wood grain
            grain = 0.1 * (math.sin(x * 0.5 + y * 0.1) + math.cos(y * 0.3))
            color = (
                max(0, min(1, base_color[0] + grain)),
                max(0, min(1, base_color[1] + grain)),
                max(0, min(1, base_color[2] + grain)),
                1.0
            )
            pixels[i:i+4] = list(color)
    
    image.pixels = pixels
    image.pack()
    image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}_albedo.png")
    image.save()
    
    return image

def create_roughness_maps():
    """Create roughness maps for PBR materials"""
    textures = {
        "mud_brick_roughness": 0.9,
        "plaster_roughness": 0.6,
        "stone_roughness": 0.7,
        "lapis_lazuli_roughness": 0.1,
        "gold_roughness": 0.1,
        "cedar_wood_roughness": 0.7,
        "leather_roughness": 0.8,
        "wool_roughness": 0.9
    }
    
    for name, roughness in textures.items():
        image = bpy.data.images.new(name=name, width=TEXTURE_SIZE, height=TEXTURE_SIZE, alpha=False)
        pixels = [roughness] * (TEXTURE_SIZE * TEXTURE_SIZE)
        image.pixels = pixels
        image.pack()
        image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}.png")
        image.save()

def create_metallic_maps():
    """Create metallic maps for PBR materials"""
    textures = {
        "mud_brick_metallic": 0.0,
        "plaster_metallic": 0.0,
        "stone_metallic": 0.0,
        "lapis_lazuli_metallic": 0.3,
        "gold_metallic": 1.0,
        "cedar_wood_metallic": 0.0,
        "leather_metallic": 0.0,
        "wool_metallic": 0.0
    }
    
    for name, metallic in textures.items():
        image = bpy.data.images.new(name=name, width=TEXTURE_SIZE, height=TEXTURE_SIZE, alpha=False)
        pixels = [metallic] * (TEXTURE_SIZE * TEXTURE_SIZE)
        image.pixels = pixels
        image.pack()
        image.filepath_raw = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{name}.png")
        image.save()

def main():
    """Main function to generate all textures"""
    print("Generating Mesopotamian PBR textures...")
    
    ensure_output_dir()
    
    # Create albedo maps
    print("Creating albedo maps...")
    create_mud_brick_texture()
    create_plaster_texture()
    create_stone_texture()
    create_lapis_lazuli_texture()
    create_gold_texture()
    create_cedar_wood_texture()
    
    # Create roughness maps
    print("Creating roughness maps...")
    create_roughness_maps()
    
    # Create metallic maps
    print("Creating metallic maps...")
    create_metallic_maps()
    
    print(f"\nTextures saved to: {bpy.path.abspath(OUTPUT_DIR)}")
    print("\nGenerated textures:")
    print("  - mud_brick_albedo.png")
    print("  - plaster_albedo.png")
    print("  - stone_albedo.png")
    print("  - lapis_lazuli_albedo.png")
    print("  - gold_albedo.png")
    print("  - cedar_wood_albedo.png")
    print("  - roughness maps for each")
    print("  - metallic maps for each")
    
    print("\nNote: These are procedural textures. For production, replace with")
    print("high-quality hand-painted or photographed textures.")

if __name__ == "__main__":
    main()
