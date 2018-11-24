from sap.errors import SAPCliError

class HTTPRequestError(SAPCliError):

    def __init__(self, request, response):
        self.request = request
        self.response = response

    def __repr__(self):
        return '{status_code}\n{text}'.format(
            status_code=self.response.status_code, text=self.response.text)

    def __str__(self):
        return repr(self)
