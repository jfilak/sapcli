#!/usr/bin/env python3

import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import yaml

import sap.cli.config


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
        console.printerr.assert_called_once_with('No current context is set.')


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


if __name__ == '__main__':
    unittest.main()
