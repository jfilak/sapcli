#!/usr/bin/env python3

import unittest
import sap.adt

from mock import Connection, Response, Request
from fixtures_adt_table import TABLE_DEFINITION_ADT_XML, TABLE_NAME, CREATE_TABLE_ADT_XML


class TestADTTable(unittest.TestCase):

    def test_table_fetch(self):
        connection = Connection([Response(text=TABLE_DEFINITION_ADT_XML, status_code=200, headers={})])

        table = sap.adt.Table(connection, TABLE_NAME)
        table.fetch()

        self.assertEqual(table.name, TABLE_NAME)
        self.assertEqual(table.active, 'active')
        self.assertEqual(table.master_language, 'EN')
        self.assertEqual(table.description, 'Test table')

    def test_table_serialize(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='Test table', language='EN', master_language='EN',
                                       responsible='ANZEIGER')
        table = sap.adt.Table(connection, TABLE_NAME, package='PACKAGE', metadata=metadata)
        table.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/ddic/tables',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.tables.v2+xml; charset=utf-8'},
            body=bytes(CREATE_TABLE_ADT_XML, 'utf-8'),
            params=None
        )
        self.assertEqual(connection.execs[0], expected_request)
