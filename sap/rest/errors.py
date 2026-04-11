"""HTTP related errors"""

from sap.errors import SAPCliError

from sap.http import (  # noqa: F401  # pylint: disable=unused-import
    HTTPRequestError,
    UnexpectedResponseContent,
    UnauthorizedError,
    TimedOutRequestError,
)


class GCTSConnectionError(SAPCliError):
    """Exception for connection errors"""

    def __init__(self, host, port, ssl, message):
        super().__init__()
        msg = f'[HOST:"{host}", PORT:"{port}", SSL:"{ssl}"] Error: '
        if 'Errno -5' in message:
            msg += 'Name resolution error. Check the HOST configuration.'
        elif 'Errno 111' in message:
            msg += 'Cannot connect to the system. Check the HOST and PORT configuration.'
        else:
            msg += message
        self.message = msg

    def __str__(self):
        return f'GCTS connection error: {self.message}'
