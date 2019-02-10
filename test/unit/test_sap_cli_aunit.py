#!/usr/bin/env python3

import unittest
from unittest.mock import patch
from types import SimpleNamespace

from sap.errors import SAPCliError
import sap.cli.aunit

from mock import Connection, Response
from fixtures_adt import LOCK_RESPONSE_OK, EMPTY_RESPONSE_OK


class TestAUnitWrite(unittest.TestCase):

    def test_aunit_invalid(self):
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.aunit.run('wrongconn', SimpleNamespace(type='foo'))

        self.assertEqual(str(cm.exception), 'Unknown type: foo')

    def test_aunit_program(self):
        connection = Connection([Response(status_code=200, text='program unit tests results', headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(type='program', name='yprogram'))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('programs/programs/yprogram', connection.execs[0].body)
        mock_print.assert_called_once_with('program unit tests results')

    def test_aunit_class(self):
        connection = Connection([Response(status_code=200, text='class unit tests results', headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(type='class', name='yclass'))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('oo/classes/yclass', connection.execs[0].body)
        mock_print.assert_called_once_with('class unit tests results')

    def test_aunit_package(self):
        connection = Connection([Response(status_code=200, text='package unit tests results', headers={})])

        with patch('sap.cli.aunit.print') as mock_print:
            sap.cli.aunit.run(connection, SimpleNamespace(type='package', name='ypackage'))

        self.assertEqual(len(connection.execs), 1)
        self.assertIn('packages/ypackage', connection.execs[0].body)
        mock_print.assert_called_once_with('package unit tests results')


if __name__ == '__main__':
    unittest.main()
