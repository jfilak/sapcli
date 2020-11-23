import unittest
from types import SimpleNamespace
from unittest.mock import patch, mock_open, call, Mock

import sap.cli.strust
from sap.errors import SAPCliError
from sap.rfc.strust import CLIENT_ANONYMOUS, CLIENT_STANDART


class TestCommandGroup(unittest.TestCase):

    def test_cli_ddl_commands_constructor(self):
        sap.cli.strust.CommandGroup()


class TestAddAllFiles(unittest.TestCase):

    def test_smooth_run(self):
        def rfc_response(function, *args):
            return {
                'SSFR_PSE_CHECK': {'ET_BAPIRET2': [{'TYPE': 'S'}]},
                'SSFR_PUT_CERTIFICATE': {'ET_BAPIRET2': []},
                'ICM_SSL_PSE_CHANGED': None,
                'SSFR_GET_CERTIFICATELIST': {'ET_CERTIFICATELIST': ['xcert', ]},
                'SSFR_PARSE_CERTIFICATE': {'EV_SUBJECT': None}
            }[function]

        mock_connection = Mock()
        mock_connection.call = Mock(side_effect=rfc_response)
        mock_connection.__enter__ = Mock(return_value=mock_connection)
        mock_connection.__exit__ = Mock(return_value=False)

        with patch('sap.cli.strust.open', mock_open(read_data='CERT')) as mock_file:
            sap.cli.strust.putcertificate(
                mock_connection, SimpleNamespace(
                    paths=['/path/1', '/path/2'],
                    storage=[CLIENT_STANDART, CLIENT_ANONYMOUS, ],
                    identity=[]
                ))

        self.assertEquals(
            mock_file.mock_calls,
            [call('/path/1'),
             call().__enter__(),
             call().read(),
             call().__exit__(None, None, None),
             call('/path/2'),
             call().__enter__(),
             call().read(),
             call().__exit__(None, None, None)])

        print(mock_connection.call.call_args_list)

        self.assertEquals(
            mock_connection.call.call_args_list,
            [call('SSFR_PSE_CHECK',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}}),
             call('SSFR_PSE_CHECK',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}}),
             call('SSFR_PUT_CERTIFICATE',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}, 'IV_CERTIFICATE': 'CERT'}),
             call('SSFR_PUT_CERTIFICATE',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}, 'IV_CERTIFICATE': 'CERT'}),
             call('SSFR_PUT_CERTIFICATE',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}, 'IV_CERTIFICATE': 'CERT'}),
             call('SSFR_PUT_CERTIFICATE',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}, 'IV_CERTIFICATE': 'CERT'}),
             call('ICM_SSL_PSE_CHANGED', {}),
             call('SSFR_GET_CERTIFICATELIST',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}}),
             call('SSFR_PARSE_CERTIFICATE',
                  {'IV_CERTIFICATE': 'xcert'}),
             call('SSFR_GET_CERTIFICATELIST',
                  {'IS_STRUST_IDENTITY': {'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}}),
             call('SSFR_PARSE_CERTIFICATE',
                  {'IV_CERTIFICATE': 'xcert'})])

    def test_invalid_rage(self):
        mock_connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.strust.putcertificate(
                mock_connection, SimpleNamespace(
                    paths=['/path/1', '/path/2'],
                    storage=['foo'],
                    identity=[]
                ))

        self.assertEqual('Unknown storage: foo', str(caught.exception))

    def test_invalid_identity(self):
        mock_connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.strust.putcertificate(
                mock_connection, SimpleNamespace(
                    paths=['/path/1', '/path/2'],
                    storage=[CLIENT_ANONYMOUS],
                    identity=['foo']
                ))

        self.assertEqual('Invalid identity format', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
