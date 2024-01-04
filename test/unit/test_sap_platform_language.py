#!/usr/bin/env python3

import unittest
from unittest.mock import patch

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


class TestSAPPlatformLanguageLocale(unittest.TestCase):

    def test_locale_lang_to_sap_code_ok(self):
        with patch('sap.platform.language.getlocale', return_value=('en_US', 'UTF-8')):
            sap_lang = sap.platform.language.locale_lang_sap_code()

            self.assertEqual(sap_lang, 'E')

    def test_locale_lang_to_sap_code_C(self):
        """This is a special case for a short case because C is kinda special
           as it is the POSIX portable locale and we may want to handle it
           differently in feature.
        """

        with patch('sap.platform.language.getlocale', return_value=('C', 'UTF-8')):
            with self.assertRaises(sap.errors.SAPCliError) as caught:
                sap_lang = sap.platform.language.locale_lang_sap_code()

        self.assertEqual(str(caught.exception), 'The current system locale language is not ISO 3166: C')

    def test_locale_lang_to_sap_code_short(self):
        with patch('sap.platform.language.getlocale', return_value=('e', 'UTF-8')):
            with self.assertRaises(sap.errors.SAPCliError) as caught:
                sap_lang = sap.platform.language.locale_lang_sap_code()

        self.assertEqual(str(caught.exception), 'The current system locale language is not ISO 3166: e')

    def test_locale_lang_to_sap_code_unknown(self):
        with patch('sap.platform.language.getlocale', return_value=('WF', 'UTF-8')):
            with self.assertRaises(sap.errors.SAPCliError) as caught:
                sap_lang = sap.platform.language.locale_lang_sap_code()

        self.assertEqual(str(caught.exception), 'The current system locale language cannot be converted to SAP language code: WF')


if __name__ == '__main__':
    unittest.main()
