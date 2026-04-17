"""HTTP client for SAP ABAP systems built on top of Python requests."""

import requests
import requests.exceptions
from requests.auth import HTTPBasicAuth

from sap import get_logger, config_get
from sap.http.errors import (
    HTTPRequestError,
    UnauthorizedError,
    TimedOutRequestError,
)


def build_query_args(client=None, saml2=None):
    """Build the query arguments for the ABAP HTTP request."""
    args = {}

    if saml2 is not None:
        saml2_arg = 'enabled' if saml2 else 'disabled'
        args['saml2'] = saml2_arg

    if client is not None:
        args['sap-client'] = client

    return args


def build_url(ssl=True, host=None, port=None, path=None, client=None, saml2=None):
    """Build the base URL for the ABAP HTTP request."""

    protocol = 'https' if ssl else 'http'
    default_port = '443' if ssl else '80'
    port = port or default_port

    base = f'{protocol}://{host}:{port}'
    url = f'{base}/{path}' if path is not None else base
    return url, build_query_args(client, saml2)


def default_http_error_handler(client, req, res):
    """Default error handler that raises UnauthorizedError for 401 and HTTPRequestError otherwise."""

    if res.status_code == 401:
        raise UnauthorizedError(req, res, client.user)

    raise HTTPRequestError(req, res)


# pylint: disable=too-many-instance-attributes
class HTTPClient():
    """HTTP client for SAP ABAP systems built on top of Python requests."""

    # pylint: disable=too-many-arguments
    def __init__(self,
                 ssl=True,
                 host=None,
                 port=None,
                 user=None,
                 password=None,
                 saml2=None,
                 client=None,
                 verify=None,
                 ssl_server_cert=None,
                 login_path='',
                 login_method='HEAD'
                 ):

        self.ssl = ssl
        self.host = host
        self.port = port
        if ssl:
            self.protocol = 'https'
            if port is None:
                self.port = '443'
        else:
            self.protocol = 'http'
            if port is None:
                self.port = '80'

        self._base_url, _ = build_url(self.ssl, self.host, self.port)

        self.ssl_verify = verify
        self.ssl_server_cert = ssl_server_cert

        self.user = user
        self.client = client
        self.saml2 = saml2
        self.login_path = login_path
        self.login_method = login_method

        self.timeout = config_get('http_timeout')

        self._auth = HTTPBasicAuth(user, password)

        self.error_handlers = [default_http_error_handler]
        self._connection_error_handler = None

    def add_error_handler(self, handler):
        """Add an error handler to the client.

        The handler will be called with the request and response objects
        when an error occurs.

        The handler is supposed to either raise an exception or return None. If
        it returns None, the next handler will be called. If no handler raises
        an exception, the default behavior is to raise an HTTPRequestError.
        """

        self.error_handlers.insert(0, handler)

    def handle_http_error(self, req, res):
        """Raise the correct exception based on response content.

        Calls the error handlers in order until one of them raises an
        exception. If no handler raises an exception, a HTTPRequestError is
        raised.
        """

        for handler in self.error_handlers:
            handler(self, req, res)

    def set_connection_error_handler(self, handler):
        """Set the connection error handler for the client.

        The handler will be called with the client and error
        when a requests.exceptions.ConnectionError occurs.

        def my_connection_error_handler(client: sap.http.client.HTTPClient, error: requests.exceptions.ConnectionError):
            # Handle the connection error, e.g. by logging it or raising a custom exception

        If the handler does not raise an exception, the original ConnectionError will be re-raised.
        """

        self._connection_error_handler = handler

    def retrieve(self, session, method, path, params=None, headers=None, body=None):
        """Execute an HTTP request and return the raw (request, response) tuple."""

        url = f'{self._base_url}/{path.lstrip("/")}'
        default_params = build_query_args(self.client, self.saml2)
        default_params.update(params or {})
        req = requests.Request(method.upper(), url, params=default_params, data=body, headers=headers)
        req = session.prepare_request(req)

        get_logger().info('Executing %s %s', method, url)

        if body is not None:
            get_logger().info('Body %s ', body)

        try:
            res = session.send(req, timeout=self.timeout)
        except requests.exceptions.ConnectTimeout as ex:
            raise TimedOutRequestError(req, self.timeout) from ex
        except requests.exceptions.ReadTimeout as ex:
            raise TimedOutRequestError(req, self.timeout) from ex
        except requests.exceptions.ConnectionError as ex:
            if self._connection_error_handler is not None:
                self._connection_error_handler(self, ex)
                # Handler must raise; if not we reraise the original exception
            raise

        get_logger().debug('Response %s %s:\n++++\n%s\n++++', method, url, res.text)

        return (req, res)

    def execute_with_session(self, session, method, path, params=None, headers=None, body=None):
        """Executes the given URL using the given method in
           the common HTTP session.
        """

        req, res = self.retrieve(session, method, path, params=params, headers=headers, body=body)

        if res.status_code == 403 and (not headers or headers.get('x-csrf-token', '') != 'Fetch'):
            get_logger().debug('Re-Fetching CSRF token')

            session.headers.pop('x-csrf-token', None)

            response = self.execute_with_session(
                session,
                self.login_method,
                self.login_path,
                headers={'x-csrf-token': 'Fetch'}
            )

            session.headers['x-csrf-token'] = response.headers['x-csrf-token']

            req, res = self.retrieve(session, method, path, params=params, headers=headers, body=body)

        if res.status_code >= 400:
            self.handle_http_error(req, res)

        return res

    def build_session(self):
        """Build the HTTP session for the ABAP HTTP request."""

        session = requests.Session()
        session.auth = self._auth

        # requests.session.verify is either boolean or path to CA to use!
        if self.ssl_server_cert:
            session.verify = self.ssl_server_cert
            get_logger().info('Using custom SSL Server cert path: %s', self.ssl_server_cert)
        elif self.ssl_verify is False:
            import urllib3
            urllib3.disable_warnings()
            get_logger().info('SSL Server cert will not be verified: SAP_SSL_VERIFY = no')
            session.verify = False

        login_headers = {'x-csrf-token': 'Fetch'}
        csrf_token = None

        response = self.execute_with_session(session, self.login_method, self.login_path, headers=login_headers)

        if 'x-csrf-token' in response.headers:
            csrf_token = response.headers['x-csrf-token']
            session.headers.update({'x-csrf-token': csrf_token})

        return session, response
