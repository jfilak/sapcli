#!/usr/bin/env python3

import unittest
from unittest.mock import patch, Mock

import sap.cli.gcts
import sap.cli.core

from infra import generate_parse_args

from test.unit.mock import (
    ConsoleOutputTestCase,
    PatcherTestCase,
)


parse_args = generate_parse_args(sap.cli.gcts.CommandGroup())

class TestgCTSRepoMessages(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None
        self.patch_console(console=self.console)

        self.fake_connection = Mock()
        self.messages_data = [
            {'rid': 'the_repo', 'process': 'CCC', 'processName': 'SWITCH_BRANCH', 'caller': 'DEVELOPER', 'time': 20260112134732, 'status': 'ERROR'},
            {'rid': 'the_repo', 'process': 'BBB', 'processName': 'PULL_BY_COMMIT', 'caller': 'DEVELOPER', 'time': 20251217133049, 'status': 'WARNING'},
            {'rid': 'the_repo', 'process': 'AAA', 'processName': 'CLONE', 'caller': 'DEVELOPER', 'time': 20260112104031, 'status': 'INFO'},
        ]

        self.expected_json_messages = sap.cli.core.json_dumps(self.messages_data)
        # Note: trailing spaces match column padding from TableWriter
        self.expected_human_messages = 'Date                | Caller    | Operation      | Status  | Process\n' \
            '--------------------------------------------------------------------\n' \
            '2026-01-12 13:47:32 | DEVELOPER | SWITCH_BRANCH  | ERROR   | CCC    \n' \
            '2025-12-17 13:30:49 | DEVELOPER | PULL_BY_COMMIT | WARNING | BBB    \n' \
            '2026-01-12 10:40:31 | DEVELOPER | CLONE          | INFO    | AAA    '

        self.process_data = [
            {'rid': 'the_repo', 'process': 'CCC', 'action': 'COMPARE_BRANCH', 'application': 'Client', 'applId': '20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08',
             'applInfo': '[{"type":"Parameters","protocol":["{\\"repodir\\":\\"/usr/sap/A4H/D00/gcts/the_repo/data/\\",\\"logfile\\":\\"/usr/sap/A4H/D00/gcts/the_repo/log/20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08.log\\",\\"loglevel\\":\\"INFORMATION\\",\\"remoteplatform\\":\\"GITHUB\\",\\"apploglevel\\":\\"INFORMATION\\",\\"command\\":\\"getdifferences\\",\\"tobranch\\":\\"foo\\"}"]},{"type":"Client Log","protocol":["client log line"]},'
                 + '{"type":"Client Response","protocol":["'
                 +    '{\\"log\\":['
                 +        '{\\"code\\":\\"GCTS.CLIENT.500\\",\\"type\\":\\"INFO\\",\\"message\\":\\"Non Empty line 1\\",\\"step\\":\\"LOG.COMMIT.DATA\\"},'
                 +        '{\\"code\\":\\"GCTS.CLIENT.500\\",\\"type\\":\\"INFO\\",\\"message\\":\\"\\",\\"step\\":\\"LOG.COMMIT.DATA\\"},'
                 +        '{\\"code\\":\\"GCTS.CLIENT.500\\",\\"type\\":\\"INFO\\",\\"message\\":\\"Non Empty line 2\\",\\"step\\":\\"LOG.COMMIT.DATA\\"}'
                 +   ']}'
                 + '"]},'
                 + '{"type":"Client Stack Log","protocol":["[]"]}]',
             'time': 20260112134733,
             'severity': 'ERROR'},

            {'rid': 'the_repo', 'process': 'CCC', 'action': 'COMPARE_BRANCH', 'application': 'Transport Tools',
             'applInfo': '{"returnCode":"0236","cmdLine":"SAPVCSCALL 6IT client100 pf=/usr/sap/trans/bin/TP_DOMAIN_A4H.PFL -DSYSTEM_PF=/usr/sap/A4H/SYS/profile/A4H_D00_saphost -DSAPINSTANCENAME=A4H_ddci SAPVCSPARAMS=-requestid 20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08 SAPVCSPARAMS=-responsedir /usr/sap/C5","stdout":[{"line":"This is tp version 381.724.83 (release 919) (Patch level:0)"},{},{"line":"standard output from tp and from tools called by tp:"},{},{},{"line":"ABAP to VCS (c) - SAP SE 2025 - Version 1.29.0-20251105155931_5a33982436600ed77b8f1c860670bfcb2cd503be from 2025-11-05 16:06:04"},{},{"line":"Error: \'The specified directory \'/usr/sap/A4H/D00/gcts/the_repo/data/\' is not a working directory of a version control"},{"line":" system\'"},{},{"line":"tp returncode summary:"},{},{"line":"TOOLS: Highest return code of single steps was: 12"},{"line":"ERRORS: Highest tp internal error was: 0236"},{"line":"tp call duration was: 0.352889 sec"}],"system":"6IT","alog":"ALOG2603.6IT","slog":"SLOG2603.6IT"}',
             'time': 20260112134733,
             'severity': 'ERROR'},

            {'rid': 'the_repo', 'process': 'CCC', 'action': 'LOG_LEVEL', 'application': 'gCTS',
             'applInfo': 'Log level is INFO',
             'time': 20260112134732,
             'severity': 'INFO'}
        ]

        # The expected JSON process output is the list of json_object values from ProcessMessage.appl_info
        # Each application type processes the raw applInfo differently:
        # - Client: parses the JSON list and decodes protocol strings
        # - Transport Tools: parses JSON and replaces stdout items with their line values
        # - gCTS: returns the raw string as-is
        expected_json_process_data = [
            # Client application info (processed)
            [
                {
                    "type": "Parameters",
                    "protocol": {
                        "repodir": "/usr/sap/A4H/D00/gcts/the_repo/data/",
                        "logfile": "/usr/sap/A4H/D00/gcts/the_repo/log/20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08.log",
                        "loglevel": "INFORMATION",
                        "remoteplatform": "GITHUB",
                        "apploglevel": "INFORMATION",
                        "command": "getdifferences",
                        "tobranch": "foo"
                    }
                },
                {
                    "type": "Client Log",
                    "protocol": ["client log line"]
                },
                {
                    "type": "Client Response",
                    "protocol": {
                        "log": [
                            {"code": "GCTS.CLIENT.500", "type": "INFO", "message": "Non Empty line 1", "step": "LOG.COMMIT.DATA"},
                            {"code": "GCTS.CLIENT.500", "type": "INFO", "message": "", "step": "LOG.COMMIT.DATA"},
                            {"code": "GCTS.CLIENT.500", "type": "INFO", "message": "Non Empty line 2", "step": "LOG.COMMIT.DATA"}
                        ]
                    }
                },
                {
                    "type": "Client Stack Log",
                    "protocol": []
                }
            ],
            # Transport Tools application info (processed - stdout items replaced with line values)
            {
                "returnCode": "0236",
                "cmdLine": "SAPVCSCALL 6IT client100 pf=/usr/sap/trans/bin/TP_DOMAIN_A4H.PFL -DSYSTEM_PF=/usr/sap/A4H/SYS/profile/A4H_D00_saphost -DSAPINSTANCENAME=A4H_ddci SAPVCSPARAMS=-requestid 20260112_134732_B0A57FE31D1553BC5AA6E78808D3FE08 SAPVCSPARAMS=-responsedir /usr/sap/C5",
                "stdout": [
                    "This is tp version 381.724.83 (release 919) (Patch level:0)",
                    "",
                    "standard output from tp and from tools called by tp:",
                    "",
                    "",
                    "ABAP to VCS (c) - SAP SE 2025 - Version 1.29.0-20251105155931_5a33982436600ed77b8f1c860670bfcb2cd503be from 2025-11-05 16:06:04",
                    "",
                    "Error: 'The specified directory '/usr/sap/A4H/D00/gcts/the_repo/data/' is not a working directory of a version control",
                    " system'",
                    "",
                    "tp returncode summary:",
                    "",
                    "TOOLS: Highest return code of single steps was: 12",
                    "ERRORS: Highest tp internal error was: 0236",
                    "tp call duration was: 0.352889 sec"
                ],
                "system": "6IT",
                "alog": "ALOG2603.6IT",
                "slog": "SLOG2603.6IT"
            },
            # gCTS application info (raw string)
            "Log level is INFO"
        ]
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
    def test_messages_no_params(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.messages_data
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.messages.assert_called_once()
        self.assert_query_params(None)

        self.assertConsoleContents(self.console, stdout=self.expected_json_messages+'\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_human(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.messages_data
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo', '--format', 'HUMAN')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.messages.assert_called_once()
        self.assert_query_params(None)

        self.assertConsoleContents(self.console, stdout=self.expected_human_messages+'\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_with_process(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.process_data
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.messages_cmd('the_repo', '--process', 'CCC')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.messages.assert_called_once()
        self.assert_query_params('CCC')

        self.maxDiff = None
        self.assertConsoleContents(self.console, stdout=self.expected_json_process+'\n')

    @patch('sap.cli.gcts.get_repository')
    def test_messages_with_process_human(self, fake_get_repository):
        self.fake_repo.messages.return_value = self.process_data
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
