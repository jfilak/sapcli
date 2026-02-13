#!/usr/bin/env python3

import unittest

import sap.adt
import sap.adt.wb

from mock import Connection, Response

from fixtures_adt import GET_DCL_ADT_XML, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_ACTIVATION_REQUEST_XML='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/acm/dcl/sources/zmyacl" adtcore:name="ZMYACL"/>
</adtcore:objectReferences>'''

FIXTURE_DCL_CODE='''@EndUserText.label: 'My Access Control'
@MappingRole: true
define role ZMYACL {
  grant
    select
      on
        ZMyView
          where
            ( CompanyCode ) =
              aspect pfcg_auth ( F_BUKRS_MD, BUKRS, actvt = '03' );
}
'''


class TestADTAccessControl(unittest.TestCase):

    def test_adt_dcl_init(self):
        metadata = sap.adt.ADTCoreData()

        dcl = sap.adt.AccessControl('CONNECTION', name='ZMYACL', package='PACKAGE', metadata=metadata)
        self.assertEqual(dcl.name, 'ZMYACL')
        self.assertEqual(dcl.reference.name, 'PACKAGE')
        self.assertEqual(dcl.coredata, metadata)

    def test_adt_dcl_objtype(self):
        dcl = sap.adt.AccessControl('CONNECTION', name='ZMYACL')
        self.assertEqual(dcl.objtype.code, 'DCLS/DL')
        self.assertEqual(dcl.objtype.basepath, 'acm/dcl/sources')
        self.assertEqual(dcl.objtype.mimetype, 'application/vnd.sap.adt.dclSource+xml')
        self.assertEqual(dcl.objtype.xmlname, 'dclSource')

    def test_adt_dcl_uri(self):
        dcl = sap.adt.AccessControl('CONNECTION', name='ZMYACL')
        self.assertEqual(dcl.uri, 'acm/dcl/sources/zmyacl')

    def test_adt_dcl_read(self):
        conn = Connection([Response(text=FIXTURE_DCL_CODE,
                                 status_code=200,
                                 headers={'Content-Type': 'text/plain; charset=utf-8'})])

        dcl = sap.adt.AccessControl(conn, name='ZMYACL')
        code = dcl.text

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/acm/dcl/sources/zmyacl/source/main')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept'])
        self.assertEqual(get_request.headers['Accept'], 'text/plain')

        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.body)

        self.maxDiff = None
        self.assertEqual(code, FIXTURE_DCL_CODE)

    def test_adt_dcl_activate(self):
        conn = Connection([
            EMPTY_RESPONSE_OK,
            Response(text=GET_DCL_ADT_XML,
                status_code=200,
                headers={'Content-Type': 'application/xml; charset=utf-8'})
            ])

        dcl = sap.adt.AccessControl(conn, name='ZMYACL')
        sap.adt.wb.activate(dcl)

        self.assertEqual(conn.mock_methods(), [
            ('POST', '/sap/bc/adt/activation'),
            ('GET', '/sap/bc/adt/acm/dcl/sources/zmyacl')
        ])

        # two requests - activation + fetch
        self.assertEqual(len(conn.execs), 2)

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
