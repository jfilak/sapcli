#!/usr/bin/env python3

import os
import re
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import sap.adt
import sap.errors
import sap.fileformat.abapgit.ddls
from sap.adt.errors import ExceptionCheckinFailure
from sap.errors import SAPCliError
from sap.fileformat import CheckinContext, ObjectHandler, RepoObject, RepoPackage
from sap.fileformat.abapgit.ddls import DataDefinitionHandler

from mock import Connection, ConsoleOutputTestCase, PatcherTestCase, Response, StringIOFile
from fixtures_sap_fileformat_abapgit_ddls import DDLS_SOURCE_CODE, DDLS_ABAPGIT_XML, \
    DDLS_NO_SOURCE_TYPE_ABAPGIT_XML, DDLS_ADT_NEW_OBJECT_REQUEST_XML, DDLS_NAME, DDLS_XML, DDLS_ALL_FIELDS_XML, \
    DDLS_ADT_ALREADY_EXISTS_RESPONSE_XML, DDLS_ADT_GET_RESPONSE_XML


class TestDataDefinitionHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = DataDefinitionHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'ddls')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.DataDefinition.OBJTYPE.code,))


class TestDataDefinitionHandlerLocate(unittest.TestCase):

    def setUp(self):
        self.handler = DataDefinitionHandler()
        package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('ddls', 'zfoo', './src/zfoo.ddls.xml',
                                   ['./src/zfoo.ddls.asddls'], package, self.handler)

    def test_main(self):
        self.assertEqual(self.handler.locate(self.repo_obj, 'source/main', 12),
                         ('./src/zfoo.ddls.asddls', 12))

    def test_unknown_part(self):
        self.assertIsNone(self.handler.locate(self.repo_obj, 'includes/testclasses', 1))

    def test_file_not_in_repository(self):
        self.repo_obj.files.remove('./src/zfoo.ddls.asddls')

        self.assertIsNone(self.handler.locate(self.repo_obj, 'source/main', 12))


class TestDDLSSourceType(unittest.TestCase):

    def test_ddls_source_type_view(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type('''@AbapCatalog.sqlViewName: 'ZSAPCLI_CDS_V'
@EndUserText.label: 'Test CDS view'
define view ZSAPCLI_CDS
  as select from tadir
{
  pgmid
}
''')

        self.assertEqual(source_type, 'V')

    def test_ddls_source_type_view_entity(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type(DDLS_SOURCE_CODE)

        self.assertEqual(source_type, 'W')

    def test_ddls_source_type_root_view_entity(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type('''define root view entity ZSAPCLI_CDS as select from tadir
 {
  key pgmid
}
''')

        self.assertEqual(source_type, 'W')

    def test_ddls_source_type_view_entity_upper_case(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type('''DEFINE VIEW ENTITY ZSAPCLI_CDS
  AS SELECT FROM tadir
{
  pgmid
}
''')

        self.assertEqual(source_type, 'W')

    def test_ddls_source_type_projection_view(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type('''define root view entity ZSAPCLI_C_CDS
  provider contract transactional_query
  as projection on ZSAPCLI_CDS
{
  key pgmid
}
''')

        self.assertEqual(source_type, 'P')

    def test_ddls_source_type_table_function(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type('''define table function ZSAPCLI_CDS
returns {
  client : abap.clnt;
  pgmid  : pgmid;
}
implemented by method zcl_sapcli_cds=>get_data;
''')

        self.assertEqual(source_type, 'F')

    def test_ddls_source_type_abstract_entity(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type('''define abstract entity ZSAPCLI_CDS
{
  num : abap.int4;
}
''')

        self.assertEqual(source_type, 'A')

    def test_ddls_source_type_unknown(self):
        source_type = sap.fileformat.abapgit.ddls.ddls_source_type('''define custom entity ZSAPCLI_CDS
{
  key num : abap.int4;
}
''')

        self.assertIsNone(source_type)


class TestDataDefinitionHandlerCheckout(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = DataDefinitionHandler()

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
            self.handler.checkout(connection, 'DDLS/DF', DDLS_NAME, destdir)

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


DDLS_SOURCE_MIME = 'text/plain; charset=utf-8'


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestDataDefinitionHandlerCheckin(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = DataDefinitionHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.source_file = f'./src/{DDLS_NAME.lower()}.ddls.asddls'
        self.baseinfo_file = f'./src/{DDLS_NAME.lower()}.ddls.baseinfo'
        self.repo_obj = RepoObject('ddls', DDLS_NAME.lower(), f'./src/{DDLS_NAME.lower()}.ddls.xml',
                                   [self.source_file], self.package, self.handler)

        self.fake_open = self.patch('sap.fileformat.abapgit.cds.open')
        self.fake_open.side_effect = [StringIOFile(DDLS_XML), StringIOFile(DDLS_SOURCE_CODE)]

    def responses_ok(self):
        return [
            Response(text='', status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, create_params=None, write_params=None):
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/ddl/sources')
        self.assertEqual(connection.execs[0].params, create_params)
        self.maxDiff = None
        self.assertEqual(connection.execs[0].body.decode('utf-8'), DDLS_ADT_NEW_OBJECT_REQUEST_XML)

        self.assertEqual(connection.execs[1].method, 'PUT')
        self.assertEqual(connection.execs[1].adt_uri, f'/sap/bc/adt/ddic/ddl/sources/{DDLS_NAME.lower()}/source/main')
        self.assertEqual(connection.execs[1].headers, {'Content-Type': DDLS_SOURCE_MIME})
        self.assertEqual(connection.execs[1].params, write_params or {'lockHandle': 'lock_handle'})
        self.assertEqual(connection.execs[1].body.decode('utf-8'), DDLS_SOURCE_CODE[:-1])

    def checkin_object(self, connection, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj)
        context = CheckinContext(connection, '$TMP', corrnr, check_before_save)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_ddls(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        result = self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(self.fake_open.call_args_list, [call(self.repo_obj.path, encoding='utf-8'),
                                                         call(self.source_file, 'r', encoding='utf-8')])

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, DDLS_NAME)
        self.assertEqual(result.used_files, [self.source_file])

        self.assertConsoleContents(self.console, stdout=f'''Creating Data Definition: {DDLS_NAME.lower()}
Writing Data Definition: {DDLS_NAME.lower()}
''')

    def test_checkin_ddls_with_baseinfo(self, fake_lock, fake_unlock):
        self.repo_obj.files.append(self.baseinfo_file)
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        result = self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)
        self.assertEqual(self.fake_open.call_args_list, [call(self.repo_obj.path, encoding='utf-8'),
                                                         call(self.source_file, 'r', encoding='utf-8')])
        self.assertEqual(result.used_files, [self.source_file, self.baseinfo_file])

    def test_checkin_ddls_all_fields(self, fake_lock, fake_unlock):
        self.fake_open.side_effect = [StringIOFile(DDLS_ALL_FIELDS_XML), StringIOFile(DDLS_SOURCE_CODE)]
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)

    def test_checkin_ddls_with_corrnr(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj, corrnr='420')

        self.assert_requests(connection, create_params={'corrNr': '420'},
                             write_params={'lockHandle': 'lock_handle', 'corrNr': '420'})

    def test_checkin_ddls_already_exists(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[0] = Response(text=DDLS_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                                headers={'content-type': 'application/xml'})
        connection = Connection(responses, user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)

    def test_checkin_ddls_no_source_file(self, fake_lock, fake_unlock):
        repo_obj = self.repo_obj._replace(files=[self.baseinfo_file])
        connection = Connection([], user='DEVELOPER')

        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin_object(connection, repo_obj)

        self.assertEqual(str(caught.exception), f'No source file for data definition {DDLS_NAME.lower()}')
        self.assertEqual(connection.execs, [])
        self.fake_open.assert_not_called()

    def test_checkin_ddls_check_before_save(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        with patch('sap.fileformat.adt.write_source') as fake_write:
            result = self.checkin_object(connection, self.repo_obj, check_before_save=True)

        fake_write.assert_called_once_with(DDLS_SOURCE_CODE, result.abap_objects[0], corrnr=None,
                                           source_label=self.source_file, check_before_save=True)


if __name__ == '__main__':
    unittest.main()
