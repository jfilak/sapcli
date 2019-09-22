"""ADT proxy for ABAP Package (Developmen Class)"""

from sap import get_logger

import sap.adt
import sap.adt.checks
from sap.adt.errors import ExceptionResourceAlreadyExists

import sap.cli.core


def mod_log():
    """ADT Module logger"""

    return get_logger()


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Package methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('package')


@CommandGroup.argument_corrnr()
@CommandGroup.argument('--no-error-existing', action='store_true', default=False,
                       help='Do not fail if already exists')
@CommandGroup.argument('--transport-layer', default=None, help='Transport layer')
@CommandGroup.argument('--software-component', default='LOCAL', help='Software component')
@CommandGroup.argument('--app-component', default=None, help='Application component')
@CommandGroup.argument('--super-package', default=None, help='Parent package name')
@CommandGroup.argument('description')
@CommandGroup.argument('name')
@CommandGroup.command()
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

    try:
        package.create(corrnr=args.corrnr)
    except ExceptionResourceAlreadyExists as err:
        if not args.no_error_existing:
            raise err

        mod_log().info(err.message)


@CommandGroup.argument('-r', '--recursive', default=False, action='store_true', help='List sub-packages')
@CommandGroup.argument('name')
@CommandGroup.command('list')
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


def _run_reporters_for_objects(connection, reporters, package_objects):

    results = []
    for reporter in reporters:
        check_objects = sap.adt.checks.CheckObjectList()

        for objref in package_objects:
            if reporter.supports_type(objref.typ):
                check_objects.add_uri(objref.uri)

        reports = sap.adt.checks.run(connection, reporter, check_objects)
        results.extend(reports)

    return results


def _print_out_messages(reports, console):

    messages = 0
    warnings = 0
    errors = 0

    for report in reports:
        for message in report.messages:
            messages += 1

            if message.typ == 'W':
                warnings += 1
            elif message.typ == 'E':
                errors += 1

            console.printout(f'{message.typ} :: {message.category} :: {message.short_text}')

    console.printout(f'Messages: {messages}')
    console.printout(f'Warnings: {warnings}')
    console.printout(f'Errors:   {errors}')

    return (messages, warnings, errors)


@CommandGroup.argument('-c', '--checks', nargs='*', help='name of the check reporter; default: all available')
@CommandGroup.argument('name')
@CommandGroup.command()
def check(connection, args):
    """Run ADT checks for all objects in all sub-packages"""

    reporters = sap.adt.checks.fetch_reporters(connection)
    if not reporters:
        sap.cli.core.printerr('No ADT Checks Reporters provided by the system')
        return 1

    package = sap.adt.Package(connection, args.name)

    all_objects = []
    for _, __, objects in sap.adt.package.walk(package):
        all_objects.extend(objects)

    if not all_objects:
        sap.cli.core.printerr('No objects found')
        return 1

    reports = _run_reporters_for_objects(connection, reporters, all_objects)

    _, __, errors = _print_out_messages(reports, sap.cli.core.get_console())

    return 0 if errors == 0 else 1
