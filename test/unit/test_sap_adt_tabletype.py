#!/usr/bin/env python3

import unittest

import sap.adt
import sap.adt.tabletype
from sap.adt.marshalling import Marshal

from mock import Connection, Response, Request
from fixtures_sap_adt_tabletype import (
    TABLE_TYPE_NAME,
    TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML,
    TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML,
    TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML,
    TABLE_TYPE_ADT_GET_RANGE_RESPONSE_XML,
    TABLE_TYPE_ADT_NEW_OBJECT_REQUEST_XML,
    TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML,
    TABLE_TYPE_ADT_DEFINE_SORTED_REQUEST_XML,
    TABLE_TYPE_ADT_SECONDARY_KEYS_REQUEST_XML,
)


def fetch_table_type(response_xml):
    connection = Connection([Response(text=response_xml, status_code=200, headers={})])

    table_type = sap.adt.TableType(connection, TABLE_TYPE_NAME)
    table_type.fetch()

    return (connection, table_type)


class TestADTTableType(unittest.TestCase):

    def test_table_type_objtype(self):
        table_type = sap.adt.TableType(Connection(), TABLE_TYPE_NAME)

        self.assertEqual(table_type.objtype.code, 'TTYP/DA')
        self.assertEqual(table_type.uri, f'ddic/tabletypes/{TABLE_TYPE_NAME.lower()}')

    def test_table_type_fetch_request(self):
        connection, _ = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].adt_uri, f'/sap/bc/adt/ddic/tabletypes/{TABLE_TYPE_NAME.lower()}')

    def test_table_type_fetch_header(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        self.assertEqual(table_type.name, TABLE_TYPE_NAME)
        self.assertEqual(table_type.description, 'Test table type')
        self.assertEqual(table_type.active, 'new')
        self.assertEqual(table_type.master_language, 'EN')
        self.assertEqual(table_type.master_system, 'A4H')
        self.assertEqual(table_type.responsible, 'DEVELOPER')
        self.assertEqual(table_type.reference.name, '$TMP')

    def test_table_type_fetch_row_type_predefined(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        self.assertEqual(table_type.row_type.type_kind, 'predefinedAbapType')
        self.assertEqual(table_type.row_type.type_name, '')
        self.assertEqual(table_type.row_type.built_in_type.data_type, 'CHAR')
        self.assertEqual(table_type.row_type.built_in_type.length, '000001')
        self.assertEqual(table_type.row_type.built_in_type.decimals, '000000')
        self.assertEqual(table_type.row_type.range_type, '')

    def test_table_type_fetch_row_type_range(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_RANGE_RESPONSE_XML)

        self.assertEqual(table_type.row_type.type_kind, 'rangeTypeOnDataelement')
        self.assertEqual(table_type.row_type.type_name, '/AIF/NRT_MSGGUID_E')
        self.assertEqual(table_type.row_type.built_in_type.data_type, 'RAW')
        self.assertEqual(table_type.row_type.built_in_type.length, '000016')
        self.assertEqual(table_type.row_type.range_type, '/AIF/NRT_MSGGUID_RANGE_S')

    def test_table_type_fetch_access(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML)

        self.assertEqual(table_type.initial_row_count, '00000')
        self.assertEqual(table_type.access_type, 'sorted')

    def test_table_type_fetch_primary_key_standard(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        primary_key = table_type.primary_key
        self.assertEqual(primary_key.is_visible, 'true')
        self.assertEqual(primary_key.is_editable, 'true')
        self.assertEqual(primary_key.definition, 'standard')
        self.assertEqual(primary_key.kind, 'nonUnique')
        self.assertEqual(primary_key.components.is_visible, 'false')
        self.assertEqual(len(primary_key.components), 0)
        self.assertEqual(primary_key.alias, '')

    def test_table_type_fetch_primary_key_components(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML)

        primary_key = table_type.primary_key
        self.assertEqual(primary_key.definition, 'keyComponents')
        self.assertEqual(primary_key.kind, 'unique')
        self.assertEqual(primary_key.components.is_visible, 'true')
        self.assertEqual([component.name for component in primary_key.components], ['TYPE', 'ID'])

    def test_table_type_fetch_secondary_keys_none(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        secondary_keys = table_type.secondary_keys
        self.assertEqual(secondary_keys.is_visible, 'true')
        self.assertEqual(secondary_keys.is_editable, 'true')
        self.assertEqual(secondary_keys.allowed, 'notSpecified')
        self.assertEqual(secondary_keys.keys, [])

    def test_table_type_fetch_secondary_keys(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML)

        secondary_keys = table_type.secondary_keys
        self.assertEqual(len(secondary_keys.keys), 1)

        secondary_key = secondary_keys.keys[0]
        self.assertEqual(secondary_key.identifier, 'PATH_LINE')
        self.assertEqual(secondary_key.description, 'key for field path and line number')
        self.assertEqual(secondary_key.language, 'E')
        self.assertEqual(secondary_key.access, 'nonUniqueSorted')
        self.assertEqual(secondary_key.definition, 'keyComponents')
        self.assertEqual(secondary_key.components.is_visible, 'true')
        self.assertEqual([component.name for component in secondary_key.components], ['FIELD_PATH', 'LINE_NR'])

    def test_table_type_fetch_value_helps(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        value_helps = table_type.value_helps
        self.assertEqual([value_help.key for value_help in value_helps.type_kind_values],
                         ['dictionaryType', 'predefinedAbapType', 'refToPredefinedAbapType', 'refToDictionaryType',
                          'refToClassOrInterfaceType', 'rangeTypeOnPredefinedType', 'rangeTypeOnDataelement'])
        self.assertEqual([value_help.key for value_help in value_helps.key_definition_values],
                         ['standard', 'rowType', 'keyComponents', 'empty', 'notSpecified'])
        self.assertEqual([value_help.key for value_help in value_helps.key_kind_values],
                         ['unique', 'nonUnique', 'notSpecified'])
        self.assertEqual([value_help.key for value_help in value_helps.access_type_values],
                         ['standard', 'sorted', 'hashed', 'index', 'notSpecified'])
        self.assertEqual([value_help.key for value_help in value_helps.sec_key_access_values],
                         ['uniqueHashed', 'uniqueSorted', 'nonUniqueSorted'])
        self.assertEqual([value_help.key for value_help in value_helps.sec_key_definition_values],
                         ['rowType', 'keyComponents'])
        self.assertEqual([value_help.key for value_help in value_helps.sec_key_allowed_values],
                         ['allowed', 'notAllowed', 'notSpecified'])

    def test_table_type_fetch_value_help_item(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        value_help = table_type.value_helps.access_type_values[1]
        self.assertEqual(value_help.key, 'sorted')
        self.assertEqual(value_help.value, 'Sorted Table')
        self.assertEqual(value_help.description, '')

    def test_table_type_create(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='Test table type', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        table_type = sap.adt.TableType(connection, TABLE_TYPE_NAME, package='$TMP', metadata=metadata)
        table_type.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/ddic/tabletypes',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.tabletype.v1+xml; charset=utf-8'},
            body=bytes(TABLE_TYPE_ADT_NEW_OBJECT_REQUEST_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(connection.execs[0], self)

    def test_table_type_serialize_secondary_keys(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_SECONDARY_KEYS_RESPONSE_XML)

        self.maxDiff = None
        self.assertEqual(Marshal().serialize(table_type), TABLE_TYPE_ADT_SECONDARY_KEYS_REQUEST_XML)

    def test_table_type_set_dictionary_row_type(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        table_type.set_dictionary_row_type('BAPIRET2')

        self.maxDiff = None
        self.assertEqual(Marshal().serialize(table_type), TABLE_TYPE_ADT_DEFINE_STANDARD_REQUEST_XML)

    def test_table_type_set_primary_key(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_NEW_RESPONSE_XML)

        table_type.set_dictionary_row_type('BAPIRET2')
        table_type.access_type = 'sorted'
        table_type.set_primary_key('keyComponents', 'unique', ['TYPE', 'ID'])

        self.maxDiff = None
        self.assertEqual(Marshal().serialize(table_type), TABLE_TYPE_ADT_DEFINE_SORTED_REQUEST_XML)

    def test_table_type_set_primary_key_without_components(self):
        _, table_type = fetch_table_type(TABLE_TYPE_ADT_GET_KEY_COMPONENTS_RESPONSE_XML)

        table_type.set_primary_key('standard', 'nonUnique', [])

        self.assertEqual(table_type.primary_key.definition, 'standard')
        self.assertEqual(table_type.primary_key.kind, 'nonUnique')
        self.assertEqual(table_type.primary_key.components.is_visible, 'false')
        self.assertEqual(len(table_type.primary_key.components), 0)


if __name__ == '__main__':
    unittest.main()
