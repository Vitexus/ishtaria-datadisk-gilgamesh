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
| Lion (Epic) | Mountain lion already in disk models-src; wild spawn optional later |

## Cedar Forest / wilderness of the Epic

Higher density of deer/stag and wolf; no sheep flocks. Lions as story NPCs / creatures remain
separate from passable scenery fauna.
