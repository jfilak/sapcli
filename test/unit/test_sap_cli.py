#!/bin/python

import unittest

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


if __name__ == '__main__':
    unittest.main()
