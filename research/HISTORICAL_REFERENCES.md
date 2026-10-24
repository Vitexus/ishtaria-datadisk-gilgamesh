# Historical References for Gilgamesh Datadisk
# Mesopotamian Art, Architecture, and Costume Research

This document compiles accurate historical references for creating authentic Mesopotamian artwork, costumes, and architecture for the Gilgamesh datadisk.

## 📜 Primary Sources

### Epic of Gilgamesh Text References

1. **N.K. Sanders Translation** (Public Domain)
   - Source: https://archive.org/stream/TheEpicofGilgamesh_201606/eog_djvu.txt
   - Based on Assyrian tablets from Nineveh (7th century BCE)
   - Contains the most complete version of the epic

2. **Standard Babylonian Version**
   - Tablet XI contains the flood story
   - Written in Akkadian cuneiform
   - Dates to 13th-10th century BCE

3. **Old Babylonian Version**
   - Earliest surviving fragments
   - Dates to 18th century BCE
   - More primitive narrative structure

### Archaeological Sources

#### Museum Collections

1. **British Museum, London**
   - [Mesopotamia Collection](https://www.britishmuseum.org/collection/galleries/mesopotamia)
   - **Key Pieces**:
     - Standard of Ur (2600-2400 BCE)
     - Cylinder Seals with Gilgamesh scenes
     - Ishtar Gate reconstructions
     - Ziggurat models
     - Royal statues from Uruk period

2. **Louvre Museum, Paris**
   - [Near Eastern Antiquities](https://www.louvre.fr/en/departments/near-eastern-antiquities)
   - **Key Pieces**:
     - Stele of Naram-Sin (2254-2218 BCE)
     - Statues of Gudea (2120 BCE)
     - Cuneiform tablets
     - Mesopotamian jewelry

3. **Pergamon Museum, Berlin**
   - [Ishtar Gate](https://www.smb.museum/en/museums-institutions/pergamonmuseum/home/)
   - **Key Pieces**:
     - Reconstructed Ishtar Gate (6th century BCE)
     - Processional Way glazed bricks
     - Throne room reconstructions
     - Babylonian art and artifacts

4. **Iraq Museum, Baghdad**
   - **Key Pieces**:
     - Uruk artifacts
     - Sumerian statues
     - Cuneiform tablets with epic fragments

## 🏛️ Architectural References

### Ziggurats

**Living catalog for the disk:** `research/ZIGGURATS.md` (which cities get a tower, distinct vs
clone models, Ur ≠ Uruk Anu, Woolley / Schmid dimensions). Prefer that file over the short notes
below; they are kept as a quick index.

#### 1. Ziggurat of Ur / Etemenniguru (Tell el-Muqayyar) — Nanna/Sîn
- **Date**: c. 2100 BCE (Ur-Nammu / Šulgi); Nabonidus restored later
- **Dimensions**: 64 × 45 m base, originally ~30 m; **3** Neo-Sumerian stages
- **Disk**: `ziggurat_ur.glb` at place `ur` (distinct). Not the White Temple of Uruk.
- **References**: Woolley, *Ur Excavations* V; Heinrich 1982; https://en.wikipedia.org/wiki/Great_Ziggurat_of_Ur

#### 2. Ziggurat of Anu + White Temple (Uruk / Warka)
- **Date**: terrace raised over many phases; White Temple c. 3500 BCE
- **Form**: **one** terrace ~12 m, court ~50 × 45 m, temple 22 × 17 m
- **Disk**: `ziggurat_anu.glb` / baked into `uruk_walls.glb`
- See also Ishtar's stepped tower in Eanna (`uruk_ishtar_ziggurat.glb`) — story addition

#### 3. Ziggurat of Aqar Quf (Dur-Kurigalzu)
- **Date**: Kassite (2nd millennium BCE); often cited as among the best-preserved in Iraq
- **Dimensions** (published summaries): ~69 × 67 m base, tall core
- **Disk**: city not pinned; do not confuse with Ur or Nippur

#### 4. Etemenanki (Babylon)
- **Date**: Neo-Babylonian (c. 6th century BCE); anachronism on the Epic map (owner decision)
- **Dimensions**: ~91 m square, usual reconstr. ~90 m / 7 stages (Schmid/George; not the ~54 m travel estimate)
- **Disk**: `ziggurat_etemenanki.glb` (`places/babylon.yaml`)

### Architectural Features

#### Construction Materials

1. **Mud Brick**
   - **Composition**: Sun-dried clay mixed with straw or chaff
   - **Size**: 40x20x10 cm (standard Sumerian)
   - **Color**: Tan to light brown
   - **Use**: Primary building material for all structures
   - **Advantages**: Abundant, good insulation
   - **Disadvantages**: Vulnerable to water, requires maintenance

2. **Fired Brick**
   - **Composition**: Clay fired in kilns
   - **Use**: Important structures, waterproofing
   - **Color**: Red to orange-red
   - **Advantages**: More durable, water-resistant
   - **Disadvantages**: More expensive, requires fuel

3. **Plaster**
   - **Composition**: Gypsum or lime
   - **Use**: Exterior finish, interior walls
   - **Color**: White to cream
   - **Texture**: Smooth, often painted
   - **Thickness**: 2-5 cm

4. **Bitumen**
   - **Use**: Waterproofing (foundations, bathrooms)
   - **Composition**: Natural asphalt from Hit, Iraq
   - **Color**: Black

5. **Stone**
   - **Types**: Limestone, basalt, alabaster
   - **Use**: Foundations, door sills, special features
   - **Source**: Imported from nearby regions
   - **Rarity**: Expensive, used sparingly

6. **Wood**
   - **Types**: Cedar (from Lebanon), date palm, poplar
   - **Use**: Beams, doors, furniture, roofing
   - **Importance**: Very expensive, imported

7. **Reed**
   - **Use**: Roofing, mats, fencing
   - **Types**: Marsh reeds from Tigris/Euphrates
   - **Advantages**: Lightweight, good insulation

#### Decorative Materials

1. **Glazed Brick**
   - **Colors**: Blue, turquoise, yellow, red, white, black
   - **Use**: Facades, decorative bands, geometric patterns
   - **Technique**: Glass coating fused to brick
   - **Period**: Neo-Babylonian (6th century BCE)
   - **Reference**: Ishtar Gate, Processional Way

2. **Lapis Lazuli**
   - **Color**: Deep blue
   - **Use**: Inlays, jewelry, temple ornaments
   - **Source**: Afghanistan (imported)
   - **Value**: Extremely valuable

3. **Carnelian**
   - **Color**: Red-orange
   - **Use**: Inlays, jewelry, decorative elements
   - **Source**: Various regions

4. **Gold**
   - **Use**: Temple ornaments, royal items, jewelry
   - **Source**: Imported
   - **Purity**: Often alloyed with copper or silver

5. **Shell**
   - **Types**: Mother-of-pearl, cowrie
   - **Use**: Inlays, decorative elements
   - **Source**: Persian Gulf

6. **Faience**
   - **Composition**: Glassy silica material
   - **Colors**: Various, especially turquoise
   - **Use**: Small decorative objects, beads

#### Architectural Elements

1. **Buttresses**
   - **Function**: Structural reinforcement
   - **Spacing**: Every 2-3 meters
   - **Projection**: 0.5-1 meter
   - **Shape**: Rectangular

2. **Niches**
   - **Function**: Decorative, structural, for statues
   - **Depth**: 0.3-0.5 meters
   - **Shape**: Rectangular or arched
   - **Arrangement**: Regular intervals

3. **Friezes**
   - **Function**: Decorative bands
   - **Content**: Geometric patterns, figurative scenes
   - **Location**: Near roofline, on walls
   - **Materials**: Plaster, glazed brick

4. **Crenellations**
   - **Function**: Defensive, decorative
   - **Shape**: Rectangular merlons and crenels
   - **Height**: 1-1.5 meters
   - **Location**: Wall tops

5. **Staircases**
   - **Location**: Central or multiple
   - **Width**: 3-5 meters
   - **Slope**: Steep (30-45 degrees)
   - **Materials**: Mud brick, stone steps

6. **Doors**
   - **Materials**: Wood (cedar) with bronze fittings
   - **Size**: 2-3 meters height, 1-1.5 meters width
   - **Features**: Bronze reinforcement, stone thresholds
   - **Decorations**: Carved panels, bronze plaques

7. **Windows**
   - **Type**: Slits or small openings
   - **Function**: Light, ventilation
   - **Size**: 0.5-1 meter height, 0.2-0.3 meters width
   - **Placement**: High on walls

8. **Roofs**
   - **Type**: Flat
   - **Construction**: Wooden beams with reed mat and mud plaster
   - **Parapets**: Low walls around edges
   - **Drainage**: Slight slope, drainage channels

### Uruk-Specific Architecture

#### City Walls
- **Outer Wall**: 
  - **Date**: c. 2900 BCE
  - **Length**: 9.5 km
  - **Height**: 8-10 meters
  - **Thickness**: 5-6 meters
  - **Materials**: Mud brick with white plaster
  - **Features**: Fortified towers every 50-60 meters

- **Inner Wall**:
  - **Distance from Outer**: 15-20 meters
  - **Height**: 6-7 meters
  - **Thickness**: 4-5 meters

#### City Gates
- **Number**: 9 main gates mentioned in texts
- **Famous Gates**:
  - **Kullaba Gate**: Main western gate
  - **Eanna Gate**: Near Anu ziggurat
  - **Ishtar Gate**: Southern gate

#### Ziggurat of Anu (Uruk)
- **Form**: **one** terrace (~12 m), not 3–4 tiers (that was a Ur/Uruk mix-up; see `ZIGGURATS.md`)
- **Location**: Anu district (Kullaba), beside Eanna; OSM footprint in `LANDSCAPE.md`
- **Dedication**: Sky god Anu; White Temple on the bitumen court
- **Disk**: `ziggurat_anu.glb` / `uruk_walls.glb`

#### Ziggurat of Ishtar (Uruk)
- **Note**: Stepped tower at `ishtar_temple` is a story addition in Eanna, not a Woolley plan of Ur
- **Disk**: `uruk_ishtar_ziggurat.glb`

#### White Temple
- **Date**: c. 3500-3000 BCE (built 3517–3358 BCE in published ranges)
- **Location**: On Anu terrace court
- **Dimensions**: ~22 × 17 m; roof ~21 m above the plain
- **Features**: whitewashed, tripartite, entrances do not face the access stairs

#### Royal Palace
- **Location**: Near city center
- **Size**: Large complex
- **Features**:
  - Multiple courtyards
  - Throne room with raised dais
  - Private quarters
  - Audience halls
  - Administrative offices
  - Storage rooms

## 👗 Costume References

### Historical Depictions

#### 1. Standard of Ur (2600-2400 BCE)
- **Location**: British Museum
- **Period**: Early Dynastic III
- **Scenes**: War side and Peace side
- **Costume Details**:
  - **Men**: Loincloths (kaunakes), belted tunics
  - **Women**: Wrapped dresses, shawls
  - **Royalty**: Long robes, jewelry
  - **Soldiers**: Helmets, spears, shields
  - **Footwear**: Sandals

#### 2. Stele of Naram-Sin (2254-2218 BCE)
- **Location**: Louvre Museum
- **Period**: Akkadian Empire
- **Scene**: Naram-Sin's victory over Lullubi
- **Costume Details**:
  - **King**: Horned helmet, long robe, weapons
  - **Soldiers**: Helmets, tunics, spears
  - **Enemies**: Naked or loincloths, long hair

#### 3. Statues of Gudea (2120 BCE)
- **Location**: Louvre, British Museum
- **Period**: Neo-Sumerian (Lagash)
- **Features**:
  - **Attire**: Kaunakes (sheep-fleece skirt)
  - **Hair**: Long, curled beard
  - **Hat**: Cylinder hat or turban
  - **Hands**: Clasped in prayer or holding objects

#### 4. Stele of Ur-Nammu (2112-2095 BCE)
- **Location**: Louvre, British Museum
- **Period**: Ur III
- **Scene**: Victory stele
- **Costume Details**:
  - **King**: Long robe, kaunakes, cylinder hat
  - **Soldiers**: Helmets, spears, kaunakes

#### 5. Ishtar Gate (6th century BCE)
- **Location**: Pergamon Museum
- **Period**: Neo-Babylonian
- **Features**:
  - **Glazed Brick**: Blue and yellow dragons, bulls
  - **Color Scheme**: Blue background, yellow animals
  - **Pattern**: Processional friezes

### Clothing Types

#### 1. Kaunakes (Sheep-Fleece Skirt)
- **Description**: Skirt made to resemble sheep fleece
- **Period**: Early Dynastic to Ur III
- **Worn by**: Royalty, elite men
- **Construction**: 
  - Horizontal rows of tufts
  - Often belted at waist
  - Length: Knee-length to ankle-length
- **Materials**: Wool, possibly leather
- **Color**: Natural wool colors (white, brown, black)

#### 2. Tunic
- **Description**: Simple garment covering torso
- **Period**: All periods
- **Worn by**: Common men, women
- **Construction**:
  - Rectangular piece of fabric
  - Sleeveless or short sleeves
  - Belted at waist
  - Length: Knee-length to ankle-length
- **Materials**: Linen, wool
- **Color**: Natural or dyed

#### 3. Robe
- **Description**: Long, flowing garment
- **Period**: All periods
- **Worn by**: Royalty, priests, elite
- **Construction**:
  - Rectangular or T-shaped
  - Long sleeves or sleeveless
  - Belted or unbelted
  - Length: Ankle-length
- **Materials**: Fine linen, wool, silk (later periods)
- **Color**: White, dyed colors

#### 4. Dress
- **Description**: Wrapped garment for women
- **Period**: All periods
- **Construction**:
  - Rectangular piece wrapped around body
  - One shoulder bare or both covered
  - Belted at waist
  - Length: Ankle-length
- **Materials**: Linen, wool
- **Color**: Various colors

#### 5. Shawl
- **Description**: Rectangular cloth draped over shoulders
- **Period**: All periods
- **Worn by**: Men and women
- **Construction**:
  - Lightweight fabric
  - Draped or pinned
  - Often fringed
- **Materials**: Linen, wool
- **Color**: Various colors

### Headwear

#### 1. Cylinder Hat
- **Period**: Early Dynastic to Ur III
- **Worn by**: Elite men
- **Construction**:
  - Cylindrical shape
  - Height: 10-20 cm
  - Diameter: 8-12 cm
- **Materials**: Felt, leather, cloth

#### 2. Turban
- **Period**: Akkadian to Neo-Babylonian
- **Worn by**: Elite men
- **Construction**:
  - Wound cloth
  - Height: 10-15 cm
  - Often with decorative elements
- **Materials**: Linen, wool

#### 3. Horned Headdress
- **Period**: Akkadian
- **Worn by**: Gods, kings (divine symbolism)
- **Construction**:
  - Cylinder hat with horn-like projections
  - 2-4 horns
  - Symbol of divinity
- **Example**: Naram-Sin stele

#### 4. Headdress (Women)
- **Period**: All periods
- **Construction**:
  - Decorative headband
  - Often with lappets (hanging ends)
  - Sometimes with floral or geometric motifs
- **Materials**: Cloth, gold, beads

#### 5. Crown
- **Period**: All periods
- **Worn by**: Royalty
- **Construction**:
  - Circlet or cap
  - Often with decorative elements
  - Symbol of authority
- **Materials**: Gold, precious stones

### Footwear

#### 1. Sandals
- **Period**: All periods
- **Construction**:
  - Sole: Leather, papyrus, wood
  - Straps: Leather, cloth
  - Style: Toe strap, ankle strap
- **Materials**: Leather, papyrus, wood

#### 2. Boots
- **Period**: Akkadian to Neo-Babylonian
- **Worn by**: Soldiers, royalty
- **Construction**:
  - Ankle-high or knee-high
  - Laced or buckled
- **Materials**: Leather

#### 3. Barefoot
- **Period**: All periods
- **Worn by**: Common people, priests (in temples)

### Jewelry

#### 1. Necklaces
- **Materials**: Gold, silver, lapis lazuli, carnelian, shell, faience
- **Styles**:
  - Beaded: Multiple strands of beads
  - Pendant: Single large piece
  - Collar: Broad, flat piece
- **Placement**: Around neck, sometimes draped

#### 2. Earrings
- **Materials**: Gold, silver, precious stones
- **Styles**:
  - Hoop: Circular
  - Stud: Simple post
  - Dangling: With pendants
- **Period**: Early Dynastic onwards

#### 3. Bracelets
- **Materials**: Gold, silver, precious stones
- **Styles**:
  - Bangle: Rigid circular
  - Cuff: Open, wide
- **Placement**: Wrist, upper arm

#### 4. Rings
- **Materials**: Gold, silver, precious stones
- **Styles**:
  - Signet: Engraved with owner's mark
  - Simple: Plain band
- **Period**: Akkadian onwards

#### 5. Armlets
- **Materials**: Gold, silver
- **Placement**: Upper arm
- **Style**: Spiral or cuff

#### 6. Anklets
- **Materials**: Gold, silver
- **Placement**: Ankle
- **Style**: Chain or bangle

### Hairstyles

#### Men
- **Early Period**: Long hair, shoulder-length
- **Akkadian Period**: Short to medium length
- **Beard**: Full beard, often curled
- **Mustache**: Thick, often curled
- **Styles**:
  - Straight
  - Curled (using hot irons)
  - Braided

#### Women
- **Long Hair**: Shoulder-length to waist-length
- **Styles**:
  - Straight with parting
  - Braided
  - Wrapped in shawl
- **Adornments**:
  - Headbands
  - Hair rings
  - Ribbons

### Costume by Character

#### Gilgamesh (King of Uruk)
- **Period**: Early Dynastic (c. 2700 BCE)
- **Attire**:
  - **Head**: Golden diadem/crown with lapis lazuli inlays
  - **Upper Body**: White linen tunic with gold embroidery
  - **Lower Body**: Kaunakes (sheep-fleece skirt)
  - **Belt**: Wide leather belt with gold buckle
  - **Footwear**: Sandals with gold decoration
  - **Jewelry**: Gold necklace, bracelets, signet ring
  - **Hair**: Short to medium, well-kept beard (curled)
  - **Weapons**: Sword at belt, dagger
- **Color Scheme**: White, gold, lapis lazuli blue
- **References**:
  - Standard of Ur (royal figures)
  - Statues of Gudea (similar period)

#### Enkidu (Wild)
- **Period**: Before civilization
- **Attire**:
  - **Head**: Long, matted hair covering shoulders
  - **Upper Body**: Bare chest
  - **Lower Body**: Animal skin loincloth
  - **Footwear**: Barefoot
  - **Jewelry**: None
  - **Hair**: Long, wild, matted
  - **Beard**: Long, unkempt
- **Color Scheme**: Earth tones, animal hide colors
- **References**:
  - Depictions of wild men in Mesopotamian art
  - Descriptions from epic text

#### Enkidu (Civilized)
- **Period**: After meeting Shamhat
- **Attire**:
  - **Head**: Simple headband
  - **Upper Body**: Simple linen tunic
  - **Lower Body**: Kaunakes or plain skirt
  - **Belt**: Leather belt
  - **Footwear**: Sandals
  - **Jewelry**: Minimal (one bracelet from Shamhat)
  - **Hair**: Still long but cleaner, beard trimmed
- **Color Scheme**: Natural linen, leather brown
- **References**:
  - Standard of Ur (common men)
  - Descriptions from epic text

#### Ishtar (Goddess)
- **Period**: All periods
- **Attire**:
  - **Head**: Horned headdress with star motifs, lappets
  - **Upper Body**: Red and gold ceremonial robes
  - **Lower Body**: Long, flowing skirt
  - **Belt**: Gold belt with precious stone inlays
  - **Footwear**: Gold sandals
  - **Jewelry**: Multiple necklaces, bracelets, armlets, anklets, earrings
  - **Weapons**: Mace or bow at side
  - **Hair**: Long, elaborately styled
  - **Makeup**: Heavy eye makeup (kohl), red lips
- **Color Scheme**: Red, gold, lapis lazuli, carnelian
- **References**:
  - Ishtar Gate glazed bricks
  - Votive statues of Ishtar
  - Cylinder seals with goddess depictions

#### Shamhat (Temple Priestess)
- **Period**: Early Dynastic
- **Attire**:
  - **Head**: Gold headdress with lappets
  - **Upper Body**: White ceremonial robes with gold embroidery
  - **Lower Body**: Long, pleated dress
  - **Belt**: Gold belt
  - **Footwear**: Gold sandals
  - **Jewelry**: Gold necklace, bracelets, earrings
  - **Accessories**: Small ceremonial knife at belt
  - **Hair**: Long, elaborately styled
  - **Makeup**: Eye makeup, subtle
- **Color Scheme**: White, gold
- **References**:
  - Statues of priestesses
  - Cylinder seals with temple scenes

#### Humbaba (Monster)
- **Period**: Mythological
- **Attire**:
  - **Head**: None (monstrous face)
  - **Upper Body**: Animal skins and furs draped
  - **Lower Body**: Bone armor or scales
  - **Footwear**: None or simple hide
  - **Jewelry**: Stone and bone decorations
  - **Weapons**: Massive club or axe
  - **Special**: Sevenfold terrors (exaggerated features)
- **Color Scheme**: Dark, earthy, terrifying
- **References**:
  - Descriptions from epic text ("his roar is a floodwater, his mouth is fire")
  - Depictions of monsters in Mesopotamian art

#### Utnapishtim (Flood Survivor)
- **Period**: Later period (post-flood)
- **Attire**:
  - **Head**: Simple headband or turban
  - **Upper Body**: White robes
  - **Lower Body**: Long skirt
  - **Belt**: Simple leather belt
  - **Footwear**: Sandals
  - **Jewelry**: Minimal (wise elder)
  - **Accessories**: Staff, clay tablets
  - **Hair**: Long, white/gray
  - **Beard**: Long, white/gray
- **Color Scheme**: White, natural tones
- **References**:
  - Depictions of wise elders in art
  - Descriptions from epic text

#### Ur-Shanabi (Ferryman)
- **Period**: Later period
- **Attire**:
  - **Head**: Simple cloth head covering
  - **Upper Body**: Simple loincloth or tunic
  - **Lower Body**: Plain skirt or loincloth
  - **Footwear**: None or simple sandals
  - **Jewelry**: None or minimal
  - **Accessories**: Oar/pole, pouch at belt
  - **Hair**: Practical, short
  - **Beard**: Short, practical
- **Color Scheme**: Natural, practical
- **References**:
  - Depictions of boatmen in art
  - Descriptions from epic text

#### Scorpion Man (Guardian)
- **Period**: Mythological
- **Attire**:
  - **Upper Body**: Human torso with armor plates
  - **Lower Body**: Scorpion body with chitin armor
  - **Tail**: Segmented scorpion tail with stinger
  - **Pincers**: Large, menacing
  - **Color**: Human skin on upper body, chitin/armor on lower
  - **Weapons**: None (natural weapons)
- **Color Scheme**: Human tones, brown/black chitin
- **References**:
  - Descriptions from epic text
  - Depictions of hybrid creatures in art

#### Ninsun (Gilgamesh's Mother)
- **Period**: Early Dynastic
- **Attire**:
  - **Head**: Goddess headdress
  - **Upper Body**: White robes with gold embroidery
  - **Lower Body**: Long, flowing skirt
  - **Belt**: Gold belt
  - **Footwear**: Gold sandals
  - **Jewelry**: Multiple gold pieces
  - **Hair**: Long, elaborately styled
  - **Makeup**: Heavy eye makeup
- **Color Scheme**: White, gold
- **References**:
  - Depictions of goddesses in art
  - Descriptions from epic text (wise, divine)

#### Aruru (Creatrix; Enkidu from clay)
- **Period**: Mythological (named in Gilgameš, Babylonian cuneiform copies from
  c. 1750 BCE; tradition older)
- **Role in the disk**: Tablet I prologue of the Hunter quest — the gods call her to
  create Gilgameš’s equal; she washes her hands, pinches clay, and forms Enkidu
  (`quest.hunter.excerpt`). Story wording follows eBL / George 2022; see
  [`EPIC.md`](EPIC.md).
- **Attributes** (secondary summary): earth and birth mother; creatrix of humanity
  from muddy substance; matron of clay work / figure-making; often identified or
  paired with Mami, Ninḫursag (Nin-Kharsag), and related mother titles.
- **References**:
  - [The Goddess Aruru — Holladay Paganism cyclopedia](http://www.holladaypaganism.com/goddesses/cyclopedia/a/ARURU.HTM)
    (compiles Graves, Gray *NEM*, Kaster, Mackenzie, Monaghan *BGH*, Pritchard *ANET*,
    Walker *WEMS*, etc.)
  - Poem of Gilgameš SB I (George 2022 eBL): creation of Enkidu

#### Anu (Sky God)
- **Period**: All periods
- **Attire**:
  - **Head**: Horned headdress with multiple tiers
  - **Upper Body**: White or blue robes
  - **Lower Body**: Long skirt
  - **Belt**: Wide gold belt
  - **Footwear**: Gold sandals
  - **Jewelry**: Extensive gold with lapis lazuli
  - **Accessories**: Scepter, symbols of sky
  - **Hair**: Long, white/gray
  - **Beard**: Long, white/gray, curled
- **Color Scheme**: White, blue, gold
- **References**:
  - Standard depictions of sky gods
  - Descriptions from religious texts

#### Bull of Heaven
- **Period**: Mythological
- **Attire**:
  - **Body**: Divine bull with exaggerated features
  - **Color**: Red and black (as described in text)
  - **Size**: Massive, larger than normal bull
  - **Special Effects**: Smoke, fire (optional)
- **References**:
  - Descriptions from epic text (Tablet VI)
  - Depictions of divine animals in art

### Historical Figures (Uruk Citizens)

#### High Priest of Anu
- **Attire**:
  - **Head**: White headdress with lappets
  - **Upper Body**: White linen tunic and robe
  - **Lower Body**: Long skirt
  - **Belt**: Lapis lazuli bead necklace as belt
  - **Footwear**: White sandals
  - **Jewelry**: Ceremonial dagger, clay tablet at belt
  - **Hair**: Long, well-kept
  - **Beard**: Long, well-kept
- **Color Scheme**: White, lapis lazuli blue

#### High Priestess of Ishtar
- **Attire**:
  - **Head**: Star headdress
  - **Upper Body**: Red and gold robes
  - **Lower Body**: Long skirt
  - **Belt**: Gold belt
  - **Footwear**: Gold sandals
  - **Jewelry**: Multiple gold pieces, ceremonial mace
  - **Hair**: Long, elaborately styled
  - **Makeup**: Heavy
- **Color Scheme**: Red, gold

#### Temple Scribe
- **Attire**:
  - **Head**: Simple headband
  - **Upper Body**: White tunic
  - **Lower Body**: Plain skirt
  - **Accessories**: Clay tablets in satchel, reed stylus at belt
  - **Footwear**: Sandals
  - **Hair**: Practical cut
  - **Beard**: Short
- **Color Scheme**: White, natural

#### Royal Guard
- **Attire**:
  - **Head**: Plumed helmet
  - **Upper Body**: Bronze scale armor
  - **Lower Body**: Leather skirt over armor
  - **Legs**: Bronze greaves
  - **Footwear**: Leather boots
  - **Weapons**: Sword and spear
  - **Hair**: Short, practical
  - **Beard**: Short, practical
- **Color Scheme**: Bronze, leather brown

#### Uruk Noble
- **Attire**:
  - **Head**: Turban or cylinder hat
  - **Upper Body**: Fine linen tunic with embroidery
  - **Lower Body**: Long skirt
  - **Belt**: Gold belt
  - **Footwear**: Gold sandals
  - **Accessories**: Staff or walking stick
  - **Jewelry**: Gold necklace, bracelets, rings
  - **Hair**: Well-kept
  - **Beard**: Well-kept, curled
- **Color Scheme**: Fine fabrics, gold

#### Uruk Merchant
- **Attire**:
  - **Head**: Turban
  - **Upper Body**: Colorful tunic
  - **Lower Body**: Skirt
  - **Accessories**: Balance scale, money pouch
  - **Footwear**: Practical sandals
  - **Hair**: Practical
  - **Beard**: Practical
- **Color Scheme**: Various colors

#### Potter
- **Attire**:
  - **Head**: Simple cloth covering
  - **Upper Body**: Simple tunic
  - **Lower Body**: Plain skirt
  - **Accessories**: Clay-covered apron, wooden tools at belt
  - **Footwear**: Barefoot or sandals
  - **Hair**: Practical, possibly dusty
- **Color Scheme**: Natural, clay-stained

#### Weaver
- **Attire**:
  - **Head**: Head covering
  - **Upper Body**: Simple dress
  - **Lower Body**: Long skirt
  - **Accessories**: Shuttle at belt, fabric samples
  - **Footwear**: Barefoot or sandals
  - **Hair**: Practical, covered
- **Color Scheme**: Natural fabrics

## 🎨 Color Palette

### Architectural Colors
- **Mud Brick**: #8B4513, #A0522D, #CD853F (tan to brown)
- **Plaster**: #F5F5DC, #FFFFFF, #FFFAF0 (cream to white)
- **Stone**: #696969, #A9A9A9, #808080 (gray)
- **Glazed Brick**: #0066CC, #0099FF, #00CCFF (blue)
- **Lapis Lazuli**: #38618B, #0047AB, #1E90FF (deep blue)
- **Carnelian**: #B31B1B, #CD5C5C, #DC143C (red-orange)
- **Gold**: #FFD700, #FF8C00, #DAA520 (gold)

### Costume Colors
- **White**: #FFFFFF, #F8F8FF (ceremonial, priestly)
- **Red**: #FF0000, #DC143C, #B22222 (Ishtar, royalty)
- **Blue**: #0000FF, #191970, #4169E1 (lapis lazuli, royalty)
- **Gold**: #FFD700, #FFD700 (royalty, divinity)
- **Black**: #000000 (hair, beards, some jewelry)
- **Brown**: #8B4513, #A0522D (leather, common garments)
- **Green**: #006400, #228B22 (vegetation, some fabrics)

### Symbolic Colors
- **White**: Purity, divinity, Anu
- **Red**: Life, vitality, war, Ishtar
- **Blue**: Heaven, divinity, lapis lazuli
- **Gold**: Royalty, divinity, wealth
- **Black**: Earth, underworld, fertility
- **Green**: Fertility, vegetation, growth

## 📚 Academic References

### Books
1. **Pollock, S. (1999). *Ancient Mesopotamia*. Cambridge University Press.**
   - Comprehensive overview of Mesopotamian civilization
   - Architectural descriptions and illustrations

2. **Roaf, M. (1990). *Cultural Atlas of Mesopotamia and the Ancient Near East*. Facts on File.**
   - Maps, architectural plans, historical context

3. **Crawford, H. (2015). *Sumer and the Sumerians*. Cambridge University Press.**
   - Sumerian art, architecture, and society

4. **Kuhrt, A. (1995). *The Ancient Near East: c. 3000-330 BCE*. Routledge.**
   - Historical context and descriptions

5. **Postgate, N. (1992). *Early Mesopotamia: Society and Economy at the Dawn of History*. Routledge.**
   - Social structure and daily life

6. **Collon, D. (1987). *Ancient Near Eastern Art*. University of California Press.**
   - Art historical analysis

7. **Frankfort, H. (1954). *Art and Architecture of the Ancient Orient*. Pelican History of Art.**
   - Architectural analysis and reconstructions

### Articles
1. **Heinrich, E. (1982). "The Temple of Nanna at Ur". *Iraq* 44(1): 1-26.**
   - Detailed analysis of ziggurat construction

2. **W поль, M. (1939). *Ur of the Chaldees*. Penguin Books.**
   - Excavation reports and architectural descriptions

3. **Andrae, W. (1977). *Babylon: The Wonders of the Ancient World*. Thames and Hudson.**
   - Babylonian architecture and reconstructions

4. **Oppenheim, A. L. (1977). *Ancient Mesopotamia: Portrait of a Dead Civilization*. University of Chicago Press.**
   - Daily life, costumes, and social customs

5. **Hall, H. R. (1905). "The Cylinder Seals of Western Asia". *British Museum*.**
   - Cylinder seal imagery and descriptions

### Web Resources
1. **British Museum - Mesopotamia**: https://www.britishmuseum.org/collection/galleries/mesopotamia
2. **Louvre - Near Eastern Antiquities**: https://www.louvre.fr/en/departments/near-eastern-antiquities
3. **Pergamon Museum**: https://www.smb.museum/en/museums-institutions/pergamonmuseum/home/
4. **Metropolitan Museum - Mesopotamia**: https://www.metmuseum.org/toah/hd/meso/hd_meso.htm
5. **CDLI (Cuneiform Digital Library Initiative)**: https://cdli.ucla.edu/
6. **Livius.org - Mesopotamia**: https://www.livius.org/mesopotamia/

### Online Databases
1. **CDLI**: https://cdli.ucla.edu/ - Cuneiform tablets and texts
2. **Oriental Institute**: https://oi.uchicago.edu/ - Publications and resources
3. **Ashmolean Museum**: https://www.ashmolean.org/ - Near Eastern collections
4. **Vorderasiatisches Museum**: https://www.smb.museum/vam/ - Berlin's Near Eastern museum

## 🎨 Style Guide for Artwork

### General Principles
1. **Historical Accuracy**: Use archaeological evidence as primary reference
2. **Period Appropriateness**: Match art style to character's period
3. **Cultural Authenticity**: Use Mesopotamian iconography and symbolism
4. **Consistency**: Maintain consistent style across all artwork
5. **Ishtaria Integration**: Ensure compatibility with Ishtaria's aesthetic

### Portrait Style
- **Format**: 512x512 pixels (square)
- **Background**: Transparent or gradient
- **Pose**: Upper body or full figure, 3/4 view recommended
- **Lighting**: Soft, directional (from upper left)
- **Style**: Semi-realistic with stylized elements
- **Line Work**: Clean, defined edges
- **Color**: Rich, earthy tones with selective bright colors

### Cover Image Style
- **Format**: 1024x768 pixels (landscape)
- **Composition**: Gilgamesh and Enkidu in foreground, Uruk ziggurats in background
- **Style**: Cinematic, atmospheric
- **Lighting**: Dramatic (golden hour or sunrise)
- **Color Scheme**: Warm tones (gold, tan) with cool accents (blue, green)
- **Elements**:
  - Gilgamesh: Central, heroic pose
  - Enkidu: Supporting, slightly behind
  - Ziggurats: Multiple in background
  - Cedar Forest: Dark green in distance
  - Sky: Clear, with subtle clouds

### Architectural Style
- **Accuracy**: Based on archaeological reconstructions
- **Materials**: Visible texture of mud brick, plaster, stone
- **Weathering**: Slight wear and aging
- **Details**: Architectural features (buttresses, niches, friezes)
- **Lighting**: Natural sunlight with shadows
- **Scale**: Accurate proportions based on historical data

### Character Modeling Style
- **Proportions**: Based on Mesopotamian artistic conventions
  - Head: Large relative to body (1:6 to 1:7)
  - Eyes: Large, almond-shaped
  - Nose: Straight profile
  - Lips: Full, defined
  - Ears: Large, prominent
- **Features**: Exaggerated for important characters
- **Poses**: Static, hierarchical (royalty upright, commoners slightly bent)
- **Hair**: Styled, often with visible strands
- **Beards**: Curled, detailed

### Texture Style
- **Resolution**: 1024x1024 or 2048x2048 for main textures
- **Format**: PNG with alpha channel
- **Style**: Hand-painted or photorealistic
- **Details**: Visible material properties (fabric weave, brick texture, metal reflections)
- **Color**: Historical color palette

## ✅ Verification Checklist

### For Each Artwork Piece
- [ ] Based on at least 2 historical references
- [ ] Period-appropriate (Early Dynastic for Gilgamesh era)
- [ ] Culturally accurate (Mesopotamian/Sumerian)
- [ ] Consistent style with other pieces
- [ ] Proper proportions and scale
- [ ] Accurate color scheme
- [ ] Historically accurate details (clothing, weapons, jewelry)
- [ ] Verified against primary sources

### For Portraits
- [ ] 512x512 pixels
- [ ] Character recognizable
- [ ] Costume accurate to character description
- [ ] Appropriate pose and expression
- [ ] Consistent lighting
- [ ] Clean edges (transparent background)

### For Architecture
- [ ] Accurate dimensions
- [ ] Correct materials and textures
- [ ] Historical architectural features
- [ ] Appropriate level of detail
- [ ] Optimized for performance (polycount)

### For 3D Models
- [ ] 1 unit = 1 meter scale
- [ ] GLB format
- [ ] Under 4 MiB per model
- [ ] Properly UV unwrapped
- [ ] PBR materials where appropriate
- [ ] LOD versions for large objects
- [ ] Collision meshes for interactive objects

---

**Next Steps**:
1. Use these references to create accurate character portraits
2. Model architecture based on archaeological reconstructions
3. Ensure all costumes match historical descriptions
4. Verify all artwork against primary sources
