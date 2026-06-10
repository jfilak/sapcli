"""Verify TLS server certificates against the operating system trust store.

By default Python requests validates server certificates against the CA bundle
shipped with the certifi package, ignoring CAs installed into the operating
system (e.g. corporate root CAs added via update-ca-certificates, the Windows
Certificate Store or the macOS Keychain).

The optional truststore package bridges that gap: a single inject_into_ssl()
call makes the whole ssl/urllib3/requests stack validate against the OS trust
store, so it covers every sapcli HTTP path (ADT, REST/gCTS, OData, OAuth token
fetch and remote config download) at once.
"""

from sap import get_logger
from sap.errors import SAPCliError


class TruststoreNotAvailableError(SAPCliError):
    """Raised when the OS trust store was requested but truststore is missing."""

    def __init__(self):
        super().__init__(
            'Cannot verify SSL certificates against the operating system trust '
            'store: the "truststore" package could not be imported. It is a '
            'regular sapcli dependency, so this usually means the installation '
            'is incomplete; reinstall sapcli (or run: pip install truststore)')


# Non-empty once inject_into_ssl() has run; guards against injecting twice.
_INJECTED: list = []


def enable_system_cert_store():
    """Make Python requests verify TLS server certificates against the operating
       system trust store instead of the bundled certifi CA list.

       Idempotent: repeated calls inject only once.

       Raises TruststoreNotAvailableError when the truststore package cannot be
       imported.
    """

    if _INJECTED:
        return

    try:
        import truststore
    except ImportError as ex:
        raise TruststoreNotAvailableError() from ex

    truststore.inject_into_ssl()
    _INJECTED.append(True)
    get_logger().info('Verifying SSL certificates against the operating system trust store')
