import unittest
from types import SimpleNamespace
from unittest.mock import patch, mock_open, call, Mock

import argparse

import sap.cli.strust
from sap.errors import SAPCliError
from sap.rfc.strust import CLIENT_ANONYMOUS, CLIENT_STANDART


from infra import generate_parse_args
from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase
)


parse_args = generate_parse_args(sap.cli.strust.CommandGroup())


class RFCCall:

    def __init__(self, function, **kwargs):
        self.function = function
        self.kwargs = kwargs

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        params = ', '.join((f'{name}={value}' for name, value in self.kwargs.items()))
        return f'{self.function}({params})'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.function == other.function and self.kwargs == other.kwargs


class TestCommandGroup(unittest.TestCase):

    def test_cli_ddl_commands_constructor(self):
        sap.cli.strust.CommandGroup()


class TestAddAllFiles(unittest.TestCase):

    def setUp(self):
        self.rfc_calls = list()
        self.ssfr_pse_check_return_value = {'ET_BAPIRET2': [{'TYPE': 'S'}]}

        def rfc_response(function, **kwargs):
            self.rfc_calls.append(RFCCall(function, **kwargs))

            return {
                'SSFR_PSE_CHECK': self.ssfr_pse_check_return_value,
                'SSFR_PSE_CREATE': {'ET_BAPIRET2': []},
                'SSFR_PUT_CERTIFICATE': {'ET_BAPIRET2': []},
                'ICM_SSL_PSE_CHANGED': None,
                'SSFR_GET_CERTIFICATELIST': {'ET_CERTIFICATELIST': ['xcert', ]},
                'SSFR_PARSE_CERTIFICATE': {'EV_SUBJECT': None}
            }[function]

        self.mock_connection = Mock()
        self.mock_connection.call = Mock(side_effect=rfc_response)
        self.mock_connection.__enter__ = Mock(return_value=self.mock_connection)
        self.mock_connection.__exit__ = Mock(return_value=False)


    def assert_smooth_run(self, params):
        with patch('sap.cli.strust.open', mock_open(read_data='CERT')) as mock_file:
            sap.cli.strust.putcertificate(self.mock_connection, params)

        #print(mock_file.mock_calls)

        self.assertEquals(
            mock_file.mock_calls,
            [call('/path/1', 'rb'),
             call().__enter__(),
             call().read(),
             call().__exit__(None, None, None),
             call('/path/2', 'rb'),
             call().__enter__(),
             call().read(),
             call().__exit__(None, None, None)])

        #print(mock_connection.call.call_args_list)

        self.assertEquals(
            self.mock_connection.call.call_args_list,
            [call('SSFR_PSE_CHECK',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}),
             call('SSFR_PSE_CHECK',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'},
                  IV_CERTIFICATE='CERT'),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'},
                  IV_CERTIFICATE='CERT'),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'},
                  IV_CERTIFICATE='CERT'),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'},
                  IV_CERTIFICATE='CERT'),
             call('ICM_SSL_PSE_CHANGED'),
             call('SSFR_GET_CERTIFICATELIST',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}),
             call('SSFR_PARSE_CERTIFICATE',
                  IV_CERTIFICATE='xcert'),
             call('SSFR_GET_CERTIFICATELIST',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}),
             call('SSFR_PARSE_CERTIFICATE',
                  IV_CERTIFICATE='xcert')])

    def test_smooth_run_storage(self):
        self.assert_smooth_run(SimpleNamespace(
            paths=['/path/1', '/path/2'],
            storage=[CLIENT_STANDART, CLIENT_ANONYMOUS, ],
            identity=[]
        ))

    def test_smooth_run_identity(self):
        self.assert_smooth_run(SimpleNamespace(
            paths=['/path/1', '/path/2'],
            storage=[],
            identity=['SSLC/DFAULT', 'SSLC/ANONYM']
        ))

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

    def test_with_pse_file_params(self):
        args = parse_args('putcertificate',
                          '-i', 'CONT/APP',
                          '-d', 'ou=sapcli',
                          '-k', '4096',
                          '-l', 'H',
                          '/path/1')

        self.ssfr_pse_check_return_value = {'ET_BAPIRET2': [{'TYPE': 'E', 'NUMBER': '031'}]}
        with patch('sap.cli.strust.open', mock_open(read_data='CERT')) as mock_file:
            args.execute(self.mock_connection, args)

        self.assertEqual(self.rfc_calls[1],
                         RFCCall('SSFR_PSE_CREATE',
                                 IS_STRUST_IDENTITY={'PSE_CONTEXT': 'CONT',
                                                     'PSE_APPLIC': 'APP'},
                                 IV_ALG='H',
                                 IV_KEYLEN=4096,
                                 IV_REPLACE_EXISTING_PSE='-',
                                 IV_DN='ou=sapcli'
                                )
                        )


class TestCreatePSE(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()
        self.fixture_nice_dn = 'CN=SuccessfulExists, OU=Victory, O=Cool, C=CZ'

    def assert_defaults_for_server_standard(self, fake_exists, fake_create, **kwargs):
        fake_exists.assert_called_once()

        storage = fake_exists.call_args.args[0]
        self.assertEqual(
            storage.identity,
            {'PSE_CONTEXT': 'SSLS',
             'PSE_APPLIC': 'DFAULT'
            }
        )

        fake_create.assert_called_once_with(
            storage,
            alg=kwargs.get('alg', 'S'),
            keylen=kwargs.get('keylen', 2048),
            dn=self.fixture_nice_dn,
            replace=kwargs.get('replace', False)
        )

    def createpse(self, *test_args):
        cmd_args = parse_args('createpse', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def test_storage_invalid(self):
        with self.assertRaises(SystemExit):
            self.createpse('-s', 'something', '--dn', 'CN=SuccessfulFailure')

    def test_identity_invalid(self):
        with self.assertRaises(SAPCliError) as caught:
            self.createpse('-i', 'foo/bar/blah', '--dn', 'CN=SuccessfulFailure')

        self.assertEqual('Invalid identity format: foo/bar/blah', str(caught.exception))

    def test_neither_identity_nor_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.createpse('--dn', 'CN=SuccessfulFailure')

        self.assertEqual('Neither -i nor -s was provided.', str(caught.exception))

    def test_both_identity_and_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.createpse('-i', 'SSLS/DFAULT', '-s', 'server_standard', '--dn', 'CN=SuccessfulFailure')

        self.assertEqual('User either -i or -s but not both.', str(caught.exception))

    @patch('sap.rfc.strust.SSLCertStorage.create', side_effect=Exception)
    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=True)
    def test_storage_ok_exists(self, fake_exists, fake_create):
        self.createpse('-s', 'server_standard', '--dn', 'CN=SuccessfulExists')

        fake_exists.assert_called_once()
        fake_create.assert_not_called()
        self.assertConsoleContents(console=self.console, stdout='Nothing to do - the PSE SSLS/DFAULT already exists\n')

    @patch('sap.rfc.strust.SSLCertStorage.create', side_effect=Exception)
    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=True)
    def test_identity_ok_exists(self, fake_exists, fake_create):
        self.createpse('-i', 'SQRT/DNKROZ', '--dn', 'CN=SuccessfulExists')

        fake_exists.assert_called_once()
        fake_create.assert_not_called()

        self.assertConsoleContents(console=self.console, stdout='Nothing to do - the PSE SQRT/DNKROZ already exists\n')

    @patch.object(sap.rfc.strust.SSLCertStorage, 'create', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'exists', autospec=True)
    def test_storage_ok_create(self, fake_exists, fake_create):
        fake_exists.return_value = False

        self.createpse('-s', 'server_standard', '--dn', self.fixture_nice_dn)
        self.assert_defaults_for_server_standard(fake_exists, fake_create)

    @patch.object(sap.rfc.strust.SSLCertStorage, 'create', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'exists', autospec=True)
    def test_identity_ok_create(self, fake_exists, fake_create):
        fake_exists.return_value = False

        self.createpse('-i', 'SSLS/DFAULT', '--dn', self.fixture_nice_dn)
        self.assert_defaults_for_server_standard(fake_exists, fake_create)

    @patch.object(sap.rfc.strust.SSLCertStorage, 'create', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'exists', autospec=True)
    def test_storage_ok_create_overwrite(self, fake_exists, fake_create):
        fake_exists.return_value = True

        self.createpse('-s', 'server_standard', '--dn', 'CN=SuccessfulExists, OU=Victory, O=Cool, C=CZ', '--overwrite')
        self.assert_defaults_for_server_standard(fake_exists, fake_create, replace=True)

    @patch.object(sap.rfc.strust.SSLCertStorage, 'create', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'exists', autospec=True)
    def test_identity_ok_create_overwrite(self, fake_exists, fake_create):
        fake_exists.return_value = True

        self.createpse('-i', 'SSLS/DFAULT', '--dn', 'CN=SuccessfulExists, OU=Victory, O=Cool, C=CZ', '--overwrite')
        self.assert_defaults_for_server_standard(fake_exists, fake_create, replace=True)

    @patch.object(sap.rfc.strust.SSLCertStorage, 'create', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'exists', autospec=True)
    def test_storage_ok_create_all(self, fake_exists, fake_create):
        fake_exists.return_value = False

        self.createpse('-s', 'server_standard', '-l', 'RSA', '-k', '4096', '--dn', self.fixture_nice_dn)
        self.assert_defaults_for_server_standard(fake_exists, fake_create, alg='R', keylen=4096)

    @patch.object(sap.rfc.strust.SSLCertStorage, 'create', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'exists', autospec=True)
    def test_identity_ok_create_all(self, fake_exists, fake_create):
        fake_exists.return_value = False

        self.createpse('-i', 'SSLS/DFAULT', '-l', 'RSA', '-k', '4096', '--dn', self.fixture_nice_dn)
        self.assert_defaults_for_server_standard(fake_exists, fake_create, alg='R', keylen=4096)


if __name__ == '__main__':
    unittest.main()
