"""Keep only the skeleton and the animation of a Hyper3D export, as a small glTF.

    blender -b --python models-src/hunter/extract_clip.py -- \
        ~/Downloads/rodin3D-hunter-swim-85b93290-bfc4-4962-ac05-b44c6cdd4f30/base_basic_pbr.glb \
        models-src/hunter/hunter_swim_clip.glb

The swimming export of the hunter (Hyper3D job 85b93290, the Mixamo rig of `hunter_rodin_raw.glb`) is a 700 k vertex mesh
of 66 MB; `retarget_clips.py` needs only the bones and the `HumanSwimming` action, so the mesh and its textures go.
"""
import os
import sys

import bpy

SRC, OUT = sys.argv[sys.argv.index("--") + 1 :][:2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(SRC))
for obj in [o for o in bpy.data.objects if o.type == "MESH"]:
    bpy.data.objects.remove(obj, do_unlink=True)
for image in list(bpy.data.images):
    bpy.data.images.remove(image)
armature = max((o for o in bpy.data.objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))
print("actions:", [a.name for a in bpy.data.actions], flush=True)
bpy.ops.object.select_all(action="DESELECT")
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
bpy.ops.export_scene.gltf(
    filepath=os.path.abspath(OUT),
    export_format="GLB",
    use_selection=True,
    export_animations=True,
    export_skins=True,
)
print("wrote", OUT, os.path.getsize(OUT), flush=True)
