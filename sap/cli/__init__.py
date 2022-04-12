"""CLI specific functionality.

This module provides a facade for use of adt and rfc from cli.

Dependency modules are lazy loaded to enable partial modular installation.
"""


import os
from functools import partial
from types import SimpleNamespace
from sap import rfc


class CommandsCache:
    """Cached of available commands"""

    adt = None
    rfc = None
    rest = None
    odata = None

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
        import sap.cli.atc
        import sap.cli.datapreview
        import sap.cli.package
        import sap.cli.cts
        import sap.cli.gcts
        import sap.cli.checkout
        import sap.cli.activation
        import sap.cli.adt
        import sap.cli.abapgit
        import sap.cli.bsp
        import sap.cli.flp
        import sap.cli.rap

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
                (adt_connection_from_args, sap.cli.atc.CommandGroup()),
                (adt_connection_from_args, sap.cli.datapreview.CommandGroup()),
                (adt_connection_from_args, sap.cli.package.CommandGroup()),
                (adt_connection_from_args, sap.cli.cts.CommandGroup()),
                (adt_connection_from_args, sap.cli.checkout.CommandGroup()),
                (adt_connection_from_args, sap.cli.activation.CommandGroup()),
                (adt_connection_from_args, sap.cli.adt.CommandGroup()),
                (adt_connection_from_args, sap.cli.abapgit.CommandGroup()),
                (adt_connection_from_args, sap.cli.rap.CommandGroup())
            ]

        if CommandsCache.rest is None:
            CommandsCache.rest = [
                (gcts_connection_from_args, sap.cli.gcts.CommandGroup())
            ]

        if CommandsCache.rfc is None:
            import sap.cli.startrfc
            import sap.cli.strust
            import sap.cli.user

            CommandsCache.rfc = [
                (rfc_connection_from_args, sap.cli.startrfc.CommandGroup()),
                (rfc_connection_from_args, sap.cli.strust.CommandGroup()),
                (rfc_connection_from_args, sap.cli.user.CommandGroup())
            ]

        if CommandsCache.odata is None:
            CommandsCache.odata = [
                (partial(odata_connection_from_args, 'UI5/ABAP_REPOSITORY_SRV'), sap.cli.bsp.CommandGroup()),
                (partial(odata_connection_from_args, 'UI2/PAGE_BUILDER_CUST'), sap.cli.flp.CommandGroup())
            ]

        return CommandsCache.adt + CommandsCache.rest + CommandsCache.rfc + CommandsCache.odata


def adt_connection_from_args(args):
    """Returns ADT connection constructed from the passed args (Namespace)
    """

    import sap.adt

    if args.ashost and args.password and not args.rest_over_rfc:
        return sap.adt.ConnectionViaHTTP(args.ashost,
                                         args.client,
                                         args.user,
                                         args.password,
                                         port=args.port,
                                         ssl=args.ssl,
                                         verify=args.verify)

    rfc_connection = rfc_connection_from_args(args)
    return sap.adt.ConnectionViaRFC(rfc_connection)


def rfc_connection_from_args(args):
    """Returns RFC connection constructed from the passed args (Namespace)
    """

    rfc_args_name = [
        "ashost", "sysnr", "client", "user", "password", "mshost", "msserv",
        "sysid", "rfc_group", "snc_qop", "snc_myname", "snc_partnername",
        "snc_lib"
    ]

    name_rewrite = {"password": "passwd", "rfc_group": "group"}

    rfc_args = {
        name_rewrite.get(name, name): getattr(args, name)
        for name in rfc_args_name if name in args and getattr(args, name)
    }

    return rfc.connect(**rfc_args)


def gcts_connection_from_args(args):
    """Returns REST connection constructed from the passed args (Namespace)
       and configured for gCTS calls.
    """

    import sap.rest

    return sap.rest.Connection('sap/bc/cts_abapvcs', 'system', args.ashost, args.client,
                               args.user, args.password, port=args.port, ssl=args.ssl,
                               verify=args.verify)


def odata_connection_from_args(service_name, args):
    """Returns RFC connection constructed from the passed args (Namespace)
    """

    import sap.odata
    return sap.odata.Connection(service_name, args.ashost, args.port,
                                args.client, args.user, args.password, args.ssl,
                                args.verify)


def get_commands():
    """Builds and returns a list of CLI commands where each item
       is a tuple converting the common CLI parameters to a connection object
       for the implemented command (ADT or RFC).
    """

    return CommandsCache.commands()


def build_empty_connection_values():
    """Returns empty connection settings. Particularly useful
       when passed to the function resolve_default_connection_values
       which will fill the object with values from Environment Variables.
    """

    return SimpleNamespace(
        ashost=None,
        sysnr=None,
        client=None,
        port=None,
        ssl=None,
        verify=None,
        user=None,
        password=None,
        corrnr=None
    )


# pylint: disable=too-many-branches, invalid-name
def resolve_default_connection_values(args):
    """Add default values to connection specification. The values are loaded
       from Environment variables.
    """

    if not args.ashost:
        args.ashost = os.getenv('SAP_ASHOST')

    if not args.sysnr:
        args.sysnr = os.getenv('SAP_SYSNR', '00')

    if not args.client:
        args.client = os.getenv('SAP_CLIENT')

    if not args.port:
        port = os.getenv('SAP_PORT')
        if port:
            args.port = int(port)
        else:
            args.port = 443

    if args.ssl is None:
        ssl = os.getenv('SAP_SSL')
        if ssl is not None:
            args.ssl = ssl.lower() not in ('n', 'no', 'false', 'off')
        else:
            args.ssl = True

    if args.verify is None:
        verify = os.getenv('SAP_SSL_VERIFY')
        if verify is not None:
            args.verify = verify.lower() not in ('n', 'no', 'false', 'off')
        else:
            args.verify = True

    if not args.user:
        args.user = os.getenv('SAP_USER')

    if not args.password:
        args.password = os.getenv('SAP_PASSWORD')

    if hasattr(args, 'corrnr') and args.corrnr is None:
        args.corrnr = os.getenv('SAP_CORRNR')


__all__ = [
    get_commands.__name__,
]
