"""CDS Metadata Extension (DDLX) ADT functionality module"""

from sap.adt.objects import ADTObject, ADTObjectType, ADTObjectSourceEditor, xmlns_adtcore_ancestor


class MetadataExtension(ADTObject):
    """CDS Metadata Extension definition (DDLX)"""

    OBJTYPE = ADTObjectType(
        'DDLX/EX',
        'ddic/ddlx/sources',
        xmlns_adtcore_ancestor('ddlx', 'http://www.sap.com/adt/ddic/ddlxsources'),
        'application/vnd.sap.adt.ddic.ddlx.v1+xml',
        {'text/plain': 'source/main'},
        'ddlxSource',
        editor_factory=ADTObjectSourceEditor.plain_text
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
