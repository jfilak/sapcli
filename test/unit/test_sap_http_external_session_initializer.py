#!/usr/bin/env python3

import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import requests

from sap.http.auth_plugin import (
    AuthPluginError,
    AuthPluginResponse,
    ConnectionInfo,
)
from sap.http.client import HTTPClient, HTTPSessionInitializer
from sap.http.client_cert import ClientCertificateError
from sap.http.errors import UnauthorizedError
from sap.http.external_session_initializer import HTTPExternalSessionInitializer

from fixtures_sap_http_client_cert import (
    CERTIFICATE_PEM,
    ENCRYPTED_PKCS8_KEY_PEM,
    PLAIN_KEY_PEM,
    SERVER_CA_PEM,
)


def _connection():
    return ConnectionInfo(
        proto='https',
        ashost='abap.example.org',
        port='44300',
        client='100',
        type='adt',
        path='/sap/bc/adt/core/systeminformation',
    )


def _response(content, message='ok', expiration=None):
    return AuthPluginResponse(
        message=message,
        content=content,
        expiration=expiration,
    )


class TestConstruction(unittest.TestCase):

    def test_satisfies_session_initializer_protocol(self):
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )

        self.assertIsInstance(initializer, HTTPSessionInitializer)

    @patch('sap.http.external_session_initializer.run_plugin')
    def test_does_not_run_plugin_at_construction(self, mock_run):
        HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )

        mock_run.assert_not_called()

    @patch('sap.http.external_session_initializer.run_plugin')
    def test_initialize_session_returns_same_session(self, mock_run):
        mock_run.return_value = _response({'type': 'cookie', 'cookies': []})
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )
        session = requests.Session()

        returned = initializer.initialize_session(session)

        self.assertIs(returned, session)

    @patch('sap.http.external_session_initializer.run_plugin')
    def test_initialize_session_invokes_plugin_with_configured_args(self, mock_run):
        mock_run.return_value = _response({'type': 'cookie', 'cookies': []})
        connection = _connection()
        parameters = {'channel': 'msedge'}
        initializer = HTTPExternalSessionInitializer(
            command='sapcli-windows-cert-auth',
            parameters=parameters,
            connection=connection,
            user='u',
        )

        initializer.initialize_session(requests.Session())

        mock_run.assert_called_once_with(
            'sapcli-windows-cert-auth', parameters, connection
        )

    @patch('sap.http.external_session_initializer.run_plugin')
    def test_initialize_session_propagates_plugin_error(self, mock_run):
        mock_run.side_effect = AuthPluginError('plugin crashed')
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )

        with self.assertRaisesRegex(AuthPluginError, 'plugin crashed'):
            initializer.initialize_session(requests.Session())

    def test_build_unauthorized_error_carries_user(self):
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='alice'
        )
        req = Mock()
        res = Mock()

        err = initializer.build_unauthorized_error(req, res)

        self.assertIsInstance(err, UnauthorizedError)
        self.assertIs(err.request, req)
        self.assertIs(err.response, res)
        self.assertEqual(err.user, 'alice')


class TestCookieDispatch(unittest.TestCase):

    def _initialize(self, content):
        with patch(
            'sap.http.external_session_initializer.run_plugin',
            return_value=_response(content),
        ):
            initializer = HTTPExternalSessionInitializer(
                command='cmd', parameters={}, connection=_connection(), user='u'
            )
            session = requests.Session()
            initializer.initialize_session(session)
            return session

    def test_minimal_cookie_sets_name_and_value(self):
        session = self._initialize({
            'type': 'cookie',
            'cookies': [{'name': 'SAP_SESSIONID', 'value': 'abc123'}],
        })

        self.assertEqual(session.cookies.get('SAP_SESSIONID'), 'abc123')

    def test_multiple_cookies_all_set(self):
        session = self._initialize({
            'type': 'cookie',
            'cookies': [
                {'name': 'A', 'value': '1'},
                {'name': 'B', 'value': '2'},
            ],
        })

        self.assertEqual(session.cookies.get('A'), '1')
        self.assertEqual(session.cookies.get('B'), '2')

    def test_cookie_with_domain_and_path(self):
        session = self._initialize({
            'type': 'cookie',
            'cookies': [{
                'name': 'SAP_SESSIONID',
                'value': 'abc',
                'domain': 'abap.example.org',
                'path': '/sap',
            }],
        })

        # Read back via get with the same domain/path filter we passed in.
        self.assertEqual(
            session.cookies.get('SAP_SESSIONID', domain='abap.example.org', path='/sap'),
            'abc',
        )

    def test_missing_cookies_field_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "cookies"):
            self._initialize({'type': 'cookie'})

    def test_cookies_not_a_list_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "cookies"):
            self._initialize({'type': 'cookie', 'cookies': 'not-a-list'})

    def test_cookie_without_name_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "name"):
            self._initialize({
                'type': 'cookie',
                'cookies': [{'value': 'abc'}],
            })

    def test_cookie_without_value_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "value"):
            self._initialize({
                'type': 'cookie',
                'cookies': [{'name': 'X'}],
            })

    def test_cookie_entry_not_object_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "object"):
            self._initialize({
                'type': 'cookie',
                'cookies': ['name=value; Path=/'],
            })


class TestHeaderDispatch(unittest.TestCase):

    def _initialize(self, content):
        with patch(
            'sap.http.external_session_initializer.run_plugin',
            return_value=_response(content),
        ):
            initializer = HTTPExternalSessionInitializer(
                command='cmd', parameters={}, connection=_connection(), user='u'
            )
            session = requests.Session()
            initializer.initialize_session(session)
            return session

    def test_authorization_header_set(self):
        session = self._initialize({
            'type': 'http_authorization_header',
            'headers': {'Authorization': 'Basic abc123'},
        })

        self.assertEqual(session.headers.get('Authorization'), 'Basic abc123')

    def test_multiple_headers_set(self):
        session = self._initialize({
            'type': 'http_authorization_header',
            'headers': {
                'Authorization': 'Bearer xyz',
                'X-Custom': 'value',
            },
        })

        self.assertEqual(session.headers.get('Authorization'), 'Bearer xyz')
        self.assertEqual(session.headers.get('X-Custom'), 'value')

    def test_missing_headers_field_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "headers"):
            self._initialize({'type': 'http_authorization_header'})

    def test_empty_headers_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "headers"):
            self._initialize({
                'type': 'http_authorization_header',
                'headers': {},
            })

    def test_headers_not_a_dict_raises(self):
        with self.assertRaisesRegex(AuthPluginError, "headers"):
            self._initialize({
                'type': 'http_authorization_header',
                'headers': ['Authorization: Basic abc'],
            })


class TestCertificatesDispatch(unittest.TestCase):

    def setUp(self):
        # pylint: disable=consider-using-with
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp_dir.cleanup)

    def _write(self, name, content):
        path = os.path.join(self._tmp_dir.name, name)
        with open(path, 'w', encoding='ascii') as pem_file:
            pem_file.write(content)

        return path

    def _initialize(self, content):
        with patch(
            'sap.http.external_session_initializer.run_plugin',
            return_value=_response(content),
        ):
            initializer = HTTPExternalSessionInitializer(
                command='cmd', parameters={}, connection=_connection(), user='u'
            )
            session = requests.Session()
            initializer.initialize_session(session)
            return session

    def test_certificate_and_key_set_session_cert(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', PLAIN_KEY_PEM)

        session = self._initialize({
            'type': 'certificates',
            'certificate': cert,
            'key': key,
        })

        self.assertEqual(session.cert, (cert, key))

    def test_issuer_certificate_sets_session_verify(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', PLAIN_KEY_PEM)
        issuer = self._write('ca.pem', SERVER_CA_PEM)

        session = self._initialize({
            'type': 'certificates',
            'certificate': cert,
            'key': key,
            'issuer_certificate': issuer,
        })

        self.assertEqual(session.verify, issuer)

    def test_missing_certificate_raises(self):
        key = self._write('client.key', PLAIN_KEY_PEM)

        with self.assertRaisesRegex(AuthPluginError, "certificate"):
            self._initialize({
                'type': 'certificates',
                'key': key,
            })

    def test_missing_key_raises(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)

        with self.assertRaisesRegex(AuthPluginError, "key"):
            self._initialize({
                'type': 'certificates',
                'certificate': cert,
            })

    def test_nonexistent_certificate_file_raises(self):
        key = self._write('client.key', PLAIN_KEY_PEM)
        missing = os.path.join(self._tmp_dir.name, 'nosuch.crt')

        with self.assertRaisesRegex(ClientCertificateError, 'nosuch.crt'):
            self._initialize({
                'type': 'certificates',
                'certificate': missing,
                'key': key,
            })

    def test_encrypted_key_file_raises(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', ENCRYPTED_PKCS8_KEY_PEM)

        with self.assertRaisesRegex(ClientCertificateError, 'encrypted'):
            self._initialize({
                'type': 'certificates',
                'certificate': cert,
                'key': key,
            })


class TestUnknownContentType(unittest.TestCase):

    @patch('sap.http.external_session_initializer.run_plugin')
    def test_unknown_type_raises(self, mock_run):
        mock_run.return_value = _response({'type': 'oauth_token'})
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )

        with self.assertRaisesRegex(AuthPluginError, 'oauth_token'):
            initializer.initialize_session(requests.Session())

    @patch('sap.http.external_session_initializer.run_plugin')
    def test_missing_type_raises(self, mock_run):
        mock_run.return_value = _response({'cookies': []})
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )

        with self.assertRaisesRegex(AuthPluginError, 'type'):
            initializer.initialize_session(requests.Session())

    @patch('sap.http.external_session_initializer.run_plugin')
    def test_content_not_a_dict_raises(self, mock_run):
        mock_run.return_value = _response('not-an-object')
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )

        with self.assertRaisesRegex(AuthPluginError, 'content'):
            initializer.initialize_session(requests.Session())


class TestHTTPClientWithExternalInitializer(unittest.TestCase):

    def test_external_initializer_is_used_when_provided(self):
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='u'
        )

        client = HTTPClient(host='h', user='u', password=None, session_initializer=initializer)

        self.assertIs(client._session_initializer, initializer)

    def test_build_unauthorized_error_delegates_to_initializer(self):
        initializer = HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(), user='alice'
        )
        client = HTTPClient(host='h', user='u', password=None, session_initializer=initializer)
        req = Mock()
        res = Mock()

        err = client.build_unauthorized_error(req, res)

        self.assertIsInstance(err, UnauthorizedError)
        self.assertEqual(err.user, 'alice')


class TestCacheIntegration(unittest.TestCase):
    """When cache_key is set, initialize_session must:
       1. consult the cache first;
       2. on miss/expired, run the plugin and store the result;
       3. never read or write the cache when cache_key is None (back-compat
          for callers that did not opt in to caching).
    """

    def _make(self, cache_key=None):
        return HTTPExternalSessionInitializer(
            command='cmd', parameters={}, connection=_connection(),
            user='u', cache_key=cache_key,
        )

    @patch('sap.http.external_session_initializer.get_response_store')
    @patch('sap.http.external_session_initializer.run_plugin')
    def test_no_cache_key_skips_cache_entirely(self, mock_run, mock_store):
        mock_run.return_value = _response({'type': 'cookie', 'cookies': []})

        self._make(cache_key=None).initialize_session(requests.Session())

        mock_run.assert_called_once()
        mock_store.assert_not_called()

    @patch('sap.http.external_session_initializer.get_response_store')
    @patch('sap.http.external_session_initializer.run_plugin')
    def test_cache_miss_runs_plugin_and_stores(self, mock_run, mock_store):
        store = Mock()
        store.get.return_value = None
        mock_store.return_value = store
        plugin_response = _response({'type': 'cookie', 'cookies': []})
        mock_run.return_value = plugin_response

        self._make(cache_key='ctx|conn|u').initialize_session(requests.Session())

        store.get.assert_called_once_with('ctx|conn|u')
        mock_run.assert_called_once()
        store.set.assert_called_once_with('ctx|conn|u', plugin_response)

    @patch('sap.http.external_session_initializer.get_response_store')
    @patch('sap.http.external_session_initializer.run_plugin')
    def test_cache_hit_skips_plugin(self, mock_run, mock_store):
        store = Mock()
        cached = _response(
            {'type': 'cookie', 'cookies': [{'name': 'X', 'value': 'cached'}]},
        )
        store.get.return_value = cached
        mock_store.return_value = store
        session = requests.Session()

        self._make(cache_key='k').initialize_session(session)

        mock_run.assert_not_called()
        store.set.assert_not_called()
        # Cookies from the cached response must land on the session.
        self.assertEqual(session.cookies.get('X'), 'cached')

    @patch('sap.http.external_session_initializer.get_response_store')
    @patch('sap.http.external_session_initializer.run_plugin')
    def test_expired_cache_entry_is_refreshed(self, mock_run, mock_store):
        store = Mock()
        # is_expired() returning True makes the initializer treat it as a miss.
        expired = AuthPluginResponse(
            message='stale', content={'type': 'cookie', 'cookies': []},
            expiration=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        store.get.return_value = expired
        mock_store.return_value = store
        fresh = _response({'type': 'cookie', 'cookies': []})
        mock_run.return_value = fresh

        self._make(cache_key='k').initialize_session(requests.Session())

        mock_run.assert_called_once()
        store.set.assert_called_once_with('k', fresh)

    @patch('sap.http.external_session_initializer.get_response_store')
    @patch('sap.http.external_session_initializer.run_plugin')
    def test_plugin_error_does_not_poison_cache(self, mock_run, mock_store):
        store = Mock()
        store.get.return_value = None
        mock_store.return_value = store
        mock_run.side_effect = AuthPluginError('plugin crashed')

        with self.assertRaises(AuthPluginError):
            self._make(cache_key='k').initialize_session(requests.Session())

        store.set.assert_not_called()


if __name__ == '__main__':
    unittest.main()
