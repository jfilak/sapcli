"""
ADT proxy for New BAdI (Enhancement Implementation BAdIs) commands
"""

import sap
import sap.adt
import sap.cli.core
import sap.cli.object


def mod_log():
    """ADT Module logger"""

    return sap.get_logger()


def _get_enhancement_implementation(connection, args):
    enho = sap.adt.EnhancementImplementation(connection, args.enhancement_implementation)
    enho.fetch()
    return enho


def _list(connection, args):
    console = sap.cli.core.get_console()

    enho = _get_enhancement_implementation(connection, args)

    for badi in enho.specific.badis.implementations:
        console.printout(badi.name, badi.active, badi.implementing_class.name, badi.badi_definition.name,
                         badi.customizing_lock, badi.default, badi.example, badi.short_text)


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for BAdI"""

    def __init__(self):
        super().__init__('badi')

    def install_parser(self, arg_parser):
        super().install_parser(arg_parser)

        arg_parser.set_defaults(execute=_list)
        arg_parser.add_argument('-i', '--enhancement_implementation', help='BAdI Enhancement Implementation Name')


@CommandGroup.command('list')
def list_badis(connection, args):
    """List BAdIs for the given Enhancement Implementation name"
    """

    return _list(connection, args)


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

    console = sap.cli.core.get_console()

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
    sap.cli.object.activate_object_list(activator, ((args.enhancement_implementation, enho),), count=1)
    return 0
