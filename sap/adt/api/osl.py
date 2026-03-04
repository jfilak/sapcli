"""ADT API OSL - Object Set Definitions

# <osl:objectSet
#    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#    xmlns:osl="http://www.sap.com/api/osl"
#    xsi:type="osl:flatObjectSet">
#
#   <osl:object type="PROG|CLAS name="OBJECT_NAME""/>
#
#  </osl:objectSet>

fls = FlatObjectSet()
fls.append("PROG", "OBJECT_NAME")

#  <osl:objectSet
#     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#     xmlns:osl="http://www.sap.com/api/osl"
#     xsi:type="osl:multiPropertySet">
#
#    <osl:property key="package" value="SOOL"/>
#
#  </osl:objectSet>

fls = MultiPropertyObjectSet()
fls.append("package", "SOOL")
"""

from sap.adt.objects import XMLNamespace, ADTObjectType
from sap.adt.annotations import (
    OrderedClassMembers,
    XmlNodeAttributeProperty,
    xml_element,
)


XMLNS_XSI = XMLNamespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
XMLNS_OSL = XMLNamespace('osl', 'http://www.sap.com/api/osl', parents=[XMLNS_XSI])


# pylint: disable=too-few-public-methods
class AAAObjectSet(metaclass=OrderedClassMembers):
    """Base class for OSL object set definitions"""

    objtype = ADTObjectType(None, None, XMLNS_OSL, None, None, 'objectSet')

    xsi_type = XmlNodeAttributeProperty('xsi:type')

    def __init__(self, typ):
        self.xsi_type = typ
        self._contents = []


class MultiPropertyObjectSet(AAAObjectSet):
    """OSL multi-property object set (e.g. packages)"""

    # pylint: disable=too-few-public-methods
    class SetProperty(metaclass=OrderedClassMembers):
        """Node with the attributes key and value."""

        key = XmlNodeAttributeProperty('key')
        value = XmlNodeAttributeProperty('value')

        def __init__(self, key=None, value=None):
            self.key = key
            self.value = value

    def __init__(self):
        super().__init__('osl:multiPropertySet')

    @xml_element('osl:property')
    def properties(self):
        """Returns the list of set properties"""
        return self._contents

    def append(self, key: str, value: str) -> "MultiPropertyObjectSet":
        """Appends a key-value property to the set"""
        self._contents.append(MultiPropertyObjectSet.SetProperty(key, value))
        return self

    def add_package(self, name: str) -> "MultiPropertyObjectSet":
        """Appends a package property to the set"""
        return self.append('package', name)


class FlatObjectSet(AAAObjectSet):
    """OSL flat object set (e.g. classes, programs)"""

    # pylint: disable=too-few-public-methods
    class SetObject(metaclass=OrderedClassMembers):
        """Node with the attributes name and type."""

        name = XmlNodeAttributeProperty('name')
        abaptype = XmlNodeAttributeProperty('type')

        def __init__(self, name=None, abaptype=None):
            self.name = name
            self.abaptype = abaptype

    def __init__(self):
        super().__init__('osl:flatObjectSet')

    @xml_element('osl:object')
    def objects(self):
        """Returns the list of set objects"""
        return self._contents

    def append(self, abaptype: str, name: str) -> "FlatObjectSet":
        """Appends an object with given type and name to the set"""
        self._contents.append(FlatObjectSet.SetObject(name, abaptype))
        return self
