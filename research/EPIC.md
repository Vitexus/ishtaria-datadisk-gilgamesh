# Epic of Gilgamesh — research corpus

Working materials for the Gilgamesh datadisk: the fullest recoverable text we can
assemble from open scholarly and public-domain witnesses, with citations for
every layer. Game dialogue and quest copy must **paraphrase** story events and
cite sources; do not paste the eBL bilingual edition into shipped i18n.

## Layout

| Path | What it is | Reuse |
| --- | --- | --- |
| [`epic/ebl/`](epic/ebl/) | Full **electronic Babylonian Library** Poem of Gilgameš (L/1/4): SB I–XII, OB, MB, NA chapters; Akkadian + English line tables | **Copyrighted** (George 2022 eBL). Attribute; quote sparingly |
| [`epic/ebl/README.md`](epic/ebl/README.md) | Inventory, DOI, retrieval notes (JSON API) | — |
| [`epic/sources/thompson-1928-twelve-tablets.txt`](epic/sources/thompson-1928-twelve-tablets.txt) | R. Campbell Thompson, *The Epic of Gilgamish* (London, 1928), continuous OCR | **Public domain (US)** |
| [`epic/sources/thompson-tablets/`](epic/sources/thompson-tablets/) | Same, split into Tablets I–XII | PD |
| [`epic/sources/thompson-1928-gilgamish.epub`](epic/sources/thompson-1928-gilgamish.epub) | Archive.org EPUB of Thompson 1928 | PD |
| [`epic/sources/jastrow-clay-1920-ob-gilgamesh.txt`](epic/sources/jastrow-clay-1920-ob-gilgamesh.txt) | Jastrow & Clay, Old Babylonian version (Yale, 1920; Project Gutenberg #11000) | PD |
| [`QUESTLINE.md`](QUESTLINE.md) | Planned multi-protagonist quest redesign mapped onto Tablet I–II | Design |

## Primary scholarly edition (prefer for accuracy)

**electronic Babylonian Library** — [library](https://www.ebl.lmu.de/library), corpus
[Poem of Gilgameš L/1/4](https://www.ebl.lmu.de/corpus/L/1/4), catalogue entry
[~3150 verses](https://www.ebl.badw.de/corpus).

> George, A. R. (2022). Poem of Gilgameš. With contributions by E. Jiménez and
> G. Rozzi. Translated by Anmar A. Fadhil, Andrew R. George and Wasim Khatabe.
> electronic Babylonian Library. https://doi.org/10.5282/ebl/l/1/4

Local mirror: **39 chapters, ~4221 line records** (SB 2683 + OB 882 + MB 569 + NA 87).
Retrieved from `GET https://www.ebl.lmu.de/api/texts/L/1/4/chapters/...` (SPA HTML
alone does not expose the edition).

## Public-domain continuous English (prefer for free reading copy)

- **Thompson 1928** — first essentially complete hexameter translation from BM
  tablets; OCR from Internet Archive `thompson-1928-gilgamesh`. Dated Assyyiology;
  use eBL when lines conflict.
- **Jastrow & Clay 1920** — Old Babylonian Pennsylvania / Yale tablets only (not
  the twelve-tablet Standard Babylonian poem).

Modern Penguin/World Classics translations (e.g. George 1999/2003 paperback) are
**not** copied here; they remain under copyright.

## Standard Babylonian outline (twelve tablets)

| Tablet | Arc (eBL / consensus) |
| ---: | --- |
| I | Prologue (walls of Uruk); tyranny; Aruru creates Enkidu; hunter at the water-hole; advice of the father; Gilgameš sends Šamḫat |
| II | Šamḫat civilizes Enkidu; bread and ale; journey to Uruk; wrestle / friendship with Gilgameš |
| III–V | Expedition against Ḫumbaba in the Cedar Forest |
| VI | Ištar; Bull of Heaven |
| VII–VIII | Death and mourning of Enkidu |
| IX–X | Gilgameš seeks Uta-napišti |
| XI | Flood; plant of youth lost |
| XII | Appendix: Enkidu and the Netherworld (Sumerian tradition grafted on) |

## Quest UI: excerpt + cuneiform

At the start of each playable quest, show:

1. A **localized** intro (EN/CS) spoken by the narrator, with subtitles — paraphrasing
   the relevant eBL lines (or a short PD Thompson quotation where licence allows).
2. **Akkadian** (normalized Latin transliteration) carved sign-by-sign as
   **Unicode cuneiform** (U+12000+, Noto Sans Cuneiform) on the clay tablet —
   ornament synced to the voice, not a second full translation.

### Hunter quest prologue — Aruru creates Enkidu (Tablet I)

Shipped keys: `quest.hunter.excerpt` / `quest.hunter.excerpt.akkadian`
(`the_hunter_and_the_wild_man`). The Czech/English intro retells the gods calling
Aruru and her fashioning Enkidu from clay (SB I, after the lament over Gilgameš’s
tyranny). Story authority for the lines remains **George 2022 eBL**
(`doi.org/10.5282/ebl/l/1/4`); character notes for Aruru as creatrix of clay:

- [The Goddess Aruru](http://www.holladaypaganism.com/goddesses/cyclopedia/a/ARURU.HTM)
  (Holladay Paganism cyclopedia) — Sumerian/Babylonian mother and birth goddess;
  washes her hands, pinches clay, creates Gilgameš’s double Enkidu after the image
  of Anu; cross-refs Mami / Ninḫursag and cites Pritchard *ANET*, Monaghan, Gray, etc.
  Use as a **secondary orientation** for titles and attributes, not as a substitute for
  the epic edition.

## Alignment with the planned datadisk story

The opening of the Standard Babylonian poem **is** the hunter–traps–Enkidu–father–
Šamḫat–three-day journey sequence. See [`QUESTLINE.md`](QUESTLINE.md) for how the
player embodies Hunter → Šamḫat → Enkidu → Gilgameš without contradicting the tablets.

## Refreshing the eBL mirror

```sh
# Example: one chapter
curl -sS 'https://www.ebl.lmu.de/api/texts/L/1/4/chapters/SB/I' -o /tmp/SB_I.json
# Convert with the same script used to build epic/ebl/*.md (see epic/ebl/README.md)
```

Do not commit regenerated eBL dumps without keeping the attribution block in each file.
