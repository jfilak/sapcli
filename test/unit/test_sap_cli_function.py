#!/usr/bin/env python3

from argparse import ArgumentParser
import unittest
from unittest.mock import call, patch, Mock, PropertyMock
from io import StringIO

import sap.cli.function

from mock import Connection, Response
from fixtures_adt import EMPTY_RESPONSE_OK, LOCK_RESPONSE_OK
from fixtures_adt_function import (
        CREATE_FUNCTION_GROUP_ADT_XML,
        CREATE_FUNCTION_MODULE_ADT_XML,
        GET_FUNCTION_MODULE_ADT_XML,
        PUT_FUNCITON_MODULE_ADT_XML)


fugr_parser = ArgumentParser()
sap.cli.function.CommandGroupFunctionGroup().install_parser(fugr_parser)

fm_parser = ArgumentParser()
sap.cli.function.CommandGroupFunctionModule().install_parser(fm_parser)


def fugr_parse_args(*argv):
    global fugr_parser
    return fugr_parser.parse_args(argv)


def fm_parse_args(*argv):
    global fm_parser
    return fm_parser.parse_args(argv)


class TestFunctionGroupCreate(unittest.TestCase):

    def test_create_fugr_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK], user='FILAK')

        args = fugr_parse_args('create', 'ZFG_HELLO_WORLD', 'Hello FUGR!', '$TEST')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/functions/groups')])

        post_req = connection.execs[0]

        self.assertEqual(sorted(post_req.headers.keys()), ['Content-Type'])
        self.assertEqual(post_req.headers['Content-Type'], 'application/vnd.sap.adt.functions.groups.v2+xml')

        self.assertIsNone(post_req.params)

        self.maxDiff = None
        self.assertEqual(post_req.body, CREATE_FUNCTION_GROUP_ADT_XML)


class TestFunctionModuleCreate(unittest.TestCase):

    def test_create_func_mod_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = fm_parse_args('create', 'ZFG_HELLO_WORLD', 'Z_FN_HELLO_WORLD', 'Hello Function!')
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/functions/groups/zfg_hello_world/fmodules')])

        post_req = connection.execs[0]

        self.assertEqual(sorted(post_req.headers.keys()), ['Content-Type'])
        self.assertEqual(post_req.headers['Content-Type'], 'application/vnd.sap.adt.functions.fmodules.v2+xml')

        self.assertIsNone(post_req.params)

        self.maxDiff = None
        self.assertEqual(post_req.body, CREATE_FUNCTION_MODULE_ADT_XML)


class TestFunctionModuleChattr(unittest.TestCase):

    def test_fmod_chattr_rfc(self):
        connection = Connection([Response(text=GET_FUNCTION_MODULE_ADT_XML,
                                          status_code=200,
                                          headers={'Content-Type': 'application/vnd.sap.adt.functions.fmodules.v2+xml; charset=utf-8'}),
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
        self.assertEqual(put_req.headers['Content-Type'], 'application/vnd.sap.adt.functions.fmodules.v2+xml')

        self.assertEqual(sorted(put_req.params.keys()), ['lockHandle'])
        self.assertEqual(put_req.params['lockHandle'], 'win')

        self.maxDiff = None
        self.assertEqual(put_req.body, PUT_FUNCITON_MODULE_ADT_XML)


if __name__ == '__main__':
    unittest.main()
