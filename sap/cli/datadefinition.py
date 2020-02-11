"""ADT proxy for Data Definition (CDS)"""

import sap.adt
import sap.adt.wb
import sap.cli.core
import sap.cli.object


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

    activator = sap.cli.wb.ObjectActivationWorker()
    activated_items = ((name, sap.adt.DataDefinition(connection, name)) for name in args.name)
    sap.cli.object.activate_object_list(activator, activated_items, count=len(args.name))
