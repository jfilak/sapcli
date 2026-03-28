#!/usr/bin/env python3

from functools import partial

import unittest
from requests.exceptions import ConnectionError, ReadTimeout
from unittest.mock import Mock, patch

from sap.rest.connection import Connection
from sap.rest.errors import UnauthorizedError, GCTSConnectionError, TimedOutRequestError


def stub_retrieve(response, session, method, url, params=None, headers=None, body=None):
    req = Mock()
    req.method = method
    req.url = url
    req.params = params
    req.headers = headers
    req.body = body

    return (req, response)


class TestConnectionExecute(unittest.TestCase):

    def setUp(self):
        icf_path = '/foo'
        login_path = '/bar'
        host = 'books.fr'
        client = '69'
        user = 'Arsan'
        password = 'Emmanuelle'

        self.conn = Connection(icf_path, login_path, host, client, user, password)

    @patch('sap.rest.connection.Connection._retrieve')
    def test_unauthorized_error(self, fake_retrieve):
        icf_path = '/foo'
        login_path = '/bar'
        host = 'books.fr'
        client = '69'
        user = 'Arsan'
        password = 'Emmanuelle'
        method = 'GET'
        url = '/all'

        conn = Connection(icf_path, login_path, host, client, user, password)

        res = Mock()
        res.status_code = 401
        fake_retrieve.side_effect = partial(stub_retrieve, res)

        with self.assertRaises(UnauthorizedError) as caught:
            conn._execute_with_session(conn._session, method, url)

        self.assertEqual(str(caught.exception), f'Authorization for the user "{user}" has failed: {method} {url}')

    @patch('sap.rest.connection.requests.Request')
    def test_protocol_error(self, _):
        session = Mock()
        session.send.side_effect = ConnectionError('Remote end closed connection without response')

        method = 'GET'
        url = '/all'

        with self.assertRaises(GCTSConnectionError) as cm:
            self.conn._retrieve(session, method, url)

        self.assertEqual(str(cm.exception),
                         f'GCTS connection error: [HOST:"{self.conn._host}", PORT:"443", '
                         'SSL:"True"] Error: Remote end closed connection without response')

    @patch('sap.rest.connection.requests.Request')
    def test_dns_error(self, _):
        session = Mock()
        session.send.side_effect = ConnectionError('[Errno -5] Dummy name resolution error')

        method = 'GET'
        url = '/all'

        with self.assertRaises(GCTSConnectionError) as cm:
            self.conn._retrieve(session, method, url)

        self.assertEqual(str(cm.exception),
                         f'GCTS connection error: [HOST:"{self.conn._host}", PORT:"443", '
                         'SSL:"True"] Error: Name resolution error. Check the HOST configuration.')

    @patch('sap.rest.connection.requests.Request')
    def test_connection_error(self, _):
        session = Mock()
        session.send.side_effect = ConnectionError('[Errno 111] Dummy connection error')

        method = 'GET'
        url = '/all'

        with self.assertRaises(GCTSConnectionError) as cm:
            self.conn._retrieve(session, method, url)

        self.assertEqual(str(cm.exception),
                         f'GCTS connection error: [HOST:"{self.conn._host}", PORT:"443", '
                         'SSL:"True"] Error: Cannot connect to the system. Check the HOST and PORT configuration.')

    @patch('sap.rest.connection.requests.Request')
    def test_read_timeout(self, _):
        session = Mock()
        session.send.side_effect = ReadTimeout('HTTPSConnectionPool read timed out')

        method = 'GET'
        url = '/all'

        with self.assertRaises(TimedOutRequestError) as cm:
            self.conn._retrieve(session, method, url)

        self.assertIn('took more than', str(cm.exception))


class TestConnectionSSLServerCert(unittest.TestCase):
    """Test ssl_server_cert parameter wiring in REST Connection."""

    def test_ssl_server_cert_default_none(self):
        conn = Connection('/foo', '/bar', 'host', '100', 'user', 'pass')
        self.assertIsNone(conn._ssl_server_cert)

    def test_ssl_server_cert_stored(self):
        conn = Connection('/foo', '/bar', 'host', '100', 'user', 'pass',
                          ssl_server_cert='/path/to/ca.pem')
        self.assertEqual(conn._ssl_server_cert, '/path/to/ca.pem')

    @patch('sap.rest.connection.Connection._execute_with_session')
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

    @patch('sap.rest.connection.Connection._execute_with_session')
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
