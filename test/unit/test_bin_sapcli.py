#!/usr/bin/env python3

import os
import sys
import unittest
from unittest.mock import patch, Mock
from io import StringIO

import importlib.util
from importlib.machinery import SourceFileLoader

import sap

loader = SourceFileLoader(fullname='sapcli', path='bin/sapcli')
spec = importlib.util.spec_from_file_location('sapcli', 'bin/sapcli', loader=loader)
sapcli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sapcli)
sys.modules['sapcli'] = sapcli

ALL_PARAMETERS = [
    'sapcli', '--ashost', 'fixtures', '--sysnr', '69', '--client', '975',
    '--port', '3579', '--no-ssl', '--skip-ssl-validation', '--user',
    'fantomas', '--password', 'Down1oad', '--snc_lib', 'somelib.dylib'
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
            vars(args), {
                'ashost': 'fixtures',
                'sysnr': '69',
                'client': '975',
                'ssl': False,
                'port': 3579,
                'user': 'fantomas',
                'password': 'Down1oad',
                'verify': False,
                'verbose_count': 0,
                'group': None,
                'mshost': None,
                'msserv': None,
                'snc_myname': None,
                'snc_partnername': None,
                'snc_qop': None,
                'snc_lib': "somelib.dylib",
                'sysid': None,
            })

    def test_args_no_ashost(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--ashost')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            sapcli.parse_command_line(test_params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertTrue(fake_output.getvalue().startswith('No SAP Application Server Host name provided: use the option --ashost or the environment variable SAP_ASHOST'))

    def test_args_default_no_ssl(self):
        test_params = ALL_PARAMETERS.copy()
        test_params.remove('--sysnr')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        args = sapcli.parse_command_line(test_params)

        self.assertEqual(args.sysnr, '00')

    def test_args_no_client(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--client')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            sapcli.parse_command_line(test_params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertEqual(fake_output.getvalue().split('\n')[0], 'No SAP Client provided: use the option --client or the environment variable SAP_CLIENT')

    def test_args_no_port(self):
        test_params = ALL_PARAMETERS.copy()
        remove_cmd_param_from_list(test_params, '--port')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        args = sapcli.parse_command_line(test_params)

        self.assertEqual(args.port, 443)

    def test_args_default_no_ssl(self):
        test_params = ALL_PARAMETERS.copy()
        test_params.remove('--no-ssl')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        args = sapcli.parse_command_line(test_params)

        self.assertTrue(args.ssl)

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
        remove_cmd_param_from_list(test_params, '--sysnr')
        remove_cmd_param_from_list(test_params, '--password')
        remove_cmd_param_from_list(test_params, '--user')
        remove_cmd_param_from_list(test_params, '--client')
        remove_cmd_param_from_list(test_params, '--port')
        test_params.remove('--no-ssl')
        test_params.remove('--skip-ssl-validation')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        os.environ['SAP_USER'] = 'fantomas'
        os.environ['SAP_PASSWORD'] = 'Down1oad'
        os.environ['SAP_ASHOST'] = 'vhcalnplci.env.variable'
        os.environ['SAP_SYSNR'] = '33'
        os.environ['SAP_CLIENT'] = '137'
        os.environ['SAP_PORT'] = '13579'
        os.environ['SAP_SSL'] = 'false'

        try:
            args = sapcli.parse_command_line(test_params)
        finally:
            del os.environ['SAP_USER']
            del os.environ['SAP_PASSWORD']
            del os.environ['SAP_ASHOST']
            del os.environ['SAP_SYSNR']
            del os.environ['SAP_CLIENT']
            del os.environ['SAP_PORT']
            del os.environ['SAP_SSL']

        self.assertEqual(args.user, 'fantomas')
        self.assertEqual(args.password, 'Down1oad')
        self.assertEqual(args.ashost, 'vhcalnplci.env.variable')
        self.assertEqual(args.sysnr, '33')
        self.assertEqual(args.port, 13579)
        self.assertEqual(args.client, '137')
        self.assertFalse(args.ssl)
        self.assertTrue(args.verify)


    def test_args_env_no_ssl_variants(self):
        test_params = ALL_PARAMETERS.copy()
        test_params.remove('--no-ssl')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        for variant in ('n', 'N', 'No', 'no', 'NO', 'false', 'FALSE', 'False', 'Off', 'off'):
            os.environ['SAP_SSL'] = variant

            try:
                args = sapcli.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL']

            self.assertFalse(args.ssl, msg=variant)


        for variant in ('any', 'thing', 'else', 'is', 'true', 'or', 'on', 'or', 'YES'):
            os.environ['SAP_SSL'] = variant

            try:
                args = sapcli.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL']

            self.assertTrue(args.ssl, msg=variant)

    def test_args_env_skip_ssl_validation_variants(self):
        test_params = ALL_PARAMETERS.copy()
        test_params.remove('--skip-ssl-validation')
        print("PARAMS: ", str(test_params), file=sys.stderr)

        for variant in ('n', 'N', 'No', 'no', 'NO', 'false', 'FALSE', 'False', 'Off', 'off'):
            os.environ['SAP_SSL_VERIFY'] = variant

            try:
                args = sapcli.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL_VERIFY']

            self.assertFalse(args.verify, msg=variant)


        for variant in ('any', 'thing', 'else', 'is', 'true', 'or', 'on', 'or', 'YES'):
            os.environ['SAP_SSL_VERIFY'] = variant

            try:
                args = sapcli.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL_VERIFY']

            self.assertTrue(args.verify, msg=variant)


class TestParseCommandLineWithCorrnr(unittest.TestCase):

    def configure_mock(self, fake_commands):
        fake_cmd = Mock()
        fake_cmd.name = 'pytest'
        fake_cmd.install_parser = Mock()

        def side_install_parser(subparser):
            command_args = subparser.add_subparsers()

            get_args = command_args.add_parser('command')
            get_args.add_argument('--corrnr')

        fake_cmd.install_parser.side_effect = side_install_parser

        fake_commands.return_value = [(Mock(), fake_cmd)]

    @patch('sap.cli.get_commands')
    def test_args_env_corrnr(self, fake_commands):
        self.configure_mock(fake_commands)

        test_params = ALL_PARAMETERS.copy()
        test_params.append('pytest')
        test_params.append('command')

        exp_corrnr = 'NPLK000001'
        os.environ['SAP_CORRNR'] = exp_corrnr

        try:
            args = sapcli.parse_command_line(test_params)
        finally:
            del os.environ['SAP_CORRNR']

        self.assertEqual(args.corrnr, exp_corrnr)

    @patch('sap.cli.get_commands')
    def test_args_env_and_param_corrnr(self, fake_commands):
        self.configure_mock(fake_commands)

        test_params = ALL_PARAMETERS.copy()
        test_params.append('pytest')
        test_params.append('command')
        test_params.append('--corrnr')
        test_params.append('420WEEDTIME')

        exp_corrnr = 'NPLK000001'
        os.environ['SAP_CORRNR'] = exp_corrnr

        try:
            args = sapcli.parse_command_line(test_params)
        finally:
            del os.environ['SAP_CORRNR']

        self.assertEqual(args.corrnr, '420WEEDTIME')

class TestMainBinary(unittest.TestCase):

    @patch('sapcli.parse_command_line')
    def test_execution_successful(self, fake_parse_command_line):

        fake_parse_command_line.return_value.execute.return_value = 0

        params = ALL_PARAMETERS.copy()
        retval = sapcli.main(params)
        self.assertEqual(retval, 0)

    @patch('sapcli.parse_command_line')
    def test_execution_interrupted(self, fake_parse_command_line):

        fake_parse_command_line.return_value.execute.side_effect = KeyboardInterrupt

        with patch('sys.stderr', new_callable=StringIO) as fake_output:
            params = ALL_PARAMETERS.copy()
            retval = sapcli.main(params)
#
        self.assertEqual(retval, 1)
        self.assertEqual(fake_output.getvalue(), 'Program interrupted!\n')

    @patch('sapcli.parse_command_line')
    def test_execution_failed(self, fake_parse_command_line):

        fake_parse_command_line.return_value.execute.side_effect = sap.errors.ResourceAlreadyExistsError

        with patch('sys.stderr', new_callable=StringIO) as fake_output:
            with patch('sys.stdout', new_callable=StringIO) as fake_stdout_output:
                params = ALL_PARAMETERS.copy()
                retval = sapcli.main(params)

        self.assertEqual(retval, 1)
        self.assertRegex(fake_output.getvalue(), r'^Exception \(ResourceAlreadyExistsError\):')
        self.assertRegex(fake_output.getvalue(), r'Resource already exists')

if __name__ == '__main__':
    unittest.main()
