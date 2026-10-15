"""One box as a collision model (a statue or a plaque that is walked round, not through).

    blender -b --python models-src/architecture/box_collision.py -- out.glb x0 x1 y0 y1 z0 z1      (Blender axes, metres; front of a model is -Y)
"""
import sys

import bpy

out = sys.argv[sys.argv.index("--") + 1]
x0, x1, y0, y1, z0, z1 = (float(v) for v in sys.argv[sys.argv.index("--") + 2:][:6])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
box = bpy.context.active_object
box.scale = (x1 - x0, y1 - y0, z1 - z0)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, use_selection=True)
