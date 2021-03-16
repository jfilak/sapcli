'''ADT oData service wraper tests.'''
# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
import unittest.mock as mock

import sap.adt.businessservice

from mock import Connection, Response, Request

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
        <srvb:content srvb:version="0002" srvb:releaseState="">
            <srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/test_service_2" adtcore:type="SRVD/SRV"
                adtcore:name="TEST_SERVICE_2" />
        </srvb:content>
    </srvb:services>
    <srvb:binding srvb:type="ODATA" srvb:version="V2" srvb:category="0">
        <srvb:implementation adtcore:name="TEST_BINDING" />
    </srvb:binding>
</srvb:serviceBinding>'''

RESPONSE_BINDING_OK=Response(
    text=SAMPLE_ODATA_BINDING_V2,
    status_code=200,
    content_type='application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'
)


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


class TestbusinessserviceBinding(unittest.TestCase):
    '''oData service binding class tests'''

    def test_binding_fetch(self):
        connection = Connection([RESPONSE_BINDING_OK])

        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()

        self.assertEqual(binding.name, binding_name)
        self.assertEqual(binding.published, 'true')
        self.assertEqual(binding.release_supported, 'false')

        self.assertEqual(binding.binding.typ, 'ODATA')
        self.assertEqual(binding.binding.version, 'V2')
        self.assertEqual(binding.binding.implementation.name, binding_name)

        self.assertEqual(binding.services[0].version, '0001')
        self.assertEqual(binding.services[0].release_state, '')
        self.assertEqual(binding.services[0].definition.uri, '/sap/bc/adt/ddic/srvd/sources/test_service')
        self.assertEqual(binding.services[0].definition.typ, 'SRVD/SRV')
        self.assertEqual(binding.services[0].definition.name, 'TEST_SERVICE')

        self.assertEqual(binding.services[1].version, '0002')
        self.assertEqual(binding.services[1].release_state, '')
        self.assertEqual(binding.services[1].definition.uri, '/sap/bc/adt/ddic/srvd/sources/test_service_2')
        self.assertEqual(binding.services[1].definition.typ, 'SRVD/SRV')
        self.assertEqual(binding.services[1].definition.name, 'TEST_SERVICE_2')

    def test_service_published(self):
        connection = Connection([
            RESPONSE_BINDING_OK,
            Response(
                status_code=200,
                content_type='application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.StatusMessage',
                text="""<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <SEVERITY>OK</SEVERITY>
      <SHORT_TEXT>Local Service Endpoint of service TEST_SERVICE_2 with version 0002 is activated locally</SHORT_TEXT>
      <LONG_TEXT/>
    </DATA>
  </asx:values>
</asx:abap>
""")
        ])

        service_version = '0001'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        status = binding.publish('TEST_SERVICE_2')

        connection.execs[1].assertEqual(
            Request.post(
                    uri='/sap/bc/adt/businessservices/odatav2/publishjobs',
                    headers={
                        'Accept': 'application/xml, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.StatusMessage',
                        'Content-Type':'application/xml'
                    },
                    params={
                        'servicename': 'TEST_BINDING',
                        'serviceversion': '0002'
                    },
                    body='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/businessservices/bindings/test_binding" adtcore:name="TEST_BINDING"/>
</adtcore:objectReferences>'''
            ),
            self
        )

        self.assertEqual(status.SEVERITY, "OK")
        self.assertEqual(status.SHORT_TEXT, "Local Service Endpoint of service TEST_SERVICE_2 with version 0002 is activated locally")
        self.assertEqual(status.LONG_TEXT, "")
