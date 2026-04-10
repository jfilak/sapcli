#!/usr/bin/env python3

import unittest

import sap.cli.authorizationfield
from sap.errors import SAPCliError

from mock import (
    BufferConsole,
    Connection,
    Response,
)

from infra import generate_parse_args
from fixtures_sap_adt_authorization_field import (
    AUTHORIZATION_FIELD_NAME,
    AUTHORIZATION_FIELD_ADT_GET_RESPONSE_XML,
)


class TestAuthorizationFieldRead(unittest.TestCase):

    def authorization_field_read_cmd(self, *args, **kwargs):
        # Lazy initialization to avoid module-level CommandGroup instantiation
        parser = generate_parse_args(sap.cli.authorizationfield.CommandGroup())
        return parser('read', *args, **kwargs)

    def test_read(self):
        connection = Connection([
            Response(text=AUTHORIZATION_FIELD_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        the_cmd = self.authorization_field_read_cmd(AUTHORIZATION_FIELD_NAME)
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        expected_output = 'Authorization Field: BEGRU\nDescription: Authorization Group\nPackage: S_BUPA_GENERAL\nResponsible: KNOETIG\nMaster Language: DE\n\nContent:\n  Field Name: BEGRU\n  Roll Name: BEGRU\n  Check Table: \n  Exit FB: \n  Domain Name: BEGRU\n  Output Length: 000004\n  Conversion Exit: \n  Search: false\n  Object Exit: false\n  Org Level Info: Field is not defined as Organizational level.\n  Collective Search Help: false\n  Collective Search Help Name: \n  Collective Search Help Description: \n'

        self.assertEqual(console.capout, expected_output)

    def test_read_uppercase_name(self):
        """Test that lowercase input is converted to uppercase"""
        connection = Connection([
            Response(text=AUTHORIZATION_FIELD_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        the_cmd = self.authorization_field_read_cmd('begru')  # lowercase
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        # Should still work and show BEGRU (uppercase) in output
        self.assertIn('Authorization Field: BEGRU', console.capout)

    def test_read_abap_format_not_implemented(self):
        """Test that ABAP format raises error"""
        connection = Connection([
            Response(text=AUTHORIZATION_FIELD_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        the_cmd = self.authorization_field_read_cmd(AUTHORIZATION_FIELD_NAME, '--format=ABAP')
        the_cmd.console_factory = lambda: console

        with self.assertRaises(SAPCliError) as cm:
            the_cmd.execute(connection, the_cmd)

        self.assertIn('ABAP format output is not implemented yet', str(cm.exception))


class TestAuthorizationFieldUnsupportedOperations(unittest.TestCase):
    """Test that unsupported operations raise appropriate errors"""

    def test_create_not_supported(self):
        """Test that create operation raises error"""
        connection = Connection()
        cmd_group = sap.cli.authorizationfield.CommandGroup()

        with self.assertRaises(SAPCliError) as cm:
            cmd_group.create_object(connection, None)

        self.assertIn('Create Authorization Field is not implemented yet', str(cm.exception))

    def test_delete_not_supported(self):
        """Test that delete operation raises error"""
        connection = Connection()
        cmd_group = sap.cli.authorizationfield.CommandGroup()

        with self.assertRaises(SAPCliError) as cm:
            cmd_group.delete_object(connection, None)

        self.assertIn('Delete Authorization Field is not implemented yet', str(cm.exception))

    def test_write_not_supported(self):
        """Test that write operation raises error"""
        connection = Connection()
        cmd_group = sap.cli.authorizationfield.CommandGroup()

        with self.assertRaises(SAPCliError) as cm:
            cmd_group.write_object_text(connection, None)

        self.assertIn('Write Authorization Field is not implemented yet', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
