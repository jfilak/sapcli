#!/usr/bin/env python3

import sys
import unittest
from unittest.mock import patch
from io import StringIO
from types import SimpleNamespace

import importlib.util
from importlib.machinery import SourceFileLoader

loader = SourceFileLoader(fullname='sapcli', path='bin/sapcli')
spec = importlib.util.spec_from_file_location('sapcli', 'bin/sapcli', loader=loader)
sapcli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sapcli)
sys.modules['sapcli'] = sapcli

class TestParseCommandLine(unittest.TestCase):

    def test_args_sanity(self):
        args = sapcli.parse_command_line(['sapcli', '--user', 'fantomas', '--passwd', 'Down1oad'])

        self.assertEqual(
            vars(args),
            {'ashost':'localhost', 'client':'001', 'ssl':True, 'port':443,
             'user':'fantomas', 'passwd':'Down1oad', 'verbose_count':0})

    def test_args_ask_user(self):
        with patch('sapcli.input', lambda pfx: 'fantomas') as fake_input:
            args = sapcli.parse_command_line(['sapcli', '--passwd', 'Down1oad'])

        self.assertEqual(args.user, 'fantomas')

    def test_args_ask_password(self):
        with patch('getpass.getpass', lambda : 'Down1oad') as fake_getpass:
            args = sapcli.parse_command_line(['sapcli', '--user', 'fantomas'])

        self.assertEqual(args.user, 'fantomas')

    def test_args_ask_user_and_password(self):
        with patch('getpass.getpass', lambda : 'Down1oad') as fake_getpass, \
             patch('sapcli.input', lambda pfx: 'fantomas') as fake_input:
            args = sapcli.parse_command_line(['sapcli'])

        self.assertEqual(args.user, 'fantomas')
        self.assertEqual(args.passwd, 'Down1oad')


if __name__ == '__main__':
    unittest.main()
