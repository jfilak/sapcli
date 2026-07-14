#!/usr/bin/env python3

from argparse import ArgumentParser

import unittest
from unittest.mock import patch, MagicMock, Mock, call, mock_open, PropertyMock
from types import SimpleNamespace

import sap.adt.checks
import sap.cli.object
import sap.errors

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
        # name, source, --activate, --ignore-errors, --warning-errors,
        # --check, --no-check, --corrnr
        self.assertEqual(len(exp_write_cmd.arguments), 8)

    def test_define_activate(self):
        exp_activate_cmd = self.group.define_activate(self.commands)
        act_activate_cmd = self.commands.get_declaration(self.group.activate_objects)

        self.assertEqual(act_activate_cmd, exp_activate_cmd)
        self.assertEqual(len(exp_activate_cmd.arguments), 3)

    def test_define_delete(self):
        exp_delete_cmd = self.group.define_delete(self.commands)
        act_delete_cmd = self.commands.get_declaration(self.group.delete_object)

        self.assertEqual(act_delete_cmd, exp_delete_cmd)
        self.assertEqual(len(exp_delete_cmd.arguments), 2)

    def test_define_whereused(self):
        exp_whereused_cmd = self.group.define_whereused(self.commands)
        act_whereused_cmd = self.commands.get_declaration(self.group.whereused_object)

        self.assertEqual(act_whereused_cmd, exp_whereused_cmd)
        self.assertEqual(len(exp_whereused_cmd.arguments), 1)

    def test_define_edit(self):
        exp_edit_cmd = self.group.define_edit(self.commands)
        act_edit_cmd = self.commands.get_declaration(self.group.edit_object)

        self.assertEqual(act_edit_cmd, exp_edit_cmd)
        # name, --activate, --ignore-errors, --warning-errors,
        # --check, --no-check, --corrnr
        self.assertEqual(len(exp_edit_cmd.arguments), 7)

    def test_define(self):
        self.group.define_create = MagicMock()
        self.group.define_read = MagicMock()
        self.group.define_write = MagicMock()
        self.group.define_activate = MagicMock()
        self.group.define_delete = MagicMock()
        self.group.define_whereused = MagicMock()
        self.group.define_edit = MagicMock()

        del self.group.__class__._instance
        del self.group.__class__.commands

        self.group.define()

        commands = self.group.__class__.get_commands()

        self.group.define_create.assert_called_once_with(commands)
        self.group.define_read.assert_called_once_with(commands)
        self.group.define_write.assert_called_once_with(commands)
        self.group.define_activate.assert_called_once_with(commands)
        self.group.define_delete.assert_called_once_with(commands)
        self.group.define_whereused.assert_called_once_with(commands)
        self.group.define_edit.assert_called_once_with(commands)

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

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=None)
        self.assertEqual(fake_console.capout, 'source code\n')

    def test_edit_object_modified(self):
        connection = MagicMock()
        self.group.new_object_mock.text = 'original code'

        args = self.parse_args('edit', 'myname')

        self.assertEqual(args.name, 'myname')
        self.assertEqual(args.corrnr, None)
        self.assertIsNone(args.check)
        self.assertEqual(args.execute, self.group.edit_object)

        with patch('sap.cli.object.edit_text_in_editor', return_value='edited code') as fake_edit, \
             patch('sap.cli.object.config_get', return_value=False), \
             patch_get_print_console_with_buffer() as fake_console:
            exit_code = args.execute(connection, args)

        self.assertEqual(exit_code, 0)
        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=None)
        fake_edit.assert_called_once_with('original code')
        self.group.new_object_mock.open_editor.assert_called_once_with(corrnr=None)
        self.group.open_editor_mock.write.assert_called_once_with('edited code')
        self.assertEqual(fake_console.capout, 'Writing: str(myname)\n')

    def test_edit_object_unchanged(self):
        connection = MagicMock()
        self.group.new_object_mock.text = 'original code'

        args = self.parse_args('edit', 'myname')

        with patch('sap.cli.object.edit_text_in_editor', return_value='original code'), \
             patch('sap.cli.object.config_get', return_value=False), \
             patch_get_print_console_with_buffer() as fake_console:
            exit_code = args.execute(connection, args)

        self.assertEqual(exit_code, 0)
        self.group.new_object_mock.open_editor.assert_called_once_with(corrnr=None)
        self.group.open_editor_mock.write.assert_not_called()
        self.assertEqual(fake_console.capout, 'No changes to myname\n')

    def test_edit_object_corrnr(self):
        connection = MagicMock()
        self.group.new_object_mock.text = 'original code'

        args = self.parse_args('edit', 'myname', '--corrnr', '123456')

        self.assertEqual(args.corrnr, '123456')

        with patch('sap.cli.object.edit_text_in_editor', return_value='edited code'), \
             patch('sap.cli.object.config_get', return_value=False), \
             patch_get_print_console_with_buffer():
            args.execute(connection, args)

        self.group.new_object_mock.open_editor.assert_called_once_with(corrnr='123456')
        self.group.open_editor_mock.write.assert_called_once_with('edited code')

    def test_edit_object_check_flag_runs_pre_check(self):
        connection = MagicMock()
        self.group.new_object_mock.text = 'original code'

        args = self.parse_args('edit', 'myname', '--check')

        self.assertTrue(args.check)

        with patch('sap.cli.object.edit_text_in_editor', return_value='edited code'), \
             patch('sap.adt.checks.run_object_check') as fake_check, \
             patch_get_print_console_with_buffer():
            fake_check.return_value = SimpleNamespace(has_errors=False, messages=iter([]))
            args.execute(connection, args)

        fake_check.assert_called_once()
        self.group.open_editor_mock.write.assert_called_once_with('edited code')

    def test_edit_object_check_findings_raise_and_skip(self):
        connection = MagicMock()
        self.group.new_object_mock.text = 'original code'

        args = self.parse_args('edit', 'myname', '--check')

        bad_result = SimpleNamespace(has_errors=True, messages=iter([]))

        with patch('sap.cli.object.edit_text_in_editor', return_value='edited code'), \
             patch('sap.adt.checks.run_object_check', return_value=bad_result), \
             patch_get_print_console_with_buffer():
            with self.assertRaises(sap.adt.checks.ObjectCheckFindings):
                args.execute(connection, args)

        self.group.open_editor_mock.write.assert_not_called()
        self.group.new_object_mock.open_editor.assert_called_once_with(corrnr=None)

    def test_edit_object_source_changed_aborts(self):
        connection = MagicMock()
        self.addCleanup(delattr, type(self.group.new_object_mock), 'text')
        type(self.group.new_object_mock).text = PropertyMock(
            side_effect=['original code', 'someone elses code'])

        args = self.parse_args('edit', 'myname')

        with patch('sap.cli.object.edit_text_in_editor', return_value='edited code'), \
             patch('sap.cli.object.config_get', return_value=False), \
             patch_get_print_console_with_buffer():
            with self.assertRaises(sap.errors.SAPCliError):
                args.execute(connection, args)

        self.group.open_editor_mock.write.assert_not_called()
        self.group.new_object_mock.open_editor.assert_called_once_with(corrnr=None)

    @patch('sap.adt.wb.try_activate')
    def test_edit_object_activate(self, fake_activate):
        connection = MagicMock()
        self.group.new_object_mock.text = 'original code'

        args = self.parse_args('edit', 'myname', '--activate')

        self.assertTrue(args.activate)
        self.assertFalse(args.ignore_errors)
        self.assertFalse(args.warning_errors)

        def fake_activate_fn(obj):
            # simulate object activation
            obj.active = 'active'
            return (sap.adt.wb.CheckResults(), None)

        fake_activate.side_effect = fake_activate_fn

        with patch('sap.cli.object.edit_text_in_editor', return_value='edited code'), \
             patch('sap.cli.object.config_get', return_value=False), \
             patch_get_print_console_with_buffer() as fake_console:
            exit_code = args.execute(connection, args)

        self.assertEqual(exit_code, 0)
        self.group.open_editor_mock.write.assert_called_once_with('edited code')
        fake_activate.assert_called_once_with(self.group.new_object_mock)
        self.assertEqual(fake_console.capout, '''Writing: str(myname)
Activating:
* myname
Activation has finished
Warnings: 0
Errors: 0
''')

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

        def fake_activate_fn(obj):
            # simulate object activation
            obj.active = 'active'
            return (sap.adt.wb.CheckResults(), None)

        fake_activate.side_effect = fake_activate_fn

        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open, \
             patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        #self.group.new_object_mock.fetch.assert_called_once()
        # print(self.group.new_object_mock)
        self.assertEqual(fake_activate.call_args_list, [call(self.group.new_object_mock), call(self.group.new_object_mock)])
        self.assertEqual(fake_console.capout, '''Writing:
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

    def test_write_no_check_by_default(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-')
        self.assertIsNone(args.check)

        with patch('sap.cli.object.config_get', return_value=False) as fake_cfg, \
             patch('sap.adt.checks.run_object_check') as fake_check, \
             patch('sys.stdin.readlines', return_value='source code'):
            args.execute(connection, args)

        fake_cfg.assert_called_once_with('check_before_save', False)
        fake_check.assert_not_called()
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_check_flag_runs_pre_check(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-', '--check')
        self.assertTrue(args.check)

        with patch('sap.cli.object.config_get') as fake_cfg, \
             patch('sap.adt.checks.run_object_check') as fake_check, \
             patch('sys.stdin.readlines', return_value='source code'):
            fake_check.return_value = SimpleNamespace(has_errors=False, messages=iter([]))
            args.execute(connection, args)

        # The CLI flag wins; config_get is not even consulted.
        fake_cfg.assert_not_called()
        fake_check.assert_called_once()
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_no_check_flag_overrides_env_true(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-', '--no-check')
        self.assertFalse(args.check)

        # Even with the env-var saying "check", the explicit --no-check
        # must skip both the pre-check and the catch-on-failure path.
        with patch('sap.cli.object.config_get', return_value=True) as fake_cfg, \
             patch('sap.adt.checks.run_object_check') as fake_check, \
             patch('sys.stdin.readlines', return_value='source code'):
            args.execute(connection, args)

        fake_cfg.assert_not_called()
        fake_check.assert_not_called()
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_env_true_runs_pre_check(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-')
        self.assertIsNone(args.check)

        with patch('sap.cli.object.config_get', return_value=True) as fake_cfg, \
             patch('sap.adt.checks.run_object_check') as fake_check, \
             patch('sys.stdin.readlines', return_value='source code'):
            fake_check.return_value = SimpleNamespace(has_errors=False, messages=iter([]))
            args.execute(connection, args)

        fake_cfg.assert_called_once_with('check_before_save', False)
        fake_check.assert_called_once()
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_check_findings_raise_and_skip(self):
        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-', '--check')

        bad_result = SimpleNamespace(has_errors=True, messages=iter([]))

        with patch('sap.adt.checks.run_object_check', return_value=bad_result), \
             patch('sys.stdin.readlines', return_value='source code'), \
             patch_get_print_console_with_buffer():
            with self.assertRaises(sap.adt.checks.ObjectCheckFindings):
                args.execute(connection, args)

        self.group.open_editor_mock.write.assert_not_called()
        self.group.new_object_mock.open_editor.assert_not_called()

    def test_write_failed_put_runs_check_and_raises_findings(self):
        import sap.adt.errors

        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-')

        save_failure = sap.adt.errors.ExceptionResourceSaveFailure('PUT failed')
        self.group.open_editor_mock.write.side_effect = save_failure

        bad_result = SimpleNamespace(has_errors=True, messages=iter([]))

        with patch('sap.cli.object.config_get', return_value=False), \
             patch('sap.adt.checks.run_object_check', return_value=bad_result) as fake_check, \
             patch('sys.stdin.readlines', return_value='source code'), \
             patch_get_print_console_with_buffer():
            with self.assertRaises(sap.adt.checks.ObjectCheckFindings):
                args.execute(connection, args)

        # The pre-check is off (default), so the only invocation is the
        # post-PUT recheck triggered by ExceptionResourceSaveFailure.
        fake_check.assert_called_once()
        self.group.open_editor_mock.write.assert_called_once_with('source code')

    def test_write_failed_put_with_clean_check_reraises_original(self):
        import sap.adt.errors

        connection = MagicMock()

        args = self.parse_args('write', 'myname', '-')

        save_failure = sap.adt.errors.ExceptionResourceSaveFailure('locked')
        self.group.open_editor_mock.write.side_effect = save_failure

        clean_result = SimpleNamespace(has_errors=False, messages=iter([]))

        with patch('sap.cli.object.config_get', return_value=False), \
             patch('sap.adt.checks.run_object_check', return_value=clean_result) as fake_check, \
             patch('sys.stdin.readlines', return_value='source code'), \
             patch_get_print_console_with_buffer():
            with self.assertRaises(sap.adt.errors.ExceptionResourceSaveFailure):
                args.execute(connection, args)

        fake_check.assert_called_once()

    def test_delete_object(self):
        connection = MagicMock()

        args = self.parse_args('delete', 'myname')

        self.assertEqual(args.name, ['myname'])
        self.assertEqual(args.corrnr, None)
        self.assertEqual(args.execute, self.group.delete_object)

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=None)
        self.group.new_object_mock.delete.assert_called_once_with(corrnr=None)
        self.assertEqual(fake_console.capout, 'Deleting myname ...\nDeleted myname\n')

    def test_delete_multiple_objects(self):
        connection = MagicMock()

        args = self.parse_args('delete', 'myname', 'anothername')

        self.assertEqual(args.name, ['myname', 'anothername'])

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        self.assertEqual(self.group.instace_mock.call_args_list,
                         [call(connection, 'myname', args, metadata=None),
                          call(connection, 'anothername', args, metadata=None)])

        self.assertEqual(self.group.new_object_mock.delete.call_args_list,
                         [call(corrnr=None), call(corrnr=None)])

        self.assertEqual(fake_console.capout,
                         'Deleting myname ...\nDeleted myname\n'
                         'Deleting anothername ...\nDeleted anothername\n')

    def test_delete_object_with_corrnr(self):
        connection = MagicMock()

        args = self.parse_args('delete', 'myname', '--corrnr', '123456')

        self.assertEqual(args.corrnr, '123456')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        self.group.new_object_mock.delete.assert_called_once_with(corrnr='123456')

    @patch('sap.adt.whereused.where_used')
    def test_whereused_object_zero_results(self, fake_where_used):
        connection = MagicMock()

        mock_result = MagicMock()
        mock_result.result_description = '[A4H] Where-Used List: MYNAME (Program)'
        mock_result.referenced_objects = []
        fake_where_used.return_value = mock_result

        args = self.parse_args('whereused', 'myname')

        self.assertEqual(args.name, 'myname')
        self.assertEqual(args.execute, self.group.whereused_object)

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        self.group.instace_mock.assert_called_once_with(connection, 'myname', args, metadata=None)
        fake_where_used.assert_called_once_with(connection, self.group.new_object_mock.full_adt_uri)
        self.assertEqual(fake_console.capout, '')
        self.assertEqual(fake_console.caperr, '')

    @patch('sap.adt.whereused.where_used')
    def test_whereused_object_with_results(self, fake_where_used):
        connection = MagicMock()

        pkg_ref1 = MagicMock()
        pkg_ref1.name = '$ABAPGIT_ENV'

        adt_obj1 = MagicMock()
        adt_obj1.typ = 'CLAS/OC'
        adt_obj1.name = 'ZCL_ABAPGIT_ABAP_LANGUAGE_VERS'
        adt_obj1.package_ref = pkg_ref1

        ref_obj1 = MagicMock()
        ref_obj1.adt_object = adt_obj1

        pkg_ref2 = MagicMock()
        pkg_ref2.name = '$ABAPGIT_ENV'

        adt_obj2 = MagicMock()
        adt_obj2.typ = None
        adt_obj2.name = 'Local Test Classes'
        adt_obj2.package_ref = pkg_ref2

        ref_obj2 = MagicMock()
        ref_obj2.adt_object = adt_obj2

        mock_result = MagicMock()
        mock_result.result_description = '[A4H] Where-Used List: MYNAME (Program)'
        mock_result.referenced_objects = [ref_obj1, ref_obj2]
        fake_where_used.return_value = mock_result

        args = self.parse_args('whereused', 'myname')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(connection, args)

        self.assertEqual(fake_console.capout,
                         '  CLAS/OC ZCL_ABAPGIT_ABAP_LANGUAGE_VERS\n'
                         '   Local Test Classes\n')

    def test_activate_objects(self):
        connection = MagicMock()

        args = self.parse_args('activate', 'myname', 'anothername')

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:

            def fake_activate_fn(obj):
                # simulate object activation
                obj.active = 'active'
                return (sap.adt.wb.CheckResults(), None)

            fake_activate.side_effect = fake_activate_fn

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 0)

        self.assertEqual(fake_activate.call_args_list, [call(self.group.new_object_mock),
                                                        call(self.group.new_object_mock)])

        self.assertEqual(self.group.instace_mock.call_args_list, [call(connection, 'myname', args, metadata=None),
                                                                  call(connection, 'anothername', args, metadata=None)])


        self.assertEqual(fake_console.capout, '''Activating 2 objects:
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

        response_iter = iter([('active', (message_builder.build_results_without_messages(), None)),
                              ('inactive', (message_builder.build_results_with_errors(), None))])

        def fake_activate_fn(obj):
            response = next(response_iter) 
            # simulate object activation
            obj.active = response[0]
            return response[1]

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:
            fake_activate.side_effect = fake_activate_fn

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 1)

        self.assertEqual(fake_console.capout, f'''Activating 2 objects:
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

        response_iter = iter([('active', (message_builder.build_results_without_messages(), None)),
                              ('inactive', (message_builder.build_results_with_errors(), None))])

        def fake_activate_fn(obj):
            response = next(response_iter) 
            # simulate object activation
            obj.active = response[0]
            return response[1]

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:
            fake_activate.side_effect = fake_activate_fn

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 1)

        self.assertEqual(fake_console.capout, f'''Activating 2 objects:
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

        response_iter = iter([('active', (message_builder.build_results_without_messages(), None)),
                             ('active',  (message_builder.build_results_with_warnings(), None))])

        def fake_activate_fn(obj):
            response = next(response_iter) 
            # simulate object activation
            obj.active = response[0]
            return response[1]

        with patch('sap.adt.wb.try_activate') as fake_activate, \
             patch_get_print_console_with_buffer() as fake_console:
            fake_activate.side_effect = fake_activate_fn

            exit_code = args.execute(connection, args)
            self.assertEqual(exit_code, 1)

        self.assertEqual(fake_console.capout, f'''Activating 2 objects:
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

        self._check_patcher = patch('sap.cli.object.config_get', return_value=False)
        self._check_patcher.start()

    def tearDown(self):
        self._check_patcher.stop()

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


class TestEditTextInEditor(unittest.TestCase):

    def _run_editor(self, environ, read_data='edited code', returncode=0):
        fake_run_result = Mock()
        fake_run_result.returncode = returncode

        with patch('sap.cli.object.tempfile.mkstemp', return_value=(5, '/tmp/obj.abap')) as fake_mkstemp, \
             patch('sap.cli.object.os.fdopen', mock_open()) as fake_fdopen, \
             patch('sap.cli.object.subprocess.run', return_value=fake_run_result) as fake_run, \
             patch('sap.cli.object.open', mock_open(read_data=read_data)) as fake_open, \
             patch('sap.cli.object.os.unlink') as fake_unlink, \
             patch.dict('sap.cli.object.os.environ', environ, clear=True):
            result = sap.cli.object.edit_text_in_editor('original code')

        return SimpleNamespace(result=result, mkstemp=fake_mkstemp, fdopen=fake_fdopen,
                               run=fake_run, open=fake_open, unlink=fake_unlink)

    def test_writes_reads_and_returns_edited_content(self):
        ctx = self._run_editor({'EDITOR': 'nano'})

        self.assertEqual(ctx.result, 'edited code')
        ctx.mkstemp.assert_called_once_with(suffix='.abap')
        ctx.fdopen().write.assert_called_once_with('original code')
        ctx.run.assert_called_once_with(['nano', '/tmp/obj.abap'], check=False)
        ctx.open.assert_called_once_with('/tmp/obj.abap', 'r', encoding='utf8')
        ctx.unlink.assert_called_once_with('/tmp/obj.abap')

    def test_editor_precedence_prefers_sapcli_editor(self):
        ctx = self._run_editor({'SAPCLI_EDITOR': 'code --wait', 'EDITOR': 'nano', 'VISUAL': 'vim'})

        ctx.run.assert_called_once_with(['code', '--wait', '/tmp/obj.abap'], check=False)

    def test_editor_precedence_falls_back_to_editor(self):
        ctx = self._run_editor({'EDITOR': 'nano', 'VISUAL': 'vim'})

        ctx.run.assert_called_once_with(['nano', '/tmp/obj.abap'], check=False)

    def test_editor_precedence_falls_back_to_visual(self):
        ctx = self._run_editor({'VISUAL': 'vim'})

        ctx.run.assert_called_once_with(['vim', '/tmp/obj.abap'], check=False)

    def test_editor_default_is_vi(self):
        ctx = self._run_editor({})

        ctx.run.assert_called_once_with(['vi', '/tmp/obj.abap'], check=False)

    def test_non_zero_exit_raises_and_cleans_up(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self._run_editor({'EDITOR': 'nano'}, returncode=1)

        self.assertIn('nano', str(caught.exception))
        self.assertIn('1', str(caught.exception))

    def test_launch_oserror_raises_sapclierror_and_cleans_up(self):
        with patch('sap.cli.object.tempfile.mkstemp', return_value=(5, '/tmp/obj.abap')), \
             patch('sap.cli.object.os.fdopen', mock_open()), \
             patch('sap.cli.object.subprocess.run', side_effect=OSError('no such file')), \
             patch('sap.cli.object.os.unlink') as fake_unlink, \
             patch.dict('sap.cli.object.os.environ', {'EDITOR': 'nano'}, clear=True):
            with self.assertRaises(sap.errors.SAPCliError) as caught:
                sap.cli.object.edit_text_in_editor('original code')

        self.assertIn('nano', str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, OSError)
        fake_unlink.assert_called_once_with('/tmp/obj.abap')

    def test_launch_valueerror_raises_sapclierror_and_cleans_up(self):
        with patch('sap.cli.object.tempfile.mkstemp', return_value=(5, '/tmp/obj.abap')), \
             patch('sap.cli.object.os.fdopen', mock_open()), \
             patch('sap.cli.object.subprocess.run', side_effect=ValueError('bad quoting')), \
             patch('sap.cli.object.os.unlink') as fake_unlink, \
             patch.dict('sap.cli.object.os.environ', {'EDITOR': 'nano'}, clear=True):
            with self.assertRaises(sap.errors.SAPCliError) as caught:
                sap.cli.object.edit_text_in_editor('original code')

        self.assertIn('nano', str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, ValueError)
        fake_unlink.assert_called_once_with('/tmp/obj.abap')


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
