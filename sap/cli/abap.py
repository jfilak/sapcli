"""ABAP CLI commands"""

import sys

import sap.cli.core
import sap.cli.helpers
import sap.adt.search
import sap.adt.system
import sap.errors
import sap.platform.abap.run


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for ABAP"""

    def __init__(self):
        super().__init__('abap')


@CommandGroup.argument('--package', type=str, default=sap.platform.abap.run.DEFAULT_PACKAGE)
@CommandGroup.argument('--prefix', type=str, default=sap.platform.abap.run.DEFAULT_PREFIX)
@CommandGroup.argument('source', type=str)
@CommandGroup.command()
def run(connection, args):
    """Runs ABAP code from a file or stdin (use - for stdin)"""

    console = args.console_factory()

    if args.source == '-':
        user_code = sys.stdin.read()
    else:
        with open(args.source, 'r', encoding='utf-8') as source_file:
            user_code = source_file.read()

    result = sap.platform.abap.run.execute_abap(
        connection,
        user_code,
        prefix=args.prefix,
        package=args.package
    )

    console.printout(result)


@CommandGroup.argument('--key', type=str, default=None, help='Print only the value for the given key')
@CommandGroup.command()
def systeminfo(connection, args):
    """Prints system information"""

    console = args.console_factory()

    info = sap.adt.system.get_information(connection)

    if args.key:
        value = info.get(args.key)
        if value is not None:
            console.printout(value)
    else:
        for entry in info:
            console.printout(f'{entry.identity}: {entry.title}')


@CommandGroup.argument('--max-results', type=int, default=51, help='Maximum number of results')
@CommandGroup.argument('term', type=str)
@CommandGroup.command()
def find(connection, args):
    """Find ABAP objects by name"""

    console = args.console_factory()

    term = args.term.strip()
    if not term:
        raise sap.errors.SAPCliError('No search term provided')

    if args.max_results <= 0:
        raise sap.errors.SAPCliError(f'Maximum number of results must be positive, got: {args.max_results}')

    if not term.endswith('*'):
        term = term + '*'

    search = sap.adt.search.ADTSearch(connection)
    results = search.quick_search(term, max_results=args.max_results)

    columns = (
        sap.cli.helpers.TableWriter.Columns()
        ('typ', 'Object type')
        ('name', 'Name')
        ('description', 'Description')
        .done()
    )

    sap.cli.helpers.TableWriter(results.references, columns).printout(console)
