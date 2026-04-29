"""OAuth 2.0 password grant flow with token caching for BTP Steampunk."""

import json
import os
import time
from pathlib import Path

import requests
from requests.auth import AuthBase

from sap.errors import SAPCliError
from sap.http.errors import UnauthorizedError

TOKEN_CACHE_PATH = Path('~/.sapcli/tokens.json').expanduser()
REFRESH_MARGIN = 60


class OAuthTokenError(SAPCliError):
    """Raised when an OAuth token cannot be obtained from the auth server."""


class BearerAuth(AuthBase):
    """Requests auth handler that injects an OAuth 2.0 Bearer token."""

    def __init__(self, token):
        self._token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self._token}'
        return r


# ---------------------------------------------------------------------------
# Token cache
# ---------------------------------------------------------------------------

def _load_token_cache():
    try:
        with open(TOKEN_CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        # Missing or corrupt cache files are not fatal: we simply have no
        # cached tokens and will fetch fresh ones.
        return {}


def _save_token_cache(cache):
    TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(TOKEN_CACHE_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def _cache_key(token_url, client_id):
    return f'{token_url}|{client_id}'


def get_cached_token(token_url, client_id):
    """Return a non-expired cached access token, or None."""

    cache = _load_token_cache()
    entry = cache.get(_cache_key(token_url, client_id))
    if not entry:
        return None
    if time.time() > entry.get('expires_at', 0) - REFRESH_MARGIN:
        return None
    return entry['access_token']


def get_cached_refresh_token(token_url, client_id):
    """Return the cached refresh token, or None."""

    cache = _load_token_cache()
    entry = cache.get(_cache_key(token_url, client_id))
    if not entry:
        return None
    return entry.get('refresh_token')


def save_token_response(token_url, client_id, token_response):
    """Persist an access/refresh token pair into the token cache."""

    cache = _load_token_cache()
    expires_in = token_response.get('expires_in', 3600)
    cache[_cache_key(token_url, client_id)] = {
        'access_token': token_response['access_token'],
        'refresh_token': token_response.get('refresh_token'),
        'expires_at': time.time() + expires_in,
    }
    _save_token_cache(cache)


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------

def refresh_access_token(token_url, client_id, client_secret, refresh_token):
    """Try to swap a refresh token for a new access token. Returns None on failure."""

    response = requests.post(
        token_url.rstrip('/') + '/oauth/token',
        auth=(client_id, client_secret),
        data={'grant_type': 'refresh_token', 'refresh_token': refresh_token},
        timeout=30,
    )
    if not response.ok:
        return None
    token_data = response.json()
    save_token_response(token_url, client_id, token_data)
    return token_data['access_token']


# ---------------------------------------------------------------------------
# Interactive password grant
# ---------------------------------------------------------------------------

def fetch_token_with_credentials(token_url, client_id, client_secret, user, password):
    """Obtain a Bearer token via OAuth 2.0 password grant using provided credentials."""

    response = requests.post(
        token_url.rstrip('/') + '/oauth/token',
        auth=(client_id, client_secret),
        data={
            'grant_type': 'password',
            'username': user,
            'password': password,
        },
        timeout=30,
    )

    if not response.ok:
        raise OAuthTokenError(
            f'OAuth login failed ({response.status_code}): {response.text}'
        )

    token_data = response.json()
    save_token_response(token_url, client_id, token_data)
    return token_data['access_token']


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def get_token(token_url, client_id, client_secret, user=None, password=None):
    """Return a valid Bearer token - from cache, refresh, or credentials grant."""

    token = get_cached_token(token_url, client_id)
    if token:
        return token

    refresh_token = get_cached_refresh_token(token_url, client_id)
    if refresh_token:
        token = refresh_access_token(token_url, client_id, client_secret, refresh_token)
        if token:
            return token

    return fetch_token_with_credentials(token_url, client_id, client_secret, user, password)


# ---------------------------------------------------------------------------
# Session initializer
# ---------------------------------------------------------------------------

class OAuthHTTPSessionInitializer:
    """HTTPSessionInitializer that authenticates the session via OAuth 2.0.

    The token is fetched lazily inside initialize_session; constructing the
    initializer must not perform network I/O.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, token_url, client_id, client_secret, user, password):
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._user = user
        self._password = password

    def initialize_session(self, session):
        """Fetch a Bearer token and attach it to the session."""

        token = get_token(
            self._token_url, self._client_id, self._client_secret,
            user=self._user, password=self._password,
        )
        session.auth = BearerAuth(token)
        return session

    def build_unauthorized_error(self, req, res):
        """Build an UnauthorizedError carrying the configured user."""

        return UnauthorizedError(req, res, self._user)
