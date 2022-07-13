#!/usr/bin/env python3

import os
import unittest
from unittest.mock import Mock

import sap
import sap.adt
import sap.adt.checks
from sap.adt.marshalling import Marshal

from mock import ConnectionViaHTTP as Connection, Response
from fixtures_adt_checks import ADT_XML_CHECK_REPORTERS, ADT_XML_RUN_CHECK_2_REPORTERS


FIXTURE_TWO_CLASSES_REQUEST = '''<?xml version="1.0" encoding="UTF-8"?>
<chkrun:checkObjectList xmlns:chkrun="http://www.sap.com/adt/checkrun" xmlns:adtcore="http://www.sap.com/adt/core">
<chkrun:checkObject adtcore:uri="/sap/bc/adt/oo/classes/cl_first" chkrun:version="active"/>
<chkrun:checkObject adtcore:uri="/sap/bc/adt/oo/classes/cl_second" chkrun:version="active"/>
</chkrun:checkObjectList>'''


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


class TestCheckObjectLiss(unittest.TestCase):

    def test_serialize(self):
        connection = Connection()

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_object(sap.adt.Class(connection, 'CL_FIRST'))
        obj_list.add_object(sap.adt.Class(connection, 'CL_SECOND'))

        xml_obj_list = Marshal().serialize(obj_list)

        self.maxDiff = None
        self.assertEqual(xml_obj_list, FIXTURE_TWO_CLASSES_REQUEST)

    def test_object_list_add_uri(self):
        connection = Connection()

        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_uri(sap.adt.Class(connection, 'CL_FIRST').full_adt_uri)
        obj_list.add_uri(sap.adt.Class(connection, 'CL_SECOND').full_adt_uri)

        xml_obj_list = Marshal().serialize(obj_list)

        self.maxDiff = None
        self.assertEqual(xml_obj_list, FIXTURE_TWO_CLASSES_REQUEST)

    def test_object_list_iter(self):
        obj_list = sap.adt.checks.CheckObjectList()
        obj_list.add_uri('/1/uri')
        obj_list.add_uri('/2/uri')

        self.assertEqual(['/1/uri', '/2/uri'], [obj.uri for obj in obj_list])


class TestRunForObjects(unittest.TestCase):

    def test_2_reportes_2_classes(self):
        connection = Connection([Response(status_code=200,
                                          content_type='application/vnd.sap.adt.checkmessages+xml; charset=utf-8',
                                          text=ADT_XML_RUN_CHECK_2_REPORTERS)])

        reporter = sap.adt.checks.Reporter('abapCheckRun')
        reporter.supported_types = '*'

        reports = sap.adt.checks.run_for_supported_objects(connection, reporter,
                                                           [sap.adt.Class(connection, 'CL_FIRST'),
                                                            sap.adt.Class(connection, 'CL_SECOND')])

        self.assertEqual(connection.mock_methods(), [('POST', '/sap/bc/adt/checkruns')])
        self.assertEqual(connection.execs[0].body, FIXTURE_TWO_CLASSES_REQUEST)

        self.assertEqual(['abapCheckRun', 'tableStatusCheck'], [report.reporter for report in reports])
        self.assertEqual(['First', 'Second'], [msg.short_text for msg in reports[0].messages])
        self.assertEqual(['Third', 'Fourth'], [msg.short_text for msg in reports[1].messages])


if __name__ == '__main__':
    unittest.main(verbosity=100)
