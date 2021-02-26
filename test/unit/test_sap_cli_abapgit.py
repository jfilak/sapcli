'''Abapgit CLI tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
from unittest.mock import Mock, patch, call

from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase,
)

import sap.cli.abapgit

from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.abapgit.CommandGroup())


class TestAbapgitLink(PatcherTestCase, ConsoleOutputTestCase):
    '''Test Abapgit Link command'''

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.link_patch = self.patch('sap.adt.abapgit.Repository.link')
        self.link_patch.return_value = Mock()

        self.param_branch = 'branch'
        self.param_remote_user = 'user'
        self.param_remote_password = 'password'
        self.param_corrnr = 'request'
        self.param_package = 'PKG'
        self.param_url = 'URL'

    def execute_link_all_params(self):
        args = parse_args(
            'link',
            '--remote-user', self.param_remote_user,
            '--remote-password', self.param_remote_password,
            '--corrnr', self.param_corrnr,
            '--branch', self.param_branch,
            self.param_package,
            self.param_url)
        return args.execute(self.connection, args)

    def build_abapgit_params(self, package=None):
        return {
            'package': self.param_package if package is None else package,
            'url': self.param_url,
            'branchName': self.param_branch,
            'remoteUser': self.param_remote_user,
            'remotePassword': self.param_remote_password,
            'transportRequest': self.param_corrnr
        }

    def test_link_repo_ok(self):
        self.link_patch.return_value.status_code = 200

        self.execute_link_all_params()

        self.link_patch.assert_called_once_with(self.connection, self.build_abapgit_params())

        self.assertConsoleContents(console=self.console, stdout='''Repository was linked.
''')

    def test_link_repo_ok_uppercase(self):
        self.link_patch.return_value.status_code = 200

        self.param_package = 'lower_case'
        self.execute_link_all_params()

        self.link_patch.assert_called_once_with(self.connection,
                                                self.build_abapgit_params(package='LOWER_CASE'))

    def test_link_repo_error(self):
        self.link_patch.return_value.status_code = 500

        self.execute_link_all_params()

        self.link_patch.assert_called_once()

        self.assertConsoleContents(console=self.console, stderr=f'''Failed to link repository: PKG {self.link_patch.return_value}
''')


class TestAbapgitPull(PatcherTestCase, ConsoleOutputTestCase):
    '''Test Abapgit Pull command'''

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.heartbeat_patch = self.patch('sap.cli.helpers.ConsoleHeartBeat')
        self.repo_patch = self.patch('sap.adt.abapgit.Repository')

        self.repo_inst = self.repo_patch.return_value
        self.repo_inst.fetch = Mock()
        self.repo_inst.pull = Mock()
        self.repo_inst.get_status_text = Mock(return_value='STATUS_TEXT')

        self.param_branch = 'branch'
        self.param_remote_user = 'user'
        self.param_remote_password = 'password'
        self.param_corrnr = 'request'
        self.param_package = 'PKG'

    def build_abapgit_params(self):
        return {
            'branchName': self.param_branch,
            'remoteUser': self.param_remote_user,
            'remotePassword': self.param_remote_password,
            'transportRequest': self.param_corrnr
        }

    def execute_pull_all_params(self):
        args = parse_args('pull',
            '--remote-user', self.param_remote_user,
            '--remote-password', self.param_remote_password,
            '--corrnr', self.param_corrnr,
            '--branch', self.param_branch,
            self.param_package)

        return args.execute(self.connection, args)


    @patch('time.sleep')
    def test_pull_repo_ok(self, sleep_patch):
        self.repo_inst.get_status = Mock(side_effect=['R', 'S', 'S', 'S'])

        self.execute_pull_all_params()

        self.repo_patch.assert_called_once_with(self.connection, 'PKG')
        self.repo_inst.pull.assert_called_once_with(self.build_abapgit_params())

        sleep_patch.assert_called_once_with(1)

        self.heartbeat_patch.assert_called_once_with(self.console, 1)
        self.assertConsoleContents(console=self.console, stdout='''STATUS_TEXT
''')

    @patch('time.sleep')
    def test_pull_repo_ok_uppercase(self, sleep_patch):
        self.param_package = 'lower_case'
        self.execute_pull_all_params()
        self.repo_patch.assert_called_once_with(self.connection, 'LOWER_CASE')

    def test_pull_repo_error(self):
        self.repo_inst.get_status = Mock(return_value='E')
        self.repo_inst.get_error_log = Mock(return_value='ERROR_LOG')

        self.execute_pull_all_params()

        self.repo_inst.pull.assert_called_once()

        self.heartbeat_patch.assert_called_once_with(self.console, 1)
        self.assertConsoleContents(console=self.console, stderr='''STATUS_TEXT
ERROR_LOG
''')
