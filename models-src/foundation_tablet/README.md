# Foundation tablet (Temple of Ishtar)

A small inscribed steatite foundation tablet, after the Ur-Namma tablets of Inanna's Eanna in Uruk
(`research/foundtion-tablet.jpg`, Ur III, c. 2100 BCE). The disk is set about six centuries earlier, so the
tablet does not copy Ur-Namma's text. It carries the same formula without a king's name:

    d-inanna / nin-a-ni / lugal / unug{ki}-ga-ke4 / e2-a-ni / mu-na-du3
    "For Inanna, his lady, the king of Uruk built her temple."

The signs are drawn with Noto Sans Cuneiform (SIL OFL; only the rendered pixels are kept). Those are
Neo-Assyrian sign forms in the later left-to-right orientation, a stand-in for Early Dynastic monumental
script, like the client's clay tablet.

| File | Role |
| --- | --- |
| `make_textures.py` | Paints `textures/` (inscribed face and plain steatite, albedo and normal) |
| `build_foundation_tablet.py` | Blender: builds the models below and, given a path, the 128 px inventory icon |
| `../../media/models/foundation_tablet.glb` | The item: the tablet alone, 10 x 5.2 x 1.6 cm, lying face up |
| `../../media/knowledge/foundation_tablet.jpg` | The picture of the tablet's knowledge card |
| `../../media/models/architecture/foundation_deposit.glb` | The opened box of baked bricks with the tablet, the lid aside (place `foundation_deposit`, `places/uruk.yaml`) |

    python3 -I models-src/foundation_tablet/make_textures.py
    blender -b --python models-src/foundation_tablet/build_foundation_tablet.py -- \
        ../ishtaria-client/assets/icons/items/foundation_tablet.png

The item type `foundation_tablet` is server migration `0061_foundation_tablet.sql`. No way to obtain the item is
wired yet. The tablet in the deposit can be read: standing at the box the player presses E and gets the knowledge
card `foundation_tablet` (`knowledge.yaml`, picture `media/knowledge/foundation_tablet.jpg` rendered by this
script) and the disk's hidden achievement `foundation_reader` (`achievements.yaml`).

Licence: original geometry and textures for the datadisk (CC BY-SA 4.0 with the disk).
