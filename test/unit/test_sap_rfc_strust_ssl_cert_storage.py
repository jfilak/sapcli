from unittest.mock import Mock

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

    def test_raise_if_not_ok_raises(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': [{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'RAISE', 'TEST')

        with self.assertRaises(InvalidSSLStorage) as cm:
            ssl_storage.sanitize()

        print(mock_connectionection.call.call_args_list)
        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PSE_CHECK',
                                     dict(IS_STRUST_IDENTITY={'PSE_CONTEXT': 'RAISE',
                                                              'PSE_APPLIC': 'TEST'}))])

        self.assertEquals(str(cm.exception),
                          'The SSL Storage RAISE/TEST is broken: Invalid storage')

    def test_raise_if_not_ok(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': [{'TYPE': 'S'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'NOTRAISE', 'TEST')
        ssl_storage.sanitize()

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PSE_CHECK',
                                     dict(IS_STRUST_IDENTITY={'PSE_CONTEXT': 'NOTRAISE',
                                                              'PSE_APPLIC': 'TEST'}))])

    def test_put_certificate(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {'ET_BAPIRET2': []}

        ssl_storage = SSLCertStorage(mock_connectionection, 'PUTOK', 'TEST')

        ssl_storage.put_certificate('plain old data')

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PUT_CERTIFICATE',
                                     dict(IS_STRUST_IDENTITY={'PSE_CONTEXT': 'PUTOK',
                                                              'PSE_APPLIC': 'TEST'},
                                          IV_CERTIFICATE=u'plain old data'))])

    def test_put_certificate_fail(self):
        mock_connectionection = Mock()
        mock_connectionection.call.return_value = {
            'ET_BAPIRET2': [{'TYPE': 'E', 'MESSAGE': 'Put has failed'}]}

        ssl_storage = SSLCertStorage(mock_connectionection, 'PUTERR', 'TEST')

        with self.assertRaises(PutCertificateError) as cm:
            ssl_storage.put_certificate('plain old data')

        self.assertEquals(mock_connectionection.call.call_args_list,
                          [mock.call('SSFR_PUT_CERTIFICATE',
                                     dict(IS_STRUST_IDENTITY={'PSE_CONTEXT': 'PUTERR',
                                                              'PSE_APPLIC': 'TEST'},
                                          IV_CERTIFICATE=u'plain old data'))])

        self.assertEquals(str(cm.exception),
                          'Failed to put the CERT to the SSL Storage PUTERR/TEST: '
                          'Put has failed')


if __name__ == '__main__':
    unittest.main()
