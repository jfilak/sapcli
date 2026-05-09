#!/usr/bin/env python3
"""sapcli auth plugin: HTTP Basic Auth -> session cookies.

Performs HTTP Basic authentication against the ABAP system and returns the
session cookies set by the server. Functionally equivalent to sapcli's
built-in BasicAuth flow; its purpose is to exercise the auth-plugin
protocol end-to-end with the simplest possible authentication mechanism
so the rest of the plugin pipeline (subprocess invocation, JSON envelope,
content-type dispatch) can be validated against a real ABAP system.

Credentials come from environment variables, NOT from the request payload
or the plugin's `parameters`. This keeps plaintext secrets out of the
sapcli config file:

    SAP_USER       - logon user
    SAP_PASSWORD   - logon password

Configure in your sapcli config:

    users:
      basic-auth-cookies-user:
        auth_plugin:
          command: /absolute/path/to/plugins/auth/basic-auth-cookies.py

Manual invocation (for end-to-end testing without the full CLI wiring):

    echo '{
      "connection": {
        "proto": "https",
        "ashost": "abap.example.org",
        "port": "443",
        "client": "100",
        "type": "adt",
        "path": "/sap/bc/adt/core/systeminformation"
      },
      "parameters": {}
    }' | SAP_USER=me SAP_PASSWORD=secret \\
        python3 plugins/auth/basic-auth-cookies.py
"""

import json
import os
import sys

import requests
from requests.auth import HTTPBasicAuth


def _build_url(connection):
    return (
        f"{connection['proto']}://{connection['ashost']}:"
        f"{connection['port']}{connection['path']}"
    )


def _serialize_cookies(jar):
    cookies = []
    for cookie in jar:
        entry = {'name': cookie.name, 'value': cookie.value}
        if cookie.domain:
            entry['domain'] = cookie.domain
        if cookie.path:
            entry['path'] = cookie.path
        if cookie.expires is not None:
            entry['expires'] = cookie.expires
        if cookie.secure:
            entry['secure'] = True
        cookies.append(entry)
    return cookies


def _emit(message, content=None):
    payload = {'message': message, 'content': content or {}}
    sys.stdout.write(json.dumps(payload))


def _fail(message, code=1):
    _emit(message)
    sys.exit(code)


def main():
    try:
        request = json.loads(sys.stdin.read())
    except json.JSONDecodeError as ex:
        _fail(f'Invalid JSON request on stdin: {ex}')

    connection = request.get('connection')
    if not isinstance(connection, dict):
        _fail("Request is missing the 'connection' object")

    required = ('proto', 'ashost', 'port', 'path', 'client')
    missing = [name for name in required if not connection.get(name)]
    if missing:
        _fail(
            'Request connection is missing required field(s): '
            + ', '.join(missing)
        )

    user = os.environ.get('SAP_USER')
    password = os.environ.get('SAP_PASSWORD')
    if not user or not password:
        _fail('SAP_USER and SAP_PASSWORD environment variables must be set')

    # requests' verify is either bool or path to a CA bundle. ssl_server_cert
    # wins when set, otherwise we fall back to the boolean.
    verify = connection.get('ssl_server_cert') or connection.get('verify', True)
    if verify is False:
        # Suppress the InsecureRequestWarning the user has explicitly
        # opted into via ssl_verify: false / SAP_SSL_VERIFY=no.
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        # GET, not HEAD: newer ABAP systems return 400 on HEAD against
        # /sap/bc/adt/core/discovery and only set the session cookie on
        # GET. Mirrors sap.adt.core.Connection's login_method='GET'.
        response = requests.get(
            _build_url(connection),
            params={'sap-client': connection['client']},
            auth=HTTPBasicAuth(user, password),
            headers={'x-csrf-token': 'Fetch'},
            verify=verify,
            timeout=30,
        )
    except requests.RequestException as ex:
        _fail(f'Request failed: {ex}')

    if response.status_code == 401:
        _fail(f'Authentication failed for user {user!r}: HTTP 401')
    if response.status_code >= 400:
        _fail(
            f'Login endpoint returned HTTP {response.status_code}: '
            f'{response.text[:200]}'
        )

    cookies = _serialize_cookies(response.cookies)
    if not cookies:
        _fail('Server did not set any cookies on the response')

    _emit(
        'Authentication successful',
        content={'type': 'cookie', 'cookies': cookies},
    )


if __name__ == '__main__':
    main()
