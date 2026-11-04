# Jotheri a spol. 2018: povodí Uruku v holocénu (research/Jotherietal2017.pdf)

**Jotheri, J., Altaweel, M., Tuji, A., Anma, R., Pennington, B., Rost, S., Watanabe, C.**: *Holocene fluvial and anthropogenic
processes in the region of Uruk in southern Mesopotamia*, Quaternary International (2018), doi:10.1016/j.quaint.2017.11.037
(ve složce výzkumu: `Jotherietal2017.pdf`, 13 stran, přečteno celé včetně obrázků). Obrázky Fig. 4 a Fig. 6 jsou ty, které jsme
dostali jako samostatné soubory (`The-identified-channels-...jpeg`, `Channel-networks-of-the-Uruk-region-...webp`) a které
`tools/digitize_channel_network.py` přepisuje do kanálů hry.

## Co práce říká (a jak se to použilo)

| Zjištění | Použití v datadisku |
| --- | --- |
| Metody: SRTM, CORONA (1959–72), QuickBird, 5 vrtů (BH38, BH54, M25, BH55, M38), radiokarbon, rozsivky; paleokoryta datována podle osídlení podél nich (Adams 1981) | souřadnice vrtů ověřují georeferenci obrázků (M38 31°22′46.98″ N 45°48′50.66″ E vyšlo v Fig. 4 na 16,9 km východně a 6,5 km severně od Uruku, jak má) |
| **Čtyři časové intervaly** sítě koryt: **A** raný 4. tis. až pozdní 1. tis. př. n. l.; **B** pozdní 1. tis. př. n. l. až polovina 2. tis. n. l.; **C** po islámu do 80. let 20. stol.; **D** od 80. let (jedno meandrující koryto) | **jen A je z doby Gilgameše**; B, C, D se ve hře nekreslí (`tools/data/uruk_region_network.json` „earlier“/„later“) |
| Síť A je **anastomózní**: propojená koryta obklopují záplavové pánve, rozcházejí se a znovu setkávají; severně od dnešního Eufratu je tak propletená, že se hlavní koryto nepozná od větví, jižně je jedno hlavní koryto s větvemi | proto je síť ve hře hustá a bez „hlavní řeky“; hlavní kanál přes Uruk z kapitoly „B“ ve hře není |
| **Hlavní koryto od severozápadu k Uruku a jižně kolem něj je vykopané v sasánovské době** (vrt: 3 m střepů, dole bažinné uloženiny 3. tis.) | koryta z Fig. 4, která nejsou v panelu A, jsou pozdější: **nepoužita** (318 čar odloženo) |
| Dnešní Eufrat nemá starověká koryta ani lokality podél sebe (je překryl, nebo tu byla poušť a hluboké bažiny) | modré aktivní koryto z obrázku **nepoužito**; náš raně dynastický Eufrat zůstává podle Adamse (`build_world_map.py`) |
| Více než **400 lokalit** 4.–1. tis. př. n. l., většinou podél paleokoryt; Uruk jediný osídlený po většinu doby | tečky lokalit z Fig. 4 se odstraňují; **jejich polohy zatím nejsou ve hře** (nápad: osady a pole u lokalit 3. tis., viz níže) |
| Hráze koryt jsou o **2–5 m výš** než niva; závlaha jen samospádem u hrází; nejdřív se kopaly kanály přes **crevasse splay** | tvar kanálů „rybí kost“ z obrázku od uživatele (jez, splay, polní kanály) |
| Klínopisné záznamy: závlaha zůstala jednoduchá, **krátké primární kanály uspořádané do rybí kosti** až do 2. tis. př. n. l.; Urnanše z Lagaše hlásí sedm primárních kanálů, Ur-Namma sedm „přes zemi“; velikost kanálů texty neříkají | důvod, proč u Uruku stavíme krátké kanály s rybí kostí (a ne velké plánované soustavy) |
| Uruk: 5. tis. osídlen, od poloviny 4. tis. velké město (200+ ha), **ve 3. tis. asi 400 ha**; ~1600 př. n. l. opuštěn, 1400 znovu, ~1200 opět, v 1. tis. př. n. l. 50+ ha | **rozpor**: Oko a naše hradba mají ~550 ha kolem 2700 př. n. l. (`OKO_YIN_URUK.md`); Jotheri píše 400 ha pro 3. tis. |
| Celý Holocén sladkovodní prostředí, žádný vliv přílivu ani Zálivu u Uruku; bažiny (rákos, ryby, ptáci, prasata) střídají koryta | výzdoba: rákos a bažiny u vod (`uruk.yaml` wildlife); potvrzuje, že Záliv v Epu nesahá k Uruku |
| Střídání koryt a bažin = časté avulze | důvod, proč ve hře není jedna stálá řeka |

## Dál (nápady z práce)

1. Osady a pole na polohách lokalit 3. tis. př. n. l. z Fig. 4 (červené tečky; v obrázku jsou digitalizovatelné).
2. Nivu 2–5 m pod hrázemi: hráze podél hlavních kanálů (výška terénu), dnes kanály jen kopou koryto.
3. Bažiny mezi hrázemi (maska vody v mělké nivě).
