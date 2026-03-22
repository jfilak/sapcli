#!/bin/python

import unittest

from sap.adt.errors import InvalidURIError
from sap.adt.uri import StatementPosition, parse_statement_uri, parse_object_implementation_start_uri


class TestParseStatementUri(unittest.TestCase):

    def test_source_main_path(self):
        uri = '/sap/bc/adt/oo/classes/zcx_foo/source/main#start=183,1;end=183,20'
        result = parse_statement_uri(uri)
        self.assertEqual(result.object_name, 'zcx_foo')
        self.assertEqual(result.object_part, 'source/main')
        self.assertEqual(result.start_line, 183)
        self.assertEqual(result.start_column, 1)
        self.assertEqual(result.end_line, 183)
        self.assertEqual(result.end_column, 20)

    def test_includes_implementations_path(self):
        uri = '/sap/bc/adt/oo/classes/zcx_foo/includes/implementations#start=50,4;end=50,35'
        result = parse_statement_uri(uri)
        self.assertEqual(result.object_name, 'zcx_foo')
        self.assertEqual(result.object_part, 'includes/implementations')
        self.assertEqual(result.start_line, 50)
        self.assertEqual(result.start_column, 4)
        self.assertEqual(result.end_line, 50)
        self.assertEqual(result.end_column, 35)

    def test_multi_line_range(self):
        uri = '/sap/bc/adt/oo/classes/foo/source/main#start=340,1;end=343,12'
        result = parse_statement_uri(uri)
        self.assertEqual(result.start_line, 340)
        self.assertEqual(result.start_column, 1)
        self.assertEqual(result.end_line, 343)
        self.assertEqual(result.end_column, 12)

    def test_missing_fragment_raises(self):
        with self.assertRaises(InvalidURIError):
            parse_statement_uri('/sap/bc/adt/oo/classes/foo/source/main')

    def test_missing_end_raises(self):
        with self.assertRaises(InvalidURIError):
            parse_statement_uri('/sap/bc/adt/oo/classes/foo/source/main#start=52,9')

    def test_returns_statement_position_namedtuple(self):
        uri = '/sap/bc/adt/oo/classes/foo/source/main#start=1,1;end=1,10'
        result = parse_statement_uri(uri)
        self.assertIsInstance(result, StatementPosition)


class TestParseObjectImplementationStartUri(unittest.TestCase):

    def test_line_and_column(self):
        self.assertEqual(parse_object_implementation_start_uri('/foo/source/main#start=52,9'), (52, 9))

    def test_missing_column_defaults_to_zero(self):
        self.assertEqual(parse_object_implementation_start_uri('/foo#start=10'), (10, 0))

    def test_empty_string_returns_zeros(self):
        self.assertEqual(parse_object_implementation_start_uri(''), (0, 0))

    def test_none_returns_zeros(self):
        self.assertEqual(parse_object_implementation_start_uri(None), (0, 0))


if __name__ == '__main__':
    unittest.main()
