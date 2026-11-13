#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, PropertyMock, call, mock_open, patch

import sap.adt.errors
import sap.fileformat.abapgit.files as files

from mock import ConsoleOutputTestCase, PatcherTestCase


class TestBuildFilename(unittest.TestCase):

    def test_without_destdir(self):
        self.assertEqual(files.build_filename('ZCL_FOO', '.clas', 'abap'), 'zcl_foo.clas.abap')

    def test_with_destdir(self):
        self.assertEqual(files.build_filename('ZCL_FOO', '.clas', 'xml', destdir='/Repo/SRC'),
                         '/Repo/SRC/zcl_foo.clas.xml')


class FilesTestCase(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()


class TestWriteSource(FilesTestCase):

    def test_write_source(self):
        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            files.write_source('class zcl_foo', 'ZCL_FOO', '.clas', destdir='/repo/src')

        fake_open.assert_called_once_with('/repo/src/zcl_foo.clas.abap', 'w', encoding='utf8')
        fake_open.return_value.write.assert_called_once_with('class zcl_foo')
        self.assertConsoleContents(self.console, stdout='- zcl_foo.clas.abap\n')

    def test_write_source_file_extension(self):
        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            files.write_source('define view', 'ZVIEW', '.ddls', fileext='asddls')

        fake_open.assert_called_once_with('zview.ddls.asddls', 'w', encoding='utf8')
        self.assertConsoleContents(self.console, stdout='- zview.ddls.asddls\n')


class TestDownloadAbapSource(FilesTestCase):

    def test_download(self):
        source_object = Mock(text='class zcl_foo')

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            files.download_abap_source('ZCL_FOO', source_object, '.clas', destdir='/repo')

        fake_open.assert_called_once_with('/repo/zcl_foo.clas.abap', 'w', encoding='utf8')
        fake_open.return_value.write.assert_called_once_with('class zcl_foo')

    def test_download_error(self):
        source_object = Mock()
        type(source_object).text = PropertyMock(side_effect=sap.adt.errors.ExceptionResourceNotFound('No tests'))

        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open:
            files.download_abap_source('ZCL_FOO', source_object, '.clas.testclasses')

        fake_open.assert_not_called()
        self.assertConsoleContents(self.console, stderr='Download of ABAP source code failed: No tests\n')


class TestDumpAttributesToFile(FilesTestCase):

    def test_dump(self):
        with patch('sap.fileformat.abapgit.files.open', mock_open()) as fake_open, \
             patch('sap.fileformat.abapgit.files.XMLWriter') as fake_writer:
            files.dump_attributes_to_file('ZCL_FOO', ('first', 'second'), '.clas', 'LCL_OBJECT_CLAS',
                                          destdir='/repo')

        fake_open.assert_called_once_with('/repo/zcl_foo.clas.xml', 'w', encoding='utf8')
        fake_writer.assert_called_once_with('LCL_OBJECT_CLAS', fake_open.return_value)
        self.assertEqual(fake_writer.return_value.mock_calls, [call.add('first'), call.add('second'), call.close()])
        self.assertConsoleContents(self.console, stdout='- zcl_foo.clas.xml\n')


if __name__ == '__main__':
    unittest.main()
