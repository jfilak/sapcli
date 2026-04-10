#!/usr/bin/env python3

import unittest
import sap.adt
import sap.adt.authorization_field

from mock import Connection, Response
from fixtures_sap_adt_authorization_field import AUTHORIZATION_FIELD_NAME, AUTHORIZATION_FIELD_ADT_GET_RESPONSE_XML


class TestADTAuthorizationField(unittest.TestCase):

    def test_authorization_field_fetch(self):
        connection = Connection([Response(text=AUTHORIZATION_FIELD_ADT_GET_RESPONSE_XML, status_code=200, headers={})])

        auth_field = sap.adt.AuthorizationField(connection, AUTHORIZATION_FIELD_NAME)
        auth_field.fetch()

        self.assertEqual(auth_field.name, AUTHORIZATION_FIELD_NAME)
        self.assertEqual(auth_field.master_language, 'DE')
        self.assertEqual(auth_field.description, 'Authorization Group')
        self.assertEqual(auth_field.content.field_name, 'BEGRU')
        self.assertEqual(auth_field.content.roll_name, 'BEGRU')
        self.assertEqual(auth_field.content.search, 'false')
        self.assertEqual(auth_field.content.objexit, 'false')
        self.assertEqual(auth_field.content.domname, 'BEGRU')
        self.assertEqual(auth_field.content.outputlen, '000004')
        self.assertEqual(auth_field.content.orglvlinfo, 'Field is not defined as Organizational level.')
        self.assertEqual(auth_field.content.col_searchhelp, 'false')

    def test_authorization_field_with_package(self):
        """Test that package parameter is correctly set"""
        connection = Connection()

        auth_field = sap.adt.AuthorizationField(connection, AUTHORIZATION_FIELD_NAME, package='TEST_PACKAGE')

        self.assertEqual(auth_field.name, AUTHORIZATION_FIELD_NAME)
        self.assertEqual(auth_field.reference.name, 'TEST_PACKAGE')


if __name__ == '__main__':
    unittest.main()
