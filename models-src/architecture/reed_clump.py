"""Procedural Phragmites-style reed clump for Early Dynastic marsh banks.

    blender -b --python models-src/architecture/reed_clump.py -- \\
        ../../ishtaria-client/assets/kenney/nature-kit/Models/GLTF\\ format/reed_clump.glb
"""
import math
import os
import random
import sys

import bpy

args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
OUT = os.path.abspath(args[0] if args else "reed_clump.glb")

bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(2700)

mat = bpy.data.materials.new("reed")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.35, 0.48, 0.18, 1.0)
bsdf.inputs["Roughness"].default_value = 0.85

meshes = []
for i in range(28):
    angle = random.uniform(0, math.tau)
    radius = random.uniform(0.02, 0.35)
    x, y = math.cos(angle) * radius, math.sin(angle) * radius
    height = random.uniform(1.4, 2.6)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=5, radius=0.012 + random.uniform(0, 0.008), depth=height, location=(x, y, height / 2)
    )
    stem = bpy.context.active_object
    stem.rotation_euler = (
        random.uniform(-0.12, 0.12),
        random.uniform(-0.12, 0.12),
        random.uniform(0, math.tau),
    )
    stem.data.materials.append(mat)
    meshes.append(stem)
    # seed head
    bpy.ops.mesh.primitive_cone_add(
        vertices=6,
        radius1=0.04,
        radius2=0.01,
        depth=0.22,
        location=(x, y, height + 0.08),
    )
    head = bpy.context.active_object
    head.data.materials.append(mat)
    meshes.append(head)

bpy.ops.object.select_all(action="DESELECT")
for obj in meshes:
    obj.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
clump = bpy.context.active_object
clump.name = "reed_clump"

os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True)
print("wrote", OUT)
