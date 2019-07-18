"""ADT SQL Console Functions"""

import json

import sap.adt
from sap.cli.core import printout
import sap.cli.core


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.DataPreview methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('datapreview')


@CommandGroup.argument('-n', '--noheadings', action='store_true', default=False)
@CommandGroup.argument('-o', '--output', choices=['human', 'json'], default='human')
@CommandGroup.argument('--noaging', action='store_false', default=True)
@CommandGroup.argument('--rows', type=int, default=100)
@CommandGroup.argument('statement', type=str, help='ABAP SQL syntax without period')
@CommandGroup.command()
def osql(connection, args):
    """Executes OpenSQL query"""

    sqlconsole = sap.adt.DataPreview(connection)
    table = sqlconsole.execute(args.statement, rows=args.rows, aging=args.noaging)

    if args.output == 'json':
        printout(json.dumps(table, indent=2))
    else:
        header = args.noheadings
        for row in table:
            if not header:
                printout(' | '.join(row.keys()))
                header = True

            printout(' | '.join(row.values()))
