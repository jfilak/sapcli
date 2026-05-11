"""Behavior Definition ADT functionality module"""

from sap.adt.objects import (
    xmlns_adtcore_ancestor,
    ADTObject,
    ADTObjectType,
    ADTObjectSourceEditor,
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
