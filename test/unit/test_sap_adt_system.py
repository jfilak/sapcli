#!/usr/bin/env python3

import unittest

import sap.adt.system

from mock import (
    Connection,
    Response,
    Request,
)
from fixtures_adt_system import (
    RESPONSE_SYSTEM_INFORMATION,
    RESPONSE_JSON_SYSTEM_INFORMATION,
    SYSTEM_INFORMATION_XML,
    JSON_SYSTEM_INFORMATION,
)


def make_connection():
    """Create a Connection with both XML and JSON responses"""
    return Connection([RESPONSE_SYSTEM_INFORMATION, RESPONSE_JSON_SYSTEM_INFORMATION])


class TestGetInformation(unittest.TestCase):

    def test_get_information_sends_two_requests(self):
        """Test that get_information sends GET requests to both endpoints"""
        connection = make_connection()
        sap.adt.system.get_information(connection)

        self.assertEqual(len(connection.execs), 2)

    def test_get_information_xml_request(self):
        """Test that the first request goes to system/information"""
        connection = make_connection()
        sap.adt.system.get_information(connection)

        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/system/information')

    def test_get_information_json_request(self):
        """Test that the second request goes to core/http/systeminformation with JSON accept"""
        connection = make_connection()
        sap.adt.system.get_information(connection)

        self.assertEqual(connection.execs[1].method, 'GET')
        self.assertEqual(connection.execs[1].adt_uri, '/sap/bc/adt/core/http/systeminformation')
        self.assertEqual(connection.execs[1].headers['Accept'], 'application/vnd.sap.adt.core.http.systeminformation.v1+json')

    def test_get_information_parses_all_entries(self):
        """Test that entries from both endpoints are merged"""
        connection = make_connection()
        result = sap.adt.system.get_information(connection)

        # 24 from XML + 5 from JSON, but no overlap in the sample data
        self.assertEqual(len(result.entries), 29)

    def test_get_information_xml_entry_values(self):
        """Test that XML entry values are correctly parsed"""
        connection = make_connection()
        result = sap.adt.system.get_information(connection)

        self.assertEqual(result.get('ApplicationServerName'), 'C50_ddci')
        self.assertEqual(result.get('DBLibrary'), 'SQLDBC 2.27.024.1772569942')
        self.assertEqual(result.get('DBName'), 'C50/02')
        self.assertEqual(result.get('DBRelease'), '2.00.089.01.1769502981')
        self.assertEqual(result.get('DBSchema'), 'SAPHANADB')
        self.assertEqual(result.get('DBServer'), 'saphost')
        self.assertEqual(result.get('DBSystem'), 'HDB')
        self.assertEqual(result.get('IPAddress'), '172.27.4.5')
        self.assertEqual(result.get('KernelCompilationDate'),
                         'Linux GNU SLES-15 x86_64  cc10.3.0 use-pr260304 Mar 09 2026 11:05:09')
        self.assertEqual(result.get('KernelKind'), 'opt')
        self.assertEqual(result.get('KernelPatchLevel'), '0')
        self.assertEqual(result.get('KernelRelease'), '920')
        self.assertEqual(result.get('MachineType'), 'x86_64')
        self.assertEqual(result.get('NodeName'), 'saphost')
        self.assertEqual(result.get('OSName'), 'Linux')
        self.assertEqual(result.get('OSVersion'), '6.4.0-150600.23.60-default')
        self.assertEqual(result.get('SAPSystemID'), '390')
        self.assertEqual(result.get('SAPSystemNumber'), '000000000000000001')
        self.assertEqual(result.get('UnicodeSystem'), 'True')

    def test_get_information_json_entry_values(self):
        """Test that JSON entry values are correctly parsed"""
        connection = make_connection()
        result = sap.adt.system.get_information(connection)

        self.assertEqual(result.get('SID'), 'C50')
        self.assertEqual(result.get('userName'), 'DEVELOPER')
        self.assertEqual(result.get('userFullName'), '')
        self.assertEqual(result.get('client'), '100')
        self.assertEqual(result.get('language'), 'EN')

    def test_get_information_not_authorized_flags(self):
        """Test that NotAuthorized flags are correctly parsed"""
        connection = make_connection()
        result = sap.adt.system.get_information(connection)

        self.assertEqual(result.get('NotAuthorizedDB'), 'false')
        self.assertEqual(result.get('NotAuthorizedHost'), 'false')
        self.assertEqual(result.get('NotAuthorizedKernel'), 'false')
        self.assertEqual(result.get('NotAuthorizedSystem'), 'false')
        self.assertEqual(result.get('NotAuthorizedUser'), 'false')

    def test_get_information_unknown_entry(self):
        """Test that get() returns None for unknown entries"""
        connection = make_connection()
        result = sap.adt.system.get_information(connection)

        self.assertIsNone(result.get('NonExistentEntry'))

    def test_get_information_iterable(self):
        """Test that SystemInformation is iterable over merged entries"""
        connection = make_connection()
        result = sap.adt.system.get_information(connection)

        entries = list(result)
        self.assertEqual(len(entries), 29)

    def test_get_information_xml_takes_precedence(self):
        """Test that XML entries override JSON entries with the same key"""
        xml_response = Response(
            text='''<?xml version="1.0" encoding="utf-8"?>
<atom:feed xmlns:atom="http://www.w3.org/2005/Atom">
<atom:entry>
    <atom:id>SID</atom:id>
    <atom:title>XML_VALUE</atom:title>
</atom:entry>
</atom:feed>''',
            status_code=200,
            headers={'Content-Type': 'application/atom+xml;type=feed'},
        )

        json_response = Response(
            status_code=200,
            json={'systemID': 'JSON_VALUE', 'extra': 'ONLY_IN_JSON'},
            headers={'Content-Type': 'application/vnd.sap.adt.core.http.systeminformation.v1+json'},
        )

        connection = Connection([xml_response, json_response])
        result = sap.adt.system.get_information(connection)

        self.assertEqual(result.get('SID'), 'XML_VALUE')
        self.assertEqual(result.get('extra'), 'ONLY_IN_JSON')
        self.assertEqual(len(result.entries), 2)


class TestSystemInfoEntry(unittest.TestCase):

    def test_entry_attributes(self):
        """Test SystemInfoEntry stores identity and title"""
        entry = sap.adt.system.SystemInfoEntry('TestKey', 'TestValue')
        self.assertEqual(entry.identity, 'TestKey')
        self.assertEqual(entry.title, 'TestValue')


class TestSystemInformation(unittest.TestCase):

    def test_empty_information(self):
        """Test SystemInformation with no entries"""
        info = sap.adt.system.SystemInformation([])
        self.assertEqual(len(info.entries), 0)
        self.assertIsNone(info.get('anything'))

    def test_entries_property(self):
        """Test entries property returns list of entries"""
        entries = [
            sap.adt.system.SystemInfoEntry('Key1', 'Value1'),
            sap.adt.system.SystemInfoEntry('Key2', 'Value2'),
        ]
        info = sap.adt.system.SystemInformation(entries)
        self.assertEqual(len(info.entries), 2)


if __name__ == '__main__':
    unittest.main()
