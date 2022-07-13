#!/bin/python

import unittest

import sap.adt

from mock import ConnectionViaHTTP as Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK

from fixtures_adt_program import CREATE_EXECUTABLE_PROGRAM_ADT_XML, GET_EXECUTABLE_PROGRAM_ADT_XML

FIXTURE_REPORT_CODE='report zhello_world.\n\n  write: \'Hello, World!\'.\n'


class TestADTProgram(unittest.TestCase):

    def test_program_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        program = sap.adt.Program(conn, 'ZHELLO_WORLD', package='$TEST', metadata=metadata)
        program.description = 'Say hello!'
        program.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/programs/programs')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.programs.programs.v2+xml; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3].decode('utf-8'), CREATE_EXECUTABLE_PROGRAM_ADT_XML)

    def test_program_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        program = sap.adt.Program(conn, 'ZHELLO_WORLD')
        with program.open_editor() as editor:
            editor.write(FIXTURE_REPORT_CODE)

        self.assertEqual(len(conn.execs), 3)

        put_request = conn.execs[1]

        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/programs/programs/zhello_world/source/main')
        self.assertEqual(put_request.headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body, bytes(FIXTURE_REPORT_CODE[:-1], 'utf-8'))

    def test_program_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        program = sap.adt.Program(conn, 'ZHELLO_WORLD')
        with program.open_editor(corrnr='420') as editor:
            editor.write(FIXTURE_REPORT_CODE)

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})

    def test_adt_program_fetch(self):
        conn = Connection([Response(text=GET_EXECUTABLE_PROGRAM_ADT_XML, status_code=200, headers={})])
        program = sap.adt.Program(conn, 'ZHELLO_WORLD')
        program.fetch()

        self.assertEqual(program.name, 'ZHELLO_WORLD')
        self.assertEqual(program.active, 'active')
        self.assertEqual(program.program_type, '1')
        self.assertEqual(program.master_language, 'EN')
        self.assertEqual(program.description, 'Say hello!')
        self.assertEqual(program.logical_database.reference.name, 'D$S')
        self.assertEqual(program.fix_point_arithmetic, True)
        self.assertEqual(program.case_sensitive, True)
        self.assertEqual(program.application_database, 'S')


if __name__ == '__main__':
    unittest.main()
