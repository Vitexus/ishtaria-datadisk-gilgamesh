# Jak přispět / How to contribute

*Česky nejdřív, English below.*

Děkujeme, že zvažuješ pomoc. Datadisk **Epos o Gilgamešovi** je soubor dat (texty, postavy, dialogy,
místa), ne program. **Programovat se nemusíš umět.** Nejcennější je, co sami neumíme posoudit: odborná
správnost. Hra je v raném stadiu; funguje svět, Uruk, dialogy a první úkoly, ne všechno je hotové.

## 1. Co můžeš udělat

| Co | Kde to je | Příklad |
| --- | --- | --- |
| Zkontrolovat text a dialogy proti edicím eposu | `dialogues/`, `quests/`, `i18n/en.yaml`, `i18n/cs.yaml`, `research/EPIC.md` | „Tato replika neodpovídá tabulce VI, 10–12.“ |
| Napsat nebo opravit kodex postavy a události | `lore/epic.yaml` (texty v `i18n/*.yaml`, klíče `lore.*`) | Gilgameš, Enkidu, Ištar, Šamḫat |
| Karta „řekni mi o sobě“ (obrázek, krátký text, odkaz) | `knowledge.yaml`, `i18n/*.yaml` (`knowledge.*`) | Utnapištim |
| Posoudit Uruk, chrámy, zikkurat, město | `research/CITY.md`, `ZIGGURATS.md`, `STRUCTURES_PROPOSAL.md`, `places/` | Eanna, brány, hradby |
| Jména, titulatura, přepis, akkadské nebo sumerské repliky | `i18n/*.yaml`, `npcs/` | `Šamḫat`, `Ištar` vs. `Inanna` |
| Flóra, fauna, každodennost raně dynastického jihu | `research/FLORA.md`, `FAUNA.md`, `places/*.yaml` (část `wildlife`) | Co tam opravdu rostlo |
| Překlad do dalšího jazyka | `i18n/` (zkopíruj `en.yaml`) | Němčina, arabština, … |

Nejmenší užitečný příspěvek: **jedna připomínka k jedné scéně** s odkazem na zdroj.

## 2. Tři cesty, od nejjednodušší

1. **Poznámka.** Otevři *issue* na https://git.vitexsoftware.com/Ishtaria/ishtaria-datadisk-gilgamesh
   (nebo napiš správci). Uveď: kde (soubor nebo scéna), co je špatně, **zdroj** (edice, tabulka a řádek,
   článek, strana). Opravu zapíšeme my a uvedeme tě.
2. **Přímá úprava.** Uprav soubor a pošli *pull request* (viz níže). Chyba v textu se opravuje
   přímo v `i18n/en.yaml` a `i18n/cs.yaml`.
3. **Nový obsah.** Napiš kodex, kartu nebo scénu. Domluv se předem v issue, ať se nedělá dvakrát.

## 3. Úprava souboru

* Texty hry jsou **jen** v `i18n/en.yaml` (zdrojová řeč) a `i18n/cs.yaml`. Soubory `lore/`, `dialogues/`,
  `quests/`, `npcs/` a `places/` na ně odkazují **klíči** (`lore.gilgamesh`). **Klíče nepřejmenovávej.**
* Dlouhý text se píše jako složený blok:

  ```yaml
  lore.gilgamesh: >
    Gilgameš, král Uruku, ze dvou třetin bůh a z jedné třetiny člověk. …
  ```

* Mění-li se význam, uprav **obě** řeči (`en` a `cs`). Chybí-li ti jedna, napiš aspoň poznámku.
* Řekni, **čím se opíráš**: do `research/` (krátký odstavec se zdrojem) nebo do popisu změny.
  Kde se odborníci rozcházejí, napiš to, nevybírej mlčky.
* **Autorská práva:** nevkládej texty z cizích překladů ani edic, které nejsou volné. Použij vlastní slova
  a cituj. Základ eposu je volný překlad N. K. Sanderse. Krátké citace z eBL a jiných edic jsou v pořádku
  se zdrojem.

### Kontrola

```sh
python3 ../ishtaria-protocol/tests/validate_datadisk.py .
```

Vyžaduje `python3-jsonschema` a `python3-yaml`, repozitář `ishtaria-protocol` vedle tohoto. Zkontroluje
schéma, odkazy a média. Správnost obsahu tahle kontrola neposoudí, to děláš ty.

### Pull request

1. Vytvoř si účet na https://git.vitexsoftware.com (Forgejo) a udělej *fork* repozitáře.
2. Vytvoř větev, proveď změnu, spusť kontrolu a potvrď (*commit*) s popisnou zprávou
   (např. `fix(i18n): Enkidu's lament follows tablet VIII`).
3. Otevři *pull request*. Napiš, co jsi změnil, podle čeho a co jsi nemohl ověřit.

Nechceš-li Git, pošli změnu jako text nebo `diff`; správce ji zapracuje.

## 4. Uvedení jména

Každý, kdo přispěje, se může zapsat do souboru [`CONTRIBUTORS`](CONTRIBUTORS): jméno, přezdívka nebo jen
instituce, jak chceš. Zapíšeme tě po první přijaté úpravě nebo připomínce a pošleme ti potvrzení pro
životopis, pokud o ně požádáš. Dohodnuté uvedení lze kdykoli změnit nebo vzít zpět.

## 5. Na rovinu

* Část podkladů (modely, portréty, hlasy) vznikla s pomocí nástrojů umělé inteligence a kód s Claude Code.
  Je to uvedeno v `datadisk.yaml` (`attribution`) a v souboru `CONTRIBUTORS`. Právě proto potřebujeme
  odborné oko.
* Odborné věci rozhodují odborníci. Chybu opravíme, nebudeme ji hájit.
* Hra je pro hráče, kteří chtějí zažít příběh; není to učebnice. Zjednodušení (například zkrácené cesty)
  jsou záměrná a označená, ale fakta mají být správně.

## 6. Licence

Příspěvky patří pod **CC BY-SA 4.0**, jako celý disk (`datadisk.yaml`). Hudba a některé modely mají vlastní
licence uvedené v `attribution`. Odesláním příspěvku s tím souhlasíš.

---

# How to contribute

Thank you for considering it. The **Epic of Gilgamesh** disk is data (texts, characters, dialogue, places),
not a program, and **you need no programming**. What we most need is what we cannot judge ourselves:
scholarly accuracy. The game is early: the world, Uruk, dialogue and the first quests work; not all of it
is finished.

## 1. What you can do

* Check text and dialogue against editions of the epic (`dialogues/`, `quests/`, `i18n/*.yaml`, `research/EPIC.md`).
* Write or correct codex entries (`lore/epic.yaml`, texts under the keys `lore.*` in `i18n/*.yaml`).
* Write a "tell me about yourself" card (`knowledge.yaml`, `knowledge.*` keys).
* Review Uruk, the temples, the ziggurat and the city (`research/CITY.md`, `ZIGGURATS.md`, `places/`).
* Names, titles, transliteration, Akkadian or Sumerian lines (`i18n/*.yaml`, `npcs/`).
* Flora, fauna and daily life of the Early Dynastic south (`research/FLORA.md`, `FAUNA.md`).
* Translate to another language: copy `i18n/en.yaml`.

The smallest useful contribution is **one remark on one scene** with a source.

## 2. Three ways, easiest first

1. **A remark:** open an issue at https://git.vitexsoftware.com/Ishtaria/ishtaria-datadisk-gilgamesh with the
   file or scene, what is wrong and **the source** (edition, tablet and line, article, page).
2. **A direct edit:** change the file and send a pull request.
3. **New content:** agree on it in an issue first.

## 3. Editing

* Game text lives **only** in `i18n/en.yaml` (source language) and `i18n/cs.yaml`; the other files refer to it
  by **key** (`lore.gilgamesh`). **Do not rename keys.** Write long text as a folded block (`key: >`).
* If the meaning changes, update **both** languages, or at least leave a note for the missing one.
* State **what you rely on** (a short paragraph in `research/` or the pull request). Where scholars disagree, say so.
* **Copyright:** do not paste text from non-free translations or editions. Use your own words and cite.
  The base is the public-domain translation of N. K. Sanders; short quotations from eBL and other editions are
  welcome with a source.

Check your change (needs `python3-jsonschema`, `python3-yaml` and `ishtaria-protocol` next to this repository):

```sh
python3 ../ishtaria-protocol/tests/validate_datadisk.py .
```

This checks schema, references and media, not whether the content is right.

For a pull request: make an account on https://git.vitexsoftware.com (Forgejo), fork, branch, change, check,
commit with a descriptive message and open the pull request saying what you changed, on what basis and what you
could not verify. Without Git, send the change as text or a diff; the maintainer will apply it.

## 4. Credit

Contributors may be listed in [`CONTRIBUTORS`](CONTRIBUTORS) by name, pseudonym or institution only, as they
like, after the first accepted change or remark. A confirmation for your CV on request; the credit can be
changed or withdrawn at any time.

## 5. Honestly

Part of the models, portraits and voices was made with AI tools, and the code with Claude Code (stated in
`datadisk.yaml` and `CONTRIBUTORS`); this is why expert eyes are needed. Scholars decide scholarly questions;
errors are corrected, not defended. The game is for players who want to live a story, not a textbook;
simplifications are deliberate and marked, but facts should be right.

## 6. Licence

Contributions are **CC BY-SA 4.0**, like the whole disk. Music and some models carry their own licences
listed in `attribution`. By submitting you agree.
