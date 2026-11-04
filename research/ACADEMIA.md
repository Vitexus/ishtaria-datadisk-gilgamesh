# Akademické zdroje (`research/academia/`) – co z nich hra použila

Složka obsahuje sbírku z Academia.edu (dva hlavní články, dva balíčky podobných prací). Většina je
mimo téma (dánské a norské eseje, biblická lingvistika M. Ehrensvärda, Hizballáh, Wittgenstein). Tady je
jen to, co se týká Gilgameše, Uruku a krajiny. Texty hry jsou **parafráze**, nic není citováno doslova.

## Použito ve hře

| Zdroj | Co z něj plyne | Kde ve hře |
| --- | --- | --- |
| *Ishtar i Underverdenen* (dánský překlad akkadského Sestupu Ištar, ninivská verze; Carstens, Christensen, Jensen) | sedm bran, u každé se odebírá jedna ozdoba (koruna, náušnice, náhrdelník, náprsní šperky, pás s kameny porodu, náramky, roucho); hlína místo chleba, mrtví oděni peřím; Ereškigal „zelená jako přeříznutý tamaryšek“; návrat týmiž branami, šperky v opačném pořadí; voda života; Tammúz | `dialogues/high_priestess_ishtar.yaml` (`descent`, `gates`), lore `descent_of_ishtar` |
| Annus a Sarv, *The Ball Game Motif in the Gilgamesh Tradition* | epos začíná i končí hrou s míčem (*pukku*) a kladívkem (*mekkû*); čteno jako královský kruh a žezlo, symbol smrtelného království; v XII. tabulce padají do podsvětí | `dialogues/temple_scribe.yaml` (`ball`), lore `ball_and_mallet` |
| Niblett, *The Cult of Gilgameš* (2025); Klein, George, Woods (citováni tamtéž) | po smrti božský soudce podsvětí, „bratr“ králů Ur-Nammy a Šulgiho, kult předků a oběti jídla a pití | `temple_scribe` (`cult`), lore `gilgamesh_cult` |
| Wasserman, *Venerating Gilgameš in Larsa* (2025) | dva hliněné kužely krále Abí-sarea z Larsy (1897–1887 př. n. l.) zmiňují dosud neznámý chrám Gilgameše, který postavil Bingattum | lore `gilgamesh_cult`; v dialogu jen jako předpověď písaře |
| Fink, *The Genealogy of Gilgamesh* | tři tradice: syn Lugalbandy a Ninsun; syn *lillu* (ducha/větru); ze dvou třetin bůh | `dialogues/uruk_elder.yaml` (`birth`), lore `gilgamesh_parentage` |
| Miglio, *Soundscapes, Portentous Calls, and Bird Symbolism* | popis Cedrového lesa: holub, hrdlička, čáp, kuropatev/francolín, cikády; les jako příbytek bohů | `dialogues/humbaba.yaml` (`forest`) |
| *Changing Watercourses in Babylonia*, sv. 1 (eds. Gasche a Tanret, Gent a Oriental Institute, 1998) | řeky netvoří jeden tok, ale rozvětvující se a opět se spojující síť; Eufrat široký asi 250 m a hluboký 5–8 m; osídlení na přírodních hrázích | `dialogues/uruk_water_carrier.yaml` (`river`); doplňuje `RIVER_NETWORK.md` |

## Druhá vlna (ptejte se NPC)

| Téma | Postava (klíče `*.ask_*`) | Zdroj |
| --- | --- | --- |
| Jak se Enkidu měnil (dva týdny, ne jedna noc) | `shamhat` (`growth`) | George, OB fragment Cornell |
| Gazely před ním utíkají | `enkidu` (`beasts`) | Barron; Tabulka I |
| Země se pod patami rozestoupila | `enkidu` (`rift`), lore `why_the_rift` | George, *The Day the Earth Divided* |
| Pták attattu se zlomeným křídlem | `ishtar` (`bird`) | George (Tabulka VI 48–50) |
| Proč had svléká kůži | `utnapishtim` (`snake`) | George (Tabulka XI 287–89) |
| Nevěsty a králova vláda | `uruk_noblewoman` (`brides`) | Rubio (Tabulka I 76–78) |
| Epos mimo Uruk | lore `epic_far_away` | Ugarit, Megiddo (Goren a spol.), Lamassu |

## Přečteno, ale zatím nepoužito (nápady)

- **Barron; Nayeri; *Ecological Predicament*** – Gilgamešovo odmítnutí Ištar jako konflikt civilizace s přírodou; téma pro Enkidův a Šamhatin dialog, nikoli fakta.

## Mimo téma (nepoužito)

Gilgal II (neolitické pazourky), Wittgenstein a hry, dánské a norské eseje, Ehrensvärdovy práce o biblické hebrejštině,
Hizballáh a další.

## Poznámky k dataci

Kult Gilgameše a chrám v Larse jsou doloženy až z doby Ur III a Isin-Larsa (kolem 2100–1890 př. n. l.), tedy po Gilgamešově době
(~2750 př. n. l.). Postavy ve hře o nich mluví jako o budoucnosti nebo jako o proroctví, ne jako o minulosti.
