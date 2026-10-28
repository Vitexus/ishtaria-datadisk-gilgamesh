# Lamassu (aladlammu) and the small shedu: where they come from

Article used for the look and the places: https://cs.wikipedia.org/wiki/Aladlammú (a human bearded head, a bull's body, an eagle's wings, a horned tiara; pairs
of colossal statues at the gates of cities and the entrances of palaces; small shedu at the doors of houses).

**Source of the models (2026-10-28).** The guardians are the 0 A.D. models `pers_lamassu` and `pers_lamassu_small` (Wildfire Games, CC BY-SA 3.0), mirrored on this
disk under `media/models/architecture/zeroad/` (converted from 0 A.D.'s public.zip by `ishtaria-client/tools/zeroad-structures.py`; licence text:
`media/models/architecture/zeroad/License.txt`). `models-src/architecture/lamassu_models.py` welds, decimates and scales them to 7.6 m (a pair 9.5 m apart, standing on
the ground and looking south at yaw 0) and 2.2 m (5.4 m apart) and writes `lamassu_pair.glb`, `shedu_pair.glb` and their collision boxes. `tools/build_statues.py`
places the pairs in Uruk (`places/uruk_statues.yaml`) and `places/lamassu_guardians.yaml` stands the raw 0 A.D. statues at Susa. The 0 A.D. statues face the same way
the old model did (the head at -Y after a glTF import, i.e. glTF +Z at yaw 0), so no place had to be moved; the build script checks the head side and refuses to write
a pair that looks the wrong way.

**Replaced for the licence.** Until 2026-10 the guardians were derived from "Persian Lamassu" by Peter Farell, https://www.printables.com/model/665507-persian-lamassu
(CC BY-NC): a render of that mesh was the reference of a Hyper3D Rodin generation, which was recoloured after the museum reconstruction of the polychromy
(`research/lamassu-color.jpg`; `models-src/architecture/paint_lamassu.py`) and turned into the pair models. CC BY-NC does not fit the CC BY-SA 4.0 of the datadisk
(non-commercial only, and the derived work stays NC), so the owner decided (2026-10-28) to replace the statues with the 0 A.D. ones, whose CC BY-SA 3.0 fits.
The Printables-derived sources are removed: the 3MF, the render used as the Rodin reference, the Rodin generations (`lamassu_printables_derived`, and the unused
two-part `lamassu_body` / `lamassu_head` assembly), the coloured model, `paint_lamassu.py`, `rodin_lamassu_assemble.py`, `rodin/make_lamassu_head.py` and the lamassu
concept images. `debian/copyright` attributes the pair models to Wildfire Games.

**Not used:** the Sketchfab models "Ishtar Mesopotamian goddess (Ereshkigal)" by Mayantique (not downloadable, licence "Standard") and "The Queen of the Night" by Raiz (not
downloadable, no licence): only looked at.
