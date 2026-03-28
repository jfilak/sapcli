#!/usr/bin/env python3

import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import yaml

import sap.cli.config
import sap.config


SAMPLE_CONFIG = {
    'current-context': 'dev',
    'connections': {
        'dev-server': {
            'ashost': 'dev-system.example.com',
            'client': '100',
            'port': 443,
            'ssl': True,
            'ssl_verify': True,
            'sysnr': '00',
        },
        'prod-server': {
            'ashost': 'prod-system.example.com',
            'client': '200',
            'port': 443,
            'ssl': True,
            'ssl_verify': True,
        },
    },
    'users': {
        'dev-user': {
            'user': 'DEVELOPER',
        },
        'prod-user': {
            'user': 'DEPLOYER',
        },
    },
    'contexts': {
        'dev': {
            'connection': 'dev-server',
            'user': 'dev-user',
        },
        'prod': {
            'connection': 'prod-server',
            'user': 'prod-user',
        },
    },
}


def _write_config(path, data):
    """Helper to write config YAML to a file."""
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False)


def _create_config_file(data=None):
    """Create a temp config file and return path."""
    if data is None:
        data = SAMPLE_CONFIG
    tmp = tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False)
    yaml.dump(data, tmp, default_flow_style=False)
    tmp.close()
    return tmp.name


class TestConfigView(unittest.TestCase):

    def test_view_with_config(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.view(None, args)

            self.assertEqual(retval, 0)
            # Should print the config file path and YAML content
            calls = console.printout.call_args_list
            self.assertTrue(any('Configuration file' in str(call) for call in calls))
        finally:
            os.unlink(path)

    def test_view_without_config(self):
        args = SimpleNamespace(config='/nonexistent/config.yml')
        console = MagicMock()
        with patch('sap.cli.core.get_console', return_value=console):
            retval = sap.cli.config.view(None, args)

        self.assertEqual(retval, 0)
        console.printout.assert_called_once_with('No configuration file found.')


class TestConfigCurrentContext(unittest.TestCase):

    def test_current_context_set(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name=None)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.current_context(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with('dev')
        finally:
            os.unlink(path)

    def test_current_context_not_set(self):
        path = _create_config_file({'connections': {}, 'users': {}, 'contexts': {}})
        try:
            args = SimpleNamespace(config=path, name=None)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.current_context(None, args)

            self.assertEqual(retval, 1)
            console.printerr.assert_called_once_with('No current context is set.')
        finally:
            os.unlink(path)

    def test_current_context_with_name_arg(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='prod')
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.current_context(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with('prod')
        finally:
            os.unlink(path)

    def test_current_context_no_config_file(self):
        args = SimpleNamespace(config='/nonexistent/config.yml', name=None)
        console = MagicMock()
        with patch('sap.cli.core.get_console', return_value=console):
            retval = sap.cli.config.current_context(None, args)

        self.assertEqual(retval, 1)
        console.printerr.assert_called_once_with('No configuration file found.')

    def test_current_context_with_nonexistent_name_arg(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='nonexistent')
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.current_context(None, args)

            self.assertEqual(retval, 1)
            console.printerr.assert_called_once_with(
                "Context 'nonexistent' not found in configuration file.")
        finally:
            os.unlink(path)


class TestConfigUseContext(unittest.TestCase):

    def test_use_context_success(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='prod')
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.use_context(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Switched to context 'prod'.")

            # Verify the file was updated
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            self.assertEqual(data['current-context'], 'prod')
        finally:
            os.unlink(path)

    def test_use_context_not_found(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='nonexistent')
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.use_context(None, args)

            self.assertEqual(retval, 1)
            console.printerr.assert_called_once_with("Context 'nonexistent' not found in configuration file.")
        finally:
            os.unlink(path)

    def test_use_context_no_config_file(self):
        args = SimpleNamespace(config='/nonexistent/config.yml', name='dev')
        console = MagicMock()
        with patch('sap.cli.core.get_console', return_value=console):
            retval = sap.cli.config.use_context(None, args)

        self.assertEqual(retval, 1)
        console.printerr.assert_called_once_with('No configuration file found.')


class TestConfigGetContexts(unittest.TestCase):

    def test_get_contexts_with_contexts(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.get_contexts(None, args)

            self.assertEqual(retval, 0)
            calls = console.printout.call_args_list
            # Should have 2 context lines (dev and prod)
            self.assertEqual(len(calls), 2)

            # The dev context should be marked with *
            dev_line = str(calls[0])
            self.assertIn('*', dev_line)
            self.assertIn('dev', dev_line)

            # prod context should not be marked
            prod_line = str(calls[1])
            self.assertNotIn('*', prod_line.split('prod')[0])
        finally:
            os.unlink(path)

    def test_get_contexts_empty(self):
        path = _create_config_file({'connections': {}, 'users': {}, 'contexts': {}})
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.get_contexts(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with('No contexts defined.')
        finally:
            os.unlink(path)

    def test_get_contexts_no_config(self):
        args = SimpleNamespace(config='/nonexistent/config.yml')
        console = MagicMock()
        with patch('sap.cli.core.get_console', return_value=console):
            retval = sap.cli.config.get_contexts(None, args)

        self.assertEqual(retval, 0)
        console.printout.assert_called_once_with('No contexts defined.')


class TestConfigCommandGroup(unittest.TestCase):

    def test_command_group_name(self):
        cmd_group = sap.cli.config.CommandGroup()
        self.assertEqual(cmd_group.name, 'config')

    def test_commands_registered(self):
        commands = sap.cli.config.CommandGroup.get_commands()
        command_names = [cmd.name for cmd in commands.values()]
        self.assertIn('view', command_names)
        self.assertIn('current-context', command_names)
        self.assertIn('use-context', command_names)
        self.assertIn('get-contexts', command_names)
        self.assertIn('merge', command_names)
        self.assertIn('set-connection', command_names)
        self.assertIn('delete-connection', command_names)
        self.assertIn('get-connections', command_names)
        self.assertIn('set-user', command_names)
        self.assertIn('delete-user', command_names)
        self.assertIn('get-users', command_names)
        self.assertIn('set-context', command_names)
        self.assertIn('delete-context', command_names)


SOURCE_CONFIG = {
    'connections': {
        'shared-server': {
            'ashost': 'shared.example.com',
            'client': '300',
            'port': 443,
            'ssl': True,
        },
    },
    'users': {
        'shared-user': {
            'user': 'SHARED',
        },
    },
    'contexts': {
        'shared': {
            'connection': 'shared-server',
            'user': 'shared-user',
        },
    },
}


class TestConfigMerge(unittest.TestCase):

    def test_merge_from_local_file(self):
        target_path = _create_config_file()
        source_path = _create_config_file(SOURCE_CONFIG)
        try:
            args = SimpleNamespace(config=target_path, source=source_path, overwrite=False, insecure=False)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.merge(None, args)

            self.assertEqual(retval, 0)

            with open(target_path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            # Original entries preserved
            self.assertIn('dev-server', saved['connections'])
            self.assertIn('prod-server', saved['connections'])
            # New entries added
            self.assertIn('shared-server', saved['connections'])
            self.assertIn('shared-user', saved['users'])
            self.assertIn('shared', saved['contexts'])
        finally:
            os.unlink(target_path)
            os.unlink(source_path)

    def test_merge_from_local_file_overwrite(self):
        target_data = {
            'current-context': 'dev',
            'connections': {
                'shared-server': {
                    'ashost': 'old.example.com',
                    'client': '100',
                },
            },
            'users': {},
            'contexts': {},
        }
        target_path = _create_config_file(target_data)
        source_path = _create_config_file(SOURCE_CONFIG)
        try:
            args = SimpleNamespace(config=target_path, source=source_path, overwrite=True, insecure=False)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.merge(None, args)

            self.assertEqual(retval, 0)

            with open(target_path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            # Overwritten
            self.assertEqual(saved['connections']['shared-server']['ashost'], 'shared.example.com')
        finally:
            os.unlink(target_path)
            os.unlink(source_path)

    def test_merge_into_empty_config(self):
        """Merge into a non-existent config file creates it."""
        source_path = _create_config_file(SOURCE_CONFIG)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                target_path = os.path.join(tmpdir, 'new_config.yml')
                args = SimpleNamespace(config=target_path, source=source_path, overwrite=False, insecure=False)
                console = MagicMock()
                with patch('sap.cli.core.get_console', return_value=console):
                    retval = sap.cli.config.merge(None, args)

                self.assertEqual(retval, 0)
                self.assertTrue(os.path.exists(target_path))

                with open(target_path, 'r', encoding='utf-8') as f:
                    saved = yaml.safe_load(f)

                self.assertIn('shared-server', saved['connections'])
                self.assertIn('shared-user', saved['users'])
                self.assertIn('shared', saved['contexts'])
        finally:
            os.unlink(source_path)

    def test_merge_prints_summary_added(self):
        source_path = _create_config_file(SOURCE_CONFIG)
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                target_path = os.path.join(tmpdir, 'config.yml')
                args = SimpleNamespace(config=target_path, source=source_path, overwrite=False, insecure=False)
                console = MagicMock()
                with patch('sap.cli.core.get_console', return_value=console):
                    sap.cli.config.merge(None, args)

                calls = [str(c) for c in console.printout.call_args_list]
                self.assertTrue(any('Added connections' in c and 'shared-server' in c for c in calls))
                self.assertTrue(any('Added users' in c and 'shared-user' in c for c in calls))
                self.assertTrue(any('Added contexts' in c and 'shared' in c for c in calls))
        finally:
            os.unlink(source_path)

    def test_merge_prints_summary_skipped(self):
        target_path = _create_config_file()
        # Source has a connection with the same name as target
        source_with_overlap = {
            'connections': {
                'dev-server': {'ashost': 'other.example.com'},
            },
        }
        source_path = _create_config_file(source_with_overlap)
        try:
            args = SimpleNamespace(config=target_path, source=source_path, overwrite=False, insecure=False)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                sap.cli.config.merge(None, args)

            calls = [str(c) for c in console.printout.call_args_list]
            self.assertTrue(any('Skipped' in c and 'dev-server' in c for c in calls))
        finally:
            os.unlink(target_path)
            os.unlink(source_path)

    def test_merge_nothing_to_merge(self):
        target_path = _create_config_file()
        source_path = _create_config_file({})
        try:
            args = SimpleNamespace(config=target_path, source=source_path, overwrite=False, insecure=False)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                sap.cli.config.merge(None, args)

            console.printout.assert_called_once_with('Nothing to merge.')
        finally:
            os.unlink(target_path)
            os.unlink(source_path)

    def test_merge_source_not_found(self):
        target_path = _create_config_file()
        try:
            args = SimpleNamespace(config=target_path, source='/nonexistent/source.yml', overwrite=False, insecure=False)
            with self.assertRaises(sap.config.SAPCliConfigError) as cm:
                sap.cli.config.merge(None, args)
            self.assertIn('not found', str(cm.exception))
        finally:
            os.unlink(target_path)

    def test_merge_preserves_current_context(self):
        target_path = _create_config_file()
        source_with_context = {
            'current-context': 'shared',
            'connections': {'shared-srv': {'ashost': 'shared.example.com'}},
        }
        source_path = _create_config_file(source_with_context)
        try:
            args = SimpleNamespace(config=target_path, source=source_path, overwrite=False, insecure=False)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                sap.cli.config.merge(None, args)

            with open(target_path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['current-context'], 'dev')
        finally:
            os.unlink(target_path)
            os.unlink(source_path)

    def test_merge_with_insecure_flag(self):
        """--insecure is passed through to fetch_config_source."""
        target_path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=target_path, source='http://config.example.com/config.yml',
                overwrite=False, insecure=True, verify=None,
            )
            source_data = {
                'connections': {'new-srv': {'ashost': 'new.example.com'}},
            }
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                with patch('sap.cli.config.fetch_config_source', return_value=source_data) as mock_fetch:
                    sap.cli.config.merge(None, args)

            mock_fetch.assert_called_once_with('http://config.example.com/config.yml',
                                               insecure=True, ssl_verify=True)
        finally:
            os.unlink(target_path)

    def test_merge_with_skip_ssl_validation(self):
        """--skip-ssl-validation (verify=False) is passed as ssl_verify=False."""
        target_path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=target_path, source='https://config.example.com/config.yml',
                overwrite=False, insecure=False, verify=False,
            )
            source_data = {
                'connections': {'new-srv': {'ashost': 'new.example.com'}},
            }
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                with patch('sap.cli.config.fetch_config_source', return_value=source_data) as mock_fetch:
                    sap.cli.config.merge(None, args)

            mock_fetch.assert_called_once_with('https://config.example.com/config.yml',
                                               insecure=False, ssl_verify=False)
        finally:
            os.unlink(target_path)

    def test_merge_verify_defaults_to_true_when_none(self):
        """When verify is None (local commands), ssl_verify defaults to True."""
        target_path = _create_config_file()
        try:
            # No 'verify' attr at all — getattr returns None
            args = SimpleNamespace(
                config=target_path, source='https://config.example.com/config.yml',
                overwrite=False, insecure=False,
            )
            source_data = {
                'connections': {'new-srv': {'ashost': 'new.example.com'}},
            }
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                with patch('sap.cli.config.fetch_config_source', return_value=source_data) as mock_fetch:
                    sap.cli.config.merge(None, args)

            mock_fetch.assert_called_once_with('https://config.example.com/config.yml',
                                               insecure=False, ssl_verify=True)
        finally:
            os.unlink(target_path)


# ---------------------------------------------------------------------------
# set-connection
# ---------------------------------------------------------------------------

class TestConfigSetConnection(unittest.TestCase):

    def test_create_new_connection(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'config.yml')
            args = SimpleNamespace(
                config=path, name='new-srv',
                ashost='new.example.com', client='100', port=443,
                ssl=True, ssl_verify=None, ssl_server_cert=None,
                sysnr=None, mshost=None, msserv=None, sysid=None,
                group=None, snc_qop=None, snc_myname=None,
                snc_partnername=None, snc_lib=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_connection(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Created connection 'new-srv'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['connections']['new-srv']['ashost'], 'new.example.com')
            self.assertEqual(saved['connections']['new-srv']['client'], '100')
            self.assertEqual(saved['connections']['new-srv']['port'], 443)
            self.assertTrue(saved['connections']['new-srv']['ssl'])

    def test_update_existing_connection(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='dev-server',
                ashost=None, client=None, port=8443,
                ssl=None, ssl_verify=None, ssl_server_cert=None,
                sysnr=None, mshost=None, msserv=None, sysid=None,
                group=None, snc_qop=None, snc_myname=None,
                snc_partnername=None, snc_lib=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_connection(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Updated connection 'dev-server'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            # Updated field
            self.assertEqual(saved['connections']['dev-server']['port'], 8443)
            # Preserved original fields
            self.assertEqual(saved['connections']['dev-server']['ashost'], 'dev-system.example.com')
            self.assertEqual(saved['connections']['dev-server']['client'], '100')
        finally:
            os.unlink(path)

    def test_no_fields_specified(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='dev-server',
                ashost=None, client=None, port=None,
                ssl=None, ssl_verify=None, ssl_server_cert=None,
                sysnr=None, mshost=None, msserv=None, sysid=None,
                group=None, snc_qop=None, snc_myname=None,
                snc_partnername=None, snc_lib=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_connection(None, args)

            self.assertEqual(retval, 1)
            console.printerr.assert_called_once_with('No connection fields specified.')
        finally:
            os.unlink(path)

    def test_set_ssl_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'config.yml')
            args = SimpleNamespace(
                config=path, name='no-ssl-srv',
                ashost='host.example.com', client=None, port=None,
                ssl=False, ssl_verify=None, ssl_server_cert=None,
                sysnr=None, mshost=None, msserv=None, sysid=None,
                group=None, snc_qop=None, snc_myname=None,
                snc_partnername=None, snc_lib=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_connection(None, args)

            self.assertEqual(retval, 0)

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertFalse(saved['connections']['no-ssl-srv']['ssl'])


# ---------------------------------------------------------------------------
# delete-connection
# ---------------------------------------------------------------------------

class TestConfigDeleteConnection(unittest.TestCase):

    def test_delete_unreferenced_connection(self):
        data = {
            'connections': {
                'standalone': {'ashost': 'alone.example.com'},
                'dev-server': {'ashost': 'dev.example.com'},
            },
            'users': {},
            'contexts': {},
        }
        path = _create_config_file(data)
        try:
            args = SimpleNamespace(config=path, name='standalone', force=False)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.delete_connection(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Deleted connection 'standalone'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertNotIn('standalone', saved['connections'])
            self.assertIn('dev-server', saved['connections'])
        finally:
            os.unlink(path)

    def test_delete_referenced_connection_blocked(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='dev-server', force=False)
            with self.assertRaises(sap.config.SAPCliConfigError) as cm:
                sap.cli.config.delete_connection(None, args)
            self.assertIn('Cannot delete', str(cm.exception))
            self.assertIn('dev', str(cm.exception))
        finally:
            os.unlink(path)

    def test_delete_referenced_connection_force(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='dev-server', force=True)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.delete_connection(None, args)

            self.assertEqual(retval, 0)

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertNotIn('dev-server', saved['connections'])
        finally:
            os.unlink(path)

    def test_delete_nonexistent_connection(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='nonexistent', force=False)
            with self.assertRaises(sap.config.SAPCliConfigError) as cm:
                sap.cli.config.delete_connection(None, args)
            self.assertIn('not found', str(cm.exception))
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# get-connections
# ---------------------------------------------------------------------------

class TestConfigGetConnections(unittest.TestCase):

    def test_get_connections_with_data(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.get_connections(None, args)

            self.assertEqual(retval, 0)
            calls = console.printout.call_args_list
            self.assertEqual(len(calls), 2)

            all_output = ' '.join(str(c) for c in calls)
            self.assertIn('dev-server', all_output)
            self.assertIn('dev-system.example.com', all_output)
            self.assertIn('prod-server', all_output)
        finally:
            os.unlink(path)

    def test_get_connections_empty(self):
        path = _create_config_file({'connections': {}, 'users': {}, 'contexts': {}})
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.get_connections(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with('No connections defined.')
        finally:
            os.unlink(path)

    def test_get_connections_no_config(self):
        args = SimpleNamespace(config='/nonexistent/config.yml')
        console = MagicMock()
        with patch('sap.cli.core.get_console', return_value=console):
            retval = sap.cli.config.get_connections(None, args)

        self.assertEqual(retval, 0)
        console.printout.assert_called_once_with('No connections defined.')

    def test_get_connections_shows_mshost_when_no_ashost(self):
        data = {
            'connections': {
                'msg-server': {'mshost': 'msg.example.com', 'client': '100'},
            },
            'users': {},
            'contexts': {},
        }
        path = _create_config_file(data)
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.get_connections(None, args)

            self.assertEqual(retval, 0)
            output = str(console.printout.call_args_list[0])
            self.assertIn('msg.example.com', output)
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# set-user
# ---------------------------------------------------------------------------

class TestConfigSetUser(unittest.TestCase):

    def test_create_new_user(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'config.yml')
            args = SimpleNamespace(
                config=path, name='new-user',
                user_value='NEWDEV', password=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_user(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Created user 'new-user'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['users']['new-user']['user'], 'NEWDEV')

    def test_update_existing_user(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='dev-user',
                user_value=None, password='newpass',
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_user(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Updated user 'dev-user'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['users']['dev-user']['password'], 'newpass')
            # Original field preserved
            self.assertEqual(saved['users']['dev-user']['user'], 'DEVELOPER')
        finally:
            os.unlink(path)

    def test_no_fields_specified(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='dev-user',
                user_value=None, password=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_user(None, args)

            self.assertEqual(retval, 1)
            console.printerr.assert_called_once_with('No user fields specified.')
        finally:
            os.unlink(path)

    def test_create_user_with_both_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'config.yml')
            args = SimpleNamespace(
                config=path, name='full-user',
                user_value='ADMIN', password='secret',
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_user(None, args)

            self.assertEqual(retval, 0)

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['users']['full-user']['user'], 'ADMIN')
            self.assertEqual(saved['users']['full-user']['password'], 'secret')


# ---------------------------------------------------------------------------
# delete-user
# ---------------------------------------------------------------------------

class TestConfigDeleteUser(unittest.TestCase):

    def test_delete_unreferenced_user(self):
        data = {
            'connections': {},
            'users': {
                'standalone': {'user': 'ALONE'},
                'dev-user': {'user': 'DEV'},
            },
            'contexts': {},
        }
        path = _create_config_file(data)
        try:
            args = SimpleNamespace(config=path, name='standalone', force=False)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.delete_user(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Deleted user 'standalone'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertNotIn('standalone', saved['users'])
        finally:
            os.unlink(path)

    def test_delete_referenced_user_blocked(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='dev-user', force=False)
            with self.assertRaises(sap.config.SAPCliConfigError) as cm:
                sap.cli.config.delete_user(None, args)
            self.assertIn('Cannot delete', str(cm.exception))
            self.assertIn('dev', str(cm.exception))
        finally:
            os.unlink(path)

    def test_delete_referenced_user_force(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='dev-user', force=True)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.delete_user(None, args)

            self.assertEqual(retval, 0)
        finally:
            os.unlink(path)

    def test_delete_nonexistent_user(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='nonexistent', force=False)
            with self.assertRaises(sap.config.SAPCliConfigError) as cm:
                sap.cli.config.delete_user(None, args)
            self.assertIn('not found', str(cm.exception))
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# get-users
# ---------------------------------------------------------------------------

class TestConfigGetUsers(unittest.TestCase):

    def test_get_users_with_data(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.get_users(None, args)

            self.assertEqual(retval, 0)
            calls = console.printout.call_args_list
            self.assertEqual(len(calls), 2)

            all_output = ' '.join(str(c) for c in calls)
            self.assertIn('dev-user', all_output)
            self.assertIn('DEVELOPER', all_output)
            self.assertIn('prod-user', all_output)
            self.assertIn('DEPLOYER', all_output)
        finally:
            os.unlink(path)

    def test_get_users_empty(self):
        path = _create_config_file({'connections': {}, 'users': {}, 'contexts': {}})
        try:
            args = SimpleNamespace(config=path)
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.get_users(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with('No users defined.')
        finally:
            os.unlink(path)

    def test_get_users_no_config(self):
        args = SimpleNamespace(config='/nonexistent/config.yml')
        console = MagicMock()
        with patch('sap.cli.core.get_console', return_value=console):
            retval = sap.cli.config.get_users(None, args)

        self.assertEqual(retval, 0)
        console.printout.assert_called_once_with('No users defined.')


# ---------------------------------------------------------------------------
# set-context
# ---------------------------------------------------------------------------

class TestConfigSetContext(unittest.TestCase):

    def test_create_new_context(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='qa',
                connection='dev-server', user_ref='dev-user',
                ashost=None, sysnr=None, client=None, port=None,
                ssl=None, ssl_verify=None, ssl_server_cert=None,
                mshost=None, msserv=None, sysid=None, group=None,
                snc_qop=None, snc_myname=None, snc_partnername=None,
                snc_lib=None, ctx_password=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_context(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Created context 'qa'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['contexts']['qa']['connection'], 'dev-server')
            self.assertEqual(saved['contexts']['qa']['user'], 'dev-user')
        finally:
            os.unlink(path)

    def test_update_existing_context(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='dev',
                connection=None, user_ref=None,
                ashost='override.example.com', sysnr=None, client=None,
                port=None, ssl=None, ssl_verify=None, ssl_server_cert=None,
                mshost=None, msserv=None, sysid=None, group=None,
                snc_qop=None, snc_myname=None, snc_partnername=None,
                snc_lib=None, ctx_password=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_context(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Updated context 'dev'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            # Override added
            self.assertEqual(saved['contexts']['dev']['ashost'], 'override.example.com')
            # Original fields preserved
            self.assertEqual(saved['contexts']['dev']['connection'], 'dev-server')
            self.assertEqual(saved['contexts']['dev']['user'], 'dev-user')
        finally:
            os.unlink(path)

    def test_set_context_with_password_override(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='dev',
                connection=None, user_ref=None,
                ashost=None, sysnr=None, client=None, port=None,
                ssl=None, ssl_verify=None, ssl_server_cert=None,
                mshost=None, msserv=None, sysid=None, group=None,
                snc_qop=None, snc_myname=None, snc_partnername=None,
                snc_lib=None, ctx_password='ctx-secret',
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_context(None, args)

            self.assertEqual(retval, 0)

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['contexts']['dev']['password'], 'ctx-secret')
        finally:
            os.unlink(path)

    def test_no_fields_specified(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(
                config=path, name='dev',
                connection=None, user_ref=None,
                ashost=None, sysnr=None, client=None, port=None,
                ssl=None, ssl_verify=None, ssl_server_cert=None,
                mshost=None, msserv=None, sysid=None, group=None,
                snc_qop=None, snc_myname=None, snc_partnername=None,
                snc_lib=None, ctx_password=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_context(None, args)

            self.assertEqual(retval, 1)
            console.printerr.assert_called_once_with('No context fields specified.')
        finally:
            os.unlink(path)

    def test_create_context_into_empty_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'config.yml')
            args = SimpleNamespace(
                config=path, name='new-ctx',
                connection='srv', user_ref='usr',
                ashost=None, sysnr=None, client=None, port=None,
                ssl=None, ssl_verify=None, ssl_server_cert=None,
                mshost=None, msserv=None, sysid=None, group=None,
                snc_qop=None, snc_myname=None, snc_partnername=None,
                snc_lib=None, ctx_password=None,
            )
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.set_context(None, args)

            self.assertEqual(retval, 0)

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertEqual(saved['contexts']['new-ctx']['connection'], 'srv')
            self.assertEqual(saved['contexts']['new-ctx']['user'], 'usr')


# ---------------------------------------------------------------------------
# delete-context
# ---------------------------------------------------------------------------

class TestConfigDeleteContext(unittest.TestCase):

    def test_delete_context(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='prod')
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.delete_context(None, args)

            self.assertEqual(retval, 0)
            console.printout.assert_called_once_with("Deleted context 'prod'.")

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertNotIn('prod', saved['contexts'])
            # current-context unchanged
            self.assertEqual(saved['current-context'], 'dev')
        finally:
            os.unlink(path)

    def test_delete_current_context_unsets_current(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='dev')
            console = MagicMock()
            with patch('sap.cli.core.get_console', return_value=console):
                retval = sap.cli.config.delete_context(None, args)

            self.assertEqual(retval, 0)

            with open(path, 'r', encoding='utf-8') as f:
                saved = yaml.safe_load(f)

            self.assertNotIn('dev', saved['contexts'])
            self.assertNotIn('current-context', saved)
        finally:
            os.unlink(path)

    def test_delete_nonexistent_context(self):
        path = _create_config_file()
        try:
            args = SimpleNamespace(config=path, name='nonexistent')
            with self.assertRaises(sap.config.SAPCliConfigError) as cm:
                sap.cli.config.delete_context(None, args)
            self.assertIn('not found', str(cm.exception))
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
