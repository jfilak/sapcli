#!/bin/python

import unittest

import sap
import sap.adt
from fixtures_adt_coverage import ACOVERAGE_RESULTS_XML
from sap.adt.aunit import Alert, AlertSeverity
from sap.adt.objects import ADTObjectSets

from fixtures_adt import DummyADTObject
from fixtures_adt_aunit import AUNIT_RESULTS_XML, AUNIT_NO_TEST_RESULTS_XML

from mock import ConnectionViaHTTP as Connection


class TestACoverage(unittest.TestCase):

    def test_query_default(self):
        connection = Connection()

        victory = DummyADTObject(connection=connection)

        tested_objects = ADTObjectSets()
        tested_objects.include_object(victory)

        coverage_identifier = 'FOOBAR'
        runner = sap.adt.acoverage.ACoverage(connection)
        response = runner.execute(coverage_identifier, tested_objects)

        self.assertEqual(connection.execs[0].body,
'''<?xml version="1.0" encoding="UTF-8"?>
<cov:query xmlns:cov="http://www.sap.com/adt/cov">
<adtcore:objectSets xmlns:adtcore="http://www.sap.com/adt/core">
<objectSet kind="inclusive">
<adtcore:objectReferences>
<adtcore:objectReference adtcore:uri="/sap/bc/adt/awesome/success/noobject" adtcore:name="NOOBJECT"/>
</adtcore:objectReferences>
</objectSet>
</adtcore:objectSets>
</cov:query>''')

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/runtime/traces/coverage/measurements/FOOBAR')


class TestACoverageParseResults(unittest.TestCase):

    def test_parse_full(self):
        root_node = sap.adt.acoverage.parse_acoverage_response(ACOVERAGE_RESULTS_XML).root_node

        self.assertEqual(root_node.name, 'ADT_ROOT_NODE')

        self.assertEqual([node.name for node in root_node.nodes], ['TEST_CHECK_LIST'])

        self.assertEqual([coverage.type for coverage in root_node.nodes[0].coverages], ['branch', 'procedure', 'statement'])
        self.assertEqual([coverage.total for coverage in root_node.nodes[0].coverages], [134, 52, 331])

        self.assertEqual(root_node.nodes[0].nodes[0].nodes[0].nodes[0].name, 'METHOD_A')

        self.assertEqual(len(root_node.nodes[0].nodes), 2)
        self.assertEqual(len(root_node.nodes[0].nodes[1].nodes), 0)


    def test_parse_no_coverage(self):
        pass
        # TODO implement


if __name__ == '__main__':
    unittest.main()
