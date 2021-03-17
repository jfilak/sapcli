"""
ADT proxy for service binding commands
"""

import sap.adt.abapgit
import sap.cli.core
import sap.cli.helpers


class BindingGroup(sap.cli.core.CommandGroup):
    """Container for binding commands."""

    def __init__(self):
        super().__init__('binding')


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for rap """

    def __init__(self):
        super().__init__('rap')

        self.binding_grp = BindingGroup()

    def install_parser(self, arg_parser):
        activation_group = super().install_parser(arg_parser)

        binding_parser = activation_group.add_parser(self.binding_grp.name)

        self.binding_grp.install_parser(binding_parser)


@CommandGroup.argument('binding_name', nargs='?')
@CommandGroup.argument('--service', nargs='?', default=None)
@CommandGroup.argument('--version', nargs='?', default=None)
@CommandGroup.command()
def publish(connection, args):
    """ publish odata service that belongs to a service binding identified by a version
    """

    binding = sap.adt.businessservice.ServiceBinding(connection, args.binding_name)
    binding.fetch()

    status = binding.publish(args.service, args.version)

    console = sap.cli.core.get_console()

    console.printout(status.SHORT_TEXT)
    if status.LONG_TEXT:
        console.printout(status.LONG_TEXT)

    if status.SEVERITY == "OK":
        console.printout(
            f'Service in binding {args.binding_name} published successfully.')
    else:
        console.printerr(f'Failed to publish {args.binding_name}')
