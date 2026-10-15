# Burney Relief (Queen of the Night): restoration for the game

Source: photogrammetry scan "The Burney Relief" by danielpett, CC BY 4.0 (`license.txt`). The relief (British Museum, about 1800-1750 BCE,
find-site unknown) is later than Gilgamesh's Uruk (about 2700 BCE); known compromise, like the Ishtar Gate.

Owner's wish (2026-10-13): the goddess as she left the workshop, not weathered; freestanding like the Sketchfab model by Mayantique (not
downloadable, licence "Standard": only looked at, never used). Built by `models-src/architecture/burney_restore.py` (Blender, live or headless).

What was done and why
- Mirror: the left half of the goddess survives; the right ear, hair roll, cheek, neck, half of the necklace and the right half of the hat were
  broken off. The left faces are mirrored about the centre line x = 0.68 (found by comparing a height map of the scan with its mirror image)
  and keep their UVs, so the colour comes along.
- Cut: the slab leans and has a step along the crack, so the figures are found by their height over a fitted slab plane (>0.45 units), the
  low-relief wings by two hand-traced outlines. The goddess, the owls and the lions with their base strip are kept; the slab is gone.
- Close: small holes are filled, a thin shell (Solidify 0.35 units) closes the back. 59000 faces, 2048 px textures, 2.4 m high, front along -Y.
- Units of the scan are about 18.7 per metre of the plaque model (34 x 45 units for 1.8 x 2.4 m); the axis x = 0.68 and the plane are in them.

Tried and dropped
- Smoothing depth and inpainting the texture in place: crumpled the neck, left a smudge on the crack.
- img2img (InvokeAI) "restored" images and Rodin from them: the figure turns into a generic (Indian-looking) goddess, owls became lions.
- Welding the axis strip and filling larger holes: long spikes.
- Orthographic viewport in Blender: pixels per unit = 700 / view_distance for a 1000 px wide screenshot (not 99 at distance 14).

Known weak spots: a thin sliver near the right lion's paw, the necklace area is rough, the hands are as scanned (the rods and rings are only
engraved lines and are gone with the slab), the back shell shows the front texture, a faint hairline along the axis of the face.
Not done: the original colours (pigment traces on the scan; red ochre body, black background, per the museum) - see below.
Pigment: the scan shows traces of red pigment; ancient figures were painted. Painting the restored colours is open (needs the museum's
analysis as a source, check before use).
