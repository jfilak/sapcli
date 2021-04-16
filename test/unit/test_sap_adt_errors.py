#!/usr/bin/env python3

import unittest

import sap.adt.errors

from fixtures_adt import (
    ERROR_XML_PACKAGE_ALREADY_EXISTS,
    ERROR_XML_PROGRAM_ALREADY_EXISTS,
    ERROR_XML_MADEUP_PROBLEM
)

from fixtures_adt_package import GET_PACKAGE_ADT_XML_NOT_FOUND


class TestADTError(unittest.TestCase):

    def test_returns_none_for_invalid_data(self):
        error = sap.adt.errors.new_adt_error_from_xml('whatever')
        self.assertIsNone(error)

    def test_parse_existing_package(self):
        error = sap.adt.errors.new_adt_error_from_xml(ERROR_XML_PACKAGE_ALREADY_EXISTS)

        self.assertEqual(error.namespace, 'com.sap.adt')
        self.assertEqual(error.type, 'ExceptionResourceAlreadyExists')
        self.assertEqual(error.message, 'Resource Package $SAPCLI_TEST_ROOT does already exist.')

        self.assertEqual(str(error), error.message)
        self.assertEqual(repr(error), 'com.sap.adt.ExceptionResourceAlreadyExists')
        self.assertIsInstance(error, sap.adt.errors.ExceptionResourceAlreadyExists)

    def test_parse_existing_program(self):
        error = sap.adt.errors.new_adt_error_from_xml(ERROR_XML_PROGRAM_ALREADY_EXISTS)

        self.assertEqual(error.namespace, 'com.sap.adt')
        self.assertEqual(error.type, 'ExceptionResourceCreationFailure')
        self.assertEqual(error.message, 'A program or include already exists with the name SAPCLI_TEST_REPORT.')

        self.assertEqual(str(error), error.message)
        self.assertEqual(repr(error), 'com.sap.adt.ExceptionResourceCreationFailure')
        self.assertIsInstance(error, sap.adt.errors.ExceptionResourceCreationFailure)


    def test_parse_not_found_package(self):
        error = sap.adt.errors.new_adt_error_from_xml(GET_PACKAGE_ADT_XML_NOT_FOUND)

        self.assertEqual(error.namespace, 'com.sap.adt')
        self.assertEqual(error.type, 'ExceptionResourceNotFound')
        self.assertEqual(error.message, 'Error while importing object PKG_NAME from the database.')

        self.assertEqual(str(error), error.message)
        self.assertEqual(repr(error), 'com.sap.adt.ExceptionResourceNotFound')
        self.assertIsInstance(error, sap.adt.errors.ExceptionResourceNotFound)

    def test_parse_arbitrary_error(self):
        error = sap.adt.errors.new_adt_error_from_xml(ERROR_XML_MADEUP_PROBLEM)

        self.assertEqual(error.namespace, 'org.example.whatever')
        self.assertEqual(error.type, 'UnitTestSAPCLI')
        self.assertEqual(error.message, 'Made up problem.')

        self.assertEqual(str(error), 'UnitTestSAPCLI: Made up problem.')
        self.assertEqual(repr(error), 'org.example.whatever.UnitTestSAPCLI')
        self.assertIsInstance(error, sap.adt.errors.ADTError)


if __name__ == '__main__':
    unittest.main()
