# Character design: Uruk, Early Dynastic period (c. 2700 BCE)

Basis for the 3D character models in `media/models/` and the portraits rendered from them.
The game sets Gilgamesh in Early Dynastic Uruk, so the look follows Sumerian art of 2900-2350 BCE
(votive statues, the Standard of Ur, the Royal Cemetery of Ur) rather than later Babylonian or Assyrian dress.

## What the sources say

- **Kaunakes**: the typical garment of both sexes, a skirt (or whole dress) of sheepskin or wool with tufted or
  flounced layers. Length marks rank: knee-length for workers and soldiers, ankle-length for the upper class and kings.
  The upper body of men is usually bare; women wear a long tufted dress draped over one shoulder or a shawl.
  Felt or leather cloaks fastened at the neck are worn over it.
- **Men**: either shaven (bald) or with long hair parted in the middle and a long, often braided or curled beard.
  Votive statues of Tell Asmar (Eshnunna) show hands clasped at the chest, huge inlaid eyes (white shell, black
  limestone, a lapis pupil) and painted hair.
- **Women**: hair parted in the middle and plaited into a heavy braid wound round the head; elaborate headdresses of
  ribbons, beads and pendants (Queen Puabi of Ur: gold leaves, lapis and carnelian beads, large lunate earrings).
- **Soldiers** (Standard of Ur, c. 2600 BCE): leather or copper helmets with a chin strap, a cloak studded with metal
  discs, short kaunakes, spears and axes; no plate armour yet. Bronze scale armour in `3D_MODELS.md` is Late Bronze Age, not used.
- **Jewellery and colours**: gold, lapis lazuli (blue), carnelian (red), white shell. Wool is natural cream or
  brown; dyes are rare. Linen is for priests and the wealthy.
- **Gods and monsters**: divinity is shown by a horned cap (several pairs of horns for the greater gods).
  Scorpion-men on seals have a bearded human head and torso, a scorpion body and an upright tail, and a horned cap.
  Humbaba is the Cedar Forest's guardian; later art shows his face as coiled intestines (the Sippar clay mask) with
  a fierce brow and a snarling mouth.
- **Tools of trades**: scribe with a reed stylus and clay tablet, merchant with a balance and weights and a sealed
  bag, potter in a short kaunakes with clay stains, weaver with a spindle and a reed shuttle.

## Design table (heights are in metres and used by the Blender builder)

| NPC id | Body | Height | Dress and hair | Attributes |
| --- | --- | --- | --- | --- |
| gilgamesh | man, heroic | 2.00 | ankle-length white kaunakes, bare chest, wide gold belt, long curled beard, hair in a bun | gold diadem with lapis, armbands, mace |
| enkidu | man, stocky | 1.90 | hair covering the body, tattered hide loincloth, long matted hair and beard | bare feet, mud-brown skin |
| enkidu_civilized | man, stocky | 1.90 | knee-length cream kaunakes, belt, long hair tied back, trimmed beard | sandals, simple armband |
| ishtar | woman, tall | 1.85 | red-and-white tufted dress over one shoulder, long hair braid | horned crown with star disc, lapis and gold jewellery, bow case |
| shamhat | woman | 1.70 | white linen draped dress over one shoulder, braid wound round head | gold earrings, carnelian beads |
| humbaba | monster, huge | 3.00 | fur and hide wrap, bone and stone ornaments, matted mane | tusked face, heavy brow, large club |
| utnapishtim | man, old | 1.75 | long plain white robe, long white beard, hair long and white | wooden staff, no jewellery |
| ur_shanabi | man, lean | 1.78 | short kaunakes of undyed wool, bare chest, shaved head, short beard | long punting pole, belt pouch |
| scorpion_man | hybrid | 2.50 | bearded human torso, scorpion lower body, horned cap | pincers, upright tail, spear |
| ninsun | woman | 1.75 | long tufted ankle-length dress, hair braided and pinned | horned cap, gold necklace |
| anu | man, tall | 2.10 | ankle-length blue-white robe, long beard | multi-horned tall crown, sceptre |
| bull_of_heaven | beast | 2.60 (shoulder 2.2) | quadruped bull | heavy horns, lapis-blue beard and glowing eyes |
| high_priest_anu | man | 1.80 | shaved head, white linen skirt, bare chest, nude priest convention | lapis necklace, tablet |
| high_priestess_ishtar | woman | 1.72 | red tufted dress, tall headdress | gold jewellery, mace |
| temple_scribe | man | 1.70 | shaved head, cream knee-length skirt | satchel of tablets, stylus |
| royal_guard | man | 1.85 | knee-length kaunakes, studded leather cloak | copper helmet with strap, spear, shield |
| uruk_noble | man | 1.80 | ankle-length kaunakes, beard, hair in bun | gold collar, staff |
| uruk_merchant | man | 1.72 | knee-length coloured wool skirt, cloak, cap | balance, weights, pouch |
| potter | man, strong | 1.75 | short skirt, clay-stained apron, shaved head | clay pot, tools |
| weaver | woman | 1.65 | long wool dress, head scarf | spindle, shuttle |

## Sources

- [Fashion & Dress in Ancient Mesopotamia, World History Encyclopedia](https://www.worldhistory.org/article/2198/fashion--dress-in-ancient-mesopotamia/)
- [Early Dynastic sculpture 2900-2350 B.C., Metropolitan Museum of Art](https://www.metmuseum.org/essays/early-dynastic-sculpture-2900-2350-b-c)
- [Tell Asmar Hoard](https://en.wikipedia.org/wiki/Tell_Asmar_Hoard)
- [Standard of Ur](https://en.wikipedia.org/wiki/Standard_of_Ur)
- [Kaunakes](https://en.wikipedia.org/wiki/Kaunakes)
- [Face of the demon Humbaba (Sippar mask)](https://worldhistory.org/image/8103/face-of-the-demon-humbaba)
- Penn Museum and Metropolitan Museum cylinder-seal records for scorpion-men and Gilgamesh scenes.
- N. K. Sanders, *The Epic of Gilgamesh* (public domain edition used by the datadisk).
