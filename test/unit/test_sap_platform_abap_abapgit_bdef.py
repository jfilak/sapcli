#!/usr/bin/env python3

import os
import re
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, mock_open, patch

import sap.adt
import sap.errors
import sap.platform.abap.abapgit.bdef
from sap.adt.errors import ExceptionCheckinFailure
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import CheckinContext, ObjectHandler, RepoObject, RepoPackage
from sap.platform.abap.abapgit.bdef import BehaviorDefinitionHandler

from mock import Connection, ConsoleOutputTestCase, PatcherTestCase, Response, StringIOFile
from fixtures_sap_platform_abap_abapgit_bdef import BDEF_SOURCE_CODE, BDEF_ABAPGIT_XML, \
    BDEF_ADT_NEW_OBJECT_REQUEST_XML, BDEF_NAME, BDEF_XML, BDEF_ADT_ALREADY_EXISTS_RESPONSE_XML
from fixtures_sap_adt_behaviordefinition import BDEF_ADT_GET_RESPONSE_XML


class TestBehaviorDefinitionHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = BehaviorDefinitionHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'bdef')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.BehaviorDefinition.OBJTYPE.code,))


class TestBehaviorDefinitionHandlerLocate(unittest.TestCase):

    def setUp(self):
        self.handler = BehaviorDefinitionHandler()
        package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('bdef', 'zfoo', './src/zfoo.bdef.xml',
                                   ['./src/zfoo.bdef.asbdef'], package, self.handler)

    def test_main(self):
        self.assertEqual(self.handler.locate(self.repo_obj, 'source/main', 12),
                         ('./src/zfoo.bdef.asbdef', 12))

    def test_unknown_part(self):
        self.assertIsNone(self.handler.locate(self.repo_obj, 'includes/testclasses', 1))

    def test_file_not_in_repository(self):
        self.repo_obj.files.remove('./src/zfoo.bdef.asbdef')

        self.assertIsNone(self.handler.locate(self.repo_obj, 'source/main', 12))


class TestBehaviorDefinitionHandlerCheckout(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = BehaviorDefinitionHandler()

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

        with patch('sap.platform.abap.abapgit.files.open', side_effect=open_file):
            self.handler.checkout(connection, 'BDEF/BDO', BDEF_NAME, destdir)

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


@patch('sap.adt.objects.ADTObject.unlock')
@patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
class TestBehaviorDefinitionHandlerCheckin(ConsoleOutputTestCase, PatcherTestCase):

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
        self.handler = BehaviorDefinitionHandler()

        self.package = RepoPackage('./src', './src/package.devc.xml', None)
        self.source_file = f'./src/{BDEF_NAME.lower()}.bdef.asbdef'
        self.repo_obj = RepoObject('bdef', BDEF_NAME.lower(), f'./src/{BDEF_NAME.lower()}.bdef.xml',
                                   [self.source_file], self.package, self.handler)

        self.fake_open = self.patch('sap.platform.abap.abapgit.cds.open')
        self.fake_open.side_effect = [StringIOFile(BDEF_XML), StringIOFile(BDEF_SOURCE_CODE)]

    def responses_ok(self):
        return [
            Response(text='', status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ]

    def assert_requests(self, connection, create_params=None, write_params=None):
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/bo/behaviordefinitions')
        self.assertEqual(connection.execs[0].params, create_params)
        self.maxDiff = None
        self.assertEqual(connection.execs[0].body.decode('utf-8'), BDEF_ADT_NEW_OBJECT_REQUEST_XML)

        self.assertEqual(connection.execs[1].method, 'PUT')
        self.assertEqual(connection.execs[1].adt_uri,
                         f'/sap/bc/adt/bo/behaviordefinitions/{BDEF_NAME.lower()}/source/main')
        self.assertEqual(connection.execs[1].headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(connection.execs[1].params, write_params or {'lockHandle': 'lock_handle'})
        self.assertEqual(connection.execs[1].body.decode('utf-8'), BDEF_SOURCE_CODE)

    def checkin_object(self, connection, repo_obj, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(repo_obj)
        context = CheckinContext(connection, '$TMP', corrnr, check_before_save)
        return self.handler.checkin(context, repo_obj, prepared)

    def test_checkin_bdef(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        result = self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)
        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        self.assertEqual(self.fake_open.call_args_list, [call(self.repo_obj.path, encoding='utf-8'),
                                                         call(self.source_file, 'r', encoding='utf-8')])

        self.assertEqual(len(result.abap_objects), 1)
        self.assertEqual(result.abap_objects[0].name, BDEF_NAME)
        self.assertEqual(result.used_files, [self.source_file])

        self.assertConsoleContents(self.console, stdout=f'''Creating Behavior Definition: {BDEF_NAME.lower()}
Writing Behavior Definition: {BDEF_NAME.lower()}
''')

    def test_checkin_bdef_with_corrnr(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj, corrnr='420')

        self.assert_requests(connection, create_params={'corrNr': '420'},
                             write_params={'lockHandle': 'lock_handle', 'corrNr': '420'})

    def test_checkin_bdef_already_exists(self, fake_lock, fake_unlock):
        responses = self.responses_ok()
        responses[0] = Response(text=BDEF_ADT_ALREADY_EXISTS_RESPONSE_XML, status_code=500,
                                headers={'content-type': 'application/xml'})
        connection = Connection(responses, user='DEVELOPER')

        self.checkin_object(connection, self.repo_obj)

        self.assert_requests(connection)

    def test_checkin_bdef_no_source_file(self, fake_lock, fake_unlock):
        repo_obj = self.repo_obj._replace(files=[])
        connection = Connection([], user='DEVELOPER')

        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.checkin_object(connection, repo_obj)

        self.assertEqual(str(caught.exception), f'No source file for behavior definition {BDEF_NAME.lower()}')
        self.assertEqual(connection.execs, [])
        self.fake_open.assert_not_called()

    def test_checkin_bdef_check_before_save(self, fake_lock, fake_unlock):
        connection = Connection(self.responses_ok(), user='DEVELOPER')

        with patch('sap.adt.checks.write_source') as fake_write:
            result = self.checkin_object(connection, self.repo_obj, check_before_save=True)

        fake_write.assert_called_once_with(BDEF_SOURCE_CODE, result.abap_objects[0], corrnr=None,
                                           source_label=self.source_file, check_before_save=True)


if __name__ == '__main__':
    unittest.main()
