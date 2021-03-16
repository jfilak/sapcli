'''ADT oData service wraper tests.'''
# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
import unittest.mock as mock

import sap.adt.odataservice

SAMPLE_ODATA_BINDING_V2 = '''<?xml version="1.0" encoding="utf-8"?>
<srvb:serviceBinding srvb:releaseSupported="false" srvb:published="true" srvb:bindingCreated="true"
    xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core">
    <atom:link href="/sap/bc/adt/businessservices/odatav2/TEST_BINDING" rel="http://www.sap.com/categories/odatav2"
        type="application/vnd.sap.adt.businessservices.odatav2.v2+xml" title="ODATAV2"
        xmlns:atom="http://www.w3.org/2005/Atom" />
    <atom:link href="/sap/bc/adt/businessservices/testclass" rel="http://www.sap.com/categories/testclass"
        type="application/vnd.sap.adt.businessservices.testclass.v1+xml" title="TESTCLASS"
        xmlns:atom="http://www.w3.org/2005/Atom" />
    <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP"
        adtcore:description="desc" />
    <srvb:services srvb:name="TEST_BINDING">
        <srvb:content srvb:version="0001" srvb:releaseState="">
            <srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/test_service" adtcore:type="SRVD/SRV"
                adtcore:name="TEST_SERVICE" />
        </srvb:content>
    </srvb:services>
    <srvb:binding srvb:type="ODATA" srvb:version="V2" srvb:category="0">
        <srvb:implementation adtcore:name="TEST_BINDING" />
    </srvb:binding>
</srvb:serviceBinding>'''


def sample_connection_ok():
    response = mock.MagicMock()
    response.status_code = 200
    response.text = SAMPLE_ODATA_BINDING_V2
    connection = mock.MagicMock()
    connection.execute = mock.Mock(return_value=response)
    return connection


def sample_connection_err():
    response = mock.MagicMock()
    response.status_code = 500
    connection = mock.MagicMock()
    connection.execute = mock.Mock(return_value=response)
    return connection


class TestOdataServiceBinding(unittest.TestCase):
    '''oData service binding class tests'''

    def test_binding_init(self):
        connection = 'CONN'

        service_version = '0001'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.odataservice.ServiceBinding(connection, service_version, binding_name)
        self.assertIs(binding._connection, connection)
        self.assertIs(binding._service_version, service_version)
        self.assertEqual(binding._binding_name, binding_name.lower())

    def test_binding_type_valid(self):
        service_version = '0001'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.odataservice.ServiceBinding(sample_connection_ok(), service_version, binding_name)

        expected_binding_type = 'odatav2'
        actual_binding_type = binding.get_binding_type()

        self.assertEqual(expected_binding_type, actual_binding_type, 'Different binding type expected!')

    def test_binding_type_invalid(self):
        service_version = '0001'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.odataservice.ServiceBinding(sample_connection_err(), service_version, binding_name)
        with self.assertRaises(RuntimeError):
            binding.get_binding_type()

    def test_service_published(self):
        service_version = '0001'
        binding_name = 'TEST_BINDING'

        connection = sample_connection_ok()
        sap.adt.odataservice.ServiceBinding(connection, service_version, binding_name).publish()

        connection.execute.assert_called_with(
            'POST',
            'businessservices/odatav2/publishjobs',
            content_type='application/xml',
            params={
                'servicename': 'test_binding',
                'serviceversion': '0001'
            },
            body='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:name="TEST_BINDING"/>
</adtcore:objectReferences>'''
        )
