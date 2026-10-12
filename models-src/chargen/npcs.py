"""The 20 NPCs of the Gilgamesh datadisk: look of each, from research/CHARACTER_DESIGN.md.

Run:  blender -b --python models-src/build_models.py -- <npc_id|all> media/models
"""
from .core import reset_scene
from .humanoid import Humanoid

SKIN_DARK = (0.62, 0.42, 0.28)
SKIN_MID = (0.72, 0.52, 0.36)
SKIN_LIGHT = (0.8, 0.6, 0.45)
HAIR_BLACK = (0.04, 0.03, 0.025)
HAIR_GREY = (0.7, 0.68, 0.65)
WOOL = (0.82, 0.74, 0.55)
WOOL_WHITE = (0.93, 0.9, 0.8)
WOOL_RED = (0.6, 0.12, 0.08)
WOOL_BLUE = (0.22, 0.3, 0.6)
WOOL_BROWN = (0.5, 0.36, 0.22)


def gilgamesh(h):
    h.hair("bun", HAIR_BLACK); h.brow(HAIR_BLACK); h.beard("curled", HAIR_BLACK)
    h.kaunakes("ankle", WOOL_WHITE); h.belt("gold", 0.04)
    h.collar(); h.armbands(); h.bracelets(); h.band("gold", 0.962, ("lapis", "carnelian", "lapis"))
    h.sandals(); h.hold("mace", "R")


def enkidu(h):
    H = h.H
    h.hair("matted", (0.22, 0.14, 0.08)); h.brow((0.22, 0.14, 0.08), 1.4); h.beard("long", (0.22, 0.14, 0.08))
    h.hide_wrap((0.28, 0.18, 0.1), 0.565, 0.42)
    parts = []
    for s, side in ((1, "L"), (-1, "R")):
        parts.append((h.side("shoulder", s), h.side("elbow", s), h.limb * 1.05, "UpperArm_" + side))
        parts.append((h.side("elbow", s), h.side("wrist", s), h.limb * 0.9, "Forearm_" + side))
        parts.append((h.side("hip", s), h.side("knee", s), h.limb * 1.3, "Thigh_" + side))
        parts.append((h.side("knee", s), h.side("ankle", s), h.limb * 0.95, "Shin_" + side))
    parts.append(((0, 0, 0.62 * H), (0, 0, 0.78 * H), h.sh * 0.8, "Chest"))
    h.fur_tufts(parts, 36, (0.4, 0.27, 0.16))


def enkidu_civilized(h):
    h.hair("long", (0.14, 0.09, 0.05)); h.brow((0.14, 0.09, 0.05), 1.2); h.beard("short", (0.14, 0.09, 0.05))
    h.kaunakes("knee", WOOL); h.belt("brown", 0.035)
    h.armbands("copper"); h.sandals(); h.back_item("pouch")


def ishtar(h):
    h.hair("long", HAIR_BLACK); h.brow(HAIR_BLACK, 0.8)
    h.dress(WOOL_RED, "ankle", tufted=True, shoulder="R"); h.belt("gold", 0.03, False)
    h.collar(); h.earrings(); h.bracelets(); h.armbands()
    h.horns(2, "gold", 0.985, size=1.2); h.star_disc("gold", 1.05)
    h.sandals(); h.back_item("quiver")


def shamhat(h):
    h.hair("braid_wrap", HAIR_BLACK); h.brow(HAIR_BLACK, 0.8)
    h.dress(WOOL_WHITE, "ankle", tufted=False, shoulder="L"); h.belt("gold", 0.025, False)
    h.earrings(); h.bracelets(); h.collar()
    h.sandals()


def humbaba(h):
    H = h.H
    h.hair("matted", (0.1, 0.08, 0.05)); h.brow((0.1, 0.08, 0.05), 3.0); h.beard("long", (0.1, 0.08, 0.05))
    h.horned_features()
    h.hide_wrap((0.2, 0.14, 0.09), 0.57, 0.38)
    h.hold("club", "R")
    bone = None
    parts = []
    for s, side in ((1, "L"), (-1, "R")):
        parts.append((h.side("shoulder", s), h.side("elbow", s), h.limb * 1.05, "UpperArm_" + side))
        parts.append((h.side("hip", s), h.side("knee", s), h.limb * 1.3, "Thigh_" + side))
    parts.append(((0, 0, 0.62 * H), (0, 0, 0.78 * H), h.sh * 0.8, "Chest"))
    h.fur_tufts(parts, 40, (0.3, 0.26, 0.18), seed=21)
    # bone and stone necklace
    from .core import material, sphere
    from .humanoid import COLORS
    bm = material("bonebead", COLORS["bone"], None, 0.6)
    import math
    for k in range(9):
        a = math.radians(190 + k * 20)
        h.add(sphere("bead", (0.1 * H * math.cos(a), 0.09 * H * math.sin(a) - 0.02 * H, 0.775 * H), (0.012 * H,) * 3, bm, 6, 4), "Chest")


def utnapishtim(h):
    h.hair("long", HAIR_GREY); h.brow(HAIR_GREY); h.beard("white", HAIR_GREY)
    h.long_robe(WOOL_WHITE, sleeves=True); h.belt("brown", 0.03, False)
    h.sandals(); h.hold("staff", "R")


def ur_shanabi(h):
    h.hair("bald"); h.brow(HAIR_BLACK); h.beard("short", HAIR_BLACK)
    h.kaunakes("short", WOOL_BROWN); h.belt("brown", 0.03, False); h.back_item("pouch")
    h.hold("pole", "R")


def ninsun(h):
    h.hair("braid_wrap", HAIR_BLACK); h.brow(HAIR_BLACK, 0.8)
    h.dress(WOOL_BLUE, "ankle", tufted=True, shoulder="R"); h.belt("gold", 0.03, False)
    h.collar(); h.earrings(); h.armbands(); h.horns(1, "gold", 0.985); h.sandals()


def anu(h):
    h.hair("long", HAIR_GREY); h.brow(HAIR_GREY); h.beard("white", HAIR_GREY)
    h.long_robe((0.55, 0.65, 0.9), sleeves=True); h.belt("gold", 0.04)
    h.collar(); h.tall_crown("gold", 4); h.hold("mace", "R"); h.sandals()


def high_priest_anu(h):
    h.hair("bald"); h.brow(HAIR_BLACK, 0.9); h.beard("short", (0.1, 0.08, 0.06))
    h.kaunakes("ankle", WOOL_WHITE); h.collar(); h.band("gold", 0.962, ("lapis",)); h.belt("brown", 0.03, False)
    h.hold("tablet", "L"); h.sandals()


def high_priestess_ishtar(h):
    h.hair("braid_wrap", HAIR_BLACK); h.brow(HAIR_BLACK, 0.8)
    h.dress(WOOL_RED, "ankle", tufted=True, shoulder="R"); h.belt("gold", 0.03, False)
    h.collar(); h.earrings(); h.bracelets(); h.horns(1, "gold", 0.985); h.hold("mace", "R"); h.sandals()


def temple_scribe(h):
    h.hair("bald"); h.brow(HAIR_BLACK, 0.9); h.beard("stubble", HAIR_BLACK)
    h.kaunakes("knee", WOOL); h.belt("brown", 0.03, False); h.back_item("satchel"); h.hold("tablet", "L"); h.sandals()


def royal_guard(h):
    h.hair("short", HAIR_BLACK); h.brow(HAIR_BLACK, 1.2); h.beard("short", HAIR_BLACK)
    h.kaunakes("knee", WOOL); h.cloak((0.3, 0.2, 0.12), "leather", 0.42, studs=True); h.helmet("copper")
    h.belt("brown", 0.04); h.hold("spear", "R"); h.hold("shield", "L"); h.sandals()


def uruk_noble(h):
    h.hair("bun", HAIR_BLACK); h.brow(HAIR_BLACK); h.beard("curled", HAIR_BLACK)
    h.kaunakes("ankle", (0.72, 0.62, 0.9)); h.belt("gold", 0.035)
    h.collar(); h.armbands(); h.bracelets(); h.hold("staff", "R"); h.sandals()


def uruk_merchant(h):
    h.hair("short", HAIR_BLACK); h.brow(HAIR_BLACK); h.beard("short", HAIR_BLACK)
    h.kaunakes("knee", (0.75, 0.5, 0.25)); h.cloak((0.55, 0.28, 0.2), "wool", 0.5)
    h.belt("brown", 0.035); h.back_item("pouch"); h.hold("balance", "R"); h.sandals()


def potter(h):
    h.hair("bald"); h.brow(HAIR_BLACK); h.beard("stubble", HAIR_BLACK)
    h.kaunakes("short", WOOL_BROWN); h.apron((0.55, 0.36, 0.22)); h.belt("brown", 0.03, False)
    h.hold("pot", "L")


def weaver(h):
    h.hair("long", HAIR_BLACK); h.brow(HAIR_BLACK, 0.8); h.scarf((0.7, 0.55, 0.35))
    h.dress((0.6, 0.45, 0.28), "ankle", tufted=False, shoulder="R"); h.belt("brown", 0.03, False)
    h.earrings(); h.hold("spindle", "R"); h.sandals()


# id -> (builder, height, build, female, skin)
HUMANOIDS = {
    "gilgamesh": (gilgamesh, 2.0, "hero", False, SKIN_MID),
    "enkidu": (enkidu, 1.9, "stocky", False, (0.58, 0.42, 0.3)),
    "enkidu_civilized": (enkidu_civilized, 1.9, "stocky", False, (0.64, 0.46, 0.32)),
    "ishtar": (ishtar, 1.85, "woman", True, SKIN_LIGHT),
    "shamhat": (shamhat, 1.7, "woman", True, SKIN_LIGHT),
    "humbaba": (humbaba, 3.0, "monster", False, (0.4, 0.38, 0.28)),
    "utnapishtim": (utnapishtim, 1.75, "old", False, SKIN_DARK),
    "ur_shanabi": (ur_shanabi, 1.78, "lean", False, SKIN_DARK),
    "ninsun": (ninsun, 1.75, "woman", True, SKIN_LIGHT),
    "anu": (anu, 2.1, "hero", False, (0.78, 0.66, 0.55)),
    "high_priest_anu": (high_priest_anu, 1.8, "man", False, SKIN_LIGHT),
    "high_priestess_ishtar": (high_priestess_ishtar, 1.72, "woman", True, SKIN_MID),
    "temple_scribe": (temple_scribe, 1.7, "lean", False, SKIN_MID),
    "royal_guard": (royal_guard, 1.85, "hero", False, SKIN_DARK),
    "uruk_noble": (uruk_noble, 1.8, "man", False, SKIN_LIGHT),
    "uruk_merchant": (uruk_merchant, 1.72, "stocky", False, SKIN_MID),
    "potter": (potter, 1.75, "stocky", False, SKIN_DARK),
    "weaver": (weaver, 1.65, "woman", True, SKIN_MID),
}


def build_humanoid(npc_id, out_path):
    builder, height, build, female, skin = HUMANOIDS[npc_id]
    reset_scene()
    h = Humanoid(npc_id, height, build, female, skin)
    h.build_body()
    builder(h)
    return h.finish(out_path)
