#!/usr/bin/env python3
import os
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

from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.atc.CommandGroup())


class TestConfiguration(unittest.TestCase):

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


class TestRun(unittest.TestCase):

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

    def execute_run(self, *args, **kwargs):
        cmd_args = parse_args('run', *args, **kwargs)
        return cmd_args.execute(self.connection, cmd_args)

    def test_invalid_type(self):
        connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.atc.run(connection, SimpleNamespace(type='foo', name='bar'))

        self.assertEqual('Unknown type: foo', str(caught.exception))

    def test_invalid_format(self):
        connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.atc.run(connection, SimpleNamespace(type='program', name='bar', output='foo'))

        self.assertEqual('Unknown format: foo', str(caught.exception))

    def test_invalid_severity_mapping(self):
        connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.atc.run(connection, SimpleNamespace(
                type='program', name='bar', output='checkstyle', severity_mapping='[1,2,3]'
            ))

        self.assertEqual('Severity mapping has incorrect format', str(caught.exception))

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
    def test_class(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, 'ZCL_CLASS', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'class', fake_object.name)
        args.execute(self.connection, args)

        self.assertRunCalls(fake_object, fake_fetch_customizing, fake_sets, fake_runner, fake_print)

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_package(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name)
        args.execute(self.connection, args)

        self.assertRunCalls(fake_object, fake_fetch_customizing, fake_sets, fake_runner, fake_print)

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_package_multiple(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):

        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name, '$TMP')
        args.execute(self.connection, args)

        self.assertEqual(fake_object.call_args_list, [call(self.connection, fake_object.name), call(self.connection, '$TMP')])
        self.assertEqual(fake_sets.return_value.include_object.call_args_list, [call(fake_object.return_value), call(fake_object.return_value)])

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

    @patch('sap.cli.atc.print_worklist_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_text_format(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):
        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name, '-o', 'human')
        args.execute(self.connection, args)

        fake_print.assert_called_once_with('WORKLIST', sys.stdout, error_level=2)

    @patch('sap.cli.atc.print_worklist_as_html_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_html_format(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):
        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name, '-o', 'html')
        args.execute(self.connection, args)

        fake_print.assert_called_once_with('WORKLIST', sys.stdout, error_level=2)

    @patch('sap.cli.atc.print_worklist_as_checkstyle_xml_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_xml_format(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):
        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        args = parse_args('run', 'package', fake_object.name, '-o', 'checkstyle')
        args.execute(self.connection, args)

        fake_print.assert_called_once_with('WORKLIST', sys.stdout, error_level=2, severity_mapping=None)


    @patch('sap.cli.atc.print_worklist_as_checkstyle_xml_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_xml_format_with_mapping_from_arg(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):
        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        severity_mapping_str = '{"1":"error"}'
        args = parse_args(
            'run', 'package', fake_object.name, '-o', 'checkstyle', '-s', severity_mapping_str
        )
        args.execute(self.connection, args)

        fake_print.assert_called_once_with('WORKLIST', sys.stdout, error_level=2, severity_mapping={'1': 'error'})

    @patch('sap.cli.atc.print_worklist_as_checkstyle_xml_to_stream')
    @patch('sap.adt.objects.ADTObjectSets')
    @patch('sap.adt.atc.ChecksRunner')
    @patch('sap.adt.atc.fetch_customizing')
    @patch('sap.adt.Package')
    def test_with_xml_format_with_mapping_from_env(self, fake_object, fake_fetch_customizing, fake_runner, fake_sets, fake_print):
        self.setUpRunMocks(fake_object, '$PACKAGE', fake_fetch_customizing, fake_runner, fake_sets)

        severity_mapping_str = '{"1":"error"}'
        args = parse_args(
            'run', 'package', fake_object.name, '-o', 'checkstyle'
        )
        with patch.dict(os.environ, {'SEVERITY_MAPPING': severity_mapping_str}):
            args.execute(self.connection, args)

        fake_print.assert_called_once_with('WORKLIST', sys.stdout, error_level=2, severity_mapping={'1': 'error'})


class TestPrintWorklistMixin:

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


class TestPrintWorklistToStream(TestPrintWorklistMixin, unittest.TestCase):

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


class TestPrintWorklistToStreamAsHtml(TestPrintWorklistMixin, unittest.TestCase):

    def test_all_loops(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_as_html_to_stream(self.worklist, output)
        self.assertEqual(output.getvalue(),
'''<table>
<tr><th>Object type ID</th>
<th>Name</th></tr>
<tr><td>FAKE/TEST</td>
<td>MADE_UP_OBJECT</td></tr>
<tr><th>Priority</th>
<th>Check title</th>
<th>Message title</th></tr>
<tr><td>1</td>
<td>UNIT_TEST</td>
<td>Unit tests for ATC module of sapcli</td></tr>
<tr><td>2</td>
<td>PRIO_2</td>
<td>Prio 2</td></tr>
<tr><td>3</td>
<td>PRIO_3</td>
<td>Prio 3</td></tr>
<tr><td>4</td>
<td>PRIO_4</td>
<td>Prio 4</td></tr>
</table>
''')
        self.assertEqual(1, ret)

    def test_error_level_2(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_as_html_to_stream(self.worklist, output, error_level=2)
        self.assertEqual(output.getvalue(),
'''<table>
<tr><th>Object type ID</th>
<th>Name</th></tr>
<tr><td>FAKE/TEST</td>
<td>MADE_UP_OBJECT</td></tr>
<tr><th>Priority</th>
<th>Check title</th>
<th>Message title</th></tr>
<tr><td>1</td>
<td>UNIT_TEST</td>
<td>Unit tests for ATC module of sapcli</td></tr>
<tr><td>2</td>
<td>PRIO_2</td>
<td>Prio 2</td></tr>
<tr><td>3</td>
<td>PRIO_3</td>
<td>Prio 3</td></tr>
<tr><td>4</td>
<td>PRIO_4</td>
<td>Prio 4</td></tr>
</table>
''')
        self.assertEqual(1, ret)

    def test_error_level_0(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_as_html_to_stream(self.worklist, output, error_level=0)
        self.assertEqual(output.getvalue(),
'''<table>
<tr><th>Object type ID</th>
<th>Name</th></tr>
<tr><td>FAKE/TEST</td>
<td>MADE_UP_OBJECT</td></tr>
<tr><th>Priority</th>
<th>Check title</th>
<th>Message title</th></tr>
<tr><td>1</td>
<td>UNIT_TEST</td>
<td>Unit tests for ATC module of sapcli</td></tr>
<tr><td>2</td>
<td>PRIO_2</td>
<td>Prio 2</td></tr>
<tr><td>3</td>
<td>PRIO_3</td>
<td>Prio 3</td></tr>
<tr><td>4</td>
<td>PRIO_4</td>
<td>Prio 4</td></tr>
</table>
''')
        self.assertEqual(0, ret)

class TestPrintWorklistToStreamAsXml(TestPrintWorklistMixin, unittest.TestCase):

    def test_all_loops(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_as_checkstyle_xml_to_stream(self.worklist, output)
        self.assertEqual(output.getvalue(),
'''<?xml version="1.0" encoding="UTF-8"?>
<checkstyle version="8.36">
<file name="FAKE/TEST/MADE_UP_OBJECT">
<error severity="error" message="Unit tests for ATC module of sapcli" source="UNIT_TEST"/>
<error severity="error" message="Prio 2" source="PRIO_2"/>
<error severity="warning" message="Prio 3" source="PRIO_3"/>
<error severity="warning" message="Prio 4" source="PRIO_4"/>
</file>
</checkstyle>
''')
        self.assertEqual(1, ret)

    def test_error_level_2(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_as_checkstyle_xml_to_stream(self.worklist, output, error_level=2)
        self.assertEqual(output.getvalue(),
'''<?xml version="1.0" encoding="UTF-8"?>
<checkstyle version="8.36">
<file name="FAKE/TEST/MADE_UP_OBJECT">
<error severity="error" message="Unit tests for ATC module of sapcli" source="UNIT_TEST"/>
<error severity="error" message="Prio 2" source="PRIO_2"/>
<error severity="warning" message="Prio 3" source="PRIO_3"/>
<error severity="warning" message="Prio 4" source="PRIO_4"/>
</file>
</checkstyle>
''')
        self.assertEqual(1, ret)

    def test_error_level_0(self):
        output = StringIO()
        ret = sap.cli.atc.print_worklist_as_checkstyle_xml_to_stream(self.worklist, output, error_level=0)
        self.assertEqual(output.getvalue(),
'''<?xml version="1.0" encoding="UTF-8"?>
<checkstyle version="8.36">
<file name="FAKE/TEST/MADE_UP_OBJECT">
<error severity="error" message="Unit tests for ATC module of sapcli" source="UNIT_TEST"/>
<error severity="error" message="Prio 2" source="PRIO_2"/>
<error severity="warning" message="Prio 3" source="PRIO_3"/>
<error severity="warning" message="Prio 4" source="PRIO_4"/>
</file>
</checkstyle>
''')
        self.assertEqual(0, ret)

    def test_severity_mapping(self):
        output = StringIO()
        severity_mapping = {
            '1': 'info',
            '2': 'warning',
            '3': 'error'
        }
        ret = sap.cli.atc.print_worklist_as_checkstyle_xml_to_stream(self.worklist, output, severity_mapping=severity_mapping)
        self.assertEqual(output.getvalue(),
'''<?xml version="1.0" encoding="UTF-8"?>
<checkstyle version="8.36">
<file name="FAKE/TEST/MADE_UP_OBJECT">
<error severity="info" message="Unit tests for ATC module of sapcli" source="UNIT_TEST"/>
<error severity="warning" message="Prio 2" source="PRIO_2"/>
<error severity="error" message="Prio 3" source="PRIO_3"/>
<error severity="info" message="Prio 4" source="PRIO_4"/>
</file>
</checkstyle>
''')
        self.assertEqual(1, ret)

if __name__ == '__main__':
    unittest.main()
