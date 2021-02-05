'''Odata error classes tests'''
#!/usr/bin/env python3

# pylint: disable=missing-function-docstring

import unittest

from sap.errors import ResourceAlreadyExistsError

class TestResourceAlreadyExistsError(unittest.TestCase):
    '''Test ResourceAlreadyExistsError class'''

    def test_str_and_repr(self):
        inst = ResourceAlreadyExistsError()
        self.assertEqual(str(inst), 'Resource already exists')
