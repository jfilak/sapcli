#!/bin/python

import unittest

import sap.adt

from mock import Connection


FIXTURE_XML="""<?xml version="1.0" encoding="UTF-8"?>
<program:abapProgram xmlns:program="http://www.sap.com/adt/programs/programs" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:version="active" adtcore:type="PROG/P" adtcore:description="Say hello!" adtcore:language="EN" adtcore:name="ZHELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK">
<adtcore:packageRef adtcore:name="$TEST"/>
</program:abapProgram>"""


class TestADTProgram(unittest.TestCase):

    def test_program_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        program = sap.adt.Program(conn, 'ZHELLO_WORLD', package='$TEST', metadata=metadata)
        program.description = 'Say hello!'
        program.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], 'programs/programs')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.programs.programs.v2+xml'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], FIXTURE_XML)


if __name__ == '__main__':
    unittest.main()
