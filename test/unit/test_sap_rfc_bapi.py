#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

from sap.rfc.bapi import BAPIError


def create_bapiret(typ:str=None, message:str=None, msg_class:str=None, msg_number:str=None):
    return {'TYPE': typ, 'ID': msg_class, 'NUMBER': msg_number, 'MESSAGE': message}


def create_bapiret_error(message:str):
    return create_bapiret(typ='E', message=message, msg_class='ERR', msg_number='333')


def create_bapiret_warning(message:str):
    return create_bapiret(typ='W', message=message, msg_class='WRN', msg_number='777')


class TestBAPIError(unittest.TestCase):

    def setUp(self):
        self.message_e = 'Error message'
        self.message_w = 'Warning message'

        self.bapirettab = [create_bapiret_error(self.message_e), create_bapiret_warning(self.message_w)]
        self.response = Mock()

    def assertExDataMatch(self, ex):
        self.assertEqual(str(ex), '''E/ERR/333: Error message
W/WRN/777: Warning message''')

        self.assertEqual(ex.bapirettab, self.bapirettab)
        self.assertEqual(ex.response, self.response)

    def test_ctor_join_list(self):
        ex = BAPIError(self.bapirettab, self.response)
        self.assertExDataMatch(ex)

    def test_raises_for_error(self):
        with self.assertRaises(BAPIError) as caught:
            BAPIError.raise_for_error(self.bapirettab, self.response)

        self.assertExDataMatch(caught.exception)

    def test_raises_for_error_with_instance(self):
        with self.assertRaises(BAPIError) as caught:
            BAPIError.raise_for_error(self.bapirettab[0], self.response)

        self.assertEqual(caught.exception.bapirettab, self.bapirettab[0:1])

    def test_does_not_raise(self):
        BAPIError.raise_for_error([create_bapiret_warning(self.message_w)], self.response)

    def test_contains(self):
        ex = BAPIError(self.bapirettab, self.response)
        self.assertTrue(ex.contains('ERR', '333'))
        self.assertFalse(ex.contains('NOP', '222'))
