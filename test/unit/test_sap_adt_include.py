#!/usr/bin/env python3

import unittest

import sap.adt

from mock import Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK

from fixtures_adt_program import CREATE_INCLUDE_PROGRAM_ADT_XML, GET_INCLUDE_PROGRAM_ADT_XML

FIXTURE_INCLUDE_CODE='types: my_boolean type abap_bool.'


class TestADTInclude(unittest.TestCase):

    def test_adt_include_and_master(self):
        conn = Connection()

        include_with = sap.adt.Include(conn, 'ZHELLO_WITH', master='ZHELLO_WORLD')
        include_without = sap.adt.Include(conn, 'ZHELLO_WITHOUT')

        self.assertEqual(include_with.master, 'ZHELLO_WORLD')
        self.assertIsNone(include_without.master)

        exp_master_uri = '%2Fsap%2Fbc%2Fadt%2Fprograms%2Fprograms%2Fzhello_world'
        self.assertEqual(include_with.uri, f'programs/includes/zhello_with?context={exp_master_uri}')
        self.assertEqual(include_without.uri, 'programs/includes/zhello_without')

        include_with.master = 'NEW_MASTER'
        include_without.master = 'NEW_MASTER'

        exp_new_master_uri = '%2Fsap%2Fbc%2Fadt%2Fprograms%2Fprograms%2Fnew_master'
        self.assertEqual(include_with.uri, f'programs/includes/zhello_with?context={exp_new_master_uri}')
        self.assertEqual(include_without.uri, f'programs/includes/zhello_without?context={exp_new_master_uri}')

    def test_adt_include_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE', package='$TEST', metadata=metadata)
        include.description = 'Hello include!'
        include.create()

        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/programs/includes')])
        self.assertEqual(conn.execs[0].headers, {'Content-Type': 'application/vnd.sap.adt.programs.includes.v2+xml; charset=utf-8'})
        self.assertIsNone(conn.execs[0].params)

        self.maxDiff = None
        self.assertEqual(conn.execs[0].body, CREATE_INCLUDE_PROGRAM_ADT_XML)

    def test_adt_include_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE')
        with include.open_editor() as editor:
            editor.write(FIXTURE_INCLUDE_CODE)

        self.assertEqual(len(conn.execs), 3)

        put_request = conn.execs[1]

        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/programs/includes/zhello_include/source/main')
        self.assertEqual(put_request.headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body, bytes(FIXTURE_INCLUDE_CODE, 'utf-8'))

    def test_adt_include_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE')
        with include.open_editor(corrnr='420') as editor:
            editor.write(FIXTURE_INCLUDE_CODE)

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})

    def test_adt_include_fetch(self):
        conn = Connection([Response(text=GET_INCLUDE_PROGRAM_ADT_XML, status_code=200, headers={})])
        include = sap.adt.Include(conn, 'ZHELLO_INCLUDE')
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
