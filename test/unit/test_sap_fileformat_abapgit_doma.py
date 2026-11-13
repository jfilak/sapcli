#!/usr/bin/env python3

import os
import re
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import sap.adt
import sap.errors
import sap.fileformat.abapgit.doma
from sap.adt.errors import ExceptionCheckinFailure
from sap.errors import SAPCliError
from sap.fileformat import CheckinContext, ObjectHandler, RepoObject, RepoPackage
from sap.fileformat.abapgit.doma import DomainHandler

from mock import Connection, ConsoleOutputTestCase, PatcherTestCase, Response, StringIOFile
from fixtures_sap_fileformat_abapgit_doma import DOMA_ABAPGIT_XML, DOMA_ALL_FIELDS_ABAPGIT_XML, \
    DOMA_RAWSTRING_ABAPGIT_XML, DOMA_XML, DOMA_ALL_FIELDS_XML, DOMA_TRANSLATIONS_XML
from fixtures_adt_domain import DOMAIN_ADT_GET_SAMPLE_RESPONSE_XML, DOMAIN_ADT_GET_ALL_FIELDS_RESPONSE_XML, \
    DOMAIN_ADT_GET_RAWSTRING_RESPONSE_XML, DOMAIN_ADT_NEW_OBJECT_REQUEST_XML, DOMAIN_ADT_DEFINE_SAMPLE_REQUEST_XML, \
    DOMAIN_NEW_NAME, DOMAIN_ADT_DEFINE_ALL_FIELDS_REQUEST_XML, DOMAIN_ADT_ALREADY_EXISTS_RESPONSE_XML, \
    DOMAIN_ADT_GET_NEW_RESPONSE_XML


class TestDomainHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = DomainHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'doma')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.Domain.OBJTYPE.code,))


class TestDomainHandlerLocate(unittest.TestCase):

    def test_no_source_code(self):
        handler = DomainHandler()
        repo_obj = RepoObject('doma', 'zfoo', './src/zfoo.doma.xml', [],
                              RepoPackage('./src', './src/package.devc.xml', None), handler)

        self.assertIsNone(handler.locate(repo_obj, 'source/main', 1))


class TestDomainHandlerCheckout(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = DomainHandler()

    def checkout(self, adt_response_xml, destdir=None):
        connection = Connection([Response(text=adt_response_xml, status_code=200, headers={})])

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            self.handler.checkout(connection, 'DOMA/DD', DOMAIN_NEW_NAME, destdir)

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


DOMA_MIME = 'application/vnd.sap.adt.domains.v2+xml; charset=utf-8'


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestDomainHandlerCheckin(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = DomainHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('doma', DOMAIN_NEW_NAME.lower(), f'./src/{DOMAIN_NEW_NAME.lower()}.doma.xml',
                                   [], self.package, self.handler)

    def checkin(self, abapgit_xml, responses):
        connection = Connection(responses, user='DEVELOPER')

        with patch('sap.fileformat.abapgit.doma.open', mock_open(read_data=abapgit_xml)) as fake_open:
            result = self.checkin_object(connection, self.repo_obj)

        fake_open.assert_called_once_with(self.repo_obj.path, encoding='utf-8')

        return (connection, result)

    def responses_ok(self):
        return [
            Response(text='', status_code=201, headers={}),
            Response(text=DOMAIN_ADT_GET_NEW_RESPONSE_XML, status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, define_request_xml):
        self.assertEqual(len(connection.execs), 3)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/domains')
        self.assertEqual(connection.execs[0].body.decode('utf-8'), DOMAIN_ADT_NEW_OBJECT_REQUEST_XML)

        self.assertEqual(connection.execs[1].method, 'GET')
        self.assertEqual(connection.execs[1].adt_uri, f'/sap/bc/adt/ddic/domains/{DOMAIN_NEW_NAME.lower()}')

        self.assertEqual(connection.execs[2].method, 'PUT')
        self.assertEqual(connection.execs[2].adt_uri, f'/sap/bc/adt/ddic/domains/{DOMAIN_NEW_NAME.lower()}')
        self.assertEqual(connection.execs[2].headers, {'Content-Type': DOMA_MIME})
        self.assertEqual(connection.execs[2].params, {'lockHandle': 'lock_handle'})
        self.maxDiff = None
        self.assertEqual(connection.execs[2].body.decode('utf-8'), define_request_xml)

    def checkin_object(self, connection, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj)
        context = CheckinContext(connection, '$TMP', corrnr, check_before_save)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_doma_sample(self, fake_lock, fake_unlock):
        connection, result = self.checkin(DOMA_XML, self.responses_ok())

        self.assert_requests(connection, DOMAIN_ADT_DEFINE_SAMPLE_REQUEST_XML)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, DOMAIN_NEW_NAME)
        self.assertEqual(result.used_files, [])

        self.assertConsoleContents(self.console, stdout=f'''Creating Domain: {DOMAIN_NEW_NAME.lower()}
Writing Domain: {DOMAIN_NEW_NAME.lower()}
''')

    def test_checkin_doma_all_fields(self, fake_lock, fake_unlock):
        abapgit_xml = DOMA_ALL_FIELDS_XML.replace('<DDTEXT>All fields</DDTEXT>', '<DDTEXT>Testing</DDTEXT>')
        define_request_xml = DOMAIN_ADT_DEFINE_ALL_FIELDS_REQUEST_XML.replace('adtcore:description="All fields"',
                                                                            'adtcore:description="Testing"')

        connection, _ = self.checkin(abapgit_xml, self.responses_ok())

        self.assert_requests(connection, define_request_xml)

    def test_checkin_doma_already_exists(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[0] = Response(text=DOMAIN_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                                headers={'content-type': 'application/xml'})
        responses[1] = Response(text=DOMAIN_ADT_GET_NEW_RESPONSE_XML.replace('adtcore:description="Testing"',
                                                                            'adtcore:description="Old"'),
                                status_code=200, headers={})

        connection, _ = self.checkin(DOMA_XML, responses)

        self.assert_requests(connection, DOMAIN_ADT_DEFINE_SAMPLE_REQUEST_XML)

    def test_checkin_doma_translations_not_supported(self, fake_lock, fake_unlock):
        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin(DOMA_TRANSLATIONS_XML, [])

        self.assertEqual(str(caught.exception),
                         f'Unsupported contents of domain {DOMAIN_NEW_NAME.lower()}: Got unexpected tag I18N_LANGS')
        fake_lock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
