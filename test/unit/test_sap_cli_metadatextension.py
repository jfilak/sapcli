#!/usr/bin/env python3

import unittest
from unittest.mock import call, patch, Mock

import sap.adt
import sap.cli.metadatextension

from infra import generate_parse_args
from mock import patch_get_print_console_with_buffer


parse_args = generate_parse_args(sap.cli.metadatextension.CommandGroup())


class TestCommandGroup(unittest.TestCase):

    def test_cli_ddlx_commands_constructor(self):
        sap.cli.metadatextension.CommandGroup()


class TestDDLXActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.MetadataExtension')
    def test_cli_ddlx_activate_defaults(self, fake_ddlx, fake_activate):
        instances = []

        def add_instance(conn, name, package=None, metadata=None):
            ddlx = Mock()
            ddlx.name = name
            ddlx.active = 'active'

            instances.append(ddlx)
            return ddlx

        fake_ddlx.side_effect = add_instance

        fake_conn = Mock()

        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        args = parse_args('activate', 'z_test_md_ext_v0', 'z_test_md_ext_v1')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        self.assertEqual(fake_ddlx.mock_calls, [
            call(fake_conn, 'Z_TEST_MD_EXT_V0', package=None, metadata=None),
            call(fake_conn, 'Z_TEST_MD_EXT_V1', package=None, metadata=None)])

        self.assertEqual(instances[0].name, 'Z_TEST_MD_EXT_V0')
        self.assertEqual(instances[1].name, 'Z_TEST_MD_EXT_V1')

        self.assertEqual(fake_activate.mock_calls, [call(instances[0]), call(instances[1])])

        self.assertEqual(fake_console.caperr, '')
        self.assertEqual(fake_console.capout, '''Activating 2 objects:
* z_test_md_ext_v0 (1/2)
* z_test_md_ext_v1 (2/2)
Activation has finished
Warnings: 0
Errors: 0
''')


class TestDDLXRead(unittest.TestCase):

    @patch('sap.adt.MetadataExtension')
    def test_cli_ddlx_read_defaults(self, fake_ddlx):
        fake_conn = Mock()
        fake_ddlx.return_value = Mock()
        fake_ddlx.return_value.text = 'source code'

        args = parse_args('read', 'Z_TEST_MD_EXT_V0')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        fake_ddlx.assert_called_once_with(fake_conn, 'Z_TEST_MD_EXT_V0', package=None, metadata=None)
        self.assertEqual(fake_console.capout, 'source code\n')


class TestDDLXCreate(unittest.TestCase):

    @patch('sap.adt.MetadataExtension')
    def test_cli_ddlx_create_defaults(self, fake_ddlx):
        fake_conn = Mock()
        fake_instance = Mock()
        fake_ddlx.return_value = fake_instance

        args = parse_args('create', 'Z_TEST_MD_EXT_V0', 'Description', '$TMP')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        self.assertEqual(fake_ddlx.call_count, 1)
        _, kwargs = fake_ddlx.call_args
        self.assertEqual(fake_ddlx.call_args[0][0], fake_conn)
        self.assertEqual(fake_ddlx.call_args[0][1], 'Z_TEST_MD_EXT_V0')
        self.assertEqual(kwargs['package'], '$TMP')
        self.assertEqual(kwargs['metadata'].description, None)
        self.assertEqual(fake_instance.description, 'Description')
        fake_instance.create.assert_called_once_with(corrnr=None)


if __name__ == '__main__':
    unittest.main()
