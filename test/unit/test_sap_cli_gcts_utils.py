"""Test sap.cli.gcts_utils module"""

import unittest
from unittest.mock import patch, Mock
from test.unit.mock import (
    ConsoleOutputTestCase
)
from sap.cli.gcts_utils import (
    print_gcts_task_info,
    is_checkout_activity_success,
    is_cloned_activity_success,
    get_activity_rc,
    print_gcts_message,
    dump_gcts_messages,
    gcts_exception_handler,
)
from sap.rest.errors import HTTPRequestError
from sap.rest.gcts.errors import SAPCliError, GCTSRequestError


class TestPrintGCTSTaskInfo(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_console = Mock()
        self.mock_console.printerr = Mock()
        self.mock_console.printout = Mock()

        self.task_dict = {
            'tid': '123',
            'rid': 'sample',
            'type': 'CLONE_REPOSITORY',
            'status': 'RUNNING'
        }

    @patch('sap.cli.core.get_console')
    def test_print_gcts_task_info_with_task(self, mock_get_console):
        """Test print_gcts_task_info when task is provided (no error)"""
        mock_get_console.return_value = self.mock_console

        print_gcts_task_info(None, self.task_dict)

        mock_get_console.assert_called_once()

        self.mock_console.printerr.assert_not_called()
        self.mock_console.printout.assert_called_once_with(f'\nTask Status: {self.task_dict["status"]}')

    @patch('sap.cli.core.get_console')
    def test_print_gcts_task_info_with_error(self, mock_get_console):
        """Test print_gcts_task_info when error message is provided"""
        mock_get_console.return_value = self.mock_console
        error_message = 'Task retrieval failed: Connection error'

        print_gcts_task_info(error_message, None)

        mock_get_console.assert_called_once()

        self.mock_console.printerr.assert_called_once_with(error_message)

        self.mock_console.printout.assert_not_called()


class TestIsCheckoutActivitySuccess(ConsoleOutputTestCase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_repo = Mock()

    @patch('sap.cli.gcts_utils.get_activity_rc')
    def test_is_checkout_activity_success_successful(self, mock_get_activity_rc):
        """Test is_checkout_activity_success when checkout is successful (return code 4)"""
        mock_get_activity_rc.return_value = 4

        result = is_checkout_activity_success(self.console, self.mock_repo)

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.BRANCH_SW
        )

        self.assertTrue(result)

        self.assertConsoleContents(console=self.console, stderr='')

    @patch('sap.cli.gcts_utils.get_activity_rc')
    def test_is_checkout_activity_success_unsuccessful(self, mock_get_activity_rc):
        """Test is_checkout_activity_success when checkout fails (return code > 4)"""
        code = 5
        mock_get_activity_rc.return_value = code

        result = is_checkout_activity_success(self.console, self.mock_repo)

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.BRANCH_SW
        )

        self.assertFalse(result)

        self.assertConsoleContents(console=self.console, stderr=f'Checkout process failed with return code: {code}!\n')


class TestIsClonedActivitySuccess(ConsoleOutputTestCase, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_repo = Mock()

    @patch('sap.cli.gcts_utils.get_activity_rc')
    def test_is_cloned_activity_success_successful(self, mock_get_activity_rc):
        mock_get_activity_rc.return_value = 4

        result = is_cloned_activity_success(self.console, self.mock_repo)

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.CLONE
        )

        self.assertTrue(result)

        self.assertConsoleContents(console=self.console, stderr='')

    @patch('sap.cli.gcts_utils.get_activity_rc')
    def test_is_cloned_activity_success_unsuccessful(self, mock_get_activity_rc):
        code = 5
        mock_get_activity_rc.return_value = code

        result = is_cloned_activity_success(self.console, self.mock_repo)

        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams
        mock_get_activity_rc.assert_called_once_with(
            self.mock_repo,
            RepoActivitiesQueryParams.Operation.CLONE
        )

        self.assertFalse(result)

        self.assertConsoleContents(console=self.console, stderr=f'Clone process failed with return code: {code}!\n')


class TestGetActivityRc(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mock_repo = Mock()
        self.mock_repo.rid = 'test_repo'

    def test_get_activity_rc_successful(self):
        """Test get_activity_rc when activities returns a valid result with return code"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = [{'rc': '0'}]

        operation = RepoActivitiesQueryParams.Operation.CLONE
        result = get_activity_rc(self.mock_repo, operation)

        self.assertEqual(result, 0)

        self.mock_repo.activities.assert_called_once()
        call_args = self.mock_repo.activities.call_args[0][0]
        self.assertEqual(call_args.get_params()['type'], operation.value)

    def test_get_activity_rc_http_error(self):
        """Test get_activity_rc when repo.activities raises HTTPRequestError"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        fake_response = Mock()
        fake_response.text = 'Connection failed'
        fake_response.status_code = 500

        http_error = HTTPRequestError(None, fake_response)
        self.mock_repo.activities.side_effect = http_error

        operation = RepoActivitiesQueryParams.Operation.CLONE

        with self.assertRaises(SAPCliError) as context:
            get_activity_rc(self.mock_repo, operation)

        error_message = str(context.exception)
        self.assertIn('Unable to obtain activities of repository: "test_repo"', error_message)
        self.assertIn('Connection failed', error_message)

        self.mock_repo.activities.assert_called_once()

    def test_get_activity_rc_empty_activities(self):
        """Test get_activity_rc when activities returns empty list"""
        from sap.rest.gcts.remote_repo import RepoActivitiesQueryParams

        self.mock_repo.activities.return_value = []

        operation = RepoActivitiesQueryParams.Operation.CLONE

        with self.assertRaises(SAPCliError) as context:
            get_activity_rc(self.mock_repo, operation)

        error_message = str(context.exception)
        self.assertIn(f'Expected {operation.value} activity not found! Repository: "test_repo"', error_message)

        self.mock_repo.activities.assert_called_once()


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
        def test_func():
            return 0

        result = test_func()
        self.assertEqual(result, 0)
        mock_get_console.assert_not_called()

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_gcts_request_error(self, mock_get_console, mock_dump_gcts_messages):
        mock_get_console.return_value = self.mock_console
        mock_messages = {'errorLog': [{'message': 'GCTS error'}]}
        gcts_error = GCTSRequestError(mock_messages)

        @gcts_exception_handler
        def test_func():
            raise gcts_error

        result = test_func()
        self.assertEqual(result, 1)
        mock_get_console.assert_called_once()
        mock_dump_gcts_messages.assert_called_once_with(self.mock_console, mock_messages)

    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_sap_cli_error(self, mock_get_console):
        mock_get_console.return_value = self.mock_console
        sap_error = SAPCliError('SAP CLI error message')

        @gcts_exception_handler
        def test_func():
            raise sap_error

        result = test_func()
        self.assertEqual(result, 1)
        mock_get_console.assert_called_once()
        self.mock_console.printerr.assert_called_once_with('SAP CLI error message')

    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_other_exception(self, mock_get_console):
        mock_get_console.return_value = self.mock_console

        @gcts_exception_handler
        def test_func():
            raise ValueError('Other error')

        with self.assertRaises(ValueError):
            test_func()
        mock_get_console.assert_not_called()

    @patch('sap.cli.core.get_console')
    def test_gcts_exception_handler_with_args_kwargs(self, mock_get_console):
        mock_get_console.return_value = self.mock_console

        @gcts_exception_handler
        def test_func(arg1, arg2, kwarg1=None):
            return arg1 + arg2 + (kwarg1 or 0)

        result = test_func(1, 2, kwarg1=3)
        self.assertEqual(result, 6)
        mock_get_console.assert_not_called()
