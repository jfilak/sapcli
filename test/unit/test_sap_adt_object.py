#!/bin/python

import unittest

from sap.errors import SAPCliError
import sap.adt

from fixtures_adt import DummyADTObject
from mock import Response, Connection


FIXTURE_LOCK_RESPONSE_OK = Response(text='win',
                                    status_code=200,
                                    headers={'Content-Type': 'dataname=com.sap.adt.lock.Result'})


class TestADTObject(unittest.TestCase):

    def test_uri(self):
        victory = DummyADTObject()

        self.assertEquals(victory.uri, 'awesome/success/noobject')

    def test_lock_modify_ok(self):
        connection = Connection([FIXTURE_LOCK_RESPONSE_OK])

        victory = DummyADTObject(connection=connection)
        victory.lock()
        self.assertEquals(victory._lock, FIXTURE_LOCK_RESPONSE_OK.text)

        try:
            victory.lock()
            self.assertFail('Exception was expected')
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: already locked')

    def test_lock_modify_invalid(self):
        response = Response(text='invalid',
                            status_code=200,
                            headers={'Content-Type': 'text/plain'})

        connection = Connection([response, response])

        victory = DummyADTObject(connection=connection)

        try:
            victory.lock()
            self.assertFail('Exception was expected')
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: lock response does not have lock result\ninvalid')

        try:
            victory.lock()
            self.assertFail('Exception was expected')
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: lock response does not have lock result\ninvalid')

    def test_unlock_ok(self):
        connection = Connection([FIXTURE_LOCK_RESPONSE_OK, None])

        victory = DummyADTObject(connection=connection)
        victory.lock()
        victory.unlock()
        self.assertIsNone(victory._lock)

    def test_unlock_not_locked(self):
        victory = DummyADTObject()

        try:
            victory.unlock()
        except SAPCliError as ex:
            self.assertEquals(str(ex), f'Object {victory.uri}: not locked')


if __name__ == '__main__':
    unittest.main()
