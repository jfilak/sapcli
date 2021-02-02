'''Abapgit CLI tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
from unittest.mock import Mock, patch, call

import sap.cli.abapgit


def get_sample_link_args():
    args = Mock()
    args.package = 'PKG'
    args.url = 'URL'
    args.branch = 'branch'
    args.remote_user = 'user'
    args.remote_password = 'password'
    args.transport_request = 'request'
    return args


def get_sample_pull_args():
    args = Mock()
    args.package = 'PKG'
    args.branch = 'branch'
    args.remote_user = 'user'
    args.remote_password = 'password'
    args.transport_request = 'request'
    return args


class TestAbapgitCommands(unittest.TestCase):
    '''Test Abapgit cli commands'''

    @patch('sap.cli.core.get_console', return_value=Mock())
    @patch('sap.adt.abapgit.Repository.link', return_value=Mock())
    def test_link_repo_ok(self, link_patch, console_patch):
        link_patch.return_value.status_code = 200
        console_patch.return_value.printout = Mock()

        sap.cli.abapgit.link('CONNECTION', get_sample_link_args())

        link_patch.assert_called_once_with(
            'CONNECTION',
            {
                'package': 'PKG',
                'url': 'URL',
                'branchName': 'branch',
                'remoteUser': 'user',
                'remotePassword': 'password',
                'transportRequest': 'request'
            })

        console_patch.return_value.printout.assert_called_once_with('Repository was linked.')

    @patch('sap.cli.core.get_console', return_value=Mock())
    @patch('sap.adt.abapgit.Repository.link', return_value=Mock())
    def test_link_repo_error(self, link_patch, console_patch):
        link_patch.return_value.status_code = 500
        console_patch.return_value.printerr = Mock()

        sap.cli.abapgit.link('CONNECTION', get_sample_link_args())

        link_patch.assert_called_once()
        console_patch.return_value.printerr.assert_called_once_with(
            'Failed to link repository: PKG', link_patch.return_value)

    @patch('time.sleep')
    @patch('sap.cli.helpers.ConsoleHeartBeat')
    @patch('sap.cli.core.get_console', return_value=Mock())
    @patch('sap.adt.abapgit.Repository', return_value=Mock())
    def test_pull_repo_ok(self, repo_patch, console_patch, hartbeat_patch, sleep_patch):
        repo = repo_patch.return_value
        repo.fetch = Mock()
        repo.pull = Mock()
        repo.get_status = Mock(side_effect=['R', 'S', 'S', 'S'])
        repo.get_status_text = Mock(return_value='STATUS_TEXT')

        console_patch.return_value.printout = Mock()

        sap.cli.abapgit.pull('CONNECTION', get_sample_pull_args())

        repo_patch.assert_called_once_with('CONNECTION', 'PKG')
        repo.pull.assert_called_once_with({
            'branchName': 'branch',
            'remoteUser': 'user',
            'remotePassword': 'password',
            'transportRequest': 'request'
        })

        sleep_patch.assert_called_once_with(1)
        hartbeat_patch.assert_called_once_with(console_patch.return_value, 1)
        console_patch.return_value.printout.assert_called_once_with('STATUS_TEXT')

    @patch('sap.cli.helpers.ConsoleHeartBeat')
    @patch('sap.cli.core.get_console', return_value=Mock())
    @patch('sap.adt.abapgit.Repository', return_value=Mock())
    def test_pull_repo_error(self, repo_patch, console_patch, hartbeat_patch):
        repo = repo_patch.return_value
        repo.fetch = Mock()
        repo.pull = Mock()
        repo.get_status = Mock(return_value='E')
        repo.get_status_text = Mock(return_value='STATUS_TEXT')
        repo.get_error_log = Mock(return_value='ERROR_LOG')

        console_patch.return_value.printerr = Mock()

        sap.cli.abapgit.pull('CONNECTION', get_sample_pull_args())

        repo.pull.assert_called_once()
        hartbeat_patch.assert_called_once_with(console_patch.return_value, 1)
        console_patch.return_value.printerr.assert_has_calls([call('STATUS_TEXT'), call('ERROR_LOG')])
