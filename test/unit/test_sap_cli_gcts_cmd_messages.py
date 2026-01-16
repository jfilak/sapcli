#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock

import sap.cli.gcts
import sap.cli.core
from sap.rest.gcts.log_messages import ActionMessage

from infra import generate_parse_args

from test.unit.mock import (
    ConsoleOutputTestCase,
    PatcherTestCase,
)

from test.unit.fixtures_sap_rest_gcts_log_messages import (
    GCTS_LOG_MESSAGES_DATA,
    GCTS_LOG_MESSAGES_JSON_EXP,
    GCTS_LOG_MESSAGES_PROCESS_CCC_DATA,
    GCTS_LOG_MESSAGES_PROCESS_CCC_JSON_EXP,
)


parse_args = generate_parse_args(sap.cli.gcts.CommandGroup())


class TestgCTSRepoMessages(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None
        self.patch_console(console=self.console)

        self.fake_connection = Mock()
        self.messages_data = GCTS_LOG_MESSAGES_DATA
        # ActionMessage renames 'process' to 'processId', so copy dicts to avoid modifying original
        self.action_data = [ActionMessage(dict(msg)) for msg in self.messages_data]

        # Expected JSON has 'processId' at the end (ActionMessage deletes 'process' and adds 'processId')
        expected_json_data = GCTS_LOG_MESSAGES_JSON_EXP
        self.expected_json_messages = sap.cli.core.json_dumps(expected_json_data)

        # Note: trailing spaces match column padding from TableWriter
        self.expected_human_messages = 'Date                | Caller    | Operation      | Status  | Process\n' \
            '--------------------------------------------------------------------\n' \
            '2026-01-12 13:47:32 | DEVELOPER | SWITCH_BRANCH  | ERROR   | CCC    \n' \
            '2025-12-17 13:30:49 | DEVELOPER | PULL_BY_COMMIT | WARNING | BBB    \n' \
            '2026-01-12 10:40:31 | DEVELOPER | CLONE          | INFO    | AAA    '

        self.process_data = GCTS_LOG_MESSAGES_PROCESS_CCC_DATA

        # ActionMessage with process messages (for --process queries)
        self.process_action_data = [ActionMessage(None, raw_process_messages=self.process_data)]

        # The expected JSON process output is the list of json_object values from ProcessMessage
        expected_json_process_data = GCTS_LOG_MESSAGES_PROCESS_CCC_JSON_EXP
        self.expected_json_process = sap.cli.core.json_dumps(expected_json_process_data)

        # Note: trailing spaces match column padding from TableWriter
        self.expected_human_process = 'Date                | Action         | Application     | Severity\n' \
            '-----------------------------------------------------------------\n' \
            '2026-01-12 13:47:33 | COMPARE_BRANCH | Client          | ERROR   \n' \
            '    INFO: Non Empty line 1\n' \
            '    INFO: Non Empty line 2\n' \
            '2026-01-12 13:47:33 | COMPARE_BRANCH | Transport Tools | ERROR   \n' \
            "    This is tp version 381.724.83 (release 919) (Patch level:0)\n" \
            '    standard output from tp and from tools called by tp:\n' \
            '    ABAP to VCS (c) - SAP SE 2025 - Version 1.29.0-20251105155931_5a33982436600ed77b8f1c860670bfcb2cd503be from 2025-11-05 16:06:04\n' \
            "    Error: 'The specified directory '/usr/sap/A4H/D00/gcts/the_repo/data/' is not a working directory of a version control\n" \
            "     system'\n" \
            '    tp returncode summary:\n' \
            '    TOOLS: Highest return code of single steps was: 12\n' \
            '    ERRORS: Highest tp internal error was: 0236\n' \
            '    tp call duration was: 0.352889 sec\n' \
            '2026-01-12 13:47:32 | LOG_LEVEL      | gCTS            | INFO    \n' \
            '    Log level is INFO'

        self.fake_repo = Mock()

    def messages_cmd(self, *args, **kwargs):
        return parse_args('repo', 'messages', *args, **kwargs)

    def assert_query_params(self, expected_process):
        query_params = self.fake_repo.messages.call_args.args[0]
        expected_path = 'log' if expected_process is None else f'log/{expected_process}'
        self.assertEqual(query_params.get_path('log'), expected_path)
        self.assertEqual(query_params.get_params(), {})

    @patch('sap.cli.gcts.get_repository')
    def test_messages_json(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.action_data
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo', '--format', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.messages.assert_called_once()
        self.assert_query_params(None)

        self.assertConsoleContents(self.console, stdout=self.expected_json_messages+'\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_human(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.action_data
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo', '--format', 'HUMAN')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.messages.assert_called_once()
        self.assert_query_params(None)

        self.assertConsoleContents(self.console, stdout=self.expected_human_messages+'\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_with_process_json(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.process_action_data
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo', '--process', 'CCC', '--format', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.messages.assert_called_once()
        self.assert_query_params('CCC')

        self.maxDiff = None
        self.assertConsoleContents(self.console, stdout=self.expected_json_process+'\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_with_process_human(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.process_action_data
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo', '--process', 'CCC', '--format', 'HUMAN')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.messages.assert_called_once()
        self.assert_query_params('CCC')

        self.maxDiff = None
        self.assertConsoleContents(self.console, stdout=self.expected_human_process+'\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_repo_not_found(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.messages_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot get repository.\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_request_error(self, fake_get_repository):
        self.fake_repo.messages.side_effect = sap.cli.gcts.GCTSRequestError({'exception': 'Request failed.'})
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='''Exception:
  Request failed.
''')
