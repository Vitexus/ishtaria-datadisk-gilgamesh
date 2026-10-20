# eBL Poem of Gilgameš (research mirror)

Local working copies of the [electronic Babylonian Library](https://www.ebl.lmu.de/) edition of the *Poem of Gilgameš* (corpus **L/1/4**), retrieved for Ishtaria datadisk research.

## Citation (George 2022 eBL)

Primary citation for the Standard Babylonian poem in eBL:

> George, A. R. (2022). Poem of Gilgameš. With contributions by E. Jiménez and G. Rozzi. Translated by Anmar A. Fadhil, Andrew R. George and Wasim Khatabe. electronic Babylonian Library. https://doi.org/10.5282/ebl/l/1/4

Each tablet/chapter file repeats the chapter-specific “How to cite” block from the eBL record (editor, revisors, translators, year).

- Corpus intro: <https://www.ebl.lmu.de/corpus/L/1/4>
- Catalogue: <https://www.ebl.badw.de/corpus>
- DOI: <https://doi.org/10.5282/ebl/l/1/4>

## License / attribution

**eBL editions must be attributed and must not be treated as public domain.**

The Akkadian reconstructions and modern translations hosted by eBL are scholarly editions (principally A. R. George 2022, with revisors and translators named per chapter). They are copyrighted research products of the eBL project and its authors. This directory is a research convenience mirror for the Gilgamesh datadisk: quote sparingly, always cite George/eBL, and do not redistribute the bilingual edition as open-content game text.

## Retrieval note

The public chapter URLs (`/corpus/L/1/4/SB/I`, etc.) are a JavaScript SPA. Plain HTTP/WebFetch often returns only the shell (“electronic Babylonian Library”). The line editions here were obtained from the eBL JSON API:

```
GET https://www.ebl.lmu.de/api/texts/L/1/4
GET https://www.ebl.lmu.de/api/texts/L/1/4/chapters/{SB|OB|MB|NA}/{name}
```

Normalized Akkadian (word separators collapsed; hemistichs marked `‖`) and English (`#tr.en`) are tabulated per line. Editorial gap notes from the eBL record are kept as italic rows.

## Retrieved chapters

## Standard Babylonian (SB) — twelve tablets

| File | Chapter | Opening / title | Lines |
| --- | --- | --- | ---: |
| [`SB_I.md`](SB_I.md) | I | [He Who Saw The Deep, The] Foundation Of The Country | 300 |
| [`SB_II.md`](SB_II.md) | II | [Enkidu] Was Sitting Before Her, […] … | 187 |
| [`SB_III.md`](SB_III.md) | III | ‘[Come Back In Safety] To [The Quay Of] Uruk! | 209 |
| [`SB_IV.md`](SB_IV.md) | IV | [At Twenty] Leagues They Broke Bread | 175 |
| [`SB_V.md`](SB_V.md) | V | They Stood Marvelling At The Forest | 274 |
| [`SB_VI.md`](SB_VI.md) | VI | He Washed His Matted Hair, He Cleaned His Equipment | 183 |
| [`SB_VII.md`](SB_VII.md) | VII | ‘My Friend, For What Reason Were The Great Gods Taking Counsel?’ | 219 |
| [`SB_VIII.md`](SB_VIII.md) | VIII | At The Very First Light Of Dawn | 206 |
| [`SB_IX.md`](SB_IX.md) | IX | For His Friend Enkidu Gilgameš | 137 |
| [`SB_X.md`](SB_X.md) | X | Šiduri Was An Ale-Wife Who Lived By The Sea-Shore | 325 |
| [`SB_XI.md`](SB_XI.md) | XI | Gilgameš Spoke To Him, To Ūta-Napišti The Far-Away | 329 |
| [`SB_XII.md`](SB_XII.md) | XII | “Today, Had I Only Left The Ball In The Carpenter’s Workshop! | 139 |

_Subtotal: 2683 lines across 12 chapters._

## Old Babylonian (OB)

| File | Chapter | Opening / title | Lines |
| --- | --- | --- | ---: |
| [`OB_II.md`](OB_II.md) | II | Gilgameš Arose To Reveal A Dream | 145 |
| [`OB_III.md`](OB_III.md) | III | ‘[…] Is Gripped, My Friend, The Body Palpitates | 219 |
| [`OB_UM.md`](OB_UM.md) | UM | ‘[Why, My Friend, Did Your] Eyes [Brim With Tears,] | 16 |
| [`OB_Schøyen₁.md`](OB_Schøyen₁.md) | Schøyen₁ | ‘[I] Have Acquired A Friend, The Counsellor [That I Kept] Seeing [In Dreams,] | 13 |
| [`OB_Schøyen₂.md`](OB_Schøyen₂.md) | Schøyen₂ | Gilgameš Was Lying Down At Rest | 94 |
| [`OB_Schøyen₃.md`](OB_Schøyen₃.md) | Schøyen₃ | “[My Friend, I Have Seen A Third (Dream).] | 47 |
| [`OB_Nippur.md`](OB_Nippur.md) | Nippur | ‘My Friend, We Have Come Close To The Forest | 26 |
| [`OB_Harmal₁.md`](OB_Harmal₁.md) | Harmal₁ | ‘Go Up On To The Mountain Crag | 21 |
| [`OB_Harmal₂.md`](OB_Harmal₂.md) | Harmal₂ | […] | 59 |
| [`OB_Ishchali.md`](OB_Ishchali.md) | Ishchali | […] Ḫuwawa | 47 |
| [`OB_IM.md`](OB_IM.md) | IM | […] | 45 |
| [`OB_VA+BM.md`](OB_VA+BM.md) | VA+BM | […] Wild Bulls, The Aurochs Of […,] | 87 |
| [`OB_CUNES.md`](OB_CUNES.md) | CUNES | Enkidu’s Legs Grew Weary, Whose [Herd Was] On [The Move] | 27 |
| [`OB_SM.md`](OB_SM.md) | SM | […] … | 36 |

_Subtotal: 882 lines across 14 chapters._

## Middle Babylonian (MB)

| File | Chapter | Opening / title | Lines |
| --- | --- | --- | ---: |
| [`MB_Nippur.md`](MB_Nippur.md) | Nippur | ‘[Let] Them Summon [Aruru], The Great [One,]	 | 19 |
| [`MB_Ur.md`](MB_Ur.md) | Ur | At The Very First Light Of Dawn | 69 |
| [`MB_Boğ₁.md`](MB_Boğ₁.md) | Boğ₁ | [The Harlot Opened Her Mouth,] | 92 |
| [`MB_Boğ₂.md`](MB_Boğ₂.md) | Boğ₂ | ‘[…] … [My] Friend […]	 | 65 |
| [`MB_Boğ₃.md`](MB_Boğ₃.md) | Boğ₃ | […] … […] | 8 |
| [`MB_Emar₁.md`](MB_Emar₁.md) | Emar₁ | […] Enkidu [Opened] His Mouth [To Speak,] | 10 |
| [`MB_Emar₂.md`](MB_Emar₂.md) | Emar₂ | ‘[Doorway And Throne Shall] Kiss [Your] Hands | 55 |
| [`MB_Megiddo.md`](MB_Megiddo.md) | Megiddo | […] … […] | 40 |
| [`MB_Priv₁.md`](MB_Priv₁.md) | Priv₁ | [The Harlot Said To Him, To Ea (Enkidu):] | 94 |
| [`MB_Ug₁.md`](MB_Ug₁.md) | Ug₁ | He Who Saw The Deep, The Foundation Of The Country | 39 |
| [`MB_Ug₂.md`](MB_Ug₂.md) | Ug₂ | […] … And […] | 78 |

_Subtotal: 569 lines across 11 chapters._

## Neo-Assyrian (NA) fragments

| File | Chapter | Opening / title | Lines |
| --- | --- | --- | ---: |
| [`NA_x.md`](NA_x.md) | x | […] … […] | 20 |
| [`NA_y.md`](NA_y.md) | y | ‘[Only The Gods] Have Dwelled For [Ever In The Sunlight.] | 67 |

_Subtotal: 87 lines across 2 chapters._


## Totals

| Group | Chapters | Approx. lines |
| --- | ---: | ---: |
| Standard Babylonian | 12 | 2683 |
| Old Babylonian | 14 | 882 |
| Middle Babylonian | 11 | 569 |
| Neo-Assyrian | 2 | 87 |
| **All** | **39** | **4221** |

eBL metadata reports about **3150** verses for the composition as a whole (`approximateVerses: true`); line counts above are eBL line *records* (including fragmentary and provisional numbers), not a claim of a complete continuous poem.

## Raw JSON

Unprocessed eBL chapter payloads used to build the markdown tables live in [`json/`](json/) (same attribution and copyright as the markdown mirror).
