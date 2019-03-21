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
@CommandGroup.argument_corrnr()
@CommandGroup.argument('--transport-layer', default=None, help='Transport layer')
@CommandGroup.argument('--software-component', default='LOCAL', help='Software component')
@CommandGroup.argument('--app-component', default=None, help='Application component')
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

    package.set_software_component(args.software_component)

    if args.app_component is not None:
        package.set_app_component(args.app_component.upper())

    if args.super_package is not None:
        package.super_package.name = args.super_package.upper()

    if args.transport_layer is not None:
        package.set_transport_layer(args.transport_layer.upper())

    package.create(corrnr=args.corrnr)


@CommandGroup.command('list')
@CommandGroup.argument('-r', '--recursive', default=False, action='store_true', help='List sub-packages')
@CommandGroup.argument('name')
def list_package(connection, args):
    """List information about package contents"""

    package = sap.adt.Package(connection, args.name)

    for pkg, subpackages, objects in sap.adt.package.walk(package):
        basedir = '/'.join(pkg)
        if basedir:
            basedir += '/'

        if not args.recursive:
            for subpkg in subpackages:
                print(f'{basedir}{subpkg}')

        for obj in objects:
            print(f'{basedir}{obj.name}')

        if not args.recursive:
            break
        elif not subpackages and not objects:
            print(f'{basedir}')

    return 0
