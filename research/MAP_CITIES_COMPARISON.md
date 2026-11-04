# Města z mapky oko.yin.cz/17/uruk/uruk-mapa.jpg a naše mapa

Mapka (`images/oko-yin-uruk-mapa.jpg`) ukazuje 21 míst. Naše kritérium (`ANCIENT_CITIES.md`): město doložené kolem 2700 př. n. l.
(Early Dynastic II), poloha lokality známá, městský charakter. Mapka míchá dobu od Uruku po Kassity a Asyřany, proto na naší mapě
být nemusí všechna. Ověřeno webovým hledáním 3. 11. 2026 (Wikipedia a odkazované zprávy z vykopávek).

## Máme (9)

Ninive, Mari, Ešnunna, Kiš, Nippur, Uruk, Larsa, Ur, Súsy (`places/ancient_cities.yaml`, `places/uruk.yaml`).

## Doplněno touto změnou (3)

| Místo | Poloha | Doklad c. 2700 př. n. l. | Zdroj |
| --- | --- | --- | --- |
| Aššur (Qal'at Širqát) | 35.4567 N 43.2625 E | radiokarbon dřeva pod chrámem Ištar 2896–2702 př. n. l. = ED I, nejstarší úroveň města | https://en.wikipedia.org/wiki/Assur |
| Terqa (Tell Ašara) | 34.9233 N 40.5694 E | vnitřní hradba asi 2900 př. n. l.; fáze Terqa V, EB I/II, 2800–2650 př. n. l.; „velké město už v ED“ | https://en.wikipedia.org/wiki/Terqa , https://www.terqa.org/ |
| Isin (Išán al-Bahríját) | 31.8850 N 45.2686 E | dvě budovy z ED I jižně od chrámového okrsku, dvě tabulky z ED, významné osídlení v ED III | https://en.wikipedia.org/wiki/Isin |

## Nemáme a nepřidáváme (9)

| Místo | Důvod |
| --- | --- |
| Babylon | první zmínka kolem 2300 př. n. l.; kritérium ho vylučuje (`ANCIENT_CITIES.md`); máme jen anachronické památky (`places/babylon.yaml`) |
| Sippar | poloha sporná (`ANCIENT_CITIES.md`) |
| Borsippa | nejstarší jisté doložení Ur III; ED doklad není (možná identifikace s BAR.KI za Naram-Sína je sporná) – https://en.wikipedia.org/wiki/Borsippa |
| Dur-Kurigalzu | založen Kurigalzu I. na počátku 14. stol. př. n. l. (kassitský) – https://en.wikipedia.org/wiki/Dur-Kurigalzu |
| Dur-Katlimmu (Tell Šajch Hamad) | pozdně chalkolitické osídlení, pak město z doby Salmanasara I. (13. stol.); ED doklad není – https://en.wikipedia.org/wiki/Tell_Sheikh_Hamad |
| Arrapha (Kirkúk) | neprozkoumaná, poloha jen předpokládaná; první písemný doklad neosumerský – https://en.wikipedia.org/wiki/Arrapha |
| Nuzi (Jorgan Tepe) | osídlení od obeidu, ale město Gasur je důležité až v akkadské době; ED doklad nepotvrzen – https://en.wikipedia.org/wiki/Nuzi |
| Der (Tell Aqar/Badra) | nenalezen doklad ED osídlení ani jistá lokalizace (hledání bez výsledku) – k dalšímu ověření |
| Qattara | doba Mari/Starobabylonská (2. tis. př. n. l.) |

Pozn.: Habuba Kabira (kolonie Uruku, c. 3200 př. n. l.) z článku `OKO_YIN_URUK.md` mapka nemá; leží před naším obdobím.

## Vesnice stejného jména (9)

Na místě každého z devíti nepřidaných měst stojí **vesnice stejného jména** (`places/ancient_villages.yaml`, `buildings/village_*.yaml`, sedm
domů z perských staveb 0 A.D.) se **starostou** (`npcs/ancient_villages.yaml`, dialog `village_mayor`). Starosta má kartu „Řekni mi o sobě“
(`knowledge.yaml`, `village_<id>`) s obrázkem z Wikimedia Commons, krátkým textem o pozdějším městě a **odkazem na Wikipedii** (anglicky,
česky tam, kde článek existuje: Babylón, Sippar, Borsippa, Dur-Kurigalzu, Kirkúk pro Arrapchu). Generuje `tools/build_ancient_villages.py`.
Poznámky: Dur-Katlimmu odkazuje na článek Tell Sheikh Hamad, Qattara na Tell al-Rimah (identifikace sporná), Der na Der (Sumer);
polohy jsou polohy lokalit (Wikipedia, Wikidata), některé může hrubá světová mapa dát do vody (Babylon, Sippar leží na Eufratu).
