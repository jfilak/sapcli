#!/usr/bin/env python3

import unittest

import sap.cli.my_object

from mock import (
    BufferConsole,
    Connection,
    Response,
)

from infra import generate_parse_args
from fixtures_sap_adt_authorization_field import (
    MY_OBJECT_NAME,
    MY_OBJECT_ADT_GET_RESPONSE_XML,
)

parse_args = generate_parse_args(sap.cli.my_object.CommandGroup())


class TestMyObjectRead(unittest.TestCase):

    def my_object_read_cmd(self, *args, **kwargs):
        return parse_args('read', *args, **kwargs)

    def test_read(self):
        connection = Connection([
            Response(text=MY_OBJECT_ADT_GET_RESPONSE_XML, status_code=200, headers={})
        ])

        console = BufferConsole()
        the_cmd = self.authorization_field_read_cmd(MY_OBJECT_NAME)
        the_cmd.console_factory = lambda: console
        the_cmd.execute(connection, the_cmd)

        expected_output = '<object read output>'

        self.assertEqual(console.capout, expected_output)


if __name__ == '__main__':
    unittest.main()
