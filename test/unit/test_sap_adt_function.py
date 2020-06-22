#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, PropertyMock, patch

from sap.errors import SAPCliError
import sap.adt.wb

from mock import Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, OBJECT_METADATA

from fixtures_adt_function import (
        CREATE_FUNCTION_GROUP_ADT_XML,
        CREATE_FUNCTION_MODULE_ADT_XML,
        GET_FUNCTION_GROUP_ADT_XML,
        GET_FUNCTION_MODULE_ADT_XML)


class TestFunctionGroup(unittest.TestCase):

    def test_function_group_serializable(self):
        conn = Connection()

        fugr = sap.adt.FunctionGroup(conn, 'ZFG_HELLO_WORLD', package='$TEST', metadata=OBJECT_METADATA)
        fugr.description = 'Hello FUGR!'
        fugr.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/functions/groups')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.functions.groups.v3+xml'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], CREATE_FUNCTION_GROUP_ADT_XML)

    def test_function_group_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        fugr = sap.adt.FunctionGroup(conn, 'ZFG_HELLO_WORLD')

        with fugr.open_editor() as editor:
            editor.write('FUGR')

        put_request = conn.execs[1]
        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/functions/groups/zfg_hello_world/source/main')

        self.assertEqual(sorted(put_request.headers), ['Accept', 'Content-Type'])
        self.assertEqual(put_request.headers['Accept'], 'text/plain')
        self.assertEqual(put_request.headers['Content-Type'], 'text/plain; charset=utf-8')

        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body, b'FUGR')

    def test_function_group_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        fugr = sap.adt.FunctionGroup(conn, 'ZFG_HELLO_WORLD')
        with fugr.open_editor(corrnr='420') as editor:
            editor.write('FUGR')

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})

    def test_function_group_fetch(self):
        conn = Connection([Response(text=GET_FUNCTION_GROUP_ADT_XML, status_code=200, headers={})])
        fugr = sap.adt.FunctionGroup(conn, 'ZFG_HELLO_WORLD')
        fugr.fetch()

        self.assertEqual(fugr.name, 'ZFG_HELLO_WORLD')
        self.assertEqual(fugr.active, 'active')
        self.assertEqual(fugr.master_language, 'EN')
        self.assertEqual(fugr.description, 'You cannot stop me!')
        self.assertEqual(fugr.fix_point_arithmetic, True)


class TestFunctionModule(unittest.TestCase):

    def test_function_module_serializable(self):
        conn = Connection()

        function = sap.adt.FunctionModule(conn, 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD', metadata=OBJECT_METADATA)
        function.description = 'Hello Function!'
        function.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.functions.fmodules.v3+xml'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3], CREATE_FUNCTION_MODULE_ADT_XML)

    def test_function_module_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        function = sap.adt.FunctionModule(conn, 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD')

        with function.open_editor() as editor:
            editor.write('FUGR')

        put_request = conn.execs[1]
        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world/source/main')

        self.assertEqual(sorted(put_request.headers), ['Accept', 'Content-Type'])
        self.assertEqual(put_request.headers['Accept'], 'text/plain')
        self.assertEqual(put_request.headers['Content-Type'], 'text/plain; charset=utf-8')

        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body, b'FUGR')

    def test_function_module_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        function = sap.adt.FunctionModule(conn, 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD')
        with function.open_editor(corrnr='420') as editor:
            editor.write('FUGR')

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})

    def test_function_module_fetch(self):
        conn = Connection([Response(text=GET_FUNCTION_MODULE_ADT_XML, status_code=200, headers={})])
        function = sap.adt.FunctionModule(conn, 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD')
        function.fetch()

        self.assertEqual(function.name, 'Z_FN_HELLO_WORLD')
        self.assertEqual(function.active, 'inactive')
        self.assertEqual(function.description, 'You cannot stop me!')
        self.assertEqual(function.processing_type, 'normal')
        self.assertEqual(function.release_state, 'notReleased')

    @patch('sap.adt.function.find_mime_version')
    def test_function_module_mime_version_ok(self, fake_find_mime_version):
        mime_template = 'application/vnd.sap.adt.functions.{0}.v3+xml'
        fake_find_mime_version.return_value = (mime_template.format('groups'), 'v3')

        connection = Mock()
        function = sap.adt.FunctionModule(connection, 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD')
        xml, mime = function.serialize()

        self.assertEqual(mime, mime_template.format('fmodules'))
        fake_find_mime_version.assert_called_once_with(connection, sap.adt.FunctionGroup.OBJTYPE)

    @patch('sap.adt.function.find_mime_version')
    def test_function_module_mime_version_err(self, fake_find_mime_version):
        mime_template = 'application/vnd.sap.adt.functions.{0}.vY+xml'
        group_mime = mime_template.format('groups')
        fake_find_mime_version.return_value = (group_mime, 'vY')

        function = sap.adt.FunctionModule(Mock(), 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD')
        with self.assertRaises(RuntimeError) as caught:
            function.serialize()

        self.assertEqual(str(caught.exception), f'Function Groups and Function Modules out of sync for: {group_mime}')


if __name__ == '__main__':
    unittest.main()
