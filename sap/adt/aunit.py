"""ABAP Unit Test framework ADT wrappers"""

from typing import NamedTuple, List

import xml.sax
from xml.sax.handler import ContentHandler

from sap import get_logger
from sap.adt.objects import ADTObjectType, XMLNamespace
from sap.adt.annotations import OrderedClassMembers, XmlElementProperty, XmlNodeProperty, XmlNodeAttributeProperty
from sap.adt.marshalling import Marshal


XMLNS_AUNIT = XMLNamespace('aunit', 'http://www.sap.com/adt/aunit')


def mod_log():
    """ADT Module logger"""

    return get_logger()


# pylint: disable=too-few-public-methods
class CoverageOption(metaclass=OrderedClassMembers):
    """Enabled/Disabled coverage for an ABAP Unit Test run.

       Usage:
         run = RunConfiguration()
         run.external.coverage.active = 'false'
    """

    active = XmlNodeAttributeProperty('active', value='false')


# pylint: disable=too-few-public-methods
class RunConfigurationOptionsExternal(metaclass=OrderedClassMembers):
    """External configuration of an ABAP Unit Test run.

       This class servers the option box purpose.

       Usage:
         run = RunConfiguration()
         run.external.coverage.active = 'false'
    """

    coverage = XmlNodeProperty('coverage')

    def __init__(self):
        self.coverage = CoverageOption()


# pylint: disable=too-few-public-methods
class UriTypeOptionValue(metaclass=OrderedClassMembers):
    """Enum of URI types of passed object sets to AUNIT run."""

    SEMANTIC = 'semantic'


# pylint: disable=too-few-public-methods
class UriTypeOption(metaclass=OrderedClassMembers):
    """URI Type of Objects in ABAP Unit Test run configuration.

       Usage:
         run = RunConfiguration()
         run.options.uri_type.value = UriTypeOptionValue.SEMANTIC
    """

    value = XmlNodeAttributeProperty('value', value=UriTypeOptionValue.SEMANTIC)


# pylint: disable=too-few-public-methods
class TestDeterminationStrategy(metaclass=OrderedClassMembers):
    """Parameters for selection of executed tests

       Usage:
         run = RunConfiguration()
         run.options.test_determination_strategy.same_program = 'true'
         run.options.test_determination_strategy.assigned_tests = 'false'
         run.options.test_determination_strategy.append_assigned_tests_preview = 'true'
    """

    same_program = XmlNodeAttributeProperty('sameProgram', value='true')
    assigned_tests = XmlNodeAttributeProperty('assignedTests', value='false')
    append_assigned_tests_preview = XmlNodeAttributeProperty('appendAssignedTestsPreview',
                                                             value='true')


# pylint: disable=too-few-public-methods
class TestRiskLevelSettings(metaclass=OrderedClassMembers):
    """Parameters for selection of executed tests.

       Usage:
         run = RunConfiguration()
         run.options.test_risk_levels.harmless = 'true'
         run.options.test_risk_levels.dangerous = 'true'
         run.options.test_risk_levels.critical = 'true'
    """

    harmless = XmlNodeAttributeProperty('harmless', value='true')
    dangerous = XmlNodeAttributeProperty('dangerous', value='true')
    critical = XmlNodeAttributeProperty('critical', value='true')


# pylint: disable=too-few-public-methods
class TestDurationSettings(metaclass=OrderedClassMembers):
    """Parameters for selection of executed tests.

       Usage:
         run = RunConfiguration()
         run.options.test_durations.short = 'true'
         run.options.test_durations.medium = 'true'
         run.options.test_durations.long = 'true'
    """

    short = XmlNodeAttributeProperty('short', value='true')
    medium = XmlNodeAttributeProperty('medium', value='true')
    long = XmlNodeAttributeProperty('long', value='true')


# pylint: disable=too-few-public-methods
class WithNavigationUriOption(metaclass=OrderedClassMembers):
    """Enable/Disable Results Navigation URI.

       Usage:
         run = RunConfiguration()
         run.options.with_navigation_uri.enabled = 'false'
    """

    enabled = XmlNodeAttributeProperty('enabled', value='false')


# pylint: disable=too-few-public-methods
class RunConfigurationOptions(metaclass=OrderedClassMembers):
    """AUnit test run configuration carrier

       Usage:
         run = RunConfiguration()

         run.options.uri_type.value = UriTypeOptionValue.SEMANTIC

         run.options.test_determination_strategy.same_program = 'true'
         run.options.test_determination_strategy.assigned_tests = 'false'
         run.options.test_determination_strategy.append_assigned_tests_preview = 'true'

         run.options.test_risk_levels.harmless = 'true'
         run.options.test_risk_levels.dangerous = 'true'
         run.options.test_risk_levels.critical = 'true'

         run.options.test_durations.short = 'true'
         run.options.test_durations.medium = 'true'
         run.options.test_durations.long = 'true'

         run.options.with_navigation_uri.enabled = 'false'
    """

    uri_type = XmlNodeProperty('uriType')
    test_determination_strategy = XmlNodeProperty('testDeterminationStrategy')
    test_risk_levels = XmlNodeProperty('testRiskLevels')
    test_durations = XmlNodeProperty('testDurations')
    with_navigation_uri = XmlNodeProperty('withNavigationUri')

    def __init__(self):
        self.uri_type = UriTypeOption()
        self.test_determination_strategy = TestDeterminationStrategy()
        self.test_risk_levels = TestRiskLevelSettings()
        self.test_durations = TestDurationSettings()
        self.with_navigation_uri = WithNavigationUriOption()


# pylint: disable=too-few-public-methods
class RunConfiguration(metaclass=OrderedClassMembers):
    """ABAP Unit Test run configuration

       Usage with all possible options re-set to default values:
         run = RunConfiguration()

         run.external.coverage.active = 'false'

         run.options.uri_type.value = UriTypeOptionValue.SEMANTIC

         run.options.test_determination_strategy.same_program = 'true'
         run.options.test_determination_strategy.assigned_tests = 'false'
         run.options.test_determination_strategy.append_assigned_tests_preview = 'true'

         run.options.test_risk_levels.harmless = 'true'
         run.options.test_risk_levels.dangerous = 'true'
         run.options.test_risk_levels.critical = 'true'

         run.options.test_durations.short = 'true'
         run.options.test_durations.medium = 'true'
         run.options.test_durations.long = 'true'

         run.options.with_navigation_uri.enabled = 'false'
    """

    objtype = ADTObjectType(None,
                            'abapunit/testruns',
                            XMLNS_AUNIT,
                            'application/vnd.sap.adt.abapunit.testruns.config.v4+xml',
                            None,
                            'runConfiguration')

    external = XmlNodeProperty('external')
    options = XmlNodeProperty('options')
    objects = XmlNodeProperty(XmlElementProperty.NAME_FROM_OBJECT)

    def __init__(self, objects):
        self.external = RunConfigurationOptionsExternal()
        self.options = RunConfigurationOptions()
        self.objects = objects


# pylint: disable=too-few-public-methods
class AUnit:
    """ABAP Unit tests
    """

    def __init__(self, connection):
        self._connection = connection

    def execute(self, adt_object_sets, activate_coverage=False):
        """Executes ABAP Unit tests on the given ADT object set"""

        run_configuration = RunConfiguration(adt_object_sets)
        run_configuration.external.coverage.active = str(activate_coverage).lower()
        test_config = Marshal().serialize(run_configuration)

        return self._connection.execute(
            'POST',
            run_configuration.objtype.basepath,
            content_type=run_configuration.objtype.mimetype,
            body=test_config)


# pylint: disable=too-few-public-methods
class RunResults(NamedTuple):
    """ABAP Unit Tests Framework ADT results Program node"""

    alerts: List
    programs: List


# pylint: disable=too-few-public-methods
class Program(NamedTuple):
    """ABAP Unit Tests Framework ADT results Program node"""

    name: str
    test_classes: List
    alerts: List


# pylint: disable=too-few-public-methods
class TestClass(NamedTuple):
    """ABAP Unit Tests Framework ADT results TestClass node"""

    name: str
    test_methods: List
    alerts: List


# pylint: disable=too-few-public-methods
class TestMethod(NamedTuple):
    """ABAP Unit Tests Framework ADT results TestMethod node"""

    name: str
    duration: int
    alerts: List


class AlertSeverity:
    """AUnit Alert severity Identifiers"""

    CRITICAL = 'critical'
    FATAL = 'fatal'
    TOLERABLE = 'tolerable'


# pylint: disable=too-few-public-methods
class Alert(NamedTuple):
    """ABAP Unit Tests Framework ADT results Alert node"""

    kind: str
    severity: str
    title: str
    details: List
    stack: List

    @property
    def is_error(self):
        """Returns true if the alert represents an error"""

        return self.severity in [AlertSeverity.CRITICAL, AlertSeverity.FATAL]

    @property
    def is_warning(self):
        """Returns true if the alert represents a warning"""

        return self.severity == AlertSeverity.TOLERABLE


# pylint: disable=too-many-instance-attributes
class AUnitResponseHandler(ContentHandler):
    """ABAP Unit Test Framework ADT results XML parser"""

    def __init__(self):
        super().__init__()

        self.run_results = RunResults([], [])
        self.coverage_identifier = None
        self._program = None
        self._test_class = None
        self._test_method = None

        self._alert_title = None
        self._alert_title_part = None
        self._alert_severity = None
        self._alert_kind = None
        self._alert_details = None
        self._alert_stack = None

    def startElement(self, name, attrs):
        mod_log().debug('XML: %s', name)
        if name == 'program':
            self._program = Program(name=attrs.get('adtcore:name'), test_classes=[], alerts=[])
            self.run_results.programs.append(self._program)
            mod_log().debug('XML: %s: %s', name, self._program.name)
        elif name == 'testClass':
            self._test_class = TestClass(name=attrs.get('adtcore:name'), test_methods=[], alerts=[])
            self._program.test_classes.append(self._test_class)
            mod_log().debug('XML: %s: %s', name, self._test_class.name)
        elif name == 'testMethod':
            duration = int(float(attrs.get('executionTime', '0.0')) * 1000)
            self._test_method = TestMethod(name=attrs.get('adtcore:name'),
                                           duration=duration,
                                           alerts=[])
            self._test_class.test_methods.append(self._test_method)
            mod_log().debug('XML: %s: %s', name, self._test_method.name)
        elif name == 'alert':
            self._alert_kind = attrs.get('kind')
            self._alert_severity = attrs.get('severity')
            self._alert_details = []
            self._alert_stack = []
            mod_log().debug('XML: %s', name)
        elif name == 'title':
            self._alert_title_part = ''
        elif name == 'detail':
            self._alert_details.append(attrs.get('text'))
            mod_log().debug('XML: %s: %s', name, self._alert_details[-1])
        elif name == 'stackEntry':
            self._alert_stack.append(attrs.get('adtcore:description'))
            mod_log().debug('XML: %s: %s', name, self._alert_stack[-1])
        elif name == 'coverage':
            self.coverage_identifier = attrs.get('adtcore:uri').rsplit('/', 1)[1]
            mod_log().debug('XML: %s', name)

    def characters(self, content):
        if self._alert_title_part is not None:
            mod_log().debug('XML: alert title: %s', content)
            self._alert_title_part += content.strip()

    def endElement(self, name):
        mod_log().debug('XML: %s: CLOSING', name)
        if name == 'program':
            self._program = None
        elif name == 'testClas':
            self._test_class = None
        elif name == 'testMethod':
            self._test_method = None
        elif name == 'title':
            self._alert_title = self._alert_title_part
            self._alert_title_part = None
        elif name == 'alert':
            alert = Alert(self._alert_kind, self._alert_severity,
                          self._alert_title, self._alert_details,
                          self._alert_stack)

            if self._test_method is not None:
                self._test_method.alerts.append(alert)
            elif self._test_class is not None:
                self._test_class.alerts.append(alert)
            elif self._program is not None:
                self._program.alerts.append(alert)
            else:
                self.run_results.alerts.append(alert)

            self._alert_title = None
            self._alert_severity = None
            self._alert_kind = None
            self._alert_details = None
            self._alert_stack = None


def parse_aunit_response(aunit_results_xml):
    """Converts XML results into Python representation"""

    xml_handler = AUnitResponseHandler()
    xml.sax.parseString(aunit_results_xml, xml_handler)

    return xml_handler
