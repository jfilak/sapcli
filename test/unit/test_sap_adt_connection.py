#!/usr/bin/env python3

import unittest

import sap.adt


class TestADTObject(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
