"""ADT proxy for ABAP Class (OO)"""

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('class')


@CommandGroup.command()
@CommandGroup.argument('name')
def read(connection, args):
    """Prints it out based on command line configuration.
    """

    cls = sap.adt.Class(connection, args.name)
    print cls.text
