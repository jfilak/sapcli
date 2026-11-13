#!/usr/bin/env python3

import os
import unittest
from unittest.mock import mock_open, patch

import sap.adt
import sap.errors
import sap.fileformat.abapgit.ttyp
from sap.adt.errors import ExceptionCheckinFailure
from sap.fileformat import CheckinContext, ObjectHandler, RepoObject, RepoPackage
from sap.fileformat.abapgit.ttyp import TableTypeHandler

from mock import Connection, ConsoleOutputTestCase, PatcherTestCase, Response
from fixtures_sap_fileformat_abapgit_ttyp import TTYP_STANDARD_XML, TTYP_SORTED_XML, TTYP_PREDEFINED_XML, \
    TTYP_SECONDARY_KEYS_XML, TTYP_RANGE_XML, TTYP_SORTED_ABAPGIT_XML, TTYP_PREDEFINED_ABAPGIT_XML, \
    TTYP_STRING_ABAPGIT_XML, TTYP_SECONDARY_KEYS_ABAPGIT_XML
from fixtures_sap_adt_tabletype import TABLE_TYPE_NAME, TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML, \
    TABLE_TYPE_ADT_NEW_OBJECT_REQUEST_XML, TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML, \
    TABLE_TYPE_ADT_DEFINE_SORTED_REQUEST_XML, TABLE_TYPE_ADT_ALREADY_EXISTS_RESPONSE_XML, \
    TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML, TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML, \
    TABLE_TYPE_ADT_GET_RANGE_RESPONSE_XML, TABLE_TYPE_ADT_GET_STRING_RESPONSE_XML


class TestTableTypeHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = TableTypeHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'ttyp')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.TableType.OBJTYPE.code,))

    def test_locate(self):
        handler = TableTypeHandler()
        repo_obj = RepoObject('ttyp', 'zttyp', './src/zttyp.ttyp.xml', [],
                              RepoPackage('./src', './src/package.devc.xml', None), handler)

        self.assertIsNone(handler.locate(repo_obj, 'source/main', 1))


class TestTableTypeHandlerCheckout(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = TableTypeHandler()

    def checkout(self, adt_response_xml, destdir=None):
        connection = Connection([Response(text=adt_response_xml, status_code=200, headers={})])

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            self.handler.checkout(connection, 'TTYP/DA', TABLE_TYPE_NAME, destdir)

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


TTYP_MIME = 'application/vnd.sap.adt.tabletype.v1+xml; charset=utf-8'


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestTableTypeHandlerCheckin(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = TableTypeHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('ttyp', TABLE_TYPE_NAME.lower(), f'./src/{TABLE_TYPE_NAME.lower()}.ttyp.xml', [],
                                   self.package, self.handler)

    def checkin(self, abapgit_xml, responses):
        connection = Connection(responses, user='DEVELOPER')

        with patch('sap.fileformat.abapgit.ttyp.open', mock_open(read_data=abapgit_xml)) as fake_open:
            result = self.handler.checkin(CheckinContext(connection, '$TMP', None, False), self.repo_obj,
                                          self.handler.prepare(self.repo_obj))

        fake_open.assert_called_once_with(self.repo_obj.path, encoding='utf-8')

        return (connection, result)

    def responses_ok(self):
        return [
            Response(text='', status_code=200, headers={}),
            Response(text=TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML, status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, define_request_xml):
        self.assertEqual(len(connection.execs), 3)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/tabletypes')
        self.assertEqual(connection.execs[0].body, bytes(TABLE_TYPE_ADT_NEW_OBJECT_REQUEST_XML, 'utf-8'))

        self.assertEqual(connection.execs[1].method, 'GET')
        self.assertEqual(connection.execs[1].adt_uri, f'/sap/bc/adt/ddic/tabletypes/{TABLE_TYPE_NAME.lower()}')

        self.assertEqual(connection.execs[2].method, 'PUT')
        self.assertEqual(connection.execs[2].adt_uri, f'/sap/bc/adt/ddic/tabletypes/{TABLE_TYPE_NAME.lower()}')
        self.assertEqual(connection.execs[2].headers, {'Content-Type': TTYP_MIME})
        self.assertEqual(connection.execs[2].params, {'lockHandle': 'lock_handle'})
        self.maxDiff = None
        self.assertEqual(connection.execs[2].body.decode('utf-8'), define_request_xml)

    def test_checkin_ttyp_standard(self, fake_lock, fake_unlock):
        connection, result = self.checkin(TTYP_STANDARD_XML, self.responses_ok())

        self.assert_requests(connection, TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, TABLE_TYPE_NAME)
        self.assertEqual(result.used_files, [])

        self.assertConsoleContents(self.console, stdout=f'''Creating Table Type: {TABLE_TYPE_NAME.lower()}
Writing Table Type: {TABLE_TYPE_NAME.lower()}
''')

    def test_checkin_ttyp_sorted_key_components(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TTYP_SORTED_XML, self.responses_ok())

        self.assert_requests(connection, TABLE_TYPE_ADT_DEFINE_SORTED_REQUEST_XML)

    def test_checkin_ttyp_predefined(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TTYP_PREDEFINED_XML, self.responses_ok())

        self.assertEqual(len(connection.execs), 3)
        self.assertIn('''<ttyp:rowType>
<ttyp:typeKind>predefinedAbapType</ttyp:typeKind>
<ttyp:typeName></ttyp:typeName>
<ttyp:builtInType>
<ttyp:dataType>STRG</ttyp:dataType>
<ttyp:length>0</ttyp:length>
<ttyp:decimals>0</ttyp:decimals>
</ttyp:builtInType>
<ttyp:rangeType></ttyp:rangeType>
</ttyp:rowType>''', connection.execs[2].body.decode('utf-8'))

    def test_checkin_ttyp_secondary_keys_skipped(self, fake_lock, fake_unlock):
        connection, _ = self.checkin(TTYP_SECONDARY_KEYS_XML, self.responses_ok())

        self.assert_requests(connection, TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML)
        self.assertEqual(self.console.caperr,
                         f'Skipping unsupported secondary keys of {TABLE_TYPE_NAME.lower()}\n')

    def test_checkin_ttyp_already_exists(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[0] = Response(text=TABLE_TYPE_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                                headers={'content-type': 'application/xml'})

        connection, _ = self.checkin(TTYP_STANDARD_XML, responses)

        self.assert_requests(connection, TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML)

    def test_checkin_ttyp_range_not_supported(self, fake_lock, fake_unlock):
        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin(TTYP_RANGE_XML, [])

        self.assertEqual(str(caught.exception),
                         f'Unsupported row type of table type {TABLE_TYPE_NAME.lower()}:'
                         ' only dictionary and predefined types are supported')
        fake_lock.assert_not_called()

    def test_checkin_ttyp_unknown_access_mode(self, fake_lock, fake_unlock):
        abapgit_xml = TTYP_STANDARD_XML.replace('<ACCESSMODE>T</ACCESSMODE>', '<ACCESSMODE>Q</ACCESSMODE>')

        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin(abapgit_xml, [])

        self.assertEqual(str(caught.exception),
                         f'Unsupported ACCESSMODE "Q" of table type {TABLE_TYPE_NAME.lower()}')


if __name__ == '__main__':
    unittest.main()
