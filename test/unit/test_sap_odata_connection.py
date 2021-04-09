'''Odata connection classes tests'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
from unittest.mock import Mock, patch
from requests.exceptions import ConnectTimeout
from sap.odata.connection import Connection
from sap.odata.errors import (
    HTTPRequestError,
    UnauthorizedError,
    TimedOutRequestError
)

class TestConnection(unittest.TestCase):

    @patch('pyodata.Client')
    @patch('requests.Request')
    @patch('requests.Session', return_value=Mock())
    def test_default_init(self, session_patch, request_patch, client_patch):
        response = Mock()
        response.status_code = 200
        response.headers.get = Mock(return_value='TOKEN')
        session = session_patch.return_value
        session.send = Mock(return_value=response)

        con = Connection('SERVICE', 'HOST', 'PORT', 'CLIENT', 'USER', 'PASSWORD', True, True)

        url = 'https://HOST:PORT/sap/opu/odata/SERVICE'
        self.assertEqual(con._base_url, url)
        self.assertEqual(con._query_args, 'sap-client=CLIENT&saml2=disabled')
        self.assertEqual(con._user, 'USER')
        self.assertEqual(con._auth.username, 'USER')
        self.assertEqual(con._auth.password, 'PASSWORD')

        self.assertEqual(session.verify, True)
        self.assertEqual(session.auth, ('USER', 'PASSWORD'))

        request_patch.assert_called_once_with('HEAD', url, headers={'x-csrf-token': 'fetch'})
        session.headers.update.assert_called_once_with({ 'x-csrf-token': 'TOKEN'})

        client_patch.assert_called_once_with(url, session)

    @patch('pyodata.Client')
    @patch('requests.Request')
    @patch('requests.Session', return_value=Mock())
    def test_default_https_port(self, session_patch, request_patch, client_patch):
        response = Mock()
        response.status_code = 200
        session = session_patch.return_value
        session.send = Mock(return_value=response)

        con = Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', True, True)

        self.assertEqual(con._base_url, 'https://HOST:443/sap/opu/odata/SERVICE')
        request_patch.assert_called_once()
        client_patch.assert_called_once()

    @patch('pyodata.Client')
    @patch('requests.Request')
    @patch('requests.Session', return_value=Mock())
    def test_default_http_port(self, session_patch, request_patch, client_patch):
        response = Mock()
        response.status_code = 200
        session = session_patch.return_value
        session.send = Mock(return_value=response)

        con = Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        self.assertEqual(con._base_url, 'http://HOST:80/sap/opu/odata/SERVICE')
        request_patch.assert_called_once()
        client_patch.assert_called_once()

    @patch('pyodata.Client')
    @patch('requests.Request')
    @patch('requests.Session', return_value=Mock())
    def test_init_timeout(self, session_patch, request_patch, client_patch):
        session = session_patch.return_value
        session.send = Mock(side_effect = ConnectTimeout())

        with self.assertRaises(TimedOutRequestError):
            Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        request_patch.assert_called_once()
        client_patch.assert_not_called()


    @patch('pyodata.Client')
    @patch('requests.Request')
    @patch('requests.Session', return_value=Mock())
    def test_init_unauthorized(self, session_patch, request_patch, client_patch):
        response = Mock()
        response.status_code = 401
        session = session_patch.return_value
        session.send = Mock(return_value=response)

        with self.assertRaises(UnauthorizedError):
            Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        request_patch.assert_called_once()
        client_patch.assert_not_called()

    @patch('pyodata.Client')
    @patch('requests.Request')
    @patch('requests.Session', return_value=Mock())
    def test_init_http_error(self, session_patch, request_patch, client_patch):
        response = Mock()
        response.status_code = 400
        session = session_patch.return_value
        session.send = Mock(return_value=response)

        with self.assertRaises(HTTPRequestError):
            Connection('SERVICE', 'HOST', None, 'CLIENT', 'USER', 'PASSWORD', False, True)

        request_patch.assert_called_once()
        client_patch.assert_not_called()
