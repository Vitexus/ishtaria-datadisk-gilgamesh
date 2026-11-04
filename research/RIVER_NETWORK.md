# Říční síť Eufratu a Tigridu, zavlažovací kanály

Stav k 3. 11. 2026. Data ve hře: `rivers/*.yaml`, server `movement::disk_river_carve`, klient `surface_environment.gd`
(`set_disk_rivers`), ADR 0017 v `ishtaria-docs`. Skripty: `tools/build_rivers.py` (velké toky),
`tools/build_river_network.py` (přítoky), `tools/build_landscape.py` (kanály v terénu Uruku).

## Velké toky

`euphrates.yaml`, `tigris.yaml`: zdroj až k ústí. Nad Hitem a Mosulem dnešní koryto (Natural Earth 1:10m, public domain), níže
raně dynastický tok z `build_world_map.py` (Adams 1981, Steinkeller 2001, Hritz 2021); Eufrat prochází středem vody uručského
výřezu terénu.

## Přítoky a potoky

`network_01.yaml`: 946 toků, 30 409 bodů, z **HydroRIVERS v1.0** (Lehner a Grill 2013, https://www.hydrosheds.org/products/hydrorivers,
CC BY 4.0 + podmínky HydroSHEDS), dlaždice „eu“ (Střední východ), povodí Šatt al-Arab (Eufrat, Tigris, Karún, Karcha, Dijála, Zábové …).

* Zahrnuto: úseky řádu `ORD_FLOW` ≤ 6 (od hlavních toků po potoky kolem 1 m³/s), šířka vody = 3,4·√Q m (10–400 m).
* Vynecháno: aluviální rovina pod 33,6° s. š. a západně od 47° v. d. (HydroRIVERS tam kreslí dnešní kanály a hráze z DEM, ne řeky
  roku 2700 př. n. l.; plochu obsluhují Eufrat, Tigris a kanály), a vše do 1 km od velkých toků.
* **Zatím chybí** potůčky řádů 7–10 (dalších ~50 000 úseků, 125 000+ bodů). Vyžadují načítání po oblastech (server by posílal jen
  řeky v okolí hráče) místo jednoho souboru; viz „Dál“.

## Zavlažovací kanály Uruku

Podklad: obrázek uživatele (substack, `images/euphrates-crevasse-splay-canals.jpg`), panel B: **splay po protržení hráze Eufratu
s jezem (barrage), kmenovým kanálem a „rybí kostí“ polních kanálů** („Canals and farms“) na souřadnicích 46.022474° E, 31.120260° N
(popisky os). **Zdroj: Jotheri a spol. 2025 (Antiquity), Fig. 2** – „An example of a contemporary crevasse splay on the modern Euphrates 30 km north-east of the Eridu Region: A) Corona 1968; B) the reconstructed crevasse splay, illustrating how farmers can modify a crevasse splay, dig irrigation canals, build a barrage to control the flooded water and claim land for farming“ (CC BY 4.0; viz níže). Měřítko: 300 m = 155 px.

* `tools/data/canal_template.json`: 41 polylinií nad panelem B (digitalizace skeletonem: kmenový kanál s měřenou šířkou 12–38 m,
  boční kanály 5–8 m), počátek v jezu.
* `tools/build_landscape.py` (`CANALS`) otáčí šablonu tak, aby kanály vedly od řeky pryč, a klade ji na tři místa u řeky u Uruku
  (východní břeh severně a jižně od města, západní břeh severně). Kanál je v terénu 1,5 m (kmen) / 0,9 m (polní) pod pláň, hladina
  0,5 m pod pláň (jako hladina řeky), takže voda z řeky stéká do kanálů.
* Rozlišení výřezu terénu je 10 m, proto mají polní kanály šířku jednoho políčka.

**Poctivost:** Uruk, ani jeho kanály nejsou v zdroji doloženy takto; šablona je skutečné uspořádání z moderního snímku a Uruk je
její použití, **ne rekonstrukce plánu kanálů Uruku**. Oko (OKO_YIN_URUK.md) výslovně píše, že hypotéza složité kanálové sítě
Uruku není potvrzena.

## Kanály mezi Urukem a Larsou (průzkum)

Podklad: mapa v `research/canals-uruk-larsa.jpg` (799 × 526 px) z průzkumu kanálů oblasti Uruk–Larsa: kanály známé z dřívějších
publikací (purpurově) a nově nalezené (zeleně), velké/střední/jemné, pojmenované W1–W5, poloha lokalit Warka Survey (Adams a
Nissen 1972) a Jotheri (2016), duny 1972 a 2022, dnešní Eufrat. Publikace na kopii **není uvedena – doplnit citaci** (cituje Jotheri 2016 a Adams a Nissen 1972; není to Jotheri a spol. 2018).

* `tools/build_uruk_larsa_canals.py` (devět kanálů, W3, W4, W5, W1, W2, severní, C6, C7 a kanál od Larsy k severovýchodu, asi 92 km): ručně
  digitalizované z malého obrázku, poloha na ±0,5 km. Georeference: tell Uruku (198, 183 px) = kotva výřezu terénu, 1 px = 53,7 m
  (měřítko 3 km = 55 px), tell Larsy vychází 20,5 km na východ (pin Larsy: 20,5 km).
* Třídy → šířka vody: velké 20 m, střední 14 m, jemné 10 m (minimum, které datadisk dovolí).
* Ve hře dvakrát: `rivers/uruk_larsa_canals.yaml` (mimo výřez Uruku) a jako polylinie v metrech, které `build_landscape.py` vyřezává
  do výřezu terénu u Uruku (tam řeky z `rivers/` nepůsobí).
* **Chybí:** stovky jemných kanálů (vložky Map 1 a Map 2: „rybí kost“ na W4 a u Larsy). Potřebují obrázek v plném rozlišení;
  pošlete-li ho, digitalizují se stejně jako ostatní.
* **Poctivost:** kanály průzkumu jsou reliktní koryta nalezená dálkovým průzkumem; jejich stáří se u jednotlivých kanálů liší
  (část je mladší než 2700 př. n. l.), hra je kreslí všechny jako vodní kanály.

## Kanálová síť oblasti Uruk–Larsa (Jotheri a spol. 2018)

Oba obrázky pocházejí z práce **Jotheri a spol. 2018** (`JOTHERI_2018_URUK_REGION.md`, `Jotherietal2017.pdf`): Fig. 4 „identified
channels and archaeological sites“ (`The-identified-channels-...jpeg`) a Fig. 6 „Channel networks of the Uruk region at different
time intervals“ (`Channel-networks-...webp`). Podstatné: **Fig. 6 A = raný 4. až pozdní 1. tis. př. n. l. (naše doba)**; B je pozdější
(hlavní kanál od severozápadu je vykopán v sasánovské době); C a D jsou nové. Fig. 4 skládá koryta všech dob, takže se z ní bere
jen to, co má i panel A.

`tools/digitize_channel_network.py`: čáry se skeletonizují, tečky lokalit, popisy a kroužky vrtů se odstraní, čáry se zjednoduší
na ~150 m. Georeference podle tellů Uruku a Larsy (20,9 km = 96,8 m/px v Fig. 4); souřadnice vrtů ověřují, že sedí (M38, M25).
Tloušťka čáry určuje třídu (silná = 30 m vody, střední 20 m, tenká 14 a 10 m; v terénu u Uruku nejvýš 20 m). Pořadí: kanály průzkumu
(`build_uruk_larsa_canals.py`) → čáry Fig. 4, které má i panel A (dvojice do 250 m se slučují) → čáry panelu A, které nemá nic z toho.
Výsledek: 263 čar, 604 km, `rivers/uruk_region_network_*.yaml` (mimo výřez Uruku řeže a kreslí server i klient) a `build_landscape.py`
je řeže do výřezu; **kolem města (hradba + 40 m) se nekope**. Odloženo: 318 čar Fig. 4 z pozdějších intervalů a panel B (75 čar),
ve hře nejsou.

**Poctivost:** časová vrstva je to, co práce uvádí (osídlení podél kanálu a radiokarbon), ne měření stáří každého kanálu; jejich
poloha je ±0,3 km.

## Pole kolem kanálů

`tools/build_fields.py` (po `build_landscape.py`): po obou stranách každého kanálu ve výřezu terénu u Uruku (kanály z
`tools/data/uruk_canals_used.json`) leží každých 30 m pole 27 m podél kanálu a 26 m (u větších kanálů 34 m) do hloubky, 14 m od osy
kanálu (cestička); **brázdy běží od kanálu pryč**, jako teče voda (brázdová závlaha, Liverani; `RTF_LOST_IN_TIME_URUK.md`,
Jotheri a spol. 2018: samospádová závlaha od hráze). Pole se vynechá, kde by stálo ve vodě, do 120 m od hradby nebo na jiném poli.
Je zelený ječmen (50 %), zralý (30 %) nebo úhor (20 %); 922 polí na 99,5 ha. Pole jsou `passable` budovy místa `uruk_fields`
(server: neblokují chůzi a leží na zemi; modely `media/models/architecture/field_*.glb` z `tools/build_field_models.py`) a zapisují
se do masky `uruk_clear.png`, aby v nich nerostly divoké stromy. **Mimo výřez Uruku (kanály 3–20 km od města) pole zatím nejsou**:
generátor jde po polylinii a výřez je jediné místo, kde terén i voda existují v 10m rastru.

## Oblast Eridu (Jotheri a spol. 2025, Antiquity)

**Jotheri, J., Rokan, M., Al-Ghanim, A., Rayne, L., de Gruchy, M., Alabdan, R.: *Identifying the preserved network of irrigation canals in the
Eridu region, southern Mesopotamia*, Antiquity 99 (2025), doi:10.15184/aqy.2025.19** (`identifying-the-preserved-network-...pdf`, 7 stran, otevřený
přístup, **CC BY 4.0**; obrázky v `research/images/eridu-*.png`). Oblast Eridu byla osídlena od rané obeidské doby po neobabylonskou
(6. tis. až raný 1. tis. př. n. l.) a pak ji opustil posun Eufratu, proto se krajina zachovala.

| Zjištění práce | Použití |
| --- | --- |
| **Více než 200 primárních kanálů** napojených přímo na dávný Eufrat, **1–9 km dlouhých a 2–5 m širokých**; **více než 4 000 menších a odbočných kanálů** 10–200 m dlouhých a 1–2 m širokých; **více než 700 farem** o ploše **500–20 000 m²** s kanály po obvodu; kanály až 100 km dlouhé (Wilkinson a spol. 2015) | `tools/digitize_eridu_canals.py` → `rivers/eridu_canals.yaml`: **170 primárních kanálů (225 km)**; velikost polí u Uruku 500–2 500 m² (`build_fields.py`) |
| Eufrat zůstal v korytě po celou dobu osídlení (jen se posouval v něm), žádné avulze → kanály byly stále napojené; **oba břehy** kanalizované, **severní víc** | dávný Eufrat u Eridu jako řeka `eridu_euphrates` (120 m vody, 34 km, středová čára světle modré plochy v Fig. 5); její severovýchodní konec leží do 2 km od raně dynastického toku u Ur (`build_world_map.py`) |
| Síť je **souhrn všech období**, nikdy nefungovala celá najednou; chronologii kanálů je třeba teprve určit | poctivě: hra kreslí všechny primární kanály, i ty, které mohou být mladší než 2700 př. n. l. |
| Bez avulzí a s hrázemi: voda teče samospádem, **crevasse splay** je přirozený začátek kanálu (Fig. 2: splay s jezem na dnešním Eufratu 30 km SV od oblasti Eridu) | šablona kanálů u Uruku (`tools/data/canal_template.json`) je právě tento obrázek (Fig. 2 B); souřadnice 31,12° s. š., 46,02° v. d. sedí na „30 km severovýchodně od Eridu“ |
| Fig. 1: topografická mapa celé aluviální roviny s paleokoryty (černě) a dnešními koryty (modře), z disertace Jotheri 2016 (fig. 2:30), s polohou oblasti Eridu | **zatím nepoužito**: paleokoryta všech období; digitalizace by potřebovala georeferenci podle dnešních koryt (HydroRIVERS) a výběr podle doby |

**Co z Fig. 5 ve hře není:** 4 000 drobných kanálů (1–2 m široké, 10–200 m dlouhé) tvořících obvody farem; při nejužší vodě datadisku (10 m) by
zatopily pole, která zavlažují. Jejich nahrazení vodou zatím není; jde o pole bez vody (viz „Pole kolem kanálů“): pro Eridu nejsou, protože oblast
Eridu nemá výřez terénu.

## Herringbone (rybí kost)

Rešerše: hlavní zavlažovací soustavy na středomezopotámské rovině mají tvar rybí kosti, vzniklé z kanálů protržených hrází
(crevasse splays), a pro Ur III ho potvrzují polní plány z Lagaše (studie z roku 2015, DOI 10.1007/s12685-015-0127-9, autory jsem neověřil; Antiquity 2025, vedoucí projektu Jaafar Jotheri – síť přes 200
hlavních kanálů napojených na dávný Eufrat a přes 4 000 menších kanálů u více než 700 polí v oblasti Eridu, Durham University).
Obrázek z https://www.researchgate.net/figure/Ancient-canal-in-herringbone-irrigation-system_fig1_325248832 **se nepodařilo
stáhnout** (ResearchGate vrací 403) a plné články jsou za paywallem; číselná geometrie (úhly, rozestupy) proto není převzata.
Pokud obrázek pošlete, digitalizuje se stejně jako první.

## Dál

1. Streaming řek po oblastech (`GET /world/rivers?x&y&z`) a potůčky řádů 7–10.
2. Zelenější krajina: malovat biomy (`world.biomes.map`) podél řek a kanálů, vegetace u vody (rákos, palmy) na místech `waterside`.
3. Kanály mimo uručský výřez (oblast Eridu) jako `rivers/*.yaml` podle nových dat z Antiquity 2025.
