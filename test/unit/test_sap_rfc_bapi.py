#!/usr/bin/env python3

import unittest
from unittest.mock import Mock

from sap.rfc.bapi import (
    bapi_message_to_str,
    BAPIReturn,
    BAPIError
)


def create_bapiret(typ:str=None, message:str=None, msg_class:str=None, msg_number:str=None):
    return {'TYPE': typ, 'ID': msg_class, 'NUMBER': msg_number, 'MESSAGE': message}


def create_bapiret_error(message:str):
    return create_bapiret(typ='E', message=message, msg_class='ERR', msg_number='333')


def create_bapiret_warning(message:str):
    return create_bapiret(typ='W', message=message, msg_class='WRN', msg_number='777')


class TestMesageToStr(unittest.TestCase):

    def getBAPIMessage(self, **kwargs):
        bapiret = {
            'ID': '',
            'TYPE': '',
            'NUMBER': '',
            'MESSAGE': 'message',
        }
        bapiret.update(kwargs)
        return bapi_message_to_str(bapiret)

    def test_short_error(self):
        self.assertEqual('Error: message', self.getBAPIMessage(TYPE='E'))

    def test_short_warning(self):
        self.assertEqual('Warning: message', self.getBAPIMessage(TYPE='W'))

    def test_short_info(self):
        self.assertEqual('Info: message', self.getBAPIMessage(TYPE='I'))

    def test_short_success(self):
        self.assertEqual('Success: message', self.getBAPIMessage(TYPE='S'))

    def test_short_abort(self):
        self.assertEqual('Abort: message', self.getBAPIMessage(TYPE='A'))

    def test_wh_id_and_wh_no(self):
        self.assertEqual('Success(SCS|737): message', self.getBAPIMessage(TYPE='S', ID='SCS', NUMBER='737'))

    def test_wo_id_and_wh_no(self):
        self.assertEqual('Success(|737): message', self.getBAPIMessage(TYPE='S', ID='', NUMBER='737'))

    def test_wh_id_and_wo_no(self):
        self.assertEqual('Success(SCS|): message', self.getBAPIMessage(TYPE='S', ID='SCS', NUMBER=''))

    def test_wh_id_and_wh_no_000(self):
        self.assertEqual('Success(SCS|000): message', self.getBAPIMessage(TYPE='S', ID='SCS', NUMBER='000'))

    def test_wo_id_and_wh_no_000(self):
        self.assertEqual('Success: message', self.getBAPIMessage(TYPE='S', ID='', NUMBER='000'))


class TestBAPIReturn(unittest.TestCase):

    def setUp(self):
        self.message_e = 'Error message'
        self.message_w = 'Warning message'

        self.bapirettab = [create_bapiret_error(self.message_e), create_bapiret_warning(self.message_w)]
        self.response = Mock()

    def test_ctor_value_error(self):
        with self.assertRaises(ValueError) as caught:
            BAPIReturn("wrong type")

        self.assertEqual(str(caught.exception), "Neither dict nor list BAPI return type: str")

    def test_is_empty(self):
        self.assertTrue(BAPIReturn([]).is_empty)

    def test_not_is_empty(self):
        self.assertFalse(BAPIReturn(self.bapirettab).is_empty)

    def test_is_error_no_error(self):
        self.assertFalse(BAPIReturn(self.bapirettab[1]).is_error)

    def test_is_error_with_error(self):
        self.assertTrue(BAPIReturn(self.bapirettab).is_error)

    def test_error_message_no_error(self):
        self.assertIsNone(BAPIReturn(self.bapirettab[1]).error_message)

    def test_error_message_with_error(self):
        self.assertEqual(BAPIReturn(self.bapirettab).error_message, 'Error(ERR|333): Error message')


class TestBAPIError(unittest.TestCase):

    def setUp(self):
        self.message_e = 'Error message'
        self.message_w = 'Warning message'

        self.bapirettab = [create_bapiret_error(self.message_e), create_bapiret_warning(self.message_w)]
        self.bapiret = BAPIReturn(self.bapirettab)
        self.response = Mock()

    def assertExDataMatch(self, ex):
        self.assertEqual(str(ex), '''Error(ERR|333): Error message
Warning(WRN|777): Warning message''')

        self.assertEqual(ex.bapiret._bapirettab, self.bapirettab)
        self.assertEqual(ex.response, self.response)

    def test_ctor_join_list(self):
        ex = BAPIError(self.bapiret, self.response)
        self.assertExDataMatch(ex)

    def test_raises_for_error(self):
        with self.assertRaises(BAPIError) as caught:
            BAPIError.raise_for_error(self.bapirettab, self.response)

        self.assertExDataMatch(caught.exception)

    def test_raises_for_error_with_instance(self):
        with self.assertRaises(BAPIError) as caught:
            BAPIError.raise_for_error(self.bapirettab[0], self.response)

        self.assertEqual(caught.exception.bapiret._bapirettab, self.bapiret[0:1])

    def test_does_not_raise(self):
        BAPIError.raise_for_error([create_bapiret_warning(self.message_w)], self.response)

    def test_contains(self):
        ex = BAPIError(self.bapiret, self.response)
        self.assertTrue(ex.bapiret.contains('ERR', '333'))
        self.assertFalse(ex.bapiret.contains('NOP', '222'))
