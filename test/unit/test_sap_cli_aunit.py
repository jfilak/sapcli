#!/usr/bin/env python3

import sys

import unittest
from unittest.mock import patch, call
from io import StringIO
from types import SimpleNamespace

from sap.errors import SAPCliError
import sap.cli.aunit

from mock import Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK
from fixtures_adt_aunit import AUNIT_NO_TEST_RESULTS_XML, AUNIT_RESULTS_XML


class TestAUnitWrite(unittest.TestCase):

    def assert_print_no_test_classes(self, mock_print):
        self.assertEqual(
            mock_print.call_args_list[0],
            call('* [tolerable] [noTestClasses] - The task definition does not refer to any test', file=sys.stdout))

        self.assertEqual(
            mock_print.call_args_list[1],
            call('Successful: 0', file=sys.stdout))

        self.assertEqual(
            mock_print.call_args_list[2],
            call('Tolerable:  0', file=sys.stdout))

        self.assertEqual(
            mock_print.call_args_list[3],
            call('Critical:   0', file=sys.stdout))

    def test_aunit_invalid(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.aunit.run('wrongconn', SimpleNamespace(type='foo', output='human'))

        self.assertEqual(str(cm.exception), 'Unknown type: foo')

    def test_aunit_program(self):
        connection = Connection([Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(type='program', name='yprogram', output='human'))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('programs/programs/yprogram', connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_class(self):
        connection = Connection([Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(type='class', name='yclass', output='human'))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('oo/classes/yclass', connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_package(self):
        connection = Connection([Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(type='package', name='ypackage', output='human'))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_package_with_results(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(type='package', name='ypackage', output='human'))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)

        self.assertEqual(mock_print.call_args_list[0], call('ZCL_THEKING_MANUAL_HARDCORE', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[1], call('  LTCL_TEST', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[2], call('    DO_THE_FAIL [ERR]', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[3], call('    DO_THE_TEST [OK]', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[4], call('  LTCL_TEST_HARDER', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[5], call('    DO_THE_FAIL [ERR]', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[6], call('    DO_THE_TEST [OK]', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[7], call('ZEXAMPLE_TESTS', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[8], call('  LTCL_TEST', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[9], call('    DO_THE_FAIL [ERR]', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[10], call('    DO_THE_TEST [OK]', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[11], call('', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[12], call('ZCL_THEKING_MANUAL_HARDCORE=>LTCL_TEST=>DO_THE_FAIL', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[13], call('*  [critical] [failedAssertion] - Critical Assertion Error: \'I am supposed to fail\'', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[14], call('ZCL_THEKING_MANUAL_HARDCORE=>LTCL_TEST_HARDER=>DO_THE_FAIL', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[15], call('*  [critical] [failedAssertion] - Critical Assertion Error: \'I am supposed to fail\'', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[16], call('ZEXAMPLE_TESTS=>LTCL_TEST=>DO_THE_FAIL', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[17], call('*  [critical] [failedAssertion] - Critical Assertion Error: \'I am supposed to fail\'', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[18], call('*  [critical] [failedAssertion] - Error<LOAD_PROGRAM_CLASS_MISMATCH>', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[19], call('', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[20], call('Successful: 3', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[21], call('Tolerable:  0', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[22], call('Critical:   3', file=sys.stdout))

    def test_aunit_package_with_results_raw(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(type='package', name='ypackage', output='raw'))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)

        self.assertEqual(mock_print.call_args_list[0], call(AUNIT_RESULTS_XML))

    def test_aunit_package_with_results_junit4(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(type='package', name='ypackage', output='junit4'))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)

        self.maxDiff = None
        self.assertEqual(mock_stdout.getvalue(),
'''<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="ypackage">
  <testsuite name="LTCL_TEST" package="ZCL_THEKING_MANUAL_HARDCORE" tests="2">
    <testcase name="DO_THE_FAIL" classname="LTCL_TEST" status="ERR">
      <system-err>True expected
Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.</system-err>
      <error type="failedAssertion" message="Critical Assertion Error: 'I am supposed to fail'">Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)</error>
    </testcase>
    <testcase name="DO_THE_TEST" classname="LTCL_TEST" status="OK"/>
  </testsuite>
  <testsuite name="LTCL_TEST_HARDER" package="ZCL_THEKING_MANUAL_HARDCORE" tests="2">
    <testcase name="DO_THE_FAIL" classname="LTCL_TEST_HARDER" status="ERR">
      <system-err>True expected
Test 'LTCL_TEST_HARDER-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.</system-err>
      <error type="failedAssertion" message="Critical Assertion Error: 'I am supposed to fail'">Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)</error>
    </testcase>
    <testcase name="DO_THE_TEST" classname="LTCL_TEST_HARDER" status="OK"/>
  </testsuite>
  <testsuite name="LTCL_TEST" package="ZEXAMPLE_TESTS" tests="2">
    <testcase name="DO_THE_FAIL" classname="LTCL_TEST" status="ERR">
      <system-err>True expected
Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZEXAMPLE_TESTS'.</system-err>
      <error type="failedAssertion" message="Critical Assertion Error: 'I am supposed to fail'">Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;24&gt; (DO_THE_FAIL)
Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;25&gt; (PREPARE_THE_FAIL)</error>
      <error type="failedAssertion" message="Error&lt;LOAD_PROGRAM_CLASS_MISMATCH&gt;"/>
    </testcase>
    <testcase name="DO_THE_TEST" classname="LTCL_TEST" status="OK"/>
  </testsuite>
</testsuites>
''')



if __name__ == '__main__':
    unittest.main()
