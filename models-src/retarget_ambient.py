"""Retarget Mixamo-style clips from a Rodin raw GLB onto a game NPC armature.

    blender -b --python models-src/retarget_ambient.py -- \
        models-src/potter/potter_rodin_raw.glb \
        media/models/potter.glb \
        media/models/potter.glb \
        models-src/clipmaps/potter.json

Keeps Idle/Walk (and other existing NLA tracks not replaced by the clipmap).
Clipmap JSON: { "HumanBoxing_Armature": ["Box", false], ... }
  second value = vertical hip offset (Jump/Sit/Die).
"""
import json
import os
import sys

import bpy
from mathutils import Matrix, Vector

ARGS = sys.argv[sys.argv.index("--") + 1 :]
RAW, GAME, OUT, CLIPMAP = ARGS[0], ARGS[1], ARGS[2], ARGS[3]

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
        if act.name.replace("_Armature", "") == base:
            return act
        if act.name.startswith(base):
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
            src_z = (src_arm.matrix_world @ src.head).z
            # Chargen Hips: local +Y is world up.
            tgt.location = Vector((0.0, src_z - src_hips_rest_z, 0.0))
        else:
            tgt.location = Vector((0.0, 0.0, 0.0))
    bpy.context.view_layer.update()


def bake_clip(src_arm, tgt_arm, src_action_name, out_name, vertical_hips):
    action = resolve_action(src_action_name)
    if action is None:
        print("missing action", src_action_name, flush=True)
        return False
    src_arm.animation_data_create()
    src_arm.animation_data.action = action
    start, end = [int(x) for x in action.frame_range]
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
            if out_name in ("Idle", "Walk"):
                continue
            try:
                bpy.data.actions.remove(act)
            except Exception:
                pass

    baked = bpy.data.actions.new(name=out_name)
    tgt_arm.animation_data_create()
    tgt_arm.animation_data.action = baked

    for frame in range(start, end + 1):
        bpy.context.scene.frame_set(frame)
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
    print("baked", action.name, "->", out_name, start, end, flush=True)
    return True


def main():
    with open(CLIPMAP, encoding="utf-8") as handle:
        clips = json.load(handle)
    clear_scene()
    game_objs = import_gltf(GAME)
    game_arm = largest_armature(game_objs)
    game_mesh = largest_mesh(game_objs)
    raw_objs = import_gltf(RAW)
    src_arm = largest_armature(raw_objs)
    for o in raw_objs:
        if o.type == "MESH":
            o.hide_render = True
            o.hide_viewport = True
    if "Hips" not in src_arm.pose.bones:
        print("skip non-humanoid armature", src_arm.name, flush=True)
        return
    src_arm.location = game_arm.location.copy()
    src_arm.rotation_mode = "XYZ"
    game_arm.rotation_mode = "XYZ"

    for src_name, spec in clips.items():
        # ["Box", false] or [["Die", true], ["Die2", true]]
        targets = spec if spec and isinstance(spec[0], list) else [spec]
        for out_name, vertical in targets:
            bake_clip(src_arm, game_arm, src_name, out_name, bool(vertical))

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
