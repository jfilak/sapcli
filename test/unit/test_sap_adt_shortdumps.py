#!/usr/bin/env python3

import unittest

import sap.adt.shortdumps
from sap.errors import SAPCliError

from mock import Connection, Response

from fixtures_adt_shortdumps import (
    DUMPS_FEED_XML,
    DUMPS_FEED_XML_NO_AUTHOR,
    DUMP_FORMATTED,
)


class TestListDumps(unittest.TestCase):

    def test_list_dumps_sends_request(self):
        connection = Connection([Response(text=DUMPS_FEED_XML, status_code=200)])

        sap.adt.shortdumps.list_dumps(connection)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/runtime/dumps')

    def test_list_dumps_returns_entries(self):
        connection = Connection([Response(text=DUMPS_FEED_XML, status_code=200)])

        entries = sap.adt.shortdumps.list_dumps(connection)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['author'], 'DEVELOPER')
        self.assertEqual(entries[0]['id'], 'https://host/sap/bc/adt/runtime/dump/ABC123')

    def test_list_dumps_without_author(self):
        connection = Connection([Response(text=DUMPS_FEED_XML_NO_AUTHOR, status_code=200)])

        entries = sap.adt.shortdumps.list_dumps(connection)

        self.assertEqual(len(entries), 1)
        self.assertNotIn('author', entries[0])


class TestReadDump(unittest.TestCase):

    def test_read_dump_sends_request(self):
        connection = Connection([Response(text=DUMP_FORMATTED, status_code=200)])

        sap.adt.shortdumps.read_dump(connection, 'ABC123')

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/runtime/dump/ABC123/formatted')

    def test_read_dump_returns_text(self):
        connection = Connection([Response(text=DUMP_FORMATTED, status_code=200)])

        result = sap.adt.shortdumps.read_dump(connection, 'ABC123')

        self.assertEqual(result, DUMP_FORMATTED)

    def test_read_dump_empty_id_raises(self):
        connection = Connection()

        with self.assertRaises(SAPCliError) as caught:
            sap.adt.shortdumps.read_dump(connection, '   ')

        self.assertIn('No dump ID provided', str(caught.exception))
        self.assertEqual(len(connection.execs), 0)


if __name__ == '__main__':
    unittest.main()
