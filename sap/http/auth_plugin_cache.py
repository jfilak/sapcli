"""File-backed cache for AuthPluginResponse objects.

Plugins can be slow - browser-based SSO can take minutes - so caching the
response across sapcli invocations is the difference between "interactive
once a day" and "interactive every command". Storage uses the same
JSONFileStore primitive that backs the OAuth token cache: atomic writes,
0o700/0o600 perms on POSIX, corruption-tolerant reads.

The cache does NOT police expiration. ``AuthPluginResponse.is_expired`` is
checked by the caller (the session initializer); the store just stores. An
expired entry is therefore still readable, which lets the initializer log
'using stale cookies' or refresh as it sees fit.

Future implementation: OS keyring backend - the response can carry a
session cookie, which is a credential. Today's plaintext-on-disk choice
matches what the OAuth token store already does, and the same migration
path applies (introduce an ABC, swap the factory).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import json
import hashlib

from sap.http.auth_plugin import AuthPluginResponse
from sap.http.json_store import JSONFileStore, _default_cache_dir


class AuthPluginResponseFileStore(JSONFileStore[AuthPluginResponse]):
    """File-backed cache of plugin responses under ``<cache_dir>/auth_plugin_responses/``."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        super().__init__(base_dir or _default_cache_dir(), "auth_plugin_responses")

    def _serialize(self, value: AuthPluginResponse) -> str:
        return value.to_json()

    def _deserialize(self, raw: str) -> AuthPluginResponse:
        return AuthPluginResponse.from_json(raw)


def cache_key_for(context: str, connection: str, user: str) -> str:
    """Build the cache key for a (context, connection, user) tuple.

    The triple captures the spec's cache-isolation requirement: changing
    any of the three must not let a cached response leak across to a
    different combination. Uses ``|`` as the separator since it is not a
    valid identifier character (no collisions) and JSONFileStore's
    filename sanitiser turns it into ``_`` on disk anyway.
    """

    raw = json.dumps([context, connection, user], separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


_response_store: Optional[AuthPluginResponseFileStore] = None


def get_response_store() -> AuthPluginResponseFileStore:
    """Return the configured plugin-response cache.

    Today: file-based.
    Tomorrow: read an env var or config flag and return a keyring-backed
    store instead, the same way ``get_token_store`` is wired.
    """

    global _response_store  # pylint: disable=global-statement
    if _response_store is None:
        _response_store = AuthPluginResponseFileStore()
    return _response_store
