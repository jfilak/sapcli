#!/bin/python

import sys

import unittest
from unittest.mock import patch, MagicMock

import sap.cli
import sap.cli.core


class TestModule(unittest.TestCase):

    def test_get_commands_blind(self):
        commands = sap.cli.get_commands()
        self.assertTrue(commands, msg='Some commands should be registered')

        for idx, cmd in enumerate(commands):
            self.assertEquals(len(cmd), 2,
                msg='The command should be 2 tuple - Command: ' + str(idx))

            self.assertTrue(callable(cmd[0]),
                msg='The first item should be callable - Command: ' + str(idx))

            self.assertIsInstance(cmd[1], sap.cli.core.CommandGroup,
                msg='The second item should be of a command group - Command: ' + str(idx))


class TestPrinting(unittest.TestCase):

    def test_get_console_returns_global(self):
        self.assertEqual(sap.cli.core.get_console(), sap.cli.core._CONSOLE)
        self.assertIsNotNone(sap.cli.core.get_console())

    def test_printout_sanity(self):
        console = MagicMock()

        with patch('sap.cli.core.get_console') as fake_get_console:
            fake_get_console.return_value = console

            sap.cli.core.printout('a', 'b', sep=':', end='$')
            sap.cli.core.printerr('e', 'r', sep='-', end='!')

        self.assertEqual(2, len(fake_get_console.call_args))
        console.printout.assert_called_once_with('a', 'b', sep=':', end='$')
        console.printerr.assert_called_once_with('e', 'r', sep='-', end='!')

    def test_printconsole_sanity_printout(self):
        console = sap.cli.core.PrintConsole()

        with patch('sap.cli.core.print') as fake_print:
            console.printout('a', 'b', sep=':', end='$')

        fake_print.assert_called_once_with('a', 'b', sep=':', end='$', file=sys.stdout)

    def test_printconsole_sanity_printerr(self):
        console = sap.cli.core.PrintConsole()

        with patch('sap.cli.core.print') as fake_print:
            console.printerr('a', 'b', sep=':', end='$')

        fake_print.assert_called_once_with('a', 'b', sep=':', end='$', file=sys.stderr)


class TestConnection(unittest.TestCase):

    def test_empty_instance(self):
        args = sap.cli.build_empty_connection_values()
        self.assertEqual(args.ashost, None)
        self.assertEqual(args.sysnr, None)
        self.assertEqual(args.client, None)
        self.assertEqual(args.port, None)
        self.assertEqual(args.ssl, None)
        self.assertEqual(args.verify, None)
        self.assertEqual(args.user, None)
        self.assertEqual(args.password, None)
        self.assertEqual(args.corrnr, None)

    def test_edit_instance(self):
        args = sap.cli.build_empty_connection_values()

        args.ashost = 'args.ashost'
        self.assertEqual(args.ashost, 'args.ashost')

        args.sysnr = 'args.sysnr'
        self.assertEqual(args.sysnr, 'args.sysnr')

        args.client = 'args.client'
        self.assertEqual(args.client, 'args.client')

        args.port = 'args.port'
        self.assertEqual(args.port, 'args.port')

        args.ssl = 'args.ssl'
        self.assertEqual(args.ssl, 'args.ssl')

        args.verify = 'args.verify'
        self.assertEqual(args.verify, 'args.verify')

        args.user = 'args.user'
        self.assertEqual(args.user, 'args.user')

        args.password = 'args.password'
        self.assertEqual(args.password, 'args.password')

        args.corrnr = 'args.corrnr'
        self.assertEqual(args.corrnr, 'args.corrnr')


if __name__ == '__main__':
    unittest.main()
