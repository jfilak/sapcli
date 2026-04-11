"""CLI specific functionality.

This module provides a facade for use of adt and rfc from cli.

Dependency modules are lazy loaded to enable partial modular installation.
"""


import os
from functools import partial
from types import SimpleNamespace
from sap import rfc
from sap.config import SAPCliConfigError


class CommandsCache:
    """Cached of available commands"""

    adt = None
    rfc = None
    rest = None
    odata = None
    local = None

    @staticmethod
    def commands():
        """Returns list of available commands"""

        import sap.cli.program
        import sap.cli.include
        import sap.cli.interface
        import sap.cli.abapclass
        import sap.cli.datadefinition
        import sap.cli.accesscontrol
        import sap.cli.behaviordefinition
        import sap.cli.function
        import sap.cli.aunit
        import sap.cli.atc
        import sap.cli.datapreview
        import sap.cli.package
        import sap.cli.cts
        import sap.cli.gcts
        import sap.cli.checkout
        import sap.cli.checkin
        import sap.cli.activation
        import sap.cli.adt
        import sap.cli.abapgit
        import sap.cli.bsp
        import sap.cli.featuretoggle
        import sap.cli.flp
        import sap.cli.rap
        import sap.cli.table
        import sap.cli.badi
        import sap.cli.structure
        import sap.cli.dataelement
        import sap.cli.domain
        import sap.cli.authorizationfield
        import sap.cli.abap
        import sap.cli.config

        if CommandsCache.adt is None:
            CommandsCache.adt = [
                (adt_connection_from_args, sap.cli.program.CommandGroup()),
                (adt_connection_from_args, sap.cli.include.CommandGroup()),
                (adt_connection_from_args, sap.cli.interface.CommandGroup()),
                (adt_connection_from_args, sap.cli.abapclass.CommandGroup()),
                (adt_connection_from_args, sap.cli.datadefinition.CommandGroup()),
                (adt_connection_from_args, sap.cli.accesscontrol.CommandGroup()),
                (adt_connection_from_args, sap.cli.behaviordefinition.CommandGroup()),
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
                (adt_connection_from_args, sap.cli.rap.CommandGroup()),
                (adt_connection_from_args, sap.cli.table.CommandGroup()),
                (adt_connection_from_args, sap.cli.structure.CommandGroup()),
                (adt_connection_from_args, sap.cli.dataelement.CommandGroup()),
                (adt_connection_from_args, sap.cli.domain.CommandGroup()),
                (adt_connection_from_args, sap.cli.authorizationfield.CommandGroup()),
                (adt_connection_from_args, sap.cli.checkin.CommandGroup()),
                (adt_connection_from_args, sap.cli.badi.CommandGroup()),
                (adt_connection_from_args, sap.cli.featuretoggle.CommandGroup()),
                (adt_connection_from_args, sap.cli.abap.CommandGroup()),
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

        if CommandsCache.local is None:
            CommandsCache.local = [
                (no_connection, sap.cli.config.CommandGroup()),
            ]

        return CommandsCache.adt + CommandsCache.rest + CommandsCache.rfc + CommandsCache.odata + CommandsCache.local


def adt_connection_from_args(args):
    """Returns ADT connection constructed from the passed args (Namespace)
    """

    import sap.adt

    return sap.adt.Connection(
        args.ashost, args.client, args.user, args.password,
        port=args.port, ssl=args.ssl, verify=args.verify,
        ssl_server_cert=args.ssl_server_cert)


def rfc_connection_from_args(args):
    """Returns RFC connection constructed from the passed args (Namespace)
    """

    rfc_args_name = [
        "ashost", "sysnr", "client", "user", "password", "mshost", "msserv",
        "sysid", "group", "snc_qop", "snc_myname", "snc_partnername", "snc_lib"
    ]

    rfc_args = {
        name if name != "password" else "passwd": getattr(args, name)
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
                               verify=args.verify, ssl_server_cert=args.ssl_server_cert)


def odata_connection_from_args(service_name, args):
    """Returns RFC connection constructed from the passed args (Namespace)
    """

    import sap.odata
    return sap.odata.Connection(service_name, args.ashost, args.port,
                                args.client, args.user, args.password, args.ssl,
                                args.verify, ssl_server_cert=args.ssl_server_cert)


def no_connection(_args):
    """Returns None - used for commands that do not require a connection."""

    return None


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
        ssl_server_cert=None,
        user=None,
        password=None,
    )


_FALSE_TOKENS = ('n', 'no', 'false', 'off')


def _normalize_bool(value):
    """Normalize a boolean value from config or environment.

    Booleans pass through directly. Strings are compared
    case-insensitively against common false tokens.
    """

    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() not in _FALSE_TOKENS

    return bool(value)


# pylint: disable=too-many-branches, invalid-name
def resolve_default_connection_values(args):
    """Add default values to connection specification. The values are loaded
       from environment variables and configuration file, with the following
       precedence: CLI args > env vars > config file > built-in defaults.
    """

    # Load config file context if available
    config_values = _get_config_context_values(args)

    if not args.ashost:
        args.ashost = os.getenv('SAP_ASHOST') or config_values.get('ashost')

    if not args.sysnr:
        args.sysnr = os.getenv('SAP_SYSNR') or config_values.get('sysnr', '00')

    if not args.client:
        args.client = os.getenv('SAP_CLIENT') or config_values.get('client')

    if not args.port:
        port = os.getenv('SAP_PORT')
        if port:
            try:
                args.port = int(port)
            except ValueError as exc:
                raise SAPCliConfigError(f"SAP_PORT must be an integer, got: '{port}'") from exc
        elif 'port' in config_values:
            try:
                args.port = int(config_values['port'])
            except (ValueError, TypeError) as exc:
                raise SAPCliConfigError(f"Config port must be an integer, got: '{config_values['port']}'") from exc
        else:
            args.port = 443

    if args.ssl is None:
        ssl = os.getenv('SAP_SSL')
        if ssl is not None:
            args.ssl = ssl.lower() not in _FALSE_TOKENS
        elif 'ssl' in config_values:
            args.ssl = _normalize_bool(config_values['ssl'])
        else:
            args.ssl = True

    if args.verify is None:
        verify = os.getenv('SAP_SSL_VERIFY')
        if verify is not None:
            args.verify = verify.lower() not in _FALSE_TOKENS
        elif 'ssl_verify' in config_values:
            args.verify = _normalize_bool(config_values['ssl_verify'])
        else:
            args.verify = True

    if not args.ssl_server_cert:
        args.ssl_server_cert = os.getenv('SAP_SSL_SERVER_CERT') or config_values.get('ssl_server_cert')

    if not args.user:
        args.user = os.getenv('SAP_USER') or config_values.get('user')

    if not args.password:
        args.password = os.getenv('SAP_PASSWORD') or config_values.get('password')

    if hasattr(args, 'corrnr') and args.corrnr is None:
        args.corrnr = os.getenv('SAP_CORRNR')

    # Apply config file values for message server / SNC params
    # that may not have been set by env vars in parse_command_line
    _apply_config_extra_params(args, config_values)


def _get_config_context_values(args):
    """Load config file and resolve the active context to a flat dict."""

    config_file = getattr(args, 'config_file', None)
    if config_file is None:
        return {}

    context_name = getattr(args, 'context', None)
    if context_name is None:
        context_name = os.environ.get('SAPCLI_CONTEXT')

    result = config_file.resolve_context(context_name)

    return result if result is not None else {}


def _apply_config_extra_params(args, config_values):
    """Apply config values for message server and SNC parameters
       when they were not already set by env vars or CLI args."""

    extra_params = {
        'mshost': 'SAP_MSHOST',
        'msserv': 'SAP_MSSERV',
        'sysid': 'SAP_SYSID',
        'group': 'SAP_GROUP',
        'snc_qop': 'SNC_QOP',
        'snc_myname': 'SNC_MYNAME',
        'snc_partnername': 'SNC_PARTNERNAME',
        'snc_lib': 'SNC_LIB',
    }

    for param in extra_params:
        if not getattr(args, param, None) and param in config_values:
            setattr(args, param, config_values[param])


__all__ = [
    get_commands.__name__,
]
