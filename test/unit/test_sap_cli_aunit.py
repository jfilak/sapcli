#!/usr/bin/env python3

import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch, call, Mock, mock_open

import sap.adt.cts
import sap.cli.aunit
from fixtures_adt_aunit import (
    AUNIT_NO_TEST_RESULTS_XML,
    AUNIT_RESULTS_XML,
    GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML,
    AUNIT_RESULTS_NO_TEST_METHODS_XML,
    AUNIT_SYNTAX_ERROR_XML
)
from fixtures_adt_coverage import ACOVERAGE_RESULTS_XML, ACOVERAGE_STATEMENTS_RESULTS_XML
from infra import generate_parse_args
from mock import Connection, Response, BufferConsole
from sap.cli.aunit import ResultOptions
from sap.errors import SAPCliError

parse_args = generate_parse_args(sap.cli.aunit.CommandGroup())


class TestAUnitWrite(unittest.TestCase):

    def setUp(self):
        self.connection = Connection()

    def assert_print_no_test_classes(self, mock_print):
        self.assertEqual(
            mock_print.return_value.capout,
            'Successful: 0\n'
            'Warnings:   0\n'
            'Errors:     0\n')

        self.assertEqual(
            mock_print.return_value.caperr,
            '* [tolerable] [noTestClasses] - The task definition does not refer to any test\n')

    def test_aunit_invalid(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.aunit.run('wrongconn', SimpleNamespace(type='foo', output='human'))

        self.assertEqual(str(cm.exception), 'Unknown type: foo')

    def test_print_aunit_output_raises(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.aunit.print_aunit_output(SimpleNamespace(output='foo'), Mock(), Mock())

        self.assertEqual(str(cm.exception), 'Unsupported output type: foo')

    def execute_run(self, *args, **kwargs):
        cmd_args = parse_args('run', *args, **kwargs)
        return cmd_args.execute(self.connection, cmd_args)

    def test_aunit_program(self):
        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={})
        )

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            self.execute_run('program', '--output', 'human', 'yprogram', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('programs/programs/yprogram', self.connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_class_human(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            self.execute_run('class', 'yclass', '--output', 'human', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('oo/classes/yclass', self.connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_class_human_syntax_error(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_SYNTAX_ERROR_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            retval = self.execute_run('class', 'yclass', '--output', 'human', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('oo/classes/yclass', self.connection.execs[0].body)
        self.assertEqual(mock_print.return_value.capout,
'''CL_FOO
* [critical] [warning] - CL_FOO has syntax errors and cannot be analyzed for existence of unit tests

Successful: 0
Warnings:   0
Errors:     1
''')
        self.assertEqual(retval, 1)

    def test_aunit_package(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            self.execute_run('package', 'ypackage', '--output', 'human', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('packages/ypackage', self.connection.execs[0].body)

    def test_aunit_junit4_no_test_methods(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_RESULTS_NO_TEST_METHODS_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_stdout:
            self.execute_run('package', 'ypackage', '--output', 'junit4', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(len(self.connection.execs), 1)
        self.assertEqual(
            mock_stdout.return_value.capout,
            """<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="ypackage">
  <testsuite name="LTCL_TEST" package="ZCL_THEKING_MANUAL_HARDCORE" tests="0"/>
</testsuites>
"""
        )

    def test_aunit_package_with_results(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            exit_code = self.execute_run('package', 'ypackage', '--output', 'human', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('packages/ypackage', self.connection.execs[0].body)

        self.maxDiff = None
        self.assertEqual(mock_print.return_value.capout,
'''ZCL_THEKING_MANUAL_HARDCORE
  LTCL_TEST
    DO_THE_FAIL [ERR]
    DO_THE_WARN [SKIP]
    DO_THE_TEST [OK]
  LTCL_TEST_HARDER
    DO_THE_FAIL [ERR]
    DO_THE_TEST [OK]
ZEXAMPLE_TESTS
  LTCL_TEST
    DO_THE_FAIL [ERR]
    DO_THE_TEST [OK]

ZCL_THEKING_MANUAL_HARDCORE=>LTCL_TEST=>DO_THE_FAIL
* [critical] [failedAssertion] - Critical Assertion Error: \'I am supposed to fail\'
ZCL_THEKING_MANUAL_HARDCORE=>LTCL_TEST_HARDER=>DO_THE_FAIL
* [critical] [failedAssertion] - Critical Assertion Error: \'I am supposed to fail\'
ZEXAMPLE_TESTS=>LTCL_TEST=>DO_THE_FAIL
* [critical] [failedAssertion] - Critical Assertion Error: \'I am supposed to fail\'
* [critical] [failedAssertion] - Error<LOAD_PROGRAM_CLASS_MISMATCH>

Successful: 3
Warnings:   1
Errors:     3
''')

    def test_aunit_package_with_results_raw(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            exit_code = self.execute_run('package', 'ypackage', '--output', 'raw', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('packages/ypackage', self.connection.execs[0].body)

        self.assertEqual(mock_print.return_value.capout, AUNIT_RESULTS_XML + "\n")

    def test_aunit_package_with_results_junit4(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_stdout:
            exit_code = self.execute_run('package', 'ypackage', '--output', 'junit4', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('packages/ypackage', self.connection.execs[0].body)

        self.maxDiff = None
        self.assertEqual(mock_stdout.return_value.capout,
'''<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="ypackage">
  <testsuite name="LTCL_TEST" package="ZCL_THEKING_MANUAL_HARDCORE" tests="3">
    <testcase name="DO_THE_FAIL" classname="ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST" status="ERR">
      <system-err>True expected
Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.</system-err>
      <error type="failedAssertion" message="Critical Assertion Error: 'I am supposed to fail'">Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)</error>
    </testcase>
    <testcase name="DO_THE_WARN" classname="ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST" status="SKIP">
      <system-err>True expected
Test 'LTCL_TEST-&gt;DO_THE_WARN' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.</system-err>
      <error type="failedAssertion" message="Warning: 'I am supposed to warn'">Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_WARN)</error>
    </testcase>
    <testcase name="DO_THE_TEST" classname="ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST" status="OK"/>
  </testsuite>
  <testsuite name="LTCL_TEST_HARDER" package="ZCL_THEKING_MANUAL_HARDCORE" tests="2">
    <testcase name="DO_THE_FAIL" classname="ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST_HARDER" status="ERR">
      <system-err>True expected
Test 'LTCL_TEST_HARDER-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.</system-err>
      <error type="failedAssertion" message="Critical Assertion Error: 'I am supposed to fail'">Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)</error>
    </testcase>
    <testcase name="DO_THE_TEST" classname="ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST_HARDER" status="OK"/>
  </testsuite>
  <testsuite name="LTCL_TEST" package="ZEXAMPLE_TESTS" tests="2">
    <testcase name="DO_THE_FAIL" classname="ZEXAMPLE_TESTS=&gt;LTCL_TEST" status="ERR">
      <system-err>True expected
Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZEXAMPLE_TESTS'.</system-err>
      <error type="failedAssertion" message="Critical Assertion Error: 'I am supposed to fail'">Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;24&gt; (DO_THE_FAIL)
Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;25&gt; (PREPARE_THE_FAIL)</error>
      <error type="failedAssertion" message="Error&lt;LOAD_PROGRAM_CLASS_MISMATCH&gt;"/>
    </testcase>
    <testcase name="DO_THE_TEST" classname="ZEXAMPLE_TESTS=&gt;LTCL_TEST" status="OK"/>
  </testsuite>
</testsuites>
''')

    def test_aunit_class_junit4_syntax_error(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_SYNTAX_ERROR_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            retval = self.execute_run('class', 'yclass', '--output', 'junit4', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('oo/classes/yclass', self.connection.execs[0].body)
        self.maxDiff = None
        self.assertEqual(mock_print.return_value.capout, '''<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="yclass">
  <testcase name="CL_FOO" classname="CL_FOO" status="ERR">
    <system-err>"ME-&gt;MEMBER" is not type-compatible with formal parameter "BAR".</system-err>
    <error type="warning" message="CL_FOO has syntax errors and cannot be analyzed for existence of unit tests">CL_FOO======CCAU:428</error>
  </testcase>
</testsuites>
''')
        self.assertEqual(mock_print.return_value.caperr,
'''''')
        self.assertEqual(retval, 1)

    def test_aunit_package_with_results_sonar(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_stdout:
            exit_code = self.execute_run('package', 'ypackage', '--output', 'sonar', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('packages/ypackage', self.connection.execs[0].body)

        self.maxDiff = None
        self.assertEqual(mock_stdout.return_value.capout,
'''<?xml version="1.0" encoding="UTF-8" ?>
<testExecutions version="1">
  <file path="ypackage/ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST">
    <testCase name="DO_THE_FAIL" duration="33">
      <error message="Critical Assertion Error: 'I am supposed to fail'">
True expected
Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.

Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)
      </error>
    </testCase>
    <testCase name="DO_THE_WARN" duration="33">
      <skipped message="Warning: 'I am supposed to warn'">
True expected
Test 'LTCL_TEST-&gt;DO_THE_WARN' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.

Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_WARN)
      </skipped>
    </testCase>
    <testCase name="DO_THE_TEST" duration="0"/>
  </file>
  <file path="ypackage/ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST_HARDER">
    <testCase name="DO_THE_FAIL" duration="0">
      <error message="Critical Assertion Error: 'I am supposed to fail'">
True expected
Test 'LTCL_TEST_HARDER-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.

Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)
      </error>
    </testCase>
    <testCase name="DO_THE_TEST" duration="0"/>
  </file>
  <file path="ypackage/ZEXAMPLE_TESTS=&gt;LTCL_TEST">
    <testCase name="DO_THE_FAIL" duration="0">
      <error message="Critical Assertion Error: 'I am supposed to fail'">
True expected
Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZEXAMPLE_TESTS'.

Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;24&gt; (DO_THE_FAIL)
Include: &lt;ZEXAMPLE_TESTS&gt; Line: &lt;25&gt; (PREPARE_THE_FAIL)
      </error>
      <error message="Error&lt;LOAD_PROGRAM_CLASS_MISMATCH&gt;">
      </error>
    </testCase>
    <testCase name="DO_THE_TEST" duration="0"/>
  </file>
</testExecutions>
''')

    def test_aunit_parser_results_global_class_tests(self):
        results = sap.adt.aunit.parse_aunit_response(GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML).run_results
        output = BufferConsole()
        sap.cli.aunit.print_aunit_junit4(results, SimpleNamespace(name=['$TMP']), output)

        self.maxDiff = None
        self.assertEqual(output.capout,
'''<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="$TMP">
  <testsuite name="ZCL_TEST_CLASS" package="ZCL_TEST_CLASS" tests="1">
    <testcase name="DO_THE_TEST" classname="ZCL_TEST_CLASS" status="OK"/>
  </testsuite>
</testsuites>
''')

    def test_aunit_parser_results_global_class_tests_multiple_targets(self):
        results = sap.adt.aunit.parse_aunit_response(GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML)
        output = BufferConsole()
        sap.cli.aunit.print_aunit_junit4(results.run_results, SimpleNamespace(name=['$TMP', '$LOCAL', '$BAR']), output)

        self.maxDiff = None
        self.assertEqual(output.capout,
'''<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="$TMP|$LOCAL|$BAR">
  <testsuite name="ZCL_TEST_CLASS" package="ZCL_TEST_CLASS" tests="1">
    <testcase name="DO_THE_TEST" classname="ZCL_TEST_CLASS" status="OK"/>
  </testsuite>
</testsuites>
''')

    def test_aunit_parser_results_global_class_tests_sonar(self):
        results = sap.adt.aunit.parse_aunit_response(GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML).run_results
        output = BufferConsole()
        sap.cli.aunit.print_aunit_sonar(results, SimpleNamespace(name=['$TMP']), output)

        self.maxDiff = None
        self.assertEqual(output.capout,
'''<?xml version="1.0" encoding="UTF-8" ?>
<testExecutions version="1">
  <file path="$TMP/ZCL_TEST_CLASS=&gt;ZCL_TEST_CLASS">
    <testCase name="DO_THE_TEST" duration="0"/>
    <testCase name="ZCL_TEST_CLASS" duration="0">
      <skipped message="The global test class [ZCL_TEST_CLASS] is not abstract">
You can find further informations in document &lt;CHAP&gt; &lt;SAUNIT_TEST_CL_POOL&gt;
      </skipped>
    </testCase>
  </file>
</testExecutions>
''')

    @patch('os.walk')
    def test_print_aunit_sonar_filename_is_not_none(self, walk):
        walk.return_value = [('.', None, ['zcl_theking_manual_hardcore.clas.testclasses.abap', 'bar'])]
        results = sap.adt.aunit.parse_aunit_response(AUNIT_RESULTS_NO_TEST_METHODS_XML).run_results
        output = BufferConsole()
        sap.cli.aunit.print_aunit_sonar(results, SimpleNamespace(name=['foo']), output)

        self.assertEqual(
            output.capout,
            '''<?xml version="1.0" encoding="UTF-8" ?>
<testExecutions version="1">
  <file path="zcl_theking_manual_hardcore.clas.testclasses.abap">
  </file>
</testExecutions>
''')

    def test_aunit_class_sonar_syntax_error(self):
        self.connection.set_responses(Response(status_code=200, text=AUNIT_SYNTAX_ERROR_XML, headers={}))

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            retval = self.execute_run('class', 'yclass', '--output', 'sonar', '--result', ResultOptions.ONLY_UNIT.value)

        self.assertEqual(len(self.connection.execs), 1)
        self.assertIn('oo/classes/yclass', self.connection.execs[0].body)
        self.maxDiff = None
        self.assertEqual(mock_print.return_value.capout, '''<?xml version="1.0" encoding="UTF-8" ?>
<testExecutions version="1">
    <testCase name="CL_FOO" duration="0">
      <error message="CL_FOO has syntax errors and cannot be analyzed for existence of unit tests">
"ME-&gt;MEMBER" is not type-compatible with formal parameter "BAR".

CL_FOO======CCAU:428
      </error>
    </testCase>
</testExecutions>
''')
        self.assertEqual(mock_print.return_value.caperr,
'''''')
        self.assertEqual(retval, 1)

    def test_print_acoverage_output_raises(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.aunit.print_acoverage_output(SimpleNamespace(coverage_output='foo'), Mock(), Mock(), Mock())

        self.assertEqual(str(cm.exception), 'Unsupported output type: foo')

    @patch('sap.cli.aunit.get_acoverage_statements')
    def test_acoverage_package_with_results_raw(self, get_acoverage_statements):
        get_acoverage_statements.return_value = []

        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={})
        )

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            exit_code = self.execute_run(
                'package', 'ypackage', '--coverage-output', 'raw', '--result', ResultOptions.ONLY_COVERAGE.value
            )

        self.assertEqual(exit_code, None)
        self.assertEqual(len(self.connection.execs), 2)

        self.assertEqual(mock_print.return_value.capout, ACOVERAGE_RESULTS_XML + "\n")

    @patch('sap.cli.aunit.get_acoverage_statements')
    def test_acoverage_package_with_results_human(self, get_acoverage_statements):
        get_acoverage_statements.return_value = []

        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={})
        )

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_stdout:
            exit_code = self.execute_run(
                'package', 'ypackage', '--coverage-output', 'human', '--result', ResultOptions.ONLY_COVERAGE.value
            )

        self.assertEqual(exit_code, None)
        self.assertEqual(len(self.connection.execs), 2)

        self.assertEqual(mock_stdout.return_value.capout,
'''TEST_CHECK_LIST : 29.00%
  FOO===========================CP : 95.24%
    FOO : 95.24%
      METHOD_A : 100.00%
      METHOD_B : 75.00%
  BAR===========================CP : 0.00%
''')

    def test_acoverage_package_with_results_jacoco(self):
        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_STATEMENTS_RESULTS_XML, headers={}),
        )

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_stdout:
            exit_code = self.execute_run(
                'package', 'ypackage', '--coverage-output', 'jacoco', '--result', ResultOptions.ONLY_COVERAGE.value
            )

        self.assertEqual(exit_code, None)
        self.assertEqual(len(self.connection.execs), 3)
        self.assertEqual(mock_stdout.return_value.capout,
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">
<report name="ypackage">
   <package name="TEST_CHECK_LIST">
      <class name="FOO" sourcefilename="FOO">
         <method name="METHOD_A" line="52">
            <counter type="BRANCH" missed="2" covered="3"/>
            <counter type="METHOD" missed="0" covered="1"/>
            <counter type="INSTRUCTION" missed="0" covered="5"/>
         </method>
         <method name="METHOD_B" line="199">
            <counter type="BRANCH" missed="1" covered="1"/>
            <counter type="METHOD" missed="0" covered="1"/>
            <counter type="INSTRUCTION" missed="2" covered="6"/>
         </method>
         <counter type="BRANCH" missed="7" covered="22"/>
         <counter type="METHOD" missed="0" covered="8"/>
         <counter type="INSTRUCTION" missed="3" covered="60"/>
      </class>
      <sourcefile name="FOO">
         <line nr="53" mi="0" ci="1"/>
         <line nr="54" mi="0" ci="1"/>
         <line nr="55" mi="0" ci="1"/>
         <line nr="56" mi="0" ci="1"/>
         <line nr="59" mi="0" ci="1"/>
         <line nr="209" mi="0" ci="1"/>
         <line nr="212" mi="0" ci="1"/>
         <line nr="215" mi="0" ci="1"/>
         <line nr="216" mi="0" ci="1"/>
         <line nr="219" mi="0" ci="1"/>
         <line nr="220" mi="0" ci="1"/>
         <line nr="224" mi="1" ci="0"/>
         <line nr="225" mi="1" ci="0"/>
      </sourcefile>
      <class name="BAR" sourcefilename="BAR">
         <counter type="BRANCH" missed="0" covered="0"/>
         <counter type="METHOD" missed="0" covered="0"/>
         <counter type="INSTRUCTION" missed="0" covered="0"/>
      </class>
      <counter type="BRANCH" missed="105" covered="29"/>
      <counter type="METHOD" missed="42" covered="10"/>
      <counter type="INSTRUCTION" missed="235" covered="96"/>
   </package>
</report>
''')

    def test_result_option_all(self):
        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_STATEMENTS_RESULTS_XML, headers={}),
        )

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            exit_code = self.execute_run(
                'package', 'ypackage', '--output', 'raw', '--coverage-output', 'raw', '--result', ResultOptions.ALL.value
            )

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(self.connection.execs), 3)

        self.assertEqual(mock_print.return_value.capout, AUNIT_RESULTS_XML + "\n" + ACOVERAGE_RESULTS_XML + "\n")

    def test_result_option_unit(self):
        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})
        )

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            exit_code = self.execute_run(
                'package', 'ypackage', '--output', 'raw', '--coverage-output', 'raw', '--result', ResultOptions.ONLY_UNIT.value
            )

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(self.connection.execs), 1)

        self.maxDiff = None
        self.assertEqual(mock_print.return_value.capout, AUNIT_RESULTS_XML + "\n")

    def test_result_option_coverage(self):
        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_STATEMENTS_RESULTS_XML, headers={}),
        )

        with patch('sap.cli.core.get_console', return_value=BufferConsole()) as mock_print:
            exit_code = self.execute_run(
                'package', 'ypackage', '--output', 'raw', '--coverage-output', 'raw', '--result', ResultOptions.ONLY_COVERAGE.value
            )

        self.assertEqual(exit_code, None)
        self.assertEqual(len(self.connection.execs), 3)

        self.assertEqual(mock_print.return_value.capout, ACOVERAGE_RESULTS_XML + "\n")

    def test_coverage_filepath(self):
        self.connection.set_responses(
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_STATEMENTS_RESULTS_XML, headers={}),
        )

        coverage_filepath = 'path/to/coverage'
        with patch('sap.cli.aunit.open', mock_open()) as mock_file:
            exit_code = self.execute_run(
                'package', 'ypackage', '--output', 'raw', '--coverage-output', 'raw', '--result', ResultOptions.ONLY_COVERAGE.value,
                '--coverage-filepath', coverage_filepath
            )

        mock_file.assert_called_with(coverage_filepath, 'w+', encoding='utf8')

    def test_aunit_parser_results_global_class_tests_sonar_multiple_targets(self):
        results = sap.adt.aunit.parse_aunit_response(GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML)
        output = BufferConsole()
        sap.cli.aunit.print_aunit_sonar(results.run_results, SimpleNamespace(name=['$LOCAL', '$TMP']), output)

        self.maxDiff = None
        self.assertEqual(output.capout,
'''<?xml version="1.0" encoding="UTF-8" ?>
<testExecutions version="1">
  <file path="UNKNOWN_PACKAGE/ZCL_TEST_CLASS=&gt;ZCL_TEST_CLASS">
    <testCase name="DO_THE_TEST" duration="0"/>
    <testCase name="ZCL_TEST_CLASS" duration="0">
      <skipped message="The global test class [ZCL_TEST_CLASS] is not abstract">
You can find further informations in document &lt;CHAP&gt; &lt;SAUNIT_TEST_CL_POOL&gt;
      </skipped>
    </testCase>
  </file>
</testExecutions>
''')


class TestAUnitCommandRunTransport(unittest.TestCase):

    @patch('sap.adt.cts.Workbench.fetch_transport_request')
    def test_not_found_transport(self, fake_fetch_transports):
        fake_fetch_transports.return_value = None

        connection = Mock()
        args = parse_args('run', 'transport', 'NPLK123456')
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            args.execute(connection, args)

        self.assertEqual(str(caught.exception), 'The transport was not found: NPLK123456')

    @patch('sap.cli.core.printerr')
    @patch('sap.adt.cts.Workbench.fetch_transport_request')
    def test_no_testable_objects(self, fake_fetch_transports, fake_printerr):
        connection = Mock()

        fake_fetch_transports.return_value = sap.adt.cts.WorkbenchTransport(
            [], connection, 'NPLK123456', 'FILAK', 'Description', 'D')

        args = parse_args('run', 'transport', 'NPLK123456')
        ret = args.execute(connection, args)

        fake_printerr.assert_called_once_with('No testable objects found')
        self.assertEqual(ret, 1)

    @patch('sap.adt.cts.Workbench.fetch_transport_request')
    @patch('sap.adt.AUnit.execute')
    def test_all_kinds_and_more(self, fake_execute, fake_fetch_transports):
        connection = Connection()

        fake_fetch_transports.return_value = sap.adt.cts.WorkbenchTransport(
            [sap.adt.cts.WorkbenchTask('NPLK123456',
                [sap.adt.cts.WorkbenchABAPObject('R3TR', 'PROG', 'program', 'T', 'descr', 'X', '000000'),
                 sap.adt.cts.WorkbenchABAPObject('R3TR', 'CLAS', 'class', 'T', 'descr', 'X', '000001'),
                ],
                connection, 'NPLK123457', 'FILAK', 'Description', 'D'),
             sap.adt.cts.WorkbenchTask('NPLK123456',
                [sap.adt.cts.WorkbenchABAPObject('R3TR', 'FUGR', 'functions', 'T', 'descr', 'X', '000000'),
                 sap.adt.cts.WorkbenchABAPObject('R3TR', 'TABU', 'table', 'T', 'descr', 'X', '000001'),
                ],
                connection, 'NPLK123458', 'FILAK', 'Description', 'D'),
            ],
            connection, 'NPLK123456', 'FILAK', 'Description', 'D')

        class SentinelError(Exception):
            pass

        def assert_objects(obj_sets, activate_coverage):
            inclusive = [(ref.uri, ref.name) for ref in obj_sets.inclusive.references.references]
            self.assertEqual(inclusive, [('/sap/bc/adt/programs/programs/program', 'PROGRAM'),
                                         ('/sap/bc/adt/oo/classes/class', 'CLASS'),
                                         ('/sap/bc/adt/functions/groups/functions', 'FUNCTIONS')])
            raise SentinelError()

        fake_execute.side_effect = assert_objects

        args = parse_args('run', 'transport', 'NPLK123456')
        with self.assertRaises(SentinelError):
            args.execute(connection, args)


if __name__ == '__main__':
    unittest.main()
