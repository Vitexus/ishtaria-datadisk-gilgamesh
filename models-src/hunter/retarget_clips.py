"""Retarget Hyper3D Mixamo-style clips onto the game hunter armature.

    blender -b --python models-src/hunter/retarget_clips.py -- \
        models-src/hunter/hunter_rodin_raw.glb \
        media/models/hunter.glb \
        media/models/hunter.glb

Keeps Idle and Walk from `rodin_rig` (same smooth procedural gait as Enkidu). Adds Jump, Die, Box
and Kick from the Mixamo raw export. Do not bake HumanWalking or HumanInjuredRun: those produced
jerks and hops when paced against the server's walk speed.

An optional fourth argument is the skeleton and action of the swimming export
(`extract_clip.py`, `hunter_swim_clip.glb`), baked as Swim; with `-` as the first argument only that clip is added
to a model that already has the others:

    blender -b --python models-src/hunter/retarget_clips.py -- - media/models/hunter.glb media/models/hunter.glb \
        models-src/hunter/hunter_swim_clip.glb

Boxing and Kicking give the trapper combat clips against water-hole predators. No sitting or clean
run clip — the client speeds Walk for a sprint and falls back for Sit.

Jump, Die, Box and Kick use world-space bone turns (same as Swim / retarget_ambient.py `world`):
the Mixamo and chargen bones are rolled differently, so a local `matrix_basis` copy twists limbs.
Hips still get a vertical location channel on Jump/Die.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

ARGS = sys.argv[sys.argv.index("--") + 1 :]
RAW, GAME, OUT = ARGS[0], ARGS[1], ARGS[2]
SWIM = ARGS[3] if len(ARGS) > 3 else ""

BONE_MAP = [
    ("Hips", "Hips"),
    ("Spine", "Spine"),
    ("Spine1", "Chest"),
    ("Neck", "Neck"),
    ("Head", "Head"),
    ("LeftUpLeg", "Thigh_L"),
    ("LeftLeg", "Shin_L"),
    ("LeftFoot", "Foot_L"),
    ("RightUpLeg", "Thigh_R"),
    ("RightLeg", "Shin_R"),
    ("RightFoot", "Foot_R"),
    ("LeftArm", "UpperArm_L"),
    ("LeftForeArm", "Forearm_L"),
    ("LeftHand", "Hand_L"),
    ("RightArm", "UpperArm_R"),
    ("RightForeArm", "Forearm_R"),
    ("RightHand", "Hand_R"),
]

# (action, out_name, vertical_hips, world)
# Idle/Walk stay from rodin_rig (Enkidu-quality gait). Only combat and fall clips are Mixamo.
CLIPS = {
    "HumanForwardJump_Armature": ("Jump", True, True),
    "HumanDying_Armature": ("Die", True, True),
    "HumanBoxing_Armature": ("Box", False, True),
    "HumanKicking_Armature": ("Kick", False, True),
}


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def import_gltf(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def largest_armature(objects):
    return max((o for o in objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))


def largest_mesh(objects):
    return max((o for o in objects if o.type == "MESH"), key=lambda o: len(o.data.polygons))


def resolve_action(name):
    if name in bpy.data.actions:
        return bpy.data.actions[name]
    base = name.replace("_Armature", "")
    for act in bpy.data.actions:
        if act.name.replace("_Armature", "") == base or act.name.startswith(base):
            return act
    return None


def apply_frame(src_arm, tgt_arm, vertical_hips, src_hips_rest_z):
    bpy.context.view_layer.update()
    for src_name, tgt_name in BONE_MAP:
        if src_name not in src_arm.pose.bones or tgt_name not in tgt_arm.pose.bones:
            continue
        src = src_arm.pose.bones[src_name]
        tgt = tgt_arm.pose.bones[tgt_name]
        tgt.rotation_mode = "QUATERNION"
        _loc, rot, _scale = src.matrix_basis.decompose()
        tgt.rotation_quaternion = rot
        if src_name == "Hips" and vertical_hips:
            # Chargen Hips: bone local +Y is world up (local +Z is -Y).
            src_z = (src_arm.matrix_world @ src.head).z
            tgt.location = Vector((0.0, src_z - src_hips_rest_z, 0.0))
        else:
            tgt.location = Vector((0.0, 0.0, 0.0))
    bpy.context.view_layer.update()


def apply_frame_world(src_arm, tgt_arm, vertical_hips, src_hips_rest_z):
    """Pose each game bone so it turns in the world as its Mixamo bone does (parents first in BONE_MAP)."""
    for src_name, tgt_name in BONE_MAP:
        if src_name not in src_arm.pose.bones or tgt_name not in tgt_arm.pose.bones:
            continue
        src = src_arm.pose.bones[src_name]
        tgt = tgt_arm.pose.bones[tgt_name]
        tgt.rotation_mode = "QUATERNION"
        pose = (src_arm.matrix_world @ src.matrix).to_3x3()
        rest = (src_arm.matrix_world @ src.bone.matrix_local).to_3x3()
        delta = pose @ rest.inverted()
        tgt_rest = (tgt_arm.matrix_world @ tgt.bone.matrix_local).to_3x3()
        bpy.context.view_layer.update()
        head = (tgt_arm.matrix_world @ tgt.matrix).translation
        world = (delta @ tgt_rest).to_4x4()
        world.translation = head
        tgt.matrix = tgt_arm.matrix_world.inverted() @ world
        if src_name == "Hips" and vertical_hips:
            src_z = (src_arm.matrix_world @ src.head).z
            tgt.location = Vector((0.0, src_z - src_hips_rest_z, 0.0))
        bpy.context.view_layer.update()


# Clips that repeat: their last key is the pose of the first, so the loop has no seam.
LOOPING = {"Walk", "Run", "Swim"}


def bake_clip(src_arm, tgt_arm, src_action_name, out_name, vertical_hips, world=False):
    action = resolve_action(src_action_name)
    if action is None:
        print("missing action", src_action_name, flush=True)
        return False
    src_arm.animation_data_create()
    src_arm.animation_data.action = action
    # The Mixamo clips are 30 fps and the scene 24: HumanWalking ends at frame 24.8. Rounding
    # down dropped its last 0.8 frame, and the loop jumped by up to 8 degrees at the seam.
    start, end = int(action.frame_range[0]), math.ceil(action.frame_range[1])
    bpy.context.scene.frame_set(start)
    bpy.context.view_layer.update()
    src_hips_rest_z = (src_arm.matrix_world @ src_arm.pose.bones["Hips"].head).z

    for _src, tgt_name in BONE_MAP:
        if tgt_name in tgt_arm.pose.bones:
            tgt_arm.pose.bones[tgt_name].rotation_mode = "QUATERNION"
            tgt_arm.pose.bones[tgt_name].matrix_basis = Matrix.Identity(4)
    if tgt_arm.animation_data:
        for track in list(tgt_arm.animation_data.nla_tracks):
            if track.name == out_name or any(
                s.action and (s.action.name == out_name or s.action.name.startswith(out_name + "_"))
                for s in track.strips
            ):
                tgt_arm.animation_data.nla_tracks.remove(track)
        tgt_arm.animation_data.action = None
    for act in list(bpy.data.actions):
        if act.name == out_name or act.name.startswith(out_name + "_"):
            try:
                bpy.data.actions.remove(act)
            except Exception:
                pass
    baked = bpy.data.actions.new(name=out_name)
    tgt_arm.animation_data_create()
    tgt_arm.animation_data.action = baked

    for frame in range(start, end + 1):
        looped = out_name in LOOPING and frame == end
        bpy.context.scene.frame_set(start if looped else frame)
        if world:
            apply_frame_world(src_arm, tgt_arm, vertical_hips, src_hips_rest_z)
        else:
            apply_frame(src_arm, tgt_arm, vertical_hips, src_hips_rest_z)
        for _src, tgt_name in BONE_MAP:
            if tgt_name not in tgt_arm.pose.bones:
                continue
            pb = tgt_arm.pose.bones[tgt_name]
            pb.keyframe_insert("location", frame=frame)
            pb.keyframe_insert("rotation_quaternion", frame=frame)

    track = tgt_arm.animation_data.nla_tracks.new()
    track.name = out_name
    track.strips.new(out_name, start, baked)
    tgt_arm.animation_data.action = None
    print("baked", src_action_name, "->", out_name, start, end, "world" if world else "local", flush=True)
    return True


def main():
    clear_scene()
    game_objs = import_gltf(GAME)
    game_arm = largest_armature(game_objs)
    game_mesh = largest_mesh(game_objs)
    game_arm.rotation_mode = "XYZ"
    if RAW != "-":
        raw_objs = import_gltf(RAW)
        src_arm = largest_armature(raw_objs)
        for o in raw_objs:
            if o.type == "MESH":
                o.hide_render = True
                o.hide_viewport = True

        src_arm.location = game_arm.location.copy()
        src_arm.rotation_mode = "XYZ"

        for src_name, (out_name, vertical_hips, world) in CLIPS.items():
            bake_clip(src_arm, game_arm, src_name, out_name, vertical_hips, world=world)
    if SWIM:
        swim_arm = largest_armature(import_gltf(SWIM))
        swim_arm.location = game_arm.location.copy()
        swim_arm.rotation_mode = "XYZ"
        # The swimmer lies on the water: the body's pose is in the Hips rotation, its height is the client's to set.
        bake_clip(swim_arm, game_arm, "HumanSwimming_Armature", "Swim", False, world=True)

    bpy.ops.object.select_all(action="DESELECT")
    game_arm.select_set(True)
    game_mesh.select_set(True)
    bpy.context.view_layer.objects.active = game_arm
    bpy.ops.export_scene.gltf(
        filepath=os.path.abspath(OUT),
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_animation_mode="NLA_TRACKS",
        export_skins=True,
        export_image_format="JPEG",
    )
    print("wrote", OUT, os.path.getsize(OUT), flush=True)


if __name__ == "__main__":
    main()
