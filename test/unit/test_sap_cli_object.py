#!/usr/bin/env python3

from argparse import ArgumentParser

import unittest
from unittest.mock import patch, MagicMock, Mock, call, mock_open
from types import SimpleNamespace

import sap.cli.object

from mock import patch_get_print_console_with_buffer
from fixtures_adt import DummyADTObject, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, OBJECT_METADATA
from fixtures_adt_wb import MessageBuilder


class DummyADTObjectCommandGroup(sap.cli.object.CommandGroupObjectTemplate):

    def __init__(self):
        super(DummyADTObjectCommandGroup, self).__init__('command')

        self._init_mocks()
        self.define()

    def _init_mocks(self):
        self.open_editor_mock = MagicMock()
        self.open_editor_mock.write = Mock()
        self.open_editor_mock.__enter__ = Mock()
        self.open_editor_mock.__enter__.return_value = self.open_editor_mock

        self.new_object_mock = MagicMock()
        self.new_object_mock.name = 0
        self.new_object_mock.open_editor = Mock()
        self.new_object_mock.open_editor.return_value = self.open_editor_mock
        self.new_object_mock.__str__ = lambda obj: f'str({obj.name})'

        self.instace_mock = MagicMock()
        self.instace_mock.return_value = self.new_object_mock

        self.metadata_mock = MagicMock()
        self.build_new_metadata_mock = MagicMock()
        self.build_new_metadata_mock.return_value = self.metadata_mock

    def instance(self, connection, name, args, metadata=None):
        """Returns new instance of the ADT Object proxy class"""

        self.new_object_mock.name = name
        self.new_object_mock.objtype.code = 'FAKE'
        return self.instace_mock(connection, name, args, metadata=metadata)

    def build_new_metadata(self, connection, args):
        """Creates an instance of the ADT Object Metadata class for a new object"""

        return self.build_new_metadata_mock(connection, args)


class TestCommandGroupObjectTemplateDefine(unittest.TestCase):

    def setUp(self):
        self.group = DummyADTObjectCommandGroup()
        self.commands = sap.cli.core.CommandsList()

    def test_define_create(self):
        exp_create_cmd = self.group.define_create(self.commands)
        act_create_cmd = self.commands.get_declaration(self.group.create_object)

        self.assertEqual(act_create_cmd, exp_create_cmd)
        self.assertEqual(len(exp_create_cmd.arguments), 3)

    def test_define_read(self):
        exp_read_cmd = self.group.define_read(self.commands)
        act_read_cmd = self.commands.get_declaration(self.group.read_object_text)

        self.assertEqual(act_read_cmd, exp_read_cmd)
        self.assertEqual(len(exp_read_cmd.arguments), 1)

    def test_define_write(self):
        exp_write_cmd = self.group.define_write(self.commands)
        act_write_cmd = self.commands.get_declaration(self.group.write_object_text)

        self.assertEqual(act_write_cmd, exp_write_cmd)
        self.assertEqual(len(exp_write_cmd.arguments), 6)

    def test_define_activate(self):
        exp_activate_cmd = self.group.define_activate(self.commands)
        act_activate_cmd = self.commands.get_declaration(self.group.activate_objects)

        self.assertEqual(act_activate_cmd, exp_activate_cmd)
        self.assertEqual(len(exp_activate_cmd.arguments), 3)

    def test_define(self):
        self.group.define_create = MagicMock()
        self.group.define_read = MagicMock()
        self.group.define_write = MagicMock()
        self.group.define_activate = MagicMock()

        del self.group.__class__._instance
        del self.group.__class__.commands

        self.group.define()

        commands = self.group.__class__.get_commands()

        self.group.define_create.assert_called_once_with(commands)
        self.group.define_read.assert_called_once_with(commands)
        self.group.define_write.assert_called_once_with(commands)
        self.group.define_activate.assert_called_once_with(commands)

        del self.group.__class__._instance
        del self.group.__class__.commands


class TestCommandGroupObjectTemplate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = ArgumentParser()

        cls.group = DummyADTObjectCommandGroup()
        cls.group.install_parser(cls.parser)

    @property
    def group(self):
        return self.__class__.group

    def setUp(self):
        self.group._init_mocks()

    def parse_args(self, *argv):
        return self.__class__.parser.parse_args(argv)

    def test_build_new_object(self):
        connection = MagicMock()
        args = MagicMock()
        args.name = 'myname'
        metadata = MagicMock()

        self.group.instace_mock.return_value = 'new_object'
        new_obj = self.group.build_new_object(connection, args, metadata)

        self.assertEqual('new_object', new_obj)

    def test_create_object(self):
        connection = MagicMock()

        args = self.parse_args('create', 'myname', 'description')

        self.assertEqual(args.name, 'myname')
        self.assertEqual(args.description, 'description')
        self.assertEqual(args.corrnr, None)
        self.assertEqual(args.execute, self.group.create_object)

        args.execute(connection, args)

        self.group.build_new_metadata_mock.assert_called_once_with(connection, args)
        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=self.group.metadata_mock)

        self.assertEqual(self.group.new_object_mock.description, 'description')

        self.group.new_object_mock.create.assert_called_once_with(corrnr=None)

    def test_create_object_with_corrnr(self):
        connection = MagicMock()

        args = self.parse_args('create', 'myname', 'description', '--corrnr', '123456')

        self.assertEqual(args.corrnr, '123456')

        args.execute(connection, args)

        self.group.new_object_mock.create.assert_called_once_with(corrnr='123456')

    def test_read_object_text(self):
        self.group.new_object_mock.text = 'source code'

        connection = MagicMock()

        args = self.parse_args('read', 'myname')

        self.assertEqual(args.name, 'myname')
        self.assertEqual(args.execute, self.group.read_object_text)

        with patch('sap.cli.object.print') as fake_print:
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=None)
        fake_print.assert_called_once_with('source code')

    def test_write_object_text_stdin(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-')

        self.assertEqual(args.name, 'myname')
        self.assertEqual(args.source, ['-'])
        self.assertEqual(args.corrnr, None)
        self.assertEqual(args.execute, self.group.write_object_text)

        with patch('sys.stdin.readlines') as fake_readlines:
            fake_readlines.return_value = 'source code'
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=None)
        self.group.new_object_mock.open_editor.assert_called_once_with(corrnr=None)
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_object_text_file(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', 'source.abap')

        self.assertEqual(args.source, ['source.abap'])

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open:
            args.execute(connection, args)

        self.assertEqual(fake_open.call_args_list, [call('source.abap', 'r', encoding='utf8')])
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_object_name_from_file(self):
        connection = MagicMock()

        args = self.parse_args('write', '-', 'objname.abap')

        self.assertEqual(args.source, ['objname.abap'])

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open:
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'objname', args, metadata=None)
        self.assertEqual(fake_open.call_args_list, [call('objname.abap', 'r', encoding='utf8')])

    def test_write_object_text_stdin_corrnr(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-', '--corrnr', '123456')

        self.assertEqual(args.corrnr, '123456')

        with patch('sys.stdin.readlines') as fake_readlines:
            fake_readlines.return_value = 'source code'
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=None)
        self.group.new_object_mock.open_editor.assert_called_once_with(corrnr='123456')
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    @patch('sap.adt.wb.try_activate')
    def test_write_object_text_stdin_corrnr_activate(self, fake_activate):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-', '--corrnr', '123456', '--activate')

        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)

        with patch('sys.stdin.readlines') as fake_readlines:
            fake_readlines.return_value = 'source code'
            args.execute(connection, args)

        fake_activate.assert_called_once_with(self.group.new_object_mock)

    @patch('sap.adt.wb.try_activate')
    def test_write_object_text_name_from_files_activate(self, fake_activate):
        connection = MagicMock()

        args = self.parse_args('write', '-', 'z_one.abap', 'z_one.incl.abap', 'z_two.abap', '--corrnr', '123456', '--activate')

        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open, \
             patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        self.assertEqual(fake_activate.call_args_list, [call(self.group.new_object_mock), call(self.group.new_object_mock)])
        self.assertEqual(fake_console.return_value.std_output.getvalue(), '''Writing:
* str(z_one)
* str(z_one)
* str(z_two)
Activating 2 objects:
* z_one (1/2)
* z_two (2/2)
Activation has finished
Warnings: 0
Errors: 0
''')

    def test_activate_objects(self):
        connection = MagicMock()

        args = self.parse_args('activate', 'myname', 'anothername')

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:
            fake_activate.return_value = (sap.adt.wb.CheckResults(), None)

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 0)

        self.assertEqual(fake_activate.call_args_list, [call(self.group.new_object_mock),
                                                        call(self.group.new_object_mock)])

        self.assertEqual(self.group.instace_mock.call_args_list, [call(connection, 'myname', args, metadata=None),
                                                                  call(connection, 'anothername', args, metadata=None)])


        self.assertEqual(fake_console.return_value.std_output.getvalue(), '''Activating 2 objects:
* myname (1/2)
* anothername (2/2)
Activation has finished
Warnings: 0
Errors: 0
''')

    def test_activate_objects_with_error(self):
        connection = MagicMock()

        args = self.parse_args('activate', 'myname', 'anothername')

        message_builder = MessageBuilder()

        response_iter = iter([(message_builder.build_results_without_messages(), None),
                              (message_builder.build_results_with_errors(), None)])

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:
            fake_activate.side_effect = lambda x: next(response_iter)

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 1)

        self.assertEqual(fake_console.return_value.std_output.getvalue(), f'''Activating 2 objects:
* myname (1/2)
* anothername (2/2)
{message_builder.error_message[1]}Activation has stopped
Warnings: 0
Errors: 1
Active objects:
  FAKE anothername
''')

    def test_activate_objects_with_ignored_error(self):
        connection = MagicMock()

        args = self.parse_args('activate', '--ignore-errors', 'myname', 'anothername')

        message_builder = MessageBuilder()

        response_iter = iter([(message_builder.build_results_without_messages(), None),
                              (message_builder.build_results_with_errors(), None)])

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:
            fake_activate.side_effect = lambda x: next(response_iter)

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 1)

        self.assertEqual(fake_console.return_value.std_output.getvalue(), f'''Activating 2 objects:
* myname (1/2)
* anothername (2/2)
{message_builder.error_message[1]}Activation has finished
Warnings: 0
Errors: 1
Inactive objects:
  FAKE anothername
''')

    def test_activate_objects_with_warning_as_error(self):
        connection = MagicMock()

        args = self.parse_args('activate', '--ignore-errors', '--warning-errors', 'myname', 'anothername')

        message_builder = MessageBuilder()

        response_iter = iter([(message_builder.build_results_without_messages(), None),
                              (message_builder.build_results_with_warnings(), None)])

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:
            fake_activate.side_effect = lambda x: next(response_iter)

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 1)

        self.assertEqual(fake_console.return_value.std_output.getvalue(), f'''Activating 2 objects:
* myname (1/2)
* anothername (2/2)
{message_builder.warning_message[1]}Activation has finished
Warnings: 1
Errors: 1
''')



class MasterDummyADTObjectCommandGroup(sap.cli.object.CommandGroupObjectMaster):

    def __init__(self):
        super(MasterDummyADTObjectCommandGroup, self).__init__('command')

        self._init_mocks()
        self.define()

    def _init_mocks(self):
        self.open_editor_mock = MagicMock()
        self.open_editor_mock.write = Mock()
        self.open_editor_mock.__enter__ = Mock()
        self.open_editor_mock.__enter__.return_value = self.open_editor_mock

        self.new_object_mock = MagicMock()
        self.new_object_mock.open_editor = Mock()
        self.new_object_mock.open_editor.return_value = self.open_editor_mock

        self.instace_mock = MagicMock()
        self.instace_mock.return_value = self.new_object_mock

    def instance(self, connection, name, args, metadata=None):
        """Returns new instance of the ADT Object proxy class"""

        return self.instace_mock(connection, name, args, metadata=metadata)


class TestCommandGroupObjectMaster(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = ArgumentParser()

        cls.group = MasterDummyADTObjectCommandGroup()
        cls.group.install_parser(cls.parser)

    @property
    def group(self):
        return self.__class__.group

    def setUp(self):
        self.group._init_mocks()

    def parse_args(self, *argv):
        return self.__class__.parser.parse_args(argv)

    def test_build_new_metadata(self):
        connection = MagicMock()
        connection.user = 'user'

        args = SimpleNamespace(package='package')

        metadata = self.group.build_new_metadata(connection, args)

        self.assertEqual(metadata.responsible, 'USER')
        self.assertEqual(metadata.package, 'PACKAGE')
        self.assertEqual(metadata.language, 'EN')
        self.assertEqual(metadata.master_language, 'EN')

    def test_create_with_package(self):
        connection = MagicMock()

        args = self.parse_args('create', 'myname', 'description', 'devc')

        self.assertEqual(args.name, 'myname')
        self.assertEqual(args.description, 'description')
        self.assertEqual(args.package, 'devc')
        self.assertEqual(args.corrnr, None)
        self.assertEqual(args.execute, self.group.create_object)

        with patch.object(self.group, 'build_new_metadata', return_value='mock') as fake_metadata:
            args.execute(connection, args)

        fake_metadata.assert_called_once_with(connection, args)
        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata='mock')
        self.group.new_object_mock.create.assert_called_once_with(corrnr=None)


class TestObjNameFromSourceFile(unittest.TestCase):

    def test_empty_string(self):
        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            sap.cli.object.object_name_from_source_file('')

        self.assertEqual('"" does not match the pattern NAME.SUFFIX', str(caught.exception))

    def test_no_dot(self):
        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            sap.cli.object.object_name_from_source_file('foo')

        self.assertEqual('"foo" does not match the pattern NAME.SUFFIX', str(caught.exception))

    def test_single_dot(self):
        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            sap.cli.object.object_name_from_source_file('.')

        self.assertEqual('"." does not match the pattern NAME.SUFFIX', str(caught.exception))

    def test_empty_suffix(self):
        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            sap.cli.object.object_name_from_source_file('foo.')

        self.assertEqual('"foo." does not match the pattern NAME.SUFFIX', str(caught.exception))

    def test_empty_name(self):
        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            sap.cli.object.object_name_from_source_file('.foo')

        self.assertEqual('".foo" does not match the pattern NAME.SUFFIX', str(caught.exception))

    def test_valid_filename(self):
        name, suffix = sap.cli.object.object_name_from_source_file('foo.bar.blah')

        self.assertEqual(name, 'foo')
        self.assertEqual(suffix, 'bar.blah')

    def test_valid_path_withdirectory(self):
        name, suffix = sap.cli.object.object_name_from_source_file('./src/foo.bar.blah')

        self.assertEqual(name, 'foo')
        self.assertEqual(suffix, 'bar.blah')


class TestWriteArgsToObjects(unittest.TestCase):

    def test_name_with_several_files(self):
        command = MagicMock()
        connection = MagicMock()
        args = MagicMock()
        args.name = 'zabap_object'
        args.source = ['zabap_object.abap', 'accidental_file.abap']

        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            objects = [obj_text for obj_text in sap.cli.object.write_args_to_objects(command, connection, args, metadata='metadata')]

        self.assertEqual('Source file can be a list only when Object name is -', str(caught.exception))

    def test_name_with_stdin(self):
        command = MagicMock()
        command.instance = Mock()
        command.instance.return_value = 'instance'

        connection = MagicMock()
        args = MagicMock()
        args.name = 'zabap_object'
        args.source = ['-']

        with patch('sys.stdin.readlines') as fake_readlines:
            fake_readlines.return_value = ['source code']
            objects = [obj_text for obj_text in sap.cli.object.write_args_to_objects(command, connection, args, metadata='metadata')]

        fake_readlines.assert_called_once()
        command.instance.assert_called_once_with(connection, 'zabap_object', args, metadata='metadata')
        self.assertEqual([('instance', ['source code'])], objects)

    def test_name_with_file(self):
        command = MagicMock()
        command.instance = Mock()
        command.instance.return_value = 'instance'

        connection = MagicMock()
        args = MagicMock()
        args.name = 'zabap_object'
        args.source = ['zabap_object.abap']

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open:
            objects = [obj_text for obj_text in sap.cli.object.write_args_to_objects(command, connection, args, metadata='metadata')]

        fake_open.assert_called_once_with('zabap_object.abap', 'r', encoding='utf8')
        command.instance.assert_called_once_with(connection, 'zabap_object', args, metadata='metadata')
        self.assertEqual([('instance', ['source code'])], objects)

    def test_name_dash_file_dash(self):
        command = MagicMock()
        connection = MagicMock()
        args = MagicMock()
        args.name = '-'
        args.source = ['-']

        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            objects = [obj_text for obj_text in sap.cli.object.write_args_to_objects(command, connection, args, metadata='metadata')]

        self.assertEqual('Source file cannot be - when Object name is - too', str(caught.exception))

    def test_name_with_2_file(self):
        command = MagicMock()
        command.instance_from_file_path = Mock()
        command.instance_from_file_path.return_value = 'instance'

        connection = MagicMock()
        args = MagicMock()
        args.name = '-'
        args.source = ['zabap_object.abap', 'zanother_object.abap']

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open:
            objects = [obj_text for obj_text in sap.cli.object.write_args_to_objects(command, connection, args, metadata='metadata')]

        self.assertEqual(fake_open.call_args_list, [call('zabap_object.abap', 'r', encoding='utf8'), call('zanother_object.abap', 'r', encoding='utf8')])
        self.assertEqual(command.instance_from_file_path.call_args_list, [call(connection, 'zabap_object.abap', args, metadata='metadata'),
                                                                          call(connection, 'zanother_object.abap', args, metadata='metadata')])
        self.assertEqual(objects, [('instance', ['source code']),
                                   ('instance', ['source code'])])


if __name__ == '__main__':
    unittest.main()
