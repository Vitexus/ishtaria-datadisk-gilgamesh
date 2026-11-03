# Atra-Hasis, the legend of the Mesopotamians

"Inuma ilu awilum", "When the gods were man": the Old Babylonian epic (c. 1650 BCE, on three tablets) of the labour of
the gods, the making of mankind, its noise and the flood. For the people of the disk it is what the story of Jesus is
for us: so well known that it is only alluded to. Sources read: Wikipedia (Atra-Hasis; cs: Mýtus o Atrachasísovi);
the standard translation is Lambert & Millard, *Atra-Hasis* (Oxford 1969), and Foster, *Before the Muses*. Those
translations are copyrighted, so the disk's texts are our own retelling of the plot and quote nothing from them.

## Plot (as used by the disk)

1. **Tablet I.** The lesser gods (Igigi) dig canals for the Anunnaki; after 40 years they rebel and surround Enlil's
   house. Enki and the birth goddess Mami make mankind of clay and the flesh and blood of the slain god Geshtu-e
   (We-ila), to carry the basket in the gods' place.
2. **Tablet II.** After 1200 years the noise of mankind keeps Enlil from sleep: he sends plague (Namtar), then
   drought and hunger (Adad, Nisaba). Enki tells Atra-Hasis to offer to that god alone, and the god gives way.
3. **Tablet III.** Enlil decrees the flood and binds Enki by oath; Enki speaks to the reed wall of Atra-Hasis's house
   and tells him to build a boat. After the storm Enki sets the limits of mankind: death, barren women, celibate
   priestesses.

The Gilgamesh epic (tablet XI) retells it with Utnapishtim; the Sumerian *Eridu Genesis* with Ziusudra.

## In the game

`places/atrahasis_tablets.yaml`: one tablet in each of Eridu (I), Nippur (II) and Shuruppak (III), 22 m
east-south-east of the city's middle. Reading all three (`E`) earns `three_tablets` (`achievements.yaml`, `read_all`;
server migration `0069_place_reads.sql`). Each tablet's face carries the incipit and its number in real signs
(`models-src/atrahasis_tablets/`). Allusions in dialogue (idioms such as "the wall hears", offerings to Namtar alone)
are not written yet.
