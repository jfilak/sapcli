#!/usr/bin/env python3

import os
import tempfile
import unittest
from unittest.mock import Mock

import requests

from sap.errors import SAPCliError
from sap.http.client import HTTPSessionInitializer
from sap.http.client_cert import (
    ClientCertificateError,
    ClientCertificateHTTPSessionInitializer,
)
from sap.http.errors import UnauthorizedError

from fixtures_sap_http_client_cert import (
    CERTIFICATE_PEM,
    COMBINED_CERT_AND_ENCRYPTED_KEY_PEM,
    COMBINED_CERT_AND_PLAIN_KEY_PEM,
    ENCRYPTED_LEGACY_KEY_PEM,
    ENCRYPTED_PKCS8_KEY_PEM,
    PLAIN_KEY_PEM,
    SERVER_CA_PEM,
)


class ClientCertFilesTestCase(unittest.TestCase):
    """Base providing on-disk PEM files for initializer tests."""

    def setUp(self):
        # pylint: disable=consider-using-with
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp_dir.cleanup)

    def _write(self, name, content):
        path = os.path.join(self._tmp_dir.name, name)
        with open(path, 'w', encoding='ascii') as pem_file:
            pem_file.write(content)

        return path


class TestConstruction(ClientCertFilesTestCase):

    def test_satisfies_session_initializer_protocol(self):
        initializer = ClientCertificateHTTPSessionInitializer('/cert.pem', '/key.pem')

        self.assertIsInstance(initializer, HTTPSessionInitializer)

    def test_error_derives_from_sapclierror(self):
        self.assertTrue(issubclass(ClientCertificateError, SAPCliError))

    def test_construction_does_no_io(self):
        # Constructing with non-existent paths must not raise - plugin
        # provided ephemeral files may only exist at initialize time.
        ClientCertificateHTTPSessionInitializer(
            '/does/not/exist.pem', '/does/not/exist.key'
        )


class TestInitializeSession(ClientCertFilesTestCase):

    def test_certificate_and_key_set_session_cert_tuple(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', PLAIN_KEY_PEM)
        session = requests.Session()

        initializer = ClientCertificateHTTPSessionInitializer(cert, key)
        returned = initializer.initialize_session(session)

        self.assertIs(returned, session)
        self.assertEqual(session.cert, (cert, key))

    def test_combined_file_without_key_sets_session_cert_path(self):
        combined = self._write('client.pem', COMBINED_CERT_AND_PLAIN_KEY_PEM)
        session = requests.Session()

        ClientCertificateHTTPSessionInitializer(combined).initialize_session(session)

        self.assertEqual(session.cert, combined)

    def test_server_ca_sets_session_verify(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', PLAIN_KEY_PEM)
        server_ca = self._write('ca.pem', SERVER_CA_PEM)
        session = requests.Session()

        ClientCertificateHTTPSessionInitializer(
            cert, key, server_ca=server_ca
        ).initialize_session(session)

        self.assertEqual(session.verify, server_ca)

    def test_no_server_ca_leaves_session_verify_untouched(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', PLAIN_KEY_PEM)
        session = requests.Session()

        ClientCertificateHTTPSessionInitializer(cert, key).initialize_session(session)

        self.assertIs(session.verify, True)

    def test_missing_certificate_file_raises(self):
        key = self._write('client.key', PLAIN_KEY_PEM)
        missing = os.path.join(self._tmp_dir.name, 'nosuch.crt')

        initializer = ClientCertificateHTTPSessionInitializer(missing, key)

        with self.assertRaisesRegex(ClientCertificateError, 'nosuch.crt'):
            initializer.initialize_session(requests.Session())

    def test_missing_key_file_raises(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        missing = os.path.join(self._tmp_dir.name, 'nosuch.key')

        initializer = ClientCertificateHTTPSessionInitializer(cert, missing)

        with self.assertRaisesRegex(ClientCertificateError, 'nosuch.key'):
            initializer.initialize_session(requests.Session())


class TestEncryptedKeyDetection(ClientCertFilesTestCase):

    def test_encrypted_pkcs8_key_raises(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', ENCRYPTED_PKCS8_KEY_PEM)

        initializer = ClientCertificateHTTPSessionInitializer(cert, key)

        with self.assertRaisesRegex(ClientCertificateError, 'encrypted'):
            initializer.initialize_session(requests.Session())

    def test_encrypted_legacy_key_raises(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', ENCRYPTED_LEGACY_KEY_PEM)

        initializer = ClientCertificateHTTPSessionInitializer(cert, key)

        with self.assertRaisesRegex(ClientCertificateError, 'encrypted'):
            initializer.initialize_session(requests.Session())

    def test_encrypted_key_error_names_the_way_out(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', ENCRYPTED_PKCS8_KEY_PEM)

        initializer = ClientCertificateHTTPSessionInitializer(cert, key)

        with self.assertRaisesRegex(ClientCertificateError, 'auth plugin'):
            initializer.initialize_session(requests.Session())

    def test_encrypted_key_in_combined_file_raises(self):
        combined = self._write('client.pem', COMBINED_CERT_AND_ENCRYPTED_KEY_PEM)

        initializer = ClientCertificateHTTPSessionInitializer(combined)

        with self.assertRaisesRegex(ClientCertificateError, 'encrypted'):
            initializer.initialize_session(requests.Session())

    def test_encrypted_key_does_not_touch_session(self):
        cert = self._write('client.crt', CERTIFICATE_PEM)
        key = self._write('client.key', ENCRYPTED_PKCS8_KEY_PEM)
        session = requests.Session()

        initializer = ClientCertificateHTTPSessionInitializer(cert, key)

        with self.assertRaises(ClientCertificateError):
            initializer.initialize_session(session)

        self.assertIsNone(session.cert)


class TestBuildUnauthorizedError(ClientCertFilesTestCase):

    def test_with_user_carries_user(self):
        initializer = ClientCertificateHTTPSessionInitializer(
            '/cert.pem', '/key.pem', user='alice'
        )
        req = Mock()
        res = Mock()

        err = initializer.build_unauthorized_error(req, res)

        self.assertIsInstance(err, UnauthorizedError)
        self.assertIs(err.request, req)
        self.assertIs(err.response, res)
        self.assertEqual(err.user, 'alice')

    def test_without_user_names_certificate(self):
        initializer = ClientCertificateHTTPSessionInitializer('/cert.pem', '/key.pem')

        err = initializer.build_unauthorized_error(Mock(), Mock())

        self.assertEqual(err.user, 'client-cert:/cert.pem')


if __name__ == '__main__':
    unittest.main()
