#!/usr/bin/env python3

import unittest
from argparse import ArgumentParser
from io import StringIO
from unittest.mock import patch, mock_open

import sap.cli.abap
import sap.platform.abap.run

from mock import BufferConsole

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

    def test_run_prints_output(self):
        file_content = 'WRITE.'
        expected_output = 'execution result'

        with patch('builtins.open', mock_open(read_data=file_content)):
            _, console = self._run_with_mock(
                ['run', 'script.abap'],
                execute_abap_retval=expected_output
            )

        self.assertEqual(console.capout, expected_output + '\n')


if __name__ == '__main__':
    unittest.main()
