#!/bin/python

import unittest

import sap.adt

from mock import Connection
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_XML="""<?xml version="1.0" encoding="UTF-8"?>
<program:abapProgram xmlns:program="http://www.sap.com/adt/programs/programs" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="PROG/P" adtcore:description="Say hello!" adtcore:language="EN" adtcore:name="ZHELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK" adtcore:version="active">
<adtcore:packageRef adtcore:name="$TEST"/>
</program:abapProgram>"""

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
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.programs.programs.v2+xml'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], FIXTURE_XML)

    def test_program_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK])

        program = sap.adt.Program(conn, 'ZHELLO_WORLD')
        program.lock()
        program.change_text(FIXTURE_REPORT_CODE)

        self.assertEqual(len(conn.execs), 2)

        put_request = conn.execs[1]

        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/programs/programs/zhello_world/source/main')
        self.assertEqual(put_request.headers, {'Content-Type': 'text/plain; charset=utf-8'})
        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body, FIXTURE_REPORT_CODE)

    def test_program_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK])

        program = sap.adt.Program(conn, 'ZHELLO_WORLD')
        program.lock()
        program.change_text(FIXTURE_REPORT_CODE, corrnr='420')

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrnr': '420'})


if __name__ == '__main__':
    unittest.main()
