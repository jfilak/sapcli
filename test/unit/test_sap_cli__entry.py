import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from io import StringIO

import sap
import sap.cli._entry as entry
from sap.config import ConfigFile
from sap.http.truststore_support import TruststoreNotAvailableError
from sap.rest.errors import TimedOutRequestError as RestTimedOutRequestError
from sap.odata.errors import TimedOutRequestError as ODataTimedOutRequestError

TEST_CONFIG_PATH = Path('/test/config.yml')

ALL_PARAMETERS = [
    'sapcli', '--ashost', 'fixtures', '--sysnr', '69', '--client', '975',
    '--port', '3579', '--no-ssl', '--skip-ssl-validation', '--user',
    'fantomas', '--password', 'Down1oad', '--snc_lib', 'somelib.dylib'
]

MOCK_COMMAND_NAME = 'mockcommand'
MOCK_SUBCOMMAND_NAME = 'run'


def remove_cmd_param_from_list(params_list, param_name):
    index = params_list.index(param_name)
    del params_list[index]
    del params_list[index]


def make_mock_command():
    """Create a mock command that registers a subcommand with execute default."""

    mock_execute = Mock(return_value=0)
    fake_cmd = Mock()
    fake_cmd.name = MOCK_COMMAND_NAME
    fake_cmd.description = 'Mock command for testing'

    def side_install_parser(subparser):
        command_args = subparser.add_subparsers()
        get_args = command_args.add_parser(MOCK_SUBCOMMAND_NAME)
        get_args.set_defaults(execute=mock_execute)

    fake_cmd.install_parser.side_effect = side_install_parser
    return fake_cmd


def get_tested_parameters():
    """Return ALL_PARAMETERS with the mock command and subcommand appended."""

    return ALL_PARAMETERS + [MOCK_COMMAND_NAME, MOCK_SUBCOMMAND_NAME]


def get_tls_verifying_parameters():
    """Tested parameters with TLS enabled and certificate validation on.

    ALL_PARAMETERS disables both (--no-ssl, --skip-ssl-validation); drop them so
    the operating system trust store is actually consulted.
    """

    params = get_tested_parameters()
    params.remove('--no-ssl')
    params.remove('--skip-ssl-validation')
    return params


class TestParseCommandLine(unittest.TestCase):

    def setUp(self):
        self._get_commands_patcher = patch('sap.cli.get_commands')
        fake_commands = self._get_commands_patcher.start()
        self._fake_cmd = make_mock_command()
        fake_commands.return_value = [(Mock(), self._fake_cmd)]

        self._config_patcher = patch('sap.cli._entry.ConfigFile.load', return_value=ConfigFile({}, TEST_CONFIG_PATH))
        self._config_patcher.start()

    def tearDown(self):
        self._config_patcher.stop()
        self._get_commands_patcher.stop()

    def test_args_sanity(self):
        params = get_tested_parameters()
        args = entry.parse_command_line(params)

        parsed = vars(args)

        self.assertEqual(parsed['ashost'], 'fixtures')
        self.assertEqual(parsed['sysnr'], '69')
        self.assertEqual(parsed['client'], '975')
        self.assertFalse(parsed['ssl'])
        self.assertEqual(parsed['port'], 3579)
        self.assertEqual(parsed['user'], 'fantomas')
        self.assertEqual(parsed['password'], 'Down1oad')
        self.assertFalse(parsed['verify'])
        self.assertEqual(parsed['verbose_count'], 0)
        self.assertIsNone(parsed['group'])
        self.assertIsNone(parsed['mshost'])
        self.assertIsNone(parsed['msserv'])
        self.assertIsNone(parsed['snc_myname'])
        self.assertIsNone(parsed['snc_partnername'])
        self.assertIsNone(parsed['snc_qop'])
        self.assertEqual(parsed['snc_lib'], 'somelib.dylib')
        self.assertIsNone(parsed['sysid'])
        self.assertIsNone(parsed['ssl_server_cert'])
        self.assertTrue(callable(parsed['execute']))

    def test_args_no_ashost(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--ashost')

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            entry.parse_command_line(test_params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertTrue(fake_output.getvalue().startswith(
            'No SAP Application Server Host name provided: use the option --ashost or the environment variable SAP_ASHOST'))

    def test_args_default_sysnr(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--sysnr')

        args = entry.parse_command_line(test_params)

        self.assertEqual(args.sysnr, '00')

    def test_args_no_client(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--client')

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            entry.parse_command_line(test_params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertEqual(fake_output.getvalue().split('\n')[0],
                         'No SAP Client provided: use the option --client or the environment variable SAP_CLIENT')

    def test_args_no_port(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--port')

        args = entry.parse_command_line(test_params)

        self.assertEqual(args.port, 443)

    def test_args_default_no_ssl(self):
        test_params = get_tested_parameters()
        test_params.remove('--no-ssl')

        args = entry.parse_command_line(test_params)

        self.assertTrue(args.ssl)

    def test_args_ask_user(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--user')

        with patch('builtins.input', lambda pfx: 'fantomas'):
            args = entry.parse_command_line(test_params)

        self.assertEqual(args.user, 'fantomas')

    def test_args_ask_password(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--password')

        with patch('getpass.getpass', lambda: 'Down1oad'):
            args = entry.parse_command_line(test_params)

        self.assertEqual(args.password, 'Down1oad')

    def test_args_skip_password_prompt_when_token_cached(self):
        """When OAuth has a usable cached token, getpass must not be called
           even if --password was not supplied."""

        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--password')

        getpass_mock = Mock(return_value='should-not-be-used')

        with patch('sap.http.oauth.password_required', return_value=False) as mock_pwd_req, \
             patch('getpass.getpass', getpass_mock):
            args = entry.parse_command_line(test_params)

        mock_pwd_req.assert_called_once()
        getpass_mock.assert_not_called()
        self.assertIsNone(args.password)

    def test_args_prompt_password_when_token_required(self):
        """password_required returning True must trigger getpass prompt."""

        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--password')

        with patch('sap.http.oauth.password_required', return_value=True), \
             patch('getpass.getpass', lambda: 'prompted-pwd'):
            args = entry.parse_command_line(test_params)

        self.assertEqual(args.password, 'prompted-pwd')

    def test_args_skip_user_and_password_prompt_when_auth_plugin_set(self):
        """When the resolved context configures an auth_plugin, the user
           prompt and the password prompt must both be suppressed - the
           plugin is responsible for credentials.
        """

        config_data = {
            'current-context': 'plugin-ctx',
            'connections': {
                'server': {'ashost': 'h.example.com', 'client': '100'},
            },
            'users': {
                'plug-user': {
                    'auth_plugin': {'command': '/p'},
                },
            },
            'contexts': {
                'plugin-ctx': {'connection': 'server', 'user': 'plug-user'},
            },
        }
        self._config_patcher.stop()
        self._config_patcher = patch(
            'sap.cli._entry.ConfigFile.load',
            return_value=ConfigFile(config_data, TEST_CONFIG_PATH),
        )
        self._config_patcher.start()

        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--password')
        remove_cmd_param_from_list(test_params, '--user')
        remove_cmd_param_from_list(test_params, '--ashost')
        remove_cmd_param_from_list(test_params, '--client')

        getpass_mock = Mock(return_value='should-not-be-used')
        input_mock = Mock(return_value='should-not-be-used')

        with patch('getpass.getpass', getpass_mock), \
             patch('builtins.input', input_mock):
            args = entry.parse_command_line(test_params)

        getpass_mock.assert_not_called()
        input_mock.assert_not_called()
        self.assertIsNone(args.password)
        self.assertEqual(args.auth_plugin, {'command': '/p'})

    def test_args_ask_user_and_password(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--password')
        remove_cmd_param_from_list(test_params, '--user')

        with patch('getpass.getpass', lambda: 'Down1oad'), \
             patch('builtins.input', lambda pfx: 'fantomas'):
            args = entry.parse_command_line(test_params)

        self.assertEqual(args.user, 'fantomas')
        self.assertEqual(args.password, 'Down1oad')

    def test_args_env(self):
        test_params = get_tested_parameters()
        remove_cmd_param_from_list(test_params, '--ashost')
        remove_cmd_param_from_list(test_params, '--sysnr')
        remove_cmd_param_from_list(test_params, '--password')
        remove_cmd_param_from_list(test_params, '--user')
        remove_cmd_param_from_list(test_params, '--client')
        remove_cmd_param_from_list(test_params, '--port')
        test_params.remove('--no-ssl')
        test_params.remove('--skip-ssl-validation')

        os.environ['SAP_USER'] = 'fantomas'
        os.environ['SAP_PASSWORD'] = 'Down1oad'
        os.environ['SAP_ASHOST'] = 'vhcalnplci.env.variable'
        os.environ['SAP_SYSNR'] = '33'
        os.environ['SAP_CLIENT'] = '137'
        os.environ['SAP_PORT'] = '13579'
        os.environ['SAP_SSL'] = 'false'

        try:
            args = entry.parse_command_line(test_params)
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
        test_params = get_tested_parameters()
        test_params.remove('--no-ssl')

        for variant in ('n', 'N', 'No', 'no', 'NO', 'false', 'FALSE', 'False', 'Off', 'off'):
            os.environ['SAP_SSL'] = variant

            try:
                args = entry.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL']

            self.assertFalse(args.ssl, msg=variant)

        for variant in ('any', 'thing', 'else', 'is', 'true', 'or', 'on', 'or', 'YES'):
            os.environ['SAP_SSL'] = variant

            try:
                args = entry.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL']

            self.assertTrue(args.ssl, msg=variant)

    def test_args_env_skip_ssl_validation_variants(self):
        test_params = get_tested_parameters()
        test_params.remove('--skip-ssl-validation')

        for variant in ('n', 'N', 'No', 'no', 'NO', 'false', 'FALSE', 'False', 'Off', 'off'):
            os.environ['SAP_SSL_VERIFY'] = variant

            try:
                args = entry.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL_VERIFY']

            self.assertFalse(args.verify, msg=variant)

        for variant in ('any', 'thing', 'else', 'is', 'true', 'or', 'on', 'or', 'YES'):
            os.environ['SAP_SSL_VERIFY'] = variant

            try:
                args = entry.parse_command_line(test_params)
            finally:
                del os.environ['SAP_SSL_VERIFY']

            self.assertTrue(args.verify, msg=variant)

    def test_args_ssl_server_cert(self):
        test_params = get_tested_parameters()
        test_params.insert(1, '--ssl-server-cert')
        test_params.insert(2, '/path/to/ca.pem')

        args = entry.parse_command_line(test_params)

        self.assertEqual(args.ssl_server_cert, '/path/to/ca.pem')

    def test_args_ssl_server_cert_default_none(self):
        test_params = get_tested_parameters()

        args = entry.parse_command_line(test_params)

        self.assertIsNone(args.ssl_server_cert)

    def test_args_system_certs_enabled_by_default(self):
        """Without any flag the operating system trust store is used."""
        test_params = get_tls_verifying_parameters()

        with patch('sap.cli._entry.enable_system_cert_store') as fake_enable:
            args = entry.parse_command_line(test_params)

        self.assertTrue(args.ssl_use_system_certs)
        fake_enable.assert_called_once_with()

    def test_args_ssl_no_system_certs_flag(self):
        """--ssl-no-system-certs opts out of the operating system trust store."""
        test_params = get_tls_verifying_parameters()
        test_params.insert(1, '--ssl-no-system-certs')

        with patch('sap.cli._entry.enable_system_cert_store') as fake_enable:
            args = entry.parse_command_line(test_params)

        self.assertFalse(args.ssl_use_system_certs)
        fake_enable.assert_not_called()

    def test_args_system_certs_skipped_when_validation_disabled(self):
        """With --skip-ssl-validation there is nothing to verify against."""
        test_params = get_tls_verifying_parameters()
        test_params.insert(1, '--skip-ssl-validation')

        with patch('sap.cli._entry.enable_system_cert_store') as fake_enable:
            args = entry.parse_command_line(test_params)

        self.assertTrue(args.ssl_use_system_certs)
        fake_enable.assert_not_called()

    def test_args_system_certs_skipped_with_custom_ca(self):
        """An explicit --ssl-server-cert takes precedence over the OS store."""
        test_params = get_tls_verifying_parameters()
        test_params.insert(1, '/path/to/ca.pem')
        test_params.insert(1, '--ssl-server-cert')

        with patch('sap.cli._entry.enable_system_cert_store') as fake_enable:
            args = entry.parse_command_line(test_params)

        self.assertTrue(args.ssl_use_system_certs)
        fake_enable.assert_not_called()

    def test_args_system_certs_missing_truststore_warns_and_continues(self):
        """A broken truststore install must not break every connection."""
        test_params = get_tls_verifying_parameters()

        with patch('sap.cli._entry.enable_system_cert_store',
                   side_effect=TruststoreNotAvailableError()) as fake_enable, \
                patch('sap.cli._entry.log') as fake_log:
            args = entry.parse_command_line(test_params)

        self.assertTrue(args.ssl_use_system_certs)
        fake_enable.assert_called_once_with()
        fake_log.warning.assert_called_once()

    def test_args_auth_plugin_disable_cache_default_false(self):
        """Without the flag and without env, the resolved value is False
           - the cache is on by default (the on-disk store is opt-out)."""

        test_params = get_tested_parameters()

        with patch.dict(os.environ, {}, clear=False) as _env:
            os.environ.pop('SAPCLI_AUTH_PLUGIN_DISABLE_CACHE', None)
            args = entry.parse_command_line(test_params)

        self.assertFalse(args.auth_plugin_disable_cache)

    def test_args_auth_plugin_disable_cache_flag(self):
        """--auth-plugin-disable-cache flips the value to True."""

        test_params = get_tested_parameters()
        test_params.insert(1, '--auth-plugin-disable-cache')

        args = entry.parse_command_line(test_params)

        self.assertTrue(args.auth_plugin_disable_cache)

    def test_args_auth_plugin_disable_cache_env_var_true(self):
        """SAPCLI_AUTH_PLUGIN_DISABLE_CACHE in the env enables it without
           a CLI flag."""

        test_params = get_tested_parameters()

        os.environ['SAPCLI_AUTH_PLUGIN_DISABLE_CACHE'] = 'true'
        try:
            args = entry.parse_command_line(test_params)
        finally:
            del os.environ['SAPCLI_AUTH_PLUGIN_DISABLE_CACHE']

        self.assertTrue(args.auth_plugin_disable_cache)

    def test_args_auth_plugin_disable_cache_env_var_false_tokens(self):
        """False tokens (no/off/false/n) keep the cache enabled. Same
           normalization rules as SAP_SSL / SAP_SSL_VERIFY."""

        test_params = get_tested_parameters()

        for variant in ('n', 'no', 'No', 'NO', 'false', 'FALSE', 'off', 'Off'):
            os.environ['SAPCLI_AUTH_PLUGIN_DISABLE_CACHE'] = variant
            try:
                args = entry.parse_command_line(test_params)
            finally:
                del os.environ['SAPCLI_AUTH_PLUGIN_DISABLE_CACHE']

            self.assertFalse(args.auth_plugin_disable_cache, msg=variant)


class TestParseCommandLineAuthCert(unittest.TestCase):

    def setUp(self):
        self._get_commands_patcher = patch('sap.cli.get_commands')
        fake_commands = self._get_commands_patcher.start()
        self._fake_cmd = make_mock_command()
        fake_commands.return_value = [(Mock(), self._fake_cmd)]

        self._config_patcher = patch('sap.cli._entry.ConfigFile.load', return_value=ConfigFile({}, TEST_CONFIG_PATH))
        self._config_patcher.start()

    def tearDown(self):
        self._config_patcher.stop()
        self._get_commands_patcher.stop()

    def _cert_parameters(self, *extra):
        """Tested parameters without user/password/no-ssl, with the given
           extra global options inserted before the command name."""

        params = get_tested_parameters()
        remove_cmd_param_from_list(params, '--user')
        remove_cmd_param_from_list(params, '--password')
        params.remove('--no-ssl')
        params[1:1] = list(extra)
        return params

    def test_args_auth_cert_and_key_skip_prompts(self):
        params = self._cert_parameters(
            '--auth-cert', '/certs/me.crt', '--auth-key', '/certs/me.key')

        getpass_mock = Mock(return_value='should-not-be-used')
        input_mock = Mock(return_value='should-not-be-used')

        with patch('getpass.getpass', getpass_mock), \
             patch('builtins.input', input_mock):
            args = entry.parse_command_line(params)

        getpass_mock.assert_not_called()
        input_mock.assert_not_called()
        self.assertEqual(args.auth_cert, '/certs/me.crt')
        self.assertEqual(args.auth_key, '/certs/me.key')
        self.assertIsNone(args.user)
        self.assertIsNone(args.password)

    def test_args_auth_cert_without_key_is_combined_file(self):
        params = self._cert_parameters('--auth-cert', '/certs/me.pem')

        with patch('builtins.input', Mock(return_value='unused')):
            args = entry.parse_command_line(params)

        self.assertEqual(args.auth_cert, '/certs/me.pem')
        self.assertIsNone(args.auth_key)

    def test_args_auth_cert_with_user_is_allowed(self):
        # Some servers map one certificate to several users via login
        # modules and honor a user hint - the combination is legal.
        params = self._cert_parameters(
            '--auth-cert', '/certs/me.crt', '--user', 'fantomas')

        args = entry.parse_command_line(params)

        self.assertEqual(args.auth_cert, '/certs/me.crt')
        self.assertEqual(args.user, 'fantomas')

    def test_args_auth_key_without_auth_cert_errors(self):
        params = self._cert_parameters('--auth-key', '/certs/me.key')

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            entry.parse_command_line(params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertIn('--auth-cert', fake_output.getvalue())

    def test_args_auth_cert_with_password_errors(self):
        params = self._cert_parameters(
            '--auth-cert', '/certs/me.crt', '--password', 'Down1oad')

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            entry.parse_command_line(params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertIn('mutually exclusive', fake_output.getvalue())

    def test_args_auth_cert_with_no_ssl_errors(self):
        params = self._cert_parameters('--auth-cert', '/certs/me.crt', '--no-ssl')

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            entry.parse_command_line(params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertIn('TLS', fake_output.getvalue())

    def test_args_skip_prompts_when_config_auth_cert(self):
        """When the resolved context configures auth_cert, the user prompt
           and the password prompt must both be suppressed - the server
           derives the user from the certificate.
        """

        config_data = {
            'current-context': 'cert-ctx',
            'connections': {
                'server': {'ashost': 'h.example.com', 'client': '100'},
            },
            'users': {
                'cert-user': {'auth_cert': '/certs/me.crt'},
            },
            'contexts': {
                'cert-ctx': {'connection': 'server', 'user': 'cert-user'},
            },
        }
        self._config_patcher.stop()
        self._config_patcher = patch(
            'sap.cli._entry.ConfigFile.load',
            return_value=ConfigFile(config_data, TEST_CONFIG_PATH),
        )
        self._config_patcher.start()

        params = self._cert_parameters()
        remove_cmd_param_from_list(params, '--ashost')
        remove_cmd_param_from_list(params, '--client')

        getpass_mock = Mock(return_value='should-not-be-used')
        input_mock = Mock(return_value='should-not-be-used')

        with patch('getpass.getpass', getpass_mock), \
             patch('builtins.input', input_mock):
            args = entry.parse_command_line(params)

        getpass_mock.assert_not_called()
        input_mock.assert_not_called()
        self.assertEqual(args.auth_cert, '/certs/me.crt')
        self.assertIsNone(args.password)


class TestParseCommandLineNoCommand(unittest.TestCase):

    @patch('sap.cli._entry.ConfigFile.load', return_value=ConfigFile({}, TEST_CONFIG_PATH))
    @patch('sap.cli.get_commands')
    def test_no_command_specified(self, fake_commands, _fake_config):
        fake_cmd = make_mock_command()
        fake_commands.return_value = [(Mock(), fake_cmd)]

        test_params = ALL_PARAMETERS.copy()

        with patch('sys.stderr', new_callable=StringIO) as fake_output, \
             self.assertRaises(SystemExit) as exit_cm:
            entry.parse_command_line(test_params)

        self.assertEqual(str(exit_cm.exception), '3')
        self.assertTrue(fake_output.getvalue().startswith(
            'No command specified - please consult the help and specify a command to execute'))


class TestParseCommandLineWithCorrnr(unittest.TestCase):

    def configure_mock(self, fake_commands):
        fake_cmd = Mock()
        fake_cmd.name = 'pytest'
        fake_cmd.description = 'Mock pytest command'
        fake_cmd.install_parser = Mock()

        def side_install_parser(subparser):
            command_args = subparser.add_subparsers()

            get_args = command_args.add_parser('command')
            get_args.add_argument('--corrnr')
            get_args.set_defaults(execute=Mock())

        fake_cmd.install_parser.side_effect = side_install_parser

        fake_commands.return_value = [(Mock(), fake_cmd)]

    @patch('sap.cli._entry.ConfigFile.load', return_value=ConfigFile({}, TEST_CONFIG_PATH))
    @patch('sap.cli.get_commands')
    def test_args_env_corrnr(self, fake_commands, _fake_config):
        self.configure_mock(fake_commands)

        test_params = ALL_PARAMETERS.copy()
        test_params.append('pytest')
        test_params.append('command')

        exp_corrnr = 'NPLK000001'
        os.environ['SAP_CORRNR'] = exp_corrnr

        try:
            args = entry.parse_command_line(test_params)
        finally:
            del os.environ['SAP_CORRNR']

        self.assertEqual(args.corrnr, exp_corrnr)

    @patch('sap.cli._entry.ConfigFile.load', return_value=ConfigFile({}, TEST_CONFIG_PATH))
    @patch('sap.cli.get_commands')
    def test_args_env_and_param_corrnr(self, fake_commands, _fake_config):
        self.configure_mock(fake_commands)

        test_params = ALL_PARAMETERS.copy()
        test_params.append('pytest')
        test_params.append('command')
        test_params.append('--corrnr')
        test_params.append('420WEEDTIME')

        exp_corrnr = 'NPLK000001'
        os.environ['SAP_CORRNR'] = exp_corrnr

        try:
            args = entry.parse_command_line(test_params)
        finally:
            del os.environ['SAP_CORRNR']

        self.assertEqual(args.corrnr, '420WEEDTIME')


class TestMainEntry(unittest.TestCase):

    @patch('sap.cli._entry.parse_command_line')
    def test_execution_successful(self, fake_parse_command_line):

        fake_parse_command_line.return_value.execute.return_value = 0

        params = ALL_PARAMETERS.copy()
        retval = entry.main(params)
        self.assertEqual(retval, 0)

    @patch('sap.cli._entry.parse_command_line')
    def test_execution_interrupted(self, fake_parse_command_line):

        fake_parse_command_line.return_value.execute.side_effect = KeyboardInterrupt

        with patch.object(entry.log, 'error') as mock_log_error:
            params = ALL_PARAMETERS.copy()
            retval = entry.main(params)

        self.assertEqual(retval, 1)
        mock_log_error.assert_called_once_with('Program interrupted!')

    @patch('sap.cli._entry.parse_command_line')
    def test_execution_failed(self, fake_parse_command_line):

        fake_parse_command_line.return_value.execute.side_effect = sap.errors.ResourceAlreadyExistsError

        with patch('sys.stderr', new_callable=StringIO) as fake_output:
            with patch('sys.stdout', new_callable=StringIO):
                params = ALL_PARAMETERS.copy()
                retval = entry.main(params)

        self.assertEqual(retval, 1)
        self.assertRegex(fake_output.getvalue(), r'^Exception \(ResourceAlreadyExistsError\):')
        self.assertRegex(fake_output.getvalue(), r'Resource already exists')


    @patch('sap.cli._entry.parse_command_line')
    def test_execution_rest_timeout(self, fake_parse_command_line):
        request = Mock()
        request.method = 'GET'
        request.url = 'http://example.com/sap/bc/cts_abapvcs'

        fake_parse_command_line.return_value.execute.side_effect = RestTimedOutRequestError(request, 900.0)

        with patch('sys.stderr', new_callable=StringIO) as fake_output:
            with patch('sys.stdout', new_callable=StringIO):
                retval = entry.main(ALL_PARAMETERS.copy())

        self.assertEqual(retval, 1)
        self.assertIn('TimedOutRequestError', fake_output.getvalue())
        self.assertIn('SAPCLI_HTTP_TIMEOUT', fake_output.getvalue())

    @patch('sap.cli._entry.parse_command_line')
    def test_execution_odata_timeout(self, fake_parse_command_line):
        request = Mock()
        request.method = 'GET'
        request.url = 'http://example.com/sap/opu/odata/SERVICE'

        fake_parse_command_line.return_value.execute.side_effect = ODataTimedOutRequestError(request, 900.0)

        with patch('sys.stderr', new_callable=StringIO) as fake_output:
            with patch('sys.stdout', new_callable=StringIO):
                retval = entry.main(ALL_PARAMETERS.copy())

        self.assertEqual(retval, 1)
        self.assertIn('TimedOutRequestError', fake_output.getvalue())
        self.assertIn('SAPCLI_HTTP_TIMEOUT', fake_output.getvalue())


class TestParseCommandLineConfigFile(unittest.TestCase):

    def setUp(self):
        self._get_commands_patcher = patch('sap.cli.get_commands')
        fake_commands = self._get_commands_patcher.start()
        self._fake_cmd = make_mock_command()
        fake_commands.return_value = [(Mock(), self._fake_cmd)]

        self._config_patcher = patch('sap.cli._entry.ConfigFile.load', return_value=ConfigFile({}, TEST_CONFIG_PATH))
        self._config_patcher.start()

    def tearDown(self):
        self._config_patcher.stop()
        self._get_commands_patcher.stop()

    def test_config_flag_default_none(self):
        params = get_tested_parameters()
        args = entry.parse_command_line(params)
        self.assertIsNone(args.config)

    def test_context_flag_default_none(self):
        params = get_tested_parameters()
        args = entry.parse_command_line(params)
        self.assertIsNone(args.context)

    def test_config_flag_set(self):
        params = get_tested_parameters()
        params.insert(1, '--config')
        params.insert(2, '/some/path/config.yml')
        args = entry.parse_command_line(params)
        self.assertEqual(args.config, '/some/path/config.yml')

    def test_context_flag_set(self):
        self._config_patcher.stop()
        config_data = {
            'connections': {'srv': {'ashost': 'host', 'client': '100'}},
            'users': {'usr': {'user': 'USER'}},
            'contexts': {'prod': {'connection': 'srv', 'user': 'usr'}},
        }
        with patch('sap.cli._entry.ConfigFile.load', return_value=ConfigFile(config_data, TEST_CONFIG_PATH)):
            params = get_tested_parameters()
            params.insert(1, '--context')
            params.insert(2, 'prod')
            args = entry.parse_command_line(params)
        self._config_patcher.start()
        self.assertEqual(args.context, 'prod')

    def test_config_file_attached_to_args(self):
        params = get_tested_parameters()
        args = entry.parse_command_line(params)
        self.assertTrue(hasattr(args, 'config_file'))

    def test_config_command_skips_connection_validation(self):
        """The config subcommand should not require ashost/client/etc."""
        # Stop the get_commands mock so real commands (including 'config') are registered
        self._get_commands_patcher.stop()
        try:
            params = ['sapcli', 'config', 'get-contexts']
            # This should not exit or error even though no host/client/user is provided
            args = entry.parse_command_line(params)
            self.assertIsNotNone(args)
        finally:
            # Restart the patcher so tearDown can stop it cleanly
            fake_commands = self._get_commands_patcher.start()
            fake_commands.return_value = [(Mock(), make_mock_command())]


if __name__ == '__main__':
    unittest.main()
