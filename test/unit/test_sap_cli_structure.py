#!/usr/bin/env python3

import unittest

import sap.cli.structure

from mock import (
    Connection,
    Response,
    Request,
    patch,
    patch_get_print_console_with_buffer,
)
from io import StringIO

from infra import generate_parse_args
from fixtures_adt_structure import (
    STRUCTURE_NAME,
    CREATE_STRUCTURE_ADT_XML,
    READ_STRUCTURE_BODY,
    WRITE_STRUCTURE_BODY,
    FAKE_LOCK_HANDLE,
    ACTIVATE_STRUCTURE_BODY,
    STRUCTURE_DEFINITION_ADT_XML
)
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK

parse_args = generate_parse_args(sap.cli.structure.CommandGroup())


class TestStructureCreate(unittest.TestCase):

    def structure_create_cmd(self, *args, **kwargs):
        return parse_args('create', *args, **kwargs)

    def test_create(self):
        connection = Connection()

        the_cmd = self.structure_create_cmd(STRUCTURE_NAME, 'Test structure', 'package')
        the_cmd.execute(connection, the_cmd)

        exptected_request = Request(
            adt_uri='/sap/bc/adt/ddic/structures',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.structures.v2+xml; charset=utf-8'},
            body=bytes(CREATE_STRUCTURE_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], exptected_request)


class TestStructureRead(unittest.TestCase):

    def structure_read_cmd(self, *args, **kwargs):
        return parse_args('read', *args, **kwargs)

    def test_read(self):
        connection = Connection([(Response(
            text=READ_STRUCTURE_BODY,
            status_code=200,
            headers={'Content-Type': 'text/plain; charset=utf-8'}
        ), Request.get(
            adt_uri=f'ddic/structures/{STRUCTURE_NAME.lower()}/source/main',
            accept='text/plain',
        ))], asserter=self)

        the_cmd = self.structure_read_cmd(STRUCTURE_NAME)
        with patch_get_print_console_with_buffer() as fake_console:
            the_cmd.execute(connection, the_cmd)

        expected_stdout = READ_STRUCTURE_BODY + '\n'
        self.assertEqual(fake_console.capout, expected_stdout)


class TestStructureWrite(unittest.TestCase):

    def structure_write_cmd(self, *args, **kwargs):
        return parse_args('write', *args, **kwargs)

    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    @patch('sap.adt.objects.ADTObject.unlock')
    def test_write(self, fake_lock, fake_unlock):
        connection = Connection()

        the_cmd = self.structure_write_cmd(STRUCTURE_NAME, '-')
        with patch('sys.stdin', StringIO(WRITE_STRUCTURE_BODY)):
            the_cmd.execute(connection, the_cmd)

        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        expected_request = Request(
            adt_uri=f'/sap/bc/adt/ddic/structures/{STRUCTURE_NAME.lower()}/source/main',
            method='PUT',
            headers={'Content-Type': 'text/plain; charset=utf-8'},
            body=bytes(WRITE_STRUCTURE_BODY, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )

        self.assertEqual(connection.execs[0], expected_request)


class TestStructureActivate(unittest.TestCase):

    def structure_activate_cmd(self, *args, **kwargs):
        return parse_args('activate', *args, **kwargs)

    def test_activate(self):
        connection = Connection([
            RESPONSE_ACTIVATION_OK,
            Response(text=STRUCTURE_DEFINITION_ADT_XML, status_code=200, headers={})
        ])

        the_cmd = self.structure_activate_cmd(STRUCTURE_NAME)
        the_cmd.execute(connection, the_cmd)

        expected_request = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=ACTIVATE_STRUCTURE_BODY,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        self.assertEqual(connection.execs[0], expected_request)
