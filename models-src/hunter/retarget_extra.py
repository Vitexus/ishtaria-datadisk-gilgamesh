"""Adds clips of a Hyper3D (Rodin) export to the game hunter, through the bone map of `retarget_clips.py`.

    blender -b --python models-src/hunter/retarget_extra.py -- media/models/hunter.glb media/models/hunter.glb \
        ~/Downloads/hunter-rodin3D-85b93290-bfc4-4962-ac05-b44c6cdd4f30/base_basic_pbr.glb \
        a6b5abf0=Sit 0db755fa=Sit2 c9a61005=Sit3

The last arguments are `<start of the action's UUID>=<clip name>`. The Rodin job names its clips by UUID only; which is which
was read off a contact sheet (and by the project owner: the first three seated clips, the third with a leg over the other).
The sitting clips loop; the pose is turned bone by bone as in the world and the hips follow the seat's height.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[sys.argv.index("--") + 1 :]
GAME, OUT, SOURCE = ARGS[0], ARGS[1], ARGS[2]
WANTED = [item.split("=", 1) for item in ARGS[3:]]

# retarget_clips reads its arguments when it is imported: hand it "no raw export, this model in, this model out".
sys.argv = sys.argv[: sys.argv.index("--") + 1] + ["-", GAME, OUT]
spec = importlib.util.spec_from_file_location("retarget_clips", os.path.join(HERE, "retarget_clips.py"))
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

rc.LOOPING.update(name for _uuid, name in WANTED if name.startswith("Sit"))
rc.clear_scene()
game_objs = rc.import_gltf(os.path.abspath(GAME))
game_arm = rc.largest_armature(game_objs)
game_mesh = rc.largest_mesh(game_objs)
game_arm.rotation_mode = "XYZ"
raw_objs = rc.import_gltf(os.path.abspath(os.path.expanduser(SOURCE)))
src_arm = rc.largest_armature(raw_objs)
for obj in raw_objs:
    if obj.type == "MESH":
        obj.hide_render = obj.hide_viewport = True
src_arm.location = game_arm.location.copy()
src_arm.rotation_mode = "XYZ"
for uuid, name in WANTED:
    action = next((a for a in rc.bpy.data.actions if a.name.startswith(uuid)), None)
    if action is None:
        print("missing action", uuid, flush=True)
        continue
    rc.bake_clip(src_arm, game_arm, action.name, name, True, world=True)

rc.bpy.ops.object.select_all(action="DESELECT")
game_arm.select_set(True)
game_mesh.select_set(True)
rc.bpy.context.view_layer.objects.active = game_arm
rc.bpy.ops.export_scene.gltf(
    filepath=os.path.abspath(OUT), export_format="GLB", use_selection=True, export_animations=True,
    export_animation_mode="NLA_TRACKS", export_skins=True, export_image_format="JPEG",
)
print("wrote", OUT, os.path.getsize(OUT), flush=True)
