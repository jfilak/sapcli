"""SAP STRUST utilities"""


class Identity:
    """PSE Identity tuple"""

    def __init__(self, pse_context, pse_applic):
        self.pse_context = pse_context
        self.pse_applic = pse_applic

    def __str__(self):
        return f'{self.pse_context}/{self.pse_applic}'


SERVER_STANDARD = 'server_standard'
CLIENT_ANONYMOUS = 'client_anonymous'
CLIENT_STANDART = 'client_standart'

# SSFPSE_FILENAME
IDENTITY_MAPPING = {
    SERVER_STANDARD: Identity('SSLS', 'DFAULT'),
    CLIENT_ANONYMOUS: Identity('SSLC', 'ANONYM'),
    CLIENT_STANDART: Identity('SSLC', 'DFAULT')
}

# SSFPSE_CREATE
PSE_ALGORITHM_MAPPING = {
    'RSA': 'R',
    'RSAwithSHA256': 'S',
    'GOST_R_34.10-94': 'G',
    'GOST_R_34.10-2001': 'H',
    'CCL': 'X',  # This one accepts the CCLALG string (e.g. RSA:4096:SHA256)
                 # but we cannot pass it via the RFC FM SSFR_PSE_CREATE
    'DSA': 'D'
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
            raise InvalidSSLStorage(
                'The {0} is broken: {1}'.format(str(self), ret[0]['MESSAGE'])
            )

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
            'Failed to put the CERT to the {0}: {1}'.format(
                str(self),
                ret[0]['MESSAGE'])
        )

    def get_certificates(self):
        """Returns the certificate list"""

        stat = self._connection.call(
            'SSFR_GET_CERTIFICATELIST',
            IS_STRUST_IDENTITY=self.identity
        )

        return stat['ET_CERTIFICATELIST']

    def get_csr(self):
        """Returns Certificate Signing Request"""

        csr_resp = self._connection.call(
            'SSFR_GET_CERTREQUEST',
            IS_STRUST_IDENTITY=self.identity
        )

        bapiret = BAPIReturn(csr_resp['ET_BAPIRET2'])
        if bapire.is_error():
            raise BAPIError(bapiret, csr_resp)

        csr_contents = "\n".join(csr_resp['ET_CERTREQUEST'])

        return csr_contents

    def put_identity_cert(self, data):
        """Uploads Identity Certificate signed by an Authority"""

        csr_resp = self._connection.call(
            'SSFR_PUT_CERTRESPONSE',
            IS_STRUST_IDENTITY=self.identity,
            IT_CERTRESPONSE='',
            IV_CERTRESPONSE_LEN,
            IV_PSEPIN
        )

        bapiret = BAPIReturn(csr_resp['ET_BAPIRET2'])
        if bapire.is_error():
            raise BAPIError(bapiret, csr_resp)


def notify_icm_changed_pse(connection):
    """Informs ICM about changed PSE"""

    connection.call('ICM_SSL_PSE_CHANGED')


def iter_storage_certificates(ssl_storage: SSLCertStorage):
    """Returns the certificate list"""

    for xcert in ssl_storage.get_certificates():
        # pylint: disable=protected-access
        parse_ret = ssl_storage._connection.call('SSFR_PARSE_CERTIFICATE', IV_CERTIFICATE=xcert)
        yield parse_ret
