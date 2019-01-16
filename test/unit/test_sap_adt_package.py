#!/bin/python

import unittest

import sap.adt


class TestADTPackage(unittest.TestCase):

    def test_init(self):
        adt_package = sap.adt.Package(None, 'devc')


if __name__ == '__main__':
    unittest.main()
