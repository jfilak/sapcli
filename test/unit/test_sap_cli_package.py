#!/usr/bin/env python3

import unittest
from unittest.mock import patch, call
from types import SimpleNamespace
from argparse import ArgumentParser

from sap.errors import SAPCliError
import sap.cli.package

from mock import Connection, Response
from fixtures_adt import EMPTY_RESPONSE_OK


def parse_args(*argv):
    parser = ArgumentParser()
    sap.cli.package.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestPackageCreate(unittest.TestCase):

    def test_create_package_with_super(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--super-package', '$MASTER')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:superPackage adtcore:name="$MASTER"/>', connection.execs[0].body)

    def test_create_package_without_super(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:superPackage/>', connection.execs[0].body)

    def test_create_package_with_app_component(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--app-component', 'LOD')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:applicationComponent pak:name="LOD"/>', connection.execs[0].body)

    def test_create_package_with_sw_component(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--software-component', 'SAP')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:softwareComponent pak:name="SAP"/>', connection.execs[0].body)

    def test_create_package_with_transport_layer(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--transport-layer', 'SAP')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:transportLayer pak:name="SAP"/>', connection.execs[0].body)

    def test_create_package_with_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--corrnr', '420')
        sap.cli.package.create(connection, args)

        self.assertEqual(connection.execs[0].params['corrNr'], '420')


class TestPackageList(unittest.TestCase):

    def configure_mock_walk(self, conn, fake_walk):
        fake_walk.return_value = iter(
            (([],
              ['$VICTORY_TESTS', '$VICTORY_DOC'],
              [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD'),
               SimpleNamespace(typ='CLAS/OC', name='ZCL_HELLO_WORLD'),
               SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD')]),
             (['$VICTORY_TESTS'],
              [],
              [SimpleNamespace(typ='CLAS/OC', name='ZCL_TESTS')]),
             (['$VICTORY_DOC'],
              [],
              []))
        )

    @patch('sap.adt.package.walk')
    def test_without_recursion(self, fake_walk):
        conn = Connection()

        self.configure_mock_walk(conn, fake_walk)
        args = parse_args('list', '$VICTORY')

        with patch('sap.cli.package.print') as fake_print:
            args.execute(conn, args)

        self.assertEqual(fake_print.mock_calls, [call('$VICTORY_TESTS'),
                                                 call('$VICTORY_DOC'),
                                                 call('ZIF_HELLO_WORLD'),
                                                 call('ZCL_HELLO_WORLD'),
                                                 call('Z_HELLO_WORLD')])
    @patch('sap.adt.package.walk')
    def test_with_recursion(self, fake_walk):
        conn = Connection()

        self.configure_mock_walk(conn, fake_walk)
        args = parse_args('list', '$VICTORY', '-r')

        with patch('sap.cli.package.print') as fake_print:
            args.execute(conn, args)

        self.assertEqual(fake_print.mock_calls, [call('ZIF_HELLO_WORLD'),
                                                 call('ZCL_HELLO_WORLD'),
                                                 call('Z_HELLO_WORLD'),
                                                 call('$VICTORY_TESTS/ZCL_TESTS'),
                                                 call('$VICTORY_DOC/')])


if __name__ == '__main__':
    unittest.main()
