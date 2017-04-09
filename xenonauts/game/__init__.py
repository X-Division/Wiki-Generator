import os

import xenonauts.game.assets


class Game:
    def __init__(self, path, mods):
        self.path = path
        self.mods = mods

    def get_spreadsheet(self, file):
        spreadsheet = xenonauts.game.assets.SpreadSheet(
            "%s/assets/%s" % (self.path, file),
            **xenonauts.game.assets.spreadsheets[file]
        )
        for mod, strategy in self.mods.items():
            caller = getattr(spreadsheet, strategy["spreadsheet"])
            caller(
                "%s/assets/mod/%s/%s" % (self.path, mod, file)
            )
        return spreadsheet

    def get_xml(self, file):
        xml = xenonauts.game.assets.XML(
            "%s/assets/%s" % (self.path, file)
        )
        for mod, strategy in self.mods.items():
            caller = getattr(xml, strategy["xml"])
            caller(
                "%s/assets/mod/%s/%s" % (self.path, mod, file)
            )
        return xml

    def get_image(self, file):
        for mod in list(self.mods.keys())[::-1]:
            mod_path = "%s/assets/mods/%s/%s.png" % (self.path, mod, file)
            if os.path.exists(mod_path):
                return mod_path

        base_path = "%s/assets/%s.png" % (self.path, file)
        if os.path.exists(base_path):
            return base_path

