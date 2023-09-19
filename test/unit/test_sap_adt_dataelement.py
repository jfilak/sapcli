#!/usr/bin/env python3

import unittest
import sap.adt
import sap.adt.dataelement

from mock import Connection, Response, Request
from fixtures_adt_dataelement import DATA_ELEMENT_DEFINITION_ADT_XML, DATA_ELEMENT_NAME, CREATE_DATA_ELEMENT_ADT_XML


class TestADTDataElement(unittest.TestCase):

    def test_data_element_fetch(self):
        connection = Connection([Response(text=DATA_ELEMENT_DEFINITION_ADT_XML, status_code=200, headers={})])

        data_element = sap.adt.DataElement(connection, DATA_ELEMENT_NAME)
        data_element.fetch()

        self.assertEqual(data_element.name, DATA_ELEMENT_NAME)
        self.assertEqual(data_element.active, 'active')
        self.assertEqual(data_element.master_language, 'EN')
        self.assertEqual(data_element.description, 'Test data element')

    def test_data_element_serialize(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='Test data element', language='EN', master_language='EN',
                                       responsible='ANZEIGER')
        data_element = sap.adt.DataElement(connection, DATA_ELEMENT_NAME, package='PACKAGE', metadata=metadata)
        data_element.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/ddic/dataelements',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.dataelements.v2+xml; charset=utf-8'},
            body=bytes(CREATE_DATA_ELEMENT_ADT_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(connection.execs[0], self)
