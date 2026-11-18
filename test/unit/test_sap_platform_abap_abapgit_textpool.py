#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, call

import sap.adt.errors
import sap.platform.abap.abapgit.textpool as textpool
from sap.adt.textelements import TextSymbol
from sap.platform.abap.ddic import TPOOL

from sap.platform.abap.localrepository import RepositoryObserver

from mock import PatcherTestCase


class TextPoolTestCase(unittest.TestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def setUp(self):
        super().setUp()
        self.observer = Mock(spec=RepositoryObserver)

    def tearDown(self):
        try:
            self.unpatch_all()
        finally:
            super().tearDown()


class TestDownloadTextSymbols(TextPoolTestCase):

    def test_download(self):
        text_elements = Mock(text='@MaxLength:20\n001=Hello, world!\n\n@MaxLength:10\n002=a=b')

        symbols = textpool.download_text_symbols(self.observer, text_elements)

        self.assertEqual(symbols, [TextSymbol('001', 'Hello, world!', 20), TextSymbol('002', 'a=b', 10)])
        self.assertEqual(self.observer.mock_calls, [])

    def test_download_error(self):
        text_elements = Mock()
        type(text_elements).text = PropertyMock(side_effect=sap.adt.errors.ExceptionResourceNotFound('No texts'))

        symbols = textpool.download_text_symbols(self.observer, text_elements)

        self.assertEqual(symbols, [])
        self.assertEqual(self.observer.mock_calls, [call.warning('Download of text elements failed: No texts')])


class TestBuildTextPool(unittest.TestCase):

    def test_build(self):
        tpool = textpool.build_text_pool([TextSymbol('001', 'Hello', 20), TextSymbol('002', 'World', 10)])

        self.assertEqual(len(tpool), 2)
        self.assertEqual((tpool[0].ID, tpool[0].KEY, tpool[0].ENTRY, tpool[0].LENGTH), ('I', '001', 'Hello', 20))
        self.assertEqual((tpool[1].ID, tpool[1].KEY, tpool[1].ENTRY, tpool[1].LENGTH), ('I', '002', 'World', 10))

    def test_build_empty(self):
        self.assertEqual(len(textpool.build_text_pool([])), 0)


class TestTextSymbolsFromTPool(TextPoolTestCase):

    def setUp(self):
        super().setUp()

        self.tpool = TPOOL()
        self.tpool.append(ID='I', KEY='001', ENTRY='Hello', LENGTH='20')
        self.tpool.append(ID='R', ENTRY='Title', LENGTH='5')
        self.tpool.append(ID='S', KEY='P_PARAM', ENTRY='Parameter', LENGTH='17')

    def test_symbols_and_skipped_entries(self):
        symbols = textpool.text_symbols_from_tpool(self.observer, self.tpool, 'zprog')

        self.assertEqual(symbols, [TextSymbol('001', 'Hello', 20)])
        self.assertEqual(self.observer.mock_calls, [
            call.warning('Skipping unsupported text pool entry R of zprog'),
            call.warning('Skipping unsupported text pool entry S P_PARAM of zprog'),
        ])

    def test_symbol_without_entry(self):
        tpool = TPOOL()
        tpool.append(ID='I', KEY='002', LENGTH='10')

        symbols = textpool.text_symbols_from_tpool(self.observer, tpool, 'zprog')

        self.assertEqual(symbols, [TextSymbol('002', '', 10)])
        self.assertEqual(self.observer.mock_calls, [])

    def test_known_ids_are_not_reported(self):
        symbols = textpool.text_symbols_from_tpool(self.observer, self.tpool, 'zprog', known_ids=('R',))

        self.assertEqual(symbols, [TextSymbol('001', 'Hello', 20)])
        self.assertEqual(self.observer.mock_calls, [
            call.warning('Skipping unsupported text pool entry S P_PARAM of zprog'),
        ])

    def test_no_supported_ids(self):
        symbols = textpool.text_symbols_from_tpool(self.observer, self.tpool, 'zincl', known_ids=('R', 'S'), supported_ids=())

        self.assertEqual(symbols, [])
        self.assertEqual(self.observer.mock_calls, [
            call.warning('Skipping unsupported text pool entry I 001 of zincl'),
        ])


class TestWriteTextSymbols(unittest.TestCase):

    def test_write(self):
        editor = MagicMock()
        editor.__enter__.return_value = editor
        text_elements = Mock()
        text_elements.open_editor.return_value = editor

        textpool.write_text_symbols(text_elements, [TextSymbol('001', 'Hello, world!', 20)], 'K900001')

        text_elements.open_editor.assert_called_once_with(corrnr='K900001')
        editor.write.assert_called_once_with('@MaxLength:20\r\n001=Hello, world!\r\n')


if __name__ == '__main__':
    unittest.main()
