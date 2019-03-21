#!/usr/bin/env python3

import unittest
from argparse import ArgumentParser

import sap.cli.core


class DummyCommandGroup(sap.cli.core.CommandGroup):
    """Test command group"""

    def __init__(self):
        super(DummyCommandGroup, self).__init__('pytest')


@DummyCommandGroup.command()
@DummyCommandGroup.argument_corrnr()
def dummy_corrnr(connection, args):

    return args.corrnr


def parse_args(argv):
    parser = ArgumentParser()
    DummyCommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestCommandGroup(unittest.TestCase):

    def test_argument_corrnr_default(self):
        args = parse_args(['dummy_corrnr'])
        self.assertIsNone(args.corrnr)

    def test_argument_corrnr_value(self):
        args = parse_args(['dummy_corrnr', '--corrnr', '420'])
        self.assertEqual(args.corrnr, '420')


if __name__ == '__main__':
    unittest.main()
