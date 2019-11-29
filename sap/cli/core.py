"""CLI basic functionality"""

import sys

from sap.errors import SAPCliError


class InvalidCommandLineError(SAPCliError):
    """Exception type for wrong command line parameters"""

    # pylint: disable=unnecessary-pass
    pass


class CommandDeclaration:
    """Command forward declaration"""

    def __init__(self, handler, name):
        self.handler = handler
        self.name = name
        self.arguments = list()

    def append_argument(self, *args, **kwargs):
        """Declares a new ArgParser argument at the end of the list"""

        self.insert_argument(len(self.arguments), *args, **kwargs)

    def insert_argument(self, position, *args, **kwargs):
        """Declares a new ArgParser argument at the specified position"""

        self.arguments.insert(position, (args, kwargs))

    def declare_corrnr(self, position=None):
        """Declares a new ArgParser argument"""

        if position is None:
            position = len(self.arguments)

        self.insert_argument(position, '--corrnr', nargs='?', default=None)

    def install_arguments(self, parser):
        """Installs declared arguments to a ArgParser"""

        for args, kwargs in self.arguments:
            parser.add_argument(*args, **kwargs)


class CommandsList:
    """List of Command Declarations"""

    def __init__(self):
        self.declarations = {}

    def add_command(self, handler, name=None):
        """Adds a new command"""

        fname = handler.__name__

        if fname in self.declarations:
            raise SAPCliError(f'Handler already registered: {fname}')

        cmd = CommandDeclaration(handler, name if name is not None else fname)
        self.declarations[fname] = cmd

        return cmd

    def get_declaration(self, handler):
        """Returns the command declaration for the handler"""

        try:
            return self.declarations[handler.__name__]
        except KeyError:
            raise SAPCliError(f'No such Command Declaration: {handler.__name__}')

    def values(self):
        """Returns the list of declared values"""

        return self.declarations.values()


class CommandGroup:
    """Base class for CLI Commands which should be implemented as methods
       ancestor classes.

       Command objects should be adapters transforming command line parameters
       to functional method calls.
    """

    def __init__(self, name):
        self.name = name

    # pylint: disable=unused-argument, no-self-use
    def _tune_parser(self, group_parser, command_subparser):
        """For ancestors - must return command_subparser or a new subparser
        """

        return command_subparser

    def install_parser(self, arg_parser):
        """Add own commands as sub-parser of the given ArgParser.
        """

        command_args = arg_parser.add_subparsers()

        for command in self.__class__.get_commands().values():
            get_args = command_args.add_parser(command.name)
            get_args.set_defaults(execute=command.handler)
            command.install_arguments(get_args)

        return self._tune_parser(arg_parser, command_args)

    @classmethod
    def get_commands(cls):
        """Get a dictionary of command definitions where the key is an
           arbitrary key (in our case it is the name of the decorated function
           implementing the command functionality) and the value is
           CommandDeclaration
        """

        if not hasattr(cls, 'commands'):
            cls.commands = CommandsList()

        return cls.commands

    @classmethod
    def get_command_declaration(cls, func):
        """Returns command declaration"""

        return cls.get_commands().get_declaration(func)

    @classmethod
    def command(cls, cmd_name=None):
        """Python Decorator marking a method a CLI command
        """

        def p_command(func):
            """A closure that actually processes the decorated function
            """

            cls.get_commands().add_command(func, cmd_name)

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

            cls.get_command_declaration(func).append_argument(*args, **kwargs)

            return func

        return p_argument

    @classmethod
    def argument_corrnr(cls):
        """Decorator adding the corrnr argument to a cli command"""

        def p_argument(func):
            """A closure that actually processes the decorated function
            """

            cls.get_command_declaration(func).declare_corrnr()

            return func

        return p_argument


class PrintConsole:
    """Standard user output"""

    def __init__(self, out_file=None, err_file=None):
        self._out = out_file if out_file is not None else sys.stdout
        self._err = err_file if err_file is not None else sys.stderr

    # pylint: disable=no-self-use
    def _do_print(self, objects, file, sep=' ', end='\n'):
        print(*objects, sep=sep, end=end, file=file)

    def printout(self, *objects, sep=' ', end='\n'):
        """Prints out using the python's print function"""

        self._do_print(objects, sep=sep, end=end, file=self._out)

    def printerr(self, *objects, sep=' ', end='\n'):
        """Prints out an error message"""

        self._do_print(objects, sep=sep, end=end, file=self._err)


_CONSOLE = None


def get_console():
    """Standard user output. Don't user for logging!"""

    # pylint: disable=global-statement
    global _CONSOLE

    if _CONSOLE is None:
        _CONSOLE = PrintConsole()

    return _CONSOLE


def printout(*objects, sep=' ', end='\n'):
    """A shortcut for get_console().printout()"""

    get_console().printout(*objects, sep=sep, end=end)


def printerr(*objects, sep=' ', end='\n'):
    """A shortcut for get_console().printerr()"""

    get_console().printerr(*objects, sep=sep, end=end)
