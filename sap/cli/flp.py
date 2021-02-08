"""flp methods"""

import sap.cli.core
import sap.flp


class CommandGroup(sap.cli.core.CommandGroup):
    """Management for FLP Catalog"""

    def __init__(self):
        super().__init__('flp')


@CommandGroup.argument('--config', type=str, required=True, help="Configuration file path")
@CommandGroup.command()
def init(connection, args):
    """Initializes the Fiori Launchpad
    """

    builder = sap.flp.builder.Builder(connection, args.config)
    builder.run()
