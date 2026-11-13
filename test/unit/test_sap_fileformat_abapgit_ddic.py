#!/usr/bin/env python3

import unittest

import sap.fileformat.abapgit.ddic as ddic


class TestAdtToDdicDatatype(unittest.TestCase):

    def test_adt_name_differs(self):
        self.assertEqual(ddic.ADT_TO_DDIC_DATATYPE['STRING'], 'STRG')

    def test_same_names_are_not_mapped(self):
        self.assertNotIn('CHAR', ddic.ADT_TO_DDIC_DATATYPE)


class TestDdicNumber(unittest.TestCase):

    def test_zero_padded(self):
        self.assertEqual(ddic.ddic_number('10', 6), '000010')

    def test_integer(self):
        self.assertEqual(ddic.ddic_number(3, 4), '0003')

    def test_zero_is_not_written(self):
        self.assertIsNone(ddic.ddic_number('0', 6))

    def test_empty_is_not_written(self):
        self.assertIsNone(ddic.ddic_number('', 6))

    def test_none_is_not_written(self):
        self.assertIsNone(ddic.ddic_number(None, 6))


if __name__ == '__main__':
    unittest.main()
