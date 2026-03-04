#!/bin/python

import unittest

from sap.adt.marshalling import Marshal
from sap.adt.api.aunit import (
    AUnit,
    AUnitRunStatusHandler,
    AUnitRunStatus,
    ACCEPT_AUNIT_RESULTS,
    ACCEPT_JUNIT_RESULTS,
    build_test_run,
    TestRun,
    TestMeasurements,
)
from sap.adt.api.osl import MultiPropertyObjectSet

from fixtures_adt_aunit import (
    AUNIT_RESULTS_XML,
    AUNIT_NO_TEST_RESULTS_XML,
    AUNIT_API_RUN_STATUS_RUNNING_XML,
    AUNIT_API_RUN_STATUS_FINISHED_XML,
)

from mock import Connection, Response

AUNIT_RUN_WITH_COVERAGE = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" title="FOLDER: SOOL" context="ADT4Eclipse ABAP Unit Test Runner">
<aunit:options>
<aunit:measurements type="coverage"/>
<aunit:scope ownTests="true" foreignTests="true" addForeignTestsAsPreview="false"/>
<aunit:riskLevel harmless="true" dangerous="true" critical="true"/>
<aunit:duration short="true" medium="true" long="true"/>
</aunit:options>
<osl:objectSet xmlns:osl="http://www.sap.com/api/osl" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="osl:multiPropertySet">
<osl:property key="package" value="SOOL"/>
</osl:objectSet>
</aunit:run>'''

EXPECTED_XML_CLASS = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" title="Run" context="ABAP Unit Test Run">
<aunit:options>
<aunit:scope ownTests="true" foreignTests="true" addForeignTestsAsPreview="true"/>
<aunit:riskLevel harmless="true" dangerous="true" critical="true"/>
<aunit:duration short="true" medium="true" long="true"/>
</aunit:options>
<osl:objectSet xmlns:osl="http://www.sap.com/api/osl" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="osl:flatObjectSet">
<osl:object name="CL_FOO" type="CLAS"/>
</osl:objectSet>
</aunit:run>'''

EXPECTED_XML_PROGRAM = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" title="Run" context="ABAP Unit Test Run">
<aunit:options>
<aunit:scope ownTests="true" foreignTests="true" addForeignTestsAsPreview="true"/>
<aunit:riskLevel harmless="true" dangerous="true" critical="true"/>
<aunit:duration short="true" medium="true" long="true"/>
</aunit:options>
<osl:objectSet xmlns:osl="http://www.sap.com/api/osl" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="osl:flatObjectSet">
<osl:object name="ZPROG" type="PROG"/>
</osl:objectSet>
</aunit:run>'''

EXPECTED_XML_PACKAGE = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" title="Run" context="ABAP Unit Test Run">
<aunit:options>
<aunit:scope ownTests="true" foreignTests="true" addForeignTestsAsPreview="true"/>
<aunit:riskLevel harmless="true" dangerous="true" critical="true"/>
<aunit:duration short="true" medium="true" long="true"/>
</aunit:options>
<osl:objectSet xmlns:osl="http://www.sap.com/api/osl" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="osl:multiPropertySet">
<osl:property key="package" value="ZPKG"/>
</osl:objectSet>
</aunit:run>'''

EXPECTED_XML_CLASS_COVERAGE = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" title="Run" context="ABAP Unit Test Run">
<aunit:options>
<aunit:measurements type="coverage"/>
<aunit:scope ownTests="true" foreignTests="true" addForeignTestsAsPreview="true"/>
<aunit:riskLevel harmless="true" dangerous="true" critical="true"/>
<aunit:duration short="true" medium="true" long="true"/>
</aunit:options>
<osl:objectSet xmlns:osl="http://www.sap.com/api/osl" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="osl:flatObjectSet">
<osl:object name="CL_FOO" type="CLAS"/>
</osl:objectSet>
</aunit:run>'''

EXPECTED_XML_FUGR = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" title="Run" context="ABAP Unit Test Run">
<aunit:options>
<aunit:scope ownTests="true" foreignTests="true" addForeignTestsAsPreview="true"/>
<aunit:riskLevel harmless="true" dangerous="true" critical="true"/>
<aunit:duration short="true" medium="true" long="true"/>
</aunit:options>
<osl:objectSet xmlns:osl="http://www.sap.com/api/osl" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="osl:flatObjectSet">
<osl:object name="ZFUGR" type="FUGR"/>
</osl:objectSet>
</aunit:run>'''

EXPECTED_XML_MULTI_OBJECTS = '''<?xml version="1.0" encoding="UTF-8"?>
<aunit:run xmlns:aunit="http://www.sap.com/adt/api/aunit" title="Run" context="ABAP Unit Test Run">
<aunit:options>
<aunit:scope ownTests="true" foreignTests="true" addForeignTestsAsPreview="true"/>
<aunit:riskLevel harmless="true" dangerous="true" critical="true"/>
<aunit:duration short="true" medium="true" long="true"/>
</aunit:options>
<osl:objectSet xmlns:osl="http://www.sap.com/api/osl" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="osl:flatObjectSet">
<osl:object name="PROGRAM" type="PROG"/>
<osl:object name="CLASS" type="CLAS"/>
<osl:object name="FUNCTIONS" type="FUGR"/>
</osl:objectSet>
</aunit:run>'''


class TestAunitRun(unittest.TestCase):

    def test_with_coverage(self):
        os = MultiPropertyObjectSet()
        os.add_package('SOOL')

        run = TestRun(os)
        run.title = 'FOLDER: SOOL'
        run.context = 'ADT4Eclipse ABAP Unit Test Runner'
        run.options.measurements = TestMeasurements.coverage()
        run.options.scope.own_tests = 'true'
        run.options.scope.foreign_tests = 'true'
        run.options.scope.add_foreign_tests_as_preview = 'false'

        act = Marshal().serialize(run)
        self.assertEqual(act, AUNIT_RUN_WITH_COVERAGE)


class TestBuildTestRun(unittest.TestCase):

    def test_class(self):
        xml = Marshal().serialize(build_test_run([('cl_foo', 'class')]))
        self.assertEqual(xml, EXPECTED_XML_CLASS)

    def test_program(self):
        xml = Marshal().serialize(build_test_run([('zprog', 'program')]))
        self.assertEqual(xml, EXPECTED_XML_PROGRAM)

    def test_package(self):
        xml = Marshal().serialize(build_test_run([('zpkg', 'package')]))
        self.assertEqual(xml, EXPECTED_XML_PACKAGE)

    def test_class_with_coverage(self):
        xml = Marshal().serialize(build_test_run([('cl_foo', 'class')], activate_coverage=True))
        self.assertEqual(xml, EXPECTED_XML_CLASS_COVERAGE)

    def test_function_group(self):
        xml = Marshal().serialize(build_test_run([('zfugr', 'function-group')]))
        self.assertEqual(xml, EXPECTED_XML_FUGR)

    def test_osl_types_passthrough(self):
        """OSL types like CLAS, PROG, FUGR should be used as-is"""
        xml = Marshal().serialize(build_test_run([
            ('program', 'PROG'),
            ('class', 'CLAS'),
            ('functions', 'FUGR'),
        ]))
        self.assertEqual(xml, EXPECTED_XML_MULTI_OBJECTS)

    def test_names_uppercased(self):
        xml = Marshal().serialize(build_test_run([('lowercase_name', 'class')]))
        self.assertIn('name="LOWERCASE_NAME"', xml)


class TestAUnitRunStatusHandler(unittest.TestCase):

    def test_parse_finished_status(self):
        import xml.sax
        handler = AUnitRunStatusHandler()
        xml.sax.parseString(AUNIT_API_RUN_STATUS_FINISHED_XML.encode('utf-8'), handler)

        self.assertEqual(handler.status, 'FINISHED')
        self.assertEqual(handler.percentage, '100')
        self.assertEqual(handler.results_href, '/sap/bc/adt/abapunit/results/RUN_ID_123')

    def test_parse_running_status(self):
        import xml.sax
        handler = AUnitRunStatusHandler()
        xml.sax.parseString(AUNIT_API_RUN_STATUS_RUNNING_XML.encode('utf-8'), handler)

        self.assertEqual(handler.status, 'RUNNING')
        self.assertEqual(handler.percentage, '50')
        self.assertIsNone(handler.results_href)


class TestAUnit(unittest.TestCase):

    def _make_start_response(self, run_id='RUN_ID_123'):
        return Response(
            status_code=200,
            text='',
            headers={'Location': f'/sap/bc/adt/abapunit/runs/{run_id}'}
        )

    def _make_poll_finished_response(self):
        return Response(
            status_code=200,
            text=AUNIT_API_RUN_STATUS_FINISHED_XML,
            headers={}
        )

    def _make_poll_running_response(self):
        return Response(
            status_code=200,
            text=AUNIT_API_RUN_STATUS_RUNNING_XML,
            headers={}
        )

    def _make_results_response(self, text=AUNIT_NO_TEST_RESULTS_XML,
                               content_type=ACCEPT_AUNIT_RESULTS):
        return Response(
            status_code=200,
            text=text,
            headers={'Content-Type': content_type}
        )

    def test_start_run(self):
        connection = Connection([self._make_start_response()])

        aunit = AUnit(connection)
        run_id = aunit.start_run('<xml/>')

        self.assertEqual(run_id, 'RUN_ID_123')
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('abapunit/runs', connection.execs[0].adt_uri)
        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].body, '<xml/>')

    def test_poll_run_finished(self):
        connection = Connection([self._make_poll_finished_response()])

        aunit = AUnit(connection)
        handler = aunit.poll_run('RUN_ID_123')

        self.assertEqual(handler.status, AUnitRunStatus.FINISHED)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('abapunit/runs/RUN_ID_123', connection.execs[0].adt_uri)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].params, {'withLongPolling': 'true'})

    def test_poll_run_running_then_finished(self):
        connection = Connection([
            self._make_poll_running_response(),
            self._make_poll_finished_response(),
        ])

        aunit = AUnit(connection)
        handler = aunit.poll_run('RUN_ID_123')

        self.assertEqual(handler.status, AUnitRunStatus.FINISHED)
        self.assertEqual(len(connection.execs), 2)

    def test_fetch_results(self):
        connection = Connection([self._make_results_response()])

        aunit = AUnit(connection)
        response = aunit.fetch_results('RUN_ID_123')

        self.assertEqual(response.text, AUNIT_NO_TEST_RESULTS_XML)
        self.assertEqual(len(connection.execs), 1)
        self.assertIn('abapunit/results/RUN_ID_123', connection.execs[0].adt_uri)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[0].headers, {'Accept': ACCEPT_AUNIT_RESULTS})

    def test_fetch_results_junit(self):
        connection = Connection([
            self._make_results_response(content_type=ACCEPT_JUNIT_RESULTS)
        ])

        aunit = AUnit(connection)
        response = aunit.fetch_results('RUN_ID_123', accept=ACCEPT_JUNIT_RESULTS)

        self.assertEqual(response.text, AUNIT_NO_TEST_RESULTS_XML)
        self.assertEqual(connection.execs[0].headers, {'Accept': ACCEPT_JUNIT_RESULTS})

    def test_execute_end_to_end(self):
        connection = Connection([
            self._make_start_response(),
            self._make_poll_finished_response(),
            self._make_results_response(AUNIT_RESULTS_XML),
        ])

        test_run = build_test_run([('cl_foo', 'class')])
        aunit = AUnit(connection)
        response = aunit.execute(test_run)

        self.assertEqual(response.text, AUNIT_RESULTS_XML)
        self.assertEqual(len(connection.execs), 3)

        # Verify step 1: POST to start run with expected XML body
        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertIn('abapunit/runs', connection.execs[0].adt_uri)
        self.assertNotIn('results', connection.execs[0].adt_uri)
        self.assertEqual(connection.execs[0].body, EXPECTED_XML_CLASS)

        # Verify step 2: GET to poll
        self.assertEqual(connection.execs[1].method, 'GET')
        self.assertIn('abapunit/runs/RUN_ID_123', connection.execs[1].adt_uri)

        # Verify step 3: GET results with default ABAPUnit accept
        self.assertEqual(connection.execs[2].method, 'GET')
        self.assertIn('abapunit/results/RUN_ID_123', connection.execs[2].adt_uri)
        self.assertEqual(connection.execs[2].headers, {'Accept': ACCEPT_AUNIT_RESULTS})

    def test_execute_with_junit_accept(self):
        connection = Connection([
            self._make_start_response(),
            self._make_poll_finished_response(),
            self._make_results_response(AUNIT_RESULTS_XML,
                                        content_type=ACCEPT_JUNIT_RESULTS),
        ])

        test_run = build_test_run([('cl_foo', 'class')])
        aunit = AUnit(connection)
        response = aunit.execute(test_run, accept=ACCEPT_JUNIT_RESULTS)

        self.assertEqual(response.text, AUNIT_RESULTS_XML)
        self.assertEqual(connection.execs[2].headers, {'Accept': ACCEPT_JUNIT_RESULTS})

    def test_execute_with_coverage(self):
        connection = Connection([
            self._make_start_response(),
            self._make_poll_finished_response(),
            self._make_results_response(AUNIT_RESULTS_XML),
        ])

        test_run = build_test_run([('cl_foo', 'class')], activate_coverage=True)
        aunit = AUnit(connection)
        response = aunit.execute(test_run)

        self.assertEqual(response.text, AUNIT_RESULTS_XML)
        self.assertEqual(connection.execs[0].body, EXPECTED_XML_CLASS_COVERAGE)

    def test_execute_with_running_poll(self):
        connection = Connection([
            self._make_start_response(),
            self._make_poll_running_response(),
            self._make_poll_finished_response(),
            self._make_results_response(AUNIT_NO_TEST_RESULTS_XML),
        ])

        test_run = build_test_run([('zpkg', 'package')])
        aunit = AUnit(connection)
        response = aunit.execute(test_run)

        self.assertEqual(response.text, AUNIT_NO_TEST_RESULTS_XML)
        self.assertEqual(len(connection.execs), 4)
        self.assertEqual(connection.execs[0].body, EXPECTED_XML_PACKAGE)

    def test_execute_request_body_class(self):
        connection = Connection([
            self._make_start_response(),
            self._make_poll_finished_response(),
            self._make_results_response(),
        ])

        test_run = build_test_run([('cl_foo', 'class')])
        aunit = AUnit(connection)
        aunit.execute(test_run)

        self.assertEqual(connection.execs[0].body, EXPECTED_XML_CLASS)

    def test_execute_request_body_package(self):
        connection = Connection([
            self._make_start_response(),
            self._make_poll_finished_response(),
            self._make_results_response(),
        ])

        test_run = build_test_run([('zpkg', 'package')])
        aunit = AUnit(connection)
        aunit.execute(test_run)

        self.assertEqual(connection.execs[0].body, EXPECTED_XML_PACKAGE)


if __name__ == '__main__':
    unittest.main()
