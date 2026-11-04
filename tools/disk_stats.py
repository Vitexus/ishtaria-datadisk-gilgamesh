#!/usr/bin/env python3
"""Counts what the datadisk contains, for its description (README.md, debian/control): `make stats`.

    tools/disk_stats.py

  * houses: the separately modelled buildings of the cities and villages (buildings/uruk.yaml, hunter_village.yaml and
    village_*.yaml; the irrigation works and the field plots are not houses). Uruk's plan lists more houses
    (tools/data/uruk_city.json) than are drawn one by one;
  * quests: quests/*.yaml;
  * characters: the named inhabitants (npcs/*.yaml without the `crowd` tag), NPCs: all inhabitants, the crowd of townspeople
    and villagers included;
  * achievements: achievements.yaml.
Pure Python with PyYAML; prints the numbers and one line ready to paste.
"""
import glob
import os

import yaml

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def load(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def count():
    houses = sum(len(load(path)["items"]) for path in ["buildings/uruk.yaml", "buildings/hunter_village.yaml"]
                 + sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "buildings", "village_*.yaml"))))
    npcs = [npc for path in sorted(glob.glob(os.path.join(ROOT, "npcs", "*.yaml"))) for npc in (load(os.path.relpath(path, ROOT)) or [])
            if isinstance(npc, dict)]
    crowd = sum(1 for npc in npcs if "crowd" in (npc.get("tags") or []))
    achievements = load("achievements.yaml")
    return {
        "houses": houses,
        "quests": len(glob.glob(os.path.join(ROOT, "quests", "*.yaml"))),
        "characters": len(npcs) - crowd,
        "npcs": len(npcs),
        "achievements": len(achievements["achievements"] if isinstance(achievements, dict) else achievements),
        "dialogues": len(glob.glob(os.path.join(ROOT, "dialogues", "*.yaml"))),
    }


if __name__ == "__main__":
    numbers = count()
    for key, value in numbers.items():
        print("%-13s %d" % (key, value))
    print("%(houses)d houses, %(quests)d quests, %(characters)d named characters among %(npcs)d NPCs, %(achievements)d achievements" % numbers)
