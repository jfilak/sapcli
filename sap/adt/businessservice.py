"""Odataservice ADT wrappers"""

from typing import Union
from enum import Enum
from sap import get_logger
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
    ADTObjectReference,
    ADTObjectReferences,
)
from sap.adt.annotations import (
    XmlNodeAttributeProperty,
    XmlNodeProperty,
    XmlListNodeProperty,
)
from sap.adt.marshalling import Marshal


def mod_log():
    """ADT Module logger"""

    return get_logger()


XMLNS_SRVB = xmlns_adtcore_ancestor('srvb', 'http://www.sap.com/adt/ddic/ServiceBindings')
XMLNS_SRVD = xmlns_adtcore_ancestor('srvd', 'http://www.sap.com/adt/ddic/srvdsources')
XMLNS_ODATAV2 = xmlns_adtcore_ancestor('odatav2', 'http://www.sap.com/categories/odatav2')
XMLNS_ODATAV4 = xmlns_adtcore_ancestor('odatav4', 'http://www.sap.com/categories/odatav4')


# Enum for JobName -> publish, unpublish
# pylint: disable=too-few-public-methods
class JobName(Enum):
    """Enum for JobName"""

    PUBLISH = "publishjobs"
    UNPUBLISH = "unpublishjobs"


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


class ServicesContainer(metaclass=OrderedClassMembers):
    """Service container that also carries the srvb:name attribute."""

    name = XmlNodeAttributeProperty('srvb:name')
    link = XmlNodeProperty('srvb:content', factory=DefinitionLink)

    @property
    def definition(self):
        """Backward compatibility property to mirror the original structure of the XML, which had
           the service definition directly under the services container. This allows
           existing code that accessed `service.services.link.definition` to continue
           working without modification.
        """

        return self.link.definition

    @property
    def version(self):
        """Backward compatibility property to mirror the original structure of the XML, which had
           the service version directly under the services container. This allows
           existing code that accessed `service.services.version` to continue
           working without modification.
        """

        return self.link.version

    @property
    def release_state(self):
        """Backward compatibility property to mirror the original structure of the XML, which had
           the service release state directly under the services container. This allows
           existing code that accessed `service.services.release_state` to continue
           working without modification.
        """

        return self.link.release_state


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
    collection = XmlListNodeProperty('serviceInfo:collection', value=[], factory=ServiceInformationCollection)


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
    allowed_action = XmlNodeAttributeProperty('odatav2:allowedAction')
    service_information = XmlNodeProperty('serviceInfo:serviceInformation', factory=ServiceInformation)


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
    def get(cls, connection, name: str, version: str, srvdname: str) -> "ODataV2ServiceList":
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
    def get(cls, connection, name: str, version: str, srvdname: str) -> "ODataV4ServiceGroup":
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
    services = XmlListNodeProperty('srvb:services', value=[], factory=ServicesContainer)
    binding = XmlNodeProperty('srvb:binding', factory=Binding)

    def __init__(self, connection, name, package=None, typ=None, version=None, category=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package

        inner_binding = Binding()
        inner_binding.typ = typ
        inner_binding.version = version
        inner_binding.category = category
        inner_binding.implementation = Implementation()
        inner_binding.implementation.name = ''

        self.binding = inner_binding

    def add_service(self, service_name: str, service_definition: str, service_version: str):
        """Add Service Definition as a new Service"""

        service = ServicesContainer()
        service.name = service_name
        service.link = DefinitionLink()
        service.link.version = service_version
        service.link.release_state = 'NOT_RELEASED'
        service.link.definition = Definition()
        service.link.definition.name = service_definition
        service.link.definition.typ = 'SRVD/SRV'

        self.services.append(service)

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

    def get_service_group(self, service: ServicesContainer) -> Union[None | ODataV4ServiceGroup | ODataV2ServiceList]:
        """Returns the Service Group or None"""

        if self.binding.typ != 'ODATA':
            mod_log().warning(
                "Service Binding '%s' is of type '%s', expected 'ODATA'. Cannot fetch Service Group.",
                self.name,
                self.binding.typ)
            return None

        match self.binding.version:
            case 'V2':
                return ODataV2ServiceList.get(self.connection, service.name, service.version, service.definition.name)
            case 'V4':
                return ODataV4ServiceGroup.get(self.connection, service.name, service.version, service.definition.name)

        mod_log().warning(
            "Service Binding '%s' has unsupported OData version '%s'. Cannot fetch Service Group.",
            self.name,
            self.binding.version)
        return None

    def _execute_service_job(self, jobname: JobName, service):
        references = ADTObjectReferences()

        params = None
        match self.binding.term:
            case 'odatav2':
                references.add_reference(ADTObjectReference(name=service.name))
                params = {
                    'servicename': self.name,
                    'serviceversion': service.version,
                }
            case 'odatav4':
                references.add_reference(ADTObjectReference(typ='SCGR', name=service.name))
            case _:
                raise SAPCliError(f"Unsupported service binding type '{self.binding.term}'")

        response = self.connection.execute(
            'POST',
            f'businessservices/{self.binding.term}/{jobname.value}',
            params=params,
            headers={
                # pylint: disable=line-too-long
                'Accept': 'application/xml, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.StatusMessage',
                'Content-Type': 'application/xml'
            },
            body=Marshal().serialize(references)
        )

        return from_xml(StatusMessage(), response.text, root_elem="DATA")

    def publish(self, service):
        """Publish service definition"""

        return self._execute_service_job(JobName.PUBLISH, service)

    def unpublish(self, service):
        """Unpublish service definition"""

        return self._execute_service_job(JobName.UNPUBLISH, service)


# pylint: disable=too-few-public-methods
class SourceType(Enum):
    """Enum for Service Definition source type (srvd:srvdSourceType)"""

    DEFINITION = "S"
    EXTENSION = "X"


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

    # Source Types:
    # - S: Service Definition
    # - X: Extension
    source_type = XmlNodeAttributeProperty('srvd:srvdSourceType')

    def __init__(self, connection, name, package=None, metadata=None, source_type: SourceType = SourceType.DEFINITION):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
        self.source_type = source_type.value
