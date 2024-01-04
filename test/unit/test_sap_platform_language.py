#!/usr/bin/env python3

import unittest

import sap.errors
import sap.platform.language


class TestSAPPlatformLanguageCodes(unittest.TestCase):

    def test_sap_code_to_iso_code_ok(self):
        self.assertEqual(sap.platform.language.sap_code_to_iso_code('E'), 'EN')

    def test_sap_code_to_iso_code_not_found(self):
        with self.assertRaises(sap.errors.SAPCliError) as raised:
            sap.platform.language.sap_code_to_iso_code('#')

        self.assertEqual(str(raised.exception), 'Not found SAP Language Code: #')

    def test_iso_code_to_sap_code_ok(self):
        self.assertEqual(sap.platform.language.iso_code_to_sap_code('EN'), 'E')

    def test_iso_code_to_sap_code_lower_ok(self):
        self.assertEqual(sap.platform.language.iso_code_to_sap_code('en'), 'E')

    def test_iso_code_to_sap_code_not_found(self):
        with self.assertRaises(sap.errors.SAPCliError) as raised:
            sap.platform.language.iso_code_to_sap_code('#')

        self.assertEqual(str(raised.exception), 'Not found ISO Code: #')


if __name__ == '__main__':
    unittest.main()
