#!/usr/bin/env python3

from functools import partial

import unittest
from requests.exceptions import ConnectionError, ReadTimeout
from unittest.mock import Mock, patch

from sap.rest.connection import Connection
from sap.http import HTTPRequestError
from sap.rest.errors import UnauthorizedError, GCTSConnectionError, TimedOutRequestError, UnexpectedResponseContent


def stub_retrieve(response, session, method, path, params=None, headers=None, body=None):
    req = Mock()
    req.method = method
    req.url = path
    req.params = params
    req.headers = headers
    req.body = body

    return (req, response)


class TestConnectionExecute(unittest.TestCase):

    def setUp(self):
        self.icf_path = '/foo'
        login_path = '/bar'
        host = 'books.fr'
        client = '69'
        self.user = 'Arsan'
        password = 'Emmanuelle'

        self.conn = Connection(self.icf_path, login_path, host, client, self.user, password)

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.HTTPClient.retrieve')
    def test_unauthorized_error(self, fake_retrieve, mock_get_session):
        mock_get_session.return_value = Mock()

        res = Mock()
        res.status_code = 401
        fake_retrieve.side_effect = partial(stub_retrieve, res)

        method = 'GET'
        uri_path = 'all'

        with self.assertRaises(UnauthorizedError) as caught:
            self.conn.execute(method, uri_path)

        expected_path = f'{self.icf_path}/{uri_path}'
        self.assertEqual(str(caught.exception),
                         f'Authorization for the user "{self.user}" has failed: {method} {expected_path}')

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.requests.Request')
    def test_protocol_error(self, _, mock_get_session):
        session = Mock()
        session.send.side_effect = ConnectionError('Remote end closed connection without response')
        mock_get_session.return_value = session

        with self.assertRaises(GCTSConnectionError) as cm:
            self.conn.execute('GET', 'all')

        self.assertEqual(str(cm.exception),
                         f'GCTS connection error: [HOST:"{self.conn._http_client.host}", PORT:"443", '
                         'SSL:"True"] Error: Remote end closed connection without response')

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.requests.Request')
    def test_dns_error(self, _, mock_get_session):
        session = Mock()
        session.send.side_effect = ConnectionError('[Errno -5] Dummy name resolution error')
        mock_get_session.return_value = session

        with self.assertRaises(GCTSConnectionError) as cm:
            self.conn.execute('GET', 'all')

        self.assertEqual(str(cm.exception),
                         f'GCTS connection error: [HOST:"{self.conn._http_client.host}", PORT:"443", '
                         'SSL:"True"] Error: Name resolution error. Check the HOST configuration.')

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.requests.Request')
    def test_connection_error(self, _, mock_get_session):
        session = Mock()
        session.send.side_effect = ConnectionError('[Errno 111] Dummy connection error')
        mock_get_session.return_value = session

        with self.assertRaises(GCTSConnectionError) as cm:
            self.conn.execute('GET', 'all')

        self.assertEqual(str(cm.exception),
                         f'GCTS connection error: [HOST:"{self.conn._http_client.host}", PORT:"443", '
                         'SSL:"True"] Error: Cannot connect to the system. Check the HOST and PORT configuration.')

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.requests.Request')
    def test_read_timeout(self, _, mock_get_session):
        session = Mock()
        session.send.side_effect = ReadTimeout('HTTPSConnectionPool read timed out')
        mock_get_session.return_value = session

        with self.assertRaises(TimedOutRequestError) as cm:
            self.conn.execute('GET', 'all')

        self.assertIn('took more than', str(cm.exception))

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.HTTPClient.execute_with_session')
    def test_execute_no_optional_args(self, mock_exec, mock_get_session):
        """No accept, content_type, or headers → headers=None passed to execute_with_session."""
        mock_get_session.return_value = Mock()
        mock_exec.return_value = Mock()

        self.conn.execute('GET', 'all')

        self.assertIsNone(mock_exec.call_args.kwargs['headers'])

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.HTTPClient.execute_with_session')
    def test_execute_accept_string(self, mock_exec, mock_get_session):
        """accept as string → Accept header set and response Content-Type validated."""
        mock_get_session.return_value = Mock()
        response = Mock()
        response.headers = {'Content-Type': 'application/json'}
        mock_exec.return_value = response

        self.conn.execute('GET', 'all', accept='application/json')

        self.assertEqual(mock_exec.call_args.kwargs['headers'], {'Accept': 'application/json'})

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.HTTPClient.execute_with_session')
    def test_execute_accept_list(self, mock_exec, mock_get_session):
        """accept as list → Accept header is comma-joined and response Content-Type validated."""
        mock_get_session.return_value = Mock()
        response = Mock()
        response.headers = {'Content-Type': 'text/xml'}
        mock_exec.return_value = response

        self.conn.execute('GET', 'all', accept=['application/json', 'text/xml'])

        self.assertEqual(mock_exec.call_args.kwargs['headers'], {'Accept': 'application/json, text/xml'})

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.HTTPClient.execute_with_session')
    def test_execute_content_type(self, mock_exec, mock_get_session):
        """content_type set → Content-Type header set; no response Content-Type validation."""
        mock_get_session.return_value = Mock()
        mock_exec.return_value = Mock()

        self.conn.execute('POST', 'all', content_type='application/json')

        self.assertEqual(mock_exec.call_args.kwargs['headers'], {'Content-Type': 'application/json'})

    @patch('sap.http.client.HTTPClient.build_session')
    def test_get_session_propagates_404(self, mock_build_session):
        req = Mock()
        res = Mock()
        res.status_code = 404
        mock_build_session.side_effect = HTTPRequestError(req, res)

        with self.assertRaises(HTTPRequestError):
            self.conn._get_session()

    @patch('sap.rest.connection.Connection._get_session')
    @patch('sap.http.client.HTTPClient.execute_with_session')
    def test_execute_accept_content_type_mismatch(self, mock_exec, mock_get_session):
        """Response Content-Type not in accept → UnexpectedResponseContent raised."""
        mock_get_session.return_value = Mock()
        response = Mock()
        response.headers = {'Content-Type': 'text/html'}
        mock_exec.return_value = response

        with self.assertRaises(UnexpectedResponseContent):
            self.conn.execute('GET', 'all', accept='application/json')


class TestConnectionPathJoining(unittest.TestCase):
    """Verify that path joining in __init__ and _build_url never produces double slashes."""

    # --- __init__: login_path = f'{icf_path}/{login_path}' ---

    def test_login_path_no_leading_slashes(self):
        conn = Connection('sap/bc/cts', 'system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._http_client.login_path, 'sap/bc/cts/system')

    def test_login_path_login_has_leading_slash(self):
        conn = Connection('sap/bc/cts', '/system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._http_client.login_path, 'sap/bc/cts/system')

    def test_login_path_icf_has_leading_slash(self):
        conn = Connection('/sap/bc/cts', 'system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._http_client.login_path, '/sap/bc/cts/system')

    def test_login_path_both_have_leading_slash(self):
        conn = Connection('/sap/bc/cts', '/system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._http_client.login_path, '/sap/bc/cts/system')

    # --- _build_url: f'{self._icf_path}/{uri_path}' ---

    def test_build_url_no_leading_slashes(self):
        conn = Connection('sap/bc/cts', 'system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._build_url('repository'), 'sap/bc/cts/repository')

    def test_build_url_uri_has_leading_slash(self):
        conn = Connection('sap/bc/cts', 'system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._build_url('/repository'), 'sap/bc/cts/repository')

    def test_build_url_icf_has_leading_slash(self):
        conn = Connection('/sap/bc/cts', 'system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._build_url('repository'), '/sap/bc/cts/repository')

    def test_build_url_both_have_leading_slash(self):
        conn = Connection('/sap/bc/cts', 'system', 'host', '100', 'user', 'pass')
        self.assertEqual(conn._build_url('/repository'), '/sap/bc/cts/repository')


class TestConnectionSSLServerCert(unittest.TestCase):
    """Test ssl_server_cert parameter wiring in REST Connection."""

    def test_ssl_server_cert_default_none(self):
        conn = Connection('/foo', '/bar', 'host', '100', 'user', 'pass')
        self.assertIsNone(conn._http_client.ssl_server_cert)

    def test_ssl_server_cert_stored(self):
        conn = Connection('/foo', '/bar', 'host', '100', 'user', 'pass',
                          ssl_server_cert='/path/to/ca.pem')
        self.assertEqual(conn._http_client.ssl_server_cert, '/path/to/ca.pem')

    @patch('sap.http.client.HTTPClient.execute_with_session')
    def test_ssl_server_cert_sets_session_verify(self, mock_exec):
        """When ssl_server_cert is set, session.verify is the cert path."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'x-csrf-token': 'token123'}
        mock_exec.return_value = mock_response

        conn = Connection('/foo', '/bar', 'host', '100', 'user', 'pass',
                          ssl_server_cert='/path/to/ca.pem')
        session = conn._get_session()
        self.assertEqual(session.verify, '/path/to/ca.pem')

    @patch('sap.http.client.HTTPClient.execute_with_session')
    def test_ssl_server_cert_takes_precedence_over_verify_false(self, mock_exec):
        """ssl_server_cert takes precedence over verify=False."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'x-csrf-token': 'token123'}
        mock_exec.return_value = mock_response

        conn = Connection('/foo', '/bar', 'host', '100', 'user', 'pass',
                          verify=False, ssl_server_cert='/path/to/ca.pem')
        session = conn._get_session()
        self.assertEqual(session.verify, '/path/to/ca.pem')
