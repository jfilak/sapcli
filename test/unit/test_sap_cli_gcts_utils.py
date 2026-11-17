"""Test sap.cli.gcts_utils module"""

import unittest
import types
from unittest.mock import patch, Mock
from test.unit.mock import (
    ConsoleOutputTestCase,
    BufferConsole
)
from sap.cli.gcts_utils import (
    print_gcts_task_info,
    print_gcts_message,
    dump_gcts_messages,
    gcts_exception_handler,
    print_process_messages,
    parse_object_spec,
    parse_object_list,
)
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.errors import SAPCliError, GCTSRequestError, GCTSProcessError
from sap.rest.gcts.log_messages import ProcessMessage

from test.unit.fixtures_sap_rest_gcts import CLONE_ERROR_PROCESS_MESSAGES_RAW


class TestPrintGCTSTaskInfo(ConsoleOutputTestCase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.task_dict = {
            'tid': '123',
            'rid': 'sample',
            'type': 'CLONE_REPOSITORY',
            'status': 'RUNNING'
        }

    def test_print_gcts_task_info_with_task(self):
        """Test print_gcts_task_info when task is provided (no error)"""

        print_gcts_task_info(self.console, None, self.task_dict)
        self.assertConsoleContents(console=self.console, stdout=f'\nTask Status: {self.task_dict["status"]}\n', stderr='')

    def test_print_gcts_task_info_with_error(self):
        """Test print_gcts_task_info when error message is provided"""
        error_message = 'Task retrieval failed: Connection error'

        print_gcts_task_info(self.console, error_message, None)
        self.assertConsoleContents(console=self.console, stderr= error_message + '\n', stdout='')


class TestPrintGCTSMessage(ConsoleOutputTestCase, unittest.TestCase):
    def test_print_gcts_message_with_string(self):
        log = 'Simple error message'
        print_gcts_message(self.console, log)
        self.assertConsoleContents(console=self.console, stderr='  Simple error message\n')

    def test_print_gcts_message_with_string_custom_prefix(self):
        log = 'Error message'
        print_gcts_message(self.console, log, prefix='>>>')
        self.assertConsoleContents(console=self.console, stderr='>>> Error message\n')

    def test_print_gcts_message_with_dict_message_only(self):
        log = {'message': 'Dict error message'}
        print_gcts_message(self.console, log)
        self.assertConsoleContents(console=self.console, stderr='  Dict error message\n')

    def test_print_gcts_message_with_dict_no_message(self):
        log = {'other': 'value'}
        print_gcts_message(self.console, log)
        self.assertConsoleContents(console=self.console, stderr='')

    def test_print_gcts_message_with_dict_protocol_dict(self):
        log = {
            'message': 'Main message',
            'protocol': {
                'message': 'Protocol message'
            }
        }
        print_gcts_message(self.console, log)
        self.assertConsoleContents(console=self.console, stderr='  Main message\n    Protocol message\n')

    def test_print_gcts_message_with_dict_protocol_list(self):
        log = {
            'message': 'Main message',
            'protocol': [
                {'message': 'Protocol message 1'},
                {'message': 'Protocol message 2'}
            ]
        }
        print_gcts_message(self.console, log)
        self.assertConsoleContents(console=self.console, stderr='  Main message\n    Protocol message 1\n    Protocol message 2\n')

    def test_print_gcts_message_with_dict_nested_protocol(self):
        log = {
            'message': 'Level 1',
            'protocol': {
                'message': 'Level 2',
                'protocol': {
                    'message': 'Level 3'
                }
            }
        }
        print_gcts_message(self.console, log)
        self.assertConsoleContents(console=self.console, stderr='  Level 1\n    Level 2\n      Level 3\n')

    def test_print_gcts_message_with_dict_no_protocol_key(self):
        log = {'message': 'Message without protocol'}
        print_gcts_message(self.console, log)
        self.assertConsoleContents(console=self.console, stderr='  Message without protocol\n')

    def test_print_gcts_message_with_non_dict_non_string(self):
        log = 123
        with self.assertRaises(AttributeError):
            print_gcts_message(self.console, log)


class TestDumpGCTSMessages(ConsoleOutputTestCase, unittest.TestCase):
    @patch('sap.cli.gcts_utils.print_gcts_message')
    def test_dump_gcts_messages_with_error_log(self, mock_print_gcts_message):
        messages = {
            'errorLog': [
                {'message': 'Error 1'},
                {'message': 'Error 2'}
            ]
        }
        dump_gcts_messages(self.console, messages)
        self.assertEqual(mock_print_gcts_message.call_count, 2)
        self.assertConsoleContents(console=self.console, stderr='Error Log:\n')

    @patch('sap.cli.gcts_utils.print_gcts_message')
    def test_dump_gcts_messages_with_log(self, mock_print_gcts_message):
        messages = {
            'log': [
                {'message': 'Log 1'},
                {'message': 'Log 2'}
            ]
        }
        dump_gcts_messages(self.console, messages)
        self.assertEqual(mock_print_gcts_message.call_count, 2)
        self.assertConsoleContents(console=self.console, stderr='Log:\n')

    @patch('sap.cli.gcts_utils.print_gcts_message')
    def test_dump_gcts_messages_with_exception(self, mock_print_gcts_message):
        messages = {
            'exception': 'Exception message here'
        }
        dump_gcts_messages(self.console, messages)
        mock_print_gcts_message.assert_not_called()
        self.assertConsoleContents(console=self.console, stderr='Exception:\n  Exception message here\n')

    @patch('sap.cli.gcts_utils.print_gcts_message')
    def test_dump_gcts_messages_with_all_fields(self, mock_print_gcts_message):
        messages = {
            'errorLog': [{'message': 'Error 1'}],
            'log': [{'message': 'Log 1'}],
            'exception': 'Exception text'
        }
        dump_gcts_messages(self.console, messages)
        self.assertEqual(mock_print_gcts_message.call_count, 2)
        expected_stderr = 'Error Log:\nLog:\nException:\n  Exception text\n'
        self.assertConsoleContents(console=self.console, stderr=expected_stderr)

    def test_dump_gcts_messages_with_no_output(self):
        messages = {}
        dump_gcts_messages(self.console, messages)
        self.assertConsoleContents(console=self.console, stderr='{}\n')

    def test_dump_gcts_messages_with_none_values(self):
        messages = {
            'errorLog': None,
            'log': None,
            'exception': None
        }
        dump_gcts_messages(self.console, messages)
        self.assertConsoleContents(console=self.console, stderr='{\'errorLog\': None, \'log\': None, \'exception\': None}\n')


class TestGCTSExceptionHandler(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_console = Mock()
        self.mock_console.printerr = Mock()

    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_success(self, mock_get_console):
        mock_get_console.return_value = self.mock_console

        @gcts_exception_handler
        def test_func(connection, args):
            return 0

        result = test_func(Mock(), Mock())
        self.assertEqual(result, 0)
        mock_get_console.assert_not_called()

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_gcts_request_error(self, mock_get_console, mock_dump_gcts_messages):
        mock_get_console.return_value = self.mock_console
        mock_messages = {'errorLog': [{'message': 'GCTS error'}]}
        gcts_error = GCTSRequestError(mock_messages)

        @gcts_exception_handler
        def test_func(connection, args):
            raise gcts_error

        result = test_func(Mock(), Mock())
        self.assertEqual(result, 1)
        mock_get_console.assert_called_once()
        mock_dump_gcts_messages.assert_called_once_with(self.mock_console, mock_messages)

    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_sap_cli_error(self, mock_get_console):
        mock_get_console.return_value = self.mock_console
        sap_error = SAPCliError('SAP CLI error message')

        @gcts_exception_handler
        def test_func(connection, args):
            raise sap_error

        result = test_func(Mock(), Mock())
        self.assertEqual(result, 1)
        mock_get_console.assert_called_once()
        self.mock_console.printerr.assert_called_once_with('SAP CLI error message')

    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_other_exception(self, mock_get_console):
        mock_get_console.return_value = self.mock_console

        @gcts_exception_handler
        def test_func(connection, args):
            raise ValueError('Other error')

        with self.assertRaises(ValueError):
            test_func(Mock(), Mock())
        mock_get_console.assert_not_called()


    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_gcts_exception_handler_gcts_request_error(self, mock_dump_gcts_messages):
        mock_messages = {'errorLog': [{'message': 'GCTS error'}]}
        gcts_error = GCTSRequestError(mock_messages)

        my_console = Mock()
        def test_console_factory():
            return my_console

        @gcts_exception_handler
        def test_func(connection, args):
            raise gcts_error

        result = test_func(Mock(), types.SimpleNamespace(console_factory=test_console_factory))
        self.assertEqual(result, 1)
        mock_dump_gcts_messages.assert_called_once_with(my_console, mock_messages)

    def test_gcts_exception_handler_sap_cli_error(self):
        sap_error = SAPCliError('SAP CLI error message')

        console = BufferConsole()
        def test_console_factory():
            return console

        @gcts_exception_handler
        def test_func(connection, args):
            raise sap_error

        result = test_func(Mock(), types.SimpleNamespace(console_factory=test_console_factory))
        self.assertEqual(result, 1)
        self.assertEqual(console.caperr, 'SAP CLI error message\n')


class TestGCTSExceptionHandlerProcessError(ConsoleOutputTestCase, unittest.TestCase):

    def test_gcts_exception_handler_catches_process_error(self):

        process_messages = [ProcessMessage(msg) for msg in CLONE_ERROR_PROCESS_MESSAGES_RAW]
        process_error = GCTSProcessError(process_messages)

        console = BufferConsole()
        def test_console_factory():
            return console

        @gcts_exception_handler
        def test_func(connection, args):
            raise process_error

        result = test_func(Mock(), types.SimpleNamespace(console_factory=test_console_factory))
        self.assertEqual(result, 1)
        self.assertIn('Date', console.capout)
        self.assertIn('Action', console.capout)
        self.assertIn('Application', console.capout)
        self.assertIn('Severity', console.capout)
        self.assertIn('FINISH_JOB', console.capout)
        self.assertIn('gCTS', console.capout)
        self.assertIn('ERROR', console.capout)
        self.assertIn('2026-06-04 16:43:23', console.capout)
        self.assertIn('Job GCTS_CLONE_REPO finished but the action failed', console.capout)
        self.assertIn('GET_SOURCE_FROM_REMOTE', console.capout)
        self.assertIn('Transport Tools', console.capout)
        self.assertIn('This is tp version 381.742.08 (release 920) (Patch level:4)', console.capout)
        self.assertIn('CLONE', console.capout)
        self.assertIn('Error when cloning repository.', console.capout)
        self.assertIn('EXECUTE_JOB', console.capout)
        self.assertIn('RUNNING', console.capout)
        self.assertIn('LOG_LEVEL', console.capout)
        self.assertIn('SCHEDULE_JOB', console.capout)
        self.assertIn('SCHEDULED', console.capout)

    @patch('sap.cli.gcts_utils.print_process_messages')
    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_process_error_calls_print_process_messages(self, mock_get_console, mock_print):
        mock_console = Mock()
        mock_get_console.return_value = mock_console

        process_messages = [ProcessMessage({'action': 'CLONE', 'severity': 'ERROR', 'application': 'gCTS', 'applInfo': 'Error', 'time': 20260604164322})]
        process_error = GCTSProcessError(process_messages)

        @gcts_exception_handler
        def test_func(connection, args):
            raise process_error

        result = test_func(Mock(), types.SimpleNamespace())
        self.assertEqual(result, 1)
        mock_get_console.assert_called_once()
        mock_print.assert_called_once_with(mock_console, process_messages)



class TestParseObjectSpec(unittest.TestCase):

    def assert_invalid_spec(self, spec):
        with self.assertRaises(SAPCliError) as caught:
            parse_object_spec(spec)

        self.assertEqual(str(caught.exception),
                         f'Invalid object "{spec}": expected [PGMID:]TYPE:NAME[,NAME...]')

    def test_type_and_name_defaults_to_r3tr(self):
        self.assertEqual(parse_object_spec('CLAS:ZCL_FOO'), [('R3TR', 'CLAS', 'ZCL_FOO')])

    def test_pgmid_type_and_name(self):
        self.assertEqual(parse_object_spec('LIMU:METH:ZCL_FOO                       BAR'),
                         [('LIMU', 'METH', 'ZCL_FOO                       BAR')])

    def test_more_names(self):
        self.assertEqual(parse_object_spec('R3TR:CLAS:ZCL_A,ZCL_B,ZCL_C'),
                         [('R3TR', 'CLAS', 'ZCL_A'),
                          ('R3TR', 'CLAS', 'ZCL_B'),
                          ('R3TR', 'CLAS', 'ZCL_C')])

    def test_more_names_defaults_to_r3tr(self):
        self.assertEqual(parse_object_spec('PROG:ZREPORT,ZINCLUDE'),
                         [('R3TR', 'PROG', 'ZREPORT'),
                          ('R3TR', 'PROG', 'ZINCLUDE')])

    def test_surrounding_spaces_are_removed(self):
        self.assertEqual(parse_object_spec(' limu : meth : ZCL_A                         RUN , ZCL_B '),
                         [('LIMU', 'METH', 'ZCL_A                         RUN'),
                          ('LIMU', 'METH', 'ZCL_B')])

    def test_blank_name_in_list(self):
        self.assert_invalid_spec('CLAS:ZCL_A, ,ZCL_B')

    def test_namespaced_name(self):
        self.assertEqual(parse_object_spec('CLAS:/NMSPC/CL_FOO'), [('R3TR', 'CLAS', '/NMSPC/CL_FOO')])

    def test_pgmid_and_type_are_upper_cased(self):
        self.assertEqual(parse_object_spec('limu:reps:ZREPORT'), [('LIMU', 'REPS', 'ZREPORT')])

    def test_names_are_upper_cased(self):
        self.assertEqual(parse_object_spec('clas:zcl_a,/nmspc/cl_b'),
                         [('R3TR', 'CLAS', 'ZCL_A'),
                          ('R3TR', 'CLAS', '/NMSPC/CL_B')])

    def test_name_only(self):
        self.assert_invalid_spec('ZCL_FOO')

    def test_too_many_parts(self):
        self.assert_invalid_spec('R3TR:CLAS:ZCL_FOO:BAR')

    def test_empty_pgmid(self):
        self.assert_invalid_spec(':CLAS:ZCL_FOO')

    def test_empty_type(self):
        self.assert_invalid_spec(':ZCL_FOO')

    def test_empty_name(self):
        self.assert_invalid_spec('CLAS:')

    def test_empty_name_in_list(self):
        self.assert_invalid_spec('CLAS:ZCL_A,,ZCL_B')

    def test_trailing_comma(self):
        self.assert_invalid_spec('CLAS:ZCL_A,')

    def assert_line_break_in_name(self, spec):
        with self.assertRaises(SAPCliError) as caught:
            parse_object_spec(spec)

        self.assertEqual(str(caught.exception),
                         f'Invalid object "{spec}": names must not contain line breaks')

    def test_name_with_line_feed(self):
        self.assert_line_break_in_name('CLAS:ZCL_A\nZCL_B')

    def test_name_with_carriage_return(self):
        self.assert_line_break_in_name('CLAS:ZCL_A\rZCL_B')

    def test_name_with_line_break_in_list(self):
        self.assert_line_break_in_name('CLAS:ZCL_A,ZCL_B\r\nZCL_C')

    def test_trailing_line_break_is_removed(self):
        self.assertEqual(parse_object_spec('CLAS:ZCL_A\n'), [('R3TR', 'CLAS', 'ZCL_A')])


class TestParseObjectList(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(parse_object_list([], 'objects.txt'), [])

    def test_tab_separated(self):
        self.assertEqual(parse_object_list(['R3TR\tCLAS\tZCL_FOO\n'], 'objects.txt'),
                         [('R3TR', 'CLAS', 'ZCL_FOO')])

    def test_space_separated(self):
        self.assertEqual(parse_object_list(['  R3TR   PROG ZREPORT  \n'], 'objects.txt'),
                         [('R3TR', 'PROG', 'ZREPORT')])

    def test_windows_line_endings(self):
        self.assertEqual(parse_object_list(['R3TR CLAS ZCL_FOO\r\n'], 'objects.txt'),
                         [('R3TR', 'CLAS', 'ZCL_FOO')])

    def test_name_with_spaces(self):
        self.assertEqual(parse_object_list(['R3TR\tAPIS\tSTRING_TABLE                        TTYP\n',
                                            'LIMU METH ZCL_FOO                       BAR\n'], 'objects.txt'),
                         [('R3TR', 'APIS', 'STRING_TABLE                        TTYP'),
                          ('LIMU', 'METH', 'ZCL_FOO                       BAR')])

    def test_pgmid_and_type_are_upper_cased(self):
        self.assertEqual(parse_object_list(['limu wapp ZBSP_APP                      index.htm\n'], 'objects.txt'),
                         [('LIMU', 'WAPP', 'ZBSP_APP                      index.htm')])

    def test_comments_and_blank_lines(self):
        self.assertEqual(parse_object_list(['# objects to commit\n',
                                            '\n',
                                            'R3TR CLAS ZCL_FOO\n',
                                            '   \n',
                                            '  # R3TR CLAS ZCL_SKIPPED\n',
                                            'R3TR PROG ZREPORT'], 'objects.txt'),
                         [('R3TR', 'CLAS', 'ZCL_FOO'),
                          ('R3TR', 'PROG', 'ZREPORT')])

    def test_missing_name(self):
        with self.assertRaises(SAPCliError) as caught:
            parse_object_list(['R3TR CLAS ZCL_FOO\n',
                               '# comment\n',
                               'R3TR CLAS\n'], 'objects.txt')

        self.assertEqual(str(caught.exception),
                         'objects.txt:3: Invalid object "R3TR CLAS": expected PGMID TYPE NAME')

    def test_compact_notation_is_not_accepted(self):
        with self.assertRaises(SAPCliError) as caught:
            parse_object_list(['CLAS:ZCL_FOO\n'], '<stdin>')

        self.assertEqual(str(caught.exception),
                         '<stdin>:1: Invalid object "CLAS:ZCL_FOO": expected PGMID TYPE NAME')
