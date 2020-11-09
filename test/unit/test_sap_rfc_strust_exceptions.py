import unittest

from sap.rfc.strust import UploadCertError, InvalidSSLStorage, PutCertificateError


class TestUploadException(unittest.TestCase):

    def test_ctor_with_message(self):
        ex = UploadCertError('Something has failed')
        self.assertEqual(str(ex), 'Something has failed')


class TestInvalidSSLStorage(unittest.TestCase):

    def test_ctor_with_message(self):
        ex = InvalidSSLStorage('Something has failed')
        self.assertEqual(str(ex), 'Something has failed')


class TestPutCertificateError(unittest.TestCase):

    def test_ctor_with_message(self):
        ex = PutCertificateError('Something has failed')
        self.assertEqual(str(ex), 'Something has failed')


if __name__ == '__main__':
    unittest.main()
