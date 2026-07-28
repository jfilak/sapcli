"""Enhancement Spot ADT wrappers"""

from typing import List

from sap.adt.objects import (
    xmlns_adtcore_ancestor,
    ADTObject,
    ADTObjectType,
    OrderedClassMembers,
    ADTObjectPropertyEditor,
)
from sap.adt.annotations import (
    XmlNodeAttributeProperty,
    XmlNodeProperty,
    XmlContainer,
)
from sap.adt.repository import Repository
# The enhancements core nodes (enhcore:referencedObject and the plain adtcore
# references) have the very same shape in Enhancement Spots as in Enhancement
# Implementations, so they are reused instead of being defined twice.
from sap.adt.enhancement_implementation import (
    ADTCoreReferenceSimple,
    EnhancementImplementation,
    ReferencedObjectContainer,
)


XMLNS_ENHS = xmlns_adtcore_ancestor('enhs', 'http://www.sap.com/adt/enhancements/enhs')


# pylint: disable=too-few-public-methods
class ContentCommon(metaclass=OrderedClassMembers):
    """The xml node enhs:contentCommon"""

    tool_type = XmlNodeAttributeProperty('enhs:toolType')
    internal = XmlNodeAttributeProperty('enhs:internal')
    internal_flag_editable = XmlNodeAttributeProperty('enhs:internalFlagEditable')

    usages = XmlNodeProperty('enhs:usages', factory=ReferencedObjectContainer)


# pylint: disable=too-few-public-methods
class BadiDefinition(metaclass=OrderedClassMembers):
    """The xml node enhs:badiDefinition"""

    name = XmlNodeAttributeProperty('enhs:name')
    short_text = XmlNodeAttributeProperty('enhs:shorttext')
    single_use = XmlNodeAttributeProperty('enhs:singleUse')
    use_fallback_class = XmlNodeAttributeProperty('enhs:useFallbackClass')
    filter_limitation = XmlNodeAttributeProperty('enhs:filterLimitation')
    documentation_id = XmlNodeAttributeProperty('enhs:documentationId')
    context_mode = XmlNodeAttributeProperty('enhs:contextMode')
    amdp = XmlNodeAttributeProperty('enhs:amdp')
    internal_use = XmlNodeAttributeProperty('enhs:internalUse')
    custom_logic_registered = XmlNodeAttributeProperty('enhs:customLogicRegistered')

    interface = XmlNodeProperty('enhs:interface', factory=ADTCoreReferenceSimple)


BadiDefinitionContainer = XmlContainer.define('enhs:badiDefinition', BadiDefinition)


# pylint: disable=too-few-public-methods
class BadiTechnology(metaclass=OrderedClassMembers):
    """The xml node enhs:badiTechnology"""

    definitions = XmlNodeProperty('enhs:badiDefinitions', factory=BadiDefinitionContainer)


# pylint: disable=too-few-public-methods
class ContentSpecific(metaclass=OrderedClassMembers):
    """The xml node enhs:contentSpecific"""

    badis = XmlNodeProperty('enhs:badiTechnology', factory=BadiTechnology)


class EnhancementSpot(ADTObject):
    """The ADT object Enhancement Spot"""

    OBJTYPE = ADTObjectType(
        'ENHS/XSB',
        'enhancements/enhsxsb',
        XMLNS_ENHS,
        ['application/vnd.sap.adt.enh.enhs.v2+xml'],
        {},
        'objectData',
        editor_factory=ADTObjectPropertyEditor
    )

    common = XmlNodeProperty('enhs:contentCommon', factory=ContentCommon)
    specific = XmlNodeProperty('enhs:contentSpecific', factory=ContentSpecific)

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package

    def get_implementations(self) -> List[str]:
        """Get a list of enhancement implementation names for this enhancement spot"""

        repo = Repository(self._connection)
        node = repo.read_node(self, nodekeys=['000000'])
        enhs_node_key = None
        for typ in node.types:
            if typ.OBJECT_TYPE == EnhancementImplementation.OBJTYPE.code:
                enhs_node_key = typ.NODE_ID

        if enhs_node_key is None:
            return []

        impls = repo.read_node(self, nodekeys=[enhs_node_key])
        return [impl.OBJECT_NAME for impl in impls.objects]
