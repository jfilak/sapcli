#!/usr/bin/env python3

import sys
import unittest
from unittest.mock import call, patch, MagicMock

from argparse import ArgumentParser

import sap.errors
import sap.cli.core


class TestCommandDeclaration(unittest.TestCase):

    def test_init(self):
        cmd_decl = sap.cli.core.CommandDeclaration(print, 'printer')

        self.assertEqual(cmd_decl.name, 'printer')
        self.assertEqual(cmd_decl.handler, print)

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
        pass

    def setUp(self):
        self.cmd_list = sap.cli.core.CommandsList()

    def test_add_command_without_name(self):
        self.cmd_list.add_command(self.handler)
        commands = self.cmd_list.values()
        command = next(iter(commands))

        self.assertEqual(len(commands), 1)
        self.assertEqual(command.name, 'handler')
        self.assertEqual(command.handler, self.handler)

    def test_add_command_with_name(self):
        self.cmd_list.add_command(self.handler, name='command')
        commands = self.cmd_list.values()
        command = next(iter(commands))

        self.assertEqual(len(commands), 1)
        self.assertEqual(command.name, 'command')
        self.assertEqual(command.handler, self.handler)

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
        self._tune_parser_called = False

    def _tune_parser(self, group_parers, command_subparser):
        self._tune_parser_called = True
        return command_subparser


class EmptyDummyCommandGroup(sap.cli.core.CommandGroup):
    """Test empty command group for the case where you need
       want to have a group of groups (i.e. you have no commands).
    """

    def __init__(self):
        super(EmptyDummyCommandGroup, self).__init__('empty-pytest')


@DummyCommandGroup.argument('name')
@DummyCommandGroup.argument_corrnr()
@DummyCommandGroup.command()
def dummy_corrnr(connection, args):

    return (args.corrnr, args.name)


def parse_args(argv):
    parser = ArgumentParser()

    group = DummyCommandGroup()
    group.install_parser(parser)
    assert group._tune_parser_called

    return parser.parse_args(argv)


class TestCommandGroup(unittest.TestCase):

    def test_get_command_declaration(self):
        command = DummyCommandGroup.get_command_declaration(dummy_corrnr)
        self.assertIsNotNone(command)

    def test_get_commands(self):
        commands = DummyCommandGroup.get_commands()
        self.assertEqual(len(commands.values()), 1)

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

        with patch('argparse.ArgumentParser.add_subparsers') as fake_adder:
            fake_adder.return_value = 'FakeParser'

            act_ret = EmptyDummyCommandGroup().install_parser(parser)

        self.assertEqual(act_ret, fake_adder.return_value)


class TestPrintConsole(unittest.TestCase):

    def test_print_console_ctor_default(self):
        console = sap.cli.core.PrintConsole()
        self.assertIs(console._out, sys.stdout)
        self.assertIs(console._err, sys.stderr)

    def test_print_console_ctor_values(self):
        console = sap.cli.core.PrintConsole(out_file='Foo', err_file='Bar')
        self.assertIs(console._out, 'Foo')
        self.assertIs(console._err, 'Bar')


if __name__ == '__main__':
    unittest.main()
