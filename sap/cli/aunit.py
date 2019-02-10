"""ADT proxy for ABAP Unit"""

import sap.adt
import sap.cli.core
from sap.errors import SAPCliError


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('aunit')


@CommandGroup.command()
@CommandGroup.argument('name')
@CommandGroup.argument('type', choices=['program', 'class', 'package'])
def run(connection, args):
    """Prints it out based on command line configuration.

       Exceptions:
         - SAPCliError:
           - when the given type does not belong to the type white list
    """

    types = {'program': sap.adt.Program, 'class': sap.adt.Class, 'package': sap.adt.Package}
    try:
        typ = types[args.type]
    except KeyError:
        raise SAPCliError(f'Unknown type: {args.type}')

    aunit = sap.adt.AUnit(connection)
    obj = typ(connection, args.name)
    results = aunit.execute(obj)
    print(results.text)
