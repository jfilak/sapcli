#!/usr/bin/env python3

from unittest.mock import MagicMock

import sap.cli.adt

from mock import ConsoleOutputTestCase, PatcherTestCase
from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.adt.CommandGroup())


class TestADT(ConsoleOutputTestCase, PatcherTestCase):

    def setUp(self):
        super(TestADT, self).setUp()

        assert self.console is not None

        self.patch_console(console=self.console)

        self.collection_types = {
            '/uri/first': ['first.v1', 'first.v2'],
            '/uri/second': ['second.v1', 'second.v2']
        }

        self.adt_connection = MagicMock()
        self.adt_connection.collection_types = self.collection_types

    def tearDown(self):
        self.unpatch_all()

    def parse_collections(self):
        return parse_args('collections')

    def test_adt_without_parameters(self):
        args = self.parse_collections()

        args.execute(self.adt_connection, args)

        self.assertConsoleContents(self.console, stderr='', stdout='''/uri/first
  first.v1
  first.v2
/uri/second
  second.v1
  second.v2
''')
