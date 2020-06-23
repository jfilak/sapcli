#!/bin/python

import unittest

import sap
import sap.adt
from sap.adt.aunit import Alert, AlertSeverity
from sap.adt.objects import ADTObjectSets

from fixtures_adt import DummyADTObject
from fixtures_adt_aunit import AUNIT_RESULTS_XML, AUNIT_NO_TEST_RESULTS_XML

from mock import Connection


class TestAUnit(unittest.TestCase):

    def test_run_configuration_default(self):
        connection = Connection()

        victory = DummyADTObject(connection=connection)

        tested_objects = ADTObjectSets()
        tested_objects.include_object(victory)

        runner = sap.adt.aunit.AUnit(connection)
        response = runner.execute(tested_objects)

        self.maxDiff = None

        self.assertEqual(connection.execs[0].body,
'''<?xml version="1.0" encoding="UTF-8"?>
<aunit:runConfiguration xmlns:aunit="http://www.sap.com/adt/aunit">
<external>
<coverage active="false"/>
</external>
<options>
<uriType value="semantic"/>
<testDeterminationStrategy sameProgram="true" assignedTests="false" appendAssignedTestsPreview="true"/>
<testRiskLevels harmless="true" dangerous="true" critical="true"/>
<testDurations short="true" medium="true" long="true"/>
<withNavigationUri enabled="false"/>
</options>
<adtcore:objectSets xmlns:adtcore="http://www.sap.com/adt/core">
<objectSet kind="inclusive">
<adtcore:objectReferences>
<adtcore:objectReference adtcore:uri="/sap/bc/adt/awesome/success/noobject" adtcore:name="NOOBJECT"/>
</adtcore:objectReferences>
</objectSet>
</adtcore:objectSets>
</aunit:runConfiguration>''')

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/abapunit/testruns')

class TestAlert(unittest.TestCase):

    def test_error_as_severity_fatal(self):
        alert = sap.adt.aunit.Alert(severity=AlertSeverity.FATAL, kind=None, title=None, details=None, stack=None)
        self.assertTrue(alert.is_error)
        self.assertFalse(alert.is_warning)

    def test_error_as_severity_critical(self):
        alert = sap.adt.aunit.Alert(severity=AlertSeverity.CRITICAL, kind=None, title=None, details=None, stack=None)
        self.assertTrue(alert.is_error)
        self.assertFalse(alert.is_warning)

    def test_warning_as_severity_tolerable(self):
        alert = sap.adt.aunit.Alert(severity=AlertSeverity.TOLERABLE, kind=None, title=None, details=None, stack=None)
        self.assertTrue(alert.is_warning)
        self.assertFalse(alert.is_error)

    def test_ok_as_severity_random(self):
        alert = sap.adt.aunit.Alert(severity='UNKNOWN', kind=None, title=None, details=None, stack=None)
        self.assertFalse(alert.is_warning)
        self.assertFalse(alert.is_error)


class TestAUnitParseResults(unittest.TestCase):

    def test_parse_full(self):
        run_results = sap.adt.aunit.parse_run_results(AUNIT_RESULTS_XML)

        self.assertEqual([program.name for program in run_results.programs], ['ZCL_THEKING_MANUAL_HARDCORE', 'ZEXAMPLE_TESTS'])

        program_the_king = run_results.programs[0]
        self.assertEqual([test_class.name for test_class in program_the_king.test_classes], ['LTCL_TEST', 'LTCL_TEST_HARDER'])

        test_class = program_the_king.test_classes[0]
        self.assertEqual([test_method.name for test_method in test_class.test_methods], ['DO_THE_FAIL', 'DO_THE_TEST'])
        self.assertEqual([test_method.duration for test_method in test_class.test_methods], [33, 0])

        test_method = test_class.test_methods[0]
        self.assertEqual([(alert.kind, alert.severity, alert.title) for alert in test_method.alerts],
                         [('failedAssertion', 'critical', 'Critical Assertion Error: \'I am supposed to fail\'')])

        program_example = run_results.programs[1]
        self.assertEqual([test_class.name for test_class in program_example.test_classes], ['LTCL_TEST'])

    def test_parse_no_tests(self):
        run_results = sap.adt.aunit.parse_run_results(AUNIT_NO_TEST_RESULTS_XML)

        self.assertEqual([(alert.kind, alert.severity, alert.title) for alert in run_results.alerts],
                         [('noTestClasses', 'tolerable', 'The task definition does not refer to any test')])


if __name__ == '__main__':
    unittest.main()
