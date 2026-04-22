#!/usr/bin/env python3

import unittest
import sap.adt
import sap.adt.my_object

from mock import Connection, Response, Request
from fixtures_sap_adt_my_object import MY_OBJECT_NAME, MY_OBJECT_ADT_GET_RESPONSE_XML, MY_OBJECT_ADT_POST_REQUEST_XML

class TestADTMyObject(unittest.TestCase):

    def test_my_object_fetch(self):
        connection = Connection([Response(text=MY_OBJECT_ADT_GET_RESPONSE_XML, status_code=200, headers={})])

        data_element = sap.adt.MyObject(connection, MY_OBJECT_NAME)
        data_element.fetch()

        # add all asserts to check if the object is correctly deserialized from the XML response


    def test_my_object_serialize(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='Test data element', language='EN', master_language='EN',
                                       responsible='ANZEIGER')
        my_object = sap.adt.MyObject(connection, MY_OBJECT_NAME, package='PACKAGE', metadata=metadata)
        my_object.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/oo/classes',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.oo.classes.v4+xml; charset=utf-8'},
            body=bytes(MY_OBJECT_ADT_POST_REQUEST_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(connection.execs[0], self)
