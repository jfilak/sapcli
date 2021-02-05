'''BSP CLI tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

import sap.cli.bsp
from sap.errors import ResourceAlreadyExistsError
from pyodata.exceptions import HttpError


def get_sample_create_args():
    args = Mock()
    args.bsp = 'BSP'
    args.package = 'PKG'
    args.app = 'PATH'
    args.corrnr = 'TREQ'
    return args


class TestBspCommands(unittest.TestCase):
    '''Test BSP cli commands'''

    @patch('builtins.open', mock_open(read_data='SOME_DATA'))
    def test_create_ok(self):
        resp = Mock()
        resp.status_code = 404
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))

        sap.cli.bsp.create(connection, get_sample_create_args())

        connection.client.entity_sets.Repositories.create_entity.assert_called_once()

    @patch('builtins.open', mock_open(read_data='SOME_DATA'))
    def test_create_already_exist(self):
        connection = MagicMock()

        with self.assertRaises(ResourceAlreadyExistsError):
            sap.cli.bsp.create(connection, get_sample_create_args())

    @patch('builtins.open', mock_open(read_data='SOME_DATA'))
    def test_create_http_error(self):
        resp = Mock()
        resp.status_code = 400
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))

        with self.assertRaises(HttpError):
            sap.cli.bsp.create(connection, get_sample_create_args())

    @patch('logging.getLogger', return_value=MagicMock())
    @patch('builtins.open', mock_open(read_data='SOME_DATA'))
    def test_create_error_creating(self, log_patch):
        resp = Mock()
        resp.status_code = 404
        resp.text = '{"a":"b"}'
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))
        create_request = connection.client.entity_sets.Repositories.create_entity().custom().custom().custom()
        create_request.execute = Mock(side_effect=HttpError('MSG', resp))

        with self.assertRaises(HttpError):
            sap.cli.bsp.create(connection, get_sample_create_args())

        create_request.set.assert_called_once_with(**{
            'Name': 'BSP',
            'Package': 'PKG',
            'ZipArchive': 'SOME_DATA'
        })

        log_patch.return_value.info.assert_called_once_with("{'a': 'b'}")
