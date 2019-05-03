"""ADT proxy for Data Definition (CDS)"""

import sap.adt
import sap.adt.wb
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.DataDefinition
       methods calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('ddl')


@CommandGroup.argument('name')
@CommandGroup.command()
def read(connection, args):
    """Prints it out based on command line configuration.
    """

    ddl = sap.adt.DataDefinition(connection, args.name)
    print(ddl.text)


@CommandGroup.argument('name', nargs='+')
@CommandGroup.command()
def activate(connection, args):
    """Actives the given class.
    """

    for name in args.name:
        print(name, end=' ... ')
        ddl = sap.adt.DataDefinition(connection, name)
        sap.adt.wb.activate(ddl)
        print('DONE')
