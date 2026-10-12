#!/usr/bin/env python3
"""
Create 3D models of Mesopotamian ziggurats using Blender Python API.

Usage:
    blender --background --python create_ziggurat.py -- ziggurat_simple output.obj
    blender --background --python create_ziggurat.py -- ziggurat_etemenanki output.glb

Requirements:
    - Blender installed
    - Run with: blender --background --python create_ziggurat.py
"""

import bpy
import sys
import os
from pathlib import Path

# Get arguments
model_type = sys.argv[-2] if len(sys.argv) > 1 else "ziggurat_simple"
output_path = sys.argv[-1] if len(sys.argv) > 2 else "output.glb"

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Function to create a simple ziggurat
# Ziggurats have multiple tiers/levels that step inward
def create_simple_ziggurat(name="Ziggurat", tiers=4, base_size=10, tier_height=2, tier_reduction=0.8):
    """Create a simple stepped ziggurat"""
    
    # Start with the base cube
    bpy.ops.mesh.primitive_cube_add(size=base_size, location=(0, 0, tier_height/2))
    base_cube = bpy.context.object
    base_cube.name = f"{name}_Base"
    
    # Create each tier
    for i in range(1, tiers):
        size = base_size * (tier_reduction ** i)
        height = tier_height * (i + 1)
        
        bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, height - tier_height/2))
        tier_cube = bpy.context.object
        tier_cube.name = f"{name}_Tier_{i}"
    
    # Select all and join
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    ziggurat = bpy.context.object
    ziggurat.name = name
    
    # Add a brick-like material
    mat = bpy.data.materials.new(name="Ziggurat_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.6, 0.45, 0.3, 1)  # Sandy brown
        bsdf.inputs['Roughness'].default_value = 0.8
    
    ziggurat.data.materials.append(mat)
    
    return ziggurat


def create_etemenanki_ziggurat(name="Ziggurat_Etemenanki", base_size=20, tiers=7):
    """Create the Great Ziggurat of Babylon (Etemenanki)"""
    
    # Etemenanki was believed to be a massive structure with 7 tiers
    # Each tier had different colors dedicated to celestial bodies
    colors = {
        0: (0, 0, 0, 1),        # Black (base/platform)
        1: (1, 1, 1, 1),        # White (Nibu - Jupiter)
        2: (0.6, 0.4, 0.2, 1), # Orange/Brown (Anu - Sky god)
        3: (0.8, 0.2, 0.2, 1), # Red (Enlil - Air god)
        4: (1, 0.8, 0, 1),     # Yellow/Gold (Inanna/Ishtar - Venus)
        5: (0.2, 0.6, 1, 1),   # Blue (Nanna/Sin - Moon)
        6: (0.5, 0.5, 0.5, 1) # Silver (Utu/Shamash - Sun)
    }
    
    current_size = base_size
    current_height = 0
    
    for i in range(tiers):
        height = 3 if i == 0 else 2.5  # Base is taller
        
        bpy.ops.mesh.primitive_cube_add(size=current_size, location=(0, 0, current_height + height/2))
        tier = bpy.context.object
        tier.name = f"{name}_Tier_{i}"
        
        # Add material with celestial color
        mat = bpy.data.materials.new(name=f"Tier_{i}_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = colors[i]
            bsdf.inputs['Roughness'].default_value = 0.7
        
        tier.data.materials.append(mat)
        
        current_height += height
        current_size *= 0.85  # Each tier is 15% smaller
    
    # Select all and join
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    ziggurat = bpy.context.object
    ziggurat.name = name
    
    return ziggurat


def create_temple_complex(name="Temple_Complex", ziggurat_tiers=4, with_walls=True):
    """Create a complete temple complex with ziggurat and surrounding structures"""
    
    # Create main ziggurat
    ziggurat = create_simple_ziggurat(f"{name}_Ziggurat", tiers=ziggurat_tiers, base_size=15)
    
    # Create temple building at the base
    bpy.ops.mesh.primitive_cube_add(size=8, location=(20, 0, 2))
    temple = bpy.context.object
    temple.name = f"{name}_Temple"
    
    # Add temple material
    mat = bpy.data.materials.new(name="Temple_Material")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.7, 0.6, 0.5, 1)  # Sandstone
        bsdf.inputs['Roughness'].default_value = 0.8
    temple.data.materials.append(mat)
    
    # Create surrounding walls if requested
    if with_walls:
        # Create rectangular wall
        bpy.ops.mesh.primitive_cube_add(size=50, location=(0, 0, 1.5))
        wall = bpy.context.object
        wall.scale = (5, 0.5, 2)
        wall.name = f"{name}_Wall"
        
        # Add wall material
        mat = bpy.data.materials.new(name="Wall_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get('Principled BSDF')
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.55, 0.45, 0.35, 1)  # Mud brick
            bsdf.inputs['Roughness'].default_value = 0.9
        wall.data.materials.append(mat)
    
    return ziggurat


def create_ziggurat_staircase(name="Ziggurat_Stairs", tiers=4, base_size=10):
    """Create a ziggurat with external staircases"""
    
    ziggurat = create_simple_ziggurat(f"{name}_Base", tiers=tiers, base_size=base_size)
    ziggurat.name = name
    
    # Add staircase (simplified as a ramp for now)
    # In real ziggurats, stairs were on the sides
    bpy.ops.mesh.primitive_cube_add(size=3, location=(base_size/2 + 1, 0, 1))
    stairs = bpy.context.object
    stairs.scale = (2, 5, 0.5)
    stairs.rotation_euler = (0.4, 0, 0)  # Tilt to create ramp
    stairs.name = f"{name}_Stairs"
    
    return ziggurat


def create_mesopotamian_temple(name="Mesopotamian_Temple", width=15, length=20, height=6):
    """Create a typical Mesopotamian temple building"""
    
    # Create main structure
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
    temple = bpy.context.object
    temple.scale = (width, length, height)
    temple.name = name
    
    # Add architectural details (simplified)
    # Create columns/entrance
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, length/2 + 1, 0))
    entrance = bpy.context.object
    entrance.scale = (1, 0.5, height * 0.8)
    entrance.name = f"{name}_Entrance"
    
    # Add material
    mat = bpy.data.materials.new(name="Temple_Stone")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.65, 0.55, 0.45, 1)  # Limestone
        bsdf.inputs['Roughness'].default_value = 0.75
    
    for obj in [temple, entrance]:
        obj.data.materials.append(mat)
    
    # Join objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    return bpy.context.object


def create_city_gate(name="City_Gate", gate_name="Ishtar_Gate"):
    """Create a Mesopotamian city gate (like the Ishtar Gate)"""
    
    # Main gate arch
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 5))
    gate = bpy.context.object
    gate.scale = (15, 3, 10)
    gate.name = name
    
    # Create arch shape (simplified)
    # Add decorative towers
    for x in [-6, 6]:
        bpy.ops.mesh.primitive_cube_add(size=2, location=(x, 0, 8))
        tower = bpy.context.object
        tower.scale = (2, 3, 6)
        tower.name = f"{name}_Tower_{x}"
    
    # Add glaze material (Ishtar Gate was famous for its blue glazed bricks)
    mat = bpy.data.materials.new(name="Lapis_Lazuli_Glaze")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.1, 0.2, 0.8, 1)  # Deep blue
        bsdf.inputs['Metallic'].default_value = 0.3
        bsdf.inputs['Specular IOR Level'].default_value = 0.5  # Replaces Specular in Blender 4.x
        bsdf.inputs['Roughness'].default_value = 0.3
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.materials.append(mat)
    
    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    return bpy.context.object


def create_ziggurat_with_temple_courtyard(name="Ziggurat_Complex"):
    """Create a complete ziggurat complex with temple and courtyard"""
    
    # Create ziggurat
    ziggurat = create_simple_ziggurat(f"{name}_Ziggurat", tiers=5, base_size=12)
    
    # Create temple at top
    bpy.ops.mesh.primitive_cube_add(size=4, location=(0, 0, 15))
    temple = bpy.context.object
    temple.name = f"{name}_Temple"
    
    # Create courtyard walls
    wall_size = 30
    bpy.ops.mesh.primitive_cube_add(size=wall_size, location=(0, wall_size/2, 1))
    north_wall = bpy.context.object
    north_wall.scale = (wall_size, 1, 3)
    north_wall.name = f"{name}_North_Wall"
    
    bpy.ops.mesh.primitive_cube_add(size=wall_size, location=(0, -wall_size/2, 1))
    south_wall = bpy.context.object
    south_wall.scale = (wall_size, 1, 3)
    south_wall.name = f"{name}_South_Wall"
    
    bpy.ops.mesh.primitive_cube_add(size=wall_size, location=(wall_size/2, 0, 1))
    east_wall = bpy.context.object
    east_wall.scale = (1, wall_size, 3)
    east_wall.name = f"{name}_East_Wall"
    
    bpy.ops.mesh.primitive_cube_add(size=wall_size, location=(-wall_size/2, 0, 1))
    west_wall = bpy.context.object
    west_wall.scale = (1, wall_size, 3)
    west_wall.name = f"{name}_West_Wall"
    
    # Add materials
    sand_material = bpy.data.materials.new(name="Sand_Stone")
    sand_material.use_nodes = True
    bsdf = sand_material.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.7, 0.6, 0.5, 1)
        bsdf.inputs['Roughness'].default_value = 0.8
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.materials.append(sand_material)
    
    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    return bpy.context.object


# Main: Create model based on type
print(f"Creating model: {model_type}")
print(f"Output path: {output_path}")

# Create the requested model
if model_type == "ziggurat_simple":
    obj = create_simple_ziggurat("Ziggurat")
elif model_type == "ziggurat_etemenanki":
    obj = create_etemenanki_ziggurat("Etemenanki")
elif model_type == "ziggurat_stairs":
    obj = create_ziggurat_staircase("Ziggurat_with_Stairs")
elif model_type == "temple":
    obj = create_mesopotamian_temple("Mesopotamian_Temple")
elif model_type == "city_gate":
    obj = create_city_gate("Ishtar_Gate")
elif model_type == "complex":
    obj = create_ziggurat_with_temple_courtyard("Ziggurat_Complex")
else:
    obj = create_simple_ziggurat("Ziggurat")

# Select the object
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Export based on file extension
output_path = Path(output_path)
if output_path.suffix.lower() == '.glb':
    bpy.ops.export_scene.gltf(filepath=str(output_path), export_format='GLB')
elif output_path.suffix.lower() == '.glb' or output_path.suffix.lower() == '.gltf':
    bpy.ops.export_scene.gltf(filepath=str(output_path))
elif output_path.suffix.lower() == '.obj':
    bpy.ops.export_scene.obj(filepath=str(output_path))
elif output_path.suffix.lower() == '.fbx':
    bpy.ops.export_scene.fbx(filepath=str(output_path))
else:
    # Default to GLB
    bpy.ops.export_scene.gltf(filepath=str(output_path), export_format='GLB')

print(f"✅ Model exported to: {output_path}")
