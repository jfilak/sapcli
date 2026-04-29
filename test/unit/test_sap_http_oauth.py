#!/usr/bin/env python3

import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from sap.http.client import HTTPClient
from sap.http.errors import UnauthorizedError
from sap.http.oauth import (
    BearerAuth,
    OAuthHTTPSessionInitializer,
    OAuthTokenError,
    _cache_key,
    fetch_token_with_credentials,
    get_cached_token,
    get_cached_refresh_token,
    get_token,
    password_required,
    refresh_access_token,
    save_token_response,
)
from sap.http.token_cache import Token

from test.unit.mock import InMemoryTokenStore


# ---------------------------------------------------------------------------
# Disk-write guard
#
# A test must never hit the default FileTokenStore: that would write under the
# real user's home directory. We patch sap.http.oauth.get_token_store at module
# scope so any path that forgets a per-test patch still gets an in-memory store
# instead of falling through to disk. Per-test @patch decorators override this
# guard for their own scope, then it is restored automatically on teardown.
# ---------------------------------------------------------------------------

_module_token_store_patcher = None


def setUpModule():
    global _module_token_store_patcher
    _module_token_store_patcher = patch(
        'sap.http.oauth.get_token_store',
        side_effect=InMemoryTokenStore,
    )
    _module_token_store_patcher.start()


def tearDownModule():
    _module_token_store_patcher.stop()


# ---------------------------------------------------------------------------
# BearerAuth
# ---------------------------------------------------------------------------

class TestBearerAuth(unittest.TestCase):

    def test_adds_authorization_header(self):
        auth = BearerAuth('my-token')
        request = Mock()
        request.headers = {}

        result = auth(request)

        self.assertEqual(request.headers['Authorization'], 'Bearer my-token')
        self.assertIs(result, request)

    def test_overwrites_existing_authorization_header(self):
        auth = BearerAuth('new-token')
        request = Mock()
        request.headers = {'Authorization': 'Basic old'}

        auth(request)

        self.assertEqual(request.headers['Authorization'], 'Bearer new-token')


# ---------------------------------------------------------------------------
# OAuthHTTPSessionInitializer
# ---------------------------------------------------------------------------

class TestOAuthHTTPSessionInitializer(unittest.TestCase):

    fixture_token_url = 'https://auth.example.com'
    fixture_client_id = 'my-client-id'
    fixture_client_secret = 'my-client-secret'
    fixture_user = 'user@sap.com'
    fixture_password = 'secret'

    def _make_initializer(self):
        return OAuthHTTPSessionInitializer(
            self.fixture_token_url,
            self.fixture_client_id,
            self.fixture_client_secret,
            self.fixture_user,
            self.fixture_password,
        )

    @patch('sap.http.oauth.get_token')
    def test_does_not_fetch_token_at_construction(self, mock_get_token):
        """Token fetch must be lazy and happen only inside initialize_session."""

        self._make_initializer()

        mock_get_token.assert_not_called()

    @patch('sap.http.oauth.get_token', return_value='bearer-token-123')
    def test_initialize_session_fetches_token_and_sets_bearer_auth(self, mock_get_token):
        initializer = self._make_initializer()
        session = Mock()

        returned = initializer.initialize_session(session)

        mock_get_token.assert_called_once_with(
            self.fixture_token_url,
            self.fixture_client_id,
            self.fixture_client_secret,
            user=self.fixture_user,
            password=self.fixture_password,
        )
        self.assertIs(returned, session)
        self.assertIsInstance(session.auth, BearerAuth)

    @patch('sap.http.oauth.get_token', return_value='abc')
    def test_initialize_session_passes_token_to_bearer_auth(self, mock_get_token):
        initializer = self._make_initializer()
        session = Mock()

        initializer.initialize_session(session)

        # Verify the BearerAuth carries the token returned by get_token
        request = Mock()
        request.headers = {}
        session.auth(request)
        self.assertEqual(request.headers['Authorization'], 'Bearer abc')

    def test_build_unauthorized_error_uses_user(self):
        initializer = self._make_initializer()
        req = Mock()
        res = Mock()

        err = initializer.build_unauthorized_error(req, res)

        self.assertIsInstance(err, UnauthorizedError)
        self.assertIs(err.request, req)
        self.assertIs(err.response, res)
        self.assertEqual(err.user, self.fixture_user)


# ---------------------------------------------------------------------------
# HTTPClient with OAuth initializer
# ---------------------------------------------------------------------------

class TestHTTPClientWithOAuthInitializer(unittest.TestCase):

    def test_default_initializer_is_basic_auth(self):
        client = HTTPClient(host='c50.example.com', user='ELBEZI', password='pass')

        # Default still BasicAuth — no OAuth knobs on HTTPClient ctor.
        self.assertIsInstance(client._session_initializer.build_unauthorized_error(Mock(), Mock()), UnauthorizedError)

    def test_oauth_initializer_is_used_when_provided(self):
        initializer = OAuthHTTPSessionInitializer(
            'https://auth.example.com', 'cid', 'csec', 'usr', 'pwd'
        )

        client = HTTPClient(host='h', user='usr', password='pwd', session_initializer=initializer)

        self.assertIs(client._session_initializer, initializer)


# ---------------------------------------------------------------------------
# Token cache
# ---------------------------------------------------------------------------

class TestTokenCache(unittest.TestCase):

    def _make_token_response(self, access_token='access-123', refresh_token='refresh-456', expires_in=3600):
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': expires_in,
        }

    @patch('sap.http.oauth.get_token_store')
    def test_save_token_response_stores_entry(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store
        save_token_response('https://auth.example.com', 'client-id', self._make_token_response())
        key = _cache_key('https://auth.example.com', 'client-id')
        token = inmemory_store.get(key)
        self.assertIsNotNone(token)
        self.assertEqual(token.access_token, 'access-123')
        self.assertEqual(token.refresh_token, 'refresh-456')
        self.assertAlmostEqual(token.expires_at.timestamp(), time.time() + 3600, delta=5)

    @patch('sap.http.oauth.get_token_store')
    def test_save_token_response_persists_token_type_and_scope(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        response = self._make_token_response()
        response['token_type'] = 'MAC'
        response['scope'] = 'openid email'

        save_token_response('https://auth.example.com', 'client-id', response)

        token = inmemory_store.get(_cache_key('https://auth.example.com', 'client-id'))
        self.assertEqual(token.token_type, 'MAC')
        self.assertEqual(token.scope, 'openid email')

    @patch('sap.http.oauth.get_token_store')
    def test_save_token_response_defaults_token_type_to_bearer(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        # Response without token_type or scope.
        save_token_response('https://auth.example.com', 'client-id', self._make_token_response())

        token = inmemory_store.get(_cache_key('https://auth.example.com', 'client-id'))
        self.assertEqual(token.token_type, 'Bearer')
        self.assertIsNone(token.scope)

    @patch('sap.http.oauth.get_token_store')
    def test_save_token_response_falls_back_to_default_expires_in(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        # No expires_in field — implementation must fall back to DEFAULT_EXPIRES_IN (3600).
        save_token_response(
            'https://auth.example.com', 'client-id',
            {'access_token': 'a', 'refresh_token': 'r'},
        )

        token = inmemory_store.get(_cache_key('https://auth.example.com', 'client-id'))
        self.assertAlmostEqual(token.expires_at.timestamp(), time.time() + 3600, delta=5)

    @patch('sap.http.oauth.get_token_store')
    def test_get_cached_token_returns_valid_token(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        key = _cache_key('https://auth.example.com', 'client-id')

        inmemory_store.set(
            key,
            Token(
                access_token='valid-token',
                expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600)
            )
        )

        token = get_cached_token('https://auth.example.com', 'client-id')

        self.assertEqual(token, 'valid-token')

    @patch('sap.http.oauth.get_token_store')
    def test_get_cached_token_returns_none_when_expired(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        key = _cache_key('https://auth.example.com', 'client-id')

        inmemory_store.set(
            key,
            Token(
                access_token='valid-token',
                expires_at=datetime.now(timezone.utc) - timedelta(seconds=3600)
            )
        )

        token = get_cached_token('https://auth.example.com', 'client-id')

        self.assertIsNone(token)

    @patch('sap.http.oauth.get_token_store')
    def test_get_cached_token_returns_none_when_missing(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        token = get_cached_token('https://auth.example.com', 'client-id')
        self.assertIsNone(token)

    @patch('sap.http.oauth.get_token_store')
    def test_get_cached_refresh_token_returns_value(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        key = _cache_key('https://auth.example.com', 'client-id')
        inmemory_store.set(
            key,
            Token(
                access_token='expired_token',
                refresh_token='my-refresh-token',
                expires_at=datetime.now(timezone.utc) - timedelta(seconds=3600)
            )
        )

        refresh = get_cached_refresh_token('https://auth.example.com', 'client-id')

        self.assertEqual(refresh, 'my-refresh-token')

    @patch('sap.http.oauth.get_token_store')
    def test_get_cached_refresh_token_returns_none_when_missing(self, fake_token_store):
        inmemory_store = InMemoryTokenStore()
        fake_token_store.return_value = inmemory_store

        refresh = get_cached_refresh_token('https://auth.example.com', 'client-id')
        self.assertIsNone(refresh)


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------

class TestRefreshAccessToken(unittest.TestCase):

    fixture_token_url = 'https://auth.example.com'
    fixture_client_id = 'client-id'
    fixture_client_secret = 'client-secret'

    @patch('sap.http.oauth.requests.post')
    @patch('sap.http.oauth.get_token_store')
    def test_refresh_success(self, fake_token_store, mock_post):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store

        mock_post.return_value = Mock(
            ok=True,
            json=lambda: {'access_token': 'new-token', 'expires_in': 3600}
        )

        token = refresh_access_token(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret, 'old-refresh'
        )

        self.assertEqual(token, 'new-token')
        mock_post.assert_called_once_with(
            'https://auth.example.com/oauth/token',
            auth=(self.fixture_client_id, self.fixture_client_secret),
            data={'grant_type': 'refresh_token', 'refresh_token': 'old-refresh'},
            timeout=30,
        )

        stored = store.get(_cache_key(self.fixture_token_url, self.fixture_client_id))
        self.assertIsNotNone(stored)
        self.assertEqual(stored.access_token, 'new-token')

    @patch('sap.http.oauth.requests.post')
    @patch('sap.http.oauth.get_token_store')
    def test_refresh_failure_returns_none(self, fake_token_store, mock_post):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store

        mock_post.return_value = Mock(ok=False, status_code=401, text='invalid')

        token = refresh_access_token(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret, 'bad-refresh'
        )

        self.assertIsNone(token)
        # On failure nothing should have been written to the store.
        self.assertIsNone(store.get(_cache_key(self.fixture_token_url, self.fixture_client_id)))


# ---------------------------------------------------------------------------
# Interactive password grant
# ---------------------------------------------------------------------------

class TestFetchTokenWithCredentials(unittest.TestCase):

    fixture_token_url = 'https://auth.example.com'
    fixture_client_id = 'client-id'
    fixture_client_secret = 'client-secret'

    @patch('sap.http.oauth.requests.post')
    @patch('sap.http.oauth.get_token_store')
    def test_password_grant_success(self, fake_token_store, mock_post):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store

        mock_post.return_value = Mock(
            ok=True,
            json=lambda: {'access_token': 'user-token', 'refresh_token': 'r-token', 'expires_in': 43200}
        )

        token = fetch_token_with_credentials(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret,
            'user@sap.com', 'mypassword'
        )

        self.assertEqual(token, 'user-token')
        mock_post.assert_called_once_with(
            'https://auth.example.com/oauth/token',
            auth=(self.fixture_client_id, self.fixture_client_secret),
            data={
                'grant_type': 'password',
                'username': 'user@sap.com',
                'password': 'mypassword',
            },
            timeout=30,
        )

        stored = store.get(_cache_key(self.fixture_token_url, self.fixture_client_id))
        self.assertIsNotNone(stored)
        self.assertEqual(stored.access_token, 'user-token')
        self.assertEqual(stored.refresh_token, 'r-token')

    @patch('sap.http.oauth.requests.post')
    @patch('sap.http.oauth.get_token_store')
    def test_password_grant_failure_raises(self, fake_token_store, mock_post):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store

        mock_post.return_value = Mock(ok=False, status_code=401, text='invalid_grant')

        with self.assertRaises(OAuthTokenError) as cm:
            fetch_token_with_credentials(
                self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret,
                'user@sap.com', 'wrongpass'
            )

        self.assertIn('401', str(cm.exception))
        self.assertIn('invalid_grant', str(cm.exception))
        # Failed grant must not pollute the store.
        self.assertIsNone(store.get(_cache_key(self.fixture_token_url, self.fixture_client_id)))


# ---------------------------------------------------------------------------
# OAuthTokenError is a SAPCliError subclass
# ---------------------------------------------------------------------------

class TestOAuthTokenError(unittest.TestCase):

    def test_is_sapcli_error(self):
        from sap.errors import SAPCliError
        self.assertTrue(issubclass(OAuthTokenError, SAPCliError))


# ---------------------------------------------------------------------------
# get_token — orchestration
# ---------------------------------------------------------------------------

class TestGetToken(unittest.TestCase):

    fixture_token_url = 'https://auth.example.com'
    fixture_client_id = 'client-id'
    fixture_client_secret = 'client-secret'

    def _key(self):
        return _cache_key(self.fixture_token_url, self.fixture_client_id)

    @patch('sap.http.oauth.fetch_token_with_credentials')
    @patch('sap.http.oauth.refresh_access_token')
    @patch('sap.http.oauth.get_token_store')
    def test_returns_cached_token_without_refresh_or_login(
            self, fake_token_store, mock_refresh, mock_password):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store
        store.set(self._key(), Token(
            access_token='cached-token',
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=3600),
        ))

        token = get_token(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret
        )

        self.assertEqual(token, 'cached-token')
        mock_refresh.assert_not_called()
        mock_password.assert_not_called()

    @patch('sap.http.oauth.fetch_token_with_credentials')
    @patch('sap.http.oauth.refresh_access_token', return_value='refreshed-token')
    @patch('sap.http.oauth.get_token_store')
    def test_uses_refresh_token_when_access_token_expired(
            self, fake_token_store, mock_refresh, mock_password):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store
        store.set(self._key(), Token(
            access_token='expired',
            refresh_token='old-refresh',
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        ))

        token = get_token(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret
        )

        self.assertEqual(token, 'refreshed-token')
        mock_refresh.assert_called_once_with(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret, 'old-refresh',
        )
        mock_password.assert_not_called()

    @patch('sap.http.oauth.fetch_token_with_credentials', return_value='new-login-token')
    @patch('sap.http.oauth.refresh_access_token', return_value=None)
    @patch('sap.http.oauth.get_token_store')
    def test_falls_back_to_password_when_refresh_fails(
            self, fake_token_store, mock_refresh, mock_password):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store
        store.set(self._key(), Token(
            access_token='expired',
            refresh_token='stale-refresh',
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        ))

        token = get_token(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret
        )

        self.assertEqual(token, 'new-login-token')
        mock_refresh.assert_called_once()
        mock_password.assert_called_once()

    @patch('sap.http.oauth.fetch_token_with_credentials', return_value='login-token')
    @patch('sap.http.oauth.refresh_access_token')
    @patch('sap.http.oauth.get_token_store')
    def test_prompts_login_when_no_cache_at_all(
            self, fake_token_store, mock_refresh, mock_password):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store

        token = get_token(
            self.fixture_token_url, self.fixture_client_id, self.fixture_client_secret
        )

        self.assertEqual(token, 'login-token')
        mock_refresh.assert_not_called()
        mock_password.assert_called_once()


# ---------------------------------------------------------------------------
# password_required
# ---------------------------------------------------------------------------

class TestPasswordRequired(unittest.TestCase):

    fixture_token_url = 'https://auth.example.com'
    fixture_client_id = 'client-id'

    def _key(self):
        return _cache_key(self.fixture_token_url, self.fixture_client_id)

    @patch('sap.http.oauth.get_token_store')
    def test_returns_false_when_valid_cached_token(self, fake_token_store):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store
        store.set(self._key(), Token(
            access_token='cached',
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))

        self.assertFalse(password_required(self.fixture_token_url, self.fixture_client_id))

    @patch('sap.http.oauth.get_token_store')
    def test_returns_false_when_only_refresh_token_cached(self, fake_token_store):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store
        store.set(self._key(), Token(
            access_token='expired',
            refresh_token='refresh-1',
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
        ))

        self.assertFalse(password_required(self.fixture_token_url, self.fixture_client_id))

    @patch('sap.http.oauth.get_token_store')
    def test_returns_true_when_nothing_cached(self, fake_token_store):
        fake_token_store.return_value = InMemoryTokenStore()

        self.assertTrue(password_required(self.fixture_token_url, self.fixture_client_id))

    @patch('sap.http.oauth.get_token_store')
    def test_returns_true_when_token_url_is_none(self, fake_token_store):
        store = InMemoryTokenStore()
        fake_token_store.return_value = store
        # Even if a token happens to exist under this key, missing token_url means OAuth is off.
        store.set(self._key(), Token(
            access_token='cached',
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))

        self.assertTrue(password_required(None, self.fixture_client_id))

    @patch('sap.http.oauth.get_token_store')
    def test_returns_true_when_client_id_is_none(self, fake_token_store):
        fake_token_store.return_value = InMemoryTokenStore()

        self.assertTrue(password_required(self.fixture_token_url, None))


if __name__ == '__main__':
    unittest.main()
