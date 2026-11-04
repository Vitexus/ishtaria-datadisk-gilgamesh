#!/usr/bin/env python3
"""The elders of the world: each knows ONE tale and where ONE clay tablet lies (written by this tool; do not edit the output).

    tools/build_elders.py

An elder used to tell every legend of the disk and name every tablet, so one grandfather was enough and the player had no
reason to ask another. Now an elder (an NPC tagged `elder`, men and women have their own tales) tells one story, with all
its chapters, and, as a separate choice of the dialogue, says where ONE tablet of that story lies (`reveal_places` of that
tablet alone). To learn the other stories, or the places of the other tablets of the same story, the player has to ask
other elders. A tablet is known to the elders assigned to it; with more elders than tablets of one kind the first ones
are told by two.

Writes dialogues/elder_<story>_<number>_<m|w>.yaml (one per tablet and sex that an elder is assigned), the text block
between `# BEGIN elders` and `# END elders` of i18n/en.yaml and i18n/cs.yaml, and points the elders of npcs/crowd.yaml and
npcs/hunter_village_folk.yaml at their dialogue. `dialogue_id(sex, index)` is the assignment (index 0 is the elder of the
market of Uruk, 1.. the elders of the homes of the hunter's village), which tools/build_village.py imports.

Pure Python; deterministic.
"""
import glob
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

# sex -> story -> (greet text key, [(choice text key, node id, text key)] chapters, tablet places)
MAN, WOMAN = "m", "w"
STORIES = {
    MAN: {
        "atrahasis": {
            "greet": "elder_tales_man.greet",
            "chapters": [("elder_tales_man.ask_men", "men", "elder_tales_man.men"),
                         ("elder_tales_man.ask_death", "death", "elder_tales_man.death"),
                         ("elder_tales_man.ask_flood", "flood", "elder_tales_man.flood")],
            "tablets": ["atrahasis_tablet_1", "atrahasis_tablet_2", "atrahasis_tablet_3"],
        },
        "etana": {
            "greet": "elder_story.etana_man.greet",
            "chapters": [("elder_tales_man.ask_etana", "etana", "elder_tales_man.etana")],
            "tablets": ["etana_tablet_1", "etana_tablet_2", "etana_tablet_3"],
        },
        "adapa": {
            "greet": "elder_story.adapa_man.greet",
            "chapters": [("elder_tales_man.ask_adapa", "adapa", "elder_tales_man.adapa")],
            "tablets": ["adapa_tablet_1", "adapa_tablet_2"],
        },
        "enuma_elish": {
            "greet": "elder_story.enuma_elish_man.greet",
            "chapters": [("elder_tales_man.ask_akitu", "akitu_gate", None)],
            "tablets": ["enuma_elish_tablet_%d" % n for n in range(1, 8)],
        },
    },
    WOMAN: {
        "ishtar_descent": {
            "greet": "elder_tales_woman.greet",
            "chapters": [("elder_tales_woman.ask_gates", "gates", "elder_tales_woman.gates"),
                         ("elder_tales_woman.ask_return", "return", "elder_tales_woman.return"),
                         ("elder_tales_woman.ask_dumuzi", "dumuzi", "elder_tales_woman.dumuzi")],
            "tablets": ["ishtar_descent_tablet_%d" % n for n in range(1, 7)],
        },
        "enuma_elish": {
            "greet": "elder_story.enuma_elish_woman.greet",
            "chapters": [("elder_tales_woman.ask_akitu", "akitu_gate", None)],
            "tablets": ["enuma_elish_tablet_%d" % n for n in range(1, 8)],
        },
        "dilmun": {
            "greet": "elder_story.dilmun_woman.greet",
            "chapters": [("elder_tales_woman.ask_dilmun", "dilmun", "elder_tales_woman.dilmun")],
            "tablets": ["dilmun_tablet_1", "dilmun_tablet_2"],
        },
        "nergal": {
            "greet": "elder_story.nergal_woman.greet",
            "chapters": [("elder_tales_woman.ask_nergal", "nergal", "elder_tales_woman.nergal")],
            "tablets": ["nergal_tablet_1", "nergal_tablet_2"],
        },
    },
}
LEAVE = {MAN: "elder_tales_man.leave", WOMAN: "elder_tales_woman.leave"}
AKITU = {MAN: ("elder_tales_man.akitu", "elder_tales_man.akitu_now"), WOMAN: ("elder_tales_woman.akitu", "elder_tales_woman.akitu_now")}

NEW_GREETS = {
    "elder_story.etana_man.greet": (
        "Sit, child. Kingship came down from heaven to Kish, and I know how it was found: the old tale of Etana and the eagle, as my father told it. Ask, and I will tell.",
        "Posaď se, dítě. Království sestoupilo z nebe do Kiše a já vím, jak se našlo: stará povídka o Etanovi a orlu, tak jak mi ji vyprávěl otec. Ptej se, povím."),
    "elder_story.adapa_man.greet": (
        "Sit, child. I know the tale of Adapa of Eridu, the wise man who lost his chance of living for ever, as my father told it. Ask, and I will tell.",
        "Posaď se, dítě. Znám příběh o Adapovi z Eridu, moudrém muži, který přišel o věčný život, tak jak mi ho vyprávěl otec. Ptej se, povím."),
    "elder_story.enuma_elish_man.greet": (
        "Sit, child. Every New Year I hear the great song of Marduk and Tiamat, and I know it by heart. Ask, and I will tell.",
        "Posaď se, dítě. Každý Nový rok slyším velkou píseň o Mardukovi a Tiamat a znám ji nazpaměť. Ptej se, povím."),
    "elder_story.enuma_elish_woman.greet": (
        "Come close to the fire, little one. I carry a lamp in the procession of the New Year and I know the song of Marduk and Tiamat. Ask, and I will sing.",
        "Pojď blíž k ohni, maličká. Nosím lampu v novoročním průvodu a píseň o Mardukovi a Tiamat znám. Ptej se, zazpívám."),
    "elder_story.dilmun_woman.greet": (
        "Come close to the fire, little one. I know the tale of Dilmun, the clean land, and of Enki and the eight plants, as my mother sang it. Ask, and I will tell.",
        "Pojď blíž k ohni, maličká. Znám příběh o Dilmunu, čisté zemi, a o Enkim a osmi rostlinách, tak jak ho zpívala moje matka. Ptej se, povím."),
    "elder_story.nergal_woman.greet": (
        "Come close to the fire, little one. I know why plague and the dead keep house together: the tale of Nergal and Ereshkigal. Ask, and I will tell.",
        "Pojď blíž k ohni, maličká. Vím, proč spolu bydlí mor a mrtví: příběh o Nergalovi a Ereškigal. Ptej se, povím."),
}
ASK_HINT = ("elder_hint.ask",
            "Where could I find one of these tales written on clay?",
            "Kde bych našel některý z těch příběhů zapsaný na hlíně?")

STORY_NAMES = {  # the story as the elder names it; in Czech with its participle ("zapsán" a tale, "zapsána" a song)
    "atrahasis": ("the tale of Atra-Hasis", "zapsán příběh o Atrachasísovi"),
    "etana": ("the tale of Etana and the eagle", "zapsán příběh o Etanovi a orlu"),
    "adapa": ("the tale of Adapa", "zapsán příběh o Adapovi"),
    "enuma_elish": ("the New Year song of Marduk and Tiamat", "zapsána novoroční píseň o Mardukovi a Tiamat"),
    "ishtar_descent": ("the song of Ishtar going down", "zapsána píseň o sestupu Ištar"),
    "dilmun": ("the tale of Dilmun", "zapsán příběh o Dilmunu"),
    "nergal": ("the tale of Nergal and Ereshkigal", "zapsán příběh o Nergalovi a Ereškigal"),
}
# parent place of a tablet -> where to go, in English and in Czech
WHERE = {
    "eridu": ("to Eridu, the city of Enki", "do Eridu, města boha Enkiho"),
    "nippur": ("to Nippur, the city of Enlil", "do Nippuru, města Enlilova"),
    "shuruppak": ("to Shuruppak, the city of the flood hero", "do Šuruppaku, města hrdiny potopy"),
    "kish": ("to Kish", "do Kiše"),
    "etemenanki": ("to Etemenanki, the tower of Babylon", "k Etemenanki, babylonské věži"),
    "uruk": ("to Uruk", "do Uruku"),
    "assur": ("to Assur", "do Aššuru"),
    "ishtar_temple": ("to the Temple of Ishtar", "do Chrámu Ištar"),
    "eanna_temple": ("to the Temple of Eanna", "do Chrámu Eanna"),
    "ur": ("to Ur", "do Uru"),
    "uruk_pasture": ("to the pasture outside the walls of Uruk", "na pastvinu za hradbami Uruku"),
    "ziggurat_of_anu": ("to the Ziggurat of Anu", "k zikkuratu boha Anua"),
    "adab": ("to Adab", "do Adabu"),
    "larsa": ("to Larsa", "do Larsy"),
}
ORDINAL = [("first", "První"), ("second", "Druhá"), ("third", "Třetí"), ("fourth", "Čtvrtá"), ("fifth", "Pátá"),
           ("sixth", "Šestá"), ("seventh", "Sedmá")]

BEGIN, END = "# BEGIN elders (written by tools/build_elders.py; do not edit)", "# END elders"


def tablet_parents():
    """tablet place id -> id of the place it stands in."""
    parents = {}
    for path in glob.glob(os.path.join(ROOT, "places", "*.yaml")):
        for place in yaml.safe_load(open(path)) or []:
            if isinstance(place, dict) and re.match(r"^(atrahasis|enuma_elish|ishtar_descent|etana|adapa|dilmun|nergal)_tablet_\d+$", place.get("id", "")):
                parents[place["id"]] = place.get("parent") or place["locate"]["from"]
    return parents


def combos(sex):
    """The (story, tablet) pairs of one sex, the stories taken turn by turn so that neighbours differ."""
    stories = STORIES[sex]
    result = []
    for number in range(max(len(s["tablets"]) for s in stories.values())):
        for story, spec in stories.items():
            if number < len(spec["tablets"]):
                result.append((story, spec["tablets"][number]))
    return result


def dialogue_id(sex, index):
    """The dialogue of the elder number `index` of a sex (0 = the market of Uruk, 1.. = the homes of the village)."""
    pairs = combos(sex)
    story, tablet = pairs[index % len(pairs)]
    return "elder_%s_%s_%s" % (story, tablet.rsplit("_", 1)[1], sex)


def dialogue_of(sex, story, tablet):
    spec = STORIES[sex][story]
    topics = [(ask, node) for ask, node, _ in spec["chapters"]]
    lines = ["# One tale and one tablet (tools/build_elders.py; do not edit): the elder tells %s and says where %s lies." % (story, tablet),
             "id: elder_%s_%s_%s" % (story, tablet.rsplit("_", 1)[1], sex), "status: reviewed", "start: greet", "", "nodes:"]

    def choices(skip=None, hint=True):
        rows = ["      - {text_key: %s, goto: %s}" % (ask, node) for ask, node in topics if node != skip]
        if hint and skip != "where":
            rows.append("      - {text_key: %s, goto: where}" % ASK_HINT[0])
        rows.append("      - {text_key: %s}" % LEAVE[sex])
        return "\n".join(rows)

    lines += ["  greet:", "    text_key: %s" % spec["greet"], "    choices:", choices(), ""]
    for ask, node, text in spec["chapters"]:
        if node == "akitu_gate":
            # In the days of the New Year (the server's flag `festival:akitu`) the elder speaks of the festival that is on.
            lines += ["  akitu_gate:", "    branch:", '      - {if: {flag: "festival:akitu"}, goto: akitu_now}', "      - {goto: akitu}", "",
                      "  akitu:", "    text_key: %s" % AKITU[sex][0], "    choices:", choices(skip="akitu_gate"), "",
                      "  akitu_now:", "    text_key: %s" % AKITU[sex][1], "    choices:", choices(skip="akitu_gate"), ""]
        else:
            lines += ["  %s:" % node, "    text_key: %s" % text, "    choices:", choices(skip=node), ""]
    lines += ["  where:", "    text_key: elder_hint.%s" % tablet, "    effects:", "      - {reveal_places: [%s]}" % tablet,
              "    choices:", choices(skip="where", hint=False)]
    return "\n".join(lines) + "\n"


def texts(used, parents):
    en, cs = {}, {}
    for key, (a, b) in NEW_GREETS.items():
        en[key], cs[key] = a, b
    en[ASK_HINT[0]], cs[ASK_HINT[0]] = ASK_HINT[1], ASK_HINT[2]
    for sex, story, tablet in used:
        number = int(tablet.rsplit("_", 1)[1])
        where_en, where_cs = WHERE[parents[tablet]]
        name_en, name_cs = STORY_NAMES[story]
        key = "elder_hint.%s" % tablet
        en[key] = "Go %s, child. The %s tablet of %s lies there on a brick bench, written on clay." % (where_en, ORDINAL[number - 1][0], name_en)
        cs[key] = "Jdi %s, dítě. %s hliněná tabulka, na níž je %s, leží tam na cihlové lavici." % (where_cs, ORDINAL[number - 1][1], name_cs)
    return en, cs


def write_block(path, entries):
    text = open(path, encoding="utf-8").read()
    start, end = text.find(BEGIN), text.find(END)
    if start >= 0 and end > start:
        text = text[:start].rstrip("\n") + "\n" + text[end + len(END):].lstrip("\n")
    block = [BEGIN]
    for key in sorted(entries):
        block.append("%s: %s" % (key, json.dumps(entries[key], ensure_ascii=False)))
    block.append(END)
    text = text.rstrip("\n") + "\n\n" + "\n".join(block) + "\n"
    open(path, "w", encoding="utf-8").write(text)


def assign(path, counters):
    """Points every elder block of an npcs file at its dialogue (the sex is that of the dialogue it had)."""
    text = open(path, encoding="utf-8").read()
    blocks = re.split(r"(?m)^(?=- id: )", text)
    out = []
    for block in blocks:
        match = re.search(r"(?m)^  dialogue: (elder_tales_man|elder_tales_woman|elder_[a-z_]+_\d+_[mw])$", block)
        if match:
            old = match.group(1)
            sex = MAN if old.endswith("_m") or old == "elder_tales_man" else WOMAN
            block = block.replace("  dialogue: " + old, "  dialogue: " + dialogue_id(sex, counters[sex]))
            counters[sex] += 1
        out.append(block)
    open(path, "w", encoding="utf-8").write("".join(out))


def main():
    parents = tablet_parents()
    missing = [t for sex in STORIES for s in STORIES[sex].values() for t in s["tablets"] if t not in parents or parents[t] not in WHERE]
    if missing:
        sys.exit("tablets without a place or a way to say where they lie: %s" % missing)
    counters = {MAN: 0, WOMAN: 0}
    # the elders in the order of the files: the market of Uruk, then the homes of the hunter's village
    for name in ("crowd.yaml", "hunter_village_folk.yaml"):
        assign(os.path.join(ROOT, "npcs", name), counters)
    used = []
    for sex in (MAN, WOMAN):
        for index in range(counters[sex]):
            story, tablet = combos(sex)[index % len(combos(sex))]
            used.append((sex, story, tablet))
    for old in glob.glob(os.path.join(ROOT, "dialogues", "elder_*.yaml")):
        os.remove(old)
    for sex, story, tablet in sorted(set(used)):
        with open(os.path.join(ROOT, "dialogues", "elder_%s_%s_%s.yaml" % (story, tablet.rsplit("_", 1)[1], sex)), "w", encoding="utf-8") as out:
            out.write(dialogue_of(sex, story, tablet))
    en, cs = texts(sorted(set(used)), parents)
    write_block(os.path.join(ROOT, "i18n", "en.yaml"), en)
    write_block(os.path.join(ROOT, "i18n", "cs.yaml"), cs)
    tales = {}
    for sex, story, tablet in used:
        tales.setdefault((story, tablet), 0)
        tales[(story, tablet)] += 1
    print("%d elders (%d men, %d women), %d dialogues; every tablet is known to %d..%d of them" % (
        len(used), counters[MAN], counters[WOMAN], len(set(used)), min(tales.values()), max(tales.values())))
    every = {t for sex in STORIES for s in STORIES[sex].values() for t in s["tablets"]}
    unknown = sorted(every - {t for _, t in tales})
    if unknown:
        print("tablets no elder knows: %s" % unknown)


if __name__ == "__main__":
    main()
