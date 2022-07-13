#!/usr/bin/env python3

import unittest

import sap.adt
import sap.adt.wb

from mock import ConnectionViaHTTP as Connection, Response

from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_ACTIVATION_REQUEST_XML='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/ddic/ddl/sources/myusers" adtcore:name="MYUSERS"/>
</adtcore:objectReferences>'''

FIXTURE_CDS_CODE='''define view MyUsers
  as select from usr02
{
}
'''


class TestADTDataDefinition(unittest.TestCase):

    def test_adt_ddl_init(self):
        metadata = sap.adt.ADTCoreData()

        ddl = sap.adt.DataDefinition('CONNECTION', name='MyUsers', package='PACKAGE', metadata=metadata)
        self.assertEqual(ddl.name, 'MyUsers')
        self.assertEqual(ddl.reference.name, 'PACKAGE')
        self.assertEqual(ddl.coredata, metadata)

    def test_adt_ddl_read(self):
        conn = Connection([Response(text=FIXTURE_CDS_CODE,
                                 status_code=200,
                                 headers={'Content-Type': 'text/plain; charset=utf-8'})])

        ddl = sap.adt.DataDefinition(conn, name='MyUsers')
        code = ddl.text

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/ddic/ddl/sources/myusers/source/main')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept'])
        self.assertEqual(get_request.headers['Accept'], 'text/plain')

        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.body)

        self.maxDiff = None
        self.assertEqual(code, FIXTURE_CDS_CODE)

    def test_adt_ddl_activate(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        ddl = sap.adt.DataDefinition(conn, name='MyUsers')
        sap.adt.wb.activate(ddl)

        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/activation')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept', 'Content-Type'])
        self.assertEqual(get_request.headers['Accept'], 'application/xml')
        self.assertEqual(get_request.headers['Content-Type'], 'application/xml')

        self.assertEqual(sorted(get_request.params), ['method', 'preauditRequested'])
        self.assertEqual(get_request.params['method'], 'activate')
        self.assertEqual(get_request.params['preauditRequested'], 'true')

        self.assertEqual(get_request.body, FIXTURE_ACTIVATION_REQUEST_XML)


if __name__ == '__main__':
    unittest.main()
