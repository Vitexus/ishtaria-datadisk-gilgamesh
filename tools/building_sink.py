"""How deep each building model is sunk below the lowest ground of its plot (`sink_m` of a buildings item).

The 0 A.D. models do not share one floor level: a house is made to be raised on a slope (its walls end at the floor, its stair
starts at the origin), while the corral is a low fence with a shed whose posts stand on the origin. Every model has its own value
here, measured against the game's view of it; a model that is not listed keeps the server's default (3 m).
"""
import os

SINK_M = {
    # houses: the lowest stair at the level of the ground (checked in the client, 3 m)
    "pers_house_a": 3.0, "pers_house_b": 3.0, "pers_house_c": 3.0, "pers_house_d": 3.0,
    "pers_farmstead": 3.0, "pers_storehouse": 3.0, "pers_workshop": 3.0,
    # the shepherd's corral: a fence about 2.8 m tall in model units, so a sunken 2 m left 0.8 m of it above ground
    # and 3 m buried it; 1 m shows it whole.
    "pers_corral": 1.0,
    # the building sites are our own models, standing on the ground as they were made
    "uruk_site_a": 1.0, "uruk_site_b": 1.0, "uruk_site_c": 1.0, "uruk_site_d": 1.0,
}


def sink_for(model):
    """The `sink_m` of a model path, or None for the server's default."""
    return SINK_M.get(os.path.splitext(os.path.basename(model))[0])


def sink_field(model):
    """The `, sink_m: N` part of a buildings line (empty for a model that uses the default)."""
    value = sink_for(model)
    return "" if value is None else ", sink_m: %g" % value
