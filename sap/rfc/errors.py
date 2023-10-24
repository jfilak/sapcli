"""Wrappers for RFC module errors"""
from sap.errors import SAPCliError


class RFCConnectionError(SAPCliError):
    """Wrapper for RFC connection error"""

    def __init__(self, host, user, message):
        self.message = f'[HOST:"{host}", USER:"{user}"] Error: {message}'

    def __str__(self):
        return f'RFC connection error: {self.message}'


class RFCLoginError(RFCConnectionError):
    """Wrapper for RFC Login error"""

    def __init__(self, host, user, exception):
        super().__init__(host, user, exception.message)


class RFCCommunicationError(RFCConnectionError):
    """Wrapper for RFC Communication error"""

    def __init__(self, host, user, exception):
        msg = exception.message.split('\n')
        msg = next(filter(lambda line: line.startswith('ERROR'), msg))
        msg = ' '.join(msg.split()[1:])
        super().__init__(host, user, msg)
