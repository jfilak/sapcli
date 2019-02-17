"""CLI basic functionality"""

from collections import defaultdict


class CommandGroup:
    """Base class for CLI Commands which should be implemented as methods
       ancestor classes.

       Command objects should be adapters transforming command line parameters
       to functional method calls.
    """

    def __init__(self, name):
        self.name = name

    def install_parser(self, arg_parser):
        """Add own commands as sub-parser of the given ArgParser.
        """

        command_args = arg_parser.add_subparsers()

        for command in self.__class__.commands.values():
            get_args = command_args.add_parser(command['name'])
            get_args.set_defaults(execute=command['execute'])

            for argument in command['arguments']:
                get_args.add_argument(*argument[0], **argument[1])

    @classmethod
    def get_commands(cls):
        """Get a dictionary of command definitions where the key is
           an arbitrary key (in our case it is the name of the decorated function
           implementing the command functionality) and the value is
           a dictionary containing command definition.

           The recognized command definition keys are the following:
             - name: displayed named
             - arguments: a tuple (*args, **kwargs) passed to
                          the method add_argument() of ArgPasers
             - execute: callable implementing the command
        """

        if not hasattr(cls, 'commands'):
            cls.commands = defaultdict(lambda: {'arguments': []})

        return cls.commands

    @classmethod
    def command(cls, cmd_name=None):
        """Python Decorator marking a method a CLI command
        """

        def p_command(func):
            """A closure that actually processes the decorated function
            """

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
        """Decorator adding argument to a cli command
           The parameters *args and **kwargs will be passed to
           the method add_argument() of ArgPasers
        """

        def p_argument(func):
            """A closure that actually processes the decorated function
            """

            commands = cls.get_commands()
            commands[func.__name__]['arguments'].append((args, kwargs))

            return func

        return p_argument
