#!/usr/bin/env python3

import os
import unittest
from unittest.mock import Mock

import sap
import sap.adt
import sap.adt.checks

from mock import Connection, Response, Request
from fixtures_adt_checks import ADT_XML_CHECK_REPORTERS



class TestFetchReporters(unittest.TestCase):

    def test_fech_reporters_ok(self):
        connection = Connection([Response(status_code=200,
                                          headers={'Content-Type': 'application/vnd.sap.adt.reporters+xml'},
                                          text=ADT_XML_CHECK_REPORTERS)])

        result = sap.adt.checks.fetch_reporters(connection)

        self.assertIsInstance(result, list)
        self.assertEqual(3, len(result))

        self.assertEqual(result[0].name, 'abapCheckRun')
        self.assertEqual(result[1].name, 'abapPackageCheck')
        self.assertEqual(result[2].name, 'tableStatusCheck')

        self.assertEqual(result[0].supported_types, ['WDYN*', 'CLAS*', 'WGRP'])
        self.assertEqual(result[1].supported_types, ['PROG*', 'INTF*', 'HTTP'])
        self.assertEqual(result[2].supported_types, ['TABL/DT'])


class TestReporter(unittest.TestCase):

    def test_supports_type_and_obj(self):
        reporter = sap.adt.checks.Reporter()
        reporter.name = 'mock'
        reporter.supported_types = 'CLAS*'
        reporter.supported_types = 'TABL/DB'

        self.assertTrue(reporter.supports_type('CLAS'))
        self.assertTrue(reporter.supports_type('CLAS/OO'))
        self.assertTrue(reporter.supports_type('TABL/DB'))

        self.assertFalse(reporter.supports_type('TABL'))
        self.assertFalse(reporter.supports_type('TABL/VW'))

        connection = Mock()
        self.assertTrue(reporter.supports_object(sap.adt.Class(connection, 'CL_FOO')))


if __name__ == '__main__':
    unittest.main(verbosity=100)
