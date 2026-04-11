#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

from sap.errors import SAPCliError

from sap.http.errors import (
    UnexpectedResponseContent,
    HTTPRequestError,
    UnauthorizedError,
    TimedOutRequestError,
)


class TestUnexpectedResponseContent(unittest.TestCase):

    def test_is_sapcli_error(self):
        error = UnexpectedResponseContent('application/xml', 'text/html', '<html/>')
        self.assertIsInstance(error, SAPCliError)

    def test_attributes(self):
        error = UnexpectedResponseContent('application/xml', 'text/html', '<html/>')

        self.assertEqual(error.expected, 'application/xml')
        self.assertEqual(error.received, 'text/html')
        self.assertEqual(error.content, '<html/>')

    def test_str(self):
        error = UnexpectedResponseContent('application/xml', 'text/html', '<html/>')

        self.assertEqual(str(error), 'Unexpected Content-Type: text/html with: <html/>')

    def test_str_empty_content(self):
        error = UnexpectedResponseContent('application/json', 'text/plain', '')

        self.assertEqual(str(error), 'Unexpected Content-Type: text/plain with: ')


class TestHTTPRequestError(unittest.TestCase):

    def _make_error(self, status_code, text):
        request = Mock()
        response = Mock()
        response.status_code = status_code
        response.text = text
        return HTTPRequestError(request, response)

    def test_is_sapcli_error(self):
        error = self._make_error(500, 'fail')
        self.assertIsInstance(error, SAPCliError)

    def test_attributes(self):
        request = Mock()
        response = Mock()
        response.status_code = 403

        error = HTTPRequestError(request, response)

        self.assertIs(error.request, request)
        self.assertIs(error.response, response)
        self.assertEqual(error.status_code, 403)

    def test_repr_with_header_and_message(self):
        html = (
            '<p class="errorTextHeader"> <span >403 Forbidden</span> </p>\n'
            '<p class="detailText"> <span id="msgText">Access denied.</span></p>\n'
        )
        error = self._make_error(403, html)

        self.assertEqual(repr(error), '403 Forbidden\nAccess denied.')

    def test_str_delegates_to_repr(self):
        html = (
            '<p class="errorTextHeader"> <span >403 Forbidden</span> </p>\n'
            '<p class="detailText"> <span id="msgText">Access denied.</span></p>\n'
        )
        error = self._make_error(403, html)

        self.assertEqual(str(error), repr(error))

    def test_repr_no_error_header(self):
        html = '<p class="detailText"> <span id="msgText">Some error.</span></p>'
        error = self._make_error(500, html)

        self.assertEqual(repr(error), '500\n' + html)

    def test_repr_no_error_message(self):
        html = '<p class="errorTextHeader"> <span >500 Server Error</span> </p>'
        error = self._make_error(500, html)

        self.assertEqual(repr(error), '500\n' + html)

    def test_repr_plain_text_response(self):
        error = self._make_error(500, 'Internal Server Error')

        self.assertEqual(repr(error), '500\nInternal Server Error')

    def test_repr_filters_server_time(self):
        html = (
            '<p class="errorTextHeader"> <span >403 Forbidden</span> </p>\n'
            '<p class="detailText"> <span id="msgText">Blocked by UCON.</span></p>\n'
            '<p class="detailText"> <span id="msgText">Server time: 2022-07-25</span></p>\n'
        )
        error = self._make_error(403, html)

        self.assertEqual(repr(error), '403 Forbidden\nBlocked by UCON.')

    def test_repr_multiline_error_message(self):
        html = (
            '<p class="errorTextHeader"> <span >403 Forbidden</span> </p>\n'
            '<p class="detailText"> <span id="msgText">Line one\nLine two.</span></p>\n'
        )
        error = self._make_error(403, html)

        self.assertEqual(repr(error), '403 Forbidden\nLine one Line two.')

    def test_repr_multiple_detail_messages(self):
        html = (
            '<p class="errorTextHeader"> <span >403 Forbidden</span> </p>\n'
            '<p class="detailText"> <span id="msgText">First error.</span></p>\n'
            '<p class="detailText"> <span id="msgText">Second error.</span></p>\n'
        )
        error = self._make_error(403, html)

        self.assertEqual(repr(error), '403 Forbidden\nFirst error.\nSecond error.')

    def test_repr_only_server_time_messages(self):
        """When all detail messages are Server time entries, error_msg is empty."""
        html = (
            '<p class="errorTextHeader"> <span >403 Forbidden</span> </p>\n'
            '<p class="detailText"> <span id="msgText">Server time: 2022-07-25</span></p>\n'
        )
        error = self._make_error(403, html)

        self.assertEqual(repr(error), '403\n' + html)

    def test_repr_empty_response_text(self):
        error = self._make_error(500, '')

        self.assertEqual(repr(error), '500\n')


class TestUnauthorizedError(unittest.TestCase):

    def _make_error(self):
        request = Mock()
        request.method = 'GET'
        request.url = 'https://example.com/sap/bc/adt'
        response = Mock()
        response.status_code = 401
        return UnauthorizedError(request, response, 'SAP*'), request, response

    def test_is_sapcli_error(self):
        error, _, _ = self._make_error()
        self.assertIsInstance(error, SAPCliError)

    def test_attributes(self):
        error, request, response = self._make_error()

        self.assertIs(error.request, request)
        self.assertIs(error.response, response)
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.method, 'GET')
        self.assertEqual(error.url, 'https://example.com/sap/bc/adt')
        self.assertEqual(error.user, 'SAP*')

    def test_repr(self):
        error, _, _ = self._make_error()

        self.assertEqual(repr(error), 'Authorization for the user "SAP*" has failed: GET https://example.com/sap/bc/adt')

    def test_str_delegates_to_repr(self):
        error, _, _ = self._make_error()

        self.assertEqual(str(error), repr(error))


class TestTimedOutRequestError(unittest.TestCase):

    def _make_error(self):
        request = Mock()
        request.method = 'POST'
        request.url = 'https://example.com/sap/bc/adt'
        return TimedOutRequestError(request, 30), request

    def test_is_sapcli_error(self):
        error, _ = self._make_error()
        self.assertIsInstance(error, SAPCliError)

    def test_attributes(self):
        error, request = self._make_error()

        self.assertIs(error.request, request)
        self.assertEqual(error.method, 'POST')
        self.assertEqual(error.url, 'https://example.com/sap/bc/adt')
        self.assertEqual(error.timeout, 30)

    def test_repr(self):
        error, _ = self._make_error()

        self.assertEqual(repr(error), 'The request POST https://example.com/sap/bc/adt took more than 30s')

    def test_str_delegates_to_repr(self):
        error, _ = self._make_error()

        self.assertEqual(str(error), repr(error))


if __name__ == '__main__':
    unittest.main()
