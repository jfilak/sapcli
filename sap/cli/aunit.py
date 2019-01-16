"""ADT proxy for ABAP Unit"""

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('aunit')


@CommandGroup.command()
@CommandGroup.argument('name')
@CommandGroup.argument('type', choices=['program', 'class'])
def run(connection, args):
    """Prints it out based on command line configuration.
    """

    obj = None
    if args.type == 'program':
        obj = sap.adt.Program(connection, args.name)
    elif args.type == 'class':
        obj = sap.adt.Class(connection, args.name)

    aunit = sap.adt.AUnit(connection)
    results = aunit.execute(obj)
    print(results.text)
