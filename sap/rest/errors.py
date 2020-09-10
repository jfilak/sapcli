"""HTTP related errors"""

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

    def __repr__(self):
        return '{status_code}\n{text}'.format(
            status_code=self.response.status_code, text=self.response.text)

    def __str__(self):
        return repr(self)
