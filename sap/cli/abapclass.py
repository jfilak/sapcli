"""ADT proxy for ABAP Class (OO)"""

import sys
import sap.adt
import sap.adt.wb
import sap.cli.core


SOURCE_TYPES = ['main', 'definitions', 'implementations', 'testclasses']


def get_source_code_objec(clas, source_code_type):
    """Returns object based on type"""

    if source_code_type == 'definitions':
        return clas.definitions

    if source_code_type == 'implementations':
        return clas.implementations

    if source_code_type == 'testclasses':
        return clas.test_classes

    return clas


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('class')

    @classmethod
    def argument_source_type(cls):
        """Adds the --type argument"""

        return CommandGroup.argument('--type', default=SOURCE_TYPES[0], choices=SOURCE_TYPES)


@CommandGroup.argument_source_type()
@CommandGroup.argument('name')
@CommandGroup.command()
def read(connection, args):
    """Prints it out based on command line configuration.
    """

    cls = sap.adt.Class(connection, args.name)
    print(get_source_code_objec(cls, args.type).text)


@CommandGroup.argument_corrnr()
@CommandGroup.argument('package')
@CommandGroup.argument('description')
@CommandGroup.argument('name')
@CommandGroup.command()
def create(connection, args):
    """Creates the requested class"""

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper())
    clas = sap.adt.Class(connection, args.name.upper(), package=args.package.upper(), metadata=metadata)
    clas.description = args.description
    clas.create(corrnr=args.corrnr)


@CommandGroup.argument_corrnr()
@CommandGroup.argument('source', help='a path or - for stdin')
@CommandGroup.argument_source_type()
@CommandGroup.argument('name')
@CommandGroup.command()
def write(connection, args):
    """Changes main source code of the given class"""

    text = None

    if args.source == '-':
        text = sys.stdin.readlines()
    else:
        with open(args.source) as filesrc:
            text = filesrc.readlines()

    clas = sap.adt.Class(connection, args.name.upper())

    with get_source_code_objec(clas, args.type).open_editor(corrnr=args.corrnr) as editor:
        editor.write(''.join(text))


@CommandGroup.argument('name')
@CommandGroup.command()
def activate(connection, args):
    """Actives the given class.
    """

    clas = sap.adt.Class(connection, args.name)
    sap.adt.wb.activate(clas)


@CommandGroup.argument('name')
@CommandGroup.command()
def attributes(connection, args):
    """Prints out some attributes of the given class.
    """

    clas = sap.adt.Class(connection, args.name)
    clas.fetch()

    print(f'Name       : {clas.name}')
    print(f'Description: {clas.description}')
    print(f'Responsible: {clas.responsible}')
    # pylint: disable=no-member
    print(f'Package    : {clas.reference.name}')
