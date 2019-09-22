#!/usr/bin/env python3

import unittest
from unittest.mock import patch, call, Mock
from types import SimpleNamespace
from argparse import ArgumentParser
from io import StringIO

from sap.errors import SAPCliError
from sap.adt.errors import ExceptionResourceAlreadyExists
import sap.cli.package

from mock import Connection, Response
from fixtures_adt import EMPTY_RESPONSE_OK, ERROR_XML_PACKAGE_ALREADY_EXISTS

RESPONSE_PACKAGE_EXISTS = Response(status_code=405,
                                   headers={'content-type': 'application/xml'},
                                   text=ERROR_XML_PACKAGE_ALREADY_EXISTS)

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

    def test_create_package_error_exists_ignored(self):
        connection = Connection([RESPONSE_PACKAGE_EXISTS])

        mock_logger = Mock()

        args = parse_args('create', '$TEST', 'description', '--no-error-existing')

        with patch('sap.cli.package.mod_log', Mock(return_value=mock_logger)) as mock_mod_log:
            sap.cli.package.create(connection, args)

        mock_mod_log.assert_called_once()
        mock_logger.info.assert_called_once_with('Resource Package $SAPCLI_TEST_ROOT does already exist.')

    def test_create_package_error_exists_reported(self):
        connection = Connection([RESPONSE_PACKAGE_EXISTS])

        args = parse_args('create', '$TEST', 'description')
        with self.assertRaises(ExceptionResourceAlreadyExists):
            sap.cli.package.create(connection, args)


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


class TestPackageCheck(unittest.TestCase):

    @patch('sap.cli.core.get_console')
    @patch('sap.adt.checks.run')
    @patch('sap.adt.package.walk')
    @patch('sap.adt.checks.fetch_reporters')
    def test_check_with_objects(self, fake_fetch_reporters, fake_walk, fake_run, fake_get_console):

        reporter_all = sap.adt.checks.Reporter('all')
        reporter_all.supported_types = '*'

        reporter_clas = sap.adt.checks.Reporter('clas')
        reporter_clas.supported_types = 'CLAS'

        reporter_tabl = sap.adt.checks.Reporter('tabl')
        reporter_tabl.supported_types = 'TABL/*'

        fake_fetch_reporters.return_value = [reporter_all, reporter_clas, reporter_tabl]

        fake_walk.return_value = [('foo',
                                   None,
                                   [SimpleNamespace(typ='PROG', name='ZPROGRAM', uri='programs/programs/zprogram'),
                                    SimpleNamespace(typ='CLAS', name='ZCL', uri='oo/classes/zcl')]),
                                  ('foo_sub',
                                   None,
                                   [SimpleNamespace(typ='TABL/DB', name='ZTABLE', uri='ddic/tables/ztable')])]

        runs = []
        def sap_adt_checks_run(connection, reporter, object_list):
            runs.append([reporter.name] + [obj.uri for obj in object_list])

            check_report = sap.adt.checks.CheckReport()
            check_report.reporter = reporter.name

            check_message = sap.adt.checks.CheckMessage()
            check_message.uri = f'fake/uri/{reporter.name}'

            if reporter.name == 'all':
                check_message.typ = 'W'
            else:
                check_message.typ = 'E'

            check_message.short_text = f'Test {reporter.name}'
            check_message.category = reporter.name[0]

            check_report.messages.append(check_message)

            return [check_report]

        fake_run.side_effect = sap_adt_checks_run

        std_output = StringIO()
        err_output = StringIO()

        fake_get_console.return_value = sap.cli.core.PrintConsole(std_output, err_output)

        connection = Connection()

        args = parse_args('check', 'foo')
        args.execute(connection, args)

        self.assertEqual(runs, [['all', 'programs/programs/zprogram', 'oo/classes/zcl', 'ddic/tables/ztable'],
                                ['clas', 'oo/classes/zcl'],
                                ['tabl', 'ddic/tables/ztable']])

        self.assertEqual(std_output.getvalue(), '''W :: a :: Test all
E :: c :: Test clas
E :: t :: Test tabl
Messages: 3
Warnings: 1
Errors:   2
''')
        self.assertEqual(err_output.getvalue(), '')


if __name__ == '__main__':
    unittest.main()
