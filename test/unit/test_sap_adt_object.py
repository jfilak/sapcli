#!/bin/python

import unittest

import sap.adt

from fixtures_adt import DummyADTObject


class TestADTObject(unittest.TestCase):

    def test_uri(self):
        victory = DummyADTObject()

        self.assertEquals(victory.uri, 'awesome/success/noobject')


if __name__ == '__main__':
    unittest.main()
