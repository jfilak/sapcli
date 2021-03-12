'''BSP CLI tests.'''
#!/usr/bin/env python3

# pylint: disable=protected-access,missing-function-docstring

import base64
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


def get_sample_stat_args():
    args = Mock()
    args.bsp = 'BSP'
    return args


def get_sample_delete_args():
    args = Mock()
    args.bsp = 'BSP'
    args.corrnr = 'TREQ'
    return args


class TestBspCommands(unittest.TestCase):
    '''Test BSP cli commands'''

    @patch('builtins.open', mock_open(read_data=b'SOME_DATA'))
    def test_upload_create_ok(self):
        resp = Mock()
        resp.status_code = 404
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))

        sap.cli.bsp.upload(connection, get_sample_create_args())

        connection.client.entity_sets.Repositories.create_entity.assert_called_once()

    @patch('builtins.open', mock_open(read_data=b'SOME_DATA'))
    def test_upload_update_ok(self):
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock()

        sap.cli.bsp.upload(connection, get_sample_create_args())

        connection.client.entity_sets.Repositories.update_entity.assert_called_once()

    @patch('builtins.open', mock_open(read_data=b'SOME_DATA'))
    def test_upload_http_error(self):
        resp = Mock()
        resp.status_code = 400
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))

        with self.assertRaises(HttpError):
            sap.cli.bsp.upload(connection, get_sample_create_args())

    @patch('logging.getLogger', return_value=MagicMock())
    @patch('builtins.open', mock_open(read_data=b'SOME_DATA'))
    def test_upload_error_creating(self, log_patch):
        resp = Mock()
        resp.status_code = 404
        resp.text = '{"a":"b"}'
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))
        create_request = connection.client.entity_sets.Repositories.create_entity()
        create_request.execute = Mock(side_effect=HttpError('MSG', resp))

        with self.assertRaises(HttpError):
            sap.cli.bsp.upload(connection, get_sample_create_args())

        create_request.custom().custom().custom().set.assert_called_once_with(**{
            'Name': 'BSP',
            'Package': 'PKG',
            'ZipArchive': base64.b64encode(b'SOME_DATA').decode('utf8')
        })

        log_patch.return_value.info.assert_called_with("{'a': 'b'}")

    def test_stat_ok(self):
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock()

        result = sap.cli.bsp.stat(connection, get_sample_stat_args())

        self.assertEqual(result, 0)

    def test_stat_not_found(self):
        resp = Mock()
        resp.status_code = 404
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))

        result = sap.cli.bsp.stat(connection, get_sample_stat_args())

        self.assertEqual(result, 10)

    def test_stat_http_error(self):
        resp = Mock()
        resp.status_code = 500
        connection = MagicMock()
        connection.client.entity_sets.Repositories.get_entity().execute = Mock(
            side_effect=HttpError('MSG', resp))

        with self.assertRaises(HttpError):
            sap.cli.bsp.stat(connection, get_sample_create_args())

    def test_delete_ok(self):
        connection = MagicMock()
        connection.client.entity_sets.Repositories.delete_entity().custom().execute = Mock()

        sap.cli.bsp.delete(connection, get_sample_delete_args())

        self.assertEqual(connection.client.entity_sets.Repositories.delete_entity.call_count, 2)

    def test_delete_not_found(self):
        resp = Mock()
        resp.status_code = 404
        connection = MagicMock()
        connection.client.entity_sets.Repositories.delete_entity().custom().execute = Mock(
            side_effect=HttpError('MSG', resp))

        sap.cli.bsp.delete(connection, get_sample_delete_args())

        self.assertEqual(connection.client.entity_sets.Repositories.delete_entity.call_count, 2)

    def test_delete_http_error(self):
        resp = Mock()
        resp.status_code = 500
        connection = MagicMock()
        connection.client.entity_sets.Repositories.delete_entity().custom().execute = Mock(
            side_effect=HttpError('MSG', resp))

        with self.assertRaises(HttpError):
            sap.cli.bsp.delete(connection, get_sample_delete_args())
