"""Odataservice ADT wrappers"""

from sap.errors import SAPCliError
from sap.platform.abap import (
    from_xml,
    Structure
)
from sap.adt.objects import (
    xmlns_adtcore_ancestor,
    ADTObject,
    ADTObjectType,
    ADTObjectSourceEditor,
    ADTRootObject,
    OrderedClassMembers,
    ADTObjectReferences
)
from sap.adt.annotations import (
    XmlNodeAttributeProperty,
    XmlNodeProperty,
    XmlListNodeProperty,
    XmlElementKind,
    XmlContainer
)
from sap.adt.marshalling import Marshal
import sap.adt.core


XMLNS_SRVB = xmlns_adtcore_ancestor('srvb', 'http://www.sap.com/adt/ddic/ServiceBindings')
XMLNS_SRVD = xmlns_adtcore_ancestor('srvd', 'http://www.sap.com/adt/ddic/srvdsources')
XMLNS_ODATAV2 = xmlns_adtcore_ancestor('odatav2', 'http://www.sap.com/categories/odatav2')
XMLNS_ODATAV4 = xmlns_adtcore_ancestor('odatav4', 'http://www.sap.com/categories/odatav4')


# pylint: disable=too-few-public-methods
class StatusMessage(Structure):
    """Status reported by the publish action"""

    SEVERITY: str
    SHORT_TEXT: str
    LONG_TEXT: str


# pylint: disable=too-few-public-methods
class Definition(metaclass=OrderedClassMembers):
    """The node serviceBinding/services/content/serviceDefinition"""

    uri = XmlNodeAttributeProperty('adtcore:uri')
    typ = XmlNodeAttributeProperty('adtcore:type')
    name = XmlNodeAttributeProperty('adtcore:name')


# pylint: disable=too-few-public-methods
class DefinitionLink(metaclass=OrderedClassMembers):
    """The node serviceBinding/services/content"""

    version = XmlNodeAttributeProperty('srvb:version')
    release_state = XmlNodeAttributeProperty('srvb:releaseState')
    definition = XmlNodeProperty('srvb:serviceDefinition', factory=Definition)


ServicesContainer = XmlContainer.define('srvb:content', DefinitionLink)


# `<srvb:services>` carries an `srvb:name` attribute on the wire (live captures
# show it equals the parent binding's name in every observed binding). The
# bare `XmlContainer.define` factory produces a synthesised class that mypy
# cannot subclass; declare a parallel container directly off `XmlContainer`
# instead, replicating the items property so we get both the list-of-children
# behaviour and the container-level srvb:name attribute. ServiceBinding
# populates `name` from the binding's own name on construction.
class ServicesContainerWithName(XmlContainer):
    """Service container that also carries the srvb:name attribute."""

    name = XmlNodeAttributeProperty('srvb:name')
    items = XmlListNodeProperty('srvb:content', deserialize=True,
                                factory=DefinitionLink, value=[],
                                kind=XmlElementKind.OBJECT)


# pylint: disable=too-few-public-methods
class Implementation(metaclass=OrderedClassMembers):
    """The node serviceBinding/binding/implementation"""

    name = XmlNodeAttributeProperty('adtcore:name')


class Binding(metaclass=OrderedClassMembers):
    """The node serviceBinding/binding"""

    # [ODATA]
    typ = XmlNodeAttributeProperty('srvb:type')
    # [V2,V4]
    version = XmlNodeAttributeProperty('srvb:version')
    # [0]
    category = XmlNodeAttributeProperty('srvb:category')
    # Holds Name of the Business Service Binding object
    implementation = XmlNodeProperty('srvb:implementation', factory=Implementation)

    @property
    def term(self):
        """Rerturns code for URL. The name 'term' comes
           from /sap/bc/adt/discovery.
        """

        return f'{self.typ.lower()}{self.version.lower()}'


# Published Service Info

class ServiceInformationCollection(metaclass=OrderedClassMembers):
    """ADT service information collection"""

    name = XmlNodeAttributeProperty('serviceInfo:name')
    is_leading = XmlNodeAttributeProperty('serviceInfo:isLeading')
    is_root = XmlNodeAttributeProperty('serviceInfo:isRoot')


class ServiceInformation(metaclass=OrderedClassMembers):
    """ADT service information"""

    service_name = XmlNodeAttributeProperty('serviceInfo:name')
    service_version = XmlNodeAttributeProperty('serviceInfo:version')
    collection = XmlNodeProperty('serviceInfo:collection', factory=ServiceInformationCollection)


# OData V2

class ODataV2ApplicationDetails(metaclass=OrderedClassMembers):
    """ADT OData V2 Application Details"""

    application_state = XmlNodeAttributeProperty('odatav2:applicationState')
    application_description = XmlNodeAttributeProperty('odatav2:applicationDescription')
    application_id = XmlNodeAttributeProperty('odatav2:applicationId')


class ODataV2Service(metaclass=OrderedClassMembers):
    """ADT OData V2 service"""

    repository_id = XmlNodeAttributeProperty('odatav2:repositoryId')
    service_id = XmlNodeAttributeProperty('odatav2:serviceId')
    service_version = XmlNodeAttributeProperty('odatav2:serviceVersion')
    service_url = XmlNodeAttributeProperty('odatav2:serviceUrl')
    annotation_url = XmlNodeAttributeProperty('odatav2:annotationUrl')
    created = XmlNodeAttributeProperty('odatav2:created')
    published = XmlNodeAttributeProperty('odatav2:published')
    allowed_action = XmlNodeProperty('odatav2:allowedAction')


class ODataV2ServiceList(ADTRootObject):
    """ADT ODataV2 Service Group"""

    OBJTYPE = ADTObjectType(
        None,  # Object code - not used for ServiceGroup because it is not an ABAP object type
        'businessservices/odatav2',
        XMLNS_ODATAV2,
        ['application/vnd.sap.adt.businessservices.odatav2.v3+xml'],
        {},  # Content types - not used for ServiceGroup as it is only the XML
        'serviceList')

    services = XmlNodeProperty('odatav2:services', factory=ODataV2Service)

    @classmethod
    def get(cls, connection: sap.adt.core.Connection, name: str, version: str, srvdname: str) -> "ODataV2ServiceList":
        """Fetches the OData V2 Service Group with the given name and version from the back-end"""

        response = connection.execute(
            'GET',
            cls.OBJTYPE.basepath + f'/{name}',
            params={
                'servicename': name,
                'serviceversion': version,
                'srvdname': srvdname
            },
            accept=cls.OBJTYPE.all_mimetypes,
        )

        return Marshal().deserialize(response.text, cls())


# OData V4

class ODataV4ApplicationDetails(metaclass=OrderedClassMembers):
    """ADT OData V4 Application Details"""

    application_state = XmlNodeAttributeProperty('odatav4:applicationState')
    application_description = XmlNodeAttributeProperty('odatav4:applicationDescription')
    application_id = XmlNodeAttributeProperty('odatav4:applicationId')


class ODataV4Service(metaclass=OrderedClassMembers):
    """ADT OData V4 service"""

    repository_id = XmlNodeAttributeProperty('odatav4:repositoryId')
    service_id = XmlNodeAttributeProperty('odatav4:serviceId')
    service_version = XmlNodeAttributeProperty('odatav4:serviceVersion')
    service_url = XmlNodeAttributeProperty('odatav4:serviceUrl')
    annotation_url = XmlNodeAttributeProperty('odatav4:annotationUrl')
    created = XmlNodeAttributeProperty('odatav4:created')
    service_information = XmlNodeProperty('serviceInfo:serviceInformation', factory=ServiceInformation)
    application_details = XmlNodeProperty('odatav4:applicationDetails', factory=ODataV4ApplicationDetails)


class ODataV4ServiceGroup(ADTRootObject):
    """ADT ODataV4 Service Group"""

    OBJTYPE = ADTObjectType(
        None,  # Object code - not used for ServiceGroup because it is not an ABAP object type
        'businessservices/odatav4',
        XMLNS_ODATAV4,
        ['application/vnd.sap.adt.businessservices.odatav4.v2+xml'],
        {},  # Content types - not used for ServiceGroup as it is only the XML
        'serviceGroup')

    published = XmlNodeAttributeProperty('odatav4:published')
    service_url_prefix = XmlNodeAttributeProperty('odatav4:serviceUrlPrefix')
    name = XmlNodeAttributeProperty('adtcore:name')
    services = XmlNodeProperty('odatav4:services', factory=ODataV4Service)

    @classmethod
    def get(cls, connection: sap.adt.core.Connection, name: str, version: str, srvdname: str) -> "ODataV4ServiceGroup":
        """Fetches the OData V4 Service Group with the given name and version from the back-end"""

        response = connection.execute(
            'GET',
            cls.OBJTYPE.basepath + f'/{name}',
            params={
                'servicename': name,
                'serviceversion': version,
                'srvdname': srvdname
            },
            accept=cls.OBJTYPE.all_mimetypes,
        )

        return Marshal().deserialize(response.text, cls())


# Service Binding


class ServiceBinding(ADTObject):
    """Business Service binding abstraction"""

    OBJTYPE = ADTObjectType(
        'SRVB/SVB',
        'businessservices/bindings',
        XMLNS_SRVB,
        ['application/vnd.sap.adt.businessservices.servicebinding.v2+xml',
         'application/vnd.sap.adt.businessservices.servicebinding.v1+xml'],
        {},
        'serviceBinding'
    )

    release_supported = XmlNodeAttributeProperty('srvb:releaseSupported')
    published = XmlNodeAttributeProperty('srvb:published')
    bindingCreated = XmlNodeAttributeProperty('srvb:bindingCreated')
    services = XmlNodeProperty('srvb:services', factory=ServicesContainerWithName)
    binding = XmlNodeProperty('srvb:binding', factory=Binding)

    def __init__(self, connection, name, package=None, typ=None, version=None,
                 service_name=None, service_version='0001', metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package

        # The classes Binding / Implementation / Definition / DefinitionLink /
        # ServicesContainer are constructed with `metaclass=OrderedClassMembers`.
        # pylint inspects the metaclass `__init__` signature instead of the
        # class's (empty) `__init__`, hence the spurious E1120 noise. Suppress
        # it locally — these constructions are exercised by unit tests.
        # pylint: disable=no-value-for-parameter
        if typ is not None or version is not None:
            inner_binding = Binding()
            inner_binding.typ = typ
            inner_binding.version = version
            inner_binding.category = '0'
            inner_binding.implementation = Implementation()
            inner_binding.implementation.name = name
            self.binding = inner_binding

        if service_name is not None:
            services = ServicesContainerWithName()
            # Live captures show `<srvb:services srvb:name=...>` always equals
            # the parent binding's name. Mirror that here so the POST body
            # matches the wire shape the back-end expects.
            services.name = name
            link = DefinitionLink()
            link.version = service_version
            link.release_state = 'NOT_RELEASED'
            link.definition = Definition()
            link.definition.name = service_name
            link.definition.typ = 'SRVD/SRV'
            services.append(link)
            self.services = services

    def find_service(self, service_name=None, service_version=None):
        """Returns a first service matching the given parameters.

           If any parameter is None, the parameter is not considered for
           comparison.
        """

        # `self.services` is a dynamically-built XmlContainer; pylint's static
        # inference flags iteration over it as not-iterable. Suppress the
        # false positive locally.
        # pylint: disable=not-an-iterable
        if service_name and service_version:
            return next(
                (item for item in self.services
                 if item.definition.name == service_name and item.version == service_version),
                None
            )

        if service_name is not None:
            return next(
                (item for item in self.services
                 if item.definition.name == service_name),
                None
            )

        if service_version is not None:
            return next(
                (item for item in self.services
                 if item.version == service_version),
                None
            )

        raise SAPCliError("You must specify either Service Name or Service Version or both")

    def publish(self, service):
        """Publish service definition"""

        references = ADTObjectReferences()
        references.add_object(self)

        response = self.connection.execute(
            'POST',
            f'businessservices/{self.binding.term}/publishjobs',
            params={
                'servicename': self.name,
                'serviceversion': service.version,
            },
            headers={
                # pylint: disable=line-too-long
                'Accept': 'application/xml, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.StatusMessage',
                'Content-Type': 'application/xml'
            },
            body=Marshal().serialize(references)
        )

        return from_xml(StatusMessage(), response.text, root_elem="DATA")


class ServiceDefinition(ADTObject):
    """Business Service Definition abstraction"""

    OBJTYPE = ADTObjectType(
        'SRVD/SRV',
        'ddic/srvd/sources',
        XMLNS_SRVD,
        ['application/vnd.sap.adt.ddic.srvd.v1+xml'],
        {'text/plain': 'source/main'},
        'srvdSource',
        editor_factory=ADTObjectSourceEditor.plain_text
    )

    # Required by the back-end on POST: without it the server rejects with
    # `ExceptionResourceCreationFailure: Service Definition type '' does not
    # exist`. Fixed value 'S' (= "Definition") is the only one observed in
    # captures - 'E' for "Extension" may exist but is out of scope for v1.
    source_type = XmlNodeAttributeProperty('srvd:srvdSourceType', value='S')

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
