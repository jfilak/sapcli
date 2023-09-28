#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import call, patch, Mock, PropertyMock, MagicMock, mock_open
from io import StringIO

import sap.cli.function

from mock import Connection, Response, Request
from fixtures_adt import EMPTY_RESPONSE_OK, LOCK_RESPONSE_OK
from fixtures_adt_wb import RESPONSE_ACTIVATION_OK
from fixtures_adt_function import (
        CLI_CREATE_FUNCTION_GROUP_ADT_XML,
        CREATE_FUNCTION_MODULE_ADT_XML,
        GET_FUNCTION_MODULE_ADT_XML,
        PUT_FUNCITON_MODULE_ADT_XML,
        FAKE_LOCK_HANDLE,
        CREATE_FUNCTION_GROUP_INCLUDE_ADT_XML,
        WRITE_FUNCTION_GROUP_INCLUDE_BODY,
        READ_FUNCTION_GROUP_INCLUDE_BODY,
        FUNCTION_GROUP_INCLUDE_ADT_XML,
        ACTIVATE_FUNCTION_GROUP_INCLUDE_BODY
        )

fugr_parser = ArgumentParser()
sap.cli.function.CommandGroupFunctionGroup().install_parser(fugr_parser)

fm_parser = ArgumentParser()
sap.cli.function.CommandGroupFunctionModule().install_parser(fm_parser)

fugri_parser = ArgumentParser()
sap.cli.function.CommandGroupFunctionGroupInclude().install_parser(fugri_parser)


def fugr_parse_args(*argv):
    global fugr_parser
    return fugr_parser.parse_args(argv)


def fm_parse_args(*argv):
    global fm_parser
    return fm_parser.parse_args(argv)


def fugri_parse_args(*argv):
    global fugri_parser
    return fugri_parser.parse_args(argv)


class TestFunctionGroupCreate(unittest.TestCase):

    def test_create_fugr_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK], user='FILAK')

        args = fugr_parse_args('create', 'ZFG_HELLO_WORLD', 'Hello FUGR!', '$TEST')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/functions/groups')])

        post_req = connection.execs[0]

        self.assertEqual(sorted(post_req.headers.keys()), ['Content-Type'])
        self.assertEqual(post_req.headers['Content-Type'], 'application/vnd.sap.adt.functions.groups.v3+xml; charset=utf-8')

        self.assertIsNone(post_req.params)

        self.maxDiff = None
        self.assertEqual(post_req.body.decode('utf-8'), CLI_CREATE_FUNCTION_GROUP_ADT_XML)


class TestFunctionModuleCreate(unittest.TestCase):

    def test_create_func_mod_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = fm_parse_args('create', 'ZFG_HELLO_WORLD', 'Z_FN_HELLO_WORLD', 'Hello Function!')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules')])

        post_req = connection.execs[0]

        self.assertEqual(sorted(post_req.headers.keys()), ['Content-Type'])
        self.assertEqual(post_req.headers['Content-Type'], 'application/vnd.sap.adt.functions.fmodules.v3+xml; charset=utf-8')

        self.assertIsNone(post_req.params)

        self.maxDiff = None
        self.assertEqual(post_req.body.decode('utf-8'), CREATE_FUNCTION_MODULE_ADT_XML)


class TestFunctionModuleWrite(unittest.TestCase):

    def assert_raises_for_invalid_file_name(self, invalid_name, basename=None):
        connection = MagicMock()

        args = fm_parse_args('write', '-', '-', invalid_name)

        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            args.execute(connection, args)

        basename = basename if basename is not None else invalid_name

        self.assertEqual(str(caught.exception),
                         f'"{basename}" does not match the pattern FUNCTIONGROUP.fugr.FUNCTIONMODULE.abap')

    def test_write_name_from_invalid_file_name(self):
        self.assert_raises_for_invalid_file_name('')
        self.assert_raises_for_invalid_file_name('.')
        self.assert_raises_for_invalid_file_name('.fugr.module.abap')
        self.assert_raises_for_invalid_file_name('group..module.abap')
        self.assert_raises_for_invalid_file_name('group.fugr.module.txt')
        self.assert_raises_for_invalid_file_name('group.fugr..abap')

    def test_write_name_from_valid_file_name(self):
        connection = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        args = fm_parse_args('write', '-', '-', './src/zfg_hello_world.fugr.z_fn_hello_world.abap')
        with patch('sap.cli.object.open', mock_open(read_data='source code')) as fake_open:
            args.execute(connection, args)

        fake_open.assert_called_once_with('./src/zfg_hello_world.fugr.z_fn_hello_world.abap', 'r', encoding='utf8')

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs],
                          [('POST', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world'),
                           ('PUT', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world/source/main'),
                           ('POST', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world')])


class TestFunctionModuleChattr(unittest.TestCase):

    def test_fmod_chattr_rfc(self):
        connection = Connection([Response(text=GET_FUNCTION_MODULE_ADT_XML,
                                          status_code=200,
                                          headers={'Content-Type': 'application/vnd.sap.adt.functions.fmodules.v3+xml; charset=utf-8'}),
                                 LOCK_RESPONSE_OK,
                                 EMPTY_RESPONSE_OK,
                                 EMPTY_RESPONSE_OK])

        args = fm_parse_args('chattr', 'ZFG_HELLO_WORLD', 'Z_FN_HELLO_WORLD', '-t', 'rfc')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs],
                          [('GET', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world'),
                           ('POST', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world'),
                           ('PUT', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world'),
                           ('POST', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules/z_fn_hello_world')])

        put_req = connection.execs[2]

        self.assertEqual(sorted(put_req.headers.keys()), ['Content-Type'])
        self.assertEqual(put_req.headers['Content-Type'], 'application/vnd.sap.adt.functions.fmodules.v3+xml; charset=utf-8')

        self.assertEqual(sorted(put_req.params.keys()), ['lockHandle'])
        self.assertEqual(put_req.params['lockHandle'], 'win')

        self.maxDiff = None
        self.assertEqual(put_req.body.decode('utf-8'), PUT_FUNCITON_MODULE_ADT_XML)


class TestFunctionGroupIncludeCreate(unittest.TestCase):

    def test_create_fugr_include_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK], user='FILAK')

        args = fugri_parse_args('create', 'ZFG_HELLO_WORLD', 'ZFG_I_HELLO_WORLD', 'Hello FUGR/I!')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/functions/groups/zfg_hello_world/includes')])

        post_req = connection.execs[0]

        self.assertEqual(sorted(post_req.headers.keys()), ['Content-Type'])
        self.assertEqual(post_req.headers['Content-Type'], 'application/vnd.sap.adt.functions.fincludes.v2+xml; charset=utf-8')

        self.assertIsNone(post_req.params)

        self.maxDiff = None
        self.assertEqual(post_req.body.decode('utf-8'), CREATE_FUNCTION_GROUP_INCLUDE_ADT_XML)


class TestFunctionGroupIncludeWrite(unittest.TestCase):

    @patch('sap.adt.objects.ADTObject.lock', return_value=FAKE_LOCK_HANDLE)
    @patch('sap.adt.objects.ADTObject.unlock')
    def test_write(self, fake_lock, fake_unlock):
        connection = Connection()

        args = fugri_parse_args('write', 'ZFG_HELLO_WORLD', 'ZFG_I_HELLO_WORLD', '-')
        with patch('sys.stdin', StringIO(WRITE_FUNCTION_GROUP_INCLUDE_BODY)):
            args.execute(connection, args)

        fake_lock.assert_called_once()
        fake_unlock.assert_called_once()

        expected_request = Request(
            adt_uri='/sap/bc/adt/functions/groups/zfg_hello_world/includes/zfg_i_hello_world/source/main',
            method='PUT',
            headers={'Content-Type': 'text/plain; charset=utf-8', 'Accept': 'text/plain'},
            body=bytes(WRITE_FUNCTION_GROUP_INCLUDE_BODY, 'utf-8'),
            params={'lockHandle': FAKE_LOCK_HANDLE}
        )

        self.assertEqual(connection.execs[0], expected_request)


class TestFunctionGroupIncludeRead(unittest.TestCase):

    def test_read(self):
        connection = Connection([
            (
                Response(
                    text=READ_FUNCTION_GROUP_INCLUDE_BODY,
                    status_code=200,
                    headers={'Content-Type': 'text/plain; charset=utf-8'}
                ),
                Request.get(
                    adt_uri='functions/groups/zfg_hello_world/includes/zfg_i_hello_world/source/main',
                    accept='text/plain'
                )
            )
        ], asserter=self)

        args = fugri_parse_args('read', 'ZFG_HELLO_WORLD', 'ZFG_I_HELLO_WORLD')
        with patch('sys.stdin', StringIO(READ_FUNCTION_GROUP_INCLUDE_BODY)) as mock_print:
            args.execute(connection, args)

        expected_stdout = READ_FUNCTION_GROUP_INCLUDE_BODY
        self.assertEqual(mock_print.getvalue(), expected_stdout)


class TestFunctionGroupIncludeActivate(unittest.TestCase):

    def test_activate(self):
        connection = Connection([
            RESPONSE_ACTIVATION_OK,
            Response(text=FUNCTION_GROUP_INCLUDE_ADT_XML, status_code=200, headers={})
        ])

        args = fugri_parse_args('activate', 'ZFG_HELLO_WORLD', 'ZFG_I_HELLO_WORLD')
        args.execute(connection, args)

        expected_request = Request(
            adt_uri='/sap/bc/adt/activation',
            method='POST',
            headers={'Accept': 'application/xml', 'Content-Type': 'application/xml'},
            body=ACTIVATE_FUNCTION_GROUP_INCLUDE_BODY,
            params={'method': 'activate', 'preauditRequested': 'true'}
        )

        self.assertEqual(connection.execs[0], expected_request)
if __name__ == '__main__':
    unittest.main()
