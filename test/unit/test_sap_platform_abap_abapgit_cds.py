#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, Mock, call

import sap
import sap.platform.abap.abapgit.cds as cds
from sap.adt.errors import ExceptionCheckinFailure, ExceptionResourceAlreadyExists
from sap.platform.abap.localrepository import CheckinContext, RepoObject, RepoPackage, RepositoryObserver
from sap.platform.abap.ddic import DCLS

from mock import PatcherTestCase, StringIOFile

DCLS_XML = '''<?xml version="1.0" encoding="utf-8"?>
<abapGit version="v1.0.0" serializer="LCL_OBJECT_DCLS" serializer_version="v1.0.0">
 <asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
  <asx:values>
   <DCLS>
    <DCLNAME>ZFOO</DCLNAME>
    <DCLLANGUAGE>E</DCLLANGUAGE>
    <DDTEXT>Test access control</DDTEXT>
   </DCLS>
  </asx:values>
 </asx:abap>
</abapGit>
'''


class CdsTestCase(unittest.TestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.observer = Mock(spec=RepositoryObserver)

        self.fake_open = self.patch('sap.platform.abap.abapgit.cds.open')
        self.fake_open.side_effect = [StringIOFile(DCLS_XML), StringIOFile('define role zfoo')]

        package = RepoPackage('./src', './src/package.devc.xml', None)
        self.repo_obj = RepoObject('dcls', 'zfoo', './src/zfoo.dcls.xml', ['./src/zfoo.dcls.asdcls'], package, None)

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()

    def prepare(self):
        return cds.prepare_cds_source(self.repo_obj, DCLS, lambda dcls: dcls.DDTEXT, '.asdcls', 'Access Control')


class TestPrepareCdsSource(CdsTestCase):

    def test_prepare(self):
        prepared = self.prepare()

        self.assertEqual(self.fake_open.call_args_list, [call('./src/zfoo.dcls.xml', encoding='utf-8'),
                                                         call('./src/zfoo.dcls.asdcls', 'r', encoding='utf-8')])
        self.assertEqual(prepared.description, 'Test access control')
        self.assertEqual(prepared.source_file, './src/zfoo.dcls.asdcls')
        self.assertEqual(prepared.source_code, 'define role zfoo')
        self.assertEqual(self.observer.mock_calls, [])

    def test_prepare_no_source_file(self):
        self.repo_obj.files.clear()

        with self.assertRaises(ExceptionCheckinFailure) as caught:
            self.prepare()

        self.assertEqual(str(caught.exception), 'No source file for access control zfoo')
        self.fake_open.assert_not_called()


class TestCheckinCdsSource(CdsTestCase):

    def setUp(self):
        super().setUp()

        self.fake_core_data = self.patch('sap.adt.ADTCoreData')
        self.fake_write_source = self.patch('sap.adt.checks.write_source')

        self.adt_object = MagicMock()
        self.adt_type = Mock(return_value=self.adt_object)

        self.connection = Mock()
        self.connection.user = 'developer'

    def checkin(self, corrnr=None, check_before_save=False):
        context = CheckinContext(self.connection, '$TMP', corrnr, check_before_save, self.observer)
        return cds.checkin_cds_source(context, self.repo_obj, self.prepare(), self.adt_type, 'Access Control')

    def test_checkin(self):
        adt_object, source_file = self.checkin()

        self.assertIs(adt_object, self.adt_object)
        self.assertEqual(source_file, './src/zfoo.dcls.asdcls')

        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='DEVELOPER',
                                                    description='Test access control')
        self.adt_type.assert_called_once_with(self.connection, 'ZFOO', package='$TMP',
                                              metadata=self.fake_core_data.return_value)
        self.adt_object.create.assert_called_once_with(None)
        self.fake_write_source.assert_called_once_with('define role zfoo', self.adt_object, corrnr=None,
                                                       source_label='./src/zfoo.dcls.asdcls',
                                                       check_before_save=False)
        self.assertEqual(self.observer.mock_calls, [
            call.creating('Access Control', 'zfoo'),
            call.writing('Access Control', 'zfoo'),
        ])

    def test_checkin_with_corrnr_and_check(self):
        self.checkin(corrnr='420', check_before_save=True)

        self.adt_object.create.assert_called_once_with('420')
        self.fake_write_source.assert_called_once_with('define role zfoo', self.adt_object, corrnr='420',
                                                       source_label='./src/zfoo.dcls.asdcls',
                                                       check_before_save=True)

    def test_checkin_already_exists(self):
        self.adt_object.create.side_effect = ExceptionResourceAlreadyExists('Access Control ZFOO already exists')

        with self.assertLogs(sap.get_logger(), 'INFO') as logs:
            self.checkin()

        self.assertEqual([record.getMessage() for record in logs.records], ['Access Control ZFOO already exists'])
        self.fake_write_source.assert_called_once()


if __name__ == '__main__':
    unittest.main()
