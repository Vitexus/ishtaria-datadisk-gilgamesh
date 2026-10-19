# The attested cities of the world in the Epic's time (c. 2700 BCE)

`places/ancient_cities.yaml` pins every settlement known to have existed around 2700 BCE
(Early Dynastic II, the generation of the Epic) **worldwide**, not only in the Near East.
This note records, for each city, why archaeology places it in that century and where the
pin's coordinates come from. The web sources were consulted in October 2026 through web
search; Wikipedia/Wikidata pages carry the excavation literature in their references, and
the site reports cited below are the primary evidence.

## Criteria

A city is on the map when all of this holds:

- it existed and was occupied around 2700 BCE, as shown by excavation or by finds of that
  horizon (settlements whose urban or monumental phase starts a generation or two after
  the Epic - Dholavira, Caral, Arad's end - are included with a note, within the dating
  uncertainty of the period);
- its site is located: the pin is the archaeological site, not the modern town that
  borrowed the name;
- it was a town or city (walled settlements like Poliochni, Lerna, Los Millares, Zambujal
  are the urban centres of their regions, villages like Skara Brae are not).

Villages without urban character (Skara Brae, Mehrgarh), cities founded centuries later
(Mohenjo-daro's urban phase c. 2500 BCE, Babylon's first mention c. 2300 BCE, Taosi and
Shimao c. 2300 BCE, Kerma's classic city c. 2000 BCE - though its pre-Kerma settlement
is included) and cities whose site is still debated (Akshak, Bad-tibira, Sippar, Thinis)
are not on the map.

## Coordinates

Unless a better source is named, the pin is the coordinate of the site's Wikidata item,
checked against the Wikipedia article and other gazetteers (gps-coordinates.org, mindat);
where sources disagreed, the more specific one won and the choice is noted below.
`tools/build_world_map.py` fails its build when any of these pins lands in the sea.

## Sumer and neighbours

| City | Site and pin | Evidence for c. 2700 BCE | Sources |
| --- | --- | --- | --- |
| Ur | Tell el-Muqayyar, 30.9626 N 46.1030 E | Early Dynastic city, royal cemetery within a few generations (c. 2600 BC) | https://en.wikipedia.org/wiki/Ur |
| Eridu | Tell Abu Shahrain, 30.8261 N 45.9947 E | the oldest city of the King List, occupied from the Ubaid; ED shore site | https://en.wikipedia.org/wiki/Eridu |
| Kish | Tell al-Uhaymir, 32.5403 N 44.6047 E | Enmebaragesi (c. 2700 BC) is the first King List ruler confirmed by finds | https://en.wikipedia.org/wiki/Kish_(Sumer) |
| Nippur | Tell Nuffar, 32.1261 N 45.2308 E | occupied from Ubaid through the Early Dynastic | https://en.wikipedia.org/wiki/Nippur |
| Shuruppak | Tell Fara, 31.7775 N 45.5097 E | ED II city of Ubara-Tutu; excavated flood layers | https://en.wikipedia.org/wiki/Shuruppak |
| Larsa | Tell Senkereh, 31.2858 N 45.8536 E | ED occupation on the Euphrates | https://en.wikipedia.org/wiki/Larsa |
| Umma | Tell Jokha, 31.6672 N 45.8875 E | ED city of the Lagash border wars; the newer Umm al-Aqarib identification (6.5 km SE) is noted in the pin's comment | https://en.wikipedia.org/wiki/Umma |
| Lagash | Tell al-Hiba, 31.4111 N 46.4111 E | 600 ha tell; the Lagash Archaeological Project's own coordinates | https://lagash.github.io/ , https://en.wikipedia.org/wiki/Lagash |
| Girsu | Tello, 31.5653 N 46.1896 E | ED dedications, the city of Ningirsu | https://en.wikipedia.org/wiki/Girsu |
| Nigin | Tell Zurghul, 31.3768 N 46.4957 E | third city of the Lagash state at the marsh edge | https://en.wikipedia.org/wiki/Zurghul |
| Abu Tbeirah | 30.9700 N 46.2680 E | ED delta city; 7 km south of Nasiriyah and 15 km east of Ur (the mission's own distances; Wikidata's 30.81 N 46.68 E points elsewhere and was rejected) | https://en.wikipedia.org/wiki/Tal_Abu_Tbeirah , Forti et al. 2022, https://doi.org/10.1017/qua.2022.22 |
| Kissik | Tell al-Lahm, 30.6100 N 46.3600 E | port of the ED lagoon (already carved dry in the rasters) | research/WORLD.md |
| Adab | Tell Bismaya, 31.9473 N 45.6263 E | ED city of the King List's Adab dynasty | https://en.wikipedia.org/wiki/Adab_(city) |
| Eshnunna | Tell Asmar, 33.8106 N 44.7667 E | Square Temple statues ED I-II (c. 2900-2550 BC) | https://en.wikipedia.org/wiki/Eshnunna |
| Nineveh | Kuyunjik, 36.3586 N 43.1539 E | Ninevite 5 period (3000/2900-2600/2500 BC) | https://en.wikipedia.org/wiki/Nineveh |
| Tell Brak (Nagar) | 36.6700 N 41.0600 E | urban since the Uruk period, main city of the ED north | https://en.wikipedia.org/wiki/Tell_Brak |
| Mari | Tell Hariri, 34.5494 N 40.8900 E | founded c. 2900 BC as a planned city | https://en.wikipedia.org/wiki/Mari,_Syria |
| Susa | 32.1894 N 48.2561 E | Elam's capital, occupied since c. 4200 BC | https://en.wikipedia.org/wiki/Susa |
| Shahr-e Sukhteh | 30.6500 N 61.4000 E | c. 3200-2100 BC, at its height around the Epic | https://en.wikipedia.org/wiki/Shahr-e_Sukhteh |

## Levant, Egypt, Nubia

| City | Site and pin | Evidence | Sources |
| --- | --- | --- | --- |
| Ebla | Tell Mardikh, 35.7981 N 36.7986 E | EB I-II occupation before the c. 2400 BC archive | https://en.wikipedia.org/wiki/Ebla |
| Byblos | 34.1167 N 35.6500 E | EB city, cedar trade with ED Egypt | https://en.wikipedia.org/wiki/Byblos |
| Ugarit | Ras Shamra, 35.6019 N 35.7856 E | EB town on the coast | https://en.wikipedia.org/wiki/Ugarit |
| Sidon | 33.5607 N 35.3683 E | EB I settlement on bedrock at the castle mound | https://en.wikipedia.org/wiki/Sidon |
| Megiddo | Tell el-Mutesellim, 32.5833 N 35.1833 E | occupied c. 3000 BCE continuously | https://en.wikipedia.org/wiki/Tel_Megiddo |
| Jericho | Tell es-Sultan, 31.8717 N 35.4446 E | EB town at the lowest city on earth (-250 m) | https://en.wikipedia.org/wiki/Tell_es-Sultan |
| Arad | Tel Arad, 31.2808 N 35.1250 E | walled EB II city, c. 2950-2650 BC | https://en.wikipedia.org/wiki/Tel_Arad |
| Hazor | Tell el-Qedah, 33.0182 N 35.5691 E | first settled in the Early Bronze Age | https://en.wikipedia.org/wiki/Tel_Hazor |
| Memphis | Mit Rahina, 29.8447 N 31.2509 E | capital since c. 2900 BC | https://en.wikipedia.org/wiki/Memphis,_Egypt |
| Heliopolis | 30.1294 N 31.2889 E | Early Dynastic cult centre of On | https://en.wikipedia.org/wiki/Heliopolis_(ancient_Egypt) |
| Abydos | 26.1852 N 31.9189 E | first-dynasty royal cemetery at Umm el-Qa'ab | https://en.wikipedia.org/wiki/Abydos,_Egypt |
| Hierakonpolis | Kom el-Ahmar (Nekhen), 25.0972 N 32.7794 E | predynastic capital, major ED city | https://en.wikipedia.org/wiki/Hierakonpolis |
| Naqada | 25.9017 N 32.7242 E | Nubt, town of Set, occupied through ED | https://en.wikipedia.org/wiki/Naqada |
| Koptos | Qift, 25.9951 N 32.8197 E | Min colossi and Early Dynastic town | https://en.wikipedia.org/wiki/Koptos , https://www.mindat.org (Qift) |
| Elephantine | island's south tip, 24.0867 N 32.8792 E | ED temples, the first cataract border town | https://en.wikipedia.org/wiki/Elephantine |
| Buto | Tell el-Fara'in, 31.1912 N 30.7402 E | First Dynasty palace excavated | https://en.wikipedia.org/wiki/Buto |
| Kerma | 19.6008 N 30.4097 E | pre-Kerma settlement (c. 3500-2500 BC) | https://en.wikipedia.org/wiki/Kerma |

## Central Asia, the Indus, China

| City | Site and pin | Evidence | Sources |
| --- | --- | --- | --- |
| Altyn-Depe | 36.8547 N 60.4261 E | Namazga III-IV town (c. 3000-2500 BC), near Meana-Chaacha | https://en.wikipedia.org/wiki/Altyndepe |
| Namazga-Depe | 37.3703 N 59.5542 E | eponymous site of the Kopet Dag Bronze Age, by the Tejen delta | https://en.wikipedia.org/wiki/Namazga-Tepe |
| Sarazm | 39.5167 N 67.5667 E | proto-urban centre, C14 3900-2100 BC | https://en.wikipedia.org/wiki/Sarazm |
| Harappa | 30.6333 N 72.8667 E | Ravi phase from c. 3300 BC | https://en.wikipedia.org/wiki/Harappa |
| Kot Diji | 27.3416 N 68.7000 E | fortified Kot Dijian town (c. 3300-2600 BC) | https://en.wikipedia.org/wiki/Kot_Diji |
| Kalibangan | 29.4700 N 74.1300 E | walled Early Harappan KLB-I (c. 3000-2700 BC), ploughed fields | https://en.wikipedia.org/wiki/Kalibangan |
| Rehman Dheri | 31.9678 N 70.7969 E | planned walled town from c. 3300 BC | https://en.wikipedia.org/wiki/Rehman_Dheri |
| Dholavira | 23.8861 N 70.2167 E | Stage I from c. 2650 BC (a generation after the Epic) | https://en.wikipedia.org/wiki/Dholavira |
| Liangzhu | 30.3967 N 119.9853 E | walled hydraulic city, c. 3000-2300 BC | https://en.wikipedia.org/wiki/Archaeological_ruins_of_Liangzhu_City |

## Anatolia, the Aegean, Iberia, the Americas

| City | Site and pin | Evidence | Sources |
| --- | --- | --- | --- |
| Troy | Hisarlik, 39.9575 N 26.2389 E | walled Troy I, c. 2950-2550 BC | https://en.wikipedia.org/wiki/Troy |
| Poliochni | Lemnos, 39.8537 N 25.3430 E | walled EB town contemporary with Troy I | https://en.wikipedia.org/wiki/Poliochne |
| Kültepe (Kanesh) | 38.8500 N 35.6333 E | major early third millennium settlement | https://en.wikipedia.org/wiki/K%C3%BCltepe |
| Liman Tepe | Urla, 38.3633 N 26.7758 E | fortified EB harbour town | https://en.wikipedia.org/wiki/Limantepe |
| Alaca Höyük | 40.2340 N 34.6907 E | EB occupation (royal tombs c. 2400-2300 BC) | https://en.wikipedia.org/wiki/Alaca_H%C3%B6y%C3%BCk |
| Arslantepe | Malatya, 38.3819 N 38.3611 E | EB I town after the c. 2900 BC palace destruction | https://en.wikipedia.org/wiki/Arslantepe |
| Knossos | 35.2981 N 25.1631 E | EM I settlement from c. 2800 BC | https://en.wikipedia.org/wiki/Knossos |
| Lerna | 37.5512 N 22.7182 E | walled EH II settlement, 2700-2200 BC | https://en.wikipedia.org/wiki/Lerna |
| Los Millares | 36.9644 N 2.4597 W | walled chalcolithic settlement, c. 3200-2300 BC | https://en.wikipedia.org/wiki/Los_Millares |
| Zambujal | Torres Vedras, 39.0744 N 9.2858 W | fortified Copper Age town, c. 3000-2500 BC | https://en.wikipedia.org/wiki/Castro_of_Zambujal |
| Caral | Supe valley, 10.8895 S 77.5188 W | oldest city of the Americas, main phase c. 2600-2000 BC | https://en.wikipedia.org/wiki/Caral |
| Áspero | Supe mouth, 10.8156 S 77.7410 W | platform mounds of the same Norte Chico system, from c. 3000 BC | https://es.wikipedia.org/wiki/%C3%81spero_(Caral) |

## Keeping the pins dry in the base map

At 0.05 degrees a raster block is 5.5 km and can be half sea although the tell stood on
dry ground; the block-mean relief of a coastal block can even be negative. Six cities
needed the raster corrections the tool already had (see research/WORLD.md):

- `SHORE_SITES` (tells carved back to land): Kish and Shuruppak, whose blocks the drawn
  one-line rivers cross although the real Euphrates passed the bank beside the tell;
  Ugarit, Sidon and Liman Tepe, whose coastal blocks are majority sea in ETOPO 2022.
- `DRY_DEPRESSIONS` (land below sea level stays land): the Jordan valley between the
  Dead Sea and the Sea of Galilee, the floor of which is dry land 200-400 m below sea
  level - Jericho (about -250 m) stands in it, and both real seas stay water.

Rebuilding the rasters therefore changes the disk's content hash, like every change of
the world's geography (research/WORLD.md).
