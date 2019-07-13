#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

import sap.adt
import sap.adt.errors

from fixtures_adt import ERROR_XML_PACKAGE_ALREADY_EXISTS

class TestADTConnection(unittest.TestCase):
    """Connection(host, client, user, password, port=None, ssl=True)"""

    def test_adt_connection_init_default(self):
        connection = sap.adt.Connection('localhost', '357', 'anzeiger', 'password')

        self.assertEqual(connection.user, 'anzeiger')
        self.assertEqual(connection.uri, 'sap/bc/adt')
        self.assertEqual(connection._base_url, 'https://localhost:443/sap/bc/adt')
        self.assertEqual(connection._query_args, 'sap-client=357&saml2=disabled')

    def test_adt_connection_init_no_ssl(self):
        connection = sap.adt.Connection('localhost', '357', 'anzeiger', 'password', ssl=False)

        self.assertEqual(connection._base_url, 'http://localhost:80/sap/bc/adt')

    def test_adt_connection_init_ssl_own_port(self):
        connection = sap.adt.Connection('localhost', '357', 'anzeiger', 'password', port=44300)

        self.assertEqual(connection._base_url, 'https://localhost:44300/sap/bc/adt')

    def test_adt_connection_init_no_ssl_own_port(self):
        connection = sap.adt.Connection('localhost', '357', 'anzeiger', 'password', ssl=False, port=8000)

        self.assertEqual(connection._base_url, 'http://localhost:8000/sap/bc/adt')

    def test_handle_http_error_adt_exception(self):
        req = Mock()

        res = Mock()
        res.headers = {'content-type': 'application/xml'}
        res.text = ERROR_XML_PACKAGE_ALREADY_EXISTS

        with self.assertRaises(sap.adt.errors.ADTError):
            sap.adt.Connection._handle_http_error(req, res)

    def test_handle_http_error_random_xml(self):
        req = Mock()

        res = Mock()
        res.headers = {'content-type': 'application/xml'}
        res.text = '<?xml version="1.0" encoding="utf-8"><error>random failure</error>'

        with self.assertRaises(sap.adt.errors.HTTPRequestError):
            sap.adt.Connection._handle_http_error(req, res)

    def test_handle_http_error_plain_text(self):
        req = Mock()

        res = Mock()
        res.headers = {'content-type': 'plain/text'}
        res.text = 'arbitrary crash'

        with self.assertRaises(sap.adt.errors.HTTPRequestError):
            sap.adt.Connection._handle_http_error(req, res)


if __name__ == '__main__':
    unittest.main()
