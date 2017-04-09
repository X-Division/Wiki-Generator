#!/usr/bin/env python3.6

import xenonauts

"""
TODO: command line input parser
"""
XENONAUTS_PATH = "/Applications/Xenonauts.app/drive_c/Program Files/Xenonauts"

default_configuration = {
    "spreadsheet": "apply",
    "xml": "apply",
}

registered_mods = {
    "xce": dict(default_configuration, **{
        "xml": "overwrite",
    }),
    "xcesettings": dict(default_configuration, **{}),
    "xcebalance": dict(default_configuration, **{}),
    "xceextramaps": dict(default_configuration, **{}),
    "Skitso's Ultimate Megamix Map Pack 2000": dict(default_configuration, **{}),
    "Skitso's Improved Tile Art Pack": dict(default_configuration, **{}),
    "Skitso's Alien Base Booster Pack": dict(default_configuration, **{}),
    "Restored Community Map Pack": dict(default_configuration, **{}),
    "Random Map Pack Farm Edition": dict(default_configuration, **{}),
    "Random Map Pack Desert Style": dict(default_configuration, **{}),
    "Random Map Pack Arctic Collection": dict(default_configuration, **{}),
    "Khall's Tundra Tileset": dict(default_configuration, **{}),
    "X-Division 0.99 Beta": dict(default_configuration, **{}),
}

"""
Debug
"""
strings = xenonauts.game.assets.SpreadSheet(XENONAUTS_PATH + "/assets/strings.xml", columns=1, has_header=False)
for mod, config in registered_mods.items():
    caller = getattr(strings, config["spreadsheet"])
    caller(XENONAUTS_PATH + "/assets/mods/" + mod + "/strings.xml")

researches = xenonauts.game.assets.SpreadSheet(XENONAUTS_PATH + "/assets/researches.xml", columns=6)
for mod, config in registered_mods.items():
    caller = getattr(researches, config["spreadsheet"])
    caller(XENONAUTS_PATH + "/assets/mods/" + mod + "/researches.xml")

weapons_gc = xenonauts.game.assets.XML(XENONAUTS_PATH + "/assets/weapons_gc.xml")
for mod, config in registered_mods.items():
    caller = getattr(weapons_gc, config["xml"])
    caller(XENONAUTS_PATH + "/assets/mods/" + mod + "/weapons_gc.xml")
