#!/usr/bin/env python3

import os
import re
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import sap.adt
import sap.errors
import sap.platform.abap.abapgit.tabl
from sap.adt.errors import ExceptionCheckinFailure
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import CheckinContext, ObjectHandler, RepoObject, RepoPackage, RepositoryObserver
from sap.platform.abap.abapgit.tabl import TableHandler

from mock import Connection, PatcherTestCase, Response, StringIOFile
from fixtures_sap_platform_abap_abapgit_tabl import TABL_SOURCE_CODE, TABL_ABAPGIT_XML, \
    CHECKOUT_TABL_ALL_FEATURES_SOURCE_CODE, TABL_ALL_FEATURES_ABAPGIT_XML, CHECKOUT_DBTAB_GENERIC_SOURCE_CODE, \
    DBTAB_GENERIC_ABAPGIT_XML, CHECKOUT_DBTAB_FULL_SOURCE_CODE, DBTAB_FULL_ABAPGIT_XML, \
    TABL_ADT_NEW_OBJECT_REQUEST_XML, TABL_XML, TABL_NAME, TABL_ALL_FEATURES_XML, TABL_ALL_FEATURES_SOURCE_CODE, \
    TABL_NO_EXCLASS_XML, TABL_NO_EXCLASS_SOURCE_CODE, TABL_DELIMITED_GROUP_XML, TABL_DELIMITED_GROUP_SOURCE_CODE, \
    TABL_POOL_XML, TABL_UNKNOWN_EXCLASS_XML, TABL_REFERENCE_XML, TABL_UNKNOWN_DATATYPE_XML, TABL_APPEND_XML, \
    TABL_UNKNOWN_REFERENCE_XML, TABL_FOREIGN_KEYS_XML, DBTAB_XML, DBTAB_ADT_NEW_OBJECT_REQUEST_XML, \
    DBTAB_SOURCE_CODE, DBTAB_SETTINGS_REQUEST_XML, DBTAB_NAME, DBTAB_FULL_XML, DBTAB_FULL_SOURCE_CODE, \
    DBTAB_FULL_SETTINGS_REQUEST_XML, DBTAB_GENERIC_XML, DBTAB_GENERIC_SOURCE_CODE, \
    DBTAB_GENERIC_SETTINGS_REQUEST_XML, DBTAB_FOREIGN_KEYS_XML, DBTAB_KEY_INCLUDE_XML, \
    DBTAB_FULL_SETTINGS_RESPONSE_XML, TABL_ADT_ALREADY_EXISTS_RESPONSE_XML, TABL_ADT_GET_RESPONSE_XML, \
    DBTAB_ADT_GET_RESPONSE_XML
from fixtures_adt_table import TABLE_SETTINGS_ADT_GET_RESPONSE_XML


class TestTableHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = TableHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'tabl')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.Table.OBJTYPE.code, sap.adt.Structure.OBJTYPE.code))


class TestTableHandlerLocate(unittest.TestCase):

    def test_no_source_code(self):
        handler = TableHandler()
        repo_obj = RepoObject('tabl', 'zfoo', './src/zfoo.tabl.xml', [],
                              RepoPackage('./src', './src/package.devc.xml', None), handler)

        self.assertIsNone(handler.locate(repo_obj, 'source/main', 1))


class TestTableHandlerCheckoutStructure(unittest.TestCase, PatcherTestCase):

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
        self.observer = Mock(spec=RepositoryObserver)
        self.handler = TableHandler()

    def checkout(self, source_code, destdir=None):
        connection = Connection([Response(text=TABL_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text=source_code, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'})])

        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open:
            self.handler.checkout(connection, 'TABL/DS', TABL_NAME, destdir, self.observer)

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
        self.assertEqual(self.observer.mock_calls, [
            call.checking_out(TABL_NAME),
            call.file_written(f'{TABL_NAME.lower()}.tabl.xml'),
        ])

    def test_checkout_tabl_all_features(self):
        fake_open = self.checkout(CHECKOUT_TABL_ALL_FEATURES_SOURCE_CODE)

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
                                                                 '  @AbapCatalog.anonymizedWhenDelivered : true\n'
                                                                 '  created_at'))

        self.assertEqual(message, f'Checkout of structure {TABL_NAME} failed:'
                                  ' unsupported annotation @AbapCatalog.anonymizedWhenDelivered')

    def test_checkout_tabl_text_language(self):
        fake_open = self.checkout(TABL_SOURCE_CODE.replace('  is_offline', '  @AbapCatalog.textLanguage\n  is_offline'))

        self.assert_wrote_abapgit_file(fake_open, TABL_ABAPGIT_XML.replace(
            '     <ROLLNAME>XFELD</ROLLNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n',
            '     <ROLLNAME>XFELD</ROLLNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n     <LANGUFLAG>X</LANGUFLAG>\n'))

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


class TestTableHandlerCheckoutTable(unittest.TestCase, PatcherTestCase):

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
        self.observer = Mock(spec=RepositoryObserver)
        self.handler = TableHandler()

    def checkout(self, source_code, settings_xml=TABLE_SETTINGS_ADT_GET_RESPONSE_XML, destdir=None):
        connection = Connection([Response(text=DBTAB_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text=source_code, status_code=200,
                                          headers={'Content-Type': 'text/plain; charset=utf-8'}),
                                 Response(text=settings_xml, status_code=200, headers={})])

        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open:
            self.handler.checkout(connection, 'TABL/DT', DBTAB_NAME, destdir, self.observer)

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
        fake_open = self.checkout(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE)

        self.assert_wrote_abapgit_file(fake_open, DBTAB_GENERIC_ABAPGIT_XML)
        self.assertEqual(self.observer.mock_calls, [
            call.checking_out(DBTAB_NAME),
            call.file_written(f'{DBTAB_NAME.lower()}.tabl.xml'),
        ])

    def test_checkout_dbtab_full(self):
        fake_open = self.checkout(CHECKOUT_DBTAB_FULL_SOURCE_CODE, settings_xml=DBTAB_FULL_SETTINGS_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, DBTAB_FULL_ABAPGIT_XML)

    def test_checkout_dbtab_restricted_maintenance(self):
        fake_open = self.checkout(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace('#NOT_ALLOWED', '#RESTRICTED'))

        self.assert_wrote_abapgit_file(fake_open, DBTAB_GENERIC_ABAPGIT_XML.replace('    <MAINFLAG>N</MAINFLAG>\n', ''))

    def test_checkout_dbtab_text_language(self):
        fake_open = self.checkout(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace('  value ',
                                                                             '  @AbapCatalog.textLanguage\n  value '))

        self.assert_wrote_abapgit_file(fake_open, DBTAB_GENERIC_ABAPGIT_XML.replace(
            '     <MASK>  STRG</MASK>\n', '     <MASK>  STRG</MASK>\n     <LANGUFLAG>X</LANGUFLAG>\n'))

    def test_checkout_dbtab_text_language_with_value(self):
        message = self.checkout_failure(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace(
            '  value ', '  @AbapCatalog.textLanguage : true\n  value '))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unexpected token "true"')

    def test_checkout_dbtab_destdir(self):
        fake_open = self.checkout(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE, destdir='src')

        fake_open.assert_called_once_with(os.path.join('src', f'{DBTAB_NAME.lower()}.tabl.xml'), 'w',
                                          encoding='utf8')

    def test_checkout_dbtab_foreign_key(self):
        message = self.checkout_failure(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace(
            'abap.char(30) not null;', 'abap.char(30) not null with foreign key tdevc where devclass = x.name;'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unexpected token "with"')

    def test_checkout_dbtab_unsupported_table_category(self):
        message = self.checkout_failure(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace('#TRANSPARENT', '#GLOBAL_TEMPORARY'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported table category #GLOBAL_TEMPORARY')

    def test_checkout_dbtab_unsupported_data_maintenance(self):
        message = self.checkout_failure(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace('#NOT_ALLOWED', '#FOO'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported data maintenance #FOO')

    def test_checkout_dbtab_unsupported_annotation(self):
        message = self.checkout_failure(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace(
            '@AbapCatalog.tableCategory', '@AbapCatalog.activationType : #ADAPT_C_STRUCTURES\n@AbapCatalog.tableCategory'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported annotation'
                                  ' @AbapCatalog.activationType')

    def test_checkout_dbtab_key_include(self):
        message = self.checkout_failure(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace('  key name', '  key include zzs_criteria;\n  key name'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unsupported key include')

    def test_checkout_dbtab_structure(self):
        message = self.checkout_failure(CHECKOUT_DBTAB_GENERIC_SOURCE_CODE.replace('define table', 'define structure'))

        self.assertEqual(message, f'Checkout of table {DBTAB_NAME} failed: unexpected token "structure"')


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestTableHandlerCheckinStructure(unittest.TestCase, PatcherTestCase):

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
        self.observer = Mock(spec=RepositoryObserver)
        self.handler = TableHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('tabl', TABL_NAME.lower(), f'./src/{TABL_NAME.lower()}.tabl.xml',
                                   [], self.package, self.handler)

    def checkin(self, abapgit_xml, responses, corrnr=None):
        connection = Connection(responses, user='DEVELOPER')

        with patch('sap.platform.abap.abapgit.tabl.open', mock_open(read_data=abapgit_xml)) as fake_open:
            result = self.checkin_object(connection, self.repo_obj, corrnr=corrnr)

        fake_open.assert_called_once_with(self.repo_obj.path, encoding='utf-8')

        return (connection, result)

    def checkin_failure(self, abapgit_xml):
        connection = Connection([], user='DEVELOPER')

        with patch('sap.platform.abap.abapgit.tabl.open', mock_open(read_data=abapgit_xml)), \
             self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin_object(connection, self.repo_obj)

        self.assertEqual(connection.execs, [])

        return caught.exception.message

    def responses_ok(self):
        return [
            Response(text='', status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, source_code, create_params=None, write_params=None):
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/structures')
        self.assertEqual(connection.execs[0].params, create_params)
        self.maxDiff = None
        self.assertEqual(connection.execs[0].body.decode('utf-8'), TABL_ADT_NEW_OBJECT_REQUEST_XML)

        self.assertEqual(connection.execs[1].method, 'PUT')
        self.assertEqual(connection.execs[1].adt_uri, f'/sap/bc/adt/ddic/structures/{TABL_NAME.lower()}/source/main')
        self.assertEqual(connection.execs[1].headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(connection.execs[1].params, write_params or {'lockHandle': 'lock_handle'})
        self.assertEqual(connection.execs[1].body.decode('utf-8'), source_code)

    def checkin_object(self, connection, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj, self.observer)
        context = CheckinContext(connection, '$TMP', corrnr, check_before_save, self.observer)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_tabl(self, fake_lock, fake_unlock):
        connection, result = self.checkin(TABL_XML, self.responses_ok())

        self.assert_requests(connection, TABL_SOURCE_CODE)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, TABL_NAME)
        self.assertEqual(result.used_files, [])

        self.assertEqual(self.observer.mock_calls, [
            call.creating('Structure', TABL_NAME.lower()),
            call.writing('Structure', TABL_NAME.lower()),
        ])

    def test_checkin_tabl_all_features(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TABL_ALL_FEATURES_XML, self.responses_ok())

        # the description of the new object is not part of the test
        self.assertEqual(connection.execs[1].body.decode('utf-8'), TABL_ALL_FEATURES_SOURCE_CODE)

    def test_checkin_tabl_text_language(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TABL_XML.replace(
            '     <ROLLNAME>XFELD</ROLLNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n',
            '     <ROLLNAME>XFELD</ROLLNAME>\n     <ADMINFIELD>0</ADMINFIELD>\n     <LANGUFLAG>X</LANGUFLAG>\n'),
            self.responses_ok())

        self.assert_requests(connection,
                             TABL_SOURCE_CODE.replace('  is_offline', '  @AbapCatalog.textLanguage\n  is_offline'))

    def test_checkin_tabl_no_exclass(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TABL_NO_EXCLASS_XML, self.responses_ok())

        self.assert_requests(connection, TABL_NO_EXCLASS_SOURCE_CODE)

    def test_checkin_tabl_delimited_group_name(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TABL_DELIMITED_GROUP_XML, self.responses_ok())

        self.assert_requests(connection, TABL_DELIMITED_GROUP_SOURCE_CODE)

    def test_checkin_tabl_with_corrnr(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TABL_XML, self.responses_ok(), corrnr='420')

        self.assert_requests(connection, TABL_SOURCE_CODE, create_params={'corrNr': '420'},
                             write_params={'lockHandle': 'lock_handle', 'corrNr': '420'})

    def test_checkin_tabl_already_exists(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[0] = Response(text=TABL_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                                headers={'content-type': 'application/xml'})

        connection, _ = self.checkin(TABL_XML, responses)

        self.assert_requests(connection, TABL_SOURCE_CODE)

    def test_checkin_tabl_check_before_save(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        with patch('sap.platform.abap.abapgit.tabl.open', mock_open(read_data=TABL_XML)), \
             patch('sap.adt.checks.write_source') as fake_write:
            result = self.checkin_object(connection, self.repo_obj, check_before_save=True)

        fake_write.assert_called_once_with(TABL_SOURCE_CODE, result.abap_objects[0], corrnr=None,
                                           source_label=self.repo_obj.path, check_before_save=True)

    def test_checkin_tabl_pool_table(self, fake_lock, fake_unlock):
        message = self.checkin_failure(TABL_POOL_XML)

        self.assertEqual(message, f'Unsupported table category "POOL" of {TABL_NAME.lower()}:'
                                  ' only structures and transparent tables are supported')

    def test_checkin_tabl_unknown_exclass(self, fake_lock, fake_unlock):
        message = self.checkin_failure(TABL_UNKNOWN_EXCLASS_XML)

        self.assertEqual(message, f'Unsupported enhancement category "9" of structure {TABL_NAME.lower()}')

    def test_checkin_tabl_reference(self, fake_lock, fake_unlock):
        message = self.checkin_failure(TABL_REFERENCE_XML)

        self.assertEqual(message, f'Unsupported reference type of the field OBJECT of structure {TABL_NAME.lower()}')

    def test_checkin_tabl_unknown_datatype(self, fake_lock, fake_unlock):
        message = self.checkin_failure(TABL_UNKNOWN_DATATYPE_XML)

        self.assertEqual(message, f'Unsupported data type "UTCL" of the field STAMP of structure {TABL_NAME.lower()}')

    def test_checkin_tabl_append(self, fake_lock, fake_unlock):
        message = self.checkin_failure(TABL_APPEND_XML)

        self.assertEqual(message, f'Unsupported field .APPEND of structure {TABL_NAME.lower()}')

    def test_checkin_tabl_unknown_reference(self, fake_lock, fake_unlock):
        message = self.checkin_failure(TABL_UNKNOWN_REFERENCE_XML)

        self.assertEqual(message, f'Cannot determine whether the field WRBTR of structure {TABL_NAME.lower()}'
                                  ' refers to a currency or to a unit')

    def test_checkin_tabl_foreign_keys(self, fake_lock, fake_unlock):
        message = self.checkin_failure(TABL_FOREIGN_KEYS_XML)

        self.assertEqual(message, f'Unsupported contents of TABL {TABL_NAME.lower()}: Got unexpected tag DD08V_TABLE')


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestTableHandlerCheckinTable(unittest.TestCase, PatcherTestCase):

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
        self.observer = Mock(spec=RepositoryObserver)
        self.handler = TableHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('tabl', DBTAB_NAME.lower(), f'./src/{DBTAB_NAME.lower()}.tabl.xml',
                                   [], self.package, self.handler)

    def checkin(self, abapgit_xml, responses):
        connection = Connection(responses, user='DEVELOPER')

        with patch('sap.platform.abap.abapgit.tabl.open', mock_open(read_data=abapgit_xml)) as fake_open:
            result = self.checkin_object(connection, self.repo_obj)

        fake_open.assert_called_once_with(self.repo_obj.path, encoding='utf-8')

        return (connection, result)

    def checkin_failure(self, abapgit_xml):
        connection = Connection([], user='DEVELOPER')

        with patch('sap.platform.abap.abapgit.tabl.open', mock_open(read_data=abapgit_xml)), \
             self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin_object(connection, self.repo_obj)

        self.assertEqual(connection.execs, [])

        return caught.exception.message

    def responses_ok(self):
        return [
            Response(text='', status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
            Response(text=TABLE_SETTINGS_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, source_code, settings_request_xml):
        table_uri = f'/sap/bc/adt/ddic/tables/{DBTAB_NAME.lower()}'
        settings_uri = f'/sap/bc/adt/ddic/db/settings/{DBTAB_NAME.lower()}'

        self.assertEqual(connection.mock_methods(), [
            ('POST', '/sap/bc/adt/ddic/tables'),
            ('PUT', f'{table_uri}/source/main'),
            ('GET', settings_uri),
            ('PUT', settings_uri),
        ])

        self.maxDiff = None
        self.assertEqual(connection.execs[1].headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(connection.execs[1].params, {'lockHandle': 'lock_handle'})
        self.assertEqual(connection.execs[1].body.decode('utf-8'), source_code)

        self.assertEqual(connection.execs[3].headers,
                         {'Content-Type': 'application/vnd.sap.adt.table.settings.v2+xml; charset=utf-8'})
        self.assertEqual(connection.execs[3].params, {'lockHandle': 'lock_handle'})
        self.assertEqual(connection.execs[3].body.decode('utf-8'), settings_request_xml)

    def checkin_object(self, connection, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj, self.observer)
        context = CheckinContext(connection, '$TMP', corrnr, check_before_save, self.observer)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_dbtab(self, fake_lock, fake_unlock):
        connection, result = self.checkin(DBTAB_XML, self.responses_ok())

        self.assertEqual(connection.execs[0].body.decode('utf-8'), DBTAB_ADT_NEW_OBJECT_REQUEST_XML)
        self.assert_requests(connection, DBTAB_SOURCE_CODE, DBTAB_SETTINGS_REQUEST_XML)
        self.assertEqual(fake_lock.call_count, 2)
        self.assertEqual(fake_unlock.call_count, 2)

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, DBTAB_NAME)
        self.assertEqual(result.abap_objects[0].objtype.code, 'TABL/DT')
        self.assertEqual(result.used_files, [])

        self.assertEqual(self.observer.mock_calls, [
            call.creating('Table', DBTAB_NAME.lower()),
            call.writing('Table', DBTAB_NAME.lower()),
            call.writing('Technical Settings', DBTAB_NAME.lower()),
        ])

    def test_checkin_dbtab_full(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(DBTAB_FULL_XML, self.responses_ok())

        self.assert_requests(connection, DBTAB_FULL_SOURCE_CODE, DBTAB_FULL_SETTINGS_REQUEST_XML)

    def test_checkin_dbtab_generic_buffering(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(DBTAB_GENERIC_XML, self.responses_ok())

        self.assert_requests(connection, DBTAB_GENERIC_SOURCE_CODE, DBTAB_GENERIC_SETTINGS_REQUEST_XML)

    def test_checkin_dbtab_text_language(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(DBTAB_GENERIC_XML.replace(
            '     <MASK>  STRG</MASK>\n', '     <MASK>  STRG</MASK>\n     <LANGUFLAG>X</LANGUFLAG>\n'),
            self.responses_ok())

        self.assert_requests(connection,
                             DBTAB_GENERIC_SOURCE_CODE.replace('  value ', '  @AbapCatalog.textLanguage\n  value '),
                             DBTAB_GENERIC_SETTINGS_REQUEST_XML)

    def test_checkin_dbtab_foreign_keys(self, fake_lock, fake_unlock):
        message = self.checkin_failure(DBTAB_FOREIGN_KEYS_XML)

        self.assertEqual(message, f'Unsupported contents of TABL {DBTAB_NAME.lower()}: Got unexpected tag DD08V_TABLE')

    def test_checkin_dbtab_unknown_data_maintenance(self, fake_lock, fake_unlock):
        message = self.checkin_failure(DBTAB_FULL_XML.replace('<MAINFLAG>X</MAINFLAG>', '<MAINFLAG>Q</MAINFLAG>'))

        self.assertEqual(message, f'Unsupported data maintenance "Q" of table {DBTAB_NAME.lower()}')

    def test_checkin_dbtab_release_dependent_settings(self, fake_lock, fake_unlock):
        abapgit_xml = DBTAB_XML.replace('   </DD09L>', '''    <ROWORCOLST>R</ROWORCOLST>
    <SHARINGTYPE>1</SHARINGTYPE>
    <LOAD_UNIT>P</LOAD_UNIT>
   </DD09L>''')
        self.assertNotEqual(abapgit_xml, DBTAB_XML)

        connection, _ = self.checkin(abapgit_xml, self.responses_ok())

        settings_request_xml = DBTAB_SETTINGS_REQUEST_XML \
            .replace('<ts:storageType>C</ts:storageType>', '<ts:storageType>R</ts:storageType>') \
            .replace('<ts:sharingType></ts:sharingType>', '<ts:sharingType>1</ts:sharingType>') \
            .replace('<ts:loadUnit></ts:loadUnit>', '<ts:loadUnit>P</ts:loadUnit>')
        self.assert_requests(connection, DBTAB_SOURCE_CODE, settings_request_xml)

    def test_checkin_dbtab_key_include(self, fake_lock, fake_unlock):
        message = self.checkin_failure(DBTAB_KEY_INCLUDE_XML)

        self.assertEqual(message, f'Unsupported key include ZZS_CRITERIA of table {DBTAB_NAME.lower()}')


if __name__ == '__main__':
    unittest.main()
