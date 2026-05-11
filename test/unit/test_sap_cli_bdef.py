#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import call, patch, Mock, PropertyMock
from io import StringIO

import sap.cli.interface
import sap.cli.behaviordefinition
from sap.errors import SAPCliError

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


class TestBDEFListInterfaces(unittest.TestCase):

    @patch('sap.adt.behaviordefinition.BehaviorDefinition.list_interfaces')
    def test_cli_bdef_listinterfaces(self, fake_list):
        fake_conn = Mock()

        fake_item = Mock()
        fake_item.name = 'I_PRODUCTTP_2'

        fake_result = Mock()
        fake_result.__iter__ = Mock(return_value=iter([fake_item]))
        fake_list.return_value = fake_result

        args = parse_args('listinterfaces', 'R_PRODUCTTP')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        fake_list.assert_called_once_with(fake_conn, 'R_PRODUCTTP')
        self.assertEqual(fake_console.capout, 'I_PRODUCTTP_2\n')

    @patch('sap.adt.behaviordefinition.BehaviorDefinition.list_interfaces')
    def test_cli_bdef_listinterfaces_empty(self, fake_list):
        fake_conn = Mock()

        fake_result = Mock()
        fake_result.__iter__ = Mock(return_value=iter([]))
        fake_list.return_value = fake_result

        args = parse_args('listinterfaces', 'R_PRODUCTTP')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        self.assertEqual(fake_console.capout, '')


class TestBDEFCreate(unittest.TestCase):

    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_create_regular(self, fake_bdef):
        """Regular create without extension params should work as before"""
        fake_conn = Mock()
        fake_conn.user = 'DEVELOPER'
        fake_instance = Mock()
        fake_instance.template = None
        fake_bdef.return_value = fake_instance

        args = parse_args('create', 'ZMYBDEF', 'My description', 'MYPACKAGE')
        args.execute(fake_conn, args)

        fake_bdef.assert_called_once()
        fake_instance.create.assert_called_once_with(corrnr=None)
        self.assertIsNone(fake_instance.template)


class TestBDEFExtend(unittest.TestCase):

    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_extend_without_interface(self, fake_bdef):
        """Extend with base-bdef but no --interface-bdef"""
        fake_conn = Mock()
        fake_conn.user = 'DEVELOPER'
        fake_instance = Mock()
        fake_instance.template = None
        fake_bdef.return_value = fake_instance

        args = parse_args('extend', 'R_PRODUCTTP_EXT', 'My extension', 'MYPACKAGE',
                          'R_PRODUCTTP')
        args.execute(fake_conn, args)

        fake_instance.create.assert_called_once_with(corrnr=None)
        self.assertIsNotNone(fake_instance.template)
        template = fake_instance.template
        self.assertEqual(len(template.properties), 2)
        self.assertEqual(template.properties[0].key, 'base_bdef')
        self.assertEqual(template.properties[0].value, 'R_PRODUCTTP')
        self.assertEqual(template.properties[1].key, 'interface_bdef')
        self.assertIsNone(template.properties[1].value)

    @patch('sap.adt.behaviordefinition.BehaviorDefinition.list_interfaces')
    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_extend_with_valid_interface(self, fake_bdef, fake_list):
        """Extend with valid --interface-bdef"""
        fake_conn = Mock()
        fake_conn.user = 'DEVELOPER'
        fake_instance = Mock()
        fake_instance.template = None
        fake_bdef.return_value = fake_instance

        fake_item = Mock()
        fake_item.name = 'I_PRODUCTTP_2'
        fake_result = Mock()
        fake_result.items = [fake_item]
        fake_list.return_value = fake_result

        args = parse_args('extend', 'R_PRODUCTTP_EXT', 'My extension', 'MYPACKAGE',
                          'R_PRODUCTTP', '--interface-bdef', 'I_PRODUCTTP_2')
        args.execute(fake_conn, args)

        fake_list.assert_called_once_with(fake_conn, 'R_PRODUCTTP')
        fake_instance.create.assert_called_once_with(corrnr=None)
        template = fake_instance.template
        self.assertEqual(template.properties[1].key, 'interface_bdef')
        self.assertEqual(template.properties[1].value, 'I_PRODUCTTP_2')

    @patch('sap.adt.behaviordefinition.BehaviorDefinition.list_interfaces')
    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_extend_with_valid_interface_case_insensitive(self, fake_bdef, fake_list):
        """Interface validation is case-insensitive"""
        fake_conn = Mock()
        fake_conn.user = 'DEVELOPER'
        fake_instance = Mock()
        fake_instance.template = None
        fake_bdef.return_value = fake_instance

        fake_item = Mock()
        fake_item.name = 'I_PRODUCTTP_2'
        fake_result = Mock()
        fake_result.items = [fake_item]
        fake_list.return_value = fake_result

        args = parse_args('extend', 'R_PRODUCTTP_EXT', 'My extension', 'MYPACKAGE',
                          'R_PRODUCTTP', '--interface-bdef', 'i_producttp_2')
        args.execute(fake_conn, args)

        fake_instance.create.assert_called_once_with(corrnr=None)

    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_extend_uppercases_base_bdef(self, fake_bdef):
        """Extend uppercases base_bdef input"""
        fake_conn = Mock()
        fake_conn.user = 'DEVELOPER'
        fake_instance = Mock()
        fake_instance.template = None
        fake_bdef.return_value = fake_instance

        args = parse_args('extend', 'R_PRODUCTTP_EXT', 'My extension', 'MYPACKAGE',
                          'r_producttp')
        args.execute(fake_conn, args)

        template = fake_instance.template
        self.assertEqual(template.properties[0].value, 'R_PRODUCTTP')

    @patch('sap.adt.behaviordefinition.BehaviorDefinition.list_interfaces')
    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_extend_uppercases_interface_bdef(self, fake_bdef, fake_list):
        """Extend uppercases interface_bdef input"""
        fake_conn = Mock()
        fake_conn.user = 'DEVELOPER'
        fake_instance = Mock()
        fake_instance.template = None
        fake_bdef.return_value = fake_instance

        fake_item = Mock()
        fake_item.name = 'I_PRODUCTTP_2'
        fake_result = Mock()
        fake_result.items = [fake_item]
        fake_list.return_value = fake_result

        args = parse_args('extend', 'R_PRODUCTTP_EXT', 'My extension', 'MYPACKAGE',
                          'r_producttp', '--interface-bdef', 'i_producttp_2')
        args.execute(fake_conn, args)

        template = fake_instance.template
        self.assertEqual(template.properties[0].value, 'R_PRODUCTTP')
        self.assertEqual(template.properties[1].value, 'I_PRODUCTTP_2')

    @patch('sap.adt.behaviordefinition.BehaviorDefinition.list_interfaces')
    @patch('sap.adt.BehaviorDefinition')
    def test_cli_bdef_extend_with_invalid_interface(self, fake_bdef, fake_list):
        """Extend with --interface-bdef that doesn't exist should fail"""
        fake_conn = Mock()
        fake_conn.user = 'DEVELOPER'
        fake_instance = Mock()
        fake_instance.template = None
        fake_bdef.return_value = fake_instance

        fake_item = Mock()
        fake_item.name = 'I_PRODUCTTP_2'
        fake_result = Mock()
        fake_result.items = [fake_item]
        fake_list.return_value = fake_result

        args = parse_args('extend', 'R_PRODUCTTP_EXT', 'My extension', 'MYPACKAGE',
                          'R_PRODUCTTP', '--interface-bdef', 'I_NONEXISTENT')

        with self.assertRaises(SAPCliError) as cm:
            args.execute(fake_conn, args)

        self.assertIn('I_NONEXISTENT', str(cm.exception))
        fake_instance.create.assert_not_called()


if __name__ == '__main__':
    unittest.main()
