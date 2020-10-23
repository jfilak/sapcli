#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

from sap.rest.errors import UnauthorizedError


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
