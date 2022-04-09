#!/usr/bin/env python3

import unittest

from sap.adt.search import ADTSearch

from mock import Connection, Response, Request


FIXTURE_ADT_SEARCH_RESPONSE_FOUND="""<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
  <adtcore:objectReference adtcore:uri="/sap/bc/adt/programs/includes/jakub_is_awesome" adtcore:type="PROG/I" adtcore:name="JAKUB_IS_AWESOME" adtcore:packageName="GODNESS" adtcore:description="Include JAKUB_IS_AWESOME"/>
</adtcore:objectReferences>
"""


class TestADTSearch(unittest.TestCase):

    def setUp(self):
        self.mock_conn = Connection()

    def test_init(self):
        search = ADTSearch(self.mock_conn)
        self.assertEqual(search._connection, self.mock_conn)

    def test_quick_search(self):
        exp_search_term = 'SOME?ABAP& OBJEC'

        self.mock_conn.set_responses([
            Response(status_code=200, text=FIXTURE_ADT_SEARCH_RESPONSE_FOUND),
        ])

        search = ADTSearch(self.mock_conn)
        result = search.quick_search(exp_search_term)

        self.mock_conn.execs[0].assertEqual(Request.get(
            adt_uri='/sap/bc/adt/repository/informationsystem/search',
            params={
                'operation': 'quickSearch',
                'query': exp_search_term,
                'maxResults': 5,
            }
        ), self)

        self.assertEqual(result.references[0].typ, 'PROG/I')
        self.assertEqual(result.references[0].name, 'JAKUB_IS_AWESOME')
