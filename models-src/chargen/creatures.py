"""The two non-humanoid NPCs: Scorpion Man (human torso on a scorpion body) and the Bull of Heaven."""
import math

import bpy
from mathutils import Vector

from .core import assign, cone_tufts, cyl, material, reset_scene, sphere, surface_points, tube
from .humanoid import (COLORS, Humanoid, add_face_shapes, export_glb, humanoid_animations, join_and_skin,
                       local_rot, make_action, make_armature)

CHITIN = (0.3, 0.13, 0.06)


def _chain(points):
    return list(zip(points[:-1], points[1:]))


# ---------------------------------------------------------------------------------------------- scorpion man
def build_scorpion_man(out_path):
    reset_scene()
    h = Humanoid("scorpion_man", 1.9, "hero", False, (0.55, 0.38, 0.26), legs=False)
    h.build_body()
    H = h.H
    h.hair("long", (0.06, 0.04, 0.03)); h.brow((0.06, 0.04, 0.03), 1.4); h.beard("curled", (0.06, 0.04, 0.03))
    h.horns(1, "gold", 0.985, size=0.9)
    h.collar(); h.armbands("copper"); h.belt("copper", 0.05, False)
    h.hold("spear", "R")
    chit = material("chitin", CHITIN, None, 0.45, 0.3)
    chit2 = material("chitin2", (0.42, 0.2, 0.1), None, 0.4, 0.3)

    # abdomen: overlapping plates along the body, weighted to the Body bone
    plates = [(0.0, 0.34, 0.3), (0.28, 0.4, 0.33), (0.58, 0.42, 0.33), (0.9, 0.38, 0.3), (1.18, 0.3, 0.26)]
    for y, rx, rz in plates:
        h.add(sphere("plate", (0, y, 0.8), (rx, 0.2, rz), chit if int(y * 10) % 2 else chit2, 12, 8), "Body")
    h.add(sphere("carapace", (0, 0.02, 0.8), (0.42, 0.34, 0.34), chit, 12, 8), "Body")

    # pincers at the front
    for s in (1, -1):
        side = "L" if s == 1 else "R"
        p0, p1 = Vector((s * 0.34, -0.1, 0.82)), Vector((s * 0.62, -0.58, 0.74))
        h.add(cyl("pincerarm", p0, p1, 0.07, 0.06, chit, 8), "Body")
        h.add(sphere("pincerpalm", p1, (0.11, 0.14, 0.09), chit2, 8, 6), "Body")
        h.add(cyl("claw", p1 + Vector((s * 0.03, -0.05, 0.03)), p1 + Vector((-s * 0.04, -0.3, 0.02)), 0.05, 0.004, chit, 6), "Body")
        h.add(cyl("claw", p1 + Vector((s * 0.03, -0.05, -0.03)), p1 + Vector((s * 0.12, -0.28, -0.04)), 0.045, 0.004, chit, 6), "Body")

    extra = {"Body": ((0, -0.3, 0.8), (0, 1.1, 0.8), "Root"),
             "Hips": ((0, 0, 0.95), (0, 0, 1.06), "Body")}
    # legs: four pairs, two bones each
    ys = [0.0, 0.32, 0.62, 0.92]
    legs = []
    for i, y in enumerate(ys):
        for s in (1, -1):
            side = "L" if s == 1 else "R"
            root = Vector((s * 0.3, y, 0.8))
            knee = Vector((s * 0.78, y - 0.05 + 0.05 * i, 1.0))
            foot = Vector((s * 1.12, y - 0.15 + 0.12 * i, 0.0))
            up, low = "Leg%d_%s_up" % (i, side), "Leg%d_%s_low" % (i, side)
            extra[up] = (tuple(root), tuple(knee), "Body")
            extra[low] = (tuple(knee), tuple(foot), up)
            h.add(cyl("legup", root, knee, 0.065, 0.05, chit2, 8), up)
            h.add(sphere("legknee", knee, (0.06, 0.06, 0.06), chit, 8, 6), low)
            h.add(cyl("leglow", knee, foot, 0.05, 0.012, chit, 8), low)
            legs.append((up, low, i, s))
    # tail rising behind the body, ending in the sting
    tail = [Vector(p) for p in ((0, 1.1, 0.85), (0, 1.45, 0.98), (0, 1.75, 1.25), (0, 1.85, 1.6), (0, 1.7, 1.95), (0, 1.4, 2.2), (0, 1.1, 2.18))]
    names = ["Tail%d" % (k + 1) for k in range(len(tail) - 1)]
    for k, (a, b) in enumerate(_chain(tail)):
        parent = "Body" if k == 0 else names[k - 1]
        extra[names[k]] = (tuple(a), tuple(b), parent)
        r0, r1 = 0.15 - 0.012 * k, 0.15 - 0.012 * (k + 1)
        h.add(sphere("tailjoint", a, (r0 * 1.1,) * 3, chit2, 8, 6), names[k])
        h.add(cyl("tailseg", a, b, r0, r1, chit, 8), names[k])
    h.add(cyl("sting", tail[-1], tail[-1] + Vector((0, -0.28, -0.05)), 0.07, 0.003, material("sting", (0.7, 0.62, 0.4), None, 0.3), 6), names[-1])

    def anim(h_, arm):
        def walk_extra(t):
            a = 2 * math.pi * t
            d = {}
            for up, low, i, s in legs:
                phase = ((i % 2) * 0.5 + (0.0 if s == 1 else 0.5)) % 1.0
                tt = (t + phase) % 1.0
                swing = math.sin(2 * math.pi * tt)
                lift = max(0.0, math.cos(2 * math.pi * tt))
                d[up] = (local_rot(arm, up, ("Z", 0.28 * swing * s), ("X", -0.35 * lift)), None)
                d[low] = (local_rot(arm, low, ("X", 0.4 * lift)), None)
            for k, n in enumerate(names):
                d[n] = (local_rot(arm, n, ("X", 0.05 * math.sin(a + k * 0.5)), ("Z", 0.18 * math.sin(a + k * 0.4))), None)
            d["Body"] = ((0, 0, 0), None)
            return d

        def idle_extra(t):
            a = 2 * math.pi * t
            d = {}
            for k, n in enumerate(names):
                d[n] = (local_rot(arm, n, ("X", 0.05 * math.sin(a + k * 0.45)), ("Z", 0.1 * math.sin(a * 2 + k * 0.5))), None)
            return d
        humanoid_animations(h_, arm, bobbing=0.4, extra_walk=walk_extra, extra_idle=idle_extra)
    return h.finish(out_path, extra_bones=extra, anim=anim)


# ---------------------------------------------------------------------------------------------- bull of heaven
class _Parts:
    def __init__(self, name):
        self.name = name
        self.parts = []
        self.dz = 0.0

    def add(self, obj, bone, groups=()):
        self.parts.append(obj)
        return assign(obj, bone, None, groups)


def build_bull_of_heaven(out_path):
    reset_scene()
    p = _Parts("bull_of_heaven")
    hide = material("bullhide", (0.42, 0.2, 0.09), "fur", 1.0)
    dark = material("bulldark", (0.18, 0.09, 0.05), "fur", 1.0)
    horn = material("bullhorn", (0.85, 0.8, 0.65), None, 0.4)
    lapis = material("bulllapis", COLORS["lapis"], None, 0.25, 0.4)
    gold = material("bullgold", COLORS["gold"], None, 0.25, 1.0)
    hoof = material("bullhoof", (0.08, 0.06, 0.05), None, 0.5)
    eye = material("bulleye", (0.9, 0.2, 0.1), None, 0.3, emit=(0.9, 0.2, 0.1))
    table = {}

    def bone(name, head, tail, parent):
        table[name] = (head, tail, parent)

    bone("Root", (0, 0, 0), (0, 0, 0.1), None)
    bone("Hips", (0, 1.2, 1.5), (0, 0.5, 1.58), "Root")
    bone("Spine", (0, 0.5, 1.58), (0, -0.3, 1.7), "Hips")
    bone("Chest", (0, -0.3, 1.7), (0, -0.9, 1.82), "Spine")
    bone("Neck", (0, -0.9, 1.82), (0, -1.35, 1.72), "Chest")
    bone("Head", (0, -1.35, 1.72), (0, -1.85, 1.5), "Neck")
    bone("Head_end", (0, -0.9, 2.5), (0, -0.9, 2.56), "Chest")
    # body
    p.add(sphere("rump", (0, 0.95, 1.5), (0.66, 0.78, 0.66), hide, 14, 10), "Hips")
    p.add(sphere("barrel", (0, 0.15, 1.52), (0.72, 0.85, 0.72), hide, 14, 10), "Spine")
    p.add(sphere("hump", (0, -0.5, 1.7), (0.74, 0.72, 0.82), dark, 14, 10), "Chest")
    p.add(cyl("neck", (0, -0.7, 1.75), (0, -1.45, 1.6), 0.5, 0.36, dark, 12), "Neck")
    p.add(sphere("head", (0, -1.62, 1.5), (0.32, 0.5, 0.34), hide, 14, 10), "Head")
    p.add(sphere("muzzle", (0, -2.0, 1.35), (0.26, 0.28, 0.22), dark, 12, 8), "Head")
    for s in (1, -1):
        p.add(sphere("nostril", (s * 0.09, -2.25, 1.38), (0.04, 0.03, 0.035), hoof, 6, 5), "Head")
        p.add(sphere("eye", (s * 0.27, -1.78, 1.62), (0.05, 0.05, 0.05), eye, 8, 6), "Head")
        p.add(sphere("ear", (s * 0.4, -1.4, 1.62), (0.2, 0.07, 0.08), dark, 8, 6), "Head")
        # horns: out, up and forward
        pts = [Vector((s * 0.22, -1.48, 1.78)), Vector((s * 0.5, -1.5, 1.9)), Vector((s * 0.78, -1.62, 2.08)), Vector((s * 0.85, -1.85, 2.38)), Vector((s * 0.7, -2.1, 2.6))]
        for k in range(4):
            p.add(cyl("horn", pts[k], pts[k + 1], 0.1 * (1 - k * 0.2), 0.1 * (1 - (k + 1) * 0.2), horn, 8), "Head")
        p.add(cyl("hornband", pts[0] + (pts[1] - pts[0]) * 0.5, pts[0] + (pts[1] - pts[0]) * 0.65, 0.115, 0.115, gold, 10), "Head")
    # lapis beard under the chin (the Bull is described with a beard of lapis lazuli)
    for r in range(4):
        p.add(sphere("beard", (0, -1.95 + 0.04 * r, 1.12 - 0.12 * r), (0.11 - 0.015 * r, 0.1, 0.1), lapis, 8, 6), "Head")
    # legs
    legs = []
    for fy, fname in ((-0.75, "F"), (0.9, "R")):
        for s, side in ((1, "L"), (-1, "R")):
            top = Vector((s * 0.45, fy, 1.3))
            knee = Vector((s * 0.45, fy + (0.1 if fname == "R" else 0.0), 0.7))
            foot = Vector((s * 0.45, fy + (0.0), 0.12))
            up, low = "%s_%s_up" % (fname, side), "%s_%s_low" % (fname, side)
            table[up] = (tuple(top), tuple(knee), "Chest" if fname == "F" else "Hips")
            table[low] = (tuple(knee), tuple(foot), up)
            p.add(cyl("legup", top, knee, 0.2, 0.14, hide, 10), up)
            p.add(sphere("kneejoint", knee, (0.15, 0.15, 0.15), hide, 8, 6), low)
            p.add(cyl("leglow", knee, foot, 0.13, 0.1, dark, 10), low)
            p.add(cyl("hoof", foot, Vector((foot.x, foot.y - 0.02, 0.0)), 0.13, 0.15, hoof, 10), low)
            legs.append((up, low, fname, s))
    # tail
    tail = [Vector(q) for q in ((0, 1.6, 1.62), (0, 1.9, 1.3), (0, 1.98, 0.9), (0, 1.98, 0.45))]
    tnames = ["Tail1", "Tail2", "Tail3"]
    for k, (a, b) in enumerate(_chain(tail)):
        table[tnames[k]] = (tuple(a), tuple(b), "Hips" if k == 0 else tnames[k - 1])
        p.add(cyl("tail", a, b, 0.07 - 0.01 * k, 0.06 - 0.01 * k, dark, 8), tnames[k])
    p.add(sphere("tuft", tail[-1] + Vector((0, 0, -0.05)), (0.1, 0.1, 0.18), dark, 8, 6), "Tail3")

    arm = make_armature("bull_Armature", table)
    body = join_and_skin(p, arm, list(table.keys()))

    def walk(t):
        d = {}
        for up, low, fname, s in legs:
            phase = (0.0 if (fname == "F") == (s == 1) else 0.5)
            tt = (t + phase) % 1.0
            sw = math.sin(2 * math.pi * tt)
            lift = max(0.0, math.cos(2 * math.pi * tt))
            d[up] = (local_rot(arm, up, ("X", -0.38 * sw)), None)
            d[low] = (local_rot(arm, low, ("X", 0.7 * lift if fname == "F" else -0.5 * lift)), None)
        a = 2 * math.pi * t
        d["Hips"] = ((0, 0, 0), (0, 0.03 * math.cos(2 * a), 0))
        d["Spine"] = (local_rot(arm, "Spine", ("Z", 0.04 * math.sin(a))), None)
        d["Neck"] = (local_rot(arm, "Neck", ("X", 0.05 * math.sin(2 * a)), ("Z", -0.05 * math.sin(a))), None)
        d["Head"] = (local_rot(arm, "Head", ("X", -0.05 * math.sin(2 * a))), None)
        for k, n in enumerate(tnames):
            d[n] = (local_rot(arm, n, ("Y", 0.0), ("X", 0.0), ("Z", 0.25 * math.sin(a + k * 0.6))), None)
        return d

    def idle(t):
        a = 2 * math.pi * t
        d = {"Hips": ((0, 0, 0), (0, 0.006 * math.sin(a), 0))}
        d["Chest"] = (local_rot(arm, "Chest", ("X", 0.012 * math.sin(a))), None)
        d["Head"] = (local_rot(arm, "Head", ("X", 0.05 * math.sin(a - 0.5)), ("Z", 0.08 * math.sin(a))), None)
        for k, n in enumerate(tnames):
            d[n] = (local_rot(arm, n, ("Z", 0.2 * math.sin(a * 2 + k * 0.7))), None)
        return d
    make_action(arm, "Idle", 72, idle)
    make_action(arm, "Walk", 28, walk)
    export_glb(out_path)
    return arm, body
