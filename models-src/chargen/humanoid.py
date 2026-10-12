"""Rigged humanoid: body, costume parts, skeleton, Idle and Walk animations, glTF export."""
import math
import random

import bpy
from mathutils import Vector

from .core import (assign, box, cone_tufts, cyl, get_weights, material, set_weights, skin_of, smoothstep,
                   sphere, surface_points, tube)

# half shoulder width, torso depth, limb radius, hip half width (fractions of the height)
BUILDS = {
    "man": (0.115, 0.065, 0.028, 0.055),
    "hero": (0.125, 0.070, 0.031, 0.056),
    "stocky": (0.130, 0.078, 0.033, 0.062),
    "lean": (0.105, 0.058, 0.024, 0.050),
    "old": (0.105, 0.060, 0.024, 0.052),
    "woman": (0.095, 0.055, 0.024, 0.060),
    "monster": (0.150, 0.095, 0.046, 0.075),
}

ORGANIC_NAMES = {"pelvis", "belly", "chest", "bust", "neck", "head", "shoulder", "upperarm", "elbow", "forearm", "hand", "hipjoint",
                 "thigh", "knee", "shin", "foot"}

BONES_ORDER = ["Root", "Hips", "Spine", "Chest", "Neck", "Head", "Head_end"]

COLORS = {
    "gold": (0.83, 0.62, 0.15), "lapis": (0.05, 0.14, 0.55), "carnelian": (0.62, 0.12, 0.07),
    "copper": (0.72, 0.38, 0.2), "bone": (0.85, 0.82, 0.7), "wood": (0.35, 0.22, 0.1),
    "clay": (0.62, 0.38, 0.22), "white": (0.93, 0.9, 0.82), "cream": (0.8, 0.7, 0.5),
    "red": (0.55, 0.1, 0.07), "brown": (0.34, 0.2, 0.1), "black": (0.04, 0.03, 0.03),
    "grey": (0.55, 0.55, 0.55), "blue": (0.15, 0.25, 0.6), "darkred": (0.3, 0.04, 0.04),
}


class Humanoid:
    def __init__(self, name, height, build="man", female=False, skin=(0.72, 0.52, 0.36), legs=True):
        self.name = name
        self.H = height
        self.female = female
        self.legs = legs
        sh, depth, limb, hip = BUILDS[build]
        H = height
        self.sh, self.depth, self.limb, self.hip = sh * H, depth * H, limb * H, hip * H
        self.skin = skin
        self.parts = []
        self.organic = []  # skin parts that are fused into one smooth body mesh
        self.arm_swing = {"L": 1.0, "R": 1.0}
        self.m_skin = material("skin", skin, None, 0.75)
        self.dz = 0.0
        self._joints()

    # ------------------------------------------------------------------ geometry of the skeleton
    def _joints(self):
        H, sh, hip, limb = self.H, self.sh, self.hip, self.limb
        j = {}
        j["shoulder"] = Vector((sh, 0, 0.80 * H))
        elbow_dir = Vector((0.10, 0, -0.99)).normalized()
        j["elbow"] = j["shoulder"] + elbow_dir * (0.19 * H)
        wrist_dir = Vector((0.07, 0, -0.99)).normalized()
        j["wrist"] = j["elbow"] + wrist_dir * (0.17 * H)
        j["hand"] = j["wrist"] + wrist_dir * (0.085 * H)
        j["hip"] = Vector((hip * 0.9, 0, 0.50 * H))
        j["knee"] = Vector((hip * 0.82, 0, 0.265 * H))
        j["ankle"] = Vector((hip * 0.76, 0, 0.05 * H))
        j["toe"] = Vector((hip * 0.76, -0.105 * H, 0.02 * H))
        self.j = j

    def side(self, key, s):
        p = self.j[key].copy()
        p.x *= s
        return p

    def hand_pos(self, s):
        return self.side("hand", s)

    def add(self, obj, bone=None, weights=None, groups=(), organic=False):
        self.parts.append(obj)
        base = obj.name.split(".")[0]
        if organic or base.rstrip("LR") in ORGANIC_NAMES:
            self.organic.append(obj)
        return assign(obj, bone, weights, groups)

    # ------------------------------------------------------------------ the body
    def build_body(self):
        H, sh, dp, limb, hip = self.H, self.sh, self.depth, self.limb, self.hip
        sk = self.m_skin
        self.add(sphere("pelvis", (0, 0, 0.52 * H), (hip * 1.12, dp * 0.95, 0.07 * H), sk), "Hips", organic=True)
        self.add(sphere("belly", (0, 0, 0.62 * H), (hip * 1.0, dp * (1.05 if self.female else 0.95), 0.07 * H), sk), "Spine", organic=True)
        self.add(sphere("chest", (0, 0, 0.735 * H), (sh * 0.9, dp * 1.05, 0.09 * H), sk), "Chest", organic=True)
        if self.female:
            for s in (1, -1):
                self.add(sphere("bust", (s * 0.03 * H, -dp * 0.8, 0.745 * H), (0.034 * H, 0.03 * H, 0.032 * H), sk), "Chest")
        self.add(cyl("neck", (0, 0, 0.80 * H), (0, 0, 0.865 * H), 0.024 * H, 0.021 * H, sk, 10), "Neck", organic=True)
        self._head()
        for s, side in ((1, "L"), (-1, "R")):
            a, b, c, d = (self.side(k, s) for k in ("shoulder", "elbow", "wrist", "hand"))
            self.add(sphere("shoulder" + side, a, (limb * 1.3,) * 3, sk, 10, 7), "UpperArm_" + side, organic=True)
            self.add(cyl("upperarm" + side, a, b, limb * 1.05, limb * 0.88, sk, 10), "UpperArm_" + side, organic=True)
            self.add(sphere("elbow" + side, b, (limb * 0.95,) * 3, sk, 10, 7), "Forearm_" + side, organic=True)
            self.add(cyl("forearm" + side, b, c, limb * 0.9, limb * 0.7, sk, 10), "Forearm_" + side, organic=True)
            self.add(sphere("hand" + side, (c + d) / 2, (limb * 0.85, limb * 0.55, 0.05 * H), sk, 10, 7), "Hand_" + side, organic=True)
            if self.legs:
                hj, k, an, toe = (self.side(x, s) for x in ("hip", "knee", "ankle", "toe"))
                self.add(sphere("hipjoint" + side, hj, (limb * 1.4,) * 3, sk, 10, 7), "Thigh_" + side, organic=True)
                self.add(cyl("thigh" + side, hj, k, limb * 1.4, limb * 1.0, sk, 10), "Thigh_" + side, organic=True)
                self.add(sphere("knee" + side, k, (limb * 0.98,) * 3, sk, 10, 7), "Shin_" + side, organic=True)
                self.add(cyl("shin" + side, k, an, limb * 0.97, limb * 0.68, sk, 10), "Shin_" + side, organic=True)
                self.add(sphere("foot" + side, (an.x, -0.04 * H, 0.025 * H), (limb * 0.8, 0.07 * H, 0.026 * H), sk, 10, 7), "Foot_" + side, organic=True)

    def _head(self):
        H = self.H
        sk = self.m_skin
        cz = 0.925 * H
        self.add(sphere("head", (0, 0, cz), (0.062 * H, 0.072 * H, 0.08 * H), sk, 16, 12), "Head", organic=True)
        # jaw / chin
        self.add(sphere("chin", (0, -0.03 * H, 0.874 * H), (0.04 * H, 0.04 * H, 0.03 * H), sk, 12, 8), "Head")
        self.add(sphere("nose", (0, -0.073 * H, 0.915 * H), (0.011 * H, 0.02 * H, 0.025 * H), sk, 8, 6), "Head")
        for s in (1, -1):
            self.add(sphere("ear", (s * 0.058 * H, 0.0, cz - 0.005 * H), (0.008 * H, 0.015 * H, 0.022 * H), sk, 8, 6), "Head")
        eye_white = material("eyewhite", (0.92, 0.9, 0.85), None, 0.4)
        pupil = material("pupil", (0.03, 0.02, 0.02), None, 0.3)
        self.eye_centers = []
        for s in (1, -1):
            c = (s * 0.025 * H, -0.060 * H, 0.937 * H)
            self.eye_centers.append(c)
            self.add(sphere("eye", c, (0.015 * H, 0.009 * H, 0.011 * H), eye_white, 10, 8), "Head", groups=("blink",))
            self.add(sphere("pupil", (c[0], c[1] - 0.0065 * H, c[2]), (0.0075 * H, 0.0035 * H, 0.0075 * H), pupil, 8, 6), "Head", groups=("blink",))
        mouth = material("mouth", (0.35, 0.1, 0.09), None, 0.5)
        self.mouth_center = (0, -0.0665 * H, 0.883 * H)
        self.add(sphere("mouth", self.mouth_center, (0.015 * H, 0.005 * H, 0.0018 * H), mouth, 10, 6), "Head", groups=("mouth",))

    # ------------------------------------------------------------------ hair, beard, brow
    def hair(self, style, color=(0.05, 0.03, 0.025)):
        H = self.H
        m = material("hair", color, None, 0.7)
        cz = 0.925 * H
        if style == "bald":
            return
        cap = [(0.935 * H, 0.062 * H, 0.072 * H, 0, 0.003 * H), (0.985 * H, 0.052 * H, 0.062 * H, 0, 0.002 * H),
               (1.0 * H, 0.03 * H, 0.04 * H, 0, 0.0), (1.006 * H, 0.0005, 0.0005, 0, 0.0)]
        if style in ("short", "bun", "long", "matted", "braid_wrap"):
            self.add(tube("haircap", cap, m, 18), "Head")
        if style == "bun":
            self.add(sphere("bun", (0, 0.055 * H, 0.975 * H), (0.035 * H, 0.03 * H, 0.03 * H), m, 10, 8), "Head")
        if style in ("long", "matted"):
            n = 0.025 * H if style == "matted" else 0.0
            rings = [(0.975 * H, 0.063 * H, 0.074 * H, 0, 0.004 * H), (0.90 * H, 0.066 * H + n, 0.08 * H + n, 0, 0.012 * H),
                     (0.80 * H, 0.062 * H + n, 0.072 * H + n, 0, 0.03 * H), (0.70 * H, 0.05 * H + n, 0.06 * H + n, 0, 0.045 * H)]
            self.add(tube("hairback", rings, m, 16, arc=(15, 165), tuft=0.02 * H if style == "matted" else 0.0), "Head")
        if style == "braid_wrap":
            for k in range(14):
                a = 2 * math.pi * k / 14
                self.add(sphere("braid", (0.058 * H * math.cos(a), 0.066 * H * math.sin(a), 0.985 * H), (0.017 * H,) * 3, m, 8, 6), "Head")
            self.add(cyl("braidtail", (0, 0.06 * H, 0.97 * H), (0, 0.085 * H, 0.80 * H), 0.02 * H, 0.012 * H, m, 8), "Head")

    def brow(self, color=(0.05, 0.03, 0.025), heavy=1.0):
        H = self.H
        m = material("brow", color, None, 0.7)
        for s in (1, -1):
            self.add(sphere("brow", (s * 0.026 * H, -0.062 * H, 0.954 * H), (0.021 * H, 0.008 * H * heavy, 0.006 * H * heavy), m, 8, 6), "Head")

    def beard(self, style, color=(0.05, 0.03, 0.025)):
        H = self.H
        m = material("beard", color, None, 0.75)
        if style == "none":
            return
        if style == "stubble":
            self.add(sphere("stubble", (0, -0.032 * H, 0.872 * H), (0.043 * H, 0.04 * H, 0.032 * H), m, 12, 8), "Head")
            return
        if style == "short":
            self.add(sphere("beard", (0, -0.038 * H, 0.868 * H), (0.045 * H, 0.04 * H, 0.04 * H), m, 12, 8), "Head")
            return
        length = {"long": 0.14, "curled": 0.15, "white": 0.17}.get(style, 0.12)
        rows = 6
        for r in range(rows):
            t = r / (rows - 1)
            z = 0.876 * H - t * length * H
            y = -0.045 * H + 0.012 * H * t
            w = (0.044 - 0.03 * t) * H
            self.add(sphere("beard", (0, y, z), (w, 0.028 * H * (1 - 0.3 * t), 0.04 * H), m, 10, 6), "Head")
        if style == "curled":
            for r in range(5):
                t = r / 4
                z = 0.872 * H - t * length * H * 0.95
                w = (0.036 - 0.026 * t) * H
                for x in (-w, w):
                    self.add(sphere("curl", (x, -0.058 * H + 0.012 * H * t, z), (0.012 * H, 0.012 * H, 0.014 * H), m, 6, 5), "Head")
        self.add(sphere("moustache", (0, -0.066 * H, 0.895 * H), (0.03 * H, 0.01 * H, 0.008 * H), m, 8, 6), "Head")

    # ------------------------------------------------------------------ headwear
    def band(self, color_name="gold", z=0.96, jewels=("lapis",), tall=0.018):
        H = self.H
        m = material("band", COLORS[color_name], None, 0.25, 1.0)
        rings = [((z - tall / 2) * H, 0.0645 * H, 0.074 * H, 0, 0.003 * H), ((z + tall / 2) * H, 0.0645 * H, 0.074 * H, 0, 0.003 * H)]
        self.add(tube("diadem", rings, m, 20), "Head")
        for k, jewel in enumerate(jewels):
            x = (k - (len(jewels) - 1) / 2) * 0.026 * H
            self.add(sphere("jewel", (x, -0.072 * H, z * H), (0.01 * H,) * 3, material(jewel, COLORS[jewel], None, 0.2, 0.3), 8, 6), "Head")

    def horns(self, pairs=1, color_name="gold", z=0.99, spread=0.07, size=1.0):
        H = self.H
        m = material("horn", COLORS[color_name], None, 0.3, 0.8 if color_name == "gold" else 0.0)
        cap = [(0.965 * H, 0.066 * H, 0.076 * H, 0, 0.0), (z * H + 0.02 * H, 0.062 * H, 0.072 * H, 0, 0.0)]
        self.add(tube("hornband", cap, m, 18), "Head")
        for p in range(pairs):
            zz = (z + 0.016 * p) * H
            for s in (1, -1):
                pts = []
                for k in range(5):
                    t = k / 4
                    pts.append(Vector((s * (0.065 * H + 0.05 * H * size * math.sin(t * 1.3)), 0.0, zz + 0.11 * H * size * (t ** 1.4))))
                for k in range(4):
                    self.add(cyl("horn", pts[k], pts[k + 1], 0.02 * H * (1 - k * 0.2), 0.02 * H * (1 - (k + 1) * 0.2), m, 8), "Head")

    def tall_crown(self, color_name="gold", tiers=3):
        H = self.H
        m = material("crown", COLORS[color_name], None, 0.25, 1.0)
        white = material("crownwhite", COLORS["white"], "linen", 0.6)
        rings = [(0.955 * H, 0.066 * H, 0.076 * H, 0, 0.0), (1.04 * H, 0.058 * H, 0.066 * H, 0, 0.0),
                 (1.12 * H, 0.046 * H, 0.052 * H, 0, 0.0), (1.15 * H, 0.0005, 0.0005, 0, 0.0)]
        self.add(tube("tallcrown", rings, white, 20), "Head")
        self.add(tube("crownband", [(0.97 * H, 0.0665 * H, 0.0765 * H, 0, 0), (0.99 * H, 0.0665 * H, 0.0765 * H, 0, 0)], m, 20), "Head")
        for t in range(tiers):
            z = (1.0 + 0.045 * t) * H
            for s in (1, -1):
                self.add(cyl("crownhorn", (s * 0.058 * H, 0, z), (s * 0.12 * H, 0, z + 0.05 * H), 0.012 * H, 0.008 * H, m, 8), "Head")

    def star_disc(self, color_name="gold", z=1.07):
        H = self.H
        m = material("star", COLORS[color_name], None, 0.25, 1.0)
        self.add(cyl("stardisc", (0, -0.06 * H, z * H), (0, -0.068 * H, z * H), 0.03 * H, 0.03 * H, m, 16), "Head")
        for k in range(8):
            a = 2 * math.pi * k / 8
            tip = Vector((0.055 * H * math.cos(a), -0.068 * H, z * H + 0.055 * H * math.sin(a)))
            self.add(cyl("starray", Vector((0.02 * H * math.cos(a), -0.066 * H, z * H + 0.02 * H * math.sin(a))), tip, 0.011 * H, 0.001 * H, m, 5), "Head")

    def helmet(self, color_name="copper"):
        H = self.H
        m = material("helmet", COLORS[color_name], None, 0.35, 0.9)
        rings = [(0.925 * H, 0.066 * H, 0.076 * H, 0, 0.0), (0.97 * H, 0.066 * H, 0.076 * H, 0, 0.0),
                 (1.005 * H, 0.05 * H, 0.06 * H, 0, 0.0), (1.027 * H, 0.0005, 0.0005, 0, 0.0)]
        self.add(tube("helmet", rings, m, 18), "Head")
        for s in (1, -1):
            self.add(cyl("cheek", (s * 0.064 * H, 0, 0.93 * H), (s * 0.052 * H, -0.03 * H, 0.87 * H), 0.012 * H, 0.008 * H, m, 6), "Head")

    def scarf(self, color=(0.7, 0.62, 0.45)):
        H = self.H
        m = material("scarf", color, "linen", 0.8)
        rings = [(0.93 * H, 0.066 * H, 0.078 * H, 0, 0.004 * H), (0.99 * H, 0.062 * H, 0.074 * H, 0, 0.004 * H),
                 (1.02 * H, 0.03 * H, 0.04 * H, 0, 0.0), (1.03 * H, 0.0005, 0.0005, 0, 0.0)]
        self.add(tube("scarf", rings, m, 18, arc=(-85, 265)), "Head")
        self.add(tube("scarftail", [(0.93 * H, 0.062 * H, 0.074 * H, 0, 0.005 * H), (0.80 * H, 0.06 * H, 0.07 * H, 0, 0.03 * H)], m, 12, arc=(30, 150)), "Head")

    # ------------------------------------------------------------------ garments
    def _skirt_weights(self, z_top, z_bot, leg_share=0.85):
        H = self.H

        def func(co):
            t = (z_top - co.z) / max(z_top - z_bot, 1e-4)
            leg = max(0.0, (t - 0.25) / 0.75) * leg_share if self.legs else 0.0
            side = smoothstep(-0.04 * H, 0.04 * H, co.x)
            w = {}
            if leg > 0:
                w["Thigh_L"] = leg * side
                w["Thigh_R"] = leg * (1 - side)
            w["Hips"] = 1.0 - leg
            return w
        return func

    def kaunakes(self, length="knee", color=(0.82, 0.74, 0.55), upper_color=None):
        H = self.H
        z_top = 0.585 * H
        z_bot = {"short": 0.40, "knee": 0.275, "ankle": 0.075}[length] * H
        tiers = {"short": 2, "knee": 3, "ankle": 5}[length]
        flare = {"short": 0.03, "knee": 0.045, "ankle": 0.075}[length] * H
        m = material("kaunakes", color, "wool", 1.0)
        span = z_top - z_bot
        for i in range(tiers):
            t0, t1 = i / tiers, (i + 1) / tiers
            za = z_top - span * t0
            zb = z_top - span * t1 - 0.025 * H * (0 if i == tiers - 1 else 1)
            ra = lambda t: (self.hip * 1.12 + flare * t)
            rings = [(za, ra(t0) * 1.0, (self.depth * 1.05 + flare * t0 * 0.75), 0, 0), (zb, ra(t1) * 1.08, (self.depth * 1.05 + flare * t1 * 0.75) * 1.08, 0, 0)]
            obj = tube("kaunakes", rings, m, 24, tuft=0.028 * H)
            self.add(obj, None)
            set_weights(obj, self._skirt_weights(z_top, z_bot))

    def long_robe(self, color=(0.92, 0.9, 0.82), sleeves=False, tex="linen", bare_chest=False):
        H = self.H
        m = material("robe", color, tex, 0.9)
        z_top = 0.79 * H if not bare_chest else 0.585 * H
        z_bot = 0.065 * H
        rings = [(z_top, self.sh * 0.88, self.depth * 1.12, 0, 0), (0.70 * H, self.sh * 0.8, self.depth * 1.12, 0, 0),
                 (0.585 * H, self.hip * 1.15, self.depth * 1.1, 0, 0), (0.35 * H, self.hip * 1.35, self.depth * 1.3, 0, 0),
                 (z_bot, self.hip * 1.6, self.depth * 1.55, 0, 0)]
        obj = tube("robe", rings, m, 24, tuft=0.0)
        self.add(obj, None)
        top, bot = z_top, z_bot

        def func(co):
            if co.z > 0.585 * H:
                u = smoothstep(0.585 * H, 0.70 * H, co.z)
                return {"Chest": u, "Spine": 1 - u}
            return self._skirt_weights(0.585 * H, bot, 0.8)(co)
        set_weights(obj, func)
        if sleeves:
            for s, side in ((1, "L"), (-1, "R")):
                a, b, c = (self.side(k, s) for k in ("shoulder", "elbow", "wrist"))
                self.add(cyl("sleeve", a, b, self.limb * 1.5, self.limb * 1.45, m, 10), "UpperArm_" + side)
                self.add(cyl("sleeve", b, c, self.limb * 1.5, self.limb * 1.3, m, 10), "Forearm_" + side)

    def dress(self, color=(0.92, 0.9, 0.82), length="ankle", tex="linen", tufted=False, shoulder="R"):
        H = self.H
        m = material("dress", color, "wool" if tufted else tex, 0.95)
        z_top = 0.78 * H
        z_bot = {"ankle": 0.07, "knee": 0.28}[length] * H
        self.add(tube("bodice", [(z_top, self.sh * 0.78, self.depth * (1.5 if self.female else 1.15), 0, 0), (0.66 * H, self.hip * 1.05, self.depth * 1.12, 0, 0),
                                 (0.585 * H, self.hip * 1.14, self.depth * 1.12, 0, 0)], m, 22), None)
        set_weights(self.parts[-1], lambda co: {"Chest": smoothstep(0.62 * H, 0.72 * H, co.z), "Spine": 1 - smoothstep(0.62 * H, 0.72 * H, co.z)})
        tiers = 4 if tufted else 1
        span = 0.585 * H - z_bot
        for i in range(tiers):
            za = 0.585 * H - span * i / tiers
            zb = 0.585 * H - span * (i + 1) / tiers - (0.02 * H if i < tiers - 1 else 0)
            flare = (0.07 if length == "ankle" else 0.04) * H
            rings = [(za, self.hip * 1.14 + flare * i / tiers, self.depth * 1.12 + flare * 0.7 * i / tiers, 0, 0),
                     (zb, self.hip * 1.14 + flare * (i + 1) / tiers, (self.depth * 1.12 + flare * 0.7 * (i + 1) / tiers) * 1.05, 0, 0)]
            obj = tube("dressskirt", rings, m, 24, tuft=0.02 * H if tufted else 0.0)
            self.add(obj, None)
            set_weights(obj, self._skirt_weights(0.585 * H, z_bot, 0.8))
        s = -1 if shoulder == "R" else 1
        self.add(cyl("strap", (s * self.sh * 0.35, -self.depth * 1.05, 0.775 * H), (s * self.sh * 0.95, 0, 0.815 * H), 0.02 * H, 0.025 * H, m, 8), "Chest")
        if tufted:
            sh = material("shawl", color, "wool", 1.0)
            self.add(tube("shawl", [(0.84 * H, self.sh * 1.05, self.depth * 1.2, 0, 0.0), (0.74 * H, self.sh * 0.95, self.depth * 1.3, 0, 0.0)], sh, 18, arc=(100, 260), tuft=0.02 * H), "Chest")

    def hide_wrap(self, color=(0.25, 0.16, 0.09), z_top=0.565, z_bot=0.40, tex="fur"):
        H = self.H
        m = material("hide", color, tex, 1.0)
        obj = tube("hide", [(z_top * H, self.hip * 1.12, self.depth * 1.08, 0, 0), (z_bot * H, self.hip * 1.3, self.depth * 1.3, 0, 0)], m, 20, tuft=0.04 * H)
        self.add(obj, None)
        set_weights(obj, self._skirt_weights(z_top * H, z_bot * H, 0.6))

    def cloak(self, color=(0.35, 0.22, 0.12), tex="leather", length=0.42, studs=False):
        H = self.H
        m = material("cloak", color, tex, 0.9)
        rings = [(0.835 * H, self.sh * 1.0, self.depth * 1.35, 0, 0.0), (0.7 * H, self.sh * 1.05, self.depth * 1.5, 0, 0.0),
                 (length * H, self.hip * 1.4, self.depth * 1.8, 0, 0.0)]
        obj = tube("cloak", rings, m, 16, arc=(5, 175), tuft=0.0)
        self.add(obj, None)
        set_weights(obj, lambda co: {"Chest": smoothstep(0.55 * H, 0.75 * H, co.z), "Spine": 1 - smoothstep(0.55 * H, 0.75 * H, co.z)})
        if studs:
            c = material("stud", COLORS["copper"], None, 0.35, 0.9)
            for r in range(3):
                for k in range(6):
                    a = math.radians(30 + k * 24)
                    z = (0.78 - r * 0.1) * H
                    rx = self.sh * (1.02 + 0.03 * r)
                    ry = self.depth * (1.4 + 0.2 * r)
                    self.add(sphere("stud", (rx * math.cos(a), ry * math.sin(a), z), (0.008 * H,) * 3, c, 6, 4), "Chest")

    def apron(self, color=(0.45, 0.3, 0.18)):
        H = self.H
        m = material("apron", color, "leather", 0.95)
        self.add(tube("apron", [(0.74 * H, self.sh * 0.75, self.depth * 1.12, 0, 0), (0.55 * H, self.hip * 1.1, self.depth * 1.2, 0, 0), (0.36 * H, self.hip * 1.2, self.depth * 1.35, 0, 0)],
                      m, 12, arc=(215, 325)), "Spine")
        self.add(cyl("apronstrap", (0, -self.depth * 1.1, 0.74 * H), (0, 0.0, 0.84 * H), 0.012 * H, 0.012 * H, m, 6), "Chest")

    # ------------------------------------------------------------------ jewellery, belts, footwear
    def belt(self, color_name="brown", wide=0.03, buckle=True):
        H = self.H
        mat = material("belt", COLORS[color_name], "leather" if color_name in ("brown",) else None, 0.4, 0.9 if color_name == "gold" else 0.0)
        z = 0.57 * H
        self.add(tube("belt", [((z + wide / 2 * H), self.hip * 1.16, self.depth * 1.12, 0, 0), ((z - wide / 2 * H), self.hip * 1.16, self.depth * 1.12, 0, 0)], mat, 22), "Hips")
        if buckle:
            g = material("buckle", COLORS["gold"], None, 0.25, 1.0)
            self.add(box("buckle", (0, -self.depth * 1.15, z), (0.035 * H, 0.008 * H, 0.03 * H), g), "Hips")

    def collar(self, beads=True):
        H = self.H
        g = material("collar", COLORS["gold"], None, 0.25, 1.0)
        self.add(tube("collar", [(0.805 * H, 0.05 * H, 0.05 * H, 0, -0.01 * H), (0.765 * H, 0.085 * H, 0.075 * H, 0, -0.012 * H)], g, 20), "Chest")
        if beads:
            lap = material("lapisbead", COLORS["lapis"], None, 0.2, 0.2)
            for k in range(7):
                a = math.radians(200 + k * 23)
                self.add(sphere("bead", (0.075 * H * math.cos(a), 0.065 * H * math.sin(a) - 0.012 * H, 0.77 * H), (0.008 * H,) * 3, lap, 6, 4), "Chest")

    def armbands(self, color_name="gold"):
        H = self.H
        g = material("armband", COLORS[color_name], None, 0.25, 1.0)
        for s, side in ((1, "L"), (-1, "R")):
            a, b = self.side("shoulder", s), self.side("elbow", s)
            p0, p1 = a + (b - a) * 0.4, a + (b - a) * 0.55
            self.add(cyl("armband", p0, p1, self.limb * 1.2, self.limb * 1.18, g, 12), "UpperArm_" + side)

    def bracelets(self, color_name="gold"):
        g = material("bracelet", COLORS[color_name], None, 0.25, 1.0)
        for s, side in ((1, "L"), (-1, "R")):
            a, b = self.side("wrist", s), self.side("hand", s)
            self.add(cyl("bracelet", a - (b - a) * 0.15, a + (b - a) * 0.15, self.limb * 0.85, self.limb * 0.85, g, 10), "Hand_" + side)

    def earrings(self, color_name="gold"):
        H = self.H
        g = material("earring", COLORS[color_name], None, 0.25, 1.0)
        for s in (1, -1):
            self.add(sphere("earring", (s * 0.064 * H, 0, 0.9 * H), (0.008 * H, 0.01 * H, 0.016 * H), g, 8, 6), "Head")

    def sandals(self, color=(0.35, 0.22, 0.12)):
        H = self.H
        m = material("sandal", color, "leather", 0.9)
        for s, side in ((1, "L"), (-1, "R")):
            an = self.side("ankle", s)
            self.add(box("sole", (an.x, -0.04 * H, 0.004 * H), (self.limb * 1.8, 0.145 * H, 0.012 * H), m), "Foot_" + side)

    # ------------------------------------------------------------------ props (held in the hands)
    def hold(self, kind, side="R"):
        H = self.H
        s = -1 if side == "R" else 1
        hand = self.hand_pos(s)
        bone = "Hand_" + side
        wood = material("wood", COLORS["wood"], "leather", 0.8)
        gold = material("pgold", COLORS["gold"], None, 0.25, 1.0)
        copper = material("pcopper", COLORS["copper"], None, 0.35, 0.9)
        clay = material("pclay", COLORS["clay"], None, 0.95)
        hx, hy = hand.x, hand.y - 0.012 * H
        if kind == "staff":
            self.add(cyl("staff", (hx, hy, 0.0), (hx, hy, 1.1 * H), 0.012 * H, 0.014 * H, wood, 8), bone)
            self.arm_swing[side] = 0.15
        elif kind == "pole":
            self.add(cyl("pole", (hx, hy, 0.0), (hx, hy, 1.32 * H), 0.012 * H, 0.012 * H, wood, 8), bone)
            self.arm_swing[side] = 0.15
        elif kind == "spear":
            self.add(cyl("spear", (hx, hy, 0.0), (hx, hy, 1.15 * H), 0.009 * H, 0.009 * H, wood, 8), bone)
            self.add(cyl("spearhead", (hx, hy, 1.13 * H), (hx, hy, 1.27 * H), 0.025 * H, 0.001 * H, copper, 6), bone)
            self.arm_swing[side] = 0.12
        elif kind == "mace":
            self.add(cyl("mace", (hx, hy, 0.38 * H), (hx, hy, 0.58 * H), 0.01 * H, 0.011 * H, wood, 8), bone)
            self.add(sphere("macehead", (hx, hy, 0.6 * H), (0.03 * H,) * 3, gold, 10, 8), bone)
        elif kind == "club":
            self.add(cyl("club", (hx, hy, 0.4 * H), (hx, hy, 0.9 * H), 0.014 * H, 0.05 * H, wood, 8), bone)
            self.arm_swing[side] = 0.3
        elif kind == "shield":
            self.add(sphere("shield", (hx + s * 0.03 * H, hy - 0.05 * H, 0.52 * H), (0.1 * H, 0.014 * H, 0.1 * H), copper, 14, 8), bone)
        elif kind == "tablet":
            self.add(box("tablet", (hx, hy - 0.015 * H, 0.47 * H), (0.045 * H, 0.012 * H, 0.06 * H), clay), bone)
            self.add(cyl("stylus", (hx + 0.02 * H, hy, 0.42 * H), (hx + 0.02 * H, hy - 0.02 * H, 0.53 * H), 0.003 * H, 0.002 * H, wood, 5), bone)
            self.arm_swing[side] = 0.4
        elif kind == "balance":
            self.add(cyl("beam", (hx - 0.1 * H, hy, 0.6 * H), (hx + 0.1 * H, hy, 0.6 * H), 0.005 * H, 0.005 * H, copper, 6), bone)
            for ox in (-0.1, 0.1):
                self.add(cyl("pan", (hx + ox * H, hy, 0.54 * H), (hx + ox * H, hy, 0.535 * H), 0.04 * H, 0.04 * H, copper, 12), bone)
                self.add(cyl("string", (hx + ox * H, hy, 0.6 * H), (hx + ox * H, hy, 0.54 * H), 0.002 * H, 0.002 * H, copper, 4), bone)
            self.arm_swing[side] = 0.3
        elif kind == "pot":
            self.add(sphere("pot", (hx, hy - 0.03 * H, 0.46 * H), (0.045 * H, 0.045 * H, 0.05 * H), clay, 12, 8), bone)
            self.add(cyl("potneck", (hx, hy - 0.03 * H, 0.49 * H), (hx, hy - 0.03 * H, 0.54 * H), 0.025 * H, 0.032 * H, clay, 10), bone)
            self.arm_swing[side] = 0.4
        elif kind == "spindle":
            self.add(cyl("spindle", (hx, hy, 0.4 * H), (hx, hy - 0.02 * H, 0.62 * H), 0.004 * H, 0.004 * H, wood, 5), bone)
            self.add(cyl("whorl", (hx, hy - 0.005 * H, 0.45 * H), (hx, hy - 0.005 * H, 0.46 * H), 0.025 * H, 0.025 * H, clay, 10), bone)
            self.arm_swing[side] = 0.4

    def back_item(self, kind):
        H = self.H
        leather = material("leather", (0.32, 0.2, 0.11), "leather", 0.9)
        if kind == "quiver":
            self.add(cyl("quiver", (-0.05 * H, self.depth * 1.5, 0.64 * H), (0.04 * H, self.depth * 1.2, 0.92 * H), 0.025 * H, 0.03 * H, leather, 8), "Chest")
            wood = material("arrow", COLORS["wood"], None, 0.8)
            for k in range(3):
                self.add(cyl("arrow", (0.03 * H, self.depth * 1.2, 0.9 * H), (0.04 * H + 0.008 * k * H, self.depth * 1.2, 0.99 * H), 0.003 * H, 0.003 * H, wood, 4), "Chest")
        elif kind == "satchel":
            self.add(box("satchel", (self.hip * 1.25, -0.01 * H, 0.50 * H), (0.04 * H, 0.09 * H, 0.1 * H), leather), "Hips")
            self.add(cyl("satchelstrap", (-self.sh * 0.7, -self.depth * 0.9, 0.78 * H), (self.hip * 1.25, 0, 0.55 * H), 0.007 * H, 0.007 * H, leather, 5), "Chest")
        elif kind == "pouch":
            self.add(sphere("pouch", (self.hip * 1.1, -self.depth * 0.8, 0.55 * H), (0.03 * H, 0.025 * H, 0.04 * H), leather, 8, 6), "Hips")
        elif kind == "tablets":
            clay = material("pclay", COLORS["clay"], None, 0.95)
            for k in range(3):
                self.add(box("tabletstack", (self.hip * 1.3, 0.0, 0.5 * H + k * 0.012 * H), (0.05 * H, 0.07 * H, 0.01 * H), clay), "Hips")

    def horned_features(self):
        """Tusks and a heavy brow of Humbaba."""
        H = self.H
        bone_m = material("tusk", COLORS["bone"], None, 0.5)
        for s in (1, -1):
            self.add(cyl("tusk", (s * 0.02 * H, -0.062 * H, 0.884 * H), (s * 0.03 * H, -0.075 * H, 0.935 * H), 0.007 * H, 0.001 * H, bone_m, 6), "Head")

    def fur_tufts(self, parts, count=40, color=(0.22, 0.14, 0.08), seed=5):
        m = material("fur", color, "fur", 1.0)
        for i, (p0, p1, r, bone) in enumerate(parts):
            pts = surface_points(p0, p1, r, count, seed + i)
            self.add(cone_tufts("fur", m, pts, 0.022 * self.H, 0.0065 * self.H, seed=seed + i), bone)

    # ------------------------------------------------------------------ rig and export
    def finish(self, output_path, anim_arm_swing=True, extra_bones=None, post_join=None, anim=None):
        return finish_rig(self, output_path, anim_arm_swing, extra_bones, post_join, anim)


def _bone_table(h, extra=None):
    H = h.H
    t = {}
    t["Root"] = ((0, 0, 0), (0, 0, 0.05 * H), None)
    t["Hips"] = ((0, 0, 0.50 * H), (0, 0, 0.56 * H), "Root")
    t["Spine"] = ((0, 0, 0.56 * H), (0, 0, 0.66 * H), "Hips")
    t["Chest"] = ((0, 0, 0.66 * H), (0, 0, 0.80 * H), "Spine")
    t["Neck"] = ((0, 0, 0.80 * H), (0, 0, 0.85 * H), "Chest")
    t["Head"] = ((0, 0, 0.85 * H), (0, 0, 1.0 * H), "Neck")
    t["Head_end"] = ((0, 0, 1.0 * H), (0, 0, 1.03 * H), "Head")
    for s, side in ((1, "L"), (-1, "R")):
        t["UpperArm_" + side] = (h.side("shoulder", s), h.side("elbow", s), "Chest")
        t["Forearm_" + side] = (h.side("elbow", s), h.side("wrist", s), "UpperArm_" + side)
        t["Hand_" + side] = (h.side("wrist", s), h.side("hand", s), "Forearm_" + side)
        if h.legs:
            t["Thigh_" + side] = (h.side("hip", s), h.side("knee", s), "Hips")
            t["Shin_" + side] = (h.side("knee", s), h.side("ankle", s), "Thigh_" + side)
            t["Foot_" + side] = (h.side("ankle", s), h.side("toe", s), "Shin_" + side)
    if extra:
        t.update(extra)
    return t


def make_armature(name, table):
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    made = {}
    # parents first
    pending = dict(table)
    while pending:
        progress = False
        for key, (head, tail, parent) in list(pending.items()):
            if parent is None or parent in made:
                eb = arm.edit_bones.new(key)
                eb.head = Vector(head)
                eb.tail = Vector(tail)
                if (eb.tail - eb.head).length < 0.01:
                    eb.tail = eb.head + Vector((0, 0, 0.02))
                if parent is not None:
                    eb.parent = made[parent]
                made[key] = eb
                del pending[key]
                progress = True
        if not progress:
            raise RuntimeError("bone parents unresolved: %s" % list(pending))
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def _apply_part_weights(o, all_bones):
    bone, wfunc, extra = skin_of(o)
    wf = get_weights(o)
    for v in o.data.vertices:
        if wf is not None:
            weights = wf(v.co)
        elif bone:
            weights = {bone: 1.0}
        else:
            weights = {"Hips": 1.0}
        total = sum(weights.values()) or 1.0
        for b, w in weights.items():
            if w > 1e-4 and b in all_bones:
                g = o.vertex_groups.get(b) or o.vertex_groups.new(name=b)
                g.add([v.index], w / total, "REPLACE")
        for name in extra:
            g = o.vertex_groups.get(name) or o.vertex_groups.new(name=name)
            g.add([v.index], 1.0, "REPLACE")


def _smooth_weights(obj, iterations=6, blend=0.5, keep=4):
    mesh = obj.data
    neighbours = [[] for _ in mesh.vertices]
    for e in mesh.edges:
        a, b = e.vertices
        neighbours[a].append(b)
        neighbours[b].append(a)
    names = {g.index: g.name for g in obj.vertex_groups}
    weights = [{g.group: g.weight for g in v.groups} for v in mesh.vertices]
    for _ in range(iterations):
        new = []
        for i, w in enumerate(weights):
            acc = {}
            nb = neighbours[i]
            for j in nb:
                for g, x in weights[j].items():
                    acc[g] = acc.get(g, 0.0) + x / len(nb)
            out = {}
            for g in set(w) | set(acc):
                out[g] = w.get(g, 0.0) * (1 - blend) + acc.get(g, 0.0) * blend
            new.append(out)
        weights = new
    for g in list(obj.vertex_groups):
        obj.vertex_groups.remove(g)
    groups = {i: obj.vertex_groups.new(name=n) for i, n in names.items()}
    for i, w in enumerate(weights):
        top = sorted(w.items(), key=lambda kv: -kv[1])[:keep]
        total = sum(x for _, x in top) or 1.0
        for g, x in top:
            if x / total > 0.01:
                groups[g].add([i], x / total, "REPLACE")


def fuse_organic(h, all_bones):
    """Skin parts become one seamless mesh (voxel remesh, smoothed) that takes over the weights of the parts."""
    parts = list(h.organic)
    if not parts:
        return
    for o in parts:
        _apply_part_weights(o, all_bones)
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    src = bpy.context.view_layer.objects.active
    src.name = "organic_src"
    org = src.copy()
    org.data = src.data.copy()
    org.name = "organic"
    bpy.context.scene.collection.objects.link(org)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = org
    org.select_set(True)
    for g in list(org.vertex_groups):
        org.vertex_groups.remove(g)
    rm = org.modifiers.new("rm", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = h.H * 0.0062
    rm.use_smooth_shade = True
    bpy.ops.object.modifier_apply(modifier="rm")
    sm = org.modifiers.new("sm", "SMOOTH")
    sm.factor = 0.7
    sm.iterations = 8
    bpy.ops.object.modifier_apply(modifier="sm")
    count = len(org.data.vertices)
    if count > 9000:
        dec = org.modifiers.new("dec", "DECIMATE")
        dec.ratio = 9000.0 / count
        bpy.ops.object.modifier_apply(modifier="dec")
    for g in src.vertex_groups:
        org.vertex_groups.new(name=g.name)
    dt = org.modifiers.new("dt", "DATA_TRANSFER")
    dt.object = src
    dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}
    dt.vert_mapping = "NEAREST"
    dt.layers_vgroup_select_src = "ALL"
    dt.layers_vgroup_select_dst = "NAME"
    bpy.ops.object.modifier_apply(modifier="dt")
    bpy.data.objects.remove(src)
    for p in parts:
        if p in h.parts:
            h.parts.remove(p)
    _smooth_weights(org)
    for poly in org.data.polygons:
        poly.use_smooth = True
    h.parts.append(org)
    assign(org, "__keep__")


def join_and_skin(h, armature, all_bones, post_join=None, dz=0.0):
    """Give every part its vertex groups, join the parts into one mesh and add the armature modifier."""
    objs = h.parts
    for o in objs:
        if skin_of(o)[0] == "__keep__":
            continue
        _apply_part_weights(o, all_bones)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    body = bpy.context.view_layer.objects.active
    body.name = h.name
    body.data.name = h.name
    for name in ("blink", "mouth"):
        if name not in body.vertex_groups:
            body.vertex_groups.new(name=name)
    if dz:
        for v in body.data.vertices:
            v.co.z += dz
    mod = body.modifiers.new("Armature", "ARMATURE")
    mod.object = armature
    body.parent = armature
    return body


def add_face_shapes(h, body, dz=0.0):
    H = h.H
    body.shape_key_add(name="Basis", from_mix=False)
    blink_idx = body.vertex_groups["blink"].index
    mouth_idx = body.vertex_groups["mouth"].index
    me = body.data
    eye_z = [c[2] + dz for c in h.eye_centers]
    mc = Vector(h.mouth_center) + Vector((0, 0, dz))

    def in_group(v, gi):
        return any(g.group == gi and g.weight > 0.5 for g in v.groups)

    def key(name, fn_blink=None, fn_mouth=None):
        k = body.shape_key_add(name=name, from_mix=False)
        for i, v in enumerate(me.vertices):
            if fn_blink and in_group(v, blink_idx):
                c = min(eye_z, key=lambda z: abs(z - v.co.z))
                k.data[i].co = Vector((v.co.x, v.co.y, c + (v.co.z - c) * 0.08))
            if fn_mouth and in_group(v, mouth_idx):
                d = v.co - mc
                k.data[i].co = mc + fn_mouth(d)
    key("vrc_blink", fn_blink=True)
    shapes = {"aa": (1.0, 7.0, 1.4), "oh": (0.65, 6.0, 1.7), "ee": (1.35, 3.0, 0.8), "ou": (0.5, 5.0, 1.4),
              "ih": (1.1, 3.8, 1.0), "dd": (1.0, 4.0, 1.1), "ch": (0.8, 3.0, 1.2)}
    for name, (sx, sz, sy) in shapes.items():
        key("vrc_v_" + name, fn_mouth=lambda d, sx=sx, sz=sz, sy=sy: Vector((d.x * sx, d.y * sy, d.z * sz - 0.0012 * H * (sz - 1) * 0.6)))


def _pose(arm, bone, rot=None, loc=None, frame=1):
    pb = arm.pose.bones.get(bone)
    if pb is None:
        return
    pb.rotation_mode = "XYZ"
    if rot is not None:
        pb.rotation_euler = rot
        pb.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        pb.location = loc
        pb.keyframe_insert("location", frame=frame)


def make_action(arm, name, frames, fn):
    """fn(t01) -> {bone: (rot_xyz | None, loc_xyz | None)}; keyed at `frames`+1 points, cycle closed."""
    action = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = action
    n = frames
    steps = max(8, n // 3) if n > 30 else 8
    for s in range(steps + 1):
        t = s / steps
        frame = 1 + round(t * n)
        for bone, (rot, loc) in fn(t % 1.0 if s < steps else 0.0).items():
            _pose(arm, bone, rot, loc, frame)
    arm.animation_data.action = None
    track = arm.animation_data.nla_tracks.new()
    track.name = name
    track.strips.new(name, 1, action)
    return action


def local_rot(arm, bone, *turns):
    """Euler rotation of a pose bone that turns it about global axes, e.g. local_rot(arm, 'Tail1', ('X', 0.3))."""
    from mathutils import Matrix
    basis = arm.data.bones[bone].matrix_local.to_3x3()
    total = Matrix.Identity(3)
    for axis, angle in turns:
        total = Matrix.Rotation(angle, 3, axis) @ total
    return tuple((basis.inverted() @ total @ basis).to_euler('XYZ'))


def humanoid_animations(h, arm, bobbing=1.0, extra_walk=None, extra_idle=None):
    H = h.H
    swing = h.arm_swing
    stride = 0.52 if H < 2.6 else 0.4
    two_pi = 2 * math.pi

    def walk(t):
        a = two_pi * t
        d = {}
        for side, ph in (("L", 0.0), ("R", 0.5)):
            tt = t + ph
            sw = math.sin(two_pi * tt)
            flex = max(0.0, math.cos(two_pi * tt)) ** 1.5
            d["Thigh_" + side] = ((-stride * sw, 0, 0), None)
            d["Shin_" + side] = ((0.08 + 0.95 * flex, 0, 0), None)
            d["Foot_" + side] = ((0.15 * sw - 0.15 * flex, 0, 0), None)
            arm_side = "R" if side == "L" else "L"
            amp = 0.42 * swing[arm_side]
            d["UpperArm_" + arm_side] = ((amp * math.sin(two_pi * tt), 0, 0), None)
            d["Forearm_" + arm_side] = ((-0.15 - 0.25 * swing[arm_side] * max(0.0, -math.sin(two_pi * tt)), 0, 0), None)
        d["Hips"] = ((0, 0.09 * math.sin(a), 0.03 * math.sin(a * 2)), (0, bobbing * 0.014 * H * math.cos(2 * a), 0))
        d["Spine"] = ((-0.05, -0.05 * math.sin(a), 0), None)
        d["Chest"] = ((0, -0.07 * math.sin(a), 0), None)
        d["Head"] = ((0.04, 0.0, 0), None)
        if extra_walk:
            d.update(extra_walk(t))
        return d

    def idle(t):
        a = two_pi * t
        d = {}
        d["Hips"] = ((0, 0, 0), (0, 0.004 * H * math.sin(a), 0))
        d["Spine"] = ((0.015 * math.sin(a), 0, 0), None)
        d["Chest"] = ((0.02 * math.sin(a + 0.6), 0.015 * math.sin(a), 0), None)
        d["Head"] = ((0.02 * math.sin(a - 0.6), 0.06 * math.sin(a), 0), None)
        for side, s in (("L", 1), ("R", -1)):
            d["UpperArm_" + side] = ((0.025 * math.sin(a + s), 0, 0.01 * math.sin(a)), None)
            d["Forearm_" + side] = ((-0.08 - 0.02 * math.sin(a), 0, 0), None)
        if extra_idle:
            d.update(extra_idle(t))
        return d
    make_action(arm, "Idle", 72, idle)
    make_action(arm, "Walk", 24, walk)


def finish_rig(h, output_path, anim_arm_swing=True, extra_bones=None, post_join=None, anim=None):
    table = _bone_table(h, extra_bones)
    if h.dz:
        table = {k: (tuple(Vector(hd) + Vector((0, 0, h.dz))), tuple(Vector(tl) + Vector((0, 0, h.dz))), p) for k, (hd, tl, p) in table.items()}
    arm = make_armature(h.name + "_Armature", table)
    arm.show_in_front = False
    fuse_organic(h, list(table.keys()))
    body = join_and_skin(h, arm, list(table.keys()), dz=h.dz)
    add_face_shapes(h, body, h.dz)
    if post_join:
        post_join(h, arm, body)
    # shift (monsters standing on something else) is applied by the caller through h.dz before this point
    bpy.context.view_layer.objects.active = arm
    if anim:
        anim(h, arm)
    else:
        humanoid_animations(h, arm)
    export_glb(output_path)
    return arm, body


def export_glb(path):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=path, export_format="GLB", use_selection=True, export_animations=True,
        export_animation_mode="NLA_TRACKS", export_morph=True, export_skins=True, export_image_format="JPEG",
        export_jpeg_quality=85, export_yup=True, export_apply=False, export_lights=False, export_cameras=False,
        export_extras=False, export_force_sampling=True, export_frame_range=False)
