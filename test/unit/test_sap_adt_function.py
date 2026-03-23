#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, PropertyMock, patch

from sap.errors import SAPCliError
import sap.adt.wb
from sap.platform.abap.ddic import RSIMP, RSCHA, RSEXP, RSEXC, RSTBL

from mock import Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, OBJECT_METADATA

from fixtures_adt_function import (
        CREATE_FUNCTION_GROUP_ADT_XML,
        CREATE_FUNCTION_MODULE_ADT_XML,
        GET_FUNCTION_GROUP_ADT_XML,
        GET_FUNCTION_MODULE_ADT_XML,
        CREATE_FUNCTION_INCLUDE_ADT_XML,
        GET_FUNCTION_INCLUDE_ADT_XML,
        FUNCTION_MODULE_CODE,
        FUNCTION_MODULE_CODE_ABAPGIT,
        SEARCH_FUNCTION_MODULE_RESPONSE_XML,
        SEARCH_FUNCTION_MODULE_NOT_FOUND_RESPONSE_XML,
        SEARCH_FUNCTION_MODULE_WRONG_TYPE_RESPONSE_XML,)


class TestFunctionGroup(unittest.TestCase):

    def test_function_group_serializable(self):
        conn = Connection()

        fugr = sap.adt.FunctionGroup(conn, 'ZFG_HELLO_WORLD', package='$TEST', metadata=OBJECT_METADATA)
        fugr.description = 'Hello FUGR!'
        fugr.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/functions/groups')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.functions.groups.v3+xml; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3].decode('utf-8'), CREATE_FUNCTION_GROUP_ADT_XML)

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

    @patch('sap.adt.function.Repository')
    def test_function_group_walk(self, fake_repo):
        fake_walk = Mock()
        fake_walk.walk_step.return_value = 'subpackages', 'objects'
        fake_repo.return_value = fake_walk

        fugr = sap.adt.FunctionGroup(None, 'ZFG_HELLO_WORLD')

        self.assertEqual(fugr.walk(), [([], [], 'objects')])


class TestGroupNameFromUri(unittest.TestCase):

    def test_valid_uri(self):
        group = sap.adt.FunctionGroup.group_name_from_uri(
            '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world')

        self.assertEqual(group, 'ZFG_HELLO_WORLD')

    def test_valid_uri_returns_upper_case(self):
        group = sap.adt.FunctionGroup.group_name_from_uri(
            '/sap/bc/adt/functions/groups/zfg_lower/fmodules/z_fn_test')

        self.assertEqual(group, 'ZFG_LOWER')

    def test_invalid_prefix_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            sap.adt.FunctionGroup.group_name_from_uri(
                '/sap/bc/adt/programs/includes/z_fn_hello_world')

        self.assertIn('does not contain the expected Function Group marker', str(caught.exception))

    def test_empty_uri_raises(self):
        with self.assertRaises(SAPCliError):
            sap.adt.FunctionGroup.group_name_from_uri('')

    def test_none_uri_raises(self):
        with self.assertRaises(SAPCliError):
            sap.adt.FunctionGroup.group_name_from_uri(None)

    def test_non_standard_adt_root(self):
        group = sap.adt.FunctionGroup.group_name_from_uri(
            '/custom/root/functions/groups/zfg_custom/fmodules/z_fn_test')

        self.assertEqual(group, 'ZFG_CUSTOM')

    def test_empty_group_name_raises(self):
        with self.assertRaises(SAPCliError) as caught:
            sap.adt.FunctionGroup.group_name_from_uri(
                '/sap/bc/adt/functions/groups//fmodules/z_fn_hello_world')

        self.assertIn('contains an empty Function Group name', str(caught.exception))


class TestFunctionModule(unittest.TestCase):

    def test_function_module_serializable(self):
        conn = Connection()

        function = sap.adt.FunctionModule(conn, 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD', metadata=OBJECT_METADATA)
        function.description = 'Hello Function!'
        function.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.functions.fmodules.v3+xml; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3].decode('utf-8'), CREATE_FUNCTION_MODULE_ADT_XML)

    @patch('sap.adt.function.find_mime_version')
    def test_function_module_correct_mime(self, fake_find_mime_version):
        conn = Connection()

        function = sap.adt.FunctionModule(conn, 'Z_FN_HELLO_WORLD', 'ZFG_HELLO_WORLD', metadata=OBJECT_METADATA)

        try:
            function._get_mime_and_version()
        except SAPCliError:
            pass

        fake_find_mime_version.assert_called_once_with(conn, sap.adt.FunctionModule.OBJTYPE)

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

    def test_function_module_get_parameters(self):
        conn = Connection([Response(text=FUNCTION_MODULE_CODE, status_code=200, headers={})])
        function = sap.adt.FunctionModule(conn, 'TEST_FUNCTION', 'TEST_FUNCTION_GROUP')
        parameters = function.get_parameters()

        self.assertEqual(parameters['IMPORTING'], ["VALUE(IMPORT_PARAM_1) TYPE  STRING DEFAULT '/src/'",
                                                   "VALUE(IMPORT_PARAM_2) TYPE  STRING"])
        self.assertEqual(parameters['EXPORTING'], ["VALUE(EXPORT_PARAM_1) TYPE  BAPIRET2",
                                                   "REFERENCE(EXPORT_PARAM_2) TYPE  STRING"])
        self.assertEqual(parameters['CHANGING'], ["REFERENCE(CHANGING_PARAM_1) TYPE  BAPIRET2",
                                                  "VALUE(CHANGING_PARAM_2) TYPE  BAPIRET2 DEFAULT 'default'"])
        self.assertEqual(parameters['TABLES'], ["TABLES_PARAM_1 TYPE  BAPIRET2",
                                                "TABLES_PARAM_2 TYPE  BAPIRET2 OPTIONAL",
                                                "TABLES_PARAM_3 TYPE  BAPIRET2_T"])
        self.assertEqual(parameters['EXCEPTIONS'], ["TEST_EXCEPTION"])

    def test_function_module_get_local_interface(self):
        conn = Connection([Response(text=FUNCTION_MODULE_CODE, status_code=200, headers={})])
        function = sap.adt.FunctionModule(conn, 'TEST_FUNCTION', 'TEST_FUNCTION_GROUP')
        local_interface = function.get_local_interface()

        self.maxDiff=None
        self.assertEqual(local_interface['IMPORTING'], [RSIMP(PARAMETER='IMPORT_PARAM_1', DEFAULT='&apos;/src/&apos;', OPTIONAL='X', TYP='STRING'),
                                                        RSIMP(PARAMETER='IMPORT_PARAM_2', TYP='STRING')])
        self.assertEqual(local_interface['CHANGING'], [RSCHA(PARAMETER='CHANGING_PARAM_1', REFERENCE='X', TYP='BAPIRET2'),
                                                       RSCHA(PARAMETER='CHANGING_PARAM_2', DEFAULT='&apos;default&apos;', OPTIONAL='X', TYP='BAPIRET2')])
        self.assertEqual(local_interface['EXPORTING'], [RSEXP(PARAMETER='EXPORT_PARAM_1', TYP='BAPIRET2'),
                                                        RSEXP(PARAMETER='EXPORT_PARAM_2', REFERENCE='X', TYP='STRING')])
        self.assertEqual(local_interface['TABLES'], [RSTBL(PARAMETER='TABLES_PARAM_1', TYP='BAPIRET2'),
                                                     RSTBL(PARAMETER='TABLES_PARAM_2', OPTIONAL='X', TYP='BAPIRET2'),
                                                     RSTBL(PARAMETER='TABLES_PARAM_3', TYP='BAPIRET2_T')])
        self.assertEqual(local_interface['EXCEPTIONS'], [RSEXC(EXCEPTION='TEST_EXCEPTION')])

    def test_function_module_get_body(self):
        conn = Connection([Response(text=FUNCTION_MODULE_CODE, status_code=200, headers={})])
        function = sap.adt.FunctionModule(conn, 'TEST_FUNCTION', 'TEST_FUNCTION_GROUP')
        body = function.get_body()

        self.assertEqual(body, '''    Write 'Hello World'.''')


class TestResolveGroup(unittest.TestCase):

    def test_resolve_group_found(self):
        connection = Connection([
            Response(text=SEARCH_FUNCTION_MODULE_RESPONSE_XML, status_code=200)
        ])

        group = sap.adt.FunctionModule.resolve_group(connection, 'Z_FN_HELLO_WORLD')

        self.assertEqual(group, 'ZFG_HELLO_WORLD')

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertIn('repository/informationsystem/search', connection.execs[0].adt_uri)
        self.assertEqual(connection.execs[0].params['query'], 'Z_FN_HELLO_WORLD')

    def test_resolve_group_not_found_empty(self):
        connection = Connection([
            Response(text=SEARCH_FUNCTION_MODULE_NOT_FOUND_RESPONSE_XML, status_code=200)
        ])

        with self.assertRaises(SAPCliError) as caught:
            sap.adt.FunctionModule.resolve_group(connection, 'Z_FN_NONEXISTENT')

        self.assertEqual(str(caught.exception),
                         'Could not find function module "Z_FN_NONEXISTENT" in the system')

    def test_resolve_group_not_found_wrong_type(self):
        connection = Connection([
            Response(text=SEARCH_FUNCTION_MODULE_WRONG_TYPE_RESPONSE_XML, status_code=200)
        ])

        with self.assertRaises(SAPCliError) as caught:
            sap.adt.FunctionModule.resolve_group(connection, 'Z_FN_HELLO_WORLD')

        self.assertEqual(str(caught.exception),
                         'Could not find function module "Z_FN_HELLO_WORLD" in the system')

    def test_resolve_group_case_insensitive(self):
        connection = Connection([
            Response(text=SEARCH_FUNCTION_MODULE_RESPONSE_XML, status_code=200)
        ])

        group = sap.adt.FunctionModule.resolve_group(connection, 'z_fn_hello_world')

        self.assertEqual(group, 'ZFG_HELLO_WORLD')


class TestFunctionInclude(unittest.TestCase):

    def test_function_include_serializable(self):
        conn = Connection()

        include = sap.adt.FunctionInclude(conn, 'ZFI_HELLO_WORLD', 'ZFG_HELLO_WORLD', metadata=OBJECT_METADATA)
        include.description = 'Hello Include!'
        include.create()

        self.assertEqual(len(conn.execs), 1)

        self.assertEqual(conn.execs[0][0], 'POST')
        self.assertEqual(conn.execs[0][1], '/sap/bc/adt/functions/groups/zfg_hello_world/includes')
        self.assertEqual(conn.execs[0][2], {'Content-Type': 'application/vnd.sap.adt.functions.fincludes.v2+xml; charset=utf-8'})
        self.maxDiff = None
        self.assertEqual(conn.execs[0][3].decode('utf-8'), CREATE_FUNCTION_INCLUDE_ADT_XML)

    @patch('sap.adt.function.find_mime_version')
    def test_function_include_correct_mime(self, fake_find_mime_version):
        conn = Connection()

        include = sap.adt.FunctionInclude(conn, 'ZFI_HELLO_WORLD', 'ZFG_HELLO_WORLD', metadata=OBJECT_METADATA)

        try:
            include._get_mime_and_version()
        except SAPCliError:
            pass

        fake_find_mime_version.assert_called_once_with(conn, sap.adt.FunctionInclude.OBJTYPE)

    def test_function_include_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        include = sap.adt.FunctionInclude(conn, 'ZFI_HELLO_WORLD', 'ZFG_HELLO_WORLD')

        with include.open_editor() as editor:
            editor.write('FUGR')

        put_request = conn.execs[1]
        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/functions/groups/zfg_hello_world/includes/zfi_hello_world/source/main')

        self.assertEqual(sorted(put_request.headers), ['Accept', 'Content-Type'])
        self.assertEqual(put_request.headers['Accept'], 'text/plain')
        self.assertEqual(put_request.headers['Content-Type'], 'text/plain; charset=utf-8')

        self.assertEqual(put_request.params, {'lockHandle': 'win'})

        self.maxDiff = None
        self.assertEqual(put_request.body, b'FUGR')

    def test_function_include_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, None])

        include = sap.adt.FunctionInclude(conn, 'ZFI_HELLO_WORLD', 'ZFG_HELLO_WORLD')

        with include.open_editor(corrnr='420') as editor:
            editor.write('FUGR')

        put_request = conn.execs[1]
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})

    def test_function_include_fetch(self):
        conn = Connection([Response(text=GET_FUNCTION_INCLUDE_ADT_XML, status_code=200, headers={})])
        include = sap.adt.FunctionInclude(conn, 'ZFI_HELLO_WORLD', 'ZFG_HELLO_WORLD')
        include.fetch()

        self.assertEqual(include.name, 'ZFI_HELLO_WORLD')
        self.assertEqual(include.active, 'inactive')
        self.assertEqual(include.description, 'Hello Include!')
        self.assertEqual(include.language(), None)
        self.assertEqual(include.master_language(), None)
        self.assertEqual(include.master_system(), None)
        self.assertEqual(include.responsible(), None)
        self.assertEqual(include.reference(), None)


if __name__ == '__main__':
    unittest.main()
