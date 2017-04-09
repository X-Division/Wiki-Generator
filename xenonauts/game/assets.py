from io import StringIO
from xml.etree import ElementTree
import os
import re


class SpreadSheet:
    def __init__(self, file, columns, has_header=True):
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

                values[current] = item.findtext(
                    "./ss:Data", "",
                    self.namespaces
                ).strip()

                current += 1

                if current >= self.columns:
                    break

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
        print("MATCH:", element.tag, element.attrib)
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
        print("INSERT:", element.tag, element.attrib)

        tree.append(element)

    def modmerge_update(self, tree, element, match):
        if len(match) != 1:
            raise Exception("No match or match ambiguous.")
        print("UPDATE:", element.tag, element.attrib)

        for attribute, value in element.attrib.items():
            match[0].set(attribute, value)
        match[0].text = element.text

        children = element.findall("./*")
        for child in children:
            self.match(match[0], child)

    def modmerge_replace(self, tree, element, match):
        if not match:
            raise Exception("Can't replace element. Target not found.")
        print("REPLACE:", element.tag, element.attrib)

        tree.remove(match[0])
        tree.append(element)

    def modmerge_delete(self, tree, element, match):
        if not match:
            raise Exception("Can't delete element. Target not found.")
        print("DELETE:", element.tag, element.attrib)

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
