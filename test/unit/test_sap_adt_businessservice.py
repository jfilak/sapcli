'''ADT oData service wraper tests.'''
# !/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
import unittest.mock as mock

import sap.errors
import sap.adt.businessservice

from mock import Connection, Response, Request

from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK
from fixtures_adt_businessservice import (
    SERVICE_DEFINITION_ADT_XML,
    SERVICE_DEFINITION_SOURCE_TEXT,
    SERVICE_DEFINITION_ADT_POST_REQUEST_XML,
    SERVICE_DEFINITION_ADT_POST_REQUEST_XML_EXTENSION,
    SERVICE_BINDING_ADT_POST_ODATA_V4_REQUEST_XML_UI,
    SERVICE_BINDING_ADT_POST_ODATA_V4_REQUEST_XML_API,
    SERVICE_GROUP_ODATAV4_GET_XML,
    SERVICE_GROUP_ODATAV2_GET_XML,
)

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
    <srvb:services srvb:name="TEST_BINDING_V2">
        <srvb:content srvb:version="0002" srvb:releaseState="">
            <srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/test_service_2" adtcore:type="SRVD/SRV"
                adtcore:name="TEST_SERVICE_2" />
        </srvb:content>
    </srvb:services>
    <srvb:binding srvb:type="ODATA" srvb:version="V2" srvb:category="0">
        <srvb:implementation adtcore:name="TEST_BINDING" />
    </srvb:binding>
</srvb:serviceBinding>'''

SAMPLE_ODATA_BINDING_V2_SINGLE_SRVD = '''<?xml version="1.0" encoding="utf-8"?>
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
        <srvb:content srvb:version="0002" srvb:releaseState="">
            <srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/test_service" adtcore:type="SRVD/SRV"
                adtcore:name="TEST_SERVICE_2" />
        </srvb:content>
    </srvb:services>
    <srvb:binding srvb:type="ODATA" srvb:version="V2" srvb:category="0">
        <srvb:implementation adtcore:name="TEST_BINDING" />
    </srvb:binding>
</srvb:serviceBinding>'''

SAMPLE_ODATA_BINDING_V4 = '''<?xml version="1.0" encoding="utf-8"?>
<srvb:serviceBinding srvb:releaseSupported="false" srvb:published="true" srvb:bindingCreated="true"
    xmlns:srvb="http://www.sap.com/adt/ddic/ServiceBindings" xmlns:adtcore="http://www.sap.com/adt/core">
    <atom:link href="/sap/bc/adt/businessservices/odatav4/TEST_BINDING_V4" rel="http://www.sap.com/categories/odatav4"
        type="application/vnd.sap.adt.businessservices.odatav4.v2+xml" title="ODATAV4"
        xmlns:atom="http://www.w3.org/2005/Atom" />
    <adtcore:packageRef adtcore:uri="/sap/bc/adt/packages/%24tmp" adtcore:type="DEVC/K" adtcore:name="$TMP"
        adtcore:description="desc" />
    <srvb:services srvb:name="TEST_BINDING_V4">
        <srvb:content srvb:version="0001" srvb:releaseState="">
            <srvb:serviceDefinition adtcore:uri="/sap/bc/adt/ddic/srvd/sources/test_service" adtcore:type="SRVD/SRV"
                adtcore:name="TEST_SERVICE" />
        </srvb:content>
    </srvb:services>
    <srvb:binding srvb:type="ODATA" srvb:version="V4" srvb:category="0">
        <srvb:implementation adtcore:name="TEST_BINDING_V4" />
    </srvb:binding>
</srvb:serviceBinding>'''

SAMPLE_ODATA_PUBLISH_SUCCESS_TEXT = """<?xml version="1.0" encoding="UTF-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
    <DATA>
      <SEVERITY>OK</SEVERITY>
      <SHORT_TEXT>Local Service Endpoint of service TEST_SERVICE_2 with version 0002 is activated locally</SHORT_TEXT>
      <LONG_TEXT/>
    </DATA>
  </asx:values>
</asx:abap>
"""

SAMPLE_BINDING_OBJECT_REFERENCE_V2 = '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:name="TEST_BINDING"/>
</adtcore:objectReferences>'''

SAMPLE_BINDING_OBJECT_REFERENCE_V4 = '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:type="SCGR" adtcore:name="TEST_BINDING_V4"/>
</adtcore:objectReferences>'''

RESPONSE_BINDING_OK = Response(
    text=SAMPLE_ODATA_BINDING_V2,
    status_code=200,
    content_type='application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'
)

RESPONSE_BINDING_OK_SINGLE_SRVD = Response(
    text=SAMPLE_ODATA_BINDING_V2_SINGLE_SRVD,
    status_code=200,
    content_type='application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'
)

RESPONSE_BINDING_OK_V4 = Response(
    text=SAMPLE_ODATA_BINDING_V4,
    status_code=200,
    content_type='application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'
)

RESPONSE_DEFINITION_OK = Response(
    text=SERVICE_DEFINITION_ADT_XML,
    status_code=200,
    content_type='application/vnd.sap.adt.ddic.srvd.v1+xml; charset=utf-8'
)


def sample_connection_ok(response=RESPONSE_BINDING_OK):
    connection = Connection([
        response,
        Response(
            status_code=200,
            content_type='application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.StatusMessage',
            text=SAMPLE_ODATA_PUBLISH_SUCCESS_TEXT)
    ])
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
        connection = sample_connection_ok()

        service_name = 'TEST_SERVICE_2'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        status = binding.publish(binding.services[0])

        connection.execs[1].assertEqual(
            Request.post(
                uri='/sap/bc/adt/businessservices/odatav2/publishjobs',
                headers={
                    'Accept': 'application/xml, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.StatusMessage',
                    'Content-Type': 'application/xml'
                },
                params={
                    'servicename': 'TEST_BINDING',
                    'serviceversion': '0001'
                },
                body=SAMPLE_BINDING_OBJECT_REFERENCE_V2
            ),
            self
        )

        self.assertEqual(status.SEVERITY, "OK")
        self.assertEqual(status.SHORT_TEXT,
                         "Local Service Endpoint of service TEST_SERVICE_2 with version 0002 is activated locally")
        self.assertEqual(status.LONG_TEXT, "")

    def test_service_published_v4(self):
        connection = sample_connection_ok(RESPONSE_BINDING_OK_V4)

        binding_name = 'TEST_BINDING_V4'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        status = binding.publish(binding.services[0])

        connection.execs[1].assertEqual(
            Request.post(
                uri='/sap/bc/adt/businessservices/odatav4/publishjobs',
                headers={
                    'Accept': 'application/xml, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.StatusMessage',
                    'Content-Type': 'application/xml'
                },
                params=None,
                body=SAMPLE_BINDING_OBJECT_REFERENCE_V4
            ),
            self
        )

        self.assertEqual(status.SEVERITY, "OK")
        self.assertEqual(status.SHORT_TEXT,
                         "Local Service Endpoint of service TEST_SERVICE_2 with version 0002 is activated locally")
        self.assertEqual(status.LONG_TEXT, "")

    def test_service_unpublished_v2(self):
        connection = sample_connection_ok()

        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        status = binding.unpublish(binding.services[0])

        connection.execs[1].assertEqual(
            Request.post(
                uri='/sap/bc/adt/businessservices/odatav2/unpublishjobs',
                headers={
                    'Accept': 'application/xml, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.StatusMessage',
                    'Content-Type': 'application/xml'
                },
                params={
                    'servicename': 'TEST_BINDING',
                    'serviceversion': '0001'
                },
                body=SAMPLE_BINDING_OBJECT_REFERENCE_V2
            ),
            self
        )

        self.assertEqual(status.SEVERITY, "OK")
        self.assertEqual(status.SHORT_TEXT,
                         "Local Service Endpoint of service TEST_SERVICE_2 with version 0002 is activated locally")
        self.assertEqual(status.LONG_TEXT, "")

    def test_service_unpublished_v4(self):
        connection = sample_connection_ok(RESPONSE_BINDING_OK_V4)

        binding_name = 'TEST_BINDING_V4'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        status = binding.unpublish(binding.services[0])

        connection.execs[1].assertEqual(
            Request.post(
                uri='/sap/bc/adt/businessservices/odatav4/unpublishjobs',
                headers={
                    'Accept': 'application/xml, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.StatusMessage',
                    'Content-Type': 'application/xml'
                },
                params=None,
                body=SAMPLE_BINDING_OBJECT_REFERENCE_V4
            ),
            self
        )

        self.assertEqual(status.SEVERITY, "OK")
        self.assertEqual(status.SHORT_TEXT,
                         "Local Service Endpoint of service TEST_SERVICE_2 with version 0002 is activated locally")
        self.assertEqual(status.LONG_TEXT, "")

    def test_service_publish_unsupported_binding_type(self):
        connection = sample_connection_ok()

        binding = sap.adt.businessservice.ServiceBinding(connection, 'TEST_BINDING')
        binding.fetch()
        binding.binding.version = 'V9'

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            binding.publish(binding.services[0])

        self.assertEqual(str(caught.exception), "Unsupported service binding type 'odatav9'")


        connection = sample_connection_ok()

        service_name = 'TEST_SERVICE_2'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        service = binding.find_service(service_name=service_name)

        self.assertIsNotNone(service)
        self.assertEqual(service.definition.name, service_name)

    def test_service_find_by_version(self):
        connection = sample_connection_ok()

        service_version = '0002'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        service = binding.find_service(None, service_version)

        self.assertIsNotNone(service)
        self.assertEqual(service.version, service_version)

    def test_service_find_by_name_and_version(self):
        connection = sample_connection_ok()

        service_name = 'TEST_SERVICE_2'
        service_version = '0002'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()
        service = binding.find_service(service_name, service_version)

        self.assertIsNotNone(service)
        self.assertEqual(service.definition.name, service_name)
        self.assertEqual(service.version, service_version)

    def test_service_not_found(self):
        connection = sample_connection_ok()

        service_name = 'FOO_BAR'
        service_version = '0003'
        binding_name = 'TEST_BINDING'

        binding = sap.adt.businessservice.ServiceBinding(connection, binding_name)
        binding.fetch()

        self.assertIsNone(binding.find_service(service_name, None))
        self.assertIsNone(binding.find_service(None, service_version))
        self.assertIsNone(binding.find_service(service_name, service_version))


class TestbusinessserviceDefinition(unittest.TestCase):

    def test_binding_fetch(self):
        connection = Connection([RESPONSE_DEFINITION_OK])

        definition_name = 'EXAMPLE_CONFIG_SRV'

        definition = sap.adt.businessservice.ServiceDefinition(connection, definition_name)
        definition.fetch()

        self.assertEqual(definition.name, definition_name)
        self.assertEqual(definition.description, 'Example Configuration')
        self.assertEqual(definition.reference.name, 'EXAMPLE_CONFIG')
        # `srvd:srvdSourceType` is REQUIRED on POST and round-trips through GET.
        # The captured fixture carries srvd:srvdSourceType="S" - assert it
        # so the field stays wired even if someone refactors the class.
        self.assertEqual(definition.source_type, 'S')

    def test_servicedefinition_default_source_type_is_S(self):
        # New, in-memory ServiceDefinition must default source_type='S' so
        # the create POST always carries srvd:srvdSourceType (the back-end
        # rejects POST bodies without it - see live e2e captures).
        srvd = sap.adt.businessservice.ServiceDefinition(Connection(), 'ZNEW_SRV')
        self.assertEqual(srvd.source_type, 'S')

    def test_sourcetype_enum_values(self):
        self.assertEqual(sap.adt.businessservice.SourceType.DEFINITION.value, 'S')
        self.assertEqual(sap.adt.businessservice.SourceType.EXTENSION.value, 'X')

    def test_servicedefinition_source_type_extension(self):
        # The constructor must honor an explicit source type so extensions
        # can be created (srvd:srvdSourceType='X').
        srvd = sap.adt.businessservice.ServiceDefinition(
            Connection(), 'ZNEW_SRV',
            source_type=sap.adt.businessservice.SourceType.EXTENSION)
        self.assertEqual(srvd.source_type, 'X')

    def test_servicedefinition_create_extension_serializes_post_body(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible='DEVELOPER')
        srvd = sap.adt.businessservice.ServiceDefinition(
            conn, 'ZSAPCLI_TEST_SRV', package='$TMP', metadata=metadata,
            source_type=sap.adt.businessservice.SourceType.EXTENSION)
        srvd.description = 'Test service definition'
        srvd.create()

        self.assertEqual(len(conn.execs), 1)
        post = conn.execs[0]
        self.assertEqual(post.method, 'POST')
        self.assertEqual(post.adt_uri, '/sap/bc/adt/ddic/srvd/sources')

        self.maxDiff = None
        self.assertEqual(post.body.decode('utf-8'), SERVICE_DEFINITION_ADT_POST_REQUEST_XML_EXTENSION)

    def test_servicedefinition_text_property_round_trip(self):
        conn = Connection([Response(text=SERVICE_DEFINITION_SOURCE_TEXT,
                                    status_code=200,
                                    headers={'Content-Type': 'text/plain; charset=utf-8'})])

        srvd = sap.adt.businessservice.ServiceDefinition(conn, name='ZSAPCLI_TEST_SRV')
        code = srvd.text

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/ddic/srvd/sources/zsapcli_test_srv/source/main')])

        get_request = conn.execs[0]
        self.assertEqual(get_request.headers['Accept'], 'text/plain')
        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.body)

        self.assertEqual(code, SERVICE_DEFINITION_SOURCE_TEXT)

    def test_servicedefinition_open_editor_writes_source(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        srvd = sap.adt.businessservice.ServiceDefinition(conn, name='ZSAPCLI_TEST_SRV')
        with srvd.open_editor() as editor:
            editor.write(SERVICE_DEFINITION_SOURCE_TEXT)

        self.assertEqual(len(conn.execs), 3)

        put_request = conn.execs[1]
        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/ddic/srvd/sources/zsapcli_test_srv/source/main')
        self.assertEqual(put_request.headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(put_request.params, {'lockHandle': 'win'})
        self.assertEqual(put_request.body, bytes(SERVICE_DEFINITION_SOURCE_TEXT[:-1], 'utf-8'))

    def test_servicedefinition_create_serializes_post_body(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible='DEVELOPER')
        srvd = sap.adt.businessservice.ServiceDefinition(
            conn, 'ZSAPCLI_TEST_SRV', package='$TMP', metadata=metadata)
        srvd.description = 'Test service definition'
        srvd.create()

        self.assertEqual(len(conn.execs), 1)
        post = conn.execs[0]
        self.assertEqual(post.method, 'POST')
        self.assertEqual(post.adt_uri, '/sap/bc/adt/ddic/srvd/sources')

        self.maxDiff = None
        self.assertEqual(post.body.decode('utf-8'), SERVICE_DEFINITION_ADT_POST_REQUEST_XML)


class TestServiceBindingInit(unittest.TestCase):
    '''Constructor extensions: package, typ, version arguments'''

    def test_init_without_typ_version_keeps_binding_unset(self):
        # backward compatibility: existing rap binding publish callers pass
        # only (connection, name) and expect self.binding to remain None until
        # fetch() populates it.
        binding = sap.adt.businessservice.ServiceBinding(Connection(), 'TEST_BINDING')

        self.assertIsNone(binding.binding.typ)
        self.assertIsNone(binding.binding.version)
        self.assertIsNone(binding.binding.category)
        self.assertIsNotNone(binding.binding.implementation)
        self.assertEqual(binding.binding.implementation.name, '')
        self.assertEqual(binding.services, [])

    def test_init_with_typ_version_sets_binding_node_ui(self):
        binding = sap.adt.businessservice.ServiceBinding(
            Connection(), 'ZSAPCLI_TEST_BND',
            package='$TMP',
            typ='ODATA',
            version='V4',
            category='0',
        )

        self.assertIsNotNone(binding.binding)
        self.assertEqual(binding.binding.typ, 'ODATA')
        self.assertEqual(binding.binding.version, 'V4')
        self.assertEqual(binding.binding.category, '0')
        self.assertIsNotNone(binding.binding.implementation)
        self.assertEqual(binding.binding.implementation.name, '')

    def test_init_with_typ_version_sets_binding_node_api(self):
        binding = sap.adt.businessservice.ServiceBinding(
            Connection(), 'ZSAPCLI_TEST_BND',
            package='$TMP',
            typ='ODATA',
            version='V4',
            category='1'
        )

        self.assertIsNotNone(binding.binding)
        self.assertEqual(binding.binding.typ, 'ODATA')
        self.assertEqual(binding.binding.version, 'V4')
        self.assertEqual(binding.binding.category, '1')
        self.assertIsNotNone(binding.binding.implementation)
        self.assertEqual(binding.binding.implementation.name, '')

    def test_init_with_service_creates_services_link(self):
        binding = sap.adt.businessservice.ServiceBinding(
            Connection(), 'ZSAPCLI_TEST_BND',
            package='$TMP',
            typ='ODATA',
            version='V4',
            category='1',
        )

        # Live captures show <srvb:services srvb:name=...> always equals the
        # parent binding's name. The constructor must mirror that.
        binding.add_service('SERVICE_NAME', 'BINDING_NAME', '0001')
        self.assertEqual(len(binding.services), 1)

        link = binding.services[0]

        self.assertEqual(link.name, 'SERVICE_NAME')
        self.assertEqual(link.version, '0001')
        self.assertEqual(link.release_state, 'NOT_RELEASED')
        self.assertEqual(link.definition.name, 'BINDING_NAME')
        self.assertEqual(link.definition.typ, 'SRVD/SRV')

    def test_init_creates_full_post_body_ui(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible='DEVELOPER')
        binding = sap.adt.businessservice.ServiceBinding(
            conn, 'ZSAPCLI_TEST_BND',
            package='$TMP',
            typ='ODATA', version='V4', category='0',
            metadata=metadata,
        )
        binding.description = 'Test service binding'
        binding.add_service('ZSAPCLI_TEST_BND', 'ZSAPCLI_TEST_SRV', '0001')
        binding.create()

        self.assertEqual(len(conn.execs), 1)
        post = conn.execs[0]
        self.assertEqual(post.method, 'POST')
        self.assertEqual(post.adt_uri, '/sap/bc/adt/businessservices/bindings')

        self.maxDiff = None
        self.assertEqual(post.body.decode('utf-8'), SERVICE_BINDING_ADT_POST_ODATA_V4_REQUEST_XML_UI)

    def test_init_creates_full_post_body_api(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible='DEVELOPER')
        binding = sap.adt.businessservice.ServiceBinding(
            conn, 'ZSAPCLI_TEST_BND',
            package='$TMP',
            typ='ODATA', version='V4', category='1',
            metadata=metadata,
        )
        binding.description = 'Test service binding'
        binding.add_service('ZSAPCLI_TEST_BND', 'ZSAPCLI_TEST_SRV', '0001')
        binding.create()

        self.assertEqual(len(conn.execs), 1)
        post = conn.execs[0]
        self.assertEqual(post.method, 'POST')
        self.assertEqual(post.adt_uri, '/sap/bc/adt/businessservices/bindings')

        self.maxDiff = None
        self.assertEqual(post.body.decode('utf-8'), SERVICE_BINDING_ADT_POST_ODATA_V4_REQUEST_XML_API)


class TestServiceBindingGetServiceGroup(unittest.TestCase):
    '''ServiceBinding.get_service_group() path coverage tests.

       The method has four execution paths:
         1. binding.typ != 'ODATA'                       -> warn + None
         2. binding.typ == 'ODATA' and version == 'V2'   -> delegate to ODataV2ServiceList.get
         3. binding.typ == 'ODATA' and version == 'V4'   -> delegate to ODataV4ServiceGroup.get
         4. binding.typ == 'ODATA' and unknown version   -> warn + None
    '''

    def _make_binding(self, typ, version):
        binding = sap.adt.businessservice.ServiceBinding(Connection(), 'TEST_BINDING')
        binding.binding.typ = typ
        binding.binding.version = version
        return binding

    def _make_service(self, name='SRV_NAME', version='0001', definition_name='SRV_DEF'):
        service = sap.adt.businessservice.ServicesContainer()
        service.name = name
        service.link = sap.adt.businessservice.DefinitionLink()
        service.link.version = version
        service.link.definition = sap.adt.businessservice.Definition()
        service.link.definition.name = definition_name
        return service

    def test_get_service_group_returns_none_when_not_odata(self):
        binding = self._make_binding(typ='REST', version='V2')
        service = self._make_service()

        with self.assertLogs(level='WARNING') as captured:
            result = binding.get_service_group(service)

        self.assertIsNone(result)
        self.assertEqual(len(captured.records), 1)
        self.assertIn("TEST_BINDING", captured.records[0].getMessage())
        self.assertIn("REST", captured.records[0].getMessage())
        self.assertIn("expected 'ODATA'", captured.records[0].getMessage())

    def test_get_service_group_v2_delegates_to_odatav2_service_list(self):
        binding = self._make_binding(typ='ODATA', version='V2')
        service = self._make_service(name='SRV_NAME', version='0001', definition_name='SRV_DEF')

        sentinel = object()
        with mock.patch.object(
                sap.adt.businessservice.ODataV2ServiceList, 'get', return_value=sentinel) as v2_get, \
             mock.patch.object(
                sap.adt.businessservice.ODataV4ServiceGroup, 'get') as v4_get:
            result = binding.get_service_group(service)

        self.assertIs(result, sentinel)
        v2_get.assert_called_once_with(binding.connection, 'SRV_NAME', '0001', 'SRV_DEF')
        v4_get.assert_not_called()

    def test_get_service_group_v4_delegates_to_odatav4_service_group(self):
        binding = self._make_binding(typ='ODATA', version='V4')
        service = self._make_service(name='SRV_NAME', version='0002', definition_name='SRV_DEF')

        sentinel = object()
        with mock.patch.object(
                sap.adt.businessservice.ODataV4ServiceGroup, 'get', return_value=sentinel) as v4_get, \
             mock.patch.object(
                sap.adt.businessservice.ODataV2ServiceList, 'get') as v2_get:
            result = binding.get_service_group(service)

        self.assertIs(result, sentinel)
        v4_get.assert_called_once_with(binding.connection, 'SRV_NAME', '0002', 'SRV_DEF')
        v2_get.assert_not_called()

    def test_get_service_group_returns_none_for_unsupported_odata_version(self):
        binding = self._make_binding(typ='ODATA', version='V9')
        service = self._make_service()

        with mock.patch.object(sap.adt.businessservice.ODataV2ServiceList, 'get') as v2_get, \
             mock.patch.object(sap.adt.businessservice.ODataV4ServiceGroup, 'get') as v4_get, \
             self.assertLogs(level='WARNING') as captured:
            result = binding.get_service_group(service)

        self.assertIsNone(result)
        v2_get.assert_not_called()
        v4_get.assert_not_called()
        self.assertEqual(len(captured.records), 1)
        self.assertIn("TEST_BINDING", captured.records[0].getMessage())
        self.assertIn("V9", captured.records[0].getMessage())
        self.assertIn('unsupported OData version', captured.records[0].getMessage())


class TestODataV4ServiceGroupGet(unittest.TestCase):
    '''ODataV4ServiceGroup.get() HTTP request tests'''

    def test_service_group_get_sends_expected_request(self):
        connection = Connection([Response(
            text=SERVICE_GROUP_ODATAV4_GET_XML,
            status_code=200,
            content_type='application/vnd.sap.adt.businessservices.odatav4.v2+xml; charset=utf-8'
        )])

        service_group = sap.adt.businessservice.ODataV4ServiceGroup.get(
            connection,
            'ZSCLI_SVCDEMO_C',
            '0001',
            'ZSCLI_SVCDEMO_S',
        )

        self.assertEqual(len(connection.execs), 1)

        get_request = connection.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(
            get_request.adt_uri,
            '/sap/bc/adt/businessservices/odatav4/ZSCLI_SVCDEMO_C',
        )
        self.assertEqual(get_request.params, {
            'servicename': 'ZSCLI_SVCDEMO_C',
            'serviceversion': '0001',
            'srvdname': 'ZSCLI_SVCDEMO_S',
        })
        self.assertEqual(
            get_request.headers['Accept'],
            'application/vnd.sap.adt.businessservices.odatav4.v2+xml',
        )

        # Verify complete deserialization of the response XML.
        self.assertEqual(service_group.published, 'true')
        self.assertEqual(
            service_group.service_url_prefix,
            '/sap/opu/odata4/sap/zscli_svcdemo_c/srvd/',
        )
        self.assertEqual(service_group.name, 'ZSCLI_SVCDEMO_C')

        service = service_group.services
        self.assertIsNotNone(service)
        self.assertEqual(service.repository_id, 'SRVD')
        self.assertEqual(service.service_id, 'ZSCLI_SVCDEMO_C')
        self.assertEqual(service.service_version, '0001')
        self.assertEqual(
            service.service_url,
            '/sap/opu/odata4/sap/zscli_svcdemo_c/srvd/sap/zscli_svcdemo_c/0001/',
        )
        self.assertEqual(service.annotation_url, '')
        self.assertEqual(service.created, 'true')

        service_information = service.service_information
        self.assertIsNotNone(service_information)
        self.assertEqual(service_information.service_name, 'ZSCLI_SVCDEMO_C')
        self.assertEqual(service_information.service_version, '0001')

        self.assertEqual(len(service_information.collection), 2)

        first_collection = service_information.collection[0]
        self.assertEqual(first_collection.name, 'Demo')
        self.assertEqual(first_collection.is_leading, 'false')
        self.assertEqual(first_collection.is_root, 'false')

        second_collection = service_information.collection[1]
        self.assertEqual(second_collection.name, 'FourthDemo')
        self.assertEqual(second_collection.is_leading, 'false')
        self.assertEqual(second_collection.is_root, 'false')

        application_details = service.application_details
        self.assertIsNotNone(application_details)
        self.assertEqual(application_details.application_state, 'NOT_DEPLOYED')
        self.assertEqual(application_details.application_description, 'Not deployed')
        self.assertEqual(application_details.application_id, '')


class TestODataV2ServiceListGet(unittest.TestCase):
    '''ODataV2ServiceList.get() HTTP request tests'''

    def test_service_list_get_sends_expected_request(self):
        connection = Connection([Response(
            text=SERVICE_GROUP_ODATAV2_GET_XML,
            status_code=200,
            content_type='application/vnd.sap.adt.businessservices.odatav2.v3+xml; charset=utf-8'
        )])

        service_list = sap.adt.businessservice.ODataV2ServiceList.get(
            connection,
            'ZSCLI_DM_B_V2',
            '0001',
            'ZSCLI_DM_B_V2',
        )

        self.assertEqual(len(connection.execs), 1)

        get_request = connection.execs[0]
        self.assertEqual(get_request.method, 'GET')
        self.assertEqual(
            get_request.adt_uri,
            '/sap/bc/adt/businessservices/odatav2/ZSCLI_DM_B_V2',
        )
        self.assertEqual(get_request.params, {
            'servicename': 'ZSCLI_DM_B_V2',
            'serviceversion': '0001',
            'srvdname': 'ZSCLI_DM_B_V2',
        })
        self.assertEqual(
            get_request.headers['Accept'],
            'application/vnd.sap.adt.businessservices.odatav2.v3+xml',
        )

        self.assertIsNotNone(service_list.services)
        self.assertEqual(service_list.services.repository_id, '')
        self.assertEqual(service_list.services.service_id, 'ZSCLI_DM_B_V2')
        self.assertEqual(service_list.services.service_version, '0001')
        self.assertEqual(service_list.services.service_url, '/sap/opu/odata/sap/ZSCLI_DM_B_V2')
        self.assertEqual(service_list.services.annotation_url, '')
        self.assertEqual(service_list.services.created, 'true')
        self.assertEqual(service_list.services.published, 'true')
        self.assertEqual(service_list.services.allowed_action, 'UNPUBLISH')


        service_information = service_list.services.service_information
        self.assertIsNotNone(service_information)
        self.assertEqual(service_information.service_name, 'ZSCLI_DM_B_V2')
        self.assertEqual(service_information.service_version, '0007')

        self.assertEqual(len(service_information.collection), 2)

        first_collection = service_information.collection[0]
        self.assertEqual(first_collection.name, 'Demo')
        self.assertEqual(first_collection.is_leading, 'false')
        self.assertEqual(first_collection.is_root, 'true')

        second_collection = service_information.collection[1]
        self.assertEqual(second_collection.name, 'SecondDemo')
        self.assertEqual(second_collection.is_leading, 'true')
        self.assertEqual(second_collection.is_root, 'false')
