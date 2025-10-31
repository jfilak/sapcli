"""gCTS Error wrappers"""

from sap.errors import SAPCliError


class GCTSRequestError(SAPCliError):
    """Base gCTS error type"""

    def __init__(self, messages):
        super().__init__()

        self.messages = messages

    def __repr__(self):
        return f'gCTS exception: {self.messages["exception"]}'

    def __str__(self):
        return repr(self)


class GCTSRepoAlreadyExistsError(GCTSRequestError):
    """A repository already exists"""

    # pylint: disable=unnecessary-pass
    pass


class GCTSRepoNotExistsError(GCTSRequestError):
    """A repository does not exist"""

    def __init__(self, messages):
        super().__init__(messages)
        self.messages['exception'] = 'Repository does not exist'


class GCTSRepoCloneError(GCTSRequestError):
    """A repository clone error"""

    def __init__(self, messages):
        super().__init__(messages)
        self.messages['exception'] = 'Repository unable to clone. Already cloned or in use'


class GCTSRepoCloneTaskDeleteError(GCTSRequestError):
    """A repository clone task delete error"""

    def __init__(self, messages):
        super().__init__(messages)
        self.messages['exception'] = 'Task unable to delete. Already performed clone operation.'


def exception_from_http_error(http_error):
    """Converts HTTPRequestError to proper instance"""

    if 'application/json' not in http_error.response.headers.get('Content-Type', ''):
        return http_error

    messages = http_error.response.json()

    log = messages.get('log', None)
    if log and log[0].get('message', '').endswith('Error action CREATE_REPOSITORY Repository already exists'):
        return GCTSRepoAlreadyExistsError(messages)

    exception = messages.get('exception', None)
    if exception == 'No relation between system and repository':
        return GCTSRepoNotExistsError(messages)

    return GCTSRequestError(messages)
