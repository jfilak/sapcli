"""ADT proxy for ABAP Unit"""

import os
import re
import sys
from collections import defaultdict
from enum import Enum
from xml.sax.saxutils import escape, quoteattr
from itertools import islice

import sap

import sap.adt
import sap.adt.aunit
import sap.adt.objects
import sap.adt.cts
import sap.cli.core
import sap.adt.acoverage
from sap.adt.acoverage_statements import (
    ACoverageStatements,
    StatementsBulkRequest,
    StatementRequest,
    parse_statements_response
)
from sap.errors import SAPCliError


def mod_log():
    """AUnit module logger"""

    return sap.get_logger()


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super().__init__('aunit')


def print_aunit_human(run_results, stream):
    """Print AUnit results in the human readable format"""

    for alert in run_results.alerts:
        print(f'* [{alert.severity}] [{alert.kind}] - {alert.title}', file=stream)

    successful = 0
    tolerable = 0
    critical = []
    for program in run_results.programs:
        print(f'{program.name}', file=stream)

        for test_class in program.test_classes:
            print(f'  {test_class.name}', file=stream)

            for test_method in test_class.test_methods:
                result = None
                if any((alert.is_error for alert in test_method.alerts)):
                    result = 'ERR'
                    critical.append((program, test_class, test_method))
                elif any((alert.is_warning for alert in test_method.alerts)):
                    result = 'SKIP'
                    tolerable += 1
                else:
                    result = 'OK'
                    successful += 1
                print(f'    {test_method.name} [{result}]', file=stream)

    if run_results.programs:
        print('', file=stream)

    for program, test_class, test_method in critical:
        print(f'{program.name}=>{test_class.name}=>{test_method.name}', file=stream)
        for alert in test_method.alerts:
            print(f'*  [{alert.severity}] [{alert.kind}] - {alert.title}', file=stream)

    if critical:
        print('', file=stream)

    print(f'Successful: {successful}', file=stream)
    print(f'Warnings:   {tolerable}', file=stream)
    print(f'Errors:     {len(critical)}', file=stream)

    return len(critical)


def print_acoverage_human(node, stream, _indent_level=0):
    """Print ACoverage results in the human readable format"""

    ident = '  ' * _indent_level

    # pylint: disable=redefined-argument-from-local
    for node in node.nodes:
        statement_coverage = None
        for coverage in node.coverages:
            if coverage.type == 'statement':
                statement_coverage = (
                    coverage.executed / coverage.total * 100 if coverage.total else 0
                )

        print(f'{ident}{node.name} : {statement_coverage:.2f}%', file=stream)

        print_acoverage_human(node, stream, _indent_level + 1)


def print_junit4_system_err(stream, details, elem_pad):
    """Print AUnit Alert.Details in testcase/system-err"""

    if not details:
        return

    print(f'{elem_pad}<system-err>', file=stream, end='')

    for detail in islice(details, len(details) - 1):
        print(escape(detail), file=stream)

    print(escape(details[-1]), file=stream, end='')

    print('</system-err>', file=stream)


def print_junit4_testcase_error(stream, alert, elem_pad):
    """Print AUnit Alert as JUnit4 testcase/error"""

    print(f'{elem_pad}<error type={quoteattr(alert.kind)} message={quoteattr(alert.title)}',
          file=stream, end='')

    if not alert.stack:
        print('/>', file=stream)
        return

    print('>', file=stream, end='')

    for frame in islice(alert.stack, len(alert.stack) - 1):
        print(escape(frame), file=stream)

    print(escape(alert.stack[-1]), file=stream, end='')

    print('</error>', file=stream)


def print_aunit_junit4(run_results, args, stream):
    """Print results to stream in the form of JUnit"""

    testsuite_name = "|".join(args.name)

    print('<?xml version="1.0" encoding="UTF-8" ?>', file=stream)
    print(f'<testsuites name={quoteattr(testsuite_name)}>', file=stream)

    critical = 0
    for program in run_results.programs:
        for test_class in program.test_classes:
            print(f'  <testsuite name={quoteattr(test_class.name)} package={quoteattr(program.name)} \
tests="{len(test_class.test_methods)}"', file=stream, end='')

            if not test_class.test_methods:
                print('/>', file=stream)
                continue

            print('>', file=stream)

            tc_class_name = test_class.name
            if program.name != test_class.name:
                tc_class_name = f'{program.name}=>{test_class.name}'

            for test_method in test_class.test_methods:
                status = None

                if any((alert.is_error for alert in test_method.alerts)):
                    critical += 1
                    status = 'ERR'
                elif any((alert.is_warning for alert in test_method.alerts)):
                    status = 'SKIP'
                else:
                    status = 'OK'

                print(f'    <testcase name={quoteattr(test_method.name)} classname={quoteattr(tc_class_name)} \
status={quoteattr(status)}',
                      file=stream, end='')

                if not test_method.alerts:
                    print('/>', file=stream)
                    continue

                print('>', file=stream)

                for alert in test_method.alerts:
                    print_junit4_system_err(stream, alert.details, '      ')
                    print_junit4_testcase_error(stream, alert, '      ')

                print('    </testcase>', file=stream)

            print('  </testsuite>', file=stream)

    print('</testsuites>', file=stream)

    return critical


def find_testclass(package, program, testclass, file_required=False):
    """Find the relative path of the test-class file"""

    name = f'{program.lower()}.clas.testclasses.abap'
    for root, _, files in os.walk('.'):
        if name in files:
            return os.path.join(root, name)[2:]

    if file_required:
        return None

    return package + '/' + program + '=>' + testclass


def print_sonar_alert(alert, stream):
    """Print AUnit Alert as sonar message"""

    def print_alert():
        for line in alert.details:
            print(escape(line), file=stream)

        if alert.details and alert.stack:
            print('', file=stream)

        for frame in alert.stack:
            print(escape(frame), file=stream)

    if alert.is_error:
        print(f'      <error message={quoteattr(alert.title)}>', file=stream)
        print_alert()
        print('      </error>', file=stream)
    elif alert.is_warning:
        print(f'      <skipped message={quoteattr(alert.title)}>', file=stream)
        print_alert()
        print('      </skipped>', file=stream)


def print_aunit_sonar(run_results, args, stream):
    """Print results to stream in the form of Sonar Generic Execution"""

    print('<?xml version="1.0" encoding="UTF-8" ?>', file=stream)
    print('<testExecutions version="1">', file=stream)

    critical = 0
    for program in run_results.programs:
        for test_class in program.test_classes:
            for requested_name in args.name:
                filename = find_testclass(requested_name, program.name, test_class.name, file_required=True)
                if filename is not None:
                    break
            else:
                package = args.name[0] if len(args.name) == 1 else 'UNKNOWN_PACKAGE'
                filename = find_testclass(package, program.name, test_class.name, file_required=False)

            print(f'  <file path={quoteattr(filename)}>', file=stream)

            for test_method in test_class.test_methods:
                print(f'    <testCase name={quoteattr(test_method.name)} duration="{test_method.duration}"',
                      file=stream, end='')
                if not test_method.alerts:
                    print('/>', file=stream)
                    continue

                print('>', file=stream)

                if any((alert.is_error for alert in test_method.alerts)):
                    critical += 1

                for alert in test_method.alerts:
                    print_sonar_alert(alert, stream)

                print('    </testCase>', file=stream)

            if test_class.alerts:
                print(f'    <testCase name={quoteattr(test_class.name)} duration="0">', file=stream)

                for alert in test_class.alerts:
                    print_sonar_alert(alert, stream)

                print('    </testCase>', file=stream)

            print('  </file>', file=stream)

    print('</testExecutions>', file=stream)

    return critical


def print_aunit_raw(aunit_xml, run_results, stream):
    """Prints out raw AUnit XML results"""

    print(aunit_xml, file=stream)

    critical = 0
    for program in run_results.programs:
        for test_class in program.test_classes:
            for test_method in test_class.test_methods:
                if any((alert.is_error for alert in test_method.alerts)):
                    critical += 1

    return critical


def print_acoverage_raw(acoverage_xml, stream):
    """Prints out raw ACoverage XML results"""

    print(acoverage_xml, file=stream)


def get_line_and_column(location):
    """Finds line and column in uri"""

    # pylint: disable=invalid-name
    START_PATTERN = r'(start=)(?P<line>\d+)(,(?P<column>\d+))?'

    search_result = re.search(START_PATTERN, location or '')

    line = column = '0'
    if search_result:
        line = search_result.group('line')
        column = search_result.group('column') or '0'

    return line, column


def get_method_lines_mapping(statement_responses):
    """
    Build mapping using statement_responses
    Mapping structure: {(class_name, method_name):[(line_number, is_covered)]}
    """

    result = defaultdict(list)
    for statement_response in statement_responses:
        split_results = statement_response.name.rsplit('.', 2)
        class_name = split_results[-2]
        method_name = split_results[-1]
        for statement in statement_response.statements:
            line, _ = get_line_and_column(statement.uri)
            is_covered = bool(int(statement.executed or 0))
            result[(class_name, method_name)].append((line, is_covered))

    return result


def _print_counters_jacoco(node, stream, indent, indent_level):
    # pylint: disable=invalid-name
    COVERAGE_COUNTER_TYPE_MAPPING = {
        'branch': 'BRANCH',
        'procedure': 'METHOD',
        'statement': 'INSTRUCTION',
    }

    for coverage in node.coverages:
        coverage_type = COVERAGE_COUNTER_TYPE_MAPPING[coverage.type]
        missed = coverage.total - coverage.executed
        print(f'{indent * indent_level}<counter type="{coverage_type}" missed="{missed}" '
              f'covered="{coverage.executed}"/>', file=stream)


def _print_source_file_jacoco(file_name, lines_data, stream, indent, indent_level):
    file_level_indent = indent * indent_level
    line_level_indent = indent * (indent_level + 1)

    print(f'{file_level_indent}<sourcefile name="{file_name}">', file=stream)
    for line_number, is_covered in lines_data:
        covered_instructions = '1' if is_covered else '0'
        missed_instructions = '0' if is_covered else '1'

        print(
            f'{line_level_indent}<line nr="{line_number}" mi="{missed_instructions}" ci="{covered_instructions}">',
            file=stream
        )

    print(f'{file_level_indent}</sourcefile>', file=stream)


def _print_class_jacoco(node, method_lines_mapping, stream, indent, indent_level):
    class_level_indent = indent * indent_level
    method_level_indent = indent * (indent_level + 1)

    if len(node.name) == 32:
        if node.nodes:
            node = node.nodes[0]
        else:
            class_name = node.name[:30].rstrip('=')
            print(f'{class_level_indent}<class name="{class_name}" sourcefilename="{class_name}">', file=stream)
            _print_counters_jacoco(node, stream, indent, indent_level + 1)
            print(f'{class_level_indent}</class>', file=stream)
            return

    lines_data = []
    print(f'{class_level_indent}<class name="{node.name}" sourcefilename="{node.name}">', file=stream)
    for method in node.nodes:
        line, _ = get_line_and_column(method.uri)
        print(f'{method_level_indent}<method name="{method.name}" line="{line}">', file=stream)
        _print_counters_jacoco(method, stream, indent, indent_level + 2)
        print(f'{method_level_indent}</method>', file=stream)

        lines_data += method_lines_mapping[(node.name, method.name)]

    _print_counters_jacoco(node, stream, indent, indent_level + 1)
    print(f'{class_level_indent}</class>', file=stream)
    _print_source_file_jacoco(node.name, lines_data, stream, indent, indent_level)


def _print_package_jacoco(node, method_lines_mapping, stream, indent, indent_level):
    for package in node.nodes:
        print(f'{indent}<package name="{package.name}">', file=stream)
        for class_node in package.nodes:
            _print_class_jacoco(class_node, method_lines_mapping, stream, indent, indent_level + 1)
        _print_counters_jacoco(package, stream, indent, indent_level + 1)
        print(f'{indent}</package>', file=stream)

    _print_counters_jacoco(node, stream, indent, indent_level)


def print_acoverage_jacoco(root_node, statement_responses, args, stream):
    """Print results of ACoverage to stream in the form of JaCoCo"""

    method_lines_mapping = get_method_lines_mapping(statement_responses)

    # pylint: disable=invalid-name
    INDENT = '   '
    print('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', file=stream)
    print('<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">', file=stream)

    report_name = "|".join(args.name)
    print(f'<report name={quoteattr(report_name)}>', file=stream)
    _print_package_jacoco(root_node, method_lines_mapping, stream, INDENT, 1)
    print('</report>', file=stream)


def get_acoverage_statements(connection, coverage_identifier, statement_uris):
    """Retrieve and parse acoverage statements for specific coverage identifier"""

    acoverage_statements = ACoverageStatements(connection)
    statement_requests = [StatementRequest(uri) for uri in statement_uris]
    bulk_statements = StatementsBulkRequest(coverage_identifier, statement_requests)
    acoverage_statements = ACoverageStatements(connection)
    acoverage_statements_response = acoverage_statements.execute(bulk_statements)
    parsed_response = parse_statements_response(acoverage_statements_response.text)

    return parsed_response.statement_responses


class TransportObjectSelector:
    """Select all objects in the transport (task)"""

    def __init__(self, connection, number):
        self._connection = connection
        self._number = number

    def get_testable_objects(self, user=None):
        """Returns the list of all objects which can potentially have Unit tests
           and are included in the give transport.
        """

        types = {'PROG': sap.adt.Program, 'CLAS': sap.adt.Class, 'FUGR': sap.adt.FunctionGroup}

        mod_log().info('Fetching the transport or task %s', self._number)
        workbench = sap.adt.cts.Workbench(self._connection)
        transport = workbench.fetch_transport_request(self._number, user=user)

        if transport is None:
            raise SAPCliError(f'The transport was not found: {self._number}')

        result = []
        for task in transport.tasks:
            for abap_object in task.objects:
                mod_log().debug('? %s %s', abap_object.type, abap_object.name)

                try:
                    # TODO: get rid of the need to create the instances!
                    result.append(types[abap_object.type](self._connection, abap_object.name))
                    mod_log().info('+ %s %s', abap_object.type, abap_object.name)
                except KeyError:
                    pass

        return result


def print_aunit_output(args, aunit_response, aunit_parsed_response):
    """Prints AUnit output in selected format and stream"""

    result = None

    run_results = aunit_parsed_response.run_results

    if args.output == 'human':
        result = print_aunit_human(run_results, sys.stdout)

    elif args.output == 'raw':
        result = print_aunit_raw(aunit_response.text, run_results, sys.stdout)

    elif args.output == 'junit4':
        result = print_aunit_junit4(run_results, args, sys.stdout)

    elif args.output == 'sonar':
        result = print_aunit_sonar(run_results, args, sys.stdout)
    else:
        raise SAPCliError(f'Unsupported output type: {args.output}')

    return result


def print_acoverage_output(args, acoverage_response, root_node, statement_responses):
    """Prints ACoverage output in selected format and stream"""

    if args.coverage_output not in ('raw', 'human', 'jacoco'):
        raise SAPCliError(f'Unsupported output type: {args.coverage_output}')

    stream = open(args.coverage_filepath, 'w+') if args.coverage_filepath else sys.stdout

    if args.coverage_output == 'raw':
        print_acoverage_raw(acoverage_response.text, stream)
    elif args.coverage_output == 'human':
        print_acoverage_human(root_node, stream)
    elif args.coverage_output == 'jacoco':
        print_acoverage_jacoco(root_node, statement_responses, args, stream)

    if args.coverage_filepath:
        stream.close()


class ResultOptions(Enum):
    """Options of run method results displaying"""

    ONLY_UNIT = 'unit'
    ONLY_COVERAGE = 'coverage'
    ALL = 'all'


@CommandGroup.argument('--as4user', nargs='?', help='Auxiliary parameter for Transports')
@CommandGroup.argument('--output', choices=['raw', 'human', 'junit4', 'sonar'], default='human')
@CommandGroup.argument('name', nargs='+', type=str)
@CommandGroup.argument('type', choices=['program', 'class', 'package', 'transport'])
@CommandGroup.argument('--result',
                       choices=[
                           ResultOptions.ONLY_UNIT.value,
                           ResultOptions.ONLY_COVERAGE.value,
                           ResultOptions.ALL.value],
                       default=ResultOptions.ONLY_UNIT.value
                       )
@CommandGroup.argument('--coverage-output', choices=['raw', 'human', 'jacoco'], default='human')
@CommandGroup.argument('--coverage-filepath', default=None, type=str)
@CommandGroup.command()
def run(connection, args):
    """Prints it out based on command line configuration.

       Exceptions:
         - SAPCliError:
           - when the given type does not belong to the type white list
           - when the givent output and coverage-output do not belong to
           the output format whitelist
    """
    # pylint: disable=too-many-locals

    result = None

    types = {
        'program': sap.adt.Program,
        'class': sap.adt.Class,
        'package': sap.adt.Package,
        'transport': TransportObjectSelector
    }

    try:
        typ = types[args.type]
    except KeyError as ex:
        raise SAPCliError(f'Unknown type: {args.type}') from ex

    sets = sap.adt.objects.ADTObjectSets()

    for objname in args.name:
        obj = typ(connection, objname)

        if args.type == 'transport':
            testable = obj.get_testable_objects(args.as4user)

            if not testable:
                sap.cli.core.printerr('No testable objects found')
                return 1

            for tr_obj in testable:
                sets.include_object(tr_obj)
        else:
            sets.include_object(obj)

    aunit = sap.adt.AUnit(connection)
    activate_coverage = args.result in (ResultOptions.ONLY_COVERAGE.value, ResultOptions.ALL.value)
    aunit_response = aunit.execute(sets, activate_coverage=activate_coverage)
    aunit_parsed_response = sap.adt.aunit.parse_aunit_response(aunit_response.text)

    if args.result in (ResultOptions.ONLY_UNIT.value, ResultOptions.ALL.value):
        result = print_aunit_output(args, aunit_response, aunit_parsed_response)

    if activate_coverage:
        acoverage = sap.adt.ACoverage(connection)
        acoverage_response = acoverage.execute(aunit_parsed_response.coverage_identifier, sets)
        parsed_acoverage_response = sap.adt.acoverage.parse_acoverage_response(acoverage_response.text)

        statement_responses = get_acoverage_statements(
            connection,
            aunit_parsed_response.coverage_identifier,
            parsed_acoverage_response.statement_uris
        )

        root_node = parsed_acoverage_response.root_node

        print_acoverage_output(args, acoverage_response, root_node, statement_responses)

    return result
