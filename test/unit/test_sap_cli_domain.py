#!/usr/bin/env python3

import unittest
import json

import sap.cli.domain
from sap.errors import SAPCliError

from mock import (
    BufferConsole,
    Connection,
    Response,
)

from infra import generate_parse_args
from fixtures_adt_domain import (
    DOMAIN_NAME,
    DOMAIN_ADT_GET_RESPONSE_XML,
)


class TestDomainRead(unittest.TestCase):

    def domain_read_cmd(self, *args, **kwargs):
        # Lazy initialization to avoid module-level CommandGroup instantiation
        parser = generate_parse_args(sap.cli.domain.CommandGroup())
        return parser('read', *args, **kwargs)

    def test_read_abap_format(self):
        """Test reading domain in ABAP (JSON) format"""
        connection = Connection([
            Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        the_cmd = self.domain_read_cmd(DOMAIN_NAME)
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        # Parse the output as JSON
        output = json.loads(console.capout)

        # Verify the structure matches the expected ABAP format
        self.assertEqual(output['formatVersion'], '1')
        self.assertEqual(output['header']['description'], 'Authorization group in the material master')
        self.assertEqual(output['header']['originalLanguage'], 'en')
        self.assertEqual(output['format']['dataType'], 'CHAR')
        self.assertEqual(output['format']['length'], 4)
        self.assertEqual(output['outputCharacteristics']['length'], 4)

        # Verify fixed values
        self.assertEqual(len(output['fixedValues']), 2)
        self.assertEqual(output['fixedValues'][0]['fixedValue'], 'H')
        self.assertEqual(output['fixedValues'][0]['description'], 'History')
        self.assertEqual(output['fixedValues'][1]['fixedValue'], 'X')
        self.assertEqual(output['fixedValues'][1]['description'], 'Xml')

    def test_read_human_format(self):
        """Test reading domain in HUMAN format"""
        connection = Connection([
            Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        the_cmd = self.domain_read_cmd(DOMAIN_NAME, '--format=HUMAN')
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        output = console.capout

        # Verify the human-readable output contains expected information
        self.assertIn('Domain: BEGRM', output)
        self.assertIn('Description: Authorization group in the material master', output)
        self.assertIn('Package: MGA', output)
        self.assertIn('Master Language: EN', output)
        self.assertIn('Datatype: CHAR', output)
        self.assertIn('Length: 4', output)
        self.assertIn('Table Reference: TMBG', output)
        self.assertIn('- H: History', output)
        self.assertIn('- X: Xml', output)

    def test_read_uppercase_name(self):
        """Test that lowercase input is converted to uppercase"""
        connection = Connection([
            Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        the_cmd = self.domain_read_cmd('begrm')  # lowercase
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        # Parse the output as JSON (default format is ABAP)
        output = json.loads(console.capout)
        # The connection should have been called with uppercase name
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/domains/begrm')


class TestDomainUnsupportedOperations(unittest.TestCase):
    """Test that unsupported operations raise appropriate errors"""

    def test_create_not_supported(self):
        """Test that create operation raises error"""
        connection = Connection()
        cmd_group = sap.cli.domain.CommandGroup()

        with self.assertRaises(SAPCliError) as cm:
            cmd_group.create_object(connection, None)

        self.assertIn('Create Domain is not supported', str(cm.exception))

    def test_delete_not_supported(self):
        """Test that delete operation raises error"""
        connection = Connection()
        cmd_group = sap.cli.domain.CommandGroup()

        with self.assertRaises(SAPCliError) as cm:
            cmd_group.delete_object(connection, None)

        self.assertIn('Delete Domain is not supported', str(cm.exception))

    def test_write_not_supported(self):
        """Test that write operation raises error"""
        connection = Connection()
        cmd_group = sap.cli.domain.CommandGroup()

        with self.assertRaises(SAPCliError) as cm:
            cmd_group.write_object_text(connection, None)

        self.assertIn('Write Domain is not supported', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
