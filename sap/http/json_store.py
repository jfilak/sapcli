"""Generic file-backed JSON cache primitive shared by the auth subsystems.

`JSONFileStore[T]` stores typed payloads as one JSON file per key, with:
- atomic write (tmp + rename) so a kill mid-write never leaves a corrupt file,
- POSIX permission hardening (0o700 on the directory, 0o600 on each file),
- corruption-tolerant reads (any IO/parse error is treated as a cache miss).

Subclasses provide `_serialize` / `_deserialize` for their concrete payload
type T. See `sap.http.token_cache.FileTokenStore` for the OAuth specialization
and the auth-plugin response cache (forthcoming) for the second consumer.
"""

from __future__ import annotations

import os
import stat
import sys
import uuid
from pathlib import Path
from typing import Generic, Optional, TypeVar

from platformdirs import PlatformDirs

APP_NAME = "sapcli"

T = TypeVar('T')


# ---------------------------------------------------------------------------
# Generic file-backed JSON store
# ---------------------------------------------------------------------------

class JSONFileStore(Generic[T]):
    """File-backed JSON store keyed by string.

    Layout:  <base_dir>/<subdir>/<sanitized_key>.json
    POSIX:   directory chmod 0700, file chmod 0600
    Windows: relies on %LOCALAPPDATA% ACLs being user-scoped
    """

    def __init__(self, base_dir: Path, subdir: str) -> None:
        self._dir = base_dir / subdir
        self._dir.mkdir(parents=True, exist_ok=True)
        _harden_dir(self._dir)

    def _serialize(self, value: T) -> str:
        raise NotImplementedError("Subclasses must implement _serialize")

    def _deserialize(self, raw: str) -> T:
        raise NotImplementedError("Subclasses must implement _deserialize")

    def get(self, key: str) -> Optional[T]:
        """Return the payload stored under `key`, or None if absent or corrupt."""

        path = self._path_for(key)
        if not path.exists():
            return None
        try:
            return self._deserialize(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, KeyError, TypeError):
            # Corrupt or unreadable - treat as absent rather than crash.
            # TypeError covers schema drift (e.g. cached JSON is now a list
            # instead of the expected mapping, so dict-style access blows up).
            return None

    def set(self, key: str, value: T) -> None:
        """Store `value` under `key`, overwriting any existing entry atomically."""

        path = self._path_for(key)
        # Unique tmp filename per write so concurrent writers (different
        # processes or threads sharing the same cache dir) never trample each
        # other's in-flight files. Atomic os.replace at the end gives the
        # "no half-written file on disk if killed mid-write" guarantee.
        tmp = path.parent / f'{path.name}.{uuid.uuid4().hex}.tmp'
        try:
            tmp.write_text(self._serialize(value), encoding='utf-8')
            _harden_file(tmp)
            os.replace(tmp, path)
        except Exception:
            # On serialize/IO failure, drop the unique tmp so we do not
            # accumulate stale .tmp garbage in the cache directory.
            tmp.unlink(missing_ok=True)
            raise

    def delete(self, key: str) -> None:
        """Remove the entry for `key`. No-op if it doesn't exist."""

        try:
            self._path_for(key).unlink()
        except FileNotFoundError:
            # Do not crash on such lame reason
            pass

    def _path_for(self, key: str) -> Path:
        return self._dir / f"{_sanitize(key)}.json"


# ---------------------------------------------------------------------------
# Path + permission helpers
# ---------------------------------------------------------------------------

def _default_cache_dir() -> Path:
    """Return the platform-appropriate per-user cache directory for sapcli."""

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
            # Best-effort hardening: chmod can fail on read-only or sandboxed
            # filesystems (containers, NFS mounts, mandatory-access-control
            # setups). The caller already placed the directory inside the
            # user's per-user cache root, so the OS-level isolation is the
            # real defense; the explicit 0700 is belt-and-braces.
            pass


def _harden_file(path: Path) -> None:
    if os.name == "posix":
        try:
            path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
        except OSError:
            # Same rationale as _harden_dir: best-effort hardening, the
            # surrounding directory's perms are the actual access boundary.
            pass


def _sanitize(key: str) -> str:
    """Make `key` safe for use as a filename component."""

    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in key)
    return safe or "default"
