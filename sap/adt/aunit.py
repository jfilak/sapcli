"""ABAP Unit Test framework ADT wrappers"""


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
