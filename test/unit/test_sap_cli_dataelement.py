#!/usr/bin/env python3

import unittest
from unittest.mock import call
from sap.adt.errors import ExceptionResourceAlreadyExists

import sap.cli.dataelement
from sap.errors import SAPCliError

from mock import (
    Connection,
    Response,
    Request,
    patch,
)
from io import StringIO

from infra import generate_parse_args
from fixtures_adt_dataelement import (
    DATA_ELEMENT_NAME,
    CREATE_DATA_ELEMENT_ADT_XML,
    READ_DATA_ELEMENT_BODY,
    FAKE_LOCK_HANDLE,
    ACTIVATE_DATA_ELEMENT_BODY,
    DATA_ELEMENT_DEFINITION_ADT_XML,
    DEFINE_DATA_ELEMENT_W_DOMAIN_BODY,
    DEFINE_DATA_ELEMENT_W_PREDEFINED_ABAP_TYPE_BODY,
    ERROR_XML_DATA_ELEMENT_ALREADY_EXISTS
)
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK

parse_args = generate_parse_args(sap.cli.dataelement.CommandGroup())


class TestDataElementCreate(unittest.TestCase):

    def data_element_create_cmd(self, *args, **kwargs):
        return parse_args('create', *args, **kwargs)

    def test_create(self):
        connection = Connection()

        the_cmd = self.data_element_create_cmd(DATA_ELEMENT_NAME, 'Test data element', 'package')
        the_cmd.execute(connection, the_cmd)

        exptected_request = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request)


class TestDataElementActivate(unittest.TestCase):

    def data_element_activate_cmd(self, *args, **kwargs):
        return parse_args('activate', *args, **kwargs)

    def test_activate(self):
        connection = Connection([
            RESPONSE_ACTIVATION_OK,
            Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})
        ])

        the_cmd = self.data_element_activate_cmd(DATA_ELEMENT_NAME)
        the_cmd.execute(connection, the_cmd)

        expected_request = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=ACTIVATE_DATA_ELEMENT_BODY,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        self.assertEqual(connection.execs[0], expected_request)


class TestDataElementDefine(unittest.TestCase):

    def data_element_define_cmd(self, *args, **kwargs):
        return parse_args('define', *args, **kwargs)

    @patch('sap.cli.core.PrintConsole.printerr')
    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    def test_define_w_domain(self, fake_lock, fake_unlock, fake_console_print_err):
        connection = Connection([
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            Response(
                text=READ_DATA_ELEMENT_BODY,
                status_code=200,
                headers={}
            ),
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            RESPONSE_ACTIVATION_OK,
            Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})
        ], asserter=self)

        the_cmd = self.data_element_define_cmd(DATA_ELEMENT_NAME, 'Test data element', 'package', '--activate', '--type=domain', '--domain_name=ABC', '--label_short=Tst DTEL', '--label_medium=Test Label Medium', '--label_long=Test Label Long', '--label_heading=Test Label Heading')
        with patch('sys.stdin', StringIO(DATA_ELEMENT_DEFINITION_ADT_XML)):
            the_cmd.execute(connection, the_cmd)

        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()
        fake_console_print_err.assert_not_called()

        self.assertEqual(len(connection.execs), 5)

        exptected_request_create = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request_create)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[1], expected_request_fetch)

        expected_request_push = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='PUT',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(DEFINE_DATA_ELEMENT_W_DOMAIN_BODY, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )

        self.assertEqual(connection.execs[2], expected_request_push)

        expected_request_activate = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=ACTIVATE_DATA_ELEMENT_BODY,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        self.assertEqual(connection.execs[3], expected_request_activate)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[4], expected_request_fetch)

    @patch('sap.cli.core.PrintConsole.printerr')
    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    def test_define_w_predefined_abap_type(self, fake_lock, fake_unlock, fake_console_print_err):
        connection = Connection([
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            Response(
                text=READ_DATA_ELEMENT_BODY,
                status_code=200,
                headers={}
            ),
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            RESPONSE_ACTIVATION_OK,
            Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})
        ], asserter=self)

        the_cmd = self.data_element_define_cmd(DATA_ELEMENT_NAME, 'Test data element', 'package', '--activate', '--type=predefinedAbapType', '--data_type=STRING', '--data_type_length=200', '--label_short=Tst DTEL', '--label_medium=Test Label Medium', '--label_long=Test Label Long', '--label_heading=Test Label Heading')
        with patch('sys.stdin', StringIO(DATA_ELEMENT_DEFINITION_ADT_XML)):
            the_cmd.execute(connection, the_cmd)

        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()
        fake_console_print_err.assert_not_called()

        self.assertEqual(len(connection.execs), 5)

        exptected_request_create = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request_create)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[1], expected_request_fetch)

        expected_request_push = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='PUT',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(DEFINE_DATA_ELEMENT_W_PREDEFINED_ABAP_TYPE_BODY, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )

        self.assertEqual(connection.execs[2], expected_request_push)

        expected_request_activate = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=ACTIVATE_DATA_ELEMENT_BODY,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        self.assertEqual(connection.execs[3], expected_request_activate)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[4], expected_request_fetch)

    @patch('sap.cli.core.PrintConsole.printerr')
    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    def test_define_domain_not_provided(self, fake_lock, fake_unlock, fake_console_print_err):
        connection = Connection([
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            Response(
                text=READ_DATA_ELEMENT_BODY,
                status_code=200,
                headers={}
            ),
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            RESPONSE_ACTIVATION_OK,
            Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})
        ], asserter=self)

        # --domain_name argument is missing
        the_cmd = self.data_element_define_cmd(DATA_ELEMENT_NAME, 'Test data element', 'package', '--activate', '--type=domain', '--data_type=STRING', '--label_short=Tst DTEL', '--label_medium=Test Label Medium', '--label_long=Test Label Long', '--label_heading=Test Label Heading')
        with patch('sys.stdin', StringIO(DATA_ELEMENT_DEFINITION_ADT_XML)):
            the_cmd.execute(connection, the_cmd)

        fake_lock.assert_not_called()
        fake_unlock.assert_not_called()
        fake_console_print_err.assert_called_once_with('Domain name must be provided (--domain_name) if the type (--type) is "domain"')

        self.assertEqual(len(connection.execs), 2)

        exptected_request_create = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request_create)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[1], expected_request_fetch)

    @patch('sap.cli.core.PrintConsole.printerr')
    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    def test_define_predefined_abap_type_not_provided(self, fake_lock, fake_unlock, fake_console_print_err):
        connection = Connection([
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            Response(
                text=READ_DATA_ELEMENT_BODY,
                status_code=200,
                headers={}
            ),
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            RESPONSE_ACTIVATION_OK,
            Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})
        ], asserter=self)

        # --data_type argument is missing
        the_cmd = self.data_element_define_cmd(DATA_ELEMENT_NAME, 'Test data element', 'package', '--activate', '--type=predefinedAbapType', '--domain_name=ABC', '--label_short=Tst DTEL', '--label_medium=Test Label Medium', '--label_long=Test Label Long', '--label_heading=Test Label Heading')
        with patch('sys.stdin', StringIO(DATA_ELEMENT_DEFINITION_ADT_XML)):
            the_cmd.execute(connection, the_cmd)

        fake_lock.assert_not_called()
        fake_unlock.assert_not_called()
        fake_console_print_err.assert_called_once_with('Data type name must be provided (--data_type) if the type (--type) is "predefinedAbapType"')

        self.assertEqual(len(connection.execs), 2)

        exptected_request_create = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request_create)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[1], expected_request_fetch)

    @patch('sap.cli.core.PrintConsole.printerr')
    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    def test_define_data_element_already_exists(self, fake_lock, fake_unlock, fake_console_print_err):
        connection = Connection([
            Response(
                text=ERROR_XML_DATA_ELEMENT_ALREADY_EXISTS,
                status_code=500,
                headers={'content-type': 'application/xml'}
            ),
            Response(
                text=READ_DATA_ELEMENT_BODY,
                status_code=200,
                headers={}
            ),
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            RESPONSE_ACTIVATION_OK,
            Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})
        ], asserter=self)

        the_cmd = self.data_element_define_cmd(DATA_ELEMENT_NAME, 'Test data element', 'package', '--activate', '--type=domain', '--domain_name=ABC', '--label_short=Tst DTEL', '--label_medium=Test Label Medium', '--label_long=Test Label Long', '--label_heading=Test Label Heading')
        with patch('sys.stdin', StringIO(DATA_ELEMENT_DEFINITION_ADT_XML)):
            try:
                the_cmd.execute(connection, the_cmd)

                self.fail('Exception should be raised but it has not been')
            except ExceptionResourceAlreadyExists as e:
                self.assertEqual('Resource Data Element TEST_DATA_ELEMENT does already exist.', str(e))

        fake_lock.assert_not_called()
        fake_unlock.assert_not_called()
        fake_console_print_err.assert_not_called()

        self.assertEqual(len(connection.execs), 1)

        exptected_request_create = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request_create)

    @patch('sap.cli.core.PrintConsole.printerr')
    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    def test_define_data_element_already_exists_but_skipped(self, fake_lock, fake_unlock, fake_console_print_err):
        connection = Connection([
            Response(
                text=ERROR_XML_DATA_ELEMENT_ALREADY_EXISTS,
                status_code=500,
                headers={'content-type': 'application/xml'}
            ),
            Response(
                text=READ_DATA_ELEMENT_BODY,
                status_code=200,
                headers={}
            ),
            Response(
                text='',
                status_code=200,
                headers={}
            ),
            RESPONSE_ACTIVATION_OK,
            Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})
        ], asserter=self)

        the_cmd = self.data_element_define_cmd(DATA_ELEMENT_NAME, 'Test data element', 'package', '--activate', '--no-error-existing', '--type=domain', '--domain_name=ABC', '--label_short=Tst DTEL', '--label_medium=Test Label Medium', '--label_long=Test Label Long', '--label_heading=Test Label Heading')
        with patch('sys.stdin', StringIO(DATA_ELEMENT_DEFINITION_ADT_XML)):
            the_cmd.execute(connection, the_cmd)

        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()
        fake_console_print_err.assert_not_called()

        self.assertEqual(len(connection.execs), 5)

        exptected_request_create = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request_create)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[1], expected_request_fetch)

        expected_request_push = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='PUT',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(DEFINE_DATA_ELEMENT_W_DOMAIN_BODY, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )

        self.assertEqual(connection.execs[2], expected_request_push)

        expected_request_activate = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=ACTIVATE_DATA_ELEMENT_BODY,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        self.assertEqual(connection.execs[3], expected_request_activate)

        expected_request_fetch = Request(
            adt_uri=f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NAME.lower()}',
            method='GET',
            headers=None,
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[4], expected_request_fetch)
