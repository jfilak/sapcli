'''Abapgit CLI tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import os
import unittest
from unittest.mock import Mock, patch, call

from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase,
)

import sap.cli.abapgit
from sap.errors import SAPCliError
from sap.rfc.bapi import BAPIReturn

from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.abapgit.CommandGroup())


class TestAbapgitLink(ConsoleOutputTestCase, PatcherTestCase):
    '''Test Abapgit Link command'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.patch('os.environ', new={})
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

    def test_link_repo_default_branch(self):
        self.link_patch.return_value.status_code = 200

        args = parse_args('link', self.param_package, self.param_url)
        args.execute(self.connection, args)

        self.assertEqual(self.link_patch.call_args.args[1]['branchName'], 'refs/heads/master')

    def test_link_repo_explicit_steampunk(self):
        self.link_patch.return_value.status_code = 200

        args = parse_args('link', '--api', 'steampunk', self.param_package, self.param_url)
        args.execute(self.connection, args)

        self.link_patch.assert_called_once()

    def test_link_repo_steampunk_from_env(self):
        self.link_patch.return_value.status_code = 200

        os.environ['SAPCLI_ABAPGIT_API'] = 'steampunk'
        args = parse_args('link', self.param_package, self.param_url)
        args.execute(self.connection, args)

        self.link_patch.assert_called_once()

    def test_link_repo_unknown_api_from_env(self):
        os.environ['SAPCLI_ABAPGIT_API'] = 'foo'
        args = parse_args('link', self.param_package, self.param_url)

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'Unknown abapGit API "foo" (SAPCLI_ABAPGIT_API) - use one of: steampunk, rfc-via-classrun')
        self.link_patch.assert_not_called()

    def test_link_repo_steampunk_rejects_folder_logic(self):
        args = parse_args('link', '--folder-logic', 'FULL', self.param_package, self.param_url)

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'The parameter --folder-logic is supported only by the API rfc-via-classrun')
        self.link_patch.assert_not_called()

    def test_link_repo_steampunk_rejects_starting_folder(self):
        args = parse_args('link', '--starting-folder', '/abap/', self.param_package, self.param_url)

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'The parameter --starting-folder is supported only by the API rfc-via-classrun')

    def test_link_repo_steampunk_rejects_ignore_subpackages(self):
        args = parse_args('link', '--ignore-subpackages', self.param_package, self.param_url)

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'The parameter --ignore-subpackages is supported only by the API rfc-via-classrun')

    def test_link_repo_steampunk_rejects_main_lang_only(self):
        args = parse_args('link', '--main-lang-only', self.param_package, self.param_url)

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'The parameter --main-lang-only is supported only by the API rfc-via-classrun')


class TestAbapgitLinkRfcViaClassrun(ConsoleOutputTestCase, PatcherTestCase):
    '''Test Abapgit Link command with the API rfc-via-classrun'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.patch('os.environ', new={})
        self.steampunk_patch = self.patch('sap.adt.abapgit.Repository.link')
        self.link_patch = self.patch('sap.platform.abap.abapgit_rfc.link')
        self.link_patch.return_value = BAPIReturn([
            {'TYPE': 'I', 'ID': '', 'NUMBER': '', 'MESSAGE': 'Running migrations'},
            {'TYPE': 'I', 'ID': '', 'NUMBER': '', 'MESSAGE': 'Done'},
        ])

    def test_link_all_params(self):
        args = parse_args(
            'link',
            '--api', 'rfc-via-classrun',
            '--remote-user', 'user',
            '--remote-password', 'password',
            '--branch', 'refs/heads/main',
            '--folder-logic', 'FULL',
            '--starting-folder', '/abap/',
            '--ignore-subpackages',
            '--main-lang-only',
            'pkg',
            'URL')
        args.execute(self.connection, args)

        self.link_patch.assert_called_once_with(
            self.connection,
            package='PKG',
            url='URL',
            user='user',
            password='password',
            branch='refs/heads/main',
            folder_logic='FULL',
            starting_folder='/abap/',
            ignore_subpackages=True,
            main_lang_only=True)
        self.steampunk_patch.assert_not_called()

        self.assertConsoleContents(console=self.console, stdout='''Info: Running migrations
Info: Done
''')

    def test_link_defaults(self):
        args = parse_args('link', '--api', 'rfc-via-classrun', 'PKG', 'URL')
        args.execute(self.connection, args)

        self.link_patch.assert_called_once_with(
            self.connection,
            package='PKG',
            url='URL',
            user='',
            password='',
            branch='',
            folder_logic='PREFIX',
            starting_folder='/src/',
            ignore_subpackages=False,
            main_lang_only=False)

    def test_link_api_from_env(self):
        os.environ['SAPCLI_ABAPGIT_API'] = 'rfc-via-classrun'
        args = parse_args('link', 'PKG', 'URL')
        args.execute(self.connection, args)

        self.link_patch.assert_called_once()
        self.steampunk_patch.assert_not_called()

    def test_link_api_parameter_overrides_env(self):
        os.environ['SAPCLI_ABAPGIT_API'] = 'steampunk'
        args = parse_args('link', '--api', 'rfc-via-classrun', 'PKG', 'URL')
        args.execute(self.connection, args)

        self.link_patch.assert_called_once()
        self.steampunk_patch.assert_not_called()

    def test_link_rejects_corrnr(self):
        args = parse_args('link', '--api', 'rfc-via-classrun', '--corrnr', 'C50K000001', 'PKG', 'URL')

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'The parameter --corrnr is not supported by the API rfc-via-classrun')
        self.link_patch.assert_not_called()


class TestAbapgitPull(ConsoleOutputTestCase, PatcherTestCase):
    '''Test Abapgit Pull command'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.patch('os.environ', new={})
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

    @patch('time.sleep')
    def test_pull_repo_steampunk_from_env(self, sleep_patch):
        self.repo_inst.get_status = Mock(return_value='S')

        os.environ['SAPCLI_ABAPGIT_API'] = 'steampunk'
        self.execute_pull_all_params()

        self.repo_inst.pull.assert_called_once()

    def test_pull_repo_unknown_api_from_env(self):
        os.environ['SAPCLI_ABAPGIT_API'] = 'foo'
        args = parse_args('pull', self.param_package)

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'Unknown abapGit API "foo" (SAPCLI_ABAPGIT_API) - use one of: steampunk, rfc-via-classrun')
        self.repo_patch.assert_not_called()


class TestAbapgitPullRfcViaClassrun(ConsoleOutputTestCase, PatcherTestCase):
    '''Test Abapgit Pull command with the API rfc-via-classrun'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.patch('os.environ', new={})
        self.repo_patch = self.patch('sap.adt.abapgit.Repository')
        self.pull_patch = self.patch('sap.platform.abap.abapgit_rfc.pull')
        self.pull_patch.return_value = BAPIReturn([
            {'TYPE': 'I', 'ID': '', 'NUMBER': '', 'MESSAGE': 'Deserializing'},
            {'TYPE': 'I', 'ID': '', 'NUMBER': '', 'MESSAGE': 'Finished'},
        ])

    def test_pull_all_params(self):
        args = parse_args(
            'pull',
            '--api', 'rfc-via-classrun',
            '--remote-user', 'user',
            '--remote-password', 'password',
            '--corrnr', 'C50K000001',
            'pkg')
        args.execute(self.connection, args)

        self.pull_patch.assert_called_once_with(
            self.connection,
            package='PKG',
            user='user',
            password='password',
            corrnr='C50K000001')
        self.repo_patch.assert_not_called()

        self.assertConsoleContents(console=self.console, stdout='''Info: Deserializing
Info: Finished
''')

    def test_pull_defaults(self):
        args = parse_args('pull', '--api', 'rfc-via-classrun', 'PKG')
        args.execute(self.connection, args)

        self.pull_patch.assert_called_once_with(
            self.connection,
            package='PKG',
            user='',
            password='',
            corrnr='')

    def test_pull_api_from_env(self):
        os.environ['SAPCLI_ABAPGIT_API'] = 'rfc-via-classrun'
        args = parse_args('pull', 'PKG')
        args.execute(self.connection, args)

        self.pull_patch.assert_called_once()
        self.repo_patch.assert_not_called()

    def test_pull_rejects_branch(self):
        args = parse_args('pull', '--api', 'rfc-via-classrun', '--branch', 'main', 'PKG')

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'The parameter --branch is not supported by the API rfc-via-classrun')
        self.pull_patch.assert_not_called()


class TestAbapgitList(ConsoleOutputTestCase, PatcherTestCase):
    '''Test Abapgit List command'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None

        self.connection = Mock()

        self.patch_console(console=self.console)
        self.patch('os.environ', new={})
        self.list_patch = self.patch('sap.platform.abap.abapgit_rfc.list_repositories')
        self.list_patch.return_value = [
            {
                'REPO_KEY': '000000000007',
                'NAME': 'CLAS',
                'ABAP_PACKAGE': '$SAPCLI_AGRFC',
                'URL': 'https://github.com/abapGit-tests/CLAS.git',
                'BRANCH_NAME': 'refs/heads/main',
                'DESERIALIZED_AT': '20261017200708.0661700',
            },
            {
                'REPO_KEY': '000000000008',
                'NAME': 'sapcli',
                'ABAP_PACKAGE': '$SAPCLI',
                'URL': 'https://github.com/jfilak/sapcli.git',
                'BRANCH_NAME': 'refs/heads/master',
                'DESERIALIZED_AT': '0.0000000',
            },
        ]

    def test_list_rfc_via_classrun(self):
        args = parse_args('list', '--api', 'rfc-via-classrun')
        args.execute(self.connection, args)

        self.list_patch.assert_called_once_with(self.connection)
        self.assertConsoleContents(console=self.console, stdout=(
            'Key          | Package       | Name   | URL                                       | Branch            | Deserialized At    \n'
            + '-' * 123 + '\n'
            + '000000000007 | $SAPCLI_AGRFC | CLAS   | https://github.com/abapGit-tests/CLAS.git | refs/heads/main   | 2026-10-17 20:07:08\n'
            '000000000008 | $SAPCLI       | sapcli | https://github.com/jfilak/sapcli.git      | refs/heads/master |                    \n'
        ))

    def test_list_no_repositories(self):
        self.list_patch.return_value = []

        args = parse_args('list', '--api', 'rfc-via-classrun')
        args.execute(self.connection, args)

        self.assertConsoleContents(console=self.console, stdout=(
            'Key | Package | Name | URL | Branch | Deserialized At\n'
            '-----------------------------------------------------\n'
        ))

    def test_list_api_from_env(self):
        os.environ['SAPCLI_ABAPGIT_API'] = 'rfc-via-classrun'
        args = parse_args('list')
        args.execute(self.connection, args)

        self.list_patch.assert_called_once_with(self.connection)

    def test_list_steampunk_not_implemented(self):
        args = parse_args('list')

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception), 'not implemented')
        self.list_patch.assert_not_called()

    def test_list_unknown_api_from_env(self):
        os.environ['SAPCLI_ABAPGIT_API'] = 'foo'
        args = parse_args('list')

        with self.assertRaises(SAPCliError) as caught:
            args.execute(self.connection, args)

        self.assertEqual(str(caught.exception),
                         'Unknown abapGit API "foo" (SAPCLI_ABAPGIT_API) - use one of: steampunk, rfc-via-classrun')
