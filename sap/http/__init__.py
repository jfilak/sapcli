"""HTTP connection helpers and shared error types"""

import socket

from urllib3.connection import HTTPConnection

from sap import get_logger


KEEPALIVE_CONFIGURED = False


def mod_log():
    """HTTP Module logger"""

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


# Re-export submodule contents for backward compatibility
# pylint: disable=wrong-import-position

from sap.http.errors import (  # noqa: E402, F401  # pylint: disable=unused-import
    UnexpectedResponseContent,
    HTTPRequestError,
    UnauthorizedError,
    TimedOutRequestError,
)

from sap.http.client import (  # noqa: E402, F401  # pylint: disable=unused-import
    build_query_args,
    build_url,
    default_http_error_handler,
    HTTPClient,
    requests,
)
