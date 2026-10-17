#!/usr/bin/env python3

import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from argparse import ArgumentParser

import sap.cli.program

from mock import Connection, Response, patch_get_print_console_with_buffer
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK
from fixtures_adt_program import GET_EXECUTABLE_PROGRAM_ADT_XML, PROGRAM_RUN_OUTPUT
from fixtures_sap_adt_textelements import GET_PROGRAM_TEXT_ELEMENTS_XML


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
        conn = Connection([
            EMPTY_RESPONSE_OK,
            Response(text=GET_EXECUTABLE_PROGRAM_ADT_XML.replace('ZHELLO_WORLD', 'TEST_ACTIVATION'), status_code=200, headers={})
        ])

        args = parse_args('activate', 'test_activation')
        args.execute(conn, args)

        self.assertEqual(len(conn.execs), 2)
        self.assertIn('test_activation', conn.execs[0].body)

    def test_activate_with_text_elements(self):
        conn = Connection([
            EMPTY_RESPONSE_OK,
            Response(text=GET_EXECUTABLE_PROGRAM_ADT_XML.replace('ZHELLO_WORLD', 'TEST_ACTIVATION'), status_code=200, headers={})
        ])

        args = parse_args('activate', 'test_activation')
        args.execute(conn, args)

        self.assertEqual(conn.mock_methods(),
                         [('POST', '/sap/bc/adt/activation'),
                          ('GET', '/sap/bc/adt/programs/programs/test_activation')])

        self.assertIn('<adtcore:objectReference adtcore:uri="/sap/bc/adt/programs/programs/test_activation"'
                      ' adtcore:name="TEST_ACTIVATION"/>', conn.execs[0].body)
        self.assertIn('<adtcore:objectReference adtcore:uri="/sap/bc/adt/textelements/programs/test_activation"'
                      ' adtcore:name="TEST_ACTIVATION"/>', conn.execs[0].body)

    def test_write_main_activate_with_text_elements(self):
        conn = Connection([
            LOCK_RESPONSE_OK,
            EMPTY_RESPONSE_OK,
            EMPTY_RESPONSE_OK,
            EMPTY_RESPONSE_OK,
            Response(text=GET_EXECUTABLE_PROGRAM_ADT_XML.replace('ZHELLO_WORLD', 'ZPROG_WRITER'), status_code=200, headers={})
        ])

        args = parse_args('write', 'zprog_writer', '-', '--activate')
        with patch('sys.stdin', StringIO('report zprog_writer.')):
            args.execute(conn, args)

        self.assertEqual(conn.mock_methods()[3], ('POST', '/sap/bc/adt/activation'))
        self.assertIn('adtcore:uri="/sap/bc/adt/programs/programs/zprog_writer"', conn.execs[3].body)
        self.assertIn('adtcore:uri="/sap/bc/adt/textelements/programs/zprog_writer"', conn.execs[3].body)


class TestProgramTextElements(unittest.TestCase):

    def test_read_textelements(self):
        conn = Connection([Response(text='@MaxLength:20\r\n001=Hello, world!', status_code=200, headers={})])
        args = parse_args('read', 'zprog_reader', '--type', 'textelements')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        self.assertEqual(conn.mock_methods(),
                         [('GET', '/sap/bc/adt/textelements/programs/zprog_reader/source/symbols')])
        self.assertEqual(fake_console.capout, '@MaxLength:20\n001=Hello, world!\n')

    def test_read_main(self):
        conn = Connection([Response(text='report zprog_reader.', status_code=200, headers={})])
        args = parse_args('read', 'zprog_reader', '--type', 'main')

        with patch_get_print_console_with_buffer() as fake_console:
            args.execute(conn, args)

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/programs/programs/zprog_reader/source/main')])
        self.assertEqual(fake_console.capout, 'report zprog_reader.\n')

    def test_write_textelements(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args('write', 'zprog_writer', '--type', 'textelements', '-', '--corrnr', '420')

        with patch('sys.stdin', StringIO('@MaxLength:20\n001=Hello, world!\n')):
            args.execute(conn, args)

        self.assertEqual(conn.mock_methods(),
                         [('POST', '/sap/bc/adt/textelements/programs/zprog_writer'),
                          ('PUT', '/sap/bc/adt/textelements/programs/zprog_writer/source/symbols'),
                          ('POST', '/sap/bc/adt/textelements/programs/zprog_writer')])

        self.assertEqual(conn.execs[1].params, {'lockHandle': 'win', 'corrNr': '420'})
        self.assertEqual(conn.execs[1].body, b'@MaxLength:20\r\n001=Hello, world!\r\n')

    def test_write_textelements_check_is_skipped(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args('write', 'zprog_writer', '--type', 'textelements', '-', '--check')

        with patch('sys.stdin', StringIO('@MaxLength:20\n001=Hello, world!\n')):
            args.execute(conn, args)

        self.assertEqual(conn.mock_methods(),
                         [('POST', '/sap/bc/adt/textelements/programs/zprog_writer'),
                          ('PUT', '/sap/bc/adt/textelements/programs/zprog_writer/source/symbols'),
                          ('POST', '/sap/bc/adt/textelements/programs/zprog_writer')])

    def test_write_textelements_activate(self):
        conn = Connection([
            LOCK_RESPONSE_OK,
            EMPTY_RESPONSE_OK,
            EMPTY_RESPONSE_OK,
            EMPTY_RESPONSE_OK,
            Response(text=GET_PROGRAM_TEXT_ELEMENTS_XML.replace('ZPROG_HELLO_WORLD', 'ZPROG_WRITER'),
                     status_code=200, headers={})
        ])
        args = parse_args('write', 'zprog_writer', '--type', 'textelements', '-', '--activate')

        with patch('sys.stdin', StringIO('@MaxLength:20\n001=Hello, world!\n')):
            exit_code = args.execute(conn, args)

        self.assertEqual(exit_code, 0)
        self.assertEqual(conn.mock_methods(),
                         [('POST', '/sap/bc/adt/textelements/programs/zprog_writer'),
                          ('PUT', '/sap/bc/adt/textelements/programs/zprog_writer/source/symbols'),
                          ('POST', '/sap/bc/adt/textelements/programs/zprog_writer'),
                          ('POST', '/sap/bc/adt/activation'),
                          ('GET', '/sap/bc/adt/textelements/programs/zprog_writer')])

        activate_request = conn.execs[3]
        self.assertIn('adtcore:uri="/sap/bc/adt/textelements/programs/zprog_writer"', activate_request.body)
        self.assertIn('adtcore:name="ZPROG_WRITER"', activate_request.body)
        self.assertNotIn('adtcore:uri="/sap/bc/adt/programs/programs/zprog_writer"', activate_request.body)


class TestProgramExecute(unittest.TestCase):

    def test_execute(self):
        conn = Connection([Response(text=PROGRAM_RUN_OUTPUT, status_code=200, headers={'Content-Type': 'text/plain'})])

        args = parse_args('execute', 'zprog_hello_world')
        with patch('sys.stdout', new_callable=StringIO) as fake_stdout:
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 1)
        self.assertEqual(conn.execs[0].method, 'POST')
        self.assertEqual(conn.execs[0].adt_uri, '/sap/bc/adt/programs/programrun/ZPROG_HELLO_WORLD')
        self.assertEqual(fake_stdout.getvalue(), PROGRAM_RUN_OUTPUT + '\n')


if __name__ == '__main__':
    unittest.main()
