from argparse import ArgumentParser

import sap.cli.core

def generate_parse_args(command_group):

    def parse_args_impl(*argv):
        parser = ArgumentParser()
        parser.add_argument('--client', type=int, default=100, help='Client number')
        parser.add_argument('--user', type=str, default='TESTER', help='User name')
        parser.set_defaults(console_factory=sap.cli.core.get_console)

        command_group.install_parser(parser)
        return parser.parse_args(argv)

    return parse_args_impl
