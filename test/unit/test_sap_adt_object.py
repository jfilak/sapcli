#!/bin/python

import unittest

from sap.errors import SAPCliError
import sap.adt
import sap.adt.wb

from fixtures_adt import DummyADTObject, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK, GET_DUMMY_OBJECT_ADT_XML
from mock import Response, Connection


ACTIVATE_RESPONSE_FAILED='''<?xml version="1.0" encoding="utf-8"?>
  <chkl:messages xmlns:chkl="http://www.sap.com/abapxml/checklist">
    <msg objDescr="Program ZABAPGIT" type="W" line="1" href="/sap/bc/adt/programs/programs/zabapgit/source/main#start=41593,4" forceSupported="true">
      <shortText>
        <txt>The exception CX_WDY_MD_EXCEPTION is not caught or declared in the RAISING clause of "RECOVER_DEFINITION". "RECOVER_DEFINITION".</txt>
      </shortText>
      <atom:link href="art.syntax:G-Q" rel="http://www.sap.com/adt/categories/quickfixes" xmlns:atom="http://www.w3.org/2005/Atom"/>
    </msg>
  </chkl:messages>
'''


class TestADTObject(unittest.TestCase):

    def test_uri(self):
        victory = DummyADTObject()

        self.assertEquals(victory.uri, 'awesome/success/noobject')

    def test_lock_modify_ok(self):
        connection = Connection([LOCK_RESPONSE_OK])

        victory = DummyADTObject(connection=connection)
        victory.lock()
        self.assertEquals(victory._lock, 'win')

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/awesome/success/noobject')])

        lock_request = connection.execs[0]
        self.assertEqual(sorted(lock_request.params.keys()), ['_action', 'accessMode'])
        self.assertEqual(lock_request.params['_action'], 'LOCK')
        self.assertEqual(lock_request.params['accessMode'], 'MODIFY')

        self.assertEqual(sorted(lock_request.headers.keys()), ['Accept', 'X-sap-adt-sessiontype'])
        self.assertEqual(lock_request.headers['X-sap-adt-sessiontype'], 'stateful')
        self.assertEqual(lock_request.headers['Accept'], 'application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result;q=0.8, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result2;q=0.9')

        try:
            victory.lock()
            self.assertFail('Exception was expected')
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: already locked')

    def test_lock_modify_invalid(self):
        response = Response(text='invalid',
                            status_code=200,
                            headers={'Content-Type': 'text/plain'})

        connection = Connection([response, response])

        victory = DummyADTObject(connection=connection)

        try:
            victory.lock()
            self.assertFail('Exception was expected')
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: lock response does not have lock result\ninvalid')

        try:
            victory.lock()
            self.assertFail('Exception was expected')
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: lock response does not have lock result\ninvalid')

    def test_unlock_ok(self):
        connection = Connection([LOCK_RESPONSE_OK, None])

        victory = DummyADTObject(connection=connection)
        victory.lock()
        victory.unlock()

        self.assertIsNone(victory._lock)

        self.assertEqual(
            [(e.method, e.adt_uri) for e in connection.execs],
            2 * [('POST', '/sap/bc/adt/awesome/success/noobject')])

        unlock_request = connection.execs[1]
        self.assertEqual(sorted(unlock_request.params.keys()), ['_action', 'lockHandle'])
        self.assertEqual(unlock_request.params['_action'], 'UNLOCK')
        self.assertEqual(unlock_request.params['lockHandle'], 'win')

        self.assertEqual(sorted(unlock_request.headers.keys()), ['X-sap-adt-sessiontype'])
        self.assertEqual(unlock_request.headers['X-sap-adt-sessiontype'], 'stateful')

    def test_unlock_not_locked(self):
        victory = DummyADTObject()

        try:
            victory.unlock()
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: not locked')

    def test_activate(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='activator')

        sap.adt.wb.activate(victory)

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/activation')

        self.assertEqual(connection.execs[0].headers['Accept'], 'application/xml' )
        self.assertEqual(connection.execs[0].headers['Content-Type'], 'application/xml')
        self.assertEqual(sorted(connection.execs[0].headers.keys()), ['Accept', 'Content-Type'])

        self.assertEqual(connection.execs[0].params['method'], 'activate' )
        self.assertEqual(connection.execs[0].params['preauditRequested'], 'true')
        self.assertEqual(sorted(connection.execs[0].params.keys()), ['method', 'preauditRequested'])

        self.maxDiff = None
        self.assertEqual(connection.execs[0].body, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/awesome/success/activator" adtcore:name="ACTIVATOR"/>
</adtcore:objectReferences>''' )

    def test_activate_fails(self):
        connection = Connection([Response(ACTIVATE_RESPONSE_FAILED, 200, {})])
        victory = DummyADTObject(connection=connection, name='activator')

        with self.assertRaises(SAPCliError) as cm:
            sap.adt.wb.activate(victory)

        self.maxDiff = None
        self.assertEqual(str(cm.exception), f'Could not activate the object activator: {ACTIVATE_RESPONSE_FAILED}')

    def test_create_ok_wihout_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='creator')

        victory.create()

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/awesome/success')

        self.assertEqual(connection.execs[0].headers['Content-Type'], 'application/super.cool.txt+xml')
        self.assertEqual(sorted(connection.execs[0].headers.keys()), ['Content-Type'])

        self.assertIsNone(connection.execs[0].params)

        self.maxDiff = None
        self.assertEqual(connection.execs[0].body, '''<?xml version="1.0" encoding="UTF-8"?>
<win:dummies xmlns:win="http://www.example.com/never/lose" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DUMMY/S" adtcore:description="adt fixtures dummy object" adtcore:name="creator">
<adtcore:packageRef/>
</win:dummies>''' )

    def test_create_ok_wih_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='creator')

        victory.create(corrnr='NPL000008')

        self.assertEqual(connection.execs[0].params['corrNr'], 'NPL000008')
        self.assertEqual(sorted(connection.execs[0].params.keys()), ['corrNr'])

    def test_properties(self):
        victory = DummyADTObject()

        with self.assertRaises(SAPCliError) as cm:
            victory.name = 'somethingelse'

        self.assertEqual(str(cm.exception), 'Deserializing wrong object: noobject != somethingelse')

    def test_fetch(self):
        connection = Connection([Response(text=GET_DUMMY_OBJECT_ADT_XML, status_code=200, headers={})])
        victory = DummyADTObject(connection=connection, name='SOFTWARE_ENGINEER')
        victory.fetch()

        self.assertEqual(connection.mock_methods(), [('GET', '/sap/bc/adt/awesome/success/software_engineer')])

        self.assertEqual(victory.description, 'You cannot stop me!')
        self.assertEqual(victory.language, 'CZ')
        self.assertEqual(victory.name, 'SOFTWARE_ENGINEER')
        self.assertEqual(victory.master_language, 'EN')
        self.assertEqual(victory.master_system, 'NPL')
        self.assertEqual(victory.responsible, 'DEVELOPER')
        self.assertEqual(victory.active, 'active')
        self.assertEqual(victory.reference.name, 'UNIVERSE')


class TestADTObjectType(unittest.TestCase):

    def setUp(self):
        self.adt_object = sap.adt.objects.ADTObjectType(
            'code',
            'basepath',
            sap.adt.objects.XMLNamespace(name='name', uri='uri'),
            'mimetype',
            {'text/plain': '/text'},
            'xmlname')

    def test_adt_object_type_basepath(self):
        self.assertEqual(self.adt_object.basepath, 'basepath')

        self.adt_object.basepath = 'newpath'
        self.assertEqual(self.adt_object.basepath, 'newpath')


if __name__ == '__main__':
    unittest.main()
