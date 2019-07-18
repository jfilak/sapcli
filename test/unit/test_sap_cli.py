#!/bin/python

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

        fake_get_console.assert_called_once_with()
        console.printout.assert_called_once_with('a', 'b', sep=':', end='$')

    def test_printconsole_sanity(self):
        console = sap.cli.core.PrintConsole()

        with patch('sap.cli.core.print') as fake_print:
            console.printout('a', 'b', sep=':', end='$')

        fake_print.assert_called_once_with('a', 'b', sep=':', end='$')


if __name__ == '__main__':
    unittest.main()
