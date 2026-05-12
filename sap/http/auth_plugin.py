"""Plugin protocol for external authentication helpers.

sapcli runs an external command (the auth plugin) as a subprocess, writes a
JSON authentication request to its stdin, and parses the JSON response from
its stdout. This module defines the request/response shape and the
``run_plugin`` driver. Interpretation of the response payload (cookies,
Authorization header, client certificate) is the responsibility of the
caller - see ``sap.http.external_session_initializer``.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional

from sap.errors import SAPCliError


class AuthPluginError(SAPCliError):
    """Raised when the auth plugin cannot be invoked or returns invalid output."""


@dataclass(frozen=True)
# pylint: disable=too-many-instance-attributes
class ConnectionInfo:
    """Connection details forwarded to the plugin in the request payload."""

    proto: str
    ashost: str
    port: str
    client: str
    type: str
    path: str
    # Optional because HTTP-only plugins have no use for it; required by RFC
    # plugins (and by ABAP RFC SDK callers in general) since sysnr selects
    # the application-server instance (gateway port = 33<sysnr>).
    sysnr: Optional[str] = None
    # Whether the plugin should verify the server's TLS certificate.
    # Defaults to True (the safe default); sapcli forwards args.verify here
    # so a user with ssl_verify: false in config doesn't have to teach
    # every plugin about SAP_SSL_VERIFY independently.
    verify: bool = True
    # Optional path to a custom CA bundle, mirroring sapcli's
    # SAP_SSL_SERVER_CERT / ssl_server_cert config knob.
    ssl_server_cert: Optional[str] = None

    def to_dict(self) -> dict:
        """Return the JSON-serializable form."""

        return asdict(self)


@dataclass(frozen=True)
class AuthPluginRequest:
    """Request sent to the plugin on stdin."""

    connection: ConnectionInfo
    parameters: dict

    def to_dict(self) -> dict:
        """Return the JSON-serializable form."""

        return {
            'connection': self.connection.to_dict(),
            'parameters': dict(self.parameters),
        }

    def to_json(self) -> str:
        """Return the JSON string ready for stdin."""

        return json.dumps(self.to_dict())


@dataclass(frozen=True)
class AuthPluginResponse:
    """Response received from the plugin on stdout."""

    message: str
    content: dict
    expiration: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data) -> 'AuthPluginResponse':
        """Build a response from a parsed JSON object, validating required fields."""

        if not isinstance(data, dict):
            raise ValueError(
                f'response is not a JSON object, got {type(data).__name__}'
            )

        if 'message' not in data:
            raise ValueError("response missing required field 'message'")

        if 'content' not in data:
            raise ValueError("response missing required field 'content'")

        return cls(
            message=data['message'],
            content=data['content'],
            expiration=_parse_expiration(data.get('expiration')),
        )

    @classmethod
    def from_json(cls, raw: str) -> 'AuthPluginResponse':
        """Build a response from a JSON string."""

        return cls.from_dict(json.loads(raw))

    def to_dict(self) -> dict:
        """Return the JSON-serializable form, omitting absent expiration."""

        data: dict = {'message': self.message, 'content': self.content}
        if self.expiration is not None:
            # Naive datetimes are interpreted as UTC; better than crashing
            # or silently round-tripping them as local time.
            ts = self.expiration
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            data['expiration'] = ts.astimezone(timezone.utc).isoformat()
        return data

    def to_json(self) -> str:
        """Return the JSON string, suitable for cache storage."""

        return json.dumps(self.to_dict())

    def is_expired(self, *, leeway_seconds: int = 30) -> bool:
        """Return True when the response is at or past its expiration.

        Mirrors Token.is_expired: missing expiration means "never expires"
        - the server is responsible for ultimately invalidating the
        session. Plugins that know their token lifetime should set
        expiration explicitly.
        """

        if self.expiration is None:
            return False

        ts = self.expiration
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return (ts - datetime.now(timezone.utc)).total_seconds() <= leeway_seconds


def _parse_expiration(value) -> Optional[datetime]:
    if not value:
        return None

    if not isinstance(value, str):
        raise ValueError(
            f'expiration must be an ISO 8601 string, got {type(value).__name__}'
        )

    # datetime.fromisoformat in 3.10 does not understand the trailing Z;
    # rewriting it to +00:00 keeps the parser portable across versions.
    normalized = value[:-1] + '+00:00' if value.endswith('Z') else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as ex:
        raise ValueError(f'invalid expiration {value!r}: {ex}') from ex


def run_plugin(command: str, parameters, connection: ConnectionInfo) -> AuthPluginResponse:
    """Run the external auth plugin and return its parsed response.

    Raises ``AuthPluginError`` if the plugin cannot be started, exits non-zero,
    or returns output that is not a valid response.
    """

    request = AuthPluginRequest(connection=connection, parameters=parameters or {})

    try:
        completed = subprocess.run(
            [command],
            input=request.to_json(),
            capture_output=True,
            check=False,
            encoding='utf-8',
        )
    except OSError as ex:
        raise AuthPluginError(
            f"Failed to start auth plugin '{command}': {ex}"
        ) from ex

    if completed.returncode != 0:
        raise AuthPluginError(
            f"Auth plugin '{command}' exited with code {completed.returncode}\n"
            f"stdout: {completed.stdout}\n"
            f"stderr: {completed.stderr}"
        )

    try:
        return AuthPluginResponse.from_json(completed.stdout)
    except (ValueError, TypeError) as ex:
        raise AuthPluginError(
            f"Auth plugin '{command}' returned invalid response: {ex}\n"
            f"stdout: {completed.stdout}\n"
            f"stderr: {completed.stderr}"
        ) from ex
