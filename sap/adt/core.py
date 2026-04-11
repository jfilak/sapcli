"""Base ADT functionality module"""

import xml.sax
from xml.sax.handler import ContentHandler

import sap.http
from sap import get_logger
from sap.adt.errors import new_adt_error_from_xml, ADTConnectionError
from sap.http import (
    HTTPRequestError,
    UnexpectedResponseContent,
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


def _adt_http_error_handler(client, req, res):  # pylint: disable=unused-argument

    if res.headers['content-type'] == 'application/xml':
        error = new_adt_error_from_xml(res.text)

        if error is not None:
            raise error


def _adt_http_connection_error_handler(client, ex):
    msg = str(ex)
    raise ADTConnectionError(client.host, client.port, client.ssl, msg) from ex


# pylint: disable=too-many-instance-attributes
class Connection:
    """ADT Connection for HTTP communication built on top Python requests.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, host, client, user, password, port=None, ssl=True, verify=True, ssl_server_cert=None):
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

        self._base_adt_path = 'sap/bc/adt'

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
            # This must be the default login path because newer ABAP systems
            # did not return cookies and CSRF token with the old default login
            # path (GET /sap/bc/adt/discovery) and thus did not work with
            # the default login method of HTTPClient.
            login_path=f'{self._base_adt_path}/core/discovery',
            login_method='GET'
        )

        self._http_client.add_error_handler(_adt_http_error_handler)
        self._http_client.set_connection_error_handler(_adt_http_connection_error_handler)

        self._session = None
        self._collection_types = None

    @property
    def user(self):
        """Connected user"""

        return self._http_client.user

    @property
    def uri(self):
        """ADT path for building URLs (e.g. sap/bc/adt)"""

        return self._base_adt_path

    def _build_adt_url(self, adt_uri):
        """Creates complete URL from a fragment of ADT URI
           where the fragment usually refers to an ADT object
        """

        return f'{self._base_adt_path}/{adt_uri}'

    def _get_session(self):
        """Returns the working HTTP session.
           The session's cookies are populated by executing a dummy GET which
           also retrieves X-CSRF-Token.
        """

        if self._session is None:
            try:
                self._session, _ = self._http_client.build_session()
            except HTTPRequestError as ex:
                # Because some systems do to not have /sap/bc/adt/core/discovery endpoint.
                if ex.response.status_code != 404:
                    raise ex

            # Reset login path to discovery because some system do no have /sap/bc/adt/core/discovery
            # endpoint but do have /sap/bc/adt/discovery.
            # Also if we lose session (403) we must use the /sap/bc/adt/discovery too. I do not know why!
            self._http_client.login_path = f'{self._base_adt_path}/discovery'

            response = None
            if self._session is None:
                # It means 404 on /sap/bc/adt/core/discovery endpoint,
                # try to build session with /sap/bc/adt/discovery endpoint
                self._session, response = self._http_client.build_session()

            if response is None:
                response = self._http_client.execute_with_session(self._session, 'GET', self._build_adt_url('discovery'))

            self._collection_types = _get_collection_accepts(response.text)

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

        resp = self._http_client.execute_with_session(session, method, url, params=params, headers=headers, body=body)

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

        uri = f'/{self._base_adt_path}/{basepath}'
        try:
            return self.collection_types[uri]
        except KeyError:
            return [default_mimetype]
