"""ABAP Domain ADT functionality module"""

from sap.adt.objects import ADTObject, ADTObjectType
from sap.adt.annotations import (
    OrderedClassMembers,
    xml_text_node_property,
    XmlNodeProperty,
    XmlListNodeProperty,
    XmlNodeAttributeProperty,
)
from sap.adt.objects import XMLNamespace, XMLNS_ADTCORE

XMLNS_DOMA = XMLNamespace('doma', 'http://www.sap.com/dictionary/domain', parents=[XMLNS_ADTCORE])


class DomainTypeInformation(metaclass=OrderedClassMembers):
    """Domain type information"""

    datatype = xml_text_node_property('doma:datatype')
    length = xml_text_node_property('doma:length')
    decimals = xml_text_node_property('doma:decimals')


class DomainOutputInformation(metaclass=OrderedClassMembers):
    """Domain output information"""

    length = xml_text_node_property('doma:length')
    style = xml_text_node_property('doma:style')
    conversion_exit = xml_text_node_property('doma:conversionExit')
    sign_exists = xml_text_node_property('doma:signExists')
    lowercase = xml_text_node_property('doma:lowercase')
    ampm_format = xml_text_node_property('doma:ampmFormat')


class DomainFixValue(metaclass=OrderedClassMembers):
    """Domain fixed value"""

    position = xml_text_node_property('doma:position')
    low = xml_text_node_property('doma:low')
    high = xml_text_node_property('doma:high')
    text = xml_text_node_property('doma:text')


class DomainValueTableRef(metaclass=OrderedClassMembers):
    """Domain value table reference"""

    name = XmlNodeAttributeProperty('adtcore:name')
    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')


class DomainValueInformation(metaclass=OrderedClassMembers):
    """Domain value information"""

    value_table_ref = XmlNodeProperty('doma:valueTableRef', factory=DomainValueTableRef)
    append_exists = xml_text_node_property('doma:appendExists')
    fix_values = XmlListNodeProperty('doma:fixValues/doma:fixValue', factory=DomainFixValue)


class DomainContent(metaclass=OrderedClassMembers):
    """Domain content"""

    type_information = XmlNodeProperty('doma:typeInformation', factory=DomainTypeInformation)
    output_information = XmlNodeProperty('doma:outputInformation', factory=DomainOutputInformation)
    value_information = XmlNodeProperty('doma:valueInformation', factory=DomainValueInformation)


class Domain(ADTObject):
    """ABAP Domain"""

    OBJTYPE = ADTObjectType(
        'DOMA/DD',
        'ddic/domains',
        XMLNS_DOMA,
        'application/vnd.sap.adt.domains.v2+xml',
        {'application/vnd.sap.adt.domains.v2+xml': ''},
        'domain',
        editor_factory=None
    )

    content = XmlNodeProperty('doma:content', factory=DomainContent)

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata, active_status='active')

        self._metadata.package_reference.name = package
        self.content = DomainContent()
        self.content.type_information = DomainTypeInformation()
        self.content.output_information = DomainOutputInformation()
        self.content.value_information = DomainValueInformation()
