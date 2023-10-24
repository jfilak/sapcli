"""HTTP related errors"""

import re
from sap.errors import SAPCliError


class UnexpectedResponseContent(SAPCliError):
    """Exception for unexpected responses content"""

    def __init__(self, expected, received, content):
        super().__init__()

        self.expected = expected
        self.received = received
        self.content = content

    def __str__(self):
        return f'Unexpected Content-Type: {self.received} with: {self.content}'


class HTTPRequestError(SAPCliError):
    """Exception for unexpected HTTP responses"""

    def __init__(self, request, response):
        super().__init__()

        self.request = request
        self.response = response
        self.status_code = response.status_code

    def _get_error_header(self):
        return re.search('.*<p class="errorTextHeader"> *<span >(.*)</span> *</p>.*', self.response.text)

    def _get_error_message(self):
        error_msg = re.finditer('<p class="detailText"> *<span id="msgText">(.*?)</span> *</p>', self.response.text,
                                flags=re.DOTALL)
        error_msg = [msg[1] for msg in error_msg if 'Server time:' not in msg[1]]
        error_msg = [' '.join(msg.split('\n')) for msg in error_msg]
        error_msg = '\n'.join(error_msg)

        return error_msg

    def __repr__(self):
        error_text_header = self._get_error_header()
        error_msg = self._get_error_message()
        if error_text_header and error_msg:
            return f'{error_text_header[1]}\n{error_msg}'

        return f'{self.response.status_code}\n{self.response.text}'

    def __str__(self):
        return repr(self)


class UnauthorizedError(SAPCliError):
    """Exception for unauthorized """

    def __init__(self, request, response, user):
        super().__init__()

        self.request = request
        self.response = response
        self.status_code = response.status_code
        self.method = request.method
        self.url = request.url
        self.user = user

    def __repr__(self):
        return f'Authorization for the user "{self.user}" has failed: {self.method} {self.url}'

    def __str__(self):
        return repr(self)


class TimedOutRequestError(SAPCliError):
    """Exception for timeout requests"""

    def __init__(self, request, timeout):
        super().__init__()

        self.request = request
        self.method = request.method
        self.url = request.url
        self.timeout = timeout

    def __repr__(self):
        return f'The request {self.method} {self.url} took more than {self.timeout}s'

    def __str__(self):
        return repr(self)


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
