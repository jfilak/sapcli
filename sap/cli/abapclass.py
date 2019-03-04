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
    print(cls.text)


@CommandGroup.command()
@CommandGroup.argument('package')
@CommandGroup.argument('description')
@CommandGroup.argument('name')
def create(connection, args):
    """Creates the requested class"""

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper())
    clas = sap.adt.Class(connection, args.name.upper(), package=args.package.upper(), metadata=metadata)
    clas.description = args.description
    clas.create()


@CommandGroup.command()
@CommandGroup.argument('name')
def activate(connection, args):
    """Actives the given class.
    """

    clas = sap.adt.Class(connection, args.name)
    clas.activate()
