"""
ADT proxy for Enhancement Spots commands
"""

import sap.adt
import sap.cli.core
import sap.cli.helpers


BADI_DEFINITION_COLUMNS = (
    sap.cli.helpers.TableWriter.Columns()
    ('name', 'Name')
    ('interface.name', 'Interface')
    ('single_use', 'Single Use')
    ('use_fallback_class', 'Fallback Class')
    ('short_text', 'Short Text')
    .done()
)


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for Enhancement Spots"""

    def __init__(self):
        super().__init__('enhs')


@CommandGroup.argument('enhancement_spot', help='Enhancement Spot Name')
@CommandGroup.command('list-implementations')
def list_implementations(connection, args):
    """List Enhancement Implementations of the given Enhancement Spot
    """

    console = args.console_factory()

    enhs = sap.adt.EnhancementSpot(connection, args.enhancement_spot)
    impls = enhs.get_implementations()
    for impl in impls:
        console.printout(f'{impl}')


@CommandGroup.argument('--columns', type=str, default=None,
                       help=sap.cli.helpers.columns_help(BADI_DEFINITION_COLUMNS))
@CommandGroup.argument('--noheadings', action='store_true', default=False, help='Do not print the header')
@CommandGroup.argument('enhancement_spot', help='Enhancement Spot Name')
@CommandGroup.command('list-badi-definitions')
def list_badi_definitions(connection, args):
    """List BAdI Definitions of the given Enhancement Spot;
       the Interface is the one the implementing classes must implement
    """

    console = args.console_factory()

    enhs = sap.adt.EnhancementSpot(connection, args.enhancement_spot.upper())
    enhs.fetch()

    sap.cli.helpers.TableWriter(
        enhs.specific.badis.definitions,
        BADI_DEFINITION_COLUMNS,
        display_header=not args.noheadings,
        visible_columns=None if not args.columns else args.columns.split(',')
    ).printout(console)
