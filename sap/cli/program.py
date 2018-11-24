"""ADT proxy for ABAP Program (Report)"""

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Program methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('program')


@CommandGroup.command()
@CommandGroup.argument('name')
@CommandGroup.argument('--test', action='count', default=0)
def read(connection, args):
    """Retrieves the request command prints it out based on command line
       configuration.
    """

    program = sap.adt.Program(connection, args.name)
    print program.text
