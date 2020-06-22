"""ADT proxy for ABAP Unit"""

import os
import sys
from xml.sax.saxutils import escape
from itertools import islice

import sap

import sap.adt
import sap.adt.aunit
import sap.adt.objects
import sap.adt.cts
import sap.cli.core
from sap.errors import SAPCliError


def mod_log():
    """AUnit module logger"""

    return sap.get_logger()


class CommandGroup(sap.cli.core.CommandGroup):
    """Adapter converting command line parameters to sap.adt.Class methods
       calls.
    """

    def __init__(self):
        super(CommandGroup, self).__init__('aunit')


def print_results_to_stream(run_results, stream):
    """Print results to stream"""

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

    print(f'{elem_pad}<error type="{escape(alert.kind)}" message="{escape(alert.title)}"',
          file=stream, end='')

    if not alert.stack:
        print('/>', file=stream)
        return

    print('>', file=stream, end='')

    for frame in islice(alert.stack, len(alert.stack) - 1):
        print(escape(frame), file=stream)

    print(escape(alert.stack[-1]), file=stream, end='')

    print('</error>', file=stream)


def print_junit4(run_results, args, stream):
    """Print results to stream in the form of JUnit"""

    print('<?xml version="1.0" encoding="UTF-8" ?>', file=stream)
    print(f'<testsuites name="{escape(args.name)}">', file=stream)

    critical = 0
    for program in run_results.programs:
        for test_class in program.test_classes:
            print(f'  <testsuite name="{escape(test_class.name)}" package="{escape(program.name)}" \
tests="{len(test_class.test_methods)}"', file=stream, end='')

            if not test_class.test_methods:
                print('/>', file=stream)
                continue

            print('>', file=stream)

            tc_class_name = test_class.name
            if program.name != test_class.name:
                tc_class_name = f'{program.name}=>{test_class.name}'

            tc_class_name = escape(tc_class_name)

            for test_method in test_class.test_methods:
                status = None

                if any((alert.is_error for alert in test_method.alerts)):
                    critical += 1
                    status = 'ERR'
                elif any((alert.is_warning for alert in test_method.alerts)):
                    status = 'SKIP'
                else:
                    status = 'OK'

                print(f'    <testcase name="{escape(test_method.name)}" classname="{tc_class_name}" \
status="{escape(status)}"',
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


def find_testclass(package, program, testclass):
    """Find the relative path of the test-class file"""

    name = f'{program.lower()}.clas.testclasses.abap'
    for root, _, files in os.walk('.'):
        if name in files:
            return os.path.join(root, name)[2:]

    return escape(package + '/' + program + '=>' + testclass)


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
        print(f'      <error message="{escape(alert.title)}">', file=stream)
        print_alert()
        print('      </error>', file=stream)
    elif alert.is_warning:
        print(f'      <skipped message="{escape(alert.title)}">', file=stream)
        print_alert()
        print('      </skipped>', file=stream)


def print_sonar(run_results, args, stream):
    """Print results to stream in the form of Sonar Generic Execution"""

    print('<?xml version="1.0" encoding="UTF-8" ?>', file=stream)
    print('<testExecutions version="1">', file=stream)

    critical = 0
    for program in run_results.programs:
        for test_class in program.test_classes:
            filename = find_testclass(args.name, program.name, test_class.name)
            print(f'  <file path="{filename}">', file=stream)

            for test_method in test_class.test_methods:
                print(f'    <testCase name="{escape(test_method.name)}" duration="{test_method.duration}"',
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
                print(f'    <testCase name="{escape(test_class.name)}" duration="0">', file=stream)

                for alert in test_class.alerts:
                    print_sonar_alert(alert, stream)

                print('    </testCase>', file=stream)

            print('  </file>', file=stream)

    print('</testExecutions>', file=stream)

    return critical


def print_raw(aunit_xml, run_results):
    """Prints out raw XML results"""

    print(aunit_xml)

    critical = 0
    for program in run_results.programs:
        for test_class in program.test_classes:
            for test_method in test_class.test_methods:
                if any((alert.is_error for alert in test_method.alerts)):
                    critical += 1

    return critical


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


@CommandGroup.argument('--as4user', nargs='?', help='Auxiliary parameter for Transports')
@CommandGroup.argument('--output', choices=['raw', 'human', 'junit4', 'sonar'], default='human')
@CommandGroup.argument('name')
@CommandGroup.argument('type', choices=['program', 'class', 'package', 'transport'])
@CommandGroup.command()
def run(connection, args):
    """Prints it out based on command line configuration.

       Exceptions:
         - SAPCliError:
           - when the given type does not belong to the type white list
    """

    types = {'program': sap.adt.Program, 'class': sap.adt.Class, 'package': sap.adt.Package,
             'transport': TransportObjectSelector}

    try:
        typ = types[args.type]
    except KeyError:
        raise SAPCliError(f'Unknown type: {args.type}')

    obj = typ(connection, args.name)
    sets = sap.adt.objects.ADTObjectSets()

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
    response = aunit.execute(sets)
    run_results = sap.adt.aunit.parse_run_results(response.text)

    if args.output == 'human':
        return print_results_to_stream(run_results, sys.stdout)

    if args.output == 'raw':
        return print_raw(response.text, run_results)

    if args.output == 'junit4':
        return print_junit4(run_results, args, sys.stdout)

    if args.output == 'sonar':
        return print_sonar(run_results, args, sys.stdout)

    raise SAPCliError(f'Unsupported output type: {args.output}')
