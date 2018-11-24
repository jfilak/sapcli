#!/bin/python

import unittest

import sap.cli.abapclass


class TestCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.abapclass.CommandGroup()


if __name__ == '__main__':
    unittest.main()
