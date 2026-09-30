#!/usr/bin/env python3

import unittest

import sap.adt.feeds

from mock import Connection, Response

from fixtures_adt_feeds import FEEDS_XML, FEEDS_XML_EMPTY
from fixtures_adt_shortdumps import DUMPS_FEED_XML, DUMPS_FEED_XML_NO_AUTHOR


class TestParseFeed(unittest.TestCase):

    def test_parses_all_entries(self):
        entries = sap.adt.feeds.parse_feed(DUMPS_FEED_XML)

        self.assertEqual(len(entries), 2)

    def test_parses_entry_fields(self):
        entries = sap.adt.feeds.parse_feed(DUMPS_FEED_XML)

        self.assertEqual(entries[0]['author'], 'DEVELOPER')
        self.assertEqual(entries[0]['title'], 'CX_SY_ZERODIVIDE\nDivision by zero')
        self.assertEqual(entries[0]['updated'], '2024-01-15T10:30:00Z')
        self.assertEqual(entries[0]['id'], 'https://host/sap/bc/adt/runtime/dump/ABC123')

    def test_omits_missing_author(self):
        entries = sap.adt.feeds.parse_feed(DUMPS_FEED_XML_NO_AUTHOR)

        self.assertEqual(len(entries), 1)
        self.assertNotIn('author', entries[0])

    def test_empty_feed_yields_no_entries(self):
        entries = sap.adt.feeds.parse_feed(FEEDS_XML_EMPTY)

        self.assertEqual(entries, [])


class TestListFeeds(unittest.TestCase):

    def test_list_feeds_sends_request(self):
        connection = Connection([Response(text=FEEDS_XML, status_code=200)])

        sap.adt.feeds.list_feeds(connection)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/feeds')

    def test_list_feeds_returns_entries(self):
        connection = Connection([Response(text=FEEDS_XML, status_code=200)])

        entries = sap.adt.feeds.list_feeds(connection)

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['title'], 'ABAP Runtime Errors')
        self.assertEqual(entries[0]['id'], '/sap/bc/adt/runtime/dumps')


class TestReadFeed(unittest.TestCase):

    def test_read_feed_sends_request_to_complete_url(self):
        connection = Connection([Response(text=FEEDS_XML, status_code=200)])

        sap.adt.feeds.read_feed(connection, '/sap/bc/adt/runtime/syslog')

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'GET')
        # complete_url=True means the URL is used verbatim
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/runtime/syslog')

    def test_read_feed_returns_entries(self):
        connection = Connection([Response(text=FEEDS_XML, status_code=200)])

        entries = sap.adt.feeds.read_feed(connection, '/sap/bc/adt/runtime/syslog')

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1]['title'], 'System Log')


if __name__ == '__main__':
    unittest.main()
