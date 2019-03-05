#!/usr/bin/env python3

import unittest

import sap.adt

from mock import Connection

from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_ELEMENTARY_IFACE_XML='''<?xml version="1.0" encoding="UTF-8"?>
<intf:abapInterface xmlns:intf="http://www.sap.com/adt/oo/interfaces" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="INTF/OI" adtcore:description="Say hello!" adtcore:language="EN" adtcore:name="ZIF_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:masterSystem="NPL" adtcore:responsible="FILAK">
<adtcore:packageRef adtcore:name="$TEST"/>
</intf:abapInterface>'''

FIXTURE_IFACE_MAIN_CODE='''interface zif_hello_world public .
  methods greet.
endinterface.
'''


class TestADTIFace(unittest.TestCase):

    def test_adt_iface_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        iface = sap.adt.Interface(conn, 'ZIF_HELLO_WORLD', package='$TEST', metadata=metadata)
        iface.description = 'Say hello!'
        iface.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/oo/interfaces')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.oo.interfaces.v2+xml'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], FIXTURE_ELEMENTARY_IFACE_XML)

    def test_adt_iface_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK])

        iface = sap.adt.Interface(conn, 'ZIF_HELLO_WORLD')
        iface.lock()

        iface.change_text(FIXTURE_IFACE_MAIN_CODE)

        self.assertEqual(
            [(e.method, e.adt_uri) for e in conn.execs[1:] ],
            [('PUT', '/sap/bc/adt/oo/interfaces/zif_hello_world/source/main')])

        put_request = conn.execs[1]
        self.assertEqual(sorted(put_request.headers), ['Content-Type'])
        self.assertEqual(put_request.headers['Content-Type'], 'text/plain; charset=utf-8')

        self.assertEqual(sorted(put_request.params), ['lockHandle'])
        self.assertEqual(put_request.params['lockHandle'], 'win')

        self.maxDiff = None
        self.assertEqual(put_request.body, FIXTURE_IFACE_MAIN_CODE)


if __name__ == '__main__':
    unittest.main()
