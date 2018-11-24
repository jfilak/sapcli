"""CLI basic functionality"""

from collections import defaultdict
from functools import partial


class CommandGroup(object):
    """Base class for CLI Commands.
       Command objects should be adapters transforming command line parameters
       to functional method calls.
    """

    def __init__(self, name):
        self.name = name

    def install_parser(self, arg_parser):
        command_args = arg_parser.add_subparsers()

        for command in self.__class__.commands.values():
            get_args = command_args.add_parser(command['name'])
            get_args.set_defaults(execute=command['execute'])

            for argument in command['arguments']:
                get_args.add_argument(*argument[0], **argument[1])

    @classmethod
    def get_commands(cls):
        if not hasattr(cls, 'commands'):
            cls.commands = defaultdict(lambda: {'arguments': []})

        return cls.commands

    @classmethod
    def command(cls, cmd_name=None):
        def p_command(func):
            fname = func.__name__

            commands = cls.get_commands()
            commands[fname]['name'] = cmd_name
            commands[fname]['execute'] = func

            if commands[fname]['name'] is None:
                commands[fname]['name'] = fname

            return func

        return p_command

    @classmethod
    def argument(cls, *args, **kwargs):
        def p_argument(func):
            commands = cls.get_commands()
            commands[func.__name__]['arguments'].append((args, kwargs))

            return func

        return p_argument
