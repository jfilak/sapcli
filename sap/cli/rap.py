"""
ADT proxy for service binding commands.

Both `rap binding publish` and `rap definition activate` are deprecated
aliases kept for backwards compatibility. They emit a single-line stderr
deprecation warning and then delegate to the new `srvb publish` / `srvd
activate` code paths.
"""

import sap.adt
import sap.cli.core
import sap.cli.helpers
import sap.cli.wb
import sap.cli.object
import sap.cli.srvb
import sap.cli.srvd


_DEPRECATION_REMOVAL = 'This alias will be removed in the next minor release.'


def _deprecation_warning(old, new):
    """Format the standard deprecation warning text used by both shims."""

    return f'WARNING: `sapcli rap {old}` is deprecated; use `sapcli {new}`. {_DEPRECATION_REMOVAL}'


class DefinitionGroup(sap.cli.core.CommandGroup):
    """Container for definition commands."""

    def __init__(self):
        super().__init__('definition')


class BindingGroup(sap.cli.core.CommandGroup):
    """Container for binding commands."""

    def __init__(self):
        super().__init__('binding')


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for rap """

    def __init__(self):
        super().__init__('rap')

        self.definition_grp = DefinitionGroup()
        self.binding_grp = BindingGroup()

    def install_parser(self, arg_parser):
        activation_group = super().install_parser(arg_parser)

        binding_parser = activation_group.add_parser(self.binding_grp.name)
        self.binding_grp.install_parser(binding_parser)

        definition_parser = activation_group.add_parser(self.definition_grp.name)
        self.definition_grp.install_parser(definition_parser)


@BindingGroup.argument('--service', nargs='?', default=None,
                       help='Service name of the binding\'s services to publish')
@BindingGroup.argument('--version', nargs='?', default=None,
                       help='Version of the binding\'s services to publish')
@BindingGroup.argument('binding_name')
@BindingGroup.command()
def publish(connection, args):
    """Deprecated alias for `sapcli srvb publish`."""

    args.console_factory().printerr(_deprecation_warning('binding publish', 'srvb publish'))

    return sap.cli.srvb.publish_binding(connection, args)


@DefinitionGroup.argument('name', nargs='+')
@DefinitionGroup.command('activate')
def definition_activate(connection, args):
    """Deprecated alias for `sapcli srvd activate`."""

    args.console_factory().printerr(_deprecation_warning('definition activate', 'srvd activate'))

    # `srvd activate` (CommandGroupObjectMaster.activate_objects) reads
    # ignore_errors / warning_errors off args; the `rap` subparser does not
    # declare those flags, so default them to False to keep the legacy
    # behaviour (continue=False, warnings_as_errors=False).
    if not hasattr(args, 'ignore_errors'):
        args.ignore_errors = False
    if not hasattr(args, 'warning_errors'):
        args.warning_errors = False

    return sap.cli.srvd.CommandGroup().activate_objects(connection, args)
