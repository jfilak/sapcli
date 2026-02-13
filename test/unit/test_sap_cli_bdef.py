#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import call, patch, Mock, PropertyMock
from io import StringIO

import sap.cli.interface
import sap.cli.behaviordefinition

from infra import generate_parse_args
from mock import patch_get_print_console_with_buffer


parse_args = generate_parse_args(sap.cli.behaviordefinition.CommandGroup())


class TestCommandGroup(unittest.TestCase):

    def test_cli_bdef_commands_constructor(self):
        sap.cli.behaviordefinition.CommandGroup()


class TestBDEFActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_activate_defaults(self, fake_bdef, fake_activate):
        instances = []

        def add_instance(conn, name, package=None, metadata=None):
            bdef = Mock()
            bdef.name = name
            bdef.active = 'active'

            instances.append(bdef)
            return bdef

        fake_bdef.side_effect = add_instance

        fake_conn = Mock()

        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        args = parse_args('activate', 'zmybdef', 'zmybdef2')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        self.assertEqual(fake_bdef.mock_calls, [
                call(fake_conn, 'ZMYBDEF', package=None, metadata=None),
                call(fake_conn, 'ZMYBDEF2', package=None, metadata=None)])

        self.assertEqual(instances[0].name, 'ZMYBDEF')
        self.assertEqual(instances[1].name, 'ZMYBDEF2')

        self.assertEqual(fake_activate.mock_calls, [call(instances[0]), call(instances[1])])

        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, '''Activating 2 objects:
* zmybdef (1/2)
* zmybdef2 (2/2)
Activation has finished
Warnings: 0
Errors: 0
''')


class TestBDEFRead(unittest.TestCase):

    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_read_defaults(self, fake_bdef):
        fake_conn = Mock()
        fake_bdef.return_value = Mock()
        fake_bdef.return_value.text = 'source code'

        args = parse_args('read', 'ZMYBDEF')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        fake_bdef.assert_called_once_with(fake_conn, 'ZMYBDEF', package=None, metadata=None)
        self.assertEqual(fake_console.capout, 'source code\n')


if __name__ == '__main__':
    unittest.main()
