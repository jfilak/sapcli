#!/usr/bin/env python3

import sys

import unittest
from unittest.mock import patch, call
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
        self.assertEqual(mock_print.call_args_list[18], call('', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[19], call('Successful: 3', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[20], call('Tolerable:  0', file=sys.stdout))
        self.assertEqual(mock_print.call_args_list[21], call('Critical:   3', file=sys.stdout))

    def test_aunit_package_with_results_raw(self):
        connection = Connection([Response(status_code=200, text=AUNIT_RESULTS_XML, headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            exit_code = sap.cli.aunit.run(connection, SimpleNamespace(type='package', name='ypackage', output='raw'))

        self.assertEqual(exit_code, 3)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)

        self.assertEqual(mock_print.call_args_list[0], call(AUNIT_RESULTS_XML))


if __name__ == '__main__':
    unittest.main()
