#!/bin/python

import unittest

from sap.errors import SAPCliError
import sap.adt

from fixtures_adt import DummyADTObject, LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK
from mock import Response, Connection

class TestADTObject(unittest.TestCase):

    def test_uri(self):
        victory = DummyADTObject()

        self.assertEquals(victory.uri, 'awesome/success/noobject')

    def test_lock_modify_ok(self):
        connection = Connection([LOCK_RESPONSE_OK])

        victory = DummyADTObject(connection=connection)
        victory.lock()
        self.assertEquals(victory._lock, 'win')

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
        connection = Connection([LOCK_RESPONSE_OK, None])

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

    def test_activate(self):
        connection = Connection([EMPTY_RESPONSE_OK])
        victory = DummyADTObject(connection=connection, name='activator')

        victory.activate()

        self.assertEqual(len(connection.execs), 1)
        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, 'activation')

        self.assertEqual(connection.execs[0].headers['Accept'], 'application/xml' )
        self.assertEqual(connection.execs[0].headers['Content-Type'], 'application/xml')
        self.assertEqual(sorted(connection.execs[0].headers.keys()), ['Accept', 'Content-Type'])

        self.assertEqual(connection.execs[0].params['method'], 'activate' )
        self.assertEqual(connection.execs[0].params['preauditRequested'], 'true')
        self.assertEqual(sorted(connection.execs[0].params.keys()), ['method', 'preauditRequested'])

        self.maxDiff = None
        self.assertEqual(connection.execs[0].body, '''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/awesome/success/activator" adtcore:name="ACTIVATOR"/>
</adtcore:objectReferences>''' )


if __name__ == '__main__':
    unittest.main()
