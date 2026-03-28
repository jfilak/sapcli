"""sapcli config commands - manage sapcli configuration file"""

import yaml

import sap.cli.core
from sap.config import ConfigFile, MERGEABLE_SECTIONS, fetch_config_source, merge_into


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
