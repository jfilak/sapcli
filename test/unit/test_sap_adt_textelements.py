#!/usr/bin/env python3

import unittest

import sap.errors
import sap.adt.errors
from sap.adt.textelements import (TextSymbol, parse_symbols, serialize_symbols, ClassTextElements,
                                  ProgramTextElements)

from mock import Connection, Response

from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK
from fixtures_sap_adt_textelements import (SYMBOLS_SINGLE, SYMBOLS_BLANK_LINES, SYMBOLS_SERIALIZED,
                                           GET_CLASS_TEXT_ELEMENTS_XML, ERROR_XML_TEXT_ELEMENTS_NOT_FOUND,
                                           ERROR_XML_TEXT_ELEMENTS_FETCH_NOT_FOUND,
                                           ERROR_XML_TEXT_ELEMENTS_SAVE_WITHOUT_PACKAGE,
                                           ERROR_XML_TEXT_ELEMENTS_SAVE_FAILURE, GET_PROGRAM_TEXT_ELEMENTS_XML,
                                           ERROR_XML_PROGRAM_TEXT_ELEMENTS_FETCH_NOT_FOUND)


SYMBOLS_MIME = 'application/vnd.sap.adt.textelements.symbols.v1'


class TestParseSymbols(unittest.TestCase):

    def test_parse_empty(self):
        self.assertEqual(parse_symbols(''), [])

    def test_parse_single(self):
        self.assertEqual(parse_symbols(SYMBOLS_SINGLE), [TextSymbol('001', 'Hello, world!', 20)])

    def test_parse_blank_lines(self):
        self.assertEqual(parse_symbols(SYMBOLS_BLANK_LINES),
                         [TextSymbol('003', 'Einblenden...', 13),
                          TextSymbol('005', 'Ausblenden', 18)])

    def test_parse_lf_only(self):
        self.assertEqual(parse_symbols('@MaxLength:20\n001=Hello\n'), [TextSymbol('001', 'Hello', 20)])

    def test_parse_text_with_equals(self):
        self.assertEqual(parse_symbols('@MaxLength:10\n002=a=b'), [TextSymbol('002', 'a=b', 10)])

    def test_parse_missing_max_length(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            parse_symbols('001=Hello')

        self.assertEqual(str(caught.exception), 'Text symbol without @MaxLength: 001=Hello')

    def test_parse_invalid_max_length(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            parse_symbols('@MaxLength:abc\n001=Hello')

        self.assertEqual(str(caught.exception), 'Invalid text symbol line: @MaxLength:abc')

    def test_parse_line_without_equals(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            parse_symbols('@MaxLength:20\nHello')

        self.assertEqual(str(caught.exception), 'Invalid text symbol line: Hello')


class TestSerializeSymbols(unittest.TestCase):

    def test_serialize_empty(self):
        self.assertEqual(serialize_symbols([]), '')

    def test_serialize_symbols(self):
        self.assertEqual(serialize_symbols([TextSymbol('001', 'Hello, world!', 20),
                                            TextSymbol('002', 'a=b', 10)]),
                         SYMBOLS_SERIALIZED)

    def test_round_trip(self):
        self.assertEqual(serialize_symbols(parse_symbols(SYMBOLS_SERIALIZED)), SYMBOLS_SERIALIZED)


class TestClassTextElements(unittest.TestCase):

    def test_str(self):
        texts = ClassTextElements(Connection(), 'ZCL_JAKUB_TEXTS')
        self.assertEqual(str(texts), 'CLAS/OCX ZCL_JAKUB_TEXTS')

    def test_uri(self):
        texts = ClassTextElements(Connection(), 'ZCL_JAKUB_TEXTS')
        self.assertEqual(texts.uri, 'textelements/classes/zcl_jakub_texts')
        self.assertEqual(texts.full_adt_uri, '/sap/bc/adt/textelements/classes/zcl_jakub_texts')

    def test_fetch(self):
        conn = Connection([Response(text=GET_CLASS_TEXT_ELEMENTS_XML, status_code=200, headers={})])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')
        texts.fetch()

        self.assertEqual(conn.execs[0].method, 'GET')
        self.assertEqual(conn.execs[0].adt_uri, '/sap/bc/adt/textelements/classes/zcl_jakub_texts')
        self.assertEqual(texts.active, 'inactive')
        self.assertEqual(texts.description, 'some texts')
        # pylint: disable=no-member
        self.assertEqual(texts.reference.name, '$TMP')

    def test_text(self):
        conn = Connection([Response(text=SYMBOLS_SINGLE, status_code=200, headers={})])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')

        self.assertEqual(texts.text, '@MaxLength:20\n001=Hello, world!')
        self.assertEqual(conn.execs[0].method, 'GET')
        self.assertEqual(conn.execs[0].adt_uri, '/sap/bc/adt/textelements/classes/zcl_jakub_texts/source/symbols')
        self.assertEqual(conn.execs[0].headers, {'Accept': SYMBOLS_MIME})

    def test_lock(self):
        conn = Connection([LOCK_RESPONSE_OK])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')

        self.assertEqual(texts.lock(), 'win')
        self.assertEqual(conn.execs[0].method, 'POST')
        self.assertEqual(conn.execs[0].adt_uri, '/sap/bc/adt/textelements/classes/zcl_jakub_texts')
        self.assertEqual(conn.execs[0].params, {'_action': 'LOCK', 'accessMode': 'MODIFY'})

    def test_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')
        with texts.open_editor() as editor:
            editor.write('@MaxLength:20\n001=Hello, world!\n\n@MaxLength:10\n002=a=b\n')

        self.assertEqual(len(conn.execs), 3)

        put_request = conn.execs[1]
        self.assertEqual(put_request.method, 'PUT')
        self.assertEqual(put_request.adt_uri, '/sap/bc/adt/textelements/classes/zcl_jakub_texts/source/symbols')
        self.assertEqual(put_request.headers, {'Content-Type': SYMBOLS_MIME, 'Accept': SYMBOLS_MIME})
        self.assertEqual(put_request.params, {'lockHandle': 'win'})
        self.assertEqual(put_request.body, bytes(SYMBOLS_SERIALIZED, 'utf-8'))

        unlock_request = conn.execs[2]
        self.assertEqual(unlock_request.method, 'POST')
        self.assertEqual(unlock_request.adt_uri, '/sap/bc/adt/textelements/classes/zcl_jakub_texts')
        self.assertEqual(unlock_request.params, {'_action': 'UNLOCK', 'lockHandle': 'win'})

    def test_write_with_corrnr(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')
        with texts.open_editor(corrnr='420') as editor:
            editor.write(SYMBOLS_SINGLE)

        self.assertEqual(conn.execs[1].params, {'lockHandle': 'win', 'corrNr': '420'})

    def test_write_empty(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')
        with texts.open_editor() as editor:
            editor.write('')

        self.assertEqual(conn.execs[1].body, b'')

    def test_write_invalid_does_not_send(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')
        with self.assertRaises(sap.errors.SAPCliError):
            with texts.open_editor() as editor:
                editor.write('Hello')

        self.assertEqual(len(conn.execs), 2)
        self.assertEqual(conn.execs[1].params['_action'], 'UNLOCK')



def error_response(status_code, xml):
    return Response(text=xml, status_code=status_code, headers={'content-type': 'application/xml'})


class TestClassTextElementsNotFound(unittest.TestCase):

    def test_text_class_not_found(self):
        conn = Connection([error_response(404, ERROR_XML_TEXT_ELEMENTS_NOT_FOUND)])

        texts = ClassTextElements(conn, 'ZCL_MISSING')
        with self.assertRaises(sap.adt.errors.ExceptionResourceNotFound) as caught:
            texts.text

        self.assertEqual(str(caught.exception), 'Cannot access text elements: class ZCL_MISSING does not exist')

    def test_fetch_class_not_found(self):
        conn = Connection([error_response(404, ERROR_XML_TEXT_ELEMENTS_FETCH_NOT_FOUND)])

        texts = ClassTextElements(conn, 'ZCL_MISSING')
        with self.assertRaises(sap.adt.errors.ExceptionResourceNotFound) as caught:
            texts.fetch()

        self.assertEqual(str(caught.exception), 'Cannot access text elements: class ZCL_MISSING does not exist')

    def test_write_class_not_found(self):
        conn = Connection([LOCK_RESPONSE_OK,
                           error_response(500, ERROR_XML_TEXT_ELEMENTS_SAVE_WITHOUT_PACKAGE),
                           error_response(404, ERROR_XML_TEXT_ELEMENTS_FETCH_NOT_FOUND),
                           EMPTY_RESPONSE_OK])

        texts = ClassTextElements(conn, 'ZCL_MISSING')
        with self.assertRaises(sap.adt.errors.ExceptionResourceNotFound) as caught:
            with texts.open_editor() as editor:
                editor.write(SYMBOLS_SINGLE)

        self.assertEqual(str(caught.exception), 'Cannot access text elements: class ZCL_MISSING does not exist')
        self.assertIsInstance(caught.exception.__cause__, sap.adt.errors.ExceptionResourceSaveFailure)
        self.assertEqual(conn.mock_methods(),
                         [('POST', '/sap/bc/adt/textelements/classes/zcl_missing'),
                          ('PUT', '/sap/bc/adt/textelements/classes/zcl_missing/source/symbols'),
                          ('GET', '/sap/bc/adt/textelements/classes/zcl_missing'),
                          ('POST', '/sap/bc/adt/textelements/classes/zcl_missing')])

    def test_write_other_save_failure(self):
        conn = Connection([LOCK_RESPONSE_OK,
                           error_response(500, ERROR_XML_TEXT_ELEMENTS_SAVE_FAILURE),
                           Response(text=GET_CLASS_TEXT_ELEMENTS_XML, status_code=200, headers={}),
                           EMPTY_RESPONSE_OK])

        texts = ClassTextElements(conn, 'ZCL_JAKUB_TEXTS')
        with self.assertRaises(sap.adt.errors.ExceptionResourceSaveFailure) as caught:
            with texts.open_editor() as editor:
                editor.write(SYMBOLS_SINGLE)

        self.assertEqual(caught.exception.message, 'Some other save failure')


class TestProgramTextElements(unittest.TestCase):

    def test_str(self):
        texts = ProgramTextElements(Connection(), 'ZPROG_HELLO_WORLD')
        self.assertEqual(str(texts), 'PROG/PX ZPROG_HELLO_WORLD')

    def test_uri(self):
        texts = ProgramTextElements(Connection(), 'ZPROG_HELLO_WORLD')
        self.assertEqual(texts.uri, 'textelements/programs/zprog_hello_world')
        self.assertEqual(texts.full_adt_uri, '/sap/bc/adt/textelements/programs/zprog_hello_world')

    def test_fetch(self):
        conn = Connection([Response(text=GET_PROGRAM_TEXT_ELEMENTS_XML, status_code=200, headers={})])

        texts = ProgramTextElements(conn, 'ZPROG_HELLO_WORLD')
        texts.fetch()

        self.assertEqual(conn.mock_methods(), [('GET', '/sap/bc/adt/textelements/programs/zprog_hello_world')])
        self.assertEqual(texts.active, 'active')
        self.assertEqual(texts.description, 'test')

    def test_text(self):
        conn = Connection([Response(text=SYMBOLS_SINGLE, status_code=200, headers={})])

        texts = ProgramTextElements(conn, 'ZPROG_HELLO_WORLD')

        self.assertEqual(texts.text, '@MaxLength:20\n001=Hello, world!')
        self.assertEqual(conn.mock_methods(),
                         [('GET', '/sap/bc/adt/textelements/programs/zprog_hello_world/source/symbols')])
        self.assertEqual(conn.execs[0].headers, {'Accept': SYMBOLS_MIME})

    def test_write(self):
        conn = Connection([LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK, EMPTY_RESPONSE_OK])

        texts = ProgramTextElements(conn, 'ZPROG_HELLO_WORLD')
        with texts.open_editor(corrnr='420') as editor:
            editor.write('@MaxLength:20\n001=Hello, world!\n\n@MaxLength:10\n002=a=b\n')

        self.assertEqual(conn.mock_methods(),
                         [('POST', '/sap/bc/adt/textelements/programs/zprog_hello_world'),
                          ('PUT', '/sap/bc/adt/textelements/programs/zprog_hello_world/source/symbols'),
                          ('POST', '/sap/bc/adt/textelements/programs/zprog_hello_world')])

        put_request = conn.execs[1]
        self.assertEqual(put_request.headers, {'Content-Type': SYMBOLS_MIME, 'Accept': SYMBOLS_MIME})
        self.assertEqual(put_request.params, {'lockHandle': 'win', 'corrNr': '420'})
        self.assertEqual(put_request.body, bytes(SYMBOLS_SERIALIZED, 'utf-8'))

    def test_text_program_not_found(self):
        conn = Connection([error_response(404, ERROR_XML_TEXT_ELEMENTS_NOT_FOUND)])

        texts = ProgramTextElements(conn, 'ZPROG_MISSING')
        with self.assertRaises(sap.adt.errors.ExceptionResourceNotFound) as caught:
            texts.text

        self.assertEqual(str(caught.exception), 'Cannot access text elements: program ZPROG_MISSING does not exist')

    def test_fetch_program_not_found(self):
        conn = Connection([error_response(404, ERROR_XML_PROGRAM_TEXT_ELEMENTS_FETCH_NOT_FOUND)])

        texts = ProgramTextElements(conn, 'ZPROG_MISSING')
        with self.assertRaises(sap.adt.errors.ExceptionResourceNotFound) as caught:
            texts.fetch()

        self.assertEqual(str(caught.exception), 'Cannot access text elements: program ZPROG_MISSING does not exist')


if __name__ == '__main__':
    unittest.main()
