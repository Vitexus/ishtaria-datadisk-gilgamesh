# „Lost in time: Uruk“ (Rethinking The Future, rtf-rethinkingthefuture.com)

Soubor: `Lost in time_ Uruk - RTF _ Rethinking The Future.html` a složka `..._files/` (čteno 3. 11. 2026). Popularizační článek
studentů architektury (6 minut čtení); **sekundární a v místech chybný zdroj**. Použito jen to, co potvrzují jiné naše prameny.

## Obrázky ve složce (A8565-Lost-in-time-Uruk-*)

| Soubor | Co ukazuje | Použití |
| --- | --- | --- |
| `Image-1` | plán **Anu district of Uruk III** (Wikipedia, CC): terasa s ziggurátem Anu, oltář, schodiště pro procesí, Bílý chrám (W), kamenná budova (S) | podklad půdorysu Bílého chrámu a terasy (`ZIGGURATS.md`) |
| `Image-2` | **Bílý chrám a ziggurat ve Warce**, pohled od západu (rekonstrukce) a plán, archaické období 3500–3000 př. n. l.; svahy teras s šikmým žebrováním, rampa | kontrola modelu ziggurátu Anu v `places/uruk*.yaml` |
| `Image-3` | **mozaika z kamenných kuželů** (Eanna, vystavená v muzeu; foto Usama Shakir Muhammad Amin, CC BY-SA) | textura zdi Eanny (kuželová mozaika) |
| `Image-4` | plán **Eanna district of Uruk IV** (Wikipedia, CC): velký dvůr (GC), velká hala (GH), sloupový sál (PH), červený chrám (RT), budovy A–N, budoucí ziggurat Ur-Nammu | uspořádání Eanny; poznámka: budova E a velký dvůr = „Eanna“ 300 × 300 m (`OKO_YIN_URUK.md`) |
| `770x515` | koláž s rekonstrukcí města a kompasem (ilustrace, bez autora) | bez použití |

## Fakta z textu a jak se k nim stavíme

| Tvrzení článku | Posouzení | Použití |
| --- | --- | --- |
| **Rozsáhlý kanálový systém procházel Urukem od severu k jihu; velké kanály sloužily dopravě: přístavy, vodní brány, přístaviště** | **potvrzeno** naší vlastní prací (magnetogram, `tools/build_city.py`: síť kanálů uvnitř hradby, hlavní kanál s vodní bránou, `uruk_harbour`) | už ve hře; kanály z Jotheri a spol. 2018 se kolem města (hradba + 40 m) nekopou, aby nepřebíjely plán města |
| Furrow irrigation (brázdová závlaha) vyžadovala centrální správu, vedla k nástrojům a tahu zvířat (Liverani) | rozumné (Liverani, *Uruk: the first city*) | **brázdy polí** běží od kanálu pryč (`tools/build_fields.py`); orba s voly = námět pro NPC orače (`uruk_plowman`) |
| Dvě čtvrti: **Eanna** (Inana/Ištar) a **Anu** (bůh nebes; starší, jedna terasa se ziggurátem Anu, 14 stavebních fází, vápenec a bitumen na udusané hlíně, vápencové schodiště pro procesí) | potvrzuje `ZIGGURATS.md`, `CITY.md` | beze změny; „14 fází“ přidáno do knowledge karty Anu (návrh) |
| Bílý chrám se sádrovou omítkou, zvyšuje ziggurat na **21 m** | kolísá podle zdroje (Bílý chrám stojí na terase asi 12–13 m) | nepřevzato |
| Eanna: dvory s malými místnostmi (obřady, dílny, školy, úřady); první budova **Stone-Cone Temple** s vápencovou zdí a pilíři; mozaika z kamenných kuželů na sádrovém podkladu; **tripartitní** a **T-tvarový** půdorys | potvrzeno | textura kuželů (Image-3) |
| Uruk IV: velký dvůr se **zapuštěným nádvořím a akvaduktem** na zalévání zahrad | zajímavé, ve hře není | námět pro zahradu u Eanny |
| Magnetometr **2001–2019** (Mnichov: Fassbinder, Becker): střed Uruku stojí na **35 vrstvách** hlubokých **25 m**, nejstarší z **4500 př. n. l.** | potvrzeno (Fassbinder a Becker 2003 – magnetometrie Uruku) | knowledge karta / tablet |
| „Založen 4000 př. n. l.“, „nejdéle nepřetržitě obývané město světa, 5500 let“, „**40 000 obyvatel**, 5,5 km² (900 ha hradby 9 km)“, „Uruk IV Eanna 600 ha“, „velké svatyně 200 př. n. l.“, „300 let sucha v 18. stol.“, „Eufrat se posouval na západ, kanály vyschly do 4. stol. n. l.“ | **neověřeno / chybné** (Jotheri a spol. 2018: ~400 ha ve 3. tis., 200+ ha koncem 4. tis., opuštěno ~1600, ~1200 př. n. l.; plocha Eanny není 600 ha) | **nepoužito** |
| 15 km východně od Samávy, 300 km jižně od Bagdádu | v souladu (Uruk 45,64° E, Samáva 45,28° E: ~35 km východně; 15 km je chyba) | nepřevzato |

Citované práce v článku, které stojí za dohledání: Liverani (2006) *Uruk: the first city*; Fassbinder a Becker (2003) *Magnetometry at Uruk
(Iraq): the city of King Gilgamesh*; Baker (2003) *The urban landscape in first millennium BC Babylonia*; Charvát a spol. (2002) *Mesopotamia
before history*; Crawford (2004) *Sumer and the Sumerians*.
