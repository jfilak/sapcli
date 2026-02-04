"""ADT proxy for CTS Workbench (Transport organizer) """

import sys
from functools import partial

from sap.errors import SAPCliError

from sap.adt.cts import Workbench, WorkbenchTask, WorkbenchTransport, TransportTypes
import sap.cli.core


EXIT_INERNAL_ERROR = 4
REQUEST_TYPES = ['transport', 'task']


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.cts.*
       methods calls.
    """

    def __init__(self):
        super().__init__('cts')


@CommandGroup.argument('--transport-type', type=str,
                       default=TransportTypes.Workbench,
                       choices=TransportTypes.list_types(),
                       help='Type of transport: ' + TransportTypes.list_types_help())
@CommandGroup.argument('-t', '--target', type=str, default='LOCAL', help='Request description')
@CommandGroup.argument('-d', '--description', type=str, help='Request description')
@CommandGroup.argument('type', choices=REQUEST_TYPES)
@CommandGroup.command()
def create(connection, args):
    """Create CTS request"""

    try:
        factory = {'transport': partial(WorkbenchTransport, None, tmtype=TransportTypes.from_human_readable(args.transport_type)),
                   'task': partial(WorkbenchTask, None, None)}[args.type]
    except KeyError as ex:
        raise SAPCliError(f'Internal error: unknown request type: {args.type}') from ex

    request = factory(connection, None, owner=connection.user,
                      description=args.description, target=args.target)

    response = request.create()
    sap.cli.core.printout(response.number)

    return 0


@CommandGroup.argument('--recursive', action='store_true', default=False)
@CommandGroup.argument('number')
@CommandGroup.argument('type', choices=REQUEST_TYPES)
@CommandGroup.command()
def release(connection, args):
    """Releases the CTS request of the passed type and number."""

    try:
        factory = {'transport': partial(WorkbenchTransport, None),
                   'task': partial(WorkbenchTask, None, None)}[args.type]
    except KeyError as ex:
        raise SAPCliError(f'Internal error: unknown request type: {args.type}') from ex

    request = factory(connection, args.number)

    if args.recursive:
        sap.cli.core.printout(f'Fetching details of {args.number} because of recursive execution')
        request.fetch()

    sap.cli.core.printout(f'Releasing {args.number}')
    report = request.release(recursive=args.recursive)
    sap.cli.core.printout(str(report))

    return 0


@CommandGroup.argument('--recursive', action='store_true', default=False)
@CommandGroup.argument('number')
@CommandGroup.argument('type', choices=REQUEST_TYPES)
@CommandGroup.command()
def delete(connection, args):
    """Deletes the CTS request of the passed type and number."""

    try:
        factory = {'transport': partial(WorkbenchTransport, None),
                   'task': partial(WorkbenchTask, None, None)}[args.type]
    except KeyError as ex:
        raise SAPCliError(f'Internal error: unknown request type: {args.type}') from ex

    request = factory(connection, args.number)

    if args.recursive:
        sap.cli.core.printout(f'Fetching details of {args.number} because of recursive execution')
        request.fetch()

    sap.cli.core.printout(f'Deleting {args.number}')
    request.delete(recursive=args.recursive)
    sap.cli.core.printout(f'Deleted {args.number}')


@CommandGroup.argument('--recursive', action='store_true', default=False)
@CommandGroup.argument('owner')
@CommandGroup.argument('number')
@CommandGroup.argument('type', choices=REQUEST_TYPES)
@CommandGroup.command()
def reassign(connection, args):
    """Changes owner of the CTS request of the passed type and number."""

    try:
        factory = {'transport': partial(WorkbenchTransport, None),
                   'task': partial(WorkbenchTask, None, None)}[args.type]
    except KeyError as ex:
        raise SAPCliError(f'Internal error: unknown request type: {args.type}') from ex

    request = factory(connection, args.number)

    if args.recursive:
        sap.cli.core.printout(f'Fetching details of {args.number} because of recursive execution')
        request.fetch()

    sap.cli.core.printout(f'Re-assigning {args.number}')
    request.reassign(args.owner, recursive=args.recursive)
    sap.cli.core.printout(f'Re-assigned {args.number}')

    return 0


# pylint: disable=invalid-name
def void_printer(_, __):
    """Prints nothing"""

    # pylint: disable=unnecessary-pass
    pass


def prefixed_printer(prefix, stream, output):
    """Prints with prefix"""

    stream.write(prefix + output + '\n')


def printer(stream, output):
    """Prints the passed output"""

    stream.write(output + '\n')


@CommandGroup.argument('--owner')
@CommandGroup.argument('-r', '--recursive', action='count', default=0)
@CommandGroup.argument('number', nargs='*', type=str)
@CommandGroup.argument('type', choices=REQUEST_TYPES)
@CommandGroup.command(cmd_name='list')
def print_list(connection, args):
    """List the CTS request of the passed type."""

    printers = [
        void_printer,
        printer,
        partial(prefixed_printer, '  '),
        partial(prefixed_printer, '    ')
    ]
    recursion = args.recursive

    depth = 1
    if args.type == 'task':
        recursion += 1
        depth = 0
        task_format = '{} {} {} {}'
    else:
        task_format = '{} {} {}'

    transport_printer = printers[depth]
    depth += 1

    task_printer = printers[depth]
    depth += 1

    object_printer = printers[depth]

    workbench = Workbench(connection)

    transports = []

    if args.number:
        # TODO: handle the case where also the arg owner is provided.
        for number in args.number:
            transport = workbench.fetch_transport_request(number)

            if transport is None:
                sap.cli.core.printerr('The transport was not found:', number)
            else:
                transports.append(transport)
    else:
        transports = workbench.get_transport_requests(user=args.owner)

    for transport in transports:
        transport_printer(
            sys.stdout,
            f'{transport.number} {transport.status} {transport.owner} {transport.description}')
        if recursion - 1 >= 0:
            for task in transport.tasks:
                task_printer(
                    sys.stdout,
                    task_format.format(task.number, task.status, task.owner, task.description))
                if recursion - 2 >= 0:
                    for abap_object in task.objects:
                        object_printer(sys.stdout, f'{abap_object.type} {abap_object.name}')

    return 0
