#!/usr/bin/env python3

import json
from argparse import ArgumentParser
from io import StringIO

import unittest
from unittest.mock import MagicMock, patch

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

        self.response ={
            'ECHOTXT': 'whatever',
            'RESPONSE': 'SAP NW 751 anzeiger',
            'PARAMS': {
                'TABLE': ['A', 'B', 'C']
            }
        }

        self.rfc_connection = MagicMock()
        self.rfc_connection.call.return_value = self.response

    def execute_cmd(self, json_args_obj=None, exp_stdout=None, params=[]):

        if json_args_obj is None:
            args = parse_args(self.rfc_function_module, *params)
        elif json_args_obj == '-':
            args = parse_args(self.rfc_function_module, *params, '-')
        else:
            args = parse_args(self.rfc_function_module, *params, json.dumps(json_args_obj))

        args.execute(self.rfc_connection, args)

        if json_args_obj is None:
            self.rfc_connection.call.assert_called_once_with(self.rfc_function_module)
        elif json_args_obj != '-':
            self.rfc_connection.call.assert_called_once_with(self.rfc_function_module, **json_args_obj)

        if exp_stdout is None:
            exp_stdout = sap.cli.startrfc.FORMATTERS['human'](self.response) + '\n'

        self.assertConsoleContents(self.console, stdout=exp_stdout, stderr='')

    def test_startrfc_without_parameters(self):
        self.execute_cmd()

    def test_startrfc_with_parameters(self):
        self.execute_cmd({'REQUTEXT':'ping'})

    def test_startrfc_with_stdin(self):
        parameters = {'REQUTEXT':'ping pong'}

        with patch('sys.stdin', StringIO(json.dumps(parameters))):
            self.execute_cmd('-')

        self.rfc_connection.call.assert_called_once_with(self.rfc_function_module, **parameters)

    def test_startrfc_output_json(self):
        self.execute_cmd(exp_stdout=json.dumps(self.response) + '\n', params=['--output', 'json'])

    def test_startrfc_output_dump(self):
        self.execute_cmd(exp_stdout=json.dumps(self.response) + '\n', params=['--output', 'json'])
