#!/usr/bin/env python3

from argparse import ArgumentParser

import unittest
from unittest.mock import patch, Mock
from io import StringIO
from types import SimpleNamespace

from sap.errors import SAPCliError
import sap.cli.cts

from mock import Connection, Response
from fixtures_adt import (
    TASK_NUMBER,
    TRANSPORT_NUMBER,
    TASK_RELEASE_OK_RESPONSE,
    TRASNPORT_RELEASE_OK_RESPONSE,
    SHORTENED_WORKBENCH_XML
)


parser = ArgumentParser()
sap.cli.cts.CommandGroup().install_parser(parser)


def parse_args(*argv):
    return parser.parse_args(argv)


class TestCTSRelease(unittest.TestCase):

    def test_release_invalid_request_type(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.cts.release(None, SimpleNamespace(type='foo', number='WHATEVER'))

        self.assertEqual(str(cm.exception), 'Internal error: unknown request type: foo')

    def do_check_command_release(self, request_type, number, response):
        connection = Connection([Response(response, 200, {})])

        sap.cli.cts.release(connection, SimpleNamespace(type=request_type, number=number))

        self.assertEqual(
            [request.adt_uri for request in connection.execs],
            [f'/sap/bc/adt/cts/transportrequests/{number}/newreleasejobs']
        )

    def test_release_transport(self):
        self.do_check_command_release('transport', TRANSPORT_NUMBER, TRASNPORT_RELEASE_OK_RESPONSE)

    def test_release_task(self):
        self.do_check_command_release('task', TASK_NUMBER, TASK_RELEASE_OK_RESPONSE)


class TestCTSList(unittest.TestCase):

    def do_workbench_list_output(self, request_type, recursive):
        connection = Connection([Response(SHORTENED_WORKBENCH_XML, 200, {})])

        with patch('sys.stdout', new_callable=StringIO) as fake_output:
            sap.cli.cts.print_list(connection, SimpleNamespace(type=request_type, recursive=recursive, owner='FILAK', number=None))

        self.assertEqual(
            [(request.adt_uri, request.params['user']) for request in connection.execs],
            [('/sap/bc/adt/cts/transportrequests', 'FILAK')]
        )

        return fake_output.getvalue()

    def test_workbench_list_transport_0(self):
        output = self.do_workbench_list_output('transport', 0)
        self.assertEqual(output, f'{TRANSPORT_NUMBER} D FILAK Transport Description\n')

    def test_workbench_list_transport_1(self):
        output = self.do_workbench_list_output('transport', 1)
        self.assertEqual(output, f'{TRANSPORT_NUMBER} D FILAK Transport Description\n  {TASK_NUMBER} D FILAK\n')

    def test_workbench_list_transport_2(self):
        output = self.do_workbench_list_output('transport', 2)
        self.assertEqual(output, f'{TRANSPORT_NUMBER} D FILAK Transport Description\n  {TASK_NUMBER} D FILAK\n    TABD FOO\n')

    def test_workbench_list_transport_3(self):
        output = self.do_workbench_list_output('transport', 3)
        self.assertEqual(output, f'{TRANSPORT_NUMBER} D FILAK Transport Description\n  {TASK_NUMBER} D FILAK\n    TABD FOO\n')

    def test_workbench_list_task_0(self):
        output = self.do_workbench_list_output('task', 0)
        self.assertEqual(output, f'{TASK_NUMBER} D FILAK Task Description\n')

    def test_workbench_list_task_1(self):
        output = self.do_workbench_list_output('task', 1)
        self.assertEqual(output, f'{TASK_NUMBER} D FILAK Task Description\n  TABD FOO\n')

    def test_workbench_list_task_2(self):
        output = self.do_workbench_list_output('task', 2)
        self.assertEqual(output, f'{TASK_NUMBER} D FILAK Task Description\n  TABD FOO\n')

    def test_workbench_list_transport(self):
        connection = Connection([Response(SHORTENED_WORKBENCH_XML, 200, {})], user='ANZEIGER')

        with patch('sys.stdout', new_callable=StringIO) as fake_output:
            sap.cli.cts.print_list(connection, SimpleNamespace(type='transport', recursive=0, owner=None, number=None))

        self.assertEqual(
            [(request.adt_uri, request.params['user']) for request in connection.execs],
            [('/sap/bc/adt/cts/transportrequests', 'ANZEIGER')]
        )

        self.assertEqual(fake_output.getvalue(), f'{TRANSPORT_NUMBER} D FILAK Transport Description\n')

    @patch('sap.cli.core.printerr')
    @patch('sap.adt.cts.Workbench.fetch_transport_request')
    def test_workbench_display_transport(self, fake_fetch_transport_request, fake_err):
        err_output = []

        def add_err(msg, transport, sep=' ', end='\n'):
           err_output.append(sep.join((msg, transport)) + end)

        fake_err.side_effect = add_err

        def return_transport(corr_nr):
            if corr_nr == 'NPLK654321':
                return None

            return sap.adt.cts.WorkbenchTransport('connection', [], corr_nr, 'FILAK', 'TR')

        fake_fetch_transport_request.side_effect = return_transport

        connection = Mock()
        args = parse_args('list', 'transport', 'NPLK654321', 'NPLK654322', 'NPLK654323')

        with patch('sys.stdout', new_callable=StringIO) as fake_output:
            args.execute(connection, args)

        self.assertEqual(''.join(err_output), 'The transport was not found: NPLK654321\n')
        self.assertEqual(fake_output.getvalue(), f'NPLK654322 ? FILAK TR\nNPLK654323 ? FILAK TR\n')


if __name__ == '__main__':
    unittest.main()
