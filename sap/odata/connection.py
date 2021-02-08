"""OData connection helpers"""

import pyodata
import requests
from requests.auth import HTTPBasicAuth

from sap import get_logger, config_get
from sap.odata.errors import HTTPRequestError, UnauthorizedError, TimedOutRequestError


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class Connection:
    """OData communication built on top of pyodata and requests.
    """

    client = None

    # pylint: disable=too-many-arguments
    def __init__(self, service, host, port, client, user, password, ssl, verify):
        """Parameters:
            - service: id of the odata service (e.g. ABAP_REPOSITORY_SRV)
            - host: string host name or IP of
            - port: string TCP/IP port for abap application server
            - client: string SAP client
            - user: string user name
            - password: string user password
            - ssl: boolean to switch between http and https
            - verify: boolean to switch SSL validation on/off
        """

        if ssl:
            protocol = 'https'
            if port is None:
                port = '443'
        else:
            protocol = 'http'
            if port is None:
                port = '80'

        self._ssl_verify = verify

        self._base_url = '{protocol}://{host}:{port}/sap/opu/odata/{service}'.format(
            protocol=protocol, host=host, port=port, service=service)

        self._query_args = 'sap-client={client}&saml2=disabled'.format(
            client=client)

        self._user = user
        self._auth = HTTPBasicAuth(user, password)
        self._session = None
        self._timeout = config_get('http_timeout')

        self._session = requests.Session()
        self._session.verify = verify
        self._session.auth = (user, password)

        # csrf token handling for all future "create" requests
        try:
            get_logger().info('Executing head request as part of CSRF authentication %s', self._base_url)
            req = requests.Request('HEAD', self._base_url, headers={'x-csrf-token': 'fetch'})
            req = self._session.prepare_request(req)
            res = self._session.send(req, timeout=self._timeout)

        except requests.exceptions.ConnectTimeout:
            raise TimedOutRequestError(req, self._timeout)

        if res.status_code == 401:
            raise UnauthorizedError(req, res, self._user)

        if res.status_code >= 400:
            raise HTTPRequestError(req, res)

        token = res.headers.get('x-csrf-token', '')
        self._session.headers.update({'x-csrf-token': token})

        # instance of the service
        self.client = pyodata.Client(self._base_url, self._session)
