#!/usr/bin/env python3

import unittest
from argparse import ArgumentParser
from unittest.mock import patch, Mock
from io import StringIO
from types import SimpleNamespace

from sap.errors import SAPCliError
import sap.cli.cts

from mock import ConnectionViaHTTP as Connection, Response, ConsoleOutputTestCase, PatcherTestCase
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


class TestCTSCreate(unittest.TestCase):

    def test_create_invalid_request_type(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.cts.create(None, SimpleNamespace(type='foo'))

        self.assertEqual(str(cm.exception), 'Internal error: unknown request type: foo')

    @patch('sap.cli.cts.WorkbenchTransport')
    def test_create_transport(self, fake_transport):
        def mock_transport(*args, **kwargs):
            ret = Mock()
            ret.create.return_value = SimpleNamespace(number='NPLK000018', data='''<?xml version="1.0" encoding="utf-8"?><tm:root tm:useraction="newrequest" xmlns:tm="http://www.sap.com/cts/adt/tm"><tm:request tm:number="NPLK000018" tm:parent="" tm:desc="spacli transport" tm:type="K" tm:target="LOCAL" tm:target_desc="" tm:cts_project="" tm:cts_project_desc="" tm:uri="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/NPLK000018"><tm:long_desc/><atom:link href="/sap/bc/adt/cts/transportrequests/NPLK000018" rel="http://www.sap.com/cts/relations/adturi" type="application/vnd.sap.adt.transportrequests.v1+xml" title="Transport Organizer ADT URI" xmlns:atom="http://www.w3.org/2005/Atom"/><atom:link href="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/NPLK000018" rel="http://www.sap.com/cts/relations/vituri" type="application/vnd.sap.sapgui" title="Transport Organizer VIT URI" xmlns:atom="http://www.w3.org/2005/Atom"/></tm:request></tm:root>''')

            return ret

        fake_transport.side_effect = mock_transport

        connection = Mock()

        args = parse_args('create', 'transport', '-d', 'my transport')
        with patch('sap.cli.core.printout') as fake_print:
            args.execute(connection, args)

        fake_print.assert_called_once_with('NPLK000018')


class TestCTSRelease(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        ConsoleOutputTestCase.setUp(self)
        self.patch_console(console=self.console)

        self.connection = Connection()

    def test_release_invalid_request_type(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.cts.release(None, SimpleNamespace(type='foo', number='WHATEVER', recursive=False))

        self.assertEqual(str(cm.exception), 'Internal error: unknown request type: foo')

    def release(self, **kwargs):
        sap.cli.cts.release(self.connection, SimpleNamespace(**kwargs))

    def do_check_command_release(self, request_type, number, response):
        self.connection.set_responses(
            Response(response, 200, {})
        )

        self.release(type=request_type, number=number, recursive=False)

        self.assertEqual(
            [request.adt_uri for request in self.connection.execs],
            [f'/sap/bc/adt/cts/transportrequests/{number}/newreleasejobs']
        )

        self.assertConsoleContents(self.console, stdout=f'''Releasing {number}
Transport request/task {number} was successfully released
''')

    def test_release_transport(self):
        self.do_check_command_release('transport', TRANSPORT_NUMBER, TRASNPORT_RELEASE_OK_RESPONSE)

    def test_release_task(self):
        self.do_check_command_release('task', TASK_NUMBER, TASK_RELEASE_OK_RESPONSE)

    @patch('sap.adt.cts.AbstractWorkbenchRequest.fetch')
    def test_recursive_release(self, fake_fetch):
        self.connection.set_responses(
            Response(TRASNPORT_RELEASE_OK_RESPONSE, 200, {})
        )

        self.release(type='transport', number=TRANSPORT_NUMBER, recursive=True)
        self.assertConsoleContents(self.console, stdout=f'''Fetching details of {TRANSPORT_NUMBER} because of recursive execution
Releasing {TRANSPORT_NUMBER}
Transport request/task {TRANSPORT_NUMBER} was successfully released
''')
        fake_fetch.assert_called_once()


class TestCTSDelete(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        ConsoleOutputTestCase.setUp(self)
        self.patch_console(console=self.console)

        self.connection = Connection()

    def test_delete_invalid_request_type(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.cts.delete(None, SimpleNamespace(type='foo', number='WHATEVER', recursive=False))

        self.assertEqual(str(cm.exception), 'Internal error: unknown request type: foo')

    def delete(self, **kwargs):
        sap.cli.cts.delete(self.connection, SimpleNamespace(**kwargs))

    def do_check_command_delete(self, request_type, number):
        self.delete(type=request_type, number=number, recursive=False)

        self.assertEqual(
            [(request.method, request.adt_uri) for request in self.connection.execs],
            [('DELETE', f'/sap/bc/adt/cts/transportrequests/{number}')]
        )

        self.assertConsoleContents(self.console, stdout=f'''Deleting {number}
Deleted {number}
''')

    def test_delete_transport(self):
        self.do_check_command_delete('transport', TRANSPORT_NUMBER)

    def test_delete_task(self):
        self.do_check_command_delete('task', TASK_NUMBER)

    @patch('sap.adt.cts.AbstractWorkbenchRequest.fetch')
    def test_recursive_delete(self, fake_fetch):
        self.delete(type='transport', number=TRANSPORT_NUMBER, recursive=True)
        self.assertConsoleContents(self.console, stdout=f'''Fetching details of {TRANSPORT_NUMBER} because of recursive execution
Deleting {TRANSPORT_NUMBER}
Deleted {TRANSPORT_NUMBER}
''')
        fake_fetch.assert_called_once()


class TestCTSReassign(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        ConsoleOutputTestCase.setUp(self)
        self.patch_console(console=self.console)

        self.connection = Connection()

    def test_reassign_invalid_request_type(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.cts.reassign(None, SimpleNamespace(owner='someone', type='foo', number='WHATEVER', recursive=False))

        self.assertEqual(str(cm.exception), 'Internal error: unknown request type: foo')

    def reassign(self, **kwargs):
        sap.cli.cts.reassign(self.connection, SimpleNamespace(**kwargs))

    def do_check_command_reassign(self, request_type, number):
        self.reassign(owner='someone', type=request_type, number=number, recursive=False)

        self.assertEqual(
            [(request.method, request.adt_uri) for request in self.connection.execs],
            [('PUT', f'/sap/bc/adt/cts/transportrequests/{number}')]
        )

        self.assertConsoleContents(self.console, stdout=f'''Re-assigning {number}
Re-assigned {number}
''')

    def test_reassign_transport(self):
        self.do_check_command_reassign('transport', TRANSPORT_NUMBER)

    def test_reassign_task(self):
        self.do_check_command_reassign('task', TASK_NUMBER)

    @patch('sap.adt.cts.AbstractWorkbenchRequest.fetch')
    def test_recursive_reassign(self, fake_fetch):
        self.reassign(owner='someone', type='transport', number=TRANSPORT_NUMBER, recursive=True)
        self.assertConsoleContents(self.console, stdout=f'''Fetching details of {TRANSPORT_NUMBER} because of recursive execution
Re-assigning {TRANSPORT_NUMBER}
Re-assigned {TRANSPORT_NUMBER}
''')
        fake_fetch.assert_called_once()


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
