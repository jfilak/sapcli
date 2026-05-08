#!/usr/bin/env python3

"""Tests for sap.http.json_store.

All filesystem and platformdirs interaction is mocked. No real file is opened,
created, chmod'd, or replaced anywhere in this module.
"""

import json
import stat
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock, patch

import sap.http.json_store as json_store
from sap.http.json_store import (
    JSONFileStore,
    _default_cache_dir,
    _harden_dir,
    _harden_file,
    _sanitize,
)


# ---------------------------------------------------------------------------
# Disk-write guard (same shape as test_sap_http_token_cache)
# ---------------------------------------------------------------------------

_module_patchers = []


def setUpModule():
    patcher_mkdir = patch('pathlib.Path.mkdir', return_value=None)
    patcher_mkdir.start()
    _module_patchers.append(patcher_mkdir)

    patcher_chmod = patch('pathlib.Path.chmod', return_value=None)
    patcher_chmod.start()
    _module_patchers.append(patcher_chmod)

    patcher_exists = patch('pathlib.Path.exists', return_value=False)
    patcher_exists.start()
    _module_patchers.append(patcher_exists)

    patcher_unlink = patch('pathlib.Path.unlink', return_value=None)
    patcher_unlink.start()
    _module_patchers.append(patcher_unlink)

    patcher_read = patch('pathlib.Path.read_text', return_value='')
    patcher_read.start()
    _module_patchers.append(patcher_read)

    patcher_write = patch('pathlib.Path.write_text', return_value=None)
    patcher_write.start()
    _module_patchers.append(patcher_write)

    patcher_replace = patch('sap.http.json_store.os.replace', return_value=None)
    patcher_replace.start()
    _module_patchers.append(patcher_replace)


def tearDownModule():
    while _module_patchers:
        _module_patchers.pop().stop()


# ---------------------------------------------------------------------------
# A tiny payload type used to exercise JSONFileStore generically
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _Sample:
    name: str
    value: int

    def to_json(self) -> str:
        return json.dumps({'name': self.name, 'value': self.value})

    @classmethod
    def from_json(cls, raw: str) -> '_Sample':
        data = json.loads(raw)
        return cls(name=data['name'], value=data['value'])


class _SampleStore(JSONFileStore[_Sample]):
    """Concrete JSONFileStore[_Sample] used by the tests below."""

    def __init__(self, base_dir: Path, subdir: str = 'samples'):
        super().__init__(base_dir, subdir)

    def _serialize(self, value: _Sample) -> str:
        return value.to_json()

    def _deserialize(self, raw: str) -> _Sample:
        return _Sample.from_json(raw)


# ---------------------------------------------------------------------------
# JSONFileStore default _serialize / _deserialize
# ---------------------------------------------------------------------------

class TestJSONFileStoreUnimplementedHooks(unittest.TestCase):
    """A bare JSONFileStore is not directly usable - subclasses must override."""

    @patch.object(Path, 'mkdir')
    def test_default_serialize_raises_not_implemented(self, _mock_mkdir):
        store = JSONFileStore(Path('/fake/base'), 'subdir')

        with self.assertRaises(NotImplementedError):
            store._serialize(object())

    @patch.object(Path, 'mkdir')
    def test_default_deserialize_raises_not_implemented(self, _mock_mkdir):
        store = JSONFileStore(Path('/fake/base'), 'subdir')

        with self.assertRaises(NotImplementedError):
            store._deserialize('{}')


# ---------------------------------------------------------------------------
# JSONFileStore.__init__
# ---------------------------------------------------------------------------

class TestJSONFileStoreInit(unittest.TestCase):

    @patch.object(Path, 'mkdir')
    def test_creates_subdir_under_base(self, mock_mkdir):
        _SampleStore(Path('/fake/base'))

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch.object(Path, 'chmod')
    @patch.object(Path, 'mkdir')
    def test_hardens_subdir_on_posix(self, _mock_mkdir, mock_chmod):
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'posix'
            _SampleStore(Path('/fake/base'))

        mock_chmod.assert_called_once_with(stat.S_IRWXU)

    @patch.object(Path, 'chmod')
    @patch.object(Path, 'mkdir')
    def test_does_not_chmod_on_non_posix(self, _mock_mkdir, mock_chmod):
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'nt'
            _SampleStore(Path('/fake/base'))

        mock_chmod.assert_not_called()

    @patch.object(Path, 'mkdir')
    def test_subdir_name_is_used(self, _mock_mkdir):
        store = _SampleStore(Path('/fake/base'), subdir='custom-name')

        self.assertEqual(store._dir, Path('/fake/base/custom-name'))


# ---------------------------------------------------------------------------
# JSONFileStore.get
# ---------------------------------------------------------------------------

class TestJSONFileStoreGet(unittest.TestCase):

    def setUp(self):
        self.store = _SampleStore(Path('/fake/base'))

    @patch.object(Path, 'read_text')
    @patch.object(Path, 'exists', return_value=True)
    def test_returns_payload_when_file_exists(self, _mock_exists, mock_read):
        original = _Sample(name='n', value=42)
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

    @patch.object(Path, 'read_text', return_value='{"unexpected": "shape"}')
    @patch.object(Path, 'exists', return_value=True)
    def test_returns_none_when_deserialize_raises_keyerror(self, _mock_exists, _mock_read):
        # _Sample.from_json reads required keys; missing ones raise KeyError
        # which JSONFileStore.get must treat as a corrupt-cache miss.
        result = self.store.get('mykey')

        self.assertIsNone(result)

    @patch.object(Path, 'read_text', return_value='[1, 2, 3]')
    @patch.object(Path, 'exists', return_value=True)
    def test_returns_none_when_deserialize_raises_typeerror(self, _mock_exists, _mock_read):
        # Cached payload deserializes into a list (schema drift). _Sample
        # then indexes it with string keys, which raises TypeError. get()
        # must treat that as a corrupt-cache miss too.
        result = self.store.get('mykey')

        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# JSONFileStore.set
# ---------------------------------------------------------------------------

class TestJSONFileStoreSet(unittest.TestCase):

    def setUp(self):
        self.store = _SampleStore(Path('/fake/base'))

    @patch('sap.http.json_store.os.replace')
    @patch.object(Path, 'write_text')
    def test_writes_payload_then_renames_atomically(self, mock_write, mock_replace):
        sample = _Sample(name='n', value=1)

        self.store.set('mykey', sample)

        mock_write.assert_called_once()
        mock_replace.assert_called_once()

        tmp_path, final_path = mock_replace.call_args.args
        self.assertTrue(str(tmp_path).endswith('.tmp'))
        self.assertFalse(str(final_path).endswith('.tmp'))

    @patch('sap.http.json_store.os.replace')
    @patch.object(Path, 'write_text')
    def test_writes_serialized_json(self, mock_write, _mock_replace):
        sample = _Sample(name='hello', value=99)

        self.store.set('mykey', sample)

        written_payload = mock_write.call_args.args[0]
        self.assertIn('hello', written_payload)
        self.assertIn('99', written_payload)

    @patch('sap.http.json_store.os.replace')
    @patch.object(Path, 'write_text')
    def test_uses_utf8_encoding(self, mock_write, _mock_replace):
        self.store.set('mykey', _Sample(name='n', value=1))

        self.assertEqual(mock_write.call_args.kwargs['encoding'], 'utf-8')

    @patch('sap.http.json_store.os.replace')
    @patch.object(Path, 'chmod')
    @patch.object(Path, 'write_text')
    def test_hardens_tmp_file_on_posix(self, _mock_write, mock_chmod, _mock_replace):
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'posix'
            self.store.set('mykey', _Sample(name='n', value=1))

        mock_chmod.assert_called_once_with(stat.S_IRUSR | stat.S_IWUSR)

    @patch('sap.http.json_store.os.replace')
    @patch.object(Path, 'write_text')
    def test_uses_unique_tmp_filename_per_write(self, _mock_write, mock_replace):
        # Two writes to the same key must use distinct tmp paths so concurrent
        # writers cannot collide on a fixed '<key>.json.tmp' name.
        self.store.set('mykey', _Sample(name='n', value=1))
        self.store.set('mykey', _Sample(name='n', value=2))

        self.assertEqual(mock_replace.call_count, 2)
        first_tmp = mock_replace.call_args_list[0].args[0]
        second_tmp = mock_replace.call_args_list[1].args[0]
        self.assertNotEqual(first_tmp, second_tmp)

        # Both still target the same final path.
        first_final = mock_replace.call_args_list[0].args[1]
        second_final = mock_replace.call_args_list[1].args[1]
        self.assertEqual(first_final, second_final)

    @patch('sap.http.json_store.os.replace')
    @patch.object(Path, 'unlink')
    @patch.object(Path, 'write_text', side_effect=OSError('disk full'))
    def test_cleans_up_tmp_on_write_failure(self, _mock_write, mock_unlink, mock_replace):
        with self.assertRaises(OSError):
            self.store.set('mykey', _Sample(name='n', value=1))

        # The unique tmp must be removed so it does not pile up as garbage.
        mock_unlink.assert_called_once()
        # And the failed write must NOT be promoted to the final path.
        mock_replace.assert_not_called()


# ---------------------------------------------------------------------------
# JSONFileStore.delete
# ---------------------------------------------------------------------------

class TestJSONFileStoreDelete(unittest.TestCase):

    def setUp(self):
        self.store = _SampleStore(Path('/fake/base'))

    @patch.object(Path, 'unlink')
    def test_unlinks_existing_file(self, mock_unlink):
        self.store.delete('mykey')

        mock_unlink.assert_called_once()

    @patch.object(Path, 'unlink', side_effect=FileNotFoundError())
    def test_silently_ignores_missing_file(self, _mock_unlink):
        # Must not raise.
        self.store.delete('mykey')


# ---------------------------------------------------------------------------
# JSONFileStore._path_for
# ---------------------------------------------------------------------------

class TestJSONFileStorePathFor(unittest.TestCase):

    def setUp(self):
        self.store = _SampleStore(Path('/fake/base'))

    def test_path_lives_under_subdir(self):
        path = self.store._path_for('mykey')

        self.assertEqual(path, Path('/fake/base/samples/mykey.json'))

    def test_path_sanitizes_special_chars(self):
        path = self.store._path_for('https://x|client-1')

        self.assertEqual(path, Path('/fake/base/samples/https___x_client-1.json'))


# ---------------------------------------------------------------------------
# _sanitize
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


# ---------------------------------------------------------------------------
# _default_cache_dir
# ---------------------------------------------------------------------------

class TestDefaultCacheDir(unittest.TestCase):

    def _patch_platform(self, platform_name, dirs_attrs):
        platform_dirs_mock = Mock(**dirs_attrs)
        return (
            patch.object(json_store.sys, 'platform', platform_name),
            patch('sap.http.json_store.PlatformDirs', return_value=platform_dirs_mock),
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
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'posix'
            _harden_dir(path)

        path.chmod.assert_called_once_with(stat.S_IRWXU)

    def test_harden_dir_is_noop_on_non_posix(self):
        path = Mock()
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'nt'
            _harden_dir(path)

        path.chmod.assert_not_called()

    def test_harden_dir_swallows_oserror(self):
        path = Mock()
        path.chmod.side_effect = OSError('permission denied')
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'posix'
            # Must not raise.
            _harden_dir(path)

    def test_harden_file_chmods_0600_on_posix(self):
        path = Mock()
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'posix'
            _harden_file(path)

        path.chmod.assert_called_once_with(stat.S_IRUSR | stat.S_IWUSR)

    def test_harden_file_is_noop_on_non_posix(self):
        path = Mock()
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'nt'
            _harden_file(path)

        path.chmod.assert_not_called()

    def test_harden_file_swallows_oserror(self):
        path = Mock()
        path.chmod.side_effect = OSError('readonly')
        with patch.object(json_store, 'os') as mock_os:
            mock_os.name = 'posix'
            # Must not raise.
            _harden_file(path)


if __name__ == '__main__':
    unittest.main()
