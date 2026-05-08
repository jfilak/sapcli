"""Token storage for the tool with a swappable backend.

Current implementation: plaintext JSON files in the per-user cache directory
(see `sap.http.json_store.JSONFileStore`).
Future implementation: OS credential manager (Keychain / Credential Manager /
Secret Service) — drop in a new TokenStore subclass and change the factory.

Why a Token dataclass instead of dict[str, Any]. The store's contract is a
typed thing, not a bag of strings. When you swap to the keyring backend, the
new implementation has to handle the same Token shape — that constraint is what
keeps the two interchangeable. If you let dict flow through the interface,
every backend will end up disagreeing on what keys are required and you've lost
the abstraction.

Why key-by-string instead of methods like get_github_token(). OAuth helpers
usually grow a second provider eventually (GitLab, Azure, internal IdP). Keying
by client_id (or provider:client_id) means the same store handles all of them
without interface churn. If you only ever have one token, key="default" is
fine.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sap.http.json_store import (
    JSONFileStore,
    _default_cache_dir,
    _harden_dir,
    _harden_file,
    _sanitize,
)

# Re-exported for backward compatibility with code that imported these
# helpers from sap.http.token_cache.
__all__ = [
    'Token',
    'TokenStore',
    'FileTokenStore',
    'get_token_store',
    '_default_cache_dir',
    '_harden_dir',
    '_harden_file',
    '_sanitize',
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Token:
    """An OAuth bearer token plus the metadata we care about."""

    access_token: str
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None  # absolute, UTC
    refresh_token: Optional[str] = None
    scope: Optional[str] = None

    def is_expired(self, *, leeway_seconds: int = 30) -> bool:
        """Checks if the token is expired. Returns True if expired, otherwise False.
           The token is expired if the remaining time is lower than leeway_seconds.
        """

        if self.expires_at is None:
            return False

        now = datetime.now(timezone.utc)

        return (self.expires_at - now).total_seconds() <= leeway_seconds

    def to_json(self) -> str:
        """Returns JSON string of the token"""

        d = asdict(self)

        if self.expires_at is not None:
            d["expires_at"] = self.expires_at.astimezone(timezone.utc).isoformat()

        return json.dumps(d, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> "Token":
        """Factory methods turning JSON string to Token"""

        d = json.loads(raw)

        if d.get("expires_at"):
            d["expires_at"] = datetime.fromisoformat(d["expires_at"])

        return cls(**d)


# ---------------------------------------------------------------------------
# Abstract backend
# ---------------------------------------------------------------------------

class TokenStore(ABC):
    """Persist and retrieve OAuth tokens, keyed by client_id (or any string).

    Implementations must be safe to call concurrently from a single user's
    processes; cross-user safety is the OS's problem.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Token]:
        """Return the stored token for `key`, or None if absent."""

    @abstractmethod
    def set(self, key: str, token: Token) -> None:
        """Store `token` under `key`, overwriting any existing entry."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove the entry for `key`. No-op if it doesn't exist."""


# ---------------------------------------------------------------------------
# File-based implementation (today)
# ---------------------------------------------------------------------------

class FileTokenStore(JSONFileStore[Token], TokenStore):
    """File-backed Token store under <cache_dir>/tokens/.

    JSONFileStore comes first in the MRO so its concrete get/set/delete
    satisfy the abstract methods declared on TokenStore.
    """

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        super().__init__(base_dir or _default_cache_dir(), "tokens")

    def _serialize(self, value: Token) -> str:
        return value.to_json()

    def _deserialize(self, raw: str) -> Token:
        return Token.from_json(raw)


# ---------------------------------------------------------------------------
# Factory — the one place to change when swapping backends
# ---------------------------------------------------------------------------

_token_store: Optional[TokenStore] = None


def get_token_store() -> TokenStore:
    """Return the configured token store.

    Today: file-based.
    Tomorrow: read an env var or config flag and return a
    KeyringTokenStore / DPAPITokenStore / KeychainTokenStore instead.
    """

    global _token_store  # pylint: disable=global-statement
    if _token_store is None:
        _token_store = FileTokenStore()

    return _token_store
