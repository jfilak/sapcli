"""Odataservice ADT wrappers"""

from urllib.parse import quote_plus

from sap.errors import SAPCliError
from sap.adt.objects import (
    Class,
    xmlns_adtcore_ancestor,
    ADTObject,
    ADTRootObject,
    ADTObjectType,
    OrderedClassMembers,
    ADTObjectPropertyEditor
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
class ReferencedObject(ADTRootObject):
    """Usage object reference"""

    OBJTYPE = ADTObjectType(None, None, XMLNS_ENHCORE,
                            None, None, 'referencedObject')

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
                msg = f'BadiImplementation({self.name or ""}) holds invalid active: "{active_normalized}"'
                raise SAPCliError(msg)

    @is_active_implementation.setter
    def is_active_implementation(self, value: bool):
        """Enables or disables this BAdI implementation - disabled means it will not be called"""

        self.active = str(value).lower()


# pylint: disable=too-few-public-methods
class BadiImplementationContainer(metaclass=OrderedClassMembers):
    """The xml node BadiImplementations"""

    # Beware: the setter appends the value :(
    items = XmlListNodeProperty('enho:badiImplementation',
                                factory=BadiImplementation,
                                value=[])

    def __getitem__(self, value):
        for impl in self.items:
            if impl.name == value:
                return impl

        raise KeyError(value)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


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
        'objectData',
        editor_factory=ADTObjectPropertyEditor
    )

    common = XmlNodeProperty('enho:contentCommon', factory=ContentCommon)
    specific = XmlNodeProperty('enho:contentSpecific', factory=ContentSpecific)

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package

    def set_enhancement_spot(self, enhancement_spot: str):
        """Makes this object a new BAdI Enhancement Implementation
           of the given Enhancement Spot without any BAdI Implementation.
        """

        spot_reference = ReferencedObject()
        spot_reference.program_id = 'R3TR'
        spot_reference.element_usage = 'EXTO'
        spot_reference.object_reference = ADTCoreReferenceSimple()
        spot_reference.object_reference.typ = 'ENHS/XS'
        spot_reference.object_reference.name = enhancement_spot
        spot_reference.main_object_reference = ADTCoreReferenceSimple()

        self.common = ContentCommon()
        self.common.tool_type = 'BADI_IMPL'
        # pylint: disable=no-value-for-parameter
        self.common.usages = ReferencedObjectContainer()
        self.common.usages.append(spot_reference)

        self.specific = ContentSpecific()
        self.specific.badis = BadiTechnology()
        self.specific.badis.implementations = BadiImplementationContainer()

    def add_badi_implementation(self, name: str, badi_definition: str, implementing_class: str) -> BadiImplementation:
        """Adds a new active BAdI Implementation of the given BAdI Definition
           of the Enhancement Spot this Enhancement Implementation belongs to
           and returns it.
        """

        enhancement_spot = None
        if self.common is not None:
            # pylint: disable=not-an-iterable
            for usage in self.common.usages:
                if usage.element_usage == 'EXTO':
                    enhancement_spot = usage.object_reference.name

        if enhancement_spot is None:
            raise SAPCliError(f'The Enhancement Implementation {self.name} does not refer to any Enhancement Spot')

        spot_uri = f'/{self._connection.uri}/enhancements/enhsxsb/{quote_plus(enhancement_spot.lower())}'

        badi = BadiImplementation()
        badi.name = name
        badi.active = 'true'
        badi.customizing_lock = ''

        badi.enhancement_spot = ADTCoreReferenceSimple()
        badi.enhancement_spot.uri = spot_uri
        badi.enhancement_spot.typ = 'ENHS/XSB'
        badi.enhancement_spot.name = enhancement_spot

        badi.badi_definition = ADTCoreReferenceSimple()
        badi.badi_definition.uri = f'{spot_uri}#type=enhs%2fxb;name={quote_plus(badi_definition.lower())}'
        badi.badi_definition.typ = 'ENHS/XB'
        badi.badi_definition.name = badi_definition

        badi.implementing_class = ADTCoreReferenceSimple()
        badi.implementing_class.uri = Class(self._connection, implementing_class).full_adt_uri
        badi.implementing_class.typ = 'CLAS/OC'
        badi.implementing_class.name = implementing_class

        self.specific.badis.implementations.items.append(badi)

        return badi
