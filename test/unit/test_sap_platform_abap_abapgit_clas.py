#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, call, mock_open, patch

import sap.adt
import sap.adt.errors
import sap.platform.abap.abapgit.clas
from sap.adt.errors import ExceptionCheckinFailure, ExceptionResourceAlreadyExists
from sap.errors import SAPCliError
from sap.platform.abap.localrepository import CheckinContext, ObjectHandler, RepoObject, RepoPackage
from sap.platform.abap.abapgit.clas import ClassHandler

from mock import Connection, ConsoleOutputTestCase, PatcherTestCase, StringIOFile
from fixtures_sap_platform_abap_abapgit_clas import CLAS_XML, CLAS_WITH_DESCRIPTIONS_SUB_XML, CLAS_WITH_TPOOL_XML

FIXTURE_TEXT_SYMBOLS = '@MaxLength:20\r\n001=Hello, world!\r\n@MaxLength:10\r\n002=a=b\r\n'


class ClassHandlerTestCase(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.handler = ClassHandler()

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()


class TestClassHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = ClassHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'clas')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, ('CLAS/OC',))


class TestClassHandlerCheckout(ClassHandlerTestCase):

    def setUp(self):
        super().setUp()

        self.fake_class = self.patch('sap.adt.Class')
        self.fake_texts = self.patch('sap.adt.textelements.ClassTextElements')
        self.fake_writer = self.patch('sap.platform.abap.abapgit.files.XMLWriter')
        self.fake_open = self.patch('sap.platform.abap.abapgit.files.open', new_callable=mock_open)

        self.clas = Mock()
        self.clas.name = 'ZCL_HELLO_WORLD'
        self.clas.description = 'Cowabunga'
        self.clas.master_language = 'EN'
        self.clas.active = 'active'
        self.clas.modeled = False
        self.clas.fix_point_arithmetic = True
        self.clas.text = 'class zcl_hello_world'
        self.clas.definitions.text = '* definitions'
        self.clas.implementations.text = '* implementations'
        self.clas.test_classes.text = '* tests'
        self.fake_class.return_value = self.clas

        self.fake_texts.return_value.text = ''

        self.added = []
        self.fake_writer.return_value.add.side_effect = self.added.append

        self.connection = Connection()

    def test_checkout(self):
        self.handler.checkout(self.connection, 'CLAS/OC', 'ZCL_HELLO_WORLD', None)

        self.fake_class.assert_called_once_with(self.connection, 'ZCL_HELLO_WORLD')
        self.clas.fetch.assert_called_once_with()

        self.assertEqual(self.fake_open.call_args_list, [
            call('zcl_hello_world.clas.abap', 'w', encoding='utf8'),
            call('zcl_hello_world.clas.locals_def.abap', 'w', encoding='utf8'),
            call('zcl_hello_world.clas.locals_imp.abap', 'w', encoding='utf8'),
            call('zcl_hello_world.clas.testclasses.abap', 'w', encoding='utf8'),
            call('zcl_hello_world.clas.xml', 'w', encoding='utf8'),
        ])
        self.assertEqual(self.fake_open.return_value.write.call_args_list, [
            call('class zcl_hello_world'),
            call('* definitions'),
            call('* implementations'),
            call('* tests'),
        ])

        self.fake_writer.assert_called_once_with('LCL_OBJECT_CLAS', self.fake_open.return_value)
        self.fake_writer.return_value.close.assert_called_once_with()

        self.assertEqual(len(self.added), 1)
        vseoclass = self.added[0]
        self.assertEqual(vseoclass.CLSNAME, 'ZCL_HELLO_WORLD')
        self.assertEqual(vseoclass.VERSION, '1')
        self.assertEqual(vseoclass.LANGU, 'E')
        self.assertEqual(vseoclass.DESCRIPT, 'Cowabunga')
        self.assertEqual(vseoclass.STATE, '1')
        self.assertEqual(vseoclass.CLSCCINCL, 'X')
        self.assertEqual(vseoclass.FIXPT, 'X')
        self.assertEqual(vseoclass.UNICODE, 'X')

        self.assertConsoleContents(self.console, stdout='''ZCL_HELLO_WORLD
- zcl_hello_world.clas.abap
- zcl_hello_world.clas.locals_def.abap
- zcl_hello_world.clas.locals_imp.abap
- zcl_hello_world.clas.testclasses.abap
- zcl_hello_world.clas.xml
''')

    def test_checkout_to_directory(self):
        self.handler.checkout(self.connection, 'CLAS/OC', 'ZCL_HELLO_WORLD', '/repo/src')

        self.assertEqual(self.fake_open.call_args_list, [
            call('/repo/src/zcl_hello_world.clas.abap', 'w', encoding='utf8'),
            call('/repo/src/zcl_hello_world.clas.locals_def.abap', 'w', encoding='utf8'),
            call('/repo/src/zcl_hello_world.clas.locals_imp.abap', 'w', encoding='utf8'),
            call('/repo/src/zcl_hello_world.clas.testclasses.abap', 'w', encoding='utf8'),
            call('/repo/src/zcl_hello_world.clas.xml', 'w', encoding='utf8'),
        ])

    def test_checkout_inactive_modeled_class(self):
        self.clas.active = 'inactive'
        self.clas.modeled = True
        self.clas.fix_point_arithmetic = False

        self.handler.checkout(self.connection, 'CLAS/OC', 'ZCL_HELLO_WORLD', None)

        vseoclass = self.added[0]
        self.assertEqual(vseoclass.VERSION, '0')
        self.assertEqual(vseoclass.STATE, '0')
        self.assertEqual(vseoclass.FIXPT, ' ')

    def test_checkout_with_text_symbols(self):
        self.fake_texts.return_value.text = '@MaxLength:20\n001=Hello, world!\n\n@MaxLength:10\n002=a=b'

        self.handler.checkout(self.connection, 'CLAS/OC', 'ZCL_HELLO_WORLD', None)

        self.fake_texts.assert_called_once_with(self.connection, 'ZCL_HELLO_WORLD')

        self.assertEqual(len(self.added), 2)
        self.assertEqual(self.added[0].CLSNAME, 'ZCL_HELLO_WORLD')

        tpool = self.added[1]
        self.assertEqual(len(tpool), 2)
        self.assertEqual((tpool[0].ID, tpool[0].KEY, tpool[0].ENTRY, tpool[0].LENGTH), ('I', '001', 'Hello, world!', 20))
        self.assertEqual((tpool[1].ID, tpool[1].KEY, tpool[1].ENTRY, tpool[1].LENGTH), ('I', '002', 'a=b', 10))

    def test_checkout_text_symbols_error(self):
        type(self.fake_texts.return_value).text = PropertyMock(
            side_effect=sap.adt.errors.ExceptionResourceNotFound('Cannot access text elements'))

        self.handler.checkout(self.connection, 'CLAS/OC', 'ZCL_HELLO_WORLD', None)

        self.assertEqual(len(self.added), 1)
        self.assertEqual(self.console.caperr, 'Download of text elements failed: Cannot access text elements\n')


class ClassHandlerCheckinTestCase(ClassHandlerTestCase):

    def setUp(self):
        super().setUp()

        self.fake_open = self.patch('sap.platform.abap.abapgit.clas.open')

        self.package = RepoPackage('/src', '/src/package.devc.xml', None)
        self.clas_object = RepoObject('clas', 'test_clas', '/src/test_clas.clas.xml',
                                      ['foo.clas.abap', 'foo.locals_def.abap', 'foo.locals_imp.abap',
                                       'foo.testclasses.abap'],
                                      self.package, self.handler)

        self.source_files_content = ['class_body', 'locals_def_body', 'locals_imp_body', 'test_body']

    def open_files(self, clas_xml):
        self.fake_open.side_effect = [StringIOFile(content) for content in [clas_xml] + self.source_files_content]


class TestClassHandlerPrepare(ClassHandlerCheckinTestCase):

    def test_prepare(self):
        self.open_files(CLAS_XML)

        prepared = self.handler.prepare(self.clas_object)

        self.assertEqual(self.fake_open.call_args_list, [
            call('/src/test_clas.clas.xml', encoding='utf-8'),
            call('foo.clas.abap', 'r', encoding='utf-8'),
            call('foo.locals_def.abap', 'r', encoding='utf-8'),
            call('foo.locals_imp.abap', 'r', encoding='utf-8'),
            call('foo.testclasses.abap', 'r', encoding='utf-8'),
        ])
        self.assertEqual(prepared.abap_data.DESCRIPT, 'Test description')
        self.assertEqual(prepared.text_symbols, [])
        self.assertEqual(prepared.parts, [
            ('clas', 'foo.clas.abap', 'class_body'),
            ('locals_def', 'foo.locals_def.abap', 'locals_def_body'),
            ('locals_imp', 'foo.locals_imp.abap', 'locals_imp_body'),
            ('testclasses', 'foo.testclasses.abap', 'test_body'),
        ])
        self.assertEmptyConsole(self.console)

    def test_prepare_with_descriptions_sub(self):
        self.open_files(CLAS_WITH_DESCRIPTIONS_SUB_XML)

        prepared = self.handler.prepare(self.clas_object)

        self.assertEqual(prepared.abap_data.DESCRIPT, 'Test description')
        self.assertEqual(len(prepared.parts), 4)

    def test_prepare_with_text_pool(self):
        self.open_files(CLAS_WITH_TPOOL_XML)

        prepared = self.handler.prepare(self.clas_object)

        self.assertEqual(len(prepared.text_symbols), 2)
        self.assertEqual(prepared.text_symbols[0].id, '001')
        self.assertEqual(prepared.text_symbols[1].id, '002')

    def test_prepare_no_files(self):
        clas_obj = RepoObject('clas', 'no_files_clas', '/src/no_files_clas.clas.xml', [], self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(clas_obj)

        self.assertEqual(str(cm.exception), 'No source file for class no_files_clas')
        self.fake_open.assert_not_called()
        self.assertEmptyConsole(self.console)

    def test_prepare_source_file_wrong_suffix(self):
        self.fake_open.return_value = StringIOFile(CLAS_XML)
        self.clas_object.files.append('foo.wrong.prefix')

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(self.clas_object)

        self.assertEqual(str(cm.exception),
                         'No .abap suffix of source file for class test_clas: foo.wrong.prefix')

    def test_prepare_unknown_class_part(self):
        self.open_files(CLAS_XML)
        self.clas_object.files.append('foo.unknown.abap')

        prepared = self.handler.prepare(self.clas_object)

        self.assertEqual(len(prepared.parts), 4)
        self.assertConsoleContents(self.console, stderr='Unknown class part foo.unknown.abap\n')


class TestClassHandlerCheckin(ClassHandlerCheckinTestCase):

    def setUp(self):
        super().setUp()

        self.fake_core_data = self.patch('sap.adt.ADTCoreData')
        self.fake_class = self.patch('sap.adt.Class')

        self.metadata = Mock()
        self.fake_core_data.return_value = self.metadata

        self.clas_editor = MagicMock()
        self.clas_editor.__enter__.return_value = self.clas_editor

        self.package_reference = Mock()
        self.package_reference.name = 'test_package'

        self.clas = MagicMock(reference=self.package_reference)
        self.clas.open_editor.return_value = self.clas_editor
        self.clas.definitions.open_editor.return_value = self.clas_editor
        self.clas.implementations.open_editor.return_value = self.clas_editor
        self.clas.test_classes.open_editor.return_value = self.clas_editor
        self.fake_class.return_value = self.clas

        self.fake_class_text_elements = self.patch('sap.adt.textelements.ClassTextElements')
        self.texts_editor = MagicMock()
        self.texts_editor.__enter__.return_value = self.texts_editor
        self.texts = MagicMock()
        self.texts.open_editor.return_value = self.texts_editor
        self.fake_class_text_elements.return_value = self.texts

        self.connection = Mock()
        self.connection.user = 'test_user'

    def checkin(self, clas_xml=CLAS_XML, corrnr=None, check_before_save=False):
        self.open_files(clas_xml)
        prepared = self.handler.prepare(self.clas_object)

        context = CheckinContext(self.connection, 'test_package', corrnr, check_before_save)
        return self.handler.checkin(context, self.clas_object, prepared)

    def assert_open_editor_calls(self, corrnr=None):
        self.clas.open_editor.assert_called_once_with(corrnr=corrnr)
        self.clas.definitions.open_editor.assert_called_once_with(corrnr=corrnr)
        self.clas.implementations.open_editor.assert_called_once_with(corrnr=corrnr)
        self.clas.test_classes.open_editor.assert_called_once_with(corrnr=corrnr)
        self.assertEqual(self.clas_editor.write.call_args_list,
                         [call('class_body'), call('locals_def_body'), call('locals_imp_body'), call('test_body')])

    def test_checkin(self):
        result = self.checkin()

        self.assertEqual(result.abap_objects, [self.clas])
        self.assertEqual(result.used_files, ['foo.clas.abap', 'foo.locals_def.abap', 'foo.locals_imp.abap',
                                             'foo.testclasses.abap'])
        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN',
                                                    responsible='TEST_USER', description='Test description')
        self.fake_class.assert_called_once_with(self.connection, 'TEST_CLAS', package='test_package',
                                                metadata=self.metadata)
        self.clas.create.assert_called_once_with(None)
        self.assert_open_editor_calls()
        self.fake_class_text_elements.assert_not_called()
        self.assertConsoleContents(self.console, stdout='''Creating Class: test_clas
Writing Clas: test_clas clas
Writing Clas: test_clas locals_def
Writing Clas: test_clas locals_imp
Writing Clas: test_clas testclasses
''')

    def test_checkin_with_text_pool(self):
        result = self.checkin(clas_xml=CLAS_WITH_TPOOL_XML, corrnr='corrnr')

        self.assertEqual(result.abap_objects, [self.clas, self.texts])
        self.assertEqual(result.used_files, ['foo.clas.abap', 'foo.locals_def.abap', 'foo.locals_imp.abap',
                                             'foo.testclasses.abap'])
        self.fake_class_text_elements.assert_called_once_with(self.connection, 'TEST_CLAS')
        self.texts.open_editor.assert_called_once_with(corrnr='corrnr')
        self.texts_editor.write.assert_called_once_with(FIXTURE_TEXT_SYMBOLS)
        self.assertConsoleContents(self.console, stdout='''Creating Class: test_clas
Writing Clas: test_clas clas
Writing Clas: test_clas locals_def
Writing Clas: test_clas locals_imp
Writing Clas: test_clas testclasses
Writing Clas: test_clas text elements
''')

    def test_checkin_with_corrnr(self):
        self.checkin(corrnr='corrnr')

        self.clas.create.assert_called_once_with('corrnr')
        self.assert_open_editor_calls(corrnr='corrnr')

    def test_checkin_check_before_save(self):
        with patch('sap.adt.checks.write_source') as fake_write:
            self.checkin(corrnr='corrnr', check_before_save=True)

        self.assertEqual(fake_write.call_args_list, [
            call('class_body', self.clas, corrnr='corrnr', source_label='foo.clas.abap', check_before_save=True),
            call('locals_def_body', self.clas.definitions, corrnr='corrnr', source_label='foo.locals_def.abap',
                 check_before_save=True),
            call('locals_imp_body', self.clas.implementations, corrnr='corrnr', source_label='foo.locals_imp.abap',
                 check_before_save=True),
            call('test_body', self.clas.test_classes, corrnr='corrnr', source_label='foo.testclasses.abap',
                 check_before_save=True),
        ])

    def test_checkin_already_exists(self):
        self.clas.create.side_effect = [ExceptionResourceAlreadyExists('Class already exists.'), None]

        self.checkin()

        self.clas.fetch.assert_called_once()
        self.clas.delete.assert_called_once_with(None)
        self.assertEqual(self.clas.create.call_args_list, [call(None), call(None)])
        self.assertEqual(self.fake_class.call_count, 2)

    def test_checkin_already_exists_with_corrnr(self):
        self.clas.create.side_effect = [ExceptionResourceAlreadyExists('Class already exists.'), None]

        self.checkin(corrnr='corrnr')

        self.clas.fetch.assert_called_once()
        self.clas.delete.assert_called_once_with('corrnr')
        self.assertEqual(self.clas.create.call_args_list, [call('corrnr'), call('corrnr')])

    def test_checkin_in_different_package(self):
        self.clas.create.side_effect = ExceptionResourceAlreadyExists('Class already exists.')
        self.package_reference.name = 'different_package'

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.checkin()

        self.assertEqual(str(cm.exception),
                         'Cannot checkin class test_clas into package test_package.'
                         ' It already exists in package different_package.')
        self.clas.delete.assert_not_called()

    def test_checkin_create_error(self):
        self.clas.create.side_effect = SAPCliError('Class creation failed.')

        with self.assertRaises(SAPCliError) as cm:
            self.checkin()

        self.assertEqual(str(cm.exception), 'Class creation failed.')
        self.clas.open_editor.assert_not_called()


class TestClassHandlerLocate(unittest.TestCase):

    def setUp(self):
        self.handler = ClassHandler()
        package = RepoPackage('./src', './src/package.devc.xml', None)
        self.clas_object = RepoObject('clas', 'zcl_foo', './src/zcl_foo.clas.xml',
                                      ['./src/zcl_foo.clas.abap',
                                       './src/zcl_foo.clas.locals_def.abap',
                                       './src/zcl_foo.clas.locals_imp.abap',
                                       './src/zcl_foo.clas.testclasses.abap',
                                       './src/zcl_foo.clas.xml'],
                                      package, self.handler)

    def test_main(self):
        self.assertEqual(self.handler.locate(self.clas_object, 'source/main', 183),
                         ('./src/zcl_foo.clas.abap', 183))

    def test_definitions(self):
        self.assertEqual(self.handler.locate(self.clas_object, 'includes/definitions', 5),
                         ('./src/zcl_foo.clas.locals_def.abap', 5))

    def test_implementations(self):
        self.assertEqual(self.handler.locate(self.clas_object, 'includes/implementations', 7),
                         ('./src/zcl_foo.clas.locals_imp.abap', 7))

    def test_testclasses(self):
        self.assertEqual(self.handler.locate(self.clas_object, 'includes/testclasses', 42),
                         ('./src/zcl_foo.clas.testclasses.abap', 42))

    def test_unknown_part(self):
        self.assertIsNone(self.handler.locate(self.clas_object, 'includes/macros', 1))

    def test_file_not_in_repository(self):
        self.clas_object.files.remove('./src/zcl_foo.clas.testclasses.abap')

        self.assertIsNone(self.handler.locate(self.clas_object, 'includes/testclasses', 42))


if __name__ == '__main__':
    unittest.main()
