"""ABAP Authorization Field ADT functionality module"""

from sap.adt.objects import ADTObject, ADTObjectType, XMLNamespace, XMLNS_ADTCORE
# pylint: disable=unused-import
from sap.adt.annotations import (
    OrderedClassMembers,
    xml_text_node_property,
    XmlNodeProperty,
)

XMLNS_AUTH = XMLNamespace('auth', 'http://www.sap.com/iam/auth')


# pylint: disable=too-few-public-methods
class AuthorizationFieldContent(metaclass=OrderedClassMembers):
    """ADT Authorization Field content data collector"""

    field_name = xml_text_node_property('auth:fieldName')
    roll_name = xml_text_node_property('auth:rollName')
    check_table = xml_text_node_property('auth:checkTable')
    exit_fb = xml_text_node_property('auth:exitFB')
    abap_language_version = xml_text_node_property('auth:abap_language_version')
    search = xml_text_node_property('auth:search')
    objexit = xml_text_node_property('auth:objexit')
    domname = xml_text_node_property('auth:domname')
    outputlen = xml_text_node_property('auth:outputlen')
    convexit = xml_text_node_property('auth:convexit')
    orglvlinfo = xml_text_node_property('auth:orglvlinfo')
    col_searchhelp = xml_text_node_property('auth:col_searchhelp')
    col_searchhelp_name = xml_text_node_property('auth:col_searchhelp_name')
    col_searchhelp_descr = xml_text_node_property('auth:col_searchhelp_descr')


class AuthorizationField(ADTObject):
    """ABAP Authorization Field"""

    OBJTYPE = ADTObjectType(
        'AUTH',
        'aps/iam/auth',
        XMLNamespace('auth', 'http://www.sap.com/iam/auth', parents=[XMLNS_ADTCORE]),
        'application/vnd.sap.adt.blues.v1+xml',
        None,
        'auth',
        editor_factory=None
    )

    content = XmlNodeProperty('auth:content')

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        if package is not None:
            self._metadata.package_reference.name = package
        self.content = AuthorizationFieldContent()
