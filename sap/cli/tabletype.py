"""ADT proxy for ABAP DDIC Table Type"""

import sap.adt
from sap.adt.errors import ExceptionResourceAlreadyExists
import sap.cli.object
import sap.cli.wb
from sap.cli.core import InvalidCommandLineError


ACCESS_TYPES = ['standard', 'sorted', 'hashed', 'index', 'notSpecified']
KEY_DEFINITIONS = ['standard', 'rowType', 'keyComponents', 'empty', 'notSpecified']
KEY_KINDS = ['unique', 'nonUnique', 'notSpecified']


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.TableType methods
       calls.
    """

    def __init__(self):
        super().__init__('tabletype')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.TableType(connection, name.upper(), package=package, metadata=metadata)

    def define(self):
        """Defines only the commands working with the object as a whole
           because Table Type has no source code.
        """

        cls = self.__class__

        if hasattr(cls, '_instance'):
            return None

        # pylint: disable=protected-access
        cls._instance = self

        commands = cls.get_commands()

        self.define_create(commands)
        self.define_activate(commands)
        self.define_delete(commands)
        self.define_whereused(commands)

        return commands


def _default_key_kind(key_definition):
    if key_definition in ('empty', 'notSpecified'):
        return 'notSpecified'

    return 'nonUnique'


@CommandGroup.argument_corrnr()
@CommandGroup.argument('--no-error-existing', action='store_true', default=False,
                       help='Do not fail if table type already exists')
@CommandGroup.argument('-a', '--activate', action='store_true', default=False, help='Activate after modification')
@CommandGroup.argument('--key-component', dest='key_components', action='append', default=[],
                       help='Primary key component; repeat for more components')
@CommandGroup.argument('--key-kind', choices=KEY_KINDS, default=None,
                       help='Primary key kind (default: nonUnique; notSpecified for the definitions empty and '
                            'notSpecified)')
@CommandGroup.argument('--key-definition', choices=KEY_DEFINITIONS, default='standard',
                       help='Primary key definition')
@CommandGroup.argument('--access-type', choices=ACCESS_TYPES, default='standard', help='Table access type')
@CommandGroup.argument('-r', '--row-type', required=True, help='Row type - DDIC structure name')
@CommandGroup.argument('package', help='Package assignment')
@CommandGroup.argument('description', help='Table type description')
@CommandGroup.argument('name', help='Table type name')
@CommandGroup.command()
def define(connection, args):
    """Creates the Table Type of the given DDIC structure"""

    if args.key_definition == 'keyComponents' and not args.key_components:
        raise InvalidCommandLineError('The key definition keyComponents requires at least one --key-component')

    if args.key_definition != 'keyComponents' and args.key_components:
        raise InvalidCommandLineError('--key-component can be used only with --key-definition keyComponents')

    console = args.console_factory()

    name = args.name.upper()
    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user.upper(),
                                   description=args.description)
    tabletype = sap.adt.TableType(connection, name, package=args.package.upper(), metadata=metadata)

    console.printout(f'Creating table type {name}')
    try:
        tabletype.create(corrnr=args.corrnr)
    except ExceptionResourceAlreadyExists:
        console.printout(f'Table type {name} already exists')
        if not args.no_error_existing:
            raise

    # ADT fills in the definition defaults on creation
    tabletype.fetch()

    key_kind = args.key_kind or _default_key_kind(args.key_definition)

    tabletype.set_dictionary_row_type(args.row_type.upper())
    tabletype.access_type = args.access_type
    tabletype.set_primary_key(args.key_definition, key_kind, [comp.upper() for comp in args.key_components])

    console.printout(f'Defining table type {name}')
    with tabletype.open_editor(corrnr=args.corrnr) as editor:
        editor.push()

    if not args.activate:
        return 0

    console.printout(f'Activating table type {name}')
    activator = sap.cli.wb.ObjectActivationWorker()
    return sap.cli.object.activate_object_list(activator, ((name, tabletype),), 1, console)
