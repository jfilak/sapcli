#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import sap.cli.tabletype
from sap.cli.core import InvalidCommandLineError
from sap.adt.errors import ExceptionResourceAlreadyExists

from mock import (
    ConsoleOutputTestCase,
    Connection,
    Response,
    Request,
)

from infra import generate_parse_args
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK
from fixtures_sap_adt_tabletype import (
    TABLE_TYPE_NAME,
    FAKE_LOCK_HANDLE,
    TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML,
    TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML,
    TABLE_TYPE_ADT_NEW_OBJECT_REQUEST_XML,
    TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML,
    TABLE_TYPE_ADT_DEFINE_SORTED_REQUEST_XML,
    TABLE_TYPE_ADT_ACTIVATE_REQUEST_XML,
    TABLE_TYPE_ADT_ALREADY_EXISTS_RESPONSE_XML,
)

parse_args = generate_parse_args(sap.cli.tabletype.CommandGroup())

TABLE_TYPE_MIME = 'application/vnd.sap.adt.tabletype.v1+xml; charset=utf-8'
TABLE_TYPE_URI = f'/sap/bc/adt/ddic/tabletypes/{TABLE_TYPE_NAME.lower()}'

EXPECTED_REQUEST_CREATE = Request(
    adt_uri='/sap/bc/adt/ddic/tabletypes',
    method='POST',
    headers={'Content-Type': TABLE_TYPE_MIME},
    body=bytes(TABLE_TYPE_ADT_NEW_OBJECT_REQUEST_XML, 'utf-8'),
    params=None
)

EXPECTED_REQUEST_FETCH = Request(
    adt_uri=TABLE_TYPE_URI,
    method='GET',
    headers=None,
    body=None,
    params=None
)


def response_ok(text=''):
    return Response(text=text, status_code=200, headers={})


def response_already_exists():
    return Response(text=TABLE_TYPE_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                    headers={'content-type': 'application/xml'})


class TestTableTypeCommands(unittest.TestCase):

    def test_read_not_supported(self):
        with self.assertRaises(SystemExit):
            parse_args('read', TABLE_TYPE_NAME)

    def test_write_not_supported(self):
        with self.assertRaises(SystemExit):
            parse_args('write', TABLE_TYPE_NAME, '-')


class TestTableTypeCreate(ConsoleOutputTestCase):

    def test_create(self):
        connection = Connection(user='DEVELOPER')

        args = parse_args('create', TABLE_TYPE_NAME.lower(), 'Test table type', '$tmp')
        args.execute(connection, args)

        self.assertEqual(len(connection.execs), 1)
        EXPECTED_REQUEST_CREATE.assertEqual(connection.execs[0], self)


class TestTableTypeActivate(ConsoleOutputTestCase):

    def test_activate(self):
        connection = Connection([RESPONSE_ACTIVATION_OK, response_ok(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)])

        args = parse_args('activate', TABLE_TYPE_NAME)
        args.console_factory = lambda: self.console
        args.execute(connection, args)

        expected_request = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=TABLE_TYPE_ADT_ACTIVATE_REQUEST_XML,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        expected_request.assertEqual(connection.execs[0], self)


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
class TestTableTypeDefine(ConsoleOutputTestCase):

    def define(self, connection, *argv):
        args = parse_args('define', TABLE_TYPE_NAME, 'Test table type', '$TMP', *argv)
        args.console_factory = lambda: self.console
        return args.execute(connection, args)

    def test_define_standard(self, fake_lock, fake_unlock):
        connection = Connection([
            response_ok(),
            response_ok(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML),
            response_ok(),
        ], user='DEVELOPER')

        retval = self.define(connection, '--row-type', 'bapiret2')

        self.assertEqual(retval, 0)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(len(connection.execs), 3)
        EXPECTED_REQUEST_CREATE.assertEqual(connection.execs[0], self)
        EXPECTED_REQUEST_FETCH.assertEqual(connection.execs[1], self)

        expected_request_push = Request(
            adt_uri=TABLE_TYPE_URI,
            method='PUT',
            headers={'Content-Type': TABLE_TYPE_MIME},
            body=bytes(TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )
        expected_request_push.assertEqual(connection.execs[2], self)

        self.assertConsoleContents(self.console, stdout=f'''Creating table type {TABLE_TYPE_NAME}
Defining table type {TABLE_TYPE_NAME}
''')

    def test_define_sorted_activate(self, fake_lock, fake_unlock):
        connection = Connection([
            response_ok(),
            response_ok(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML),
            response_ok(),
            RESPONSE_ACTIVATION_OK,
            response_ok(TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML),
        ], user='DEVELOPER')

        retval = self.define(connection, '--row-type', 'BAPIRET2', '--access-type', 'sorted',
                             '--key-definition', 'keyComponents', '--key-kind', 'unique',
                             '--key-component', 'type', '--key-component', 'ID', '--activate')

        self.assertEqual(retval, 0)
        self.assertEqual(len(connection.execs), 5)

        expected_request_push = Request(
            adt_uri=TABLE_TYPE_URI,
            method='PUT',
            headers={'Content-Type': TABLE_TYPE_MIME},
            body=bytes(TABLE_TYPE_ADT_DEFINE_SORTED_REQUEST_XML, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )
        expected_request_push.assertEqual(connection.execs[2], self)

        self.assertEqual(connection.execs[3].adt_uri, '/sap/bc/adt/activation')
        self.assertEqual(connection.execs[3].body, TABLE_TYPE_ADT_ACTIVATE_REQUEST_XML)

        self.assertTrue(self.console.capout.startswith(f'''Creating table type {TABLE_TYPE_NAME}
Defining table type {TABLE_TYPE_NAME}
Activating table type {TABLE_TYPE_NAME}
'''))

    def test_define_empty_key_kind_not_specified(self, fake_lock, fake_unlock):
        connection = Connection([
            response_ok(),
            response_ok(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML),
            response_ok(),
        ], user='DEVELOPER')

        self.define(connection, '--row-type', 'BAPIRET2', '--key-definition', 'empty')

        body = connection.execs[2].body.decode('utf-8')
        self.assertIn('<ttyp:definition>empty</ttyp:definition>', body)
        self.assertIn('<ttyp:kind>notSpecified</ttyp:kind>', body)

    def test_define_key_components_missing(self, fake_lock, fake_unlock):
        connection = Connection([])

        with self.assertRaises(InvalidCommandLineError) as caught:
            self.define(connection, '--row-type', 'BAPIRET2', '--key-definition', 'keyComponents')

        self.assertEqual(str(caught.exception),
                         'The key definition keyComponents requires at least one --key-component')
        self.assertEqual(connection.execs, [])

    def test_define_key_components_not_expected(self, fake_lock, fake_unlock):
        connection = Connection([])

        with self.assertRaises(InvalidCommandLineError) as caught:
            self.define(connection, '--row-type', 'BAPIRET2', '--key-component', 'TYPE')

        self.assertEqual(str(caught.exception),
                         '--key-component can be used only with --key-definition keyComponents')
        self.assertEqual(connection.execs, [])

    def test_define_already_exists(self, fake_lock, fake_unlock):
        connection = Connection([response_already_exists()], user='DEVELOPER')

        with self.assertRaises(ExceptionResourceAlreadyExists):
            self.define(connection, '--row-type', 'BAPIRET2')

        self.assertEqual(len(connection.execs), 1)
        fake_lock.assert_not_called()

    def test_define_already_exists_no_error(self, fake_lock, fake_unlock):
        connection = Connection([
            response_already_exists(),
            response_ok(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML),
            response_ok(),
        ], user='DEVELOPER')

        retval = self.define(connection, '--row-type', 'BAPIRET2', '--no-error-existing')

        self.assertEqual(retval, 0)
        self.assertEqual(len(connection.execs), 3)
        self.assertEqual(connection.execs[2].body, bytes(TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML, 'utf-8'))

        self.assertConsoleContents(self.console, stdout=f'''Creating table type {TABLE_TYPE_NAME}
Table type {TABLE_TYPE_NAME} already exists
Defining table type {TABLE_TYPE_NAME}
''')


if __name__ == '__main__':
    unittest.main()
