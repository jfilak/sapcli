#!/bin/python

import unittest

import sap.adt

from fixtures_adt import DummyADTObject


connection = sap.adt.Connection('nohost', 'noclient', 'nouser', 'nopassword')

class TestAUnit(unittest.TestCase):

    def test_build_tested_object_uri(self):
        victory = DummyADTObject()

        victory_uri = sap.adt.AUnit.build_tested_object_uri(connection, victory)
        self.assertEquals(victory_uri, '/sap/bc/adt/awesome/success/noobject')


if __name__ == '__main__':
    unittest.main()
