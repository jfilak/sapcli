"""CLI specific functionality.

This module provides a facade for use of adt and rfc from cli.

Dependency modules are lazy loaded to enable partial modular installation.
"""


class CommandsCache:
    """Cached of available commands"""

    adt = None

    @staticmethod
    def commands():
        """Returns list of available commands"""

        import sap.cli.program
        import sap.cli.include
        import sap.cli.interface
        import sap.cli.abapclass
        import sap.cli.datadefinition
        import sap.cli.function
        import sap.cli.aunit
        import sap.cli.package
        import sap.cli.cts
        import sap.cli.checkout

        if CommandsCache.adt is None:
            CommandsCache.adt = [
                (adt_connection_from_args, sap.cli.program.CommandGroup()),
                (adt_connection_from_args, sap.cli.include.CommandGroup()),
                (adt_connection_from_args, sap.cli.interface.CommandGroup()),
                (adt_connection_from_args, sap.cli.abapclass.CommandGroup()),
                (adt_connection_from_args, sap.cli.datadefinition.CommandGroup()),
                (adt_connection_from_args, sap.cli.function.CommandGroupFunctionGroup()),
                (adt_connection_from_args, sap.cli.function.CommandGroupFunctionModule()),
                (adt_connection_from_args, sap.cli.aunit.CommandGroup()),
                (adt_connection_from_args, sap.cli.package.CommandGroup()),
                (adt_connection_from_args, sap.cli.cts.CommandGroup()),
                (adt_connection_from_args, sap.cli.checkout.CommandGroup())
            ]

        return CommandsCache.adt


def adt_connection_from_args(args):
    """Returns ADT connection constructed from the passed args (Namespace)
    """

    import sap.adt

    return sap.adt.Connection(
        args.ashost, args.client, args.user, args.password,
        port=args.port, ssl=args.ssl, verify=args.verify)


def get_commands():
    """Builds and returns a list of CLI commands where each item
       is a tuple converting the common CLI parameters to a connection object
       for the implemented command (ADT or RFC).
    """

    return CommandsCache.commands()


class PrintConsole:
    """Standard user output"""

    # pylint: disable=no-self-use
    def printout(self, *objects, sep=' ', end='\n'):
        """Prints out using the python's print function"""

        print(*objects, sep=sep, end=end)


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


__all__ = [
    get_commands.__name__,
    PrintConsole.__name__,
    get_console.__name__,
    printout.__name__
]
