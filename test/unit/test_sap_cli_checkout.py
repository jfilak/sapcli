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
import sap.platform.abap
from sap.adt.textelements import TextSymbol
import sap.platform.abap.abapgit
import sap.adt

from mock import Connection, Response, patch, PatcherTestCase, ConsoleOutputTestCase, StringIOFile
from test.unit.fixtures_cli_checkout import TTYP_SORTED_ABAPGIT_XML, TTYP_PREDEFINED_ABAPGIT_XML, \
    TTYP_STRING_ABAPGIT_XML, TTYP_SECONDARY_KEYS_ABAPGIT_XML, DDLS_NAME, DDLS_ADT_GET_RESPONSE_XML, DDLS_SOURCE_CODE, \
    DDLS_ABAPGIT_XML, DDLS_NO_SOURCE_TYPE_ABAPGIT_XML, DCLS_NAME, DCLS_ADT_GET_RESPONSE_XML, DCLS_SOURCE_CODE, \
    DCLS_ABAPGIT_XML, DDLX_NAME, DDLX_ADT_GET_RESPONSE_XML, DDLX_SOURCE_CODE, DDLX_ABAPGIT_XML, BDEF_ABAPGIT_XML, \
    BDEF_SOURCE_CODE, TABL_NAME, TABL_ADT_GET_RESPONSE_XML, TABL_SOURCE_CODE, TABL_ABAPGIT_XML, \
    TABL_ALL_FEATURES_SOURCE_CODE, TABL_ALL_FEATURES_ABAPGIT_XML, DOMA_ABAPGIT_XML, DOMA_ALL_FIELDS_ABAPGIT_XML, \
    DOMA_RAWSTRING_ABAPGIT_XML
from test.unit.fixtures_adt_domain import DOMAIN_NEW_NAME, DOMAIN_ADT_GET_SAMPLE_RESPONSE_XML, \
    DOMAIN_ADT_GET_ALL_FIELDS_RESPONSE_XML, DOMAIN_ADT_GET_RAWSTRING_RESPONSE_XML
from test.unit.fixtures_adt_dataelement import DATA_ELEMENT_NEW_NAME, DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML, \
    DATA_ELEMENT_ADT_GET_DOMAIN_RESPONSE_XML, DATA_ELEMENT_ADT_GET_STRING_RESPONSE_XML
from test.unit.fixtures_cli_checkout import DTEL_ABAPGIT_XML, DTEL_DOMAIN_ABAPGIT_XML, DTEL_STRING_ABAPGIT_XML
from test.unit.fixtures_cli_checkout import DBTAB_NAME, DBTAB_ADT_GET_RESPONSE_XML, DBTAB_GENERIC_SOURCE_CODE, \
    DBTAB_GENERIC_ABAPGIT_XML, DBTAB_FULL_SOURCE_CODE, DBTAB_FULL_SETTINGS_RESPONSE_XML, DBTAB_FULL_ABAPGIT_XML
from test.unit.fixtures_adt_table import TABLE_SETTINGS_ADT_GET_RESPONSE_XML
from test.unit.fixtures_sap_adt_behaviordefinition import BDEF_NAME, BDEF_ADT_GET_RESPONSE_XML
from test.unit.fixtures_sap_adt_tabletype import TABLE_TYPE_NAME, TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML, \
    TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML, TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML, \
    TABLE_TYPE_ADT_GET_RANGE_RESPONSE_XML, TABLE_TYPE_ADT_GET_STRING_RESPONSE_XML


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


class TestCheckout(unittest.TestCase):

    @patch('sap.fileformat.abapgit.clas.ClassHandler.checkout')
    def test_checkout_uppercase_name_clas(self, fake_clas):
        conn = Connection()

        args = parse_args(['class', 'zcl_lowercase'])
        args.execute(conn, args)

        args = parse_args(['class', 'ZCL_UPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_clas.mock_calls, [call(conn, 'CLAS/OC', 'ZCL_LOWERCASE', None),
                                                call(conn, 'CLAS/OC', 'ZCL_UPPERCASE', None)])

    @patch('sap.fileformat.abapgit.intf.InterfaceHandler.checkout')
    def test_checkout_uppercase_name_intf(self, fake_intf):
        conn = Connection()

        args = parse_args(['interface', 'zif_lowercase'])
        args.execute(conn, args)

        args = parse_args(['interface', 'ZIF_UPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_intf.mock_calls, [call(conn, 'INTF/OI', 'ZIF_LOWERCASE', None),
                                                call(conn, 'INTF/OI', 'ZIF_UPPERCASE', None)])

    @patch('sap.fileformat.abapgit.prog.ProgramHandler.checkout')
    def test_checkout_uppercase_name_prog(self, fake_prog):
        conn = Connection()

        args = parse_args(['program', 'zlowercase'])
        args.execute(conn, args)

        args = parse_args(['program', 'ZUPPERCASE'])
        args.execute(conn, args)

        self.assertEqual(fake_prog.mock_calls, [call(conn, 'PROG/P', 'ZLOWERCASE', None), call(conn, 'PROG/P', 'ZUPPERCASE', None)])

class TestCheckoutFunctionGroupCommand(unittest.TestCase):

    @patch('sap.cli.checkout.checkout_function_group')
    def test_default_source_format(self, fake_checkout):
        conn = Connection()

        args = parse_args(['function_group', 'zfugr_lowercase'])
        exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, 0)
        fake_checkout.assert_called_once_with(conn, 'ZFUGR_LOWERCASE',
                                              source_format=sap.cli.checkout.SourceCodeFormat.ABAPGIT)

    @patch('sap.cli.checkout.checkout_function_group')
    def test_abap_source_format(self, fake_checkout):
        conn = Connection()

        args = parse_args(['function_group', 'ZFUGR', '--format', 'ABAP'])
        exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, 0)
        fake_checkout.assert_called_once_with(conn, 'ZFUGR', source_format=sap.cli.checkout.SourceCodeFormat.ABAP)

    @patch('sap.cli.core.printerr')
    @patch('sap.cli.checkout.checkout_function_group')
    def test_failure(self, fake_checkout, fake_printerr):
        fake_checkout.side_effect = sap.cli.core.SAPCliError('Unsupported function group object: FOO BAR')

        conn = Connection()
        args = parse_args(['function_group', 'ZFUGR'])
        exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, 1)
        fake_printerr.assert_called_once_with('Checkout failed: Unsupported function group object: FOO BAR')


class TestCheckoutPackage(unittest.TestCase):

    @patch('sap.adt.Package.fetch')
    @patch('sap.cli.checkout.dump_attributes_to_file')
    @patch('sap.fileformat.abapgit.fugr.FunctionGroupHandler.checkout')
    @patch('sap.fileformat.abapgit.clas.ClassHandler.checkout')
    @patch('sap.fileformat.abapgit.intf.InterfaceHandler.checkout')
    @patch('sap.fileformat.abapgit.prog.ProgramHandler.checkout')
    @patch('sap.adt.package.walk')
    def test_checkout_package_recursive(self, fake_walk, fake_prog, fake_intf, fake_clas, fake_fugr, fake_dump, fake_fetch):
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

        args = parse_args(['package', package_name, '--recursive'])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
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
        fake_prog.assert_called_once_with(conn, 'PROG/P', 'Z_HELLO_WORLD', exp_destdir)
        fake_intf.assert_called_once_with(conn, 'INTF/OI', 'ZIF_HELLO_WORLD', exp_destdir)
        fake_fugr.assert_called_once_with(conn, 'FUGR/F', 'ZFUGR_HELLO', exp_destdir)
        self.assertEqual(fake_clas.mock_calls, [call(conn, 'CLAS/OC', 'ZCL_HELLO_WORLD', exp_destdir),
                                                call(conn, 'CLAS/OC', 'ZCL_TESTS', exp_sub_destdir)])

        self.assertEqual(fake_print.mock_calls, [call('Unsupported object: 7777/3 Magic Unicorn', file=sys.stderr)])

        self.assertEqual(fake_fetch.mock_calls, [call(), call()])
        self.assertEqual(fake_dump.mock_calls, [call('package',
                                                     (sap.platform.abap.ddic.DEVC(CTEXT='Description $VICTORY'),),
                                                     '.devc',
                                                     'LCL_OBJECT_DEVC',
                                                     destdir=exp_destdir),
                                                call('package',
                                                     (sap.platform.abap.ddic.DEVC(CTEXT='Description $VICTORY_TESTS'),),
                                                     '.devc',
                                                     'LCL_OBJECT_DEVC',
                                                     destdir=exp_sub_destdir)
                                                ])

    @patch('sap.cli.checkout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_non_recursive(self, fake_walk, fake_checkout, fake_package):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], ['$TESTS'], exp_objects),
                                       (['$TESTS'], [], [])))

        package_name = '$ROOT'
        starting_folder = 'src'
        args = parse_args(['package', package_name])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_destdir = os.path.abspath(os.path.join(package_name, starting_folder))
        fake_checkout.assert_called_once_with(conn, exp_objects, destdir=exp_destdir)

    @patch('sap.cli.checkout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_starting_folder(self, fake_walk, fake_checkout, fake_package):
        conn = Connection([])

        exp_objects = [SimpleNamespace(typ='INTF/OI', name='ZIF_HELLO_WORLD')]
        fake_walk.return_value = iter((([], [], exp_objects), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        args = parse_args(['package', package_name, '--starting-folder', starting_folder])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be executed')
            args.execute(conn, args)

        exp_repodir = os.path.abspath(package_name)
        fake_isdir.assert_called_once_with(exp_repodir)

        exp_sourcedir = os.path.abspath(os.path.join(exp_repodir, starting_folder))
        fake_checkout.assert_called_once_with(conn, exp_objects, destdir=exp_sourcedir)

    @patch('sap.platform.abap.to_xml')
    @patch('sap.cli.checkout.checkout_package')
    @patch('sap.cli.checkout.checkout_objects')
    @patch('sap.adt.package.walk')
    def test_checkout_package_create_repo(self, fake_walk, fake_checkout, fake_package, fake_to_xml):
        conn = Connection([])
        fake_walk.return_value = iter((([], [], []), ))

        package_name = '$VICTORY'
        starting_folder = os.path.join('backend', 'abap', 'src')
        args = parse_args(['package', package_name, '--starting-folder', starting_folder])
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
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

    @patch('sap.cli.checkout.checkout_package')
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
        with patch('sap.cli.checkout.open', mock_open()) as fake_open, \
             patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = True
            fake_makedirs.side_effect = Exception('Should not be evaluated')
            args.execute(conn, args)

        exp_repodir = os.path.abspath(repo_dir_name)
        fake_isdir.assert_called_once_with(exp_repodir)

        exp_sourcedir = os.path.join(exp_repodir, starting_folder)
        fake_checkout.assert_called_once_with(conn, exp_objects, destdir=exp_sourcedir)

    def test_checkout_objects_makedirs(self):
        conn = Connection([])

        starting_folder = os.path.join('backend', 'abap', 'src')
        with patch('os.path.isdir') as fake_isdir, \
             patch('os.makedirs') as fake_makedirs:
            fake_isdir.return_value = False
            sap.cli.checkout.checkout_objects(conn, [], destdir=starting_folder)

        fake_isdir.assert_called_once_with(starting_folder)
        fake_makedirs.assert_called_once_with(starting_folder)


class TestDOT_ABAP_GIT(unittest.TestCase):

    def test_for_empty_repo(self):
        dot_abap = sap.cli.checkout.DOT_ABAP_GIT.for_new_repo(STARTING_FOLDER='foo')
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


class TestCheckoutTableType(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, adt_response_xml, destdir=None):
        connection = Connection([Response(text=adt_response_xml, status_code=200, headers={})])

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            sap.cli.checkout.checkout_table_type(connection, TABLE_TYPE_NAME, destdir=destdir)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].adt_uri, f'/sap/bc/adt/ddic/tabletypes/{TABLE_TYPE_NAME.lower()}')

        return fake_open

    def assert_wrote_abapgit_file(self, fake_open, file_name, contents):
        fake_open.assert_called_once_with(file_name, 'w', encoding='utf8')

        written = ''.join(write_call.args[0] for write_call in fake_open().write.call_args_list)
        self.maxDiff = None
        self.assertEqual(written, contents)

    def test_checkout_ttyp_sorted_key_components(self):
        fake_open = self.checkout(TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, f'{TABLE_TYPE_NAME.lower()}.ttyp.xml', TTYP_SORTED_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'{TABLE_TYPE_NAME}\n- {TABLE_TYPE_NAME.lower()}.ttyp.xml\n')

    def test_checkout_ttyp_predefined(self):
        fake_open = self.checkout(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, f'{TABLE_TYPE_NAME.lower()}.ttyp.xml', TTYP_PREDEFINED_ABAPGIT_XML)

    def test_checkout_ttyp_predefined_ddic_data_type(self):
        fake_open = self.checkout(TABLE_TYPE_ADT_GET_STRING_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, f'{TABLE_TYPE_NAME.lower()}.ttyp.xml', TTYP_STRING_ABAPGIT_XML)

    def test_checkout_ttyp_destdir(self):
        fake_open = self.checkout(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML, destdir='src')

        fake_open.assert_called_once_with(os.path.join('src', f'{TABLE_TYPE_NAME.lower()}.ttyp.xml'), 'w',
                                          encoding='utf8')

    def test_checkout_ttyp_secondary_keys_skipped(self):
        fake_open = self.checkout(TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, f'{TABLE_TYPE_NAME.lower()}.ttyp.xml',
                                       TTYP_SECONDARY_KEYS_ABAPGIT_XML)
        self.assertEqual(self.console.caperr, f'Skipping unsupported secondary keys of {TABLE_TYPE_NAME}\n')

    def test_checkout_ttyp_range_not_supported(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            fake_open = self.checkout(TABLE_TYPE_ADT_GET_RANGE_RESPONSE_XML)
            # Dead code ...
            fake_open.assert_not_called()

        self.assertEqual(str(caught.exception),
                         f'Checkout of table type {TABLE_TYPE_NAME} failed: unsupported row type kind'
                         ' rangeTypeOnDataelement')

    def test_checkout_ttyp_command(self):
        args = parse_args(['tabletype', TABLE_TYPE_NAME.lower()])

        with patch('sap.cli.checkout.checkout_table_type') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', TABLE_TYPE_NAME)

    def test_checkout_objects_ttyp(self):
        objects = [SimpleNamespace(typ='TTYP/DA', name=TABLE_TYPE_NAME)]

        with patch('sap.cli.checkout.checkout_table_type') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', TABLE_TYPE_NAME, 'src')


class TestCheckoutDomain(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, adt_response_xml, destdir=None):
        connection = Connection([Response(text=adt_response_xml, status_code=200, headers={})])

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            sap.cli.checkout.checkout_domain(connection, DOMAIN_NEW_NAME, destdir=destdir)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].adt_uri, f'/sap/bc/adt/ddic/domains/{DOMAIN_NEW_NAME.lower()}')

        return fake_open

    def assert_wrote_abapgit_file(self, fake_open, file_name, contents):
        fake_open.assert_called_once_with(file_name, 'w', encoding='utf8')

        written = ''.join(write_call.args[0] for write_call in fake_open().write.call_args_list)
        self.maxDiff = None
        self.assertEqual(written, contents)

    def test_checkout_doma_sample(self):
        fake_open = self.checkout(DOMAIN_ADT_GET_SAMPLE_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, f'{DOMAIN_NEW_NAME.lower()}.doma.xml', DOMA_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'{DOMAIN_NEW_NAME}\n- {DOMAIN_NEW_NAME.lower()}.doma.xml\n')

    def test_checkout_doma_all_fields(self):
        fake_open = self.checkout(DOMAIN_ADT_GET_ALL_FIELDS_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, f'{DOMAIN_NEW_NAME.lower()}.doma.xml', DOMA_ALL_FIELDS_ABAPGIT_XML)

    def test_checkout_doma_ddic_data_type(self):
        fake_open = self.checkout(DOMAIN_ADT_GET_RAWSTRING_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, f'{DOMAIN_NEW_NAME.lower()}.doma.xml', DOMA_RAWSTRING_ABAPGIT_XML)

    def test_checkout_doma_destdir(self):
        fake_open = self.checkout(DOMAIN_ADT_GET_SAMPLE_RESPONSE_XML, destdir='src')

        fake_open.assert_called_once_with(os.path.join('src', f'{DOMAIN_NEW_NAME.lower()}.doma.xml'), 'w',
                                          encoding='utf8')

    def test_checkout_doma_command(self):
        args = parse_args(['domain', DOMAIN_NEW_NAME.lower()])

        with patch('sap.cli.checkout.checkout_domain') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', DOMAIN_NEW_NAME)

    def test_checkout_objects_doma(self):
        objects = [SimpleNamespace(typ='DOMA/DD', name=DOMAIN_NEW_NAME)]

        with patch('sap.cli.checkout.checkout_domain') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', DOMAIN_NEW_NAME, 'src')


class TestCheckoutDataElement(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, adt_response_xml, destdir=None):
        connection = Connection([Response(text=adt_response_xml, status_code=200, headers={})])

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            sap.cli.checkout.checkout_data_element(connection, DATA_ELEMENT_NEW_NAME, destdir=destdir)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].adt_uri,
                         f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NEW_NAME.lower()}')

        return fake_open

    def assert_wrote_abapgit_file(self, fake_open, contents):
        fake_open.assert_called_once_with(f'{DATA_ELEMENT_NEW_NAME.lower()}.dtel.xml', 'w', encoding='utf8')

        written = ''.join(write_call.args[0] for write_call in fake_open().write.call_args_list)
        self.maxDiff = None
        self.assertEqual(written, contents)

    def test_checkout_dtel_sample(self):
        fake_open = self.checkout(DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, DTEL_ABAPGIT_XML)
        self.assertConsoleContents(self.console,
                                   stdout=f'{DATA_ELEMENT_NEW_NAME}\n- {DATA_ELEMENT_NEW_NAME.lower()}.dtel.xml\n')

    def test_checkout_dtel_domain(self):
        fake_open = self.checkout(DATA_ELEMENT_ADT_GET_DOMAIN_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, DTEL_DOMAIN_ABAPGIT_XML)

    def test_checkout_dtel_ddic_data_type(self):
        fake_open = self.checkout(DATA_ELEMENT_ADT_GET_STRING_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, DTEL_STRING_ABAPGIT_XML)

    def test_checkout_dtel_reference_not_supported(self):
        adt_response_xml = DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML.replace(
            '<dtel:typeKind>predefinedAbapType</dtel:typeKind>', '<dtel:typeKind>refToClifType</dtel:typeKind>')

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.checkout(adt_response_xml)

        self.assertEqual(str(caught.exception),
                         f'Unsupported type of data element {DATA_ELEMENT_NEW_NAME}: refToClifType')

    def test_checkout_dtel_destdir(self):
        fake_open = self.checkout(DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML, destdir='src')

        fake_open.assert_called_once_with(os.path.join('src', f'{DATA_ELEMENT_NEW_NAME.lower()}.dtel.xml'), 'w',
                                          encoding='utf8')

    def test_checkout_dtel_command(self):
        args = parse_args(['dataelement', DATA_ELEMENT_NEW_NAME.lower()])

        with patch('sap.cli.checkout.checkout_data_element') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', DATA_ELEMENT_NEW_NAME)

    def test_checkout_objects_dtel(self):
        objects = [SimpleNamespace(typ='DTEL/DE', name=DATA_ELEMENT_NEW_NAME)]

        with patch('sap.cli.checkout.checkout_data_element') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', DATA_ELEMENT_NEW_NAME, 'src')


class TestDDICOutputLength(unittest.TestCase):

    def test_ddic_output_length_char(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('CHAR', '000001', '000000'), 1)

    def test_ddic_output_length_numc(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('NUMC', '000010', '000000'), 10)

    def test_ddic_output_length_raw(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('RAW', '000016', '000000'), 32)

    def test_ddic_output_length_lraw(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('LRAW', '000300', '000000'), 300)

    def test_ddic_output_length_dec_without_decimals(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('DEC', '000005', '000000'), 6)

    def test_ddic_output_length_dec_with_decimals(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('DEC', '000015', '000002'), 20)

    def test_ddic_output_length_dec_only_decimals(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('DEC', '000002', '000002'), 4)

    def test_ddic_output_length_dec_single_digit(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('DEC', '000001', '000000'), 1)

    def test_ddic_output_length_curr(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('CURR', '000013', '000002'), 17)

    def test_ddic_output_length_quan(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('QUAN', '000013', '000003'), 17)

    def test_ddic_output_length_int4(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('INT4', '000010', '000000'), 11)

    def test_ddic_output_length_dats(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('DATS', '000008', '000000'), 10)

    def test_ddic_output_length_string(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('STRG', '000000', '000000'), 0)

    def test_ddic_output_length_sstring(self):
        self.assertEqual(sap.cli.checkout.ddic_output_length('SSTR', '000020', '000000'), 0)

    def test_ddic_output_length_unknown(self):
        self.assertIsNone(sap.cli.checkout.ddic_output_length('D16D', '000010', '000002'))


class TestDDLSSourceType(unittest.TestCase):

    def test_ddls_source_type_view(self):
        source_type = sap.cli.checkout.ddls_source_type('''@AbapCatalog.sqlViewName: 'ZSAPCLI_CDS_V'
@EndUserText.label: 'Test CDS view'
define view ZSAPCLI_CDS
  as select from tadir
{
  pgmid
}
''')

        self.assertEqual(source_type, 'V')

    def test_ddls_source_type_view_entity(self):
        source_type = sap.cli.checkout.ddls_source_type(DDLS_SOURCE_CODE)

        self.assertEqual(source_type, 'W')

    def test_ddls_source_type_root_view_entity(self):
        source_type = sap.cli.checkout.ddls_source_type('''define root view entity ZSAPCLI_CDS as select from tadir
 {
  key pgmid
}
''')

        self.assertEqual(source_type, 'W')

    def test_ddls_source_type_view_entity_upper_case(self):
        source_type = sap.cli.checkout.ddls_source_type('''DEFINE VIEW ENTITY ZSAPCLI_CDS
  AS SELECT FROM tadir
{
  pgmid
}
''')

        self.assertEqual(source_type, 'W')

    def test_ddls_source_type_projection_view(self):
        source_type = sap.cli.checkout.ddls_source_type('''define root view entity ZSAPCLI_C_CDS
  provider contract transactional_query
  as projection on ZSAPCLI_CDS
{
  key pgmid
}
''')

        self.assertEqual(source_type, 'P')

    def test_ddls_source_type_table_function(self):
        source_type = sap.cli.checkout.ddls_source_type('''define table function ZSAPCLI_CDS
returns {
  client : abap.clnt;
  pgmid  : pgmid;
}
implemented by method zcl_sapcli_cds=>get_data;
''')

        self.assertEqual(source_type, 'F')

    def test_ddls_source_type_abstract_entity(self):
        source_type = sap.cli.checkout.ddls_source_type('''define abstract entity ZSAPCLI_CDS
{
  num : abap.int4;
}
''')

        self.assertEqual(source_type, 'A')

    def test_ddls_source_type_unknown(self):
        source_type = sap.cli.checkout.ddls_source_type('''define custom entity ZSAPCLI_CDS
{
  key num : abap.int4;
}
''')

        self.assertIsNone(source_type)


class TestCheckoutDataDefinition(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, source_code, destdir=None):
        connection = Connection([Response(text=DDLS_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text=source_code, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'})])
        written = {}

        def open_file(path, mode, encoding):
            self.assertEqual(mode, 'w')
            self.assertEqual(encoding, 'utf8')

            written[path] = StringIOFile('')
            return written[path]

        with patch('sap.fileformat.abapgit.files.open', side_effect=open_file):
            sap.cli.checkout.checkout_data_definition(connection, DDLS_NAME, destdir=destdir)

        self.assertEqual(connection.mock_methods(), [
            ('GET', f'/sap/bc/adt/ddic/ddl/sources/{DDLS_NAME.lower()}'),
            ('GET', f'/sap/bc/adt/ddic/ddl/sources/{DDLS_NAME.lower()}/source/main'),
        ])

        return written

    def test_checkout_ddls(self):
        written = self.checkout(DDLS_SOURCE_CODE)

        self.assertEqual(list(written), [f'{DDLS_NAME.lower()}.ddls.asddls', f'{DDLS_NAME.lower()}.ddls.xml'])
        self.assertEqual(written[f'{DDLS_NAME.lower()}.ddls.asddls'].getvalue(), DDLS_SOURCE_CODE)
        self.maxDiff = None
        self.assertEqual(written[f'{DDLS_NAME.lower()}.ddls.xml'].getvalue(), DDLS_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'''{DDLS_NAME}
- {DDLS_NAME.lower()}.ddls.asddls
- {DDLS_NAME.lower()}.ddls.xml
''')

    def test_checkout_ddls_adds_trailing_new_line(self):
        written = self.checkout(DDLS_SOURCE_CODE[:-1])

        self.assertEqual(written[f'{DDLS_NAME.lower()}.ddls.asddls'].getvalue(), DDLS_SOURCE_CODE)

    def test_checkout_ddls_destdir(self):
        written = self.checkout(DDLS_SOURCE_CODE, destdir='src')

        self.assertEqual(list(written), [os.path.join('src', f'{DDLS_NAME.lower()}.ddls.asddls'),
                                         os.path.join('src', f'{DDLS_NAME.lower()}.ddls.xml')])

    def test_checkout_ddls_unknown_source_type(self):
        written = self.checkout('''define custom entity ZSAPCLI_CDS
{
  key num : abap.int4;
}
''')

        self.maxDiff = None
        self.assertEqual(written[f'{DDLS_NAME.lower()}.ddls.xml'].getvalue(), DDLS_NO_SOURCE_TYPE_ABAPGIT_XML)
        self.assertEqual(self.console.caperr, f'Unknown source type of data definition {DDLS_NAME}\n')

    def test_checkout_ddls_command(self):
        args = parse_args(['ddl', DDLS_NAME.lower()])

        with patch('sap.cli.checkout.checkout_data_definition') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', DDLS_NAME)

    def test_checkout_objects_ddls(self):
        objects = [SimpleNamespace(typ='DDLS/DF', name=DDLS_NAME)]

        with patch('sap.cli.checkout.checkout_data_definition') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', DDLS_NAME, 'src')



class TestCheckoutAccessControl(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, destdir=None):
        connection = Connection([Response(text=DCLS_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text=DCLS_SOURCE_CODE, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'})])
        written = {}

        def open_file(path, mode, encoding):
            self.assertEqual(mode, 'w')
            self.assertEqual(encoding, 'utf8')

            written[path] = StringIOFile('')
            return written[path]

        with patch('sap.fileformat.abapgit.files.open', side_effect=open_file):
            sap.cli.checkout.checkout_access_control(connection, DCLS_NAME, destdir=destdir)

        self.assertEqual(connection.mock_methods(), [
            ('GET', f'/sap/bc/adt/acm/dcl/sources/{DCLS_NAME.lower()}'),
            ('GET', f'/sap/bc/adt/acm/dcl/sources/{DCLS_NAME.lower()}/source/main'),
        ])

        return written

    def test_checkout_dcls(self):
        written = self.checkout()

        self.assertEqual(list(written), [f'{DCLS_NAME.lower()}.dcls.asdcls', f'{DCLS_NAME.lower()}.dcls.xml'])
        # abapGit writes the source code of access controls as it is
        self.assertEqual(written[f'{DCLS_NAME.lower()}.dcls.asdcls'].getvalue(), DCLS_SOURCE_CODE)
        self.maxDiff = None
        self.assertEqual(written[f'{DCLS_NAME.lower()}.dcls.xml'].getvalue(), DCLS_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'''{DCLS_NAME}
- {DCLS_NAME.lower()}.dcls.asdcls
- {DCLS_NAME.lower()}.dcls.xml
''')

    def test_checkout_dcls_destdir(self):
        written = self.checkout(destdir='src')

        self.assertEqual(list(written), [os.path.join('src', f'{DCLS_NAME.lower()}.dcls.asdcls'),
                                         os.path.join('src', f'{DCLS_NAME.lower()}.dcls.xml')])

    def test_checkout_dcls_command(self):
        args = parse_args(['dcl', DCLS_NAME.lower()])

        with patch('sap.cli.checkout.checkout_access_control') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', DCLS_NAME)

    def test_checkout_objects_dcls(self):
        objects = [SimpleNamespace(typ='DCLS/DL', name=DCLS_NAME)]

        with patch('sap.cli.checkout.checkout_access_control') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', DCLS_NAME, 'src')



class TestCheckoutMetadataExtension(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, destdir=None):
        connection = Connection([Response(text=DDLX_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text=DDLX_SOURCE_CODE, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'})])
        written = {}

        def open_file(path, mode, encoding):
            self.assertEqual(mode, 'w')
            self.assertEqual(encoding, 'utf8')

            written[path] = StringIOFile('')
            return written[path]

        with patch('sap.fileformat.abapgit.files.open', side_effect=open_file):
            sap.cli.checkout.checkout_metadata_extension(connection, DDLX_NAME, destdir=destdir)

        self.assertEqual(connection.mock_methods(), [
            ('GET', f'/sap/bc/adt/ddic/ddlx/sources/{DDLX_NAME.lower()}'),
            ('GET', f'/sap/bc/adt/ddic/ddlx/sources/{DDLX_NAME.lower()}/source/main'),
        ])

        return written

    def test_checkout_ddlx(self):
        written = self.checkout()

        self.assertEqual(list(written), [f'{DDLX_NAME.lower()}.ddlx.asddlxs', f'{DDLX_NAME.lower()}.ddlx.xml'])
        # abapGit writes the source code of metadata extensions as it is
        self.assertEqual(written[f'{DDLX_NAME.lower()}.ddlx.asddlxs'].getvalue(), DDLX_SOURCE_CODE)
        self.maxDiff = None
        self.assertEqual(written[f'{DDLX_NAME.lower()}.ddlx.xml'].getvalue(), DDLX_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'''{DDLX_NAME}
- {DDLX_NAME.lower()}.ddlx.asddlxs
- {DDLX_NAME.lower()}.ddlx.xml
''')

    def test_checkout_ddlx_destdir(self):
        written = self.checkout(destdir='src')

        self.assertEqual(list(written), [os.path.join('src', f'{DDLX_NAME.lower()}.ddlx.asddlxs'),
                                         os.path.join('src', f'{DDLX_NAME.lower()}.ddlx.xml')])

    def test_checkout_ddlx_command(self):
        args = parse_args(['ddlx', DDLX_NAME.lower()])

        with patch('sap.cli.checkout.checkout_metadata_extension') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', DDLX_NAME)

    def test_checkout_objects_ddlx(self):
        objects = [SimpleNamespace(typ='DDLX/EX', name=DDLX_NAME)]

        with patch('sap.cli.checkout.checkout_metadata_extension') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', DDLX_NAME, 'src')



class TestCheckoutBehaviorDefinition(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, adt_response_xml, destdir=None):
        connection = Connection([Response(text=adt_response_xml, status_code=200, headers={}),
                                 Response(text=BDEF_SOURCE_CODE, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'})])
        written = {}

        def open_file(path, mode, encoding):
            self.assertEqual(mode, 'w')
            self.assertEqual(encoding, 'utf8')

            written[path] = StringIOFile('')
            return written[path]

        with patch('sap.fileformat.abapgit.files.open', side_effect=open_file):
            sap.cli.checkout.checkout_behavior_definition(connection, BDEF_NAME, destdir=destdir)

        self.assertEqual(connection.mock_methods(), [
            ('GET', f'/sap/bc/adt/bo/behaviordefinitions/{BDEF_NAME.lower()}'),
            ('GET', f'/sap/bc/adt/bo/behaviordefinitions/{BDEF_NAME.lower()}/source/main'),
        ])

        return written

    def test_checkout_bdef(self):
        written = self.checkout(BDEF_ADT_GET_RESPONSE_XML)

        self.assertEqual(list(written), [f'{BDEF_NAME.lower()}.bdef.asbdef', f'{BDEF_NAME.lower()}.bdef.xml'])
        # abapGit writes the source code of behavior definitions as it is
        self.assertEqual(written[f'{BDEF_NAME.lower()}.bdef.asbdef'].getvalue(), BDEF_SOURCE_CODE)
        self.maxDiff = None
        self.assertEqual(written[f'{BDEF_NAME.lower()}.bdef.xml'].getvalue(), BDEF_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'''{BDEF_NAME}
- {BDEF_NAME.lower()}.bdef.asbdef
- {BDEF_NAME.lower()}.bdef.xml
''')

    def test_checkout_bdef_cloud_development(self):
        written = self.checkout(BDEF_ADT_GET_RESPONSE_XML.replace('adtcore:abapLanguageVersion="standard"',
                                                                  'adtcore:abapLanguageVersion="cloudDevelopment"'))

        self.assertIn('    <ABAP_LANGU_VERSION>5</ABAP_LANGU_VERSION>\n',
                      written[f'{BDEF_NAME.lower()}.bdef.xml'].getvalue())

    def test_checkout_bdef_key_user(self):
        written = self.checkout(BDEF_ADT_GET_RESPONSE_XML.replace('adtcore:abapLanguageVersion="standard"',
                                                                  'adtcore:abapLanguageVersion="keyUser"'))

        self.assertIn('    <ABAP_LANGU_VERSION>2</ABAP_LANGU_VERSION>\n',
                      written[f'{BDEF_NAME.lower()}.bdef.xml'].getvalue())

    def test_checkout_bdef_without_links(self):
        written = self.checkout(re.sub(r'\s*<atom:link [^>]*/>', '', BDEF_ADT_GET_RESPONSE_XML))

        self.maxDiff = None
        self.assertEqual(written[f'{BDEF_NAME.lower()}.bdef.xml'].getvalue(),
                         re.sub(r'    <LINKS>\n.*    </LINKS>\n', '', BDEF_ABAPGIT_XML, flags=re.DOTALL))

    def test_checkout_bdef_destdir(self):
        written = self.checkout(BDEF_ADT_GET_RESPONSE_XML, destdir='src')

        self.assertEqual(list(written), [os.path.join('src', f'{BDEF_NAME.lower()}.bdef.asbdef'),
                                         os.path.join('src', f'{BDEF_NAME.lower()}.bdef.xml')])

    def test_checkout_bdef_command(self):
        args = parse_args(['bdef', BDEF_NAME.lower()])

        with patch('sap.cli.checkout.checkout_behavior_definition') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', BDEF_NAME)

    def test_checkout_objects_bdef(self):
        objects = [SimpleNamespace(typ='BDEF/BDO', name=BDEF_NAME)]

        with patch('sap.cli.checkout.checkout_behavior_definition') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', BDEF_NAME, 'src')


class TestCheckoutStructure(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, source_code, destdir=None):
        connection = Connection([Response(text=TABL_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text=source_code, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'})])

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            sap.cli.checkout.checkout_structure(connection, TABL_NAME, destdir=destdir)

        self.assertEqual(connection.mock_methods(), [
            ('GET', f'/sap/bc/adt/ddic/structures/{TABL_NAME.lower()}'),
            ('GET', f'/sap/bc/adt/ddic/structures/{TABL_NAME.lower()}/source/main'),
        ])

        return fake_open

    def checkout_failure(self, source_code):
        with self.assertRaises(sap.cli.core.SAPCliError) as caught:
            self.checkout(source_code)

        return str(caught.exception)

    def assert_wrote_abapgit_file(self, fake_open, contents):
        fake_open.assert_called_once_with(f'{TABL_NAME.lower()}.tabl.xml', 'w', encoding='utf8')

        written = ''.join(write_call.args[0] for write_call in fake_open().write.call_args_list)
        self.maxDiff = None
        self.assertEqual(written, contents)

    def test_checkout_tabl(self):
        fake_open = self.checkout(TABL_SOURCE_CODE)

        self.assert_wrote_abapgit_file(fake_open, TABL_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'{TABL_NAME}\n- {TABL_NAME.lower()}.tabl.xml\n')

    def test_checkout_tabl_all_features(self):
        fake_open = self.checkout(TABL_ALL_FEATURES_SOURCE_CODE)

        self.assert_wrote_abapgit_file(fake_open, TABL_ALL_FEATURES_ABAPGIT_XML)

    def test_checkout_tabl_no_enhancement_category(self):
        fake_open = self.checkout(TABL_SOURCE_CODE.replace('@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE\n', ''))

        self.assert_wrote_abapgit_file(fake_open, TABL_ABAPGIT_XML.replace('    <EXCLASS>1</EXCLASS>\n', ''))

    def test_checkout_tabl_destdir(self):
        fake_open = self.checkout(TABL_SOURCE_CODE, destdir='src')

        fake_open.assert_called_once_with(os.path.join('src', f'{TABL_NAME.lower()}.tabl.xml'), 'w', encoding='utf8')

    def test_checkout_tabl_unsupported_annotation(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('@AbapCatalog.enhancement.category : #NOT_EXTENSIBLE',
                                                                 '@AbapCatalog.dataMaintenance : #RESTRICTED'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed:'
                                  ' unsupported annotation @AbapCatalog.dataMaintenance')

    def test_checkout_tabl_unsupported_field_annotation(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('  created_at',
                                                                 '  @AbapCatalog.textLanguage\n  created_at'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed:'
                                  ' unsupported annotation @AbapCatalog.textLanguage')

    def test_checkout_tabl_unsupported_enhancement_category(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('#NOT_EXTENSIBLE', '#FOO'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: unsupported enhancement category #FOO')

    def test_checkout_tabl_unsupported_data_type(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('abap.char(12)', 'abap.utclong'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: unsupported data type abap.utclong')

    def test_checkout_tabl_invalid_data_type_parameters(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('abap.char(12)', 'abap.char(12,2)'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: invalid parameters of data type abap.char')

    def test_checkout_tabl_reference(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('timestampl', 'reference to cl_abap_typedescr'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: unexpected token "to"')

    def test_checkout_tabl_foreign_key(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('devclass;',
                                                                 'devclass with foreign key tdevc'
                                                                 ' where devclass = zsapcli_struct.abap_package;'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: unexpected token "with"')

    def test_checkout_tabl_table(self):
        message = self.checkout_failure(TABL_SOURCE_CODE.replace('define structure', 'define table'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: unexpected token "table"')

    def test_checkout_tabl_trailing_tokens(self):
        message = self.checkout_failure(TABL_SOURCE_CODE + ';')

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: unexpected token ";"')

    def test_checkout_tabl_unexpected_end(self):
        message = self.checkout_failure(TABL_SOURCE_CODE[:-1])

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed: unexpected end of source code')

    def test_checkout_tabl_command(self):
        args = parse_args(['structure', TABL_NAME.lower()])

        with patch('sap.cli.checkout.checkout_structure') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', TABL_NAME)

    def test_checkout_objects_tabl(self):
        objects = [SimpleNamespace(typ='TABL/DS', name=TABL_NAME)]

        with patch('sap.cli.checkout.checkout_structure') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', TABL_NAME, 'src')



class TestCheckoutTable(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def checkout(self, source_code, settings_xml=TABLE_SETTINGS_ADT_GET_RESPONSE_XML, destdir=None):
        connection = Connection([Response(text=DBTAB_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text=source_code, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'}),
                                 Response(text=settings_xml, status_code=200, headers={})])

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            sap.cli.checkout.checkout_table(connection, DBTAB_NAME, destdir=destdir)

        self.assertEqual(connection.mock_methods(), [
            ('GET', f'/sap/bc/adt/ddic/tables/{DBTAB_NAME.lower()}'),
            ('GET', f'/sap/bc/adt/ddic/tables/{DBTAB_NAME.lower()}/source/main'),
            ('GET', f'/sap/bc/adt/ddic/db/settings/{DBTAB_NAME.lower()}'),
        ])

        return fake_open

    def checkout_failure(self, source_code):
        with self.assertRaises(sap.cli.core.SAPCliError) as caught:
            self.checkout(source_code)

        return str(caught.exception)

    def assert_wrote_abapgit_file(self, fake_open, contents):
        fake_open.assert_called_once_with(f'{DBTAB_NAME.lower()}.tabl.xml', 'w', encoding='utf8')

        written = ''.join(write_call.args[0] for write_call in fake_open().write.call_args_list)
        self.maxDiff = None
        self.assertEqual(written, contents)

    def test_checkout_dbtab_generic_buffering(self):
        fake_open = self.checkout(DBTAB_GENERIC_SOURCE_CODE)

        self.assert_wrote_abapgit_file(fake_open, DBTAB_GENERIC_ABAPGIT_XML)
        self.assertConsoleContents(self.console, stdout=f'{DBTAB_NAME}\n- {DBTAB_NAME.lower()}.tabl.xml\n')

    def test_checkout_dbtab_full(self):
        fake_open = self.checkout(DBTAB_FULL_SOURCE_CODE, settings_xml=DBTAB_FULL_SETTINGS_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, DBTAB_FULL_ABAPGIT_XML)

    def test_checkout_dbtab_restricted_maintenance(self):
        fake_open = self.checkout(DBTAB_GENERIC_SOURCE_CODE.replace('#NOT_ALLOWED', '#RESTRICTED'))

        self.assert_wrote_abapgit_file(fake_open, DBTAB_GENERIC_ABAPGIT_XML.replace('    <MAINFLAG>N</MAINFLAG>\n', ''))

    def test_checkout_dbtab_destdir(self):
        fake_open = self.checkout(DBTAB_GENERIC_SOURCE_CODE, destdir='src')

        fake_open.assert_called_once_with(os.path.join('src', f'{DBTAB_NAME.lower()}.tabl.xml'), 'w',
                                          encoding='utf8')

    def test_checkout_dbtab_foreign_key(self):
        message = self.checkout_failure(DBTAB_GENERIC_SOURCE_CODE.replace(
            'abap.char(30) not null;', 'abap.char(30) not null with foreign key tdevc where devclass = x.name;'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unexpected token "with"')

    def test_checkout_dbtab_unsupported_table_category(self):
        message = self.checkout_failure(DBTAB_GENERIC_SOURCE_CODE.replace('#TRANSPARENT', '#GLOBAL_TEMPORARY'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported table category #GLOBAL_TEMPORARY')

    def test_checkout_dbtab_unsupported_data_maintenance(self):
        message = self.checkout_failure(DBTAB_GENERIC_SOURCE_CODE.replace('#NOT_ALLOWED', '#FOO'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported data maintenance #FOO')

    def test_checkout_dbtab_unsupported_annotation(self):
        message = self.checkout_failure(DBTAB_GENERIC_SOURCE_CODE.replace(
            '@AbapCatalog.tableCategory', '@AbapCatalog.activationType : #ADAPT_C_STRUCTURES\n@AbapCatalog.tableCategory'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported annotation'
                                  ' @AbapCatalog.activationType')

    def test_checkout_dbtab_key_include(self):
        message = self.checkout_failure(DBTAB_GENERIC_SOURCE_CODE.replace('  key name', '  key include zzs_criteria;\n  key name'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported key include')

    def test_checkout_dbtab_structure(self):
        message = self.checkout_failure(DBTAB_GENERIC_SOURCE_CODE.replace('define table', 'define structure'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unexpected token "structure"')

    def test_checkout_dbtab_command(self):
        args = parse_args(['table', DBTAB_NAME.lower()])

        with patch('sap.cli.checkout.checkout_table') as fake_checkout:
            args.execute('connection', args)

        fake_checkout.assert_called_once_with('connection', DBTAB_NAME)

    def test_checkout_objects_dbtab(self):
        objects = [SimpleNamespace(typ='TABL/DT', name=DBTAB_NAME)]

        with patch('sap.cli.checkout.checkout_table') as fake_checkout, \
             patch('os.path.isdir', return_value=True):
            sap.cli.checkout.checkout_objects('connection', objects, destdir='src')

        fake_checkout.assert_called_once_with('connection', DBTAB_NAME, 'src')


if __name__ == '__main__':
    unittest.main()
