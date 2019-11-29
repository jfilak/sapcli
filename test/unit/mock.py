import copy
from typing import Dict, NamedTuple
from io import StringIO
from argparse import ArgumentParser
from unittest.mock import patch

import sap.adt
import sap.cli.core


class Response:

    def __init__(self, text=None, status_code=None, headers=None, content_type=None):
        self.text = text
        self.status_code = status_code if status_code is not None else 200
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

    def to_short_str(self):
        return f'{self.method} {self.adt_uri}'

    def __str__(self):
        str_request = self.to_short_str()

        if self.params:
            str_request += '?' + '&'.join((f'{key}={value}' for (key, value) in self.params.items()))

        if self.headers:
            str_request += '\n' + '\n'.join((f'{key}: {value}' for (key, value) in self.headers.items()))

        if self.body:
            str_request += '\n' + self.body

    def assertEqual(self, other, asserter):
        asserter.assertEqual(self.to_short_str(), other.to_short_str())
        asserter.assertEqual(self.body, other.body, f'Not matching bodies for {self.to_short_str()}')
        asserter.assertEqual(self.params, other.params, f'Not matching parameters for {self.to_short_str()}')
        asserter.assertEqual(self.headers, other.headers, f'Not matching parameters for {self.to_short_str()}')

    @staticmethod
    def get(adt_uri=None, headers=None, body=None, params=None):
        return Request(method='GET', adt_uri=adt_uri, headers=headers, body=body, params=params)


    def clone_with_uri(self, uri):
        return Request(
            method=self.method,
            adt_uri=uri,
            headers=self.headers,
            body=self.body,
            params=self.params)

def ok_responses():

    yield Response(text='', status_code=200, headers={})


class SimpleAsserter:

    def assertEqual(self, lhs, rhs, message=None):
        assert lhs == rhs, message


class Connection(sap.adt.Connection):

    def __init__(self, responses=None, user='ANZEIGER', collections=None, asserter=None):
        """
        Args:
            response: A list of Response instances or tuples (Response, Request)
                      if you want to automatically check the request. Ins such
                      case, you should also pass the argument asserter.
        """
        super(Connection, self).__init__('mockhost', 'mockclient', user, 'mockpass')

        self.collections = collections
        self.execs = list()
        self._resp_iter = ok_responses() if responses is None else iter(responses)
        self.asserter = asserter if asserter is not None else SimpleAsserter()

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

        if isinstance(res, tuple):
            exp_request = res[1]
            res = res[0]

            full_uri = self._build_adt_url(exp_request.adt_uri)
            exp_request = exp_request.clone_with_uri(full_uri)

            exp_request.assertEqual(req, self.asserter)

        return (req, res)

    def mock_methods(self):
        return  [(e.method, e.adt_uri) for e in self.execs]

    def get_collection_types(self, basepath, default_mimetype):

        if self.collections is None:
            return [default_mimetype]

        return self.collections[f'/{self._adt_uri}/{basepath}']


class BufferConsole(sap.cli.core.PrintConsole):

    def __init__(self):
        self.std_output = StringIO()
        self.err_output = StringIO()

        super(BufferConsole, self).__init__(out_file=self.std_output, err_file=self.err_output)

    @property
    def capout(self):
        return self.std_output.getvalue()

    @property
    def caperr(self):
        return self.err_output.getvalue()


def patch_get_print_console_with_buffer():
    """Capture output printed out by sapcli.

        with patch_print_console_with_buffer() as fake_get_console:
            sap.cli.core.printout('Test!')
            sap.cli.core.printout('Yet another Test!')

        self.assertEqual(fake_get_console.return_value.std_output, 'Test!\nYet another Test!\n')
    """

    return patch('sap.cli.core.get_console', return_value=BufferConsole())


class GroupArgumentParser:

    def __init__(self, group_class):
        self._group = group_class()
        self._parser = ArgumentParser()
        self._group.install_parser(self._parser)

    def parse(self, *argv):
        return self._parser.parse_args(argv)


class PatcherTestCase:

    def patch(self, spec, **kwargs):
        if not hasattr(self, '_patchers'):
            self._patchers = {}

        if spec in self._patchers:
            raise RuntimeError('Cannot patch patched %s' % (spec))

        patcher = patch(spec, **kwargs)
        self._patchers[spec] = patcher
        return patcher.__enter__()

    def patch_console(self):
        return self.patch('sap.cli.core.get_console', return_value=BufferConsole())

    def tearDown(self):
        print('Patcher tear down')

        if not hasattr(self, '_patchers'):
            return

        for patcher in self._patchers.values():
            patcher.__exit__(None, None, None)
