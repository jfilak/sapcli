#!/usr/bin/env python3

from unittest.mock import MagicMock, patch, Mock

import sap.cli.gcts

from mock import ConsoleOutputTestCase, PatcherTestCase
from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.gcts.CommandGroup())


class TestgCTSClone(ConsoleOutputTestCase, PatcherTestCase):

    def setUp(self):
        super(TestgCTSClone, self).setUp()

        assert self.console is not None

        self.patch_console(console=self.console)
        self.fake_simple_clone = self.patch('sap.rest.gcts.simple_clone')

    def tearDown(self):
        self.unpatch_all()

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
            start_dir='src',
            vcs_token=None
        )
