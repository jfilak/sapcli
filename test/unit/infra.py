from argparse import ArgumentParser

def generate_parse_args(command_group):

    def parse_args_impl(*argv):
        parser = ArgumentParser()
        command_group.install_parser(parser)
        return parser.parse_args(argv)

    return parse_args_impl
