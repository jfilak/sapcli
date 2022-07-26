"""ABAP Table ADT functionality module"""

from sap.adt.objects import ADTObject, ADTObjectType, xmlns_adtcore_ancestor, ADTObjectSourceEditor


class Table(ADTObject):
    """ABAP Table"""

    OBJTYPE = ADTObjectType(
        'TABL/DT',
        'ddic/tables',
        xmlns_adtcore_ancestor('blue', 'http://www.sap.com/wbobj/blue'),
        'application/vnd.sap.adt.tables.v2+xml',
        {'text/plain': 'source/main'},
        'blueSource',
        editor_factory=ADTObjectSourceEditor
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata, active_status='inactive')

        self._metadata.package_reference.name = package
