"""Token storage for thetool with a swappable backend.

Current implementation: plaintext JSON files in the per-user cache directory.
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

The atomic write. write_text followed by os.replace is the standard
pattern for "never leave a corrupt file on disk if interrupted." Worth keeping
even though the failure mode is rare.
"""

from __future__ import annotations

import json
import os
import stat
import sys
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from platformdirs import PlatformDirs

APP_NAME = "sapcli"


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

class FileTokenStore(TokenStore):
    """Stores tokens as plaintext JSON files, one per key.

    Layout:  <base_dir>/tokens/<sanitized_key>.json
    POSIX:   directory chmod 0700, file chmod 0600
    Windows: relies on %LOCALAPPDATA% ACLs being user-scoped
    """

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self._base_dir = base_dir or _default_cache_dir()
        self._tokens_dir = self._base_dir / "tokens"
        self._tokens_dir.mkdir(parents=True, exist_ok=True)
        _harden_dir(self._tokens_dir)

    # -- TokenStore -----------------------------------------------------

    def get(self, key: str) -> Optional[Token]:
        path = self._path_for(key)
        if not path.exists():
            return None
        try:
            return Token.from_json(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, KeyError):
            # Corrupt or unreadable — treat as absent rather than crash.
            return None

    def set(self, key: str, token: Token) -> None:
        path = self._path_for(key)
        # Write to a temp file and rename, so we never leave a half-written
        # token behind if the process is killed mid-write.
        tmp = path.with_suffix(path.suffix + '.tmp')
        tmp.write_text(token.to_json(), encoding='utf-8')
        _harden_file(tmp)
        os.replace(tmp, path)

    def delete(self, key: str) -> None:
        try:
            self._path_for(key).unlink()
        except FileNotFoundError:
            # Do not crash on such lame reason
            pass

    # -- internals ------------------------------------------------------

    def _path_for(self, key: str) -> Path:
        return self._tokens_dir / f"{_sanitize(key)}.json"


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


# ---------------------------------------------------------------------------
# Path + permission helpers
# ---------------------------------------------------------------------------

def _default_cache_dir() -> Path:
    dirs = PlatformDirs(appname=APP_NAME, roaming=False)
    if sys.platform == "linux":
        path = Path(dirs.user_state_dir)
    elif sys.platform == "darwin":
        path = Path(dirs.user_data_dir)
    elif sys.platform == "win32":
        path = Path(dirs.user_data_dir)
    else:
        path = Path(dirs.user_state_dir)
    path.mkdir(parents=True, exist_ok=True)
    _harden_dir(path)
    return path


def _harden_dir(path: Path) -> None:
    if os.name == "posix":
        try:
            path.chmod(stat.S_IRWXU)  # 0o700
        except OSError:
            pass


def _harden_file(path: Path) -> None:
    if os.name == "posix":
        try:
            path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
        except OSError:
            pass


def _sanitize(key: str) -> str:
    """Make `key` safe for use as a filename component."""
    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in key)
    return safe or "default"
