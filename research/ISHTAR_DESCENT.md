# Ishtar's (Inanna's) Descent to the Netherworld

The legend of the goddess of Uruk who goes down to the land of no return, her sister Ereshkigal's realm, is told in two
traditions: the Sumerian poem "Inana's descent to the nether world" (about 1900-1600 BCE) and the Akkadian "Ishtar's
descent" (Kurnugi). The Akkadian text is known from three manuscripts: the oldest continuous one from the library of
Tiglath-pileser I at Assur (turn of the 12th to 11th century BCE), a younger one from the library of Ashurbanipal at
Nineveh (7th century BCE), and an 11-line school tablet from Assur (Czech Wikipedia). It is a compilation of Sumerian
motifs and of lines shared with the Gilgamesh epic, and much shorter than its Sumerian model. For the people of the
disk it is the story of their own city goddess and of why the dead do not come back.

## Sources read

* `research/academia/Ishtar_i_Underverdenen.pdf` - *Ištar i underverdenen*, the **Danish** translation from the Akkadian
  (Carstens, Christensen, Lundager Jensen) of the Nineveh version, the main source of the Akkadian episodes: lines
  1-138, from the decision to go down to Tammuz. (The project owner called it Dutch; it is Danish. No Dutch text
  is in `research/academia/`.)
* `research/ishtar_underground.txt` - M. Jastrow's English translation of the Akkadian descent (*The Civilization of
  Babylonia and Assyria*, 1915), **public domain**, so it may be quoted. It confirms the Danish text (Namtar and the
  sixty diseases; Asu-shu-namir; Cuthah; the return of the ornaments in reverse order; Tammuz's flute and Belili's
  lament) and differs in small things: there Shamash, not Papsukkal, goes weeping to Sin and Ea; Asu-shu-namir is
  called a eunuch and asks for the *khalziku* skin (the water bag).
* ETCSL (t.1.4.1), "Inana's descent to the nether world", Sumerian, read for the poem's plot (Ninshubur's instructions,
  Enlil and Nanna refuse, Enki's kurgarra and galatur, the galla, Dumuzid).
* Czech Wikipedia, "Sestup Ištary do podsvětí" (versions and manuscripts above; the Sumerian poem takes seven gates, the
  keeper Neti, Enlil and Nanna refuse, Enki revives her with the bread and water of life, the demons demand a substitute,
  Geshtinana shares Dumuzi's fate by half years).
* Wikipedia, "Ancient Mesopotamian underworld" (names Kur, Irkalla, Kurnugi; seven gates, the keeper Neti;
  Ereshkigal in Ganzir and Namtar her vizier; the dead eat dust, libations by clay pipe; no judgement of the dead;
  the galla, Dumuzid and Geshtinanna; Inanna goes to the funeral of Gugalanna).
* Black & Green, *Gods, Demons and Symbols of Ancient Mesopotamia*, on Dumuzi (worshipped at Uruk near Kuara).
* The translations are copyrighted; the disk's texts are our own retelling and quote nothing.

## The legend, by episode (as used by the disk)

1. **Leaving.** Ishtar decides to go to the house of darkness (dust for food, clay for bread, clothed in wings like
   birds); the Sumerian poem: she leaves heaven, earth and her temples for the funeral of Gugalanna; she charges
   Ninshubur to mourn and to seek help; at the gate she threatens to break it and raise the dead.
2. **The seven gates.** Ereshkigal turns green; at each gate Ishtar loses crown, earrings, necklace, breast
   ornament, girdle of birthstones, bracelets and anklets, robe; Namtar looses sixty sicknesses; in the Sumerian
   poem the Anunnaki judge her and she hangs as a corpse on a hook.
3. **Enlil refuses** (Sumerian; Nippur). Meanwhile the world is barren (Akkadian).
4. **Nanna-Sin refuses** (Sumerian; Ur); Papsukkal mourns to Sin and Ea (Akkadian).
5. **Enki helps** (Eridu): the kurgarra and galatur with the food and water of life (Sumerian); Asushunamir (Akkadian);
   Ereshkigal softens, Namtar sprinkles Ishtar with the water of life, the ornaments come back in reverse order.
6. **The substitute.** The galla follow Ishtar; Dumuzi is seized; Geshtinanna shares his fate; the Akkadian song turns to
   Tammuz, the flute of lapis lazuli and the rising of the dead.

## In the game

`places/ishtar_descent_tablets.yaml`: tablets 1, 2 and 6 in Uruk (near the Temple of Ishtar, Eanna and the pasture),
3 Nippur, 4 Ur, 5 Eridu. Reading all six earns `descent_tablets` ("Pilgrim of the Seven Gates"; `read_all`, server
migration `0069_place_reads.sql`). The six-part cutting and the strokes on each tablet are the disk's own; the sources do
not number the legend. The face carries KUR.NU.GI4, "Land of No Return" (`models-src/ishtar_descent_tablets/`).
The Uruk tablets have not been checked against the city's buildings. The disk already tells the descent in
`lore.descent_of_ishtar` and in the high priestess's dialogue; the tablets add to it.

The *khalziku* skin that Asu-shu-namir asks for (Jastrow; the Danish text has *vandsækken*, the water bag) is, in game terms, the
waterskin (item `waterskin`, server migration `0064_waterskin.sql`): tablet V and the elder woman's dialogue point at it.
No mechanic is attached to it.
