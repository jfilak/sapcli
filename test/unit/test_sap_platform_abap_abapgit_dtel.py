#!/usr/bin/env python3

import os
import re
import unittest

import sap.platform.abap.localrepository
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import sap.adt
import sap.errors
import sap.platform.abap.abapgit.dtel
from sap.adt.errors import ExceptionCheckinFailure
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import CheckinContext, ObjectHandler, RepoObject, RepoPackage, RepositoryObserver
from sap.platform.abap.abapgit.dtel import DataElementHandler

from mock import Connection, PatcherTestCase, Response, StringIOFile
from fixtures_sap_platform_abap_abapgit_dtel import DTEL_ABAPGIT_XML, DTEL_DOMAIN_ABAPGIT_XML, DTEL_STRING_ABAPGIT_XML, \
    DTEL_XML, DTEL_DOMAIN_XML, DTEL_TRANSLATIONS_XML, DTEL_REFERENCE_XML
from fixtures_adt_dataelement import DATA_ELEMENT_ADT_NEW_OBJECT_REQUEST_XML, \
    DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML, DATA_ELEMENT_ADT_GET_DOMAIN_RESPONSE_XML, \
    DATA_ELEMENT_ADT_GET_STRING_RESPONSE_XML, DATA_ELEMENT_ADT_DEFINE_SAMPLE_REQUEST_XML, DATA_ELEMENT_NEW_NAME, \
    DATA_ELEMENT_ADT_DEFINE_DOMAIN_REQUEST_XML, DATA_ELEMENT_ADT_ALREADY_EXISTS_RESPONSE_XML, \
    DATA_ELEMENT_ADT_GET_NEW_RESPONSE_XML


class TestDataElementHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = DataElementHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'dtel')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.DataElement.OBJTYPE.code,))


class TestDataElementHandlerLocate(unittest.TestCase):

    def test_no_source_code(self):
        handler = DataElementHandler()
        repo_obj = RepoObject('dtel', 'zfoo', './src/zfoo.dtel.xml', [],
                              RepoPackage('./src', './src/package.devc.xml', None), handler)

        self.assertIsNone(handler.locate(repo_obj, 'source/main', 1))


class TestDataElementHandlerCheckout(unittest.TestCase, PatcherTestCase):

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
        self.handler = DataElementHandler()

    def checkout(self, adt_response_xml, destdir=None):
        connection = Connection([Response(text=adt_response_xml, status_code=200, headers={})])

        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open:
            self.handler.checkout(connection, 'DTEL/DE', DATA_ELEMENT_NEW_NAME, destdir, self.observer)

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
        self.assertEqual(self.observer.mock_calls, [
            call.checking_out(DATA_ELEMENT_NEW_NAME),
            call.file_written(f'{DATA_ELEMENT_NEW_NAME.lower()}.dtel.xml'),
        ])

    def test_checkout_dtel_domain(self):
        fake_open = self.checkout(DATA_ELEMENT_ADT_GET_DOMAIN_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, DTEL_DOMAIN_ABAPGIT_XML)

    def test_checkout_dtel_ddic_data_type(self):
        fake_open = self.checkout(DATA_ELEMENT_ADT_GET_STRING_RESPONSE_XML)

        self.assert_wrote_abapgit_file(fake_open, DTEL_STRING_ABAPGIT_XML)

    def test_checkout_dtel_reference_not_supported(self):
        adt_response_xml = DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML.replace(
            '<dtel:typeKind>predefinedAbapType</dtel:typeKind>', '<dtel:typeKind>refToClifType</dtel:typeKind>')

        with self.assertRaises(sap.platform.abap.localrepository.UnsupportedContent) as caught:
            self.checkout(adt_response_xml)

        self.assertEqual(str(caught.exception),
                         f'Unsupported type of data element {DATA_ELEMENT_NEW_NAME}: refToClifType')

    def test_checkout_dtel_destdir(self):
        fake_open = self.checkout(DATA_ELEMENT_ADT_GET_SAMPLE_RESPONSE_XML, destdir='src')

        fake_open.assert_called_once_with(os.path.join('src', f'{DATA_ELEMENT_NEW_NAME.lower()}.dtel.xml'), 'w',
                                          encoding='utf8')


DTEL_MIME = 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestDataElementHandlerCheckin(unittest.TestCase, PatcherTestCase):

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
        self.handler = DataElementHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('dtel', DATA_ELEMENT_NEW_NAME.lower(), f'./src/{DATA_ELEMENT_NEW_NAME.lower()}.dtel.xml',
                                   [], self.package, self.handler)

    def checkin(self, abapgit_xml, responses):
        connection = Connection(responses, user='DEVELOPER')

        with patch('sap.platform.abap.abapgit.dtel.open', mock_open(read_data=abapgit_xml)) as fake_open:
            result = self.checkin_object(connection, self.repo_obj)

        fake_open.assert_called_once_with(self.repo_obj.path, encoding='utf-8')

        return (connection, result)

    def responses_ok(self):
        return [
            Response(text='', status_code=201, headers={}),
            Response(text=DATA_ELEMENT_ADT_GET_NEW_RESPONSE_XML, status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, define_request_xml, new_object_request_xml=DATA_ELEMENT_ADT_NEW_OBJECT_REQUEST_XML):
        uri = f'/sap/bc/adt/ddic/dataelements/{DATA_ELEMENT_NEW_NAME.lower()}'

        self.assertEqual(len(connection.execs), 3)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/dataelements')
        self.assertEqual(connection.execs[0].body.decode('utf-8'), new_object_request_xml)

        self.assertEqual(connection.execs[1].method, 'GET')
        self.assertEqual(connection.execs[1].adt_uri, uri)

        self.assertEqual(connection.execs[2].method, 'PUT')
        self.assertEqual(connection.execs[2].adt_uri, uri)
        self.assertEqual(connection.execs[2].headers, {'Content-Type': DTEL_MIME})
        self.assertEqual(connection.execs[2].params, {'lockHandle': 'lock_handle'})
        self.maxDiff = None
        self.assertEqual(connection.execs[2].body.decode('utf-8'), define_request_xml)

    def checkin_object(self, connection, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj, self.observer)
        context = CheckinContext(connection, '$TMP', corrnr, check_before_save, self.observer)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_dtel_sample(self, fake_lock, fake_unlock):
        connection, result = self.checkin(DTEL_XML, self.responses_ok())

        self.assert_requests(connection, DATA_ELEMENT_ADT_DEFINE_SAMPLE_REQUEST_XML)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, DATA_ELEMENT_NEW_NAME)
        self.assertEqual(result.used_files, [])

        self.assertEqual(self.observer.mock_calls, [
            call.creating('Data Element', DATA_ELEMENT_NEW_NAME.lower()),
            call.writing('Data Element', DATA_ELEMENT_NEW_NAME.lower()),
        ])

    def test_checkin_dtel_domain(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[1] = Response(text=DATA_ELEMENT_ADT_GET_NEW_RESPONSE_XML.replace('adtcore:description="testing"',
                                                                                  'adtcore:description="Old"'),
                                status_code=200, headers={})

        connection, _ = self.checkin(DTEL_DOMAIN_XML, responses)

        new_object_request_xml = DATA_ELEMENT_ADT_NEW_OBJECT_REQUEST_XML.replace('adtcore:description="testing"',
                                                                                 'adtcore:description="Domain &amp; labels"')
        self.assert_requests(connection, DATA_ELEMENT_ADT_DEFINE_DOMAIN_REQUEST_XML, new_object_request_xml)

    def test_checkin_dtel_domain_without_refkind(self, fake_lock, fake_unlock):
        abapgit_xml = DTEL_DOMAIN_XML.replace('    <REFKIND>D</REFKIND>\n', '')
        responses = self.responses_ok()
        responses[1] = Response(text=DATA_ELEMENT_ADT_GET_NEW_RESPONSE_XML.replace('adtcore:description="testing"',
                                                                                  'adtcore:description="Old"'),
                                status_code=200, headers={})

        connection, _ = self.checkin(abapgit_xml, responses)

        new_object_request_xml = DATA_ELEMENT_ADT_NEW_OBJECT_REQUEST_XML.replace('adtcore:description="testing"',
                                                                                 'adtcore:description="Domain &amp; labels"')
        self.assert_requests(connection, DATA_ELEMENT_ADT_DEFINE_DOMAIN_REQUEST_XML, new_object_request_xml)

    def test_checkin_dtel_ddic_data_type(self, fake_lock, fake_unlock):
        abapgit_xml = DTEL_XML.replace('<DATATYPE>CHAR</DATATYPE>', '<DATATYPE>D34N</DATATYPE>')
        define_request_xml = DATA_ELEMENT_ADT_DEFINE_SAMPLE_REQUEST_XML.replace('<dtel:dataType>CHAR</dtel:dataType>',
                                                                               '<dtel:dataType>DECFLOAT34</dtel:dataType>')

        connection, _ = self.checkin(abapgit_xml, self.responses_ok())

        self.assert_requests(connection, define_request_xml)

    def test_checkin_dtel_already_exists(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[0] = Response(text=DATA_ELEMENT_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                                headers={'content-type': 'application/xml'})

        connection, _ = self.checkin(DTEL_XML, responses)

        self.assert_requests(connection, DATA_ELEMENT_ADT_DEFINE_SAMPLE_REQUEST_XML)

    def test_checkin_dtel_already_exists_in_other_package(self, fake_lock, fake_unlock):
        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin(DTEL_XML, [
                Response(text=DATA_ELEMENT_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                         headers={'content-type': 'application/xml'}),
                Response(text=DATA_ELEMENT_ADT_GET_NEW_RESPONSE_XML.replace('adtcore:name="$TMP"', 'adtcore:name="ZPROD"'),
                         status_code=200, headers={}),
            ])

        self.assertEqual(str(caught.exception), f'Cannot checkin data element {DATA_ELEMENT_NEW_NAME} into package $TMP.'
                                                ' It already exists in package ZPROD.')
        fake_lock.assert_not_called()

    def test_checkin_dtel_translations_not_supported(self, fake_lock, fake_unlock):
        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin(DTEL_TRANSLATIONS_XML, [])

        self.assertEqual(str(caught.exception),
                         f'Unsupported contents of data element {DATA_ELEMENT_NEW_NAME.lower()}: '
                         'Got unexpected tag I18N_LANGS')
        fake_lock.assert_not_called()

    def test_checkin_dtel_reference_not_supported(self, fake_lock, fake_unlock):
        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin(DTEL_REFERENCE_XML, [])

        self.assertEqual(str(caught.exception),
                         f'Unsupported type of data element {DATA_ELEMENT_NEW_NAME.lower()}: REFKIND=R')
        fake_lock.assert_not_called()


class TestDDICOutputLength(unittest.TestCase):

    def test_ddic_output_length_char(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('CHAR', '000001', '000000'), 1)

    def test_ddic_output_length_numc(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('NUMC', '000010', '000000'), 10)

    def test_ddic_output_length_raw(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('RAW', '000016', '000000'), 32)

    def test_ddic_output_length_lraw(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('LRAW', '000300', '000000'), 300)

    def test_ddic_output_length_dec_without_decimals(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('DEC', '000005', '000000'), 6)

    def test_ddic_output_length_dec_with_decimals(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('DEC', '000015', '000002'), 20)

    def test_ddic_output_length_dec_only_decimals(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('DEC', '000002', '000002'), 4)

    def test_ddic_output_length_dec_single_digit(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('DEC', '000001', '000000'), 1)

    def test_ddic_output_length_curr(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('CURR', '000013', '000002'), 17)

    def test_ddic_output_length_quan(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('QUAN', '000013', '000003'), 17)

    def test_ddic_output_length_int4(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('INT4', '000010', '000000'), 11)

    def test_ddic_output_length_dats(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('DATS', '000008', '000000'), 10)

    def test_ddic_output_length_string(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('STRG', '000000', '000000'), 0)

    def test_ddic_output_length_sstring(self):
        self.assertEqual(sap.platform.abap.abapgit.dtel.ddic_output_length('SSTR', '000020', '000000'), 0)

    def test_ddic_output_length_unknown(self):
        self.assertIsNone(sap.platform.abap.abapgit.dtel.ddic_output_length('D16D', '000010', '000002'))


if __name__ == '__main__':
    unittest.main()
