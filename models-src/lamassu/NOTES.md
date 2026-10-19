# Lamassu (aladlammu) and the small shedu: where they come from, and the licence question

Article used for the look and the places: https://cs.wikipedia.org/wiki/Aladlammú (a human bearded head, a bull's body, an eagle's wings, a horned tiara; pairs
of colossal statues at the gates of cities and the entrances of palaces; small shedu at the doors of houses).

**Source of the model.** SDXL (InvokeAI) could not draw a man's head on a bull, and a two-part Rodin assembly (`models-src/rodin_lamassu_assemble.py`) was disliked, so the
model is **derived from "Persian Lamassu" by Peter Farell, https://www.printables.com/model/665507-persian-lamassu (licence CC BY-NC)**: a render of that mesh (from the
3MF, not committed: `models-src/lamassu/printables/`, `models-src/concepts/lamassu_printables_ref.png`) is the single reference image of a Hyper3D Rodin generation
(`models-src/rodin/generations.txt`, `lamassu_printables_derived`), which gave `lamassu_derived_rodin_source.glb`.

**Polychromy (2026-10-18).** The Rodin texture is grey stone; the museum reconstruction shows the statues painted (`research/lamassu-color.jpg`; the photo is
underexposed, so the palette is the reconstruction's canonical Assyrian one, not pixel samples: a gold horned tiara with a lapis band, a dark blue-black beard,
wings striped ivory, lapis, green and red from the top, a warm brown body, a red belly band, black hooves, leg bands and tail). `models-src/architecture/paint_lamassu.py`
repaints the diffuse texture of the source and writes the coloured model:

    blender -b --python models-src/architecture/paint_lamassu.py -- models-src/lamassu/lamassu_derived_rodin_source.glb models-src/lamassu/lamassu_colored.glb

`models-src/architecture/lamassu_models.py` then turns `lamassu_colored.glb` into `lamassu_pair.glb` and `shedu_pair.glb` (+ simple collision boxes). The coloured
model keeps the same CC BY-NC derivation status as the Rodin source (see the licence question below).

**The licence does not fit.** The datadisk is CC BY-SA 4.0 and goes into a .deb; CC BY-NC (non-commercial) is not compatible with that, and the derived work remains NC.
The owner decided (2026-10-13) to make the derived work anyway. Before the disk is released one of these must happen:
1. the author is asked for permission or another licence (https://www.printables.com/@PeterFarell), or
2. the statue is remade from material that fits (own concept, or a CC0 / CC BY scan), or
3. the disk is released with these files left out.
`debian/copyright` carries the attribution and the NC marking for these files meanwhile.
The Hyper3D terms of use for generated assets were not checked either (see the note in `debian/copyright`).

**Not used:** the Sketchfab models "Ishtar Mesopotamian goddess (Ereshkigal)" by Mayantique (not downloadable, licence "Standard") and "The Queen of the Night" by Raiz (not
downloadable, no licence): only looked at.
