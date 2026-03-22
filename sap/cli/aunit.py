"""ADT proxy for ABAP Unit"""

import os
from collections import defaultdict
from enum import Enum
from functools import partial
from xml.sax.saxutils import escape, quoteattr
from itertools import islice
from dataclasses import dataclass
from typing import List

import sap
import sap.adt
import sap.adt.uri
import sap.adt.object_factory
import sap.adt.aunit
import sap.adt.api.aunit
import sap.adt.objects
import sap.adt.cts
import sap.cli.core
from sap.cli.core import (
    ConsoleErrorDecorator
)
import sap.adt.acoverage
from sap.adt.acoverage_statements import (
    ACoverageStatements,
    StatementsBulkRequest,
    StatementRequest,
    parse_statements_response
)
from sap.adt.errors import InvalidURIError
from sap.errors import SAPCliError


def mod_log():
    """AUnit module logger"""

    return sap.get_logger()


def create_aunit_runner(connection, compat=False):
    """Factory that returns an AUnit executor.

    Returns AUnitAPI (async, new protocol) by default.
    Returns AUnit (sync, legacy protocol) when compat=True.
    """

    if compat:
        return sap.adt.AUnit(connection)

    return sap.adt.api.aunit.AUnit(connection)


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super().__init__('aunit')


def print_aunit_human_alerts(console, alerts):
    """A helper method printing out alerts not linked to any test case
       and returning number of critical errors.
    """

    errors = 0

    for alert in alerts:
        console.printout(f'* [{alert.severity}] [{alert.kind}] - {alert.title}')
        errors = errors + 1 if alert.is_error else 0

    return errors


def print_aunit_human(run_results, console):
    """Print AUnit results in the human readable format"""

    errors = print_aunit_human_alerts(ConsoleErrorDecorator(console),
                                      run_results.alerts)

    successful = 0
    tolerable = 0
    critical = []
    for program in run_results.programs:
        console.printout(f'{program.name}')

        errors += print_aunit_human_alerts(console, program.alerts)

        for test_class in program.test_classes:
            console.printout(f'  {test_class.name}')

            errors += print_aunit_human_alerts(console, test_class.alerts)

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
                console.printout(f'    {test_method.name} [{result}]')

    if run_results.programs:
        console.printout('')

    for program, test_class, test_method in critical:
        console.printout(f'{program.name}=>{test_class.name}=>{test_method.name}')
        print_aunit_human_alerts(console, test_method.alerts)

    if critical:
        console.printout('')

    errors = errors + len(critical)

    console.printout(f'Successful: {successful}')
    console.printout(f'Warnings:   {tolerable}')
    console.printout(f'Errors:     {errors}')

    return errors


def print_acoverage_human(node, console, _indent_level=0):
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

        console.printout(f'{ident}{node.name} : {statement_coverage:.2f}%')

        print_acoverage_human(node, console, _indent_level + 1)


# pylint: disable=too-few-public-methods
@dataclass
class XMLElementContext:
    """XML Element context for a naive XML recursive writer"""

    tag: str
    indent: str
    empty: bool


class XMLWriter:
    """A naive implementation of a recursive XML writer
       which quickly and efficiently writes JUnit XML to a console.

       The class abuses ContextMangers the following way:

         with xml_writer.root('parent', bar='grc'):
            with xml_writer.element('child', attr='value'):
                with xml_writer.element('sub-child'):
                    xml_writer.text('first line', end='\n')
                    xml_writer.text('second line')

                xml_writer.element('another-sub-child', attr='empty-elem').close()

       Result:
         <?xml version="1.0" encoding="UTF-8" ?>
         <parent bar="grc">
           <child attr="value">
             <sub-child>first line
second-line</sub-child>
           </child>
         </parent>
    """

    def __init__(self, console, root_tag, **attrs):
        self._console = console

        # New line to simplify generation of text where
        # the closing tag must be on the same line.
        # We cannot print new line after the opening tag
        # because of text too - text must start on the same line.
        self._indent = '  '
        self._stack = []
        self._top = None

        self._console.printout('<?xml version="1.0" encoding="UTF-8" ?>', end='')
        self.element(root_tag, **attrs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _terminate_opening_tag(self):
        if self._top.empty:
            self._console.printout('>', end='')

    def close(self):
        """Closes open element - i.e. adds closing tag"""

        if self._top.empty:
            self._console.printout('/>', end='')
        else:
            self._console.printout(f'{self._top.indent}</{self._top.tag}>', end='')

        try:
            self._top = self._stack.pop()
        except IndexError:
            # We are closing the XML document
            self._top = None
            # so print new line at the end
            self._console.printout('')

    def element(self, tag: str, **attrs):
        """Starts new element - i.e. adds opening tag"""

        if self._top is not None:
            indent = self._top.indent + self._indent
            self._terminate_opening_tag()
            self._top.empty = False
            self._stack.append(self._top)
        else:
            indent = '\n'

        self._console.printout(f'{indent}<{tag}', end='')

        for key, value in attrs.items():
            self._console.printout(f' {key}={quoteattr(value)}', end='')

        self._top = XMLElementContext(tag, indent, True)

        return self

    def text(self, lines, end=''):
        """Adds text data to the currently written element"""

        self._terminate_opening_tag()
        self._top.empty = False
        self._top.indent = ''
        self._console.printout(escape(lines), end=end)


def print_junit4_system_err(xml_writer, details):
    """Print AUnit Alert.Details in testcase/system-err"""

    if not details:
        return

    with xml_writer.element('system-err'):
        for detail in islice(details, len(details) - 1):
            xml_writer.text(detail, end='\n')

        xml_writer.text(details[-1])


def print_junit4_testcase_error(xml_writer, alert):
    """Print AUnit Alert as JUnit4 testcase/error"""

    with xml_writer.element('error', type=alert.kind, message=alert.title):
        if not alert.stack:
            return

        for frame in islice(alert.stack, len(alert.stack) - 1):
            xml_writer.text(frame, end='\n')

        xml_writer.text(alert.stack[-1])


def print_junit4_testcase_skipped(xml_writer, alert):
    """Print AUnit Alert as JUnit4 testcase/skipped"""

    xml_writer.element('skipped', message=alert.title).close()

    if not alert.stack:
        return

    with xml_writer.element('system-out'):
        for frame in islice(alert.stack, len(alert.stack) - 1):
            xml_writer.text(frame, end='\n')

        xml_writer.text(alert.stack[-1])


def print_junit4_testcase(xml_writer, test_class, method_name, alerts):
    """Prints XML content for the give alerts and returns number of errors."""

    status = 'OK'

    if any((alert.is_error for alert in alerts)):
        status = 'ERR'
    elif any((alert.is_warning for alert in alerts)):
        status = 'SKIP'

    with xml_writer.element('testcase', name=method_name, classname=test_class, status=status):
        for alert in alerts:
            print_junit4_system_err(xml_writer, alert.details)

            if alert.is_skip:
                print_junit4_testcase_skipped(xml_writer, alert)
            else:
                print_junit4_testcase_error(xml_writer, alert)

    if status == 'ERR':
        return 1

    return 0


def print_aunit_junit4(run_results, args, console):
    """Print results to console in the form of JUnit"""

    testsuite_name = "|".join(args.name)

    # We must print alerts to STDERR because STDOUT is supposed
    # to be the JUnit XML contents.
    critical = print_aunit_human_alerts(ConsoleErrorDecorator(console),
                                        run_results.alerts)

    with XMLWriter(console, 'testsuites', name=testsuite_name) as xml_writer:
        for program in run_results.programs:
            if program.alerts:
                critical += print_junit4_testcase(xml_writer,
                                                  program.name,
                                                  program.name,
                                                  program.alerts)

            for test_class in program.test_classes:
                with xml_writer.element('testsuite',
                                        name=test_class.name,
                                        package=program.name,
                                        tests=str(len(test_class.test_methods))):

                    if test_class.alerts:
                        critical += print_junit4_testcase(xml_writer,
                                                          test_class.name,
                                                          test_class.name,
                                                          test_class.alerts)

                    if not test_class.test_methods:
                        continue

                    tc_class_name = test_class.name
                    if program.name != test_class.name:
                        tc_class_name = f'{program.name}=>{test_class.name}'

                    for test_method in test_class.test_methods:
                        critical += print_junit4_testcase(xml_writer,
                                                          tc_class_name,
                                                          test_method.name,
                                                          test_method.alerts)

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


def print_sonar_alert(alert, console):
    """Print AUnit Alert as sonar message"""

    def print_alert():
        for line in alert.details:
            console.printout(escape(line))

        if alert.details and alert.stack:
            console.printout('')

        for frame in alert.stack:
            console.printout(escape(frame))

    if alert.is_error:
        console.printout(f'      <error message={quoteattr(alert.title)}>')
        print_alert()
        console.printout('      </error>')
    elif alert.is_warning:
        console.printout(f'      <skipped message={quoteattr(alert.title)}>')
        print_alert()
        console.printout('      </skipped>')


# pylint: disable=too-many-branches
def print_aunit_sonar(run_results, args, console):
    """Print results to console in the form of Sonar Generic Execution"""

    # We must print alerts to STDERR because STDOUT is supposed
    # to be the Sonar XML contents.
    critical = print_aunit_human_alerts(ConsoleErrorDecorator(console),
                                        run_results.alerts)

    console.printout('<?xml version="1.0" encoding="UTF-8" ?>')
    console.printout('<testExecutions version="1">')

    for program in run_results.programs:
        if program.alerts:
            console.printout(f'    <testCase name={quoteattr(program.name)} duration="0">')

            for alert in program.alerts:
                if alert.is_error:
                    critical += 1

                print_sonar_alert(alert, console)

            console.printout('    </testCase>')

        for test_class in program.test_classes:
            for requested_name in args.name:
                filename = find_testclass(requested_name, program.name, test_class.name, file_required=True)
                if filename is not None:
                    break
            else:
                package = args.name[0] if len(args.name) == 1 else 'UNKNOWN_PACKAGE'
                filename = find_testclass(package, program.name, test_class.name, file_required=False)

            console.printout(f'  <file path={quoteattr(filename)}>')

            for test_method in test_class.test_methods:
                console.printout(f'    <testCase name={quoteattr(test_method.name)} duration="{test_method.duration}"',
                                 end='')
                if not test_method.alerts:
                    console.printout('/>')
                    continue

                console.printout('>')

                if any((alert.is_error for alert in test_method.alerts)):
                    critical += 1

                for alert in test_method.alerts:
                    print_sonar_alert(alert, console)

                console.printout('    </testCase>')

            if test_class.alerts:
                console.printout(f'    <testCase name={quoteattr(test_class.name)} duration="0">')

                for alert in test_class.alerts:
                    print_sonar_alert(alert, console)

                console.printout('    </testCase>')

            console.printout('  </file>')

    console.printout('</testExecutions>')

    return critical


def print_aunit_raw(aunit_xml, run_results, console):
    """Prints out raw AUnit XML results"""

    console.printout(aunit_xml)

    critical = 0
    for program in run_results.programs:
        for test_class in program.test_classes:
            for test_method in test_class.test_methods:
                if any((alert.is_error for alert in test_method.alerts)):
                    critical += 1

    return critical + sum((a.is_error for a in run_results.alerts))


def print_acoverage_raw(acoverage_xml, console):
    """Prints out raw ACoverage XML results"""

    console.printout(acoverage_xml)


def _format_line_ranges(lines):
    """Format a sorted list of line numbers as a coverage-style range string.

    Consecutive lines are collapsed into ranges:
      [55, 224, 225] -> '55, 224-225'
      [183, 184, 185] -> '183-185'
    """

    parts = []
    start = prev = lines[0]
    for line in lines[1:]:
        if line == prev + 1:
            prev = line
        else:
            parts.append(str(start) if start == prev else f'{start}-{prev}')
            start = prev = line
    parts.append(str(start) if start == prev else f'{start}-{prev}')
    return ', '.join(parts)


def print_missed_statements(statement_responses, console):
    """Print statements with executed=0, grouped by object and part."""

    console.printout('Missed statements:')
    groups = {}
    for response in statement_responses:
        for statement in response.statements:
            if statement.executed == '0':
                try:
                    position = statement.get_position()
                except InvalidURIError:
                    continue
                lines = list(range(position.start_line, position.end_line + 1))
                groups.setdefault((position.object_name, position.object_part), []).extend(lines)

    for (object_name, object_part), lines in groups.items():
        console.printout(f'{object_name} ({object_part})')
        console.printout(f'- {_format_line_ranges(lines)}')


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
            try:
                position = statement.get_position()
            except InvalidURIError:
                continue
            is_covered = bool(int(statement.executed or 0))
            # TODO: shall we expand the range?
            result[(class_name, method_name)].append((position.start_line, is_covered))

    return result


def _print_counters_jacoco(node, console, indent, indent_level):
    # pylint: disable=invalid-name
    COVERAGE_COUNTER_TYPE_MAPPING = {
        'branch': 'BRANCH',
        'procedure': 'METHOD',
        'statement': 'INSTRUCTION',
    }

    for coverage in node.coverages:
        coverage_type = COVERAGE_COUNTER_TYPE_MAPPING[coverage.type]
        missed = coverage.total - coverage.executed
        console.printout(f'{indent * indent_level}<counter type="{coverage_type}" missed="{missed}" '
                         f'covered="{coverage.executed}"/>')


def _print_source_file_jacoco(file_name, lines_data, console, indent, indent_level):
    file_level_indent = indent * indent_level
    line_level_indent = indent * (indent_level + 1)

    console.printout(f'{file_level_indent}<sourcefile name="{file_name}">')
    for line_number, is_covered in lines_data:
        covered_instructions = '1' if is_covered else '0'
        missed_instructions = '0' if is_covered else '1'

        console.printout(f'{line_level_indent}<line nr="{line_number}" mi="{missed_instructions}" '
                         f'ci="{covered_instructions}" mb="" cb=""/>')

    console.printout(f'{file_level_indent}</sourcefile>')


def _print_class_jacoco(node, method_lines_mapping, console, indent, indent_level):
    class_level_indent = indent * indent_level
    method_level_indent = indent * (indent_level + 1)

    if len(node.name) == 32:
        if node.nodes:
            node = node.nodes[0]
        else:
            class_name = node.name[:30].rstrip('=')
            console.printout(f'{class_level_indent}<class name="{class_name}" sourcefilename="{class_name}">')
            _print_counters_jacoco(node, console, indent, indent_level + 1)
            console.printout(f'{class_level_indent}</class>')
            return

    lines_data = []
    console.printout(f'{class_level_indent}<class name="{node.name}" sourcefilename="{node.name}">')
    for method in node.nodes:
        line, _ = sap.adt.uri.parse_object_implementation_start_uri(method.uri)
        console.printout(f'{method_level_indent}<method name="{method.name}" desc="" line="{line}">')
        _print_counters_jacoco(method, console, indent, indent_level + 2)
        console.printout(f'{method_level_indent}</method>')

        lines_data += method_lines_mapping[(node.name, method.name)]

    _print_counters_jacoco(node, console, indent, indent_level + 1)
    console.printout(f'{class_level_indent}</class>')
    _print_source_file_jacoco(node.name, lines_data, console, indent, indent_level)


def _print_package_jacoco(node, method_lines_mapping, console, indent, indent_level):
    for package in node.nodes:
        console.printout(f'{indent}<package name="{package.name}">')
        for class_node in package.nodes:
            _print_class_jacoco(class_node, method_lines_mapping, console, indent, indent_level + 1)
        _print_counters_jacoco(package, console, indent, indent_level + 1)
        console.printout(f'{indent}</package>')

    _print_counters_jacoco(node, console, indent, indent_level)


def print_acoverage_jacoco(root_node, statement_responses, args, console):
    """Print results of ACoverage to console in the form of JaCoCo"""

    method_lines_mapping = get_method_lines_mapping(statement_responses)

    # pylint: disable=invalid-name
    INDENT = '   '
    console.printout('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    console.printout('<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">')

    report_name = "|".join(args.name)
    console.printout(f'<report name={quoteattr(report_name)}>')
    _print_package_jacoco(root_node, method_lines_mapping, console, INDENT, 1)
    console.printout('</report>')


def get_acoverage_statements(connection, coverage_identifier, statement_uris):
    """Retrieve and parse acoverage statements for specific coverage identifier"""

    acoverage_statements = ACoverageStatements(connection)
    statement_requests = [StatementRequest(uri) for uri in statement_uris]
    bulk_statements = StatementsBulkRequest(coverage_identifier, statement_requests)
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


def objects_of_transport(as4user: str, connection: sap.adt.core.Connection,
                         corrnr: str) -> List[sap.adt.objects.ADTObject]:
    """Fetches transports by corrnr and the user and returns a list of testable
       objects.
    """

    transport = TransportObjectSelector(connection, corrnr)

    testable = transport.get_testable_objects(as4user)

    if not testable:
        raise SAPCliError('No testable objects found')

    return testable


def print_aunit_output(args, aunit_response, aunit_parsed_response):
    """Prints AUnit output in selected format and console"""

    console = args.console_factory()

    result = None

    run_results = aunit_parsed_response.run_results

    if args.output == 'human':
        result = print_aunit_human(run_results, console)

    elif args.output == 'raw':
        result = print_aunit_raw(aunit_response.text, run_results, console)

    elif args.output == 'junit4':
        result = print_aunit_junit4(run_results, args, console)

    elif args.output == 'sonar':
        result = print_aunit_sonar(run_results, args, console)
    else:
        raise SAPCliError(f'Unsupported output type: {args.output}')

    return result


def print_acoverage_output(args, acoverage_response, root_node, statement_responses):
    """Prints ACoverage output in selected format and console"""

    if args.coverage_output not in ('raw', 'human', 'jacoco'):
        raise SAPCliError(f'Unsupported output type: {args.coverage_output}')

    coverage_file = None
    if args.coverage_filepath:
        # pylint: disable=consider-using-with
        coverage_file = open(args.coverage_filepath, 'w+', encoding='utf8')
        console = sap.cli.core.PrintConsole(
            out_file=coverage_file,
            err_file=coverage_file
        )
    else:
        console = args.console_factory()

    if args.coverage_output == 'raw':
        print_acoverage_raw(acoverage_response.text, console)
    elif args.coverage_output == 'human':
        print_acoverage_human(root_node, console)
    elif args.coverage_output == 'jacoco':
        print_acoverage_jacoco(root_node, statement_responses, args, console)

    if args.coverage_output == 'human' and args.report_missed_lines:
        print_missed_statements(statement_responses, console)

    if coverage_file is not None:
        coverage_file.close()


class ResultOptions(Enum):
    """Options of run method results displaying"""

    ONLY_UNIT = 'unit'
    ONLY_COVERAGE = 'coverage'
    ALL = 'all'


# Mapping from ADT object classes to OSL type codes (for transport in API mode)
_ADT_OBJ_TO_OSL_TYPE = {
    sap.adt.Program: 'PROG',
    sap.adt.Class: 'CLAS',
    sap.adt.FunctionGroup: 'FUGR',
}


def _build_adt_object_sets(connection, args):
    """Build ADTObjectSets from CLI args. May raise SAPCliError."""

    objfactory = sap.adt.object_factory.human_names_factory(connection)
    objfactory.register('transport', partial(objects_of_transport, args.as4user))

    sets = sap.adt.objects.ADTObjectSets()
    for objname in args.name:
        sets.include(objfactory.make(args.type, objname))

    return sets


def _build_objects_info_for_transport(connection, args):
    """Resolve transport objects and convert to API protocol objects_info."""

    objects = objects_of_transport(args.as4user, connection, args.name[0])
    objects_info = []
    for obj in objects:
        osl_type = _ADT_OBJ_TO_OSL_TYPE.get(type(obj))
        if osl_type:
            objects_info.append((obj.name, osl_type))

    if not objects_info:
        raise SAPCliError('No testable objects found')

    return objects_info


def _build_objects_info(args):
    """Build API protocol objects_info from CLI args."""

    objects_info = []
    for name in args.name:
        if args.type == 'program-include':
            parts = name.split('\\')
            if len(parts) > 2:
                raise SAPCliError('Program include name can be: INCLUDE or MAIN\\INCLUDE')
            objects_info.append((parts[-1], args.type))
        else:
            objects_info.append((name, args.type))

    return objects_info


@CommandGroup.argument('--as4user', nargs='?', help='Auxiliary parameter for Transports')
@CommandGroup.argument('--output', choices=['raw', 'human', 'junit4', 'sonar'], default='human')
@CommandGroup.argument('name', nargs='+', type=str)
@CommandGroup.argument('type', choices=['program', 'program-include', 'class', 'package', 'transport'])
@CommandGroup.argument('--result',
                       choices=[
                           ResultOptions.ONLY_UNIT.value,
                           ResultOptions.ONLY_COVERAGE.value,
                           ResultOptions.ALL.value],
                       default=ResultOptions.ONLY_UNIT.value
                       )
@CommandGroup.argument('--coverage-output', choices=['raw', 'human', 'jacoco'], default='human')
@CommandGroup.argument('--coverage-filepath', default=None, type=str)
@CommandGroup.argument('--report-missed-lines', action='store_true', default=False)
@CommandGroup.argument('--compat', action='store_true', default=False,
                       help='Use the deprecated non-public ADT AUnit protocol')
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
    activate_coverage = args.result in (ResultOptions.ONLY_COVERAGE.value, ResultOptions.ALL.value)
    console = args.console_factory()

    if args.compat:
        # Legacy synchronous protocol
        try:
            sets = _build_adt_object_sets(connection, args)
        except SAPCliError as ex:
            console.printerr(str(ex))
            return 1

        aunit = sap.adt.AUnit(connection)
        aunit_response = aunit.execute(sets, activate_coverage=activate_coverage)
    else:
        # API asynchronous protocol (default)
        try:
            if args.type == 'transport':
                objects_info = _build_objects_info_for_transport(connection, args)
            else:
                objects_info = _build_objects_info(args)
        except SAPCliError as ex:
            console.printerr(str(ex))
            return 1

        test_run = sap.adt.api.aunit.build_test_run(objects_info, activate_coverage=activate_coverage)
        aunit_api = sap.adt.api.aunit.AUnit(connection)

        if args.output == 'junit4' and not activate_coverage:
            accept = sap.adt.api.aunit.ACCEPT_JUNIT_RESULTS
        else:
            accept = sap.adt.api.aunit.ACCEPT_AUNIT_RESULTS

        aunit_response = aunit_api.execute(test_run, accept=accept)

    if args.output == 'junit4' and not args.compat and not activate_coverage:
        if args.result in (ResultOptions.ONLY_UNIT.value, ResultOptions.ALL.value):
            console.printout(aunit_response.text)
        aunit_parsed_response = None
    else:
        aunit_parsed_response = sap.adt.aunit.parse_aunit_response(aunit_response.text)

    if aunit_parsed_response is not None \
            and args.result in (ResultOptions.ONLY_UNIT.value, ResultOptions.ALL.value):
        result = print_aunit_output(args, aunit_response, aunit_parsed_response)

    if activate_coverage:
        if not args.compat:
            try:
                sets = _build_adt_object_sets(connection, args)
            except SAPCliError as ex:
                console.printerr(str(ex))
                return 1

        acoverage = sap.adt.ACoverage(connection)
        acoverage_response = acoverage.execute(aunit_parsed_response.coverage_identifier, sets)
        parsed_acoverage_response = acoverage.parse_response(acoverage_response)

        statement_responses = get_acoverage_statements(
            connection,
            aunit_parsed_response.coverage_identifier,
            parsed_acoverage_response.statement_uris
        )

        root_node = parsed_acoverage_response.root_node
        print_acoverage_output(args, acoverage_response, root_node, statement_responses)

    return result
