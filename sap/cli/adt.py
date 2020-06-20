"""ADT configuration and parameters"""

import sap.adt
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for discovering ADT configuration"""

    def __init__(self):
        super(CommandGroup, self).__init__('adt')


@CommandGroup.command('collections')
def abapclass(connection, _):
    """List object type and supported ADT XML format versions"""

    console = sap.cli.core.get_console()

    for typ, versions in connection.collection_types.items():
        console.printout(typ)

        for ver in versions:
            console.printout(' ', ver)
