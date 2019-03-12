"""CLI specific functionality.

This module provides a facade for use of adt and rfc from cli.

Dependency modules are lazy loaded to enable partial modular installation.
"""


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

    import sap.cli.program
    import sap.cli.interface
    import sap.cli.abapclass
    import sap.cli.aunit
    import sap.cli.package
    import sap.cli.cts
    import sap.cli.checkout

    return [
        (adt_connection_from_args, sap.cli.program.CommandGroup()),
        (adt_connection_from_args, sap.cli.interface.CommandGroup()),
        (adt_connection_from_args, sap.cli.abapclass.CommandGroup()),
        (adt_connection_from_args, sap.cli.aunit.CommandGroup()),
        (adt_connection_from_args, sap.cli.package.CommandGroup()),
        (adt_connection_from_args, sap.cli.cts.CommandGroup()),
        (adt_connection_from_args, sap.cli.checkout.CommandGroup())
    ]


__all__ = [
    get_commands.__name__
]
