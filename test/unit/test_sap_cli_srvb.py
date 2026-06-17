#!/usr/bin/env python3
'''CLI tests for sapcli srvb (Service Binding).'''

# pylint: disable=missing-function-docstring

import unittest
from unittest.mock import call, patch, Mock

import sap.cli.srvb

from infra import generate_parse_args
from mock import Connection, Response, patch_get_print_console_with_buffer
from fixtures_adt_businessservice import (
    SERVICE_BINDING_NAME,
    SERVICE_BINDING_PACKAGE,
    SERVICE_BINDING_ADT_GET_V4_XML,
)


parse_args = generate_parse_args(sap.cli.srvb.CommandGroup())


class TestCommandGroup(unittest.TestCase):

    def test_cli_srvb_commands_constructor(self):
        sap.cli.srvb.CommandGroup()

    def test_cli_srvb_has_no_write_command(self):
        # SRVB v1 does not support source-text write because the binding has
        # no text/plain source body. Make this contract explicit.
        with self.assertRaises(SystemExit):
            parse_args('write', SERVICE_BINDING_NAME, '/dev/null')


class TestSRVBCreate(unittest.TestCase):

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_odata_v4(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--type', 'ODATA', '--version', 'V4',
                          '--service', 'ZSAPCLI_TEST_SRV')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        self.assertEqual(fake_srvb.call_count, 1)
        kwargs = fake_srvb.call_args.kwargs
        self.assertEqual(kwargs['package'], SERVICE_BINDING_PACKAGE)
        self.assertEqual(kwargs['typ'], 'ODATA')
        self.assertEqual(kwargs['version'], 'V4')
        self.assertEqual(kwargs['service_name'], 'ZSAPCLI_TEST_SRV')
        # service_version defaults to '0001'
        self.assertEqual(kwargs['service_version'], '0001')

        fake_srvb.return_value.create.assert_called_once_with(corrnr=None)

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_odata_v2(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--type', 'ODATA', '--version', 'V2',
                          '--service', 'ZSAPCLI_TEST_SRV')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        kwargs = fake_srvb.call_args.kwargs
        self.assertEqual(kwargs['version'], 'V2')

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_sql_v1(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--type', 'SQL', '--version', '1',
                          '--service', 'ZSAPCLI_TEST_SRV')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        kwargs = fake_srvb.call_args.kwargs
        self.assertEqual(kwargs['typ'], 'SQL')
        self.assertEqual(kwargs['version'], '1')

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_ina_v1(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--type', 'INA', '--version', '1',
                          '--service', 'ZSAPCLI_TEST_SRV')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        kwargs = fake_srvb.call_args.kwargs
        self.assertEqual(kwargs['typ'], 'INA')

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_create_with_explicit_service_version(self, fake_srvb):
        fake_conn = Mock()
        fake_conn.user = 'TESTER'
        fake_srvb.return_value = Mock()

        args = parse_args('create', SERVICE_BINDING_NAME,
                          'Test binding', SERVICE_BINDING_PACKAGE,
                          '--type', 'ODATA', '--version', 'V4',
                          '--service', 'ZSAPCLI_TEST_SRV',
                          '--service-version', '0002')
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        kwargs = fake_srvb.call_args.kwargs
        self.assertEqual(kwargs['service_version'], '0002')

    def test_cli_srvb_create_missing_type_errors(self):
        with self.assertRaises(SystemExit):
            parse_args('create', SERVICE_BINDING_NAME, 'Test', SERVICE_BINDING_PACKAGE,
                       '--version', 'V4', '--service', 'ZSAPCLI_TEST_SRV')

    def test_cli_srvb_create_missing_version_errors(self):
        with self.assertRaises(SystemExit):
            parse_args('create', SERVICE_BINDING_NAME, 'Test', SERVICE_BINDING_PACKAGE,
                       '--type', 'ODATA', '--service', 'ZSAPCLI_TEST_SRV')

    def test_cli_srvb_create_missing_service_errors(self):
        with self.assertRaises(SystemExit):
            parse_args('create', SERVICE_BINDING_NAME, 'Test', SERVICE_BINDING_PACKAGE,
                       '--type', 'ODATA', '--version', 'V4')

    def test_cli_srvb_create_invalid_type_errors(self):
        with self.assertRaises(SystemExit):
            parse_args('create', SERVICE_BINDING_NAME, 'Test', SERVICE_BINDING_PACKAGE,
                       '--type', 'BOGUS', '--version', 'V4',
                       '--service', 'ZSAPCLI_TEST_SRV')

    def test_cli_srvb_create_invalid_version_errors(self):
        with self.assertRaises(SystemExit):
            parse_args('create', SERVICE_BINDING_NAME, 'Test', SERVICE_BINDING_PACKAGE,
                       '--type', 'ODATA', '--version', 'V99',
                       '--service', 'ZSAPCLI_TEST_SRV')


class TestSRVBRead(unittest.TestCase):

    def test_cli_srvb_read_prints_summary(self):
        conn = Connection([
            Response(text=SERVICE_BINDING_ADT_GET_V4_XML, status_code=200,
                     headers={'Content-Type':
                              'application/vnd.sap.adt.businessservices.servicebinding.v2+xml; charset=utf-8'})
        ])

        args = parse_args('read', SERVICE_BINDING_NAME)
        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        out = fake_console.capout
        self.assertIn(SERVICE_BINDING_NAME, out)
        self.assertIn('ODATA', out)
        self.assertIn('V4', out)
        self.assertIn('ZSAPCLI_TEST_SRV', out)
        self.assertIn('0001', out)


class TestSRVBActivate(unittest.TestCase):

    @patch('sap.adt.wb.try_activate')
    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_activate_defaults(self, fake_srvb, fake_activate):
        instances = []

        def add_instance(conn, name, package=None, metadata=None):
            srvb = Mock()
            srvb.name = name
            srvb.active = 'active'
            instances.append(srvb)
            return srvb

        fake_srvb.side_effect = add_instance
        fake_activate.return_value = (sap.adt.wb.CheckResults(), None)
        fake_conn = Mock()

        args = parse_args('activate', SERVICE_BINDING_NAME.lower())
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_srvb.assert_called_once_with(fake_conn, SERVICE_BINDING_NAME, package=None, metadata=None)
        fake_activate.assert_called_once_with(instances[0])


class TestSRVBDelete(unittest.TestCase):

    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_delete_defaults(self, fake_srvb):
        srvb = Mock()
        fake_srvb.return_value = srvb
        fake_conn = Mock()

        args = parse_args('delete', SERVICE_BINDING_NAME)
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_srvb.assert_called_once_with(fake_conn, SERVICE_BINDING_NAME, package=None, metadata=None)
        srvb.delete.assert_called_once_with(corrnr=None)


class TestSRVBWhereUsed(unittest.TestCase):

    @patch('sap.adt.whereused.where_used')
    @patch('sap.adt.ServiceBinding')
    def test_cli_srvb_whereused_defaults(self, fake_srvb, fake_where_used):
        fake_conn = Mock()
        srvb = Mock()
        srvb.full_adt_uri = '/sap/bc/adt/businessservices/bindings/zsapcli_test_bnd'
        fake_srvb.return_value = srvb

        result = Mock()
        result.referenced_objects = []
        fake_where_used.return_value = result

        args = parse_args('whereused', SERVICE_BINDING_NAME)
        with patch_get_print_console_with_buffer():
            args.execute(fake_conn, args)

        fake_where_used.assert_called_once_with(
            fake_conn, '/sap/bc/adt/businessservices/bindings/zsapcli_test_bnd')


if __name__ == '__main__':
    unittest.main()
