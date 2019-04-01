"""ADT proxy for ABAP Interface (OO)"""

import sys
import sap.adt
import sap.adt.wb
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Interface methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('interface')


@CommandGroup.command()
@CommandGroup.argument('name')
def read(connection, args):
    """Prints it out based on command line configuration.
    """

    cls = sap.adt.Interface(connection, args.name)
    print(cls.text)


@CommandGroup.command()
@CommandGroup.argument('package')
@CommandGroup.argument('description')
@CommandGroup.argument('name')
def create(connection, args):
    """Creates the requested interface"""

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper())
    iface = sap.adt.Interface(connection, args.name.upper(), package=args.package.upper(), metadata=metadata)
    iface.description = args.description
    iface.create()


@CommandGroup.command()
@CommandGroup.argument('source', help='a path or - for stdin')
@CommandGroup.argument('name')
def write(connection, args):
    """Changes main source code of the given interface"""

    text = None

    if args.source == '-':
        text = sys.stdin.readlines()
    else:
        with open(args.source) as filesrc:
            text = filesrc.readlines()

    iface = sap.adt.Interface(connection, args.name.upper())
    # TODO: context manager
    iface.lock()
    try:
        iface.change_text(''.join(text))
    finally:
        iface.unlock()


@CommandGroup.command()
@CommandGroup.argument('name')
def activate(connection, args):
    """Activates the given interface.
    """

    iface = sap.adt.Interface(connection, args.name)
    sap.adt.wb.activate(iface)
