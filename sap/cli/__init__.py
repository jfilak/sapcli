"""CLI specific functionality.

This module provides a facade for use of adt and rfc from cli.

Dependency modules are lazy loaded to enable partial modular installation.
"""


import os
from functools import partial
from types import SimpleNamespace
from sap import rfc
from sap.config import SAPCliConfigError
from sap.errors import SAPCliError
from sap.http.auth_plugin_cache import cache_key_for, get_response_store


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
        import sap.cli.transaction
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
                (adt_connection_from_args, sap.cli.transaction.CommandGroup()),
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

    # ADT's built-in login is GET on /sap/bc/adt/core/discovery (see
    # sap.adt.core.Connection); plugins use the same endpoint so the
    # cookies they collect are the ones sapcli would have collected.
    session_initializer = _build_session_initializer(
        args,
        conn_type='adt',
        conn_path='/sap/bc/adt/core/discovery',
    )

    return sap.adt.Connection(
        args.ashost, args.client, args.user, args.password,
        port=args.port, ssl=args.ssl, verify=args.verify,
        ssl_server_cert=args.ssl_server_cert,
        session_initializer=session_initializer)


def _build_session_initializer(args, conn_type=None, conn_path=None):
    """Pick the HTTPSessionInitializer for the given args.

    Precedence: auth_plugin > OAuth > None (HTTPClient falls back to
    BasicAuth). The three are mutually exclusive - the spec for
    auth_plugin says so explicitly, and OAuth+plugin would be
    nonsensical anyway since both want to own the session's auth.
    """

    if getattr(args, 'auth_plugin', None):
        # Mutual exclusivity with user/password and OAuth is enforced at
        # config-resolution time - see _resolve_auth_plugin_default. By the
        # time we get here, args.password may have been populated from env
        # (the plugin's subprocess inherits it), and that is fine.
        return _build_plugin_initializer(args, conn_type, conn_path)

    token_url = getattr(args, 'token_url', None)
    client_id = getattr(args, 'client_id', None)
    client_secret = getattr(args, 'client_secret', None)

    if not token_url and not client_id and not client_secret:
        return None

    if not token_url or not client_id or not client_secret:
        raise SAPCliError('Invalid OAuth configuration: must set all three: token_url, client_id, client_secret')

    from sap.http.oauth import OAuthHTTPSessionInitializer

    return OAuthHTTPSessionInitializer(
        token_url,
        client_id,
        client_secret,
        args.user,
        args.password,
    )


def _build_plugin_initializer(args, conn_type, conn_path):
    """Construct an HTTPExternalSessionInitializer from args.auth_plugin."""

    from sap.http.auth_plugin import ConnectionInfo
    from sap.http.external_session_initializer import (
        HTTPExternalSessionInitializer,
    )

    plugin_config = args.auth_plugin
    if not isinstance(plugin_config, dict):
        raise SAPCliError(
            "auth_plugin must be a mapping with a 'command' field"
        )

    command = plugin_config.get('command')
    if not command:
        raise SAPCliError("auth_plugin is missing required field 'command'")

    parameters = plugin_config.get('parameters') or {}

    proto = 'https' if args.ssl else 'http'
    # ConnectionInfo.port is str (matches the wire format the plugin sees).
    # args.port is int from argparse, so we coerce here rather than mutate
    # the user-facing args namespace.
    connection = ConnectionInfo(
        proto=proto,
        ashost=args.ashost,
        port=str(args.port),
        client=args.client,
        type=conn_type,
        path=conn_path,
        sysnr=getattr(args, 'sysnr', None),
        verify=bool(args.verify),
        ssl_server_cert=getattr(args, 'ssl_server_cert', None),
    )

    cache_key = getattr(args, 'auth_plugin_cache_key', None)

    # --auth-plugin-invalidate-cache drops the entry before the initializer
    # runs. The subsequent initialize_session call will then take the
    # cache-miss path and store a fresh response.
    if cache_key and getattr(args, 'auth_plugin_invalidate_cache', False):
        get_response_store().delete(cache_key)

    return HTTPExternalSessionInitializer(
        command=command,
        parameters=parameters,
        connection=connection,
        user=args.user,
        cache_key=cache_key,
    )


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

    # gCTS REST login lives at /sap/bc/cts_abapvcs/system. ABAP session
    # cookies are server-wide, so a plugin that authenticates here also
    # works for ADT/OData against the same system - cache reuse is the
    # whole point of the shared (context, connection, user) key.
    session_initializer = _build_session_initializer(
        args,
        conn_type='rest',
        conn_path='/sap/bc/cts_abapvcs/system',
    )

    return sap.rest.Connection('sap/bc/cts_abapvcs', 'system', args.ashost, args.client,
                               args.user, args.password, port=args.port, ssl=args.ssl,
                               verify=args.verify, ssl_server_cert=args.ssl_server_cert,
                               session_initializer=session_initializer)


def odata_connection_from_args(service_name, args):
    """Returns OData connection constructed from the passed args (Namespace).
    """

    import sap.odata

    session_initializer = _build_session_initializer(
        args,
        conn_type='odata',
        conn_path=f'/sap/opu/odata/{service_name}',
    )

    return sap.odata.Connection(service_name, args.ashost, args.port,
                                args.client, args.user, args.password, args.ssl,
                                args.verify, ssl_server_cert=args.ssl_server_cert,
                                session_initializer=session_initializer)


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
        token_url=None,
        client_id=None,
        client_secret=None,
        auth_plugin=None,
        auth_plugin_cache_key=None,
        auth_plugin_invalidate_cache=False,
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

    _resolve_oauth_defaults(args, config_values)

    _resolve_auth_plugin_default(args, config_values)

    if hasattr(args, 'corrnr') and args.corrnr is None:
        args.corrnr = os.getenv('SAP_CORRNR')

    # Apply config file values for message server / SNC params
    # that may not have been set by env vars in parse_command_line
    _apply_config_extra_params(args, config_values)


def _resolve_oauth_defaults(args, config_values):
    """Resolve OAuth-specific connection defaults from env vars and config file."""

    if not getattr(args, 'token_url', None):
        args.token_url = os.getenv('SAP_TOKEN_URL') or config_values.get('token_url')

    if not getattr(args, 'client_id', None):
        args.client_id = os.getenv('SAP_CLIENT_ID') or config_values.get('client_id')

    if not getattr(args, 'client_secret', None):
        args.client_secret = os.getenv('SAP_CLIENT_SECRET') or config_values.get('client_secret')


def _resolve_auth_plugin_default(args, config_values):
    """Resolve the auth_plugin definition from the config file and enforce
    its mutual exclusivity with password / OAuth at the *config* level.

    The plugin is configured purely in the config file (not via CLI flags
    or env vars) - it is a structured value, not a scalar, and its
    presence flips the whole authentication mode. Picking it up only from
    config keeps the precedence rules simple.

    Mutual exclusivity is checked against config_values rather than args
    because the plugin typically needs SAP_USER/SAP_PASSWORD env vars to
    be set so its subprocess can read them; those would land on
    args.password and trip a runtime check that has nothing to do with
    what the user actually configured.
    """

    if getattr(args, 'auth_plugin', None) is not None:
        args.auth_plugin_cache_key = _derive_cache_key(args)
        return

    plugin = config_values.get('auth_plugin')
    if not plugin:
        args.auth_plugin = None
        args.auth_plugin_cache_key = None
        return

    if config_values.get('password'):
        raise SAPCliConfigError(
            "auth_plugin and 'password' are mutually exclusive in the same "
            "user definition. Remove 'password' from the user (set "
            "SAP_PASSWORD via env if your plugin reads it)."
        )

    if any(config_values.get(k) for k in ('token_url', 'client_id', 'client_secret')):
        raise SAPCliConfigError(
            "auth_plugin and OAuth fields (token_url/client_id/client_secret) "
            "are mutually exclusive."
        )

    args.auth_plugin = plugin
    args.auth_plugin_cache_key = _derive_cache_key(args)


def _derive_cache_key(args):
    """Build the (context|connection|user) cache key for the active context.

    Returns None if any piece is missing - we never want to mint a key that
    would collide with a different (or anonymous) session. auth_plugin is
    config-only, so reaching this code means we came through a context;
    the triple is always available in normal usage.
    """

    config_file = getattr(args, 'config_file', None)
    if config_file is None:
        return None

    context_name = (
        getattr(args, 'context', None)
        or os.environ.get('SAPCLI_CONTEXT')
        or config_file.current_context
    )
    if not context_name:
        return None

    try:
        ctx = config_file.get_context(context_name)
    except SAPCliConfigError:
        return None

    connection = ctx.get('connection')
    user = ctx.get('user')
    if not connection or not user:
        return None

    return cache_key_for(context_name, connection, user)


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
