#!/bin/python

import unittest

import sap.adt

from mock import Connection


FIXTURE_XML="""<?xml version="1.0" encoding="UTF-8"?>
<program:abapProgram xmlns:program="http://www.sap.com/adt/programs/programs" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:version="active" adtcore:type="PROG/P" adtcore:description="Say hello!" adtcore:language="EN" adtcore:name="ZHELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK">
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
        conn = Connection()

        program = sap.adt.Program(conn, 'ZHELLO_WORLD')
        program.change_text(FIXTURE_REPORT_CODE)

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'PUT')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/programs/programs/zhello_world/source/main')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'text/plain; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], FIXTURE_REPORT_CODE)

if __name__ == '__main__':
    unittest.main()
