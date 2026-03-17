"""ABAP CLI commands"""

import sys

import sap.cli.core
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
