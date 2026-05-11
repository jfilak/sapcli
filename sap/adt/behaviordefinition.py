"""Behavior Definition ADT functionality module"""

from sap.adt.objects import (
    xmlns_adtcore_ancestor,
    ADTObject,
    ADTObjectType,
    ADTObjectSourceEditor,
    NamedItemList,
)


class BehaviorDefinition(ADTObject):
    """CDS Behavior Definition (BDEF)"""

    OBJTYPE = ADTObjectType(
        'BDEF/BDO',
        'bo/behaviordefinitions',
        xmlns_adtcore_ancestor('blue', 'http://www.sap.com/wbobj/blue'),
        'application/vnd.sap.adt.blues.v1+xml',
        {'text/plain': 'source/main'},
        'blueSource',
        editor_factory=ADTObjectSourceEditor.plain_text
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package

    @staticmethod
    def list_interfaces(connection, bdef_name: str) -> 'NamedItemList':
        """List BO interfaces assigned to the given behavior definition"""

        resp = connection.execute(
            'GET',
            'bo/behaviordefinitions/interfaces',
            params={'name': bdef_name.upper()},
            accept=['application/vnd.sap.adt.nameditems.v1+xml', 'application/xml'],
        )

        return NamedItemList.from_xml(resp.text)
