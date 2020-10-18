#!/usr/bin/env python3

import sys
from argparse import ArgumentParser

import unittest
from unittest.mock import patch, call, Mock, mock_open
from io import StringIO
from types import SimpleNamespace

from fixtures_adt_coverage import ACOVERAGE_RESULTS_XML
from sap.errors import SAPCliError
import sap.cli.aunit
import sap.adt.cts

from mock import Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK
from fixtures_adt_aunit import AUNIT_NO_TEST_RESULTS_XML, AUNIT_RESULTS_XML, GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML
from sap.cli.aunit import ResultOptions

parser = ArgumentParser()
sap.cli.aunit.CommandGroup().install_parser(parser)


def parse_args(*argv):
    return parser.parse_args(argv)


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
            call('Warnings:   0', file=sys.stdout))

        self.assertEqual(
            mock_print.call_args_list[3],
            call('Errors:     0', file=sys.stdout))

    def test_aunit_invalid(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.aunit.run('wrongconn', SimpleNamespace(type='foo', output='human'))

        self.assertEqual(str(cm.exception), 'Unknown type: foo')

    def test_aunit_program(self):
        connection = Connection([Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(
                type='program', name='yprogram', output='human', result=ResultOptions.ONLY_UNIT.value
            ))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('programs/programs/yprogram', connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_class(self):
        connection = Connection([Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(
                type='class', name='yclass', output='human', result=ResultOptions.ONLY_UNIT.value
            ))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('oo/classes/yclass', connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_package(self):
        connection = Connection([Response(status_code=200, text=AUNIT_NO_TEST_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage', output='human', result=ResultOptions.ONLY_UNIT.value
            ))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)
        self.assert_print_no_test_classes(mock_print)

    def test_aunit_package_with_results(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage', output='human', result=ResultOptions.ONLY_UNIT.value
            ))

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
        self.assertEqual(mock_print.call_args_list[21], call('Warnings:   0', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[22], call('Errors:     3', file=sys.stdout))

    def test_aunit_package_with_results_raw(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage', output='raw', result=ResultOptions.ONLY_UNIT.value
            ))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)

        self.assertEqual(mock_print.call_args_list[0][0], (AUNIT_RESULTS_XML,))

    def test_aunit_package_with_results_junit4(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage', output='junit4', result=ResultOptions.ONLY_UNIT.value
            ))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)

        self.maxDiff = None
        self.assertEqual(mock_stdout.getvalue(),
'''<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="ypackage">
  <testsuite name="LTCL_TEST" package="ZCL_THEKING_MANUAL_HARDCORE" tests="2">
    <testcase name="DO_THE_FAIL" classname="ZCL_THEKING_MANUAL_HARDCORE=&gt;LTCL_TEST" status="ERR">
      <system-err>True expected
Test 'LTCL_TEST-&gt;DO_THE_FAIL' in Main Program 'ZCL_THEKING_MANUAL_HARDCORE===CP'.</system-err>
      <error type="failedAssertion" message="Critical Assertion Error: 'I am supposed to fail'">Include: &lt;ZCL_THEKING_MANUAL_HARDCORE===CCAU&gt; Line: &lt;19&gt; (DO_THE_FAIL)</error>
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

    def test_aunit_package_with_results_sonar(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage', output='sonar', result=ResultOptions.ONLY_UNIT.value
            ))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)

        self.maxDiff = None
        self.assertEqual(mock_stdout.getvalue(),
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
        output = StringIO()
        sap.cli.aunit.print_aunit_junit4(results, SimpleNamespace(name='$TMP'), output)

        self.maxDiff = None
        self.assertEqual(output.getvalue(),
'''<?xml version="1.0" encoding="UTF-8" ?>
<testsuites name="$TMP">
  <testsuite name="ZCL_TEST_CLASS" package="ZCL_TEST_CLASS" tests="1">
    <testcase name="DO_THE_TEST" classname="ZCL_TEST_CLASS" status="OK"/>
  </testsuite>
</testsuites>
''')

    def test_aunit_parser_results_global_class_tests_sonar(self):
        results = sap.adt.aunit.parse_aunit_response(GLOBAL_TEST_CLASS_AUNIT_RESULTS_XML).run_results
        output = StringIO()
        sap.cli.aunit.print_aunit_sonar(results, SimpleNamespace(name='$TMP'), output)

        self.maxDiff = None
        self.assertEqual(output.getvalue(),
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

    def test_acoverage_package_with_results_raw(self):
        connection = Connection([
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
        ])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage',
                coverage_output='raw', coverage_filepath=None,
                result=sap.cli.aunit.ResultOptions.ONLY_COVERAGE.value
            ))

        self.assertEqual(exit_code, None)
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(mock_print.call_args_list[0], call(ACOVERAGE_RESULTS_XML, file=sys.stdout))

    def test_acoverage_package_with_results_human(self):
        connection = Connection([
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
        ])

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage',
                coverage_output='human', coverage_filepath=None,
                result=sap.cli.aunit.ResultOptions.ONLY_COVERAGE.value
            ))

        self.assertEqual(exit_code, None)
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(mock_stdout.getvalue(),
'''TEST_CHECK_LIST : 29.00%
  FOO===========================CP : 95.24%
    FOO : 95.24%
      METHOD_A : 100.00%
      METHOD_B : 75.00%
  BAR===========================CP : 0.00%
''')

    def test_acoverage_package_with_results_jacoco(self):
        connection = Connection([
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
        ])

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage',
                coverage_output='jacoco', coverage_filepath=None,
                result=sap.cli.aunit.ResultOptions.ONLY_COVERAGE.value
            ))

        self.assertEqual(exit_code, None)
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(mock_stdout.getvalue(),
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">
<report name="ypackage">
   <package name="TEST_CHECK_LIST">
      <class name="FOO===========================CP">
         <counter type="BRANCH" missed="7" covered="22"/>
         <counter type="METHOD" missed="0" covered="8"/>
         <counter type="INSTRUCTION" missed="3" covered="60"/>
      </class>
      <class name="FOO">
         <method name="METHOD_A">
            <counter type="BRANCH" missed="2" covered="3"/>
            <counter type="METHOD" missed="0" covered="1"/>
            <counter type="INSTRUCTION" missed="0" covered="5"/>
         </method>
         <method name="METHOD_B">
            <counter type="BRANCH" missed="1" covered="1"/>
            <counter type="METHOD" missed="0" covered="1"/>
            <counter type="INSTRUCTION" missed="2" covered="6"/>
         </method>
         <counter type="BRANCH" missed="7" covered="22"/>
         <counter type="METHOD" missed="0" covered="8"/>
         <counter type="INSTRUCTION" missed="3" covered="60"/>
      </class>
      <class name="BAR===========================CP">
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
        connection = Connection([
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
        ])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage',
                coverage_output='raw', output='raw',
                coverage_filepath=None,
                result=sap.cli.aunit.ResultOptions.ALL.value
            ))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(len(mock_print.call_args_list), 2)
        self.assertEqual(mock_print.call_args_list[0], call(AUNIT_RESULTS_XML, file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[1], call(ACOVERAGE_RESULTS_XML, file=sys.stdout))

    def test_result_option_unit(self):
        connection = Connection([
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
        ])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage',
                coverage_output='raw', output='raw',
                coverage_filepath=None,
                result=sap.cli.aunit.ResultOptions.ONLY_UNIT.value
            ))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)

        self.assertEqual(len(mock_print.call_args_list), 1)
        self.assertEqual(mock_print.call_args_list[0], call(AUNIT_RESULTS_XML, file=sys.stdout))

    def test_result_option_coverage(self):
        connection = Connection([
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
        ])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage',
                coverage_output='raw', output='raw',
                coverage_filepath=None,
                result=sap.cli.aunit.ResultOptions.ONLY_COVERAGE.value
            ))

        self.assertEqual(exit_code, None)
        self.assertEqual(len(connection.execs), 2)

        self.assertEqual(len(mock_print.call_args_list), 1)
        self.assertEqual(mock_print.call_args_list[0], call(ACOVERAGE_RESULTS_XML, file=sys.stdout))

    def test_coverage_filepath(self):
        connection = Connection([
            Response(status_code=200, text=AUNIT_RESULTS_XML, headers={}),
            Response(status_code=200, text=ACOVERAGE_RESULTS_XML, headers={}),
        ])

        coverage_filepath = 'path/to/coverage'
        with patch('sap.cli.aunit.open', mock_open()) as mock_file:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(
                type='package', name='ypackage',
                coverage_output='raw', output='raw',
                coverage_filepath=coverage_filepath,
                result=sap.cli.aunit.ResultOptions.ONLY_COVERAGE.value
            ))

        mock_file.assert_called_with(coverage_filepath, 'w+')


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
                [sap.adt.cts.WorkbenchABAPObject('R3TR', 'PROG', 'program', 'T', 'descr', 'X'),
                 sap.adt.cts.WorkbenchABAPObject('R3TR', 'CLAS', 'class', 'T', 'descr', 'X'),
                ],
                connection, 'NPLK123457', 'FILAK', 'Description', 'D'),
             sap.adt.cts.WorkbenchTask('NPLK123456',
                [sap.adt.cts.WorkbenchABAPObject('R3TR', 'FUGR', 'functions', 'T', 'descr', 'X'),
                 sap.adt.cts.WorkbenchABAPObject('R3TR', 'TABU', 'table', 'T', 'descr', 'X'),
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
