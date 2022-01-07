from unittest.mock import Mock, patch

from sap.rfc.strust import SSLCertStorage, InvalidSSLStorage, PutCertificateError

import unittest
from unittest import mock
from mock import Connection


class TestSSLCertStorage(unittest.TestCase):

    def test_ctor(self):
        mock_connectionection = Mock()

        ssl_storage = SSLCertStorage(mock_connectionection, 'CTXT', 'APPL')

        self.assertIs(ssl_storage._connection, mock_connectionection)
        self.assertEqual(ssl_storage.identity['PSE_CONTEXT'], 'CTXT')
        self.assertEqual(ssl_storage.identity['PSE_APPLIC'], 'APPL')

    def test_repr(self):
        mock_connectionection = Mock()

        ssl_storage = SSLCertStorage(mock_connectionection, 'REPR', 'TEST')
        self.assertEquals(repr(ssl_storage), 'SSL Storage REPR/TEST')

    def test_str(self):
        conn = Connection()

        ssl_storage = SSLCertStorage(conn, 'STR', 'TEST')
        self.assertEquals(str(ssl_storage), 'SSL Storage STR/TEST')

    def test_exists_raises(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': [{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'RAISE', 'TEST')

        with self.assertRaises(InvalidSSLStorage) as cm:
            ssl_storage.exists()

        self.assertEqual(mock_connectionection.call.call_args_list,
                         [mock.call('SSFR_PSE_CHECK',
                                    IS_STRUST_IDENTITY={'PSE_CONTEXT': 'RAISE',
                                                        'PSE_APPLIC': 'TEST'})])

        self.assertEqual(str(cm.exception),
                         'The SSL Storage RAISE/TEST is broken: Invalid storage')

    def test_exists_raises_if_not_ret(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': []}

        ssl_storage = SSLCertStorage(mock_connectionection, 'RAISE', 'TEST')

        with self.assertRaises(InvalidSSLStorage) as cm:
            ssl_storage.exists()

        self.assertEqual(mock_connectionection.call.call_args_list,
                         [mock.call('SSFR_PSE_CHECK',
                                    IS_STRUST_IDENTITY={'PSE_CONTEXT': 'RAISE',
                                                        'PSE_APPLIC': 'TEST'})])

        self.assertEqual(str(cm.exception),
                         'Received no response from the server - check STRUST manually.')


    def test_exists_yes(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': [{'TYPE': 'S'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'NOTRAISE', 'TEST')
        self.assertTrue(ssl_storage.exists())

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PSE_CHECK',
                                     IS_STRUST_IDENTITY={'PSE_CONTEXT': 'NOTRAISE',
                                                         'PSE_APPLIC': 'TEST'})])

    def test_create_ok_default(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': []}

        ssl_storage = SSLCertStorage(mock_connectionection, 'NOTRAISE', 'TEST')
        ssl_storage.create()

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PSE_CREATE',
                                     IS_STRUST_IDENTITY={'PSE_CONTEXT': 'NOTRAISE',
                                                         'PSE_APPLIC': 'TEST'},
                                     IV_ALG='R',
                                     IV_KEYLEN=2048,
                                     IV_REPLACE_EXISTING_PSE='-'
                                    )
                           ])

    def test_create_ok_all_params(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': []}

        ssl_storage = SSLCertStorage(mock_connectionection, 'NOTRAISE', 'TEST')
        ssl_storage.create(alg='S', keylen=4096, replace=True, dn='ou=test')

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PSE_CREATE',
                                     IS_STRUST_IDENTITY={'PSE_CONTEXT': 'NOTRAISE',
                                                         'PSE_APPLIC': 'TEST'},
                                     IV_ALG='S',
                                     IV_KEYLEN=4096,
                                     IV_REPLACE_EXISTING_PSE='X',
                                     IV_DN='ou=test'
                                    )
                           ])

    def test_create_raises(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': [
            {'TYPE': 'E', 'MESSAGE': 'Invalid storage'}
        ]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'RAISE', 'TEST')

        with self.assertRaises(InvalidSSLStorage) as cm:
            ssl_storage.create()

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PSE_CREATE',
                                     IS_STRUST_IDENTITY={'PSE_CONTEXT': 'RAISE',
                                                           'PSE_APPLIC': 'TEST'},
                                     IV_ALG='R',
                                     IV_KEYLEN=2048,
                                     IV_REPLACE_EXISTING_PSE='-'
                                    )
                           ])

        self.assertEqual(str(cm.exception),
                         str([{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}])
                         )

    def test_put_certificate(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': []}

        ssl_storage = SSLCertStorage(mock_connectionection, 'PUTOK', 'TEST')

        result = ssl_storage.put_certificate('plain old data')

        self.assertEqual(result, 'OK')

        self.assertEqual(mock_connectionection.call.call_args_list,
                         [mock.call('SSFR_PUT_CERTIFICATE',
                                    IS_STRUST_IDENTITY={'PSE_CONTEXT': 'PUTOK',
                                                        'PSE_APPLIC': 'TEST'},
                                    IV_CERTIFICATE=u'plain old data')])

    def test_put_certificate_fail(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': [{'TYPE': 'E', 'MESSAGE': 'Put has failed'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'PUTERR', 'TEST')

        with self.assertRaises(PutCertificateError) as cm:
            ssl_storage.put_certificate('plain old data')

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PUT_CERTIFICATE',
                                     IS_STRUST_IDENTITY={'PSE_CONTEXT': 'PUTERR',
                                                         'PSE_APPLIC': 'TEST'},
                                     IV_CERTIFICATE=u'plain old data')])

        self.assertEquals(str(cm.exception),
                          'Failed to put the CERT to the SSL Storage PUTERR/TEST: '
                          'Put has failed')

    def test_put_certificate_fail_and_return_msg(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': [{'TYPE': 'E', 'NUMBER': '522', 'MESSAGE': 'Put has failed'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'PUTERR', 'TEST')

        result = ssl_storage.put_certificate('plain old data')

        self.assertEqual(result,
                         'SSFR_PUT_CERTIFICATE reported Error 522 - ' \
                         'probably already exists (check manually): Put has failed'
                         )

        self.assertEqual(mock_connectionection.call.call_args_list,
                         [mock.call('SSFR_PUT_CERTIFICATE',
                                    IS_STRUST_IDENTITY={'PSE_CONTEXT': 'PUTERR',
                                                        'PSE_APPLIC': 'TEST'},
                                    IV_CERTIFICATE=u'plain old data')])

    def test_parse_certificate(self):
        mock_connection = Mock()
        mock_connection.call.return_value = {'EV_SUBJECT': 'cert subject'}

        ssl_storage = SSLCertStorage(mock_connection, 'PUTOK', 'TEST')

        result = ssl_storage.parse_certificate(b'binary cert data')

        self.assertEqual(mock_connection.call.call_args_list,
                         [mock.call('SSFR_PARSE_CERTIFICATE',
                                    IV_CERTIFICATE=b'binary cert data')])

        self.assertEqual(result, {'EV_SUBJECT': 'cert subject'})

if __name__ == '__main__':
    unittest.main()
