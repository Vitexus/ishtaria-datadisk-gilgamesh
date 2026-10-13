#!/usr/bin/env python3
"""Concept images of the Uruk citizens for Hyper3D Rodin (InvokeAI, remote server, Juggernaut XL v9).

    python3 models-src/rodin/make_concepts.py [npc_id ...]  ->  models-src/concepts/<id>_<n>.png

Full body, front view, arms a little away from the body and hands visible, because Rodin does not follow poses and
merges a hand that touches the dress into it.
"""
import asyncio
import os
import pathlib
import sys

os.environ["INVOKEAI_BASE_URL"] = "http://10.11.18.22:9090"
sys.path.insert(0, os.path.expanduser("~/Projects/Packaging/mcp-server-invokeai"))
import httpx  # noqa: E402
import invokeai_mcp_server as inv  # noqa: E402

MODEL = "76cba3e7-6ed4-4fd6-b5c1-f72fcdd2297e"
OUT = pathlib.Path(__file__).resolve().parent.parent / "concepts"
STYLE = ("wide shot of the entire figure from the top of the head to the soles of the feet, full body photograph, small figure in the frame with empty space around, standing straight, front view, arms slightly away from the body, both hands open and visible, "
         "feet visible, plain light grey studio background, soft even lighting, Sumerian Early Dynastic period 2700 BCE, "
         "historically accurate, realistic, highly detailed, sharp focus")
NEG = ("medieval, knight, chainmail, plate armour, black clothing, trousers, boots, hands together, hands clasped, arms raised, hands on head, nude, naked, loincloth, fur skirt, half-naked, bare chest, short skirt, dark skin, statue, relief, plinth, cropped, legs only, torso only, headless, face not visible, out of frame, cut off, close-up, hands in pockets, hands touching clothes, crossed arms, holding objects, modern clothing, "
       "cartoon, anime, text, watermark, blurry, extra limbs, deformed hands, multiple people, busy background")
CHARS = {
    "uruk_farmer": "a sun-browned Sumerian farmer, man of about 40, shaved head, short beard, lean muscular, short undyed sheepskin "
                   "kaunakes skirt, bare chest, bare feet, a plain rope belt, humble village man",
    "uruk_water_carrier": "a young Sumerian village woman, black hair in a simple braid, plain undyed wool dress draped over one shoulder, "
                          "bare feet, a rope band, no jewellery except a single copper bracelet, humble",
    "uruk_mason": "a strong Sumerian townsman brickmaker of about 45, short trimmed black beard, short black hair, knee-length wool kaunakes, "
                  "leather apron stained with clay, broad shoulders, leather sandals, bronze arm ring",
    "uruk_alewife": "a cheerful middle-aged Sumerian townswoman, hair pinned up with bronze pins, ochre-dyed wool dress draped over one shoulder, "
                    "patterned shawl, bronze earrings, a copper bead necklace, leather sandals, warm smile",
    "uruk_elder": "a dignified elderly Sumerian nobleman with fair olive skin, long curled grey beard, grey hair, fully dressed in a long "
                  "white wool robe with fringed hem reaching the ankles and covering the chest and one shoulder, wide gold belt, heavy gold collar "
                  "with lapis lazuli beads, gold armbands, leather sandals, standing upright, authoritative",
    "uruk_noblewoman": "a beautiful Sumerian noblewoman, tall headdress of gold leaves with lapis lazuli and carnelian beads, large lunate gold "
                       "earrings, long tufted ankle-length dress deep blue and cream draped over one shoulder, beaded collar, gold bracelets, sandals",
    "uruk_temple_courtesan": "a beautiful Sumerian woman consecrated to the goddess Ishtar, fully dressed in a long red tufted wool dress "
                             "draped over one shoulder and covering the chest, gold leaf hair ornament with lapis lazuli and carnelian beads, long "
                             "black hair, large gold earrings, beaded collar, gold bracelets, barefoot, serene expression, arms hanging "
                             "relaxed at her sides a hand's width away from the dress, dignified temple attire",
    "uruk_plowman": "a weathered elderly Sumerian farmer of 60, short grey beard, sun-faded felt cap, wearing a sleeveless knee-length "
                    "undyed linen and wool tunic with a rope belt, bare arms, bare feet, calloused hands hanging at his sides away from the body, "
                    "leather water skin at the hip, humble, fully clothed",
    # the characters of the epic (hands free: Rodin merges what a hand holds into the body)
    "enkidu": "Enkidu the wild man of the steppe, huge muscular body, long matted dark brown hair and long beard, body hair, "
              "tattered animal hide loincloth, bare chest, bare feet, mud-brown sun-weathered skin, fierce calm face",
    "enkidu_civilized": "Enkidu after civilization, stocky muscular Sumerian man, long dark brown hair tied back, trimmed beard, "
                        "knee-length cream wool kaunakes skirt, leather belt with a pouch, one copper armband, leather sandals, bare chest",
    "shamhat": "Shamhat, a graceful Sumerian temple woman, black hair in a braid wound round her head, long white linen dress "
               "draped over one shoulder and covering the chest, gold earrings, carnelian bead necklace, barefoot, wise gentle face",
    "humbaba": "Humbaba, the monstrous giant guardian of the Cedar Forest, enormous ogre-like figure, tusked snarling face, heavy brow, "
               "matted mane and beard, fur and hide wrap, bone and stone necklace, thick muscular arms, bare feet",
    "utnapishtim": "Utnapishtim, an ancient wise old Sumerian man, very long white hair and long white beard, long plain white linen "
                   "robe with long sleeves reaching the ankles, rope belt, no jewellery, barefoot, serene face",
    "ur_shanabi": "Ur-Shanabi the ferryman, lean weathered Sumerian man, shaved head, short black beard, short undyed wool kaunakes "
                  "skirt, bare chest, leather belt with a pouch, bare feet",
    "ninsun": "Ninsun, a goddess queen mother, tall elegant Middle Eastern woman with olive skin and dark eyes, black hair braided and "
              "pinned, small golden horned cap, long tufted ankle-length deep blue wool dress draped over one shoulder, gold necklace "
              "and earrings, sandals",
    "anu": "Anu, the tall sky god, very tall majestic old man, long grey beard, tall golden crown with several tiers of horns, "
           "ankle-length blue and white robe with a gold collar and gold belt, sandals, powerful stern face",
    "high_priest_anu": "a high priest of Anu, shaved head, short black beard, white linen skirt to the ankles, bare chest, "
                       "lapis lazuli necklace and gold band on the brow, sandals, solemn face",
    "high_priestess_ishtar": "the high priestess of Ishtar, Middle Eastern woman with olive skin, black braided hair, tall golden "
                             "headdress with a small horned crown, long bright red tufted wool dress draped over one shoulder and covering "
                             "the chest, gold collar and bracelets, sandals, standing on the bare floor, no pedestal, no frame",
    "temple_scribe": "a temple scribe, shaved head, thin short stubble, cream knee-length wool skirt, small leather satchel on a "
                     "strap across the chest, bare chest, leather belt, sandals, intelligent face",
    "royal_guard": "a Sumerian soldier of Early Dynastic Uruk 2700 BCE, strong man with short black hair and black beard, copper helmet "
                   "with a chin strap, bare chest and arms, knee-length cream wool kaunakes skirt, short leather cloak with metal discs "
                   "fastened at the neck, leather belt, leather sandals, bare legs, no armour, no chainmail, no black clothing, no trousers, no boots",
    "uruk_noble": "a wealthy Sumerian nobleman, hair in a bun, curled black beard, long ankle-length lavender wool kaunakes, wide gold "
                  "belt, gold collar, gold armbands and bracelets, sandals",
    "uruk_merchant": "a Sumerian merchant of about 40, short black hair and beard, knee-length ochre-dyed wool skirt, red-brown wool "
                     "cloak over the shoulders, leather belt with a pouch, sandals, shrewd friendly face",
    "potter": "a strong Sumerian potter, shaved head, short stubble beard, short brown wool skirt, clay-stained brown leather apron, "
              "leather belt, bare feet, muscular forearms",
    "weaver": "a Sumerian weaver woman, long black hair under a cream head scarf, long brown wool dress draped over one shoulder, "
              "leather belt, bronze earrings, sandals, kind face",
}

# creatures: not standing humans, so the human STYLE does not fit; seen from three quarters so that the legs and the tail show
CREATURE_STYLE = ("wide shot of the entire creature from head to feet and tail, full body, three-quarter front view, standing on the ground, "
                  "empty space around, plain light grey studio background, soft even lighting, Sumerian mythology, cylinder seal "
                  "inspired design, realistic, highly detailed, sharp focus")
CREATURE_NEG = ("human legs, human feet, knees, standing man, crouching man, jumping, dancing, cartoon, anime, text, watermark, blurry, cropped, out of frame, cut off, close-up, multiple creatures, busy background, "
                "plinth, statue, relief, modern, medieval armour, extra heads")
CREATURES = {
    # SDXL cannot draw the hybrid in one picture: the scorpion man is assembled from the two parts (models-src/rodin_scorpion.py)
    "scorpion_body": "a giant dark brown armoured scorpion in strict side view facing left, two large pincer claws held out in front at the left end, "
                     "eight jointed legs spread on the ground, a broad flat armoured plate at the front of the body instead of a head, "
                     "a ridged segmented abdomen, the long thick segmented tail grows out of the rear right end of the abdomen, "
                     "rises in a high arc over the back and curls forward ending in a curved sting above the middle of the body",
    "bull_of_heaven": "the Bull of Heaven, a gigantic mythical aurochs bull, massive muscular body with a high hump, thick dark brown hide, "
                      "long curved heavy cream-coloured horns with gold rings, a braided blue lapis lazuli beard under the chin, "
                      "glowing red eyes, four strong legs with black hooves planted wide apart, head lowered, tail hanging, all four legs clearly visible",
}
CHARS.update(CREATURES)
CHARS["scorpion_torso"] = ("a bearded Sumerian mountain guardian, huge muscular man with long black hair, thick curled black beard, a small golden horned "
                           "cap, bare chest, heavy gold collar, copper armbands, a wide copper belt, standing straight with the arms hanging "
                           "slightly away from the body and the hands open, a plain short dark loincloth")


async def main():
    OUT.mkdir(exist_ok=True)
    for npc in sys.argv[1:] or CHARS:
        for n in (1, 2):
            style, neg = (CREATURE_STYLE, CREATURE_NEG) if npc in CREATURES else (STYLE, NEG)
            graph = await inv.create_text2img_graph(f"{CHARS[npc]}, {style}", neg, model_key=MODEL, width=1216 if npc in CREATURES else 832, height=832 if npc in CREATURES else 1216,
                                                    steps=35, cfg_scale=6.0, scheduler="dpmpp_2m")
            _, name = await inv._run_graph(graph)
            async with httpx.AsyncClient(timeout=120) as c:
                r = await c.get(f"{inv.INVOKEAI_BASE_URL}/api/v1/images/i/{name}/full")
            (OUT / f"{npc}_{n}.png").write_bytes(r.content)
            print(npc, n, name, flush=True)


asyncio.run(main())
