"""ABAP Table ADT functionality module"""

from sap.adt.objects import (
    ADTObject,
    ADTObjectType,
    ADTObjectPropertyEditor,
    ADTObjectSourceEditor,
    XMLNamespace,
    XMLNS_ADTCORE,
    xmlns_adtcore_ancestor,
)
from sap.adt.annotations import OrderedClassMembers, XmlNodeProperty, xml_text_node_property

XMLNS_TS = XMLNamespace('ts', 'http://www.sap.com/dictionary/table/settings', parents=[XMLNS_ADTCORE])


class Table(ADTObject):
    """ABAP Table"""

    OBJTYPE = ADTObjectType(
        'TABL/DT',
        'ddic/tables',
        xmlns_adtcore_ancestor('blue', 'http://www.sap.com/wbobj/blue'),
        'application/vnd.sap.adt.tables.v2+xml',
        {'text/plain': 'source/main'},
        'blueSource',
        editor_factory=ADTObjectSourceEditor.plain_text
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata, active_status='inactive')

        self._metadata.package_reference.name = package


# pylint: disable=too-few-public-methods
class TableSettingsBuffering(metaclass=OrderedClassMembers):
    """Buffering of database table"""

    allowed = xml_text_node_property('ts:allowed')
    type = xml_text_node_property('ts:type')
    area_key_fields = xml_text_node_property('ts:areaKeyFields')


class TableSettings(ADTObject):
    """Technical settings of database table

       ADT creates the settings together with the table.
    """

    OBJTYPE = ADTObjectType(
        'TABL/DTT',
        'ddic/db/settings',
        XMLNS_TS,
        'application/vnd.sap.adt.table.settings.v2+xml',
        {'application/vnd.sap.adt.table.settings.v2+xml': ''},
        'tableSettings',
        editor_factory=ADTObjectPropertyEditor
    )

    data_class = xml_text_node_property('ts:dataClassCategory')
    size_category = xml_text_node_property('ts:sizeCategory')
    buffering = XmlNodeProperty('ts:buffering', factory=TableSettingsBuffering)
    storage_type = xml_text_node_property('ts:storageType')
    sharing_type = xml_text_node_property('ts:sharingType')
    load_unit = xml_text_node_property('ts:loadUnit')
    logging_enabled = xml_text_node_property('ts:loggingEnabled')

    def __init__(self, connection, name, metadata=None):
        super().__init__(connection, name, metadata)

        self.buffering = TableSettingsBuffering()

    # pylint: disable=invalid-overridden-method
    def reference(self):
        """Technical settings have no package reference but ADT drops
           the values of the settings if the request contains packageRef
        """

        return None
