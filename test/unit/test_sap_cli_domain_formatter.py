#!/usr/bin/env python3

import unittest

import sap.cli.domain_formatter
from mock import BufferConsole, Connection, Response
from fixtures_adt_domain import DOMAIN_NAME, DOMAIN_ADT_GET_RESPONSE_XML
import sap.adt


class TestDomainFormatterHuman(unittest.TestCase):

    def test_format_domain_human_basic(self):
        """Test basic domain formatting without indent"""
        connection = Connection([Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})])
        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        console = BufferConsole()
        sap.cli.domain_formatter.format_domain_human(console, domain, indent='')

        output = console.capout
        self.assertIn('Type Information:', output)
        self.assertIn('Datatype: CHAR', output)
        self.assertIn('Length: 4', output)
        self.assertIn('Output Information:', output)
        self.assertIn('Value Information:', output)

    def test_format_domain_human_with_indent(self):
        """Test domain formatting with indentation"""
        connection = Connection([Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})])
        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        console = BufferConsole()
        sap.cli.domain_formatter.format_domain_human(console, domain, indent='    ')

        output = console.capout
        # Check that indentation is applied
        self.assertIn('    Type Information:', output)
        self.assertIn('    Output Information:', output)
        self.assertIn('    Value Information:', output)

    def test_format_domain_human_with_fixed_values(self):
        """Test domain formatting includes fixed values"""
        connection = Connection([Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})])
        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        console = BufferConsole()
        sap.cli.domain_formatter.format_domain_human(console, domain, indent='')

        output = console.capout
        self.assertIn('Fix Values:', output)
        self.assertIn('- H: History', output)
        self.assertIn('- X: Xml', output)

    def test_format_domain_human_with_table_ref(self):
        """Test domain formatting includes table reference"""
        connection = Connection([Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})])
        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        console = BufferConsole()
        sap.cli.domain_formatter.format_domain_human(console, domain, indent='')

        output = console.capout
        self.assertIn('Table Reference: TMBG', output)


class TestDomainFormatterAbap(unittest.TestCase):

    def test_format_domain_abap(self):
        """Test ABAP format dict structure"""
        connection = Connection([Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})])
        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        output = sap.cli.domain_formatter.format_domain_abap(domain)

        self.assertEqual(output['formatVersion'], '1')
        self.assertEqual(output['header']['description'], 'Authorization group in the material master')
        self.assertEqual(output['header']['originalLanguage'], 'en')
        self.assertEqual(output['format']['dataType'], 'CHAR')
        self.assertEqual(output['format']['length'], 4)
        self.assertEqual(output['outputCharacteristics']['length'], 4)

    def test_format_domain_abap_with_fixed_values(self):
        """Test ABAP format includes fixed values"""
        connection = Connection([Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})])
        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        output = sap.cli.domain_formatter.format_domain_abap(domain)

        self.assertIn('fixedValues', output)
        self.assertEqual(len(output['fixedValues']), 2)
        self.assertEqual(output['fixedValues'][0]['fixedValue'], 'H')
        self.assertEqual(output['fixedValues'][0]['description'], 'History')
        self.assertEqual(output['fixedValues'][1]['fixedValue'], 'X')
        self.assertEqual(output['fixedValues'][1]['description'], 'Xml')


if __name__ == '__main__':
    unittest.main()
