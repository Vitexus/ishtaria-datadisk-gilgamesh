# Atra-Hasis, the legend of the Mesopotamians

"Inuma ilu awilum", "When the gods were man": the Old Babylonian epic (c. 1650 BCE, on three tablets) of the labour of
the gods, the making of mankind, its noise and the flood. For the people of the disk it is what the story of Jesus is
for us: so well known that it is only alluded to. Sources read: Lambert & Millard, *Atra-Hasis: The Babylonian Story of the Flood* (Oxford 1969; the scan is
`research/atrahasisbabylon0000unse_1.pdf`, not committed), introduction and translation of tablets I-III; first
Wikipedia (Atra-Hasis; cs: Mýtus o Atrachasísovi), whose division of the plot between the tablets is wrong (it puts the
plague into tablet II). The translation is copyrighted, so the disk's texts are our own retelling of the plot and quote
nothing from it. The Old Babylonian text was copied by the scribe Ku-Aya (Sippar).

## Plot, by tablet (Lambert & Millard)

1. **Tablet I.** Anu, Enlil and Enki divide the world by lot; the junior gods (Igigi) dig the rivers and canals for the
   Anunnaki. After 40 years they burn their tools and surround Enlil's house, the Ekur of Nippur, by night. Enki
   proposes mankind; the mother goddess Mami (Nintu, Belet-ili) makes it of clay and the flesh and blood of the slain
   god We (We-ila); Enki treads the clay, fourteen birth goddesses shape seven men and seven women, born in the tenth
   month. Mankind multiplies, Enlil loses his sleep and sends plague (Namtar); Atra-Hasis, a king, is advised by his
   god Enki to have the elders offer to Namtar alone, and the plague ends.
2. **Tablet II.** The same again: Adad withholds the rain (famine, Nisaba), Enki advises Atra-Hasis, who succeeds;
   Enlil sets guards (Anu and Adad in heaven, himself on earth, Enki below). The middle is damaged (fish fall on the
   hungry). Enlil's council forbids any god to save mankind again; Enki laughs; the flood is decided and Enki is bound
   by an oath.
3. **Tablet III.** Atra-Hasis has a dream; Enki speaks to the reed hut ("Reed-hut! Wall!") to build a boat (pitch,
   animals and birds, seven days, the water clock set for the seventh night). Atra-Hasis tells the elders he goes to his
   god, holds a feast he cannot eat, boards. The flood lasts seven days; the hungry gods grieve, Mami blames Enlil and
   wears the lapis flies. Atra-Hasis offers; Enlil is angry at Enki and then accepts mankind if it is better ordered
   (women who bear no child, priestesses); the rest of the epilogue is lost.

The Gilgamesh epic (tablet XI) retells the flood with Utnapishtim; the Sumerian *Eridu Genesis* with Ziusudra.

## In the game

`places/atrahasis_tablets.yaml`: one tablet in each of Eridu (I), Nippur (II, the Ekur is Enlil's house) and Shuruppak (III), 22 m
east-south-east of the city's middle. Reading all three (`E`) earns `three_tablets` (`achievements.yaml`, `read_all`;
server migration `0069_place_reads.sql`). Each tablet's face carries the incipit and its number in real signs
(`models-src/atrahasis_tablets/`). Allusions in dialogue (idioms such as "the wall hears", offerings to Namtar alone)
are not written yet.
