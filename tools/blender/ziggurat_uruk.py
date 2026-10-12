#!/usr/bin/env blender --background --python
"""
Blender script to create Ziggurat of Uruk
Mesopotamian stepped temple tower
Based on archaeological reconstructions

Scale: 1 Blender unit = 1 meter
Output: media/models/architecture/ziggurat_uruk.glb

Historical Reference:
- Ziggurat of Ur (2100 BCE): 64m x 46m base, ~21m height
- 3 tiered platforms
- Mud brick construction with white plaster finish
- Central staircase
- Temple at summit
"""

import bpy
import bmesh
import math
import os
import sys

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Configuration
OUTPUT_DIR = "//media/models/architecture"
MODEL_NAME = "ziggurat_uruk"

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    path = bpy.path.abspath(OUTPUT_DIR)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def create_material(name, base_color, roughness=0.8, metallic=0.0, specular=0.5):
    """Create a PBR material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # Create nodes
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Specular'].default_value = specular
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_ziggurat():
    """Create the Ziggurat of Uruk with 3 tiers"""
    
    # Dimensions based on Ziggurat of Ur
    # Base tier: 60m x 50m, 8m height
    # Second tier: 45m x 35m, 6m height (total 14m)
    # Third tier: 30m x 20m, 5m height (total 19m)
    # Temple on top: 15m x 10m, 3m height (total 22m)
    
    base_size = (60, 50)
    base_height = 8
    
    second_size = (45, 35)
    second_height = 6
    
    third_size = (30, 20)
    third_height = 5
    
    temple_size = (15, 10)
    temple_height = 3
    
    # Materials
    mud_brick = create_material("MudBrick", (0.55, 0.27, 0.07, 1), roughness=0.9, metallic=0.0)
    plaster = create_material("Plaster", (0.96, 0.96, 0.92, 1), roughness=0.6, metallic=0.0)
    stone = create_material("Stone", (0.7, 0.7, 0.7, 1), roughness=0.7, metallic=0.0)
    
    # Create base tier
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, base_height/2))
    base = bpy.context.active_object
    base.name = "Ziggurat_Base"
    base.scale = (base_size[0], base_size[1], base_height)
    base.data.materials.append(mud_brick)
    
    # Create second tier
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, base_height + second_height/2))
    tier2 = bpy.context.active_object
    tier2.name = "Ziggurat_Tier2"
    tier2.scale = (second_size[0], second_size[1], second_height)
    tier2.data.materials.append(mud_brick)
    
    # Create third tier
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, base_height + second_height + third_height/2))
    tier3 = bpy.context.active_object
    tier3.name = "Ziggurat_Tier3"
    tier3.scale = (third_size[0], third_size[1], third_height)
    tier3.data.materials.append(mud_brick)
    
    # Create temple on top
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, base_height + second_height + third_height + temple_height/2))
    temple = bpy.context.active_object
    temple.name = "Temple"
    temple.scale = (temple_size[0], temple_size[1], temple_height)
    temple.data.materials.append(plaster)
    
    # Create staircase
    create_staircase(base_height + second_height + third_height)
    
    # Add buttresses
    add_buttresses(base_size, base_height)
    add_buttresses(second_size, second_height, base_height)
    
    # Add niches
    add_niches(base_size, base_height)
    add_niches(second_size, second_height, base_height)
    
    # Add plaster coating to upper tiers
    add_plaster_coating(second_size, second_height, base_height)
    add_plaster_coating(third_size, third_height, base_height + second_height)
    
    # Parent all objects
    for obj in bpy.context.scene.objects:
        if obj.name != "Ziggurat_Base":
            obj.parent = base
    
    return base

def create_staircase(base_height):
    """Create central staircase"""
    # Staircase: 8m wide, 20m long, steps every 0.3m rise
    stair_width = 8
    stair_length = 20
    step_height = 0.3
    
    # Create base of staircase
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, base_height/2))
    stairs = bpy.context.active_object
    stairs.name = "Staircase_Base"
    stairs.scale = (stair_length, stair_width, 1)
    
    # Create individual steps
    num_steps = int((base_height + 6 + 5) / step_height)  # Total height to third tier
    
    for i in range(num_steps):
        height = i * step_height
        
        # Tread (horizontal part)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, base_height + height + step_height/2))
        tread = bpy.context.active_object
        tread.name = f"Step_{i}_Tread"
        tread.scale = (2, stair_width - 0.5, step_height/2)
        tread.location.x = -stair_length/2 + 2 + i * 0.5
        
        # Risers (vertical parts) - skip for performance, use single plane
    
    # Simplify: Create single staircase mesh with ramp
    bpy.ops.object.select_all(action='DESELECT')
    stairs.select_set(True)
    bpy.ops.object.delete()
    
    for obj in [o for o in bpy.context.scene.objects if o.name.startswith("Step_")]:
        obj.select_set(True)
    bpy.ops.object.delete()
    
    # Create simplified staircase as single mesh
    bm = bmesh.new()
    
    # Create staircase profile
    width = stair_width
    length = stair_length
    total_height = base_height + 6 + 5  # To third tier
    
    # Vertices
    v1 = bm.verts.new((-length/2, -width/2, 0))
    v2 = bm.verts.new((length/2, -width/2, 0))
    v3 = bm.verts.new((length/2, width/2, 0))
    v4 = bm.verts.new((-length/2, width/2, 0))
    
    v5 = bm.verts.new((-length/2 + 2, -width/2 + 0.5, total_height))
    v6 = bm.verts.new((length/2 - 2, -width/2 + 0.5, total_height))
    v7 = bm.verts.new((length/2 - 2, width/2 - 0.5, total_height))
    v8 = bm.verts.new((-length/2 + 2, width/2 - 0.5, total_height))
    
    # Faces
    bm.faces.new((v1, v2, v3, v4))
    bm.faces.new((v1, v4, v8, v5))
    bm.faces.new((v4, v3, v7, v8))
    bm.faces.new((v2, v1, v5, v6))
    bm.faces.new((v3, v2, v6, v7))
    bm.faces.new((v5, v6, v7, v8))
    
    # Create mesh
    me = bpy.data.meshes.new("Staircase")
    bm.to_mesh(me)
    bm.free()
    
    stairs = bpy.data.objects.new("Staircase", me)
    bpy.context.collection.objects.link(stairs)
    stairs.location = (0, 0, 0)
    
    # Assign material
    stone_mat = create_material("Stone_Stairs", (0.6, 0.6, 0.6, 1), roughness=0.8)
    stairs.data.materials.append(stone_mat)

def add_buttresses(size, height, offset_z=0):
    """Add buttresses to ziggurat tier"""
    buttress_width = 1.5
    buttress_depth = 1.0
    buttress_height = height
    spacing = 5.0  # meters between buttresses
    
    half_size_x = size[0] / 2
    half_size_y = size[1] / 2
    
    # Buttresses on long sides
    for x in range(-int(half_size_x - 1), int(half_size_x - 1), int(spacing)):
        # North side
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, half_size_y + buttress_depth/2, offset_z + height/2))
        buttress = bpy.context.active_object
        buttress.name = f"Buttress_N_{x}"
        buttress.scale = (buttress_width, buttress_depth, buttress_height)
        buttress.data.materials.append(bpy.data.materials["MudBrick"])
        
        # South side
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -half_size_y - buttress_depth/2, offset_z + height/2))
        buttress = bpy.context.active_object
        buttress.name = f"Buttress_S_{x}"
        buttress.scale = (buttress_width, buttress_depth, buttress_height)
        buttress.data.materials.append(bpy.data.materials["MudBrick"])
    
    # Buttresses on short sides
    for y in range(-int(half_size_y - 1), int(half_size_y - 1), int(spacing)):
        # East side
        bpy.ops.mesh.primitive_cube_add(size=1, location=(half_size_x + buttress_depth/2, y, offset_z + height/2))
        buttress = bpy.context.active_object
        buttress.name = f"Buttress_E_{y}"
        buttress.scale = (buttress_depth, buttress_width, buttress_height)
        buttress.data.materials.append(bpy.data.materials["MudBrick"])
        
        # West side
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-half_size_x - buttress_depth/2, y, offset_z + height/2))
        buttress = bpy.context.active_object
        buttress.name = f"Buttress_W_{y}"
        buttress.scale = (buttress_depth, buttress_width, buttress_height)
        buttress.data.materials.append(bpy.data.materials["MudBrick"])

def add_niches(size, height, offset_z=0):
    """Add decorative niches"""
    niche_width = 2.0
    niche_height = 2.0
    niche_depth = 0.5
    spacing = 8.0
    
    half_size_x = size[0] / 2
    half_size_y = size[1] / 2
    
    # Niches on all sides
    for x in range(-int(half_size_x - 1), int(half_size_x - 1), int(spacing)):
        for side in ['N', 'S']:
            y = half_size_y + 0.5 if side == 'N' else -half_size_y - 0.5
            
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, offset_z + height - niche_height/2))
            niche = bpy.context.active_object
            niche.name = f"Niche_{side}_{x}"
            niche.scale = (niche_width, niche_depth, niche_height)
            
            # Create niche cavity
            bpy.ops.object.modifier_add(type='BOOL')
            niche.modifiers["Bool"].operation = 'DIFFERENCE'
            # Would need target, simplified for now
    
    # Simplified: Just create niche shapes
    for obj in [o for o in bpy.context.scene.objects if o.name.startswith("Niche_")]:
        obj.select_set(True)
    if [o for o in bpy.context.scene.objects if o.name.startswith("Niche_")]:
        bpy.ops.object.delete()

def add_plaster_coating(size, height, offset_z):
    """Add white plaster coating to tier"""
    plaster_thickness = 0.2
    
    half_size_x = size[0] / 2 - plaster_thickness
    half_size_y = size[1] / 2 - plaster_thickness
    half_height = height / 2
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, offset_z + half_height))
    plaster = bpy.context.active_object
    plaster.name = f"Plaster_{offset_z}"
    plaster.scale = (size[0] - 2*plaster_thickness, 
                     size[1] - 2*plaster_thickness, 
                     height - plaster_thickness)
    plaster.location.z = offset_z + half_height
    
    # Position on top surface and sides
    plaster.data.materials.append(bpy.data.materials["Plaster"])

def add_entrance():
    """Add main entrance to ziggurat"""
    entrance_width = 10
    entrance_height = 6
    entrance_depth = 3
    
    # Create entrance arch
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -30, 2))
    entrance = bpy.context.active_object
    entrance.name = "Entrance"
    entrance.scale = (entrance_width, entrance_depth, entrance_height)
    entrance.data.materials.append(bpy.data.materials["Stone"])
    
    # Add decorative elements
    # This is a simplified version

def export_model():
    """Export the model as GLB"""
    ensure_output_dir()
    
    # Select all objects
    bpy.ops.object.select_all(action='SELECT')
    
    # Export path
    export_path = os.path.join(bpy.path.abspath(OUTPUT_DIR), f"{MODEL_NAME}.glb")
    
    # Export settings
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLB',
        use_selection=True,
        export_materials='EXPORT',
        export_textures=True,
        export_normals=True,
        export_tangents=True,
        export_apply=True  # Apply modifiers
    )
    
    print(f"Exported ziggurat to: {export_path}")

def main():
    """Main function"""
    print("Creating Ziggurat of Uruk...")
    
    # Create ziggurat
    ziggurat = create_ziggurat()
    
    # Add entrance
    add_entrance()
    
    # Set up camera for preview
    bpy.ops.object.camera_add(location=(100, -100, 50))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Set up lighting
    bpy.ops.object.light_add(type='SUN', location=(50, -50, 100))
    light = bpy.context.active_object
    light.data.energy = 5.0
    
    bpy.ops.object.light_add(type='HEMI', location=(0, 0, 100))
    light2 = bpy.context.active_object
    light2.data.energy = 2.0
    
    print("Ziggurat created!")
    print(f"Total objects: {len(bpy.context.scene.objects)}")
    
    # Export model
    export_model()
    
    print("Done!")

if __name__ == "__main__":
    main()
