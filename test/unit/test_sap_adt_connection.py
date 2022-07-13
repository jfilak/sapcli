#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch

import sap.adt
import sap.adt.errors

from mock import Request, Response, ConnectionViaHTTP as Connection

from fixtures_adt import ERROR_XML_PACKAGE_ALREADY_EXISTS, DISCOVERY_ADT_XML


class TestADTConnection(unittest.TestCase):
    """Connection(host, client, user, password, port=None, ssl=True)"""

    def setUp(self):
        self.connection = sap.adt.ConnectionViaHTTP('example.host.org', '123',
                                                    'SAP*', 'PASS')

    def test_adt_connection_init_default(self):
        connection = sap.adt.ConnectionViaHTTP('localhost', '357', 'anzeiger',
                                               'password')

        self.assertEqual(connection.user, 'anzeiger')
        self.assertEqual(connection.uri, 'sap/bc/adt')
        self.assertEqual(connection._base_url, 'https://localhost:443/sap/bc/adt')
        self.assertEqual(connection._query_args, 'sap-client=357&saml2=disabled')

    def test_adt_connection_init_no_ssl(self):
        connection = sap.adt.ConnectionViaHTTP('localhost',
                                               '357',
                                               'anzeiger',
                                               'password',
                                               ssl=False)

        self.assertEqual(connection._base_url, 'http://localhost:80/sap/bc/adt')

    def test_adt_connection_init_ssl_own_port(self):
        connection = sap.adt.ConnectionViaHTTP('localhost',
                                               '357',
                                               'anzeiger',
                                               'password',
                                               port=44300)

        self.assertEqual(connection._base_url, 'https://localhost:44300/sap/bc/adt')

    def test_adt_connection_init_no_ssl_own_port(self):
        connection = sap.adt.ConnectionViaHTTP('localhost',
                                               '357',
                                               'anzeiger',
                                               'password',
                                               ssl=False,
                                               port=8000)

        self.assertEqual(connection._base_url, 'http://localhost:8000/sap/bc/adt')

    def test_handle_http_error_adt_exception(self):
        req = Mock()

        res = Mock()
        res.status_code = 500
        res.headers = {'content-type': 'application/xml'}
        res.text = ERROR_XML_PACKAGE_ALREADY_EXISTS

        with self.assertRaises(sap.adt.errors.ADTError):
            self.connection._handle_http_error(req, res)

    def test_handle_http_error_random_xml(self):
        req = Mock()

        res = Mock()
        res.status_code = 500
        res.headers = {'content-type': 'application/xml'}
        res.text = '<?xml version="1.0" encoding="utf-8"><error>random failure</error>'

        with self.assertRaises(sap.rest.errors.HTTPRequestError):
            self.connection._handle_http_error(req, res)

    def test_handle_http_error_plain_text(self):
        req = Mock()

        res = Mock()
        res.status_code = 500
        res.headers = {'content-type': 'plain/text'}
        res.text = 'arbitrary crash'

        with self.assertRaises(sap.rest.errors.HTTPRequestError):
            self.connection._handle_http_error(req, res)

    def test_handle_http_error_unauthorized(self):
        req = Mock()

        res = Mock()
        res.status_code = 401
        res.headers = {'content-type': 'plain/text'}
        res.text = 'arbitrary crash'

        with self.assertRaises(sap.rest.errors.UnauthorizedError):
            self.connection._handle_http_error(req, res)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_content_type_no_headers(self, mock_exec, mock_session, mock_adt_url):
        self.connection.execute('GET', 'url', content_type='application/xml')

        mock_exec.assert_called_once_with('session', 'GET', 'url',
                                          params=None,
                                          headers={'Content-Type': 'application/xml'},
                                          body=None)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_content_type_with_headers(self, mock_exec, mock_session, mock_adt_url):
        self.connection.execute('GET', 'example',
                                headers={'Content-Type': 'text/plain'},
                                content_type='application/xml')

        mock_exec.assert_called_once_with('session', 'GET', 'url',
                                          params=None,
                                          headers={'Content-Type': 'application/xml'},
                                          body=None)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_accept_no_headers(self, mock_exec, mock_session, mock_adt_url):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/xml'}

        self.connection.execute('GET', 'example',
                                accept='application/xml')

        mock_exec.assert_called_once_with('session', 'GET', 'url',
                                          params=None,
                                          headers={'Accept': 'application/xml'},
                                          body=None)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_accept_with_headers(self, mock_exec, mock_session, mock_adt_url):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/xml'}

        self.connection.execute('GET', 'example',
                                headers={'Accept': 'text/plain'},
                                accept='application/xml')

        mock_exec.assert_called_once_with('session', 'GET', 'url',
                                          params=None,
                                          headers={'Accept': 'application/xml'},
                                          body=None)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_content_type_and_accept(self, mock_exec, mock_session, mock_adt_url):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/xml'}

        self.connection.execute('GET', 'example',
                                content_type='application/json',
                                accept='application/xml')

        mock_exec.assert_called_once_with('session', 'GET', 'url',
                                          params=None,
                                          headers={'Accept': 'application/xml',
                                                   'Content-Type': 'application/json'},
                                          body=None)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_content_type_and_accept_with_headers(self, mock_exec, mock_session, mock_adt_url):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/xml'}

        self.connection.execute('GET', 'example',
                                headers={'Accept': 'text/plain',
                                         'Content-Type': 'text/plain'},
                                content_type='application/json',
                                accept='application/xml')

        mock_exec.assert_called_once_with('session', 'GET', 'url',
                                          params=None,
                                          headers={'Accept': 'application/xml',
                                                   'Content-Type': 'application/json'},
                                          body=None)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_accept_list(self, mock_exec, mock_session, mock_adt_url):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/json'}

        self.connection.execute('GET', 'example',
                                accept=['application/xml', 'application/json'])

        mock_exec.assert_called_once_with('session', 'GET', 'url',
                                          params=None,
                                          headers={'Accept': 'application/xml, application/json'},
                                          body=None)

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_accept_unmatched_string(self, mock_exec, mock_session, mock_adt_url):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/json'}
        mock_exec.return_value.text = 'mock'

        with self.assertRaises(sap.rest.errors.UnexpectedResponseContent) as caught:
            self.connection.execute('GET', 'example',
                                    accept='application/xml')

        self.assertEqual(str(caught.exception),
                         'Unexpected Content-Type: application/json with: mock')

    @patch('sap.adt.core.ConnectionViaHTTP._build_adt_url', return_value='url')
    @patch('sap.adt.core.ConnectionViaHTTP._get_session',
           return_value='session')
    @patch('sap.adt.core.ConnectionViaHTTP._execute_with_session')
    def test_execute_accept_unmatched_list(self, mock_exec, mock_session, mock_adt_url):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'text/plain'}
        mock_exec.return_value.text = 'mock'

        with self.assertRaises(sap.rest.errors.UnexpectedResponseContent) as caught:
            self.connection.execute('GET', 'example',
                                    accept=['application/xml', 'application/json'])

        self.assertEqual(str(caught.exception),
                         'Unexpected Content-Type: text/plain with: mock')


    @patch('sap.adt.core.ConnectionViaHTTP.execute')
    def test_property_collection_init(self, mock_exec):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/xml'}
        mock_exec.return_value.text = DISCOVERY_ADT_XML

        self.assertIsNone(self.connection._collection_types)

        collection_types = self.connection.collection_types

        self.assertIsNotNone(collection_types)
        self.assertIsNotNone(self.connection._collection_types)


    def test_property_collection_cache(self):
        fake_value = Mock()
        self.connection._collection_types = fake_value
        collection_types = self.connection.collection_types
        self.assertEqual(collection_types, fake_value)


    @patch('sap.adt.core.ConnectionViaHTTP.execute')
    def test_parse_collection_accept(self, mock_exec):
        mock_exec.return_value = Mock()
        mock_exec.return_value.headers = {'Content-Type': 'application/xml'}
        mock_exec.return_value.text = DISCOVERY_ADT_XML

        results = {
            'bopf/businessobjects': ['application/vnd.sap.ap.adt.bopf.businessobjects.v4+xml',
                                     'application/vnd.sap.ap.adt.bopf.businessobjects.v2+xml',
                                     'application/vnd.sap.ap.adt.bopf.businessobjects.v3+xml'],
            'bopf/businessobjects/$validation': ['foo/mock+bopf/businessobjects/$validation'],
            'packages': ['application/vnd.sap.adt.packages.v1+xml'],
            'functions/groups': ['application/vnd.sap.adt.functions.groups.v2+xml'],
            'functions/groups/{groupname}/fmodules': ['application/vnd.sap.adt.functions.fmodules.v3+xml'],
            'functions/groups/{groupname}/includes': ['application/vnd.sap.adt.functions.fincludes.v2+xml'],
            'ddic/ddl/formatter/identifiers': ['text/plain'],
            'sadl/gw/mde': ['application/xml'],
            'quickfixes/evaluation': ['application/vnd.sap.adt.quickfixes.evaluation+xml;version=1.0.0'],
            'wdy/views': ['application/vnd.sap.adt.wdy.view+xml',
                          'application/vnd.sap.adt.wdy.view.v1+xml']
        }

        for basepath, exp_mimetypes in results.items():
            mimetype = f'foo/mock+{basepath}'

            act_types = self.connection.get_collection_types(basepath, mimetype)
            self.assertEqual(act_types, exp_mimetypes)

    @patch('sap.adt.core._get_collection_accepts')
    @patch('sap.adt.core.ConnectionViaHTTP._retrieve')
    def test_execute_session_new(self, fake_retrieve, fake_accepts):
        dummy_conn = Connection(responses=[
            Response(status_code=200, headers={'x-csrf-token': 'first'}),
            Response(status_code=200, headers={'x-csrf-token': 'second'}),
            Response(status_code=200, text='success')
        ])

        fake_retrieve.side_effect = dummy_conn._retrieve

        resp = self.connection.execute('GET', 'test')

        self.assertEqual(resp.text, 'success')

    @patch('sap.adt.core._get_collection_accepts')
    @patch('sap.adt.core.ConnectionViaHTTP._retrieve')
    def test_execute_session_new_forbidden(self, fake_retrieve, fake_accepts):
        dummy_conn = Connection(responses=[
            Response(text='''<?xml version="1.0" encoding="utf-8"?><mock type=test/>''',
                     status_code=403,
                     content_type='application/xml')
        ])

        fake_retrieve.side_effect = dummy_conn._retrieve

        with self.assertRaises(sap.rest.errors.HTTPRequestError):
            self.connection.execute('GET', 'test')

    @patch('sap.adt.core._get_collection_accepts')
    @patch('sap.adt.core.ConnectionViaHTTP._retrieve')
    def test_execute_session_refetch_csfr(self, fake_retrieve, fake_accepts):
        dummy_conn = Connection(responses=[
            Response(status_code=200, headers={'x-csrf-token': 'first'}),
            Response(status_code=200, headers={'x-csrf-token': 'second'}),
            Response(text='''<?xml version="1.0" encoding="utf-8"?><mock type=test/>''',
                     status_code=403,
                     content_type='application/xml'),
            Response(status_code=200, headers={'x-csrf-token': 'third'}),
            Response(status_code=200, text='success')
        ])

        fake_retrieve.side_effect = dummy_conn._retrieve

        resp = self.connection.execute('GET', 'test')
        self.assertEqual(resp.text, 'success')

    @patch('sap.adt.core._get_collection_accepts')
    @patch('sap.adt.core.ConnectionViaHTTP._retrieve')
    def test_execute_session_refetch_csfr_headers(self, fake_retrieve, fake_accepts):
        dummy_conn = Connection(responses=[
            Response(status_code=200, headers={'x-csrf-token': 'first'}),
            Response(status_code=200, headers={'x-csrf-token': 'second'}),
            Response(text='''<?xml version="1.0" encoding="utf-8"?><mock type=test/>''',
                     status_code=403,
                     content_type='application/xml'),
            Response(status_code=200, headers={'x-csrf-token': 'third'}),
            Response(status_code=200, text='success')
        ])

        fake_retrieve.side_effect = dummy_conn._retrieve

        resp = self.connection.execute('GET', 'test', headers={'awesome': 'fabulous'})
        self.assertEqual(resp.text, 'success')


if __name__ == '__main__':
    unittest.main()
