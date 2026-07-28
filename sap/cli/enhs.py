"""
ADT proxy for Enhancement Spots commands
"""

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for Enhancement Spots"""

    def __init__(self):
        super().__init__('enhs')

    def install_parser(self, arg_parser):
        super().install_parser(arg_parser)

        arg_parser.add_argument('enhancement_spot', help='Enhancement Spot Name')


@CommandGroup.command('list-implementations')
def list_implementations(connection, args):
    """List Enhancement Implementations of the given Enhancement Spot
    """

    console = args.console_factory()

    enhs = sap.adt.EnhancementSpot(connection, args.enhancement_spot)
    impls = enhs.get_implementations()
    for impl in impls:
        console.printout(f'{impl}')
