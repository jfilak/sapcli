#!/bin/python

from argparse import ArgumentParser
import unittest
from unittest.mock import patch, mock_open
from io import StringIO

import sap.cli.abapclass

from mock import Connection
from fixtures_adt import EMPTY_RESPONSE_OK, LOCK_RESPONSE_OK


FIXTURE_ELEMENTARY_CLASS_XML="""<?xml version="1.0" encoding="UTF-8"?>
<class:abapClass xmlns:class="http://www.sap.com/adt/oo/classes" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="CLAS/OC" adtcore:description="Class Description" adtcore:language="EN" adtcore:name="ZCL_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER" class:final="true" class:visibility="public">
<adtcore:packageRef adtcore:name="$THE_PACKAGE"/>
<class:include adtcore:name="CLAS/OC" adtcore:type="CLAS/OC" class:includeType="testclasses"/>
<class:superClassRef/>
</class:abapClass>"""


def parse_args(argv):
    parser = ArgumentParser()
    sap.cli.abapclass.CommandGroup().install_parser(parser)
    return parser.parse_args(argv)


class TestCommandGroup(unittest.TestCase):

    def test_constructor(self):
        sap.cli.abapclass.CommandGroup()


class TestClassCreate(unittest.TestCase):

    def test_class_create_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        args = parse_args(['create', 'ZCL_HELLO_WORLD', 'Class Description', '$THE_PACKAGE'])
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/oo/classes')])

        create_request = connection.execs[0]
        self.assertEqual(create_request.body, FIXTURE_ELEMENTARY_CLASS_XML)

        self.assertIsNone(create_request.params)

        self.assertEqual(sorted(create_request.headers.keys()), ['Content-Type'])
        self.assertEqual(create_request.headers['Content-Type'], 'application/vnd.sap.adt.oo.classes.v2+xml')


class TestClassActivate(unittest.TestCase):

    def test_class_activate_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        args = parse_args(['activate', 'ZCL_ACTIVATOR'])
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/activation')])

        create_request = connection.execs[0]
        self.assertIn('adtcore:uri="/sap/bc/adt/oo/classes/zcl_activator"', create_request.body)
        self.assertIn('adtcore:name="ZCL_ACTIVATOR"', create_request.body)


class TestClassWrite(unittest.TestCase):

    def test_class_read_from_stdin(self):
        args = parse_args(['write', 'ZCL_WRITER', '-'])

        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        with patch('sys.stdin', StringIO('class stdin definition')):
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], 'class stdin definition')

    def test_class_read_from_file(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args(['write', 'ZCL_WRITER', 'zcl_class.abap'])

        with patch('sap.cli.abapclass.open', mock_open(read_data='class file definition')) as m:
            args.execute(conn, args)

        m.assert_called_once_with('zcl_class.abap')

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], 'class file definition')


if __name__ == '__main__':
    unittest.main()
