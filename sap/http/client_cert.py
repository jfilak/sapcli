"""HTTP session initializer for TLS client certificate (mTLS) authentication.

The initializer only points requests at PEM files on disk - it never parses
the cryptographic material itself. requests cannot use an encrypted private
key (ssl.SSLContext.load_cert_chain is called without a password), so the
key file is inspected for PEM encryption markers up front to fail with an
actionable message instead of a cryptic OpenSSL error.
"""

import os

from sap.errors import SAPCliError
from sap.http.errors import UnauthorizedError


_PEM_ENCRYPTION_MARKERS = (
    b'BEGIN ENCRYPTED PRIVATE KEY',  # PKCS#8
    b'Proc-Type: 4,ENCRYPTED',       # legacy PKCS#1
)


class ClientCertificateError(SAPCliError):
    """Errors of TLS client certificate authentication configuration"""


class ClientCertificateHTTPSessionInitializer:
    """Populates sessions with a TLS client certificate (mTLS).

    Implements the ``HTTPSessionInitializer`` protocol from
    ``sap.http.client``. When ``key`` is None, ``certificate`` must be a
    combined PEM file holding both the certificate and the private key
    (curl's --cert without --key). Construction must not perform I/O -
    plugin provided ephemeral files may only exist at initialize time.
    """

    def __init__(self, certificate, key=None, server_ca=None, user=None):
        self._certificate = certificate
        self._key = key
        self._server_ca = server_ca
        self._user = user

    def initialize_session(self, session):
        """Set the client certificate (and optionally the server CA) on the session"""

        _check_file_exists(self._certificate, 'certificate')
        if self._key:
            _check_file_exists(self._key, 'key')

        _check_key_not_encrypted(self._key or self._certificate)

        if self._key:
            session.cert = (self._certificate, self._key)
        else:
            session.cert = self._certificate

        if self._server_ca:
            session.verify = self._server_ca

        return session

    def build_unauthorized_error(self, req, res):
        """Build an UnauthorizedError naming the user or the certificate file"""

        return UnauthorizedError(req, res, self._user or f'client-cert:{self._certificate}')


def _check_file_exists(path, role):
    if not os.path.isfile(path):
        raise ClientCertificateError(f'The client {role} file does not exist: {path}')


def _check_key_not_encrypted(path):
    try:
        with open(path, 'rb') as key_file:
            contents = key_file.read()
    except OSError as ex:
        raise ClientCertificateError(f'Cannot read the client key file {path}: {ex}') from ex

    if any(marker in contents for marker in _PEM_ENCRYPTION_MARKERS):
        raise ClientCertificateError(
            f'The client private key is encrypted and sapcli cannot use it: {path}\n'
            'Either decrypt it (openssl pkey -in encrypted.key -out plain.key)'
            ' or use an auth plugin which provides an unencrypted key.'
        )
