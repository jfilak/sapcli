"""ADT proxy for Data Definition (CDS)"""

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.DataDefinition
       methods calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('ddl')


@CommandGroup.command()
@CommandGroup.argument('name')
def read(connection, args):
    """Prints it out based on command line configuration.
    """

    ddl = sap.adt.DataDefinition(connection, args.name)
    print(ddl.text)


@CommandGroup.command()
@CommandGroup.argument('name', nargs='+')
def activate(connection, args):
    """Actives the given class.
    """

    for name in args.name:
        print(name, end=' ... ')
        ddl = sap.adt.DataDefinition(connection, name)
        ddl.activate()
        print('DONE')
