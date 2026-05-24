#!/usr/bin/env python3

import json
import unittest

import sap.cli.messageclass

from mock import Connection, Response, BufferConsole
from infra import generate_parse_args
from fixtures_sap_adt_messageclass import (
    MESSAGE_CLASS_NAME,
    MESSAGE_CLASS_ADT_GET_RESPONSE_XML,
    MESSAGE_CLASS_ADT_GET_RESPONSE_EMPTY_XML,
    LOCK_RESPONSE_XML,
)

parse_args = generate_parse_args(sap.cli.messageclass.CommandGroup())


class TestMessageClassCreate(unittest.TestCase):

    def test_create(self):
        connection = Connection()
        args = parse_args('create', MESSAGE_CLASS_NAME, 'Testing messages', '$TMP')
        args.execute(connection, args)

        self.assertEqual(connection.execs[0].method, 'POST')
        self.assertEqual(connection.execs[0].adt_uri, '/sap/bc/adt/messageclass')


class TestMessageClassRead(unittest.TestCase):

    def test_read_human_default(self):
        connection = Connection([
            Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        args = parse_args('read', MESSAGE_CLASS_NAME)
        args.console_factory = lambda: console
        args.execute(connection, args)

        self.assertIn('Description: Testing messages', console.capout)
        self.assertIn('No. |', console.capout)
        self.assertIn('000 |', console.capout)

    def test_read_json(self):
        connection = Connection([
            Response(text=MESSAGE_CLASS_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        args = parse_args('read', MESSAGE_CLASS_NAME, '--output', 'JSON')
        args.console_factory = lambda: console
        args.execute(connection, args)

        output = json.loads(console.capout)
        self.assertEqual(output['formatVersion'], '1')
        self.assertEqual(output['header']['description'], 'Testing messages')
        self.assertEqual(len(output['messages']), 2)
        self.assertEqual(output['messages'][0]['number'], '000')
        self.assertEqual(output['messages'][0]['text'], '&')
        self.assertEqual(output['messages'][0]['selfexplanatory'], True)


class TestMessageClassWrite(unittest.TestCase):

    def test_write_not_implemented(self):
        connection = Connection()

        console = BufferConsole()
        args = parse_args('write', MESSAGE_CLASS_NAME)
        args.console_factory = lambda: console
        args.execute(connection, args)

        self.assertIn('Not implemented yet', console.capout)


class TestMessageClassActivate(unittest.TestCase):

    def test_activate(self):
        connection = Connection()

        console = BufferConsole()
        args = parse_args('activate', MESSAGE_CLASS_NAME)
        args.console_factory = lambda: console
        args.execute(connection, args)

        self.assertIn('Message classes do not require activation', console.capout)


if __name__ == '__main__':
    unittest.main()
