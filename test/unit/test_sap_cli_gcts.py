#!/usr/bin/env python3

from io import StringIO
import unittest
import json
from unittest.mock import MagicMock, patch, Mock, PropertyMock, mock_open, call, ANY
from sap.rest.gcts import package_name_from_url
from sap.rest.gcts.sugar import (LogTaskOperationProgress)
import sap.cli.gcts
import sap.cli.gcts_utils
import sap.cli.core
from sap.rest.errors import HTTPRequestError
from sap.errors import OperationTimeoutError

from test.unit.mock import (
    RESTConnection,
    Request,
    ConsoleOutputTestCase,
    PatcherTestCase,
    GCTSLogBuilder,
    GCTSLogMessages,
    GCTSLogProtocol,
    make_gcts_log_error
)

from fixtures_sap_rest_gcts import (
    GCTS_RESPONSE_REPO_NOT_EXISTS,
    GCTS_RESPONSE_REPO_PULL_OK,
)

from infra import generate_parse_args
from sap.rest.gcts.repo_task import RepositoryTask


parse_args = generate_parse_args(sap.cli.gcts.CommandGroup())


def dummy_gcts_error_log():
    log_builder = GCTSLogBuilder()

    log_builder.log_error(
        make_gcts_log_error(
            'Line 1',
            protocol=GCTSLogProtocol('Program',
                                     GCTSLogMessages('protocol 1',
                                                     'protocol 2'))))

    log_builder.log_error(make_gcts_log_error('Line 2'))
    log_builder.log_exception('Message', 'ERROR')
    return log_builder.get_contents()


def mock_repository(fake_fetch_repos, **kwargs):
    fake_repo = Mock()
    fake_repo.__dict__.update(**kwargs)

    if isinstance(fake_fetch_repos.return_value, list):
        fake_fetch_repos.return_value.append(fake_repo)
    else:
        fake_fetch_repos.return_value = [fake_repo]

    return fake_repo


class TestgCTSDumpError(ConsoleOutputTestCase, unittest.TestCase):

    def test_dump_first_level(self):
        messages = dummy_gcts_error_log()
        sap.cli.gcts_utils.dump_gcts_messages(self.console, messages)
        self.assertConsoleContents(self.console, stderr='''Error Log:
  Line 1
    protocol 1
    protocol 2
  Line 2
  Message
Log:
  Line 1
    protocol 1
    protocol 2
  Line 2
Exception:
  Message
'''
                                   )

    def test_dump_uknown_messages(self):
        sap.cli.gcts_utils.dump_gcts_messages(self.console, {'random': 'error'})
        self.assertConsoleContents(self.console, stderr='''{'random': 'error'}
''')

    def test_dump_only_error_log(self):
        sap.cli.gcts_utils.dump_gcts_messages(self.console, {'errorLog': ['error']})
        self.assertConsoleContents(self.console, stderr='''Error Log:
  error
''')

    def test_dump_only_log(self):
        sap.cli.gcts_utils.dump_gcts_messages(self.console, {'log': ['error']})
        self.assertConsoleContents(self.console, stderr='''Log:
  error
''')

    def test_dump_only_exception(self):
        sap.cli.gcts_utils.dump_gcts_messages(self.console, {'exception': 'error'})
        self.assertConsoleContents(self.console, stderr='''Exception:
  error
''')


class TestgCTSGetRepository(PatcherTestCase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.connection = Mock()
        self.fake_fetch_repos = self.patch('sap.rest.gcts.simple.fetch_repos')

    def test_get_repository_name(self):
        repo_rid = 'repo-id'
        repo = sap.cli.gcts.get_repository(self.connection, repo_rid)

        self.assertEqual(repo.rid, repo_rid)
        self.fake_fetch_repos.assert_not_called()

    def test_get_repository_url(self):
        repo_rid = 'repo-id'
        repo_url = 'http://github.com/the_repo.git'

        fake_repo = mock_repository(self.fake_fetch_repos, rid=repo_rid, url=repo_url)
        repo = sap.cli.gcts.get_repository(self.connection, repo_url)

        self.assertEqual(repo, fake_repo)
        self.fake_fetch_repos.assert_called_once_with(self.connection)
        repo.wipe_data.assert_called_once()

    def test_get_repository_url_https(self):
        repo_rid = 'repo-id'
        repo_url = 'https://github.com/the_repo.git'

        fake_repo = mock_repository(self.fake_fetch_repos, rid=repo_rid, url=repo_url)
        repo = sap.cli.gcts.get_repository(self.connection, repo_url)

        self.assertEqual(repo, fake_repo)
        self.fake_fetch_repos.assert_called_once_with(self.connection)
        repo.wipe_data.assert_called_once()

    def test_get_repository_url_not_found(self):
        repo_url = 'http://github.com/the_repo.git'

        with self.assertRaises(sap.cli.gcts.SAPCliError) as cm:
            sap.cli.gcts.get_repository(self.connection, repo_url)

        self.assertEqual(
            f'No repository found with the URL "{repo_url}".',
            str(cm.exception)
        )
        self.fake_fetch_repos.assert_called_once_with(self.connection)

    def test_get_repository_url_not_unique(self):
        repo_url = 'http://github.com/the_repo.git'

        mock_repository(self.fake_fetch_repos, name='the_repo_1', url=repo_url)
        mock_repository(self.fake_fetch_repos, name='the_repo_2', url=repo_url)

        with self.assertRaises(sap.cli.gcts.SAPCliError) as cm:
            sap.cli.gcts.get_repository(self.connection, repo_url)

        self.assertEqual(
            f'Cannot uniquely identify the package based on the URL "{repo_url}".',
            str(cm.exception)
        )
        self.fake_fetch_repos.assert_called_once_with(self.connection)


class TestgCTSCloneSync(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_clone = self.patch('sap.rest.gcts.simple.clone')
        self.fake_get_repository = self.patch('sap.cli.gcts.get_repository')
        self.fake_simple_wait_for_operation = self.patch('sap.rest.gcts.simple.wait_for_operation')
        self.fake_heartbeat = self.patch('sap.cli.helpers.ConsoleHeartBeat', return_value=MagicMock())

        self.spy_is_clone_activity_success = self.patch(
            'sap.cli.gcts.is_clone_activity_success',
            wraps=sap.rest.gcts.activities.is_clone_activity_success)

        self.conn = Mock()
        self.fake_repo = sap.rest.gcts.remote_repo.Repository(self.conn, 'sample', data={
            'url': 'https://example.org/repo/git/sample.git',
            'branch': 'main',
            'currentCommit': 'FEDBCA9876543210'
        })
        self.fake_repo.activities = Mock()
        self.fake_repo.activities.return_value = [{'rc': '004'}]
        self.fake_simple_clone.return_value = self.fake_repo
        self.fake_get_repository.return_value = self.fake_repo

    def clone(self, *args, **kwargs):
        return parse_args('clone', *args, **kwargs)

    def test_clone_with_url_only(self):
        args = self.clone('https://example.org/repo/git/sample.git', '--sync-clone')

        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone.assert_called_once_with(
            self.conn,
            'https://example.org/repo/git/sample.git',
            'sample',
            start_dir='src/',
            vsid='6IT',
            vcs_token=None,
            error_exists=True,
            typ='GITHUB',
            role='SOURCE',
            no_import=False,
            buffer_only=False,
            progress_consumer=None,
        )

        self.assertConsoleContents(console=self.console, stdout='''Clone activity finished with return code: 4
Cloned repository:
 URL   : https://example.org/repo/git/sample.git
 branch: main
 HEAD  : FEDBCA9876543210
''')

    def test_clone_with_all_params(self):
        args = self.clone(
            'https://example.org/repo/git/sample.git',
            '--vsid', 'GIT',
            '--vcs-token', '12345',
            '--starting-folder', 'backend/src/',
            '--no-fail-exists',
            '--role', 'TARGET',
            '--type', 'GIT',
            '--wait-for-ready', '10',
            '--sync-clone',
            '--no-import',
            '--buffer-only',
            '--heartbeat', '1',
        )

        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone.assert_called_once_with(
            self.conn,
            'https://example.org/repo/git/sample.git',
            'sample',
            start_dir='backend/src/',
            vsid='GIT',
            vcs_token='12345',
            error_exists=False,
            typ='GIT',
            role='TARGET',
            no_import=True,
            buffer_only=True,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_clone.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.spy_is_clone_activity_success.assert_not_called()

        self.fake_heartbeat.assert_called_once_with(self.console, 1)

    def test_clone_with_no_import(self):
        args = self.clone(
            'https://example.org/repo/git/sample.git',
            '--vsid', 'GIT',
            '--vcs-token', '12345',
            '--starting-folder', 'backend/src/',
            '--no-fail-exists',
            '--role', 'TARGET',
            '--type', 'GIT',
            '--wait-for-ready', '10',
            '--sync-clone',
            '--no-import',
            '--heartbeat', '1',
        )

        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone.assert_called_once_with(
            self.conn,
            'https://example.org/repo/git/sample.git',
            'sample',
            start_dir='backend/src/',
            vsid='GIT',
            vcs_token='12345',
            error_exists=False,
            typ='GIT',
            role='TARGET',
            no_import=True,
            buffer_only=False,
            progress_consumer=ANY,
        )

        call_args = self.fake_simple_clone.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.spy_is_clone_activity_success.assert_not_called()

    def test_clone_with_buffer_only(self):
        args = self.clone(
            'https://example.org/repo/git/sample.git',
            '--vsid', 'GIT',
            '--vcs-token', '12345',
            '--starting-folder', 'backend/src/',
            '--no-fail-exists',
            '--role', 'TARGET',
            '--type', 'GIT',
            '--wait-for-ready', '10',
            '--sync-clone',
            '--buffer-only',
            '--heartbeat', '1',
        )

        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone.assert_called_once_with(
            self.conn,
            'https://example.org/repo/git/sample.git',
            'sample',
            start_dir='backend/src/',
            vsid='GIT',
            vcs_token='12345',
            error_exists=False,
            typ='GIT',
            role='TARGET',
            no_import=False,
            buffer_only=True,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_clone.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.spy_is_clone_activity_success.assert_called_once()

    def test_clone_existing(self):
        repo_url = 'https://example.org/repo/git/sample.git'
        args = self.clone(repo_url, '--no-fail-exists', '--sync-clone')

        args.execute(self.conn, args)
        self.fake_simple_clone.assert_called_once_with(
            self.conn,
            'https://example.org/repo/git/sample.git',
            'sample',
            start_dir='src/',
            vsid='6IT',
            vcs_token=None,
            error_exists=False,
            typ='GITHUB',
            role='SOURCE',
            no_import=False,
            buffer_only=False,
            progress_consumer=None,
        )
        self.fake_heartbeat.assert_called_once_with(self.console, 0)

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_clone_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_clone.return_value = None
        self.fake_simple_clone.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.clone('url', '--sync-clone')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 1)
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.spy_is_clone_activity_success.assert_not_called()
        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    def test_clone_internal_error_no_wait(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        self.fake_simple_clone.side_effect = HTTPRequestError(None, fake_response)

        args = self.clone('url', '--sync-clone', '--wait-for-ready', '0')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(
            self.console,
            stdout='Clone request responded with an error.\nCheckout "--wait-for-ready" parameter!\n',
            stderr='500\nTest Exception\n'
        )

    def test_clone_internal_error_with_wait(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        self.fake_simple_clone.side_effect = HTTPRequestError(None, fake_response)

        args = self.clone('url', '--wait-for-ready', '10', '--sync-clone', '--heartbeat', '2')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 0)

        repo = self.fake_simple_wait_for_operation.mock_calls[0].args[0]
        clone_test = self.fake_simple_wait_for_operation.mock_calls[0].args[1]
        self.assertTrue(clone_test(repo))
        self.assertEqual(self.fake_repo.activities.mock_calls[0].args[0].get_params()['type'], 'CLONE')
        self.fake_heartbeat.assert_has_calls([call(self.console, 2), call(self.console, 2)])
        self.assertConsoleContents(self.console, stdout='''Clone request responded with an error. Checking clone process ...
Clone activity finished with return code: 4
Clone process finished successfully.
Waiting for repository to be ready ...
Cloned repository:
 URL   : https://example.org/repo/git/sample.git
 branch: main
 HEAD  : FEDBCA9876543210
''')

    def test_clone_internal_error_with_wait_get_activity_rc_error(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        clone_exception = HTTPRequestError(None, fake_response)

        self.fake_simple_clone.side_effect = clone_exception
        self.fake_repo.activities.side_effect = HTTPRequestError(None, fake_response)

        args = self.clone('url', '--wait-for-ready', '10', '--sync-clone')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.fake_repo.activities.assert_called_once()
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.assertConsoleContents(self.console,
                                   stdout='Clone request responded with an error. Checking clone process ...\n',
                                   stderr='Unable to obtain activities of repository: "sample"\n500\nTest Exception\n')

    def test_clone_internal_error_with_wait_get_activity_rc_empty(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        self.fake_simple_clone.side_effect = HTTPRequestError(None, fake_response)
        self.fake_repo.activities.return_value = []

        args = self.clone('url', '--wait-for-ready', '10', '--sync-clone')

        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.fake_repo.activities.assert_called_once()
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.assertConsoleContents(self.console,
                                   stdout='Clone request responded with an error. Checking clone process ...\n',
                                   stderr='Expected CLONE activity is empty! Repository: "sample"\n')

    def test_clone_internal_error_with_wait_get_activity_rc_failed(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        self.fake_simple_clone.side_effect = HTTPRequestError(None, fake_response)
        self.fake_repo.activities.return_value = [{'rc': '8'}]

        args = self.clone('url', '--wait-for-ready', '10', '--sync-clone')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.fake_repo.activities.assert_called_once()
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.assertConsoleContents(self.console,
                                   stdout='Clone request responded with an error. Checking clone process ...\n'
                                          'Clone activity finished with return code: 8\n',
                                    stderr='500\nTest Exception\n')

    def test_clone_internal_error_with_wait_timeout(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        clone_exception = HTTPRequestError(None, fake_response)

        self.fake_simple_clone.side_effect = clone_exception
        self.fake_simple_wait_for_operation.side_effect = sap.rest.errors.SAPCliError('Waiting for clone process timed out')

        args = self.clone('url', '--wait-for-ready', '10', '--sync-clone')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.fake_heartbeat.assert_has_calls([call(self.console, 0), call(self.console, 0)])

        self.assertConsoleContents(
            self.console,
            stdout='Clone request responded with an error. Checking clone process ...\n'
                   'Clone activity finished with return code: 4\n'
                   'Clone process finished successfully.\n'
                   'Waiting for repository to be ready ...\n',
            stderr='Waiting for clone process timed out\n'
        )


class TestgCTSCloneAsync(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_clone_with_task = self.patch('sap.rest.gcts.simple.clone_with_task')
        self.fake_get_repository = self.patch('sap.cli.gcts.get_repository')
        self.fake_print_gcts_task_info = self.patch('sap.cli.gcts_utils.print_gcts_task_info')
        self.fake_heartbeat = self.patch('sap.cli.helpers.ConsoleHeartBeat', return_value=MagicMock())
        self.fake_is_clone_activity_success = self.patch('sap.cli.gcts.is_clone_activity_success')
        self.conn = Mock()
        self.conn.get_json.return_value = {
            'result': {
                'url': 'https://example.org/repo/git/sample.git',
                'branch': 'main',
                'currentCommit': 'FEDBCA9876543210'
            }
        }

        self.defaults = {
            'wait_for_ready': 600,
            'heartbeat': 0,
            'vsid': '6IT',
            'starting_folder': 'src/',
            'poll_period': 30,
            'type': 'GITHUB',
            'role': 'SOURCE',
        }

        self.command_arguments = {
            'wait_for_ready': 10,
            'heartbeat': 1,
            'vsid': '7IT',
            'starting_folder': 'backend/src/',
            'poll_period': 50,
            'type': 'GIT',
            'role': 'TARGET',
            'vcs-token': '12345',
            'url': 'https://example.org/repo/git/sample.git',
            'package': 'sample',
        }
        self.default_repo_branch = 'main'
        self.default_repo_head = 'FEDBCA9876543210'

        self.fake_repo = sap.rest.gcts.remote_repo.Repository(self.conn, 'sample', data={
            'url': self.command_arguments['url'],
            'branch': self.default_repo_branch,
            'currentCommit': self.default_repo_head,
            'status': 'CLONED'
        })

        self.fake_simple_clone_with_task.return_value = self.fake_repo
        self.fake_is_clone_activity_success.return_value = True

    def clone(self, *args, **kwargs):
        return parse_args('clone', *args, **kwargs)

    def expected_console_output(self, url=None, branch=None, head=None):
        if url is None:
            url = self.fake_repo.url
        if branch is None:
            branch = self.default_repo_branch
        if head is None:
            head = self.default_repo_head

        return f'''Cloned repository:
 URL   : {url}
 branch: {branch}
 HEAD  : {head}
'''

    def test_async_clone_with_url(self):
        args = self.clone(self.command_arguments['url'])
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone_with_task.assert_called_once_with(
            self.conn,
            self.command_arguments['url'],
            package_name_from_url(self.command_arguments['url']),
            start_dir=self.defaults['starting_folder'],
            vcs_token=None,
            vsid=self.defaults['vsid'],
            error_exists=True,
            role=self.defaults['role'],
            typ=self.defaults['type'],
            wait_for_ready=self.defaults['wait_for_ready'],
            poll_period=self.defaults['poll_period'],
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_clone_with_task.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, LogTaskOperationProgress)
        self.fake_is_clone_activity_success.assert_called_once()
        self.fake_heartbeat.assert_called_once_with(self.console, 0)

        expected_output = f'''Cloned repository:
 URL   : {self.command_arguments['url']}
 branch: {self.default_repo_branch}
 HEAD  : {self.default_repo_head}
'''
        self.assertConsoleContents(
            console=self.console,
            stdout=expected_output
        )

    def test_async_clone_with_all_params(self):
        args = self.clone(
            self.command_arguments['url'],
            '--vsid', self.command_arguments['vsid'],
            '--vcs-token', self.command_arguments['vcs-token'],
            '--starting-folder', self.command_arguments['starting_folder'],
            '--no-fail-exists',
            '--role', self.command_arguments['role'],
            '--type', self.command_arguments['type'],
            '--wait-for-ready', f"{self.command_arguments['wait_for_ready']}",
            '--poll-period', f"{self.command_arguments['poll_period']}",
            '--heartbeat', f"{self.command_arguments['heartbeat']}",
            '--no-import',
            '--buffer-only',
        )

        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone_with_task.assert_called_once_with(
            self.conn,
            self.command_arguments['url'],
            package_name_from_url(self.command_arguments['url']),
            start_dir=self.command_arguments['starting_folder'],
            vcs_token=self.command_arguments['vcs-token'],
            vsid=self.command_arguments['vsid'],
            error_exists=False,
            role=self.command_arguments['role'],
            typ=self.command_arguments['type'],
            wait_for_ready=self.command_arguments['wait_for_ready'],
            poll_period=self.command_arguments['poll_period'],
            no_import=True,
            buffer_only=True,
            progress_consumer=ANY,
        )

        self.fake_heartbeat.assert_called_once_with(self.console, self.command_arguments['heartbeat'])
        self.fake_is_clone_activity_success.assert_not_called()
        expected_output = f'''Cloned repository:
 URL   : {self.command_arguments['url']}
 branch: {self.default_repo_branch}
 HEAD  : {self.default_repo_head}
'''
        self.assertConsoleContents(console=self.console, stdout=expected_output)

    def test_async_clone_with_no_import(self):
        args = self.clone(
            self.command_arguments['url'],
            '--no-import',
        )

        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone_with_task.assert_called_once_with(
            self.conn,
            self.command_arguments['url'],
            package_name_from_url(self.command_arguments['url']),
            start_dir=self.defaults['starting_folder'],
            vcs_token=None,
            vsid=self.defaults['vsid'],
            error_exists=True,
            role=self.defaults['role'],
            typ=self.defaults['type'],
            wait_for_ready=self.defaults['wait_for_ready'],
            poll_period=self.defaults['poll_period'],
            no_import=True,
            buffer_only=False,
            progress_consumer=ANY,
        )

        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.fake_is_clone_activity_success.assert_not_called()
        expected_output = f'''Cloned repository:
 URL   : {self.command_arguments['url']}
 branch: {self.default_repo_branch}
 HEAD  : {self.default_repo_head}
'''
        self.assertConsoleContents(console=self.console, stdout=expected_output)

    def test_async_clone_with_buffer_only(self):
        args = self.clone(
            self.command_arguments['url'],
            '--buffer-only',
        )

        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_clone_with_task.assert_called_once_with(
            self.conn,
            self.command_arguments['url'],
            package_name_from_url(self.command_arguments['url']),
            start_dir=self.defaults['starting_folder'],
            vcs_token=None,
            vsid=self.defaults['vsid'],
            error_exists=True,
            role=self.defaults['role'],
            typ=self.defaults['type'],
            wait_for_ready=self.defaults['wait_for_ready'],
            poll_period=self.defaults['poll_period'],
            no_import=False,
            buffer_only=True,
            progress_consumer=ANY,
        )

        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.fake_is_clone_activity_success.assert_called_once()
        expected_output = f'''Cloned repository:
 URL   : {self.command_arguments['url']}
 branch: {self.default_repo_branch}
 HEAD  : {self.default_repo_head}
'''
        self.assertConsoleContents(console=self.console, stdout=expected_output)

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_async_simple_clone_unexpected_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_clone_with_task.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.clone(self.command_arguments['url'], '--wait-for-ready', '0')
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 1)
        self.fake_simple_clone_with_task.assert_called_once_with(
            self.conn,
            self.command_arguments['url'],
            package_name_from_url(self.command_arguments['url']),
            start_dir=self.defaults['starting_folder'],
            vcs_token=None, vsid=self.defaults['vsid'],
            error_exists=True,
            role=self.defaults['role'],
            typ=self.defaults['type'],
            wait_for_ready=0,
            poll_period=self.defaults['poll_period'],
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )
        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    def test_async_clone_http_request_error(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        self.fake_simple_clone_with_task.side_effect = HTTPRequestError(None, fake_response)

        args = self.clone(self.command_arguments['url'])
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 1)

        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.fake_is_clone_activity_success.assert_not_called()
        self.assertConsoleContents(
            self.console,
            stdout='Clone request responded with an error.\n',
            stderr='500\nTest Exception\n'
        )

    def test_async_clone_timeout_error(self):
        fake_response = Mock()
        fake_response.text = 'Test Exception'
        fake_response.status_code = 500

        self.fake_simple_clone_with_task.side_effect = OperationTimeoutError(None, fake_response)

        args = self.clone(self.command_arguments['url'])
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 1)

        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.fake_is_clone_activity_success.assert_not_called()
        self.assertConsoleContents(
            self.console,
            stdout=f'You can check the task status using the following command:\n  sapcli gcts task list {package_name_from_url(self.command_arguments['url'])}\n',
            stderr='Clone task did not finish in the period specified by the "--wait-for-ready" parameter.\n'
        )


class TestgCTSRepoList(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_fetch_repos = self.patch('sap.rest.gcts.simple.fetch_repos')

    def repolist(self, *args, **kwargs):
        return parse_args('repolist', *args, **kwargs)

    def test_repolist_no_params(self):
        conn = Mock()

        self.fake_simple_fetch_repos.return_value = [
            sap.rest.gcts.remote_repo.Repository(conn, 'one_rid', data={
                'rid': 'one_rid',
                'name': 'one',
                'status': 'CREATED',
                'branch': 'one_branch',
                'url': 'one_url',
                'vsid': 'vS1D',
                'currentCommit': '123'}),
            sap.rest.gcts.remote_repo.Repository(conn, 'two_rid', data={
                'rid': 'two_rid',
                'name': 'two',
                'status': 'READY',
                'branch': 'two_branch',
                'url': 'two_url',
                'vsid': 'vS2D',
                'currentCommit': '456'}),
            sap.rest.gcts.remote_repo.Repository(conn, 'third_rid', data={
                'rid': 'third_rid',
                'name': 'three',
                'status': 'CLONED',
                'branch': 'third_branch',
                'url': 'third_url',
                'vsid': 'vS3D',
                'currentCommit': '7890'}),
        ]

        args = self.repolist()
        args.execute(conn, args)

        self.fake_simple_fetch_repos.assert_called_once_with(conn)
        self.maxDiff = None
        self.assertConsoleContents(self.console, stdout='''Name  | RID       | Branch       | Commit | Status  | vSID | URL      
----------------------------------------------------------------------
one   | one_rid   | one_branch   | 123    | CREATED | vS1D | one_url  
two   | two_rid   | two_branch   | 456    | READY   | vS2D | two_url  
three | third_rid | third_branch | 7890   | CLONED  | vS3D | third_url
''')

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_repolist_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_fetch_repos.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.repolist()
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)


class TestgCTSDelete(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_delete = self.patch('sap.rest.gcts.simple.delete')

    def delete(self, *args, **kwargs):
        return parse_args('delete', *args, **kwargs)

    def test_delete_no_params(self):
        conn = Mock()
        repo_rid = 'repo_id'

        args = self.delete(repo_rid)
        args.execute(conn, args)

        repo = self.fake_simple_delete.call_args.kwargs['repo']
        self.assertEqual(repo.rid, repo_rid)

        self.fake_simple_delete.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console, stdout='''The repository "repo_id" has been deleted
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_delete_with_url(self, fake_fetch_repos):
        conn = Mock()

        repo_rid = 'repo-id'
        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, rid=repo_rid, name=repo_name, url=repo_url, configuration={})

        args = self.delete(repo_url)
        args.execute(conn, args)

        self.fake_simple_delete.assert_called_once_with(conn, repo=fake_repo)
        self.assertConsoleContents(self.console, stdout=f'''The repository "{repo_rid}" has been deleted
''')

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_delete_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_delete.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.delete('a_repo')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_delete_url_error(self, _):
        repo_url = 'http://github.com/the_repo.git'

        args = self.delete(repo_url)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stderr=f'No repository found with the URL "{repo_url}".\n')


class TestgCTSCheckout(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None
        self.conn = Mock()

        self.patch_console(console=self.console)
        self.fake_simple_checkout = self.patch('sap.rest.gcts.simple.checkout')
        self.fake_heartbeat = self.patch('sap.cli.helpers.ConsoleHeartBeat', return_value=MagicMock())
        self.fake_get_activity_rc = self.patch('sap.rest.gcts.activities.get_activity_rc')
        self.fake_get_repository = self.patch('sap.cli.gcts.get_repository')
        self.repo_url = 'http://github.com/the_repo.git'
        self.rid = 'the_repo'
        self.repo_from_branch = 'old_branch'
        self.repo_from_commit = '123'
        self.repo_to_commit = '456'
        self.repo_to_branch = 'new_branch'
        self.response_request = 'YGCTS987654321'
        self.repo = sap.rest.gcts.remote_repo.Repository(self.conn, self.rid, data={
            'branch': self.repo_from_branch,
            'currentCommit': self.repo_from_commit,
            'status': 'READY'
        })
        self.repo._fetch_data = Mock(return_value=self.repo._data)

        self.raised_http_error_in_checkout = None

        def fake_checkout(connection, branch, repo=None, **_):
            if repo is None:
                repo = self.repo

            repo._data['branch'] = branch
            repo._data['currentCommit'] = self.repo_to_commit
            repo._data['fromCommit'] = self.repo_from_commit
            repo._data['toCommit'] = self.repo_to_commit

            if self.raised_http_error_in_checkout:
                raise self.raised_http_error_in_checkout

            return {
                'fromCommit': self.repo_from_commit,
                'toCommit': self.repo_to_commit,
                'request': self.response_request
            }

        self.fake_simple_checkout.side_effect = fake_checkout
        self.fake_get_repository.return_value = self.repo
        self.expected_output = [f'The repository "{self.repo.rid}" has been set to the branch "{self.repo_to_branch}"',
                                f'({self.repo_from_branch}:{self.repo_from_commit}) -> ({self.repo_to_branch}:{self.repo_to_commit})']

    def checkout(self, *args, **kwargs):
        return parse_args('checkout', *args, **kwargs)

    def test_checkout_no_params(self):
        args = self.checkout(self.repo_url, self.repo_to_branch)
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        self.fake_simple_checkout.assert_called_once_with(
            self.conn,
            self.repo_to_branch,
            repo=self.repo,
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_checkout.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.assertConsoleContents(self.console, stdout='\n'.join(self.expected_output) + '\n')

    def test_checkout_with_url(self):
        args = self.checkout(self.repo_url, self.repo_to_branch)
        args.execute(self.conn, args)

        self.fake_simple_checkout.assert_called_once_with(
            self.conn,
            self.repo_to_branch,
            repo=self.repo,
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_checkout.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.assertConsoleContents(self.console, stdout='\n'.join(self.expected_output) + '\n')

    def test_checkout_json_output(self):
        args = self.checkout(self.repo_url, self.repo_to_branch, '--format', 'JSON')
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)

        expected_output = ['{',
                           '  "fromCommit": "123",',
                           '  "toCommit": "456",',
                           '  "request": "YGCTS987654321"',
                           '}']
        self.assertConsoleContents(self.console, stdout='\n'.join(expected_output) + '\n')

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_checkout_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_checkout.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.checkout(self.repo_url, self.repo_to_branch)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    def test_checkout_url_error(self):
        self.fake_get_repository.side_effect = sap.rest.errors.SAPCliError(f'No repository found with the URL "{self.repo_url}".')
        args = self.checkout(self.repo_url, self.repo_to_branch)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stderr=f'No repository found with the URL "{self.repo_url}".\n')

    def test_checkout_with_http_error(self):
        self.fake_simple_checkout.side_effect = HTTPRequestError(None, Mock(text='Checkout exception', status_code=500))
        args = self.checkout(self.repo_url, self.repo_to_branch)
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 1)

        self.fake_get_repository.assert_called_once_with(self.conn, self.repo_url)

        self.fake_simple_checkout.assert_called_once_with(
            self.conn, self.repo_to_branch, repo=self.repo,
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )

        call_args = self.fake_simple_checkout.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        self.assertConsoleContents(self.console, stdout='Checkout request responded with an error. Checkout "--wait-for-ready" parameter!\n',
                                   stderr='500\nCheckout exception\n')

    @patch('sap.rest.gcts.simple.wait_for_operation')
    def test_checkout_with_http_error_wait_success(self, fake_wait_for_operation):
        self.fake_get_activity_rc.return_value = 0
        self.raised_http_error_in_checkout = HTTPRequestError(None, Mock(text='Checkout exception', status_code=500))
        args = self.checkout(self.repo_url, self.repo_to_branch, '--wait-for-ready', '10')
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)
        checkout_test = fake_wait_for_operation.mock_calls[0].args[1]
        self.assertTrue(checkout_test(self.repo))
        self.fake_simple_checkout.assert_called_once_with(
            self.conn, self.repo_to_branch, repo=self.repo,
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )
        expected_output = ['Checkout request responded with an error. Checking checkout process ...',
                           'Checkout activity finished with return code: 0',
                           'Checkout process finished successfully. Waiting for repository to be ready ...',
                           f'The repository "{self.repo.rid}" has been set to the branch "{self.repo_to_branch}"',
                           f'({self.repo_from_branch}:{self.repo_from_commit}) -> ({self.repo_to_branch}:{self.repo_to_commit})']
        self.assertConsoleContents(self.console, stdout='\n'.join(expected_output) + '\n')

    def test_checkout_with_http_error_activity_error(self):

        self.fake_get_activity_rc.return_value = 12
        self.raised_http_error_in_checkout = HTTPRequestError(None, Mock(text='Checkout exception', status_code=500))
        args = self.checkout(self.repo_url, self.repo_to_branch, '--wait-for-ready', '10')
        exit_code = args.execute(self.conn, args)

        self.assertEqual(exit_code, 1)
        self.fake_simple_checkout.assert_called_once_with(
            self.conn, self.repo_to_branch, repo=self.repo,
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_checkout.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.fake_heartbeat.assert_called_once_with(self.console, 0)
        expected_output = [
            'Checkout request responded with an error. Checking checkout process ...',
            'Checkout activity finished with return code: 12'
        ]
        self.assertConsoleContents(self.console, stdout='\n'.join(expected_output) + '\n',
                                   stderr='''500
Checkout exception
''')

    def test_checkout_with_http_error_no_import_flag(self):
        '''Not checking activities because of --no-import flag'''
        self.raised_http_error_in_checkout = HTTPRequestError(None, Mock(text='Checkout exception', status_code=500))
        args = self.checkout(self.repo_url, self.repo_to_branch, '--wait-for-ready', '10', '--no-import')
        exit_code = args.execute(self.conn, args)

        self.assertEqual(exit_code, 0)
        self.fake_simple_checkout.assert_called_once_with(
            self.conn, self.repo_to_branch, repo=self.repo,
            no_import=True,
            buffer_only=False,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_checkout.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)
        self.fake_heartbeat.assert_has_calls([call(self.console, 0), call(self.console, 0)])
        self.assertConsoleContents(self.console, stdout='\n'.join(self.expected_output) + '\n')
    
    @patch('sap.rest.gcts.simple.wait_for_operation')
    def test_checkout_with_http_error_buffer_only_flag(self, _):
        '''Checking activities because of --buffer-only flag dont change the behavior of the checkout command'''
        self.fake_get_activity_rc.return_value = 0
        self.raised_http_error_in_checkout = HTTPRequestError(None, Mock(text='Checkout exception', status_code=500))
        args = self.checkout(self.repo_url, self.repo_to_branch, '--wait-for-ready', '10', '--buffer-only')
        exit_code = args.execute(self.conn, args)
        self.assertEqual(exit_code, 0)
       
        self.fake_simple_checkout.assert_called_once_with(
            self.conn, self.repo_to_branch, repo=self.repo,
            no_import=False,
            buffer_only=True,
            progress_consumer=ANY,
        )
        expected_output = ['Checkout request responded with an error. Checking checkout process ...',
                           'Checkout activity finished with return code: 0',
                           'Checkout process finished successfully. Waiting for repository to be ready ...',
                           f'The repository "{self.repo.rid}" has been set to the branch "{self.repo_to_branch}"',
                           f'({self.repo_from_branch}:{self.repo_from_commit}) -> ({self.repo_to_branch}:{self.repo_to_commit})']
        self.assertConsoleContents(self.console, stdout='\n'.join(expected_output) + '\n')
    
    @patch('sap.rest.gcts.simple.wait_for_operation')
    def test_checkout_with_http_error_wait_error(self, fake_wait_for_operation):
        self.fake_get_activity_rc.return_value = 0
        self.raised_http_error_in_checkout = HTTPRequestError(None, Mock(text='Checkout exception', status_code=500))
        wait_for_operation_error_msg = 'Waiting for the operation timed out\nHTTP 500!'
        fake_wait_for_operation.side_effect = sap.cli.gcts.SAPCliError(wait_for_operation_error_msg)
        args = self.checkout(self.repo_url, self.repo_to_branch, '--wait-for-ready', '1')
        exit_code = args.execute(self.conn, args)

        self.assertEqual(exit_code, 1)
        self.fake_simple_checkout.assert_called_once_with(
            self.conn, self.repo_to_branch, repo=self.repo,
            no_import=False,
            buffer_only=False,
            progress_consumer=ANY,
        )
        call_args = self.fake_simple_checkout.call_args
        progress_consumer = call_args.kwargs['progress_consumer']
        self.assertIsInstance(progress_consumer, sap.cli.gcts_utils.ConsoleSugarOperationProgress)

        fake_wait_for_operation.assert_called_once()
        self.assertEqual(self.fake_heartbeat.call_count, 2)
        self.fake_heartbeat.assert_any_call(self.console, 0)
        self.assertConsoleContents(self.console,
            stdout='Checkout request responded with an error. Checking checkout process ...\n'
                   'Checkout activity finished with return code: 0\n'
                   'Checkout process finished successfully. Waiting for repository to be ready ...\n',
            stderr=wait_for_operation_error_msg + '\n')


class TestgCTSLog(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_log = self.patch('sap.rest.gcts.simple.log')

    def log(self, *args, **kwargs):
        return parse_args('log', *args, **kwargs)

    def test_log_no_params(self):
        conn = Mock()
        repo_rid = 'repo-id'
        self.fake_simple_log.return_value = [
            {'id': '456',
             'author': 'Billy Lander',
             'authorMail': 'billy.lander@example.com',
             'date': '2020-10-09',
             'message': 'Finall commit'
             },
            {'id': '123',
             'author': 'Hugh Star',
             'authorMail': 'hugh.star@example.com',
             'date': '2020-10-02',
             'message': 'Popping commit'
             },
        ]

        args = self.log(repo_rid)
        args.execute(conn, args)

        repo = self.fake_simple_log.call_args.kwargs['repo']
        self.assertEqual(repo.rid, repo_rid)

        self.fake_simple_log.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console, stdout='''commit 456
Author: Billy Lander <billy.lander@example.com>
Date:   2020-10-09

    Finall commit

commit 123
Author: Hugh Star <hugh.star@example.com>
Date:   2020-10-02

    Popping commit
''')

    def test_log_no_params_no_commits(self):
        conn = Mock()
        repo_rid = 'repo-id'
        self.fake_simple_log.return_value = []

        args = self.log(repo_rid)
        args.execute(conn, args)

        repo = self.fake_simple_log.call_args.kwargs['repo']
        self.assertEqual(repo.rid, repo_rid)

        self.fake_simple_log.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_log_with_url(self, fake_fetch_repos):
        conn = Mock()
        self.fake_simple_log.return_value = []

        repo_rid = 'repo-id'
        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, rid=repo_rid, name=repo_name, url=repo_url)

        args = self.log(repo_url)
        args.execute(conn, args)

        self.fake_simple_log.assert_called_once_with(conn, repo=fake_repo)

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_log_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_log.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.log('a_repo')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_log_url_error(self, _):
        repo_url = 'http://github.com/the_repo.git'

        args = self.log(repo_url)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stderr=f'No repository found with the URL "{repo_url}".\n')


class TestgCTSPull(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_pull = self.patch('sap.rest.gcts.simple.pull')

    def pull(self, *args, **kwargs):
        return parse_args('pull', *args, **kwargs)

    def test_pull_no_params(self):
        conn = Mock()
        repo_rid = 'repo-id'
        self.fake_simple_pull.return_value = {
            'fromCommit': '123',
            'toCommit': '456'
        }

        args = self.pull(repo_rid)
        args.execute(conn, args)

        repo = self.fake_simple_pull.call_args.kwargs['repo']
        self.assertEqual(repo.rid, repo_rid)

        self.fake_simple_pull.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console, stdout=f'''The repository "{repo_rid}" has been pulled
123 -> 456
''')

    def test_pull_no_from_commit(self):
        conn = Mock()
        repo_name = 'the_repo'
        self.fake_simple_pull.return_value = {
            'toCommit': '456'
        }

        args = self.pull(repo_name)
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''The repository "the_repo" has been pulled
New HEAD is 456
''')

    def test_pull_no_to_commit(self):
        conn = Mock()
        repo_name = 'the_repo'
        self.fake_simple_pull.return_value = {}

        args = self.pull(repo_name)
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''The repository "the_repo" has been pulled
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_pull_with_url(self, fake_fetch_repos):
        conn = Mock()
        self.fake_simple_pull.return_value = {
            'fromCommit': '123',
            'toCommit': '456'
        }

        repo_rid = 'repo-id'
        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, rid=repo_rid, name=repo_name, url=repo_url)

        args = self.pull(repo_url)
        args.execute(conn, args)

        self.fake_simple_pull.assert_called_once_with(conn, repo=fake_repo)

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_pull_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_pull.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.pull('a_repo')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_pull_url_error(self, _):
        repo_url = 'http://github.com/the_repo.git'

        args = self.pull(repo_url)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stderr=f'No repository found with the URL "{repo_url}".\n')

    def test_pull_json_output(self):
        self.fake_simple_pull.return_value = GCTS_RESPONSE_REPO_PULL_OK.json()

        args = self.pull('the_repo', '-f', 'JSON')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 0)

        self.assertConsoleContents(self.console, stdout='''{
  "fromCommit": "123",
  "toCommit": "456",
  "history": {
    "fromCommit": "123",
    "toCommit": "456",
    "type": "PULL"
  }
}
''')


class TestgCTSConfig(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_repository = self.patch('sap.cli.gcts.Repository')
        self.fake_instance = Mock()
        self.fake_repository.return_value = self.fake_instance
        self.fake_instance.get_config.return_value = None

    def config(self, *args, **kwargs):
        return parse_args('config', *args, **kwargs)

    def test_config_no_params_error(self):
        args = self.config('the_repo')
        args.execute(None, args)

        self.assertConsoleContents(self.console, stderr='''Invalid command line options
Run: sapcli gcts config --help
''')

    def test_config_params(self):
        conn = Mock()
        self.fake_instance.configuration = {
            'the_key_one': 'one',
            'the_key_two': 'two',
        }

        args = self.config('-l', 'the_repo')
        args.execute(conn, args)

        self.fake_repository.assert_called_once_with(conn, 'the_repo')
        self.assertConsoleContents(self.console, stdout='''the_key_one=one
the_key_two=two
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_config_with_url(self, fake_fetch_repos):
        conn = Mock()

        repo_rid = 'repo-id'
        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        repo_config = {
            'the_key_one': 'one',
            'the_key_two': 'two',
        }

        mock_repository(fake_fetch_repos, rid=repo_rid, name=repo_name, url=repo_url, configuration=repo_config)

        args = self.config('-l', repo_url)
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''the_key_one=one
the_key_two=two
''')

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_config_list_error(self, fake_dumper):
        messages = {'exception': 'test'}
        type(self.fake_instance).configuration = PropertyMock(side_effect=sap.rest.gcts.errors.GCTSRequestError(messages))

        args = self.config('a_repo', '-l')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    @patch('sap.cli.gcts.get_repository')
    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_config_request_error(self, fake_dumper, fake_get_repository):
        messages = {'exception': 'test'}
        fake_get_repository.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.config('a_repo', '-l')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(self.console, messages)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_config_url_error(self, _):
        repo_url = 'http://github.com/the_repo.git'

        args = self.config('-l', repo_url)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stderr=f'No repository found with the URL "{repo_url}".\n')

    def test_config_set(self):
        key = 'THE_KEY'
        old_value = 'the_old_value'
        value = 'the_value'
        self.fake_instance.get_config.return_value = old_value

        args = self.config('the_repo', key, value)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 0)

        self.fake_instance.get_config.assert_called_once_with(key)
        self.fake_instance.set_config.assert_called_once_with(key, value)
        self.assertConsoleContents(self.console, stdout=f'{key}={old_value} -> {value}\n')

    def test_config_set_key_not_in_config(self):
        key = 'THE_KEY'
        value = 'the_value'

        args = self.config('the_repo', key, value)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 0)

        self.fake_instance.get_config.assert_called_once_with(key)
        self.fake_instance.set_config.assert_called_once_with(key, value)
        self.assertConsoleContents(self.console, stdout=f'{key}={""} -> {value}\n')

    def test_config_set_no_value_error(self):
        args = self.config('the_repo', 'the_key')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.fake_instance.set_config.assert_not_called()
        self.assertConsoleContents(self.console, stderr='Cannot execute the set operation: "VALUE" was not provided.\n')

    def test_config_set_no_name_error(self):
        args = self.config('the_repo')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.fake_instance.set_config.assert_not_called()
        self.assertConsoleContents(self.console,
                                   stderr='Invalid command line options\nRun: sapcli gcts config --help\n')

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_config_set_request_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_instance.set_config.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.config('the_repo', 'the_key', 'the_value')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(self.console, messages)

    def test_config_unset(self):
        key = 'THE_KEY'
        old_value = 'the_old_value'
        self.fake_instance.get_config.return_value = old_value

        args = self.config('the_repo', key, '--unset')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 0)

        self.fake_instance.get_config.assert_called_once_with(key)
        self.fake_instance.delete_config.assert_called_once_with(key)
        self.assertConsoleContents(self.console, stdout=f'unset {key}={old_value}\n')

    def test_config_unset_key_not_in_config(self):
        key = 'THE_KEY'

        args = self.config('the_repo', key, '--unset')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 0)

        self.fake_instance.get_config.assert_called_once_with(key)
        self.fake_instance.delete_config.assert_called_once_with(key)
        self.assertConsoleContents(self.console, stdout=f'unset {key}={""}\n')

    def test_config_unset_no_name(self):
        args = self.config('the_repo', '--unset')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.fake_instance.delete_config.assert_not_called()
        self.assertConsoleContents(self.console,
                                   stderr='Invalid command line options\nRun: sapcli gcts config --help\n')

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_config_unset_request_error(self, fake_dumper):
        key = 'THE_KEY'
        messages = {'exception': 'test'}
        self.fake_instance.delete_config.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.config('the_repo', key, '--unset')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(self.console, messages)


class TestgCTSCommit(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = RESTConnection()

    def commit_cmd(self, *args, **kwargs):
        return parse_args('commit', *args, **kwargs)

    def test_commit_transport_full(self):
        repo_name = 'the_repo'
        corrnr = 'CORRNR'
        message = 'Message'
        description = 'Description'

        commit_cmd = self.commit_cmd(repo_name, corrnr, '-m', message, '--description', description)
        commit_cmd.execute(self.fake_connection, commit_cmd)

        self.fake_connection.execs[0].assertEqual(
            Request.post_json(
                uri=f'repository/{repo_name}/commit',
                body={
                    'message': message,
                    'autoPush': 'true',
                    'objects': [{'object': corrnr, 'type': 'TRANSPORT'}],
                    'description': description
                }
            ),
            self
        )

        self.assertConsoleContents(self.console, stdout=f'''The transport "{corrnr}" has been committed\n''')

    def test_commit_transport_short(self):
        repo_name = 'the_repo'
        corrnr = 'CORRNR'

        commit_cmd = self.commit_cmd(repo_name, corrnr)
        commit_cmd.execute(self.fake_connection, commit_cmd)

        self.fake_connection.execs[0].assertEqual(
            Request.post_json(
                uri=f'repository/{repo_name}/commit',
                body={
                    'message': f'Transport {corrnr}',
                    'autoPush': 'true',
                    'objects': [{'object': corrnr, 'type': 'TRANSPORT'}]
                }
            ),
            self
        )

        self.assertConsoleContents(self.console, stdout=f'''The transport "{corrnr}" has been committed\n''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_commit_with_url(self, fake_fetch_repos):
        repo_rid = 'repo-id'
        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        corrnr = 'CORRNR'

        fake_repo = mock_repository(fake_fetch_repos, rid=repo_rid, name=repo_name, url=repo_url)

        commit_cmd = self.commit_cmd(repo_url, corrnr)
        commit_cmd.execute(self.fake_connection, commit_cmd)

        fake_repo.commit_transport.assert_called_once()

    def test_commit_with_error(self):
        repo_name = 'the_repo'
        corrnr = 'CORRNR'

        self.fake_connection.set_responses(GCTS_RESPONSE_REPO_NOT_EXISTS)

        commit_cmd = self.commit_cmd(repo_name, corrnr)
        commit_cmd.execute(self.fake_connection, commit_cmd)

        self.assertConsoleContents(self.console, stderr=f'''Exception:\n  Repository does not exist\n''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_commit_url_error(self, _):
        repo_url = 'http://github.com/the_repo.git'
        corrnr = 'CORRNR'

        commit_cmd = self.commit_cmd(repo_url, corrnr)
        exit_code = commit_cmd.execute(None, commit_cmd)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stderr=f'No repository found with the URL "{repo_url}".\n')

    def test_commit_package_full(self):
        repo_name = 'the_repo'
        message = 'Message'
        description = 'Description'
        devc = 'PACKAGE'

        commit_cmd = self.commit_cmd(repo_name, '-m', message, '-d', devc, '--description', description)
        exit_code = commit_cmd.execute(self.fake_connection, commit_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_connection.execs[0].assertEqual(
            Request.post_json(
                uri=f'repository/{repo_name}/commit',
                body={
                    'message': message,
                    'autoPush': 'true',
                    'objects': [{'object': devc, 'type': 'FULL_PACKAGE'}],
                    'description': description
                }
            ),
            self
        )

        self.assertConsoleContents(self.console, stdout=f'''The package "{devc}" has been committed\n''')

    def test_commit_package_short(self):
        repo_name = 'the_repo'
        devc = repo_name.upper()

        commit_cmd = self.commit_cmd(repo_name)
        exit_code = commit_cmd.execute(self.fake_connection, commit_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_connection.execs[0].assertEqual(
            Request.post_json(
                uri=f'repository/{repo_name}/commit',
                body={
                    'message': f'Export package {devc}',
                    'autoPush': 'true',
                    'objects': [{'object': devc, 'type': 'FULL_PACKAGE'}]
                }
            ),
            self
        )


class TestgCTSRepoSetUrl(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = None

    def set_url_cmd(self, *args, **kwargs):
        return parse_args('repo', 'set-url', *args, **kwargs)

    @patch('sap.cli.gcts.Repository.set_url')
    def test_repo_set_url(self, fake_set_url):
        repo_name = 'the_repo'
        new_url = 'https://successful.test.org/fabulous/repo'

        the_cmd = self.set_url_cmd(repo_name, new_url)
        with self.assertWarns(DeprecationWarning):
            exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        fake_set_url.assert_called_once_with(new_url)

    @patch('sap.cli.gcts.Repository.set_url')
    def test_repo_set_url_error(self, fake_set_url):
        repo_name = 'the_repo'
        new_url = 'https://successful.test.org/fabulous/repo'

        fake_set_url.side_effect = sap.cli.gcts.SAPCliError('Cannot set new URL.')

        the_cmd = self.set_url_cmd(repo_name, new_url)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot set new URL.\n')


class TestgCTSRepoGetProperty(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()

        self.repo_rid = 'rid'
        self.repo_name = 'the name'
        self.repo_url = 'http://github.com/name.git'
        self.repo_data = {
            'rid': self.repo_rid,
            'name': self.repo_name,
            'branch': 'branch',
            'head': 'head',
            'status': 'status',
            'vsid': 'vsid',
            'role': 'role',
            'url': self.repo_url,
            'currentCommit': 'head'
        }

        self.fake_repo = sap.cli.gcts.Repository(self.fake_connection, self.repo_rid, data=self.repo_data)

    def get_properties_cmd(self, *args, **kwargs):
        return parse_args('repo', 'property', 'get', *args, **kwargs)

    @patch('sap.cli.gcts.get_repository')
    def test_get_properties(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.get_properties_cmd(self.repo_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.assertConsoleContents(self.console, stdout=f'''Name: {self.repo_name}
RID: {self.repo_rid}
Branch: branch
Commit: head
Status: status
vSID: vsid
Role: role
URL: {self.repo_url}
''')

    @patch('sap.cli.gcts.get_repository')
    def test_get_property_found(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        properties = [
            ('Name', f'{self.repo_name}\n'),
            ('RID', f'{self.repo_rid}\n'),
            ('Branch', 'branch\n'),
            ('Commit', 'head\n'),
            ('Status', 'status\n'),
            ('vSID', 'vsid\n'),
            ('Role', 'role\n'),
            ('URL', f'{self.repo_url}\n')
        ]

        for name, value in properties:
            the_cmd = self.get_properties_cmd(self.repo_name, name)
            exit_code = the_cmd.execute(self.fake_connection, the_cmd)

            self.assertEqual(exit_code, 0)
            self.assertConsoleContents(self.console, stdout=value)

            self.console.reset()

    @patch('sap.cli.gcts.get_repository')
    def test_get_property_nofound(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.get_properties_cmd(self.repo_name, 'Awesome_Success')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='The property was not found: Awesome_Success\n')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_get_properties_with_url(self, fake_fetch_repos):
        mock_repository(fake_fetch_repos, **self.repo_data)

        the_cmd = self.get_properties_cmd(self.repo_url)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.assertConsoleContents(self.console, stdout=f'''Name: {self.repo_name}
RID: {self.repo_rid}
Branch: branch
Commit: head
Status: status
vSID: vsid
Role: role
URL: {self.repo_url}
''')

    @patch('sap.cli.gcts.get_repository')
    def test_get_properties_error(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.get_properties_cmd(self.repo_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot get repository.\n')


class TestgCTSRepoSetProperty(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()
        self.fake_repo = Mock()

    def set_repository_cmd(self, *args, **kwargs):
        return parse_args('repo', 'property', 'set', *args, **kwargs)

    @patch('sap.cli.gcts.get_repository')
    def test_set_property(self, fake_get_repository):
        property_name = 'name'
        new_value = 'new_name'

        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.set_repository_cmd('the_repo', property_name, new_value)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.set_item.assert_called_once_with(property_name, new_value)

    @patch('sap.cli.gcts.get_repository')
    def test_set_property_bad_name(self, fake_get_repository):
        self.fake_repo.set_item.side_effect = sap.cli.gcts.SAPCliError('Incorrect property name.')
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.set_repository_cmd('the_repo', 'incorrect_property', 'value')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Incorrect property name.\n')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_set_property_with_url(self, fake_fetch_repos):
        repo_url = 'http://github.com/the_repo.git'
        property_name = 'name'
        new_value = 'new_name'

        fake_repo = mock_repository(fake_fetch_repos, url=repo_url)

        the_cmd = self.set_repository_cmd(repo_url, property_name, new_value)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        fake_repo.set_item.assert_called_once_with(property_name, new_value)

    @patch('sap.cli.gcts.get_repository')
    def test_set_property_with_url_error(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.set_repository_cmd('the_repo', 'property', 'value')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot get repository.\n')


class TestgCTSRepoActivities(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None
        self.patch_console(console=self.console)

        self.fake_connection = Mock()
        activities_data = [{
            'checkoutTime': 20220927091700,
            'caller': 'caller',
            'type': 'CLONE',
            'request': 'request',
            'fromCommit': '123',
            'toCommit': '456',
            'state': 'READY',
            'rc': 1,
        }]
        self.fake_repo = Mock()
        self.fake_repo.activities.return_value = activities_data

    def activities_cmd(self, *args, **kwargs):
        return parse_args('repo', 'activities', *args, **kwargs)

    def assert_query_params(self, expected_params):
        query_params = self.fake_repo.activities.call_args.args[0]
        self.assertEqual(query_params.get_params(), expected_params)

    @patch('sap.cli.gcts.get_repository')
    def test_activities_no_params(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.activities_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        self.fake_repo.activities.assert_called_once()

        expected_params = {'limit': '10', 'offset': '0'}
        self.assert_query_params(expected_params)

        self.assertConsoleContents(self.console, stdout='''Date                | Caller | Operation | Transport | From Commit | To Commit | State | Code
---------------------------------------------------------------------------------------------
2022-09-27 09:17:00 | caller | CLONE     | request   | 123         | 456       | READY | 1   
''')

    @patch('sap.cli.gcts.get_repository')
    def test_activities_format_json(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.activities_cmd('the_repo', '--format', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        expected_params = {'limit': '10', 'offset': '0'}
        self.assert_query_params(expected_params)

        self.assertConsoleContents(self.console, stdout="[{'checkoutTime': 20220927091700, 'caller': 'caller', 'type': 'CLONE',"
                                   " 'request': 'request', 'fromCommit': '123', 'toCommit': '456', 'state': 'READY',"
                                   " 'rc': 1}]\n")

    @patch('sap.cli.gcts.get_repository')
    def test_activities_all_query_params(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.activities_cmd('the_repo', '--limit', '15', '--offset', '10', '--fromcommit', '123',
                                      '--tocommit', '456', '--operation', 'CLONE')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)
        self.assertEqual(exit_code, 0)

        expected_params = {'limit': '15', 'offset': '10', 'fromCommit': '123', 'toCommit': '456', 'type': 'CLONE'}
        self.assert_query_params(expected_params)

    @patch('sys.stderr', new_callable=StringIO)
    def test_activities_incorrect_operation(self, mock_stderr):

        with self.assertRaises(SystemExit):
            the_cmd = self.activities_cmd('the_repo', '--operation', 'NOT_CLONE')

        self.assertIn("--operation: invalid choice: 'NOT_CLONE' (choose from", mock_stderr.getvalue())

    @patch('sap.cli.gcts.get_repository')
    def test_activities_repo_not_found(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.activities_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot get repository.\n')

    @patch('sap.cli.gcts.get_repository')
    def test_activities_request_error(self, fake_get_repository):
        self.fake_repo.activities.side_effect = sap.cli.gcts.GCTSRequestError({'exception': 'Request failed.'})
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.activities_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='''Exception:
  Request failed.
''')


class TestgCTSRepoCreateBranch(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None
        self.patch_console(console=self.console)

        self.branch_name = 'branch'
        self.fake_connection = Mock()
        self.fake_repo = Mock()
        self.expected_branch = {'name': self.branch_name, 'type': 'active', 'isSymbolic': False, 'isPeeled': False,
                                'ref': f'refs/heads/{self.branch_name}'}
        self.fake_repo.create_branch.return_value = self.expected_branch

    def create_branch_cmd(self, *args, **kwargs):
        return parse_args('repo', 'branch', 'create', *args, **kwargs)

    @patch('sap.cli.gcts.get_repository')
    def test_create_branch(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.create_branch_cmd('the_repo', self.branch_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.create_branch.assert_called_once_with(self.branch_name, symbolic=False, peeled=False,
                                                             local_only=False)
        self.assertConsoleContents(self.console,
                                   stdout=f'Branch "{self.branch_name}" was created and now is active branch.\n')

    @patch('sap.cli.gcts.get_repository')
    def test_create_branch_json(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.create_branch_cmd('the_repo', self.branch_name, '-f', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.create_branch.assert_called_once_with(self.branch_name, symbolic=False, peeled=False,
                                                             local_only=False)
        self.assertConsoleContents(self.console, stdout=f'{json.dumps(self.expected_branch, indent=2)}\n')

    @patch('sap.cli.gcts.get_repository')
    def test_create_branch_all_params(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.create_branch_cmd('the_repo', self.branch_name, '--local-only', '--peeled', '--symbolic')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.create_branch.assert_called_once_with(self.branch_name, symbolic=True, peeled=True,
                                                             local_only=True)

    @patch('sap.cli.gcts.get_repository')
    def test_create_branch_request_error(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo
        self.fake_repo.create_branch.side_effect = sap.cli.gcts.GCTSRequestError({'exception': 'Request failed.'})

        the_cmd = self.create_branch_cmd('the_repo', self.branch_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_repo.create_branch.assert_called_once_with(self.branch_name, symbolic=False, peeled=False,
                                                             local_only=False)
        self.assertConsoleContents(self.console, stderr='''Exception:
  Request failed.
''')

    @patch('sap.cli.gcts.get_repository')
    def test_create_branch_repo_not_found(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.create_branch_cmd('the_repo', self.branch_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot get repository.\n')


class TestgCTSRepoDeleteBranch(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None
        self.patch_console(console=self.console)

        self.branch_name = 'branch'
        self.fake_connection = Mock()
        self.fake_repo = Mock()
        self.fake_repo.delete_branch.return_value = {}

    def delete_branch_cmd(self, *args, **kwargs):
        return parse_args('repo', 'branch', 'delete', *args, **kwargs)

    @patch('sap.cli.gcts.get_repository')
    def test_delete_branch(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.delete_branch_cmd('the_repo', self.branch_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.delete_branch.assert_called_once_with(self.branch_name)
        self.assertConsoleContents(self.console, stdout=f'Branch "{self.branch_name}" was deleted.\n')

    @patch('sap.cli.gcts.get_repository')
    def test_delete_branch_json(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.delete_branch_cmd('the_repo', self.branch_name, '-f', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.delete_branch.assert_called_once_with(self.branch_name)
        self.assertConsoleContents(self.console, stdout='{}\n')

    @patch('sap.cli.gcts.get_repository')
    def test_delete_branch_request_error(self, fake_get_repository):
        self.fake_repo.delete_branch.side_effect = sap.cli.gcts.GCTSRequestError({'exception': 'Request failed.'})
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.delete_branch_cmd('the_repo', self.branch_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_repo.delete_branch.assert_called_once_with(self.branch_name)
        self.assertConsoleContents(self.console, stderr='''Exception:
  Request failed.
''')

    @patch('sap.cli.gcts.get_repository')
    def test_delete_branch_repo_not_found(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.delete_branch_cmd('the_repo', self.branch_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot get repository.\n')


class TestgCTSRepoListBranches(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None
        self.patch_console(console=self.console)

        self.branches = [{'name': 'branch1', 'type': 'active', 'isSymbolic': False, 'isPeeled': False,
                         'ref': 'refs/heads/branch1'},
                         {'name': 'branch1', 'type': 'local', 'isSymbolic': False, 'isPeeled': False,
                         'ref': 'refs/heads/branch1'},
                         {'name': 'branch1', 'type': 'remote', 'isSymbolic': False, 'isPeeled': False,
                         'ref': 'refs/remotes/origin/branch1'}]
        self.fake_connection = Mock()
        self.fake_repo = Mock()
        self.fake_repo.list_branches.return_value = self.branches

    def list_branches_cmd(self, *args, **kwargs):
        return parse_args('repo', 'branch', 'list', *args, **kwargs)

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.list_branches_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.list_branches.assert_called_once()
        self.assertConsoleContents(self.console, stdout='''Name     | Type  | Symbolic | Peeled | Reference         
---------------------------------------------------------
branch1* | local | False    | False  | refs/heads/branch1
''')

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches_only_remote(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.list_branches_cmd('the_repo', '-r')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.list_branches.assert_called_once()
        self.assertConsoleContents(self.console, stdout='''Name    | Type   | Symbolic | Peeled | Reference                  
------------------------------------------------------------------
branch1 | remote | False    | False  | refs/remotes/origin/branch1
''')

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches_all(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.list_branches_cmd('the_repo', '-a')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.list_branches.assert_called_once()
        self.assertConsoleContents(self.console, stdout='''Name     | Type   | Symbolic | Peeled | Reference                  
-------------------------------------------------------------------
branch1* | local  | False    | False  | refs/heads/branch1         
branch1  | remote | False    | False  | refs/remotes/origin/branch1
''')

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches_json(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.list_branches_cmd('the_repo', '-f', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.list_branches.assert_called_once()
        self.assertConsoleContents(
            self.console,
            stdout='{}\n'.format(json.dumps([branch for branch in self.branches if branch['type'] == 'local'],
                                            indent=2))
        )

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches_json_only_remote(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.list_branches_cmd('the_repo', '-f', 'JSON', '-r')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.list_branches.assert_called_once()
        self.assertConsoleContents(
            self.console,
            stdout='{}\n'.format(json.dumps([branch for branch in self.branches if branch['type'] == 'remote'],
                                            indent=2))
        )

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches_json_all(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.list_branches_cmd('the_repo', '-f', 'JSON', '-a')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.list_branches.assert_called_once()
        self.assertConsoleContents(
            self.console,
            stdout='{}\n'.format(json.dumps(self.branches, indent=2))
        )

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches_request_error(self, fake_get_repository):
        self.fake_repo.list_branches.side_effect = sap.cli.gcts.GCTSRequestError({'exception': 'Request failed.'})
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.list_branches_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_repo.list_branches.assert_called_once()
        self.assertConsoleContents(self.console, stderr='''Exception:
  Request failed.
''')

    @patch('sap.cli.gcts.get_repository')
    def test_list_branches_repo_not_found(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.list_branches_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr='Cannot get repository.\n')


class TestqCTSUserGetCredentials(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = None
        self.api_url = 'https://api.github.com/v3/'
        self.fake_get_credentials = self.patch('sap.rest.gcts.simple.get_user_credentials')
        self.fake_get_credentials.return_value = [{'endpoint': self.api_url, 'type': 'token', 'state': 'false'}]

    def get_credentials_cmd(self, *args, **kwargs):
        return parse_args('user', 'get-credentials', *args, **kwargs)

    def test_get_user_credentials_json(self):
        output_format = 'JSON'

        the_cmd = self.get_credentials_cmd('-f', output_format)
        the_cmd.execute(self.fake_connection, the_cmd)

        self.assertConsoleContents(self.console,
                                   stdout=f"[{{'endpoint': '{self.api_url}', 'type': 'token', 'state': 'false'}}]\n")

    def test_get_user_credentials_human(self):
        output_format = 'HUMAN'

        the_cmd = self.get_credentials_cmd('-f', output_format)
        the_cmd.execute(self.fake_get_credentials, the_cmd)

        self.assertConsoleContents(
            self.console,
            stdout=(
                "Endpoint                   | Type  | State\n"
                "------------------------------------------\n"
                f"{self.api_url} | token | false\n"
            )
        )

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_get_user_credentials_request_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_get_credentials.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        the_cmd = self.get_credentials_cmd()
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        fake_dumper.assert_called_once_with(self.console, messages)


class TestgCTSUserSetCredentials(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = None

    def set_credentials_cmd(self, *args, **kwargs):
        return parse_args('user', 'set-credentials', *args, **kwargs)

    @patch('sap.rest.gcts.simple.set_user_api_token')
    def test_repo_set_url(self, fake_set_credentials):
        api_url = 'https://api.github.com/v3/'
        token = 'ATOKEN'

        the_cmd = self.set_credentials_cmd("-a", api_url, "-t", token)
        the_cmd.execute(self.fake_connection, the_cmd)

        fake_set_credentials.assert_called_once_with(self.fake_connection, api_url, token)

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    @patch('sap.rest.gcts.simple.set_user_api_token')
    def test_set_user_credentials_request_error(self, fake_set_credentials, fake_dumper):
        messages = {'exception': 'test'}
        fake_set_credentials.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        the_cmd = self.set_credentials_cmd('-a', 'the_url')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        fake_dumper.assert_called_once_with(self.console, messages)


class TestgCTSUserDeleteCredentials(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = None

    def delete_credentials_cmd(self, *args, **kwargs):
        return parse_args('user', 'delete-credentials', *args, **kwargs)

    @patch('sap.rest.gcts.simple.delete_user_credentials')
    def test_delete_user_credentials(self, fake_delete_credentials):
        api_url = 'https://api.github.com/v3/'

        the_cmd = self.delete_credentials_cmd('-a', api_url)
        the_cmd.execute(self.fake_connection, the_cmd)

        fake_delete_credentials.asser_called_once_with(self.fake_connection, api_url)

    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    @patch('sap.rest.gcts.simple.delete_user_credentials')
    def test_delete_user_credentials_request_error(self, fake_delete_credentials, fake_dumper):
        messages = {'exception': 'test'}
        fake_delete_credentials.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        the_cmd = self.delete_credentials_cmd('-a', 'the_url')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        fake_dumper.assert_called_once_with(self.console, messages)


class TestgCTSGetSystemConfigProperty(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()

        self.config_key = 'THE_KEY'
        self.config_value = 'the_value'
        self.expected_property = {'key': self.config_key, 'value': self.config_value}

        self.fake_get_config_property = self.patch('sap.rest.gcts.simple.get_system_config_property')
        self.fake_get_config_property.return_value = self.expected_property

    def get_config_property_cmd(self, *args, **kwargs):
        return parse_args('system', 'config', 'get', *args, **kwargs)

    def test_get_system_config_property(self):
        the_cmd = self.get_config_property_cmd(self.config_key)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_get_config_property.assert_called_once_with(self.fake_connection, self.config_key)
        self.assertConsoleContents(self.console, stdout=f'''Key: {self.config_key}
Value: {self.config_value}
''')

    def test_get_system_config_property_json(self):
        the_cmd = self.get_config_property_cmd(self.config_key, '-f', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_get_config_property.assert_called_once_with(self.fake_connection, self.config_key)
        self.assertConsoleContents(self.console,
                                   stdout='{}\n'.format(json.dumps(self.expected_property, indent=2)))

    def test_get_system_config_property_request_error(self):
        self.fake_get_config_property.side_effect = sap.cli.gcts.SAPCliError('Request error')

        the_cmd = self.get_config_property_cmd(self.config_key)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_get_config_property.assert_called_once_with(self.fake_connection, self.config_key)
        self.assertConsoleContents(self.console, stderr='Request error\n')


class TestgCTSListSystemConfig(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()

        self.expected_config = [
            {'key': 'THE_KEY1', 'value': 'the_value1', 'category': 'SYSTEM', 'changedAt': 2022, 'changedBy': 'Test'},
            {'key': 'THE_KEY2', 'value': 'the_value2', 'category': 'SYSTEM', 'changedAt': 2022, 'changedBy': 'Test'}
        ]
        self.fake_list_system_config = self.patch('sap.rest.gcts.simple.list_system_config')
        self.fake_list_system_config.return_value = self.expected_config

    def list_system_config_cmd(self, *args, **kwargs):
        return parse_args('system', 'config', 'list', *args, **kwargs)

    def test_list_system_config(self):
        the_cmd = self.list_system_config_cmd()
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_list_system_config.assert_called_once_with(self.fake_connection)
        self.assertConsoleContents(self.console, stdout='''Key      | Value      | Category | Changed At | Changed By
----------------------------------------------------------
THE_KEY1 | the_value1 | SYSTEM   | 2022       | Test      
THE_KEY2 | the_value2 | SYSTEM   | 2022       | Test      
''')

    def test_list_system_config_json(self):
        the_cmd = self.list_system_config_cmd('-f', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_list_system_config.assert_called_once_with(self.fake_connection)
        self.assertConsoleContents(self.console,
                                   stdout='{}\n'.format(json.dumps(self.expected_config, indent=2)))

    def test_list_system_config_request_error(self):
        self.fake_list_system_config.side_effect = sap.cli.gcts.SAPCliError('Request error')

        the_cmd = self.list_system_config_cmd()
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_list_system_config.assert_called_once_with(self.fake_connection)
        self.assertConsoleContents(self.console, stderr='Request error\n')


class TestgCTSSetSystemConfigProperty(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()

        self.config_key = 'THE_KEY'
        self.config_value = 'the_value'
        self.expected_property = {'key': self.config_key, 'value': self.config_value}

        self.fake_set_config_property = self.patch('sap.rest.gcts.simple.set_system_config_property')
        self.fake_set_config_property.return_value = self.expected_property

    def set_config_property_cmd(self, *args, **kwargs):
        return parse_args('system', 'config', 'set', *args, **kwargs)

    def test_set_system_config_property(self):
        the_cmd = self.set_config_property_cmd(self.config_key, self.config_value)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_set_config_property.assert_called_once_with(self.fake_connection, self.config_key, self.config_value)
        self.assertConsoleContents(self.console, stdout=f'''Key: {self.config_key}
Value: {self.config_value}
''')

    def test_set_system_config_json(self):
        the_cmd = self.set_config_property_cmd(self.config_key, self.config_value, '-f', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_set_config_property.assert_called_once_with(self.fake_connection, self.config_key, self.config_value)
        self.assertConsoleContents(self.console,
                                   stdout='{}\n'.format(json.dumps(self.expected_property, indent=2)))

    def test_set_system_config_request_error(self):
        self.fake_set_config_property.side_effect = sap.cli.gcts.SAPCliError('Request error')

        the_cmd = self.set_config_property_cmd(self.config_key, self.config_value)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_set_config_property.assert_called_once_with(self.fake_connection, self.config_key, self.config_value)
        self.assertConsoleContents(self.console, stderr='Request error\n')


class TestgCTSDeleteSystemConfigProperty(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()

        self.config_key = 'THE_KEY'
        self.fake_delete_config_property = self.patch('sap.rest.gcts.simple.delete_system_config_property')
        self.fake_delete_config_property.return_value = {}

    def delete_config_property_cmd(self, *args, **kwargs):
        return parse_args('system', 'config', 'unset', *args, **kwargs)

    def test_delete_system_config_property(self):
        the_cmd = self.delete_config_property_cmd(self.config_key)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_delete_config_property.assert_called_once_with(self.fake_connection, self.config_key)
        self.assertConsoleContents(self.console, stdout=f'Config property "{self.config_key}" was unset.\n')

    def test_delete_system_config_property_json(self):
        the_cmd = self.delete_config_property_cmd(self.config_key, '-f', 'JSON')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_delete_config_property.assert_called_once_with(self.fake_connection, self.config_key)
        self.assertConsoleContents(self.console, stdout='{}\n')

    def test_delete_system_config_property_request_error(self):
        self.fake_delete_config_property.side_effect = sap.cli.gcts.SAPCliError('Request error')

        the_cmd = self.delete_config_property_cmd(self.config_key)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_delete_config_property.assert_called_once_with(self.fake_connection, self.config_key)
        self.assertConsoleContents(self.console, stderr='Request error\n')


class TestgCTSConsoleSugarOperationProgress(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)

    def test_progress_handle_update(self):
        progress = sap.cli.gcts.ConsoleSugarOperationProgress(self.console)
        progress.update('My message')

        self.assertConsoleContents(self.console, stdout='My message\n')

    def test_progress_handle_update_with_pid_and_recover_message(self):
        progress = sap.cli.gcts.ConsoleSugarOperationProgress(self.console)
        progress.update('My message', recover_message='Recover message', pid='test-pid-123')

        self.assertConsoleContents(self.console, stdout='My message\n')
        self.assertEqual(progress._recover_messages.get('test-pid-123'), 'Recover message')

    def test_progress_recover_notification(self):
        progress = sap.cli.gcts.ConsoleSugarOperationProgress(self.console)
        progress.update('My message', recover_message='Recover message', pid='test-pid-123')
        progress.process_recover_notification()

        self.assertConsoleContents(self.console, stdout='My message\n', stderr='Recover message\n')
        self.assertEqual(progress._recover_messages.get('test-pid-123'), 'Recover message')

    def test_progress_clear_recover_message(self):
        progress = sap.cli.gcts.ConsoleSugarOperationProgress(self.console)
        progress.update('My message', recover_message='Recover message', pid='test-pid-123')

        self.assertEqual(progress._recover_messages.get('test-pid-123'), 'Recover message')

        del progress._recover_messages['test-pid-123']

        self.assertIsNone(progress._recover_messages.get('test-pid-123'))


class TestgCTSUpdateFilesystem(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()

        progress_patcher = patch('sap.cli.gcts.ConsoleSugarOperationProgress._handle_updated')
        self.addCleanup(progress_patcher.stop)
        progress_patcher.start()

        self.from_commit = 'fromCommit'
        self.to_commit = 'toCommit'
        self.pull_response = {
            'fromCommit': self.from_commit,
            'toCommit': self.to_commit
        }
        self.fake_repo = Mock()
        self.fake_repo.pull.return_value = self.pull_response

        self.fake_get_repository_patcher = patch('sap.cli.gcts.get_repository')
        self.addCleanup(self.fake_get_repository_patcher.stop)
        self.fake_get_repository = self.fake_get_repository_patcher.start()
        self.fake_get_repository.return_value = self.fake_repo

    def update_filesystem_cmd(self, *args, **kwargs):
        return parse_args('repo', 'branch', 'update_filesystem', *args, **kwargs)

    @patch('sap.cli.gcts.temporary_switched_branch')
    @patch('sap.cli.gcts.abap_modifications_disabled')
    def test_update_filesystem(self, fake_abap_mod_disabled, fake_temp_switched_branch):
        repo_name = 'the_repo'
        branch = 'the_branch'

        the_cmd = self.update_filesystem_cmd(repo_name, branch)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.pull.assert_called_once()
        self.assertConsoleContents(
            self.console,
            stdout=f'Updating the currently active branch {branch} ...\n'
            f'The branch "{branch}" has been updated: {self.from_commit} -> {self.to_commit}\n'
        )
        fake_abap_mod_disabled.assert_called_once()
        fake_temp_switched_branch.assert_called_once()

    def test_update_filesystem_output_to_file(self):
        repo_name = 'the_repo'
        branch = 'the_branch'
        output_file = 'file'

        with patch('sap.cli.gcts.os.path.exists', return_value=False):
            with patch('builtins.open', mock_open()) as fake_open:
                the_cmd = self.update_filesystem_cmd(repo_name, branch, '-o', output_file)
                exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        fake_open().write.assert_called_once_with(sap.cli.core.json_dumps(self.pull_response))
        self.assertEqual(exit_code, 0)
        self.assertConsoleContents(
            self.console,
            stdout=f'Updating the currently active branch {branch} ...\n'
            f'The branch "{branch}" has been updated: {self.from_commit} -> {self.to_commit}\n'
            f'Writing gCTS JSON response to {output_file} ...\n'
            f'Successfully wrote gCTS JSON response to {output_file}\n'
        )

    def test_update_filesystem_output_to_existing_file(self):
        repo_name = 'the_repo'
        branch = 'the_branch'
        output_file = 'file'

        with patch('sap.cli.gcts.os.path.exists', return_value=True):
            the_cmd = self.update_filesystem_cmd(repo_name, branch, '-o', output_file)
            exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr=f'Output file must not exist: {output_file}\n')

    def test_update_filesystem_output_to_file_no_pull_response(self):
        self.fake_repo.pull.return_value = {}
        repo_name = 'the_repo'
        branch = 'the_branch'

        with patch('sap.cli.gcts.os.path.exists', return_value=False):
            the_cmd = self.update_filesystem_cmd(repo_name, branch, '-o', 'file')
            exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.fake_repo.pull.assert_called_once()
        self.assertConsoleContents(
            self.console,
            stdout=f'Updating the currently active branch {branch} ...\n'
            f'The branch "{branch}" has been updated: () -> ()\n'
        )

    def test_update_filesystem_abap_mod_disabled_error(self):
        self.fake_repo.get_config.return_value = None
        gcts_messages = {'exception': 'Delete config error.'}
        self.fake_repo.delete_config.side_effect = sap.cli.gcts.GCTSRequestError(gcts_messages)
        repo_name = 'the_repo'
        branch = 'the_branch'

        the_cmd = self.update_filesystem_cmd(repo_name, branch)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(
            self.console,
            stdout=f'Updating the currently active branch {branch} ...\n'
            f'The branch "{branch}" has been updated: {self.from_commit} -> {self.to_commit}\n',
            stderr='Exception:\n  Delete config error.\n'
                   'Please delete the configuration option VCS_NO_IMPORT manually\n'
        )

    def test_update_filesystem_temp_switched_branch_error(self):
        self.fake_repo.branch = 'old_branch'
        gcts_messages = {'exception': 'Checkout error.'}
        self.fake_repo.checkout.side_effect = sap.cli.gcts.GCTSRequestError(gcts_messages)
        repo_name = 'the_repo'
        branch = 'the_branch'

        the_cmd = self.update_filesystem_cmd(repo_name, branch)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_repo.pull.assert_not_called()
        self.assertConsoleContents(
            self.console,
            stderr='Exception:\n  Checkout error.\n'
                   'Please double check if the original branch old_branch is active\n'
        )

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_update_filesystem_repo_pull_error(self, fake_dump_msgs):
        old_branch = 'old_branch'
        self.fake_repo.branch = old_branch
        gcts_messages = {'log': 'Pull error.'}
        self.fake_repo.pull.side_effect = sap.cli.gcts.GCTSRequestError(gcts_messages)
        self.fake_repo.get_config.return_value = None
        repo_name = 'the_repo'
        branch = 'the_branch'

        the_cmd = self.update_filesystem_cmd(repo_name, branch)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_repo.pull.assert_called_once()
        fake_dump_msgs.assert_called_once_with(self.console, gcts_messages)
        self.fake_repo.checkout.assert_has_calls([call(branch), call(old_branch)])
        self.fake_repo.set_config.assert_called_once_with('VCS_NO_IMPORT', 'X')
        self.fake_repo.delete_config.assert_called_once_with('VCS_NO_IMPORT')
        self.assertConsoleContents(
            self.console,
            stdout=f'Updating the currently active branch {branch} ...\n',
        )

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_update_filesystem_url(self, fake_fetch_repos):
        self.fake_get_repository_patcher.stop()
        repo_rid = 'repo-id'
        repo_name = 'the_repo'
        branch = 'the_branch'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, rid=repo_rid, name=repo_name, url=repo_url, **self.fake_repo.__dict__)

        the_cmd = self.update_filesystem_cmd(repo_url, branch)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        fake_repo.pull.assert_called_once()
        self.assertConsoleContents(
            self.console,
            stdout=f'Updating the currently active branch {branch} ...\n'
            f'The branch "{branch}" has been updated: {self.from_commit} -> {self.to_commit}\n'
        )

    def test_update_filesystem_repo_not_found(self):
        self.fake_get_repository.side_effect = sap.cli.core.SAPCliError('Repo not found.')
        repo_name = 'the_repo'
        branch = 'the_branch'

        the_cmd = self.update_filesystem_cmd(repo_name, branch)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.fake_repo.pull.assert_not_called()
        self.assertConsoleContents(
            self.console,
            stderr='Repo not found.\n'
        )


class TestgCTSSetRole(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        self.connection = Mock()
        self.fake_repository = Mock()
        self.repo_rid = 'my-repo'

    def repo(self, *args, **kwargs):
        args = parse_args('repo', *args, **kwargs)
        with patch('sap.cli.gcts.get_repository', return_value=self.fake_repository) as fake_get_repository:
            exit_code = args.execute(self.connection, args)
            fake_get_repository.assert_called_once_with(self.connection, self.repo_rid)
        return exit_code

    def set_role_target(self, *args, **kwargs):
        return self.repo('set-role-target', *args, **kwargs)

    def set_role_source(self, *args, **kwargs):
        return self.repo('set-role-source', *args, **kwargs)

    def test_set_role_target(self):
        exit_code = self.set_role_target(self.repo_rid)
        self.fake_repository.set_role.assert_called_once_with('TARGET')
        self.assertEqual(exit_code, 0)

    def test_set_role_source(self):
        exit_code = self.set_role_source(self.repo_rid)
        self.fake_repository.set_role.assert_called_once_with('SOURCE')
        self.assertEqual(exit_code, 0)


class TestgCTSRepoObjects(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = None
        self.fake_repo = Mock()
        self.fake_repo.objects.return_value = [
            {'pgmid': 'R3TR', 'type': 'FUGR', 'object': 'OBJECT1', 'description': 'DESCRIPTION1'},
            {'pgmid': 'R3TR', 'type': 'DEVC', 'object': 'OBJECT2', 'description': 'DESCRIPTION2'},
            {'pgmid': 'R3TR', 'type': 'SUSH', 'object': 'OBJECT3', 'description': 'DESCRIPTION3'},
        ]

    def repo_objects_cmd(self, *args, **kwargs):
        return parse_args('repo', 'objects', *args, **kwargs)

    @patch('sap.cli.gcts.get_repository')
    @patch('sap.cli.helpers.TableWriter')
    def test_repo_objects_with_default_format_human(self, fake_table_writer, fake_get_repository):
        package = 'test_package'
        fake_get_repository.return_value = self.fake_repo
        mock_columns_instance = Mock()
        mock_columns_class = Mock(return_value=mock_columns_instance)
        fake_table_writer.Columns = mock_columns_class
        mock_columns_instance.return_value = mock_columns_instance
        mock_columns_instance.done.return_value = [
            ('pgmid', 'Program'),
            ('type', 'Type'),
            ('object', 'Name')
        ]
        mock_table_writer_instance = Mock()
        fake_table_writer.return_value = mock_table_writer_instance

        objects_list_cmd = self.repo_objects_cmd(package)
        objects_list_exit_code = objects_list_cmd.execute(self.fake_connection, objects_list_cmd)

        self.assertEqual(objects_list_exit_code, 0)
        fake_get_repository.assert_called_once_with(self.fake_connection, package)
        self.fake_repo.objects.assert_called_once()
        mock_columns_class.assert_called_once()
        # TW columns setup check
        self.assertEqual(mock_columns_instance.call_count, 3)
        expected_calls = [
            call('pgmid', 'Program'),
            call('type', 'Type'),
            call('object', 'Name')
        ]
        mock_columns_instance.assert_has_calls(expected_calls)
        mock_columns_instance.done.assert_called_once()
        # TW instance setup check
        fake_table_writer.assert_called_once_with(
            self.fake_repo.objects.return_value, 
            mock_columns_instance.done.return_value, 
            display_header=True, 
            visible_columns=None
        )
        mock_table_writer_instance.printout.assert_called_once_with(self.console)

    @patch('sap.cli.gcts.get_repository')
    @patch('sap.cli.helpers.TableWriter')
    def test_repo_objects_with_human_format_columsns_noheadings(self, fake_table_writer, fake_get_repository):
        package = 'test_package'
        fake_get_repository.return_value = self.fake_repo
        mock_columns_instance = Mock()
        mock_columns_class = Mock(return_value=mock_columns_instance)
        fake_table_writer.Columns = mock_columns_class
        mock_columns_instance.return_value = mock_columns_instance
        mock_columns_instance.done.return_value = [
            ('pgmid', 'Program'),
            ('type', 'Type'),
            ('object', 'Name')
        ]
        mock_table_writer_instance = Mock()
        fake_table_writer.return_value = mock_table_writer_instance

        objects_list_cmd = self.repo_objects_cmd(package, '-f', 'HUMAN', '--noheadings', '--columns', 'pgmid,type')
        objects_list_exit_code = objects_list_cmd.execute(self.fake_connection, objects_list_cmd)

        self.assertEqual(objects_list_exit_code, 0)
        fake_get_repository.assert_called_once_with(self.fake_connection, package)
        self.fake_repo.objects.assert_called_once()
        mock_columns_class.assert_called_once()
        self.assertEqual(mock_columns_instance.call_count, 3)
        expected_calls = [
            call('pgmid', 'Program'),
            call('type', 'Type'),
            call('object', 'Name')
        ]
        mock_columns_instance.assert_has_calls(expected_calls)
        mock_columns_instance.done.assert_called_once()
        fake_table_writer.assert_called_once_with(
            self.fake_repo.objects.return_value,
            mock_columns_instance.done.return_value,
            display_header=False,
            visible_columns=['pgmid', 'type']
        )
        mock_table_writer_instance.printout.assert_called_once_with(self.console)

    @patch('sap.cli.gcts.get_repository')
    def test_repo_objects_with_json_format(self, fake_get_repository):
        package = 'test_package'
        fake_get_repository.return_value = self.fake_repo

        objects_list_cmd = self.repo_objects_cmd(package, '-f', 'JSON')
        objects_list_exit_code = objects_list_cmd.execute(self.fake_connection, objects_list_cmd)

        self.assertEqual(objects_list_exit_code, 0)
        fake_get_repository.assert_called_once_with(self.fake_connection, package)
        self.fake_repo.objects.assert_called_once()
        self.assertConsoleContents(self.console, stdout=sap.cli.core.json_dumps(self.fake_repo.objects.return_value) + '\n')

    @patch('sap.cli.gcts.get_repository')
    def test_repo_objects_with_transport_format(self, fake_get_repository):
        package = 'test_package'
        fake_get_repository.return_value = self.fake_repo

        objects_list_cmd = self.repo_objects_cmd(package, '-f', 'TRANSPORT')
        objects_list_exit_code = objects_list_cmd.execute(self.fake_connection, objects_list_cmd)

        self.assertEqual(objects_list_exit_code, 0)
        fake_get_repository.assert_called_once_with(self.fake_connection, package)
        self.fake_repo.objects.assert_called_once()
        self.assertConsoleContents(self.console, stdout='R3TR\tFUGR\tOBJECT1\nR3TR\tDEVC\tOBJECT2\nR3TR\tSUSH\tOBJECT3\n')

    @patch('sap.cli.gcts.get_repository')
    @patch('sap.cli.gcts_utils.dump_gcts_messages')
    def test_repo_objects_request_error(self, fake_dump_msgs, fake_get_repository):
        package = 'test_package'
        messages = {'exception': 'Request error.'}
        fake_get_repository.return_value = self.fake_repo
        self.fake_repo.objects.side_effect = sap.cli.gcts.GCTSRequestError(messages)
        objects_list_cmd = self.repo_objects_cmd(package)
        objects_list_exit_code = objects_list_cmd.execute(self.fake_connection, objects_list_cmd)

        self.assertEqual(objects_list_exit_code, 1)
        fake_get_repository.assert_called_once_with(self.fake_connection, package)
        fake_dump_msgs.assert_called_once_with(self.console, messages)
        
