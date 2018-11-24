"""CLI specific functionality.

This module provides a facade for use of adt and rfc from cli.

Dependency modules are lazy loaded to enable partial modular installation.
"""


def rfc_connection_from_args(args):
    """Returns RFC connection constructed from the passed args (Namespace)
    """

    import sap.rfc

    raise NotImplementedError


def adt_connection_from_args(args):
    """Returns ADT connection constructed from the passed args (Namespace)
    """

    import sap.adt

    return sap.adt.Connection(
            args.ashost, args.client, args.user, args.passwd,
            port=args.port, ssl=args.ssl)


def get_commands():
    import sap.cli.program
    import sap.cli.abapclass
    import sap.cli.aunit

    return [
        (adt_connection_from_args, sap.cli.program.CommandGroup()),
        (adt_connection_from_args, sap.cli.abapclass.CommandGroup()),
        (adt_connection_from_args, sap.cli.aunit.CommandGroup())
    ]


__all__ = [
    get_commands.__name__
]
