
"""ADT proxy for CTS Workbench (Transport organizer) """

from functools import partial

from sap.errors import SAPCliError

from sap.adt.cts import WorkbenchTask, WorkbenchTransport
import sap.cli.core


EXIT_INERNAL_ERROR = 4


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.cts.*
       methods calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('cts')


@CommandGroup.command()
@CommandGroup.argument('number')
@CommandGroup.argument('type', choices=['transport', 'task'])
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
