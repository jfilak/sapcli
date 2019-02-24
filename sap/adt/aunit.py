"""ABAP Unit Test framework ADT wrappers"""

from typing import NamedTuple, List

import xml.sax
from xml.sax.handler import ContentHandler

from sap import get_logger


def mod_log():
    """ADT Module logger"""

    return get_logger()


class AUnit:
    """ABAP Unit tests
    """

    def __init__(self, connection):
        self._connection = connection

    @staticmethod
    def build_tested_object_uri(connection, adt_object):
        """Build URL for the tested object.
        """

        return '/' + connection.uri + '/' + adt_object.uri

    @staticmethod
    def build_test_configuration(adt_object_uri):
        """Build the AUnit ADT URI of the tested object.
        """

        test_config = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:runConfiguration xmlns:aunit="http://www.sap.com/adt/aunit">
  <external>
    <coverage active="false"/>
  </external>
  <options>
    <uriType value="semantic"/>
    <testDeterminationStrategy sameProgram="true" assignedTests="false" appendAssignedTestsPreview="true"/>
    <testRiskLevels harmless="true" dangerous="true" critical="true"/>
    <testDurations short="true" medium="true" long="true"/>
  </options>
  <adtcore:objectSets xmlns:adtcore="http://www.sap.com/adt/core">
    <objectSet kind="inclusive">
      <adtcore:objectReferences>
        <adtcore:objectReference adtcore:uri="'''

        test_config += adt_object_uri

        test_config += '''"/>
      </adtcore:objectReferences>
    </objectSet>
  </adtcore:objectSets>
</aunit:runConfiguration>'''

        return test_config

    def execute(self, adt_object):
        """Executes ABAP Unit tests on the given ADT object
        """

        adt_object_uri = AUnit.build_tested_object_uri(self._connection, adt_object)
        test_config = AUnit.build_test_configuration(adt_object_uri)

        return self._connection.execute(
            'POST', 'abapunit/testruns',
            headers={
                'Content-Type': 'application/vnd.sap.adt.abapunit.testruns.config.v4+xml'},
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


# pylint: disable=too-few-public-methods
class TestClass(NamedTuple):
    """ABAP Unit Tests Framework ADT results TestClass node"""

    name: str
    test_methods: List


# pylint: disable=too-few-public-methods
class TestMethod(NamedTuple):
    """ABAP Unit Tests Framework ADT results TestMethod node"""

    name: str
    alerts: List


# pylint: disable=too-few-public-methods
class Alert(NamedTuple):
    """ABAP Unit Tests Framework ADT results Alert node"""

    kind: str
    severity: str
    title: str
    details: List
    stack: List


# pylint: disable=too-many-instance-attributes
class AUnitResponseHandler(ContentHandler):
    """ABAP Unit Test Framework ADT results XML parser"""

    def __init__(self):
        super(AUnitResponseHandler, self).__init__()

        self.run_results = RunResults(list(), list())
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
            self._program = Program(name=attrs.get('adtcore:name'), test_classes=[])
            self.run_results.programs.append(self._program)
            mod_log().debug('XML: %s: %s', name, self._program.name)
        elif name == 'testClass':
            self._test_class = TestClass(name=attrs.get('adtcore:name'), test_methods=[])
            self._program.test_classes.append(self._test_class)
            mod_log().debug('XML: %s: %s', name, self._test_class.name)
        elif name == 'testMethod':
            self._test_method = TestMethod(name=attrs.get('adtcore:name'), alerts=[])
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

    def characters(self, content):
        if self._alert_title_part is not None:
            mod_log().debug('XML: alert title: %s', content)
            self._alert_title_part += content.strip()

    def endElement(self, name):
        mod_log().debug('XML: %s: CLOSING', name)
        if name == 'program':
            self._program = None
        elif name == 'testclas':
            self._test_class = None
        elif name == 'testmethod':
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
            else:
                self.run_results.alerts.append(alert)

            self._alert_title = None
            self._alert_severity = None
            self._alert_kind = None
            self._alert_details = None
            self._alert_stack = None


def parse_run_results(aunit_results_xml):
    """Converts XML results into Python representation"""

    xml_handler = AUnitResponseHandler()
    xml.sax.parseString(aunit_results_xml, xml_handler)

    return xml_handler.run_results
