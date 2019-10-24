from typing import Dict, NamedTuple

import sap.adt


class Response:

    def __init__(self, text=None, status_code=None, headers=None, content_type=None):
        self.text = text
        self.status_code = status_code
        self.headers = headers

        if content_type is not None:
            if self.headers is None:
                self.headers = {}

            self.headers['Content-Type'] = content_type


class Request(NamedTuple):

    method: str
    adt_uri: str
    headers: Dict
    body: str
    params: Dict


def ok_responses():

    yield Response(text='', status_code=200, headers={})


class Connection(sap.adt.Connection):

    def __init__(self, responses=None, user='ANZEIGER', collections=None):
        super(Connection, self).__init__('mockhost', 'mockclient', user, 'mockpass')

        self.collections = collections
        self.execs = list()
        self._resp_iter = ok_responses() if responses is None else iter(responses)

    def _get_session(self):
        return 'bogus session'

    def _build_adt_url(self, adt_uri):
        return f'/{self.uri}/{adt_uri}'

    def _retrieve(self, session, method, url, params=None, headers=None, body=None):
        req = Request(method, url, headers, body, params)
        self.execs.append(req)

        res = next(self._resp_iter)
        if res is None:
            res = next(ok_responses())

        return (req, res)

    def mock_methods(self):
        return  [(e.method, e.adt_uri) for e in self.execs]

    def get_collection_types(self, basepath, default_mimetype):

        if self.collections is None:
            return [default_mimetype]

        return self.collections[f'/{self._adt_uri}/{basepath}']
