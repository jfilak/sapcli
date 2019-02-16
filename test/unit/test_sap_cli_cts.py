#!/usr/bin/env python3

import unittest
from types import SimpleNamespace

from sap.errors import SAPCliError
import sap.cli.cts

from mock import Connection, Response
from fixtures_adt import (
    TASK_NUMBER,
    TRANSPORT_NUMBER,
    TASK_RELEASE_OK_RESPONSE,
    TRASNPORT_RELEASE_OK_RESPONSE
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


if __name__ == '__main__':
    unittest.main()

