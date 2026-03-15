#!/usr/bin/env python3

import unittest

import sap.adt.whereused
from sap.adt.marshalling import Marshal

from mock import Connection, Response, Request
from fixtures_adt_whereused import (
    WHEREUSED_SCOPE_REQUEST_XML,
    WHEREUSED_SCOPE_RESPONSE_XML,
    WHEREUSED_SEARCH_REQUEST_XML,
    WHEREUSED_SEARCH_RESPONSE_ZERO_RESULTS_XML,
    WHEREUSED_SEARCH_RESPONSE_WITH_RESULTS_XML,
)

OBJECT_URI = '/sap/bc/adt/programs/programs/z_test_report_xyz/source/main?version=active#start=1,1'


class TestUsageScopeRequest(unittest.TestCase):

    def test_serialization(self):
        request = sap.adt.whereused.UsageScopeRequest()
        xml = Marshal().serialize(request)
        self.assertEqual(xml, WHEREUSED_SCOPE_REQUEST_XML)


class TestUsageScopeResult(unittest.TestCase):

    def test_deserialization(self):
        result = sap.adt.whereused.UsageScopeResult()
        Marshal.deserialize(WHEREUSED_SCOPE_RESPONSE_XML, result)

        self.assertEqual(result.local_usage, 'false')
        self.assertEqual(result.object_identifier.display_name, 'Z_TEST_REPORT_XYZ (Program)')
        self.assertEqual(result.object_identifier.global_type, 'PROG/P')
        self.assertEqual(result.grade.definitions, 'false')
        self.assertEqual(result.grade.elements, 'false')
        self.assertEqual(result.grade.indirect_references, 'true')
        self.assertEqual(len(result.object_types), 3)
        self.assertEqual(result.object_types[0].name, 'CLAS/OC')
        self.assertEqual(result.object_types[0].is_selected, 'true')
        self.assertEqual(result.object_types[0].is_default, 'true')
        self.assertEqual(result.object_types[1].name, 'INTF/OI')
        self.assertEqual(result.object_types[2].name, 'PROG/P')
        self.assertEqual(result.payload, 'dGVzdHBheWxvYWRiYXNlNjQ=')


class TestUsageReferenceRequest(unittest.TestCase):

    def test_serialization(self):
        scope_result = sap.adt.whereused.UsageScopeResult()
        Marshal.deserialize(WHEREUSED_SCOPE_RESPONSE_XML, scope_result)

        request = sap.adt.whereused.UsageReferenceRequest()
        scope = request.scope

        scope.local_usage = scope_result.local_usage
        scope.object_identifier = scope_result.object_identifier
        scope.grade = scope_result.grade
        scope.object_types = scope_result.object_types
        scope.payload = scope_result.payload

        xml = Marshal().serialize(request)
        self.assertEqual(xml, WHEREUSED_SEARCH_REQUEST_XML)


class TestUsageReferenceResult(unittest.TestCase):

    def test_deserialization_zero_results(self):
        result = sap.adt.whereused.UsageReferenceResult()
        Marshal.deserialize(WHEREUSED_SEARCH_RESPONSE_ZERO_RESULTS_XML, result)

        self.assertEqual(result.number_of_results, '0')
        self.assertEqual(result.result_description, '[A4H] Where-Used List: Z_TEST_REPORT_XYZ (Program)')
        self.assertEqual(result.referenced_object_identifier, '')
        self.assertEqual(len(result.referenced_objects), 0)

    def test_deserialization_with_results(self):
        result = sap.adt.whereused.UsageReferenceResult()
        Marshal.deserialize(WHEREUSED_SEARCH_RESPONSE_WITH_RESULTS_XML, result)

        self.assertEqual(result.number_of_results, '2')
        self.assertEqual(result.result_description, '[A4H] Where-Used List: Z_TEST_REPORT_XYZ (Program)')
        self.assertEqual(len(result.referenced_objects), 2)

        obj1 = result.referenced_objects[0]
        self.assertEqual(obj1.uri, '/sap/bc/adt/oo/classes/zcl_abapgit_abap_language_vers')
        self.assertEqual(obj1.parent_uri, '/sap/bc/adt/packages/%24abapgit_env')
        self.assertEqual(obj1.is_result, 'false')
        self.assertEqual(obj1.can_have_children, 'false')
        self.assertEqual(obj1.adt_object.name, 'ZCL_ABAPGIT_ABAP_LANGUAGE_VERS')
        self.assertEqual(obj1.adt_object.typ, 'CLAS/OC')
        self.assertEqual(obj1.adt_object.responsible, 'DEVELOPER')
        self.assertEqual(obj1.adt_object.package_ref.name, '$ABAPGIT_ENV')
        self.assertEqual(obj1.adt_object.package_ref.typ, 'DEVC/K')

        obj2 = result.referenced_objects[1]
        self.assertEqual(obj2.uri, '/sap/bc/adt/oo/classes/zcl_abapgit_abap_language_vers/includes/testclasses')
        self.assertEqual(obj2.can_have_children, 'true')
        self.assertEqual(obj2.usage_information, 'gradeDirect,includeTest')
        self.assertEqual(obj2.adt_object.name, 'Local Test Classes')
        self.assertEqual(obj2.adt_object.package_ref.name, '$ABAPGIT_ENV')


class TestGetScope(unittest.TestCase):

    def test_get_scope(self):
        conn = Connection([Response(status_code=200,
                                    content_type=sap.adt.whereused.SCOPE_RESPONSE_MIME_TYPE,
                                    text=WHEREUSED_SCOPE_RESPONSE_XML)])

        result = sap.adt.whereused.get_scope(conn, OBJECT_URI)

        self.assertEqual(len(conn.execs), 1)
        req = conn.execs[0]
        self.assertEqual(req.method, 'POST')
        self.assertIn('repository/informationsystem/usageReferences/scope', req.adt_uri)
        self.assertEqual(req.params, {'uri': OBJECT_URI, 'version': 'active'})
        self.assertEqual(req.headers['Accept'], sap.adt.whereused.SCOPE_RESPONSE_MIME_TYPE)
        self.assertEqual(req.headers['Content-Type'], sap.adt.whereused.SCOPE_REQUEST_MIME_TYPE)
        self.assertEqual(req.body, WHEREUSED_SCOPE_REQUEST_XML)

        self.assertEqual(result.local_usage, 'false')
        self.assertEqual(result.object_identifier.display_name, 'Z_TEST_REPORT_XYZ (Program)')


class TestGetWhereUsed(unittest.TestCase):

    def test_get_where_used(self):
        conn = Connection([Response(status_code=200,
                                    content_type=sap.adt.whereused.SEARCH_RESPONSE_MIME_TYPE,
                                    text=WHEREUSED_SEARCH_RESPONSE_WITH_RESULTS_XML)])

        scope_result = sap.adt.whereused.UsageScopeResult()
        Marshal.deserialize(WHEREUSED_SCOPE_RESPONSE_XML, scope_result)

        result = sap.adt.whereused.get_where_used(conn, OBJECT_URI, scope_result)

        self.assertEqual(len(conn.execs), 1)
        req = conn.execs[0]
        self.assertEqual(req.method, 'POST')
        self.assertIn('repository/informationsystem/usageReferences', req.adt_uri)
        self.assertEqual(req.params, {'uri': OBJECT_URI, 'version': 'active'})
        self.assertEqual(req.headers['Accept'], sap.adt.whereused.SEARCH_RESPONSE_MIME_TYPE)
        self.assertEqual(req.headers['Content-Type'], sap.adt.whereused.SEARCH_REQUEST_MIME_TYPE)
        self.assertEqual(req.body, WHEREUSED_SEARCH_REQUEST_XML)

        self.assertEqual(result.number_of_results, '2')
        self.assertEqual(len(result.referenced_objects), 2)


class TestWhereUsed(unittest.TestCase):

    def test_where_used(self):
        conn = Connection([
            Response(status_code=200,
                     content_type=sap.adt.whereused.SCOPE_RESPONSE_MIME_TYPE,
                     text=WHEREUSED_SCOPE_RESPONSE_XML),
            Response(status_code=200,
                     content_type=sap.adt.whereused.SEARCH_RESPONSE_MIME_TYPE,
                     text=WHEREUSED_SEARCH_RESPONSE_WITH_RESULTS_XML),
        ])

        result = sap.adt.whereused.where_used(conn, OBJECT_URI)

        self.assertEqual(len(conn.execs), 2)

        scope_req = conn.execs[0]
        self.assertEqual(scope_req.method, 'POST')
        self.assertIn('usageReferences/scope', scope_req.adt_uri)

        search_req = conn.execs[1]
        self.assertEqual(search_req.method, 'POST')
        self.assertIn('usageReferences', search_req.adt_uri)
        self.assertNotIn('scope', search_req.adt_uri.split('usageReferences')[1])

        self.assertEqual(result.number_of_results, '2')
        self.assertEqual(len(result.referenced_objects), 2)


if __name__ == '__main__':
    unittest.main()
