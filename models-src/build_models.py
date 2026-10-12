"""Builds the NPC models of the Gilgamesh datadisk.

    blender -b --python models-src/build_models.py -- <npc_id|all> media/models
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from chargen import creatures, npcs  # noqa: E402


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    which = args[0] if args else "all"
    out = os.path.abspath(args[1] if len(args) > 1 else os.path.join(HERE, "..", "media", "models"))
    os.makedirs(out, exist_ok=True)
    ids = list(npcs.HUMANOIDS) + ["scorpion_man", "bull_of_heaven"] if which == "all" else which.split(",")
    for npc_id in ids:
        path = os.path.join(out, npc_id + ".glb")
        if npc_id in npcs.HUMANOIDS:
            npcs.build_humanoid(npc_id, path)
        elif npc_id == "scorpion_man":
            creatures.build_scorpion_man(path)
        elif npc_id == "bull_of_heaven":
            creatures.build_bull_of_heaven(path)
        else:
            raise SystemExit("unknown npc " + npc_id)
        print("built", path, os.path.getsize(path), "bytes")


main()
