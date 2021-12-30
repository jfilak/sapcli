#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, Mock

import sap.errors
import sap.rfc.core

class TestRFCCore(unittest.TestCase):

    def tearDown(self):
        sap.rfc.core._unimport_pyrfc()

    def test_rfc_is_available_no(self):
        with patch('importlib.__import__') as fake_import:
            fake_import.side_effect = ImportError('mock error')

            self.assertFalse(sap.rfc.core.rfc_is_available())

    def test_rfc_is_available_yes(self):
        fake_pyrfc = MagicMock()

        with patch.dict('sys.modules', pyrfc=fake_pyrfc):
            self.assertTrue(sap.rfc.core.rfc_is_available())

        # Make sure it does not try to import it again
        with patch('importlib.__import__') as fake_import:
            fake_import.side_effect = ImportError('mock error')

            self.assertTrue(sap.rfc.core.rfc_is_available())

    def test_connect_non_available(self):
        with self.assertRaises(sap.errors.SAPCliError) as caught:
            with patch('importlib.__import__') as fake_import:
                fake_import.side_effect = ImportError('mock error')

                sap.rfc.core.connect(ashost='ashost',
                                     sysnr='00',
                                     client='100',
                                     user='anzeiger',
                                     password='display')

        self.assertEqual(str(caught.exception),
                         'RFC functionality is not available(enabled)')

    def test_connect_available(self):
        fake_pyrfc = MagicMock()

        with patch.dict('sys.modules', pyrfc=fake_pyrfc):
            conn = sap.rfc.core.connect(ashost='ashost',
                                        sysnr='00',
                                        client='100',
                                        user='anzeiger',
                                        passwd='display')

        self.assertIsNotNone(conn)
        self.assertEqual(conn, fake_pyrfc.Connection.return_value)
        fake_pyrfc.Connection.assert_called_once_with(ashost='ashost',
                                                      sysnr='00',
                                                      client='100',
                                                      user='anzeiger',
                                                      passwd='display')
