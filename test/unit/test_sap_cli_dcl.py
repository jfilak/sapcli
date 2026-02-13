#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import call, patch, Mock, PropertyMock
from io import StringIO

import sap.cli.interface
import sap.cli.accesscontrol

from infra import generate_parse_args
from mock import patch_get_print_console_with_buffer


parse_args = generate_parse_args(sap.cli.accesscontrol.CommandGroup())


class TestCommandGroup(unittest.TestCase):

    def test_cli_dcl_commands_constructor(self):
        sap.cli.accesscontrol.CommandGroup()


class TestDCLActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.AccessControl')
    def test_cli_dcl_activate_defaults(self, fake_dcl, fake_activate):
        instances = []

        def add_instance(conn, name, package=None, metadata=None):
            dcl = Mock()
            dcl.name = name
            dcl.active = 'active'

            instances.append(dcl)
            return dcl

        fake_dcl.side_effect = add_instance

        fake_conn = Mock()

        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        args = parse_args('activate', 'zmyacl', 'zmyacl2')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        self.assertEqual(fake_dcl.mock_calls, [
                call(fake_conn, 'ZMYACL', package=None, metadata=None),
                call(fake_conn, 'ZMYACL2', package=None, metadata=None)])

        self.assertEqual(instances[0].name, 'ZMYACL')
        self.assertEqual(instances[1].name, 'ZMYACL2')

        self.assertEqual(fake_activate.mock_calls, [call(instances[0]), call(instances[1])])

        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, '''Activating 2 objects:
* zmyacl (1/2)
* zmyacl2 (2/2)
Activation has finished
Warnings: 0
Errors: 0
''')


class TestDCLRead(unittest.TestCase):

    @patch('sap.adt.AccessControl')
    def test_cli_dcl_read_defaults(self, fake_dcl):
        fake_conn = Mock()
        fake_dcl.return_value = Mock()
        fake_dcl.return_value.text = 'source code'

        args = parse_args('read', 'ZMYACL')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        fake_dcl.assert_called_once_with(fake_conn, 'ZMYACL', package=None, metadata=None)
        self.assertEqual(fake_console.capout, 'source code\n')


if __name__ == '__main__':
    unittest.main()
