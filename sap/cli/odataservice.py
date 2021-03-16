"""
ADT proxy for odataservice commands
"""

import sap.adt.abapgit
import sap.cli.core
import sap.cli.helpers


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for odataservice"""

    def __init__(self):
        super().__init__('odataservice')


@CommandGroup.argument('binding_name')
@CommandGroup.argument('--service_version', type=str, nargs='?')
@CommandGroup.command()
def publish(connection, args):
    """ publish odata service that belongs to a service binding identified by a version
    """

    response = sap.adt.odataservice.ServiceBinding(connection, args.service_version, args.binding_name).publish()

    console = sap.cli.core.get_console()

    if response.status_code == 200:
        console.printout(
            f'Service version {args.service_version} in binding {args.binding_name} published successfully.')
    else:
        console.printerr(f'Failed to publish {args.binding_name}', response)
