#!/usr/bin/env python3

import unittest

import sap.adt

from mock import Connection

# TODO: remove adtcore:version
# TODO: fix adtcore:type - CLAS/I -> CLAS/OC

FIXTURE_ELEMENTARY_CLASS_XML="""<?xml version="1.0" encoding="UTF-8"?>
<class:abapClass xmlns:class="http://www.sap.com/adt/oo/classes" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="CLAS/OC" adtcore:description="Say hello!" adtcore:language="EN" adtcore:name="ZCL_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK" class:final="true" class:visibility="public">
<adtcore:packageRef adtcore:name="$TEST"/>
<class:include adtcore:name="CLAS/OC" adtcore:type="CLAS/OC" class:includeType="testclasses"/>
<class:superClassRef/>
</class:abapClass>"""


class TestADTClass(unittest.TestCase):

    def test_adt_class_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        program = sap.adt.Class(conn, 'ZCL_HELLO_WORLD', package='$TEST', metadata=metadata)
        program.description = 'Say hello!'
        program.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/oo/classes')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.oo.classes.v2+xml'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], FIXTURE_ELEMENTARY_CLASS_XML)
