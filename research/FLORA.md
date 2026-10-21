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
| Extra palm / reed / cedar variants | Import from 0 A.D. (below) — more visual diversity, not a replacement |

## 0 A.D. import checklist (flora)

Source: Wildfire Games `public` mod, **CC BY-SA 3.0** (attribute in datadisk / client credits).
Actors live under `art/actors/flora/` and `art/actors/props/flora/`; meshes under `art/meshes/`.
Debian `public.zip` ships only `.dae.cached.pmd` — export needs the **source Collada** art tree,
then Blender → `.glb` into client catalog (prefix `zeroad.`), register in `ishtaria-server/etc/world_objects.json`,
and add weights to place `wildlife.flora` overlays. Existing `nature.*` / `quaternius.*` / `hyper3d.*` stay.

Catalogue prefix is **`zeroad.`** (same as the bridges). Converter: `ishtaria-client/tools/zeroad-scenery.py`.

### Priority 1 — Uruk banks, marshes, orchards

| ID | Status | 0ad actor / mesh | Overlay hint |
| --- | --- | --- | --- |
| `zeroad.palm_date_a` … `_e` | **shipped** | `trees/palm_date.xml` | Uruk, abu_tbeirah — mix with `nature.tree_palm*` |
| `zeroad.palm_date_new_1` … `_4` | **shipped** | `trees/palm_date_new.xml` | Orchard / bank variants |
| `zeroad.reed_pond_lush` | **shipped** | `props/flora/reeds_pond_lush_*` | Marsh overlays |
| `zeroad.reed_beach_a` / `_b` | **shipped** | `props/flora/reeds_beach.xml` | Channel margins |
| `zeroad.papyrus_1` / `_2` | **shipped** | `props/flora/papyrus.xml` | Marsh / lagoon |
| `zeroad.cattails` | **shipped** | `props/flora/cattails.xml` | Pond edges |
| `zeroad.tamarix_a` | **shipped** (trunk) | `trees/tamarix.xml` | Beside `hyper3d.tamarisk` |
| `zeroad.poplar_lombardy` | **shipped** | `lombardy_poplar_01` | Uruk channel / orchard fringe |
| `zeroad.bush_desert_a` | **shipped** | `bush_dese_a` | Dry fringe, Susa, Cedar understorey |
| `zeroad.willow_a` | **shipped** | `trees/willow_a.xml` | Uruk channel fringe |
| `zeroad.fig_a` / `fig_b` | **shipped** (trunk+canopy) | `trees/fig.xml` | Uruk orchard |
| `zeroad.fig_top_a` / `_b` | **shipped** (canopy only) | fig tops | light understorey |
| `zeroad.cretan_date_01` … `_04` | **shipped** | `palm_cretan_date.xml` | Uruk light mix |
| `zeroad.reed_giant` | **shipped** | `reeds_giant.xml` (papyrus + giantcane) | Marsh overlays |
| `zeroad.aleppo_pine_1` … `_8` | **shipped** | full Aleppo set | Cedar Forest |
| `zeroad.palm_date_fruit_1` / `_2` | **shipped** | fruiting date palms | Uruk orchard |
| `zeroad.palm_dead_1` … `_3` | **shipped** | dead date trunks | Uruk light mix |
| `zeroad.cedar_atlas_dead_1` / `_2` | **shipped** | dead cedar skin | Cedar Forest |
| `zeroad.poplar_lombardy_dead` | **shipped** | dead poplar | Uruk channel |

### Priority 2 — Cedar Forest, highlands, Susa / Iranian fringe

| ID | Status | 0ad actor | Overlay hint |
| --- | --- | --- | --- |
| `zeroad.cedar_atlas_1` … `_3` | **shipped** | `trees/cedar_atlas.xml` | `cedar_forest` — prefer over generic pine |
| `zeroad.cypress_med` / `_tall` | **shipped** | mediterranean cypress | Susa, Cedar Forest fringe |
| `zeroad.acacia_01` | **shipped** | `trees/acacia` trunk | Susa plain |
| `zeroad.aleppo_pine_1` … `_3` | **shipped** | `trees/aleppo_pine.xml` | Cedar Forest understorey |
| `zeroad.olive_01` … `_03` | **shipped** | `trees/olive.xml` | Byblos / Levant gardens |
| `zeroad.palm_doum_1` / `_2` | **shipped** | `trees/palm_doum.xml` | Memphis / southern fringe |

### Priority 3 — skip or later (wrong biome / low value)

| 0ad actor | Why skip for ED Mesopotamia |
| --- | --- |
| `palm_tropical*`, `palm_royal`, `palm_nipa`, `palm_areca` | Tropical, not alluvial ED |
| `palm_palmyra`, `palm_senegal_date` | Wrong region; optional far-south pins only |
| Oak / temperate / snow pine / tropic bush biomes | Anachronistic on the Uruk plain |
| Berry bushes, lavender, poppy (temperate deco) | Not the fidelity target |
| Decals only (`decal_palms.xml`, …) | Useful later as ground stamps; not first mesh import |

### Terrain ground textures (not flora props)

Heightmap geometry stays the disk’s PGM. Optional **surface** albedos from 0ad
`art/terrains/biome-persia/` and `art/textures/terrain/types/` (`desert_*_persia*`,
`persia/dirt_plants_01`, grassland / farmland / rock). Same CC BY-SA; convert DDS/PNG for the
client terrain shader. Detail: `research/LANDSCAPE.md` (0 A.D. terrain textures).

### Import order (flora)

1. ~~`zeroad.palm_date*` + reeds / papyrus / cattails~~ — done
2. ~~`zeroad.tamarix`, `poplar_lombardy`, `bush_desert`~~ — done
3. ~~`zeroad.cedar_atlas_*` + cypress / acacia~~ — done (`cedar_forest`, Susa overlays)
4. ~~Fig / willow / olive / Aleppo pine / doum / Cretan / reed_giant~~ — done

## What the disk does *not* claim

- Global climate replacement for the whole Earth strip (still seed moisture + latitude).
- Crop meshes inside `clear` (tilled ground stays empty of wild flora by design).
- Exact species for every Nature Kit prop — palms and reeds are the fidelity target.
- That 0ad meshes replace Kenney/Quaternius — they **add** catalog weight for variety.
