#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import patch, mock_open
from io import StringIO

import sap.cli.interface

from mock import ConnectionViaHTTP as Connection
from fixtures_adt import EMPTY_RESPONSE_OK, LOCK_RESPONSE_OK


FIXTURE_ELEMENTARY_IFACE_XML='''<?xml version="1.0" encoding="UTF-8"?>
<intf:abapInterface xmlns:intf="http://www.sap.com/adt/oo/interfaces" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="INTF/OI" adtcore:description="Interface Description" adtcore:language="EN" adtcore:name="ZIF_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER">
<adtcore:packageRef adtcore:name="$THE_PACKAGE"/>
</intf:abapInterface>'''


parser = ArgumentParser()
sap.cli.interface.CommandGroup().install_parser(parser)


def parse_args(*argv):
    return parser.parse_args(argv)


class TestInterfaceCreate(unittest.TestCase):

    def test_interface_create_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        args = parse_args('create', 'ZIF_HELLO_WORLD', 'Interface Description', '$THE_PACKAGE')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/oo/interfaces')])

        create_request = connection.execs[0]
        self.assertEqual(create_request.body, bytes(FIXTURE_ELEMENTARY_IFACE_XML, 'utf-8'))

        self.assertIsNone(create_request.params)

        self.assertEqual(sorted(create_request.headers.keys()), ['Content-Type'])
        self.assertEqual(create_request.headers['Content-Type'], 'application/vnd.sap.adt.oo.interfaces.v2+xml; charset=utf-8')


class TestInterfaceActivate(unittest.TestCase):

    def test_interface_activate_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        args = parse_args('activate', 'ZIF_ACTIVATOR')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/activation')])

        create_request = connection.execs[0]
        self.assertIn('adtcore:uri="/sap/bc/adt/oo/interfaces/zif_activator"', create_request.body)
        self.assertIn('adtcore:name="ZIF_ACTIVATOR"', create_request.body)


class TestInterfaceWrite(unittest.TestCase):

    def test_interface_read_from_stdin(self):
        args = parse_args('write', 'ZIF_WRITER', '-')

        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        with patch('sys.stdin', StringIO('iface stdin definition')):
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], b'iface stdin definition')

    def test_interface_read_from_file(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args('write', 'ZIF_WRITER', 'zif_iface.abap')

        with patch('sap.cli.object.open', mock_open(read_data='iface file definition')) as m:
            args.execute(conn, args)

        m.assert_called_once_with('zif_iface.abap', 'r', encoding='utf8')

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], b'iface file definition')


if __name__ == '__main__':
    unittest.main()
