"""AUnit ADT API

ABAP Unit Test framework ADT API protocol wrappers

The API protocol uses an asynchronous 3-step flow:
  1. POST /sap/bc/adt/abapunit/runs (Location header with run ID)
  2. GET  /sap/bc/adt/abapunit/runs/{id}?withLongPolling=true
  3. GET  /sap/bc/adt/abapunit/results/{id} (Accept JUnit or ABAPUnit)

os = MultiPropertyObjectSet().add_package('SOOL')
aunitRun = TestRun(os)

Test coverage:
  1. POST /sap/bc/adt/runtime/traces/coverage/measurements/{id}
     ?withAdditionalTypeInfo=true
     Response contains atom:link with rel="next" pointing to child objects.
  2. GET /sap/bc/adt/runtime/traces/coverage/results/{id}/children/{path}
"""

import xml.sax
from xml.sax.handler import ContentHandler

from sap import get_logger

from sap.adt.annotations import (
    OrderedClassMembers,
    XmlNodeProperty,
    XmlNodeAttributeProperty,
    XmlElementProperty,
    xml_element,
)
from sap.adt.marshalling import Marshal
from sap.adt.objects import XMLNamespace, ADTObjectType
from sap.adt.api.osl import MultiPropertyObjectSet, FlatObjectSet


XMLNS_ADT_API_AUNIT = XMLNamespace('aunit', 'http://www.sap.com/adt/api/aunit')

AUNIT_RUNS_BASEPATH = 'abapunit/runs'
AUNIT_RESULTS_BASEPATH = 'abapunit/results'
CONTENT_TYPE_AUNIT_RUN = 'application/vnd.sap.adt.api.abapunit.run.v2+xml'

ACCEPT_AUNIT_RESULTS = 'application/vnd.sap.adt.api.abapunit.run-result.v1+xml'
ACCEPT_JUNIT_RESULTS = 'application/vnd.sap.adt.api.junit.run-result.v1+xml'

# Mapping from sapcli human-readable types to OSL object types
OBJECT_TYPE_MAP = {
    'class': 'CLAS',
    'program': 'PROG',
    'program-include': 'PROG',
    'function-group': 'FUGR',
}


def mod_log():
    """ADT Module logger"""

    return get_logger()


# pylint: disable=too-few-public-methods
class TestScope(metaclass=OrderedClassMembers):
    """Parameters for selection of executed tests

       Usage:
         run = TestRun()
         run.options.scope.own_tests = 'true'
         run.options.scope.foreign_tests = 'false'
         run.options.scope.add_foreign_tests_as_preview = 'true'
    """

    own_tests = XmlNodeAttributeProperty(
        'ownTests',
        value='true')

    foreign_tests = XmlNodeAttributeProperty(
        'foreignTests',
        value='false')

    add_foreign_tests_as_preview = XmlNodeAttributeProperty(
        'addForeignTestsAsPreview',
        value='true')


class TestMeasurements(metaclass=OrderedClassMembers):
    """Measurements of executed tests

       Usage:
         run = TestRun()
         run.options.measurements = TestMeasurements.coverage()
    """

    typ = XmlNodeAttributeProperty('type')

    @staticmethod
    def coverage() -> 'TestMeasurements':
        """Creates TestMeasurements with type=coverage"""
        tm = TestMeasurements()
        tm.typ = 'coverage'
        return tm


# pylint: disable=too-few-public-methods
class TestOptions(metaclass=OrderedClassMembers):
    """Complete configuration of AUnit Execution

       Usage:
         run = TestRun()
         run.options.measurements = TestMeasurements.coverage()
         run.options.scope.own_tests = 'true'
         run.options.scope.foreign_tests = 'false'
         run.options.scope.add_foreign_tests_as_preview = 'true'
         run.options.risk_level.harmless = 'true'
         run.options.risk_level.dangerous = 'true'
         run.options.risk_level.critical = 'true'
         run.options.duration.short = 'true'
         run.options.duration.medium = 'true'
         run.options.duration.long = 'true'
    """

    measurements = XmlNodeProperty('aunit:measurements', ignore_empty=True)
    scope = XmlNodeProperty('aunit:scope')
    risk_level = XmlNodeProperty('aunit:riskLevel')
    duration = XmlNodeProperty('aunit:duration')

    def __init__(self):
        # Lazy import to avoid cyclic import (sap.adt.api.aunit <-> sap.adt.aunit)
        from sap.adt.aunit import TestRiskLevelSettings, TestDurationSettings

        self.scope = TestScope()
        self.risk_level = TestRiskLevelSettings()
        self.duration = TestDurationSettings()

# Not yet coverved:
# <aunit:parallelProcessing mode="package" numberOfProcesses="4"/>


# pylint: disable=too-few-public-methods
class TestRun(metaclass=OrderedClassMembers):
    """AUnit test run request object"""

    objtype = ADTObjectType(None,
                            'abapunit/runs',
                            XMLNS_ADT_API_AUNIT,
                            'application/vnd.sap.adt.api.abapunit.run.v2+xml',
                            None,
                            'run')

    title = XmlNodeAttributeProperty('title', value='test_run')
    context = XmlNodeAttributeProperty('context', value='sapcli Python Aunit Test Runner')

    def __init__(self, objects):
        self._options = TestOptions()
        self.objectSet = objects

    @xml_element('aunit:options')
    def options(self):
        """Returns the test run options"""
        return self._options

    objectSet = XmlNodeProperty(XmlElementProperty.NAME_FROM_OBJECT)


def build_test_run(objects_info, activate_coverage=False):
    """Build a TestRun object for the API AUnit run request.

    Args:
        objects_info: list of (name, type_key) tuples where type_key is
                      a sapcli type (class, program, package, ...) or
                      an OSL type (CLAS, PROG, FUGR).
        activate_coverage: whether to enable coverage measurements

    Returns:
        TestRun object ready for serialization via Marshal().serialize()
    """

    is_package = any(obj_type == 'package' for _, obj_type in objects_info)

    if is_package:
        object_set = MultiPropertyObjectSet()
        for name, _ in objects_info:
            object_set.add_package(name.upper())
    else:
        object_set = FlatObjectSet()
        for name, obj_type in objects_info:
            osl_type = OBJECT_TYPE_MAP.get(obj_type, obj_type)
            object_set.append(osl_type, name.upper())

    test_run = TestRun(object_set)
    test_run.title = 'Run'
    test_run.context = 'ABAP Unit Test Run'
    test_run.options.scope.own_tests = 'true'
    test_run.options.scope.foreign_tests = 'true'

    if activate_coverage:
        test_run.options.measurements = TestMeasurements.coverage()

    return test_run


class AUnitRunStatus:
    """Status constants for AUnit API run"""

    FINISHED = 'FINISHED'


class AUnitRunStatusHandler(ContentHandler):
    """SAX handler for parsing AUnit API run status response"""

    def __init__(self):
        super().__init__()

        self.status = None
        self.percentage = None
        self.results_href = None

    def startElement(self, name, attrs):
        if name == 'aunit:progress':
            self.status = attrs.get('status')
            self.percentage = attrs.get('percentage')
        elif name == 'atom:link':
            if attrs.get('rel') == 'results':
                self.results_href = attrs.get('href')


class AUnit:
    """ABAP Unit tests using the API protocol (asynchronous 3-step flow)"""

    def __init__(self, connection):
        self._connection = connection

    def start_run(self, xml_body):
        """POST to start a new AUnit run, returns the run ID"""

        response = self._connection.execute(
            'POST',
            AUNIT_RUNS_BASEPATH,
            content_type=CONTENT_TYPE_AUNIT_RUN,
            body=xml_body
        )

        location = response.headers['Location']
        run_id = location.rsplit('/', 1)[1]
        return run_id

    def poll_run(self, run_id):
        """Poll for AUnit run completion, returns status handler when finished"""

        while True:
            response = self._connection.execute(
                'GET',
                f'{AUNIT_RUNS_BASEPATH}/{run_id}',
                params={'withLongPolling': 'true'}
            )

            handler = AUnitRunStatusHandler()
            xml.sax.parseString(response.text.encode('utf-8'), handler)

            if handler.status == AUnitRunStatus.FINISHED:
                return handler

            mod_log().debug(
                'AUnit run %s: status=%s percentage=%s',
                run_id, handler.status, handler.percentage)

    def fetch_results(self, run_id, accept=None):
        """Fetch the results of a completed AUnit run

        Args:
            run_id: the run identifier
            accept: result format MIME type (default: ACCEPT_AUNIT_RESULTS)
        """

        if accept is None:
            accept = ACCEPT_AUNIT_RESULTS

        return self._connection.execute(
            'GET',
            f'{AUNIT_RESULTS_BASEPATH}/{run_id}',
            accept=accept
        )

    def execute(self, test_run, accept=None):
        """Execute AUnit tests using the API protocol.

        Args:
            test_run: TestRun object to serialize and execute
            accept: result format MIME type (default: ACCEPT_AUNIT_RESULTS)

        Returns:
            Response with .text containing test results XML
        """

        xml_body = Marshal().serialize(test_run)
        run_id = self.start_run(xml_body)
        self.poll_run(run_id)
        return self.fetch_results(run_id, accept=accept)
