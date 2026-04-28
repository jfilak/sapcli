"""OData connection helpers"""

import pyodata

import sap.http
from sap import get_logger


def mod_log():
    """OData Module logger"""

    return get_logger()


# pylint: disable=too-many-instance-attributes,too-few-public-methods
class Connection:
    """OData communication built on top of pyodata and requests.
    """

    client = None

    # pylint: disable=too-many-arguments
    def __init__(self, service, host, port, client, user, password, ssl, verify, ssl_server_cert=None,
                 session_initializer=None):
        """Parameters:
            - service: id of the odata service (e.g. UI5/ABAP_REPOSITORY_SRV)
            - host: string host name or IP of
            - port: string TCP/IP port for abap application server
            - client: string SAP client
            - user: string user name
            - password: string user password
            - ssl: boolean to switch between http and https
            - verify: boolean to switch SSL validation on/off
            - ssl_server_cert: optional path to a custom CA certificate file
            - session_initializer: optional HTTPSessionInitializer; when None,
                    BasicAuth with the given user/password is used
        """

        sap.http.setup_keepalive()

        service_path = f'sap/opu/odata/{service}'

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
            login_path=service_path,
            login_method='HEAD',
            session_initializer=session_initializer,
        )

        session, _ = self._http_client.build_session()

        base_url, _ = sap.http.build_url(ssl=ssl, host=host, port=port, path=service_path)
        self.client = pyodata.Client(base_url, session)
