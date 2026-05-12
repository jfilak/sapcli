#!/usr/bin/env python3

import os
import stat
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from sap.http.auth_plugin import AuthPluginResponse
from sap.http.auth_plugin_cache import (
    AuthPluginResponseFileStore,
    cache_key_for,
    get_response_store,
)


def _response(message='ok', content=None, expiration=None):
    return AuthPluginResponse(
        message=message,
        content=content if content is not None else {'type': 'cookie', 'cookies': []},
        expiration=expiration,
    )


class TestCacheKeyFor(unittest.TestCase):

    def test_combines_three_components_with_pipe(self):
        # The triple is the cache-isolation contract from the spec: changing
        # any of context, connection, or user must not reuse a cached entry
        # minted for a different combination.
        self.assertEqual(
            cache_key_for('dev', 'localhost', 'developer'),
            '8bb9ac567da8a43ca1f89ac47fdefc15a61b1bcfc711e9a6018bd50599e4aa11',
        )

    def test_different_combinations_produce_different_keys(self):
        keys = {
            cache_key_for('dev', 'host1', 'u1'),
            cache_key_for('dev', 'host2', 'u1'),
            cache_key_for('dev', 'host1', 'u2'),
            cache_key_for('prod', 'host1', 'u1'),
        }
        self.assertEqual(len(keys), 4)


class TestAuthPluginResponseFileStoreRoundTrip(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = AuthPluginResponseFileStore(base_dir=Path(self._tmp.name))

    def test_set_then_get_returns_equivalent_response(self):
        original = _response(
            content={'type': 'cookie', 'cookies': [{'name': 'X', 'value': 'y'}]},
            expiration=datetime(2026, 5, 8, 12, tzinfo=timezone.utc),
        )

        key = cache_key_for('dev', 'localhost', 'developer')
        self.store.set(key, original)
        loaded = self.store.get(key)

        self.assertEqual(loaded.message, original.message)
        self.assertEqual(loaded.content, original.content)
        self.assertEqual(loaded.expiration, original.expiration)

    def test_get_missing_key_returns_none(self):
        key = cache_key_for('absent', 'key', 'here')
        self.assertIsNone(self.store.get(key))

    def test_set_overwrites_existing_entry(self):
        self.store.set('k', _response(message='first'))
        self.store.set('k', _response(message='second'))

        self.assertEqual(self.store.get('k').message, 'second')

    def test_delete_removes_entry(self):
        self.store.set('k', _response())
        self.store.delete('k')

        self.assertIsNone(self.store.get('k'))

    def test_delete_missing_key_is_noop(self):
        self.store.delete('never-stored')

    def test_response_without_expiration_round_trips(self):
        # No expiration field is the common case for cookie plugins; the
        # store must not require one.
        self.store.set('k', _response(expiration=None))
        loaded = self.store.get('k')

        self.assertIsNone(loaded.expiration)

    def test_two_keys_are_isolated(self):
        self.store.set('a', _response(message='for-a'))
        self.store.set('b', _response(message='for-b'))

        self.assertEqual(self.store.get('a').message, 'for-a')
        self.assertEqual(self.store.get('b').message, 'for-b')

    def test_cache_directory_has_owner_only_permissions(self):
        self.store.set('k', _response())
        cache_dir = Path(self._tmp.name) / 'auth_plugin_responses'
        mode = stat.S_IMODE(cache_dir.stat().st_mode)
        self.assertEqual(mode, 0o700)

    def test_cache_file_has_owner_only_permissions(self):
        self.store.set('k', _response())
        cache_dir = Path(self._tmp.name) / 'auth_plugin_responses'
        for entry in cache_dir.iterdir():
            mode = stat.S_IMODE(entry.stat().st_mode)
            self.assertEqual(mode, 0o600)

    def test_keys_with_pipe_separator_sanitized_in_filename(self):
        # Pipe is not a portable filename character; JSONFileStore sanitizes
        # it. We only care that the round-trip works - the on-disk filename
        # is an implementation detail.
        key = cache_key_for('dev', 'host', 'user')
        self.store.set(key, _response(message='live'))
        self.assertEqual(self.store.get(key).message, 'live')


class TestExpiredResponseStillReadable(unittest.TestCase):
    """The store does not police expiration - that's the caller's job. An
       expired response must still be readable so the caller can decide
       whether to refresh.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = AuthPluginResponseFileStore(base_dir=Path(self._tmp.name))

    def test_expired_response_round_trips(self):
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        self.store.set('k', _response(expiration=past))

        loaded = self.store.get('k')

        self.assertIsNotNone(loaded)
        self.assertTrue(loaded.is_expired())


class TestGetResponseStoreSingleton(unittest.TestCase):

    def test_returns_same_instance_on_repeat_calls(self):
        # Reset the module-level singleton for an isolated test.
        with patch('sap.http.auth_plugin_cache._response_store', None):
            first = get_response_store()
            second = get_response_store()

        self.assertIs(first, second)

    def test_default_instance_uses_default_cache_dir(self):
        with patch('sap.http.auth_plugin_cache._response_store', None), \
             patch('sap.http.auth_plugin_cache._default_cache_dir') as mock_dir:
            mock_dir.return_value = Path(tempfile.mkdtemp())
            try:
                store = get_response_store()
                self.assertIsInstance(store, AuthPluginResponseFileStore)
                mock_dir.assert_called_once()
            finally:
                import shutil
                shutil.rmtree(mock_dir.return_value, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
