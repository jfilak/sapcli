#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import sap.adt
import sap.adt.domain

from mock import Connection, Response
from fixtures_adt_domain import DOMAIN_NAME, DOMAIN_ADT_GET_RESPONSE_XML, DOMAIN_NEW_NAME, \
    DOMAIN_ADT_NEW_OBJECT_REQUEST_XML, DOMAIN_ADT_GET_NEW_RESPONSE_XML


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

    def test_domain_fetch_new_without_fix_values(self):
        connection = Connection([Response(text=DOMAIN_ADT_GET_NEW_RESPONSE_XML, status_code=200, headers={})])

        domain = sap.adt.Domain(connection, DOMAIN_NEW_NAME)
        domain.fetch()

        self.assertEqual(len(domain.content.value_information.fix_values), 0)
        self.assertIsNone(domain.content.value_information.value_table_ref.name)

    def test_domain_create_without_content(self):
        connection = Connection([Response(text='', status_code=201, headers={})])

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible='DEVELOPER',
                                       description='Testing')
        domain = sap.adt.Domain(connection, DOMAIN_NEW_NAME, package='$TMP', metadata=metadata)
        domain.create()

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/ddic/domains')
        self.assertEqual(connection.execs[0].body.decode('utf-8'), DOMAIN_ADT_NEW_OBJECT_REQUEST_XML)

    @patch('sap.adt.objects.ADTObject.unlock')
    @patch('sap.adt.objects.ADTObject.lock', return_value='lock_handle')
    def test_domain_push_fix_values(self, fake_lock, fake_unlock):
        connection = Connection([
            Response(text=DOMAIN_ADT_GET_RESPONSE_XML, status_code=200, headers={}),
            Response(text='', status_code=200, headers={}),
        ])

        domain = sap.adt.Domain(connection, DOMAIN_NAME)
        domain.fetch()

        with domain.open_editor() as editor:
            editor.push()

        self.assertEqual(connection.execs[1].method, 'PUT')
        self.assertEqual(connection.execs[1].adt_uri, f'/sap/bc/adt/ddic/domains/{DOMAIN_NAME.lower()}')
        self.assertEqual(connection.execs[1].params, {'lockHandle': 'lock_handle'})
        self.assertIn('''<doma:fixValues>
<doma:fixValue>
<doma:position>0006</doma:position>
<doma:low>H</doma:low>
<doma:high></doma:high>
<doma:text>History</doma:text>
</doma:fixValue>
<doma:fixValue>
<doma:position>0007</doma:position>
<doma:low>X</doma:low>
<doma:high></doma:high>
<doma:text>Xml</doma:text>
</doma:fixValue>
</doma:fixValues>''', connection.execs[1].body.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
