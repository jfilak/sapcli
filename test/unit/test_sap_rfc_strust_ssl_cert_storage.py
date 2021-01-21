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

    def test_sanitize_raises(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': [{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'RAISE', 'TEST')

        with self.assertRaises(InvalidSSLStorage) as cm:
            ssl_storage.sanitize()

        self.assertEqual(mock_connectionection.call.call_args_list,
                         [mock.call('SSFR_PSE_CHECK',
                                    IS_STRUST_IDENTITY={'PSE_CONTEXT': 'RAISE',
                                                        'PSE_APPLIC': 'TEST'})])

        self.assertEqual(str(cm.exception),
                         'The SSL Storage RAISE/TEST is broken: Invalid storage')

    def test_sanitize_raises_if_not_ret(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': []}

        ssl_storage = SSLCertStorage(mock_connectionection, 'RAISE', 'TEST')

        with self.assertRaises(InvalidSSLStorage) as cm:
            ssl_storage.sanitize()

        self.assertEqual(mock_connectionection.call.call_args_list,
                         [mock.call('SSFR_PSE_CHECK',
                                    IS_STRUST_IDENTITY={'PSE_CONTEXT': 'RAISE',
                                                        'PSE_APPLIC': 'TEST'})])

        self.assertEqual(str(cm.exception),
                         'Received no response from the server - check STRUST manually.')

    def test_sanitize_create(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': [{'TYPE': 'E', 'NUMBER': '031'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'CREATE', 'TEST')

        with patch('sap.rfc.strust.SSLCertStorage.create', Mock()) as mock_create:
            ssl_storage.sanitize()

        self.assertEqual(mock_connectionection.call.call_args_list,
                         [mock.call('SSFR_PSE_CHECK',
                                    IS_STRUST_IDENTITY={'PSE_CONTEXT': 'CREATE',
                                                        'PSE_APPLIC': 'TEST'})])
        mock_create.assert_called_once()

    def test_sanitize(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': [{'TYPE': 'S'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'NOTRAISE', 'TEST')
        ssl_storage.sanitize()

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PSE_CHECK',
                                     IS_STRUST_IDENTITY={'PSE_CONTEXT': 'NOTRAISE',
                                                         'PSE_APPLIC': 'TEST'})])

    def test_create(self):
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


if __name__ == '__main__':
    unittest.main()
