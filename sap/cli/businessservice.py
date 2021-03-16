"""
ADT proxy for businessservice commands
"""

import sap.adt.abapgit
import sap.cli.core
import sap.cli.helpers


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for businessservice"""

    def __init__(self):
        super().__init__('businessservice')


@CommandGroup.argument('service_name')
@CommandGroup.argument('binding_name')
@CommandGroup.command()
def publish(connection, args):
    """ publish odata service that belongs to a service binding identified by a version
    """

    binding = sap.adt.businessservice.ServiceBinding(connection, args.binding_name)
    binding.fetch()

    status = binding.publish(args.service_name)

    console = sap.cli.core.get_console()

    console.printout(status.SHORT_TEXT)
    if status.LONG_TEXT:
        console.printout(status.LONG_TEXT)

    if status.SEVERITY == "OK":
        console.printout(
            f'Service version {args.service_name} in binding {args.binding_name} published successfully.')
    else:
        console.printerr(f'Failed to publish {args.binding_name}')
