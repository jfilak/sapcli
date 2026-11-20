#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

import sap
from sap.adt.checkin import check_package, create_in_package
from sap.adt.errors import ExceptionCheckinFailure, ExceptionResourceAlreadyExists, ExceptionResourceCreationFailure


class TestCheckPackage(unittest.TestCase):

    def setUp(self):
        self.adt_object = Mock()
        self.adt_object.name = 'ZIF_UTIL'
        self.adt_object.reference.name = 'ZPROD'

    def test_same_package(self):
        check_package(self.adt_object, 'ZPROD', 'interface')

        self.adt_object.fetch.assert_called_once_with()

    def test_same_package_other_case(self):
        check_package(self.adt_object, 'zprod', 'interface')

        self.adt_object.fetch.assert_called_once_with()

    def test_other_package(self):
        with self.assertRaises(ExceptionCheckinFailure) as caught:
            check_package(self.adt_object, '$ZFOO', 'interface')

        self.assertEqual(str(caught.exception),
                         'Cannot checkin interface ZIF_UTIL into package $ZFOO. It already exists in package ZPROD.')


class TestCreateInPackage(unittest.TestCase):

    def setUp(self):
        self.adt_object = Mock()
        self.adt_object.name = 'ZIF_UTIL'
        self.adt_object.reference.name = 'ZPROD'

    def test_created(self):
        created = create_in_package(self.adt_object, '420', 'ZPROD', 'interface')

        self.assertTrue(created)
        self.adt_object.create.assert_called_once_with('420')
        self.adt_object.fetch.assert_not_called()

    def test_exists_in_package(self):
        self.adt_object.create.side_effect = ExceptionResourceAlreadyExists('Interface ZIF_UTIL already exists')

        with self.assertLogs(sap.get_logger(), 'INFO') as logs:
            created = create_in_package(self.adt_object, '420', 'ZPROD', 'interface')

        self.assertFalse(created)
        self.adt_object.create.assert_called_once_with('420')
        self.adt_object.fetch.assert_called_once_with()
        self.assertEqual([record.getMessage() for record in logs.records], ['Interface ZIF_UTIL already exists'])

    def test_exists_in_other_package(self):
        already_exists = ExceptionResourceAlreadyExists('Interface ZIF_UTIL already exists')
        self.adt_object.create.side_effect = already_exists

        with self.assertRaises(ExceptionCheckinFailure) as caught:
            create_in_package(self.adt_object, None, '$ZFOO', 'interface')

        self.assertEqual(str(caught.exception),
                         'Cannot checkin interface ZIF_UTIL into package $ZFOO. It already exists in package ZPROD.')
        self.assertIs(caught.exception.__context__, already_exists)

    def test_creation_error(self):
        self.adt_object.create.side_effect = ExceptionResourceCreationFailure('No authorization')

        with self.assertRaises(ExceptionResourceCreationFailure):
            create_in_package(self.adt_object, None, 'ZPROD', 'interface')

        self.adt_object.fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
