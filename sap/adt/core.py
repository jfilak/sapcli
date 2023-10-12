"""Base ADT functionality module"""

import os

import xml.sax
from xml.sax.handler import ContentHandler

import requests
from requests.auth import HTTPBasicAuth

from sap import get_logger, config_get
from sap.rest.connection import setup_keepalive
from sap.adt.errors import new_adt_error_from_xml, ADTConnectionError
from sap.rest.errors import (
    HTTPRequestError,
    UnexpectedResponseContent,
    UnauthorizedError,
    TimedOutRequestError,
)


def mod_log():
    """ADT Module logger"""

    return get_logger()


class _DiscoveryHandler(ContentHandler):

    def __init__(self):
        super().__init__()

        self.result = {}
        self._collection = None
        self._mimetypes = None
        self._accept = None

    def startElement(self, name, attrs):
        if name == 'app:collection':
            self._collection = attrs['href']
            self._mimetypes = []
        elif name == 'app:accept':
            self._accept = ''
        elif name == 'adtcomp:templateLink':
            if 'type' in attrs:
                self.result[attrs['template']] = [attrs['type']]

    def characters(self, content):
        if self._accept is None:
            return

        self._accept += content

    def endElement(self, name):
        if name == 'app:collection':
            if self._mimetypes:
                self.result[self._collection] = self._mimetypes

            self._collection = None
            self._mimetypes = None
        elif name == 'app:accept':
            self._mimetypes.append(self._accept)
            self._accept = None


def _get_collection_accepts(discovery_xml):
    """Transform the following XML excerpt:
        <app:service>
          <app:workspace>
            <app:collection href="/sap/bc/adt/...">
              <app:accept>application/vnd.sap.ap.adt.?.v?+xml<app:accept>
              <app:accept>application/vnd.sap.ap.adt.?.v?+xml<app:accept>
              <adtcomp:templateLinks xmlns:adtcomp="http://www.sap.com/adt/compatibility">
                <adtcomp:templateLink title="Function Modules"
                    rel="http://www.sap.com/adt/categories/functiongroups/functionmodules"
                    template="/sap/bc/adt/functions/groups/{groupname}/fmodules"
                    type="application/vnd.sap.adt.functions.fmodules.v3+xml"/>

       To:
         {href: [app:accept, app:accept],
          template: [type]}
    """

    xml_handler = _DiscoveryHandler()
    xml.sax.parseString(discovery_xml, xml_handler)

    return xml_handler.result


# pylint: disable=too-many-instance-attributes
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

        self._adt_uri = 'sap/bc/adt'
        self._base_url = f'{protocol}://{host}:{port}/{self._adt_uri}'
        self._query_args = f'sap-client={client}&saml2=disabled'
        self._user = user
        self._auth = HTTPBasicAuth(user, password)
        self._session = None
        self._collection_types = None
        self._timeout = config_get('http_timeout')

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

        return f'{self._base_url}/{adt_uri}?{self._query_args}'

    def _handle_http_error(self, req, res):
        """Raise the correct exception based on response content."""

        if res.headers['content-type'] == 'application/xml':
            error = new_adt_error_from_xml(res.text)

            if error is not None:
                raise error

        # else - unformatted text
        if res.status_code == 401:
            raise UnauthorizedError(req, res, self._user)

        raise HTTPRequestError(req, res)

    def _retrieve(self, session, method, url, params=None, headers=None, body=None):
        """A helper method for easier testing."""

        req = requests.Request(method.upper(), url, params=params, data=body, headers=headers)
        req = session.prepare_request(req)

        mod_log().info('Executing %s %s', method, url)

        try:
            res = session.send(req, timeout=self._timeout)
        except requests.exceptions.ConnectTimeout as ex:
            raise TimedOutRequestError(req, self._timeout) from ex
        except requests.exceptions.ConnectionError as ex:
            raise ADTConnectionError(ex.args[-1]) from ex

        mod_log().debug('Response %s %s:\n++++\n%s\n++++', method, url, res.text)

        return (req, res)

    def _execute_with_session(self, session, method, url, params=None, headers=None, body=None):
        """Executes the given URL using the given method in
           the common HTTP session.
        """

        req, res = self._retrieve(session, method, url, params=params, headers=headers, body=body)

        if res.status_code == 403 and (not headers or headers.get('x-csrf-token', '') != 'Fetch'):
            mod_log().debug('Re-Fetching CSRF token')

            del session.headers['x-csrf-token']

            response = self._execute_with_session(
                session,
                'GET',
                self._build_adt_url('discovery'),
                headers={'x-csrf-token': 'Fetch'}
            )

            session.headers['x-csrf-token'] = response.headers['x-csrf-token']

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

            discovery_headers = {'x-csrf-token': 'Fetch'}
            csrf_token = None
            url = self._build_adt_url('core/discovery')

            try:
                response = self._execute_with_session(self._session, 'GET', url, headers=discovery_headers)
                discovery_headers = {}
                csrf_token = response.headers['x-csrf-token']
            except HTTPRequestError as ex:
                if ex.response.status_code != 404:
                    raise ex

            url = self._build_adt_url('discovery')
            response = self._execute_with_session(self._session, 'GET', url, headers=discovery_headers)
            self._collection_types = _get_collection_accepts(response.text)

            if csrf_token is None:
                csrf_token = response.headers['x-csrf-token']

            self._session.headers.update({'x-csrf-token': csrf_token})

        return self._session

    def execute(self, method, adt_uri, params=None, headers=None, body=None, accept=None, content_type=None):
        """Executes the given ADT URI as an HTTP request and returns
           the requests response object
        """

        session = self._get_session()

        url = self._build_adt_url(adt_uri)

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

    def get_text(self, relativeuri):
        """Executes a GET HTTP request with the headers Accept = text/plain.
        """

        return self.execute('GET', relativeuri, headers={'Accept': 'text/plain'}).text

    @property
    def collection_types(self):
        """Returns dictionary of Object type URI fragment and list of
           supported MIME types.
        """

        if self._collection_types is None:
            response = self.execute('GET', 'discovery')
            self._collection_types = _get_collection_accepts(response.text)

        return self._collection_types

    def get_collection_types(self, basepath, default_mimetype):
        """Returns the accepted object XML format - mime type"""

        uri = f'/{self._adt_uri}/{basepath}'
        try:
            return self.collection_types[uri]
        except KeyError:
            return [default_mimetype]
