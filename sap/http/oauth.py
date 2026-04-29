"""OAuth 2.0 password grant flow with token caching for BTP Steampunk."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import requests
from requests.auth import AuthBase

from sap.errors import SAPCliError
from sap.http.errors import UnauthorizedError
from sap.http.token_cache import get_token_store, Token

DEFAULT_EXPIRES_IN = 3600

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

def _load_token(token_key: str) -> Optional[Token]:
    return get_token_store().get(token_key)


def _save_token(token_key: str, token: Token) -> None:
    get_token_store().set(token_key, token)


def _cache_key(token_url: str, client_id: str) -> str:
    return f'{token_url}|{client_id}'


def get_cached_token(token_url: str, client_id: str) -> Optional[str]:
    """Return a non-expired cached access token, or None."""

    token = _load_token(_cache_key(token_url, client_id))

    if not token:
        return None

    if token.is_expired(leeway_seconds=REFRESH_MARGIN):
        return None

    return token.access_token


def get_cached_refresh_token(token_url: str, client_id: str):
    """Return the cached refresh token, or None."""

    token = _load_token(_cache_key(token_url, client_id))

    if not token:
        return None

    return token.refresh_token


def save_token_response(token_url: str, client_id: str, token_response: dict) -> None:
    """Persist an access/refresh token pair into the token cache."""

    expires_in = token_response.get('expires_in', DEFAULT_EXPIRES_IN)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))

    new_token = Token(
        access_token=token_response['access_token'],
        token_type=token_response.get('token_type', 'Bearer'),
        expires_at=expires_at,
        refresh_token=token_response.get('refresh_token'),
        scope=token_response.get('scope'),
    )
    _save_token(_cache_key(token_url, client_id), new_token)


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


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def password_required(token_url: Optional[str], client_id: Optional[str]) -> bool:
    """Returns true if user must provide password"""

    has_valid_token = (
        token_url and client_id and (
            get_cached_token(token_url, client_id)
            or get_cached_refresh_token(token_url, client_id)
        )
    )

    return not has_valid_token
