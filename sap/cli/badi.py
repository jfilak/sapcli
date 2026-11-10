"""
ADT proxy for New BAdI (Enhancement Implementation BAdIs) commands
"""

import sap
import sap.adt
import sap.cli.core
import sap.cli.helpers
import sap.cli.object


BADI_LIST_COLUMNS = (
    sap.cli.helpers.TableWriter.Columns()
    ('name', 'Name')
    ('active', 'Active')
    ('implementing_class.name', 'Class')
    ('badi_definition.name', 'Definition')
    ('customizing_lock', 'Customizing')
    ('default', 'Default')
    ('example', 'Example')
    ('short_text', 'Short Text')
    .done()
)


def mod_log():
    """ADT Module logger"""

    return sap.get_logger()


def _get_enhancement_implementation(connection, args):
    enho = sap.adt.EnhancementImplementation(connection, args.enhancement_implementation.upper())
    enho.fetch()
    return enho


def _list(connection, args):
    console = args.console_factory()

    enho = _get_enhancement_implementation(connection, args)

    # The default action of the command group (without the sub-command list)
    # does not have the list's arguments, hence getattr with defaults.
    noheadings = getattr(args, 'noheadings', False)
    visible_columns = getattr(args, 'columns', None)

    sap.cli.helpers.TableWriter(
        enho.specific.badis.implementations,
        BADI_LIST_COLUMNS,
        display_header=not noheadings,
        visible_columns=None if not visible_columns else visible_columns.split(',')
    ).printout(console)


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for BAdI"""

    def __init__(self):
        super().__init__('badi')

    def install_parser(self, arg_parser):
        super().install_parser(arg_parser)

        arg_parser.set_defaults(execute=_list)
        # --enhancement_implementation is the original spelling kept for backward compatibility
        arg_parser.add_argument('-i', '--enhancement-implementation', '--enhancement_implementation',
                                dest='enhancement_implementation', required=True,
                                help='BAdI Enhancement Implementation Name')


@CommandGroup.argument('--columns', type=str, default=None,
                       help=sap.cli.helpers.columns_help(BADI_LIST_COLUMNS))
@CommandGroup.argument('--noheadings', action='store_true', default=False, help='Do not print the header')
@CommandGroup.command('list')
def list_badis(connection, args):
    """List BAdIs for the given Enhancement Implementation name"
    """

    return _list(connection, args)


@CommandGroup.argument('-a', '--activate', action='store_true', default=False,
                       help='Activate the enhancement implementation after the change')
@CommandGroup.argument('--corrnr', nargs='?', default=None, help='transport number')
@CommandGroup.argument('-c', '--implementing-class', required=True,
                       help='Existing ABAP class implementing the interface of the BAdI definition')
@CommandGroup.argument('-d', '--badi-definition', required=True,
                       help='BAdI definition of the enhancement spot of the enhancement implementation;'
                            ' use "enhs list-badi-definitions" to list them')
@CommandGroup.argument('-b', '--badi', required=True, help='New BAdI implementation name')
@CommandGroup.command('create')
def create(connection, args):
    """Create a new active BAdI implementation in the enhancement implementation
    """

    console = args.console_factory()

    name = args.badi.upper()
    badi_definition = args.badi_definition.upper()
    enho_name = args.enhancement_implementation.upper()

    enho = _get_enhancement_implementation(connection, args)
    try:
        enho.specific.badis.implementations[name]
    except KeyError:
        # The BAdI does not exist yet which is exactly what we need
        pass
    else:
        raise sap.errors.SAPCliError(f'The BAdI {name} already exists in the enhancement implementation {enho_name}')

    badi = enho.add_badi_implementation(name, badi_definition, args.implementing_class.upper())

    enhs = sap.adt.EnhancementSpot(connection, badi.enhancement_spot.name)
    enhs.fetch()
    definitions = [definition.name for definition in enhs.specific.badis.definitions]
    if badi_definition not in definitions:
        raise sap.errors.SAPCliError(f'The BAdI Definition {badi_definition} not found in the enhancement spot'
                                     f' {enhs.name}; available BAdI Definitions: {", ".join(definitions)}')

    console.printout('Creating:')
    console.printout(f'* {enho_name}/{name}')
    with enho.open_editor(corrnr=args.corrnr) as editor:
        editor.push()

    if not args.activate:
        return 0

    activator = sap.cli.wb.ObjectActivationWorker()
    sap.cli.object.activate_object_list(activator, ((enho_name, enho),), 1, console)
    return 0


@CommandGroup.argument('-a', '--activate', action='store_true', default=False, help='Activate after modification')
@CommandGroup.argument('--corrnr', nargs='?', default=None, help='transport number')
@CommandGroup.argument('-b', '--badi', required=True, help='BAdI implementation name')
@CommandGroup.argument('active', choices=['true', 'false'], help='New value for Active')
@CommandGroup.command('set-active')
def set_active(connection, args):
    """Modify the active state
    """

    try:
        value = {'true': True, 'false': False}[args.active]
    except KeyError as exc:
        raise sap.errors.SAPCliError(f'BUG: unexpected value of the argument active: {args.active}') from exc

    console = args.console_factory()

    enho = _get_enhancement_implementation(connection, args)
    try:
        badi = enho.specific.badis.implementations[args.badi]
    except KeyError as exc:
        msg = f'The BAdI {args.badi} not found in the enhancement implementation {args.enhancement_implementation}'
        raise sap.errors.SAPCliError(msg) from exc

    if badi.is_active_implementation == value:
        console.printout(f'Nothing to do! The BAdI {args.badi}\'s Active is already: {args.active}')
        return 0

    badi.is_active_implementation = value

    console.printout('Updating:')
    console.printout(f'* {args.enhancement_implementation}/{args.badi}')
    with enho.open_editor(corrnr=args.corrnr) as editor:
        editor.push()

    if not args.activate:
        return 0

    activator = sap.cli.wb.ObjectActivationWorker()
    sap.cli.object.activate_object_list(activator, ((args.enhancement_implementation, enho),), 1, console)
    return 0
