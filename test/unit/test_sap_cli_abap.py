#!/usr/bin/env python3

import unittest
from argparse import ArgumentParser
from io import StringIO
from unittest.mock import patch, mock_open

import sap.cli.abap
import sap.platform.abap.run
from sap.errors import SAPCliError

from mock import BufferConsole, Connection, Response

from fixtures_adt_system import (
    RESPONSE_SYSTEM_INFORMATION,
    RESPONSE_JSON_SYSTEM_INFORMATION,
)

FIXTURE_SEARCH_RESPONSE_TWO_RESULTS = """<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:objectReference
    adtcore:uri="/sap/bc/adt/ddic/tabletypes/bapiret2_t"
    adtcore:type="TTYP/DA"
    adtcore:name="BAPIRET2_T"
    adtcore:packageName="SDFM"
    adtcore:description="Return parameter table"/>
  <adtcore:objectReference
    adtcore:uri="/sap/bc/adt/ddic/structures/bapiret2_t1"
    adtcore:type="TABL/DS"
    adtcore:name="BAPIRET2_T1"
    adtcore:packageName="S_EPM_PI"
    adtcore:description="Proxy Structure (generated)"/>
</adtcore:objectReferences>
"""

FIXTURE_SEARCH_RESPONSE_EMPTY = """<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
</adtcore:objectReferences>
"""

parser = ArgumentParser()
sap.cli.abap.CommandGroup().install_parser(parser)


def parse_args(argv):
    args = parser.parse_args(argv)
    return args


def make_console_factory():
    console = BufferConsole()
    return console, lambda: console


class TestAbapRun(unittest.TestCase):

    def _run_with_mock(self, argv, execute_abap_retval='output', stdin_content=None):
        args = parse_args(argv)
        console, factory = make_console_factory()
        args.console_factory = factory

        with patch('sap.platform.abap.run.execute_abap', return_value=execute_abap_retval) as mock_exec:
            if stdin_content is not None:
                with patch('sys.stdin', StringIO(stdin_content)):
                    args.execute('mock_connection', args)
            else:
                args.execute('mock_connection', args)

        return mock_exec, console

    def test_run_from_file(self):
        file_content = 'WRITE "hello".\n'

        with patch('builtins.open', mock_open(read_data=file_content)):
            mock_exec, console = self._run_with_mock(
                ['run', 'my_script.abap'],
                execute_abap_retval='hello'
            )

        mock_exec.assert_called_once_with(
            'mock_connection',
            file_content,
            prefix=sap.platform.abap.run.DEFAULT_PREFIX,
            package=sap.platform.abap.run.DEFAULT_PACKAGE
        )
        self.assertEqual(console.capout, 'hello\n')

    def test_run_from_stdin(self):
        stdin_content = 'WRITE "from stdin".\n'

        mock_exec, console = self._run_with_mock(
            ['run', '-'],
            execute_abap_retval='from stdin',
            stdin_content=stdin_content
        )

        mock_exec.assert_called_once_with(
            'mock_connection',
            stdin_content,
            prefix=sap.platform.abap.run.DEFAULT_PREFIX,
            package=sap.platform.abap.run.DEFAULT_PACKAGE
        )
        self.assertEqual(console.capout, 'from stdin\n')

    def test_run_custom_prefix(self):
        file_content = 'WRITE.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            mock_exec, _ = self._run_with_mock(
                ['run', '--prefix', 'zcl_myrun', 'script.abap']
            )

        mock_exec.assert_called_once_with(
            'mock_connection',
            file_content,
            prefix='zcl_myrun',
            package=sap.platform.abap.run.DEFAULT_PACKAGE
        )

    def test_run_custom_package(self):
        file_content = 'WRITE.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            mock_exec, _ = self._run_with_mock(
                ['run', '--package', '$mypackage', 'script.abap']
            )

        mock_exec.assert_called_once_with(
            'mock_connection',
            file_content,
            prefix=sap.platform.abap.run.DEFAULT_PREFIX,
            package='$mypackage'
        )

    def test_run_with_define_substitutes_token(self):
        file_content = 'WRITE {{VALUE}}.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            mock_exec, _ = self._run_with_mock(
                ['run', '--define', 'VALUE=42', 'script.abap']
            )

        mock_exec.assert_called_once_with(
            'mock_connection',
            'WRITE 42.',
            prefix=sap.platform.abap.run.DEFAULT_PREFIX,
            package=sap.platform.abap.run.DEFAULT_PACKAGE
        )

    def test_run_with_define_short_flag(self):
        file_content = 'WRITE {{VALUE}}.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            mock_exec, _ = self._run_with_mock(
                ['run', '-D', 'VALUE=42', 'script.abap']
            )

        mock_exec.assert_called_once_with(
            'mock_connection',
            'WRITE 42.',
            prefix=sap.platform.abap.run.DEFAULT_PREFIX,
            package=sap.platform.abap.run.DEFAULT_PACKAGE
        )

    def test_run_with_multiple_defines(self):
        file_content = '{{A}} {{B}}'

        with patch('builtins.open', mock_open(read_data=file_content)):
            mock_exec, _ = self._run_with_mock(
                ['run', '--define', 'A=foo', '--define', 'B=bar', 'script.abap']
            )

        mock_exec.assert_called_once_with(
            'mock_connection',
            'foo bar',
            prefix=sap.platform.abap.run.DEFAULT_PREFIX,
            package=sap.platform.abap.run.DEFAULT_PACKAGE
        )

    def test_run_without_define_token_in_source_raises(self):
        file_content = 'WRITE {{VALUE}}.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            args = parse_args(['run', 'script.abap'])
            _, factory = make_console_factory()
            args.console_factory = factory

            with patch('sap.platform.abap.run.execute_abap') as mock_exec:
                with self.assertRaises(SAPCliError) as caught:
                    args.execute('mock_connection', args)

            mock_exec.assert_not_called()

        self.assertIn('VALUE', str(caught.exception))

    def test_run_define_value_may_contain_equals(self):
        file_content = 'cond = {{EXPR}}.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            mock_exec, _ = self._run_with_mock(
                ['run', '--define', 'EXPR=a = b', 'script.abap']
            )

        mock_exec.assert_called_once_with(
            'mock_connection',
            'cond = a = b.',
            prefix=sap.platform.abap.run.DEFAULT_PREFIX,
            package=sap.platform.abap.run.DEFAULT_PACKAGE
        )

    def test_run_undefined_token_raises_and_skips_execution(self):
        file_content = 'WRITE {{MISSING}}.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            args = parse_args(['run', '--define', 'OTHER=1', 'script.abap'])
            _, factory = make_console_factory()
            args.console_factory = factory

            with patch('sap.platform.abap.run.execute_abap') as mock_exec:
                with self.assertRaises(SAPCliError) as caught:
                    args.execute('mock_connection', args)

            mock_exec.assert_not_called()

        self.assertIn('MISSING', str(caught.exception))

    def test_run_reserved_delimiter_raises_and_skips_execution(self):
        file_content = '{% if x %}WRITE.{% endif %}'

        with patch('builtins.open', mock_open(read_data=file_content)):
            args = parse_args(['run', 'script.abap'])
            _, factory = make_console_factory()
            args.console_factory = factory

            with patch('sap.platform.abap.run.execute_abap') as mock_exec:
                with self.assertRaises(SAPCliError) as caught:
                    args.execute('mock_connection', args)

            mock_exec.assert_not_called()

        self.assertIn('{%', str(caught.exception))

    def test_run_define_invalid_format_raises(self):
        file_content = 'WRITE.'

        with patch('builtins.open', mock_open(read_data=file_content)):
            args = parse_args(['run', '--define', 'NOEQUALS', 'script.abap'])
            _, factory = make_console_factory()
            args.console_factory = factory

            with self.assertRaises(SAPCliError) as caught:
                args.execute('mock_connection', args)

        self.assertIn('NOEQUALS', str(caught.exception))

    def test_run_prints_output(self):
        file_content = 'WRITE.'
        expected_output = 'execution result'

        with patch('builtins.open', mock_open(read_data=file_content)):
            _, console = self._run_with_mock(
                ['run', 'script.abap'],
                execute_abap_retval=expected_output
            )

        self.assertEqual(console.capout, expected_output + '\n')


class TestParseDefinitions(unittest.TestCase):

    def test_single_definition(self):
        self.assertEqual(sap.cli.abap._parse_definitions(['A=1']), {'A': '1'})

    def test_multiple_definitions(self):
        self.assertEqual(
            sap.cli.abap._parse_definitions(['A=1', 'B=2']),
            {'A': '1', 'B': '2'}
        )

    def test_value_may_contain_equals(self):
        self.assertEqual(sap.cli.abap._parse_definitions(['A=1=2']), {'A': '1=2'})

    def test_empty_value_allowed(self):
        self.assertEqual(sap.cli.abap._parse_definitions(['A=']), {'A': ''})

    def test_later_definition_overrides_earlier(self):
        self.assertEqual(sap.cli.abap._parse_definitions(['A=1', 'A=2']), {'A': '2'})

    def test_missing_equals_raises(self):
        with self.assertRaises(SAPCliError):
            sap.cli.abap._parse_definitions(['NOEQ'])

    def test_empty_name_raises(self):
        with self.assertRaises(SAPCliError):
            sap.cli.abap._parse_definitions(['=value'])

    def test_name_with_underscore_allowed(self):
        self.assertEqual(sap.cli.abap._parse_definitions(['MY_NAME=1']), {'MY_NAME': '1'})

    def test_name_with_space_raises(self):
        with self.assertRaises(SAPCliError):
            sap.cli.abap._parse_definitions(['A B=1'])

    def test_name_with_colon_dash_raises(self):
        with self.assertRaises(SAPCliError):
            sap.cli.abap._parse_definitions(['A:-B=1'])

    def test_name_with_pipe_raises(self):
        with self.assertRaises(SAPCliError):
            sap.cli.abap._parse_definitions(['A|B=1'])

    def test_name_starting_with_digit_raises(self):
        with self.assertRaises(SAPCliError):
            sap.cli.abap._parse_definitions(['1A=2'])


class TestAbapSystemInfo(unittest.TestCase):

    def test_systeminfo_prints_all_entries(self):
        """Test that systeminfo prints key: value lines for all entries"""
        connection = Connection([RESPONSE_SYSTEM_INFORMATION, RESPONSE_JSON_SYSTEM_INFORMATION])
        args = parse_args(['systeminfo'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        output = console.capout
        lines = output.strip().split('\n')

        # 24 XML entries + 5 JSON entries
        self.assertEqual(len(lines), 29)

    def test_systeminfo_output_format(self):
        """Test that systeminfo prints entries in key: value format"""
        connection = Connection([RESPONSE_SYSTEM_INFORMATION, RESPONSE_JSON_SYSTEM_INFORMATION])
        args = parse_args(['systeminfo'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        output = console.capout
        self.assertIn('ApplicationServerName: C50_ddci\n', output)
        self.assertIn('DBName: C50/02\n', output)
        self.assertIn('OSName: Linux\n', output)
        self.assertIn('SID: C50\n', output)
        self.assertIn('userName: DEVELOPER\n', output)
        self.assertIn('client: 100\n', output)
        self.assertIn('language: EN\n', output)

    def test_systeminfo_sends_requests(self):
        """Test that systeminfo sends GET requests to both endpoints"""
        connection = Connection([RESPONSE_SYSTEM_INFORMATION, RESPONSE_JSON_SYSTEM_INFORMATION])
        args = parse_args(['systeminfo'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(len(connection.execs), 2)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/system/information')
        self.assertEqual(connection.execs[1].method, 'GET')
        self.assertEqual(connection.execs[1].adt_uri, '/sap/bc/adt/core/http/systeminformation')

    def test_systeminfo_key_prints_value_only(self):
        """Test that --key prints only the matching value"""
        connection = Connection([RESPONSE_SYSTEM_INFORMATION, RESPONSE_JSON_SYSTEM_INFORMATION])
        args = parse_args(['systeminfo', '--key', 'OSName'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(console.capout, 'Linux\n')

    def test_systeminfo_key_json_entry(self):
        """Test that --key works for entries from the JSON endpoint"""
        connection = Connection([RESPONSE_SYSTEM_INFORMATION, RESPONSE_JSON_SYSTEM_INFORMATION])
        args = parse_args(['systeminfo', '--key', 'userName'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(console.capout, 'DEVELOPER\n')

    def test_systeminfo_key_not_found(self):
        """Test that --key with unknown key prints nothing"""
        connection = Connection([RESPONSE_SYSTEM_INFORMATION, RESPONSE_JSON_SYSTEM_INFORMATION])
        args = parse_args(['systeminfo', '--key', 'NonExistent'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(console.capout, '')


class TestAbapFind(unittest.TestCase):

    def test_find_prints_table_with_results(self):
        connection = Connection([
            Response(text=FIXTURE_SEARCH_RESPONSE_TWO_RESULTS, status_code=200),
        ])
        args = parse_args(['find', 'BAPIRET2_T'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        output = console.capout
        lines = output.strip().split('\n')
        self.assertEqual(len(lines), 4)  # header + separator + 2 results

        self.assertIn('Object type', lines[0])
        self.assertIn('Name', lines[0])
        self.assertIn('Description', lines[0])

        self.assertIn('TTYP/DA', lines[2])
        self.assertIn('BAPIRET2_T', lines[2])
        self.assertIn('Return parameter table', lines[2])

        self.assertIn('TABL/DS', lines[3])
        self.assertIn('BAPIRET2_T1', lines[3])
        self.assertIn('Proxy Structure (generated)', lines[3])

    def test_find_empty_results(self):
        connection = Connection([
            Response(text=FIXTURE_SEARCH_RESPONSE_EMPTY, status_code=200),
        ])
        args = parse_args(['find', 'NONEXISTENT'])
        console, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        output = console.capout
        lines = output.strip().split('\n')
        # header + separator only
        self.assertEqual(len(lines), 2)
        self.assertIn('Object type', lines[0])

    def test_find_appends_wildcard(self):
        connection = Connection([
            Response(text=FIXTURE_SEARCH_RESPONSE_EMPTY, status_code=200),
        ])
        args = parse_args(['find', 'BAPIRET2_T'])
        _, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(connection.execs[0].params['query'], 'BAPIRET2_T*')

    def test_find_does_not_double_wildcard(self):
        connection = Connection([
            Response(text=FIXTURE_SEARCH_RESPONSE_EMPTY, status_code=200),
        ])
        args = parse_args(['find', 'BAPIRET2_T*'])
        _, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(connection.execs[0].params['query'], 'BAPIRET2_T*')

    def test_find_sends_correct_request(self):
        connection = Connection([
            Response(text=FIXTURE_SEARCH_RESPONSE_EMPTY, status_code=200),
        ])
        args = parse_args(['find', 'BAPIRET2_T'])
        _, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertIn('repository/informationsystem/search', connection.execs[0].adt_uri)
        self.assertEqual(connection.execs[0].params['operation'], 'quickSearch')
        self.assertEqual(connection.execs[0].params['query'], 'BAPIRET2_T*')
        self.assertEqual(connection.execs[0].params['maxResults'], 51)

    def test_find_custom_max_results(self):
        connection = Connection([
            Response(text=FIXTURE_SEARCH_RESPONSE_EMPTY, status_code=200),
        ])
        args = parse_args(['find', '--max-results', '10', 'BAPIRET2_T'])
        _, factory = make_console_factory()
        args.console_factory = factory

        args.execute(connection, args)

        self.assertEqual(connection.execs[0].params['maxResults'], 10)

    def test_find_empty_term_raises(self):
        args = parse_args(['find', '   '])
        _, factory = make_console_factory()
        args.console_factory = factory

        with self.assertRaises(SAPCliError) as caught:
            args.execute(Connection(), args)

        self.assertIn('No search term provided', str(caught.exception))

    def test_find_zero_max_results_raises(self):
        args = parse_args(['find', '--max-results', '0', 'BAPIRET2_T'])
        _, factory = make_console_factory()
        args.console_factory = factory

        with self.assertRaises(SAPCliError) as caught:
            args.execute(Connection(), args)

        self.assertIn('must be positive', str(caught.exception))

    def test_find_negative_max_results_raises(self):
        args = parse_args(['find', '--max-results', '-5', 'BAPIRET2_T'])
        _, factory = make_console_factory()
        args.console_factory = factory

        with self.assertRaises(SAPCliError) as caught:
            args.execute(Connection(), args)

        self.assertIn('must be positive', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
