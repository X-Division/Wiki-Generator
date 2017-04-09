#!/usr/bin/env python3.6

import xenonauts

"""
TODO: command line input parser
"""
XENONAUTS_PATH = "/Applications/Xenonauts.app/drive_c/Program Files/Xenonauts"

defaults = {
    "spreadsheet": "apply",
    "xml": "apply",
    "binary": "overwrite",
}

registered_mods = {
    "xce": dict(defaults, **{
        "xml": "overwrite",
    }),
    "xcesettings": dict(defaults, **{}),
    "xcebalance": dict(defaults, **{}),
    "xceextramaps": dict(defaults, **{}),
    "Skitso's Ultimate Megamix Map Pack 2000": dict(defaults, **{}),
    "Skitso's Improved Tile Art Pack": dict(defaults, **{}),
    "Skitso's Alien Base Booster Pack": dict(defaults, **{}),
    "Restored Community Map Pack": dict(defaults, **{}),
    "Random Map Pack Farm Edition": dict(defaults, **{}),
    "Random Map Pack Desert Style": dict(defaults, **{}),
    "Random Map Pack Arctic Collection": dict(defaults, **{}),
    "Khall's Tundra Tileset": dict(defaults, **{}),
    "X-Division 0.99 Beta": dict(defaults, **{}),
}

game = xenonauts.game.Game(XENONAUTS_PATH, registered_mods)
strings = game.get_spreadsheet("strings.xml")
weapons_gc = game.get_xml("weapons_gc.xml")
image = game.get_image("tiles/farm/hedge/HedgeSW_damaged")

