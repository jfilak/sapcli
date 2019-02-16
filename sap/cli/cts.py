"""ADT proxy for CTS Workbench (Transport organizer) """

import sys
from functools import partial

from sap.errors import SAPCliError

from sap.adt.cts import Workbench, WorkbenchTask, WorkbenchTransport
import sap.cli.core


EXIT_INERNAL_ERROR = 4
REQUEST_TYPES = ['transport', 'task']


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.cts.*
       methods calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('cts')


@CommandGroup.command()
@CommandGroup.argument('number')
@CommandGroup.argument('type', choices=REQUEST_TYPES)
def release(connection, args):
    """Releases the CTS request of the passed type and number."""

    try:
        factory = {'transport': partial(WorkbenchTransport, None),
                   'task': partial(WorkbenchTask, None, None)}[args.type]
    except KeyError:
        raise SAPCliError(f'Internal error: unknown request type: {args.type}')
    else:
        request = factory(connection, args.number)
        request.release()


# pylint: disable=invalid-name
def void_printer(_, __):
    """Prints nothing"""

    pass


def prefixed_printer(prefix, stream, output):
    """Prints with prefix"""

    stream.write(prefix + output + '\n')


def printer(stream, output):
    """Prints the passed output"""

    stream.write(output + '\n')


@CommandGroup.command(cmd_name='list')
@CommandGroup.argument('--owner')
@CommandGroup.argument('-r', '--recursive', action='count', default=0)
@CommandGroup.argument('type', choices=REQUEST_TYPES)
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
