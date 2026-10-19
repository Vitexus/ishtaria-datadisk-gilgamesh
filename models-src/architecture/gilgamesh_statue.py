"""Builds the statue of Gilgamesh holding a lion for the game: gilgamesh_statue.glb (+ _collision).

    blender -b --python models-src/architecture/gilgamesh_statue.py -- media/models media/models/architecture [--preview]

Composes the two rigged character models of the disk (media/models/gilgamesh.glb: the king, 2 m; media/models/mountain_lion.glb:
an adult male lion, c. 1.3 m at the shoulder) into the statue of research/gilgamesh-lion-statue.jpg - the Neo-Assyrian king
mastering a lion: the demigod giant stands on a stone pedestal and holds the adult lion upright in his left arm, the lion's
fore paws resting on his forearm, its hind legs dangling by his thigh and its tail hanging down. The lion is a full-grown
animal, not a cub: next to the giant king it reads small because Gilgamesh is two thirds god.

Both figures keep their painted (polychrome) character textures - ancient statues were colourful, and these textures are the
museum-paint look (skin, white linen, gold, tawny fur); the pedestal is plain limestone. The poses are baked: Gilgamesh stands
in the first frame of his Idle clip with his left arm raised into the cradle; the lion stands on its hind legs (its Hips bone
aimed up, the neck aimed forward, the legs aimed down). Everything is joined into one static mesh, decimated, scaled to
KING_M (the king 4.5 m on a 1.2 m pedestal, 5.7 m in all), centred on the pedestal and stood on z = 0 (the pedestal carries
a 0.3 m foundation below its ground plane), facing -Y (glTF +Z, south at yaw 0), as every model of this disk. The collision
model is three boxes: the pedestal, the king's body, the lion.
"""
import math
import os
import sys

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree

ARGS = sys.argv[sys.argv.index("--") + 1:]
SRC_DIR, OUT_DIR = ARGS[0], ARGS[1]
PREVIEW = "--preview" in ARGS

KING_M = 4.5             # the king's height on the pedestal (a giant: the living king is 3 m in game)
KING_FACES = 15000       # decimation budgets (the sources are 18k and 30k faces)
LION_FACES = 15000
TEX = 1024               # the lion's texture is 2048, the king's 1024: both are scaled to this
PEDESTAL_TOP = 1.2       # the pedestal's upper face; the king's feet stand there
PEDESTAL_BASE = -0.3     # the foundation below the ground plane
LION_SCALE = 0.85        # the adult lion next to the giant king (its upright body c. 2.1 m)

# The king's left arm in his own model space (2 m, feet at z = 0, facing -Y, his left at +X): the elbow out to his left
# side a little below the shoulder, the forearm forward-inward under the lion's chest, the hand open under its chest.
ELBOW = (0.456, -0.077, 1.375)
WRIST = (0.222, -0.290, 1.434)
HAND = (0.26, -0.24, 1.55)
# Where the lion's fore paws grip over the middle of the forearm (statue space, the king's feet at z = PEDESTAL_TOP).
PAW_TARGET = (0.80, -0.46, 4.38)


def log(*args):
    print("[gilgamesh_statue]", *args)


def import_character(path):
    """Imports a rigged character: returns (armature object, mesh object).

    The glTF import leaves a stray unnamed icosphere in the scene (an importer artifact, not in the file); the character
    is the largest mesh, everything else goes.
    """
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE")
    mesh = max((o for o in new if o.type == "MESH"), key=lambda o: len(o.data.polygons))
    for o in new:
        if o is not arm and o is not mesh:
            bpy.data.objects.remove(o, do_unlink=True)
    return arm, mesh


def set_idle(arm, frame=0):
    """Poses the armature in a frame of its Idle clip, then drops the clip (the pose is ours to edit afterwards)."""
    ad = arm.animation_data
    action = ad.action if ad and ad.action else next(a for a in bpy.data.actions if a.name.startswith("Idle"))
    arm.animation_data_create()
    arm.animation_data.action = action
    start = int(action.frame_range[0])
    bpy.context.scene.frame_set(start + frame)
    bpy.context.view_layer.update()
    arm.animation_data_clear()


def aim(pb, target_dir):
    """Aims a pose bone's Y axis along target_dir (armature space), keeping its head and length."""
    m = pb.matrix.copy()
    tgt = Vector(target_dir).normalized()
    tgt_local = (m.to_3x3().inverted() @ tgt).normalized()
    q = Vector((0.0, 1.0, 0.0)).rotation_difference(tgt_local)
    pb.matrix = m @ q.to_matrix().to_4x4()
    bpy.context.view_layer.update()


def bone_point(pb):
    return Vector(pb.matrix.translation)


def bone_tail(pb):
    m = pb.matrix
    return m.translation + (m.to_3x3() @ Vector((0.0, 1.0, 0.0))) * pb.bone.length


def pose_king(arm):
    """The king's left arm cradles the lion; the rest of him stands as in Idle."""
    set_idle(arm)
    bones = arm.pose.bones
    shoulder = bone_point(bones["UpperArm_L"])
    aim(bones["UpperArm_L"], Vector(ELBOW) - shoulder)
    elbow = bone_tail(bones["UpperArm_L"])
    log("shoulder_L at", tuple(round(c, 3) for c in shoulder),
        "elbow_L at", tuple(round(c, 3) for c in elbow), "(wanted", ELBOW, ")")
    aim(bones["Forearm_L"], Vector(WRIST) - elbow)
    wrist = bone_tail(bones["Forearm_L"])
    log("wrist_L at", tuple(round(c, 3) for c in wrist), "(wanted", WRIST, ")")
    aim(bones["Hand_L"], Vector(HAND) - wrist)
    hand = bone_tail(bones["Hand_L"])
    log("hand_L tip at", tuple(round(c, 3) for c in hand), "(wanted", HAND, ")")
    return elbow, wrist


def pose_lion(arm):
    """The adult lion stands upright on its hind legs, looking forward, its tail hanging down."""
    set_idle(arm)
    bones = arm.pose.bones
    aim(bones["Hips"], (0.0, 0.0, 1.0))                 # the body vertical, the rump at the bottom
    aim(bones["Neck"], (0.0, -1.0, 0.0))                # the head looks forward, not at the sky
    aim(bones["Head"], (0.0, -0.97, -0.25))             # the muzzle a little down, held in the cradle
    aim(bones["R_L_up"], (0.0, 0.0, -1.0))              # the hind legs dangle down by the king's thigh
    aim(bones["R_R_up"], (0.0, 0.0, -1.0))
    aim(bones["F_L_up"], (0.0, -0.25, -1.0))            # the fore legs reach down to the king's forearm
    aim(bones["F_R_up"], (0.0, -0.25, -1.0))
    for name in ("Hips", "Neck", "Head", "F_L_low", "R_L_low", "Tail4"):
        p = bone_point(bones[name])
        log("lion %s at" % name, tuple(round(c, 3) for c in p))
    return bones


def bake(arm, mesh, faces):
    """Applies the armature (the pose) and decimates; the mesh becomes static, the armature can go."""
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    mod = next(m for m in mesh.modifiers if m.type == "ARMATURE")
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if len(mesh.data.polygons) > faces:
        dec = mesh.modifiers.new("dec", "DECIMATE")
        dec.ratio = faces / len(mesh.data.polygons)
        bpy.ops.object.modifier_apply(modifier="dec")
    log("baked %s: %d faces" % (mesh.name, len(mesh.data.polygons)))
    bpy.data.objects.remove(arm, do_unlink=True)
    for o in list(bpy.context.scene.objects):
        if o.type == "EMPTY":
            bpy.data.objects.remove(o, do_unlink=True)
    mesh.parent = None
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return mesh


def bounds(mesh):
    vs = [v.co for v in mesh.data.vertices]
    return (Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))),
            Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs))))


def stone_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def build_king():
    arm, mesh = import_character(os.path.join(SRC_DIR, "gilgamesh.glb"))
    elbow, wrist = pose_king(arm)
    mesh = bake(arm, mesh, KING_FACES)
    scale = KING_M / 2.0
    mn, mx = bounds(mesh)
    centre_x = (mn.x + mx.x) / 2
    mesh.scale = (scale, scale, scale)
    mesh.location = (-centre_x * scale, 0.0, PEDESTAL_TOP)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mn, mx = bounds(mesh)
    log("king: bounds", tuple(round(c, 2) for c in mn), tuple(round(c, 2) for c in mx))
    forearm = tuple(v * scale + Vector((0, 0, PEDESTAL_TOP)) for v in (elbow, wrist))
    log("forearm (statue space):", tuple(tuple(round(c, 2) for c in v) for v in forearm))
    return mesh


def build_lion():
    arm, mesh = import_character(os.path.join(SRC_DIR, "mountain_lion.glb"))
    bones = pose_lion(arm)
    paw = (bone_tail(bones["F_L_low"]) + bone_tail(bones["F_R_low"])) / 2
    nose = bone_point(bones["Head"])
    hind = (bone_tail(bones["R_L_low"]) + bone_tail(bones["R_R_low"])) / 2
    tail = bone_point(bones["Tail4"])
    log("lion fore paws at", tuple(round(c, 3) for c in paw), "nose", tuple(round(c, 3) for c in nose),
        "hind paws", tuple(round(c, 3) for c in hind), "tail tip", tuple(round(c, 3) for c in tail))
    mesh = bake(arm, mesh, LION_FACES)
    mesh.scale = (LION_SCALE, LION_SCALE, LION_SCALE)
    mesh.location = Vector(PAW_TARGET) - Vector(paw) * LION_SCALE
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    mn, mx = bounds(mesh)
    log("lion: bounds", tuple(round(c, 2) for c in mn), tuple(round(c, 2) for c in mx))
    return mesh


def build_pedestal():
    stone = stone_material("limestone", (0.80, 0.76, 0.68))
    dark = stone_material("limestone_base", (0.68, 0.64, 0.57))
    parts = []
    for (w, d, z0, z1, mat) in ((2.8, 1.8, PEDESTAL_BASE, 0.1, dark), (2.4, 1.4, 0.1, PEDESTAL_TOP, stone)):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, (z0 + z1) / 2))
        box = bpy.context.active_object
        box.scale = (w, d, z1 - z0)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        box.data.materials.append(mat)
        parts.append(box)
    return parts


def export(path, objects):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_yup=True,
                              export_image_format="JPEG", export_jpeg_quality=85, use_selection=True)
    log("wrote", path, "(%.2f MiB)" % (os.path.getsize(path) / 1048576))


def check(king, lion, pedestal):
    """Sanity checks on the composed statue; every failure is printed."""
    ok = True

    def want(cond, message):
        nonlocal ok
        log(("PASS " if cond else "FAIL ") + message)
        ok = ok and cond

    mn, mx = bounds(king)
    want(abs(mn.z - PEDESTAL_TOP) < 0.02, "the king's feet stand on the pedestal (z %.2f)" % mn.z)
    want(mx.z - mn.z > KING_M - 0.05, "the king is %.2f m tall" % (mx.z - mn.z))
    lmn, lmx = bounds(lion)
    want(lmx.z < mx.z, "the lion's head (%.2f) is below the king's head (%.2f)" % (lmx.z, mx.z))
    want(lmx.z > 4.5, "the lion's head (%.2f) reaches the king's shoulder" % lmx.z)
    want(lmn.z > PEDESTAL_TOP + 0.5, "the lion's hind paws (%.2f) dangle above the pedestal" % lmn.z)
    want(lmn.x > 0.4 and lmx.x < 1.4, "the lion (%.2f..%.2f) stands beside the king's left side" % (lmn.x, lmx.x))
    tree = KDTree(len(king.data.vertices))
    for i, v in enumerate(king.data.vertices):
        tree.insert(v.co, i)
    tree.balance()
    distances = []
    for v in lion.data.vertices:
        co, _, _ = tree.find(v.co)
        distances.append((v.co - co).length)
    distances.sort()
    log("lion-to-king vertex distances: min %.3f, p10 %.3f, median %.3f" %
        (distances[0], distances[len(distances) // 10], distances[len(distances) // 2]))
    want(distances[0] < 0.35, "the lion touches the king (its paws on his forearm), min distance %.2f m" % distances[0])
    want(distances[len(distances) // 10] < 1.5, "the lion is held against the king, not floating away")
    pmn, pmx = bounds(pedestal[0])
    for p in pedestal[1:]:
        b = bounds(p)
        pmn = Vector((min(pmn.x, b[0].x), min(pmn.y, b[0].y), min(pmn.z, b[0].z)))
        pmx = Vector((max(pmx.x, b[1].x), max(pmx.y, b[1].y), max(pmx.z, b[1].z)))
    want(abs(pmn.z - PEDESTAL_BASE) < 0.01 and abs(pmx.z - PEDESTAL_TOP) < 0.01,
         "the pedestal spans %.2f..%.2f" % (pmn.z, pmx.z))
    return ok


def collision_boxes(king, lion, pedestal):
    """Three boxes in statue space: the pedestal, the king's body, the lion (a little slimmer than the bodies)."""
    kmn, kmx = bounds(king)
    lmn, lmx = bounds(lion)
    pmn, pmx = bounds(pedestal[0])
    for p in pedestal[1:]:
        b = bounds(p)
        pmn = Vector((min(pmn.x, b[0].x), min(pmn.y, b[0].y), min(pmn.z, b[0].z)))
        pmx = Vector((max(pmx.x, b[1].x), max(pmx.y, b[1].y), max(pmx.z, b[1].z)))
    king_x1 = min(kmx.x, 0.70)      # the torso; the raised left arm is covered by the lion's box
    return ((pmn, pmx),
            (Vector((kmn.x, kmn.y + 0.05, kmn.z)), Vector((king_x1, kmx.y - 0.05, kmx.z))),
            (Vector((lmn.x + 0.03, lmn.y + 0.03, lmn.z + 0.03)),
             Vector((lmx.x - 0.03, lmx.y - 0.03, lmx.z - 0.03))))


def preview(path_prefix):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "TEXTURE"
    scene.render.resolution_x = 800
    scene.render.resolution_y = 1000
    scene.render.film_transparent = True
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    scene.camera = cam
    for name, loc, rot in (("front", (0, -11, 3.2), (80, 0, 0)),
                           ("side", (11, 0, 3.2), (80, 0, 90)),
                           ("three_quarter", (7.8, -7.8, 4.0), (72, 0, 45))):
        cam.location = Vector(loc)
        cam.rotation_euler = tuple(math.radians(a) for a in rot)
        scene.render.filepath = "%s_%s.png" % (path_prefix, name)
        bpy.ops.render.render(write_still=True)
        log("preview", scene.render.filepath)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    king = build_king()
    lion = build_lion()
    pedestal = build_pedestal()
    ok = check(king, lion, pedestal)
    boxes = collision_boxes(king, lion, pedestal)
    for img in bpy.data.images:
        if img.size[0] > TEX:
            img.scale(TEX, int(TEX * img.size[1] / img.size[0]))
    bpy.ops.object.select_all(action="DESELECT")
    for o in [king, lion] + pedestal:
        o.select_set(True)
    bpy.context.view_layer.objects.active = king
    bpy.ops.object.join()
    statue = bpy.context.active_object
    statue.name = "gilgamesh_statue"
    if PREVIEW:
        preview(os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders", "gilgamesh_statue"))
    export(os.path.join(OUT_DIR, "gilgamesh_statue.glb"), [statue])

    # the collision model: three boxes (the pedestal, the king's body, the lion)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for (b0, b1) in boxes:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=((b0.x + b1.x) / 2, (b0.y + b1.y) / 2, (b0.z + b1.z) / 2))
        box = bpy.context.active_object
        box.scale = (b1.x - b0.x, b1.y - b0.y, b1.z - b0.z)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    export(os.path.join(OUT_DIR, "gilgamesh_statue_collision.glb"), list(bpy.context.scene.objects))
    log("checks", "passed" if ok else "FAILED")


main()
