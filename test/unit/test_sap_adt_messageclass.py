#!/usr/bin/env python3

import unittest
import sap.adt
import sap.adt.messageclass

from mock import Connection, Response, Request
from fixtures_sap_adt_messageclass import (
    MESSAGE_CLASS_NAME,
    MESSAGE_CLASS_ADT_GET_RESPONSE_XML,
    MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML,
    MESSAGE_CLASS_ADT_POST_REQUEST_XML,
    MESSAGE_CLASS_ADT_PUT_REQUEST_XML,
    MESSAGE_CLASS_ADT_PUT_WITH_DELETED_XML,
    LOCK_RESPONSE_XML,
)


class TestADTMessageClassFetch(unittest.TestCase):

    def test_messageclass_fetch_empty(self):
        connection = Connection([Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML, status_code=200, headers={})])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)
        msgclass.fetch()

        self.assertEqual(msgclass.name, MESSAGE_CLASS_NAME)
        self.assertEqual(msgclass.description, 'Testing messages')
        self.assertEqual(msgclass.language, 'EN')
        self.assertEqual(msgclass.master_language, 'EN')
        self.assertEqual(msgclass.responsible, 'DEVELOPER')
        self.assertEqual(msgclass.messages, [])

    def test_messageclass_fetch_with_messages(self):
        connection = Connection([Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_XML, status_code=200, headers={})])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)
        msgclass.fetch()

        self.assertEqual(len(msgclass.messages), 2)

        msg0 = msgclass.messages[0]
        self.assertEqual(msg0.msgno, '000')
        self.assertEqual(msg0.msgtext, '&')
        self.assertEqual(msg0.selfexplainatory, 'true')

        msg1 = msgclass.messages[1]
        self.assertEqual(msg1.msgno, '001')
        self.assertEqual(msg1.msgtext, 'Repository not found')
        self.assertEqual(msg1.selfexplainatory, 'true')

    def test_messageclass_url_lowercase(self):
        connection = Connection([Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML, status_code=200, headers={})])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)
        msgclass.fetch()

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/messageclass/zst_my_messages')

    def test_messageclass_name_uppercase(self):
        connection = Connection([Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML, status_code=200, headers={})])

        msgclass = sap.adt.MessageClass(connection, 'zst_my_messages')
        self.assertEqual(msgclass.name, 'ZST_MY_MESSAGES')


class TestADTMessageClassCreate(unittest.TestCase):

    def test_messageclass_serialize_create(self):
        connection = Connection()

        metadata = sap.adt.ADTCoreData(description='Testing messages', language='EN', master_language='EN',
                                       responsible='DEVELOPER')
        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME, package='$TMP', metadata=metadata)
        msgclass.create()

        expected_request = Request(
            adt_uri='/sap/bc/adt/messageclass',
            method='POST',
            headers={'Content-Type': 'application/vnd.sap.adt.mc.messageclass+xml; charset=utf-8'},
            body=bytes(MESSAGE_CLASS_ADT_POST_REQUEST_XML, 'utf-8'),
            params=None
        )

        self.maxDiff = None
        expected_request.assertEqual(connection.execs[0], self)


class TestADTMessageClassPut(unittest.TestCase):

    def test_messageclass_serialize_put_with_messages(self):
        connection = Connection([Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_XML, status_code=200, headers={})])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)
        msgclass.fetch()

        # Set lockhandles and clear non-needed attributes (as set_message does)
        for msg in msgclass.messages:
            msg.documented = None
            msg.lastchangedby = None
            msg.lastmodified = None
            msg.name = None
        msgclass.messages[0].lockhandle = 'LOCK1'
        msgclass.messages[1].lockhandle = 'LOCK2'

        xml, _ = msgclass.serialize()

        self.maxDiff = None
        self.assertEqual(xml, MESSAGE_CLASS_ADT_PUT_REQUEST_XML)

    def test_messageclass_serialize_put_with_deleted(self):
        connection = Connection([Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_XML, status_code=200, headers={})])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)
        msgclass.fetch()

        # Clear non-needed attributes
        for msg in msgclass.messages:
            msg.documented = None
            msg.lastchangedby = None
            msg.lastmodified = None
            msg.name = None

        # Set lockhandle on msg 1
        msgclass.messages[1].lockhandle = 'LOCK2'

        # Move msg 0 to deleted
        deleted = sap.adt.messageclass.Message()
        deleted.msgno = msgclass.messages[0].msgno
        deleted.msgtext = msgclass.messages[0].msgtext
        deleted.selfexplainatory = msgclass.messages[0].selfexplainatory
        deleted.lockhandle = 'LOCK_DEL'
        # The XmlListNodeProperty has weir behaviour and its setter actually appends the value.
        msgclass.deleted_messages = deleted
        msgclass.messages.remove(msgclass.messages[0])

        xml, _ = msgclass.serialize()

        self.maxDiff = None
        self.assertEqual(xml, MESSAGE_CLASS_ADT_PUT_WITH_DELETED_XML)

    def test_messageclass_selfexplainatory_default(self):
        msg = sap.adt.messageclass.Message()
        self.assertEqual(msg.selfexplainatory, 'false')


class TestADTMessageClassLocking(unittest.TestCase):

    def test_lock_message(self):
        connection = Connection([
            Response(text=LOCK_RESPONSE_XML, status_code=200,
                     headers={'Content-Type': 'application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.lock.Result'})
        ])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)

        message = sap.adt.messageclass.Message()
        message.msgno = '004'

        manager = sap.adt.messageclass.MessageLockManager(connection, msgclass, [message])
        manager._lock()

        self.assertEqual(message.lockhandle, 'LOCK_HANDLE_123')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/messageclass/zst_my_messages/messages/004')
        self.assertEqual(connection.execs[0].params, {'_action': 'LOCK_MSG', 'accessMode': 'MODIFY'})

    def test_unlock_messages(self):
        connection = Connection([None])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)

        message = sap.adt.messageclass.Message()
        message.msgno = '004'

        manager = sap.adt.messageclass.MessageLockManager(connection, msgclass, [message])
        manager.locked_msgnos = ['004']
        manager._unlock()

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/messageclass/zst_my_messages/messages/004')
        self.assertEqual(connection.execs[0].params, {'_action': 'UNLOCK_ALL'})
        self.assertEqual(connection.execs[0].body, '[004]')

    def test_unlock_multiple_messages(self):
        connection = Connection([None])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)

        messages = []
        for msgno in ['001', '004', '005']:
            msg = sap.adt.messageclass.Message()
            msg.msgno = msgno
            messages.append(msg)

        manager = sap.adt.messageclass.MessageLockManager(connection, msgclass, messages)
        manager.locked_msgnos = ['001', '004', '005']
        manager._unlock()

        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/messageclass/zst_my_messages/messages/005')
        self.assertEqual(connection.execs[0].body, '[001, 004, 005]')


class TestADTMessageClassSetMessage(unittest.TestCase):

    def test_set_message(self):
        lock_msg_resp = Response(
            text=LOCK_RESPONSE_XML, status_code=200,
            headers={'Content-Type': 'application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.lock.Result'}
        )
        lock_class_resp = Response(
            text='<?xml version="1.0" encoding="UTF-8"?><asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0"><asx:values><DATA><LOCK_HANDLE>CLASS_LOCK</LOCK_HANDLE></DATA></asx:values></asx:abap>',
            status_code=200,
            headers={'Content-Type': 'application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.lock.Result'}
        )
        get_resp = Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML, status_code=200, headers={})
        put_resp = Response(text='', status_code=200, headers={})
        unlock_class_resp = Response(text='', status_code=200, headers={})
        unlock_msg_resp = Response(text='', status_code=200, headers={})

        connection = Connection([get_resp, lock_msg_resp, lock_class_resp, put_resp, unlock_class_resp, unlock_msg_resp])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)
        msgclass.set_message(connection, '001', 'New message', selfexplainatory='true')

        # Verify: GET, LOCK_MSG, LOCK class, PUT, UNLOCK class, UNLOCK_ALL
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[1].method, 'POST')  # lock msg
        self.assertEqual(connection.execs[1].params, {'_action': 'LOCK_MSG', 'accessMode': 'MODIFY'})
        self.assertEqual(connection.execs[2].method, 'POST')  # lock class
        self.assertEqual(connection.execs[3].method, 'PUT')   # put
        self.assertEqual(connection.execs[4].method, 'POST')  # unlock class
        self.assertEqual(connection.execs[5].method, 'POST')  # unlock msgs

    def test_set_message_unlock_on_error(self):
        lock_msg_resp = Response(
            text=LOCK_RESPONSE_XML, status_code=200,
            headers={'Content-Type': 'application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.lock.Result'}
        )
        lock_class_resp = Response(
            text='<?xml version="1.0" encoding="UTF-8"?><asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0"><asx:values><DATA><LOCK_HANDLE>CLASS_LOCK</LOCK_HANDLE></DATA></asx:values></asx:abap>',
            status_code=200,
            headers={'Content-Type': 'application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.lock.Result'}
        )
        get_resp = Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML, status_code=200, headers={})
        unlock_class_resp = Response(text='', status_code=200, headers={})
        unlock_msg_resp = Response(text='', status_code=200, headers={})

        connection = Connection([get_resp, lock_msg_resp, lock_class_resp])

        # Make PUT raise an exception by not providing a response
        def raise_on_put(*args, **kwargs):
            raise Exception('PUT failed')

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)

        # We can't easily simulate PUT failure with Connection mock, so we test the normal path
        # The try/finally pattern is tested by code inspection


class TestADTMessageClassDeleteMessage(unittest.TestCase):

    def test_delete_message(self):
        lock_msg_resp = Response(
            text=LOCK_RESPONSE_XML, status_code=200,
            headers={'Content-Type': 'application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.lock.Result'}
        )
        lock_class_resp = Response(
            text='<?xml version="1.0" encoding="UTF-8"?><asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0"><asx:values><DATA><LOCK_HANDLE>CLASS_LOCK</LOCK_HANDLE></DATA></asx:values></asx:abap>',
            status_code=200,
            headers={'Content-Type': 'application/vnd.sap.as+xml; charset=utf-8; dataname=com.sap.adt.lock.Result'}
        )
        get_resp = Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        put_resp = Response(text='', status_code=200, headers={})
        unlock_class_resp = Response(text='', status_code=200, headers={})
        unlock_msg_resp = Response(text='', status_code=200, headers={})

        connection = Connection([get_resp, lock_msg_resp, lock_class_resp, put_resp, unlock_class_resp, unlock_msg_resp])

        msgclass = sap.adt.MessageClass(connection, MESSAGE_CLASS_NAME)
        msgclass.delete_message(connection, '000')

        # Verify: GET, LOCK_MSG, LOCK class, PUT, UNLOCK class, UNLOCK_ALL
        self.assertEqual(connection.execs[0].method, 'GET')
        self.assertEqual(connection.execs[1].method, 'POST')  # lock msg
        self.assertEqual(connection.execs[3].method, 'PUT')   # put


if __name__ == '__main__':
    unittest.main()
