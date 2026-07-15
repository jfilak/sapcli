#!/usr/bin/env python3
'''CLI tests for sapcli srvd (Service Definition).'''

# pylint: disable=missing-function-docstring

import unittest
from unittest.mock import call, patch, Mock

import sap.cli.srvd
import sap.adt.businessservice

from infra import generate_parse_args
from mock import patch_get_print_console_with_buffer


parse_args = generate_parse_args(sap.cli.srvd.CommandGroup())

class TestCommandGroup(unittest.TestCase):

    def test_cli_srvd_commands_constructor(self):
        sap.cli.srvd.CommandGroup()


class TestSRVDCreate(unittest.TestCase):

    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_create_defaults(self, fake_srvd):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'

        srvd = Mock()
        fake_srvd.return_value = srvd

        args = parse_args('create', 'ZSAPCLI_TEST_SRV', 'Test service', '$TMP')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        # Only one positional call - the instance call inside build_new_object.
        self.assertEqual(fake_srvd.call_count, 1)
        positional = fake_srvd.call_args.args
        self.assertEqual(positional[0], fake_conn)
        self.assertEqual(positional[1], 'ZSAPCLI_TEST_SRV')

        kwargs = fake_srvd.call_args.kwargs
        self.assertEqual(kwargs['package'], '$TMP')
        self.assertIsNotNone(kwargs['metadata'])

        srvd.create.assert_called_once_with(corrnr=None)
        self.assertEqual(srvd.description, 'Test service')

    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_create_with_corrnr(self, fake_srvd):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvd.return_value = Mock()

        args = parse_args('create', 'ZSAPCLI_TEST_SRV', 'Test service', '$TMP',
                          '--corrnr', 'TR42')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_srvd.return_value.create.assert_called_once_with(corrnr='TR42')

    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_create_default_source_type(self, fake_srvd):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvd.return_value = Mock()

        args = parse_args('create', 'ZSAPCLI_TEST_SRV', 'Test service', '$TMP')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        self.assertEqual(fake_srvd.call_args.kwargs['source_type'],
                         sap.adt.businessservice.SourceType.DEFINITION)

    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_create_extension_source_type(self, fake_srvd):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvd.return_value = Mock()

        args = parse_args('create', 'ZSAPCLI_TEST_SRV', 'Test service', '$TMP',
                          '--type', 'extension')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        self.assertEqual(fake_srvd.call_args.kwargs['source_type'],
                         sap.adt.businessservice.SourceType.EXTENSION)

    def test_cli_srvd_create_invalid_source_type(self):
        with self.assertRaises(SystemExit):
            parse_args('create', 'ZSAPCLI_TEST_SRV', 'Test service', '$TMP',
                       '--type', 'nonsense')


class TestSRVDRead(unittest.TestCase):

    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_read_defaults(self, fake_srvd):
        fake_conn = Mock()
        fake_srvd.return_value = Mock()
        fake_srvd.return_value.text = 'define service ZSAPCLI_TEST_SRV {}\n'

        args = parse_args('read', 'ZSAPCLI_TEST_SRV')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        fake_srvd.assert_called_once_with(
            fake_conn, 'ZSAPCLI_TEST_SRV', package=None, metadata=None)
        self.assertEqual(fake_console.capout, 'define service ZSAPCLI_TEST_SRV {}\n\n')


class TestSRVDActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_activate_defaults(self, fake_srvd, fake_activate):
        instances = []

        def add_instance(conn, name, package=None, metadata=None):
            srvd = Mock()
            srvd.name = name
            srvd.active = 'active'
            instances.append(srvd)
            return srvd

        fake_srvd.side_effect = add_instance
        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        fake_conn = Mock()

        args = parse_args('activate', 'zsapcli_test_srv', 'zsapcli_test_srv2')
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(fake_conn, args)

        self.assertEqual(fake_srvd.mock_calls, [
            call(fake_conn, 'ZSAPCLI_TEST_SRV', package=None, metadata=None),
            call(fake_conn, 'ZSAPCLI_TEST_SRV2', package=None, metadata=None),
        ])
        self.assertEqual(fake_activate.mock_calls, [call(instances[0]), call(instances[1])])
        self.assertEqual(fake_console.caperr, '')


class TestSRVDDelete(unittest.TestCase):

    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_delete_defaults(self, fake_srvd):
        srvd = Mock()
        fake_srvd.return_value = srvd
        fake_conn = Mock()

        args = parse_args('delete', 'ZSAPCLI_TEST_SRV')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_srvd.assert_called_once_with(
            fake_conn, 'ZSAPCLI_TEST_SRV', package=None, metadata=None)
        srvd.delete.assert_called_once_with(corrnr=None)


class TestSRVDWriteUsesPlainTextEditor(unittest.TestCase):

    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_write_pipes_stdin_to_editor(self, fake_srvd):
        editor = Mock()
        editor.__enter__ = Mock(return_value=editor)
        editor.__exit__ = Mock(return_value=False)

        srvd = Mock()
        srvd.open_editor = Mock(return_value=editor)
        fake_srvd.return_value = srvd

        fake_conn = Mock()

        args = parse_args('write', 'ZSAPCLI_TEST_SRV', '-')
        # Feed code via stdin
        with patch('sys.stdin') as fake_stdin, \
             patch_get_print_console_with_buffer():
            fake_stdin.readlines.return_value = ['define service ZSAPCLI_TEST_SRV {}\n']
            args.execute(fake_conn, args)

        srvd.open_editor.assert_called_once_with(corrnr=None)
        editor.write.assert_called_once_with('define service ZSAPCLI_TEST_SRV {}\n')


class TestSRVDWhereUsed(unittest.TestCase):

    @patch('sap.adt.whereused.where_used')
    @patch('sap.adt.ServiceDefinition')
    def test_cli_srvd_whereused_defaults(self, fake_srvd, fake_where_used):
        fake_conn = Mock()
        srvd = Mock()
        srvd.full_adt_uri = '/sap/bc/adt/ddic/srvd/sources/zsapcli_test_srv'
        fake_srvd.return_value = srvd

        result = Mock()
        result.referenced_objects = []
        fake_where_used.return_value = result

        args = parse_args('whereused', 'ZSAPCLI_TEST_SRV')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_where_used.assert_called_once_with(
            fake_conn, '/sap/bc/adt/ddic/srvd/sources/zsapcli_test_srv')


if __name__ == '__main__':
    unittest.main()
