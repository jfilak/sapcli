"""ABAP Data Element ADT functionality module"""

from sap.adt.objects import ADTObject, ADTObjectType, ADTCoreData, ADTObjectSourceEditor
# pylint: disable=unused-import
from sap.adt.annotations import OrderedClassMembers, xml_element, xml_text_node_property
from sap.adt.objects import XMLNamespace, XMLNS_ADTCORE

XMLNS_DTEL = XMLNamespace('dtel', 'http://www.sap.com/adt/dictionary/dataelements')

LABELS_LENGTH = {
    'short': '10',
    'medium': '20',
    'long': '40',
    'heading': '55'
}

VALIDATION_ISSUE_KEYS = {
    'none': 'none',
    'domain_name_not_defined': 'domain_name_not_defined',
    'data_type_not_defined': 'data_type_not_defined'
}


class ADTDataElementData(ADTCoreData):
    """Data Element nodes data.
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    class DataElement(metaclass=OrderedClassMembers):
        """ADT Data Element data collector"""

        type = xml_text_node_property('dtel:typeKind')
        type_name = xml_text_node_property('dtel:typeName')
        data_type = xml_text_node_property('dtel:dataType')
        data_type_length = xml_text_node_property('dtel:dataTypeLength')
        data_type_decimals = xml_text_node_property('dtel:dataTypeDecimals')
        label_short = xml_text_node_property('dtel:shortFieldLabel')
        label_short_length = xml_text_node_property('dtel:shortFieldLength')
        label_short_max_length = xml_text_node_property('dtel:shortFieldMaxLength')
        label_medium = xml_text_node_property('dtel:mediumFieldLabel')
        label_medium_length = xml_text_node_property('dtel:mediumFieldLength')
        label_medium_max_length = xml_text_node_property('dtel:mediumFieldMaxLength')
        label_long = xml_text_node_property('dtel:longFieldLabel')
        label_long_length = xml_text_node_property('dtel:longFieldLength')
        label_long_max_length = xml_text_node_property('dtel:longFieldMaxLength')
        label_heading = xml_text_node_property('dtel:headingFieldLabel')
        label_heading_length = xml_text_node_property('dtel:headingFieldLength')
        label_heading_max_length = xml_text_node_property('dtel:headingFieldMaxLength')
        search_help = xml_text_node_property('dtel:searchHelp')
        search_help_parameter = xml_text_node_property('dtel:searchHelpParameter')
        set_get_parameter = xml_text_node_property('dtel:setGetParameter')
        default_component_name = xml_text_node_property('dtel:defaultComponentName')
        deactivate_input_history = xml_text_node_property('dtel:deactivateInputHistory')
        change_document = xml_text_node_property('dtel:changeDocument')
        left_to_right_direction = xml_text_node_property('dtel:leftToRightDirection')
        deactivate_bidi_filtering = xml_text_node_property('dtel:deactivateBIDIFiltering')

    # pylint: disable=too-many-arguments
    def __init__(self, package=None, description=None, language=None,
                 master_language=None, master_system=None, responsible=None,
                 package_reference=None, abap_language_version=None):
        super().__init__(package, description, language,
                         master_language, master_system, responsible,
                         package_reference, abap_language_version)

        self._data_element = ADTDataElementData.DataElement()

    @property
    def data_element(self):
        """The Data Element's reference"""

        return self._data_element


class DataElement(ADTObject):
    """ABAP Data Element"""

    OBJTYPE = ADTObjectType(
        'DTEL/DE',
        'ddic/dataelements',
        XMLNamespace('blue', 'http://www.sap.com/wbobj/dictionary/dtel', parents=[XMLNS_ADTCORE, XMLNS_DTEL]),
        'application/vnd.sap.adt.dataelements.v2+xml',
        {
            'application/vnd.sap.adt.dataelements.v2+xml': '',
            'application/vnd.sap.adt.dataelements.v1+xml': ''
        },
        'wbobj',
        editor_factory=ADTObjectSourceEditor
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata, active_status='inactive')

        self._metadata = ADTDataElementData(
            metadata.package, metadata.description,
            metadata.language, metadata.master_language,
            metadata.master_system, metadata.responsible,
            metadata.package_reference.name if metadata.package_reference is not None else None,
            metadata.abap_language_version
        ) if metadata is not None else ADTDataElementData()

        self._metadata.package_reference.name = package

    @xml_element('dtel:dataElement')
    def data_element(self):
        """The Data Element's reference"""

        return self._metadata.data_element

    def set_type(self, value):
        """Setter for Type Kind element"""

        self._metadata.data_element.type = value

    def set_type_name(self, value):
        """Setter for Type Name element"""

        self._metadata.data_element.type_name = value.upper() if value is not None else None

    def set_data_type(self, value):
        """Setter for Data Type element"""

        self._metadata.data_element.data_type = value.upper() if value is not None else None

    def set_data_type_length(self, value):
        """Setter for Data Type Length element"""

        self._metadata.data_element.data_type_length = value

    def set_data_type_decimals(self, value):
        """Setter for Data Type Decimals element"""

        self._metadata.data_element.data_type_decimals = value

    def set_label_short(self, value):
        """Setter for Label Short element"""

        self._metadata.data_element.label_short = value

    def set_label_medium(self, value):
        """Setter for Label Medium element"""

        self._metadata.data_element.label_medium = value

    def set_label_long(self, value):
        """Setter for Label Long element"""

        self._metadata.data_element.label_long = value

    def set_label_heading(self, value):
        """Setter for Label Heading element"""

        self._metadata.data_element.label_heading = value

    def normalize(self):
        """Validate Data Element setup before save"""
        de = self._metadata.data_element

        if de.type == 'domain':
            de.data_type = ''
            de.data_type_length = '0'
            de.data_type_decimals = '0'
        if de.type == 'predefinedAbapType':
            de.type_name = ''

        de.label_short_length = de.label_short_length if not de.label_short_length else LABELS_LENGTH['short']
        de.label_medium_length = de.label_medium_length if not de.label_medium_length else LABELS_LENGTH['medium']
        de.label_long_length = de.label_long_length if not de.label_long_length else LABELS_LENGTH['long']
        de.label_heading_length = de.label_heading_length if not de.label_heading_length else LABELS_LENGTH['heading']

        de.deactivate_input_history = de.deactivate_input_history if de.deactivate_input_history is not None else False
        de.change_document = de.change_document if de.change_document is not None else False
        de.left_to_right_direction = de.left_to_right_direction if de.left_to_right_direction is not None else False
        # pylint: disable=line-too-long
        de.deactivate_bidi_filtering = de.deactivate_bidi_filtering if de.deactivate_bidi_filtering is not None else False

    def validate(self):
        """Validate Data Element setup"""

        if self._metadata.data_element.type == 'domain' and not self._metadata.data_element.type_name:
            return VALIDATION_ISSUE_KEYS['domain_name_not_defined']
        if self._metadata.data_element.type == 'predefinedAbapType' and not self._metadata.data_element.data_type:
            return VALIDATION_ISSUE_KEYS['data_type_not_defined']

        return VALIDATION_ISSUE_KEYS['none']
