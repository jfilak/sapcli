"""SAP STRUST utilities"""

from collections import namedtuple

Identity = namedtuple('Identity', ['pse_context', 'pse_applic'])

CLIENT_ANONYMOUS = 'client_anonymous'
CLIENT_STANDART = 'client_standart'

IDENTITY_MAPPING = {
    CLIENT_ANONYMOUS: Identity('SSLC', 'ANONYM'),
    CLIENT_STANDART: Identity('SSLC', 'DFAULT')
}


class UploadCertError(Exception):
    """Base exception for errors of this tool"""

    # pylint: disable=unnecessary-pass
    pass


class InvalidSSLStorage(UploadCertError):
    """Invalid SSL storage errors"""

    # pylint: disable=unnecessary-pass
    pass


class PutCertificateError(UploadCertError):
    """Adding Certificate errors"""

    # pylint: disable=unnecessary-pass
    pass


class SSLCertStorage:
    """SAP STRUST representation"""

    def __init__(self, connection, pse_context, pse_applic):
        self._connection = connection
        self.identity = {
            'PSE_CONTEXT': pse_context,
            'PSE_APPLIC': pse_applic
        }

    def __repr__(self):
        return 'SSL Storage {PSE_CONTEXT}/{PSE_APPLIC}'.format(**self.identity)

    def __str__(self):
        return repr(self)

    def exists(self):
        """Checks if the storage is OK and if not, raise an exception
           of the type InvalidSSLStorage.
        """

        stat = self._connection.call(
            'SSFR_PSE_CHECK',
            IS_STRUST_IDENTITY=self.identity
        )

        ret = stat['ET_BAPIRET2']
        if not ret:
            raise InvalidSSLStorage(
                'Received no response from the server - check STRUST manually.'
            )

        message = ret[0]
        msgtype = message.get('TYPE', '')
        msgno = message.get('NUMBER', '')

        if msgtype == 'E' and msgno == '031':
            return False

        if msgtype != 'S':
            raise InvalidSSLStorage(f'The {str(self)} is broken: {ret[0]["MESSAGE"]}')

        return True

    # pylint: disable=invalid-name
    def create(self, alg='R', keylen=2048, replace=False, dn=None):
        """Create storage"""

        create_params = {
            'IS_STRUST_IDENTITY': self.identity,
            'IV_ALG': alg,
            'IV_KEYLEN': keylen,
            'IV_REPLACE_EXISTING_PSE': 'X' if replace else '-'
        }

        if dn is not None:
            create_params['IV_DN'] = dn

        stat = self._connection.call('SSFR_PSE_CREATE', **create_params)

        ret = stat['ET_BAPIRET2']
        if ret:
            raise InvalidSSLStorage(str(ret))

    def put_certificate(self, cert: bytes):
        """Adds the passed certificate to the storage

           Parameters:
            cert: certificate bytes
        """

        stat = self._connection.call(
            'SSFR_PUT_CERTIFICATE',
            IS_STRUST_IDENTITY=self.identity,
            IV_CERTIFICATE=cert
        )

        ret = stat['ET_BAPIRET2']
        if not ret:
            return 'OK'

        message = ret[0]
        msgtype = message.get('TYPE', '')
        msgno = message.get('NUMBER', '')

        if msgtype == 'E' and msgno == '522':
            message = ret[0]['MESSAGE']
            return f'SSFR_PUT_CERTIFICATE reported Error 522 - ' \
                   f'probably already exists (check manually): {message}'

        raise PutCertificateError(
            f'Failed to put the CERT to the {str(self)}: {ret[0]["MESSAGE"]}'
        )

    def get_certificates(self):
        """Returns the certificate list"""

        stat = self._connection.call(
            'SSFR_GET_CERTIFICATELIST',
            IS_STRUST_IDENTITY=self.identity
        )

        return stat['ET_CERTIFICATELIST']

    def parse_certificate(self, xcert):
        """Parse certificate from binary X.509 format to python structure"""
        cert = self._connection.call(
            'SSFR_PARSE_CERTIFICATE',
            IV_CERTIFICATE=xcert
        )

        return cert


def notify_icm_changed_pse(connection):
    """Informs ICM about changed PSE"""

    connection.call('ICM_SSL_PSE_CHANGED')


def iter_storage_certificates(ssl_storage: SSLCertStorage):
    """Returns the certificate list"""

    for xcert in ssl_storage.get_certificates():
        # pylint: disable=protected-access
        parse_ret = ssl_storage._connection.call('SSFR_PARSE_CERTIFICATE', IV_CERTIFICATE=xcert)
        yield parse_ret
