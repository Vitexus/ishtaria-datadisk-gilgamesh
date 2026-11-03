"""Which model draws which house of the city plan (tools/data/uruk_city.json).

Shared by models-src/architecture/uruk_city.py (the quarter models leave out the houses drawn otherwise) and
tools/build_buildings.py (buildings/uruk.yaml lists those houses as separate buildings).

  orig    the datadisk's own house, baked into the quarter model (smithies always)
  zeroad  a finished house of the 0 A.D. Persian set (CC BY-SA 3.0, media/models/architecture/zeroad/)
  site    a house still being built (media/models/architecture/uruk_site_*.glb)

The choice is a function of the house's seed alone, so the same plan always gives the same city.
"""


def kind_of(rec):
    """`rec` is a row of the plan's `houses` (see its `house_fields`)."""
    seed, smithy = rec[9], rec[10]
    if smithy:
        return "orig"
    if seed % 17 == 0:
        return "site"
    if seed % 3 == 0:
        return "zeroad"
    return "orig"
