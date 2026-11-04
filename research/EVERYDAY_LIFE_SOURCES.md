# Všední život v Mezopotámii – zdroje pro dialogy NPC

Cíl: každé NPC má vyprávět **jiný** příběh a v informačním dialogu ("Řekni mi o sobě",
`knowledge.yaml`) může odkázat na tabulku nebo studii, ze které dialog čerpá.
Tento dokument je podklad, ne hotové dialogy: obsahuje korpus, zdroje a přiřazení příběhů.

## 1. Co se podařilo získat

| Zdroj | Rozsah | Poznámka |
| --- | --- | --- |
| **CDLI bulk dump** ([github.com/cdli-gh/data](https://github.com/cdli-gh/data), stav srpen 2022) | 135 254 transliterovaných textů; **5 369 má anglický překlad** | Skript `tools/fetch_cdli_translations.py` je stáhne a vyfiltruje (výstup ~6 MB se necommituje). |
| **ETCSL** (Oxford, [etcsl.orinst.ox.ac.uk](https://etcsl.orinst.ox.ac.uk/)) | Překlady sumerské literatury, přísloví, dopisů | Stažené: Instrukce Šuruppakovy, Farmářovy instrukce, Dumuzid a Enkimdu, hymnus na Ninkasi, přísloví (kolekce 1–3, 21, Nippur/Ur/Susa), Lu-diĝirova zpráva matce, Spor motyky a pluhu, Edubba C aj. |
| Studie k archivu **Eanna** (Uruk, chrám Ištar) | Nájmy polí, naturální renty | [Univ. Vídeň – disertace](https://utheses.univie.ac.at/detail/27514), databáze [NaBuCCo](https://nabucco.acdh.oeaw.ac.at/) |

Rozdělení 5 369 přeložených tabulek podle CDLI (jen to podstatné):
Ur III administrativa 1 846, starobabylonská literatura 495, Ur III královské 266,
starobabylonská administrativa 182, **školní texty 148 (+125 z Uru)**, **dopisy ~110**,
**právní/smluvní texty ~140**, rané dynastické (ED IIIb) administrativa 34.

### Co se nepodařilo
- **ORACC** (`oracc.museum.upenn.edu`, `oracc.org`) z tohoto stroje neodpovídá, takže chybí
  neoasyrské dopisy (SAAo, ~3 000 dopisů s překladem), epsd2 a CAMS. Zkusit z jiné sítě.
- Většina z "desítek tisíc" tabulek existuje **jen v transliteraci**, bez překladu. Dá se z nich
  čerpat (jména, množství, ceny, svědci), ale překlad by byl náš a musí být označen jako takový.
- Starobabylonské dopisy sbírky AbB a Oppenheimovy *Letters from Mesopotamia* nejsou volně dostupné.

## 2. Časová poctivost

Uruk hry je z doby Gilgameše (~2700 př. n. l., rané dynastické období). Většina přeložených
všedních textů je **mladší**: nejstarší jsou dopisy a účty z Girsu (ED IIIb, ~2500–2340),
nejvíc je Ur III (~2100–2000), Larsa/Nippur/Sippar (~1900–1600), Kanesh (~1950–1850).
Instrukce Šuruppakovy mají **rané dynastické opisy** (Abu Salabikh, ~2600) – to je nejbližší
literární zdroj. Pro dialogy je to přijatelné (hospodářské poměry se v tisíciletích měnily
pomalu), ale informační dialog by měl říct "podobný text z doby…" a neprohlašovat
tabulku za dokument z Uruku Gilgameše. Pole `period` v kartě to ponese.

## 3. Návrh pole `source` ve `knowledge.yaml`

Karta dnes umí jen `wikipedia`. Navrhuji přidat (vyžaduje změnu schématu v `ishtaria-protocol`
a klienta – zatím neprovedeno):

```yaml
source:
  cdli: P384863            # https://cdli.earth/P384863
  etcsl: t.5.6.3           # https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.6.3
  citation_key: knowledge.uruk_plowman.citation   # "Civil 1994, The Farmer's Instructions"
  period_key: knowledge.period.old_babylonian
```

## 4. Příběhy pro existující NPC (jedna tabulka = jeden příběh)

Parafráze podle překladů z CDLI/ETCSL; odkazy vedou na celé tabulky.

| NPC (`dialogues/…`) | Příběh | Zdroj |
| --- | --- | --- |
| **high_priestess_ishtar** | Chrám Ištar žádá o povolení otevřít nové pole u řeky; platí naturální rentou (v archivu Eanna např. 300 kor ječmene a 5 kor sezamu ročně Paní z Uruku, nebo podíl ze sklizně 1/5 podle způsobu zavlažení). Veleknězka se dohaduje o hrázích a kanálech. | Archiv Eanna (Uruk): [disertace](https://utheses.univie.ac.at/detail/27514), [NaBuCCo 3122](https://nabucco.acdh.oeaw.ac.at/archiv/tablet/detail/3122); Farmářovy instrukce [ETCSL t.5.6.3](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.6.3); spory o kanály [BE 17/1, 003 (P266568)](https://cdli.earth/P266568) |
| **uruk_farmer** | Půjčka ječmene z chrámového hospodářství Enlilova: splatí se při sklizni a dlužník **přísahou slíbí**, že nebude tvrdit "pole mi zničila povodeň/bouře". | [NRVN 1, 180 (P122397)](https://cdli.earth/P122397), [TMH NF 1-2, 069 (P134381)](https://cdli.earth/P134381) (Nippur, Ur III) |
| **uruk_plowman** | Technika orby: osm brázd na nindan, zrno dva prsty hluboko, záložní vůl i pluh, "kdo drží osivo, hlídej ho"; spor motyky a pluhu. | [Farmářovy instrukce t.5.6.3](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.6.3), [Spor motyky a pluhu t.5.3.1](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.3.1), [Píseň orných volů t.5.5.5](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.5.5) |
| **uruk_alewife** | Pivovarnická: postup od sladu po cezené pivo (Ninkasi), zákaz nalévat pivo neumytýma rukama ("ohavnost před Utuem"). | [Hymnus Ninkasi t.4.23.1](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.4.23.1), přísloví kolekce 3 [t.6.1.03](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.6.1.03) |
| **uruk_merchant** | Kupec v Kaneši: napomíná společníka, že dostal 16 min stříbra a poslal zlato sobě, ne jemu; osel zdechl; "zavřít dlužníka do vězení". Přísloví: "Kupec zmenšil stříbro, olej i ječmen." | [P272898](https://cdli.earth/P272898), [P272899](https://cdli.earth/P272899), [OAA 1, 051 (P361694)](https://cdli.earth/P361694); [t.6.1.03](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.6.1.03) |
| **village_trader** | Muž žádá dvoukolový vůz, kterým mu nechtějí vydat; ví, že stojí v domě Baziziho – "můj vlastní člověk ho viděl!". | [Adab 0636 (P217470)](https://cdli.earth/P217470) (starý akkadský dopis) |
| **uruk_water_carrier** | Dva dělníci mají vykopat studny, aby bylo kde čerpat vodu a dům žil; píše se, kolik dní bude kopání trvat. | [PBS 1/2, 050 (P261026)](https://cdli.earth/P261026) |
| **water_seller** | Člun s hrnci k vykládání, deset dělníků; příběh o tom, kdo platí dopravu. Přísloví "Chléb je loď, voda je bidlo." | [TCS 1, 216 (P145724)](https://cdli.earth/P145724); [t.6.1.01](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.6.1.01) |
| **uruk_mason** | Cena domu: zastavěná parcela 1 SAR i se střechou za 40 šekelů stříbra, nezastavěná za 5; a dokument datovaný "rokem, kdy byla postavena velká hradba Nippuru". Plot z rákosu a závlahové příkopy. | [PBS 8/2, 103 (P262078)](https://cdli.earth/P262078), [PBS 8/2, 157 (P125408)](https://cdli.earth/P125408), [PBS 1/2, 028 (P261028)](https://cdli.earth/P261028) |
| **potter** | Hrnčíř jako svědek směny kovu; lodní náklad hrnců. | [SC-UCLA (P388587)](https://cdli.earth/P388587) (Umma, ED IIIb), [P145724](https://cdli.earth/P145724) |
| **smith** | Kovář objednává cínové odpadky a prášek, pórek, voňavé oleje, jalovec a 2 talenty mědi ("ani krátký den neotálej"). | [YOS 2, 112 (P306561)](https://cdli.earth/P306561) (Larsa); [RA 6, 139 (P247594)](https://cdli.earth/P247594) – správce a mistr kovářů po boji s Elamity (Girsu, ED IIIb) |
| **weaver** | Syn píše matce Zinu: cizí chlapci mají každý rok lepší šaty, jemu je zmenšuje; "vlna v našem majetku se spotřebovává jako chléb". | [TCL 18, 111 (P387407)](https://cdli.earth/P387407) (Larsa) |
| **uruk_noblewoman** | Nadítu (zasvěcená žena) Bēlessunu dostává od otce pole; jiná žena dostává věno: otrokyně, šaty, mlecí kameny na jemnou a hrubou mouku, dvě postele, pět židlí, "hlavní" stůl. | [VS 8, 003 (P372427)](https://cdli.earth/P372427), [BE 6/1, 101 (P258858)](https://cdli.earth/P258858) (Sippar) |
| **uruk_noble** | Spor o pole přidělené omylem: místo pole Sin-asû dostali pole Betatum. "Prošetři to, ať ti pole vrátí." | [RA 102, 051 (P247948)](https://cdli.earth/P247948) |
| **uruk_elder** | Adopce dospělého: syn, který řekne "nejsi můj otec", bude oholen a prodán; rodiče, kteří řeknou "nejsi náš syn", ztratí dům. Plus rady Šuruppakovy. | [VS 8, 127 (P372528)](https://cdli.earth/P372528); [Instrukce Šuruppakovy t.5.6.1](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.6.1) (raně dynastické opisy) |
| **temple_scribe** | Rada staršího písaře mladšímu a odpověď: "otevřel jsi mi oči jako štěněti"; písař řídí domácnost, pole i rozdělování příděl. | [Edubba C t.5.1.3](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.1.3) |
| **tablet_writer** | Přísloví o písařích: "Kdo zná jen jeden řádek, ale má pěkné písmo, je písař"; "Písař, který neumí sumersky, jak by překládal?" | [Ur, UET 6/2 – t.6.2.3](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.6.2.3); 125 školních tabulek z Uru v CDLI |
| **tablet_bearer** | Královský kurýr nese zprávu matce do Nippuru a musí ji poznat podle popisu ("její jméno je Šat-Ištar, sama udržuje dům tchána…"). | [Zpráva Lu-diĝiry matce t.5.5.1](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.5.1); [Elegie na Nannaju t.5.5.2](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.5.2) |
| **royal_guard** | Vrátní dostávají svazky rákosu (180 a 120), které guvernér přikázal vydat. | [NYPL 186 (P122724)](https://cdli.earth/P122724) (Umma, Ur III) |
| **hunter_father** | Pastýř hlásí ztrátu: 660 ovcí s jehňaty, 24 volů a krav, 16 oslů odehnáno – "musí být nahrazeni". Pastýř Ilī-ippalsam ztratil pole 3 bur, které mu dalo písmo královo. | [Nik 1, 177 (P221946)](https://cdli.earth/P221946) (Girsu, ED IIIb); [OECT 3, 1 (P384863)](https://cdli.earth/P384863) (dopis Hammurabiho) |
| **uruk_temple_courtesan** | Šugītu Damiqtum: věno, vdavky, synové jako dědicové; matka Lu-diĝiry "střeží Inanino místo". | [BE 6/1, 101 (P258858)](https://cdli.earth/P258858); [t.5.5.1](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.5.5.1) |
| **ur_shanabi** | Najatý dělník: 10 šekelů za rok práce, za každý zameškaný den se odváží 3 ban ječmene; jiná smlouva za 6 sila denně; rok pojmenován "Velká Enlilova bárka byla vysmolena". | [NATN 262 (P120960)](https://cdli.earth/P120960), [TMH NF 1-2, 024 (P134336)](https://cdli.earth/P134336) |
| **crowd_passersby** | Každý kolemjdoucí = jedno přísloví: "Kdo má stříbro, je šťastný; kdo má obilí, cítí se pohodlně; kdo má dobytek, nemůže spát." / "V městě bez psů je liškou pán." / "Osud je pes, chodí za člověkem." | [t.6.1.02](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.6.1.02), [t.6.1.03](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.6.1.03), [t.6.2.3](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.6.2.3) |

Nepřiřazená NPC (`anu`, `ninsun`, `ishtar`, `humbaba`, hrdinové eposu) jsou epické postavy; ty
se opírají o text eposu, ne o všední dokumenty.

## 5. Další nápady na nové postavy (všechny z přečtených tabulek)

- **Dlužník před svědky** – dluh oleje po sklizni, přísaha královým jménem, svědci (AUCT 2, 138, P103956).
- **Matka nalezence** – adopce kojence za 2 mniny vlny a stříbro (PBS 8/2, 107, P262227).
- **Prodej otrokyně** – za 10 šekelů, svědci: mlynář, zametač nádvoří (PBS 8/2, 157, P125408).
- **Sporný sluha před městským soudem** – strýc podává žalobu kvůli synovci (Adab, CDLJ 2002/2, P212356).
- **Zahradnice a pastýř** – spor Dumuzida a Enkimdua o ženicha a pastviny ([t.4.08.33](https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.4.08.33)).
- **Matka-hospodyně z Kaneše** – dluh stříbra, úrok podle nařízení kārum (P393107).
- **Přísežní svědci a soudce** – brána jako místo sporu (Nippur, Sippar, Adab).

## 6. Doporučený postup dál

1. Rozhodnout schéma `source` (viz bod 3) a zapsat do `ishtaria-protocol`.
2. Vybrat 3–5 příběhů, napsat je jako rozhodovací stromy (`status: draft`), lokalizovat
   `i18n/en.yaml` a `cs.yaml`, k nim přidat `knowledge.yaml` kartu s odkazem.
3. Zkusit ORACC z jiné sítě a doplnit dopisy s překladem.
4. Dialogy nejsou citace: překlady v CDLI/ETCSL mají své autory (např. Sasson, Michel,
   ETCSL/Oxford) – dialog je volná parafráze a karta uvede zdroj.
