#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import call, patch, Mock, PropertyMock
from io import StringIO

import sap.cli.interface

from mock import patch_get_print_console_with_buffer


def parse_args(argv):
    parser = ArgumentParser()
    sap.cli.datadefinition.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestCommandGroup(unittest.TestCase):

    def test_cli_ddl_commands_constructor(self):
        sap.cli.datadefinition.CommandGroup()


class TestDDLActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.DataDefinition')
    def test_cli_ddl_activate_defaults(self, fake_ddl, fake_activate):
        instances = []

        def add_instance(conn, name):
            ddl = Mock()
            ddl.name = name

            instances.append(ddl)
            return ddl

        fake_ddl.side_effect = add_instance

        fake_conn= Mock()

        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        args = parse_args(['activate', 'myusers', 'mygroups'])
        with patch_get_print_console_with_buffer() as fake_get_console:
            args.execute(fake_conn, args)

        self.assertEqual(fake_ddl.mock_calls, [call(fake_conn, 'myusers'), call(fake_conn, 'mygroups')])

        self.assertEqual(instances[0].name, 'myusers')
        self.assertEqual(instances[1].name, 'mygroups')

        self.assertEqual(fake_activate.mock_calls, [call(instances[0]), call(instances[1])])

        self.assertEqual(fake_get_console.return_value.err_output.getvalue(), '')
        self.assertEqual(fake_get_console.return_value.std_output.getvalue(), '''Activating 2 objects:
* myusers (1/2)
* mygroups (2/2)
Activation has finished
Warnings: 0
Errors: 0
''')


class TestDDLRead(unittest.TestCase):

    @patch('sap.adt.DataDefinition')
    def test_cli_ddl_read_defaults(self, fake_ddl):
        fake_conn= Mock()
        fake_ddl.return_value = Mock()
        fake_ddl.return_value.text = 'source code'

        args = parse_args(['read', 'myusers'])
        with patch('sap.cli.datadefinition.print') as fake_print:
            args.execute(fake_conn, args)

        fake_ddl.assert_called_once_with(fake_conn, 'myusers')
        fake_print.assert_called_once_with('source code')


if __name__ == '__main__':
    unittest.main()
