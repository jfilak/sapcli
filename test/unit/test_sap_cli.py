#!/bin/python

import sys

import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import sap.cli
import sap.cli.core
from sap.config import ConfigFile, SAPCliConfigError
from sap.errors import SAPCliError
import sap.http.auth_plugin_cache

from pathlib import Path

TEST_CONFIG_PATH = Path('/test/config.yml')


class TestModule(unittest.TestCase):

    def test_get_commands_blind(self):
        commands = sap.cli.get_commands()
        self.assertTrue(commands, msg='Some commands should be registered')

        for idx, cmd in enumerate(commands):
            self.assertEqual(len(cmd), 2,
                msg='The command should be 2 tuple - Command: ' + str(idx))

            self.assertTrue(callable(cmd[0]),
                msg='The first item should be callable - Command: ' + str(idx))

            self.assertIsInstance(cmd[1], sap.cli.core.CommandGroup,
                msg='The second item should be of a command group - Command: ' + str(idx))


class TestPrinting(unittest.TestCase):

    def test_get_console_returns_global(self):
        self.assertEqual(sap.cli.core.get_console(), sap.cli.core._CONSOLE)
        self.assertIsNotNone(sap.cli.core.get_console())

    def test_printout_sanity(self):
        console = MagicMock()

        with patch('sap.cli.core.get_console') as fake_get_console:
            fake_get_console.return_value = console

            sap.cli.core.printout('a', 'b', sep=':', end='$')
            sap.cli.core.printerr('e', 'r', sep='-', end='!')

        self.assertEqual(2, len(fake_get_console.call_args))
        console.printout.assert_called_once_with('a', 'b', sep=':', end='$')
        console.printerr.assert_called_once_with('e', 'r', sep='-', end='!')

    def test_printconsole_sanity_printout(self):
        console = sap.cli.core.PrintConsole()

        with patch('sap.cli.core.print') as fake_print:
            console.printout('a', 'b', sep=':', end='$')

        fake_print.assert_called_once_with('a', 'b', sep=':', end='$', file=sys.stdout)

    def test_printconsole_sanity_printerr(self):
        console = sap.cli.core.PrintConsole()

        with patch('sap.cli.core.print') as fake_print:
            console.printerr('a', 'b', sep=':', end='$')

        fake_print.assert_called_once_with('a', 'b', sep=':', end='$', file=sys.stderr)


class TestConnection(unittest.TestCase):

    def test_empty_instance(self):
        args = sap.cli.build_empty_connection_values()
        self.assertEqual(args.ashost, None)
        self.assertEqual(args.sysnr, None)
        self.assertEqual(args.client, None)
        self.assertEqual(args.port, None)
        self.assertEqual(args.ssl, None)
        self.assertEqual(args.verify, None)
        self.assertEqual(args.ssl_server_cert, None)
        self.assertEqual(args.user, None)
        self.assertEqual(args.password, None)

    def test_edit_instance(self):
        args = sap.cli.build_empty_connection_values()

        args.ashost = 'args.ashost'
        self.assertEqual(args.ashost, 'args.ashost')

        args.sysnr = 'args.sysnr'
        self.assertEqual(args.sysnr, 'args.sysnr')

        args.client = 'args.client'
        self.assertEqual(args.client, 'args.client')

        args.port = 'args.port'
        self.assertEqual(args.port, 'args.port')

        args.ssl = 'args.ssl'
        self.assertEqual(args.ssl, 'args.ssl')

        args.verify = 'args.verify'
        self.assertEqual(args.verify, 'args.verify')

        args.user = 'args.user'
        self.assertEqual(args.user, 'args.user')

        args.password = 'args.password'
        self.assertEqual(args.password, 'args.password')


class TestResolveDefaultConnectionValuesWithConfigFile(unittest.TestCase):
    """Test that resolve_default_connection_values integrates config file values."""

    def _make_args(self, **kwargs):
        """Create a SimpleNamespace with all connection fields defaulted to None."""
        defaults = dict(
            ashost=None, sysnr=None, client=None, port=None,
            ssl=None, verify=None, ssl_server_cert=None,
            user=None, password=None,
        )
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def testconfig_file_provides_defaults(self):
        """Config file values are used when CLI and env vars are not set."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'config-host.example.com',
                    'client': '100',
                    'port': 8443,
                    'ssl': True,
                    'ssl_verify': False,
                    'sysnr': '42',
                },
            },
            'users': {
                'dev-user': {
                    'user': 'CONFIG_USER',
                    'password': 'CONFIG_PASS',
                },
            },
            'contexts': {
                'dev': {
                    'connection': 'dev-server',
                    'user': 'dev-user',
                },
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'config-host.example.com')
        self.assertEqual(args.client, '100')
        self.assertEqual(args.port, 8443)
        self.assertTrue(args.ssl)
        self.assertFalse(args.verify)
        self.assertEqual(args.sysnr, '42')
        self.assertEqual(args.user, 'CONFIG_USER')
        self.assertEqual(args.password, 'CONFIG_PASS')

    def test_env_vars_overrideconfig_file(self):
        """Environment variables should take precedence over config file."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'config-host.example.com',
                    'client': '100',
                },
            },
            'users': {
                'dev-user': {
                    'user': 'CONFIG_USER',
                },
            },
            'contexts': {
                'dev': {
                    'connection': 'dev-server',
                    'user': 'dev-user',
                },
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        env = {
            'SAP_ASHOST': 'env-host.example.com',
            'SAP_CLIENT': '200',
            'SAP_USER': 'ENV_USER',
        }
        with patch.dict('os.environ', env, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'env-host.example.com')
        self.assertEqual(args.client, '200')
        self.assertEqual(args.user, 'ENV_USER')

    def test_cli_args_overrideconfig_file(self):
        """CLI arguments should take precedence over config file."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'config-host.example.com',
                    'client': '100',
                },
            },
            'users': {
                'dev-user': {
                    'user': 'CONFIG_USER',
                },
            },
            'contexts': {
                'dev': {
                    'connection': 'dev-server',
                    'user': 'dev-user',
                },
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(
            ashost='cli-host.example.com',
            client='300',
            user='CLI_USER',
            config_file=config_file,
        )

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'cli-host.example.com')
        self.assertEqual(args.client, '300')
        self.assertEqual(args.user, 'CLI_USER')

    def test_noconfig_file_uses_defaults(self):
        """Without config file, built-in defaults are used."""
        args = self._make_args()

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertIsNone(args.ashost)
        self.assertEqual(args.sysnr, '00')
        self.assertIsNone(args.client)
        self.assertEqual(args.port, 443)
        self.assertTrue(args.ssl)
        self.assertTrue(args.verify)

    def test_config_ssl_string_false_normalized(self):
        """Quoted YAML strings like 'false' must be treated as False."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'host.example.com',
                    'client': '100',
                    'ssl': 'false',
                    'ssl_verify': 'no',
                },
            },
            'users': {
                'dev-user': {'user': 'DEV'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertFalse(args.ssl)
        self.assertFalse(args.verify)

    def test_config_ssl_string_true_normalized(self):
        """Quoted YAML strings like 'true' must be treated as True."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'host.example.com',
                    'client': '100',
                    'ssl': 'true',
                    'ssl_verify': 'yes',
                },
            },
            'users': {
                'dev-user': {'user': 'DEV'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertTrue(args.ssl)
        self.assertTrue(args.verify)

    def test_context_override(self):
        """Using --context should select a different context from the config."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'dev-host.example.com',
                    'client': '100',
                },
                'prod-server': {
                    'ashost': 'prod-host.example.com',
                    'client': '200',
                },
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
                'prod-user': {'user': 'PROD_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
                'prod': {'connection': 'prod-server', 'user': 'prod-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file, context='prod')

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'prod-host.example.com')
        self.assertEqual(args.client, '200')
        self.assertEqual(args.user, 'PROD_USER')

    def testconfig_file_with_message_server_params(self):
        """Config file can provide message server parameters."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'dev-host.example.com',
                    'client': '100',
                    'mshost': 'msg-server.example.com',
                    'msserv': '3600',
                    'sysid': 'DEV',
                    'group': 'PUBLIC',
                },
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(
            config_file=config_file,
            mshost=None, msserv=None, sysid=None, group=None,
        )

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.mshost, 'msg-server.example.com')
        self.assertEqual(args.msserv, '3600')
        self.assertEqual(args.sysid, 'DEV')
        self.assertEqual(args.group, 'PUBLIC')

    def testconfig_file_with_snc_params(self):
        """Config file can provide SNC parameters."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'dev-host.example.com',
                    'client': '100',
                    'snc_qop': '3',
                    'snc_myname': 'p:client@REALM',
                    'snc_partnername': 'p:server@REALM',
                    'snc_lib': '/path/to/libsapcrypto.so',
                },
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(
            config_file=config_file,
            snc_qop=None, snc_myname=None, snc_partnername=None, snc_lib=None,
        )

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.snc_qop, '3')
        self.assertEqual(args.snc_myname, 'p:client@REALM')
        self.assertEqual(args.snc_partnername, 'p:server@REALM')
        self.assertEqual(args.snc_lib, '/path/to/libsapcrypto.so')

    def test_build_empty_connection_values_gets_extra_params_from_config(self):
        """Extra params (mshost, snc_*) are applied even when args lacks those attributes."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'dev-host.example.com',
                    'client': '100',
                    'mshost': 'msg-server.example.com',
                    'msserv': '3600',
                    'sysid': 'DEV',
                    'group': 'PUBLIC',
                    'snc_qop': '3',
                    'snc_myname': 'p:client@REALM',
                    'snc_partnername': 'p:server@REALM',
                    'snc_lib': '/path/to/libsapcrypto.so',
                },
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        # build_empty_connection_values does NOT include mshost, snc_*, etc.
        args = sap.cli.build_empty_connection_values()
        args.config_file = config_file

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.mshost, 'msg-server.example.com')
        self.assertEqual(args.msserv, '3600')
        self.assertEqual(args.sysid, 'DEV')
        self.assertEqual(args.group, 'PUBLIC')
        self.assertEqual(args.snc_qop, '3')
        self.assertEqual(args.snc_myname, 'p:client@REALM')
        self.assertEqual(args.snc_partnername, 'p:server@REALM')
        self.assertEqual(args.snc_lib, '/path/to/libsapcrypto.so')

    def test_sapcli_context_env_selects_context(self):
        """SAPCLI_CONTEXT env var selects the active context."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {'ashost': 'dev-host.example.com', 'client': '100'},
                'prod-server': {'ashost': 'prod-host.example.com', 'client': '200'},
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
                'prod-user': {'user': 'PROD_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
                'prod': {'connection': 'prod-server', 'user': 'prod-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {'SAPCLI_CONTEXT': 'prod'}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'prod-host.example.com')
        self.assertEqual(args.client, '200')
        self.assertEqual(args.user, 'PROD_USER')

    def test_cli_context_overrides_sapcli_context_env(self):
        """--context CLI flag takes precedence over SAPCLI_CONTEXT env var."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {'ashost': 'dev-host.example.com', 'client': '100'},
                'prod-server': {'ashost': 'prod-host.example.com', 'client': '200'},
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
                'prod-user': {'user': 'PROD_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
                'prod': {'connection': 'prod-server', 'user': 'prod-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file, context='dev')

        with patch.dict('os.environ', {'SAPCLI_CONTEXT': 'prod'}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'dev-host.example.com')
        self.assertEqual(args.client, '100')
        self.assertEqual(args.user, 'DEV_USER')

    def test_sapcli_context_env_overrides_current_context(self):
        """SAPCLI_CONTEXT env var takes precedence over current-context in config file."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {'ashost': 'dev-host.example.com', 'client': '100'},
                'prod-server': {'ashost': 'prod-host.example.com', 'client': '200'},
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
                'prod-user': {'user': 'PROD_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
                'prod': {'connection': 'prod-server', 'user': 'prod-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {'SAPCLI_CONTEXT': 'prod'}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'prod-host.example.com')
        self.assertEqual(args.client, '200')
        self.assertEqual(args.user, 'PROD_USER')

    def test_context_overrides_connection_fields(self):
        """Context-level connection field overrides work through the full resolution chain."""
        config_data = {
            'current-context': 'qa',
            'connections': {
                'sap-standard': {
                    'client': '100',
                    'port': 443,
                    'ssl': True,
                    'ssl_verify': True,
                    'sysnr': '00',
                },
            },
            'users': {
                'dev-user': {'user': 'DEVELOPER'},
            },
            'contexts': {
                'qa': {
                    'connection': 'sap-standard',
                    'user': 'dev-user',
                    'ashost': 'qa.example.com',
                },
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ashost, 'qa.example.com')
        self.assertEqual(args.client, '100')
        self.assertEqual(args.port, 443)
        self.assertTrue(args.ssl)
        self.assertTrue(args.verify)
        self.assertEqual(args.user, 'DEVELOPER')

    def test_nonnumeric_sap_port_env_var_raises_error(self):
        """SAP_PORT env var with a non-numeric value must raise SAPCliConfigError."""
        args = self._make_args()

        with patch.dict('os.environ', {'SAP_PORT': 'abc'}, clear=True):
            with self.assertRaises(SAPCliConfigError) as cm:
                sap.cli.resolve_default_connection_values(args)
        self.assertIn('abc', str(cm.exception))
        self.assertIn('integer', str(cm.exception))

    def test_nonnumeric_config_port_raises_error(self):
        """Config file port with a non-numeric value must raise SAPCliConfigError."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {'ashost': 'host.example.com', 'port': 'not-a-number'},
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(SAPCliConfigError) as cm:
                sap.cli.resolve_default_connection_values(args)
        self.assertIn('not-a-number', str(cm.exception))
        self.assertIn('integer', str(cm.exception))

    def test_nonconvertible_config_port_raises_error(self):
        """Config file port with a non-string/non-numeric value (e.g. None) must raise SAPCliConfigError."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {'ashost': 'host.example.com', 'port': None},
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(SAPCliConfigError) as cm:
                sap.cli.resolve_default_connection_values(args)
        self.assertIn('None', str(cm.exception))
        self.assertIn('integer', str(cm.exception))

    def test_nonexistent_context_raises_error(self):
        """A misspelled or missing context must fail fast, not silently use defaults."""
        config_data = {
            'connections': {
                'dev-server': {'ashost': 'host.example.com', 'client': '100'},
            },
            'users': {
                'dev-user': {'user': 'DEV_USER'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file, context='prodd')

        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(SAPCliConfigError) as cm:
                sap.cli.resolve_default_connection_values(args)
        self.assertIn('prodd', str(cm.exception))

    def test_ssl_server_cert_from_config_file(self):
        """Config file ssl_server_cert is used when CLI and env vars are not set."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'host.example.com',
                    'client': '100',
                    'ssl_server_cert': '/path/to/ca.pem',
                },
            },
            'users': {
                'dev-user': {'user': 'USR', 'password': 'PWD'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ssl_server_cert, '/path/to/ca.pem')

    def test_ssl_server_cert_env_overrides_config(self):
        """SAP_SSL_SERVER_CERT env var takes precedence over config file."""
        config_data = {
            'current-context': 'dev',
            'connections': {
                'dev-server': {
                    'ashost': 'host.example.com',
                    'client': '100',
                    'ssl_server_cert': '/path/from/config.pem',
                },
            },
            'users': {
                'dev-user': {'user': 'USR', 'password': 'PWD'},
            },
            'contexts': {
                'dev': {'connection': 'dev-server', 'user': 'dev-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {'SAP_SSL_SERVER_CERT': '/path/from/env.pem'}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ssl_server_cert, '/path/from/env.pem')

    def test_ssl_server_cert_cli_overrides_env(self):
        """CLI --ssl-server-cert takes precedence over env var."""
        args = self._make_args(ssl_server_cert='/path/from/cli.pem')

        with patch.dict('os.environ', {'SAP_SSL_SERVER_CERT': '/path/from/env.pem'}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.ssl_server_cert, '/path/from/cli.pem')

    def test_ssl_server_cert_none_when_not_set(self):
        """ssl_server_cert stays None when not provided anywhere."""
        args = self._make_args()

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertIsNone(args.ssl_server_cert)


class TestNoConnection(unittest.TestCase):

    def test_no_connection_returns_none(self):
        result = sap.cli.no_connection(None)
        self.assertIsNone(result)


class TestAdtConnectionFromArgs(unittest.TestCase):
    """adt_connection_from_args wires OAuth via session_initializer
       when args.token_url is set, BasicAuth otherwise.
    """

    def _make_args(self, **overrides):
        defaults = dict(
            ashost='h.example.com',
            client='100',
            user='USR',
            password='pwd',
            port=443,
            ssl=True,
            verify=True,
            ssl_server_cert=None,
            token_url=None,
            client_id=None,
            client_secret=None,
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_basic_auth_when_no_token_url(self):
        args = self._make_args()

        with patch('sap.adt.Connection') as mock_connection:
            sap.cli.adt_connection_from_args(args)

        _, kwargs = mock_connection.call_args
        self.assertIsNone(kwargs.get('session_initializer'))

    def test_oauth_initializer_when_token_url_present(self):
        from sap.http.oauth import OAuthHTTPSessionInitializer
        args = self._make_args(
            token_url='https://auth.example.com',
            client_id='cid',
            client_secret='csec',
        )

        with patch('sap.adt.Connection') as mock_connection:
            sap.cli.adt_connection_from_args(args)

        _, kwargs = mock_connection.call_args
        initializer = kwargs.get('session_initializer')
        self.assertIsInstance(initializer, OAuthHTTPSessionInitializer)

    def test_oauth_kwargs_not_passed_to_connection(self):
        """token_url/client_id/client_secret must not appear on Connection ctor."""
        args = self._make_args(
            token_url='https://auth.example.com',
            client_id='cid',
            client_secret='csec',
        )

        with patch('sap.adt.Connection') as mock_connection:
            sap.cli.adt_connection_from_args(args)

        _, kwargs = mock_connection.call_args
        self.assertNotIn('token_url', kwargs)
        self.assertNotIn('client_id', kwargs)
        self.assertNotIn('client_secret', kwargs)

    def test_partial_oauth_config_only_token_url_raises(self):
        args = self._make_args(token_url='https://auth.example.com')

        with self.assertRaises(SAPCliError) as cm:
            sap.cli.adt_connection_from_args(args)

        self.assertIn('token_url', str(cm.exception))
        self.assertIn('client_id', str(cm.exception))
        self.assertIn('client_secret', str(cm.exception))

    def test_partial_oauth_config_only_client_id_raises(self):
        args = self._make_args(client_id='cid')

        with self.assertRaises(SAPCliError):
            sap.cli.adt_connection_from_args(args)

    def test_partial_oauth_config_missing_secret_raises(self):
        args = self._make_args(
            token_url='https://auth.example.com',
            client_id='cid',
        )

        with self.assertRaises(SAPCliError):
            sap.cli.adt_connection_from_args(args)


class TestBuildEmptyConnectionValuesAuthPlugin(unittest.TestCase):

    def test_empty_values_include_auth_plugin(self):
        values = sap.cli.build_empty_connection_values()

        self.assertTrue(hasattr(values, 'auth_plugin'))
        self.assertIsNone(values.auth_plugin)


class TestResolveDefaultConnectionValuesAuthPlugin(unittest.TestCase):
    """auth_plugin is propagated from the resolved config context onto args
       so that the connection factory can construct an
       HTTPExternalSessionInitializer.
    """

    def _make_args(self, **kwargs):
        defaults = dict(
            ashost=None, sysnr=None, client=None, port=None,
            ssl=None, verify=None, ssl_server_cert=None,
            user=None, password=None,
            token_url=None, client_id=None, client_secret=None,
            auth_plugin=None,
        )
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def test_auth_plugin_propagated_from_config(self):
        config_data = {
            'current-context': 'plugin-ctx',
            'connections': {
                'server': {'ashost': 'h.example.com', 'client': '100'},
            },
            'users': {
                'plug-user': {
                    'auth_plugin': {'command': '/p', 'parameters': {'k': 'v'}},
                },
            },
            'contexts': {
                'plugin-ctx': {'connection': 'server', 'user': 'plug-user'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.auth_plugin, {
            'command': '/p', 'parameters': {'k': 'v'},
        })

    def test_auth_plugin_absent_when_not_in_config(self):
        config_data = {
            'current-context': 'basic-ctx',
            'connections': {
                'server': {'ashost': 'h.example.com', 'client': '100'},
            },
            'users': {'u': {'user': 'USR', 'password': 'pwd'}},
            'contexts': {
                'basic-ctx': {'connection': 'server', 'user': 'u'},
            },
        }
        config_file = ConfigFile(config_data, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertIsNone(args.auth_plugin)


class TestAuthPluginSessionInitializer(unittest.TestCase):
    """adt_connection_from_args must construct an
       HTTPExternalSessionInitializer when args.auth_plugin is set.
    """

    def _make_args(self, **overrides):
        defaults = dict(
            ashost='h.example.com',
            client='100',
            user=None,
            password=None,
            port=443,
            ssl=True,
            verify=True,
            ssl_server_cert=None,
            token_url=None,
            client_id=None,
            client_secret=None,
            auth_plugin=None,
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_external_initializer_when_auth_plugin_set(self):
        from sap.http.auth_plugin import ConnectionInfo
        from sap.http.external_session_initializer import (
            HTTPExternalSessionInitializer,
        )

        args = self._make_args(
            auth_plugin={'command': '/path/to/plugin', 'parameters': {'k': 'v'}},
            user='ELBEZI',
        )

        with patch('sap.adt.Connection') as mock_connection:
            sap.cli.adt_connection_from_args(args)

        _, kwargs = mock_connection.call_args
        initializer = kwargs.get('session_initializer')
        self.assertIsInstance(initializer, HTTPExternalSessionInitializer)
        # The initializer must carry the user (for UnauthorizedError messages)
        # and the connection details the plugin needs to build its URL.
        self.assertEqual(initializer._user, 'ELBEZI')
        self.assertEqual(initializer._command, '/path/to/plugin')
        self.assertEqual(initializer._parameters, {'k': 'v'})
        self.assertIsInstance(initializer._connection, ConnectionInfo)
        self.assertEqual(initializer._connection.proto, 'https')
        self.assertEqual(initializer._connection.ashost, 'h.example.com')
        self.assertEqual(initializer._connection.port, '443')
        self.assertEqual(initializer._connection.client, '100')
        self.assertEqual(initializer._connection.type, 'adt')
        # Path points to the ADT login endpoint sapcli's built-in flow uses.
        self.assertIn('discovery', initializer._connection.path)

    def test_auth_plugin_missing_command_raises(self):
        args = self._make_args(auth_plugin={'parameters': {}})

        with self.assertRaises(SAPCliError) as cm:
            sap.cli.adt_connection_from_args(args)

        self.assertIn('command', str(cm.exception).lower())

    def test_auth_plugin_with_args_password_is_fine(self):
        # Mutual exclusivity is enforced at config-resolution time, not on
        # args. SAP_PASSWORD env populates args.password so the plugin's
        # subprocess can inherit it - this is by design and must not
        # trigger an error here.
        args = self._make_args(
            auth_plugin={'command': '/p'},
            user='ELBEZI',
            password='from-env',
        )

        with patch('sap.adt.Connection'):
            sap.cli.adt_connection_from_args(args)


class TestResolveAuthPluginMutualExclusivity(unittest.TestCase):
    """auth_plugin must conflict with password / OAuth fields at the
       config level (when they appear together in a resolved context),
       not at the args level. This lets users set SAP_PASSWORD as an env
       var for the plugin to inherit without tripping the check.
    """

    def _make_args(self, **kwargs):
        defaults = dict(
            ashost=None, sysnr=None, client=None, port=None,
            ssl=None, verify=None, ssl_server_cert=None,
            user=None, password=None,
            token_url=None, client_id=None, client_secret=None,
            auth_plugin=None,
        )
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def _config_with(self, user_def):
        return ConfigFile({
            'current-context': 'ctx',
            'connections': {'srv': {'ashost': 'h', 'client': '100'}},
            'users': {'u': user_def},
            'contexts': {'ctx': {'connection': 'srv', 'user': 'u'}},
        }, TEST_CONFIG_PATH)

    def test_password_with_auth_plugin_in_user_raises(self):
        config_file = self._config_with({
            'password': 'secret',
            'auth_plugin': {'command': '/p'},
        })
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True), \
             self.assertRaises(SAPCliConfigError) as cm:
            sap.cli.resolve_default_connection_values(args)

        self.assertIn('mutually exclusive', str(cm.exception).lower())

    def test_oauth_fields_with_auth_plugin_raises(self):
        config_file = self._config_with({
            'auth_plugin': {'command': '/p'},
        })
        # OAuth fields live on the connection, but they end up in the
        # same flat resolved-context dict as auth_plugin - the conflict
        # is real even if they live in different config sections.
        config_file.connections['srv']['token_url'] = 'https://t'
        config_file.connections['srv']['client_id'] = 'cid'
        config_file.connections['srv']['client_secret'] = 'csec'

        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {}, clear=True), \
             self.assertRaises(SAPCliConfigError) as cm:
            sap.cli.resolve_default_connection_values(args)

        self.assertIn('mutually exclusive', str(cm.exception).lower())

    def test_env_sap_password_does_not_trigger_mutex(self):
        # Setting SAP_PASSWORD in the env (e.g. so the plugin's
        # subprocess inherits it) must not collide with auth_plugin.
        config_file = self._config_with({'auth_plugin': {'command': '/p'}})
        args = self._make_args(config_file=config_file)

        with patch.dict('os.environ', {'SAP_PASSWORD': 'env-pwd'}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertEqual(args.auth_plugin, {'command': '/p'})
        self.assertEqual(args.password, 'env-pwd')


class TestAuthPluginCacheKeyDerivation(unittest.TestCase):
    """The (context, connection, user) triple is the cache-isolation
       contract: changing any of the three must mint a different cache
       key so cookies do not leak across logical sessions.
    """

    def _make_args(self, **kwargs):
        defaults = dict(
            ashost=None, sysnr=None, client=None, port=None,
            ssl=None, verify=None, ssl_server_cert=None,
            user=None, password=None,
            token_url=None, client_id=None, client_secret=None,
            auth_plugin=None,
            context=None,
        )
        defaults.update(kwargs)
        return SimpleNamespace(**defaults)

    def _config(self):
        return ConfigFile({
            'current-context': 'dev',
            'connections': {
                'dev-srv': {'ashost': 'h', 'client': '100'},
                'prod-srv': {'ashost': 'p', 'client': '200'},
            },
            'users': {
                'plug-user': {'auth_plugin': {'command': '/p'}},
                'other-user': {'auth_plugin': {'command': '/p'}},
            },
            'contexts': {
                'dev': {'connection': 'dev-srv', 'user': 'plug-user'},
                'prod': {'connection': 'prod-srv', 'user': 'plug-user'},
                'dev-other': {'connection': 'dev-srv', 'user': 'other-user'},
            },
        }, TEST_CONFIG_PATH)

    def test_cache_key_built_from_context_triple(self):
        args = self._make_args(config_file=self._config())

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        key = sap.http.auth_plugin_cache.cache_key_for('dev', 'dev-srv', 'plug-user')
        self.assertEqual(args.auth_plugin_cache_key, key)

    def test_cache_key_changes_with_connection(self):
        args = self._make_args(config_file=self._config(), context='prod')

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        key = sap.http.auth_plugin_cache.cache_key_for('prod', 'prod-srv', 'plug-user')
        self.assertEqual(args.auth_plugin_cache_key, key)

    def test_cache_key_changes_with_user(self):
        args = self._make_args(config_file=self._config(), context='dev-other')

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        key = sap.http.auth_plugin_cache.cache_key_for('dev-other', 'dev-srv', 'other-user')
        self.assertEqual(args.auth_plugin_cache_key, key)

    def test_cache_key_none_when_no_auth_plugin(self):
        # auth_plugin not configured → cache key is None (caching disabled).
        config = ConfigFile({
            'current-context': 'basic',
            'connections': {'srv': {'ashost': 'h', 'client': '100'}},
            'users': {'u': {'user': 'USR', 'password': 'pwd'}},
            'contexts': {'basic': {'connection': 'srv', 'user': 'u'}},
        }, TEST_CONFIG_PATH)
        args = self._make_args(config_file=config)

        with patch.dict('os.environ', {}, clear=True):
            sap.cli.resolve_default_connection_values(args)

        self.assertIsNone(args.auth_plugin_cache_key)


class TestAuthPluginInitializerCacheKey(unittest.TestCase):
    """adt_connection_from_args must forward the cache key onto the
       constructed HTTPExternalSessionInitializer; --auth-plugin-invalidate-cache
       must drop the existing entry before the initializer runs.
    """

    def _make_args(self, **overrides):
        defaults = dict(
            ashost='h.example.com', client='100',
            user=None, password=None,
            port=443, ssl=True, verify=True, ssl_server_cert=None,
            token_url=None, client_id=None, client_secret=None,
            auth_plugin={'command': '/p'},
            auth_plugin_cache_key='ctx|conn|user',
            auth_plugin_invalidate_cache=False,
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_cache_key_forwarded_to_initializer(self):
        args = self._make_args()

        with patch('sap.adt.Connection') as mock_connection:
            sap.cli.adt_connection_from_args(args)

        initializer = mock_connection.call_args.kwargs['session_initializer']
        self.assertEqual(initializer._cache_key, 'ctx|conn|user')

    def test_invalidate_cache_drops_entry_before_run(self):
        args = self._make_args(auth_plugin_invalidate_cache=True)

        with patch('sap.cli.get_response_store') as mock_store, \
             patch('sap.adt.Connection'):
            sap.cli.adt_connection_from_args(args)

        mock_store.return_value.delete.assert_called_once_with('ctx|conn|user')

    def test_invalidate_cache_without_key_is_noop(self):
        args = self._make_args(
            auth_plugin_cache_key=None,
            auth_plugin_invalidate_cache=True,
        )

        with patch('sap.cli.get_response_store') as mock_store, \
             patch('sap.adt.Connection'):
            sap.cli.adt_connection_from_args(args)

        mock_store.return_value.delete.assert_not_called()

    def test_no_invalidate_does_not_touch_cache(self):
        args = self._make_args(auth_plugin_invalidate_cache=False)

        with patch('sap.cli.get_response_store') as mock_store, \
             patch('sap.adt.Connection'):
            sap.cli.adt_connection_from_args(args)

        mock_store.return_value.delete.assert_not_called()


if __name__ == '__main__':
    unittest.main()
