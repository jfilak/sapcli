#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, PropertyMock

from sap.errors import SAPCliError
import sap.adt.wb

from sap.adt.objects import ADTObjectReferences

from mock import Connection, Response, Request
from fixtures_adt import EMPTY_RESPONSE_OK
from fixtures_adt_wb import ACTIVATION_REFERENCES_XML, INACTIVE_OBJECTS_XML, PREAUDIT_ACTIVATION_XML, \
         RESPONSE_INACTIVE_OBJECTS_V1, ACTIVATION_WARNING_XML, ACTIVATION_WITH_PROPERTIES_XML, \
         ACTIVATION_ERROR_XML


FIXTURES_EXP_FULL_ADT_URI = '/unit/test/mobject'
FIXTURES_EXP_OBJECT_NAME = 'MOBJECT'

FIXTURES_ACTIVATION_REQUEST_SINGLE = f'''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="{FIXTURES_EXP_FULL_ADT_URI}" adtcore:name="{FIXTURES_EXP_OBJECT_NAME}"/>
</adtcore:objectReferences>'''


class TestIOCEntryData(unittest.TestCase):

    def test_forward_reference_properties(self):
        entry = sap.adt.wb.IOCEntryData()

        entry.reference.name = 'Name'
        entry.reference.typ = 'Type'
        entry.reference.uri = 'URI'
        entry.reference.parent_uri = 'Parent URI'
        entry.reference.description = 'Description'

        self.assertEqual(entry.reference.name, entry.name)
        self.assertEqual(entry.reference.typ, entry.typ)
        self.assertEqual(entry.reference.uri, entry.uri)
        self.assertEqual(entry.reference.parent_uri, entry.parent_uri)
        self.assertEqual(entry.reference.description, entry.description)


class TestADTWBActivate(unittest.TestCase):

    def create_fake_object(self, full_adt_uri, name, responses=None):
        conn = Connection(responses=responses)

        adt_object = Mock()
        adt_object.full_adt_uri = full_adt_uri
        adt_object.name = name
        adt_object.connection = conn
        
        # default state of the mocked object is "not activated"
        adt_object.active = 'inactive'

        return adt_object

    def assert_single_request(self, fake_adt_object):
        conn = fake_adt_object.connection


        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/activation')])

        self.assertEqual(sorted(conn.execs[0].headers),  ['Accept', 'Content-Type'])
        self.assertEqual(conn.execs[0].headers['Accept'], 'application/xml')
        self.assertEqual(conn.execs[0].headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(conn.execs[0].params),  ['method', 'preauditRequested'])
        self.assertEqual(conn.execs[0].params['method'], 'activate')
        self.assertEqual(conn.execs[0].params['preauditRequested'], 'true')

        self.maxDiff = None
        self.assertEqual(conn.execs[0].body, FIXTURES_ACTIVATION_REQUEST_SINGLE)

        self.assertTrue(fake_adt_object.fetch.called)

    def test_adt_wb_activate_object_ok(self):
        # user lower case name
        adt_object = self.create_fake_object(FIXTURES_EXP_FULL_ADT_URI, FIXTURES_EXP_OBJECT_NAME.lower())
        adt_object.active = 'active'

        check_results = sap.adt.wb.activate(adt_object)
        self.assert_single_request(adt_object)
        
        # this is check for generated propeerty, which is no longer used by activation engine,
        # but is still part of the CheckResults API for backward compatibility -> and needs to
        # be tested to keep coverage
        self.assertTrue(check_results.generated)

        # user upper case name
        adt_object = self.create_fake_object(FIXTURES_EXP_FULL_ADT_URI, FIXTURES_EXP_OBJECT_NAME.upper())
        adt_object.active = 'active'
        sap.adt.wb.activate(adt_object)
        self.assert_single_request(adt_object)

    def test_adt_wb_activate_object_ok_with_props(self):
        adt_object = self.create_fake_object(FIXTURES_EXP_FULL_ADT_URI,
                                             FIXTURES_EXP_OBJECT_NAME.lower(),
                                             [Response(status_code=200,
                                                       text=ACTIVATION_WITH_PROPERTIES_XML,
                                                       headers={})])
        # simulate activation
        adt_object.active = 'active'

        check_results = sap.adt.wb.activate(adt_object)
        self.assert_single_request(adt_object)

        # this is check for generated propeerty, which is no longer used by activation engine,
        # but is still part of the CheckResults API for backward compatibility -> and needs to
        # be tested to keep coverage
        self.assertTrue(check_results.generated)

    def test_adt_wb_activate_object_fail(self):
        adt_object = self.create_fake_object(FIXTURES_EXP_FULL_ADT_URI, FIXTURES_EXP_OBJECT_NAME)
        adt_object.connection = Connection([Response(status_code=200,
                                                     text=ACTIVATION_ERROR_XML,
                                                     headers={})])

        with self.assertRaises(SAPCliError) as caught:
            sap.adt.wb.activate(adt_object)

        self.assert_single_request(adt_object)
        self.assertEqual(str(caught.exception),
                         f'Could not activate: {ACTIVATION_ERROR_XML}')

    def test_adt_wb_activate_children(self):
        adt_object = self.create_fake_object('/sap/bc/adt/oo/classes/cl_hello_world',
                                             'cl_hello_world',
                                             [RESPONSE_INACTIVE_OBJECTS_V1, EMPTY_RESPONSE_OK])
        # simulate activation
        adt_object.active = 'active'

        sap.adt.wb.activate(adt_object)

        conn = adt_object.connection

        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/activation')] * 2)

        self.assertEqual(sorted(conn.execs[0].headers),  ['Accept', 'Content-Type'])
        self.assertEqual(conn.execs[0].headers['Accept'], 'application/xml')
        self.assertEqual(conn.execs[0].headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(conn.execs[0].params),  ['method', 'preauditRequested'])
        self.assertEqual(conn.execs[0].params['method'], 'activate')
        self.assertEqual(conn.execs[0].params['preauditRequested'], 'true')

        self.assertEqual(sorted(conn.execs[1].headers),  ['Accept', 'Content-Type'])
        self.assertEqual(conn.execs[1].headers['Accept'], 'application/xml')
        self.assertEqual(conn.execs[1].headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(conn.execs[1].params),  ['method', 'preauditRequested'])
        self.assertEqual(conn.execs[1].params['method'], 'activate')
        self.assertEqual(conn.execs[1].params['preauditRequested'], 'false')

        self.maxDiff = None
        self.assertEqual(conn.execs[0].body, PREAUDIT_ACTIVATION_XML)
        self.assertEqual(conn.execs[1].body, ACTIVATION_REFERENCES_XML)

    def test_adt_wb_activation_warnings(self):
        adt_object = self.create_fake_object('/sap/bc/adt/oo/classes/cl_hello_world',
                                             'cl_hello_world',
                                             [Response(status_code=200,
                                                       text=ACTIVATION_WARNING_XML,
                                                       headers={})])

        # simulate activation
        adt_object.active = 'active'

        results = sap.adt.wb.activate(adt_object)

        self.assertTrue(results.generated)
        self.assertTrue(results.has_warnings)
        self.assertFalse(results.has_errors)

        messages = results.messages

        self.assertEqual(len(messages), 2)

        self.assertEqual(messages[0].typ, 'W')
        self.assertEqual(messages[0].short_text, 'Message 1')
        self.assertEqual(messages[0].force_supported, 'true')

        self.assertEqual(messages[1].typ, 'W')
        self.assertEqual(messages[1].short_text, 'Warning 2')
        self.assertEqual(messages[1].force_supported, 'true')


class TestADTWBFetchInactive(unittest.TestCase):

    def test_fetch_inactive_objects(self):
        exp_request = Request.get(adt_uri='activation/inactiveobjects')

        conn = Connection(responses=[(RESPONSE_INACTIVE_OBJECTS_V1, exp_request)])
        conn.asserter = self

        my_inactive_objects = sap.adt.wb.fetch_inactive_objects(conn)

        self.assertEqual(my_inactive_objects.entries[0].transport.reference.name, 'C50K000377')
        self.assertEqual(my_inactive_objects.entries[1].object.reference.name, 'CL_HELLO_WORLD')


class TestADTWBTryMassActivate(unittest.TestCase):

    def test_parse_activation_warnings(self):
        conn = Connection(responses=[Response(
            status_code=200,
            text=ACTIVATION_WARNING_XML,
            content_type='application/xml'
        )])

        adt_object = Mock()
        adt_object.full_adt_uri = 'BAR'
        adt_object.name = 'FOO'
        adt_object.connection = conn

        references = ADTObjectReferences()
        references.add_object(adt_object)

        messages = sap.adt.wb.try_mass_activate(conn, references)
        self.assertEqual(len(messages), 2)

        self.assertEqual(messages[0].typ, 'W')
        self.assertEqual(messages[0].short_text, 'Message 1')
        self.assertEqual(messages[0].force_supported, 'true')

        self.assertEqual(messages[1].typ, 'W')
        self.assertEqual(messages[1].short_text, 'Warning 2')
        self.assertEqual(messages[1].force_supported, 'true')


class TestCheckMessage(unittest.TestCase):

    def test_check_message_is_errror(self):
        message = sap.adt.wb.CheckMessage()
        message.typ = sap.adt.wb.CheckMessage.Type.ERROR

        self.assertTrue(message.is_error)

    def test_check_message_is_errror_not(self):
        message = sap.adt.wb.CheckMessage()
        message.typ = sap.adt.wb.CheckMessage.Type.WARNING

        self.assertFalse(message.is_error)


if __name__ == '__main__':
    unittest.main()
