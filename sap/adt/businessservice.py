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

    def publish(self, service_definition_name):
        """Publish service defintion name"""

        service = next((item for item in self.services if item.definition.name == service_definition_name), None)

        if service is None:
            # pylint: disable=line-too-long
            raise SAPCliError(f'Business Service Binding {self.name} has no Service Defintion {service_definition_name}')

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
