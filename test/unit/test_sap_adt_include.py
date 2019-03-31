#!/usr/bin/env python3

import unittest

import sap.adt

from mock import Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK

from fixtures_adt_program import CREATE_INCLUDE_PROGRAM_ADT_XML, GET_INCLUDE_PROGRAM_ADT_XML

FIXTURE_INCLUDE_CODE='types: my_boolean type abap_bool.'


class TestADTInclude(unittest.TestCase):

    def test_adt_include_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE', package='$TEST', metadata=metadata)
        include.description = 'Hello include!'
        include.create()

        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/programs/includes')])
        self.assertEqual(conn.execs[0].headers, {'Content-Type': 'application/vnd.sap.adt.programs.includes.v2+xml'})
        self.assertIsNone(conn.execs[0].params)

        self.maxDiff = None
        self.assertEqual(conn.execs[0].body, CREATE_INCLUDE_PROGRAM_ADT_XML)

    def test_adt_include_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK])

        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE')
        include.lock()
        include.change_text(FIXTURE_INCLUDE_CODE)

        self.assertEqual(len(conn.execs), 2)

        put_request = conn.execs[1]

        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/programs/includes/zhello_include/source/main')
        self.assertEqual(put_request.headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body, FIXTURE_INCLUDE_CODE)

    def test_adt_include_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK])

        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE')
        include.lock()
        include.change_text(FIXTURE_INCLUDE_CODE, corrnr='420')

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})

    def test_adt_include_fetch(self):
        conn = Connection([Response(text=GET_INCLUDE_PROGRAM_ADT_XML, status_code=200, headers={})])
        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE')
        # get_logger().setLevel(0)
        include.fetch()

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/programs/includes/zhello_include')])

        get_request = conn.execs[0]
        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.headers)

        self.assertEqual(include.name, 'ZHELLO_INCLUDE')
        self.assertEqual(include.active, 'inactive')
        self.assertEqual(include.master_language, 'EN')
        self.assertEqual(include.description, 'Hello include!')
        self.assertEqual(include.fix_point_arithmetic, False)


if __name__ == '__main__':
    unittest.main()
