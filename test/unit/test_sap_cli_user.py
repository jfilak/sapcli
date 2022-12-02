#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, patch, Mock, PropertyMock, call

import sap.cli.user
from sap.rfc.user import today_sap_date

from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase,
)

from test_sap_rfc_bapi import (
        create_bapiret_info
)

from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.user.CommandGroup())


class TestUserDetails(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.conn = Mock()

    def test_last_login(self):
        self.conn.call.return_value = {
            'RETURN': [],
            'ALIAS': {
                'USERALIAS': 'HTTP'
            },
            'LOGONDATA': {
                'LTIME': '20200211'
            }
        }

        args = parse_args('details', 'ANZEIGER')
        args.execute(self.conn, args)

        self.assertConsoleContents(console=self.console, stdout='''User      : ANZEIGER
Alias     : HTTP
Last Login: 20200211
''')


class TestUserCreate(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.conn = Mock()

    def test_create_ok(self):
        self.conn.call.return_value = {
            'RETURN': [create_bapiret_info('User created')],
        }

        args = parse_args('create', 'ANZEIGER', '--new-password', 'Victory1!')

        args.execute(self.conn, args)

        self.conn.call.assert_called_once_with('BAPI_USER_CREATE1',
                USERNAME='ANZEIGER',
                ADDRESS={'FIRSTNAME': '', 'LASTNAME': '', 'E_MAIL': ''},
                PASSWORD={'BAPIPWD': 'Victory1!'},
                ALIAS={'USERALIAS': ''},
                LOGONDATA={'USTYP': 'Dialog',
                           'GLTGV': today_sap_date(),
                           'GLTGB': '20991231'}
       )

        self.assertConsoleContents(console=self.console, stdout='''Success(NFO|555): User created
''')


class TestUserChange(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)
        self.conn = Mock()

    def test_change_ok(self):
        self.conn.call.return_value = {
            'RETURN': [create_bapiret_info('User changed')],
        }

        args = parse_args('change', 'ANZEIGER', '--new-password', 'Victory1!')

        args.execute(self.conn, args)

        self.assertEqual(
            self.conn.call.call_args_list,
            [call('BAPI_USER_GET_DETAIL', USERNAME='ANZEIGER'),
             call('BAPI_USER_CHANGE', USERNAME='ANZEIGER',
                PASSWORD={'BAPIPWD': 'Victory1!'}, PASSWORDX={'BAPIPWD': 'X'})])

        self.assertConsoleContents(
                console=self.console,
                stdout='''Success(NFO|555): User changed
''')
