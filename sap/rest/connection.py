"""HTTP connection helpers"""

import json

import sap.http
from sap import get_logger
from sap.http import UnexpectedResponseContent
from sap.rest.errors import GCTSConnectionError


def mod_log():
    """ADT Module logger"""

    return get_logger()


def _gcts_http_connection_error_handler(client, ex):
    msg = str(ex)
    raise GCTSConnectionError(client.host, client.port, client.ssl, msg) from ex


# pylint: disable=too-many-instance-attributes
class Connection:
    """HTTP communication built on top Python requests.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, icf_path, login_path, host, client, user, password, port=None, ssl=True, verify=True,
                 ssl_server_cert=None):
        """Parameters:
            - host: string host name
            - client: string SAP client
            - user: string user name
            - password: string user password
            - port: string TCP/IP port for ADT
                    (default 80 or 443 - it depends on the parameter ssl)
            - ssl: boolean to switch between http and https
            - verify: boolean to switch SSL validation on/off
            - ssl_server_cert: optional path to a custom CA certificate file
        """

        sap.http.setup_keepalive()

        self._icf_path = icf_path

        self._http_client = sap.http.HTTPClient(
            ssl=ssl,
            host=host,
            port=port,
            user=user,
            password=password,
            saml2=False,
            client=client,
            verify=verify,
            ssl_server_cert=ssl_server_cert,
            login_path=f'{icf_path}/{login_path.lstrip("/")}',
            login_method='GET'
        )

        self._http_client.set_connection_error_handler(_gcts_http_connection_error_handler)

        self._session = None

    @property
    def user(self):
        """Connected user"""

        return self._http_client.user

    def _build_url(self, uri_path):
        """Creates path from the URI part
        """

        return f'{self._icf_path}/{uri_path.lstrip("/")}'

    def _get_session(self):
        """Returns the working HTTP session.
           The session's cookies are populated by executing a dummy GET which
           also retrieves X-CSRF-Token.
        """

        if self._session is None:
            self._session, _ = self._http_client.build_session()

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

        resp = self._http_client.execute_with_session(session, method, url, params=params, headers=headers, body=body)

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
