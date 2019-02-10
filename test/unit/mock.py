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


def ok_responses():

    yield Response(text='', status_code=200, headers={})


class Connection:

    def __init__(self, responses=None):
        self.execs = list()
        self._resp_iter = ok_responses() if responses is None else iter(responses)

    def execute(self, method, adt_uri, params=None, headers=None, body=None):
        self.execs.append(Request(method, adt_uri, headers, body, params))

        return next(self._resp_iter)
