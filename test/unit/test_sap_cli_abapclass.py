#!/bin/python

from argparse import ArgumentParser
import unittest
from unittest.mock import patch, mock_open, call
from io import StringIO

import sap.cli.abapclass

from mock import ConnectionViaHTTP as Connection, Response
from fixtures_adt import (EMPTY_RESPONSE_OK, LOCK_RESPONSE_OK, TEST_CLASSES_READ_RESPONSE_OK,
                          DEFINITIONS_READ_RESPONSE_OK, IMPLEMENTATIONS_READ_RESPONSE_OK)
from fixtures_adt_clas import GET_CLASS_ADT_XML


FIXTURE_ELEMENTARY_CLASS_XML="""<?xml version="1.0" encoding="UTF-8"?>
<class:abapClass xmlns:class="http://www.sap.com/adt/oo/classes" xmlns:adtcore="http://www.sap.com/adt/core" adtcore:type="CLAS/OC" adtcore:description="Class Description" adtcore:language="EN" adtcore:name="ZCL_HELLO_WORLD" adtcore:masterLanguage="EN" adtcore:responsible="ANZEIGER" class:final="true" class:visibility="public">
<adtcore:packageRef adtcore:name="$THE_PACKAGE"/>
<class:include adtcore:name="CLAS/OC" adtcore:type="CLAS/OC" class:includeType="testclasses"/>
<class:superClassRef/>
</class:abapClass>"""

parser = ArgumentParser()
sap.cli.abapclass.CommandGroup().install_parser(parser)

def parse_args(argv):
    return parser.parse_args(argv)

class TestClassCreate(unittest.TestCase):

    def test_class_create_defaults(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        args = parse_args(['create', 'ZCL_HELLO_WORLD', 'Class Description', '$THE_PACKAGE'])
        args.execute(connection, args)

        self.assertEqual([(e.method, e.adt_uri) for e in connection.execs], [('POST', '/sap/bc/adt/oo/classes')])

        create_request = connection.execs[0]
        self.maxDiff = None
        self.assertEqual(create_request.body.decode('utf-8'), FIXTURE_ELEMENTARY_CLASS_XML)

        self.assertIsNone(create_request.params)

        self.assertEqual(sorted(create_request.headers.keys()), ['Content-Type'])
        self.assertEqual(create_request.headers['Content-Type'], 'application/vnd.sap.adt.oo.classes.v2+xml; charset=utf-8')


    def test_create_program_with_corrnr(self):
        connection = Connection([EMPTY_RESPONSE_OK])

        args = parse_args(['create', 'ZCL_HELLO_WORLD', 'Class description', 'Package', '--corrnr', '420'])
        args.execute(connection, args)

        self.assertEqual(connection.execs[0].params['corrNr'], '420')

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
        self.assertEqual(conn.execs[1][3], b'class stdin definition')

    def test_class_read_from_file(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args(['write', 'ZCL_WRITER', 'zcl_class.abap'])

        with patch('sap.cli.object.open', mock_open(read_data='class file definition')) as m:
            args.execute(conn, args)

        m.assert_called_once_with('zcl_class.abap', 'r', encoding='utf8')

        self.assertEqual(len(conn.execs), 3)

        self.maxDiff = None
        self.assertEqual(conn.execs[1][3], b'class file definition')

    def test_class_read_from_file_with_name(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args(['write', '-', 'zcl_class.clas.abap'])

        with patch('sap.cli.object.open', mock_open(read_data='class file definition')) as m:
            args.execute(conn, args)

        m.assert_called_once_with('zcl_class.clas.abap', 'r', encoding='utf8')

        self.assertEqual(len(conn.execs), 3)
        self.assertEqual(conn.execs[1].adt_uri, '/sap/bc/adt/oo/classes/zcl_class/source/main')

    def test_class_unsupported_file_extension(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args(['write', '-', 'zreport.prog.abap'])

        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as caught:
            args.execute(conn, args)

        self.assertEqual(str(caught.exception), 'Unknown class file name suffix: "prog.abap"')

    def test_class_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])
        args = parse_args(['write', 'ZCL_WRITER', 'zcl_class.abap', '--corrnr', '420'])

        with patch('sap.cli.object.open', mock_open(read_data='class file definition')) as m:
            args.execute(conn, args)

        self.assertEqual(conn.execs[1].params['corrNr'], '420')


class TestClassIncludes(unittest.TestCase):

    def read_test(self, response, typ):
        conn = Connection([response])
        args = parse_args(['read', 'ZCL_READER', '--type', typ])

        with patch('sap.cli.object.print') as mock_print:
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 1)

        self.maxDiff = None
        self.assertEqual(conn.execs[0].adt_uri, f'/sap/bc/adt/oo/classes/zcl_reader/includes/{typ}')
        self.assertEqual(mock_print.call_args_list, [call(response.text)])

    def test_class_read_definitions(self):
        self.read_test(DEFINITIONS_READ_RESPONSE_OK, 'definitions')

    def test_class_read_implementations(self):
        self.read_test(IMPLEMENTATIONS_READ_RESPONSE_OK, 'implementations')

    def test_class_read_tests(self):
        self.read_test(TEST_CLASSES_READ_RESPONSE_OK, 'testclasses')

    def write_test(self, typ):
        args = parse_args(['write', 'ZCL_WRITER', '--type', typ, '-'])

        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        with patch('sys.stdin', StringIO('* new content')):
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 3)

        self.assertEqual(conn.execs[1].adt_uri, f'/sap/bc/adt/oo/classes/zcl_writer/includes/{typ}')

    def test_class_write_definitions(self):
        self.write_test('definitions')

    def test_class_write_implementations(self):
        self.write_test('implementations')

    def test_class_write_tests(self):
        self.write_test('testclasses')

    def write_test_file_name(self, typ):
        exts = {
            'definitions': 'locals_def',
            'testclasses': 'testclasses',
            'implementations': 'locals_imp' }


        args = parse_args(['write', '-', f'zcl_writer.clas.{exts[typ]}.abap'])

        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        with patch('sap.cli.object.open', mock_open(read_data='* new content')):
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 3)

        self.assertEqual(conn.execs[1].adt_uri, f'/sap/bc/adt/oo/classes/zcl_writer/includes/{typ}')

    def test_class_write_definitions_file_name(self):
        self.write_test_file_name('definitions')

    def test_class_write_implementations_file_name(self):
        self.write_test_file_name('implementations')

    def test_class_write_tests_file_name(self):
        self.write_test_file_name('testclasses')

    def write_test_with_activation(self, typ):
        args = parse_args(['write', 'ZCL_WRITER', '--type', typ, '-', '--activate'])

        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        with patch('sys.stdin', StringIO('* new content')):
            args.execute(conn, args)

        self.assertEqual(conn.mock_methods(),
                         [('POST', f'/sap/bc/adt/oo/classes/zcl_writer'),
                          ('PUT', f'/sap/bc/adt/oo/classes/zcl_writer/includes/{typ}'),
                          ('POST', f'/sap/bc/adt/oo/classes/zcl_writer'),
                          ('POST', f'/sap/bc/adt/activation')])

        activate_request = conn.execs[3]
        self.assertIn('adtcore:uri="/sap/bc/adt/oo/classes/zcl_writer"', activate_request.body)
        self.assertIn('adtcore:name="ZCL_WRITER"', activate_request.body)

    def test_class_write_definitions_activate(self):
        self.write_test_with_activation('definitions')

    def test_class_write_implementations_activate(self):
        self.write_test_with_activation('implementations')

    def test_class_write_tests_activate(self):
        self.write_test_with_activation('testclasses')


class TestClassAttributes(unittest.TestCase):

    def test_class_attrs_output(self):
        conn = Connection([Response(status_code=200, headers={}, text=GET_CLASS_ADT_XML)])

        args = parse_args(['attributes', 'ZCL_HELLO_WORLD'])
        with patch('sap.cli.abapclass.print', newcallable=StringIO) as fake_print:
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 1)
        self.assertEqual(fake_print.mock_calls, [call('Name       : ZCL_HELLO_WORLD'),
                                                 call('Description: You cannot stop me!'),
                                                 call('Responsible: DEVELOPER'),
                                                 call('Package    : $IAMTHEKING')])


class TestClassExecute(unittest.TestCase):

    def test_class_execute_output(self):
        expected = 'Output from executed class'
        conn = Connection([Response(text=expected, status_code=200, headers={'Content-Type': 'text/plain'})])

        args = parse_args(['execute', 'ZCL_HELLO_WORLD'])
        with patch('sap.cli.abapclass.print', newcallable=StringIO) as fake_print:
            args.execute(conn, args)

        self.assertEqual(len(conn.execs), 1)
        self.assertEqual(fake_print.mock_calls, [call(expected)])


if __name__ == '__main__':
    unittest.main()
