#!/bin/python

import unittest

from sap.errors import SAPCliError
import sap.adt
import sap.adt.objects
import sap.adt.wb

from fixtures_adt import DummyADTObject, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK, GET_DUMMY_OBJECT_ADT_XML
from mock import Response, Connection


ACTIVATE_RESPONSE_FAILED='''<?xml version="1.0" encoding="utf-8"?>
  <chkl:messages xmlns:chkl="http://www.sap.com/abapxml/checklist">
    <msg objDescr="Program ZABAPGIT" type="E" line="1" href="/sap/bc/adt/programs/programs/zabapgit/source/main#start=41593,4" forceSupported="true">
      <shortText>
        <txt>The exception CX_WDY_MD_EXCEPTION is not caught or declared in the RAISING clause of "RECOVER_DEFINITION". "RECOVER_DEFINITION".</txt>
      </shortText>
      <atom:link href="art.syntax:G-Q" rel="http://www.sap.com/adt/categories/quickfixes" xmlns:atom="http://www.w3.org/2005/Atom"/>
    </msg>
  </chkl:messages>
'''


class TestADTCoreReference(unittest.TestCase):

    def test_name_none(self):
        ref = sap.adt.objects.ADTCoreData.Reference(name=None)
        self.assertIsNone(ref.name)

        ref.name = None
        self.assertIsNone(ref.name)

    def test_name_upper(self):
        ref = sap.adt.objects.ADTCoreData.Reference(name='package')
        self.assertEqual(ref.name, 'PACKAGE')

        ref.name = 'child'
        self.assertEqual(ref.name, 'CHILD')


class TestADTObject(unittest.TestCase):

    def test_uri(self):
        victory = DummyADTObject()

        self.assertEquals(victory.uri, 'awesome/success/noobject')

    def test_str(self):
        victory = DummyADTObject(name='objname')

        self.assertEquals(str(victory), 'DUMMY/S objname')

    def test_lock_modify_ok(self):
        connection = Connection([LOCK_RESPONSE_OK, LOCK_RESPONSE_OK])

        victory = DummyADTObject(connection=connection)
        handle = victory.lock()
        self.assertEquals(handle, 'win')

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/awesome/success/noobject')])

        lock_request = connection.execs[0]
        self.assertEqual(sorted(lock_request.params.keys()), ['_action', 'accessMode'])
        self.assertEqual(lock_request.params['_action'], 'LOCK')
        self.assertEqual(lock_request.params['accessMode'], 'MODIFY')

        self.assertEqual(sorted(lock_request.headers.keys()), ['Accept', 'X-sap-adt-sessiontype'])
        self.assertEqual(lock_request.headers['X-sap-adt-sessiontype'], 'stateful')
        self.assertEqual(lock_request.headers['Accept'], 'application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result;q=0.8, application/vnd.sap.as+xml;charset=UTF-8;dataname=com.sap.adt.lock.result2;q=0.9')

        handle = victory.lock()
        self.assertEquals(handle, 'win')

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
        handle = victory.lock()
        victory.unlock(handle)

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
        connection = Connection([LOCK_RESPONSE_OK, None])

        victory = DummyADTObject(connection=connection)

        try:
            victory.unlock('NOTLOCKED')
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: not locked')

        self.assertEqual(
            [(e.method, e.adt_uri) for e in connection.execs],
            [('POST', '/sap/bc/adt/awesome/success/noobject')])

        unlock_request = connection.execs[0]
        self.assertEqual(sorted(unlock_request.params.keys()), ['_action', 'lockHandle'])
        self.assertEqual(unlock_request.params['_action'], 'UNLOCK')
        self.assertEqual(unlock_request.params['lockHandle'], 'NOTLOCKED')

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
        self.assertEqual(str(cm.exception), f'Could not activate: {ACTIVATE_RESPONSE_FAILED}')

    def test_create_ok_wihout_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='creator')

        victory.create()

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/awesome/success')

        self.assertEqual(connection.execs[0].headers['Content-Type'], 'application/vnd.sap.super.cool.txt+xml; charset=utf-8')
        self.assertEqual(sorted(connection.execs[0].headers.keys()), ['Content-Type'])

        self.assertIsNone(connection.execs[0].params)

        self.maxDiff = None
        self.assertEqual(connection.execs[0].body.decode('utf-8'), '''<?xml version="1.0" encoding="UTF-8"?>
<win:dummies xmlns:win="http://www.example.com/never/lose" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DUMMY/S" adtcore:description="adt fixtures dummy object" adtcore:name="creator">
<adtcore:packageRef/>
</win:dummies>''' )

    def test_create_ok_wih_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='creator')

        victory.create(corrnr='NPL000008')

        self.assertEqual(connection.execs[0].params['corrNr'], 'NPL000008')
        self.assertEqual(sorted(connection.execs[0].params.keys()), ['corrNr'])

    def test_create_v2(self):
        conn = Connection(collections={'/sap/bc/adt/awesome/success': ['application/vnd.sap.super.cool.txt.v2+xml']})
        victory = DummyADTObject(connection=conn)
        victory.create()

        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.super.cool.txt.v2+xml; charset=utf-8'})

        self.maxDiff = None
        self.assertEqual(conn.execs[0].body.decode('utf-8'), '''<?xml version="1.0" encoding="UTF-8"?>
<win:dummies xmlns:win="http://www.example.com/never/lose" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DUMMY/S" adtcore:description="adt fixtures dummy object" adtcore:name="noobject">
<adtcore:packageRef/>
<elemv2>version2</elemv2>
</win:dummies>''' )

    def test_create_v0_priority(self):
        conn = Connection(collections={'/sap/bc/adt/awesome/success': ['application/vnd.sap.super.cool.txt+xml',
                                                                       'application/vnd.sap.super.cool.txt.v2+xml']})
        victory = DummyADTObject(connection=conn)
        victory.create()

        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.super.cool.txt+xml; charset=utf-8'})

    def test_create_mime_not_found(self):
        conn = Connection(collections={'/sap/bc/adt/awesome/success': ['application/something.else+xml']})
        victory = DummyADTObject(connection=conn)

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            victory.create()

        self.assertEqual(str(caught.exception), 'Not supported mimes: application/something.else+xml not in application/vnd.sap.super.cool.txt+xml;application/vnd.sap.super.cool.txt.v2+xml')


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

    def test_open_editor_default(self):
        connection = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='editor_test')

        with victory.open_editor() as editor:
            self.assertEqual(editor.uri, 'awesome/success/editor_test')
            self.assertEqual(editor.mimetype, 'application/vnd.sap.super.cool.txt+xml')
            self.assertEqual(editor.connection, connection)
            self.assertEqual(editor.lock_handle, 'win')
            self.assertIsNone(editor.corrnr)

    def test_open_editor_with_lock_and_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='editor_no_lock')

        with victory.open_editor(corrnr='123456', lock_handle='clock') as editor:
            self.assertEqual(editor.lock_handle, 'clock')
            self.assertEqual(editor.corrnr, '123456')

    def test_push(self):
        connection = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='SOFTWARE_ENGINEER')

        with victory.open_editor() as editor:
            editor.push()

        self.assertEqual(connection.mock_methods(), [('POST', '/sap/bc/adt/awesome/success/software_engineer'),
                                                     ('PUT', '/sap/bc/adt/awesome/success/software_engineer'),
                                                     ('POST', '/sap/bc/adt/awesome/success/software_engineer')])

        request = connection.execs[1]

        self.assertEqual(sorted(request.headers.keys()), ['Content-Type'])
        self.assertEqual(request.headers['Content-Type'], 'application/vnd.sap.super.cool.txt+xml; charset=utf-8')

        self.assertEqual(sorted(request.params.keys()), ['lockHandle'])
        self.assertEqual(request.params['lockHandle'], 'win')

        self.maxDiff = None
        self.assertEqual(request.body.decode('utf-8'), '''<?xml version="1.0" encoding="UTF-8"?>
<win:dummies xmlns:win="http://www.example.com/never/lose" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="DUMMY/S" adtcore:description="adt fixtures dummy object" adtcore:name="SOFTWARE_ENGINEER">
<adtcore:packageRef/>
</win:dummies>''')


class TestADTObjectType(unittest.TestCase):

    def setUp(self):
        self.adt_object = sap.adt.objects.ADTObjectType(
            'code',
            'basepath',
            sap.adt.objects.XMLNamespace(name='xmlnsname', uri='uri'),
            'mimetype',
            {'text/plain': '/text'},
            'xmlelementname')

    def test_adt_object_type_basepath(self):
        self.assertEqual(self.adt_object.basepath, 'basepath')

        self.adt_object.basepath = 'newpath'
        self.assertEqual(self.adt_object.basepath, 'newpath')

    def test_adt_object_type_xmlelement(self):
        self.assertEqual(self.adt_object.xmlelement, 'xmlnsname:xmlelementname')

    def test_adt_object_type_mime_string(self):
        self.assertEqual(self.adt_object.mimetype, 'mimetype')
        self.assertEqual(self.adt_object.all_mimetypes, ['mimetype'])

    def test_adt_object_type_mime_list(self):
        self.adt_object._mimetype = ['mimetype2', 'mimetype1']
        self.assertEqual(self.adt_object.mimetype, 'mimetype2')
        self.assertEqual(self.adt_object.all_mimetypes, ['mimetype2','mimetype1'])


class TestMIMEVersion(unittest.TestCase):

    def test_parse_out_versin_from_mime(self):
        known_mime_variants = [
            ('application/vnd.sap.ap.adt.bopf.businessobjects.v2+xml', '2'),
            ('text/plain', None),
            ('application/vnd.sap.adt.quickfixes.evaluation+xml;version=1.0.0', '1.0.0'),
            ('application/vnd.sap.adt.wdy.view+xml', '0'),
            ('application/vnd.sap.adt.wdy.view.v1+xml', '1')
        ]

        for mime, exp_version in known_mime_variants:
            act_version = sap.adt.objects.mimetype_to_version(mime)
            self.assertEqual(act_version, exp_version, mime)


if __name__ == '__main__':
    unittest.main()
