#!/usr/bin/env python3

from unittest.mock import MagicMock, patch, Mock

import sap.cli.gcts

from mock import ConsoleOutputTestCase, PatcherTestCase
from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.gcts.CommandGroup())


class TestgCTSClone(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_clone = self.patch('sap.rest.gcts.simple_clone')

    def clone(self, *args, **kwargs):
        return parse_args('clone', *args, **kwargs)

    def test_clone_with_url_only(self):
        args = self.clone('https://example.org/repo/git/sample.git')
        self.fake_simple_clone.return_value = None

        conn = Mock()
        args.execute(conn, args)

        self.fake_simple_clone.assert_called_once_with(
            conn,
            'https://example.org/repo/git/sample.git',
            'sample',
            start_dir='src/',
            vcs_token=None
        )


class TestgCTSRepoList(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_fetch_repos = self.patch('sap.rest.gcts.simple_fetch_repos')

    def repolist(self, *args, **kwargs):
        return parse_args('repolist', *args, **kwargs)

    def test_repolist_no_params(self):
        conn = Mock()

        self.fake_simple_fetch_repos.return_value = [
            sap.rest.gcts.Repository(conn, 'one', data={
                'rid': 'one_rid',
                'branch': 'one_branch',
                'url': 'one_url'}),
            sap.rest.gcts.Repository(conn, 'two', data={
                'rid': 'two_rid',
                'branch': 'two_branch',
                'url': 'two_url'}),
        ]

        args = self.repolist()
        args.execute(conn, args)

        self.fake_simple_fetch_repos.assert_called_once_with(conn)
        self.assertConsoleContents(self.console, stdout=
'''one one_branch one_url
two two_branch two_url
''')


class TestgCTSDelete(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_delete = self.patch('sap.rest.gcts.simple_delete')

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


class TestgCTSCheckout(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_checkout = self.patch('sap.rest.gcts.simple_checkout')

    def checkout(self, *args, **kwargs):
        return parse_args('checkout', *args, **kwargs)

    def test_checkout_no_params(self):
        conn = Mock()

        args = self.checkout('the_repo', 'the_branch')
        args.execute(conn, args)

        self.fake_simple_checkout.assert_called_once_with(conn, 'the_repo', 'the_branch')
        self.assertConsoleContents(self.console, stdout=
'''The repository "the_repo" has been set to the branch "the_branch"
''')


class TestgCTSConfig(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_repository = self.patch('sap.rest.gcts.Repository')
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
