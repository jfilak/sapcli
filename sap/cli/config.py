"""sapcli config commands - manage sapcli configuration file"""

import yaml

import sap.cli.core
from sap.config import (
    ConfigFile, CONNECTION_FIELDS,
    MERGEABLE_SECTIONS, fetch_config_source, merge_into,
)


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for managing sapcli configuration"""

    def __init__(self):
        super().__init__('config')


def _get_config_file(args):
    """Load the config file from args, respecting --config flag."""

    config_path = getattr(args, 'config', None)
    return ConfigFile.load(config_path)


@CommandGroup.command()
def view(_, args):
    """Show the current effective configuration"""

    config_file = _get_config_file(args)
    console = sap.cli.core.get_console()

    if not config_file.data:
        console.printout('No configuration file found.')
        return 0

    if config_file.path:
        console.printout(f'# Configuration file: {config_file.path}')

    console.printout(yaml.dump(config_file.data, default_flow_style=False, sort_keys=False).rstrip())

    return 0


@CommandGroup.argument('name', nargs='?', default=None, help='Context name to display (default: current context)')
@CommandGroup.command(cmd_name='current-context')
def current_context(_, args):
    """Show the current context name"""

    config_file = _get_config_file(args)
    console = sap.cli.core.get_console()

    if not config_file.data:
        console.printerr('No configuration file found.')
        return 1

    context_name = getattr(args, 'name', None)

    if context_name is not None:
        if context_name not in config_file.contexts:
            console.printerr(f'Context \'{context_name}\' not found in configuration file.')
            return 1
    else:
        context_name = config_file.current_context
        if context_name is None:
            console.printerr('No current context is set.')
            return 1

    console.printout(context_name)

    return 0


@CommandGroup.argument('name', help='Context name to switch to')
@CommandGroup.command(cmd_name='use-context')
def use_context(_, args):
    """Switch the active context"""

    config_file = _get_config_file(args)
    console = sap.cli.core.get_console()

    if not config_file.data:
        console.printerr('No configuration file found.')
        return 1

    # Validate the context exists
    contexts = config_file.contexts
    if args.name not in contexts:
        console.printerr(f'Context \'{args.name}\' not found in configuration file.')
        return 1

    config_file.current_context = args.name
    config_file.save()

    console.printout(f'Switched to context \'{args.name}\'.')

    return 0


@CommandGroup.command(cmd_name='get-contexts')
def get_contexts(_, args):
    """List available contexts"""

    config_file = _get_config_file(args)
    console = sap.cli.core.get_console()

    contexts = config_file.contexts
    if not contexts:
        console.printout('No contexts defined.')
        return 0

    current = config_file.current_context

    for name in contexts:
        marker = '*' if name == current else ' '
        ctx = contexts[name]
        connection = ctx.get('connection', '')
        user = ctx.get('user', '')
        console.printout(f'{marker} {name:<20s} {connection:<20s} {user}')

    return 0


@CommandGroup.argument('--insecure', action='store_true', default=False,
                       help='Allow plain HTTP source URLs (not recommended)')
@CommandGroup.argument('--overwrite', action='store_true', default=False,
                       help='Overwrite existing entries with source values')
@CommandGroup.argument('--source', required=True,
                       help='Path or HTTPS URL to the source configuration file')
@CommandGroup.command()
def merge(_, args):
    """Merge a source configuration into the user config"""

    console = sap.cli.core.get_console()

    # --skip-ssl-validation is a global flag (dest='verify', store_false,
    # default=None). Treat None as True (verify by default).
    ssl_verify = getattr(args, 'verify', None)
    if ssl_verify is None:
        ssl_verify = True

    source_data = fetch_config_source(args.source, insecure=args.insecure,
                                      ssl_verify=ssl_verify)

    config_file = _get_config_file(args)

    summary = merge_into(config_file, source_data, overwrite=args.overwrite)

    config_file.save()

    has_changes = False
    for section in MERGEABLE_SECTIONS:
        added = summary['added'][section]
        if added:
            has_changes = True
            console.printout(f'Added {section}: {", ".join(added)}')

    for section in MERGEABLE_SECTIONS:
        skipped = summary['skipped'][section]
        if skipped:
            has_changes = True
            console.printout(f'Skipped {section} (already exist): {", ".join(skipped)}')

    if not has_changes:
        console.printout('Nothing to merge.')

    return 0


# -- Helpers for set-* commands -----------------------------------------------

def _collect_fields(args, field_names):
    """Collect non-None fields from parsed args into a dict."""

    fields = {}
    for field in field_names:
        value = getattr(args, field, None)
        if value is not None:
            fields[field] = value
    return fields


# -- set-connection -----------------------------------------------------------

@CommandGroup.argument('--snc-lib', dest='snc_lib', default=None,
                       help='Path to SNC library')
@CommandGroup.argument('--snc-partnername', dest='snc_partnername', default=None,
                       help='SNC partner name')
@CommandGroup.argument('--snc-myname', dest='snc_myname', default=None,
                       help='SNC my name')
@CommandGroup.argument('--snc-qop', dest='snc_qop', default=None,
                       help='SNC quality of protection')
@CommandGroup.argument('--group', default=None,
                       help='Logon group')
@CommandGroup.argument('--sysid', default=None,
                       help='System ID')
@CommandGroup.argument('--msserv', default=None,
                       help='Message server service/port')
@CommandGroup.argument('--mshost', default=None,
                       help='Message server host')
@CommandGroup.argument('--ssl-server-cert', dest='ssl_server_cert', default=None,
                       help='Path to SSL server certificate')
@CommandGroup.argument('--no-ssl-verify', dest='ssl_verify', action='store_false', default=None,
                       help='Disable SSL certificate verification')
@CommandGroup.argument('--ssl-verify', dest='ssl_verify', action='store_true', default=None,
                       help='Enable SSL certificate verification')
@CommandGroup.argument('--no-ssl', dest='ssl', action='store_false', default=None,
                       help='Disable SSL')
@CommandGroup.argument('--ssl', dest='ssl', action='store_true', default=None,
                       help='Enable SSL')
@CommandGroup.argument('--port', type=int, default=None,
                       help='TCP port')
@CommandGroup.argument('--client', default=None,
                       help='SAP client number')
@CommandGroup.argument('--sysnr', default=None,
                       help='System number')
@CommandGroup.argument('--ashost', default=None,
                       help='Application server host')
@CommandGroup.argument('name', help='Connection name')
@CommandGroup.command(cmd_name='set-connection')
def set_connection(_, args):
    """Create or update a named connection"""

    fields = _collect_fields(args, CONNECTION_FIELDS)
    if not fields:
        console = sap.cli.core.get_console()
        console.printerr('No connection fields specified.')
        return 1

    config_file = _get_config_file(args)
    is_new = args.name not in config_file.connections
    config_file.set_connection(args.name, fields)
    config_file.save()

    console = sap.cli.core.get_console()
    action = 'Created' if is_new else 'Updated'
    console.printout(f'{action} connection \'{args.name}\'.')

    return 0


# -- delete-connection --------------------------------------------------------

@CommandGroup.argument('--force', action='store_true', default=False,
                       help='Delete even if referenced by contexts')
@CommandGroup.argument('name', help='Connection name to delete')
@CommandGroup.command(cmd_name='delete-connection')
def delete_connection(_, args):
    """Delete a named connection"""

    config_file = _get_config_file(args)
    config_file.delete_connection(args.name, force=args.force)
    config_file.save()

    console = sap.cli.core.get_console()
    console.printout(f'Deleted connection \'{args.name}\'.')

    return 0


# -- get-connections ----------------------------------------------------------

@CommandGroup.command(cmd_name='get-connections')
def get_connections(_, args):
    """List all connections"""

    config_file = _get_config_file(args)
    console = sap.cli.core.get_console()

    connections = config_file.connections
    if not connections:
        console.printout('No connections defined.')
        return 0

    for name, conn in connections.items():
        if not isinstance(conn, dict):
            continue
        ashost = conn.get('ashost', conn.get('mshost', ''))
        client = conn.get('client', '')
        console.printout(f'  {name:<20s} {ashost:<30s} {client}')

    return 0


# -- set-user -----------------------------------------------------------------

@CommandGroup.argument('--password', default=None,
                       help='Password')
@CommandGroup.argument('--user', dest='user_value', default=None,
                       help='SAP user alias')
@CommandGroup.argument('name', help='User entry name')
@CommandGroup.command(cmd_name='set-user')
def set_user(_, args):
    """Create or update a named user"""

    fields = {}
    if args.user_value is not None:
        fields['user'] = args.user_value
    if args.password is not None:
        fields['password'] = args.password

    if not fields:
        console = sap.cli.core.get_console()
        console.printerr('No user fields specified.')
        return 1

    config_file = _get_config_file(args)
    is_new = args.name not in config_file.users
    config_file.set_user(args.name, fields)
    config_file.save()

    console = sap.cli.core.get_console()
    action = 'Created' if is_new else 'Updated'
    console.printout(f'{action} user \'{args.name}\'.')

    return 0


# -- delete-user --------------------------------------------------------------

@CommandGroup.argument('--force', action='store_true', default=False,
                       help='Delete even if referenced by contexts')
@CommandGroup.argument('name', help='User entry name to delete')
@CommandGroup.command(cmd_name='delete-user')
def delete_user(_, args):
    """Delete a named user"""

    config_file = _get_config_file(args)
    config_file.delete_user(args.name, force=args.force)
    config_file.save()

    console = sap.cli.core.get_console()
    console.printout(f'Deleted user \'{args.name}\'.')

    return 0


# -- get-users ----------------------------------------------------------------

@CommandGroup.command(cmd_name='get-users')
def get_users(_, args):
    """List all users"""

    config_file = _get_config_file(args)
    console = sap.cli.core.get_console()

    users = config_file.users
    if not users:
        console.printout('No users defined.')
        return 0

    for name, user_def in users.items():
        if not isinstance(user_def, dict):
            continue
        user = user_def.get('user', '')
        console.printout(f'  {name:<20s} {user}')

    return 0


# -- set-context --------------------------------------------------------------

# Build set-context arguments: connection and user references,
# plus all override fields (connection + user fields).

@CommandGroup.argument('--password', dest='ctx_password', default=None,
                       help='Password override')
@CommandGroup.argument('--snc-lib', dest='snc_lib', default=None,
                       help='Path to SNC library override')
@CommandGroup.argument('--snc-partnername', dest='snc_partnername', default=None,
                       help='SNC partner name override')
@CommandGroup.argument('--snc-myname', dest='snc_myname', default=None,
                       help='SNC my name override')
@CommandGroup.argument('--snc-qop', dest='snc_qop', default=None,
                       help='SNC quality of protection override')
@CommandGroup.argument('--group', default=None,
                       help='Logon group override')
@CommandGroup.argument('--sysid', default=None,
                       help='System ID override')
@CommandGroup.argument('--msserv', default=None,
                       help='Message server service/port override')
@CommandGroup.argument('--mshost', default=None,
                       help='Message server host override')
@CommandGroup.argument('--ssl-server-cert', dest='ssl_server_cert', default=None,
                       help='Path to SSL server certificate override')
@CommandGroup.argument('--no-ssl-verify', dest='ssl_verify', action='store_false', default=None,
                       help='Disable SSL certificate verification override')
@CommandGroup.argument('--ssl-verify', dest='ssl_verify', action='store_true', default=None,
                       help='Enable SSL certificate verification override')
@CommandGroup.argument('--no-ssl', dest='ssl', action='store_false', default=None,
                       help='Disable SSL override')
@CommandGroup.argument('--ssl', dest='ssl', action='store_true', default=None,
                       help='Enable SSL override')
@CommandGroup.argument('--port', type=int, default=None,
                       help='TCP port override')
@CommandGroup.argument('--client', default=None,
                       help='SAP client number override')
@CommandGroup.argument('--sysnr', default=None,
                       help='System number override')
@CommandGroup.argument('--ashost', default=None,
                       help='Application server host override')
@CommandGroup.argument('--user', dest='user_ref', default=None,
                       help='Reference to a named user entry')
@CommandGroup.argument('--connection', default=None,
                       help='Reference to a named connection entry')
@CommandGroup.argument('name', help='Context name')
@CommandGroup.command(cmd_name='set-context')
def set_context(_, args):
    """Create or update a named context"""

    fields = {}

    # Structural references
    if args.connection is not None:
        fields['connection'] = args.connection
    if args.user_ref is not None:
        fields['user'] = args.user_ref

    # Override fields (connection fields + password)
    for field in CONNECTION_FIELDS:
        value = getattr(args, field, None)
        if value is not None:
            fields[field] = value
    if args.ctx_password is not None:
        fields['password'] = args.ctx_password

    if not fields:
        console = sap.cli.core.get_console()
        console.printerr('No context fields specified.')
        return 1

    config_file = _get_config_file(args)
    is_new = args.name not in config_file.contexts
    config_file.set_context(args.name, fields)
    config_file.save()

    console = sap.cli.core.get_console()
    action = 'Created' if is_new else 'Updated'
    console.printout(f'{action} context \'{args.name}\'.')

    return 0


# -- delete-context -----------------------------------------------------------

@CommandGroup.argument('name', help='Context name to delete')
@CommandGroup.command(cmd_name='delete-context')
def delete_context(_, args):
    """Delete a named context"""

    config_file = _get_config_file(args)
    config_file.delete_context(args.name)
    config_file.save()

    console = sap.cli.core.get_console()
    console.printout(f'Deleted context \'{args.name}\'.')

    return 0
