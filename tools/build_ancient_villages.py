#!/usr/bin/env python3
"""Writes the namesake villages of the cities of the Oko map that the world map of 2700 BCE does not list as cities.

    tools/build_ancient_villages.py

Of the 21 places of https://oko.yin.cz/17/uruk/uruk-mapa.jpg nine are no city around 2700 BCE by the criteria of
research/ANCIENT_CITIES.md (research/MAP_CITIES_COMPARISON.md): Babylon, Sippar, Borsippa, Dur-Kurigalzu, Dur-Katlimmu, Arrapha,
Nuzi, Qattara and Der. Each gets a **village of the same name** on the site of the later city (the sites are known, the cities
come later): a few houses, and a mayor who tells about the later city on his knowledge card ("Tell me about yourself": a picture
of the site or of a find, a short text, the link to the Wikipedia article in the client's language).

It writes places/ancient_villages.yaml, buildings/village_<id>.yaml, npcs/ancient_villages.yaml, dialogues/village_mayor.yaml (once),
the nine cards in knowledge.yaml, the texts in i18n/en.yaml and i18n/cs.yaml and the pictures media/knowledge/village_<id>.jpg
(downloaded from Wikimedia Commons into tools/cache/, only freely licensed ones; the credit is read from Commons).
Run again after a change: the earlier lines of this tool are replaced (they stand between the markers "# BEGIN ancient villages"
and "# END ancient villages"). Needs network access for the pictures (a cached picture is not fetched again).
"""
import io
import json
import math
import pathlib
import re
import urllib.parse
import urllib.request

import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "tools" / "cache" / "village_pictures"
UA = {"User-Agent": "IshtariaDatadisk/0.3 (research; contact ishtaria@vitexsoftware.com)"}
BEGIN, END = "# BEGIN ancient villages (tools/build_ancient_villages.py)", "# END ancient villages"

# id, English name, Czech name, latitude, longitude, Wikipedia (en, cs or None), Commons file, mayor's model,
# English text, Czech text (the cards: two to four sentences; facts from the Wikipedia article and research/MAP_CITIES_COMPARISON.md)
VILLAGES = [
    ("babylon", "Babylon", "Babylón", 32.5425, 44.4211, ("Babylon", "Babylón"), "File:Ishtar_Gate.jpg", "crowd_court_official",
     "A village on the Euphrates. Its name is first written around 2300 BCE; centuries later Hammurabi makes it the capital of an empire, and in the 6th century BCE the Ishtar Gate and the great ziggurat Etemenanki stand here.",
     "Vesnice na Eufratu. Její jméno je poprvé zapsáno kolem roku 2300 př. n. l.; o staletí později z ní Chammurapi udělá hlavní město říše a v 6. století př. n. l. tu stojí Ištařina brána a velký ziggurat Etemenanki."),
    ("sippar", "Sippar", "Sippar", 33.0588, 44.2522, ("Sippar", "Sippar"), "File:Detail, Sun God Tablet from Sippar, Iraq, 9th century BCE. British Museum.jpg", "crowd_priest_minor",
     "A village of the sun god's worshippers on the Euphrates. Later it is a city of Utu-Shamash with the Ebabbar temple; the Sun God Tablet and a clay map of the world were found here. Whether the site is the Sippar of the oldest kings is still debated.",
     "Vesnice ctitelů boha slunce na Eufratu. Později je tu město Utua-Šamaše s chrámem Ebabbar; našla se tu Deska boha slunce a hliněná mapa světa. Zda je tahle lokalita Sippar nejstarších králů, se stále diskutuje."),
    ("borsippa", "Borsippa", "Borsippa", 32.3920, 44.3417, ("Borsippa", "Borsippa"), "File:Ruins of the ziggurat and temple of god Nabu at Borsippa, Babel Governorate, Iraq.jpg", "crowd_baker",
     "A village by the Euphrates south-west of Babylon. Its god will be Nabu, the scribe of the gods, and the ruined ziggurat of his temple is often taken for the Tower of Babel. The oldest sure mention of the city is from the Ur III period.",
     "Vesnice u Eufratu jihozápadně od Babylonu. Jejím bohem bude Nabu, písař bohů, a zřícený ziggurat jeho chrámu bývá považován za Babylonskou věž. Nejstarší jisté zmínky o městě jsou z doby Ur III."),
    ("dur_kurigalzu", "Dur-Kurigalzu", "Dur-Kurigalzu", 33.3536, 44.2022, ("Dur-Kurigalzu", "Dur-Kurigalzu"), "File:1._The_Kassite_era_ziggurat_at_Aqar-Quf_(Dur-Kurigalzu),_western_Baghdad,_Iraq._December_29,_2021.jpg", "crowd_carpenter",
     "A village in the plain west of the later Baghdad. Over a thousand years from now the Kassite king Kurigalzu I will found a fortress city here, with a royal palace and a high ziggurat; its ruin at Aqar Quf can be seen from afar.",
     "Vesnice v rovině západně od pozdějšího Bagdádu. Za více než tisíc let zde kassitský král Kurigalzu I. založí pevnostní město s královským palácem a vysokým ziggurátem; jeho zřícenina u Aqar Qufu je vidět zdaleka."),
    ("dur_katlimmu", "Dur-Katlimmu", "Dur-Katlimmu", 35.6433, 40.7403, ("Tell_Sheikh_Hamad", None), "File:SchechHamad,RedHouse2.jpg", "crowd_shepherd",
     "A farming hamlet on the lower Khabur, near its mouth. Much later, around the 13th century BCE, the Assyrian king Shalmaneser I will make it the capital of a province, and the Assyrians will build their Red House here; today the site is called Tell Sheikh Hamad.",
     "Zemědělská osada na dolním Chabúru nedaleko jeho ústí. Mnohem později, kolem 13. století př. n. l., z ní asyrský král Salmanasar I. udělá hlavní město provincie a Asyřané zde postaví svůj Červený dům; dnes se lokalita jmenuje Tell Šajch Hamad."),
    ("arrapha", "Arrapha", "Arrapcha", 35.4694, 44.3925, ("Arrapha", "Kirkúk"), "File:Kirkuk_citadel.jpg", "crowd_axeman",
     "A village under the later citadel hill of Kirkuk, below the Zagros foothills. Its name is first written in the Neo-Sumerian age; later it is the capital of a kingdom and an Assyrian province. The old town has never been excavated, so little is known of it.",
     "Vesnice pod pozdějším citadelovým pahorkem Kirkúku na úpatí Zagrosu. Její jméno je poprvé zapsáno v neosumerské době; později je hlavním městem království a asyrskou provincií. Staré město nebylo nikdy vykopáno, takže o něm víme málo."),
    ("nuzi", "Nuzi", "Nuzi", 35.3700, 44.2549, ("Nuzi", None), "File:Large pottery jar, Nuzi, Yorghan Tepe, Iraq, Stratum IV, mid 2nd millenium BC - Harvard Semitic Museum - Cambridge, MA - DSC06410.jpg", "crowd_fisherman",
     "A hamlet on a mound the Arabs will call Yorghan Tepe, farmed since the Ubaid age. In the Akkadian age the settlement is called Gasur; in the 15th and 14th centuries BCE a Hurrian town here leaves thousands of clay tablets of legal and family documents.",
     "Osada na pahorku, kterému Arabové budou říkat Jorgan Tepe, obdělávaném od doby obeidské. V době akkadské se osada jmenuje Gasur; v 15. a 14. století př. n. l. tu hurritské město zanechá tisíce hliněných tabulek s právními a rodinnými dokumenty."),
    ("qattara", "Qattara", "Qattara", 36.2571, 42.4493, ("Tell_al-Rimah", None), "File:Stele of Adad-nirari III.jpg", "crowd_textile_merchant",
     "A village in the dry-farming plain of Sinjar, on the mound now called Tell al-Rimah. Its ancient name is debated, Qattara or Karana; in the time of the letters of Mari a palace and a temple stand here, and an Assyrian king raises a stele of victory.",
     "Vesnice v rovině sucha pěstujících plodin u Sindžáru, na návrší dnes zvaném Tell ar-Rimáh. Jeho starověké jméno je sporné, Qattara nebo Karana; v době mariských dopisů tu stojí palác a chrám a asyrský král tu postaví vítěznou stélu."),
    ("der", "Der", "Der", 33.1236, 45.9314, ("Der_(Sumer)", None), "File:BM 22470 Statue dedicated to the goddess Nin-shubur of the city of Der by Enzi and his son Amar-kiku (2400 BCE).jpg", "crowd_old_man",
     "A frontier village between the plain of Sumer and the mountains of Elam. Later the city of the god Ishtaran will guard the road to Susa; a statue to the goddess Nin-shubur, dedicated here by the ruler Enzi and his son around 2400 BCE, is in the British Museum.",
     "Pohraniční vesnice mezi rovinou Sumeru a horami Elamu. Později tu město boha Ištarana bude střežit cestu do Sús; socha bohyně Nin-šubur, kterou tu kolem roku 2400 př. n. l. zasvětili vládce Enzi a jeho syn, je v Britském muzeu."),
]
MODEL_PORTRAITS = {
    "crowd_court_official": ("retro", "humanMaleA"), "crowd_priest_minor": ("retro", "humanMaleA"), "crowd_baker": ("survivors", "survivorMaleB"),
    "crowd_carpenter": ("survivors", "survivorMaleB"), "crowd_shepherd": ("survivors", "survivorMaleB"), "crowd_axeman": ("protagonists", "criminalMaleA"),
    "crowd_fisherman": ("survivors", "survivorMaleB"), "crowd_textile_merchant": ("retro", "humanMaleA"), "crowd_old_man": ("retro", "humanMaleA"),
}
DIALOGUE = {
    "en": {"greet": "Peace to you, traveller. I am the mayor of this village; we have little, but the name of this place will be known far and wide one day.",
           "ask": "What will our name mean one day?", "answer": "Ask me to tell you about myself: there is a picture, a short story and a place where you can read more.",
           "leave": "Farewell."},
    "cs": {"greet": "Pokoj tobě, poutníku. Jsem starosta téhle vesnice; máme málo, ale jméno tohoto místa se jednou rozletí do světa.",
           "ask": "Co bude naše jméno jednou znamenat?", "answer": "Požádej mě, ať ti o sobě povím: je tu obrázek, krátký příběh a místo, kde si přečteš víc.",
           "leave": "Sbohem."},
}


def api(params):
    request = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params), headers=UA)
    return json.load(urllib.request.urlopen(request, timeout=60))


def strip_html(text):
    import html
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text or ""))).strip()


def picture(village_id, file_title):
    """Downloads the picture, returns (credit author, licence, title)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    meta_path = CACHE / (village_id + ".json")
    jpg_path = ROOT / "media" / "knowledge" / (village_id + ".jpg")
    if meta_path.exists() and jpg_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return meta["author"], meta["license"], meta["title"]
    data = api({"action": "query", "format": "json", "titles": file_title, "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": 900})
    info = list(data["query"]["pages"].values())[0]["imageinfo"][0]
    extra = info["extmetadata"]
    licence = strip_html(extra.get("LicenseShortName", {}).get("value"))
    if not re.search(r"(?i)^(public domain|cc0|cc by(-sa)? \d)", licence):
        raise SystemExit("%s: licence %r is not free enough for a shipped picture" % (file_title, licence))
    author = strip_html(extra.get("Artist", {}).get("value")) or "unknown"
    request = urllib.request.Request(info["thumburl"], headers=UA)
    image = Image.open(io.BytesIO(urllib.request.urlopen(request, timeout=120).read())).convert("RGB")
    image.thumbnail((800, 800))
    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(jpg_path, "JPEG", quality=84, optimize=True)
    title = file_title.split(":", 1)[1].rsplit(".", 1)[0].replace("_", " ")
    meta_path.write_text(json.dumps({"author": author, "license": licence, "title": title}), encoding="utf-8")
    return author, licence, title


def houses(seed):
    """Six houses and a storehouse of the hunter's village, turned by `seed` degrees: the same old-Persian forms, a smaller ring."""
    source = yaml.safe_load((ROOT / "buildings" / "hunter_village.yaml").read_text(encoding="utf-8"))["items"]
    chosen = [source[i] for i in (0, 2, 4, 6, 8, 10)] + [source[18]]
    turn = math.radians(seed)
    out = []
    for item in chosen:
        x, z = item["x"] * 0.7, item["z"] * 0.7
        item = dict(item)
        item["x"] = round(x * math.cos(turn) - z * math.sin(turn), 2)
        item["z"] = round(x * math.sin(turn) + z * math.cos(turn), 2)
        item["yaw_deg"] = round((item["yaw_deg"] + math.degrees(turn)) % 360.0, 1)
        out.append(item)
    return out


def replace_block(path, block, header=""):
    text = path.read_text(encoding="utf-8") if path.exists() else header
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.S)
    text = pattern.sub("", text).rstrip("\n") + "\n\n" if text.strip() else ""
    path.write_text(text + BEGIN + "\n" + block + END + "\n", encoding="utf-8")


def q(text):
    return json.dumps(text, ensure_ascii=False)


def main():
    places, npcs, cards = [], [], []
    texts = {"en": [], "cs": []}
    for number, (key, name_en, name_cs, lat, lon, wikipedia, file_title, model, text_en, text_cs) in enumerate(VILLAGES):
        place = "village_" + key
        author, licence, title = picture(place, file_title)
        places.append(f"""- id: {place}
  kind: city
  name_key: place.{place}
  radius_m: 60
  music: land_between_rivers
  music_radius_m: 500
  # The village of the same name on the site of the later city ({name_en}); research/MAP_CITIES_COMPARISON.md says why it is a village.
  geo: {{latitude_deg: {lat}, longitude_deg: {lon}}}
""")
        (ROOT / "buildings" / (place + ".yaml")).write_text(
            f"# The houses of the village {name_en} (written by tools/build_ancient_villages.py; do not edit).\nplace: {place}\nitems:\n"
            + "".join("  - {model: %s, x: %s, z: %s, yaw_deg: %s, scale: %s, footprint: %s, sink_m: %s}\n"
                      % (i["model"], i["x"], i["z"], i["yaw_deg"], json.dumps(i["scale"]), json.dumps(i["footprint"]), i["sink_m"]) for i in houses(40.0 * number)),
            encoding="utf-8")
        pack, skin = MODEL_PORTRAITS[model]
        npcs.append(f"""- id: mayor_{key}
  name_key: npc.mayor_{key}
  place: {place}
  character: {{pack: {pack}, skin: {skin}, model: media/models/{model}.glb}}
  portrait: media/portraits/{model}.jpg
  dialogue: village_mayor
  bio_key: npc.mayor_{key}.bio
  about: {place}
  tags: [village, mayor]
""")
        wiki = "{en: %s%s}" % (wikipedia[0], (", cs: " + wikipedia[1]) if wikipedia[1] else "")
        cards.append(f"""- id: {place}
  title_key: knowledge.{place}.title
  text_key: knowledge.{place}.text
  image: media/knowledge/{place}.jpg
  credit_key: knowledge.{place}.credit
  wikipedia: {wiki}
""")
        # the picture file is named village_<id>.jpg: the card's image key must match the media file
        cards[-1] = cards[-1].replace(f"media/knowledge/{place}.jpg", f"media/knowledge/{place}.jpg")
        credit_en = f"Photo or picture: {author}, \"{title}\", {licence}, Wikimedia Commons."
        credit_cs = f"Obrázek: {author}, „{title}“, {licence}, Wikimedia Commons."
        texts["en"] += [f"place.{place}: {q(name_en)}", f"npc.mayor_{key}: {q('Mayor of ' + name_en)}",
                        f"npc.mayor_{key}.bio: {q('The mayor of the village of ' + name_en + ', which will one day be a city of that name.')}",
                        f"knowledge.{place}.title: {q(name_en)}", f"knowledge.{place}.text: {q(text_en)}", f"knowledge.{place}.credit: {q(credit_en)}"]
        texts["cs"] += [f"place.{place}: {q(name_cs)}", f"npc.mayor_{key}: {q('Starosta (' + name_cs + ')')}",
                        f"npc.mayor_{key}.bio: {q('Starosta vesnice ' + name_cs + ', která bude jednou městem téhož jména.')}",
                        f"knowledge.{place}.title: {q(name_cs)}", f"knowledge.{place}.text: {q(text_cs)}", f"knowledge.{place}.credit: {q(credit_cs)}"]
    replace_block(ROOT / "places" / "ancient_villages.yaml", "\n".join(places) + "\n")
    replace_block(ROOT / "npcs" / "ancient_villages.yaml", "\n".join(npcs) + "\n")
    replace_block(ROOT / "knowledge.yaml", "\n".join(cards) + "\n")
    for language in ("en", "cs"):
        replace_block(ROOT / "i18n" / (language + ".yaml"), "\n".join(texts[language] + [f"village_mayor.{k}: {q(v)}" for k, v in DIALOGUE[language].items()]) + "\n")
    (ROOT / "dialogues" / "village_mayor.yaml").write_text(
        "# The mayor of a namesake village (tools/build_ancient_villages.py): shared lines; what he knows is on his knowledge card.\n"
        "id: village_mayor\nstatus: reviewed\nstart: greet\n\nnodes:\n  greet:\n    text_key: village_mayor.greet\n    choices:\n"
        "      - {text_key: village_mayor.ask, goto: answer}\n      - {text_key: village_mayor.leave}\n\n  answer:\n    text_key: village_mayor.answer\n"
        "    choices:\n      - {text_key: village_mayor.leave}\n", encoding="utf-8")
    print("%d villages" % len(VILLAGES))


if __name__ == "__main__":
    main()
