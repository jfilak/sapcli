"""ADT proxy for ABAP Package (Developmen Class)"""

from collections import OrderedDict

from sap import get_logger

import sap.adt
import sap.adt.checks
from sap.adt.errors import ExceptionResourceAlreadyExists, ExceptionResourceNotFound

import sap.cli.core


def mod_log():
    """ADT Module logger"""

    return get_logger()


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Package methods
       calls.
    """

    def __init__(self):
        super().__init__('package')


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


@CommandGroup.argument('-l', '--long', default=False, action='store_true', help='Print object details')
@CommandGroup.argument('-r', '--recursive', default=False, action='store_true', help='List sub-packages')
@CommandGroup.argument('name')
@CommandGroup.command('list')
def list_package(connection, args):
    """List information about package contents"""

    package = sap.adt.Package(connection, args.name)

    console = args.console_factory()

    # Collect all items first to calculate column widths for long format
    items = []
    type_width = 0
    name_width = 0
    for pkg, subpackages, objects in sap.adt.package.walk(package, withdescr=args.long):
        basedir = '/'.join(pkg)
        if basedir:
            basedir += '/'

        if not args.recursive:
            for subpkg in subpackages:
                if args.long:
                    items.append((None, basedir, subpkg.typ, subpkg.name, subpkg.description))
                    type_width = max(type_width, len(subpkg.typ))
                    name_width = max(name_width, len(basedir) + len(subpkg.name))
                else:
                    items.append((f'{basedir}{subpkg}', None, None, None, None))

        for obj in objects:
            items.append((None, basedir, obj.typ, obj.name, obj.description))
            type_width = max(type_width, len(obj.typ))
            name_width = max(name_width, len(basedir) + len(obj.name))

        if not args.recursive:
            break

        # Print empty packages in non-long format and recursive
        if not subpackages and not objects:
            items.append((f'{basedir}', None, None, None, None))

    # Print items
    for item in items:
        if item[1] is None:  # subpackage (short format) or empty dir
            console.printout(item[0])
        else:  # object or subpackage (long format)
            _, basedir, typ, name, description = item
            if args.long:
                console.printout(f'{typ:<{type_width}}  {basedir}{name:<{name_width - len(basedir)}}  {description}')
            else:
                console.printout(f'{basedir}{name}')

    return 0


@CommandGroup.argument('name')
@CommandGroup.command('stat')
def stat(connection, args):
    """Get information about package"""

    package = sap.adt.Package(connection, args.name)

    console = args.console_factory()

    try:
        package.fetch()
    except ExceptionResourceNotFound:
        console.printerr(f'Package {args.name} not found')
        return sap.cli.core.EXIT_CODE_NOT_FOUND

    console.printout(f'Name                   :{package.name}')
    console.printout(f'Active                 :{package.active}')
    # pylint: disable=no-member
    console.printout(f'Application Component  :{package.app_component.name}')
    console.printout(f'Software Component     :{package.transport.software_component.name}')
    console.printout(f'Transport Layer        :{package.transport.transport_layer.name}')
    console.printout(f'Package Type           :{package.attributes.package_type}')

    return sap.cli.core.EXIT_CODE_OK


def _run_reporters_for_objects(connection, reporters, package_objects):

    results = []
    checks = 0
    for reporter in reporters:
        check_objects = sap.adt.checks.CheckObjectList()

        has_object = False
        for objref in package_objects:
            if reporter.supports_type(objref.typ):
                has_object = True
                mod_log().debug('Reporter %s supports %s %s', reporter.name, objref.typ, objref.name)
                check_objects.add_uri(objref.uri)

        if not has_object:
            mod_log().debug('No object for Report %s', reporter.name)
            continue

        try:
            reports = sap.adt.checks.run(connection, reporter, check_objects)
            checks += 1
        except sap.rest.errors.HTTPRequestError as ex:
            mod_log().info('Reporter %s\n%s', reporter.name, str(ex))
        else:
            results.extend(reports)

    return checks, results


# pylint: disable=too-few-public-methods
class GroupByChoice:
    """Group by options"""

    OBJECT = 'object'
    MESSAGE = 'message'


# pylint: disable=too-many-locals
def _print_out_messages(reports, checks_cntr, index, group_by, console):

    messages_cntr = 0
    warnings_cntr = 0
    errors_cntr = 0

    objects_index = OrderedDict()
    messages_index = OrderedDict()

    for report in reports:
        obj = index[report.triggering_uri]
        mod_log().debug('Processing Report: %s (%s %s %s)', report.triggering_uri, obj.typ, obj.name, obj.uri)

        for message in report.messages:
            mod_log().debug('Processing Message: %s', message.short_text)

            messages_cntr += 1

            if message.typ == 'W':
                warnings_cntr += 1
            elif message.typ == 'E':
                errors_cntr += 1

            if group_by is None:
                console.printout(f'{message.typ} :: {message.category} :: {message.short_text} :: {obj.typ} {obj.name}')
            elif group_by == GroupByChoice.OBJECT:
                items = objects_index.get(obj.uri, [])
                items.append(message)
                objects_index[obj.uri] = items
            elif group_by == GroupByChoice.MESSAGE:
                key = f'{message.typ} :: {message.category} :: {message.short_text}'
                items = messages_index.get(key, [])
                items.append(obj)
                messages_index[key] = items
            else:
                raise RuntimeError(f'Forgotten GroupByChoice {group_by}')

    for obj_uri, obj_messages in objects_index.items():
        obj = index[obj_uri]
        console.printout(f'{obj.typ} {obj.name}')
        for message in obj_messages:
            console.printout(f'* {message.typ} :: {message.category} :: {message.short_text}')

    for message, caught_objects in messages_index.items():
        console.printout(message)
        for obj in caught_objects:
            console.printout(f'* {obj.typ} {obj.name}')

    console.printout(f'Checks:   {checks_cntr}')
    console.printout(f'Messages: {messages_cntr}')
    console.printout(f'Warnings: {warnings_cntr}')
    console.printout(f'Errors:   {errors_cntr}')

    return (messages_cntr, warnings_cntr, errors_cntr)


@CommandGroup.argument('--group-by', nargs='?', choices=[GroupByChoice.OBJECT, GroupByChoice.MESSAGE],
                       help='to group output by')
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

    checks = 0
    reports = []
    index = {}
    for obj in all_objects:
        index[obj.uri] = obj

        mod_log().info('Checking object: %s %s %s', obj.typ, obj.uri, obj.name)
        runs, results = _run_reporters_for_objects(connection, reporters, [obj])
        checks += runs
        reports.extend(results)

    _, __, errors = _print_out_messages(reports, checks, index, args.group_by, args.console_factory())

    return 0 if errors == 0 else 1
