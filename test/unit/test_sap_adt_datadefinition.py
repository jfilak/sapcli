#!/usr/bin/env python3

import unittest

import sap.adt
import sap.adt.wb

from mock import Connection, Response

from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, put_exec, lock_exec, unlock_exec
from fixtures_adt_cds import CREATE_DCLS_ADT_REQ_XML, ACTIVATION_DCL_REQ_XML, FETCH_DCLS_ADT_RESP_XML, PUT_DCLS_ADT_REQ_XML


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


class TestADTDataControl(unittest.TestCase):


    def test_adt_dcl_init(self):
        metadata = sap.adt.ADTCoreData()

        dcl = sap.adt.DataControl(Connection(), name='ZDCLS_HELLO_WORLD', package='PACKAGE', metadata=metadata)
        self.assertEqual(dcl.name, 'ZDCLS_HELLO_WORLD')
        self.assertEqual(dcl.reference.name, 'PACKAGE')
        self.assertEqual(dcl.coredata, metadata)

    def test_adt_dcl_read_code(self):
        fixture_dcl_code = 'DCL CODE'
        conn = Connection([Response(text=fixture_dcl_code,
                                    status_code=200,
                                    headers={'Content-Type': 'text/plain; charset=utf-8'})])

        dcl = sap.adt.DataControl(conn, name='ZDCLS_HELLO_WORLD')
        code = dcl.text

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/acm/dcl/sources/zdcls_hello_world/source/main')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept'])
        self.assertEqual(get_request.headers['Accept'], 'text/plain')

        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.body)

        self.maxDiff = None
        self.assertEqual(code, fixture_dcl_code)

    def test_adt_dcl_create(self):
        conn = Connection([Response(text=FETCH_DCLS_ADT_RESP_XML,
                                    status_code=201,
                                    headers={'Content-Type': 'application/vnd.sap.adt.dclSource+xml; charset=utf-8'})])

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')

        dcl = sap.adt.DataControl(conn, name='ZDCLS_HELLO_WORLD', package='$test', metadata=metadata)
        dcl.description = 'You cannot stop me!'
        dcl.create()

        self.assertEqual(len(conn.execs), 1)

        create_req = conn.execs[0]

        self.assertEqual(create_req.method, 'POST')
        self.assertEqual(create_req.adt_uri, '/sap/bc/adt/acm/dcl/sources')
        self.assertEqual(create_req.headers,
                         {'Accept': 'application/vnd.sap.adt.dclSource+xml',
                          'Content-Type': 'application/vnd.sap.adt.dclSource+xml'})
        self.assertIsNone(create_req.params)

        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], CREATE_DCLS_ADT_REQ_XML)

    def test_adt_dcl_activate(self):
        conn = Connection([EMPTY_RESPONSE_OK])

        dcl = sap.adt.DataControl(conn, name='ZDCLS_HELLO_WORLD')
        sap.adt.wb.activate(dcl)

        self.assertEqual(conn.mock_methods(), [('POST', '/sap/bc/adt/activation')])

        activation_req = conn.execs[0]
        self.assertEqual(sorted(activation_req.params), ['method', 'preauditRequested'])
        self.assertEqual(activation_req.params['preauditRequested'], 'true')

        self.assertEqual(activation_req.body, ACTIVATION_DCL_REQ_XML)

    def test_adt_dcl_fetch(self):
        conn = Connection([Response(status_code=200,
                                    text=FETCH_DCLS_ADT_RESP_XML,
                                    headers={'Conent-Type': 'application/vnd.sap.adt.dclSource+xml'})])

        dcl = sap.adt.DataControl(conn, name='ZDCLS_HELLO_WORLD')
        dcl.fetch()

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/acm/dcl/sources/zdcls_hello_world')])

        get_req = conn.execs[0]

        self.assertEqual(get_req.headers, {'Accept': 'application/vnd.sap.adt.dclSource+xml'})
        self.assertIsNone(get_req.params)

        self.assertEqual(dcl.description, 'You cannot stop me!')
        self.assertEqual(dcl.reference.name, '$TEST')

    def test_adt_dcl_write(self):
        fixture_dcl_code = 'NEW CODE'
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        dcl = sap.adt.DataControl(conn, name='ZDCLS_HELLO_WORLD')
        with dcl.open_editor() as editor:
            editor.write(fixture_dcl_code)

        self.assertEquals(conn.mock_methods(), [lock_exec('/sap/bc/adt/acm/dcl/sources/zdcls_hello_world'),
                                                put_exec('/sap/bc/adt/acm/dcl/sources/zdcls_hello_world/source/main'),
                                                unlock_exec('/sap/bc/adt/acm/dcl/sources/zdcls_hello_world')])

    def test_adt_dcl_push(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        dcl = sap.adt.DataControl(conn, name='ZDCLS_HELLO_WORLD')
        with dcl.open_editor() as editor:
            editor.push()

        self.assertEquals(conn.mock_methods(), [lock_exec('/sap/bc/adt/acm/dcl/sources/zdcls_hello_world'),
                                                put_exec('/sap/bc/adt/acm/dcl/sources/zdcls_hello_world'),
                                                unlock_exec('/sap/bc/adt/acm/dcl/sources/zdcls_hello_world')])

        self.maxDiff = None
        self.assertEquals(conn.execs[1].body, PUT_DCLS_ADT_REQ_XML)


if __name__ == '__main__':
    unittest.main()
