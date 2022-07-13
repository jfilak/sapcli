#!/usr/bin/env python3

import unittest
from unittest.mock import patch, call, Mock
from types import SimpleNamespace
from argparse import ArgumentParser
from io import StringIO

from sap.errors import SAPCliError
from sap.rest.errors import HTTPRequestError
from sap.adt.errors import ExceptionResourceAlreadyExists, ExceptionResourceNotFound

import sap.cli.package
import sap.cli.core

from mock import ConnectionViaHTTP as Connection, Response, ConsoleOutputTestCase, PatcherTestCase
from fixtures_adt import EMPTY_RESPONSE_OK, ERROR_XML_PACKAGE_ALREADY_EXISTS
from fixtures_adt_package import GET_PACKAGE_ADT_XML, GET_PACKAGE_ADT_XML_NOT_FOUND


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

        self.assertIn('<pak:superPackage adtcore:name="$MASTER"/>', connection.execs[0].body.decode('utf-8'))

    def test_create_package_without_super(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:superPackage/>', connection.execs[0].body.decode('utf-8'))

    def test_create_package_with_app_component(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--app-component', 'LOD')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:applicationComponent pak:name="LOD"/>', connection.execs[0].body.decode('utf-8'))

    def test_create_package_with_sw_component(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--software-component', 'SAP')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:softwareComponent pak:name="SAP"/>', connection.execs[0].body.decode('utf-8'))

    def test_create_package_with_transport_layer(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', '$TEST', 'description', '--transport-layer', 'SAP')
        sap.cli.package.create(connection, args)

        self.assertIn('<pak:transportLayer pak:name="SAP"/>', connection.execs[0].body.decode('utf-8'))

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

class TestPackageStat(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        ConsoleOutputTestCase.setUp(self)
        self.patch_console(console=self.console)

    def test_stat_existing(self):

        conn = Connection([Response(status_code=200, headers={}, text=GET_PACKAGE_ADT_XML)])

        args = parse_args('stat', '$IAMTHEKING')

        exit_code = args.execute(conn, args)
        self.assertEqual(exit_code, sap.cli.core.EXIT_CODE_OK)

        self.assertEqual(len(conn.execs), 1)

        self.assertConsoleContents(self.console, stdout='''Name                   :$IAMTHEKING
Active                 :active
Application Component  :-
Software Component     :LOCAL
Transport Layer        :
Package Type           :development
''')

    def test_stat_not_found(self):

        conn = Connection([Response(status_code=404, headers={'content-type': 'application/xml'}, text=GET_PACKAGE_ADT_XML_NOT_FOUND)])

        args = parse_args('stat', '$IAMTHEKING')

        exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, sap.cli.core.EXIT_CODE_NOT_FOUND)
        self.assertConsoleContents(self.console, stderr='Package $IAMTHEKING not found\n')


class TestPackageCheck(unittest.TestCase):

    def run_checks(self, args, reporters, walk_results):
        with patch('sap.cli.core.get_console') as fake_get_console, \
             patch('sap.adt.checks.run') as fake_run, \
             patch('sap.adt.package.walk') as fake_walk, \
             patch('sap.adt.checks.fetch_reporters') as fake_fetch_reporters:

            fake_fetch_reporters.return_value = reporters
            fake_walk.return_value = walk_results

            runs = []
            def sap_adt_checks_run(connection, reporter, object_list):
                if reporter.name == 'Exception':
                    raise HTTPRequestError(Mock(), Mock())

                runs.append([reporter.name] + [obj.uri for obj in object_list])

                check_report = sap.adt.checks.CheckReport()
                check_report.reporter = reporter.name
                obj = next(iter(object_list))
                check_report.triggering_uri = obj.uri

                check_message = sap.adt.checks.CheckMessage()
                check_message.uri = f'fake/uri/{reporter.name}'

                if reporter.name == 'all':
                    check_message.typ = 'W'
                else:
                    check_message.typ = 'E'

                check_message.short_text = f'Test {reporter.name}'
                check_message.category = reporter.name[0]

                sap.get_logger().debug('FAKE message: %s %s', check_report.triggering_uri, check_message.short_text)
                check_report.messages.append(check_message)

                return [check_report]

            fake_run.side_effect = sap_adt_checks_run

            std_output = StringIO()
            err_output = StringIO()

            fake_get_console.return_value = sap.cli.core.PrintConsole(std_output, err_output)

            connection = Connection()

            ret = args.execute(connection, args)

            return (runs, std_output.getvalue(), err_output.getvalue(), ret)

    def run_check_with_objects(self, args, exp_std, exp_err):

        reporter_all = sap.adt.checks.Reporter('all')
        reporter_all.supported_types = '*'

        reporter_clas = sap.adt.checks.Reporter('clas')
        reporter_clas.supported_types = 'CLAS'

        reporter_tabl = sap.adt.checks.Reporter('tabl')
        reporter_tabl.supported_types = 'TABL/*'


        runs, std, err, _ = self.run_checks(
            args,
            [reporter_all, reporter_clas, reporter_tabl],
            [('foo',
              None,
              [SimpleNamespace(typ='PROG', name='ZPROGRAM', uri='programs/programs/zprogram'),
               SimpleNamespace(typ='CLAS', name='ZCL', uri='oo/classes/zcl')]),
             ('foo_sub',
              None,
              [SimpleNamespace(typ='TABL/DB', name='ZTABLE', uri='ddic/tables/ztable')])
            ],
        )

        self.assertEqual(runs, [['all', 'programs/programs/zprogram'],
                                ['all', 'oo/classes/zcl'],
                                ['clas', 'oo/classes/zcl'],
                                ['all', 'ddic/tables/ztable'],
                                ['tabl', 'ddic/tables/ztable']])

        self.assertEqual(std, exp_std)
        self.assertEqual(err, exp_err)

    def test_check_with_objects_no_grouping(self):
        args = parse_args('check', 'foo')
        self.run_check_with_objects(args,
                                    '''W :: a :: Test all :: PROG ZPROGRAM
W :: a :: Test all :: CLAS ZCL
E :: c :: Test clas :: CLAS ZCL
W :: a :: Test all :: TABL/DB ZTABLE
E :: t :: Test tabl :: TABL/DB ZTABLE
Checks:   5
Messages: 5
Warnings: 3
Errors:   2
''',
                                    '')

    def test_check_with_objects_by_object(self):
        args = parse_args('check', 'foo', '--group-by', 'object')
        self.run_check_with_objects(args,
                                    '''PROG ZPROGRAM
* W :: a :: Test all
CLAS ZCL
* W :: a :: Test all
* E :: c :: Test clas
TABL/DB ZTABLE
* W :: a :: Test all
* E :: t :: Test tabl
Checks:   5
Messages: 5
Warnings: 3
Errors:   2
''',
                                    '')

    def test_check_with_objects_by_message(self):
        args = parse_args('check', 'foo', '--group-by', 'message')
        self.run_check_with_objects(args,
                                    '''W :: a :: Test all
* PROG ZPROGRAM
* CLAS ZCL
* TABL/DB ZTABLE
E :: c :: Test clas
* CLAS ZCL
E :: t :: Test tabl
* TABL/DB ZTABLE
Checks:   5
Messages: 5
Warnings: 3
Errors:   2
''',
                                    '')

    def test_check_with_objects_no_matching_reporter(self):

        reporter_clas = sap.adt.checks.Reporter('clas')
        reporter_clas.supported_types = 'CLAS'

        args = parse_args('check', 'foo')

        runs, std, err, ret = self.run_checks(
            args,
            [reporter_clas],
            [('foo',
              None,
              [SimpleNamespace(typ='PROG', name='ZPROGRAM', uri='programs/programs/zprogram')])
            ],
        )

        self.assertEqual(runs, [])

        self.assertEqual(std, '''Checks:   0
Messages: 0
Warnings: 0
Errors:   0
''')

        self.assertEqual(err, '')
        self.assertEqual(ret, 0)

    def test_check_without_reporters(self):
        args = parse_args('check', 'foo')

        runs, std, err, ret = self.run_checks(
            args,
            [],
            [('foo',
              None,
              [SimpleNamespace(typ='PROG', name='ZPROGRAM', uri='programs/programs/zprogram')]
             )
            ],
        )
        self.assertEqual(std, '')
        self.assertEqual(err, 'No ADT Checks Reporters provided by the system\n')
        self.assertEqual(ret, 1)

    def test_check_without_objects(self):
        reporter_clas = sap.adt.checks.Reporter('clas')
        reporter_clas.supported_types = 'CLAS'

        args = parse_args('check', 'foo')

        runs, std, err, ret = self.run_checks(
            args,
            [reporter_clas],
            [],
        )

        self.assertEqual(std, '')
        self.assertEqual(err, 'No objects found\n')
        self.assertEqual(ret, 1)

    def test_check_with_http_error(self):

        reporter_clas = sap.adt.checks.Reporter('Exception')
        reporter_clas.supported_types = 'CLAS'

        args = parse_args('check', 'foo')

        runs, std, err, ret = self.run_checks(
            args,
            [reporter_clas],
            [('foo',
              None,
              [SimpleNamespace(typ='CLAS', name='ZCL', uri='oo/classes/zcl')]),
            ],
        )

        self.assertEqual(runs, [])

        self.assertEqual(std, '''Checks:   0
Messages: 0
Warnings: 0
Errors:   0
''')

        self.assertEqual(err, '')
        self.assertEqual(ret, 0)


if __name__ == '__main__':
    unittest.main()
