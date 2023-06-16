"""Odataservice ADT wrappers"""

from sap.errors import SAPCliError
from sap.adt.objects import (
    xmlns_adtcore_ancestor,
    ADTObject,
    ADTObjectType,
    OrderedClassMembers
)
from sap.adt.annotations import (
    XmlNodeAttributeProperty,
    XmlListNodeProperty,
    XmlNodeProperty,
    XmlContainer
)


XMLNS_ENHO = xmlns_adtcore_ancestor('enho', 'http://www.sap.com/adt/enhancements/enho')
XMLNS_ENHCORE = xmlns_adtcore_ancestor('enhcore', 'http://www.sap.com/abapsource/enhancementscore')


# pylint: disable=too-few-public-methods
class ADTCoreReferenceSimple(metaclass=OrderedClassMembers):
    """Usage object reference values"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')
    name = XmlNodeAttributeProperty('adtcore:name')


# pylint: disable=too-few-public-methods
class ReferencedObject(metaclass=OrderedClassMembers):
    """Usage object reference"""

    program_id = XmlNodeAttributeProperty('enhcore:program_id')
    element_usage = XmlNodeAttributeProperty('enhcore:element_usage')
    upgrade = XmlNodeAttributeProperty('enhcore:upgrade')
    automatic_transport = XmlNodeAttributeProperty('enhcore:automatic_transport')

    object_reference = XmlNodeProperty('enhcore:objectReference', factory=ADTCoreReferenceSimple)
    main_object_reference = XmlNodeProperty('enhcore:mainObjectReference', factory=ADTCoreReferenceSimple)


ReferencedObjectContainer = XmlContainer.define('enhcore:referencedObject', ReferencedObject)


# pylint: disable=too-few-public-methods
class ContentCommon(metaclass=OrderedClassMembers):
    """The xml node ContentCommon"""

    tool_type = XmlNodeAttributeProperty('enho:toolType')
    adjustment_status = XmlNodeAttributeProperty('enho:adjustmentStatus')
    upgrade_flag = XmlNodeAttributeProperty('enho:upgradeFlag')
    switch_supported = XmlNodeAttributeProperty('enho:switchSupported')
    usages = XmlNodeProperty('enho:usages', factory=ReferencedObjectContainer)


# pylint: disable=too-few-public-methods
class BadiImplementation(metaclass=OrderedClassMembers):
    """The xml node BadiImplementation"""

    name = XmlNodeAttributeProperty('enho:name')
    short_text = XmlNodeAttributeProperty('enho:shortText')
    example = XmlNodeAttributeProperty('enho:example')
    default = XmlNodeAttributeProperty('enho:default')
    active = XmlNodeAttributeProperty('enho:active')
    customizing_lock = XmlNodeAttributeProperty('enho:customizingLock')
    runtime_behavior_shorttext = XmlNodeAttributeProperty('enho:runtimeBehaviorShorttext')

    enhancement_spot = XmlNodeProperty('enho:enhancementSpot', factory=ADTCoreReferenceSimple)
    badi_definition = XmlNodeProperty('enho:badiDefinition', factory=ADTCoreReferenceSimple)
    implementing_class = XmlNodeProperty('enho:implementingClass', factory=ADTCoreReferenceSimple)

    @property
    def is_active_implementation(self) -> bool:
        """Returns logical true if the BAdI implementation will be called; otherwise false.

           Raises:
            - SAPCliError if the ADT Backed returned an unexpected value
        """

        active_normalized = self.active.lower() if self.active else ''

        match active_normalized:
            case 'true':
                return True
            case 'false':
                return False
            case _:
                msg = f'BadiImplementatiod({self.name or ""}) holds invalid active: "{active_normalized}"'
                raise SAPCliError(msg)

    @is_active_implementation.setter
    def is_active_implementation(self, value: bool):
        """Enables or disables this BAdI implementation - disabled means it will not be called"""

        self.active = str(value).lower()


# pylint: disable=too-few-public-methods
class BadiImplementationContainer(metaclass=OrderedClassMembers):
    """The xml node BadiImplementations"""

    # Beware: the setter appends the value :(
    _items = XmlListNodeProperty('enho:badiImplementation',
                                 factory=BadiImplementation,
                                 value=[])

    def __getitem__(self, value):
        for impl in self._items:
            if impl.name == value:
                return impl

        raise KeyError(value)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


# pylint: disable=too-few-public-methods
class BadiTechnology(metaclass=OrderedClassMembers):
    """The xml node BadiTechnology"""

    implementations = XmlNodeProperty('enho:badiImplementations', factory=BadiImplementationContainer)


# pylint: disable=too-few-public-methods
class ContentSpecific(metaclass=OrderedClassMembers):
    """The xml node ContentSpecific"""

    badis = XmlNodeProperty('enho:badiTechnology', factory=BadiTechnology)


class EnhancementImplementation(ADTObject):
    """The ADT object Enhancement Implementation"""

    OBJTYPE = ADTObjectType(
        'ENHO/XHB',
        'enhancements/enhoxhb',
        XMLNS_ENHO,
        ['application/vnd.sap.adt.enh.enhoxhb.v4+xml',
         'application/vnd.sap.adt.enh.enhoxhb.v3+xml'],
        {},
        'objectData'
    )

    common = XmlNodeProperty('enho:contentCommon', factory=ContentCommon)
    specific = XmlNodeProperty('enho:contentSpecific', factory=ContentSpecific)

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
