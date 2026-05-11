# pylint: disable=too-few-public-methods
"""Common auxiliary types for ADT"""

from xml.etree import ElementTree

from sap.adt.annotations import (
    xml_text,
    XmlListNodeProperty,
    XmlNodeAttributeProperty,
    OrderedClassMembers
)


XMLNS_NAMEDITEM = '{http://www.sap.com/adt/nameditem}'


class NamedItem:
    """A single item from a namedItemList response"""

    def __init__(self, name, description=None, data=None):
        self.name = name
        self.description = description
        self.data = data


class NamedItemList:
    """Parsed namedItemList XML response"""

    def __init__(self, total_item_count, items):
        self.total_item_count = total_item_count
        self.items = items

    def __iter__(self):
        return iter(self.items)

    @staticmethod
    def from_xml(xml_content):
        """Parse namedItemList XML into a NamedItemList instance"""

        root = ElementTree.fromstring(xml_content)

        total_count_elem = root.find(f'{XMLNS_NAMEDITEM}totalItemCount')
        total_count = int(total_count_elem.text) if total_count_elem is not None and total_count_elem.text else 0

        items = []
        for item_elem in root.findall(f'{XMLNS_NAMEDITEM}namedItem'):
            name_elem = item_elem.find(f'{XMLNS_NAMEDITEM}name')
            desc_elem = item_elem.find(f'{XMLNS_NAMEDITEM}description')
            data_elem = item_elem.find(f'{XMLNS_NAMEDITEM}data')

            name = name_elem.text if name_elem is not None else None
            description = desc_elem.text if desc_elem is not None and desc_elem.text else None
            data = data_elem.text if data_elem is not None and data_elem.text else None

            items.append(NamedItem(name, description, data))

        return NamedItemList(total_count, items)


class ADTTemplateProperty(metaclass=OrderedClassMembers):
    """A single property in an ADT template"""

    key = XmlNodeAttributeProperty('adtcore:key')

    def __init__(self, key=None, value=None):
        self.key = key
        self._value = value

    @xml_text()
    def value(self):
        """The property value (text content of the element)"""
        return self._value

    @value.setter
    def value(self, val):
        self._value = val


class ADTTemplate(metaclass=OrderedClassMembers):
    """ADT template containing a list of properties"""

    properties = XmlListNodeProperty('adtcore:adtProperty', value=[], factory=ADTTemplateProperty)

    def __init__(self, properties=None):
        if properties:
            self.__dict__['_adtcore_adtProperty'] = list(properties)
