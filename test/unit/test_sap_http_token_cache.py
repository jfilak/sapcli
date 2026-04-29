#!/usr/bin/env python3

"""Tests for sap.http.token_cache.

All filesystem and platformdirs interaction is mocked. No real file is opened,
created, chmod'd, or replaced anywhere in this module — patches on
pathlib.Path methods, sap.http.token_cache.os, and PlatformDirs guarantee that.
"""

import json
import stat
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import sap.http.token_cache as token_cache
from sap.http.token_cache import (
    FileTokenStore,
    Token,
    TokenStore,
    _default_cache_dir,
    _harden_dir,
    _harden_file,
    _sanitize,
    get_token_store,
)


# ---------------------------------------------------------------------------
# Disk-write guard
#
# Patches every Path method that could touch the filesystem at module scope, so
# any path that forgets a per-test patch still cannot reach disk. Per-test
# decorators override these guards within their scope and the originals are
# restored automatically on teardown.
# ---------------------------------------------------------------------------

_module_patchers = []


def setUpModule():
    targets = [
        ('pathlib.Path.mkdir', None),
        ('pathlib.Path.chmod', None),
        ('pathlib.Path.exists', False),
        ('pathlib.Path.unlink', None),
        ('pathlib.Path.read_text', ''),
        ('pathlib.Path.write_text', None),
        ('sap.http.token_cache.os.replace', None),
    ]
    for target, return_value in targets:
        patcher = patch(target, return_value=return_value)
        patcher.start()
        _module_patchers.append(patcher)


def tearDownModule():
    while _module_patchers:
        _module_patchers.pop().stop()


# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------

class TestTokenDefaults(unittest.TestCase):

    def test_default_token_type_is_bearer(self):
        token = Token(access_token='abc')
        self.assertEqual(token.token_type, 'Bearer')

    def test_default_optional_fields_are_none(self):
        token = Token(access_token='abc')
        self.assertIsNone(token.expires_at)
        self.assertIsNone(token.refresh_token)
        self.assertIsNone(token.scope)

    def test_token_is_frozen(self):
        token = Token(access_token='abc')
        with self.assertRaises(FrozenInstanceError):
            token.access_token = 'xyz'  # type: ignore[misc]


class TestTokenIsExpired(unittest.TestCase):

    def test_returns_false_when_no_expiry(self):
        token = Token(access_token='abc')
        self.assertFalse(token.is_expired())

    def test_returns_false_when_far_in_future(self):
        token = Token(
            access_token='abc',
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        self.assertFalse(token.is_expired())

    def test_returns_true_when_already_past(self):
        token = Token(
            access_token='abc',
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        )
        self.assertTrue(token.is_expired())

    def test_returns_true_when_within_default_leeway(self):
        # Default leeway is 30s; expiry 10s in the future is treated as expired.
        token = Token(
            access_token='abc',
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=10),
        )
        self.assertTrue(token.is_expired())

    def test_respects_custom_leeway(self):
        # 45s in the future, leeway 60 → expired; leeway 10 → not expired.
        token = Token(
            access_token='abc',
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=45),
        )
        self.assertTrue(token.is_expired(leeway_seconds=60))
        self.assertFalse(token.is_expired(leeway_seconds=10))


class TestTokenJsonRoundTrip(unittest.TestCase):

    def test_full_token_round_trips(self):
        original = Token(
            access_token='access-1',
            refresh_token='refresh-1',
            scope='openid email',
            expires_at=datetime(2030, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        )

        recovered = Token.from_json(original.to_json())

        self.assertEqual(recovered, original)

    def test_token_without_expiry_round_trips(self):
        original = Token(access_token='access-1')

        recovered = Token.from_json(original.to_json())

        self.assertEqual(recovered, original)
        self.assertIsNone(recovered.expires_at)

    def test_to_json_emits_iso_expires_at(self):
        token = Token(
            access_token='abc',
            expires_at=datetime(2030, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        )

        payload = json.loads(token.to_json())

        self.assertEqual(payload['expires_at'], '2030-01-02T03:04:05+00:00')

    def test_to_json_normalises_naive_or_aware_to_utc(self):
        # A non-UTC tzinfo should be converted to UTC on serialization.
        non_utc = timezone(timedelta(hours=2))
        token = Token(
            access_token='abc',
            expires_at=datetime(2030, 1, 2, 5, 0, 0, tzinfo=non_utc),
        )

        payload = json.loads(token.to_json())

        # 05:00+02:00 == 03:00+00:00
        self.assertEqual(payload['expires_at'], '2030-01-02T03:00:00+00:00')

    def test_from_json_handles_null_expires_at(self):
        raw = json.dumps({
            'access_token': 'abc',
            'token_type': 'Bearer',
            'expires_at': None,
            'refresh_token': None,
            'scope': None,
        })

        token = Token.from_json(raw)

        self.assertIsNone(token.expires_at)


# ---------------------------------------------------------------------------
# TokenStore (abstract base)
# ---------------------------------------------------------------------------

class TestTokenStoreAbstract(unittest.TestCase):

    def test_cannot_be_instantiated_directly(self):
        with self.assertRaises(TypeError):
            TokenStore()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# FileTokenStore.__init__
# ---------------------------------------------------------------------------

class TestFileTokenStoreInit(unittest.TestCase):

    @patch.object(Path, 'mkdir')
    def test_creates_tokens_directory_under_explicit_base(self, mock_mkdir):
        FileTokenStore(base_dir=Path('/fake/base'))

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('sap.http.token_cache._default_cache_dir', return_value=Path('/fake/default'))
    @patch.object(Path, 'mkdir')
    def test_uses_default_cache_dir_when_base_dir_is_none(self, _mock_mkdir, mock_default):
        FileTokenStore()

        mock_default.assert_called_once()

    @patch.object(Path, 'chmod')
    @patch.object(Path, 'mkdir')
    def test_hardens_tokens_directory_on_posix(self, _mock_mkdir, mock_chmod):
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'posix'
            FileTokenStore(base_dir=Path('/fake/base'))

        mock_chmod.assert_called_once_with(stat.S_IRWXU)

    @patch.object(Path, 'chmod')
    @patch.object(Path, 'mkdir')
    def test_does_not_chmod_on_non_posix(self, _mock_mkdir, mock_chmod):
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'nt'
            FileTokenStore(base_dir=Path('/fake/base'))

        mock_chmod.assert_not_called()


# ---------------------------------------------------------------------------
# FileTokenStore.get
# ---------------------------------------------------------------------------

class TestFileTokenStoreGet(unittest.TestCase):

    def setUp(self):
        # __init__ runs through the module-level Path.mkdir/chmod guards.
        self.store = FileTokenStore(base_dir=Path('/fake/base'))

    @patch.object(Path, 'read_text')
    @patch.object(Path, 'exists', return_value=True)
    def test_returns_token_when_file_exists(self, _mock_exists, mock_read):
        original = Token(access_token='access-1', refresh_token='refresh-1')
        mock_read.return_value = original.to_json()

        result = self.store.get('mykey')

        self.assertEqual(result, original)

    @patch.object(Path, 'exists', return_value=False)
    def test_returns_none_when_file_missing(self, _mock_exists):
        result = self.store.get('mykey')

        self.assertIsNone(result)

    @patch.object(Path, 'read_text', side_effect=OSError('disk error'))
    @patch.object(Path, 'exists', return_value=True)
    def test_returns_none_on_os_error(self, _mock_exists, _mock_read):
        result = self.store.get('mykey')

        self.assertIsNone(result)

    @patch.object(Path, 'read_text', return_value='{ this is not valid JSON')
    @patch.object(Path, 'exists', return_value=True)
    def test_returns_none_on_invalid_json(self, _mock_exists, _mock_read):
        result = self.store.get('mykey')

        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# FileTokenStore.set
# ---------------------------------------------------------------------------

class TestFileTokenStoreSet(unittest.TestCase):

    def setUp(self):
        self.store = FileTokenStore(base_dir=Path('/fake/base'))

    @patch('sap.http.token_cache.os.replace')
    @patch.object(Path, 'write_text')
    def test_writes_token_then_renames_atomically(self, mock_write, mock_replace):
        token = Token(access_token='abc')

        self.store.set('mykey', token)

        mock_write.assert_called_once()
        mock_replace.assert_called_once()

        tmp_path, final_path = mock_replace.call_args.args
        self.assertTrue(str(tmp_path).endswith('.tmp'))
        self.assertFalse(str(final_path).endswith('.tmp'))

    @patch('sap.http.token_cache.os.replace')
    @patch.object(Path, 'write_text')
    def test_writes_serialized_json(self, mock_write, _mock_replace):
        token = Token(access_token='hello-world', refresh_token='r-1')

        self.store.set('mykey', token)

        written_payload = mock_write.call_args.args[0]
        self.assertIn('hello-world', written_payload)
        self.assertIn('r-1', written_payload)

    @patch('sap.http.token_cache.os.replace')
    @patch.object(Path, 'write_text')
    def test_uses_utf8_encoding(self, mock_write, _mock_replace):
        token = Token(access_token='abc')

        self.store.set('mykey', token)

        self.assertEqual(mock_write.call_args.kwargs['encoding'], 'utf-8')

    @patch('sap.http.token_cache.os.replace')
    @patch.object(Path, 'chmod')
    @patch.object(Path, 'write_text')
    def test_hardens_tmp_file_on_posix(self, _mock_write, mock_chmod, _mock_replace):
        with patch.object(token_cache, 'os') as mock_os:
            # set() also calls os.replace — keep it as a mock call we don't care about
            mock_os.name = 'posix'
            self.store.set('mykey', Token(access_token='abc'))

        # The write_text path's chmod (file 0600). The dir's chmod happened in
        # __init__ before this test, where it was patched away separately.
        mock_chmod.assert_called_once_with(stat.S_IRUSR | stat.S_IWUSR)


# ---------------------------------------------------------------------------
# FileTokenStore.delete
# ---------------------------------------------------------------------------

class TestFileTokenStoreDelete(unittest.TestCase):

    def setUp(self):
        self.store = FileTokenStore(base_dir=Path('/fake/base'))

    @patch.object(Path, 'unlink')
    def test_unlinks_existing_file(self, mock_unlink):
        self.store.delete('mykey')

        mock_unlink.assert_called_once()

    @patch.object(Path, 'unlink', side_effect=FileNotFoundError())
    def test_silently_ignores_missing_file(self, _mock_unlink):
        # Must not raise.
        self.store.delete('mykey')


# ---------------------------------------------------------------------------
# _path_for / _sanitize
# ---------------------------------------------------------------------------

class TestSanitize(unittest.TestCase):

    def test_alphanumeric_passes_through(self):
        self.assertEqual(_sanitize('abcXYZ123'), 'abcXYZ123')

    def test_dash_dot_underscore_pass_through(self):
        self.assertEqual(_sanitize('a-b.c_d'), 'a-b.c_d')

    def test_special_chars_become_underscore(self):
        self.assertEqual(_sanitize('a/b\\c|d:e'), 'a_b_c_d_e')

    def test_pipe_replaced_with_underscore(self):
        # OAuth helpers key by '<token_url>|<client_id>'.
        self.assertEqual(_sanitize('https://x.example.com|client-1'),
                         'https___x.example.com_client-1')

    def test_empty_input_returns_default(self):
        self.assertEqual(_sanitize(''), 'default')

    def test_only_special_chars_does_not_collapse_to_default(self):
        # The 'default' fallback only fires for empty input.
        self.assertEqual(_sanitize('!!!'), '___')


class TestFileTokenStorePathFor(unittest.TestCase):

    def setUp(self):
        self.store = FileTokenStore(base_dir=Path('/fake/base'))

    def test_path_lives_under_tokens_subdir(self):
        path = self.store._path_for('mykey')
        self.assertEqual(path, Path('/fake/base/tokens/mykey.json'))

    def test_path_sanitizes_special_chars(self):
        path = self.store._path_for('https://x|client-1')
        self.assertEqual(path, Path('/fake/base/tokens/https___x_client-1.json'))


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestGetTokenStore(unittest.TestCase):

    def setUp(self):
        # Reset the module-level singleton so each test starts from a clean state.
        token_cache._token_store = None

    def tearDown(self):
        token_cache._token_store = None

    @patch('sap.http.token_cache._default_cache_dir', return_value=Path('/fake/default'))
    def test_returns_file_token_store(self, _mock_default):
        store = get_token_store()

        self.assertIsInstance(store, FileTokenStore)

    @patch('sap.http.token_cache._default_cache_dir', return_value=Path('/fake/default'))
    def test_returns_same_instance_on_repeated_calls(self, _mock_default):
        first = get_token_store()
        second = get_token_store()

        self.assertIs(first, second)

    @patch('sap.http.token_cache.FileTokenStore')
    @patch('sap.http.token_cache._default_cache_dir', return_value=Path('/fake/default'))
    def test_constructs_file_token_store_only_once(self, _mock_default, mock_ctor):
        get_token_store()
        get_token_store()
        get_token_store()

        mock_ctor.assert_called_once()


# ---------------------------------------------------------------------------
# _default_cache_dir
# ---------------------------------------------------------------------------

class TestDefaultCacheDir(unittest.TestCase):

    def _patch_platform(self, platform_name, dirs_attrs):
        """Patch sys.platform and PlatformDirs; return the mock so callers can assert."""

        platform_dirs_mock = Mock(**dirs_attrs)
        return (
            patch.object(token_cache.sys, 'platform', platform_name),
            patch('sap.http.token_cache.PlatformDirs', return_value=platform_dirs_mock),
            platform_dirs_mock,
        )

    def test_uses_user_state_dir_on_linux(self):
        sys_p, pd_p, _pd_mock = self._patch_platform(
            'linux', {'user_state_dir': '/state', 'user_data_dir': '/data'}
        )
        with sys_p, pd_p:
            self.assertEqual(_default_cache_dir(), Path('/state'))

    def test_uses_user_data_dir_on_darwin(self):
        sys_p, pd_p, _pd_mock = self._patch_platform(
            'darwin', {'user_state_dir': '/state', 'user_data_dir': '/data'}
        )
        with sys_p, pd_p:
            self.assertEqual(_default_cache_dir(), Path('/data'))

    def test_uses_user_data_dir_on_win32(self):
        sys_p, pd_p, _pd_mock = self._patch_platform(
            'win32', {'user_state_dir': '/state', 'user_data_dir': '/data'}
        )
        with sys_p, pd_p:
            self.assertEqual(_default_cache_dir(), Path('/data'))

    def test_falls_back_to_user_state_dir_on_unknown_platform(self):
        sys_p, pd_p, _pd_mock = self._patch_platform(
            'something-exotic', {'user_state_dir': '/state', 'user_data_dir': '/data'}
        )
        with sys_p, pd_p:
            self.assertEqual(_default_cache_dir(), Path('/state'))

    @patch.object(Path, 'mkdir')
    def test_creates_directory(self, mock_mkdir):
        sys_p, pd_p, _pd_mock = self._patch_platform(
            'linux', {'user_state_dir': '/state', 'user_data_dir': '/data'}
        )
        with sys_p, pd_p:
            _default_cache_dir()

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# _harden_dir / _harden_file
# ---------------------------------------------------------------------------

class TestHardenHelpers(unittest.TestCase):

    def test_harden_dir_chmods_0700_on_posix(self):
        path = Mock()
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'posix'
            _harden_dir(path)

        path.chmod.assert_called_once_with(stat.S_IRWXU)

    def test_harden_dir_is_noop_on_non_posix(self):
        path = Mock()
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'nt'
            _harden_dir(path)

        path.chmod.assert_not_called()

    def test_harden_dir_swallows_oserror(self):
        path = Mock()
        path.chmod.side_effect = OSError('permission denied')
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'posix'
            # Must not raise.
            _harden_dir(path)

    def test_harden_file_chmods_0600_on_posix(self):
        path = Mock()
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'posix'
            _harden_file(path)

        path.chmod.assert_called_once_with(stat.S_IRUSR | stat.S_IWUSR)

    def test_harden_file_is_noop_on_non_posix(self):
        path = Mock()
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'nt'
            _harden_file(path)

        path.chmod.assert_not_called()

    def test_harden_file_swallows_oserror(self):
        path = Mock()
        path.chmod.side_effect = OSError('readonly')
        with patch.object(token_cache, 'os') as mock_os:
            mock_os.name = 'posix'
            # Must not raise.
            _harden_file(path)


if __name__ == '__main__':
    unittest.main()
