#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

from fixtures_sap_rest_error import (
    GCTS_RESPONSE_FORBIDDEN,
    GCTS_RESPONSE_FORBIDDEN_NO_ERROR_HEADER,
    GCTS_RESPONSE_FORBIDDEN_NO_ERROR_MESSAGE,
)

from sap.rest.errors import (
    UnauthorizedError,
    TimedOutRequestError,
    HTTPRequestError,
)


class TestUnauthorizedError(unittest.TestCase):

    def test_str_and_repr(self):
        request = Mock()
        request.method = "GET"
        request.url = "http://example.com"
        response = Mock()
        user = "anzeiger"

        inst = UnauthorizedError(request, response, user)

        self.assertEqual(str(inst), f'Authorization for the user "{user}" has failed: {request.method} {request.url}')
        self.assertEqual(inst.response, response)


class TestTimeoutError(unittest.TestCase):

    def test_str_and_repr(self):
        request = Mock()
        request.method = "GET"
        request.url = "http://example.com"
        timeout = float(10)

        inst = TimedOutRequestError(request, timeout)

        self.assertEqual(str(inst), f'The request {request.method} {request.url} took more than {timeout}s')


class TestHttpRequestError(unittest.TestCase):

    def test_str_and_repr_with_match(self):
        response = GCTS_RESPONSE_FORBIDDEN

        inst = HTTPRequestError('Request', response)

        self.assertEqual(str(inst), '403 Forbidden\n'
                                    'The request has been blocked by UCON.\n'
                                    'And the multiline error message.')

    def test_str_and_repr_no_error_header(self):
        response = GCTS_RESPONSE_FORBIDDEN_NO_ERROR_HEADER

        inst = HTTPRequestError('Request', response)

        self.assertEqual(str(inst), f'{response.status_code}\n{response.text}')

    def test_str_and_repr_no_error_message(self):
        response = GCTS_RESPONSE_FORBIDDEN_NO_ERROR_MESSAGE

        inst = HTTPRequestError('Request', response)

        self.assertEqual(str(inst), f'{response.status_code}\n{response.text}')
