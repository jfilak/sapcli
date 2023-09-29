#!/usr/bin/env python3

from functools import partial

import unittest
from requests.exceptions import ConnectionError
from unittest.mock import Mock, patch

from sap.rest.connection import Connection
from sap.rest.errors import UnauthorizedError, GCTSConnectionError


def stub_retrieve(response, session, method, url, params=None, headers=None, body=None):
    req = Mock()
    req.method = method
    req.url = url
    req.params = params
    req.headers = headers
    req.body = body

    return (req, response)


class TestConnectionExecute(unittest.TestCase):

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
    def test_connection_error(self, _):
        session = Mock()
        session.send.side_effect = ConnectionError('Wrong creds')

        icf_path = '/foo'
        login_path = '/bar'
        host = 'books.fr'
        client = '69'
        user = 'Arsan'
        password = 'Emmanuelle'
        method = 'GET'
        url = '/all'

        conn = Connection(icf_path, login_path, host, client, user, password)

        with self.assertRaises(GCTSConnectionError) as cm:
            conn._retrieve(session, method, url)

        self.assertEqual(str(cm.exception), 'GCTS connection error: Wrong creds')
