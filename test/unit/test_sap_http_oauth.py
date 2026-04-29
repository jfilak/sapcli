#!/usr/bin/env python3

import time
import unittest
from unittest.mock import Mock, patch

from requests.auth import HTTPBasicAuth

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
    refresh_access_token,
    save_token_response,
)


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

    @patch('sap.http.oauth._save_token_cache')
    @patch('sap.http.oauth._load_token_cache', return_value={})
    def test_save_token_response_stores_entry(self, mock_load, mock_save):
        save_token_response('https://auth.example.com', 'client-id', self._make_token_response())

        saved = mock_save.call_args[0][0]
        key = _cache_key('https://auth.example.com', 'client-id')
        self.assertIn(key, saved)
        self.assertEqual(saved[key]['access_token'], 'access-123')
        self.assertEqual(saved[key]['refresh_token'], 'refresh-456')
        self.assertAlmostEqual(saved[key]['expires_at'], time.time() + 3600, delta=5)

    @patch('sap.http.oauth._load_token_cache')
    def test_get_cached_token_returns_valid_token(self, mock_load):
        key = _cache_key('https://auth.example.com', 'client-id')
        mock_load.return_value = {
            key: {
                'access_token': 'valid-token',
                'expires_at': time.time() + 3600,
            }
        }

        token = get_cached_token('https://auth.example.com', 'client-id')

        self.assertEqual(token, 'valid-token')

    @patch('sap.http.oauth._load_token_cache')
    def test_get_cached_token_returns_none_when_expired(self, mock_load):
        key = _cache_key('https://auth.example.com', 'client-id')
        mock_load.return_value = {
            key: {
                'access_token': 'expired-token',
                'expires_at': time.time() - 10,  # already expired
            }
        }

        token = get_cached_token('https://auth.example.com', 'client-id')

        self.assertIsNone(token)

    @patch('sap.http.oauth._load_token_cache', return_value={})
    def test_get_cached_token_returns_none_when_missing(self, mock_load):
        token = get_cached_token('https://auth.example.com', 'client-id')
        self.assertIsNone(token)

    @patch('sap.http.oauth._load_token_cache')
    def test_get_cached_refresh_token_returns_value(self, mock_load):
        key = _cache_key('https://auth.example.com', 'client-id')
        mock_load.return_value = {
            key: {'refresh_token': 'my-refresh-token', 'expires_at': time.time() - 1}
        }

        refresh = get_cached_refresh_token('https://auth.example.com', 'client-id')

        self.assertEqual(refresh, 'my-refresh-token')

    @patch('sap.http.oauth._load_token_cache', return_value={})
    def test_get_cached_refresh_token_returns_none_when_missing(self, mock_load):
        refresh = get_cached_refresh_token('https://auth.example.com', 'client-id')
        self.assertIsNone(refresh)


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------

class TestRefreshAccessToken(unittest.TestCase):

    @patch('sap.http.oauth.save_token_response')
    @patch('sap.http.oauth.requests.post')
    def test_refresh_success(self, mock_post, mock_save):
        mock_post.return_value = Mock(
            ok=True,
            json=lambda: {'access_token': 'new-token', 'expires_in': 3600}
        )

        token = refresh_access_token(
            'https://auth.example.com', 'client-id', 'client-secret', 'old-refresh'
        )

        self.assertEqual(token, 'new-token')
        mock_post.assert_called_once_with(
            'https://auth.example.com/oauth/token',
            auth=('client-id', 'client-secret'),
            data={'grant_type': 'refresh_token', 'refresh_token': 'old-refresh'},
            timeout=30,
        )
        mock_save.assert_called_once()

    @patch('sap.http.oauth.requests.post')
    def test_refresh_failure_returns_none(self, mock_post):
        mock_post.return_value = Mock(ok=False, status_code=401, text='invalid')

        token = refresh_access_token(
            'https://auth.example.com', 'client-id', 'client-secret', 'bad-refresh'
        )

        self.assertIsNone(token)


# ---------------------------------------------------------------------------
# Interactive password grant
# ---------------------------------------------------------------------------

class TestFetchTokenWithCredentials(unittest.TestCase):

    @patch('sap.http.oauth.save_token_response')
    @patch('sap.http.oauth.requests.post')
    def test_password_grant_success(self, mock_post, mock_save):
        mock_post.return_value = Mock(
            ok=True,
            json=lambda: {'access_token': 'user-token', 'refresh_token': 'r-token', 'expires_in': 43200}
        )

        token = fetch_token_with_credentials(
            'https://auth.example.com', 'client-id', 'client-secret',
            'user@sap.com', 'mypassword'
        )

        self.assertEqual(token, 'user-token')
        mock_post.assert_called_once_with(
            'https://auth.example.com/oauth/token',
            auth=('client-id', 'client-secret'),
            data={
                'grant_type': 'password',
                'username': 'user@sap.com',
                'password': 'mypassword',
            },
            timeout=30,
        )
        mock_save.assert_called_once()

    @patch('sap.http.oauth.requests.post')
    def test_password_grant_failure_raises(self, mock_post):
        mock_post.return_value = Mock(ok=False, status_code=401, text='invalid_grant')

        with self.assertRaises(OAuthTokenError) as cm:
            fetch_token_with_credentials(
                'https://auth.example.com', 'client-id', 'client-secret',
                'user@sap.com', 'wrongpass'
            )

        self.assertIn('401', str(cm.exception))
        self.assertIn('invalid_grant', str(cm.exception))


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

    @patch('sap.http.oauth.get_cached_token', return_value='cached-token')
    def test_returns_cached_token_without_refresh_or_login(self, mock_cached):
        token = get_token('https://auth.example.com', 'client-id', 'client-secret')

        self.assertEqual(token, 'cached-token')

    @patch('sap.http.oauth.fetch_token_with_credentials')
    @patch('sap.http.oauth.refresh_access_token', return_value='refreshed-token')
    @patch('sap.http.oauth.get_cached_refresh_token', return_value='old-refresh')
    @patch('sap.http.oauth.get_cached_token', return_value=None)
    def test_uses_refresh_token_when_access_token_expired(
            self, mock_cached, mock_refresh_tok, mock_refresh, mock_password):
        token = get_token('https://auth.example.com', 'client-id', 'client-secret')

        self.assertEqual(token, 'refreshed-token')
        mock_password.assert_not_called()

    @patch('sap.http.oauth.fetch_token_with_credentials', return_value='new-login-token')
    @patch('sap.http.oauth.refresh_access_token', return_value=None)
    @patch('sap.http.oauth.get_cached_refresh_token', return_value='stale-refresh')
    @patch('sap.http.oauth.get_cached_token', return_value=None)
    def test_falls_back_to_password_when_refresh_fails(
            self, mock_cached, mock_refresh_tok, mock_refresh, mock_password):
        token = get_token('https://auth.example.com', 'client-id', 'client-secret')

        self.assertEqual(token, 'new-login-token')

    @patch('sap.http.oauth.fetch_token_with_credentials', return_value='login-token')
    @patch('sap.http.oauth.get_cached_refresh_token', return_value=None)
    @patch('sap.http.oauth.get_cached_token', return_value=None)
    def test_prompts_login_when_no_cache_at_all(
            self, mock_cached, mock_refresh_tok, mock_password):
        token = get_token('https://auth.example.com', 'client-id', 'client-secret')

        self.assertEqual(token, 'login-token')


if __name__ == '__main__':
    unittest.main()
