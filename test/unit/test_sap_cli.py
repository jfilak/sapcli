#!/bin/python

import sys

import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import sap.cli
import sap.cli.core
from sap.config import ConfigFile, SAPCliConfigError

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


if __name__ == '__main__':
    unittest.main()
