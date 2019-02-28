"""ADT proxy for ABAP Package (Developmen Class)"""

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Package methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('package')


@CommandGroup.command()
@CommandGroup.argument('--super-package', default=None, help='Parent package name')
@CommandGroup.argument('description')
@CommandGroup.argument('name')
def create(connection, args):
    """Creates the requested ABAP package.
    """

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user)

    package = sap.adt.Package(connection, args.name.upper(), metadata=metadata)
    package.description = args.description
    package.set_package_type('development')
    package.set_software_component('LOCAL')

    if args.super_package is not None:
        package.super_package.name = args.super_package.upper()

    package.create()
