#!/bin/python

import unittest

from fixtures_adt_coverage import ACOVERAGE_STATEMENTS_RESULTS_XML
from mock import ConnectionViaHTTP as Connection
from sap.adt.acoverage_statements import parse_statements_response, ACoverageStatements, StatementRequest, StatementsBulkRequest


class TestACoverageStatements(unittest.TestCase):

    def test_query_default(self):
        connection = Connection()

        acoverage_statements = ACoverageStatements(connection)
        statement_requests = [StatementRequest(uri) for uri in ['foo', 'bar']]
        bulk_statements = StatementsBulkRequest('FOOBAR', statement_requests)
        acoverage_statements = ACoverageStatements(connection)
        acoverage_statements_response = acoverage_statements.execute(bulk_statements)

        self.assertEqual(connection.execs[0].body,
'''<?xml version="1.0" encoding="UTF-8"?>
<cov:statementsBulkRequest xmlns:cov="http://www.sap.com/adt/cov">
<statementsRequest get="foo"/>
<statementsRequest get="bar"/>
</cov:statementsBulkRequest>''')

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/runtime/traces/coverage/results/FOOBAR/statements')


class TestStatementsBulkRequest(unittest.TestCase):

    def test_add_statement_request(self):
        bulk_statements = StatementsBulkRequest('FOOBAR')

        statement_requests = [StatementRequest(uri) for uri in ['foo', 'bar']]

        bulk_statements.add_statement_request(statement_requests[0])
        bulk_statements.add_statement_request(statement_requests[1])

        self.assertEqual(bulk_statements._statement_requests, statement_requests)

class TestStatementRequest(unittest.TestCase):

    def test_setter(self):
        request = StatementRequest('foo')
        self.assertEqual(request._get, 'foo')

        request.get = 'bar'
        self.assertEqual(request._get, 'bar')


class TestACoverageStatementsParseResults(unittest.TestCase):

    def test_parse_full(self):
        statement_responses = parse_statements_response(ACOVERAGE_STATEMENTS_RESULTS_XML).statement_responses

        self.assertEqual(len(statement_responses), 2)
        self.assertEqual(len(statement_responses[0].statements), 5)
        self.assertEqual(len(statement_responses[1].statements), 8)

        self.assertEqual(statement_responses[0].name, "FOO===========================CP.FOO.METHOD_A")
        self.assertEqual(statement_responses[0].statements[0].uri, "/sap/bc/adt/oo/classes/foo/source/main#start=53,1;end=53,38")
        self.assertEqual(statement_responses[0].statements[0].executed, "4")

if __name__ == '__main__':
    unittest.main()
