"""ADT proxy for ABAP Program Include"""

import sys
import sap.adt
import sap.adt.wb
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Include methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('include')


@CommandGroup.command()
@CommandGroup.argument('name')
def read(connection, args):
    """Retrieves the request command prints it out based on command line
       configuration.
    """

    include = sap.adt.Include(connection, args.name)
    print(include.text)


@CommandGroup.command()
@CommandGroup.argument_corrnr()
@CommandGroup.argument('package')
@CommandGroup.argument('description')
@CommandGroup.argument('name')
def create(connection, args):
    """Creates the given program include"""

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper())
    include = sap.adt.Include(connection, args.name.upper(), package=args.package.upper(), metadata=metadata)
    include.description = args.description
    include.create(corrnr=args.corrnr)


@CommandGroup.command()
@CommandGroup.argument_corrnr()
@CommandGroup.argument('source', help='a path or - for stdin')
@CommandGroup.argument('name')
def write(connection, args):
    """Changes source code of the given program include"""

    text = None

    if args.source == '-':
        text = sys.stdin.readlines()
    else:
        with open(args.source) as filesrc:
            text = filesrc.readlines()

    include = sap.adt.Include(connection, args.name.upper())

    with include.open_editor(corrnr=args.corrnr) as editor:
        editor.write(''.join(text))


@CommandGroup.command()
@CommandGroup.argument('-m', '--master', nargs='?', default=None, help='Master program')
@CommandGroup.argument('name')
def activate(connection, args):
    """Actives the give program include.
    """

    include = sap.adt.Include(connection, args.name, master=args.master)
    sap.adt.wb.activate(include)
