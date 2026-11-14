#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, PropertyMock, call, mock_open, patch

import sap.adt.errors
import sap.platform.abap.abapgit.files as files

from sap.platform.abap.localrepository import RepositoryObserver

from mock import PatcherTestCase


class TestBuildFilename(unittest.TestCase):

    def test_without_destdir(self):
        self.assertEqual(files.build_filename('ZCL_FOO', '.clas', 'abap'), 'zcl_foo.clas.abap')

    def test_with_destdir(self):
        self.assertEqual(files.build_filename('ZCL_FOO', '.clas', 'xml', destdir='/Repo/SRC'),
                         '/Repo/SRC/zcl_foo.clas.xml')


class FilesTestCase(unittest.TestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.observer = Mock(spec=RepositoryObserver)

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()


class TestWriteSource(FilesTestCase):

    def test_write_source(self):
        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open:
            files.write_source(self.observer, 'class zcl_foo', 'ZCL_FOO', '.clas', destdir='/repo/src')

        fake_open.assert_called_once_with('/repo/src/zcl_foo.clas.abap', 'w', encoding='utf8')
        fake_open.return_value.write.assert_called_once_with('class zcl_foo')
        self.assertEqual(self.observer.mock_calls, [call.file_written('/repo/src/zcl_foo.clas.abap')])

    def test_write_source_file_extension(self):
        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open:
            files.write_source(self.observer, 'define view', 'ZVIEW', '.ddls', fileext='asddls')

        fake_open.assert_called_once_with('zview.ddls.asddls', 'w', encoding='utf8')
        self.assertEqual(self.observer.mock_calls, [call.file_written('zview.ddls.asddls')])


class TestDownloadAbapSource(FilesTestCase):

    def test_download(self):
        source_object = Mock(text='class zcl_foo')

        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open:
            files.download_abap_source(self.observer, 'ZCL_FOO', source_object, '.clas', destdir='/repo')

        fake_open.assert_called_once_with('/repo/zcl_foo.clas.abap', 'w', encoding='utf8')
        fake_open.return_value.write.assert_called_once_with('class zcl_foo')
        self.assertEqual(self.observer.mock_calls, [call.file_written('/repo/zcl_foo.clas.abap')])

    def test_download_error(self):
        source_object = Mock()
        type(source_object).text = PropertyMock(side_effect=sap.adt.errors.ExceptionResourceNotFound('No tests'))

        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open:
            files.download_abap_source(self.observer, 'ZCL_FOO', source_object, '.clas.testclasses')

        fake_open.assert_not_called()
        self.assertEqual(self.observer.mock_calls, [call.warning('Download of ABAP source code failed: No tests')])


class TestDumpAttributesToFile(FilesTestCase):

    def test_dump(self):
        with patch('sap.platform.abap.abapgit.files.open', mock_open()) as fake_open, \
             patch('sap.platform.abap.abapgit.files.XMLWriter') as fake_writer:
            files.dump_attributes_to_file(self.observer, 'ZCL_FOO', ('first', 'second'), '.clas', 'LCL_OBJECT_CLAS',
                                          destdir='/repo')

        fake_open.assert_called_once_with('/repo/zcl_foo.clas.xml', 'w', encoding='utf8')
        fake_writer.assert_called_once_with('LCL_OBJECT_CLAS', fake_open.return_value)
        self.assertEqual(fake_writer.return_value.mock_calls, [call.add('first'), call.add('second'), call.close()])
        self.assertEqual(self.observer.mock_calls, [call.file_written('/repo/zcl_foo.clas.xml')])


class TestFindObjectFile(unittest.TestCase):

    def setUp(self):
        self.repo_obj = Mock()
        self.repo_obj.name = 'zcl_foo'
        self.repo_obj.files = ['./src/zcl_foo.clas.xml', './src/zcl_foo.clas.abap', './src/zcl_foo.clas.testclasses.abap']

    def test_found(self):
        self.assertEqual(files.find_object_file(self.repo_obj, '.clas.abap'), './src/zcl_foo.clas.abap')

    def test_found_longer_name(self):
        self.assertEqual(files.find_object_file(self.repo_obj, '.clas.testclasses.abap'),
                         './src/zcl_foo.clas.testclasses.abap')

    def test_not_found(self):
        self.assertIsNone(files.find_object_file(self.repo_obj, '.clas.locals_imp.abap'))

    def test_name_must_match(self):
        self.repo_obj.files = ['./src/zcl_foo_bar.clas.abap']

        self.assertIsNone(files.find_object_file(self.repo_obj, '.clas.abap'))


class TestLocateMainSource(unittest.TestCase):

    def setUp(self):
        self.repo_obj = Mock()
        self.repo_obj.name = 'zif_foo'
        self.repo_obj.files = ['./src/zif_foo.intf.xml', './src/zif_foo.intf.abap']

    def test_main(self):
        self.assertEqual(files.locate_main_source(self.repo_obj, 'source/main', 12, '.intf.abap'),
                         ('./src/zif_foo.intf.abap', 12))

    def test_other_part(self):
        self.assertIsNone(files.locate_main_source(self.repo_obj, 'includes/testclasses', 12, '.intf.abap'))

    def test_no_file(self):
        self.repo_obj.files = ['./src/zif_foo.intf.xml']

        self.assertIsNone(files.locate_main_source(self.repo_obj, 'source/main', 12, '.intf.abap'))


if __name__ == '__main__':
    unittest.main()
