#!/bin/python

import unittest

import sap.adt
import sap

from fixtures_adt_datapreview import ADT_XML_FREESTYLE_TABLE_T000, ADT_XML_FREESTYLE_TABLE_T000_ONE_ROW, \
                                     ADT_XML_FREESTYLE_TABLE_T000_4_ROWS_NO_TOTAL


class TestFreeStyleTableParseResults(unittest.TestCase):

    def test_parse_full(self):
        clients = sap.adt.datapreview.parse_freestyle_table(ADT_XML_FREESTYLE_TABLE_T000, rows=100)

        self.maxDiff = None

        self.assertEqual(clients, [{'ADRNR': '',
                                    'CCCATEGORY': 'S',
                                    'CCCOPYLOCK': '',
                                    'CCCORACTIV': '1',
                                    'CCIMAILDIS': '',
                                    'CCNOCASCAD': '',
                                    'CCNOCLIIND': '',
                                    'CCORIGCONT': '',
                                    'CCSOFTLOCK': '',
                                    'CCTEMPLOCK': '',
                                    'CHANGEDATE': '20171218',
                                    'CHANGEUSER': 'DDIC',
                                    'LOGSYS': '',
                                    'MANDT': '000',
                                    'MTEXT': 'SAP SE',
                                    'MWAER': 'EUR',
                                    'ORT01': 'Walldorf'},
                                   {'ADRNR': '',
                                    'CCCATEGORY': 'C',
                                    'CCCOPYLOCK': '',
                                    'CCCORACTIV': '1',
                                    'CCIMAILDIS': '',
                                    'CCNOCASCAD': '',
                                    'CCNOCLIIND': '',
                                    'CCORIGCONT': '',
                                    'CCSOFTLOCK': '',
                                    'CCTEMPLOCK': '',
                                    'CHANGEDATE': '00000000',
                                    'CHANGEUSER': '',
                                    'LOGSYS': 'NPLCLNT001',
                                    'MANDT': '001',
                                    'MTEXT': 'SAP SE',
                                    'MWAER': 'EUR',
                                    'ORT01': 'Walldorf'}])

    def test_parse_not_all_rows(self):
        clients = sap.adt.datapreview.parse_freestyle_table(ADT_XML_FREESTYLE_TABLE_T000_ONE_ROW, rows=1)
        self.assertEqual(clients, [{'MANDT': '000'}])

    def test_parse_740(self):
        clients = sap.adt.datapreview.parse_freestyle_table(ADT_XML_FREESTYLE_TABLE_T000_4_ROWS_NO_TOTAL, rows=100)

        self.assertEqual(clients, [{'MANDT': '000'}, {'MANDT': '001'}, {'MANDT': '002'}, {'MANDT': '003'}])


if __name__ == '__main__':
    unittest.main()
