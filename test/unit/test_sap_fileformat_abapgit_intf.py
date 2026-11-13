#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, Mock, call, mock_open

import sap.adt
import sap.fileformat.abapgit.intf
from sap.adt.errors import ExceptionCheckinFailure, ExceptionResourceAlreadyExists
from sap.fileformat import CheckinContext, ObjectHandler, RepoObject, RepoPackage
from sap.fileformat.abapgit.intf import InterfaceHandler

from mock import Connection, ConsoleOutputTestCase, PatcherTestCase, StringIOFile
from fixtures_sap_fileformat_abapgit_intf import INTF_XML, INTF_WITH_DESCRIPTIONS_SUB_XML


class InterfaceHandlerTestCase(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.patch_console(self.console)

        self.handler = InterfaceHandler()

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()


class TestInterfaceHandlerIdentity(unittest.TestCase):

    def test_identity(self):
        handler = InterfaceHandler()

        self.assertIsInstance(handler, ObjectHandler)
        self.assertEqual(handler.FILE_TYPE, 'intf')
        self.assertEqual(handler.METADATA_EXT, 'xml')
        self.assertEqual(handler.ADT_TYPES, (sap.adt.Interface.OBJTYPE.code,))


class TestBuildInterfaceAbapAttributes(unittest.TestCase):

    def test_inactive_modeled_interface(self):
        intf = sap.adt.Interface(Mock(), 'ZIF_HELLO_WORLD')
        intf.description = 'This is an interface'
        intf.master_language = 'EN'
        intf.active = 'inactive'
        intf.modeled = 'true'

        vseointerf = sap.fileformat.abapgit.intf.build_interface_abap_attributes(intf)

        self.assertEqual(vseointerf.CLSNAME, 'ZIF_HELLO_WORLD')
        self.assertEqual(vseointerf.DESCRIPT, 'This is an interface')
        self.assertEqual(vseointerf.LANGU, 'E')
        self.assertEqual(vseointerf.EXPOSURE, '2')
        self.assertEqual(vseointerf.VERSION, '0')
        self.assertEqual(vseointerf.STATE, '0')
        self.assertEqual(vseointerf.UNICODE, 'X')


class TestInterfaceHandlerCheckout(InterfaceHandlerTestCase):

    def setUp(self):
        super().setUp()

        self.fake_interface = self.patch('sap.adt.Interface')
        self.fake_writer = self.patch('sap.fileformat.abapgit.files.XMLWriter')
        self.fake_open = self.patch('sap.fileformat.abapgit.files.open', new_callable=mock_open)

        self.intf = Mock()
        self.intf.name = 'ZIF_HELLO_WORLD'
        self.intf.description = 'This is an interface'
        self.intf.master_language = 'EN'
        self.intf.active = 'active'
        self.intf.modeled = False
        self.intf.text = 'interface zif_hello_world'
        self.fake_interface.return_value = self.intf

        self.added = []
        self.fake_writer.return_value.add.side_effect = self.added.append

        self.connection = Connection()

    def test_checkout(self):
        self.handler.checkout(self.connection, 'INTF/OI', 'ZIF_HELLO_WORLD', None)

        self.fake_interface.assert_called_once_with(self.connection, 'ZIF_HELLO_WORLD')
        self.intf.fetch.assert_called_once_with()

        self.assertEqual(self.fake_open.call_args_list, [
            call('zif_hello_world.intf.abap', 'w', encoding='utf8'),
            call('zif_hello_world.intf.xml', 'w', encoding='utf8'),
        ])
        self.fake_open.return_value.write.assert_called_once_with('interface zif_hello_world')

        self.fake_writer.assert_called_once_with('LCL_OBJECT_INTF', self.fake_open.return_value)
        self.fake_writer.return_value.close.assert_called_once_with()

        self.assertEqual(len(self.added), 1)
        vseointerf = self.added[0]
        self.assertEqual(vseointerf.CLSNAME, 'ZIF_HELLO_WORLD')
        self.assertEqual(vseointerf.VERSION, '1')
        self.assertEqual(vseointerf.LANGU, 'E')
        self.assertEqual(vseointerf.DESCRIPT, 'This is an interface')
        self.assertEqual(vseointerf.EXPOSURE, '2')
        self.assertEqual(vseointerf.STATE, '1')
        self.assertEqual(vseointerf.UNICODE, 'X')

        self.assertConsoleContents(self.console, stdout='''ZIF_HELLO_WORLD
- zif_hello_world.intf.abap
- zif_hello_world.intf.xml
''')

    def test_checkout_to_directory(self):
        self.handler.checkout(self.connection, 'INTF/OI', 'ZIF_HELLO_WORLD', '/repo/src')

        self.assertEqual(self.fake_open.call_args_list, [
            call('/repo/src/zif_hello_world.intf.abap', 'w', encoding='utf8'),
            call('/repo/src/zif_hello_world.intf.xml', 'w', encoding='utf8'),
        ])


class InterfaceHandlerCheckinTestCase(InterfaceHandlerTestCase):

    def setUp(self):
        super().setUp()

        self.fake_open = self.patch('sap.fileformat.abapgit.intf.open')
        self.fake_open.side_effect = [StringIOFile(INTF_XML), StringIOFile('test_intf_body')]

        self.package = RepoPackage('/src', '/src/package.devc.xml', None)
        self.interface_object = RepoObject('intf', 'test_interface', '/src/test_interface.intf.xml',
                                           ['foo.intf.abap'], self.package, self.handler)


class TestInterfaceHandlerPrepare(InterfaceHandlerCheckinTestCase):

    def test_prepare(self):
        prepared = self.handler.prepare(self.interface_object)

        self.assertEqual(self.fake_open.call_args_list, [
            call('/src/test_interface.intf.xml', encoding='utf-8'),
            call('foo.intf.abap', 'r', encoding='utf-8'),
        ])
        self.assertEqual(prepared.abap_data.DESCRIPT, 'Test intf descr')
        self.assertEqual(prepared.source_file, 'foo.intf.abap')
        self.assertEqual(prepared.source_code, 'test_intf_body')
        self.assertEmptyConsole(self.console)

    def test_prepare_with_descriptions_sub(self):
        self.fake_open.side_effect = [StringIOFile(INTF_WITH_DESCRIPTIONS_SUB_XML), StringIOFile('test_intf_body')]

        prepared = self.handler.prepare(self.interface_object)

        self.assertEqual(prepared.abap_data.DESCRIPT, 'Test intf descr')
        self.assertEqual(prepared.source_code, 'test_intf_body')

    def test_prepare_no_file(self):
        interface_object = RepoObject('intf', 'test_intf', '/src/boo', [], self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(interface_object)

        self.assertEqual(str(cm.exception), 'No source file for interface test_intf')
        self.fake_open.assert_not_called()
        self.assertEmptyConsole(self.console)

    def test_prepare_too_many_files(self):
        self.interface_object.files.append('too-many.intf.abap')

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(self.interface_object)

        self.assertEqual(str(cm.exception),
                         'Too many source files for interface test_interface: foo.intf.abap,too-many.intf.abap')

    def test_prepare_wrong_suffix(self):
        interface_object = RepoObject('intf', 'test_intf', '/src/boo', ['random.file'], self.package, self.handler)

        with self.assertRaises(ExceptionCheckinFailure) as cm:
            self.handler.prepare(interface_object)

        self.assertEqual(str(cm.exception), 'No .abap suffix of source file for interface test_intf')


class TestInterfaceHandlerCheckin(InterfaceHandlerCheckinTestCase):

    def setUp(self):
        super().setUp()

        self.fake_core_data = self.patch('sap.adt.ADTCoreData')
        self.fake_interface = self.patch('sap.adt.Interface')

        self.metadata = Mock()
        self.fake_core_data.return_value = self.metadata

        self.interface_editor = MagicMock()
        self.interface_editor.__enter__.return_value = self.interface_editor

        self.interface = MagicMock()
        self.interface.open_editor.return_value = self.interface_editor
        self.fake_interface.return_value = self.interface

        self.connection = Mock()
        self.connection.user = 'test_user'

    def checkin(self, corrnr=None, check_before_save=False):
        prepared = self.handler.prepare(self.interface_object)
        self.fake_open.reset_mock()

        context = CheckinContext(self.connection, 'test_package', corrnr, check_before_save)
        return self.handler.checkin(context, self.interface_object, prepared)

    def test_checkin(self):
        result = self.checkin()

        self.assertEqual(result.abap_objects, [self.interface])
        self.assertEqual(result.used_files, ['foo.intf.abap'])
        self.fake_open.assert_not_called()
        self.fake_core_data.assert_called_once_with(language='EN', master_language='EN', responsible='TEST_USER',
                                                    description='Test intf descr')
        self.fake_interface.assert_called_once_with(self.connection, 'TEST_INTERFACE', package='test_package',
                                                    metadata=self.metadata)
        self.interface.create.assert_called_once_with(None)
        self.interface.open_editor.assert_called_once_with(corrnr=None)
        self.interface_editor.write.assert_called_once_with('test_intf_body')
        self.assertConsoleContents(self.console, stdout='Creating Interface: test_interface\n'
                                                        'Writing Interface: test_interface\n')

    def test_checkin_with_corrnr(self):
        self.checkin(corrnr='corrnr')

        self.interface.create.assert_called_once_with('corrnr')
        self.interface.open_editor.assert_called_once_with(corrnr='corrnr')

    def test_checkin_check_before_save(self):
        fake_write_source = self.patch('sap.fileformat.adt.write_source')

        self.checkin(check_before_save=True)

        fake_write_source.assert_called_once_with('test_intf_body', self.interface, corrnr=None,
                                                  source_label='foo.intf.abap', check_before_save=True)

    def test_checkin_already_exists(self):
        self.interface.create.side_effect = ExceptionResourceAlreadyExists('Interface already exists.')

        with self.assertLogs(sap.get_logger(), 'INFO') as logs:
            self.checkin()

        self.assertEqual([record.getMessage() for record in logs.records], ['Interface already exists.'])
        self.interface.create.assert_called_once_with(None)
        self.interface.open_editor.assert_called_once_with(corrnr=None)


class TestInterfaceHandlerLocate(unittest.TestCase):

    def setUp(self):
        self.handler = InterfaceHandler()
        package = RepoPackage('./src', './src/package.devc.xml', None)
        self.interface_object = RepoObject('intf', 'zif_foo', './src/zif_foo.intf.xml',
                                           ['./src/zif_foo.intf.abap', './src/zif_foo.intf.xml'],
                                           package, self.handler)

    def test_main(self):
        self.assertEqual(self.handler.locate(self.interface_object, 'source/main', 12), ('./src/zif_foo.intf.abap', 12))

    def test_unknown_part(self):
        self.assertIsNone(self.handler.locate(self.interface_object, 'includes/testclasses', 1))

    def test_file_not_in_repository(self):
        self.interface_object.files.remove('./src/zif_foo.intf.abap')

        self.assertIsNone(self.handler.locate(self.interface_object, 'source/main', 12))


if __name__ == '__main__':
    unittest.main()
