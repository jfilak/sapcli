#!/bin/python

import unittest

import sap.adt
import sap

from fixtures_adt import DummyADTObject
from fixtures_adt_aunit import AUNIT_RESULTS_XML, AUNIT_NO_TEST_RESULTS_XML


connection = sap.adt.Connection('nohost', 'noclient', 'nouser', 'nopassword')

class TestAUnit(unittest.TestCase):

    def test_build_tested_object_uri(self):
        victory = DummyADTObject()

        victory_uri = sap.adt.AUnit.build_tested_object_uri(connection, victory)
        self.assertEquals(victory_uri, '/sap/bc/adt/awesome/success/noobject')


class TestAUnitParseResults(unittest.TestCase):

    def test_parse_full(self):
        #sap.get_logger().setLevel(0)
        run_results = sap.adt.aunit.parse_run_results(AUNIT_RESULTS_XML)

        self.assertEqual([program.name for program in run_results.programs], ['ZCL_THEKING_MANUAL_HARDCORE', 'ZEXAMPLE_TESTS'])

        program_the_king = run_results.programs[0]
        self.assertEqual([test_class.name for test_class in program_the_king.test_classes], ['LTCL_TEST', 'LTCL_TEST_HARDER'])

        test_class = program_the_king.test_classes[0]
        self.assertEqual([test_method.name for test_method in test_class.test_methods], ['DO_THE_FAIL', 'DO_THE_TEST'])

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
