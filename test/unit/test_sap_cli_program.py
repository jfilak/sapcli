#!/usr/bin/env python3

import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from types import SimpleNamespace

import sap.cli.program

from mock import Connection
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_STDIN_REPORT_SRC='report stdin.\n\n" Salute!\n\nwrite: \'hello, command line!\'\n'
FIXTURE_FILE_REPORT_SRC='report file.\n\n" Greet!\n\nwrite: \'hello, file!\'\n'


class TestProgramCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.program.CommandGroup()


class TestProgramWrite(unittest.TestCase):

    def test_read_from_stdin(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        with patch('sys.stdin', StringIO(FIXTURE_STDIN_REPORT_SRC)):
            sap.cli.program.write(conn, SimpleNamespace(name='report', source='-'))

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], FIXTURE_STDIN_REPORT_SRC)

    def test_read_from_file(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        with patch('sap.cli.program.open', mock_open(read_data=FIXTURE_FILE_REPORT_SRC)) as m:
            sap.cli.program.write(conn, SimpleNamespace(name='report', source='file.abap'))

        m.assert_called_once_with('file.abap')

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], FIXTURE_FILE_REPORT_SRC)


if __name__ == '__main__':
    unittest.main()
