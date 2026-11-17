#!/usr/bin/env python3

import os
import re
import sys
from argparse import ArgumentParser
import unittest
from unittest.mock import Mock, PropertyMock, patch, mock_open, call, MagicMock
from types import SimpleNamespace
from io import StringIO

import sap.cli.checkout
import sap.cli.localrepo
import sap.platform.abap
from sap.adt.textelements import TextSymbol
import sap.platform.abap.abapgit
import sap.adt

from mock import Connection, Response, patch, PatcherTestCase, ConsoleOutputTestCase, StringIOFile
from test.unit.fixtures_sap_platform_abap_abapgit_tabl import TABL_NAME, DBTAB_NAME
from test.unit.fixtures_sap_platform_abap_abapgit_ddls import DDLS_NAME
from test.unit.fixtures_sap_platform_abap_abapgit_dcls import DCLS_NAME
from test.unit.fixtures_sap_platform_abap_abapgit_ddlx import DDLX_NAME
from test.unit.fixtures_adt_domain import DOMAIN_NEW_NAME
from test.unit.fixtures_adt_dataelement import DATA_ELEMENT_NEW_NAME
from test.unit.fixtures_sap_adt_behaviordefinition import BDEF_NAME
from test.unit.fixtures_sap_adt_tabletype import TABLE_TYPE_NAME


def parse_args(argv):
    parser = ArgumentParser()
    sap.cli.checkout.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


def assert_wrote_file(unit_test, fake_open, file_name, contents, fileno=1):
    context_calls = 4
    if fake_open.mock_calls[4] == call().close():
       context_calls = 5

    start = (fileno - 1) * context_calls
    unit_test.assertEqual(fake_open.mock_calls[start + 0], call(file_name, 'w', encoding='utf8'))
    unit_test.assertEqual(fake_open.mock_calls[start + 1], call().__enter__())
    unit_test.assertEqual(fake_open.mock_calls[start + 2], call().write(contents))
    unit_test.assertEqual(fake_open.mock_calls[start + 3], call().__exit__(None, None, None))

    return context_calls


class TestCheckoutCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.checkout.CommandGroup()


class TestConsoleObserver(ConsoleOutputTestCase):

    def test_prints_to_the_current_console(self):
        with patch('sap.cli.core.get_console', return_value=self.console):
            observer = sap.cli.checkout._console_observer()

        observer.checking_out('ZCL_FOO')
        observer.warning('Skipping')

        self.assertIsInstance(observer, sap.cli.localrepo.ConsoleObserver)
        self.assertConsoleContents(self.console, stdout='ZCL_FOO\n', stderr='Skipping\n')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckout(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.clas.ClassHandler.checkout')
    def test_checkout_uppercase_name_clas(self, fake_clas):
        conn = Connection()

        args = parse_args(['class', 'zcl_lowercase'])
        args.execute(conn, args)

        args = parse_args(['class', 'ZCL_UPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_clas.mock_calls, [call(conn, 'CLAS/OC', 'ZCL_LOWERCASE', None, 'observer'),
                                                call(conn, 'CLAS/OC', 'ZCL_UPPERCASE', None, 'observer')])

    @patch('sap.platform.abap.abapgit.intf.InterfaceHandler.checkout')
    def test_checkout_uppercase_name_intf(self, fake_intf):
        conn = Connection()

        args = parse_args(['interface', 'zif_lowercase'])
        args.execute(conn, args)

        args = parse_args(['interface', 'ZIF_UPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_intf.mock_calls, [call(conn, 'INTF/OI', 'ZIF_LOWERCASE', None, 'observer'),
                                                call(conn, 'INTF/OI', 'ZIF_UPPERCASE', None, 'observer')])

    @patch('sap.platform.abap.abapgit.prog.ProgramHandler.checkout')
    def test_checkout_uppercase_name_prog(self, fake_prog):
        conn = Connection()

        args = parse_args(['program', 'zlowercase'])
        args.execute(conn, args)

        args = parse_args(['program', 'ZUPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_prog.mock_calls, [call(conn, 'PROG/P', 'ZLOWERCASE', None, 'observer'), call(conn, 'PROG/P', 'ZUPPERCASE', None, 'observer')])

@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutFunctionGroupCommand(unittest.TestCase):

    @patch('sap.cli.checkout.checkout_function_group')
    def test_default_source_format(self, fake_checkout):
        conn = Connection()

        args = parse_args(['function_group', 'zfugr_lowercase'])
        exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, 0)
        fake_checkout.assert_called_once_with(conn, 'ZFUGR_LOWERCASE', 'observer',
                                              source_format=sap.cli.checkout.SourceCodeFormat.ABAPGIT)

    @patch('sap.cli.checkout.checkout_function_group')
    def test_abap_source_format(self, fake_checkout):
        conn = Connection()

        args = parse_args(['function_group', 'ZFUGR', '--format', 'ABAP'])
        exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, 0)
        fake_checkout.assert_called_once_with(conn, 'ZFUGR', 'observer', source_format=sap.cli.checkout.SourceCodeFormat.ABAP)

    @patch('sap.cli.core.printerr')
    @patch('sap.cli.checkout.checkout_function_group')
    def test_failure(self, fake_checkout, fake_printerr):
        fake_checkout.side_effect = sap.cli.core.SAPCliError('Unsupported function group object: FOO BAR')

        conn = Connection()
        args = parse_args(['function_group', 'ZFUGR'])
        exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, 1)
        fake_printerr.assert_called_once_with('Checkout failed: Unsupported function group object: FOO BAR')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutTableTypeCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.ttyp.TableTypeHandler.checkout')
    def test_checkout_ttyp_command(self, fake_checkout):
        args = parse_args(['tabletype', TABLE_TYPE_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'TTYP/DA', TABLE_TYPE_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.ttyp.TableTypeHandler.checkout')
    def test_checkout_objects_ttyp(self, fake_checkout):
        objects = [SimpleNamespace(typ='TTYP/DA', name=TABLE_TYPE_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'TTYP/DA', TABLE_TYPE_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutDataDefinitionCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.ddls.DataDefinitionHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['ddl', DDLS_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'DDLS/DF', DDLS_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.ddls.DataDefinitionHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='DDLS/DF', name=DDLS_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'DDLS/DF', DDLS_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutAccessControlCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.dcls.AccessControlHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['dcl', DCLS_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'DCLS/DL', DCLS_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.dcls.AccessControlHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='DCLS/DL', name=DCLS_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'DCLS/DL', DCLS_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutMetadataExtensionCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.ddlx.MetadataExtensionHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['ddlx', DDLX_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'DDLX/EX', DDLX_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.ddlx.MetadataExtensionHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='DDLX/EX', name=DDLX_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'DDLX/EX', DDLX_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutBehaviorDefinitionCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.bdef.BehaviorDefinitionHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['bdef', BDEF_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'BDEF/BDO', BDEF_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.bdef.BehaviorDefinitionHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='BDEF/BDO', name=BDEF_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'BDEF/BDO', BDEF_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutDomainCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.doma.DomainHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['domain', DOMAIN_NEW_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'DOMA/DD', DOMAIN_NEW_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.doma.DomainHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='DOMA/DD', name=DOMAIN_NEW_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'DOMA/DD', DOMAIN_NEW_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutDataElementCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.dtel.DataElementHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['dataelement', DATA_ELEMENT_NEW_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'DTEL/DE', DATA_ELEMENT_NEW_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.dtel.DataElementHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='DTEL/DE', name=DATA_ELEMENT_NEW_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'DTEL/DE', DATA_ELEMENT_NEW_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutStructureCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.tabl.TableHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['structure', TABL_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'TABL/DS', TABL_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.tabl.TableHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='TABL/DS', name=TABL_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'TABL/DS', TABL_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutTableCommand(unittest.TestCase):

    @patch('sap.platform.abap.abapgit.tabl.TableHandler.checkout')
    def test_command(self, fake_checkout):
        args = parse_args(['table', DBTAB_NAME.lower()])
        args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', 'TABL/DT', DBTAB_NAME, None, 'observer')

    @patch('sap.platform.abap.abapgit.tabl.TableHandler.checkout')
    def test_checkout_objects(self, fake_checkout):
        objects = [SimpleNamespace(typ='TABL/DT', name=DBTAB_NAME)]

        with patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_checkout.assert_called_once_with('connection', 'TABL/DT', DBTAB_NAME, 'src', 'observer')


@patch('sap.cli.checkout._console_observer', new=lambda: 'observer')
class TestCheckoutPackage(unittest.TestCase):

    @patch('sap.adt.Package.fetch')
    @patch('sap.platform.abap.abapgit.layout.dump_attributes_to_file')
    @patch('sap.platform.abap.abapgit.fugr.FunctionGroupHandler.checkout')
    @patch('sap.platform.abap.abapgit.clas.ClassHandler.checkout')
    @patch('sap.platform.abap.abapgit.intf.InterfaceHandler.checkout')
    @patch('sap.platform.abap.abapgit.prog.ProgramHandler.checkout')
    @patch('sap.adt.package.walk')
    def test_checkout_package_recursive_by_default(self, fake_walk, fake_prog, fake_intf, fake_clas, fake_fugr, fake_dump, fake_fetch):
        conn = Connection([])

        package_name = '$VICTORY'
        sub_package_name = '$VICTORY_TESTS'
        fake_walk.return_value = iter(
            (([],
              [sub_package_name],
              [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD'),
               SimpleNamespace(typ='CLAS/OC', name='ZCL_HELLO_WORLD'),
               SimpleNamespace(typ='PROG/P', name='Z_HELLO_WORLD'),
               SimpleNamespace(typ='7777/3', name='Magic Unicorn'),
               SimpleNamespace(typ='FUGR/F', name='ZFUGR_HELLO')]),
             ([sub_package_name],
              [],
              [SimpleNamespace(typ='CLAS/OC', name='ZCL_TESTS')]))
        )

        package_factory = sap.adt.Package
        def new_package(connection, name):
            package = package_factory(connection, name)
            package.description = f'Description {name}'
            return package

        args = parse_args(['package', package_name])
        with patch('sap.platform.abap.abapgit.layout.open', mock_open()) as fake_open, \
             patch('sap.cli.checkout.print') as fake_print, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs, \
             patch('sap.adt.Package') as fake_package:

            fake_package.side_effect = new_package

            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_destdir = os.path.abspath(os.path.join(package_name, 'src'))
        exp_sub_destdir = os.path.abspath(os.path.join(package_name, 'src', sub_package_name.lower()))
        fake_prog.assert_called_once_with(conn, 'PROG/P', 'Z_HELLO_WORLD', exp_destdir, 'observer')
        fake_intf.assert_called_once_with(conn, 'INTF/OI', 'ZIF_HELLO_WORLD', exp_destdir, 'observer')
        fake_fugr.assert_called_once_with(conn, 'FUGR/F', 'ZFUGR_HELLO', exp_destdir, 'observer')
        self.assertEqual(fake_clas.mock_calls, [call(conn, 'CLAS/OC', 'ZCL_HELLO_WORLD', exp_destdir, 'observer'),
                                                call(conn, 'CLAS/OC', 'ZCL_TESTS', exp_sub_destdir, 'observer')])

        self.assertEqual(fake_print.mock_calls, [call('Unsupported object: 7777/3 Magic Unicorn', file=sys.stderr)])

        self.assertEqual(fake_fetch.mock_calls, [call(), call()])
        self.assertEqual(fake_dump.mock_calls, [call('observer', 'package',
                                                     (sap.platform.abap.ddic.DEVC(CTEXT='Description $VICTORY'),),
                                                     '.devc',
                                                     'LCL_OBJECT_DEVC',
                                                     destdir=exp_destdir),
                                                call('observer', 'package',
                                                     (sap.platform.abap.ddic.DEVC(CTEXT='Description $VICTORY_TESTS'),),
                                                     '.devc',
                                                     'LCL_OBJECT_DEVC',
                                                     destdir=exp_sub_destdir)
                                                ])

    @patch('sap.platform.abap.abapgit.layout.AbapGitLayout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_non_recursive(self, fake_walk, fake_checkout, fake_package):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], ['$TESTS'], exp_objects),
                                       (['$TESTS'], [], [])))

        package_name = '$ROOT'
        starting_folder = 'src'
        args = parse_args(['package', package_name, '--no-recursive'])
        with patch('sap.platform.abap.abapgit.layout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_destdir = os.path.abspath(os.path.join(package_name, starting_folder))
        fake_checkout.assert_called_once_with(conn, exp_objects, 'observer', destdir=exp_destdir)

    def test_checkout_package_recursive_option_default(self):
        args = parse_args(['package', '$ROOT'])

        self.assertTrue(args.recursive)

    def test_checkout_package_recursive_option(self):
        args = parse_args(['package', '$ROOT', '--recursive'])

        self.assertTrue(args.recursive)

    def test_checkout_package_no_recursive_option(self):
        args = parse_args(['package', '$ROOT', '--no-recursive'])

        self.assertFalse(args.recursive)

    @patch('sap.platform.abap.abapgit.layout.AbapGitLayout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_starting_folder(self, fake_walk, fake_checkout, fake_package):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], [], exp_objects), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        args = parse_args(['package', package_name, '--starting-folder', starting_folder])
        with patch('sap.platform.abap.abapgit.layout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be executed')
            args.execute(conn, args)

        exp_repodir = os.path.abspath(package_name)
        fake_isdir.assert_called_once_with(exp_repodir)

        exp_sourcedir = os.path.abspath(os.path.join(exp_repodir, starting_folder))
        fake_checkout.assert_called_once_with(conn, exp_objects, 'observer', destdir=exp_sourcedir)

    @patch('sap.platform.abap.to_xml')
    @patch('sap.platform.abap.abapgit.layout.AbapGitLayout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_create_repo(self, fake_walk, fake_checkout, fake_package, fake_to_xml):
        conn = Connection([])
        fake_walk.return_value = iter((([], [], []), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        args = parse_args(['package', package_name, '--starting-folder', starting_folder])
        with patch('sap.platform.abap.abapgit.layout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = False
            args.execute(conn, args)

        exp_repodir = os.path.abspath(package_name)
        fake_isdir.assert_called_once_with(exp_repodir)
        fake_makedirs.assert_called_once_with(exp_repodir)

        abapgit_file = os.path.join(exp_repodir, '.abapgit.xml')
        args, kwargs = fake_to_xml.call_args
        dot_abap = args[0]

        self.assertEqual(dot_abap.MASTER_LANGUAGE, 'E')
        self.assertEqual(dot_abap.FOLDER_LOGIC, sap.platform.abap.abapgit.FOLDER_LOGIC_FULL)
        self.assertEqual(dot_abap.STARTING_FOLDER, f'/{starting_folder}/')
        self.assertEqual([ignore for ignore in dot_abap.IGNORE], ['/.gitignore', '/LICENSE', '/README.md', '/package.json', '/.travis.yml'])
        self.assertEqual(kwargs['top_element'], 'DATA')

    @patch('sap.platform.abap.abapgit.layout.AbapGitLayout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_custom_repo_dir(self, fake_walk, fake_checkout, fake_package):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], [], exp_objects), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        repo_dir_name = 'valhalla'
        args = parse_args(['package', package_name, repo_dir_name, '--starting-folder', starting_folder])
        with patch('sap.platform.abap.abapgit.layout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_repodir = os.path.abspath(repo_dir_name)
        fake_isdir.assert_called_once_with(exp_repodir)

        exp_sourcedir = os.path.join(exp_repodir, starting_folder)
        fake_checkout.assert_called_once_with(conn, exp_objects, 'observer', destdir=exp_sourcedir)

    @patch('sap.platform.abap.abapgit.intf.InterfaceHandler.checkout', side_effect=KeyError('description'))
    def test_checkout_objects_handler_key_error(self, fake_checkout):
        objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]

        with patch('os.path.isdir', return_value=True), \
             patch('sap.cli.checkout.print') as fake_print, \
             self.assertRaises(KeyError):
            sap.cli.checkout.checkout_objects('connection', objects, 'observer', destdir='src')

        fake_print.assert_not_called()

    def test_checkout_objects_makedirs(self):
        conn = Connection([])

        starting_folder = os.path.join('backend', 'abap', 'src')
        with patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = False
            sap.cli.checkout.checkout_objects(conn, [], 'observer', destdir=starting_folder)

        fake_isdir.assert_called_once_with(starting_folder)
        fake_makedirs.assert_called_once_with(starting_folder)


class TestDOT_ABAP_GIT(unittest.TestCase):

    def test_for_empty_repo(self):
        dot_abap = sap.platform.abap.abapgit.DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='foo')
        dest = StringIO()
        sap.platform.abap.to_xml(dot_abap, dest=dest)
        self.maxDiff = None
        self.assertEqual(dest.getvalue(), '''<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DOT_ABAP_GIT>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>foo</STARTING_FOLDER>
   <FOLDER_LOGIC>FULL</FOLDER_LOGIC>
   <IGNORE>
    <item>/.gitignore</item>
    <item>/LICENSE</item>
    <item>/README.md</item>
    <item>/package.json</item>
    <item>/.travis.yml</item>
   </IGNORE>
  </DOT_ABAP_GIT>
 </asx:values>
</asx:abap>
''')


if __name__ == '__main__':
    unittest.main()
