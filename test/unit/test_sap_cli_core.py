#!/usr/bin/env python3

from io import StringIO
import sys
import unittest
from unittest.mock import call, patch, MagicMock, Mock, mock_open

from argparse import ArgumentParser

import sap.errors
import sap.cli.core


class TestCommandDeclaration(unittest.TestCase):

    def test_init(self):
        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer')

        self.assertEqual(cmd_decl.name, 'printer')
        self.assertEqual(cmd_decl.handler, print)
        self.assertIsNone(cmd_decl.description)

    def test_init_with_description(self):
        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer', description='prints out data')

        self.assertEqual(cmd_decl.name, 'printer')
        self.assertEqual(cmd_decl.handler, print)
        self.assertEqual(cmd_decl.description, 'prints out data')

    def test_insert_argument(self):
        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer')

        cmd_decl.insert_argument(0, 'first', arg1='1')
        cmd_decl.insert_argument(0, 'second', arg2='2')
        cmd_decl.insert_argument(3, 'third', arg3='3')

        self.assertEqual(cmd_decl.arguments, [(('second',), {'arg2':'2'}),
                                              (('first',), {'arg1':'1'}),
                                              (('third',), {'arg3':'3'})])

    def test_append_argument(self):
        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer')

        cmd_decl.append_argument('first', arg1='1')
        cmd_decl.append_argument('second', arg2='2')
        cmd_decl.append_argument('third', arg3='3')

        self.assertEqual(cmd_decl.arguments, [(('first',), {'arg1':'1'}),
                                              (('second',), {'arg2':'2'}),
                                              (('third',), {'arg3':'3'})])

    def test_declare_corrnr_no_position(self):
        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer')

        cmd_decl.append_argument('first', arg1='1')
        cmd_decl.declare_corrnr()

        self.assertEqual(cmd_decl.arguments, [(('first',), {'arg1':'1'}),
                                              (('--corrnr',), {'nargs':'?', 'default':None})])

    def test_declare_corrnr_with_position(self):
        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer')

        cmd_decl.append_argument('first', arg1='1')
        cmd_decl.declare_corrnr(position=0)

        self.assertEqual(cmd_decl.arguments, [(('--corrnr',), {'nargs':'?', 'default':None}),
                                              (('first',), {'arg1':'1'})])

    def test_install_arguments(self):
        parser = MagicMock()

        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer')

        cmd_decl.append_argument('first', arg1='1')
        cmd_decl.append_argument('second', arg2='2')

        cmd_decl.install_arguments(parser)

        self.assertEqual(parser.add_argument.call_args_list,
                         [call('first', arg1='1'), call('second', arg2='2')])


class TestCommandsList(unittest.TestCase):

    def handler(self):
        """test handler"""

        pass

    def setUp(self):
        self.cmd_list = sap.cli.core.CommandsList()

    def test_add_command_without_params(self):
        self.cmd_list.add_command(self.handler)
        commands = self.cmd_list.values()
        command = next(iter(commands))

        self.assertEqual(len(commands), 1)
        self.assertEqual(command.name, 'handler')
        self.assertEqual(command.handler, self.handler)
        self.assertEqual(command.description, 'test handler')

    def test_add_command_with_name(self):
        self.cmd_list.add_command(self.handler, name='command')
        commands = self.cmd_list.values()
        command = next(iter(commands))

        self.assertEqual(len(commands), 1)
        self.assertEqual(command.name, 'command')
        self.assertEqual(command.handler, self.handler)

    def test_add_command_with_description(self):
        self.cmd_list.add_command(self.handler, name='command', description='custom help')
        commands = self.cmd_list.values()
        command = next(iter(commands))

        self.assertEqual(len(commands), 1)
        self.assertEqual(command.name, 'command')
        self.assertEqual(command.handler, self.handler)
        self.assertEqual(command.description, 'custom help')

    def test_add_command_with_wrapper(self):
        def test_wrapper(_):
            def _wrapped():
                return 'wrapped'

            return _wrapped

        self.cmd_list.add_command(self.handler, handler_wrapper=test_wrapper)
        commands = self.cmd_list.values()
        command = next(iter(commands))

        self.assertEqual(len(commands), 1)
        self.assertEqual(command.name, 'handler')
        self.assertEqual(command.handler(), 'wrapped')

    def test_add_command_duplicate(self):
        self.cmd_list.add_command(self.handler)

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.cmd_list.add_command(self.handler, name='command')

        self.assertEqual(str(caught.exception), 'Handler already registered: handler')

    def test_get_declaration_missing(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            self.cmd_list.get_declaration(self.handler)

        self.assertEqual(str(caught.exception), 'No such Command Declaration: handler')

    def test_get_declaration_ok(self):
        self.cmd_list.add_command(self.handler)
        command = self.cmd_list.get_declaration(self.handler)

        self.assertEqual(command.name, 'handler')

    def test_get_declaration_ok_with_name(self):
        self.cmd_list.add_command(self.handler, name='command')
        command = self.cmd_list.get_declaration(self.handler)

        self.assertEqual(command.name, 'command')

    def test_values_empty(self):
        self.assertFalse(self.cmd_list.values())


class DummyCommandGroup(sap.cli.core.CommandGroup):
    """Test command group"""

    def __init__(self):
        super(DummyCommandGroup, self).__init__('pytest')


class EmptyDummyCommandGroup(sap.cli.core.CommandGroup):
    """Test empty command group for the case where you need
       want to have a group of groups (i.e. you have no commands).
    """

    def __init__(self):
        super(EmptyDummyCommandGroup, self).__init__('empty-pytest', description='dummy empty group')


@DummyCommandGroup.argument('name')
@DummyCommandGroup.argument_corrnr()
@DummyCommandGroup.command()
def dummy_corrnr(connection, args):
    """Dummy command help"""

    return (args.corrnr, args.name)


def parse_args(argv):
    parser = ArgumentParser()

    group = DummyCommandGroup()
    group.install_parser(parser)

    return parser.parse_args(argv)


class TestCommandGroup(unittest.TestCase):

    def test_get_command_declaration(self):
        command = DummyCommandGroup.get_command_declaration(dummy_corrnr)
        self.assertIsNotNone(command)

    def test_get_commands(self):
        commands = DummyCommandGroup.get_commands()
        self.assertEqual(len(commands.values()), 1)

    def test_get_commands_wrapper_not_specified(self):
        wrapper = DummyCommandGroup.get_commands_wrapper()
        self.assertEqual(wrapper('dummy_function'), 'dummy_function')

    def test_get_commands_wrapper(self):
        class _TestCommandGroup(DummyCommandGroup):
            commands_wrapper = 'test_wrapper'

        wrapper = _TestCommandGroup.get_commands_wrapper()
        self.assertEqual(wrapper, 'test_wrapper')

    def test_command(self):
        fake_commands_list = sap.cli.core.CommandsList()
        fake_commands_list.add_command = MagicMock()

        class _TestCommandGroup(DummyCommandGroup):
            commands = fake_commands_list
            commands_wrapper = 'test_wrapper'

        command_name = 'the_command'
        func = 'the_function'

        _TestCommandGroup.command(command_name)(func)
        fake_commands_list.add_command.assert_called_once_with(func, command_name, _TestCommandGroup.commands_wrapper)

    def test_argument_corrnr_default(self):
        args = parse_args(['dummy_corrnr', 'success'])
        self.assertEqual(args.name, 'success')
        self.assertIsNone(args.corrnr)

    def test_argument_corrnr_value(self):
        args = parse_args(['dummy_corrnr', 'fabulous', '--corrnr', '420'])
        self.assertEqual(args.name, 'fabulous')
        self.assertEqual(args.corrnr, '420')

    def test_install_parser_without_commands(self):
        parser = ArgumentParser()
        # Must not fail ...
        EmptyDummyCommandGroup().install_parser(parser)

    def test_install_parser_returns_group(self):
        parser = ArgumentParser()
        mock_command_args = MagicMock()

        with patch('argparse.ArgumentParser.add_subparsers') as fake_adder:
            fake_adder.return_value = mock_command_args

            act_ret = DummyCommandGroup().install_parser(parser)

        self.assertEqual(act_ret, fake_adder.return_value)
        mock_command_args.add_parser.assert_called_once_with('dummy_corrnr', help='Dummy command help')


class TestPrintConsole(unittest.TestCase):

    def test_print_console_ctor_default(self):
        console = sap.cli.core.PrintConsole()
        self.assertIs(console._out, sys.stdout)
        self.assertIs(console._err, sys.stderr)

    def test_print_console_ctor_values(self):
        console = sap.cli.core.PrintConsole(out_file='Foo', err_file='Bar')
        self.assertIs(console._out, 'Foo')
        self.assertIs(console._err, 'Bar')


class TestConsoleErrorDecorator(unittest.TestCase):

    def test_console_error_decorator_full(self):
        out = StringIO()
        err = StringIO()

        console = sap.cli.core.ConsoleErrorDecorator(sap.cli.core.PrintConsole(out_file=out, err_file=err))

        console.printout('OUT')
        console.printerr('ERR')
        console.flush()

        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "OUT\nERR\n")


class TestConsolePrintoutFile(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.out = StringIO()
        self.err = StringIO()
        self.print_console = sap.cli.core.PrintConsole(self.out, self.err)

    def test_console_printout_file_to_console(self):
        with sap.cli.core.console_printout_file(self.print_console, None) as console:
            console.printout('OUT')
            console.printerr('ERR')
            console.flush()

        self.assertEqual(self.out.getvalue(), 'OUT\n')
        self.assertEqual(self.err.getvalue(), 'ERR\n')

    def test_console_printout_file_to_file(self):
        with patch('builtins.open', mock_open()) as fake_open:
            with sap.cli.core.console_printout_file(self.print_console, 'path/to/file') as console:
                console.printout('OUT')
                console.printerr('ERR')
                console.flush()

        fake_open().write.assert_called_once_with('OUT\n')
        self.assertEqual(self.out.getvalue(), '')
        self.assertEqual(self.err.getvalue(), 'ERR\n')


class TestGetStdin(unittest.TestCase):

    def test_initial_sys_stdin(self):
        self.assertEqual(sys.stdin, sap.cli.core.get_stdin())

    def test_replace(self):
        fake_stdin = Mock()

        old_sapcli_stdin = sap.cli.core.set_stdin(fake_stdin)
        self.assertEqual(sys.stdin, old_sapcli_stdin)

        current_stdin = sap.cli.core.get_stdin()
        self.assertEqual(current_stdin, fake_stdin)

        previous_sapcli_stdin = sap.cli.core.set_stdin(sys.stdin)
        self.assertEqual(previous_sapcli_stdin, fake_stdin)


class TestJsonDumps(unittest.TestCase):

    def test_jsom_format_default(self):
        json_dict = sap.cli.core.json_dumps({'foo': 'bar'})
        self.assertEqual(json_dict, '''{
  "foo": "bar"
}''')


if __name__ == '__main__':
    unittest.main()
