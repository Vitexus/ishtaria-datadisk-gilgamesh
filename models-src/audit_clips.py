"""How faithfully do the retargeted clips of a game model follow the Hyper3D (Mixamo) clips they came from?

    blender -b --python models-src/audit_clips.py -- RAW.glb GAME.glb CLIPMAP.json

For each clip of the clipmap (see retarget_ambient.py) and a few frames of it, every mapped bone is compared by how far it has
turned away from its own rest pose in the world: the rotation `pose * rest^-1` of the Mixamo bone and of the game bone must be the
same. The angle between the two is the error; 0 degrees is a clip that moves exactly like its source, 90 degrees a limb that points
somewhere else (what copying local rotations did to a lying swimmer: the rigs' bones are rolled differently).
Prints one line per clip: mean and worst error over bones and frames, and the worst bone.
"""
import json
import math
import os
import sys

import bpy

RAW, GAME, CLIPMAP = sys.argv[sys.argv.index("--") + 1 :][:3]
BONE_MAP = [
    ("Hips", "Hips"), ("Spine", "Spine"), ("Spine1", "Chest"), ("Neck", "Neck"), ("Head", "Head"),
    ("LeftUpLeg", "Thigh_L"), ("LeftLeg", "Shin_L"), ("LeftFoot", "Foot_L"),
    ("RightUpLeg", "Thigh_R"), ("RightLeg", "Shin_R"), ("RightFoot", "Foot_R"),
    ("LeftArm", "UpperArm_L"), ("LeftForeArm", "Forearm_L"), ("LeftHand", "Hand_L"),
    ("RightArm", "UpperArm_R"), ("RightForeArm", "Forearm_R"), ("RightHand", "Hand_R"),
]


def import_gltf(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.abspath(path))
    objects = [o for o in bpy.data.objects if o not in before]
    armature = max((o for o in objects if o.type == "ARMATURE"), key=lambda o: len(o.data.bones))
    for o in [o for o in objects if o.type == "MESH"]:
        bpy.data.objects.remove(o, do_unlink=True)
    return armature


def find_action(name):
    base = name.replace("_Armature", "")
    for act in bpy.data.actions:
        if act.name == name or act.name.replace("_Armature", "") == base:
            return act
    for act in bpy.data.actions:
        if act.name.startswith(base):
            return act
    return None


def world_delta(arm, bone_name):
    bone = arm.pose.bones[bone_name]
    return (arm.matrix_world @ bone.matrix).to_3x3() @ (arm.matrix_world @ bone.bone.matrix_local).to_3x3().inverted()


bpy.ops.wm.read_factory_settings(use_empty=True)
game = import_gltf(GAME)
game_actions = {a.name: a for a in bpy.data.actions}
src = import_gltf(RAW)
clips = json.load(open(CLIPMAP, encoding="utf-8"))
name = os.path.basename(GAME)
for src_name, spec in clips.items():
    for out_name, _vertical in (spec if spec and isinstance(spec[0], list) else [spec]):
        src_action = find_action(src_name)
        game_action = game_actions.get(out_name) or next((a for n, a in game_actions.items() if n.startswith(out_name + "_")), None)
        if src_action is None or game_action is None:
            print("AUDIT %-24s %-10s missing (%s / %s)" % (name, out_name, src_action, game_action))
            continue
        src.animation_data_create()
        src.animation_data.action = src_action
        game.animation_data_create()
        game.animation_data.action = game_action
        start, end = [int(x) for x in src_action.frame_range]
        total, count, worst, worst_bone = 0.0, 0, 0.0, ""
        for frame in sorted({start + (end - start) * i // 5 for i in range(6)}):
            bpy.context.scene.frame_set(frame)
            bpy.context.view_layer.update()
            for s, t in BONE_MAP:
                if s not in src.pose.bones or t not in game.pose.bones:
                    continue
                error = math.degrees((world_delta(game, t).inverted() @ world_delta(src, s)).to_quaternion().angle)
                total += error
                count += 1
                if error > worst:
                    worst, worst_bone = error, t
        print("AUDIT %-24s %-10s mean %5.1f  worst %5.1f (%s)" % (name, out_name, total / max(count, 1), worst, worst_bone))
