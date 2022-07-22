#!/usr/bin/env python3

import unittest
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
    GCTS_RESPONSE_REPO_NOT_EXISTS
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

        args = self.delete('the_repo')
        args.execute(conn, args)

        self.fake_simple_delete.assert_called_once_with(conn, 'the_repo')
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


class TestgCTSCheckout(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_checkout = self.patch('sap.rest.gcts.simple.checkout')
        self.fake_repository = self.patch('sap.cli.gcts.Repository')
        self.repo = Mock()
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

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_checkout_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_checkout.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.checkout('a_repo', 'a_branch')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)


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

        args = self.log('the_repo')
        args.execute(conn, args)

        self.fake_simple_log.assert_called_once_with(conn, name='the_repo')
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
        self.fake_simple_log.return_value = []

        args = self.log('the_repo')
        args.execute(conn, args)

        self.fake_simple_log.assert_called_once_with(conn, name='the_repo')
        self.assertConsoleContents(self.console)

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_log_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_log.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.log('a_repo')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)


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
        self.fake_simple_pull.return_value = {
            'fromCommit': '123',
            'toCommit': '456'
        }

        args = self.pull('the_repo')
        args.execute(conn, args)

        self.fake_simple_pull.assert_called_once_with(conn, name='the_repo')
        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been pulled
123 -> 456
''')

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_pull_error(self, fake_dumper):
        messages = {'exception': 'test'}
        self.fake_simple_pull.side_effect = sap.rest.gcts.errors.GCTSRequestError(messages)

        args = self.pull('a_repo')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)


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

    @patch('sap.cli.gcts.dump_gcts_messages')
    def test_config_list_error(self, fake_dumper):
        messages = {'exception': 'test'}
        type(self.fake_instance).configuration = PropertyMock(side_effect=sap.rest.gcts.errors.GCTSRequestError(messages))

        args = self.config('a_repo', '-l')
        exit_code = args.execute(None, args)
        self.assertEqual(exit_code, 1)

        fake_dumper.assert_called_once_with(sap.cli.core.get_console(), messages)


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

    def test_commit_with_error(self):
        repo_name = 'the_repo'
        corrnr = 'CORRNR'

        self.fake_connection.set_responses(GCTS_RESPONSE_REPO_NOT_EXISTS)

        commit_cmd = self.commit_cmd(repo_name, corrnr)
        commit_cmd.execute(self.fake_connection, commit_cmd)

        self.assertConsoleContents(self.console, stderr=f'''Exception:\n  Repository does not exist\n''')


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
        the_cmd.execute(self.fake_connection, the_cmd)

        fake_set_url.assert_called_once_with(new_url)


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
