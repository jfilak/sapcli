"""ATC proxy for ABAP Unit"""

import sys

from sap import get_logger
import sap.adt
import sap.adt.atc
from sap.cli.core import printout
from sap.errors import SAPCliError


def mod_log():
    """Module logger"""

    return get_logger()


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('atc')


def print_worklist_to_stream(run_results, stream, error_level=99):
    """Print results to stream"""

    pad = ''
    ret = 0
    for obj in run_results.objects:
        stream.write(f'{obj.object_type_id}/{obj.name}\n')
        finiding_pad = pad + ' '
        for finding in obj.findings:
            if int(finding.priority) <= error_level:
                ret += 1

            stream.write(f'*{finiding_pad}{finding.priority} :: {finding.check_title} :: {finding.message_title}\n')

    return 0 if ret < 1 else 1


@CommandGroup.command()
def customizing(connection, _):
    """Retrieves ATC customizing"""

    settings = sap.adt.atc.fetch_customizing(connection)

    printout('System Check Variant:', settings.system_check_variant)


@CommandGroup.argument('-m', '--max-verdicts', default=100, type=int,
                       help='Maximum number of findings; default == 100')
@CommandGroup.argument('-r', '--variant', default=None, type=str,
                       help='Executed Check Variant; default: the system variant')
@CommandGroup.argument('-e', '--error-level', default=2, type=int,
                       help='Exit with non zero if a finding with this or higher prio returned')
@CommandGroup.argument('name')
@CommandGroup.argument('type', choices=['program', 'class', 'package'])
@CommandGroup.command()
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

    objects = sap.adt.objects.ADTObjectSets()
    objects.include_object(typ(connection, args.name))

    if args.variant is None:
        settings = sap.adt.atc.fetch_customizing(connection)
        args.variant = settings.system_check_variant

    mod_log().info('Variant: %s', args.variant)

    checks = sap.adt.atc.ChecksRunner(connection, args.variant)
    results = checks.run_for(objects, max_verdicts=args.max_verdicts)

    return print_worklist_to_stream(results.worklist, sys.stdout, error_level=args.error_level)
