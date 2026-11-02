"""ABAP Domain ADT functionality module"""

# pylint: disable=too-few-public-methods

from sap.adt.objects import ADTObject, ADTObjectType, ADTObjectPropertyEditor
from sap.adt.annotations import (
    OrderedClassMembers,
    xml_text_node_property,
    XmlContainer,
    XmlListNodeProperty,
    XmlNodeProperty,
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


class DomainFixValues(XmlContainer):
    """List of domain fixed values"""

    items = XmlListNodeProperty('doma:fixValue', factory=DomainFixValue, value=[])


class DomainValueTableRef(metaclass=OrderedClassMembers):
    """Domain value table reference"""

    name = XmlNodeAttributeProperty('adtcore:name')
    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')


class DomainValueInformation(metaclass=OrderedClassMembers):
    """Domain value information"""

    value_table_ref = XmlNodeProperty('doma:valueTableRef', factory=DomainValueTableRef)
    append_exists = xml_text_node_property('doma:appendExists')
    fix_values = XmlNodeProperty('doma:fixValues', factory=DomainFixValues)


class DomainContent(metaclass=OrderedClassMembers):
    """Domain content"""

    type_information = XmlNodeProperty('doma:typeInformation', factory=DomainTypeInformation)
    output_information = XmlNodeProperty('doma:outputInformation', factory=DomainOutputInformation)
    value_information = XmlNodeProperty('doma:valueInformation', factory=DomainValueInformation)


class Domain(ADTObject):
    """ABAP Domain

       ADT creates the domain from the header only and refuses the content,
       hence the content is not serialized until it is fetched.
    """

    OBJTYPE = ADTObjectType(
        'DOMA/DD',
        'ddic/domains',
        XMLNS_DOMA,
        'application/vnd.sap.adt.domains.v2+xml',
        {'application/vnd.sap.adt.domains.v2+xml': ''},
        'domain',
        editor_factory=ADTObjectPropertyEditor
    )

    content = XmlNodeProperty('doma:content', factory=DomainContent, ignore_empty=True)

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
