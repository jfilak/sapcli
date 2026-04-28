"""OAuth 2.0 password grant flow with token caching for BTP Steampunk."""

import getpass
import json
import os
import time
from pathlib import Path

import requests

TOKEN_CACHE_PATH = Path('~/.sapcli/tokens.json').expanduser()
REFRESH_MARGIN = 60


# ---------------------------------------------------------------------------
# Token cache
# ---------------------------------------------------------------------------

def _load_token_cache():
    try:
        with open(TOKEN_CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_token_cache(cache):
    TOKEN_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(TOKEN_CACHE_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def _cache_key(token_url, client_id):
    return f'{token_url}|{client_id}'


def get_cached_token(token_url, client_id):
    cache = _load_token_cache()
    entry = cache.get(_cache_key(token_url, client_id))
    if not entry:
        return None
    if time.time() > entry.get('expires_at', 0) - REFRESH_MARGIN:
        return None
    return entry['access_token']


def get_cached_refresh_token(token_url, client_id):
    cache = _load_token_cache()
    entry = cache.get(_cache_key(token_url, client_id))
    if not entry:
        return None
    return entry.get('refresh_token')


def save_token_response(token_url, client_id, token_response):
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

def fetch_token_via_password(token_url, client_id, client_secret):
    """Prompt for email + password once, cache the resulting token."""

    print('\nBTP OAuth login required.')
    username = input('Email: ')
    password = getpass.getpass('Password: ')

    response = requests.post(
        token_url.rstrip('/') + '/oauth/token',
        auth=(client_id, client_secret),
        data={
            'grant_type': 'password',
            'username': username,
            'password': password,
        },
        timeout=30,
    )

    if not response.ok:
        raise RuntimeError(
            f'OAuth login failed ({response.status_code}): {response.text}'
        )

    token_data = response.json()
    save_token_response(token_url, client_id, token_data)
    return token_data['access_token']


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def get_token(token_url, client_id, client_secret):
    """Return a valid Bearer token — from cache, refresh, or interactive login."""

    token = get_cached_token(token_url, client_id)
    if token:
        return token

    refresh_token = get_cached_refresh_token(token_url, client_id)
    if refresh_token:
        token = refresh_access_token(token_url, client_id, client_secret, refresh_token)
        if token:
            return token

    return fetch_token_via_password(token_url, client_id, client_secret)
