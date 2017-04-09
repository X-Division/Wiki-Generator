from io import StringIO
from xml.etree import ElementTree
import os
import re

defaults = {
    "has_header": True,
}

# TODO: Filter out XMLs, leave spreadsheets only
spreadsheets = {
    "AM_AirSuperiority.xml": dict(defaults, **{}),
    "AM_BaseAttack.xml": dict(defaults, **{}),
    "AM_BombingRun.xml": dict(defaults, **{}),
    "AM_Construction.xml": dict(defaults, **{}),
    "AM_GroundAttack.xml": dict(defaults, **{}),
    "AM_Research.xml": dict(defaults, **{}),
    "AM_Scout.xml": dict(defaults, **{}),
    "AM_SupplyRun.xml": dict(defaults, **{}),
    "AM_Terror.xml": dict(defaults, **{}),
    "aiprops.xml": dict(defaults, **{}),
    "aircrafts.xml": dict(defaults, **{}),
    "aircraftweapons.xml": dict(defaults, **{}),
    "ammos.xml": dict(defaults, **{}),
    "armours.xml": dict(defaults, **{}),
    "armours_gc.xml": dict(defaults, **{}),
    "buildings.xml": dict(defaults, **{}),
    "cities.xml": dict(defaults, **{}),
    "config.xml": dict(defaults, **{}),
    "config_level_editor.xml": dict(defaults, **{}),
    "corpseprops.xml": dict(defaults, **{}),
    "gameconfig.xml": dict(defaults, **{}),
    "gas_gc.xml": dict(defaults, **{}),
    "gcloading_tips.xml": dict(defaults, **{}),
    "gsgcitemtranslator.xml": dict(defaults, **{}),
    "initCharacters.xml": dict(defaults, **{}),
    "items.xml": dict(defaults, **{}),
    "levelsetup.xml": dict(defaults, **{}),
    "levelsetup_finalmission.xml": dict(defaults, **{}),
    "levelsetup_quickbattle.xml": dict(defaults, **{}),
    "manufactures - ORIGINAL.xml": dict(defaults, **{}),
    "manufactures.xml": dict(defaults, **{}),
    "missiontypeprops_gc.xml": dict(defaults, **{}),
    "moraleconfig_gc.xml": dict(defaults, **{}),
    "psioniceffects_gc.xml": dict(defaults, **{}),
    "psionicpowers_gc.xml": dict(defaults, **{}),
    "researches.xml": dict(defaults, **{
        "columns": 6
    }),
    "settings.xml": dict(defaults, **{}),
    "soldiernames.xml": dict(defaults, **{}),
    "soldiernamesfemale.xml": dict(defaults, **{}),
    "soldierprops.xml": dict(defaults, **{}),
    "sounds.xml": dict(defaults, **{}),
    "strings.xml": dict(defaults, **{
        "has_header": False,
        "columns": 1
    }),
    "tilerenderer.xml": dict(defaults, **{}),
    "vehicles.xml": dict(defaults, **{}),
    "vehicles_gc.xml": dict(defaults, **{}),
    "vehicleweapons.xml": dict(defaults, **{}),
    "vehicleweapons_gc.xml": dict(defaults, **{}),
    "weapons.xml": dict(defaults, **{
        "columns": 17
    }),
    "weapons_gc.xml": dict(defaults, **{}),
    "xenopedia.xml ": dict(defaults, **{
        "columns": 6
    }),
}


class SpreadSheet:
    def __init__(self, file, columns, has_header):
        self.file = file
        self.exists = True
        self.columns = columns
        self.has_header = has_header
        self.namespaces = {}
        self.data = {}

        if not os.path.exists(file):
            self.exists = False
            return

        with open(file) as handle:
            self.namespaces = dict([
                node for _, node in ElementTree.iterparse(
                    StringIO(handle.read()),
                    events=["start-ns"]
                )
            ])

        root = ElementTree.parse(file).getroot()
        rows = root.findall(
            "./ss:Worksheet/ss:Table/ss:Row",
            self.namespaces
        )

        if has_header:
            rows = rows[1:]

        for row in rows:
            values = [''] * self.columns

            current = 0
            items = list(row)

            if not len(items):
                continue

            key = items[0].findtext(
                "./ss:Data", "",
                self.namespaces
            ).strip()

            if not key:
                continue

            for item in items[1:]:
                index = item.get(
                    "{" + self.namespaces["ss"] + "}Index"
                )

                if index:
                    current = int(index) - 1

                if current >= self.columns:
                    break

                values[current] = item.findtext(
                    "./ss:Data", "",
                    self.namespaces
                ).strip()

                current += 1

            self[key] = values

    def apply(self, file):
        other = self.__class__(
            file,
            self.columns,
            self.has_header
        )

        if other.exists:
            for key, value in other.data.items():
                self[key] = value

    def __setitem__(self, key, value):
        if all(item == '' for item in value):
            self.data.pop(key, None)
        elif key in self:
            pattern = re.compile("MODMERGE([A-Z]+):(.*?)(?=MODMERGE|$)")

            for index, item in enumerate(value):
                matches = re.findall(pattern, item)

                if matches:
                    functions = dict(
                        (function.lower(), text) for function, text in matches
                    )

                    if "replace" in functions:
                        current_item = self.data[key][index]

                        if "with" in functions:
                            self.data[key][index] = current_item.replace(
                                functions["replace"],
                                functions["with"],
                                1
                            )
                        elif "allwith" in functions:
                            self.data[key][index] = current_item.replace(
                                functions["replace"],
                                functions["allwith"]
                            )
                    if "append" in functions:
                        self.data[key][index] += functions["append"]
                else:
                    self.data[key][index] = item
        else:
            self.data[key] = value

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, item):
        return self.data[item]


class XML:
    def __init__(self, file):
        self.exists = True

        if not os.path.exists(file):
            self.exists = False
            return

        self.data = ElementTree.parse(file)

    def match(self, tree, element, is_root=False):
        if is_root:
            if tree.tag == element.tag:
                children = element.findall("./*")

                for child in children:
                    self.match(tree, child)

        else:
            if "MODMERGEATTRIBUTE" in element.attrib:
                attribute = element.attrib["MODMERGEATTRIBUTE"]
                value = element.attrib[attribute]
                attribute_selector = "[@%s='%s']" % (
                    attribute,
                    value
                )
            else:
                attribute_selector = ""

            selector = "./%s%s" % (
                element.tag,
                attribute_selector,
            )

            match = tree.findall(selector)

            if "MODMERGE" in element.attrib:
                method = element.attrib["MODMERGE"]
            else:
                method = "undefined"

            caller = getattr(
                self,
                "modmerge_" + method
            )
            caller(tree, element, match)

    def apply(self, file):
        other = self.__class__(file)

        if other.exists:
            self.match(self.data.getroot(), other.data.getroot(), True)

    def overwrite(self, file):
        other = self.__class__(file)

        if other.exists:
            self.data = other.data

    def modmerge_undefined(self, tree, element, match):
        if not match:
            self.modmerge_insert(tree, element, match)
        elif len(match) == 1:
            children = element.findall('./*')

            for child in children:
                self.match(match[0], child)

    def modmerge_insert(self, tree, element, match):
        if len(match):
            raise Exception("Can't insert element. Matching element found.")

        tree.append(element)

    def modmerge_update(self, tree, element, match):
        if len(match) != 1:
            raise Exception("No match or match ambiguous.")

        for attribute, value in element.attrib.items():
            match[0].set(attribute, value)
        match[0].text = element.text

        children = element.findall("./*")
        for child in children:
            self.match(match[0], child)

    def modmerge_replace(self, tree, element, match):
        if not match:
            raise Exception("Can't replace element. Target not found.")

        tree.remove(match[0])
        tree.append(element)

    def modmerge_delete(self, tree, element, match):
        if not match:
            raise Exception("Can't delete element. Target not found.")

        tree.remove(match[0])

    def modmerge_replaceifexists(self, tree, element, match):
        raise Exception("STUB: Not implemented")

    def modmerge_insertreplace(self, tree, element, match):
        raise Exception("STUB: Not implemented")

    def modmerge_deleteall(self, tree, element, match):
        raise Exception("STUB: Not implemented")

    def modmerge_updateifexists(self, tree, element, match):
        raise Exception("STUB: Not implemented")

    def modmerge_updateall(self, tree, element, match):
        raise Exception("STUB: Not implemented")


class Binary:
    def __init__(self, file):
        pass
