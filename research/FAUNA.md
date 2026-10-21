# Fauna of Early Dynastic southern Mesopotamia (c. 2700 BCE)

Animals of the Uruk plain and the Epic’s wild places, mapped onto Ishtaria `world_fauna.json`
IDs for place `wildlife.fauna` overlays.

## Historical picture

Temple and palace herds were dominated by **sheep and goats**, with **cattle** secondary
(isotopic work on ED III Ur cattle; administrative texts). **Pigs** and hunted game appear more
in the archaeological record than in palace accounts. Marsh economy: **fish** and **fowl**
(Greco; Pournelle). Wild game of the steppe and river edges included **gazelle**, **onager**
(wild ass), and predators such as **lion** and **fox** (zooarchaeology and later literary
tradition; the Epic’s lions and Enkidu’s companion animals).

**Horses** and **camels** were not everyday ED southern Mesopotamian stock in the way sheep,
goats, cattle and donkeys were. The disk’s Uruk overlay therefore **excludes** `animal.horse`,
`animal.white_horse` and alpaca as plain wildlife (donkeys stay).

Tropical reef fish IDs in the global catalog are wrong for the Euphrates; the overlay keeps
freshwater-leaning IDs only where aquatic spawn applies.

## Mapping to Ishtaria asset IDs

### Domestic / herded (near settlements — prefer farm pastures; wild overlay uses lightly)

| Asset ID | Historical role |
| --- | --- |
| `animal.sheep` | Primary flock animal |
| `animal.goat` | Primary flock animal (Hyper3D mesh) |
| `animal.pig` | Village / scavenger pig |
| `animal.cow` / `animal.bull` | Draught and sacrifice herds |
| `animal.donkey` | Pack and plough |
| `animal.chicken` | Fowl stand-in (later chicken; acceptable village bird) |
| `animal.shiba_inu` / `animal.husky` | Dog stand-ins (no dedicated ED dog) |

### Wild land (outside `clear`, away from settlement cores)

| Asset ID | Historical role |
| --- | --- |
| `animal.gazelle` | Gazelle (Hyper3D mesh; Uruk overlay) |
| `animal.onager` | Onager, wild ass (Hyper3D mesh; Uruk overlay) |
| `animal.deer` / `animal.stag` | Extra ungulate; deer remains a highland stand-in |
| `animal.lizard` | Desert lizard (Hyper3D mesh; banks and steppe) |
| `animal.turtle` | Euphrates softshell turtle (Hyper3D mesh; on land) |
| `animal.pigeon` | Rock dove (Hyper3D mesh; city and fields) |
| `animal.falcon` | Saker-type falcon (Hyper3D mesh; rarer) |
| `animal.duck` | Marsh duck (Quaternius Bird mesh; banks and Abu Tbeirah) |
| `animal.goose` | Goose (Sketchfab “goos” by polarvoid, CC BY; banks and marshes) |
| `animal.fox` | Fox |
| `animal.wolf` | Wolf / jackal pressure on flocks |

### Aquatic (ED channel / marshes — patch water)

| Asset ID | Notes |
| --- | --- |
| `fish.flatfish` | Broad freshwater stand-in |
| `fish.turbot` | Larger river fish |
| `fish.tuna` | Large fish stand-in (not marine fidelity) |
| `fish.goldfish` / `fish.koi` / `fish.carp-like` | Prefer non-reef IDs only |

Avoid reef ornamentals (`clownfish`, `tang`, `lionfish`, …) in the Uruk overlay.

### Still missing

| Need | Plan |
| --- | --- |
| Gazelle / onager / goat mesh | Shipped: `animal.gazelle`, `animal.onager`, `animal.goat` (Hyper3D Rodin, client `assets/hyper3d/ed/`). Poly Pizza had no gazelle or onager. |
| Falcon / pigeon | Shipped: `animal.falcon`, `animal.pigeon` (Hyper3D). The Poly Pizza pigeon is a cartoon character and was not used. |
| Waterfowl | Shipped: `animal.duck` (Quaternius Bird, CC0), `animal.goose` (polarvoid on Sketchfab, CC BY). |
| Lion (Epic) | Mountain lion already in disk models-src; wild spawn optional later; 0ad lion below as scenery variant |
| Extra herd / predator / bird silhouettes | Import from 0 A.D. (below) — diversity beside existing IDs |

## 0 A.D. import checklist (fauna)

Source: Wildfire Games `public` mod, **CC BY-SA 3.0**. Actors under `art/actors/fauna/`;
templates under `simulation/templates/gaia/fauna_*.xml`. Same pipeline as flora: source `.dae` →
`.glb`, catalog prefix **`zeroad.`**, register in `ishtaria-server/etc/world_fauna.json`, weight in
`wildlife.fauna`. Passable scenery with **Idle/Walk** clips from `tools/zeroad-fauna-anim.py`
(do not overwrite with the flora-only `zeroad-scenery.py`). Existing `animal.*` / Hyper3D IDs
stay; 0ad entries are **additional variants**.

Note: `gazelle.xml` uses `skeletal/deer_mesh.dae` with a gazelle skin — still a useful second look.

### Priority 1 — Uruk plain / Epic game

| ID | Status | Beside existing | Overlay hint |
| --- | --- | --- | --- |
| `zeroad.gazelle` | **shipped** (Idle/Walk) | `animal.gazelle` | Uruk / hunter water-hole |
| `zeroad.goat` | **shipped** (Idle/Walk) | `animal.goat` | Settlements |
| `zeroad.sheep` | **shipped** (Idle/Walk) | `animal.sheep` | Pasture fringe |
| `zeroad.cow` / `zeroad.bull` | **shipped** (Idle/Walk) | `animal.cow` / `animal.bull` | Herds |
| `zeroad.donkey` | **shipped** (Idle/Walk) | `animal.donkey` | Paths |
| `zeroad.pig` | **shipped** (Idle/Walk) | `animal.pig` | Village edge |
| `zeroad.chicken` | **shipped** (Idle/Walk) | `animal.chicken` | Settlement |
| `zeroad.fox` | **shipped** (Idle/Walk) | `animal.fox` | Steppe |
| `zeroad.wolf` | **shipped** (Idle/Walk) | `animal.wolf` | Cedar Forest / wild |
| `zeroad.lion` / `zeroad.lioness` | **shipped** Idle/Walk (rare) | story mountain lion | Cedar Forest fringe |
| `zeroad.deer` | **shipped** (Idle/Walk) | `animal.deer` | Cedar Forest |
| `zeroad.boar` | **shipped** (Idle/Walk) | — | Forest edge |
| `zeroad.mastiff` | **shipped** (Idle/Walk=run) | settlement dog | Hunter water-hole, Byblos, Memphis |
| `zeroad.hawk` / `crow` / `seagull` | **shipped** (`flying`, altitude 14–22 m; Idle=glide, Walk=flight) | aerial wander | Uruk, hunter, lagoon |

### Priority 2 — marshes, rivers, distant pins

| ID | Status | Notes |
| --- | --- | --- |
| `zeroad.crocodile` | **shipped** (Idle/Walk) | Abu Tbeirah, Memphis — rare weight |
| `zeroad.camel` | **shipped** (Idle/Walk) | Susa / Iranian fringe only |
| `zeroad.horse_persian` | **shipped** (Idle/Walk) | Susa rare — not ED Uruk flocks |
| `zeroad.zebu` | **shipped** (Idle/Walk) | Memphis / southern cattle |
| `zeroad.fish_generic` | **shipped** (aquatic; overlay YAML weight is ignored — global water layer only) | Marsh / Memphis water |

### Priority 3 — skip for this disk

| 0ad actor | Why |
| --- | --- |
| Polar / arctic wolf, polar bear, walrus, whale, shark | Wrong climate |
| Giraffe, zebra, rhino, wildebeest, tiger, hippo (except maybe far African pins) | Wrong fauna province for Gilgamesh Earth focus |
| Asian/African war elephants | Military / later; not ED Uruk scenery |
| `dragon.xml`, `pig_flaming.xml` | Fantasy / joke |
| Peacock | Anachronistic palace vanity — optional garden prop only, not wild overlay |

### Onager gap

0ad has **no dedicated onager**. Keep `animal.onager` (Hyper3D). Do not remap donkey/horse to onager.

### Import order (fauna)

1. `zeroad.gazelle`, `zeroad.goat`, `zeroad.sheep`, cattle, `zeroad.donkey`, `zeroad.pig`
2. `zeroad.fox`, `zeroad.wolf`, `zeroad.deer`, `zeroad.boar`
3. `zeroad.lion` / `zeroad.lioness` (rare), birds (`hawk`, `crow`, chicken)
4. Marsh / pin-specific (`crocodile`, seagull, fish) and Iranian fringe (`camel`, `horse_persian`) only where places ask for them

## Cedar Forest / wilderness of the Epic

Higher density of deer/stag and wolf; no sheep flocks. Lions as story NPCs / creatures remain
separate from passable scenery fauna; `zeroad.lion` may later feed a rare wild overlay or Mashu
approach without replacing the Epic fight creature.
