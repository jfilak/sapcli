"""HTTP connection helpers"""

import os
import json

import socket
from urllib3.connection import HTTPConnection
import requests
from requests.auth import HTTPBasicAuth

import sap.adt.core
from sap import get_logger, config_get
from sap.rest.errors import (
    HTTPRequestError,
    UnexpectedResponseContent,
    UnauthorizedError,
    TimedOutRequestError,
    GCTSConnectionError,
)


KEEPALIVE_CONFIGURED = False


def mod_log():
    """ADT Module logger"""

    return get_logger()


def setup_keepalive():
    """Make sure we send keepalive TCP packets"""

    # pylint: disable=global-statement
    global KEEPALIVE_CONFIGURED

    if KEEPALIVE_CONFIGURED:
        mod_log().debug("KeepAlive already configured")
        return

    KEEPALIVE_CONFIGURED = True

    mod_log().debug("Updating urllib3.connection.HTTPConnection.default_socket_options with KeepAlive packets")

    # Special thanks to: https://www.finbourne.com/blog/the-mysterious-hanging-client-tcp-keep-alives
    # This may cause problems in Windows!
    if "TCP_KEEPIDLE" in dir(socket):
        # pylint: disable=no-member
        HTTPConnection.default_socket_options = HTTPConnection.default_socket_options + [
            (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
            (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
        ]


# pylint: disable=too-many-instance-attributes
class Connection:
    """HTTP communication built on top Python requests.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, icf_path, login_path, host, client, user, password, port=None, ssl=True, verify=True):
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

        setup_keepalive()

        if ssl:
            protocol = 'https'
            if port is None:
                port = '443'
        else:
            protocol = 'http'
            if port is None:
                port = '80'

        self._ssl_verify = verify

        self._host = host
        self._port = port
        self._ssl = ssl
        self._base_url = f'{protocol}://{host}:{port}/{icf_path}'
        self._query_args = f'sap-client={client}&saml2=disabled'

        self._user = user
        self._auth = HTTPBasicAuth(user, password)
        self._session = None
        self._login_path = login_path
        self._timeout = config_get('http_timeout')
        self._client = client

    @property
    def user(self):
        """Connected user"""

        return self._user

    def _build_url(self, uri_path):
        """Creates complete URL from the path part
        """

        return f'{self._base_url}/{uri_path}?{self._query_args}'

    def _handle_http_error(self, req, res):
        """Raise the correct exception based on response content."""

        if res.status_code == 401:
            raise UnauthorizedError(req, res, self._user)

        raise HTTPRequestError(req, res)

    def _retrieve(self, session, method, url, params=None, headers=None, body=None):
        """A helper method for easier testing."""

        req = requests.Request(method.upper(), url, params=params, data=body, headers=headers)
        req = session.prepare_request(req)

        mod_log().info('Executing %s %s', method, url)

        if body is not None:
            mod_log().info('Body %s ', body)

        try:
            res = session.send(req, timeout=self._timeout)
        except requests.exceptions.ConnectTimeout as ex:
            raise TimedOutRequestError(req, self._timeout) from ex
        except requests.exceptions.ConnectionError as ex:
            msg = str(ex)
            raise GCTSConnectionError(self._host, self._port, self._ssl, msg) from ex

        mod_log().debug('Response %s %s:\n++++\n%s\n++++', method, url, res.text)

        return (req, res)

    def _execute_with_session(self, session, method, url, params=None, headers=None, body=None):
        """Executes the given URL using the given method in
           the common HTTP session.
        """

        req, res = self._retrieve(session, method, url, params=params, headers=headers, body=body)

        if res.status_code >= 400:
            self._handle_http_error(req, res)

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

            login_headers = {'x-csrf-token': 'Fetch'}
            csrf_token = None
            url = self._build_url(self._login_path)

            try:
                response = self._execute_with_session(self._session, 'GET', url, headers=login_headers)
            except HTTPRequestError as ex:
                if ex.response.status_code != 404:
                    raise ex

            if 'x-csrf-token' in response.headers:
                csrf_token = response.headers['x-csrf-token']
                self._session.headers.update({'x-csrf-token': csrf_token})

        return self._session

    def execute(self, method, uri_path, params=None, headers=None, body=None, accept=None, content_type=None):
        """Executes the given URI as an HTTP request and returns
           the requests response object
        """

        session = self._get_session()

        url = self._build_url(uri_path)

        if headers is None:
            headers = {}

        if accept is not None:
            if isinstance(accept, list):
                headers['Accept'] = ', '.join(accept)
            else:
                headers['Accept'] = accept

        if content_type is not None:
            headers['Content-Type'] = content_type

        if not headers:
            headers = None

        resp = self._execute_with_session(session, method, url, params=params, headers=headers, body=body)

        if accept:
            resp_content_type = resp.headers['Content-Type']

            if isinstance(accept, str):
                accept = [accept]

            if not any((resp_content_type.startswith(accepted) for accepted in accept)):
                raise UnexpectedResponseContent(accept, resp_content_type, resp.text)

        return resp

    def get_json(self, uri_path, params=None):
        """Executes a GET HTTP request with the headers Accept = application/json.
        """

        response = self.execute('GET', uri_path, accept='application/json', params=params)
        return response.json()

    def post_obj_as_json(self, uri_path, obj, accept=None):
        """Executes a POST HTTP request with the headers Content-Type = application/json.
        """

        body = json.dumps(obj)
        return self.execute('POST', uri_path, content_type='application/json', body=body, accept=accept)

    def delete_json(self, uri_path, params=None):
        """Executes a DELETE HTTP request ith the headers Accept = application/json.
        """

        response = self.execute('DELETE', uri_path, accept='application/json', params=params)
        return response.json()

    def get_adt_connection(self):
        """Build ADT Connection from this connection.
        """

        return sap.adt.core.Connection(self._host, self._client, self._user, port=self._port, ssl=self._ssl,
                                       verify=self._ssl_verify, auth=self._auth)
