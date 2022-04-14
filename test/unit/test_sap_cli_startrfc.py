#!/usr/bin/env python3

import json
from argparse import ArgumentParser
from io import StringIO

import sys
import types

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open, call

from mock import ConsoleOutputTestCase, PatcherTestCase, mod_pyrfc, TestRFCLibError, RetainedStringIO
from fixtures_rfc import (
    BAPIRET2_WARNING,
    BAPIRET2_ERROR
)

sys.modules['pyrfc'] = mod_pyrfc

import sap.cli.startrfc


def parse_args(*argv):
    parser = ArgumentParser()
    sap.cli.startrfc.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestStartRFC(ConsoleOutputTestCase, PatcherTestCase):

    def setUp(self):
        super(TestStartRFC, self).setUp()

        self.rfc_function_module = 'STFC_CONNECTION'

        self.patch_console(console=self.console)

        self.response ={
            'ECHOTXT': 'whatever',
            'RESPONSE': 'SAP NW 751 anzeiger',
            'PARAMS': {
                'TABLE': ['A', 'B', 'C']
            }
        }

        self.rfc_connection = MagicMock()
        self.rfc_connection.call.return_value = self.response
        self.patch('sap.rfc.core.rfc_is_available', return_value=True)
        self.patch('sap.rfc.core.SAPRFC_MODULE', new=mod_pyrfc)

    def tearDown(self):
        self.unpatch_all()

    def execute_cmd(self, json_args_obj=None, exp_stdout=None, params=[], exp_stderr='', exp_params=None, exp_call=True):

        if json_args_obj is None:
            args = parse_args(self.rfc_function_module, *params)
        elif json_args_obj == '-':
            args = parse_args(self.rfc_function_module, *params, '-')
        else:
            args = parse_args(self.rfc_function_module, *params, json.dumps(json_args_obj))

        exit_code = args.execute(self.rfc_connection, args)

        if exp_params is not None:
            self.rfc_connection.call.assert_called_once_with(self.rfc_function_module, **exp_params)
        elif json_args_obj is None and exp_call:
            self.rfc_connection.call.assert_called_once_with(self.rfc_function_module)
        elif json_args_obj != '-' and exp_call:
            self.rfc_connection.call.assert_called_once_with(self.rfc_function_module, **json_args_obj)

        if exp_stdout is None:
            exp_stdout = sap.cli.startrfc.FORMATTERS['human'](self.response) + '\n'

        self.assertConsoleContents(self.console, stdout=exp_stdout, stderr=exp_stderr)

        return exit_code

    def test_startrfc_without_parameters(self):
        self.execute_cmd()

    def test_startrfc_with_parameters(self):
        self.execute_cmd({'REQUTEXT':'ping'})

    def test_startrfc_with_stdin(self):
        parameters = {'REQUTEXT':'ping pong'}

        with patch('sys.stdin', StringIO(json.dumps(parameters))):
            self.execute_cmd('-')

        self.rfc_connection.call.assert_called_once_with(self.rfc_function_module, **parameters)

    def test_startrfc_output_json(self):
        self.execute_cmd(exp_stdout=json.dumps(self.response) + '\n', params=['--output', 'json'])

    def test_startrfc_output_dump(self):
        self.execute_cmd(exp_stdout=json.dumps(self.response) + '\n', params=['--output', 'json'])

    def test_startrfc_exception(self):
        self.rfc_connection.call = Mock(side_effect=TestRFCLibError('test startrfc'))
        exit_code = self.execute_cmd(exp_stdout='', exp_stderr=f'''{self.rfc_function_module} failed:
test startrfc
''')
        self.assertEqual(1, exit_code)

    def test_startrfc_with_args_params(self):
        params=[
            '-F', 'arg_file1:/some/path/one',
            '-F', 'arg_file2:/some/path/two',
            '-S', 'arg_string1:first',
            '-S', 'arg_string2:second',
            '-I', 'arg_integer1:1',
            '-I', 'arg_integer2:2'
        ]

        with patch('sap.cli.startrfc.open', mock_open(read_data='source code')) as fake_open:
            exit_code = self.execute_cmd(
                params=params,
                exp_params=dict(
                    ARG_FILE1='source code',
                    ARG_FILE2='source code',
                    ARG_STRING1='first',
                    ARG_STRING2='second',
                    ARG_INTEGER1=1,
                    ARG_INTEGER2=2,
                ),
            )

        self.assertEqual(0, exit_code)

    def test_startrfc_args_param_invalid_file(self):
        params=['-F', 'arg_file1=/some/path/one']

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='',
            exp_stderr='''Error: Invalid parameter arg_file1=/some/path/one. File parameter must be NAME:VALUE.
Exiting with error code because of invalid command line parameters.
''')

        self.assertEqual(1, exit_code)

    def test_startrfc_args_param_file_cant_read(self):
        params=['-F', 'arg_file1:/some/path/one']

        with patch('sap.cli.startrfc.open', mock_open()) as fake_open:
            fake_open.side_effect = OSError('No such file')

            exit_code = self.execute_cmd(
                params=params,
                exp_call=False,
                exp_stdout='',
                exp_stderr='''Error: Cannot process the parameter arg_file1:/some/path/one: Failed to open/read: No such file
Exiting with error code because of invalid command line parameters.
''')

        self.assertEqual(1, exit_code)

    def test_startrfc_args_param_invalid_string(self):
        params=['-S', 'arg_string1=first']

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='',
            exp_stderr='''Error: Invalid parameter arg_string1=first. String parameter must be NAME:VALUE.
Exiting with error code because of invalid command line parameters.
''')

        self.assertEqual(1, exit_code)

    def test_startrfc_args_param_invalid_int(self):
        params=['-I', 'arg_integer1=1']

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='',
            exp_stderr='''Error: Invalid parameter arg_integer1=1. Integer parameter must be NAME:VALUE.
Exiting with error code because of invalid command line parameters.
''')

        self.assertEqual(1, exit_code)

    def test_startrfc_args_result_checker_bapi_for_non_bapi_result(self):
        params=['--result-checker', 'bapi']

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='',
            exp_stderr='''It was requested to evaluate response from STFC_CONNECTION as bapi result, but \
response does not contain required key RETURN. Raw response:
{ 'ECHOTXT': 'whatever',
  'PARAMS': {'TABLE': ['A', 'B', 'C']},
  'RESPONSE': 'SAP NW 751 anzeiger'}
''')

        self.assertEqual(1, exit_code)

    def test_startrfc_args_result_checker_bapi_for_invalid_bapi_result(self):
        params=['--result-checker', 'bapi']

        self.rfc_connection.call.return_value = {
            'RETURN': 'whatever'
        }

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='',
            exp_stderr='''Parsing BAPI response returned from STFC_CONNECTION failed:
Neither dict nor list BAPI return type: str
Raw response:
{'RETURN': 'whatever'}
''')

        self.assertEqual(1, exit_code)

    def test_startrfc_args_result_checker_bapi_for_positive_bapi_result(self):
        params=['--result-checker', 'bapi']

        self.rfc_connection.call.return_value = {
            'FORBIDDEN_OBJECTS': [],
            'RETURN': [BAPIRET2_WARNING]
        }

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='Warning(CICD_GCTS_TR|045): List of ABAP repository objects (piece list) is empty\n',
            exp_stderr='')

        self.assertEqual(0, exit_code)

    def test_startrfc_args_result_checker_bapi_for_negative_bapi_result(self):
        params=['--result-checker', 'bapi']

        self.rfc_connection.call.return_value = {
            'FORBIDDEN_OBJECTS': [],
            'RETURN': [BAPIRET2_ERROR]
        }

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='',
            exp_stderr='Error(CICD_GCTS_TR|045): List of ABAP repository objects (piece list) is empty\n')

        self.assertEqual(1, exit_code)

    @patch('sap.cli.startrfc.path.exists', return_value=True)
    def test_startrfc_args_response_file_exists(self, fake_exists):
        params=['--response-file', './the/file/exists']

        exit_code = self.execute_cmd(
            params=params,
            exp_call=False,
            exp_stdout='',
            exp_stderr='The response file must not exist: ./the/file/exists\n')

        self.assertEqual(fake_exists.mock_calls[-1], call('./the/file/exists'))
        self.assertEqual(1, exit_code)

    @patch('sap.cli.startrfc.path.exists', return_value=False)
    def do_startrfc_args_response_file_error_at_open(self, exception, message, fake_exists):
        params=['--response-file', './the_file']

        self.rfc_connection.call.return_value = {
            'STATUS': 'Super cool!'
        }

        with patch('sap.cli.startrfc.open', side_effect=exception) as m:
            exit_code = self.execute_cmd(
                params=params,
                exp_call=False,
                exp_stdout='',
                exp_stderr='\n'.join([message, '{\'STATUS\': \'Super cool!\'}', ''])
            )

        m.assert_called_once_with('./the_file', 'x', encoding='utf-8')
        self.assertEqual(1, exit_code)

    def test_startrfc_args_response_file_at_open_exists(self):
        self.do_startrfc_args_response_file_error_at_open(
            FileExistsError,
            'Could not create and open the file: ./the_file'
        )

    def test_startrfc_args_response_fle_at_open_permissions(self):
        self.do_startrfc_args_response_file_error_at_open(
            IOError('permissions'),
            'Could not open the file ./the_file: permissions'
        )

    @patch('sap.cli.startrfc.path.exists', return_value=False)
    def test_startrfc_args_response_file_full_success(self, fake_exists):
        params=['--response-file', './the_file']

        self.rfc_connection.call.return_value = {
            'STATUS': 'Super cool!'
        }

        buffer = RetainedStringIO()
        with patch('sap.cli.startrfc.open', mock_open(), create=True) as m:
            m.return_value = buffer
            exit_code = self.execute_cmd(
                params=params,
                exp_call=False,
                exp_stdout='\n'.join(['{\'STATUS\': \'Super cool!\'}', '']),
                exp_stderr=''
            )

        m.assert_called_once_with('./the_file', 'x', encoding='utf-8')
        self.assertEqual(buffer.finalvalue, '{\'STATUS\': \'Super cool!\'}')
        self.assertEqual(0, exit_code)


del sys.modules['pyrfc']
