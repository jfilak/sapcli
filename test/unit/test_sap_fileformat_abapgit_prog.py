#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, Mock, call, mock_open

import sap
import sap.adt
import sap.fileformat.abapgit.prog
from sap.adt.errors import ExceptionCheckinFailure, ExceptionResourceCreationFailure
from sap.adt.textelements import TextSymbol
from sap.fileformat import CheckinContext, ObjectHandler, RepoObject, RepoPackage
from sap.fileformat.abapgit.prog import ProgramHandler

from mock import Connection, ConsoleOutputTestCase, PatcherTestCase, StringIOFile
from fixtures_sap_fileformat_abapgit_prog import PROG_XML, PROG_WITH_CUA_XML, PROG_WITH_TEXTS_XML, INCLUDE_XML, \
    INCLUDE_WITH_TEXTS_XML, INVALID_TYPE_XML

FIXTURE_TEXT_SYMBOLS = '@MaxLength:20\r\n001=Hello, world!\r\n@MaxLength:10\r\n002=a=b\r\n'


class ProgramHandlerTestCase(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.handler = ProgramHandler()

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()


class TestProgramHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = ProgramHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'prog')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.Program.OBJTYPE.code,))


class TestBuildProgramAbapAttributes(unittest.TestCase):

    def test_build_program_attributes(self):
        prog = sap.adt.Program(Mock(), 'ZHELLO_WORLD')
        prog.description = 'Say hello!'
        prog.active = 'inactive'
        prog.fix_point_arithmetic = False
        prog.logical_database.reference.name = 'HANA'
        prog.program_type = 'executableProgram'

        progdir, tpool = sap.fileformat.abapgit.prog.build_program_abap_attributes(prog)

        self.assertEqual(progdir.NAME, 'ZHELLO_WORLD')
        self.assertEqual(progdir.STATE, 'S')
        self.assertEqual(progdir.DBAPL, 'S')
        self.assertEqual(progdir.VARCL, 'X')
        self.assertEqual(progdir.SUBC, '1')
        self.assertEqual(progdir.LDBNAME, 'HANA')
        self.assertEqual(progdir.UCCHECK, 'X')

        self.assertEqual(['APPL', 'DBNA', 'RLOAD', 'RSTAT'],
                         sorted([attr for attr, value in progdir.__dict__.items()
                                 if not attr.startswith('_') and value is None]))

        self.assertEqual(len(tpool), 1)
        descr = tpool[0]
        self.assertEqual(descr.ID, 'R')
        self.assertEqual(descr.ENTRY, 'Say hello!')
        self.assertEqual(descr.LENGTH, len('Say hello!'))

    def test_build_program_attributes_with_text_symbols(self):
        prog = sap.adt.Program(Mock(), 'ZHELLO_WORLD')
        prog.description = 'Say hello!'

        _, tpool = sap.fileformat.abapgit.prog.build_program_abap_attributes(
            prog, text_symbols=[TextSymbol('001', 'Hello, world!', 20), TextSymbol('002', 'a=b', 10)])

        self.assertEqual(len(tpool), 3)
        self.assertEqual((tpool[0].ID, tpool[0].KEY, tpool[0].ENTRY, tpool[0].LENGTH), ('I', '001', 'Hello, world!', 20))
        self.assertEqual((tpool[1].ID, tpool[1].KEY, tpool[1].ENTRY, tpool[1].LENGTH), ('I', '002', 'a=b', 10))
        self.assertEqual((tpool[2].ID, tpool[2].KEY, tpool[2].ENTRY, tpool[2].LENGTH), ('R', None, 'Say hello!', 10))


class TestProgramHandlerCheckout(ProgramHandlerTestCase):

    def setUp(self):
        super().setUp()

        self.fake_program = self.patch('sap.adt.Program')
        self.fake_texts = self.patch('sap.adt.textelements.ProgramTextElements')
        self.fake_writer = self.patch('sap.fileformat.abapgit.files.XMLWriter')
        self.fake_open = self.patch('sap.fileformat.abapgit.files.open', new_callable=mock_open)

        self.program = Mock()
        self.program.name = 'Z_HELLO_WORLD'
        self.program.description = 'Cowabunga'
        self.program.text = 'REPORT z_hello_world'
        self.program.active = 'active'
        self.program.application_database = 'S'
        self.program.program_type = '1'
        self.program.fix_point_arithmetic = True
        self.program.logical_database.reference.name = 'D$S'
        self.fake_program.return_value = self.program

        self.fake_texts.return_value.text = ''

        self.added = []
        self.fake_writer.return_value.add.side_effect = self.added.append

        self.connection = Connection()

    def test_checkout(self):
        self.handler.checkout(self.connection, 'PROG/P', 'Z_HELLO_WORLD', None)

        self.fake_program.assert_called_once_with(self.connection, 'Z_HELLO_WORLD')
        self.program.fetch.assert_called_once_with()

        self.assertEqual(self.fake_open.call_args_list, [
            call('z_hello_world.prog.abap', 'w', encoding='utf8'),
            call('z_hello_world.prog.xml', 'w', encoding='utf8'),
        ])
        self.fake_open.return_value.write.assert_called_once_with('REPORT z_hello_world')

        self.fake_writer.assert_called_once_with('LCL_OBJECT_PROG', self.fake_open.return_value)
        self.fake_writer.return_value.close.assert_called_once_with()

        self.assertEqual(len(self.added), 2)
        progdir = self.added[0]
        tpool = self.added[1]

        self.assertEqual(progdir.NAME, 'Z_HELLO_WORLD')
        self.assertEqual(progdir.STATE, 'A')
        self.assertEqual(progdir.VARCL, 'X')
        self.assertEqual(progdir.DBAPL, 'S')
        self.assertEqual(progdir.SUBC, '1')
        self.assertEqual(progdir.FIXPT, 'X')
        self.assertEqual(progdir.LDBNAME, 'D$S')
        self.assertEqual(progdir.UCCHECK, 'X')

        self.assertEqual(len(tpool), 1)
        self.assertEqual((tpool[0].ID, tpool[0].ENTRY, tpool[0].LENGTH), ('R', 'Cowabunga', 9))

        self.assertConsoleContents(self.console, stdout='''Z_HELLO_WORLD
- z_hello_world.prog.abap
- z_hello_world.prog.xml
''')

    def test_checkout_to_directory(self):
        self.handler.checkout(self.connection, 'PROG/P', 'Z_HELLO_WORLD', '/repo/src')

        self.assertEqual(self.fake_open.call_args_list, [
            call('/repo/src/z_hello_world.prog.abap', 'w', encoding='utf8'),
            call('/repo/src/z_hello_world.prog.xml', 'w', encoding='utf8'),
        ])

    def test_checkout_with_text_symbols(self):
        self.fake_texts.return_value.text = '@MaxLength:20\n001=Hello, world!'

        self.handler.checkout(self.connection, 'PROG/P', 'Z_HELLO_WORLD', None)

        self.fake_texts.assert_called_once_with(self.connection, 'Z_HELLO_WORLD')

        tpool = self.added[1]
        self.assertEqual(len(tpool), 2)
        self.assertEqual((tpool[0].ID, tpool[0].KEY, tpool[0].ENTRY, tpool[0].LENGTH), ('I', '001', 'Hello, world!', 20))
        self.assertEqual((tpool[1].ID, tpool[1].KEY, tpool[1].ENTRY, tpool[1].LENGTH), ('R', None, 'Cowabunga', 9))


class ProgramHandlerCheckinTestCase(ProgramHandlerTestCase):

    def setUp(self):
        super().setUp()

        self.fake_open = self.patch('sap.fileformat.abapgit.prog.open')

        self.package = RepoPackage('/src', '/src/package.devc.xml', None)
        self.prog_object = RepoObject('prog', 'test_prog', '/src/test_prog.prog.xml', ['foo.prog.abap'],
                                      self.package, self.handler)

    def open_files(self, prog_xml, source_code):
        self.fake_open.side_effect = [StringIOFile(prog_xml), StringIOFile(source_code)]


class TestProgramHandlerPrepare(ProgramHandlerCheckinTestCase):

    def test_prepare_program(self):
        self.open_files(PROG_XML, 'test_prog_body')

        prepared = self.handler.prepare(self.prog_object)

        self.assertEqual(self.fake_open.call_args_list, [
            call('/src/test_prog.prog.xml', encoding='utf-8'),
            call('foo.prog.abap', 'r', encoding='utf-8'),
        ])
        self.assertEqual(prepared.progdir.SUBC, '1')
        self.assertEqual(prepared.description, 'Test program desc')
        self.assertEqual(prepared.text_symbols, [])
        self.assertEqual(prepared.source_file, 'foo.prog.abap')
        self.assertEqual(prepared.source_code, 'test_prog_body')
        self.assertEmptyConsole(self.console)

    def test_prepare_include(self):
        self.open_files(INCLUDE_XML, 'test_include_body')

        prepared = self.handler.prepare(self.prog_object)

        self.assertEqual(prepared.progdir.SUBC, 'I')
        self.assertEqual(prepared.description, 'Test include desc')
        self.assertEqual(prepared.source_code, 'test_include_body')

    def test_prepare_with_text_symbols(self):
        self.open_files(PROG_WITH_TEXTS_XML, 'test_prog_body')

        prepared = self.handler.prepare(self.prog_object)

        self.assertEqual(prepared.text_symbols, [TextSymbol('001', 'Hello, world!', 20), TextSymbol('002', 'a=b', 10)])
        self.assertConsoleContents(self.console,
                                   stderr='Skipping unsupported text pool entry S P_MATNR of test_prog\n')

    def test_prepare_include_with_text_symbols(self):
        self.open_files(INCLUDE_WITH_TEXTS_XML, 'test_include_body')

        prepared = self.handler.prepare(self.prog_object)

        self.assertEqual(prepared.text_symbols, [])
        self.assertConsoleContents(self.console,
                                   stderr='Skipping unsupported text pool entry I 001 of test_prog\n')

    def test_prepare_no_files(self):
        prog_object = RepoObject('prog', 'test_prog', '/src/test_prog.prog.xml', [], self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(prog_object)

        self.assertEqual(str(cm.exception), 'No source file for program test_prog')
        self.fake_open.assert_not_called()
        self.assertEmptyConsole(self.console)

    def test_prepare_too_many_files(self):
        self.prog_object.files.append('foo.many.files.abap')

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(self.prog_object)

        self.assertEqual(str(cm.exception),
                         'Too many source files for program test_prog: foo.prog.abap,foo.many.files.abap')

    def test_prepare_wrong_suffix(self):
        prog_object = RepoObject('prog', 'test_prog', '/src/test_prog.prog.xml', ['foo.prog.wrong'],
                                 self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(prog_object)

        self.assertEqual(str(cm.exception), 'No .abap suffix of source file for program test_prog')

    def test_prepare_invalid_type(self):
        self.fake_open.side_effect = [StringIOFile(INVALID_TYPE_XML)]

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(self.prog_object)

        self.assertEqual(str(cm.exception), 'Unknown program type X')


class TestProgramHandlerCheckin(ProgramHandlerCheckinTestCase):

    def setUp(self):
        super().setUp()

        self.fake_core_data = self.patch('sap.adt.ADTCoreData')
        self.fake_program = self.patch('sap.adt.Program')
        self.fake_include = self.patch('sap.adt.Include')

        self.metadata = Mock()
        self.fake_core_data.return_value = self.metadata

        self.program_editor = MagicMock()
        self.program_editor.__enter__.return_value = self.program_editor

        self.program = MagicMock()
        self.program.open_editor.return_value = self.program_editor
        self.fake_program.return_value = self.program

        self.include_editor = MagicMock()
        self.include_editor.__enter__.return_value = self.include_editor

        self.include = MagicMock()
        self.include.open_editor.return_value = self.include_editor
        self.fake_include.return_value = self.include

        self.fake_program_text_elements = self.patch('sap.adt.textelements.ProgramTextElements')
        self.texts_editor = MagicMock()
        self.texts_editor.__enter__.return_value = self.texts_editor
        self.texts = MagicMock()
        self.texts.open_editor.return_value = self.texts_editor
        self.fake_program_text_elements.return_value = self.texts

        self.connection = Mock()
        self.connection.user = 'test_user'

    def checkin(self, prog_xml=PROG_XML, source_code='test_prog_body', corrnr=None, check_before_save=False):
        self.open_files(prog_xml, source_code)
        prepared = self.handler.prepare(self.prog_object)
        self.fake_open.reset_mock()

        context = CheckinContext(self.connection, 'test_package', corrnr, check_before_save)
        return self.handler.checkin(context, self.prog_object, prepared)

    def test_checkin_program(self):
        result = self.checkin()

        self.assertEqual(result.abap_objects, [self.program])
        self.assertEqual(result.used_files, ['foo.prog.abap'])
        self.fake_open.assert_not_called()
        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='TEST_USER')
        self.fake_program.assert_called_once_with(self.connection, 'test_prog', package='test_package',
                                                  metadata=self.metadata)
        self.fake_include.assert_not_called()
        self.assertEqual(self.program.description, 'Test program desc')
        self.program.create.assert_called_once_with(None)
        self.program.open_editor.assert_called_once_with(corrnr=None)
        self.program_editor.write.assert_called_once_with('test_prog_body')
        self.fake_program_text_elements.assert_not_called()
        self.assertConsoleContents(self.console, stdout='''Creating Program: test_prog
Writing Program: test_prog
''')

    def test_checkin_with_text_symbols(self):
        result = self.checkin(prog_xml=PROG_WITH_TEXTS_XML, corrnr='corrnr')

        self.assertEqual(result.abap_objects, [self.program, self.texts])
        self.assertEqual(result.used_files, ['foo.prog.abap'])
        self.assertEqual(self.program.description, 'Test program desc')
        self.program_editor.write.assert_called_once_with('test_prog_body')
        self.fake_program_text_elements.assert_called_once_with(self.connection, 'TEST_PROG')
        self.texts.open_editor.assert_called_once_with(corrnr='corrnr')
        self.texts_editor.write.assert_called_once_with(FIXTURE_TEXT_SYMBOLS)
        self.assertConsoleContents(self.console, stdout='''Creating Program: test_prog
Writing Program: test_prog
Writing Program: test_prog text elements
''', stderr='''Skipping unsupported text pool entry S P_MATNR of test_prog
''')

    def test_checkin_include_with_text_symbols(self):
        result = self.checkin(prog_xml=INCLUDE_WITH_TEXTS_XML, source_code='test_include_body')

        self.assertEqual(result.abap_objects, [self.include])
        self.assertEqual(self.include.description, 'Test include desc')
        self.fake_program_text_elements.assert_not_called()
        self.assertConsoleContents(self.console, stdout='''Creating Program: test_prog
Creating Include: test_prog
Writing Program: test_prog
''', stderr='''Skipping unsupported text pool entry I 001 of test_prog
''')

    def test_checkin_with_cua(self):
        self.checkin(prog_xml=PROG_WITH_CUA_XML)

        self.fake_program.assert_called_once_with(self.connection, 'test_prog', package='test_package',
                                                  metadata=self.metadata)
        self.assertEqual(self.program.description, 'Test program desc')
        self.program.create.assert_called_once_with(None)
        self.program_editor.write.assert_called_once_with('test_prog_body')

    def test_checkin_include(self):
        result = self.checkin(prog_xml=INCLUDE_XML, source_code='test_include_body')

        self.assertEqual(result.abap_objects, [self.include])
        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='TEST_USER')
        self.fake_include.assert_called_once_with(self.connection, 'test_prog', package='test_package',
                                                  metadata=self.metadata)
        self.fake_program.assert_not_called()
        self.assertEqual(self.include.description, 'Test include desc')
        self.include.create.assert_called_once_with(None)
        self.include.open_editor.assert_called_once_with(corrnr=None)
        self.include_editor.write.assert_called_once_with('test_include_body')
        self.assertConsoleContents(self.console, stdout='''Creating Program: test_prog
Creating Include: test_prog
Writing Program: test_prog
''')

    def test_checkin_with_corrnr(self):
        self.checkin(corrnr='corrnr')

        self.program.create.assert_called_once_with('corrnr')
        self.program.open_editor.assert_called_once_with(corrnr='corrnr')

    def test_checkin_check_before_save(self):
        fake_write_source = self.patch('sap.fileformat.adt.write_source')

        self.checkin(check_before_save=True)

        fake_write_source.assert_called_once_with('test_prog_body', self.program, corrnr=None,
                                                  source_label='foo.prog.abap', check_before_save=True)

    def test_checkin_already_exists(self):
        self.program.create.side_effect = ExceptionResourceCreationFailure(
            'A program or include already exists with the name TEST_PROG')

        with self.assertLogs(sap.get_logger(), 'INFO') as logs:
            self.checkin()

        self.assertEqual([record.getMessage() for record in logs.records],
                         ['A program or include already exists with the name TEST_PROG'])
        self.program.open_editor.assert_called_once_with(corrnr=None)
        self.program_editor.write.assert_called_once_with('test_prog_body')

    def test_checkin_creation_error(self):
        self.program.create.side_effect = ExceptionResourceCreationFailure('Failed to create program')

        with self.assertRaises(ExceptionResourceCreationFailure) as cm:
            self.checkin()

        self.assertEqual(str(cm.exception), 'Failed to create program')
        self.program.open_editor.assert_not_called()


class TestProgramHandlerLocate(unittest.TestCase):

    def setUp(self):
        self.handler = ProgramHandler()
        package = RepoPackage('./src', './src/package.devc.xml', None)
        self.prog_object = RepoObject('prog', 'zfoo', './src/zfoo.prog.xml',
                                      ['./src/zfoo.prog.abap', './src/zfoo.prog.xml'], package, self.handler)

    def test_main(self):
        self.assertEqual(self.handler.locate(self.prog_object, 'source/main', 12), ('./src/zfoo.prog.abap', 12))

    def test_unknown_part(self):
        self.assertIsNone(self.handler.locate(self.prog_object, 'includes/testclasses', 1))

    def test_file_not_in_repository(self):
        self.prog_object.files.remove('./src/zfoo.prog.abap')

        self.assertIsNone(self.handler.locate(self.prog_object, 'source/main', 12))


if __name__ == '__main__':
    unittest.main()
