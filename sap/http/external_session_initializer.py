"""HTTP session initializer that delegates authentication to an external plugin.

The plugin protocol itself lives in ``sap.http.auth_plugin``; this module turns
the plugin response into the requests.Session state HTTPClient expects: cookies,
an Authorization header, or a client certificate. Each ``content.type`` from the
plugin response maps to a single applier function, so adding a new content type
is a one-line entry in ``_HANDLERS`` plus the applier itself.
"""

from __future__ import annotations

from typing import Optional

from sap.http.auth_plugin import (
    AuthPluginError,
    AuthPluginResponse,
    ConnectionInfo,
    run_plugin,
)
from sap.http.errors import UnauthorizedError


_COOKIE_TYPE = 'cookie'
_HEADER_TYPE = 'http_authorization_header'
_CERT_TYPE = 'certificates'


class HTTPExternalSessionInitializer:
    """Run an auth plugin and apply its response to a requests.Session.

    Implements the ``HTTPSessionInitializer`` protocol from
    ``sap.http.client``. The plugin command is invoked lazily inside
    ``initialize_session`` - constructing the initializer must not perform
    subprocess I/O.
    """

    def __init__(
        self,
        command: str,
        parameters: Optional[dict],
        connection: ConnectionInfo,
        user: Optional[str] = None,
    ):
        self._command = command
        self._parameters = parameters or {}
        self._connection = connection
        self._user = user

    def initialize_session(self, session):
        """Invoke the plugin and apply its response to ``session``."""

        response = run_plugin(self._command, self._parameters, self._connection)
        _apply_response(session, response)
        return session

    def build_unauthorized_error(self, req, res):
        """Build an UnauthorizedError carrying the configured user."""

        return UnauthorizedError(req, res, self._user)


def _apply_response(session, response: AuthPluginResponse) -> None:
    content = response.content
    if not isinstance(content, dict):
        raise AuthPluginError(
            f"Plugin response 'content' must be a JSON object, got "
            f"{type(content).__name__}"
        )

    content_type = content.get('type')
    handler = _HANDLERS.get(content_type) if isinstance(content_type, str) else None
    if handler is None:
        supported = ', '.join(sorted(_HANDLERS))
        raise AuthPluginError(
            f"Unsupported plugin content type: {content_type!r}. "
            f"Expected 'type' to be one of: {supported}"
        )

    handler(session, content)


def _apply_cookies(session, content: dict) -> None:
    cookies = content.get('cookies')
    if not isinstance(cookies, list):
        raise AuthPluginError(
            "Plugin cookie response missing required field 'cookies' (list of "
            "cookie objects)"
        )

    for cookie in cookies:
        if not isinstance(cookie, dict):
            raise AuthPluginError(
                f"Plugin cookie entry must be a JSON object, got "
                f"{type(cookie).__name__}"
            )

        name = cookie.get('name')
        if not name:
            raise AuthPluginError(
                "Plugin cookie entry missing required field 'name'"
            )

        # Empty string is a valid cookie value per RFC 6265; only reject
        # missing keys.
        if 'value' not in cookie:
            raise AuthPluginError(
                "Plugin cookie entry missing required field 'value'"
            )

        kwargs = {}
        for src, dst in (('domain', 'domain'), ('path', 'path'), ('expires', 'expires')):
            if cookie.get(src) is not None:
                kwargs[dst] = cookie[src]
        if 'secure' in cookie:
            if not isinstance(cookie['secure'], bool):
                raise AuthPluginError(
                    "Plugin cookie entry field 'secure' must be a boolean"
                )
            kwargs['secure'] = cookie['secure']

        session.cookies.set(name, cookie['value'], **kwargs)


def _apply_headers(session, content: dict) -> None:
    headers = content.get('headers')
    if not isinstance(headers, dict) or not headers:
        raise AuthPluginError(
            "Plugin http_authorization_header response missing required field "
            "'headers' (non-empty object of header name/value pairs)"
        )

    session.headers.update(headers)


def _apply_certificates(session, content: dict) -> None:
    certificate = content.get('certificate')
    key = content.get('key')
    if not certificate:
        raise AuthPluginError(
            "Plugin certificates response missing required field 'certificate'"
        )
    if not key:
        raise AuthPluginError(
            "Plugin certificates response missing required field 'key'"
        )

    session.cert = (certificate, key)

    issuer = content.get('issuer_certificate')
    if issuer:
        session.verify = issuer


_HANDLERS = {
    _COOKIE_TYPE: _apply_cookies,
    _HEADER_TYPE: _apply_headers,
    _CERT_TYPE: _apply_certificates,
}
