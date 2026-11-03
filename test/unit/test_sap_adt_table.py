#!/usr/bin/env python3

import unittest
import sap.adt

from mock import Connection, Response, Request
from unittest.mock import patch

from fixtures_adt_table import TABLE_DEFINITION_ADT_XML, TABLE_NAME, CREATE_TABLE_ADT_XML, TABLE_SETTINGS_NAME, \
    TABLE_SETTINGS_ADT_GET_RESPONSE_XML, TABLE_SETTINGS_ADT_PUT_REQUEST_XML


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


class TestADTTableSettings(unittest.TestCase):

    def test_table_settings_fetch(self):
        connection = Connection([Response(text=TABLE_SETTINGS_ADT_GET_RESPONSE_XML, status_code=200, headers={})])

        settings = sap.adt.TableSettings(connection, TABLE_SETTINGS_NAME)
        settings.fetch()

        self.assertEqual(connection.execs[0].adt_uri, f'/sap/bc/adt/ddic/db/settings/{TABLE_SETTINGS_NAME.lower()}')
        self.assertEqual(settings.description, 'No maintenance')
        self.assertEqual(settings.data_class, 'APPL0')
        self.assertEqual(settings.size_category, '2')
        self.assertEqual(settings.buffering.allowed, 'X')
        self.assertEqual(settings.buffering.type, 'G')
        self.assertEqual(settings.buffering.area_key_fields, '1')
        self.assertEqual(settings.storage_type, 'C')
        self.assertEqual(settings.sharing_type, '')
        self.assertEqual(settings.load_unit, '')
        self.assertEqual(settings.logging_enabled, 'false')

    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
    def test_table_settings_push(self, fake_lock, fake_unlock):
        connection = Connection([Response(text=TABLE_SETTINGS_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
                                 Response(text='', status_code=200, headers={})])

        settings = sap.adt.TableSettings(connection, TABLE_SETTINGS_NAME)
        settings.fetch()
        settings.data_class = 'APPL1'
        settings.size_category = '3'
        settings.buffering.allowed = 'N'
        settings.buffering.type = ''
        settings.buffering.area_key_fields = '0'
        settings.logging_enabled = 'true'

        with settings.open_editor() as editor:
            editor.push()

        self.assertEqual(connection.execs[1].method, 'PUT')
        self.assertEqual(connection.execs[1].adt_uri, f'/sap/bc/adt/ddic/db/settings/{TABLE_SETTINGS_NAME.lower()}')
        self.assertEqual(connection.execs[1].headers,
                         {'Content-Type': 'application/vnd.sap.adt.table.settings.v2+xml; charset=utf-8'})
        self.assertEqual(connection.execs[1].params, {'lockHandle': 'lock_handle'})
        self.maxDiff = None
        # ADT drops the values of the settings if the request contains packageRef
        self.assertEqual(connection.execs[1].body.decode('utf-8'), TABLE_SETTINGS_ADT_PUT_REQUEST_XML)
