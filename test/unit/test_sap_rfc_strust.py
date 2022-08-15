from unittest.mock import patch, mock_open
from io import StringIO

import sap.rfc.strust
from sap.rfc.strust import SSLCertStorage, InvalidSSLStorage, PutCertificateError, PKCResponseABAPData, Identity,\
    BAPIError

import unittest
from mock import RFCConnection


class TestIdentity(unittest.TestCase):

    def test_str(self):
        pse_context = 'context'
        pse_applic = 'applic'
        identity = Identity(pse_context, pse_applic)

        self.assertEqual(str(identity), f'{pse_context}/{pse_applic}')


class TestPKCResponseABAPData(unittest.TestCase):

    def test_add_file(self):
        pkc_response = PKCResponseABAPData()
        file_content = 'this is an eighty characters long message to enforce and test the split function'

        pkc_response.add_file(StringIO(file_content * 2))

        self.assertEqual(
            pkc_response.data,
            [file_content, file_content, '']
        )

    def test_add_file_with_previous_data(self):
        initial_data = 'certificate data'

        pkc_response = PKCResponseABAPData()
        pkc_response.data = [initial_data]

        file_content = 'new data'
        pkc_response.add_file(StringIO(file_content))

        self.assertEqual(
            pkc_response.data,
            [initial_data + file_content]
        )


class TestSSLCertStorage(unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.connection = RFCConnection()

        self.pse_context = 'CTXT'
        self.pse_applic = 'APPL'
        self.ssl_storage = SSLCertStorage(self.connection, self.pse_context, self.pse_applic)
        self.expected_storage_identity = {
            'IS_STRUST_IDENTITY': {
                'PSE_CONTEXT': self.pse_context,
                'PSE_APPLIC': self.pse_applic
            }
        }

    def assert_rfc_call(self, expected_remote_function, **kwargs):
        self.assertEqual(
            self.connection.execs[0],
            (expected_remote_function, kwargs)
        )

    def test_ctor(self):
        self.assertIs(self.ssl_storage._connection, self.connection)
        self.assertEqual(self.ssl_storage.identity['PSE_CONTEXT'], self.pse_context)
        self.assertEqual(self.ssl_storage.identity['PSE_APPLIC'], self.pse_applic)

    def test_repr(self):
        self.assertEquals(repr(self.ssl_storage), f'SSL Storage {self.pse_context}/{self.pse_applic}')

    def test_str(self):
        self.assertEquals(str(self.ssl_storage), f'SSL Storage {self.pse_context}/{self.pse_applic}')

    def test_exists_raises(self):
        self.connection.set_responses([{
            'ET_BAPIRET2': [{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}]
        }])

        with self.assertRaises(InvalidSSLStorage) as cm:
            self.ssl_storage.exists()

        self.assert_rfc_call('SSFR_PSE_CHECK', **self.expected_storage_identity)

        self.assertEqual(str(cm.exception),
                         f'The SSL Storage {self.pse_context}/{self.pse_applic} is broken: Invalid storage')

    def test_exists_raises_if_not_ret(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])

        with self.assertRaises(InvalidSSLStorage) as cm:
            self.ssl_storage.exists()

        self.assert_rfc_call('SSFR_PSE_CHECK', **self.expected_storage_identity)

        self.assertEqual(str(cm.exception),
                         'Received no response from the server - check STRUST manually.')

    def test_exists_yes(self):
        self.connection.set_responses([{'ET_BAPIRET2': [{'TYPE': 'S'}]}])

        self.assertTrue(self.ssl_storage.exists())

        self.assert_rfc_call('SSFR_PSE_CHECK', **self.expected_storage_identity)

    def test_create_ok_default(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])

        self.ssl_storage.create()

        expected_call_arguments = {
            'IV_ALG': 'R',
            'IV_KEYLEN': 2048,
            'IV_REPLACE_EXISTING_PSE': '-'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PSE_CREATE', **expected_call_arguments)

    def test_create_ok_all_params(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])

        self.ssl_storage.create(alg='S', keylen=4096, replace=True, dn='ou=test')

        expected_call_arguments = {
            'IV_ALG': 'S',
            'IV_KEYLEN': 4096,
            'IV_REPLACE_EXISTING_PSE': 'X',
            'IV_DN': 'ou=test'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PSE_CREATE', **expected_call_arguments)

    def test_create_raises(self):
        self.connection.set_responses([{'ET_BAPIRET2': [
            {'TYPE': 'E', 'MESSAGE': 'Invalid storage'}
        ]}])

        with self.assertRaises(InvalidSSLStorage) as cm:
            self.ssl_storage.create()

        expected_call_arguments = {
            'IV_ALG': 'R',
            'IV_KEYLEN': 2048,
            'IV_REPLACE_EXISTING_PSE': '-'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PSE_CREATE', **expected_call_arguments)

        self.assertEqual(str(cm.exception),
                         str([{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}])
                         )

    def test_remove_ok(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])

        self.ssl_storage.remove()

        self.assert_rfc_call('SSFR_PSE_REMOVE', **self.expected_storage_identity)

    def test_remove_raises(self):
        self.connection.set_responses([{'ET_BAPIRET2': [
            {'TYPE': 'E', 'MESSAGE': 'Invalid storage'}
        ]}])

        with self.assertRaises(InvalidSSLStorage) as cm:
            self.ssl_storage.remove()

        self.assert_rfc_call('SSFR_PSE_REMOVE', **self.expected_storage_identity)

        self.assertEqual(str(cm.exception),
                         str([{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}]))

    def test_upload_ok_default(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])

        pse_data = 'data'
        self.ssl_storage.upload(pse_data)

        expected_call_arguments = {
            'IV_PSE_XSTRING': pse_data,
            'IV_REPLACE_EXISTING_PSE': '-'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PSE_UPLOAD_XSTRING', **expected_call_arguments)

    def test_upload_ok_all_params(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])

        pse_data = 'data'
        password = 'pass'
        self.ssl_storage.upload(pse_data, replace=True, password=password)

        expected_call_arguments = {
            'IV_PSE_XSTRING': pse_data,
            'IV_REPLACE_EXISTING_PSE': 'X',
            'IV_PSEPIN': password
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PSE_UPLOAD_XSTRING', **expected_call_arguments)

    def test_upload_raises(self):
        self.connection.set_responses([{'ET_BAPIRET2': [
            {'TYPE': 'E', 'MESSAGE': 'Invalid storage'}
        ]}])

        pse_data = 'data'
        with self.assertRaises(InvalidSSLStorage) as cm:
            self.ssl_storage.upload(pse_data)

        expected_call_arguments = {
            'IV_PSE_XSTRING': pse_data,
            'IV_REPLACE_EXISTING_PSE': '-'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PSE_UPLOAD_XSTRING', **expected_call_arguments)

        self.assertEqual(str(cm.exception),
                         str([{'TYPE': 'E', 'MESSAGE': 'Invalid storage'}]))

    def test_put_certificate(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])

        result = self.ssl_storage.put_certificate('plain old data')

        self.assertEqual(result, 'OK')

        expected_call_arguments = {
            'IV_CERTIFICATE': u'plain old data'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PUT_CERTIFICATE', **expected_call_arguments)

    def test_put_certificate_fail(self):
        self.connection.set_responses([{
            'ET_BAPIRET2': [{'TYPE': 'E', 'MESSAGE': 'Put has failed'}]}])

        with self.assertRaises(PutCertificateError) as cm:
            self.ssl_storage.put_certificate('plain old data')

        expected_call_arguments = {
            'IV_CERTIFICATE': u'plain old data'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PUT_CERTIFICATE', **expected_call_arguments)

        self.assertEquals(str(cm.exception),
                          f'Failed to put the CERT to the SSL Storage {self.pse_context}/{self.pse_applic}: '
                          'Put has failed')

    def test_put_certificate_fail_and_return_msg(self):
        self.connection.set_responses([{
            'ET_BAPIRET2': [{'TYPE': 'E', 'NUMBER': '522', 'MESSAGE': 'Put has failed'}]}])

        result = self.ssl_storage.put_certificate('plain old data')

        self.assertEqual(result,
                         'SSFR_PUT_CERTIFICATE reported Error 522 - '
                         'probably already exists (check manually): Put has failed'
                         )

        expected_call_arguments = {
            'IV_CERTIFICATE': u'plain old data'
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PUT_CERTIFICATE', **expected_call_arguments)

    def test_get_certificates(self):
        certs = 'certificates'
        self.connection.set_responses([{'ET_CERTIFICATELIST': certs}])

        result = self.ssl_storage.get_certificates()

        self.assertEqual(result, certs)
        self.assert_rfc_call('SSFR_GET_CERTIFICATELIST', **self.expected_storage_identity)

    def test_parse_certificate(self):
        self.connection.set_responses([{'EV_SUBJECT': 'cert subject'}])

        result = self.ssl_storage.parse_certificate(b'binary cert data')

        expected_call_arguments = {
            'IV_CERTIFICATE': b'binary cert data'
        }

        self.assert_rfc_call('SSFR_PARSE_CERTIFICATE', **expected_call_arguments)

        self.assertEqual(result, {'EV_SUBJECT': 'cert subject'})

    def test_get_csr(self):
        cert_request = ['line1', 'line2']
        self.connection.set_responses([{'ET_CERTREQUEST': cert_request, 'ET_BAPIRET2': []}])

        result = self.ssl_storage.get_csr()

        self.assertEqual(result, "\n".join(cert_request))
        self.assert_rfc_call('SSFR_GET_CERTREQUEST', **self.expected_storage_identity)

    def test_get_csr_raises(self):
        self.connection.set_responses([{'ET_BAPIRET2': [
            {'TYPE': 'E', 'ID': 1, 'NUMBER': 1, 'MESSAGE': 'Invalid storage'}
        ]}])

        with self.assertRaises(BAPIError) as cm:
            self.ssl_storage.get_csr()

        self.assertEqual('Error(1|1): Invalid storage', str(cm.exception))
        self.assert_rfc_call('SSFR_GET_CERTREQUEST', **self.expected_storage_identity)

    def test_put_identity_cert(self):
        self.connection.set_responses([{'ET_BAPIRET2': []}])
        pkc_response = PKCResponseABAPData()
        pkc_response.data = ['data']
        pkc_response.length = 1

        self.ssl_storage.put_identity_cert(pkc_response)

        expected_call_arguments = {
            'IT_CERTRESPONSE': pkc_response.data,
            'IV_CERTRESPONSE_LEN': pkc_response.length,
            'IV_PSEPIN': ''
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PUT_CERTRESPONSE', **expected_call_arguments)

    def test_put_identity_cert_raises(self):
        self.connection.set_responses([{'ET_BAPIRET2': [
            {'TYPE': 'E', 'ID': 1, 'NUMBER': 1, 'MESSAGE': 'Invalid storage'}
        ]}])
        pkc_response = PKCResponseABAPData()
        pkc_response.data = ['data']
        pkc_response.length = 1

        with self.assertRaises(BAPIError) as cm:
            self.ssl_storage.put_identity_cert(pkc_response)

        self.assertEqual('Error(1|1): Invalid storage', str(cm.exception))

        expected_call_arguments = {
            'IT_CERTRESPONSE': pkc_response.data,
            'IV_CERTRESPONSE_LEN': pkc_response.length,
            'IV_PSEPIN': ''
        }
        expected_call_arguments.update(**self.expected_storage_identity)

        self.assert_rfc_call('SSFR_PUT_CERTRESPONSE', **expected_call_arguments)

    @patch.object(sap.rfc.strust.SSLCertStorage, 'put_identity_cert', autospec=True)
    def test_put_identity_cert_file(self, fake_put_identity_cert):
        with patch('sap.rfc.strust.open', mock_open(read_data='certificate_data')):
            self.ssl_storage.put_identity_cert_file('path/to/cert')

        storage = fake_put_identity_cert.call_args.args[0]
        pkc_response = fake_put_identity_cert.call_args.args[1]

        self.assertEqual(pkc_response.data, ['certificate_data'])

        fake_put_identity_cert.assert_called_with(storage, pkc_response)


if __name__ == '__main__':
    unittest.main()
