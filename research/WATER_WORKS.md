# Water works of Early Dynastic Sumer (reference for the models)

## Sources

* `research/warers.png` - a reconstruction drawing of a Sumerian irrigation scheme with its Sumerian terms (the drawing's
  source is not named in the file): `id` canal/river, `nagkud` settling reservoir, `ka` mouth of the nagkud, `kun` tail of
  the canal or outlet of the nagkud, `kunzida` weir or dam, `gu` bank, `asa` field, `kiri` orchard, `e` house, `ganun`
  storehouse. A canal feeds a settling basin (two eddies in the drawing show the water settling) through a gated mouth;
  the outlet, behind a weir, feeds branch canals running between plots of furrowed fields; orchards and houses stand on
  the dry ground, the storehouse beside the houses.
* Fassbinder, "Beneath the Euphrates Sediments: Magnetic Traces of the Mesopotamian Megacity Uruk-Warka", The Ancient Near
  East Today 8.6 (June 2020), saved as `research/Beneath the Euphrates Sediments_...html`: the magnetometer survey of
  Uruk 2001-2002 and 2016-2019 found a main canal 10 m wide (traced for 400 m) with smaller canals branching west, canals of
  three or four widths down to field irrigation canals; two E-W structures that guide or block the canal (not visible on
  the ground; a weir or regulator is a reading, the article only says they "control or guide" the water); the south wall
  about 9 m thick in a complex nearly 40 m wide with the canal running just outside; a south-west gate nearly 15 m wide,
  read as a floodgate where the inner city's canals flowed out, flanked by towers; below it a side canal to a small
  harbour in front of a fired-brick building. The Euphrates sediments are salty and clayey.

## The models (`models-src/architecture/irrigation_works.py`)

| Model | What |
| --- | --- |
| `irrigation_nagkud.glb` | the settling reservoir: an embankment basin 36 x 24 m with a gated mouth (`ka`), an outlet (`kun`) behind a weir, two eddy rings in the water |
| `irrigation_weir.glb` | the weir (`kunzida`) across a 10 m canal: a low brick sill on timber piles with a reed-fascine apron |
| `irrigation_works.glb` | the whole scheme of the drawing: the canal, the nagkud, the weir, branch canals, furrowed fields, an orchard, houses and a storehouse (about 140 x 100 m) |

Metres, +Y up, origin on the ground in the middle of the main canal at the mouth. The water is a flat translucent plane in
the model; there is no collision.

## Where they stand

`tools/find_irrigation_sites.py` looks for sites along the **documented** canals only (the primary canals of the Eridu region, the survey
canals between Uruk and Larsa, the channel network of Jotheri et al. 2018; not the canals of the splay template, which is a modern analogue,
research/RIVER_NETWORK.md) and `tools/place_irrigation_works.py` lays the scheme at three of them (`places/irrigation_works.yaml`,
`buildings/irrigation_works_*.yaml`): near Uruk (canal `jotheri_176`, 1.9 km north of the tell), near Eridu (`eridu_canal_105`, 492 m from the
city) and near Larsa (`canal_w2`, 1.8 km from the city). The other sites (264 in all, at least 1.5 km apart) are in `research/IRRIGATION_SITES.md`.
The field plots of `buildings/uruk_fields.yaml` that stood in the footprint at Uruk were taken out (5); run `tools/place_irrigation_works.py`
again after `tools/build_fields.py`, which would put them back. The footprint in the buildings file is 100 m (the schema's limit), the scheme is
150 m along the canal; it is passable, nothing collides.
