"""Wrappers for RFC module errors"""
from sap.errors import SAPCliError


class RFCConnectionError(SAPCliError):
    """Wrapper for RFC connection error"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'RFC connection error: {self.message}'


class RFCLoginError(RFCConnectionError):
    """Wrapper for RFC Login error"""

    def __init__(self, exception):
        super().__init__(exception.message)


class RFCCommunicationError(RFCConnectionError):
    """Wrapper for RFC Communication error"""

    def __init__(self, exception):
        msg = exception.message.split('\n')
        msg = next(filter(lambda line: line.startswith('ERROR'), msg))
        msg = ' '.join(msg.split()[1:])
        super().__init__(msg)
