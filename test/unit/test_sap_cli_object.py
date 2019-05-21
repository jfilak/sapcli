#!/usr/bin/env python3

from argparse import ArgumentParser

import unittest
from unittest.mock import patch, MagicMock, Mock, call, mock_open
from types import SimpleNamespace

import sap.cli.object

from mock import Connection, Response
from fixtures_adt import DummyADTObject, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, OBJECT_METADATA


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
        self.assertEqual(len(exp_write_cmd.arguments), 4)

    def test_define_activate(self):
        exp_activate_cmd = self.group.define_activate(self.commands)
        act_activate_cmd = self.commands.get_declaration(self.group.activate_objects)

        self.assertEqual(act_activate_cmd, exp_activate_cmd)
        self.assertEqual(len(exp_activate_cmd.arguments), 1)

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
        return sefl.__class__.group

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

        self.assertEqual(fake_open.call_args_list, [call('source.abap', 'r')])
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_object_name_from_file(self):
        connection = MagicMock()

        args = self.parse_args('write', '-', 'objname.abap')

        self.assertEqual(args.source, ['objname.abap'])

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open:
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'objname', args, metadata=None)
        self.assertEqual(fake_open.call_args_list, [call('objname.abap', 'r')])

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

    @patch('sap.adt.wb.activate')
    def test_write_object_text_stdin_corrnr_activate(self, fake_activate):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-', '--corrnr', '123456', '--activate')

        with patch('sys.stdin.readlines') as fake_readlines:
            fake_readlines.return_value = 'source code'
            args.execute(connection, args)

        fake_activate.assert_called_once_with(self.group.new_object_mock)

    @patch('sap.adt.wb.activate')
    def test_write_object_text_name_from_files_activate(self, fake_activate):
        connection = MagicMock()

        args = self.parse_args('write', '-', 'z_one.abap', 'z_one.incl.abap', 'z_two.abap', '--corrnr', '123456', '--activate')

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open, \
             patch('sap.cli.printout') as fake_printout:
            args.execute(connection, args)

        self.assertEqual(fake_activate.call_args_list, [call(self.group.new_object_mock), call(self.group.new_object_mock)])

        exp = [call('Writing:'),
               call('*', 'str(z_one)'),
               call('*', 'str(z_one)'),
               call('*', 'str(z_two)'),
               call('Activating:'),
               call('*', 'z_one'),
               call('*', 'z_two')]

        self.assertEqual(fake_printout.call_args_list, exp)

        for i, cl in enumerate(fake_printout.call_args_list):
            if i >= len(exp):
                self.fail('Redundant:\n' + str(fake_printout.call_args_list[i:]))

            self.assertEqual(fake_printout.call_args_list[i], exp[i], msg=f'Pos={i}')

        if not i + 1 == len(exp):
            self.fail(f'Missing: \n' + str(exp[i:]))


    def test_activate_objects(self):
        connection = MagicMock()

        args = self.parse_args('activate', 'myname', 'anothername')

        with patch('sap.adt.wb.activate') as fake_activate, \
             patch('sap.cli.printout') as fake_printout:
            args.execute(connection, args)

        self.assertEqual(fake_activate.call_args_list, [call(self.group.new_object_mock),
                                                        call(self.group.new_object_mock)])

        self.assertEqual(self.group.instace_mock.call_args_list, [call(connection, 'myname', args, metadata=None),
                                                                  call(connection, 'anothername', args, metadata=None)])

        exp = [call('Activating:'),
               call('*', 'myname'),
               call('*', 'anothername')]

        self.assertEqual(fake_printout.call_args_list, exp)


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
        return sefl.__class__.group

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

        fake_open.assert_called_once_with('zabap_object.abap', 'r')
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

        self.assertEqual(fake_open.call_args_list, [call('zabap_object.abap', 'r'), call('zanother_object.abap', 'r')])
        self.assertEqual(command.instance_from_file_path.call_args_list, [call(connection, 'zabap_object.abap', args, metadata='metadata'),
                                                                          call(connection, 'zanother_object.abap', args, metadata='metadata')])
        self.assertEqual(objects, [('instance', ['source code']),
                                   ('instance', ['source code'])])


if __name__ == '__main__':
    unittest.main()
