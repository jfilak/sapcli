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
from sap.http.auth_plugin_cache import get_response_store
from sap.http.client_cert import ClientCertificateHTTPSessionInitializer
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

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        command: str,
        parameters: Optional[dict],
        connection: ConnectionInfo,
        user: Optional[str] = None,
        cache_key: Optional[str] = None,
    ):
        self._command = command
        self._parameters = parameters or {}
        self._connection = connection
        self._user = user
        # When cache_key is None, the cache is bypassed entirely - both
        # reads and writes. That keeps cache-less callers (tests, ad-hoc
        # invocations) from accidentally writing a response to disk.
        self._cache_key = cache_key

    def initialize_session(self, session):
        """Invoke the plugin (or reuse a cached response) and apply it to ``session``."""

        response = self._fetch_response()
        _apply_response(session, response)
        return session

    def _fetch_response(self) -> AuthPluginResponse:
        if self._cache_key:
            cached = get_response_store().get(self._cache_key)
            if cached is not None and not cached.is_expired():
                return cached

        # Plugin error must propagate without touching the cache - storing
        # half-built or failed responses would mask the problem on the
        # next run and make 'something is broken' harder to diagnose.
        response = run_plugin(self._command, self._parameters, self._connection)

        if self._cache_key:
            get_response_store().set(self._cache_key, response)

        return response

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

    ClientCertificateHTTPSessionInitializer(
        certificate, key, server_ca=content.get('issuer_certificate'),
    ).initialize_session(session)


_HANDLERS = {
    _COOKIE_TYPE: _apply_cookies,
    _HEADER_TYPE: _apply_headers,
    _CERT_TYPE: _apply_certificates,
}
