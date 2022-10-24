#!/usr/bin/env python3

from io import StringIO
import unittest
import json
from unittest.mock import MagicMock, patch, Mock, PropertyMock

import sap.cli.gcts

from mock import (
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
        sap.cli.gcts.dump_gcts_messages(self.console, messages)
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
        sap.cli.gcts.dump_gcts_messages(self.console, {'random': 'error'})
        self.assertConsoleContents(self.console, stderr='''{'random': 'error'}
''')

    def test_dump_only_error_log(self):
        sap.cli.gcts.dump_gcts_messages(self.console, {'errorLog': ['error']})
        self.assertConsoleContents(self.console, stderr='''Error Log:
  error
''')

    def test_dump_only_log(self):
        sap.cli.gcts.dump_gcts_messages(self.console, {'log': ['error']})
        self.assertConsoleContents(self.console, stderr='''Log:
  error
''')

    def test_dump_only_exception(self):
        sap.cli.gcts.dump_gcts_messages(self.console, {'exception': 'error'})
        self.assertConsoleContents(self.console, stderr='''Exception:
  error
''')


class TestgCTSGetRepository(PatcherTestCase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.connection = Mock()
        self.fake_fetch_repos = self.patch('sap.rest.gcts.simple.fetch_repos')

    def test_get_repository_name(self):
        repo_name = 'the_repo'
        repo = sap.cli.gcts.get_repository(self.connection, repo_name)

        self.assertEqual(repo.name, repo_name)
        self.fake_fetch_repos.assert_not_called()

    def test_get_repository_url(self):
        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'

        fake_repo = mock_repository(self.fake_fetch_repos, name=repo_name, url=repo_url)
        repo = sap.cli.gcts.get_repository(self.connection, repo_url)

        self.assertEqual(repo, fake_repo)
        self.fake_fetch_repos.assert_called_once_with(self.connection)
        repo.wipe_data.assert_called_once()

    def test_get_repository_url_https(self):
        repo_name = 'the_repo'
        repo_url = 'https://github.com/the_repo.git'

        fake_repo = mock_repository(self.fake_fetch_repos, name=repo_name, url=repo_url)
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


class TestgCTSClone(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_clone = self.patch('sap.rest.gcts.simple.clone')

        self.conn = Mock()
        self.fake_simple_clone.return_value = sap.rest.gcts.remote_repo.Repository(self.conn, 'sample', data={
            'url': 'https://example.org/repo/git/sample.git',
            'branch': 'main',
            'currentCommit': 'FEDBCA9876543210'
        })

    def clone(self, *args, **kwargs):
        return parse_args('clone', *args, **kwargs)

    def test_clone_with_url_only(self):
        args = self.clone('https://example.org/repo/git/sample.git')

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
            role='SOURCE'
        )

        self.assertConsoleContents(console=self.console, stdout='''Cloned repository:
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
            '--type', 'GIT'
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
            role='TARGET'
        )

    def test_clone_existing(self):
        repo_url = 'https://example.org/repo/git/sample.git'
        args = self.clone(repo_url, '--no-fail-exists')

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
            role='SOURCE'
        )

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_clone_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_clone.return_value = None
        self.fake_simple_clone.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.clone('url')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)


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
            sap.rest.gcts.remote_repo.Repository(conn, 'one', data={
                'rid': 'one_rid',
                'status': 'CREATED',
                'branch': 'one_branch',
                'url': 'one_url',
                'vsid': 'vS1D',
                'currentCommit': '123'}),
            sap.rest.gcts.remote_repo.Repository(conn, 'two', data={
                'rid': 'two_rid',
                'status': 'READY',
                'branch': 'two_branch',
                'url': 'two_url',
                'vsid': 'vS2D',
                'currentCommit': '456'}),
            sap.rest.gcts.remote_repo.Repository(conn, 'three', data={
                'rid': 'third_rid',
                'status': 'CLONED',
                'branch': 'third_branch',
                'url': 'third_url',
                'vsid': 'vS3D',
                'currentCommit': '7890'}),
        ]

        args = self.repolist()
        args.execute(conn, args)

        self.fake_simple_fetch_repos.assert_called_once_with(conn)
        self.assertConsoleContents(self.console, stdout=
'''Name  | Branch       | Commit | Status  | vSID | URL      
----------------------------------------------------------
one   | one_branch   | 123    | CREATED | vS1D | one_url  
two   | two_branch   | 456    | READY   | vS2D | two_url  
three | third_branch | 7890   | CLONED  | vS3D | third_url
''')

    @patch('sap.cli.gcts.dump_gcts_messages')
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
        repo_name = 'the_repo'

        args = self.delete(repo_name)
        args.execute(conn, args)

        repo = self.fake_simple_delete.call_args.kwargs['repo']
        self.assertEqual(repo.name, repo_name)

        self.fake_simple_delete.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been deleted
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_delete_with_url(self, fake_fetch_repos):
        conn = Mock()

        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, name=repo_name, url=repo_url, configuration={})

        args = self.delete(repo_url)
        args.execute(conn, args)

        self.fake_simple_delete.assert_called_once_with(conn, repo=fake_repo)
        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been deleted
''')

    @patch('sap.cli.gcts.dump_gcts_messages')
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

        self.assertConsoleContents(self.console, stdout=f'No repository found with the URL "{repo_url}".\n')


class TestgCTSCheckout(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_checkout = self.patch('sap.rest.gcts.simple.checkout')
        self.fake_repository = self.patch('sap.cli.gcts.Repository')
        self.repo = Mock()
        self.repo.name = 'the_repo'
        self.fake_repository.return_value = self.repo

    def checkout(self, *args, **kwargs):
        return parse_args('checkout', *args, **kwargs)

    def test_checkout_no_params(self):
        conn = Mock()
        self.repo.branch = 'old_branch'
        self.fake_simple_checkout.return_value = {'fromCommit': '123', 'toCommit': '456'}

        args = self.checkout('the_repo', 'the_branch')
        args.execute(conn, args)

        self.fake_simple_checkout.assert_called_once_with(conn, 'the_branch', repo=self.repo)
        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been set to the branch "the_branch"
(old_branch:123) -> (the_branch:456)
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_checkout_with_url(self, fake_fetch_repos):
        conn = Mock()
        checkout_branch = 'the_branch'

        repo_name = 'the_repo'
        repo_branch = 'old_branch'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, name=repo_name, branch=repo_branch, url=repo_url)

        self.fake_simple_checkout.return_value = {'fromCommit': '123', 'toCommit': '456'}
        args = self.checkout(repo_url, checkout_branch)
        args.execute(conn, args)

        self.fake_simple_checkout.assert_called_once_with(conn, checkout_branch, repo=fake_repo)
        self.assertConsoleContents(self.console, stdout=
f'''The repository "{repo_name}" has been set to the branch "{checkout_branch}"
({repo_branch}:123) -> ({checkout_branch}:456)
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_checkout_json_output(self, fake_fetch_repos):
        conn = Mock()
        checkout_branch = 'the_branch'

        repo_name = 'the_repo'
        repo_branch = 'old_branch'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, name=repo_name, branch=repo_branch, url=repo_url)

        self.fake_simple_checkout.return_value = {'fromCommit': '123', 'toCommit': '456', 'request': 'YGCTS987654321'}
        args = self.checkout(repo_url, checkout_branch, '--format', 'JSON')
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout='''{
  "fromCommit": "123",
  "toCommit": "456",
  "request": "YGCTS987654321"
}
''')

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_checkout_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_checkout.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.checkout('a_repo', 'a_branch')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_checkout_url_error(self, _):
        repo_url = 'http://github.com/the_repo.git'

        args = self.checkout(repo_url, 'a_branch')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stdout=f'No repository found with the URL "{repo_url}".\n')


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
        repo_name = 'the_repo'
        self.fake_simple_log.return_value = [
            { 'id': '456',
              'author': 'Billy Lander',
              'authorMail': 'billy.lander@example.com',
              'date': '2020-10-09',
              'message': 'Finall commit'
            },
            { 'id': '123',
              'author': 'Hugh Star',
              'authorMail': 'hugh.star@example.com',
              'date': '2020-10-02',
              'message': 'Popping commit'
            },
        ]

        args = self.log(repo_name)
        args.execute(conn, args)

        repo = self.fake_simple_log.call_args.kwargs['repo']
        self.assertEqual(repo.name, repo_name)

        self.fake_simple_log.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console, stdout=
'''commit 456
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
        repo_name = 'the_repo'
        self.fake_simple_log.return_value = []

        args = self.log(repo_name)
        args.execute(conn, args)

        repo = self.fake_simple_log.call_args.kwargs['repo']
        self.assertEqual(repo.name, repo_name)

        self.fake_simple_log.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_log_with_url(self, fake_fetch_repos):
        conn = Mock()
        self.fake_simple_log.return_value = []

        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, name=repo_name, url=repo_url)

        args = self.log(repo_url)
        args.execute(conn, args)

        self.fake_simple_log.assert_called_once_with(conn, repo=fake_repo)

    @patch('sap.cli.gcts.dump_gcts_messages')
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

        self.assertConsoleContents(self.console, stdout=f'No repository found with the URL "{repo_url}".\n')


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
        repo_name = 'the_repo'
        self.fake_simple_pull.return_value = {
            'fromCommit': '123',
            'toCommit': '456'
        }

        args = self.pull(repo_name)
        args.execute(conn, args)

        repo = self.fake_simple_pull.call_args.kwargs['repo']
        self.assertEqual(repo.name, repo_name)

        self.fake_simple_pull.assert_called_once_with(conn, repo=repo)
        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been pulled
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

        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been pulled
New HEAD is 456
''')

    def test_pull_no_to_commit(self):
        conn = Mock()
        repo_name = 'the_repo'
        self.fake_simple_pull.return_value = {}

        args = self.pull(repo_name)
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been pulled
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_pull_with_url(self, fake_fetch_repos):
        conn = Mock()
        self.fake_simple_pull.return_value = {
            'fromCommit': '123',
            'toCommit': '456'
        }

        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        fake_repo = mock_repository(fake_fetch_repos, name=repo_name, url=repo_url)

        args = self.pull(repo_url)
        args.execute(conn, args)

        self.fake_simple_pull.assert_called_once_with(conn, repo=fake_repo)

    @patch('sap.cli.gcts.dump_gcts_messages')
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

        self.assertConsoleContents(self.console, stdout=f'No repository found with the URL "{repo_url}".\n')

    def test_pull_json_output(self):
        self.fake_simple_pull.return_value = GCTS_RESPONSE_REPO_PULL_OK.json()

        args = self.pull('the_repo', '-f', 'JSON')
        exit_code = args.execute(None, args)

        self.assertEqual(exit_code, 0)

        self.assertConsoleContents(self.console, stdout=
'''{
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

    def config(self, *args, **kwargs):
        return parse_args('config', *args, **kwargs)

    def test_config_no_params_error(self):
        args = self.config('the_repo')
        args.execute(None, args)

        self.assertConsoleContents(self.console, stderr=
'''Invalid command line options
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
        self.assertConsoleContents(self.console, stdout=
'''the_key_one=one
the_key_two=two
''')

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_config_with_url(self, fake_fetch_repos):
        conn = Mock()

        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        repo_config = {
            'the_key_one': 'one',
            'the_key_two': 'two',
        }

        mock_repository(fake_fetch_repos, name=repo_name, url=repo_url, configuration=repo_config)

        args = self.config('-l', repo_url)
        args.execute(conn, args)

        self.assertConsoleContents(self.console, stdout=
'''the_key_one=one
the_key_two=two
''')

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_config_list_error(self, fake_dumper):
        messages = {'exception': 'test'}
        type(self.fake_instance).configuration = PropertyMock(side_effect=sap.rest.gcts.errors.GCTSRequestError(messages))

        args = self.config('a_repo', '-l')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)

    @patch('sap.rest.gcts.simple.fetch_repos')
    def test_config_url_error(self, _):
        repo_url = 'http://github.com/the_repo.git'

        args = self.config('-l', repo_url)
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        self.assertConsoleContents(self.console, stdout=f'No repository found with the URL "{repo_url}".\n')


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
        repo_name = 'the_repo'
        repo_url = 'http://github.com/the_repo.git'
        corrnr = 'CORRNR'

        fake_repo = mock_repository(fake_fetch_repos, name=repo_name, url=repo_url)

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

        self.assertConsoleContents(self.console, stdout=f'No repository found with the URL "{repo_url}".\n')


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
        self.assertConsoleContents(self.console, stdout='Cannot set new URL.\n')


class TestgCTSRepoGetProperty(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_connection = Mock()

        self.repo_name = 'name'
        self.repo_url = 'http://github.com/name.git'
        self.repo_data = {'rid': 'rid', 'branch': 'branch', 'head': 'head', 'status': 'status', 'vsid': 'vsid',
                          'role': 'role', 'url': self.repo_url, 'currentCommit': 'head'}
        self.fake_repo = sap.cli.gcts.Repository(self.fake_connection, self.repo_name, data=self.repo_data)

    def get_properties_cmd(self, *args, **kwargs):
        return parse_args('repo', 'property', 'get', *args, **kwargs)

    @patch('sap.cli.gcts.get_repository')
    def test_get_properties(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.get_properties_cmd(self.repo_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.assertConsoleContents(self.console, stdout=
'''Name: name
RID: rid
Branch: branch
Commit: head
Status: status
vSID: vsid
Role: role
URL: http://github.com/name.git
''')

    @patch('sap.cli.gcts.get_repository')
    def test_get_property_found(self, fake_get_repository):
        fake_get_repository.return_value = self.fake_repo

        properties = [
            ('Name', 'name\n'),
            ('RID', 'rid\n'),
            ('Branch', 'branch\n'),
            ('Commit', 'head\n'),
            ('Status', 'status\n'),
            ('vSID', 'vsid\n'),
            ('Role', 'role\n'),
            ('URL', 'http://github.com/name.git\n')
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
        mock_repository(fake_fetch_repos, name=self.repo_name, **self.repo_data)

        the_cmd = self.get_properties_cmd(self.repo_url)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 0)
        self.assertConsoleContents(self.console, stdout=
'''Name: name
RID: rid
Branch: branch
Commit: head
Status: status
vSID: vsid
Role: role
URL: http://github.com/name.git
''')

    @patch('sap.cli.gcts.get_repository')
    def test_get_properties_error(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.get_properties_cmd(self.repo_name)
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stdout='Cannot get repository.\n')


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
        self.assertConsoleContents(self.console, stdout='Incorrect property name.\n')

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
        self.assertConsoleContents(self.console, stdout='Cannot get repository.\n')


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

        self.assertConsoleContents(self.console, stdout=
'''Date                | Caller | Operation | Transport | From Commit | To Commit | State | Code
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

        self.assertConsoleContents(self.console, stdout=
                                   "[{'checkoutTime': 20220927091700, 'caller': 'caller', 'type': 'CLONE',"
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

        self.assertIn("--operation: invalid choice: 'NOT_CLONE' (choose from 'COMMIT', 'PULL', 'CHECKOUT', 'CLONE')", mock_stderr.getvalue())

    @patch('sap.cli.gcts.get_repository')
    def test_activities_repo_not_found(self, fake_get_repository):
        fake_get_repository.side_effect = sap.cli.gcts.SAPCliError('Cannot get repository.')

        the_cmd = self.activities_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stdout='Cannot get repository.\n')

    @patch('sap.cli.gcts.get_repository')
    def test_activities_request_error(self, fake_get_repository):
        self.fake_repo.activities.side_effect = sap.cli.gcts.GCTSRequestError({'exception': 'Request failed.'})
        fake_get_repository.return_value = self.fake_repo

        the_cmd = self.activities_cmd('the_repo')
        exit_code = the_cmd.execute(self.fake_connection, the_cmd)

        self.assertEqual(exit_code, 1)
        self.assertConsoleContents(self.console, stderr=
'''Exception:
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
        self.assertConsoleContents(self.console, stderr=
'''Exception:
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
        self.assertConsoleContents(self.console, stderr=
'''Exception:
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
        self.assertConsoleContents(self.console, stdout=
'''Name     | Type  | Symbolic | Peeled | Reference         
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
        self.assertConsoleContents(self.console, stdout=
'''Name    | Type   | Symbolic | Peeled | Reference                  
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
        self.assertConsoleContents(self.console, stdout=
'''Name     | Type   | Symbolic | Peeled | Reference                  
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
        self.assertConsoleContents(self.console, stderr=
'''Exception:
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
        self.assertConsoleContents(self.console, stdout=
f'''Key: {self.config_key}
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
        self.assertConsoleContents(self.console, stdout=
'''Key      | Value      | Category | Changed At | Changed By
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
        self.assertConsoleContents(self.console, stdout=
f'''Key: {self.config_key}
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
