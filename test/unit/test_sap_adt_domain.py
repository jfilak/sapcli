#!/usr/bin/env python3

import unittest
import sap.adt
import sap.adt.domain

from mock import Connection, Response
from fixtures_adt_domain import DOMAIN_NAME, DOMAIN_ADT_GET_RESPONSE_XML


class TestADTDomain(unittest.TestCase):

    def test_domain_fetch(self):
        connection = Connection([Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={})])

        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        self.assertEqual(domain.name, DOMAIN_NAME)
        self.assertEqual(domain.active, 'active')
        self.assertEqual(domain.description, 'Authorization group in the material master')
        self.assertEqual(domain._metadata.package_reference.name, 'MGA')

        # Test type information
        self.assertEqual(domain.content.type_information.datatype, 'CHAR')
        self.assertEqual(domain.content.type_information.length, '000004')
        self.assertEqual(domain.content.type_information.decimals, '000000')

        # Test output information
        self.assertEqual(domain.content.output_information.length, '000004')
        self.assertEqual(domain.content.output_information.style, '00')
        self.assertEqual(domain.content.output_information.sign_exists, 'false')
        self.assertEqual(domain.content.output_information.lowercase, 'false')
        self.assertEqual(domain.content.output_information.ampm_format, 'false')

        # Test value information
        self.assertEqual(domain.content.value_information.value_table_ref.name, 'TMBG')
        self.assertEqual(domain.content.value_information.value_table_ref.uri, '/sap/bc/adt/ddic/tables/tmbg')
        self.assertEqual(domain.content.value_information.value_table_ref.typ, 'TABL/DT')
        self.assertEqual(domain.content.value_information.append_exists, 'false')

        # Test fix values
        self.assertEqual(len(domain.content.value_information.fix_values), 2)
        self.assertEqual(domain.content.value_information.fix_values[0].position, '0006')
        self.assertEqual(domain.content.value_information.fix_values[0].low, 'H')
        self.assertEqual(domain.content.value_information.fix_values[0].text, 'History')
        self.assertEqual(domain.content.value_information.fix_values[1].position, '0007')
        self.assertEqual(domain.content.value_information.fix_values[1].low, 'X')
        self.assertEqual(domain.content.value_information.fix_values[1].text, 'Xml')


if __name__ == '__main__':
    unittest.main()
