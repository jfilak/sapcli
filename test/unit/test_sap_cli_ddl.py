#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import call, patch, Mock, PropertyMock
from io import StringIO

import sap.cli.interface
import sap.cli.datadefinition

from infra import generate_parse_args
from mock import patch_get_print_console_with_buffer


parse_args = generate_parse_args(sap.cli.datadefinition.CommandGroup())


class TestCommandGroup(unittest.TestCase):

    def test_cli_ddl_commands_constructor(self):
        sap.cli.datadefinition.CommandGroup()


class TestDDLActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.DataDefinition')
    def test_cli_ddl_activate_defaults(self, fake_ddl, fake_activate):
        instances = []

        def add_instance(conn, name, package=None, metadata=None):
            ddl = Mock()
            ddl.name = name
            ddl.active = 'active'

            instances.append(ddl)
            return ddl

        fake_ddl.side_effect = add_instance

        fake_conn= Mock()

        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        args = parse_args('activate', 'myusers', 'mygroups')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        self.assertEqual(fake_ddl.mock_calls, [
                call(fake_conn, 'MYUSERS', package=None, metadata=None),
                call(fake_conn, 'MYGROUPS', package=None, metadata=None)])

        self.assertEqual(instances[0].name, 'MYUSERS')
        self.assertEqual(instances[1].name, 'MYGROUPS')

        self.assertEqual(fake_activate.mock_calls, [call(instances[0]), call(instances[1])])

        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, '''Activating 2 objects:
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

        args = parse_args('read', 'MYUSERS')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        fake_ddl.assert_called_once_with(fake_conn, 'MYUSERS', package=None, metadata=None)
        self.assertEqual(fake_console.capout, 'source code\n')


if __name__ == '__main__':
    unittest.main()
