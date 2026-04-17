#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch, MagicMock

import requests.exceptions

from sap.http.client import (
    build_query_args,
    build_url,
    default_http_error_handler,
    HTTPClient,
)
from sap.http.errors import (
    HTTPRequestError,
    UnauthorizedError,
    TimedOutRequestError,
)


class TestBuildQueryArgs(unittest.TestCase):

    def test_no_arguments(self):
        self.assertEqual(build_query_args(), {})

    def test_client_only(self):
        self.assertEqual(build_query_args(client='100'), {'sap-client': '100'})

    def test_saml2_enabled(self):
        self.assertEqual(build_query_args(saml2=True), {'saml2': 'enabled'})

    def test_saml2_disabled(self):
        self.assertEqual(build_query_args(saml2=False), {'saml2': 'disabled'})

    def test_client_and_saml2(self):
        result = build_query_args(client='200', saml2=True)
        self.assertEqual(result, {'sap-client': '200', 'saml2': 'enabled'})

    def test_none_values_ignored(self):
        result = build_query_args(client=None, saml2=None)
        self.assertEqual(result, {})


class TestBuildUrl(unittest.TestCase):

    def test_ssl_defaults(self):
        url, params = build_url(host='example.com', path='sap/bc/adt')

        self.assertEqual(url, 'https://example.com:443/sap/bc/adt')
        self.assertEqual(params, {})

    def test_no_ssl_defaults(self):
        url, params = build_url(ssl=False, host='example.com', path='sap/bc/adt')

        self.assertEqual(url, 'http://example.com:80/sap/bc/adt')
        self.assertEqual(params, {})

    def test_custom_port(self):
        url, _ = build_url(host='example.com', port='8443', path='sap/bc/adt')

        self.assertEqual(url, 'https://example.com:8443/sap/bc/adt')

    def test_no_ssl_custom_port(self):
        url, _ = build_url(ssl=False, host='example.com', port='8080', path='api')

        self.assertEqual(url, 'http://example.com:8080/api')

    def test_with_client_and_saml2(self):
        url, params = build_url(host='example.com', path='sap/bc/adt', client='100', saml2=True)

        self.assertEqual(url, 'https://example.com:443/sap/bc/adt')
        self.assertEqual(params, {'sap-client': '100', 'saml2': 'enabled'})

    def test_no_path_returns_base_url(self):
        url, params = build_url(host='example.com')

        self.assertEqual(url, 'https://example.com:443')
        self.assertEqual(params, {})


class TestDefaultHttpErrorHandler(unittest.TestCase):

    def test_raises_unauthorized_for_401(self):
        client = Mock()
        client.user = 'SAP*'
        req = Mock()
        res = Mock()
        res.status_code = 401

        with self.assertRaises(UnauthorizedError) as cm:
            default_http_error_handler(client, req, res)

        self.assertIs(cm.exception.request, req)
        self.assertIs(cm.exception.response, res)
        self.assertEqual(cm.exception.user, 'SAP*')

    def test_raises_http_request_error_for_non_401(self):
        client = Mock()
        req = Mock()
        res = Mock()
        res.status_code = 500

        with self.assertRaises(HTTPRequestError) as cm:
            default_http_error_handler(client, req, res)

        self.assertIs(cm.exception.request, req)
        self.assertIs(cm.exception.response, res)
        self.assertEqual(cm.exception.status_code, 500)

    def test_raises_http_request_error_for_403(self):
        client = Mock()
        req = Mock()
        res = Mock()
        res.status_code = 403

        with self.assertRaises(HTTPRequestError):
            default_http_error_handler(client, req, res)

    def test_raises_http_request_error_for_404(self):
        client = Mock()
        req = Mock()
        res = Mock()
        res.status_code = 404

        with self.assertRaises(HTTPRequestError):
            default_http_error_handler(client, req, res)


class TestHTTPClientInit(unittest.TestCase):

    def test_defaults_ssl(self):
        client = HTTPClient(host='example.com', user='SAP*', password='pass')

        self.assertTrue(client.ssl)
        self.assertEqual(client.host, 'example.com')
        self.assertEqual(client.port, '443')
        self.assertEqual(client.protocol, 'https')
        self.assertEqual(client.user, 'SAP*')
        self.assertIsNone(client.client)
        self.assertIsNone(client.saml2)
        self.assertEqual(client.login_path, '')
        self.assertEqual(client.login_method, 'HEAD')
        self.assertIsNone(client.ssl_verify)
        self.assertIsNone(client.ssl_server_cert)
        self.assertEqual(client._base_url, 'https://example.com:443')

    def test_defaults_no_ssl(self):
        client = HTTPClient(ssl=False, host='example.com', user='SAP*', password='pass')

        self.assertFalse(client.ssl)
        self.assertEqual(client.port, '80')
        self.assertEqual(client.protocol, 'http')
        self.assertEqual(client._base_url, 'http://example.com:80')

    def test_custom_port_ssl(self):
        client = HTTPClient(host='example.com', port='8443', user='u', password='p')

        self.assertEqual(client.port, '8443')
        self.assertEqual(client.protocol, 'https')
        self.assertEqual(client._base_url, 'https://example.com:8443')

    def test_custom_port_no_ssl(self):
        client = HTTPClient(ssl=False, host='example.com', port='8080', user='u', password='p')

        self.assertEqual(client.port, '8080')
        self.assertEqual(client.protocol, 'http')
        self.assertEqual(client._base_url, 'http://example.com:8080')

    def test_all_parameters(self):
        client = HTTPClient(
            ssl=True,
            host='myhost',
            port='44300',
            user='admin',
            password='secret',
            saml2=True,
            client='100',
            verify=False,
            ssl_server_cert='/path/to/cert.pem',
            login_path='sap/bc/adt',
            login_method='GET'
        )

        self.assertEqual(client.host, 'myhost')
        self.assertEqual(client.port, '44300')
        self.assertEqual(client.user, 'admin')
        self.assertTrue(client.saml2)
        self.assertEqual(client.client, '100')
        self.assertFalse(client.ssl_verify)
        self.assertEqual(client.ssl_server_cert, '/path/to/cert.pem')
        self.assertEqual(client.login_path, 'sap/bc/adt')
        self.assertEqual(client.login_method, 'GET')

    def test_default_error_handlers(self):
        client = HTTPClient(host='h', user='u', password='p')

        self.assertEqual(len(client.error_handlers), 1)
        self.assertIs(client.error_handlers[0], default_http_error_handler)

    def test_no_connection_error_handler(self):
        client = HTTPClient(host='h', user='u', password='p')

        self.assertIsNone(client._connection_error_handler)


class TestHTTPClientAddErrorHandler(unittest.TestCase):

    def test_add_error_handler_prepends(self):
        client = HTTPClient(host='h', user='u', password='p')
        custom_handler = Mock()

        client.add_error_handler(custom_handler)

        self.assertEqual(len(client.error_handlers), 2)
        self.assertIs(client.error_handlers[0], custom_handler)
        self.assertIs(client.error_handlers[1], default_http_error_handler)

    def test_add_multiple_handlers_order(self):
        client = HTTPClient(host='h', user='u', password='p')
        first = Mock()
        second = Mock()

        client.add_error_handler(first)
        client.add_error_handler(second)

        self.assertEqual(len(client.error_handlers), 3)
        self.assertIs(client.error_handlers[0], second)
        self.assertIs(client.error_handlers[1], first)
        self.assertIs(client.error_handlers[2], default_http_error_handler)


class TestHTTPClientHandleHttpError(unittest.TestCase):

    def test_calls_handlers_in_order(self):
        client = HTTPClient(host='h', user='u', password='p')
        call_order = []

        def handler1(c, req, res):
            call_order.append('handler1')

        def handler2(c, req, res):
            call_order.append('handler2')

        client.error_handlers = [handler1, handler2]
        client.handle_http_error(Mock(), Mock())

        self.assertEqual(call_order, ['handler1', 'handler2'])

    def test_stops_at_first_raising_handler(self):
        client = HTTPClient(host='h', user='u', password='p')

        def raising_handler(c, req, res):
            raise HTTPRequestError(req, res)

        unreachable = Mock()
        client.error_handlers = [raising_handler, unreachable]

        with self.assertRaises(HTTPRequestError):
            client.handle_http_error(Mock(), Mock(status_code=500, text='err'))

        unreachable.assert_not_called()

    def test_default_handler_raises_unauthorized(self):
        client = HTTPClient(host='h', user='u', password='p')
        req = Mock()
        res = Mock()
        res.status_code = 401

        with self.assertRaises(UnauthorizedError):
            client.handle_http_error(req, res)

    def test_default_handler_raises_http_request_error(self):
        client = HTTPClient(host='h', user='u', password='p')
        req = Mock()
        res = Mock()
        res.status_code = 500

        with self.assertRaises(HTTPRequestError):
            client.handle_http_error(req, res)


class TestHTTPClientSetConnectionErrorHandler(unittest.TestCase):

    def test_set_connection_error_handler(self):
        client = HTTPClient(host='h', user='u', password='p')
        handler = Mock()

        client.set_connection_error_handler(handler)

        self.assertIs(client._connection_error_handler, handler)


class TestHTTPClientRetrieve(unittest.TestCase):

    def _make_client(self, **kwargs):
        defaults = dict(host='example.com', user='SAP*', password='pass', client='100')
        defaults.update(kwargs)
        return HTTPClient(**defaults)

    @patch('sap.http.client.requests.Request')
    def test_retrieve_success(self, mock_request_cls):
        client = self._make_client()
        session = Mock()

        prepared = Mock()
        session.prepare_request.return_value = prepared

        response = Mock()
        response.text = 'OK'
        session.send.return_value = response

        req, res = client.retrieve(session, 'GET', 'sap/bc/adt')

        self.assertIs(req, prepared)
        self.assertIs(res, response)
        session.send.assert_called_once_with(prepared, timeout=client.timeout)

    @patch('sap.http.client.requests.Request')
    def test_retrieve_builds_url(self, mock_request_cls):
        client = self._make_client(ssl=True, host='myhost', port='44300', client='200', saml2=True)
        session = Mock()
        session.prepare_request.return_value = Mock()
        session.send.return_value = Mock(text='')

        client.retrieve(session, 'POST', 'api/path', params={'foo': 'bar'}, headers={'X-H': '1'}, body='data')

        mock_request_cls.assert_called_once()
        args, kwargs = mock_request_cls.call_args
        self.assertEqual(args[0], 'POST')
        self.assertEqual(args[1], 'https://myhost:44300/api/path')
        self.assertEqual(kwargs['params'], {'sap-client': '200', 'saml2': 'enabled', 'foo': 'bar'})
        self.assertEqual(kwargs['data'], 'data')
        self.assertEqual(kwargs['headers'], {'X-H': '1'})

    @patch('sap.http.client.requests.Request')
    def test_retrieve_path_without_leading_slash(self, mock_request_cls):
        client = self._make_client(ssl=True, host='myhost', port='44300')
        session = Mock()
        session.prepare_request.return_value = Mock()
        session.send.return_value = Mock(text='')

        client.retrieve(session, 'GET', 'api/path')

        args = mock_request_cls.call_args[0]
        self.assertEqual(args[1], 'https://myhost:44300/api/path')

    @patch('sap.http.client.requests.Request')
    def test_retrieve_path_with_leading_slash(self, mock_request_cls):
        client = self._make_client(ssl=True, host='myhost', port='44300')
        session = Mock()
        session.prepare_request.return_value = Mock()
        session.send.return_value = Mock(text='')

        client.retrieve(session, 'GET', '/api/path')

        args = mock_request_cls.call_args[0]
        self.assertEqual(args[1], 'https://myhost:44300/api/path')

    @patch('sap.http.client.requests.Request')
    def test_retrieve_method_uppercased(self, mock_request_cls):
        client = self._make_client()
        session = Mock()
        session.prepare_request.return_value = Mock()
        session.send.return_value = Mock(text='')

        client.retrieve(session, 'get', 'path')

        args = mock_request_cls.call_args[0]
        self.assertEqual(args[0], 'GET')

    @patch('sap.http.client.requests.Request')
    def test_retrieve_connect_timeout(self, mock_request_cls):
        client = self._make_client()
        session = Mock()
        session.prepare_request.return_value = Mock(method='GET', url='https://example.com:443/path')
        session.send.side_effect = requests.exceptions.ConnectTimeout('connect timed out')

        with self.assertRaises(TimedOutRequestError) as cm:
            client.retrieve(session, 'GET', 'path')

        self.assertEqual(cm.exception.timeout, client.timeout)

    @patch('sap.http.client.requests.Request')
    def test_retrieve_read_timeout(self, mock_request_cls):
        client = self._make_client()
        session = Mock()
        session.prepare_request.return_value = Mock(method='GET', url='https://example.com:443/path')
        session.send.side_effect = requests.exceptions.ReadTimeout('read timed out')

        with self.assertRaises(TimedOutRequestError) as cm:
            client.retrieve(session, 'GET', 'path')

        self.assertEqual(cm.exception.timeout, client.timeout)

    @patch('sap.http.client.requests.Request')
    def test_retrieve_connection_error_no_handler_reraises(self, mock_request_cls):
        client = self._make_client()
        session = Mock()
        session.prepare_request.return_value = Mock()
        session.send.side_effect = requests.exceptions.ConnectionError('connection refused')

        with self.assertRaises(requests.exceptions.ConnectionError):
            client.retrieve(session, 'GET', 'path')

    @patch('sap.http.client.requests.Request')
    def test_retrieve_connection_error_handler_no_raise_reraises(self, mock_request_cls):
        client = self._make_client()
        handler = Mock()
        client.set_connection_error_handler(handler)

        session = Mock()
        session.prepare_request.return_value = Mock()
        conn_error = requests.exceptions.ConnectionError('connection refused')
        session.send.side_effect = conn_error

        with self.assertRaises(requests.exceptions.ConnectionError):
            client.retrieve(session, 'GET', 'path')

        handler.assert_called_once_with(client, conn_error)

    @patch('sap.http.client.requests.Request')
    def test_retrieve_connection_error_with_handler(self, mock_request_cls):
        client = self._make_client()
        handler = Mock()
        client.set_connection_error_handler(handler)

        session = Mock()
        session.prepare_request.return_value = Mock()
        conn_error = requests.exceptions.ConnectionError('connection refused')
        session.send.side_effect = conn_error

        # The handler is called; retrieve continues (returns res which will fail
        # because session.send raised, but the handler swallows it).
        # In the real code, the handler typically raises a different exception.
        # Here the handler doesn't raise, so code falls through to res.text
        # which will fail. Let's have the handler raise to mimic real usage.
        handler.side_effect = RuntimeError('handled')

        with self.assertRaises(RuntimeError):
            client.retrieve(session, 'GET', 'path')

        handler.assert_called_once_with(client, conn_error)

    @patch('sap.http.client.requests.Request')
    def test_retrieve_default_params_merged(self, mock_request_cls):
        client = self._make_client(client='100')
        session = Mock()
        session.prepare_request.return_value = Mock()
        session.send.return_value = Mock(text='')

        client.retrieve(session, 'GET', 'path', params={'extra': 'val'})

        kwargs = mock_request_cls.call_args[1]
        self.assertIn('sap-client', kwargs['params'])
        self.assertEqual(kwargs['params']['sap-client'], '100')
        self.assertEqual(kwargs['params']['extra'], 'val')

    @patch('sap.http.client.requests.Request')
    def test_retrieve_no_extra_params(self, mock_request_cls):
        client = self._make_client(client='100')
        session = Mock()
        session.prepare_request.return_value = Mock()
        session.send.return_value = Mock(text='')

        client.retrieve(session, 'GET', 'path')

        kwargs = mock_request_cls.call_args[1]
        self.assertEqual(kwargs['params'], {'sap-client': '100'})


class TestHTTPClientExecuteWithSession(unittest.TestCase):

    def _make_client(self, **kwargs):
        defaults = dict(host='example.com', user='SAP*', password='pass', client='100')
        defaults.update(kwargs)
        return HTTPClient(**defaults)

    def test_returns_response_on_success(self):
        client = self._make_client()
        session = Mock()

        response = Mock()
        response.status_code = 200
        client.retrieve = Mock(return_value=(Mock(), response))

        result = client.execute_with_session(session, 'GET', 'path')

        self.assertIs(result, response)

    def test_calls_retrieve_with_all_params(self):
        client = self._make_client()
        session = Mock()

        response = Mock()
        response.status_code = 200
        client.retrieve = Mock(return_value=(Mock(), response))

        client.execute_with_session(session, 'POST', 'path',
                                    params={'p': '1'}, headers={'h': 'v'}, body='data')

        client.retrieve.assert_called_once_with(
            session, 'POST', 'path',
            params={'p': '1'}, headers={'h': 'v'}, body='data'
        )

    def test_error_handler_called_on_error_status(self):
        client = self._make_client()
        session = Mock()

        req = Mock()
        response = Mock()
        response.status_code = 500
        client.retrieve = Mock(return_value=(req, response))

        with self.assertRaises(HTTPRequestError):
            client.execute_with_session(session, 'GET', 'path')

    def test_unauthorized_on_401(self):
        client = self._make_client()
        session = Mock()

        req = Mock()
        response = Mock()
        response.status_code = 401
        client.retrieve = Mock(return_value=(req, response))

        with self.assertRaises(UnauthorizedError):
            client.execute_with_session(session, 'GET', 'path')

    def test_csrf_refetch_on_403_without_fetch_header(self):
        client = self._make_client(login_method='HEAD', login_path='login')
        session = MagicMock()
        session.headers = {'x-csrf-token': 'old-token'}

        req_first = Mock()
        res_403 = Mock()
        res_403.status_code = 403

        login_req = Mock()
        login_res = Mock()
        login_res.status_code = 200
        login_res.headers = {'x-csrf-token': 'new-token'}

        req_retry = Mock()
        res_ok = Mock()
        res_ok.status_code = 200

        call_count = [0]
        retrieve_returns = [
            (req_first, res_403),
            (login_req, login_res),
            (req_retry, res_ok),
        ]

        def fake_retrieve(sess, method, path, params=None, headers=None, body=None):
            idx = call_count[0]
            call_count[0] += 1
            return retrieve_returns[idx]

        client.retrieve = fake_retrieve

        result = client.execute_with_session(session, 'GET', 'path')

        self.assertIs(result, res_ok)
        self.assertEqual(session.headers['x-csrf-token'], 'new-token')

    def test_no_csrf_refetch_when_header_is_fetch(self):
        """403 with x-csrf-token: Fetch header should NOT trigger refetch."""
        client = self._make_client()
        session = Mock()

        req = Mock()
        response = Mock()
        response.status_code = 403
        client.retrieve = Mock(return_value=(req, response))

        with self.assertRaises(HTTPRequestError):
            client.execute_with_session(session, 'GET', 'path',
                                        headers={'x-csrf-token': 'Fetch'})

        # retrieve should be called exactly once - no refetch
        client.retrieve.assert_called_once()

    def test_no_csrf_refetch_for_non_403_errors(self):
        """Non-403 errors should go straight to error handler."""
        client = self._make_client()
        session = Mock()

        req = Mock()
        response = Mock()
        response.status_code = 500
        client.retrieve = Mock(return_value=(req, response))

        with self.assertRaises(HTTPRequestError):
            client.execute_with_session(session, 'GET', 'path')

        client.retrieve.assert_called_once()

    def test_no_error_on_status_below_400(self):
        client = self._make_client()
        session = Mock()

        for status in [200, 201, 204, 301, 302, 399]:
            response = Mock()
            response.status_code = status
            client.retrieve = Mock(return_value=(Mock(), response))

            result = client.execute_with_session(session, 'GET', 'path')
            self.assertIs(result, response)

    def test_csrf_refetch_with_empty_headers(self):
        """403 with no headers at all should trigger CSRF refetch."""
        client = self._make_client(login_method='HEAD', login_path='login')
        session = MagicMock()
        session.headers = {}

        res_403 = Mock()
        res_403.status_code = 403

        login_res = Mock()
        login_res.status_code = 200
        login_res.headers = {'x-csrf-token': 'new-token'}

        res_ok = Mock()
        res_ok.status_code = 200

        call_count = [0]
        retrieve_returns = [
            (Mock(), res_403),
            (Mock(), login_res),
            (Mock(), res_ok),
        ]

        def fake_retrieve(sess, method, path, params=None, headers=None, body=None):
            idx = call_count[0]
            call_count[0] += 1
            return retrieve_returns[idx]

        client.retrieve = fake_retrieve

        result = client.execute_with_session(session, 'GET', 'path', headers=None)

        self.assertIs(result, res_ok)


class TestHTTPClientBuildSession(unittest.TestCase):

    def _make_client(self, **kwargs):
        defaults = dict(host='example.com', user='SAP*', password='pass', client='100',
                        login_path='login', login_method='HEAD')
        defaults.update(kwargs)
        return HTTPClient(**defaults)

    @patch('sap.http.client.requests.Session')
    def test_build_session_default_verify(self, mock_session_cls):
        client = self._make_client()

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {'x-csrf-token': 'token123'}
        client.execute_with_session = Mock(return_value=login_response)

        session, response = client.build_session()

        self.assertIs(session, mock_session)
        self.assertIs(response, login_response)
        # verify not explicitly set when no ssl_server_cert and ssl_verify is not False
        mock_session_cls.assert_called_once()

    @patch('sap.http.client.requests.Session')
    def test_build_session_with_ssl_server_cert(self, mock_session_cls):
        client = self._make_client(ssl_server_cert='/path/to/ca.pem')

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {'x-csrf-token': 'token123'}
        client.execute_with_session = Mock(return_value=login_response)

        session, response = client.build_session()

        self.assertEqual(mock_session.verify, '/path/to/ca.pem')

    @patch('sap.http.client.requests.Session')
    def test_build_session_with_verify_false(self, mock_session_cls):
        client = self._make_client(verify=False)

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {'x-csrf-token': 'token123'}
        client.execute_with_session = Mock(return_value=login_response)

        session, response = client.build_session()

        self.assertFalse(mock_session.verify)

    @patch('sap.http.client.requests.Session')
    def test_build_session_ssl_server_cert_precedence_over_verify_false(self, mock_session_cls):
        client = self._make_client(verify=False, ssl_server_cert='/path/to/ca.pem')

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {'x-csrf-token': 'token123'}
        client.execute_with_session = Mock(return_value=login_response)

        session, response = client.build_session()

        self.assertEqual(mock_session.verify, '/path/to/ca.pem')

    @patch('sap.http.client.requests.Session')
    def test_build_session_sets_csrf_token(self, mock_session_cls):
        client = self._make_client()

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {'x-csrf-token': 'the-csrf-token'}
        client.execute_with_session = Mock(return_value=login_response)

        session, response = client.build_session()

        self.assertEqual(mock_session.headers['x-csrf-token'], 'the-csrf-token')

    @patch('sap.http.client.requests.Session')
    def test_build_session_no_csrf_token_in_response(self, mock_session_cls):
        client = self._make_client()

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {}
        client.execute_with_session = Mock(return_value=login_response)

        session, response = client.build_session()

        self.assertNotIn('x-csrf-token', mock_session.headers)

    @patch('sap.http.client.requests.Session')
    def test_build_session_sets_auth(self, mock_session_cls):
        client = self._make_client()

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {'x-csrf-token': 'token'}
        client.execute_with_session = Mock(return_value=login_response)

        session, _ = client.build_session()

        self.assertEqual(mock_session.auth, client._auth)

    @patch('sap.http.client.requests.Session')
    def test_build_session_login_request(self, mock_session_cls):
        client = self._make_client(login_path='my/login', login_method='GET')

        mock_session = MagicMock()
        mock_session.headers = {}
        mock_session_cls.return_value = mock_session

        login_response = Mock()
        login_response.status_code = 200
        login_response.headers = {'x-csrf-token': 'token'}
        client.execute_with_session = Mock(return_value=login_response)

        client.build_session()

        client.execute_with_session.assert_called_once_with(
            mock_session, 'GET', 'my/login', headers={'x-csrf-token': 'Fetch'}
        )


if __name__ == '__main__':
    unittest.main()
