#!/usr/bin/env python3
"""Concept images of the Uruk crowd for Hyper3D Rodin (InvokeAI, RealVisXL_V4.0).

    python3 models-src/rodin/make_crowd_concepts.py [id ...]  ->  models-src/concepts/crowd_<id>_1.png

The `crowd_` figures are unnamed townsfolk for the streets and villages of Uruk, so that
not everybody in a crowd is one of the named NPCs. Same conventions as make_concepts.py:
full body, front view, arms a little away from the body and hands visible (Rodin does not
follow poses and merges a hand that touches the dress into it).

Fix pass: crowd_archer (Rodin merged a deformed bow into the body) and
crowd_pregnant_woman ("visibly with child" was read as holding a baby, plus a
flesh-coloured blob at her feet) were regenerated as crowd_<id>_2.png with the
prompts below; use make_crowd_fix_concepts.py for such corrected concepts.
"""
import asyncio
import os
import pathlib
import sys

os.environ["INVOKEAI_BASE_URL"] = os.environ.get("INVOKEAI_BASE_URL", "http://127.0.0.1:9090")
sys.path.insert(0, os.path.expanduser("~/Projects/Packaging/mcp-server-invokeai"))
import httpx  # noqa: E402
import invokeai_mcp_server as inv  # noqa: E402

MODEL = "644a2858-4d8e-42ab-a60a-ef0e3e2dd3e7"  # RealVisXL_V4.0
OUT = pathlib.Path(__file__).resolve().parent.parent / "concepts"
STYLE = ("wide shot of the entire figure from the top of the head to the soles of the feet, full body photograph, small figure in the frame with empty space around, standing straight, front view, arms slightly away from the body, both hands open and visible, "
         "feet visible, plain light grey studio background, soft even lighting, Sumerian Early Dynastic period 2700 BCE, "
         "historically accurate, realistic, highly detailed, sharp focus")
NEG = ("medieval, knight, chainmail, plate armour, black clothing, trousers, boots, hands together, hands clasped, arms raised, hands on head, nude, naked, loincloth, fur skirt, half-naked, dark skin, statue, relief, plinth, cropped, legs only, torso only, headless, face not visible, out of frame, cut off, close-up, hands in pockets, hands touching clothes, crossed arms, holding objects, modern clothing, "
       "deformed bow, bow merged into the body, bow touching the body, holding a baby, carrying a child, second person, object at feet, bundle at feet, "
       "cartoon, anime, text, watermark, blurry, extra limbs, deformed hands, multiple people, busy background")

# The crowd of Uruk: men, women, children, soldiers, merchants and nobles, after the
# Early Dynastic sources (Standard of Ur, Ur-Nanshe plaques, Eshnunna/Khafaje worshipper
# statues, graves of Ur): wool and linen one-shoulder dresses and kaunakes skirts, felt
# and leather caps, copper and bronze arms, gold and lapis for the rich, no trousers.
CHARS = {
    "crowd_fisherman": "a lean Sumerian marsh fisherman, man of about 30, shaved head, short black beard, sun-browned skin, "
                       "knee-length undyed wool kaunakes skirt, simple rope belt, bare chest, bare feet",
    "crowd_baker": "a plump Sumerian baker, man of about 35, short black hair, clean-shaven, flour-dusted knee-length brown wool "
                   "skirt, leather apron, leather sandals, friendly face",
    "crowd_carpenter": "a broad-shouldered Sumerian carpenter, man of about 40, short black beard, knee-length ochre-dyed wool "
                       "skirt, wide leather belt, bronze armband, leather sandals, bare chest",
    "crowd_shepherd": "a weathered Sumerian shepherd, man of about 50, short grey-flecked beard, undyed felt cap, sheepskin wrap "
                      "over one shoulder, knee-length wool skirt, rope belt, bare feet, sun-worn face",
    "crowd_old_man": "a frail elderly Sumerian villager, man past 70, long thin white beard, bald head, long plain undyed wool robe "
                     "with long sleeves reaching the ankles, rope belt, bare feet, thin arms hanging at his sides",
    "crowd_market_woman": "a sturdy Sumerian market woman of about 35, black hair pinned up with two copper pins, ochre-dyed wool "
                           "dress draped over one shoulder and covering the chest, patterned cream shawl, copper bead necklace, leather sandals",
    "crowd_pregnant_woman": "a young Sumerian woman in the late stage of pregnancy, visibly pregnant with a rounded belly under "
                            "the dress, long black braid, plain white wool dress draped over one shoulder and covering the chest "
                            "and belly, copper bracelet, bare feet, alone, no child, no baby, no other person, nothing at her "
                            "feet, both hands empty and open",
    "crowd_washwoman": "a young Sumerian washerwoman, black hair tied back, plain grey-blue wool dress draped over one shoulder and "
                       "covering the chest, simple linen headband, leather sandals",
    "crowd_young_woman": "a young unmarried Sumerian woman of about 18, long black braid wound with a wool cord, long cream wool "
                         "dress draped over one shoulder and covering the chest, a single lunate silver earring, leather sandals",
    "crowd_grandmother": "an elderly Sumerian grandmother, grey hair in a braided bun, deep wrinkles, long plain dark brown wool dress "
                         "with long sleeves, a cream shawl over both shoulders, a single copper bracelet, bare feet",
    "crowd_boy_8": "a Sumerian boy of about 8, shaved head with a single small braided side lock, short undyed wool tunic to the knees "
                  "covering the torso, rope belt, bare feet, cheerful",
    "crowd_girl_8": "a Sumerian girl of about 8, black hair in two braids, knee-length undyed wool tunic with short sleeves covering "
                    "the torso, leather sandals, shy smile",
    "crowd_toddler_boy": "a small Sumerian toddler boy of about 3, thin black hair, short cream wool tunic covering the torso to the "
                         "knees, bare feet",
    "crowd_teen_girl": "a Sumerian girl of about 14, black hair in a long braid, long ochre-dyed wool dress draped over one shoulder "
                       "and covering the chest, copper bracelet, leather sandals",
    "crowd_apprentice_boy": "a Sumerian apprentice boy of about 12, shaved head, short brown wool tunic to the knees covering the "
                            "torso, small leather satchel on a strap across the chest, leather sandals",
    "crowd_spearman": "a Sumerian spearman of Early Dynastic Uruk, strong man, short black beard, tall copper helmet with a leather "
                      "neck flap, bare chest and arms, knee-length cream wool kaunakes skirt, short leather cloak with small copper "
                      "discs fastened at the neck, leather belt, leather sandals, empty hands",
    "crowd_archer": "a Sumerian archer, lean man of about 25, short black hair, felt headband, bare chest, knee-length brown wool "
                    "kaunakes skirt, an empty leather quiver slung on his back, leather wrist guards, leather sandals, holding a "
                    "simple wooden self bow vertically in his right hand, right arm slightly away from the body so the bow is "
                    "clearly separate from the body, left hand empty and open, no arrows in hand",
    "crowd_axeman": "a stocky Sumerian soldier, shaved head, thick black beard, bare chest, knee-length undyed wool kaunakes skirt, a "
                    "socketed copper axe hanging from a wide leather belt at his hip, leather cloak with copper discs, leather sandals, empty hands",
    "crowd_slinger": "a young Sumerian skirmisher, thin man of about 20, short black hair, clean-shaven, bare chest, knee-length brown "
                     "wool skirt, a leather sling tucked into his rope belt, bare feet, empty hands",
    "crowd_textile_merchant": "a well-dressed Sumerian cloth merchant of about 45, curled black beard, red-dyed wool cloak over one "
                              "shoulder, long cream tunic covering the chest, gold armband, gold collar with lapis lazuli beads, leather sandals, shrewd smiling face",
    "crowd_copper_merchant": "a Sumerian copper trader of about 35, short black beard, knee-length ochre wool skirt, red-brown leather "
                             "vest open at the chest, wide leather belt with a bronze buckle, copper armband, leather sandals",
    "crowd_caravaneer": "a dusty Sumerian donkey caravan driver, man of about 40, wide felt cap, short grey-flecked beard, long brown "
                        "robe with long sleeves to mid-calf covering the chest, rope belt, worn leather sandals, tanned weathered face",
    "crowd_young_noble": "a young Sumerian nobleman of about 20, oiled black hair in a bun, short curled beard, long ankle-length "
                         "lavender wool kaunakes, wide gold belt, gold collar with lapis lazuli, gold armbands, leather sandals",
    "crowd_noble_girl": "a Sumerian noble girl of about 15, black hair in a braided updo with a gold ribbon, small gold leaf headdress, "
                        "long tufted deep blue and cream ankle-length dress draped over one shoulder and covering the chest, lunate gold "
                        "earrings, carnelian bead necklace, gold bracelets, leather sandals",
    "crowd_court_official": "a Sumerian palace official, man of about 45, neatly curled black beard, hair in a bun, fringed white wool "
                            "shawl over a long cream tunic covering the chest, gold armband, leather sandals, stern dignified face",
    "crowd_priest_minor": "a young clean-shaven Sumerian priest, shaved head and face, white linen skirt to the ankles, bare chest, a "
                          "simple copper pendant on a cord, rope belt, leather sandals, solemn young face",
}


async def main():
    OUT.mkdir(exist_ok=True)
    for i, npc in enumerate(sys.argv[1:] or CHARS):
        path = OUT / f"{npc}_1.png"
        if path.exists():
            print(f"skip {npc} (exists)", flush=True)
            continue
        graph = await inv.create_text2img_graph(f"{CHARS[npc]}, {STYLE}", NEG, model_key=MODEL,
                                                width=832, height=1216, steps=35, cfg_scale=6.0,
                                                scheduler="dpmpp_2m", seed=2000 + i)
        _, name = await inv._run_graph(graph)
        async with httpx.AsyncClient(timeout=120) as c:
            r = await c.get(f"{inv.INVOKEAI_BASE_URL}/api/v1/images/i/{name}/full")
        path.write_bytes(r.content)
        print(f"{npc} {name} -> {path.name} ({len(r.content)} bytes)", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
