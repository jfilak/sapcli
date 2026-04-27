#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock

import sap.cli.transaction
from sap.errors import SAPCliError

from mock import (
    Connection,
    Response,
    Request,
)

from infra import generate_parse_args
from fixtures_adt_transaction import (
    TRANSACTION_NAME,
    TRANSACTION_DEFINITION_ADT_XML,
    CLI_CREATE_TRANSACTION_WITH_CONTENT_ADT_XML,
)
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK

parse_args = generate_parse_args(sap.cli.transaction.CommandGroup())


class TestTransactionCreate(unittest.TestCase):

    def test_create_report_transaction(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=report',
            '--report-name=ZABAPGIT',
            '--report-dynnr=1000',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)

        expected_request = Request(
            adt_uri='/sap/bc/adt/aps/iam/tran',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.blues.v2+xml; charset=utf-8'},
            body=bytes(CLI_CREATE_TRANSACTION_WITH_CONTENT_ADT_XML, 'utf-8'),
            params=None
        )

        expected_request.assertEqual(connection.execs[0], self)

    def test_create_parameter_transaction(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', 'ZJF_TEST_JAKUB', 'test jakub', '$TMP',
            '--type=parameter',
            '--parent-transaction=/AIF/28000003',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/aps/iam/tran')
        self.assertEqual(connection.execs[0].method, 'POST')

    def test_create_dialog_transaction(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=dialog',
            '--program-name=ZABAPGIT',
            '--program-dynnr=1000',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/aps/iam/tran')
        self.assertEqual(connection.execs[0].method, 'POST')

    def test_create_oo_transaction(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=oo',
            '--class-name=ZCL_TEST',
            '--method-name=EXECUTE',
            '--oo-transaction-model',
            '--update-mode=synchronous',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/aps/iam/tran')
        self.assertEqual(connection.execs[0].method, 'POST')

    def test_create_variant_transaction(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=variant',
            '--parent-transaction=SE38',
            '--cross-client',
            '--transaction-variant-name=ZVAR1',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/aps/iam/tran')
        self.assertEqual(connection.execs[0].method, 'POST')

    def test_create_with_corrnr(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=report',
            '--report-name=ZABAPGIT',
            '--report-dynnr=1000',
            '--corrnr=NPLK900001',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].params, {'corrNr': 'NPLK900001'})

    def test_create_report_with_variant(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=report',
            '--report-name=ZABAPGIT',
            '--report-dynnr=1000',
            '--report-variant-name=MYVAR',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)

    def test_create_oo_with_local_in_program(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=oo',
            '--class-name=ZCL_TEST',
            '--method-name=EXECUTE',
            '--local-in-program',
            '--class-program-name=ZPROG',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)

    def test_create_with_abap_language_version(self):
        connection = Connection()

        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=report',
            '--report-name=ZABAPGIT',
            '--report-dynnr=1000',
            '--abap-language-version=ABAP for Key Users',
        )
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(len(connection.execs), 1)


class TestTransactionCreateValidation(unittest.TestCase):

    def test_report_missing_report_name(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=report',
            '--report-dynnr=1000',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--report-name', str(cm.exception))

    def test_report_missing_report_dynnr(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=report',
            '--report-name=ZABAPGIT',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--report-dynnr', str(cm.exception))

    def test_report_missing_both(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=report',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--report-name', str(cm.exception))
        self.assertIn('--report-dynnr', str(cm.exception))

    def test_parameter_missing_parent_transaction(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=parameter',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--parent-transaction', str(cm.exception))

    def test_dialog_missing_program_name(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=dialog',
            '--program-dynnr=0100',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--program-name', str(cm.exception))

    def test_dialog_missing_program_dynnr(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=dialog',
            '--program-name=SAPMZMY',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--program-dynnr', str(cm.exception))

    def test_oo_missing_class_name(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=oo',
            '--method-name=EXECUTE',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--class-name', str(cm.exception))

    def test_oo_missing_method_name(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=oo',
            '--class-name=ZCL_TEST',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--method-name', str(cm.exception))

    def test_variant_missing_parent_transaction(self):
        the_cmd = parse_args(
            'create', TRANSACTION_NAME, 'abapgit', '$TMP',
            '--type=variant',
        )
        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(Connection(), the_cmd)
        self.assertIn('--parent-transaction', str(cm.exception))


class TestTransactionRead(unittest.TestCase):

    def test_read(self):
        connection = Connection([
            Response(text='{"formatVersion":"1"}', status_code=200,
                     headers={'Content-Type': 'application/json'}),
        ])

        from mock import BufferConsole
        console = BufferConsole()
        the_cmd = parse_args('read', TRANSACTION_NAME)
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        self.assertIn('formatVersion', console.capout)

        expected_request = Request(
            adt_uri='/sap/bc/adt/aps/iam/tran/zabapgit/source/main',
            method='GET',
            headers={'Accept': 'application/json'},
            body=None,
            params=None
        )

        self.assertEqual(connection.execs[0], expected_request)


class TestTransactionActivate(unittest.TestCase):

    def test_activate(self):
        connection = Connection([
            RESPONSE_ACTIVATION_OK,
            Response(text=TRANSACTION_DEFINITION_ADT_XML, status_code=200, headers={})
        ])

        the_cmd = parse_args('activate', TRANSACTION_NAME)
        the_cmd.execute(connection, the_cmd)

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/activation')
        self.assertEqual(connection.execs[0].method, 'POST')


if __name__ == '__main__':
    unittest.main()
