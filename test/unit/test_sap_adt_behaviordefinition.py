#!/usr/bin/env python3

import unittest

import sap.adt
import sap.adt.wb
from sap.adt.behaviordefinition import BehaviorDefinition

from mock import Connection, Response

from fixtures_adt import GET_BDEF_ADT_XML, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


FIXTURE_ACTIVATION_REQUEST_XML='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/bo/behaviordefinitions/zmybdef" adtcore:name="ZMYBDEF"/>
</adtcore:objectReferences>'''

FIXTURE_BDEF_CODE='''projection;
strict ( 2 );
use draft;

define behavior for ZMyEntity alias MyEntity
{
  use create;
  use update;
  use delete;
}
'''


class TestADTBehaviorDefinition(unittest.TestCase):

    def test_adt_bdef_init(self):
        metadata = sap.adt.ADTCoreData()

        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF', package='PACKAGE', metadata=metadata)
        self.assertEqual(bdef.name, 'ZMYBDEF')
        self.assertEqual(bdef.reference.name, 'PACKAGE')
        self.assertEqual(bdef.coredata, metadata)

    def test_adt_bdef_objtype(self):
        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF')
        self.assertEqual(bdef.objtype.code, 'BDEF/BDO')
        self.assertEqual(bdef.objtype.basepath, 'bo/behaviordefinitions')
        self.assertEqual(bdef.objtype.mimetype, 'application/vnd.sap.adt.blues.v1+xml')
        self.assertEqual(bdef.objtype.xmlname, 'blueSource')

    def test_adt_bdef_uri(self):
        bdef = sap.adt.BehaviorDefinition('CONNECTION', name='ZMYBDEF')
        self.assertEqual(bdef.uri, 'bo/behaviordefinitions/zmybdef')

    def test_adt_bdef_read(self):
        conn = Connection([Response(text=FIXTURE_BDEF_CODE,
                                 status_code=200,
                                 headers={'Content-Type': 'text/plain; charset=utf-8'})])

        bdef = sap.adt.BehaviorDefinition(conn, name='ZMYBDEF')
        code = bdef.text

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/bo/behaviordefinitions/zmybdef/source/main')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept'])
        self.assertEqual(get_request.headers['Accept'], 'text/plain')

        self.assertIsNone(get_request.params)
        self.assertIsNone(get_request.body)

        self.maxDiff = None
        self.assertEqual(code, FIXTURE_BDEF_CODE)

    def test_adt_bdef_activate(self):
        conn = Connection([
            EMPTY_RESPONSE_OK,
            Response(text=GET_BDEF_ADT_XML,
                status_code=200,
                headers={'Content-Type': 'application/xml; charset=utf-8'})
            ])

        bdef = sap.adt.BehaviorDefinition(conn, name='ZMYBDEF')
        sap.adt.wb.activate(bdef)

        self.assertEqual(conn.mock_methods(), [
            ('POST', '/sap/bc/adt/activation'),
            ('GET', '/sap/bc/adt/bo/behaviordefinitions/zmybdef')
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


FIXTURE_LIST_INTERFACES_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<nameditem:namedItemList xmlns:nameditem="http://www.sap.com/adt/nameditem">
  <nameditem:totalItemCount>1</nameditem:totalItemCount>
  <nameditem:namedItem>
    <nameditem:name>I_PRODUCTTP_2</nameditem:name>
    <nameditem:description/>
    <nameditem:data/>
  </nameditem:namedItem>
</nameditem:namedItemList>'''

FIXTURE_LIST_INTERFACES_EMPTY_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<nameditem:namedItemList xmlns:nameditem="http://www.sap.com/adt/nameditem">
  <nameditem:totalItemCount>0</nameditem:totalItemCount>
</nameditem:namedItemList>'''


class TestBehaviorDefinitionListInterfaces(unittest.TestCase):

    def test_list_interfaces(self):
        conn = Connection([Response(text=FIXTURE_LIST_INTERFACES_XML,
                                    status_code=200,
                                    headers={'Content-Type': 'application/vnd.sap.adt.nameditems.v1+xml; charset=utf-8'})])

        result = BehaviorDefinition.list_interfaces(conn, 'r_producttp')

        self.assertEqual(conn.mock_methods(), [
            ('GET', '/sap/bc/adt/bo/behaviordefinitions/interfaces')
        ])

        get_request = conn.execs[0]
        self.assertEqual(get_request.params, {'name': 'R_PRODUCTTP'})
        self.assertEqual(get_request.headers['Accept'],
                         'application/vnd.sap.adt.nameditems.v1+xml, application/xml')

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0].name, 'I_PRODUCTTP_2')

    def test_list_interfaces_empty(self):
        conn = Connection([Response(text=FIXTURE_LIST_INTERFACES_EMPTY_XML,
                                    status_code=200,
                                    headers={'Content-Type': 'application/vnd.sap.adt.nameditems.v1+xml; charset=utf-8'})])

        result = BehaviorDefinition.list_interfaces(conn, 'R_PRODUCTTP')

        self.assertEqual(len(result.items), 0)


if __name__ == '__main__':
    unittest.main()
