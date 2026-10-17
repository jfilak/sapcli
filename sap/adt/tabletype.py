"""ABAP DDIC Table Type ADT functionality module"""

from sap.adt.objects import ADTObject, ADTObjectType, ADTObjectPropertyEditor, XMLNamespace, XMLNS_ADTCORE
from sap.adt.annotations import (
    OrderedClassMembers,
    XmlContainer,
    XmlListNodeProperty,
    XmlNodeAttributeProperty,
    XmlNodeProperty,
    xml_text_node_property,
)

XMLNS_TTYP = XMLNamespace('ttyp', 'http://www.sap.com/dictionary/tabletype', parents=[XMLNS_ADTCORE])


# pylint: disable=too-few-public-methods
class TableTypeBuiltInType(metaclass=OrderedClassMembers):
    """Predefined ABAP type of the row"""

    data_type = xml_text_node_property('ttyp:dataType')
    length = xml_text_node_property('ttyp:length')
    decimals = xml_text_node_property('ttyp:decimals')


# pylint: disable=too-few-public-methods
class TableTypeRowType(metaclass=OrderedClassMembers):
    """Row type of the table type"""

    type_kind = xml_text_node_property('ttyp:typeKind')
    type_name = xml_text_node_property('ttyp:typeName')
    built_in_type = XmlNodeProperty('ttyp:builtInType', factory=TableTypeBuiltInType)
    range_type = xml_text_node_property('ttyp:rangeType')


# pylint: disable=too-few-public-methods
class TableTypeKeyComponent(metaclass=OrderedClassMembers):
    """A component (field of the row type) of a table key"""

    name = XmlNodeAttributeProperty('ttyp:name')

    def __init__(self, name=None):
        self.name = name


class TableTypeKeyComponents(XmlContainer):
    """List of table key components"""

    is_visible = XmlNodeAttributeProperty('ttyp:isVisible')
    items = XmlListNodeProperty('ttyp:component', factory=TableTypeKeyComponent, value=[])


# pylint: disable=too-few-public-methods
class TableTypePrimaryKey(metaclass=OrderedClassMembers):
    """Primary key of the table type"""

    is_visible = XmlNodeAttributeProperty('ttyp:isVisible')
    is_editable = XmlNodeAttributeProperty('ttyp:isEditable')
    definition = xml_text_node_property('ttyp:definition')
    kind = xml_text_node_property('ttyp:kind')
    components = XmlNodeProperty('ttyp:components', factory=TableTypeKeyComponents)
    alias = xml_text_node_property('ttyp:alias')


# pylint: disable=too-few-public-methods
class TableTypeSecondaryKey(metaclass=OrderedClassMembers):
    """Secondary key of the table type"""

    identifier = XmlNodeAttributeProperty('ttyp:identifier')
    description = XmlNodeAttributeProperty('ttyp:description')
    language = XmlNodeAttributeProperty('ttyp:language')
    access = XmlNodeAttributeProperty('ttyp:access')
    definition = XmlNodeAttributeProperty('ttyp:definition')
    components = XmlNodeProperty('ttyp:components', factory=TableTypeKeyComponents)


# pylint: disable=too-few-public-methods
class TableTypeSecondaryKeys(metaclass=OrderedClassMembers):
    """Secondary keys of the table type"""

    is_visible = XmlNodeAttributeProperty('ttyp:isVisible')
    is_editable = XmlNodeAttributeProperty('ttyp:isEditable')
    allowed = xml_text_node_property('ttyp:allowed')
    keys = XmlListNodeProperty('ttyp:secondaryKey', factory=TableTypeSecondaryKey, value=[])


# pylint: disable=too-few-public-methods
class TableTypeValueHelp(metaclass=OrderedClassMembers):
    """A possible value of a table type property"""

    key = XmlNodeAttributeProperty('ttyp:key')
    value = XmlNodeAttributeProperty('ttyp:value')
    description = XmlNodeAttributeProperty('ttyp:description')


TableTypeValueHelpList = XmlContainer.define('ttyp:valueHelp', TableTypeValueHelp)


# pylint: disable=too-few-public-methods
class TableTypeValueHelps(metaclass=OrderedClassMembers):
    """Possible values of table type properties"""

    type_kind_values = XmlNodeProperty('ttyp:typeKindValues', factory=TableTypeValueHelpList)
    key_definition_values = XmlNodeProperty('ttyp:keyDefinitionValues', factory=TableTypeValueHelpList)
    key_kind_values = XmlNodeProperty('ttyp:keyKindValues', factory=TableTypeValueHelpList)
    access_type_values = XmlNodeProperty('ttyp:accessTypeValues', factory=TableTypeValueHelpList)
    sec_key_access_values = XmlNodeProperty('ttyp:secKeyAccessValues', factory=TableTypeValueHelpList)
    sec_key_definition_values = XmlNodeProperty('ttyp:secKeyDefinitionValues', factory=TableTypeValueHelpList)
    sec_key_allowed_values = XmlNodeProperty('ttyp:secKeyAllowedValues', factory=TableTypeValueHelpList)


class TableType(ADTObject):
    """ABAP DDIC Table Type

       ADT creates the table type from the header only and fills in the
       definition defaults, hence the definition is not serialized until
       it is fetched or set.
    """

    OBJTYPE = ADTObjectType(
        'TTYP/DA',
        'ddic/tabletypes',
        XMLNS_TTYP,
        'application/vnd.sap.adt.tabletype.v1+xml',
        None,
        'tableType',
        editor_factory=ADTObjectPropertyEditor
    )

    row_type = XmlNodeProperty('ttyp:rowType', factory=TableTypeRowType, ignore_empty=True)
    initial_row_count = xml_text_node_property('ttyp:initialRowCount', ignore_empty=True)
    access_type = xml_text_node_property('ttyp:accessType', ignore_empty=True)
    primary_key = XmlNodeProperty('ttyp:primaryKey', factory=TableTypePrimaryKey, ignore_empty=True)
    secondary_keys = XmlNodeProperty('ttyp:secondaryKeys', factory=TableTypeSecondaryKeys, ignore_empty=True)
    value_helps = XmlNodeProperty('ttyp:valueHelps', factory=TableTypeValueHelps, ignore_empty=True)

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package

    def _set_row_type(self, type_kind, type_name, data_type, length, decimals):
        self.row_type = TableTypeRowType()
        self.row_type.type_kind = type_kind
        self.row_type.type_name = type_name
        self.row_type.built_in_type = TableTypeBuiltInType()
        self.row_type.built_in_type.data_type = data_type
        self.row_type.built_in_type.length = length
        self.row_type.built_in_type.decimals = decimals
        self.row_type.range_type = ''

    def set_dictionary_row_type(self, type_name):
        """Sets the row type to the given DDIC type - e.g. a structure"""

        self._set_row_type('dictionaryType', type_name, '', '0', '0')

    def set_predefined_row_type(self, data_type, length, decimals):
        """Sets the row type to the given predefined ABAP type - e.g. CHAR"""

        self._set_row_type('predefinedAbapType', '', data_type, length, decimals)

    def set_primary_key(self, definition, kind, component_names):
        """Sets the primary key of the fetched table type"""

        components = TableTypeKeyComponents()
        components.is_visible = 'true' if component_names else 'false'
        for name in component_names:
            components.append(TableTypeKeyComponent(name))

        self.primary_key.definition = definition
        self.primary_key.kind = kind
        self.primary_key.components = components
