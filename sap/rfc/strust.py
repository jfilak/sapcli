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

    def sanitize(self):
        """Checks if the storage is OK and if not, raise an exception
           of the type InvalidSSLStorage.
        """

        stat = self._connection.call(
            'SSFR_PSE_CHECK',
            {'IS_STRUST_IDENTITY': self.identity}
        )

        ret = stat['ET_BAPIRET2']
        if not ret:
            raise InvalidSSLStorage(
                'The {0} is broken: received no response from the server - check STRUST manually.'
            )

        message = ret[0]
        msgtype = message.get('TYPE', '')
        msgno = message.get('NUMBER', '')

        if msgtype == 'E' and msgno == '031':
            self.create()
        elif msgtype != 'S':
            raise InvalidSSLStorage(
                'The {0} is broken: {1}'.format(str(self), ret[0]['MESSAGE'])
            )

    def create(self, alg='R', keylen=2048, replace=False):
        """Create storage"""

        stat = self._connection.call(
            'SSFR_PSE_CREATE',
            {'IS_STRUST_IDENTITY': self.identity,
             'IV_ALG': alg,
             'IV_KEYLEN': keylen,
             'IV_REPLACE_EXISTING_PSE': 'X' if replace else '-'}
        )

        ret = stat['ET_BAPIRET2']
        if ret:
            raise InvalidSSLStorage(str(ret))

    def put_certificate(self, cert):
        """Adds the passed certificate to the storage"""

        stat = self._connection.call(
            'SSFR_PUT_CERTIFICATE',
            {'IS_STRUST_IDENTITY': self.identity, 'IV_CERTIFICATE': cert}
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
            'Failed to put the CERT to the {0}: {1}'.format(
                str(self),
                ret[0]['MESSAGE'])
        )

    def get_certificates(self):
        """Returns the certificate list"""

        stat = self._connection.call(
            'SSFR_GET_CERTIFICATELIST',
            {'IS_STRUST_IDENTITY': self.identity}
        )

        return stat
