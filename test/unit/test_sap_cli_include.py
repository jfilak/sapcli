#!/usr/bin/env python3

import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from argparse import ArgumentParser

import sap.cli.include

from mock import (
    ConsoleOutputTestCase,
    Connection,
    PatcherTestCase,
    Response
)
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK
from fixtures_adt_program import (
    GET_INCLUDE_PROGRAM_ADT_XML,
    GET_INCLUDE_PROGRAM_WITH_CONTEXT_ADT_XML
)
#from test.unit.fixtures_adt_class import GET_CLASS_ADT_XML

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

        m.assert_called_once_with('zinclude.abap', 'r', encoding='utf8')

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
        conn = Connection([
            EMPTY_RESPONSE_OK,
            Response(text=GET_INCLUDE_PROGRAM_ADT_XML.replace('ZHELLO_INCLUDE', 'test_activation'), status_code=200, headers={})
        ])

        args = parse_args('activate', 'test_activation')
        args.execute(conn, args)

        self.assertEqual(len(conn.execs), 2)
        self.assertIn('test_activation"', conn.execs[0].body)

    def test_activate_with_master(self):
        conn = Connection([
            EMPTY_RESPONSE_OK,
            Response(text=GET_INCLUDE_PROGRAM_ADT_XML.replace('ZHELLO_INCLUDE', 'test_activation'), status_code=200, headers={})
        ])

        args = parse_args('activate', 'test_activation', '-m', 'MASTER_REPORT')
        args.execute(conn, args)

        self.assertEqual(len(conn.execs), 2)
        self.assertRegex(conn.execs[0].body, '.*adtcore:uri=[^?]*test_activation\?context=[^"]*master_report".*')


class TestIncludeAttributes(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)

    def test_attributes_with_context(self):
        conn = Connection(
            [Response(status_code=200, text=GET_INCLUDE_PROGRAM_WITH_CONTEXT_ADT_XML)]
        )

        args = parse_args('attributes', 'ZHELLO_INCLUDE')
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''Name       : ZHELLO_INCLUDE
Description: Hello include!
Responsible: FILAK
Package    : $TEST
Main       : ZJAKUB_IS_HANDSOME_GENIUS (PROG/P)
''')

    def test_attributes_without_context(self):
        conn = Connection(
            [Response(status_code=200, text=GET_INCLUDE_PROGRAM_ADT_XML)]
        )

        args = parse_args('attributes', 'ZHELLO_INCLUDE')
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''Name       : ZHELLO_INCLUDE
Description: Hello include!
Responsible: FILAK
Package    : $TEST
Main       :
''')


if __name__ == '__main__':
    unittest.main()
