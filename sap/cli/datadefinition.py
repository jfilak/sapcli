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
        super().__init__('ddl', description='CDS views')


@CommandGroup.argument('name', help='CDS view name')
@CommandGroup.command()
def read(connection, args):
    """prints source code of the given CDS view name
    """

    ddl = sap.adt.DataDefinition(connection, args.name)
    print(ddl.text)


@CommandGroup.argument('name', nargs='+', help='CDS view name')
@CommandGroup.command()
def activate(connection, args):
    """actives the given cds view
    """

    activator = sap.cli.wb.ObjectActivationWorker()
    activated_items = ((name, sap.adt.DataDefinition(connection, name)) for name in args.name)
    sap.cli.object.activate_object_list(activator, activated_items, count=len(args.name))
