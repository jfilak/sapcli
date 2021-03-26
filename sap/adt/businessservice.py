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
    OrderedClassMembers,
    ADTObjectReferences
)
from sap.adt.annotations import (
    XmlNodeAttributeProperty,
    XmlNodeProperty,
    XmlContainer
)
from sap.adt.marshalling import Marshal


XMLNS_SRVB = xmlns_adtcore_ancestor('srvb', 'http://www.sap.com/adt/ddic/ServiceBindings')
XMLNS_SRVD = xmlns_adtcore_ancestor('srvd', 'http://www.sap.com/adt/ddic/srvdsources')


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
    services = XmlNodeProperty('srvb:services', factory=ServicesContainer)
    binding = XmlNodeProperty('srvb:binding', factory=Binding)

    def __init__(self, connection, name, metadata=None):
        super().__init__(connection, name, metadata)

    def find_service(self, service_name=None, service_version=None):
        """Returns a first service matching the given parameters.

           If any parameter is None, the parameter is not considered for
           comparison.
        """

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
        {},
        'srvdSource'
    )

    def __init__(self, connection, name, package=None, metadata=None):
        super().__init__(connection, name, metadata)

        self._metadata.package_reference.name = package
