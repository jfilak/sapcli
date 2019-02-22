#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import patch
from io import StringIO
from types import SimpleNamespace

import importlib.util
from importlib.machinery import SourceFileLoader

loader = SourceFileLoader(fullname='sapcli', path='bin/sapcli')
spec = importlib.util.spec_from_file_location('sapcli', 'bin/sapcli', loader=loader)
sapcli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sapcli)
sys.modules['sapcli'] = sapcli


ALL_PARAMETERS = [
    'sapcli', '--ashost', 'fixtures', '--client', '975', '--port', '3579',
    '--no-ssl', '--user', 'fantomas', '--password', 'Down1oad'
]


def remove_cmd_param_from_list(params_list, param_name):
    index = params_list.index(param_name)
    del params_list[index]
    del params_list[index]


class TestParseCommandLine(unittest.TestCase):

    def test_args_sanity(self):
        params = ALL_PARAMETERS.copy()
        args = sapcli.parse_command_line(params)

        self.assertEqual(
            vars(args),
            {'ashost':'fixtures', 'client':'975', 'ssl':False, 'port':3579,
             'user':'fantomas', 'password':'Down1oad', 'verbose_count':0})

    def test_args_no_ashost(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--ashost')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            sapcli.parse_command_line(test_params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertTrue(fake_output.getvalue().startswith('No SAP Application Server Host name provided: use the option --ashost or the environment variable SAP_ASHOST'))

    def test_args_no_client(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--client')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            sapcli.parse_command_line(test_params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertEqual(fake_output.getvalue().split('\n')[0], 'No SAP Client provided: use the option --client or the environment variable SAP_CLIENT')

    def test_args_ask_user(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--user')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        with patch('sapcli.input', lambda pfx: 'fantomas') as fake_input:
            args = sapcli.parse_command_line(test_params)

        self.assertEqual(args.user, 'fantomas')

    def test_args_ask_password(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--password')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        with patch('getpass.getpass', lambda : 'Down1oad') as fake_getpass:
            args = sapcli.parse_command_line(test_params)

        self.assertEqual(args.user, 'fantomas')

    def test_args_ask_user_and_password(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--password')
        remove_cmd_param_from_list(test_params, '--user')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        with patch('getpass.getpass', lambda : 'Down1oad') as fake_getpass, \
             patch('sapcli.input', lambda pfx: 'fantomas') as fake_input:
            args = sapcli.parse_command_line(test_params)

        self.assertEqual(args.user, 'fantomas')
        self.assertEqual(args.password, 'Down1oad')

    def test_args_env(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--ashost')
        remove_cmd_param_from_list(test_params, '--password')
        remove_cmd_param_from_list(test_params, '--user')
        remove_cmd_param_from_list(test_params, '--client')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        os.environ['SAP_USER'] = 'fantomas'
        os.environ['SAP_PASSWORD'] = 'Down1oad'
        os.environ['SAP_ASHOST'] = 'vhcalnplci.env.variable'
        os.environ['SAP_CLIENT'] = '137'

        try:
            args = sapcli.parse_command_line(test_params)
        finally:
            del os.environ['SAP_USER']
            del os.environ['SAP_PASSWORD']
            del os.environ['SAP_ASHOST']
            del os.environ['SAP_CLIENT']

        self.assertEqual(args.user, 'fantomas')
        self.assertEqual(args.password, 'Down1oad')
        self.assertEqual(args.ashost, 'vhcalnplci.env.variable')
        self.assertEqual(args.port, 3579)
        self.assertEqual(args.client, '137')
        self.assertEqual(args.ssl, False)


if __name__ == '__main__':
    unittest.main()
