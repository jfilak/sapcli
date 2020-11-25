'''Odata error classes tests'''
#!/usr/bin/env python3

# pylint: disable=missing-function-docstring

import unittest
from unittest.mock import Mock

from sap.odata.errors import (
    HTTPRequestError,
    UnauthorizedError,
    TimedOutRequestError
)

class TestOdataHTTPRequestError(unittest.TestCase):
    '''Test Odata HTTPRequestError class'''

    def test_str_and_repr(self):
        response = Mock()
        response.status_code = 'STATUS'
        response.text = 'TEXT'

        inst = HTTPRequestError('REQ', response)

        self.assertEqual(str(inst), 'STATUS\nTEXT')
        self.assertEqual(inst.response, response)
        self.assertEqual(inst.request, 'REQ')

class TestOdataUnauthorizedError(unittest.TestCase):
    '''Test Odata UnauthorizedError class'''

    def test_str_and_repr(self):
        request = Mock()
        request.method = 'METHOD'
        request.url = 'URL'

        inst = UnauthorizedError(request, 'RESP', 'USER')

        self.assertEqual(str(inst), 'Authorization for the user "USER" has failed: METHOD URL')
        self.assertEqual(inst.response, 'RESP')

class TestOdataTimedOutRequestError(unittest.TestCase):
    '''Test Odata TimedOutRequestError class'''

    def test_str_and_repr(self):
        request = Mock()
        request.method = 'METHOD'
        request.url = 'URL'

        inst = TimedOutRequestError(request, 3)

        self.assertEqual(str(inst), 'The request METHOD URL took more than 3s')
        self.assertEqual(inst.request, request)
