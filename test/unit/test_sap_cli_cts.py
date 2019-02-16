#!/usr/bin/env python3

import unittest
from unittest.mock import patch
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


class TestCTSCommandGroup(unittest.TestCase):

    def test_cts_command_group_create(self):
        sap.cli.cts.CommandGroup()


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
            sap.cli.cts.print_list(connection, SimpleNamespace(type=request_type, recursive=recursive, user='FILAK'))

        self.assertEqual(
            [(request.adt_uri, request.params['user']) for request in connection.execs],
            [('/sap/bc/adt/cts/transportrequests', 'FILAK')]
        )

        return fake_output.getvalue()

    def test_workbench_list_transport_0(self):
        output = self.do_workbench_list_output('transport', 0)
        self.assertEqual(output, f'{TRANSPORT_NUMBER}\n')

    def test_workbench_list_transport_1(self):
        output = self.do_workbench_list_output('transport', 1)
        self.assertEqual(output, f'{TRANSPORT_NUMBER}\n  {TASK_NUMBER}\n')

    def test_workbench_list_transport_2(self):
        output = self.do_workbench_list_output('transport', 2)
        self.assertEqual(output, f'{TRANSPORT_NUMBER}\n  {TASK_NUMBER}\n    TABD FOO\n')

    def test_workbench_list_transport_3(self):
        output = self.do_workbench_list_output('transport', 3)
        self.assertEqual(output, f'{TRANSPORT_NUMBER}\n  {TASK_NUMBER}\n    TABD FOO\n')

    def test_workbench_list_task_0(self):
        output = self.do_workbench_list_output('task', 0)
        self.assertEqual(output, f'{TASK_NUMBER}\n')

    def test_workbench_list_task_1(self):
        output = self.do_workbench_list_output('task', 1)
        self.assertEqual(output, f'{TASK_NUMBER}\n  TABD FOO\n')

    def test_workbench_list_task_2(self):
        output = self.do_workbench_list_output('task', 2)
        self.assertEqual(output, f'{TASK_NUMBER}\n  TABD FOO\n')

    def test_workbench_list_transport(self):
        connection = Connection([Response(SHORTENED_WORKBENCH_XML, 200, {})], user='ANZEIGER')

        with patch('sys.stdout', new_callable=StringIO) as fake_output:
            sap.cli.cts.print_list(connection, SimpleNamespace(type='transport', recursive=0, user=None))

        self.assertEqual(
            [(request.adt_uri, request.params['user']) for request in connection.execs],
            [('/sap/bc/adt/cts/transportrequests', 'ANZEIGER')]
        )

        self.assertEqual(fake_output.getvalue(), f'{TRANSPORT_NUMBER}\n')


if __name__ == '__main__':
    unittest.main()
