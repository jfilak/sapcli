from typing import Dict, NamedTuple


class Response(NamedTuple):

    text: str
    status_code: int
    headers: Dict


class Request(NamedTuple):

    method: str
    adt_uri: str
    headers: Dict
    body: str
    params: Dict


class Connection:

    def __init__(self, responses=None):
        self.execs = list()

        self._resp_iter = None
        if responses is not None:
            self._resp_iter = iter(responses)

    def execute(self, method, adt_uri, params=None, headers=None, body=None):
        self.execs.append(Request(method, adt_uri, headers, body, params))

        if self._resp_iter is not None:
            return next(self._resp_iter)

        return None
