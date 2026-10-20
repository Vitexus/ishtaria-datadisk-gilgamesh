# Questline — finite indie Epic of Gilgamesh

Design for the Gilgamesh datadisk as a **short, polished narrative game** for players
interested in ancient Iraq / Mesopotamia. Story authority remains the eBL Poem of
Gilgameš (George 2022); see [`EPIC.md`](EPIC.md). Gameplay goal: playfully introduce
the epic, not retain players for dozens of hours.

**End of the game** = end of Gilgameš’s search for eternal life. **Unlike the epic**,
eternal life is **obtainable** (winning ending). Losing the plant / accepting mortality
remains a secondary ending.

## Principle — many hands, one epic

| Playable body | When control starts | When control ends |
| --- | --- | --- |
| **Hunter** (`ṣayyādu`) | New character / world start | After finding wild Enkidu with Šamḫat |
| **Šamḫat** | Handover after Hunter quest | After Enkidu is human and presented in Uruk |
| **Enkidu** | After Šamḫat presents him | After friendship wrestle with Gilgameš |
| **Gilgameš** | After brothers are sealed | Rest of the epic through immortality ending |

Each body has **one primary quest** (stage machine). Completing it triggers a
**character swap** (`set_playable`). Story flags carry over.

At **quest start**, show a short EN/CS paraphrase + Akkadian on the clay tablet UI.

## Quest checkpoint (death / fail)

If the **player dies** or a **quest fails** (e.g. companion Šamḫat dies on the road),
the game does **not** end with a permanent memorial. Instead:

1. Reset the **active** quest to its restart point (`fail_restart` on the current stage,
   else the quest’s `start_stage` + `start_place`).
2. Teleport the player there; restore health / stamina.
3. Keep completed earlier quests and story flags that belong to finished chapters.

Example: hunter dies while escorting Šamḫat, or Šamḫat dies → restart at **Uruk**
(`seek_shamhat` / temple), not at the water-hole.

During the active Gilgamesh questline, permanent death is replaced by this restart.
After the epilogue, normal world rules apply.

## Geography and travel

| Beat | Place | Notes |
| --- | --- | --- |
| Hunter start | Steppe water-hole ~3 days from Uruk | Walkable |
| Uruk hub | City, temples, palace | Walkable |
| Cedar Forest | ~953 km WNW of Uruk | **Abstracted travel** (`teleport_place`) |
| Mashu → Dilmun | Epic road | Abstracted travel / ferry dialogues |

Long epic distances are never walked in real time.

## Mandatory middle epic (varied gameplay)

These chapters are **required** (fidelity + variety):

| Beat | Gameplay mode |
| --- | --- |
| Cedar Forest | Prepare in Uruk (Ninsun) + teleport + explore cedars |
| Humbaba | Multi-phase story boss with Enkidu |
| Ištar | Dialogue / social conflict in the temple |
| Bull of Heaven | Second boss, different rhythm |
| Death of Enkidu | Ritual / memorial; motivation for immortality |

## Quest A–C — status

- **A Hunter** — done (snares, father, Gilgameš, Šamḫat escort).
- **B Šamḫat** — done (love minigame → civilization → present).
- **C Enkidu** — done (face / wrestle / brothers); then **handover to Gilgameš PC**.

## Quest D onward — Gilgameš

1. Become Gilgameš (`set_playable`); Enkidu returns as NPC companion.
2. Cedar Forest journey → Humbaba.
3. Ištar → Bull of Heaven.
4. Death of Enkidu.
5. Journey to Utnapishtim (abstracted).
6. Immortality: **win** = keep the plant / gain eternal life + epilogue; **epic path** =
   lose plant / accept mortality + shorter epilogue.

## Implementation order

1–11. Hunter → Šamḫat → Enkidu friendship — **done** (see git history / prior notes).
12. Design lock (this file + README) — **done**.
13. Quest checkpoint on death / escort fail — **done**.
14. Gilgameš as PC + Cedar quest chain + travel teleport — **done**.
15. Humbaba, Ištar, Bull, Enkidu’s death — **done** (flourish set-pieces; chains to immortality quest).
16. Immortality journey + endings + client epilogue — **done** (datadisk 0.2.22;
    keep plant → `eternal_life` + Uruk palace; snake → `lose_plant` + return quest +
    Ninsun walls; clay tablet; vigil resume; all 161 NPC spoken lines EN+CS).

Smoke (2026-10-20): staged disk on `ishtaria_gilgamesh_dev` world `localhost`
loads `gilgamesh` **0.2.22**; new player auto-starts `the_hunter_and_the_wild_man`.
After a content bump, set `world_datadisks.version` to the new version and
`sha256 = NULL`, then restart with `ISHTARIA_DATADISK_DIR=build/datadisks`.

## Licence reminder

Ship **original** EN/CS quest prose. Cite eBL/George for Akkadian lines shown as
decoration. Thompson 1928 may be quoted briefly as PD English; prefer fresh
paraphrase for UI polish.
