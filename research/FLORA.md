# Flora of Early Dynastic southern Mesopotamia (c. 2700 BCE)

What grew around Uruk and the alluvial plain of the Epic, and how the datadisk maps that onto
Ishtaria scenery IDs. Climate of the fourth–third millennia was wetter than today: marshes,
canebrakes and irrigated date orchards lined the channels (Pournelle 2003; Greco on marsh
resources; archaeobotany summarised in isotopic studies of ED Ur cattle).

## Documented plantscape

| Zone | Plants (historical) | Role |
| --- | --- | --- |
| River / canal banks | Date palm (*Phoenix dactylifera*), poplar, willow, tamarisk | Shade, fruit, timber, levee binding |
| Marshes / canebrakes (ĝeš-gi) | Common reed (*Phragmites*), sedges | Building, boats, mats; fish and fowl habitat |
| Irrigated fields | Barley (primary), emmer/wheat, flax, sesame, legumes | Staple economy; fields are `clear` (no wild spawn) |
| Gardens / orchards | Date, fig, pomegranate, grape (texts/archaeobotany) | Inside the clear mask or as props |
| Steppe beyond the irrigated belt | Sparse shrubs, C4 grasses | Dry grassland look, few trees |
| Cedar Forest (Lebanon, Epic geography) | Cedar of Lebanon and highland conifers | Only at the Cedar Forest place — not on the Uruk plain |

Barley–date irrigation and sheep/goat husbandry underpinned ED urbanisation (Early Dynastic
Period overview; Bulletin for Sumerian Agriculture). European oaks and deciduous Nature Kit
defaults are **anachronistic** on the southern plain.

## Mapping to Ishtaria asset IDs

Used by place `wildlife.flora` overlays (see protocol / ADR). Weights are relative.

### Uruk floodplain and channel banks

| Asset ID | Stands for | Notes |
| --- | --- | --- |
| `nature.tree_palmTall` | Date palm | Primary bank tree |
| `nature.tree_palmDetailedTall` | Date palm (detail) | Mix with tall |
| `nature.tree_palmShort` | Young / orchard palm | Near fields edge |
| `nature.tree_palmBend` | Wind-bent palm | Occasional |
| `quaternius.palm_1` | Date palm variant | Quaternius pack |
| `nature.plant_flatTall` | Reed / tall grass stand-in | Beside `nature.reed_clump` |
| `nature.plant_flatShort` | Low reed / sedge | Water margins |
| `hyper3d.tamarisk` | Tamarisk | Hyper3D shrub with a foliage crown, Uruk overlay only |
| `nature.plant_bushSmall` | Riverside shrub | Passable |
| `quaternius.bush_1` | Dry scrub | Steppe fringe |
| `quaternius.willow` | Willow / riverside tree | If present in catalog; else omit |

### Cedar Forest place

| Asset ID | Stands for |
| --- | --- |
| `nature.tree_pineTallA` / `nature.tree_pineTallB` / `nature.tree_pineTallC` | Cedar stand-ins (highland conifers) |
| `nature.tree_pineRoundA` | Understorey |

### Still missing (acquire or procedural)

| Need | Plan |
| --- | --- |
| Dedicated reed clump (`nature.reed_clump`) | Shipped in the Nature Kit path; passable |
| Dense bank + marsh overlays | Uruk `wildlife.density` 2.2 with heavy reed weights; Abu Tbeirah marsh fringe overlay |
| Tamarisk silhouette | Shipped as `hyper3d.tamarisk` (Hyper3D Rodin), with a foliage crown on the bare generated branches. |

## What the disk does *not* claim

- Global climate replacement for the whole Earth strip (still seed moisture + latitude).
- Crop meshes inside `clear` (tilled ground stays empty of wild flora by design).
- Exact species for every Nature Kit prop — palms and reeds are the fidelity target.
