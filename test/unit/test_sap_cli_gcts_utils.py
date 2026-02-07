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
)
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.errors import SAPCliError, GCTSRequestError


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

