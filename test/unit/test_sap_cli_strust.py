import unittest
from types import SimpleNamespace
from unittest.mock import patch, mock_open, call, Mock
from mock import (
    ConsoleOutputTestCase,
    PatcherTestCase
)

import sap.cli.strust
from sap.errors import SAPCliError
from sap.rfc.strust import CLIENT_ANONYMOUS, CLIENT_STANDART

from infra import generate_parse_args


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

        self.assertEqual('Invalid identity format: foo', str(caught.exception))

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


class TestArgumentsToStores(unittest.TestCase):

    def test_invalid_storage(self):
        mock_connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.strust.ssl_storages_from_arguments(
                mock_connection, SimpleNamespace(
                    storage=['foo'],
                    identity=[]
                ))

        self.assertEqual('Unknown storage: foo', str(caught.exception))

    def test_invalid_identity(self):
        mock_connection = Mock()

        with self.assertRaises(SAPCliError) as caught:
            sap.cli.strust.ssl_storages_from_arguments(
                mock_connection, SimpleNamespace(
                    storage=[CLIENT_ANONYMOUS],
                    identity=['foo']
                ))

        self.assertEqual('Invalid identity format: foo', str(caught.exception))

class TestListAndDumpStrustCerts(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()
        self.fixture_nice_dn = 'CN=SuccessfulExists, OU=Victory, O=Cool, C=CZ'

    def list_certs(self, *test_args):
        cmd_args = parse_args('listcertificates', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def dump_certs(self, *test_args):
        cmd_args = parse_args('dumpcertificates', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def test_storage_invalid(self):
        with self.assertRaises(SystemExit):
            self.list_certs("-s", "invalidstorage")
        with self.assertRaises(SystemExit):
            self.dump_certs("-s", "invalidstorage")

    def test_identity_invalid(self):
        with self.assertRaises(SAPCliError) as caught:
            self.list_certs("-i", "foo/bar/blah")
        self.assertEqual('Invalid identity format: foo/bar/blah', str(caught.exception))

        with self.assertRaises(SAPCliError) as caught:
            self.dump_certs("-i", "foo/bar/blah")
        self.assertEqual('Invalid identity format: foo/bar/blah', str(caught.exception))

    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=False)

    def test_unknown_storage(self, fake_exists):
        with self.assertRaises(SAPCliError) as caught:
            self.list_certs("-i", "x/y")
        self.assertEqual(
            "Storage for identity {'PSE_CONTEXT': 'x', 'PSE_APPLIC': 'y'} does not exist",
            str(caught.exception)
        )

        with self.assertRaises(SAPCliError) as caught:
            self.dump_certs("-i", "x/y")
        self.assertEqual(
            "Storage for identity {'PSE_CONTEXT': 'x', 'PSE_APPLIC': 'y'} does not exist",
            str(caught.exception)
        )

    def test_neither_identity_nor_storage(self):
        # This is valid case, no need to specify anythig for listing - the output 
        # will be empty.
        self.list_certs()
        self.assertConsoleContents(self.console, stdout='', stderr='')

        self.dump_certs()
        self.assertConsoleContents(self.console, stdout='', stderr='')

    @patch('sap.rfc.strust.SSLCertStorage.parse_certificate', return_value={"EV_SUBJECT": "cert1"})
    @patch('sap.rfc.strust.SSLCertStorage.get_certificates', return_value=["cert1"])
    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=True)
    def test_list_certs_single(self, fake_exists, fake_get_certificates, fake_parse_certificate):
        self.list_certs("-s", "client_anonymous")

        fake_exists.assert_called_once()
        fake_get_certificates.assert_called_once()
        fake_parse_certificate.assert_called_with("cert1")

        self.assertConsoleContents(self.console, stdout='* cert1\n')

    @patch('sap.rfc.strust.SSLCertStorage.parse_certificate', side_effect=(lambda cert: {"EV_SUBJECT": cert}))
    @patch('sap.rfc.strust.SSLCertStorage.get_certificates', return_value=["cert1", "cert2"])
    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=True)
    def test_list_certs_multiple(self, fake_exists, fake_get_certificates, fake_parse_certificate):

        self.list_certs("-s", "client_anonymous")

        fake_exists.assert_called_once()
        fake_get_certificates.assert_called_once()

        self.assertConsoleContents(self.console, stdout='* cert1\n* cert2\n')

    @patch('sap.rfc.strust.SSLCertStorage.get_certificates', return_value=[b"cert1"])
    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=True)
    def test_dump_certs_single(self, fake_exists, fake_get_certificates):
        self.dump_certs("-s", "client_anonymous")

        fake_exists.assert_called_once()
        fake_get_certificates.assert_called_once()

        self.assertConsoleContents(self.console, stdout='''-----BEGIN CERTIFICATE-----
Y2VydDE=
-----END CERTIFICATE-----
''')

    @patch('sap.rfc.strust.SSLCertStorage.get_certificates', return_value=[b"cert1", b"cert2"])
    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=True)
    def test_dump_certs_single(self, fake_exists, fake_get_certificates):
        self.dump_certs("-s", "client_anonymous")

        fake_exists.assert_called_once()
        fake_get_certificates.assert_called_once()

        self.assertConsoleContents(self.console, stdout='''-----BEGIN CERTIFICATE-----
Y2VydDE=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
Y2VydDI=
-----END CERTIFICATE-----
''')


if __name__ == '__main__':
    unittest.main()
