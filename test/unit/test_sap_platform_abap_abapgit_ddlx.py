#!/usr/bin/env python3

import os
import re
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import sap.adt
import sap.errors
import sap.platform.abap.abapgit.ddlx
from sap.adt.errors import ExceptionCheckinFailure
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import CheckinContext, ObjectHandler, RepoObject, RepoPackage, RepositoryObserver
from sap.platform.abap.abapgit.ddlx import MetadataExtensionHandler

from mock import Connection, PatcherTestCase, Response, StringIOFile
from fixtures_sap_platform_abap_abapgit_ddlx import DDLX_SOURCE_CODE, DDLX_ABAPGIT_XML, \
    DDLX_ADT_NEW_OBJECT_REQUEST_XML, DDLX_NAME, DDLX_XML, DDLX_ABAP_LANGUAGE_VERSION_XML, \
    DDLX_ADT_ALREADY_EXISTS_RESPONSE_XML, DDLX_ADT_GET_RESPONSE_XML


class TestMetadataExtensionHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = MetadataExtensionHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'ddlx')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.MetadataExtension.OBJTYPE.code,))


class TestMetadataExtensionHandlerLocate(unittest.TestCase):

    def setUp(self):
        self.handler = MetadataExtensionHandler()
        package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('ddlx', 'zfoo', './src/zfoo.ddlx.xml',
                                   ['./src/zfoo.ddlx.asddlxs'], package, self.handler)

    def test_main(self):
        self.assertEqual(self.handler.locate(self.repo_obj, 'source/main', 12),
                         ('./src/zfoo.ddlx.asddlxs', 12))

    def test_unknown_part(self):
        self.assertIsNone(self.handler.locate(self.repo_obj, 'includes/testclasses', 1))

    def test_file_not_in_repository(self):
        self.repo_obj.files.remove('./src/zfoo.ddlx.asddlxs')

        self.assertIsNone(self.handler.locate(self.repo_obj, 'source/main', 12))


class TestMetadataExtensionHandlerCheckout(unittest.TestCase, PatcherTestCase):

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
        self.handler = MetadataExtensionHandler()

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

        with patch('sap.platform.abap.abapgit.files.open', side_effect=open_file):
            self.handler.checkout(connection, 'DDLX/EX', DDLX_NAME, destdir, self.observer)

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
        self.assertEqual(self.observer.mock_calls, [
            call.checking_out(DDLX_NAME),
            call.file_written(f'{DDLX_NAME.lower()}.ddlx.asddlxs'),
            call.file_written(f'{DDLX_NAME.lower()}.ddlx.xml'),
        ])

    def test_checkout_ddlx_destdir(self):
        written = self.checkout(destdir='src')

        self.assertEqual(list(written), [os.path.join('src', f'{DDLX_NAME.lower()}.ddlx.asddlxs'),
                                         os.path.join('src', f'{DDLX_NAME.lower()}.ddlx.xml')])


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestMetadataExtensionHandlerCheckin(unittest.TestCase, PatcherTestCase):

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
        self.handler = MetadataExtensionHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.source_file = f'./src/{DDLX_NAME.lower()}.ddlx.asddlxs'
        self.repo_obj = RepoObject('ddlx', DDLX_NAME.lower(), f'./src/{DDLX_NAME.lower()}.ddlx.xml',
                                   [self.source_file], self.package, self.handler)

        self.fake_open = self.patch('sap.platform.abap.abapgit.cds.open')
        self.fake_open.side_effect = [StringIOFile(DDLX_XML), StringIOFile(DDLX_SOURCE_CODE)]

    def responses_ok(self):
        return [
            Response(text='', status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, create_params=None, write_params=None):
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/ddlx/sources')
        self.assertEqual(connection.execs[0].params, create_params)
        self.maxDiff = None
        self.assertEqual(connection.execs[0].body.decode('utf-8'), DDLX_ADT_NEW_OBJECT_REQUEST_XML)

        self.assertEqual(connection.execs[1].method, 'PUT')
        self.assertEqual(connection.execs[1].adt_uri, f'/sap/bc/adt/ddic/ddlx/sources/{DDLX_NAME.lower()}/source/main')
        self.assertEqual(connection.execs[1].headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(connection.execs[1].params, write_params or {'lockHandle': 'lock_handle'})
        self.assertEqual(connection.execs[1].body.decode('utf-8'), DDLX_SOURCE_CODE)

    def checkin_object(self, connection, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj, self.observer)
        context = CheckinContext(connection, '$TMP', corrnr, check_before_save, self.observer)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_ddlx(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        result = self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(self.fake_open.call_args_list, [call(self.repo_obj.path, encoding='utf-8'),
                                                         call(self.source_file, 'r', encoding='utf-8')])

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, DDLX_NAME)
        self.assertEqual(result.used_files, [self.source_file])

        self.assertEqual(self.observer.mock_calls, [
            call.creating('Metadata Extension', DDLX_NAME.lower()),
            call.writing('Metadata Extension', DDLX_NAME.lower()),
        ])

    def test_checkin_ddlx_abap_language_version(self, fake_lock, fake_unlock):
        self.fake_open.side_effect = [StringIOFile(DDLX_ABAP_LANGUAGE_VERSION_XML), StringIOFile(DDLX_SOURCE_CODE)]
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)

    def test_checkin_ddlx_with_corrnr(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj, corrnr='420')

        self.assert_requests(connection, create_params={'corrNr': '420'},
                             write_params={'lockHandle': 'lock_handle', 'corrNr': '420'})

    def test_checkin_ddlx_already_exists(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[0] = Response(text=DDLX_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                                headers={'content-type': 'application/xml'})
        connection = Connection(responses, user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)

    def test_checkin_ddlx_no_source_file(self, fake_lock, fake_unlock):
        # Old abapGit versions stored the source code in the XML file
        repo_obj = self.repo_obj._replace(files=[])
        connection = Connection([], user='DEVELOPER')

        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin_object(connection, repo_obj)

        self.assertEqual(str(caught.exception), f'No source file for metadata extension {DDLX_NAME.lower()}')
        self.assertEqual(connection.execs, [])
        self.fake_open.assert_not_called()

    def test_checkin_ddlx_check_before_save(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        with patch('sap.adt.checks.write_source') as fake_write:
            result = self.checkin_object(connection, self.repo_obj, check_before_save=True)

        fake_write.assert_called_once_with(DDLX_SOURCE_CODE, result.abap_objects[0], corrnr=None,
                                           source_label=self.source_file, check_before_save=True)


if __name__ == '__main__':
    unittest.main()
