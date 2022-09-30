#!/usr/bin/env python3

import unittest

import sap.cli.table

from mock import (
    Connection,
    Response,
    Request,
    patch,
)
from io import StringIO

from infra import generate_parse_args
from fixtures_adt_table import (
    TABLE_NAME,
    CREATE_TABLE_ADT_XML,
    READ_TABLE_BODY,
    WRITE_TABLE_BODY,
    FAKE_LOCK_HANDLE,
    ACTIVATE_TABLE_BODY,
    TABLE_DEFINITION_ADT_XML
)
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK

parse_args = generate_parse_args(sap.cli.table.CommandGroup())


class TestTableCreate(unittest.TestCase):

    def table_create_cmd(self, *args, **kwargs):
        return parse_args('create', *args, **kwargs)

    def test_create(self):
        connection = Connection()

        the_cmd = self.table_create_cmd(TABLE_NAME, 'Test table', 'package')
        the_cmd.execute(connection, the_cmd)

        exptected_request = Request(
            adt_uri='/sap/bc/adt/ddic/tables',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.tables.v2+xml; charset=utf-8'},
            body=bytes(CREATE_TABLE_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request)


class TestTableRead(unittest.TestCase):

    def table_read_cmd(self, *args, **kwargs):
        return parse_args('read', *args, **kwargs)

    def test_read(self):
        connection = Connection([(Response(
            text=READ_TABLE_BODY,
            status_code=200,
            headers={'Content-Type': 'text/plain; charset=utf-8'}
        ), Request.get(
            adt_uri=f'ddic/tables/{TABLE_NAME.lower()}/source/main',
            accept='text/plain',
        ))], asserter=self)

        the_cmd = self.table_read_cmd(TABLE_NAME)
        with patch('sys.stdout', StringIO()) as mock_print:
            the_cmd.execute(connection, the_cmd)

        expected_stdout = READ_TABLE_BODY + '\n'
        self.assertEqual(mock_print.getvalue(), expected_stdout)


class TestTableWrite(unittest.TestCase):

    def table_write_cmd(self, *args, **kwargs):
        return parse_args('write', *args, **kwargs)

    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    @patch('sap.adt.objects.ADTObject.unlock')
    def test_write(self, fake_lock, fake_unlock):
        connection = Connection()

        the_cmd = self.table_write_cmd(TABLE_NAME, '-')
        with patch('sys.stdin', StringIO(WRITE_TABLE_BODY)):
            the_cmd.execute(connection, the_cmd)

        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        expected_request = Request(
            adt_uri=f'/sap/bc/adt/ddic/tables/{TABLE_NAME.lower()}/source/main',
            method='PUT',
            headers={'Content-Type': 'text/plain; charset=utf-8'},
            body=bytes(WRITE_TABLE_BODY, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )

        self.assertEqual(connection.execs[0], expected_request)


class TestTableActivate(unittest.TestCase):

    def table_activate_cmd(self, *args, **kwargs):
        return parse_args('activate', *args, **kwargs)

    def test_activate(self):
        connection = Connection([
            RESPONSE_ACTIVATION_OK,
            Response(text=TABLE_DEFINITION_ADT_XML , status_code=200, headers={})
        ])

        the_cmd = self.table_activate_cmd(TABLE_NAME)
        the_cmd.execute(connection, the_cmd)

        expected_request = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=ACTIVATE_TABLE_BODY,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        self.assertEqual(connection.execs[0], expected_request)
