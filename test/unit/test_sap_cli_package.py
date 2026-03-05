#!/usr/bin/env python3

import unittest
from unittest.mock import patch, call, Mock
from types import SimpleNamespace
from argparse import ArgumentParser
from io import StringIO

import sap.errors
from sap.errors import SAPCliError
from sap.rest.errors import HTTPRequestError
from sap.adt.errors import ExceptionResourceAlreadyExists, ExceptionResourceNotFound

import sap.cli.package
import sap.cli.core

from mock import Connection, Response, ConsoleOutputTestCase, PatcherTestCase, patch_get_print_console_with_buffer
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


class TestPackageList(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        ConsoleOutputTestCase.setUp(self)
        self.patch_console(console=self.console)

    def configure_mock_walk(self, fake_walk):
        fake_walk.return_value = iter(
            (([],
              ['$VICTORY_TESTS', '$VICTORY_DOC'],
              [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD', description='Test interface'),
               SimpleNamespace(typ='CLAS/OC', name='ZCL_HELLO_WORLD', description='Test class'),
               SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD', description='Test program')]),
             (['$VICTORY_TESTS'],
              [],
              [SimpleNamespace(typ='CLAS/OC', name='ZCL_TESTS', description='Test class 2')]),
             (['$VICTORY_DOC'],
              [],
              []))
        )

    def configure_mock_walk_long(self, fake_walk):
        fake_walk.return_value = iter(
            (([],
              [SimpleNamespace(typ='DEVC/K', name='$VICTORY_TESTS', uri='/sap/bc/adt/packages/%24victory_tests', description='Victory Tests'),
               SimpleNamespace(typ='DEVC/K', name='$VICTORY_DOC', uri='/sap/bc/adt/packages/%24victory_doc', description='Victory Doc')],
              [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD', description='Test interface'),
               SimpleNamespace(typ='CLAS/OC', name='ZCL_HELLO_WORLD', description='Test class'),
               SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD', description='Test program')]),
             (['$VICTORY_TESTS'],
              [],
              [SimpleNamespace(typ='CLAS/OC', name='ZCL_TESTS', description='Test class 2')]),
             (['$VICTORY_DOC'],
              [],
              []))
        )

    @patch('sap.adt.package.walk')
    def test_without_recursion(self, fake_walk):
        conn = Connection()

        self.configure_mock_walk(fake_walk)
        args = parse_args('list', '$VICTORY')

        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''$VICTORY_TESTS
$VICTORY_DOC
ZIF_HELLO_WORLD
ZCL_HELLO_WORLD
Z_HELLO_WORLD
''')

    @patch('sap.adt.package.walk')
    def test_with_recursion(self, fake_walk):
        conn = Connection()

        self.configure_mock_walk(fake_walk)
        args = parse_args('list', '$VICTORY', '-r')

        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''ZIF_HELLO_WORLD
ZCL_HELLO_WORLD
Z_HELLO_WORLD
$VICTORY_TESTS/ZCL_TESTS
$VICTORY_DOC/
''')

    @patch('sap.adt.package.walk')
    def test_with_long_option(self, fake_walk):
        conn = Connection()

        self.configure_mock_walk_long(fake_walk)
        args = parse_args('list', '$VICTORY', '-l')

        args.execute(conn, args)

        fake_walk.assert_called_once()
        call_args = fake_walk.call_args
        self.assertEqual(call_args[1]['withdescr'], True)

        self.assertConsoleContents(self.console, stdout='''DEVC/K   $VICTORY_TESTS   Victory Tests
DEVC/K   $VICTORY_DOC     Victory Doc
INTF/OI  ZIF_HELLO_WORLD  Test interface
CLAS/OC  ZCL_HELLO_WORLD  Test class
PROG/P   Z_HELLO_WORLD    Test program
''')

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


class TestPackageDelete(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        ConsoleOutputTestCase.setUp(self)
        self.patch_console(console=self.console)

    def test_delete_non_recursive(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('delete', '$TEST')
        args.execute(conn, args)

        self.assertEqual(conn.execs[0].method, 'POST')
        self.assertEqual(conn.execs[0].adt_uri, '/sap/bc/adt/deletion/delete')

        self.assertConsoleContents(self.console, stdout='Deleting package $TEST ...\nDeleted package $TEST\n')

    def test_delete_non_recursive_with_corrnr(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('delete', '$TEST', '--corrnr', '420')
        args.execute(conn, args)

        body = conn.execs[0].body.decode('utf-8')
        self.assertIn('<del:transportNumber>420</del:transportNumber>', body)

    @patch('sap.adt.package.walk')
    @patch('sap.adt.objects.adt_object_delete')
    def test_delete_recursive(self, fake_delete, fake_walk):
        conn = Connection([EMPTY_RESPONSE_OK])

        fake_walk.return_value = iter([
            ([],
             [SimpleNamespace(typ='DEVC/K', name='$SUB1', uri='packages/%24sub1', description='Sub 1'),
              SimpleNamespace(typ='DEVC/K', name='$SUB2', uri='packages/%24sub2', description='Sub 2')],
             [SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD', uri='programs/programs/z_hello_world', description='Test')]),
            (['$SUB1'],
             [],
             [SimpleNamespace(typ='CLAS/OC', name='ZCL_TEST', uri='oo/classes/zcl_test', description='Test class')]),
            (['$SUB2'],
             [],
             []),
        ])

        args = parse_args('delete', '$TEST', '-r')
        args.execute(conn, args)

        # 2 objects + 2 sub-packages + 1 top-level package = 5 calls
        self.assertEqual(fake_delete.call_count, 5)
        fake_delete.assert_any_call(conn, '/sap/bc/adt/programs/programs/z_hello_world', corrnr=None)
        fake_delete.assert_any_call(conn, '/sap/bc/adt/oo/classes/zcl_test', corrnr=None)
        fake_delete.assert_any_call(conn, '/sap/bc/adt/packages/%24sub1', corrnr=None)
        fake_delete.assert_any_call(conn, '/sap/bc/adt/packages/%24sub2', corrnr=None)

        self.assertConsoleContents(self.console, stdout='''Deleting object Z_HELLO_WORLD ...
Deleted object Z_HELLO_WORLD
Deleting object ZCL_TEST ...
Deleted object ZCL_TEST
Deleting package $SUB1 ...
Deleted package $SUB1
Deleting package $SUB2 ...
Deleted package $SUB2
Deleting package $TEST ...
Deleted package $TEST
''')

    @patch('sap.adt.package.walk')
    @patch('sap.adt.objects.adt_object_delete')
    def test_delete_recursive_with_corrnr(self, fake_delete, fake_walk):
        conn = Connection([EMPTY_RESPONSE_OK])

        fake_walk.return_value = iter([
            ([],
             [],
             [SimpleNamespace(typ='PROG/P', name='Z_HELLO', uri='programs/programs/z_hello', description='Test')]),
        ])

        args = parse_args('delete', '$TEST', '-r', '--corrnr', '420')
        args.execute(conn, args)

        # 1 object + 1 top-level package
        self.assertEqual(fake_delete.call_count, 2)
        fake_delete.assert_any_call(conn, '/sap/bc/adt/programs/programs/z_hello', corrnr='420')


class TestPackageActivate(unittest.TestCase):

    def _make_obj(self, name, uri):
        return SimpleNamespace(typ='CLAS', name=name, uri=uri, description='')

    @patch('sap.adt.wb.activate')
    @patch('sap.adt.Package')
    def test_activate_package(self, fake_pkg_cls, fake_wb_activate):
        conn = Mock()
        fake_package = fake_pkg_cls.return_value

        args = parse_args('activate', 'ZPACKAGE')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        fake_pkg_cls.assert_called_once_with(conn, 'ZPACKAGE')
        fake_wb_activate.assert_called_once_with(fake_package)

        self.assertIn('Activating package ZPACKAGE', fake_console.capout)
        self.assertIn('Activated package ZPACKAGE', fake_console.capout)

    @patch('sap.adt.wb.activate')
    @patch('sap.adt.Package')
    def test_activate_multiple_packages(self, fake_pkg_cls, fake_wb_activate):
        conn = Mock()
        fake_pkg_a = Mock()
        fake_pkg_b = Mock()
        fake_pkg_cls.side_effect = [fake_pkg_a, fake_pkg_b]

        args = parse_args('activate', 'ZPKG_A', 'ZPKG_B')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        self.assertEqual(fake_pkg_cls.call_count, 2)
        fake_pkg_cls.assert_any_call(conn, 'ZPKG_A')
        fake_pkg_cls.assert_any_call(conn, 'ZPKG_B')

        self.assertEqual(fake_wb_activate.call_count, 2)
        fake_wb_activate.assert_any_call(fake_pkg_a)
        fake_wb_activate.assert_any_call(fake_pkg_b)

        self.assertIn('Activating package ZPKG_A', fake_console.capout)
        self.assertIn('Activated package ZPKG_A', fake_console.capout)
        self.assertIn('Activating package ZPKG_B', fake_console.capout)
        self.assertIn('Activated package ZPKG_B', fake_console.capout)

    @patch('sap.adt.wb.activate', side_effect=sap.errors.SAPCliError('Activation error'))
    @patch('sap.adt.Package')
    def test_activate_package_error(self, fake_pkg_cls, fake_wb_activate):
        conn = Mock()

        args = parse_args('activate', 'ZPACKAGE')

        with self.assertRaises(sap.errors.SAPCliError), \
             patch_get_print_console_with_buffer():
            args.execute(conn, args)

    @patch('sap.cli.wb.activate')
    @patch('sap.adt.package.walk')
    @patch('sap.adt.Package')
    def test_recursive_single_object(self, fake_pkg_cls, fake_walk, fake_activate):
        conn = Mock()
        obj = self._make_obj('CL_TEST', '/sap/bc/adt/classes/cl_test')
        fake_walk.return_value = iter([([], [], [obj])])

        args = parse_args('activate', '-r', 'ZPACKAGE')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        fake_activate.assert_called_once()
        call_args = fake_activate.call_args
        refs = call_args[0][1]
        self.assertEqual(len(refs.references), 1)
        self.assertEqual(refs.references[0].name, 'CL_TEST')
        self.assertEqual(refs.references[0].uri, '/sap/bc/adt/classes/cl_test')

        self.assertIn('Resolving objects of the package ZPACKAGE', fake_console.capout)
        self.assertIn('Activating 1 object(s)', fake_console.capout)
        self.assertIn('Activation completed successfully', fake_console.capout)

    @patch('sap.cli.wb.activate')
    @patch('sap.adt.package.walk')
    @patch('sap.adt.Package')
    def test_recursive_empty_package(self, fake_pkg_cls, fake_walk, fake_activate):
        conn = Mock()
        fake_walk.return_value = iter([([], [], [])])

        args = parse_args('activate', '-r', 'ZEMPTY')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        fake_activate.assert_not_called()
        self.assertIn('Resolving objects of the package ZEMPTY', fake_console.capout)
        self.assertIn('No objects found', fake_console.capout)

    @patch('sap.cli.wb.activate')
    @patch('sap.adt.package.walk')
    @patch('sap.adt.Package')
    def test_recursive(self, fake_pkg_cls, fake_walk, fake_activate):
        conn = Mock()
        obj1 = self._make_obj('CL_TOP', '/sap/bc/adt/classes/cl_top')
        obj2 = self._make_obj('CL_SUB', '/sap/bc/adt/classes/cl_sub')
        fake_walk.return_value = iter([
            ([], ['ZSUB'], [obj1]),
            (['ZSUB'], [], [obj2]),
        ])

        args = parse_args('activate', '-r', 'ZPACKAGE')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        call_args = fake_activate.call_args
        refs = call_args[0][1]
        self.assertEqual(len(refs.references), 2)
        names = {r.name for r in refs.references}
        self.assertEqual(names, {'CL_TOP', 'CL_SUB'})

    @patch('sap.cli.wb.activate')
    @patch('sap.adt.package.walk')
    @patch('sap.adt.Package')
    def test_recursive_multiple_packages(self, fake_pkg_cls, fake_walk, fake_activate):
        conn = Mock()
        obj_a = self._make_obj('CL_A', '/sap/bc/adt/classes/cl_a')
        obj_b = self._make_obj('CL_B', '/sap/bc/adt/classes/cl_b')

        fake_walk.side_effect = [
            iter([([], [], [obj_a])]),
            iter([([], [], [obj_b])]),
        ]

        args = parse_args('activate', '-r', 'ZPKG_A', 'ZPKG_B')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        fake_activate.assert_called_once()
        refs = fake_activate.call_args[0][1]
        self.assertEqual(len(refs.references), 2)
        names = {r.name for r in refs.references}
        self.assertEqual(names, {'CL_A', 'CL_B'})

        self.assertIn('Resolving objects of the package ZPKG_A', fake_console.capout)
        self.assertIn('Resolving objects of the package ZPKG_B', fake_console.capout)
        self.assertIn('Activating 2 object(s)', fake_console.capout)

    @patch('sap.cli.wb.activate', side_effect=sap.errors.SAPCliError('Activation error'))
    @patch('sap.adt.package.walk')
    @patch('sap.adt.Package')
    def test_recursive_activation_error(self, fake_pkg_cls, fake_walk, fake_activate):
        conn = Mock()
        obj = self._make_obj('CL_BROKEN', '/sap/bc/adt/classes/cl_broken')
        fake_walk.return_value = iter([([], [], [obj])])

        args = parse_args('activate', '-r', 'ZPACKAGE')

        with self.assertRaises(sap.errors.SAPCliError), \
             patch_get_print_console_with_buffer():
            args.execute(conn, args)

    @patch('sap.cli.wb.activate')
    @patch('sap.adt.package.walk')
    @patch('sap.adt.Package')
    def test_recursive_object_name_uppercased(self, fake_pkg_cls, fake_walk, fake_activate):
        conn = Mock()
        obj = self._make_obj('cl_lower', '/sap/bc/adt/classes/cl_lower')
        fake_walk.return_value = iter([([], [], [obj])])

        args = parse_args('activate', '-r', 'ZPACKAGE')

        with patch_get_print_console_with_buffer():
            args.execute(conn, args)

        refs = fake_activate.call_args[0][1]
        self.assertEqual(refs.references[0].name, 'CL_LOWER')


class TestPackageCheck(unittest.TestCase):

    def run_checks(self, args, reporters, walk_results):
        with patch_get_print_console_with_buffer() as fake_console, \
             patch('sap.adt.checks.run') as fake_run, \
             patch('sap.adt.package.walk') as fake_walk, \
             patch('sap.adt.checks.fetch_reporters') as fake_fetch_reporters:

            fake_fetch_reporters.return_value = reporters
            fake_walk.return_value = walk_results

            runs = []
            def sap_adt_checks_run(connection, reporter, object_list):
                if reporter.name == 'Exception':
                    fake_response = Mock(status_code=400, text='Error response')
                    raise HTTPRequestError(Mock(), fake_response)

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

            connection = Connection()

            ret = args.execute(connection, args)

            return (runs, fake_console.capout, fake_console.caperr, ret)

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
