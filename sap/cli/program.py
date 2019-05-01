"""ADT proxy for ABAP Program (Report)"""

import sys
import sap.adt
import sap.adt.wb
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
    print(program.text)


@CommandGroup.command()
@CommandGroup.argument_corrnr()
@CommandGroup.argument('package')
@CommandGroup.argument('description')
@CommandGroup.argument('name')
def create(connection, args):
    """Creates the requested program"""

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper())
    program = sap.adt.Program(connection, args.name.upper(), package=args.package.upper(), metadata=metadata)
    program.description = args.description
    program.create(corrnr=args.corrnr)


@CommandGroup.command()
@CommandGroup.argument_corrnr()
@CommandGroup.argument('source', help='a path or - for stdin')
@CommandGroup.argument('name')
def write(connection, args):
    """Creates the requested program"""

    text = None

    if args.source == '-':
        text = sys.stdin.readlines()
    else:
        with open(args.source) as filesrc:
            text = filesrc.readlines()

    program = sap.adt.Program(connection, args.name.upper())

    with program.open_editor(corrnr=args.corrnr) as editor:
        editor.write(''.join(text))


@CommandGroup.command()
@CommandGroup.argument('name')
def activate(connection, args):
    """Actives the passed program.
    """

    program = sap.adt.Program(connection, args.name)
    sap.adt.wb.activate(program)
