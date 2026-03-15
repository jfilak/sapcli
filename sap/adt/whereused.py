"""ADT Where-Used functionality

Types and functions for getting usage references of ABAP object.

Quick usage with preconfigured meaningful scope returned by the ADT backend:

    connection = sap.adt.Connection(...)
    clas = sap.adt.Class('ZCL_FOO_BAR', None)
    result = sap.adt.where_used(connection, class.full_adt_uri)
    print(result.referenced_objects)

If you need to refine the searched scope:

    connection = sap.adt.Connection(...)
    clas = sap.adt.Class('ZCL_FOO_BAR', None)
    scope = sap.adt.get_scope(connection, class.full_adt_uri)

    scope.grade.definitions = 'true'
    scope.grade.elements = 'true'
    scope.grade.indirect_references = 'true'

    for obj in scope.object_types:
        if obj.name = 'CLAS/OC':
            obje.is_selected = 'true'

    result = sap.adt.get_where_used(connection, class.full_adt_uri, scope)
    print(result.referenced_objects)
"""

from sap.adt.core import Connection
from sap.adt.objects import OrderedClassMembers, ADTObjectType, XMLNamespace
from sap.adt.annotations import XmlNodeAttributeProperty, XmlNodeProperty, XmlContainer, \
    xml_text_node_property, xml_element
from sap.adt.marshalling import Marshal


XMLNS_USAGEREFS = XMLNamespace('usagereferences', 'http://www.sap.com/adt/ris/usageReferences')

SCOPE_REQUEST_MIME_TYPE = 'application/vnd.sap.adt.repository.usagereferences.scope.request.v1+xml'
SCOPE_RESPONSE_MIME_TYPE = 'application/vnd.sap.adt.repository.usagereferences.scope.response.v1+xml'
SEARCH_REQUEST_MIME_TYPE = 'application/vnd.sap.adt.repository.usagereferences.request.v1+xml'
SEARCH_RESPONSE_MIME_TYPE = 'application/vnd.sap.adt.repository.usagereferences.result.v1+xml'


# pylint: disable=too-few-public-methods
class AffectedObjects(metaclass=OrderedClassMembers):
    """Empty element for affected objects"""

    objtype = ADTObjectType(None, None, XMLNS_USAGEREFS, 'application/xml', None, 'affectedObjects')


# pylint: disable=too-few-public-methods
class ObjectIdentifier(metaclass=OrderedClassMembers):
    """Object identifier with display name and global type"""

    display_name = XmlNodeAttributeProperty('displayName')
    global_type = XmlNodeAttributeProperty('globalType')


# pylint: disable=too-few-public-methods
class Grade(metaclass=OrderedClassMembers):
    """Scope specifications refining whether to check usage of the given object
        in definitions, elements and indirect references
    """

    definitions = XmlNodeAttributeProperty('definitions')
    elements = XmlNodeAttributeProperty('elements')
    indirect_references = XmlNodeAttributeProperty('indirectReferences')


# pylint: disable=too-few-public-methods
class ObjectType(metaclass=OrderedClassMembers):
    """Object type with name, selection and default flags"""

    name = XmlNodeAttributeProperty('name')
    is_selected = XmlNodeAttributeProperty('isSelected')
    is_default = XmlNodeAttributeProperty('isDefault')


# pylint: disable=invalid-name
ObjectTypeList = XmlContainer.define('usagereferences:type', ObjectType)


class UsageScopeRequest(metaclass=OrderedClassMembers):
    """Request to get the default scope configuration for the give ABAP object.

        Actually all the obsoreved initial scope HTTP requests always sent a
        dummy XML with not real data so the purpose of this object is not yet
        clear.
    """

    objtype = ADTObjectType(None, None, XMLNS_USAGEREFS, 'application/xml', None, 'usageScopeRequest')

    @xml_element('usagereferences:affectedObjects')
    def affected_objects(self):
        """Affected objects element"""
        return AffectedObjects()


# pylint: disable=too-few-public-methods
class UsageScopeResult(metaclass=OrderedClassMembers):
    """The default scope configuration returned by the ADT backend"""

    objtype = ADTObjectType(None, None, XMLNS_USAGEREFS, 'application/xml', None, 'usageScopeResult')

    local_usage = XmlNodeAttributeProperty('localUsage')
    object_identifier = XmlNodeProperty('usagereferences:objectIdentifier', factory=ObjectIdentifier)
    grade = XmlNodeProperty('usagereferences:grade', factory=Grade)
    object_types = XmlNodeProperty('usagereferences:objectTypes', factory=ObjectTypeList)
    payload = xml_text_node_property('usagereferences:payload')


# pylint: disable=too-few-public-methods
class UsageScope(metaclass=OrderedClassMembers):
    """Scope element embedded in the search request"""

    objtype = ADTObjectType(None, None, XMLNS_USAGEREFS, 'application/xml', None, 'scope')

    local_usage = XmlNodeAttributeProperty('localUsage')
    object_identifier = XmlNodeProperty('usagereferences:objectIdentifier', factory=ObjectIdentifier)
    grade = XmlNodeProperty('usagereferences:grade', factory=Grade)
    object_types = XmlNodeProperty('usagereferences:objectTypes', factory=ObjectTypeList)
    payload = xml_text_node_property('usagereferences:payload')


class UsageReferenceRequest(metaclass=OrderedClassMembers):
    """Search request object specification and scope definition"""

    objtype = ADTObjectType(None, None, XMLNS_USAGEREFS, 'application/xml', None, 'usageReferenceRequest')

    @xml_element('usagereferences:affectedObjects')
    def affected_objects(self):
        """Affected objects element"""
        return AffectedObjects()

    @xml_element('usagereferences:scope')
    def scope(self):
        """Scope element"""
        return self._scope

    def __init__(self):
        self._scope = UsageScope()


# pylint: disable=too-few-public-methods
class PackageRef(metaclass=OrderedClassMembers):
    """Package reference inside an ADT object"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')
    name = XmlNodeAttributeProperty('adtcore:name')


# pylint: disable=too-few-public-methods
class AdtObject(metaclass=OrderedClassMembers):
    """ADT object inside a referenced object"""

    responsible = XmlNodeAttributeProperty('adtcore:responsible')
    name = XmlNodeAttributeProperty('adtcore:name')
    typ = XmlNodeAttributeProperty('adtcore:type')
    package_ref = XmlNodeProperty('adtcore:packageRef', factory=PackageRef)


# pylint: disable=too-few-public-methods
class ReferencedObject(metaclass=OrderedClassMembers):
    """A single referenced object in the result"""

    uri = XmlNodeAttributeProperty('uri')
    parent_uri = XmlNodeAttributeProperty('parentUri')
    is_result = XmlNodeAttributeProperty('isResult')
    can_have_children = XmlNodeAttributeProperty('canHaveChildren')
    usage_information = XmlNodeAttributeProperty('usageInformation')
    adt_object = XmlNodeProperty('usagereferences:adtObject', factory=AdtObject)


# pylint: disable=invalid-name
ReferencedObjectList = XmlContainer.define('usagereferences:referencedObject', ReferencedObject)


# pylint: disable=too-few-public-methods
class UsageReferenceResult(metaclass=OrderedClassMembers):
    """Result of the where-used search"""

    objtype = ADTObjectType(None, None, XMLNS_USAGEREFS, 'application/xml', None, 'usageReferenceResult')

    number_of_results = XmlNodeAttributeProperty('numberOfResults')
    result_description = XmlNodeAttributeProperty('resultDescription')
    referenced_object_identifier = XmlNodeAttributeProperty('referencedObjectIdentifier')
    scope = XmlNodeProperty('usagereferences:scope', factory=UsageScope)
    referenced_objects = XmlNodeProperty('usagereferences:referencedObjects', factory=ReferencedObjectList)


def get_scope(connection: Connection, uri: str) -> UsageScopeResult:
    """Fetch the usage scope for the given ABAP object URI"""

    request = UsageScopeRequest()
    body = Marshal().serialize(request)

    resp = connection.execute(
        'POST',
        'repository/informationsystem/usageReferences/scope',
        params={'uri': uri, 'version': 'active'},
        accept=SCOPE_RESPONSE_MIME_TYPE,
        content_type=SCOPE_REQUEST_MIME_TYPE,
        body=body
    )

    result = UsageScopeResult()
    Marshal.deserialize(resp.text, result)
    return result


def get_where_used(connection: Connection, uri: str, scope_result: UsageScopeResult) -> UsageReferenceResult:
    """Search for object references using the scope from the function get_scope

       Do not build your own object for the parameter scope_result but
       call the function get_scope and modify the returned object.
    """

    request = UsageReferenceRequest()
    scope = request.scope

    scope.local_usage = scope_result.local_usage
    scope.object_identifier = scope_result.object_identifier
    scope.grade = scope_result.grade
    scope.object_types = scope_result.object_types
    scope.payload = scope_result.payload

    body = Marshal().serialize(request)

    resp = connection.execute(
        'POST',
        'repository/informationsystem/usageReferences',
        params={'uri': uri, 'version': 'active'},
        accept=SEARCH_RESPONSE_MIME_TYPE,
        content_type=SEARCH_REQUEST_MIME_TYPE,
        body=body
    )

    result = UsageReferenceResult()
    Marshal.deserialize(resp.text, result)
    return result


def where_used(connection: Connection, uri: str):
    """Convenience function returning Where used ABAP object references with
        the default ADT scope configuration.

       Parameters:
        uri: full ADT URI - /sap/bc/adt/<object type path>/lowercase(<object name>)
    """

    scope_result = get_scope(connection, uri)
    return get_where_used(connection, uri, scope_result)
