"""ATC proxy for ABAP Unit"""
import json
import os
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


def print_worklist_as_html_to_stream(run_results, stream, error_level=99):
    """Print results as html table to stream"""

    ret = 0
    stream.write('<table>\n')
    for obj in run_results.objects:
        stream.write('<tr><th>Object type ID</th>\n'
                     '<th>Name</th></tr>\n')
        stream.write(f'<tr><td>{obj.object_type_id}</td>\n'
                     f'<td>{obj.name}</td></tr>\n')
        stream.write('<tr><th>Priority</th>\n'
                     '<th>Check title</th>\n'
                     '<th>Message title</th></tr>\n')
        for finding in obj.findings:
            if int(finding.priority) <= error_level:
                ret += 1
            stream.write(f'<tr><td>{finding.priority}</td>\n'
                         f'<td>{finding.check_title}</td>\n'
                         f'<td>{finding.message_title}</td></tr>\n')

    stream.write('</table>\n')
    return 0 if ret < 1 else 1


def print_worklist_as_checkstyle_xml_to_stream(run_results, stream, error_level=99, severity_mapping=None):
    """Print results as checkstyle xml to stream"""

    CHECKSTYLE_VERSION = '8.36'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    SEVERITY_MAPPING = {
        '1': ERROR,
        '2': ERROR,
        '3': WARNING,
        '4': WARNING,
        '5': INFO
    }

    if not severity_mapping:
        severity_mapping = SEVERITY_MAPPING

    ret = 0
    stream.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    stream.write(f'<checkstyle version="{CHECKSTYLE_VERSION}">\n')
    for obj in run_results.objects:
        stream.write(f'<file name="{obj.object_type_id}/{obj.name}">\n')
        for finding in obj.findings:
            if int(finding.priority) <= error_level:
                ret += 1
            stream.write(f'<error severity="{severity_mapping.get(str(finding.priority), INFO)}" '
                         f'message="{finding.message_title}" '
                         f'source="{finding.check_title}"/>\n')
        stream.write('</file>\n')

    stream.write('</checkstyle>\n')
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
@CommandGroup.argument('-o', '--output', default='human', choices=['human', 'html', 'checkstyle'],
                       help='Output format in which checks will be printed')
@CommandGroup.argument('-s', '--severity_mapping', default=None, type=str,
                       help='Severity mapping between error levels and Checkstyle severities')
@CommandGroup.command()
def run(connection, args):
    """Prints it out based on command line configuration.

       Exceptions:
         - SAPCliError:
           - when the given type does not belong to the type white list
           - when severity_maping argument has invalid format
    """

    types = {'program': sap.adt.Program, 'class': sap.adt.Class, 'package': sap.adt.Package}
    try:
        typ = types[args.type]
    except KeyError:
        raise SAPCliError(f'Unknown type: {args.type}')

    printer_format_mapping = {
        'human': print_worklist_to_stream,
        'html': print_worklist_as_html_to_stream,
        'checkstyle': print_worklist_as_checkstyle_xml_to_stream
    }
    try:
        printer = printer_format_mapping[args.output]
    except KeyError:
        raise SAPCliError(f'Unknown format: {args.output}')

    severity_mapping = None
    if args.output == 'checkstyle':
        severity_mapping = args.severity_mapping or os.environ.get('SEVERITY_MAPPING')
        if severity_mapping:
            try:
                severity_mapping = dict(json.loads(severity_mapping))
            except (json.decoder.JSONDecodeError, TypeError):
                raise SAPCliError('Severity mapping has incorrect format')

    objects = sap.adt.objects.ADTObjectSets()
    objects.include_object(typ(connection, args.name))

    if args.variant is None:
        settings = sap.adt.atc.fetch_customizing(connection)
        args.variant = settings.system_check_variant

    mod_log().info('Variant: %s', args.variant)

    checks = sap.adt.atc.ChecksRunner(connection, args.variant)
    results = checks.run_for(objects, max_verdicts=args.max_verdicts)

    if args.output == 'checkstyle':
        result = printer(
            results.worklist, sys.stdout,
            error_level=args.error_level, severity_mapping=severity_mapping
        )
    else:
        result = printer(results.worklist, sys.stdout, error_level=args.error_level)

    return result
