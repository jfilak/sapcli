"""Base ADT functionality module"""

import os
import requests
from requests.auth import HTTPBasicAuth

from sap import get_logger
from sap.adt.errors import HTTPRequestError, new_adt_error_from_xml


def mod_log():
    """ADT Module logger"""

    return get_logger()


class Connection:
    """ADT Connection for HTTP communication built on top Python requests.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, host, client, user, password, port=None, ssl=True, verify=True):
        """Parameters:
            - host: string host name
            - client: string SAP client
            - user: string user name
            - password: string user password
            - port: string TCP/IP port for ADT
                    (default 80 or 443 - it depends on the parameter ssl)
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

        self._adt_uri = 'sap/bc/adt'
        self._base_url = '{protocol}://{host}:{port}/{adt_uri}'.format(
            protocol=protocol, host=host, port=port, adt_uri=self._adt_uri)
        self._query_args = 'sap-client={client}&saml2=disabled'.format(
            client=client)
        self._user = user
        self._auth = HTTPBasicAuth(user, password)
        self._session = None

    @property
    def user(self):
        """Connected user"""

        return self._user

    @property
    def uri(self):
        """ADT path for building URLs (e.g. sap/bc/adt)"""

        return self._adt_uri

    def _build_adt_url(self, adt_uri):
        """Creates complete URL from a fragment of ADT URI
           where the fragment usually refers to an ADT object
        """

        return '{base_url}/{adt_uri}?{query_args}'.format(
            base_url=self._base_url, adt_uri=adt_uri,
            query_args=self._query_args)

    @staticmethod
    def _handle_http_error(req, res):
        """Raise the correct exception based on response content."""

        if res.headers['content-type'] == 'application/xml':
            error = new_adt_error_from_xml(res.text)

            if error is not None:
                raise error

        # else - unformatted text
        raise HTTPRequestError(req, res)

    @staticmethod
    def _execute_with_session(session, method, url, params=None, headers=None, body=None):
        """Executes the given URL using the given method in
           the common HTTP session.
        """

        req = requests.Request(method.upper(), url, params=params, data=body, headers=headers)
        req = session.prepare_request(req)

        mod_log().info('Executing %s %s', method, url)
        res = session.send(req)

        mod_log().debug('Response %s %s:\n++++\n%s\n++++', method, url, res.text)

        if res.status_code >= 400:
            Connection._handle_http_error(req, res)

        return res

    def _get_session(self):
        """Returns the working HTTP session.
           The session's cookies are populated by executing a dummy GET which
           also retrieves X-CSRF-Token.
        """

        if self._session is None:
            self._session = requests.Session()
            self._session.auth = self._auth
            # requests.session.verify is either boolean or path to CA to use!
            self._session.verify = os.environ.get('SAP_SSL_SERVER_CERT', self._session.verify)

            if self._session.verify is not True:
                mod_log().info('Using custom SSL Server cert path: SAP_SSL_SERVER_CERT = %s', self._session.verify)
            elif self._ssl_verify is False:
                import urllib3
                urllib3.disable_warnings()
                mod_log().info('SSL Server cert will not be verified: SAP_SSL_VERIFY = no')
                self._session.verify = False

            url = self._build_adt_url('core/discovery')

            response = Connection._execute_with_session(self._session, 'GET', url, headers={'x-csrf-token': 'Fetch'})

            self._session.headers.update({'x-csrf-token': response.headers['x-csrf-token']})

        return self._session

    def execute(self, method, adt_uri, params=None, headers=None, body=None):
        """Executes the given ADT URI as an HTTP request and returns
           the requests response object
        """

        session = self._get_session()

        url = self._build_adt_url(adt_uri)

        return Connection._execute_with_session(session, method, url, params=params, headers=headers, body=body)

    def get_text(self, relativeuri):
        """Executes a GET HTTP request with the headers Accept = text/plain.
        """

        return self.execute('GET', relativeuri, headers={'Accept': 'text/plain'}).text
