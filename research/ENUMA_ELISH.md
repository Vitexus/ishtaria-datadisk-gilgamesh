# Enuma Elish, the Babylonian epic of creation

"Enuma elis", "When on high": seven tablets, about a thousand lines, the creation epic of Babylon. Marduk kills
Tiamat, makes the world of her body and mankind of the blood of Kingu, receives the kingship of the gods, Babylon and
Esagila, and fifty names. For the people of the disk it is the story of their New Year.

## Akitu, the festival

Told by the project owner and confirmed by Frahm (Orient 45, 2010): the epic was the cult legend of the Akitu
festival, at the beginning of the year in the month Nisannu, and was recited in the temple of Babylon; the festival
ended in a procession of Marduk to the Akitu house north of Babylon. The most detailed ritual text is Hellenistic; the
earlier shape is probably similar. In our time the nearest thing is Christmas: the whole city takes part, the story is
told and acted out in the temples, and everyone knows it. (How much of the recital was drama is debated; the disk
follows the project owner: it was staged as a performance.) Not implemented: a festival date or event; the server has
no calendar events (only the solar clock), so for now the festival can only be alluded to.

## Dating, honestly

Most likely written in the twelfth century BCE (Lambert, in Frahm 2010), under the second dynasty of Isin, after
Nebuchadnezzar I brought Marduk's statue back from Elam; the oldest manuscripts are Assyrian (Assur, about 900 BCE),
most library tablets are from seventh-century Nineveh. The disk is set in the Early Dynastic time (about 2700 BCE), so
the epic and Babylon's rise are later than its present. The disk accepts such overlays (Babylon, Achaemenid ancestors),
so the epic stays; the cards mention the date where it is useful.

## Sources read (research/academia/)

* `The_Enuma_Elish.pdf` - an abridged translation after Speiser (ANET), tablets I, IV, V (part), VI (part); not
  copied, retold in our own words.
* Frahm, "Counter-texts, Commentaries, and Adaptations", Orient 45 (2010): plot summary, date, Akitu, Assyrian recension.
* Frahm, "Enuma Elish outside the cuneiform tradition", in Haubold et al. (eds), *Enuma Elish* (2024, CC BY-NC-ND).
* Talon, "Enuma Elis and the transmission of Babylonian cosmology to the West", Melammu Symposia 2.
* Wikipedia (Enuma Elis), for the plot of tablets II, III, V, VII, which the abridged translation lacks.
* Not about the epic, although the file name suggests it: `Tablets_from_the_Sippar_Library_XIII_Enu*.pdf` is *Enuma Anu
  Ellil* XX, the eclipse omens.

## Plot by tablet (as used by the disk)

1. **I.** Apsu and Tiamat; the gods born; the noise; Apsu and Mummu plan to destroy them, Tiamat refuses; Ea slays Apsu
   and builds his house over him; Marduk is born; Tiamat makes eleven monsters, Kingu gets the Tablet of Destinies.
2. **II.** Ea warns; Anu is sent and turns back; Marduk agrees to fight if made supreme.
3. **III.** Gaga is sent to Lahmu and Lahamu; the gods feast and grant Marduk his terms.
4. **IV.** Enthronement, the cloth test, weapons, the four winds; the fight; Tiamat split, half is the sky.
5. **V.** Stars, calendar, moon, clouds, rain, Tigris and Euphrates; the least preserved tablet.
6. **VI.** Mankind from the blood of Kingu; the gods are freed; Babylon and Esagila; the feast; the first names.
7. **VII.** The rest of the fifty names.

## In the game

`places/enuma_elish_tablets.yaml`: I Eridu, II Nippur, III Kish, IV and VI Babylon (Etemenanki), V Uruk, VII Assur.
Reading all seven earns `seven_tablets` ("Reciter of the Akitu"; `read_all`, server migration `0069_place_reads.sql`).
Faces carry the colophon "DUB n KAM" and the incipit "e-nu-ma e-lis" (`models-src/enuma_elish_tablets/`).
Distances from Uruk are large for tablets IV and VI (Babylon, 177 km) and VII (Assur); not yet reachable by walking.
The Uruk tablet (V) is 30 m from the middle of the city at bearing 160; not yet checked against the city's buildings.
Allusions in dialogue (the Akitu, "when on high", Marduk's fifty names) are not written yet.
