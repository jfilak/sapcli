#!/usr/bin/env python3

import json
from argparse import ArgumentParser

import unittest
from unittest.mock import MagicMock

import sap.cli.startrfc

from mock import ConsoleOutputTestCase, PatcherTestCase


def parse_args(*argv):
    parser = ArgumentParser()
    sap.cli.startrfc.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestStartRFC(ConsoleOutputTestCase, PatcherTestCase):

    def setUp(self):
        super(TestStartRFC, self).setUp()

        self.rfc_function_module = 'STFC_CONNECTION'

        self.patch_console(console=self.console)

    def execute_cmd(self, json_args_obj=None):
        rfc_connection = MagicMock()
        rfc_connection.call.return_value = 'RESPONSE'

        if json_args_obj is None:
            args = parse_args(self.rfc_function_module)
        else:
            args = parse_args(self.rfc_function_module, json.dumps(json_args_obj))

        args.execute(rfc_connection, args)

        if json_args_obj is None:
            rfc_connection.call.assert_called_once_with(self.rfc_function_module)
        else:
            rfc_connection.call.assert_called_once_with(self.rfc_function_module, **json_args_obj)

        self.assertConsoleContents(self.console, stdout='RESPONSE\n', stderr='')

    def test_startrfc_without_parameters(self):
        self.execute_cmd()

    def test_startrfc_without_parameters(self):
        self.execute_cmd({'REQUTEXT':'ping'})
