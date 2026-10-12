#!/usr/bin/env blender --background --python
"""
Blender script to create Gilgamesh character model
King of Uruk, two-thirds god, one-third man

Scale: 1 Blender unit = 1 meter
Output: media/models/characters/gilgamesh.glb

Historical Reference:
- Early Dynastic period (c. 2700 BCE)
- Statues of Gudea (2120 BCE) as reference
- Standard of Ur royal figures
- Descriptions from Epic of Gilgamesh

Costume:
- Golden diadem/crown with lapis lazuli
- White linen tunic with gold embroidery
- Kaunakes (sheep-fleece skirt)
- Leather belt with gold buckle
- Sandals
- Jewelry: necklace, bracelets, signet ring
- Short beard (curled)
- Short to medium hair
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
OUTPUT_DIR = "//media/models/characters"
MODEL_NAME = "gilgamesh"
CHARACTER_HEIGHT = 2.0  # Gilgamesh is taller than normal men

def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    path = bpy.path.abspath(OUTPUT_DIR)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def create_material(name, base_color, roughness=0.8, metallic=0.0, specular=0.5, emission=0.0):
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
    bsdf.inputs['Emission'].default_value = emission
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    
    # Link nodes
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_human_base(height):
    """Create simplified human base mesh"""
    # Create a simple humanoid shape using metaballs or primitives
    # This is a placeholder - for production, use a proper base mesh
    
    # Create body (cylinder)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=0.3,
        depth=height * 0.6,
        location=(0, 0, height * 0.3)
    )
    body = bpy.context.active_object
    body.name = "Body"
    
    # Create head (sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=32,
        ring_count=16,
        radius=0.2,
        location=(0, 0, height * 0.75)
    )
    head = bpy.context.active_object
    head.name = "Head"
    
    # Create arms
    for side in ['Left', 'Right']:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=0.08,
            depth=height * 0.35,
            location=(0.35 if side == 'Right' else -0.35, 0, height * 0.5)
        )
        arm = bpy.context.active_object
        arm.name = f"Arm_{side}"
        arm.rotation_euler.z = math.radians(15 if side == 'Right' else -15)
    
    # Create legs
    for side in ['Left', 'Right']:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=0.1,
            depth=height * 0.4,
            location=(0.15 if side == 'Right' else -0.15, 0, height * 0.1)
        )
        leg = bpy.context.active_object
        leg.name = f"Leg_{side}"
    
    return body, head

def create_kaunakes_skirt():
    """Create kaunakes (sheep-fleece skirt) - signature Mesopotamian garment"""
    # Kaunakes: skirt with horizontal rows of tufts
    height = 0.6  # From waist to knees
    radius = 0.35  # Waist radius
    tuft_height = 0.05
    tuft_spacing = 0.08
    
    bm = bmesh.new()
    
    # Create base cylinder
    num_verts = 32
    for i in range(num_verts):
        angle = 2 * math.pi * i / num_verts
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        # Top vertices
        v1 = bm.verts.new((x, y, 1.0))
        # Bottom vertices
        v2 = bm.verts.new((x, y, 1.0 - height))
    
    # Create tufts (simplified as bumps)
    num_tufts = int(height / tuft_spacing)
    for j in range(num_tufts):
        z = 1.0 - j * tuft_spacing
        for i in range(num_verts):
            angle = 2 * math.pi * i / num_verts
            x = (radius + 0.02) * math.cos(angle)
            y = (radius + 0.02) * math.sin(angle)
            
            if i % 2 == 0:  # Every other vertex gets a tuft
                vt = bm.verts.new((x, y, z + tuft_height/2))
    
    # Create mesh
    me = bpy.data.meshes.new("Kaunakes")
    bm.to_mesh(me)
    bm.free()
    
    skirt = bpy.data.objects.new("Kaunakes_Skirt", me)
    bpy.context.collection.objects.link(skirt)
    skirt.location = (0, 0, CHARACTER_HEIGHT * 0.5)  # Position at waist
    
    # Material: wool texture
    wool_mat = create_material("Wool", (0.8, 0.6, 0.4, 1), roughness=0.9)
    skirt.data.materials.append(wool_mat)
    
    return skirt

def create_tunic():
    """Create white linen tunic"""
    height = 0.5  # From shoulders to waist
    radius = 0.25
    
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=32,
        radius=radius,
        depth=height,
        location=(0, 0, CHARACTER_HEIGHT * 0.65)
    )
    tunic = bpy.context.active_object
    tunic.name = "Tunic"
    tunic.scale.z = 1.2  # Slightly tapered
    
    # Add sleeves
    for side in ['Left', 'Right']:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=16,
            radius=0.08,
            depth=height * 0.8,
            location=(0.25 if side == 'Right' else -0.25, 0, CHARACTER_HEIGHT * 0.6)
        )
        sleeve = bpy.context.active_object
        sleeve.name = f"Sleeve_{side}"
        sleeve.rotation_euler.x = math.radians(10)
    
    # Material: white linen
    linen_mat = create_material("Linen", (0.95, 0.95, 0.9, 1), roughness=0.7)
    tunic.data.materials.append(linen_mat)
    
    for obj in [tunic] + [o for o in bpy.context.scene.objects if o.name.startswith("Sleeve_")]:
        obj.data.materials.append(linen_mat)
    
    return tunic

def create_crown():
    """Create golden diadem/crown"""
    # Mesopotamian crown: circlet with decorative elements
    radius = 0.22  # Head radius
    height = 0.05
    thickness = 0.02
    
    bpy.ops.mesh.primitive_torus_add(
        align='WORLD',
        major_radius=radius,
        minor_radius=thickness,
        major_segments=32,
        minor_segments=8,
        location=(0, 0, CHARACTER_HEIGHT * 0.8)
    )
    crown = bpy.context.active_object
    crown.name = "Crown"
    
    # Add decorative lapis lazuli elements
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = (radius + 0.03) * math.cos(angle)
        y = (radius + 0.03) * math.sin(angle)
        
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=0.02,
            depth=0.04,
            location=(x, y, CHARACTER_HEIGHT * 0.8)
        )
        gem = bpy.context.active_object
        gem.name = f"Gem_{i}"
        gem.rotation_euler.z = angle
    
    # Material: gold
    gold_mat = create_material("Gold", (0.83, 0.69, 0.22, 1), roughness=0.1, metallic=1.0)
    crown.data.materials.append(gold_mat)
    
    # Material: lapis lazuli
    lapis_mat = create_material("LapisLazuli", (0.22, 0.38, 0.55, 1), roughness=0.1, metallic=0.3)
    for obj in [o for o in bpy.context.scene.objects if o.name.startswith("Gem_")]:
        obj.data.materials.append(lapis_mat)
    
    return crown

def create_belt():
    """Create leather belt with gold buckle"""
    waist_radius = 0.35
    belt_width = 0.05
    belt_thickness = 0.01
    
    # Belt
    bpy.ops.mesh.primitive_torus_add(
        align='WORLD',
        major_radius=waist_radius,
        minor_radius=belt_width/2,
        major_segments=32,
        minor_segments=4,
        location=(0, 0, CHARACTER_HEIGHT * 0.5)
    )
    belt = bpy.context.active_object
    belt.name = "Belt"
    
    # Belt rotation
    belt.rotation_euler.x = math.radians(90)
    
    # Buckle
    bpy.ops.mesh.primitive_cube_add(
        size=0.05,
        location=(0.1, 0, CHARACTER_HEIGHT * 0.5)
    )
    buckle = bpy.context.active_object
    buckle.name = "Buckle"
    buckle.scale = (0.08, 0.06, 0.02)
    
    # Materials
    leather_mat = create_material("Leather", (0.5, 0.3, 0.1, 1), roughness=0.8)
    belt.data.materials.append(leather_mat)
    
    gold_mat = create_material("Gold", (0.83, 0.69, 0.22, 1), roughness=0.1, metallic=1.0)
    buckle.data.materials.append(gold_mat)
    
    return belt

def create_sandals():
    """Create sandals"""
    foot_length = 0.25
    foot_width = 0.1
    thickness = 0.01
    
    for side in ['Left', 'Right']:
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(0.1 if side == 'Right' else -0.1, 0, 0.05)
        )
        sandal = bpy.context.active_object
        sandal.name = f"Sandal_{side}"
        sandal.scale = (foot_length, foot_width, thickness)
        
        # Add straps
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=0.01,
            depth=0.1,
            location=(0.1 if side == 'Right' else -0.1, 0, 0.1)
        )
        strap = bpy.context.active_object
        strap.name = f"Strap_{side}"
        strap.rotation_euler.x = math.radians(45)
    
    # Material: leather
    leather_mat = create_material("Leather", (0.5, 0.3, 0.1, 1), roughness=0.8)
    for obj in [o for o in bpy.context.scene.objects if o.name.startswith("Sandal_") or o.name.startswith("Strap_")]:
        obj.data.materials.append(leather_mat)

def create_jewelry():
    """Create necklace, bracelets, and ring"""
    # Necklace
    bpy.ops.mesh.primitive_torus_add(
        align='WORLD',
        major_radius=0.18,
        minor_radius=0.01,
        major_segments=32,
        minor_segments=4,
        location=(0, 0, CHARACTER_HEIGHT * 0.7)
    )
    necklace = bpy.context.active_object
    necklace.name = "Necklace"
    necklace.rotation_euler.x = math.radians(90)
    
    # Pendant
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8,
        radius=0.02,
        depth=0.03,
        location=(0, 0, CHARACTER_HEIGHT * 0.65)
    )
    pendant = bpy.context.active_object
    pendant.name = "Pendant"
    
    # Bracelets
    for side in ['Left', 'Right']:
        bpy.ops.mesh.primitive_torus_add(
            align='WORLD',
            major_radius=0.07,
            minor_radius=0.005,
            major_segments=16,
            minor_segments=4,
            location=(0.3 if side == 'Right' else -0.3, 0, CHARACTER_HEIGHT * 0.45)
        )
        bracelet = bpy.context.active_object
        bracelet.name = f"Bracelet_{side}"
        bracelet.rotation_euler.x = math.radians(90)
    
    # Materials
    gold_mat = create_material("Gold", (0.83, 0.69, 0.22, 1), roughness=0.1, metallic=1.0)
    lapis_mat = create_material("LapisLazuli", (0.22, 0.38, 0.55, 1), roughness=0.1, metallic=0.3)
    
    for obj in [necklace, pendant] + [o for o in bpy.context.scene.objects if o.name.startswith("Bracelet_")]:
        obj.data.materials.append(gold_mat)
    
    pendant.data.materials.append(lapis_mat)

def create_beard():
    """Create short, curled beard"""
    # Simplified beard as mesh
    bm = bmesh.new()
    
    # Create beard vertices
    center_z = CHARACTER_HEIGHT * 0.72
    width = 0.15
    depth = 0.1
    length = 0.15
    
    # Vertices
    v1 = bm.verts.new((-width/2, -0.2, center_z))
    v2 = bm.verts.new((width/2, -0.2, center_z))
    v3 = bm.verts.new((width/2, -0.2, center_z - length))
    v4 = bm.verts.new((-width/2, -0.2, center_z - length))
    
    # Curved vertices
    v5 = bm.verts.new((-width/2 + 0.02, -0.18, center_z - length/2))
    v6 = bm.verts.new((width/2 - 0.02, -0.18, center_z - length/2))
    
    # Faces
    bm.faces.new((v1, v2, v6, v5))
    bm.faces.new((v1, v5, v4, v3, v2))  # This might not work, simplified
    
    # Create mesh
    me = bpy.data.meshes.new("Beard")
    bm.to_mesh(me)
    bm.free()
    
    beard = bpy.data.objects.new("Beard", me)
    bpy.context.collection.objects.link(beard)
    
    # Material: hair
    hair_mat = create_material("Hair", (0.1, 0.05, 0.02, 1), roughness=0.9)
    beard.data.materials.append(hair_mat)
    
    return beard

def create_hair():
    """Create short to medium length hair"""
    bm = bmesh.new()
    
    # Create hair cap
    center_z = CHARACTER_HEIGHT * 0.85
    radius = 0.2
    
    # Top vertices
    v1 = bm.verts.new((0, 0, center_z + 0.05))
    
    # Side vertices
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = radius * math.cos(angle) * 0.8
        y = radius * math.sin(angle) * 0.8
        v = bm.verts.new((x, y, center_z))
    
    # Connect center to sides
    sides = [v for v in bm.verts if v != v1]
    for v in sides:
        bm.edges.new((v1, v))
    
    # Create mesh
    me = bpy.data.meshes.new("Hair")
    bm.to_mesh(me)
    bm.free()
    
    hair = bpy.data.objects.new("Hair", me)
    bpy.context.collection.objects.link(hair)
    
    # Material: hair
    hair_mat = create_material("Hair", (0.1, 0.05, 0.02, 1), roughness=0.9)
    hair.data.materials.append(hair_mat)
    
    return hair

def create_weapons():
    """Create sword and dagger"""
    # Sword at belt
    bpy.ops.mesh.primitive_cube_add(
        size=0.02,
        location=(0.1, 0, CHARACTER_HEIGHT * 0.48)
    )
    sword_hilt = bpy.context.active_object
    sword_hilt.name = "Sword_Hilt"
    sword_hilt.scale = (0.02, 0.08, 0.03)
    
    # Sword blade
    bpy.ops.mesh.primitive_cube_add(
        size=0.01,
        location=(0.15, 0, CHARACTER_HEIGHT * 0.45)
    )
    sword_blade = bpy.context.active_object
    sword_blade.name = "Sword_Blade"
    sword_blade.scale = (0.3, 0.05, 0.01)
    
    # Materials
    bronze_mat = create_material("Bronze", (0.8, 0.5, 0.2, 1), roughness=0.3, metallic=0.8)
    for obj in [sword_hilt, sword_blade]:
        obj.data.materials.append(bronze_mat)

def export_model():
    """Export the character model as GLB"""
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
        export_apply=True,
        export_current_frame=True
    )
    
    print(f"Exported Gilgamesh to: {export_path}")

def main():
    """Main function"""
    print("Creating Gilgamesh character model...")
    
    # Create base body (simplified for now)
    print("Creating base body...")
    body, head = create_human_base(CHARACTER_HEIGHT)
    
    # Create costume
    print("Creating costume...")
    tunic = create_tunic()
    skirt = create_kaunakes_skirt()
    
    # Create accessories
    print("Creating accessories...")
    crown = create_crown()
    belt = create_belt()
    create_sandals()
    create_jewelry()
    
    # Create hair and beard
    print("Creating hair and beard...")
    hair = create_hair()
    beard = create_beard()
    
    # Create weapons
    print("Creating weapons...")
    create_weapons()
    
    # Set up camera
    bpy.ops.object.camera_add(location=(3, -3, 2))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.radians(60), 0, math.radians(45))
    bpy.context.scene.camera = camera
    
    # Set up lighting
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    light = bpy.context.active_object
    light.data.energy = 5.0
    
    bpy.ops.object.light_add(type='HEMI', location=(0, 0, 10))
    light2 = bpy.context.active_object
    light2.data.energy = 2.0
    
    print(f"Gilgamesh created! Total objects: {len(bpy.context.scene.objects)}")
    
    # Export model
    export_model()
    
    print("Done!")
    print("\nNext steps:")
    print("- Import into Ishtaria as custom character model")
    print("- Use in NPC definition: character: {pack: protagonists, skin: warriorMaleA, model: media/models/characters/gilgamesh.glb}")

if __name__ == "__main__":
    main()
