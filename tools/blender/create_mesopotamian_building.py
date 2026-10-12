#!/usr/bin/env python3
"""
Create additional Mesopotamian buildings using Blender Python API.

Usage:
    blender --background --python create_mesopotamian_building.py -- palace output.glb
    blender --background --python create_mesopotamian_building.py -- residential output.glb
    blender --background --python create_mesopotamian_building.py -- marketplace output.glb
"""

import bpy
import sys
from pathlib import Path

# Get arguments
building_type = sys.argv[-2] if len(sys.argv) > 1 else "palace"
output_path = sys.argv[-1] if len(sys.argv) > 2 else "output.glb"

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()


def create_palace(name="Royal_Palace"):
    """Create a Mesopotamian royal palace with throne room"""
    
    # Main palace building - rectangular with multiple sections
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3))
    main = bpy.context.object
    main.scale = (30, 20, 6)
    main.name = f"{name}_Main"
    
    # Throne room (raised section)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 5))
    throne_room = bpy.context.object
    throne_room.scale = (15, 10, 4)
    throne_room.name = f"{name}_Throne_Room"
    
    # Towers at corners
    for x, y, tower_name in [(-12, -8, "SW"), (-12, 8, "NW"), (12, -8, "SE"), (12, 8, "NE")]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 4))
        tower = bpy.context.object
        tower.scale = (4, 4, 8)
        tower.name = f"{name}_Tower_{tower_name}"
    
    # Add materials
    mat_brick = bpy.data.materials.new(name="Mud_Brick")
    mat_brick.use_nodes = True
    bsdf = mat_brick.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.55, 0.45, 0.35, 1)
        bsdf.inputs['Roughness'].default_value = 0.9
    
    mat_wood = bpy.data.materials.new(name="Cedar_Wood")
    mat_wood.use_nodes = True
    bsdf = mat_wood.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.3, 0.2, 0.1, 1)
        bsdf.inputs['Roughness'].default_value = 0.6
    
    # Assign materials
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if "Tower" in obj.name:
                obj.data.materials.append(mat_brick)
            else:
                obj.data.materials.append(mat_brick)
    
    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    return bpy.context.object


def create_residential_building(name="Residential_House"):
    """Create a typical Mesopotamian residential building"""
    
    # Main house - simple rectangular mud brick structure
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
    house = bpy.context.object
    house.scale = (8, 6, 3)
    house.name = name
    
    # Flat roof (Mesopotamian houses had flat roofs)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3.25))
    roof = bpy.context.object
    roof.scale = (8.5, 6.5, 0.5)
    roof.name = f"{name}_Roof"
    
    # Small courtyard wall
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -4, 1))
    wall = bpy.context.object
    wall.scale = (10, 0.5, 2)
    wall.name = f"{name}_Wall"
    
    # Add material
    mat = bpy.data.materials.new(name="Mud_Brick_Residential")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.6, 0.5, 0.4, 1)
        bsdf.inputs['Roughness'].default_value = 0.95
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.materials.append(mat)
    
    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    return bpy.context.object


def create_marketplace(name="Marketplace"):
    """Create a Mesopotamian marketplace with stalls"""
    
    # Ground plane
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = f"{name}_Ground"
    
    # Market stalls (simple representations)
    for i, loc in enumerate([(-8, 0), (0, 0), (8, 0), (-8, 8), (8, 8)]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], 1.5))
        stall = bpy.context.object
        stall.scale = (3, 2, 2.5)
        stall.name = f"{name}_Stall_{i}"
        
        # Stall roof
        bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], 2.75))
        roof = bpy.context.object
        roof.scale = (3.5, 2.5, 0.3)
        roof.name = f"{name}_Stall_Roof_{i}"
    
    # Central trading platform
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -10, 1))
    platform = bpy.context.object
    platform.scale = (10, 5, 2)
    platform.name = f"{name}_Platform"
    
    # Add materials
    mat_ground = bpy.data.materials.new(name="Packed_Earth")
    mat_ground.use_nodes = True
    bsdf = mat_ground.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.4, 0.35, 0.25, 1)
        bsdf.inputs['Roughness'].default_value = 1.0
    
    mat_stall = bpy.data.materials.new(name="Market_Stall_Wood")
    mat_stall.use_nodes = True
    bsdf = mat_stall.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.4, 0.3, 0.2, 1)
        bsdf.inputs['Roughness'].default_value = 0.7
    
    # Assign materials
    ground.data.materials.append(mat_ground)
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != ground:
            obj.data.materials.append(mat_stall)
    
    # Join all except ground
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj != ground:
            obj.select_set(True)
    bpy.ops.object.join()
    
    return ground


def create_grain_storage(name="Grain_Storage"):
    """Create a Mesopotamian grain storage building"""
    
    # Large cylindrical storage (simplified as cube with rounded appearance)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2))
    storage = bpy.context.object
    storage.scale = (10, 10, 4)
    storage.name = name
    
    # Small access door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4.5, 1))
    door = bpy.context.object
    door.scale = (1.5, 0.5, 1.5)
    door.name = f"{name}_Door"
    
    # Add material
    mat = bpy.data.materials.new(name="Storage_Mud")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.5, 0.45, 0.35, 1)
        bsdf.inputs['Roughness'].default_value = 0.9
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.data.materials.append(mat)
    
    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    return bpy.context.object


def create_shrine(name="Shrine"):
    """Create a small Mesopotamian shrine"""
    
    # Base platform
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
    base = bpy.context.object
    base.scale = (5, 5, 1)
    base.name = f"{name}_Base"
    
    # Shrine structure
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2))
    shrine = bpy.context.object
    shrine.scale = (3, 3, 3)
    shrine.name = name
    
    # Decorative pillars
    for x in [-1, 1]:
        for y in [-1, 1]:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x * 1.5, y * 1.5, 1.5))
            pillar = bpy.context.object
            pillar.scale = (0.3, 0.3, 2)
            pillar.name = f"{name}_Pillar_{x}_{y}"
    
    # Add materials
    mat_stone = bpy.data.materials.new(name="Shrine_Stone")
    mat_stone.use_nodes = True
    bsdf = mat_stone.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.4, 0.4, 0.4, 1)
        bsdf.inputs['Roughness'].default_value = 0.7
    
    mat_gold = bpy.data.materials.new(name="Gold_Trim")
    mat_gold.use_nodes = True
    bsdf = mat_gold.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.2, 1)
        bsdf.inputs['Metallic'].default_value = 0.8
        bsdf.inputs['Roughness'].default_value = 0.2
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if "Pillar" in obj.name:
                obj.data.materials.append(mat_gold)
            else:
                obj.data.materials.append(mat_stone)
    
    # Join all
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.join()
    
    return bpy.context.object


# Main: Create building based on type
print(f"Creating building: {building_type}")
print(f"Output path: {output_path}")

# Create the requested building
if building_type == "palace":
    obj = create_palace("Royal_Palace")
elif building_type == "residential":
    obj = create_residential_building("Residential_House")
elif building_type == "marketplace":
    obj = create_marketplace("Marketplace")
elif building_type == "grain_storage":
    obj = create_grain_storage("Grain_Storage")
elif building_type == "shrine":
    obj = create_shrine("Shrine")
else:
    obj = create_palace("Royal_Palace")

# Select the object
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Export based on file extension
output_path = Path(output_path)
if output_path.suffix.lower() in ['.glb', '.gltf']:
    bpy.ops.export_scene.gltf(filepath=str(output_path), export_format='GLB')
elif output_path.suffix.lower() == '.obj':
    bpy.ops.export_scene.obj(filepath=str(output_path))
elif output_path.suffix.lower() == '.fbx':
    bpy.ops.export_scene.fbx(filepath=str(output_path))
else:
    # Default to GLB
    bpy.ops.export_scene.gltf(filepath=str(output_path), export_format='GLB')

print(f"✅ Building exported to: {output_path}")
