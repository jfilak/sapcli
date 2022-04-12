import copy
import json
import types
from typing import Dict, NamedTuple
from io import StringIO
from argparse import ArgumentParser

import unittest
from unittest.mock import patch

import sap.adt
import sap.cli.core


class Response:

    def __init__(self, text=None, status_code=None, headers=None, content_type=None, json=None):
        self.text = text
        self.status_code = status_code if status_code is not None else 200
        self.headers = headers or {}
        self._json = json

        if content_type is not None:
            if self.headers is None:
                self.headers = {}

            self.headers['Content-Type'] = content_type
            self.headers['content-type'] = content_type

    def json(self):
        if self._json is None:
            raise ValueError()

        return self._json

    @staticmethod
    def with_json(json=None, status_code=None, headers=None):
        return Response(json=json, content_type='application/json', headers=headers, status_code=status_code)

    @staticmethod
    def ok():
        return Response(status_code=200)


class Request(NamedTuple):

    method: str
    adt_uri: str
    headers: Dict
    body: str
    params: Dict

    @property
    def url(self):
        return self.adt_uri

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

    def assertEqual(self, other, asserter, json_body=False):
        asserter.assertEqual(self.to_short_str(), other.to_short_str())

        if json_body:
            asserter.assertEqual(json.loads(self.body), json.loads(other.body), f'Not matching JSON bodies for {self.to_short_str()}')
        else:
            asserter.assertEqual(self.body, other.body, f'Not matching bodies for {self.to_short_str()}')

        asserter.assertEqual(self.params, other.params, f'Not matching parameters for {self.to_short_str()}')
        asserter.assertEqual(self.headers, other.headers, f'Not matching parameters for {self.to_short_str()}')

    @staticmethod
    def get(adt_uri=None, headers=None, params=None, accept=None):
        if accept:
            headers = dict(headers or {})
            headers['Accept'] = accept

        return Request(method='GET', adt_uri=adt_uri, headers=headers, body=None, params=params)

    @staticmethod
    def get_json(uri=None, headers=None, params=None):
        return Request.get(adt_uri=uri, headers=headers, params=params, accept='application/json')

    @staticmethod
    def post(uri=None, headers=None, body=None, params=None, accept=None, content_type=None):
        if accept:
            headers = headers or {}
            headers['Accept'] = accept

        if content_type:
            headers = headers or {}
            headers['Content-Type'] = content_type

        return Request(method='POST', adt_uri=uri, headers=headers, body=body, params=params)

    @staticmethod
    def post_xml(uri=None, headers=None, body=None, params=None, accept=None):
        return Request.post(
                uri=uri,
                headers=headers,
                params=params,
                accept=accept,
                content_type='application/xml',
                body=body
            )


    @staticmethod
    def post_json(uri=None, headers=None, body=None, params=None, accept=None):
        headers = headers or {}
        headers.update({'Content-Type': 'application/json'})
        if accept:
            headers['Accept'] = accept

        json_body = json.dumps(body)
        return Request(method='POST', adt_uri=uri, headers=headers, body=json_body, params=params)

    @staticmethod
    def post_text(uri=None, headers=None, body=None, params=None, accept=None):
        headers = headers or {}
        headers.update({'Content-Type': 'text/plain'})
        if accept:
            headers['Accept'] = accept

        return Request(method='POST', adt_uri=uri, headers=headers, body=body, params=params)

    @staticmethod
    def delete(uri=None, headers=None, body=None, params=None):
        return Request(method='DELETE', adt_uri=uri, headers=headers, body=body, params=params)

    @staticmethod
    def put(uri=None, headers=None, body=None, params=None):
        return Request(method='PUT', adt_uri=uri, headers=headers, body=body, params=params)

    def clone_with_uri(self, uri):
        return Request(
            method=self.method,
            adt_uri=uri,
            headers=self.headers,
            body=self.body,
            params=self.params)

def ok_responses():

    while True:
        yield Response(text='', status_code=200, headers={})


class SimpleAsserter:

    def assertEqual(self, lhs, rhs, message=None):
        assert lhs == rhs, message


class RESTConnection(sap.rest.Connection):

    def __init__(self, responses=None, user='ANZEIGER', asserter=None):
        """
        Args:
            response: A list of Response instances or tuples (Response, Request)
                      if you want to automatically check the request. Ins such
                      case, you should also pass the argument asserter.
        """
        super().__init__('/icf/path', 'login/url', 'host', '100', user, 'mockpass')

        self.execs = list()
        self.asserter = asserter if asserter is not None else SimpleAsserter()
        self.set_responses_iter(ok_responses() if responses is None else iter(responses))

    def set_responses(self, *responses):
        if responses and isinstance(responses[0], list):
            responses = responses[0]

        self.set_responses_iter(iter(responses))

    def set_responses_iter(self, responses_iter):
        self._resp_iter = responses_iter

    def _get_session(self):
        return 'bogus session'

    def _build_url(self, uri_path):
        return uri_path

    def _retrieve(self, session, method, url, params=None, headers=None, body=None):
        req = Request(method, url, headers, body, params)
        self.execs.append(req)

        res = next(self._resp_iter)
        if res is None:
            res = next(ok_responses())

        if isinstance(res, tuple):
            exp_request = res[1]
            res = res[0]

            full_uri = self._build_url(exp_request.adt_uri)
            exp_request = exp_request.clone_with_uri(full_uri)

            exp_request.assertEqual(req, self.asserter)

        return (req, res)

    def mock_methods(self):
        return  [(e.method, e.adt_uri) for e in self.execs]


class ConnectionViaHTTP(sap.adt.ConnectionViaHTTP):

    def __init__(self, responses=None, user='ANZEIGER', collections=None, asserter=None):
        """
        Args:
            response: A list of Response instances or tuples (Response, Request)
                      if you want to automatically check the request. Ins such
                      case, you should also pass the argument asserter.
        """
        super().__init__('mockhost', 'mockclient', user, 'mockpass')

        self.collections = collections
        self.execs = list()
        self.asserter = asserter if asserter is not None else SimpleAsserter()
        self.set_responses_iter(ok_responses() if responses is None else iter(responses))

    def set_responses(self, *responses):
        if responses and isinstance(responses[0], list):
            responses = responses[0]

        self.set_responses_iter(iter(responses))

    def set_responses_iter(self, responses_iter):
        self._resp_iter = responses_iter

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
        print('Patching', spec)

        if not hasattr(self, '_patchers'):
            self._patchers = {}

        if spec in self._patchers:
            raise RuntimeError('Cannot patch patched %s' % (spec))

        patcher = patch(spec, **kwargs)
        self._patchers[spec] = patcher
        return patcher.__enter__()

    def patch_console(self, console=None):
        if console is None:
            console = BufferConsole()

        return self.patch('sap.cli.core.get_console', return_value=console)

    def tearDown(self):
        self.unpatch_all()

    def unpatch_all(self):
        print('Patcher tear down')

        if not hasattr(self, '_patchers'):
            return

        for patcher in self._patchers.values():
            patcher.__exit__(None, None, None)


class ConsoleOutputTestCase(unittest.TestCase):

    def setUp(self):
        self.console = BufferConsole()

    def assertEmptyConsole(self, console,):
        self.assertEqual(console.capout, '')
        self.assertEqual(console.caperr, '')

    def assertConsoleContents(self, console, stdout='', stderr=''):
        self.assertEqual(console.capout, stdout)
        self.assertEqual(console.caperr, stderr)


class GCTSLogMessages:

    def __init__(self, *messages):
        self.data = messages


class GCTSLogProtocol:

    def __init__(self, typ, protocol):
        self.data = {
            'type': typ,
            'protocol': protocol.data
        }


def make_gcts_log_entry(severity, message, time=None, user=None, section=None, action=None, code=None, protocol=None):
    entry = {'severity': severity, 'message': message}

    if time is not None:
        entry['time'] = time

    if user is not None:
        entry['user'] = user

    if section is not None:
        entry['section'] = section

    if action is not None:
        entry['action'] = action

    if code is not None:
        entry['code'] = code

    if protocol is not None:
        entry['protocol'] = protocol.data

    return entry


def make_gcts_log_error(message, time=None, user=None, section=None, action=None, code=None, protocol=None):
    return make_gcts_log_entry(
        'ERROR',
        message,
        time=time,
        user=user,
        section=section,
        action=action,
        code=code,
        protocol=protocol
    )


class GCTSLogBuilder:

    def __init__(self, errorLog=None, log=None, exception=None):
        self.errorLog = errorLog or list()
        self.log = log or list()
        self.exception = exception

    def get_contents(self):
        contents = {}
        contents['errorLog'] = self.errorLog or list()
        contents['log'] = self.log or list()
        contents['exception'] = self.exception or 'Server Side Exception'

        return contents

    def log_error(self, entry):
        self.log.append(entry)
        self.errorLog.append(entry)
        return self

    def log_exception(self, message, code):
        self.exception = message
        self.errorLog.append(make_gcts_log_error(message=message, code=code))
        return self


class TestRFCLibError(Exception):

    def __init__(self, message):
        super().__init__(message)


mod_exception = types.SimpleNamespace(RFCLibError=TestRFCLibError)
mod_pyrfc = types.SimpleNamespace(_exception=mod_exception)
