"""Odataservice ADT wrappers"""

from xml.etree import ElementTree

SERVICE_BINDING_XML_SPACE = '{http://www.sap.com/adt/ddic/ServiceBindings}'


def get_publish_request_body(binding_name):
    """creates a required request body for service publish"""

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:name="{binding_name}"/>
</adtcore:objectReferences>'''


def get_element(element_tree, xml_space, element_key):
    """Gets required element from supplied XML space"""
    return element_tree.find(f'{xml_space}{element_key}')


class ServiceBinding:
    """oData service binding abstraction"""

    def __init__(self, connection, service_version, binding_name):
        self._connection = connection
        self._service_version = service_version
        self._binding_name = binding_name.lower()
        self._binding_info = None

    def publish(self):
        """Publishes selected version of oData service through it's binding"""

        path = f'businessservices/{self.get_binding_type()}/publishjobs'

        return self._connection.execute(
            'POST',
            path,
            content_type='application/xml',
            params={
                'servicename': self._binding_name,
                'serviceversion': self._service_version
            },
            body=get_publish_request_body(self._binding_name.upper())
        )

    def get_binding_type(self):
        """Retrieves binding type from binding response"""
        binding = get_element(self._retrieve_binding_info(), SERVICE_BINDING_XML_SPACE, 'binding')
        binding_type = binding.attrib["{http://www.sap.com/adt/ddic/ServiceBindings}type"]
        binding_version = binding.attrib["{http://www.sap.com/adt/ddic/ServiceBindings}version"]
        return f'{binding_type.lower()}{binding_version.lower()}'

    def _retrieve_binding_info(self):
        if self._binding_info is None:
            path = f'businessservices/bindings/{self._binding_name}'
            response = self._connection.execute(
                'GET',
                path,
                params={
                    'version': 'inactive',
                },
                content_type='application/vnd.sap.adt.businessservices.servicebinding.v2+xml'
            )

            if response.status_code != 200:
                raise RuntimeError(f'Failed to retrieve service binding {self._binding_name}: {response.text} ')

            self._binding_info = ElementTree.fromstring(response.text)

        return self._binding_info
