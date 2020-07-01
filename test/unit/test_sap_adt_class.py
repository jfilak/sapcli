#!/usr/bin/env python3

import unittest

from sap import get_logger
import sap.adt

from mock import Connection, Response

from fixtures_adt import (LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, TEST_CLASSES_READ_RESPONSE_OK,
                          DEFINITIONS_READ_RESPONSE_OK, IMPLEMENTATIONS_READ_RESPONSE_OK)

from fixtures_adt_clas import CREATE_CLASS_ADT_XML, GET_CLASS_ADT_XML


FIXTURE_CLASS_MAIN_CODE='''class zcl_hello_world definition public.
  public section.
    methods: greet.
endclass.
class zcl_hello_world implementation.
  method greet.
    write: 'Hola!'.
  endmethod.
endclass.
'''


class TestADTClass(unittest.TestCase):

    def test_adt_class_serialize(self):
        conn = Connection()

        metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', master_system='NPL', responsible='FILAK')
        clas = sap.adt.Class(conn, 'ZCL_HELLO_WORLD', package='$TEST', metadata=metadata)
        clas.description = 'Say hello!'
        clas.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/oo/classes')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.oo.classes.v2+xml; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3].decode('utf-8'), CREATE_CLASS_ADT_XML)

        self.assertEqual('CLAS/OC ZCL_HELLO_WORLD', str(clas))
        self.assertEqual('CLAS/OC ZCL_HELLO_WORLD/definitions', str(clas.definitions))
        self.assertEqual('CLAS/OC ZCL_HELLO_WORLD/implementations', str(clas.implementations))
        self.assertEqual('CLAS/OC ZCL_HELLO_WORLD/testclasses', str(clas.test_classes))

    def test_adt_class_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        clas = sap.adt.Class(conn, 'ZCL_HELLO_WORLD')
        with clas.open_editor() as editor:
            editor.write(FIXTURE_CLASS_MAIN_CODE)

        put_request = conn.execs[1]
        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/oo/classes/zcl_hello_world/source/main')
        self.assertEqual(sorted(put_request.headers), ['Accept', 'Content-Type'])
        self.assertEqual(put_request.headers['Accept'], 'text/plain')
        self.assertEqual(put_request.headers['Content-Type'], 'text/plain; charset=utf-8')

        self.assertEqual(sorted(put_request.params), ['lockHandle'])
        self.assertEqual(put_request.params['lockHandle'], 'win')

        self.maxDiff = None
        self.assertEqual(put_request.body, bytes(FIXTURE_CLASS_MAIN_CODE[:-1], 'utf-8'))

    def test_adt_class_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        clas = sap.adt.Class(conn, 'ZCL_HELLO_WORLD')
        with clas.open_editor(corrnr='420') as editor:
            editor.write(FIXTURE_CLASS_MAIN_CODE)

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})

    def include_read_test(self, response, getter, includes_uri):
        conn = Connection([response])

        clas = sap.adt.Class(conn, 'ZCL_HELLO_WORLD')
        source_code = getter(clas).text

        self.assertEqual(source_code, response.text)

        self.assertEqual(
            [(e.method, e.adt_uri) for e in conn.execs],
            [('GET', f'/sap/bc/adt/oo/classes/zcl_hello_world/{includes_uri}')])

        get_request = conn.execs[0]
        self.assertEqual(sorted(get_request.headers), ['Accept'])
        self.assertEqual(get_request.headers['Accept'], 'text/plain')

        self.assertIsNone(get_request.params)

    def test_adt_class_read_definitions(self):
        self.include_read_test(DEFINITIONS_READ_RESPONSE_OK, lambda clas: clas.definitions, 'includes/definitions')

    def test_adt_class_read_implementations(self):
        self.include_read_test(IMPLEMENTATIONS_READ_RESPONSE_OK, lambda clas: clas.implementations, 'includes/implementations')

    def test_adt_class_read_tests(self):
        self.include_read_test(TEST_CLASSES_READ_RESPONSE_OK, lambda clas: clas.test_classes, 'includes/testclasses')

    def include_write_test(self, getter, includes_uri):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        clas = sap.adt.Class(conn, 'ZCL_HELLO_WORLD')
        with getter(clas).open_editor() as editor:
            editor.write('* new content')

        put_request = conn.execs[1]
        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, f'/sap/bc/adt/oo/classes/zcl_hello_world/{includes_uri}')
        self.assertEqual(sorted(put_request.headers), ['Accept', 'Content-Type'])
        self.assertEqual(put_request.headers['Accept'], 'text/plain')
        self.assertEqual(put_request.headers['Content-Type'], 'text/plain; charset=utf-8')

        self.assertEqual(sorted(put_request.params), ['lockHandle'])
        self.assertEqual(put_request.params['lockHandle'], 'win')

        self.maxDiff = None
        self.assertEqual(put_request.body, b'* new content')

    def test_adt_class_write_definitions(self):
        self.include_write_test(lambda clas: clas.definitions, 'includes/definitions')

    def test_adt_class_write_implementations(self):
        self.include_write_test(lambda clas: clas.implementations, 'includes/implementations')

    def test_adt_class_write_tests(self):
        self.include_write_test(lambda clas: clas.test_classes, 'includes/testclasses')

    def include_activate_test(self, getter, includes_uri):
        conn = Connection([EMPTY_RESPONSE_OK])

        clas = sap.adt.Class(conn, 'ZCL_HELLO_WORLD')
        sap.adt.wb.activate(getter(clas))

        post_request = conn.execs[0]
        self.assertEqual(post_request.method, 'POST')
        self.assertEqual(post_request.adt_uri, '/sap/bc/adt/activation')

        self.assertIn('<adtcore:objectReference adtcore:uri="/sap/bc/adt/oo/classes/zcl_hello_world" adtcore:name="ZCL_HELLO_WORLD"/>',
                      post_request.body)

    def test_adt_class_activate_definitions(self):
        self.include_activate_test(lambda clas: clas.definitions, 'includes/definitions')

    def test_adt_class_activate_implementations(self):
        self.include_activate_test(lambda clas: clas.implementations, 'includes/implementations')

    def test_adt_class_activate_tests(self):
        self.include_activate_test(lambda clas: clas.test_classes, 'includes/testclasses')

    def test_adt_class_fetch(self):
        conn = Connection([Response(text=GET_CLASS_ADT_XML, status_code=200, headers={})])
        clas = sap.adt.Class(conn, 'ZCL_HELLO_WORLD')
        clas.fetch()

        self.assertEqual(clas.name, 'ZCL_HELLO_WORLD')
        self.assertEqual(clas.active, 'active')
        self.assertEqual(clas.master_language, 'EN')
        self.assertEqual(clas.description, 'You cannot stop me!')
        self.assertEqual(clas.modeled, False)
        self.assertEqual(clas.fix_point_arithmetic, True)


if __name__ == '__main__':
    unittest.main()
