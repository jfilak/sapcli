#!/usr/bin/env python3

import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from argparse import ArgumentParser

import sap.cli.program

from mock import ConnectionViaHTTP as Connection
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_STDIN_REPORT_SRC='report stdin.\n\n" Salute!\n\nwrite: \'hello, command line!\'\n'
FIXTURE_FILE_REPORT_SRC='report file.\n\n" Greet!\n\nwrite: \'hello, file!\'\n'

parser = ArgumentParser()
sap.cli.program.CommandGroup().install_parser(parser)

def parse_args(*argv):
    return parser.parse_args(argv)

class TestProgramCreate(unittest.TestCase):

    def test_create_program_with_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('create', 'report', 'description', 'package', '--corrnr', '420')
        args.execute(connection, args)

        self.assertEqual(connection.execs[0].params['corrNr'], '420')


class TestProgramWrite(unittest.TestCase):

    def test_read_from_stdin(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'report', '-')
        with patch('sys.stdin', StringIO(FIXTURE_STDIN_REPORT_SRC)):
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], bytes(FIXTURE_STDIN_REPORT_SRC[:-1], 'utf-8'))

    def test_read_from_file(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'report', 'file.abap')
        with patch('sap.cli.object.open', mock_open(read_data=FIXTURE_FILE_REPORT_SRC)) as m:
            args.execute(conn, args)

        m.assert_called_once_with('file.abap', 'r', encoding='utf8')

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], bytes(FIXTURE_FILE_REPORT_SRC[:-1], 'utf-8'))

    def test_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = parse_args('write', 'report', 'file.abap', '--corrnr', '420')
        with patch('sap.cli.object.open', mock_open(read_data=FIXTURE_FILE_REPORT_SRC)) as m:
            args.execute(conn, args)

        self.assertEqual(conn.execs[1].params['corrNr'], '420')


class TestProgramActivate(unittest.TestCase):

    def test_activate(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        args = parse_args('activate', 'test_activation')
        args.execute(conn, args)

        self.assertEqual(len(conn.execs), 1)
        self.assertIn('test_activation', conn.execs[0].body)


if __name__ == '__main__':
    unittest.main()
