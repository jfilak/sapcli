#!/usr/bin/env python3

import json
import time
import unittest
from unittest.mock import MagicMock, Mock, patch, call

from sap.http.client import BearerAuth, HTTPClient
from sap.http.oauth import (
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
# HTTPClient OAuth init
# ---------------------------------------------------------------------------

class TestHTTPClientOAuthInit(unittest.TestCase):

    @patch('sap.http.client.get_token', return_value='bearer-token-123')
    def test_uses_bearer_auth_when_oauth_params_provided(self, mock_get_token):
        client = HTTPClient(
            host='btp.example.com',
            user='user@sap.com',
            password='secret',
            token_url='https://auth.example.com',
            client_id='my-client-id',
            client_secret='my-client-secret',
        )

        mock_get_token.assert_called_once_with(
            'https://auth.example.com', 'my-client-id', 'my-client-secret',
            user='user@sap.com', password='secret'
        )
        self.assertIsInstance(client._auth, BearerAuth)

    @patch('sap.http.client.get_token')
    def test_uses_basic_auth_when_no_token_url(self, mock_get_token):
        from requests.auth import HTTPBasicAuth
        client = HTTPClient(host='c50.example.com', user='ELBEZI', password='pass')

        mock_get_token.assert_not_called()
        self.assertIsInstance(client._auth, HTTPBasicAuth)

    @patch('sap.http.client.get_token')
    def test_uses_basic_auth_when_token_url_missing(self, mock_get_token):
        from requests.auth import HTTPBasicAuth
        client = HTTPClient(
            host='c50.example.com',
            user='ELBEZI',
            password='pass',
            client_id='some-id',
            client_secret='some-secret',
            # token_url deliberately omitted
        )

        mock_get_token.assert_not_called()
        self.assertIsInstance(client._auth, HTTPBasicAuth)


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

        with self.assertRaises(RuntimeError) as cm:
            fetch_token_with_credentials(
                'https://auth.example.com', 'client-id', 'client-secret',
                'user@sap.com', 'wrongpass'
            )

        self.assertIn('401', str(cm.exception))


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
