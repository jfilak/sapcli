#!/usr/bin/env python3

import sys
import unittest
from unittest.mock import patch, Mock, call
from argparse import ArgumentParser
from types import SimpleNamespace
from io import StringIO

from sap.errors import SAPCliError
import sap.cli.atc
from sap.adt.objects import ADTObjectSets

from mock import Connection, Response


parser = ArgumentParser()
sap.cli.atc.CommandGroup().install_parser(parser)


def parse_args(*argv):
    global parser
    return parser.parse_args(argv)


class TetsConfiguration(unittest.TestCase):

    @patch('sap.adt.atc.fetch_customizing')
    def test_default(self, fake_fetch_customizing):
        connection = Mock()

        fake_fetch_customizing.return_value = Mock()
        fake_fetch_customizing.return_value.system_check_variant = 'THE_VARIANT'

        args = parse_args('customizing')
        with patch('sap.cli.atc.printout', Mock()) as fake_printout:
            args.execute(connection, args)

        fake_fetch_customizing.assert_called_once_with(connection)
        fake_printout.assert_called_once_with('System Check Variant:', 'THE_VARIANT')


class TetsRun(unittest.TestCase):

    def setUp(self):
        self.connection = Connection()

    def setUpObject(self, fake_object, name):
        fake_object.return_value = Mock()
        fake_object.name = name

    def setUpCustomizing(self, fake_fetch_customizing):
        fake_fetch_customizing.return_value = Mock()
        fake_fetch_customizing.return_value.system_check_variant = 'THE_VARIANT'

    def setUpChecksRunner(self, fake_runner):
        fake_runner.return_value = Mock()
        fake_runner.return_value.run_for.return_value = SimpleNamespace(run_results='RESULTS', worklist='WORKLIST')

    def setUpADTObjectSets(self, fake_runner):
        fake_runner.return_value = Mock()
        fake_runner.return_value.include_object = Mock()

    def setUpRunMocks(self, fake_object, object_name, fake_fetch_customizing, fake_runner, fake_sets):
        self.setUpObject(fake_object, object_name)
        self.setUpCustomizing(fake_fetch_customizing)
        self.setUpChecksRunner(fake_runner)
        self.setUpADTObjectSets(fake_sets)

    def assertRunCalls(self, fake_object, fake_fetch_customizing, fake_sets, fake_runner, fake_print):
        fake_fetch_customizing.assert_called_once_with(self.connection)

        fake_object.assert_called_once_with(self.connection, fake_object.name)

        fake_sets.assert_called_once()
        fake_sets.return_value.include_object.assert_called_once_with(fake_object.return_value)

        fake_runner.assert_called_once_with(self.connection, 'THE_VARIANT')
        fake_runner.return_value.run_for.assert_called_once_with(fake_sets.return_value, max_verdicts=100)

        fake_print.assert_called_once_with('WORKLIST', sys.stdout, error_level=2)

    def test_invalid_type(self):
        connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.atc.run(connection, SimpleNamespace(type='foo', name='bar'))

        self.assertEqual('Unknown type: foo', str(caught.exception))

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Program')
    def test_program(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, 'ZREPORT', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'program', fake_object.name)
        args.execute(self.connection, args)

        self.assertRunCalls(fake_object, fake_fetch_customizing, fake_sets, fake_runner, fake_print)

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Class')
    def test_program(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, 'ZCL_CLASS', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'class', fake_object.name)
        args.execute(self.connection, args)

        self.assertRunCalls(fake_object, fake_fetch_customizing, fake_sets, fake_runner, fake_print)

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_program(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name)
        args.execute(self.connection, args)

        self.assertRunCalls(fake_object, fake_fetch_customizing, fake_sets, fake_runner, fake_print)

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_variant(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name, '-r', 'MY_SPECIAL_VARIANT')
        args.execute(self.connection, args)

        fake_fetch_customizing.assert_not_called()
        fake_runner.assert_called_once_with(self.connection, 'MY_SPECIAL_VARIANT')

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_max_verdicts(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name, '-m', '69')
        args.execute(self.connection, args)

        fake_runner.return_value.run_for.assert_called_once_with(fake_sets.return_value, max_verdicts=69)

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_erro_level(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name, '-e', '100')
        args.execute(self.connection, args)

        fake_print.assert_called_once_with('WORKLIST', sys.stdout, error_level=100)


class TetsPrintWorklistToStream(unittest.TestCase):

    def setUp(self):
        atcobject = sap.adt.atc.ATCObject()
        atcobject.object_type_id = 'FAKE/TEST'
        atcobject.name = 'MADE_UP_OBJECT'
        atcobject.findings = sap.adt.atc.ATCFindingList()

        finding = sap.adt.atc.ATCFinding()
        finding.priority = 1
        finding.check_title = 'UNIT_TEST'
        finding.message_title = 'Unit tests for ATC module of sapcli'
        atcobject.findings.append(finding)

        finding = sap.adt.atc.ATCFinding()
        finding.priority = 2
        finding.check_title = 'PRIO_2'
        finding.message_title = 'Prio 2'
        atcobject.findings.append(finding)

        finding = sap.adt.atc.ATCFinding()
        finding.priority = 3
        finding.check_title = 'PRIO_3'
        finding.message_title = 'Prio 3'
        atcobject.findings.append(finding)

        finding = sap.adt.atc.ATCFinding()
        finding.priority = 4
        finding.check_title = 'PRIO_4'
        finding.message_title = 'Prio 4'
        atcobject.findings.append(finding)

        self.worklist = sap.adt.atc.WorkList()
        self.worklist.objects = sap.adt.atc.ATCObjectList()
        self.worklist.objects.append(atcobject)

    def test_all_loops(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_to_stream(self.worklist, output)
        self.assertEqual(output.getvalue(),
'''FAKE/TEST/MADE_UP_OBJECT
* 1 :: UNIT_TEST :: Unit tests for ATC module of sapcli
* 2 :: PRIO_2 :: Prio 2
* 3 :: PRIO_3 :: Prio 3
* 4 :: PRIO_4 :: Prio 4
''')
        self.assertEqual(1, ret)

    def test_error_level_2(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_to_stream(self.worklist, output, error_level=2)
        self.assertEqual(output.getvalue(),
'''FAKE/TEST/MADE_UP_OBJECT
* 1 :: UNIT_TEST :: Unit tests for ATC module of sapcli
* 2 :: PRIO_2 :: Prio 2
* 3 :: PRIO_3 :: Prio 3
* 4 :: PRIO_4 :: Prio 4
''')
        self.assertEqual(1, ret)

    def test_error_level_0(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_to_stream(self.worklist, output, error_level=0)
        self.assertEqual(output.getvalue(),
'''FAKE/TEST/MADE_UP_OBJECT
* 1 :: UNIT_TEST :: Unit tests for ATC module of sapcli
* 2 :: PRIO_2 :: Prio 2
* 3 :: PRIO_3 :: Prio 3
* 4 :: PRIO_4 :: Prio 4
''')
        self.assertEqual(0, ret)


if __name__ == '__main__':
    unittest.main()
