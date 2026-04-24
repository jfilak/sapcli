#!/usr/bin/env python3

import os
import stat
import tempfile
import unittest
import warnings
from pathlib import Path
from unittest.mock import patch, Mock

import requests
import yaml

import sap.config
from sap.config import (
    ConfigFile,
    SAPCliConfigError,
    _resolve_config_path,
    _check_file_permissions,
    _has_passwords,
    _load_config_file,
    _validate_config_data,
    merge_into,
    fetch_config_source,
    MERGEABLE_SECTIONS,
)


TEST_CONFIG_PATH = Path('/test/config.yml')

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
            'password': 'secret',
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


class TestConfigGet(unittest.TestCase):

    def test_return_default(self):
        default = 'foo'
        actual = sap.config.config_get('bar', default=default)

        self.assertEqual(actual, default)

    def test_return_http_timeout(self):
        timeout = sap.config.config_get('http_timeout')

        self.assertEqual(timeout, 900)

    def test_return_http_timeout_from_env(self):
        with patch('os.environ', {'SAPCLI_HTTP_TIMEOUT': '0.777'}):
            timeout = sap.config.config_get('http_timeout')

        self.assertEqual(timeout, 0.777)

    def test_check_before_save_default(self):
        with patch('os.environ', {}):
            self.assertTrue(sap.config.config_get('check_before_save'))

    def test_check_before_save_truthy_spellings(self):
        for value in ('1', 'true', 'TRUE', 'yes', 'ON', ' true '):
            with patch('os.environ', {'SAPCLI_CHECK_BEFORE_SAVE': value}):
                self.assertTrue(
                    sap.config.config_get('check_before_save'),
                    f'truthy value {value!r} should enable the check',
                )

    def test_check_before_save_falsy_spellings(self):
        for value in ('0', 'false', 'FALSE', 'no', 'OFF', ' false '):
            with patch('os.environ', {'SAPCLI_CHECK_BEFORE_SAVE': value}):
                self.assertFalse(
                    sap.config.config_get('check_before_save'),
                    f'falsy value {value!r} should disable the check',
                )

    def test_check_before_save_unknown_value_falls_back_to_default(self):
        with patch('os.environ', {'SAPCLI_CHECK_BEFORE_SAVE': 'maybe'}):
            self.assertTrue(sap.config.config_get('check_before_save'))


class TestResolveConfigPath(unittest.TestCase):

    def test_cli_path_exists(self):
        with tempfile.NamedTemporaryFile(suffix='.yml') as tmp:
            result = _resolve_config_path(tmp.name)
            self.assertEqual(result, Path(tmp.name))

    def test_cli_path_not_exists(self):
        result = _resolve_config_path('/nonexistent/path/config.yml')
        self.assertEqual(result, Path('/nonexistent/path/config.yml'))

    def test_env_variable_path(self):
        with tempfile.NamedTemporaryFile(suffix='.yml') as tmp:
            with patch.dict(os.environ, {'SAPCLI_CONFIG': tmp.name}):
                result = _resolve_config_path()
                self.assertEqual(result, Path(tmp.name))

    def test_env_variable_path_not_exists(self):
        with patch.dict(os.environ, {'SAPCLI_CONFIG': '/nonexistent/config.yml'}):
            result = _resolve_config_path()
            self.assertEqual(result, Path('/nonexistent/config.yml'))

    def test_default_path_not_exists(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove SAPCLI_CONFIG if present
            env = os.environ.copy()
            env.pop('SAPCLI_CONFIG', None)
            with patch.dict(os.environ, env, clear=True):
                # Default path likely doesn't exist in test environment
                result = _resolve_config_path()
                self.assertIsInstance(result, Path)

    def test_cli_path_takes_precedence_over_env(self):
        with tempfile.NamedTemporaryFile(suffix='.yml') as tmp:
            with patch.dict(os.environ, {'SAPCLI_CONFIG': '/some/other/path.yml'}):
                result = _resolve_config_path(tmp.name)
                self.assertEqual(result, Path(tmp.name))


class TestLoadConfigFile(unittest.TestCase):

    def test_load_valid_yaml(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            yaml.dump(SAMPLE_CONFIG, tmp)
            tmp_path = tmp.name

        try:
            data = _load_config_file(Path(tmp_path))
            self.assertEqual(data['current-context'], 'dev')
            self.assertIn('connections', data)
            self.assertIn('users', data)
            self.assertIn('contexts', data)
        finally:
            os.unlink(tmp_path)

    def test_load_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            tmp.write('')
            tmp_path = tmp.name

        try:
            data = _load_config_file(Path(tmp_path))
            self.assertEqual(data, {})
        finally:
            os.unlink(tmp_path)

    def test_load_invalid_yaml_not_dict(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            tmp.write('- item1\n- item2\n')
            tmp_path = tmp.name

        try:
            with self.assertRaises(SAPCliConfigError):
                _load_config_file(Path(tmp_path))
        finally:
            os.unlink(tmp_path)

    def test_load_malformed_yaml_raises_config_error(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            tmp.write('invalid: yaml: content:\n  - :\n')
            tmp_path = tmp.name

        try:
            with self.assertRaises(SAPCliConfigError) as cm:
                _load_config_file(Path(tmp_path))
            self.assertIn('Failed to parse', str(cm.exception))
        finally:
            os.unlink(tmp_path)

    def test_load_unreadable_file_raises_config_error(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            tmp.write('current-context: dev\n')
            tmp_path = tmp.name

        try:
            os.chmod(tmp_path, 0o000)
            with self.assertRaises(SAPCliConfigError) as cm:
                _load_config_file(Path(tmp_path))
            self.assertIn('Failed to read', str(cm.exception))
        finally:
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)
            os.unlink(tmp_path)


class TestHasPasswords(unittest.TestCase):

    def test_no_users_section(self):
        self.assertFalse(_has_passwords({}))

    def test_users_without_passwords(self):
        data = {'users': {'dev-user': {'user': 'DEV'}}}
        self.assertFalse(_has_passwords(data))

    def test_users_with_passwords(self):
        data = {'users': {'dev-user': {'user': 'DEV', 'password': 'secret'}}}
        self.assertTrue(_has_passwords(data))

    def test_users_with_empty_password(self):
        data = {'users': {'dev-user': {'user': 'DEV', 'password': ''}}}
        self.assertFalse(_has_passwords(data))

    def test_invalid_users_structure(self):
        data = {'users': 'not-a-dict'}
        self.assertFalse(_has_passwords(data))

    def test_context_with_password_override(self):
        data = {'contexts': {'prod': {'connection': 'srv', 'user': 'u', 'password': 'secret'}}}
        self.assertTrue(_has_passwords(data))

    def test_context_without_password(self):
        data = {'contexts': {'dev': {'connection': 'srv', 'user': 'u'}}}
        self.assertFalse(_has_passwords(data))

    def test_context_with_empty_password(self):
        data = {'contexts': {'dev': {'connection': 'srv', 'user': 'u', 'password': ''}}}
        self.assertFalse(_has_passwords(data))

    def test_invalid_contexts_structure(self):
        data = {'contexts': 'not-a-dict'}
        self.assertFalse(_has_passwords(data))

    def test_invalid_context_entry_structure(self):
        data = {'contexts': {'dev': 'not-a-dict'}}
        self.assertFalse(_has_passwords(data))

    def test_password_in_context_but_not_users(self):
        data = {
            'users': {'dev-user': {'user': 'DEV'}},
            'contexts': {'prod': {'connection': 'srv', 'user': 'dev-user', 'password': 'secret'}},
        }
        self.assertTrue(_has_passwords(data))


class TestCheckFilePermissions(unittest.TestCase):

    def test_warns_when_world_readable(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                _check_file_permissions(Path(tmp_path))
                self.assertEqual(len(w), 1)
                self.assertIn('world-readable', str(w[0].message))
        finally:
            os.unlink(tmp_path)

    def test_no_warning_when_restricted(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                _check_file_permissions(Path(tmp_path))
                self.assertEqual(len(w), 0)
        finally:
            os.unlink(tmp_path)


class TestConfigFile(unittest.TestCase):

    def _create_config_file(self, data=None):
        """Create a temporary config file and return the path."""
        if data is None:
            data = SAMPLE_CONFIG
        tmp = tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False)
        yaml.dump(data, tmp)
        tmp.close()
        return tmp.name

    def test_load_from_file(self):
        path = self._create_config_file()
        try:
            config = ConfigFile.load(path)
            self.assertIsNotNone(config.path)
            self.assertEqual(config.current_context, 'dev')
        finally:
            os.unlink(path)

    def test_load_no_file(self):
        config = ConfigFile.load('/nonexistent/config.yml')
        self.assertEqual(config.path, Path('/nonexistent/config.yml'))
        self.assertEqual(config.data, {})

    def test_load_cli_path_is_directory_raises_error(self):
        """--config pointing to a directory must raise, not silently ignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(SAPCliConfigError) as cm:
                ConfigFile.load(tmpdir)
            self.assertIn('not a regular file', str(cm.exception))
            self.assertIn(tmpdir, str(cm.exception))

    def test_load_env_path_is_directory_raises_error(self):
        """SAPCLI_CONFIG pointing to a directory must raise, not silently ignore."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict('os.environ', {'SAPCLI_CONFIG': tmpdir}, clear=False):
                with self.assertRaises(SAPCliConfigError) as cm:
                    ConfigFile.load()
                self.assertIn('not a regular file', str(cm.exception))

    def test_load_default_path_is_directory_returns_empty(self):
        """Default config path being a directory should silently return empty."""
        with tempfile.TemporaryDirectory() as tmpdir:
            default_path = os.path.join(tmpdir, 'config.yml')
            os.mkdir(default_path)
            with patch('sap.config.DEFAULT_CONFIG_PATH', default_path):
                with patch.dict('os.environ', {}, clear=True):
                    config = ConfigFile.load()
            self.assertEqual(config.data, {})

    def test_load_malformed_section_raises_error(self):
        """ConfigFile.load rejects configs where a section is not a mapping."""
        path = self._create_config_file({'connections': ['not', 'a', 'dict']})
        try:
            with self.assertRaises(SAPCliConfigError) as cm:
                ConfigFile.load(path)
            self.assertIn('connections', str(cm.exception))
            self.assertIn('not a valid mapping', str(cm.exception))
        finally:
            os.unlink(path)

    def test_current_context(self):
        config = ConfigFile(SAMPLE_CONFIG.copy(), TEST_CONFIG_PATH)
        self.assertEqual(config.current_context, 'dev')

    def test_set_current_context(self):
        data = SAMPLE_CONFIG.copy()
        config = ConfigFile(data, TEST_CONFIG_PATH)
        config.current_context = 'prod'
        self.assertEqual(config.current_context, 'prod')

    def test_connections(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        self.assertIn('dev-server', config.connections)
        self.assertIn('prod-server', config.connections)

    def test_users(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        self.assertIn('dev-user', config.users)
        self.assertIn('prod-user', config.users)

    def test_contexts(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        self.assertIn('dev', config.contexts)
        self.assertIn('prod', config.contexts)

    def test_get_context_exists(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        ctx = config.get_context('dev')
        self.assertEqual(ctx['connection'], 'dev-server')
        self.assertEqual(ctx['user'], 'dev-user')

    def test_get_context_not_exists(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_context('nonexistent')
        self.assertIn('nonexistent', str(cm.exception))

    def test_get_connection_exists(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        conn = config.get_connection('dev-server')
        self.assertEqual(conn['ashost'], 'dev-system.example.com')

    def test_get_connection_not_exists(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_connection('nonexistent')
        self.assertIn('nonexistent', str(cm.exception))

    def test_get_user_exists(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        user = config.get_user('dev-user')
        self.assertEqual(user['user'], 'DEVELOPER')

    def test_get_user_not_exists(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_user('nonexistent')
        self.assertIn('nonexistent', str(cm.exception))

    def test_empty_config_sections(self):
        config = ConfigFile({}, TEST_CONFIG_PATH)
        self.assertIsNone(config.current_context)
        self.assertEqual(config.connections, {})
        self.assertEqual(config.users, {})
        self.assertEqual(config.contexts, {})

    def test_get_context_section_not_dict(self):
        config = ConfigFile({'contexts': ['dev', 'prod']}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_context('dev')
        self.assertIn('contexts', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_get_context_entry_not_dict(self):
        config = ConfigFile({'contexts': {'dev': 'not-a-mapping'}}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_context('dev')
        self.assertIn('dev', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_get_connection_section_not_dict(self):
        config = ConfigFile({'connections': 'not-a-dict'}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_connection('dev-server')
        self.assertIn('connections', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_get_connection_entry_not_dict(self):
        config = ConfigFile({'connections': {'dev-server': 42}}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_connection('dev-server')
        self.assertIn('dev-server', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_get_user_section_not_dict(self):
        config = ConfigFile({'users': ['dev-user']}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_user('dev-user')
        self.assertIn('users', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_get_user_entry_not_dict(self):
        config = ConfigFile({'users': {'dev-user': 'DEVELOPER'}}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.get_user('dev-user')
        self.assertIn('dev-user', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))


class TestConfigFileResolveContext(unittest.TestCase):

    def test_resolve_dev_context(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        result = config.resolve_context('dev')

        self.assertEqual(result['ashost'], 'dev-system.example.com')
        self.assertEqual(result['client'], '100')
        self.assertEqual(result['port'], 443)
        self.assertTrue(result['ssl'])
        self.assertTrue(result['ssl_verify'])
        self.assertEqual(result['sysnr'], '00')
        self.assertEqual(result['user'], 'DEVELOPER')
        self.assertNotIn('password', result)

    def test_resolve_prod_context(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        result = config.resolve_context('prod')

        self.assertEqual(result['ashost'], 'prod-system.example.com')
        self.assertEqual(result['client'], '200')
        self.assertEqual(result['user'], 'DEPLOYER')
        self.assertEqual(result['password'], 'secret')

    def test_resolve_current_context(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        result = config.resolve_context()

        self.assertEqual(result['ashost'], 'dev-system.example.com')
        self.assertEqual(result['user'], 'DEVELOPER')

    def test_resolve_no_context(self):
        config = ConfigFile({}, TEST_CONFIG_PATH)
        result = config.resolve_context()
        self.assertIsNone(result)

    def test_resolve_nonexistent_context(self):
        config = ConfigFile(SAMPLE_CONFIG, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError):
            config.resolve_context('nonexistent')

    def test_resolve_context_missing_connection(self):
        data = {
            'contexts': {'bad': {'user': 'some-user'}},
            'users': {'some-user': {'user': 'TEST'}},
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.resolve_context('bad')
        self.assertIn('does not specify a connection', str(cm.exception))

    def test_resolve_context_missing_user(self):
        data = {
            'contexts': {'bad': {'connection': 'some-conn'}},
            'connections': {'some-conn': {'ashost': 'host', 'client': '100'}},
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.resolve_context('bad')
        self.assertIn('does not specify a user', str(cm.exception))

    def test_resolve_context_connection_not_found(self):
        data = {
            'contexts': {'bad': {'connection': 'missing-conn', 'user': 'some-user'}},
            'users': {'some-user': {'user': 'TEST'}},
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError):
            config.resolve_context('bad')

    def test_resolve_context_user_not_found(self):
        data = {
            'contexts': {'bad': {'connection': 'some-conn', 'user': 'missing-user'}},
            'connections': {'some-conn': {'ashost': 'host', 'client': '100'}},
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError):
            config.resolve_context('bad')

    def test_resolve_context_malformed_context_entry(self):
        data = {
            'contexts': {'bad': 'not-a-mapping'},
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.resolve_context('bad')
        self.assertIn('bad', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_resolve_context_malformed_connection_entry(self):
        data = {
            'contexts': {'ctx': {'connection': 'broken-conn', 'user': 'some-user'}},
            'connections': {'broken-conn': 'not-a-mapping'},
            'users': {'some-user': {'user': 'TEST'}},
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.resolve_context('ctx')
        self.assertIn('broken-conn', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_resolve_context_malformed_user_entry(self):
        data = {
            'contexts': {'ctx': {'connection': 'some-conn', 'user': 'broken-user'}},
            'connections': {'some-conn': {'ashost': 'host', 'client': '100'}},
            'users': {'broken-user': 'not-a-mapping'},
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.resolve_context('ctx')
        self.assertIn('broken-user', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_resolve_context_overrides_connection_ashost(self):
        data = {
            'current-context': 'dev',
            'connections': {
                'base-server': {
                    'ashost': 'base-host.example.com',
                    'client': '100',
                    'port': 443,
                    'ssl': True,
                },
            },
            'users': {
                'dev-user': {'user': 'DEVELOPER'},
            },
            'contexts': {
                'dev': {
                    'connection': 'base-server',
                    'user': 'dev-user',
                    'ashost': 'override-host.example.com',
                },
            },
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        result = config.resolve_context('dev')

        self.assertEqual(result['ashost'], 'override-host.example.com')
        self.assertEqual(result['client'], '100')
        self.assertEqual(result['port'], 443)
        self.assertTrue(result['ssl'])

    def test_resolve_context_overrides_user_password(self):
        data = {
            'connections': {
                'server': {'ashost': 'host.example.com', 'client': '100'},
            },
            'users': {
                'base-user': {'user': 'BASE_USER', 'password': 'base-pass'},
            },
            'contexts': {
                'ctx': {
                    'connection': 'server',
                    'user': 'base-user',
                    'password': 'override-pass',
                },
            },
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        result = config.resolve_context('ctx')

        self.assertEqual(result['user'], 'BASE_USER')
        self.assertEqual(result['password'], 'override-pass')

    def test_resolve_context_overrides_multiple_fields(self):
        data = {
            'connections': {
                'base-server': {
                    'ashost': 'base-host.example.com',
                    'client': '100',
                    'port': 443,
                    'sysnr': '00',
                },
            },
            'users': {
                'base-user': {'user': 'BASE_USER'},
            },
            'contexts': {
                'ctx': {
                    'connection': 'base-server',
                    'user': 'base-user',
                    'ashost': 'new-host.example.com',
                    'port': 8443,
                    'client': '200',
                },
            },
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        result = config.resolve_context('ctx')

        self.assertEqual(result['ashost'], 'new-host.example.com')
        self.assertEqual(result['port'], 8443)
        self.assertEqual(result['client'], '200')
        self.assertEqual(result['sysnr'], '00')

    def test_resolve_context_does_not_override_user_reference(self):
        """The 'user' key in context is always a reference name, not an override."""
        data = {
            'connections': {
                'server': {'ashost': 'host.example.com', 'client': '100'},
            },
            'users': {
                'base-user': {'user': 'BASE_USER'},
            },
            'contexts': {
                'ctx': {
                    'connection': 'server',
                    'user': 'base-user',
                },
            },
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)
        result = config.resolve_context('ctx')

        # 'user' in result comes from the users definition, not the context reference
        self.assertEqual(result['user'], 'BASE_USER')

    def test_resolve_context_shared_connection_different_hosts(self):
        """Real-world scenario: same connection config, different hosts per context."""
        data = {
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
                'dev': {
                    'connection': 'sap-standard',
                    'user': 'dev-user',
                    'ashost': 'dev.example.com',
                },
                'qa': {
                    'connection': 'sap-standard',
                    'user': 'dev-user',
                    'ashost': 'qa.example.com',
                },
                'prod': {
                    'connection': 'sap-standard',
                    'user': 'dev-user',
                    'ashost': 'prod.example.com',
                },
            },
        }
        config = ConfigFile(data, TEST_CONFIG_PATH)

        dev = config.resolve_context('dev')
        qa = config.resolve_context('qa')
        prod = config.resolve_context('prod')

        self.assertEqual(dev['ashost'], 'dev.example.com')
        self.assertEqual(qa['ashost'], 'qa.example.com')
        self.assertEqual(prod['ashost'], 'prod.example.com')

        # All share the same base connection values
        for result in (dev, qa, prod):
            self.assertEqual(result['client'], '100')
            self.assertEqual(result['port'], 443)
            self.assertTrue(result['ssl'])
            self.assertTrue(result['ssl_verify'])
            self.assertEqual(result['sysnr'], '00')
            self.assertEqual(result['user'], 'DEVELOPER')


class TestConfigFileSave(unittest.TestCase):

    def test_save_to_existing_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'config.yml'
            config = ConfigFile(SAMPLE_CONFIG.copy(), path)
            config.save()

            self.assertTrue(path.exists())

            with open(path, 'r', encoding='utf-8') as f:
                saved_data = yaml.safe_load(f)
            self.assertEqual(saved_data['current-context'], 'dev')

    def test_save_to_new_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'subdir' / 'config.yml'
            config = ConfigFile(SAMPLE_CONFIG.copy(), TEST_CONFIG_PATH)
            config.save(path)

            self.assertTrue(path.exists())
            self.assertEqual(config.path, path)

    def test_save_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'a' / 'b' / 'c' / 'config.yml'
            config = ConfigFile({'current-context': 'test'}, TEST_CONFIG_PATH)
            config.save(path)

            self.assertTrue(path.exists())

    def test_save_updates_current_context(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'config.yml'
            data = SAMPLE_CONFIG.copy()
            config = ConfigFile(data, path)
            config.current_context = 'prod'
            config.save()

            with open(path, 'r', encoding='utf-8') as f:
                saved_data = yaml.safe_load(f)
            self.assertEqual(saved_data['current-context'], 'prod')

    def test_save_creates_file_with_restrictive_permissions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'config.yml'
            config = ConfigFile(SAMPLE_CONFIG.copy(), path)
            config.save()

            file_mode = os.stat(path).st_mode & 0o777
            self.assertEqual(file_mode, 0o600)

    def test_save_mkdir_oserror_raises_config_error(self):
        """OSError from mkdir is wrapped in SAPCliConfigError."""
        original_path = TEST_CONFIG_PATH
        config = ConfigFile({'current-context': 'dev'}, original_path)
        target = Path('/proc/0/impossible/config.yml')

        with self.assertRaises(SAPCliConfigError) as cm:
            config.save(target)
        self.assertIn('Failed to create directory', str(cm.exception))
        # self._path must not be updated on failure
        self.assertEqual(config.path, original_path)

    def test_save_open_oserror_raises_config_error(self):
        """OSError from os.open is wrapped in SAPCliConfigError."""
        original_path = TEST_CONFIG_PATH
        config = ConfigFile({'current-context': 'dev'}, original_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / 'config.yml'
            # Make the directory read-only so os.open fails
            os.chmod(tmpdir, stat.S_IRUSR | stat.S_IXUSR)
            try:
                with self.assertRaises(SAPCliConfigError) as cm:
                    config.save(target)
                self.assertIn('Failed to write', str(cm.exception))
                self.assertEqual(config.path, original_path)
            finally:
                os.chmod(tmpdir, stat.S_IRWXU)

    def test_save_yaml_error_raises_config_error(self):
        """yaml.YAMLError from yaml.dump is wrapped in SAPCliConfigError."""
        original_path = TEST_CONFIG_PATH
        config = ConfigFile({'current-context': 'dev'}, original_path)

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / 'config.yml'
            with patch('yaml.dump', side_effect=yaml.YAMLError('bad data')):
                with self.assertRaises(SAPCliConfigError) as cm:
                    config.save(target)
            self.assertIn('Failed to serialize', str(cm.exception))
            self.assertEqual(config.path, original_path)


class TestConfigFileLoadWithPermissions(unittest.TestCase):

    def test_warns_world_readable_with_passwords(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            yaml.dump(SAMPLE_CONFIG, tmp)
            tmp_path = tmp.name

        try:
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                ConfigFile.load(tmp_path)
                self.assertTrue(any('world-readable' in str(warning.message) for warning in w))
        finally:
            os.unlink(tmp_path)

    def test_no_warning_without_passwords(self):
        data = {
            'current-context': 'dev',
            'connections': {'dev': {'ashost': 'host', 'client': '100'}},
            'users': {'dev-user': {'user': 'DEV'}},
            'contexts': {'dev': {'connection': 'dev', 'user': 'dev-user'}},
        }

        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            yaml.dump(data, tmp)
            tmp_path = tmp.name

        try:
            os.chmod(tmp_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH)
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                ConfigFile.load(tmp_path)
                self.assertFalse(any('world-readable' in str(warning.message) for warning in w))
        finally:
            os.unlink(tmp_path)


class TestValidateConfigData(unittest.TestCase):

    def test_valid_data(self):
        _validate_config_data(SAMPLE_CONFIG, 'test')

    def test_empty_dict(self):
        _validate_config_data({}, 'test')

    def test_not_a_dict(self):
        with self.assertRaises(SAPCliConfigError) as cm:
            _validate_config_data('not-a-dict', 'Source')
        self.assertIn('Source', str(cm.exception))
        self.assertIn('valid YAML mapping', str(cm.exception))

    def test_list_raises(self):
        with self.assertRaises(SAPCliConfigError) as cm:
            _validate_config_data(['a', 'b'], 'Source')
        self.assertIn('valid YAML mapping', str(cm.exception))

    def test_connections_not_dict(self):
        with self.assertRaises(SAPCliConfigError) as cm:
            _validate_config_data({'connections': 'bad'}, 'Source')
        self.assertIn('connections', str(cm.exception))
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_users_not_dict(self):
        with self.assertRaises(SAPCliConfigError) as cm:
            _validate_config_data({'users': ['a']}, 'Source')
        self.assertIn('users', str(cm.exception))

    def test_contexts_not_dict(self):
        with self.assertRaises(SAPCliConfigError) as cm:
            _validate_config_data({'contexts': 42}, 'Source')
        self.assertIn('contexts', str(cm.exception))

    def test_missing_sections_are_ok(self):
        _validate_config_data({'current-context': 'dev'}, 'test')


class TestMergeInto(unittest.TestCase):

    def _make_target(self, data=None):
        if data is None:
            data = {}
        return ConfigFile(data, TEST_CONFIG_PATH)

    def test_merge_into_empty_target(self):
        target = self._make_target()
        source = {
            'connections': {'srv': {'ashost': 'host', 'client': '100'}},
            'users': {'usr': {'user': 'DEV'}},
            'contexts': {'ctx': {'connection': 'srv', 'user': 'usr'}},
        }
        summary = merge_into(target, source)

        self.assertEqual(target.data['connections']['srv']['ashost'], 'host')
        self.assertEqual(target.data['users']['usr']['user'], 'DEV')
        self.assertEqual(target.data['contexts']['ctx']['connection'], 'srv')
        self.assertEqual(summary['added']['connections'], ['srv'])
        self.assertEqual(summary['added']['users'], ['usr'])
        self.assertEqual(summary['added']['contexts'], ['ctx'])
        self.assertEqual(summary['skipped']['connections'], [])
        self.assertEqual(summary['skipped']['users'], [])
        self.assertEqual(summary['skipped']['contexts'], [])

    def test_merge_empty_source(self):
        target = self._make_target({
            'connections': {'srv': {'ashost': 'host'}},
        })
        summary = merge_into(target, {})

        self.assertEqual(target.data['connections']['srv']['ashost'], 'host')
        for section in MERGEABLE_SECTIONS:
            self.assertEqual(summary['added'][section], [])
            self.assertEqual(summary['skipped'][section], [])

    def test_merge_connections_no_overlap(self):
        target = self._make_target({
            'connections': {'srv1': {'ashost': 'host1'}},
        })
        source = {'connections': {'srv2': {'ashost': 'host2'}}}
        summary = merge_into(target, source)

        self.assertIn('srv1', target.data['connections'])
        self.assertIn('srv2', target.data['connections'])
        self.assertEqual(summary['added']['connections'], ['srv2'])
        self.assertEqual(summary['skipped']['connections'], [])

    def test_merge_connections_overlap_no_overwrite(self):
        target = self._make_target({
            'connections': {'srv': {'ashost': 'original'}},
        })
        source = {'connections': {'srv': {'ashost': 'new'}}}
        summary = merge_into(target, source, overwrite=False)

        self.assertEqual(target.data['connections']['srv']['ashost'], 'original')
        self.assertEqual(summary['skipped']['connections'], ['srv'])
        self.assertEqual(summary['added']['connections'], [])

    def test_merge_connections_overlap_overwrite(self):
        target = self._make_target({
            'connections': {'srv': {'ashost': 'original'}},
        })
        source = {'connections': {'srv': {'ashost': 'new'}}}
        summary = merge_into(target, source, overwrite=True)

        self.assertEqual(target.data['connections']['srv']['ashost'], 'new')
        self.assertEqual(summary['added']['connections'], ['srv'])
        self.assertEqual(summary['skipped']['connections'], [])

    def test_merge_users_no_overlap(self):
        target = self._make_target({
            'users': {'usr1': {'user': 'A'}},
        })
        source = {'users': {'usr2': {'user': 'B'}}}
        summary = merge_into(target, source)

        self.assertIn('usr1', target.data['users'])
        self.assertIn('usr2', target.data['users'])
        self.assertEqual(summary['added']['users'], ['usr2'])

    def test_merge_users_overlap_no_overwrite(self):
        target = self._make_target({
            'users': {'usr': {'user': 'ORIGINAL'}},
        })
        source = {'users': {'usr': {'user': 'NEW'}}}
        summary = merge_into(target, source, overwrite=False)

        self.assertEqual(target.data['users']['usr']['user'], 'ORIGINAL')
        self.assertEqual(summary['skipped']['users'], ['usr'])

    def test_merge_users_overlap_overwrite(self):
        target = self._make_target({
            'users': {'usr': {'user': 'ORIGINAL'}},
        })
        source = {'users': {'usr': {'user': 'NEW'}}}
        summary = merge_into(target, source, overwrite=True)

        self.assertEqual(target.data['users']['usr']['user'], 'NEW')
        self.assertEqual(summary['added']['users'], ['usr'])

    def test_merge_contexts_no_overlap(self):
        target = self._make_target({
            'contexts': {'ctx1': {'connection': 'srv1', 'user': 'usr1'}},
        })
        source = {'contexts': {'ctx2': {'connection': 'srv2', 'user': 'usr2'}}}
        summary = merge_into(target, source)

        self.assertIn('ctx1', target.data['contexts'])
        self.assertIn('ctx2', target.data['contexts'])
        self.assertEqual(summary['added']['contexts'], ['ctx2'])

    def test_merge_contexts_overlap_no_overwrite(self):
        target = self._make_target({
            'contexts': {'ctx': {'connection': 'srv1', 'user': 'usr1'}},
        })
        source = {'contexts': {'ctx': {'connection': 'srv2', 'user': 'usr2'}}}
        summary = merge_into(target, source, overwrite=False)

        self.assertEqual(target.data['contexts']['ctx']['connection'], 'srv1')
        self.assertEqual(summary['skipped']['contexts'], ['ctx'])

    def test_merge_contexts_overlap_overwrite(self):
        target = self._make_target({
            'contexts': {'ctx': {'connection': 'srv1', 'user': 'usr1'}},
        })
        source = {'contexts': {'ctx': {'connection': 'srv2', 'user': 'usr2'}}}
        summary = merge_into(target, source, overwrite=True)

        self.assertEqual(target.data['contexts']['ctx']['connection'], 'srv2')
        self.assertEqual(summary['added']['contexts'], ['ctx'])

    def test_merge_all_sections_combined(self):
        target = self._make_target({
            'connections': {'existing-srv': {'ashost': 'old'}},
            'users': {'existing-usr': {'user': 'OLD'}},
            'contexts': {'existing-ctx': {'connection': 'existing-srv', 'user': 'existing-usr'}},
        })
        source = {
            'connections': {
                'existing-srv': {'ashost': 'new'},
                'new-srv': {'ashost': 'new-host'},
            },
            'users': {
                'new-usr': {'user': 'NEW'},
            },
            'contexts': {
                'new-ctx': {'connection': 'new-srv', 'user': 'new-usr'},
            },
        }
        summary = merge_into(target, source)

        self.assertEqual(target.data['connections']['existing-srv']['ashost'], 'old')
        self.assertEqual(target.data['connections']['new-srv']['ashost'], 'new-host')
        self.assertEqual(summary['added']['connections'], ['new-srv'])
        self.assertEqual(summary['skipped']['connections'], ['existing-srv'])
        self.assertEqual(summary['added']['users'], ['new-usr'])
        self.assertEqual(summary['added']['contexts'], ['new-ctx'])

    def test_merge_preserves_current_context(self):
        target = self._make_target({
            'current-context': 'my-ctx',
            'connections': {},
            'users': {},
            'contexts': {},
        })
        source = {
            'current-context': 'other-ctx',
            'connections': {'srv': {'ashost': 'host'}},
        }
        merge_into(target, source)

        self.assertEqual(target.data['current-context'], 'my-ctx')

    def test_merge_creates_missing_sections(self):
        target = self._make_target({'current-context': 'dev'})
        source = {
            'connections': {'srv': {'ashost': 'host'}},
            'users': {'usr': {'user': 'DEV'}},
            'contexts': {'ctx': {'connection': 'srv', 'user': 'usr'}},
        }
        merge_into(target, source)

        self.assertIn('connections', target.data)
        self.assertIn('users', target.data)
        self.assertIn('contexts', target.data)

    def test_merge_invalid_source_not_dict(self):
        target = self._make_target()
        with self.assertRaises(SAPCliConfigError) as cm:
            merge_into(target, 'not-a-dict')
        self.assertIn('valid YAML mapping', str(cm.exception))

    def test_merge_invalid_source_section_not_dict(self):
        target = self._make_target()
        with self.assertRaises(SAPCliConfigError) as cm:
            merge_into(target, {'connections': 'bad'})
        self.assertIn('connections', str(cm.exception))


class TestFetchConfigSource(unittest.TestCase):

    def test_fetch_local_file(self):
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            yaml.dump(SAMPLE_CONFIG, tmp)
            tmp_path = tmp.name

        try:
            data = fetch_config_source(tmp_path)
            self.assertEqual(data['current-context'], 'dev')
            self.assertIn('connections', data)
        finally:
            os.unlink(tmp_path)

    def test_fetch_local_file_not_found(self):
        with self.assertRaises(SAPCliConfigError) as cm:
            fetch_config_source('/nonexistent/file.yml')
        self.assertIn('not found', str(cm.exception))

    def test_fetch_https_url(self):
        yaml_content = yaml.dump(SAMPLE_CONFIG)
        mock_response = Mock()
        mock_response.text = yaml_content
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response) as mock_get:
            data = fetch_config_source('https://config.example.com/config.yml')

        mock_get.assert_called_once_with('https://config.example.com/config.yml', timeout=30, verify=True)
        self.assertEqual(data['current-context'], 'dev')
        self.assertIn('connections', data)

    def test_fetch_https_url_network_error(self):
        with patch('sap.config.requests.get', side_effect=requests.ConnectionError('refused')):
            with self.assertRaises(SAPCliConfigError) as cm:
                fetch_config_source('https://config.example.com/config.yml')
        self.assertIn('Failed to fetch', str(cm.exception))

    def test_fetch_https_url_http_error(self):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError('404 Not Found')

        with patch('sap.config.requests.get', return_value=mock_response):
            with self.assertRaises(SAPCliConfigError) as cm:
                fetch_config_source('https://config.example.com/config.yml')
        self.assertIn('Failed to fetch', str(cm.exception))

    def test_fetch_https_url_invalid_yaml(self):
        mock_response = Mock()
        mock_response.text = 'invalid: yaml: content:\n  - :\n'
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response):
            with self.assertRaises(SAPCliConfigError) as cm:
                fetch_config_source('https://config.example.com/config.yml')
        self.assertIn('Failed to parse', str(cm.exception))

    def test_fetch_https_url_not_dict(self):
        mock_response = Mock()
        mock_response.text = '- item1\n- item2\n'
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response):
            with self.assertRaises(SAPCliConfigError) as cm:
                fetch_config_source('https://config.example.com/config.yml')
        self.assertIn('valid YAML mapping', str(cm.exception))

    def test_fetch_https_url_empty_response(self):
        mock_response = Mock()
        mock_response.text = ''
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response):
            data = fetch_config_source('https://config.example.com/config.yml')
        self.assertEqual(data, {})

    def test_fetch_http_url_rejected(self):
        with self.assertRaises(SAPCliConfigError) as cm:
            fetch_config_source('http://config.example.com/config.yml')
        self.assertIn('Plain HTTP is not allowed', str(cm.exception))
        self.assertIn('HTTPS', str(cm.exception))
        self.assertIn('--insecure', str(cm.exception))

    def test_fetch_http_url_with_insecure(self):
        yaml_content = yaml.dump({'connections': {'srv': {'ashost': 'host'}}})
        mock_response = Mock()
        mock_response.text = yaml_content
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response) as mock_get:
            data = fetch_config_source('http://config.example.com/config.yml', insecure=True)

        # HTTP with insecure=True always passes verify=True (no SSL to verify)
        mock_get.assert_called_once_with('http://config.example.com/config.yml', timeout=30, verify=True)
        self.assertIn('srv', data['connections'])

    def test_fetch_https_url_skip_ssl_verify(self):
        yaml_content = yaml.dump({'connections': {'srv': {'ashost': 'host'}}})
        mock_response = Mock()
        mock_response.text = yaml_content
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response) as mock_get:
            data = fetch_config_source('https://config.example.com/config.yml', ssl_verify=False)

        mock_get.assert_called_once_with('https://config.example.com/config.yml', timeout=30, verify=False)
        self.assertIn('srv', data['connections'])

    def test_fetch_https_url_ssl_verify_default_true(self):
        yaml_content = yaml.dump({'connections': {'srv': {'ashost': 'host'}}})
        mock_response = Mock()
        mock_response.text = yaml_content
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response) as mock_get:
            data = fetch_config_source('https://config.example.com/config.yml')

        mock_get.assert_called_once_with('https://config.example.com/config.yml', timeout=30, verify=True)
        self.assertIn('srv', data['connections'])

    def test_fetch_http_url_insecure_ignores_ssl_verify(self):
        """When insecure=True and ssl_verify=False, HTTP requests still use verify=True."""
        yaml_content = yaml.dump({'connections': {'srv': {'ashost': 'host'}}})
        mock_response = Mock()
        mock_response.text = yaml_content
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response) as mock_get:
            data = fetch_config_source('http://config.example.com/config.yml',
                                       insecure=True, ssl_verify=False)

        # ssl_verify is irrelevant for HTTP; always passes verify=True
        mock_get.assert_called_once_with('http://config.example.com/config.yml', timeout=30, verify=True)
        self.assertIn('srv', data['connections'])

    def test_fetch_warns_passwords_in_local_source(self):
        data_with_password = {
            'users': {'usr': {'user': 'DEV', 'password': 'secret'}},
        }
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            yaml.dump(data_with_password, tmp)
            tmp_path = tmp.name

        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                fetch_config_source(tmp_path)
                self.assertTrue(any('passwords' in str(warning.message).lower() for warning in w))
        finally:
            os.unlink(tmp_path)

    def test_fetch_warns_passwords_in_remote_source(self):
        data_with_password = {
            'users': {'usr': {'user': 'DEV', 'password': 'secret'}},
        }
        mock_response = Mock()
        mock_response.text = yaml.dump(data_with_password)
        mock_response.raise_for_status = Mock()

        with patch('sap.config.requests.get', return_value=mock_response):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                fetch_config_source('https://config.example.com/config.yml')
                self.assertTrue(any('passwords' in str(warning.message).lower() for warning in w))

    def test_fetch_no_warning_without_passwords(self):
        data_no_password = {
            'connections': {'srv': {'ashost': 'host'}},
            'users': {'usr': {'user': 'DEV'}},
        }
        with tempfile.NamedTemporaryFile(suffix='.yml', mode='w', delete=False) as tmp:
            yaml.dump(data_no_password, tmp)
            tmp_path = tmp.name

        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                fetch_config_source(tmp_path)
                self.assertFalse(any('passwords' in str(warning.message).lower() for warning in w))
        finally:
            os.unlink(tmp_path)


class TestConfigFileSetConnection(unittest.TestCase):

    def _make_config(self, data=None):
        import copy
        return ConfigFile(copy.deepcopy(data or SAMPLE_CONFIG), TEST_CONFIG_PATH)

    def test_create_new_connection(self):
        config = self._make_config()
        config.set_connection('new-server', {'ashost': 'new.example.com', 'client': '300'})
        self.assertIn('new-server', config.connections)
        self.assertEqual(config.connections['new-server']['ashost'], 'new.example.com')
        self.assertEqual(config.connections['new-server']['client'], '300')

    def test_update_existing_connection_merges(self):
        config = self._make_config()
        config.set_connection('dev-server', {'port': 8443})
        # Updated field
        self.assertEqual(config.connections['dev-server']['port'], 8443)
        # Original fields preserved
        self.assertEqual(config.connections['dev-server']['ashost'], 'dev-system.example.com')
        self.assertEqual(config.connections['dev-server']['client'], '100')

    def test_create_connection_in_empty_config(self):
        config = ConfigFile({}, TEST_CONFIG_PATH)
        config.set_connection('srv', {'ashost': 'host.example.com'})
        self.assertIn('srv', config.connections)
        self.assertEqual(config.connections['srv']['ashost'], 'host.example.com')

    def test_create_connection_when_section_missing(self):
        config = ConfigFile({'current-context': 'dev'}, TEST_CONFIG_PATH)
        config.set_connection('srv', {'ashost': 'host.example.com'})
        self.assertIn('srv', config.connections)

    def test_set_connection_malformed_section_raises(self):
        config = ConfigFile({'connections': 'not-a-dict'}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError) as cm:
            config.set_connection('srv', {'ashost': 'host'})
        self.assertIn('not a valid mapping', str(cm.exception))

    def test_update_connection_malformed_entry_replaces(self):
        """If an existing entry is not a dict, it gets replaced."""
        import copy
        data = copy.deepcopy(SAMPLE_CONFIG)
        data['connections']['bad-entry'] = 'not-a-dict'
        config = ConfigFile(data, TEST_CONFIG_PATH)
        config.set_connection('bad-entry', {'ashost': 'host'})
        self.assertEqual(config.connections['bad-entry'], {'ashost': 'host'})


class TestConfigFileSetUser(unittest.TestCase):

    def _make_config(self, data=None):
        import copy
        return ConfigFile(copy.deepcopy(data or SAMPLE_CONFIG), TEST_CONFIG_PATH)

    def test_create_new_user(self):
        config = self._make_config()
        config.set_user('new-user', {'user': 'NEWDEV'})
        self.assertIn('new-user', config.users)
        self.assertEqual(config.users['new-user']['user'], 'NEWDEV')

    def test_update_existing_user_merges(self):
        config = self._make_config()
        config.set_user('dev-user', {'password': 'newpass'})
        self.assertEqual(config.users['dev-user']['password'], 'newpass')
        # Original field preserved
        self.assertEqual(config.users['dev-user']['user'], 'DEVELOPER')

    def test_create_user_in_empty_config(self):
        config = ConfigFile({}, TEST_CONFIG_PATH)
        config.set_user('usr', {'user': 'DEV'})
        self.assertIn('usr', config.users)

    def test_set_user_malformed_section_raises(self):
        config = ConfigFile({'users': 'not-a-dict'}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError):
            config.set_user('usr', {'user': 'DEV'})


class TestConfigFileSetContext(unittest.TestCase):

    def _make_config(self, data=None):
        import copy
        return ConfigFile(copy.deepcopy(data or SAMPLE_CONFIG), TEST_CONFIG_PATH)

    def test_create_new_context(self):
        config = self._make_config()
        config.set_context('qa', {'connection': 'dev-server', 'user': 'dev-user'})
        self.assertIn('qa', config.contexts)
        self.assertEqual(config.contexts['qa']['connection'], 'dev-server')

    def test_update_existing_context_merges(self):
        config = self._make_config()
        config.set_context('dev', {'ashost': 'override.example.com'})
        # New override field added
        self.assertEqual(config.contexts['dev']['ashost'], 'override.example.com')
        # Original fields preserved
        self.assertEqual(config.contexts['dev']['connection'], 'dev-server')
        self.assertEqual(config.contexts['dev']['user'], 'dev-user')

    def test_create_context_in_empty_config(self):
        config = ConfigFile({}, TEST_CONFIG_PATH)
        config.set_context('ctx', {'connection': 'srv', 'user': 'usr'})
        self.assertIn('ctx', config.contexts)

    def test_set_context_malformed_section_raises(self):
        config = ConfigFile({'contexts': 'not-a-dict'}, TEST_CONFIG_PATH)
        with self.assertRaises(SAPCliConfigError):
            config.set_context('ctx', {'connection': 'srv'})


class TestConfigFileFindReferencingContexts(unittest.TestCase):

    def _make_config(self, data=None):
        import copy
        return ConfigFile(copy.deepcopy(data or SAMPLE_CONFIG), TEST_CONFIG_PATH)

    def test_find_connection_references(self):
        config = self._make_config()
        refs = config.find_referencing_contexts('connection', 'dev-server')
        self.assertEqual(refs, ['dev'])

    def test_find_user_references(self):
        config = self._make_config()
        refs = config.find_referencing_contexts('user', 'dev-user')
        self.assertEqual(refs, ['dev'])

    def test_find_no_references(self):
        config = self._make_config()
        refs = config.find_referencing_contexts('connection', 'nonexistent')
        self.assertEqual(refs, [])

    def test_find_multiple_references(self):
        import copy
        data = copy.deepcopy(SAMPLE_CONFIG)
        data['contexts']['qa'] = {'connection': 'dev-server', 'user': 'dev-user'}
        config = ConfigFile(data, TEST_CONFIG_PATH)
        refs = config.find_referencing_contexts('connection', 'dev-server')
        self.assertIn('dev', refs)
        self.assertIn('qa', refs)
        self.assertEqual(len(refs), 2)

    def test_find_refs_empty_contexts(self):
        config = ConfigFile({}, TEST_CONFIG_PATH)
        refs = config.find_referencing_contexts('connection', 'srv')
        self.assertEqual(refs, [])

    def test_find_refs_invalid_section_raises(self):
        config = self._make_config()
        with self.assertRaises(ValueError):
            config.find_referencing_contexts('invalid', 'name')

    def test_find_refs_skips_malformed_context_entries(self):
        import copy
        data = copy.deepcopy(SAMPLE_CONFIG)
        data['contexts']['bad'] = 'not-a-dict'
        config = ConfigFile(data, TEST_CONFIG_PATH)
        refs = config.find_referencing_contexts('connection', 'dev-server')
        self.assertEqual(refs, ['dev'])


class TestConfigFileDeleteConnection(unittest.TestCase):

    def _make_config(self, data=None):
        import copy
        return ConfigFile(copy.deepcopy(data or SAMPLE_CONFIG), TEST_CONFIG_PATH)

    def test_delete_unreferenced_connection(self):
        import copy
        data = copy.deepcopy(SAMPLE_CONFIG)
        data['connections']['standalone'] = {'ashost': 'alone.example.com'}
        config = ConfigFile(data, TEST_CONFIG_PATH)
        config.delete_connection('standalone')
        self.assertNotIn('standalone', config.connections)

    def test_delete_referenced_connection_blocked(self):
        config = self._make_config()
        with self.assertRaises(SAPCliConfigError) as cm:
            config.delete_connection('dev-server')
        self.assertIn('Cannot delete', str(cm.exception))
        self.assertIn('dev-server', str(cm.exception))
        self.assertIn('dev', str(cm.exception))
        # Connection should still exist
        self.assertIn('dev-server', config.connections)

    def test_delete_referenced_connection_force(self):
        config = self._make_config()
        config.delete_connection('dev-server', force=True)
        self.assertNotIn('dev-server', config.connections)

    def test_delete_nonexistent_connection_raises(self):
        config = self._make_config()
        with self.assertRaises(SAPCliConfigError) as cm:
            config.delete_connection('nonexistent')
        self.assertIn('not found', str(cm.exception))


class TestConfigFileDeleteUser(unittest.TestCase):

    def _make_config(self, data=None):
        import copy
        return ConfigFile(copy.deepcopy(data or SAMPLE_CONFIG), TEST_CONFIG_PATH)

    def test_delete_unreferenced_user(self):
        import copy
        data = copy.deepcopy(SAMPLE_CONFIG)
        data['users']['standalone'] = {'user': 'ALONE'}
        config = ConfigFile(data, TEST_CONFIG_PATH)
        config.delete_user('standalone')
        self.assertNotIn('standalone', config.users)

    def test_delete_referenced_user_blocked(self):
        config = self._make_config()
        with self.assertRaises(SAPCliConfigError) as cm:
            config.delete_user('dev-user')
        self.assertIn('Cannot delete', str(cm.exception))
        self.assertIn('dev-user', str(cm.exception))
        self.assertIn('dev', str(cm.exception))
        # User should still exist
        self.assertIn('dev-user', config.users)

    def test_delete_referenced_user_force(self):
        config = self._make_config()
        config.delete_user('dev-user', force=True)
        self.assertNotIn('dev-user', config.users)

    def test_delete_nonexistent_user_raises(self):
        config = self._make_config()
        with self.assertRaises(SAPCliConfigError) as cm:
            config.delete_user('nonexistent')
        self.assertIn('not found', str(cm.exception))


class TestConfigFileDeleteContext(unittest.TestCase):

    def _make_config(self, data=None):
        import copy
        return ConfigFile(copy.deepcopy(data or SAMPLE_CONFIG), TEST_CONFIG_PATH)

    def test_delete_context(self):
        config = self._make_config()
        config.delete_context('prod')
        self.assertNotIn('prod', config.contexts)
        # current-context is 'dev', should be untouched
        self.assertEqual(config.current_context, 'dev')

    def test_delete_current_context_unsets_current(self):
        config = self._make_config()
        config.delete_context('dev')
        self.assertNotIn('dev', config.contexts)
        self.assertIsNone(config.current_context)

    def test_delete_nonexistent_context_raises(self):
        config = self._make_config()
        with self.assertRaises(SAPCliConfigError) as cm:
            config.delete_context('nonexistent')
        self.assertIn('not found', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
