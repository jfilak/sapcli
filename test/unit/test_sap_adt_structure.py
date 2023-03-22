#!/usr/bin/env python3

import logging
import unittest
import sap.adt

from mock import Connection, Response, Request
from fixtures_adt_structure import STRUCTURE_DEFINITION_ADT_XML, STRUCTURE_NAME, CREATE_STRUCTURE_ADT_XML


class TestADTStructure(unittest.TestCase):

    def test_structure_fetch(self):
        connection = Connection([Response(text=STRUCTURE_DEFINITION_ADT_XML, status_code=200, headers={})])

        structure = sap.adt.Structure(connection, STRUCTURE_NAME)
        structure.fetch()

        self.assertEqual(structure.name, STRUCTURE_NAME)
        self.assertEqual(structure.active, 'active')
        self.assertEqual(structure.master_language, 'EN')
        self.assertEqual(structure.description, 'Test structure')

    def test_structure_serialize(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='Test structure', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        structure = sap.adt.Structure(connection, STRUCTURE_NAME, package='PACKAGE', metadata=metadata)
        structure.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/ddic/structures',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.structures.v2+xml; charset=utf-8'},
            body=bytes(CREATE_STRUCTURE_ADT_XML, 'utf-8'),
            params=None
        )

        self.assertEqual(connection.execs[0], expected_request)
