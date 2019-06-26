#!/usr/bin/env python3

import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from argparse import ArgumentParser

import sap.cli.include

from mock import Connection
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_STDIN_REPORT_SRC='* from stdin'
FIXTURE_FILE_REPORT_SRC='* from file'


parser = ArgumentParser()
sap.cli.include.CommandGroup().install_parser(parser)


def parse_args(*argv):
    return parser.parse_args(argv)


class TestIncludeCreate(unittest.TestCase):

    def test_create_include_with_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', 'zinclude', 'description', 'package', '--corrnr', '420')
        args.execute(connection, args)

        self.assertEqual(connection.execs[0].params['corrNr'], '420')


class TestIncludeWrite(unittest.TestCase):

    def test_read_from_stdin(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'zinclude', '-')
        with patch('sys.stdin', StringIO(FIXTURE_STDIN_REPORT_SRC)):
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], bytes(FIXTURE_STDIN_REPORT_SRC, 'utf-8'))

    def test_read_from_file(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'zinclude', 'zinclude.abap')
        with patch('sap.cli.object.open', mock_open(read_data=FIXTURE_FILE_REPORT_SRC)) as m:
            args.execute(conn, args)

        m.assert_called_once_with('zinclude.abap', 'r')

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], bytes(FIXTURE_FILE_REPORT_SRC, 'utf-8'))

    def test_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'zinclude', 'zinclude.abap', '--corrnr', '420')
        with patch('sap.cli.object.open', mock_open(read_data=FIXTURE_FILE_REPORT_SRC)) as m:
            args.execute(conn, args)

        self.assertEqual(conn.execs[1].params['corrNr'], '420')


class TestIncludeActivate(unittest.TestCase):

    def test_activate(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('activate', 'test_activation')
        args.execute(conn, args)

        self.assertEqual(len(conn.execs), 1)
        self.assertIn('test_activation"', conn.execs[0].body)

    def test_activate_with_master(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('activate', 'test_activation', '-m', 'MASTER_REPORT')
        args.execute(conn, args)

        self.assertEqual(len(conn.execs), 1)
        self.assertRegex(conn.execs[0].body, '.*adtcore:uri=[^?]*test_activation\?context=[^"]*master_report".*')


if __name__ == '__main__':
    unittest.main()
