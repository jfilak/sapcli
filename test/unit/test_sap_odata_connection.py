'''Odata connection classes tests'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
from unittest.mock import Mock, patch
from requests.exceptions import ConnectTimeout, ReadTimeout

from sap.odata.connection import Connection
from sap.http.errors import (
    HTTPRequestError,
    UnauthorizedError,
    TimedOutRequestError,
)


class TestConnectionInit(unittest.TestCase):

    @patch('sap.odata.connection.pyodata.Client')
    @patch('sap.http.client.HTTPClient.build_session')
    def test_default_init(self, mock_build_session, mock_pyodata):
        session = Mock()
        mock_build_session.return_value = (session, Mock())

        con = Connection('SERVICE', 'HOST', 'PORT', 'CLIENT', 'USER', 'PASSWORD', True, True)

        self.assertEqual(con._http_client.host, 'HOST')
        self.assertEqual(con._http_client.port, 'PORT')
        self.assertEqual(con._http_client.user, 'USER')
        self.assertEqual(con._http_client.client, 'CLIENT')
        self.assertTrue(con._http_client.ssl)
        self.assertFalse(con._http_client.saml2)
        self.assertEqual(con._http_client.login_path, 'sap/opu/odata/SERVICE')
        self.assertEqual(con._http_client.login_method, 'HEAD')
        self.assertTrue(con._http_client.ssl_verify)

        url = 'https://HOST:PORT/sap/opu/odata/SERVICE'
        mock_pyodata.assert_called_once_with(url, session)
        self.assertIs(con.client, mock_pyodata.return_value)

    @patch('sap.odata.connection.pyodata.Client')
    @patch('sap.http.client.HTTPClient.build_session')
    def test_default_https_port(self, mock_build_session, mock_pyodata):
        session = Mock()
        mock_build_session.return_value = (session, Mock())

        Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', True, True)

        mock_pyodata.assert_called_once_with('https://HOST:443/sap/opu/odata/SERVICE', session)

    @patch('sap.odata.connection.pyodata.Client')
    @patch('sap.http.client.HTTPClient.build_session')
    def test_default_http_port(self, mock_build_session, mock_pyodata):
        session = Mock()
        mock_build_session.return_value = (session, Mock())

        Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        mock_pyodata.assert_called_once_with('http://HOST:80/sap/opu/odata/SERVICE', session)


class TestConnectionInitErrors(unittest.TestCase):

    @patch('sap.odata.connection.pyodata.Client')
    @patch('requests.Session', return_value=Mock())
    def test_init_timeout(self, mock_session_cls, mock_pyodata):
        session = mock_session_cls.return_value
        session.send.side_effect = ConnectTimeout()

        with self.assertRaises(TimedOutRequestError):
            Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        mock_pyodata.assert_not_called()

    @patch('sap.odata.connection.pyodata.Client')
    @patch('requests.Session', return_value=Mock())
    def test_init_read_timeout(self, mock_session_cls, mock_pyodata):
        session = mock_session_cls.return_value
        session.send.side_effect = ReadTimeout()

        with self.assertRaises(TimedOutRequestError):
            Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        mock_pyodata.assert_not_called()

    @patch('sap.odata.connection.pyodata.Client')
    @patch('requests.Session', return_value=Mock())
    def test_init_unauthorized(self, mock_session_cls, mock_pyodata):
        response = Mock()
        response.status_code = 401
        session = mock_session_cls.return_value
        session.send.return_value = response

        with self.assertRaises(UnauthorizedError):
            Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        mock_pyodata.assert_not_called()

    @patch('sap.odata.connection.pyodata.Client')
    @patch('requests.Session', return_value=Mock())
    def test_init_http_error(self, mock_session_cls, mock_pyodata):
        response = Mock()
        response.status_code = 500
        session = mock_session_cls.return_value
        session.send.return_value = response

        with self.assertRaises(HTTPRequestError):
            Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        mock_pyodata.assert_not_called()


class TestConnectionSSLServerCert(unittest.TestCase):
    """Test ssl_server_cert parameter wiring in OData Connection."""

    @patch('sap.odata.connection.pyodata.Client')
    @patch('sap.http.client.HTTPClient.build_session')
    def test_ssl_server_cert_default_none(self, mock_build_session, mock_pyodata):
        mock_build_session.return_value = (Mock(), Mock())

        con = Connection('SERVICE', 'HOST', 'PORT', 'CLIENT', 'USER', 'PASSWORD', True, True)

        self.assertIsNone(con._http_client.ssl_server_cert)

    @patch('sap.odata.connection.pyodata.Client')
    @patch('sap.http.client.HTTPClient.build_session')
    def test_ssl_server_cert_forwarded(self, mock_build_session, mock_pyodata):
        mock_build_session.return_value = (Mock(), Mock())

        con = Connection('SERVICE', 'HOST', 'PORT', 'CLIENT', 'USER', 'PASSWORD',
                         True, True, ssl_server_cert='/path/to/ca.pem')

        self.assertEqual(con._http_client.ssl_server_cert, '/path/to/ca.pem')


if __name__ == '__main__':
    unittest.main()
