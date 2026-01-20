"""Wrappers for RFC module errors"""
from sap.errors import SAPCliError


class RFCConnectionError(SAPCliError):
    """Wrapper for RFC connection error"""

    def __init__(self, host, user, message):
        self.message = f'[HOST:"{host}", USER:"{user}"]: {message}'

    def __str__(self):
        return f'RFC Connection Error: {self.message}'


class RFCLoginError(RFCConnectionError):
    """Wrapper for RFC Login error"""

    def __init__(self, host, user, exception):
        super().__init__(host, user, exception.message)


class RFCCommunicationError(RFCConnectionError):
    """Wrapper for RFC Communication error"""

    def __init__(self, host, user, exception):
        # Convert:
        # LOCATION    CPIC (TCP/IP) on local host with Unicode
        # ERROR       partner
        #             'very.long.dns.name.for.testing
        #             .com:3301' not reached
        # TIME        Tue Jan 20 17:44:07 2026
        # RELEASE     753
        # COMPONENT   NI (network interface)
        # VERSION     40
        # RC          -10
        # MODULE      /bas/753_REL/src/base/ni/nixxi.cpp
        # LINE        3458
        # DETAIL      NiPConnect2: 10.10.10.7:3301
        # SYSTEM CALL connect
        # ERRNO       111
        # ERRNO TEXT  Connection refused
        # COUNTER     6
        #
        # To: partner 'very.long.dns.name.for.testing.com:3301' not reached

        msg = ""
        error_section = False
        for line in exception.message.split('\n'):
            if line.startswith('ERROR'):
                error_section = True
                msg = line.replace('ERROR', '').strip() + ' '
            elif error_section:
                if not line[0].isspace():
                    error_section = False
                else:
                    msg += line.strip()

        super().__init__(host, user, msg.strip())
