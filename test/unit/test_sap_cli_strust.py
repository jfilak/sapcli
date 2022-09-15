import unittest
import sap.cli.strust

from types import SimpleNamespace
from unittest.mock import patch, mock_open, call, Mock
from io import StringIO
from sap.errors import SAPCliError
from sap.rfc.strust import CLIENT_ANONYMOUS, CLIENT_STANDARD, CLIENT_STANDART

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


class TestReadCertificates(unittest.TestCase):

    def test_single_certificates(self):
        mock_certificate='''-----BEGIN CERTIFICATE-----
01234
-----END CERTIFICATE-----
'''

        sap.cli.core.set_stdin(StringIO(mock_certificate))

        certs = sap.cli.strust.read_certificates()

        self.assertEqual(certs[0], mock_certificate)
        self.assertEqual(len(certs), 1)


    def test_multiple_certificates(self):
        mock_certificate='''-----BEGIN CERTIFICATE-----
56789
-----END CERTIFICATE-----
'''
        mock_certificate_2='''-----BEGIN CERTIFICATE-----
ABCDEF
-----END CERTIFICATE-----
'''

        sap.cli.core.set_stdin(StringIO(mock_certificate + mock_certificate_2))

        certs = sap.cli.strust.read_certificates()

        self.assertEqual(certs[0], mock_certificate)
        self.assertEqual(certs[1], mock_certificate_2)
        self.assertEqual(len(certs), 2)


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
            storage=[CLIENT_STANDARD, CLIENT_ANONYMOUS, ],
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

    def test_with_certificate(self):
        from sap.cli.core import set_stdin

        mock_certificate='''-----BEGIN CERTIFICATE-----
dGVzdF93aXRoX2NlcnRpZmljYXRl
-----END CERTIFICATE-----
'''

        set_stdin(StringIO(mock_certificate))

        sap.cli.strust.putcertificate(self.mock_connection, SimpleNamespace(
            paths=['-'],
            storage=[],
            identity=['SSLC/DFAULT', 'SSLC/ANONYM']
        ))

        # print(self.mock_connection.call.call_args_list)

        self.assertEquals(
            self.mock_connection.call.call_args_list,
            [call('SSFR_PSE_CHECK',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}),
             call('SSFR_PSE_CHECK',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'},
                  IV_CERTIFICATE=str.encode(mock_certificate)),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'},
                  IV_CERTIFICATE=str.encode(mock_certificate)),
             call('ICM_SSL_PSE_CHANGED'),
             call('SSFR_GET_CERTIFICATELIST',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}),
             call('SSFR_PARSE_CERTIFICATE',
                  IV_CERTIFICATE='xcert'),
             call('SSFR_GET_CERTIFICATELIST',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}),
             call('SSFR_PARSE_CERTIFICATE',
                  IV_CERTIFICATE='xcert')])

        set_stdin(None)

    def test_with_multiple_certificates(self):
        from sap.cli.core import set_stdin

        mock_certificate='''-----BEGIN CERTIFICATE-----
dGVzdF93aXRoX2NlcnRpZmljYXRl
-----END CERTIFICATE-----
'''
        mock_certificate_2='''-----BEGIN CERTIFICATE-----
dGVzdF93aXRoX3NlY29uZF9jZXJ0aWZpY2F0ZQ==
-----END CERTIFICATE-----
'''

        set_stdin(StringIO(mock_certificate + mock_certificate_2))

        sap.cli.strust.putcertificate(self.mock_connection, SimpleNamespace(
            paths=['-'],
            storage=[],
            identity=['SSLC/DFAULT', 'SSLC/ANONYM']
        ))

        # print(self.mock_connection.call.call_args_list)

        self.assertEquals(
            self.mock_connection.call.call_args_list,
            [call('SSFR_PSE_CHECK',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}),
             call('SSFR_PSE_CHECK',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'},
                  IV_CERTIFICATE=str.encode(mock_certificate)),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'},
                  IV_CERTIFICATE=str.encode(mock_certificate_2)),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'},
                  IV_CERTIFICATE=str.encode(mock_certificate)),
             call('SSFR_PUT_CERTIFICATE',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'},
                  IV_CERTIFICATE=str.encode(mock_certificate_2)),
             call('ICM_SSL_PSE_CHANGED'),
             call('SSFR_GET_CERTIFICATELIST',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'DFAULT'}),
             call('SSFR_PARSE_CERTIFICATE',
                  IV_CERTIFICATE='xcert'),
             call('SSFR_GET_CERTIFICATELIST',
                  IS_STRUST_IDENTITY={'PSE_CONTEXT': 'SSLC', 'PSE_APPLIC': 'ANONYM'}),
             call('SSFR_PARSE_CERTIFICATE',
                  IV_CERTIFICATE='xcert')])

        set_stdin(None)


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

    def test_use_deprecated_storage(self):
        mock_connection = Mock()

        with self.assertWarns(DeprecationWarning):
            sap.cli.strust._get_ssl_storage_from_args(
                mock_connection, SimpleNamespace(
                    storage=CLIENT_STANDART,
                    identity=None
                )
            )

        with self.assertWarns(DeprecationWarning):
            sap.cli.strust.ssl_storages_from_arguments(
                mock_connection, SimpleNamespace(
                    storage=[CLIENT_STANDART],
                    identity=[]
                )
            )


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
        identity = {
            'PSE_CONTEXT': 'SSLS',
            'PSE_APPLIC': 'DFAULT'
        }

        self.createpse('-s', 'server_standard', '--dn', 'CN=SuccessfulExists')

        fake_exists.assert_called_once()
        fake_create.assert_not_called()
        self.assertConsoleContents(console=self.console, stdout=f'Nothing to do - the PSE {identity} already exists\n')

    @patch('sap.rfc.strust.SSLCertStorage.create', side_effect=Exception)
    @patch('sap.rfc.strust.SSLCertStorage.exists', return_value=True)
    def test_identity_ok_exists(self, fake_exists, fake_create):
        identity = {
            'PSE_CONTEXT': 'SQRT',
            'PSE_APPLIC': 'DNKROZ'
        }
        identity_arg = '{PSE_CONTEXT}/{PSE_APPLIC}'.format(**identity)

        self.createpse('-i', identity_arg, '--dn', 'CN=SuccessfulExists')

        fake_exists.assert_called_once()
        fake_create.assert_not_called()

        self.assertConsoleContents(console=self.console, stdout=f'Nothing to do - the PSE {identity} already exists\n')

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


class TestRemovePSE(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()

    def removepse(self, *test_args):
        cmd_args = parse_args('removepse', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def test_storage_invalid(self):
        with self.assertRaises(SystemExit):
            self.removepse('-s', 'something')

    def test_identity_invalid(self):
        identity = 'something'

        with self.assertRaises(SAPCliError) as caught:
            self.removepse('-i', identity)

        self.assertEqual(f'Invalid identity format: {identity}', str(caught.exception))

    def test_neither_identity_nor_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.removepse()

        self.assertEqual('Neither -i nor -s was provided.', str(caught.exception))

    def test_both_identity_and_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.removepse('-s', 'server_standard', '-i', 'identity')

        self.assertEqual('User either -i or -s but not both.', str(caught.exception))

    @patch.object(sap.rfc.strust.SSLCertStorage, 'remove', autospec=True)
    def test_storage_ok_remove(self, fake_remove):
        self.removepse('-s', 'server_standard')

        fake_remove.assert_called_once()

        storage = fake_remove.call_args.args[0]
        self.assertEqual(
            storage.identity,
            {
                'PSE_CONTEXT': 'SSLS',
                'PSE_APPLIC': 'DFAULT'
            }
        )

    @patch.object(sap.rfc.strust.SSLCertStorage, 'remove', autospec=True)
    def test_identity_ok_remove(self, fake_remove):
        identity = {
            'PSE_CONTEXT': 'SQRT',
            'PSE_APPLIC': 'DNKROZ'
        }
        identity_arg = '{PSE_CONTEXT}/{PSE_APPLIC}'.format(**identity)

        self.removepse('-i', identity_arg)

        fake_remove.assert_called_once()

        storage = fake_remove.call_args.args[0]
        self.assertEqual(
            storage.identity,
            identity
        )


class TestGetCSR(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()

    def getcsr(self, *test_args):
        cmd_args = parse_args('getcsr', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def test_storage_invalid(self):
        with self.assertRaises(SystemExit):
            self.getcsr('-s', 'something')

    def test_identity_invalid(self):
        identity = 'something'

        with self.assertRaises(SAPCliError) as caught:
            self.getcsr('-i', identity)

        self.assertEqual(f'Invalid identity format: {identity}', str(caught.exception))

    def test_neither_identity_nor_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.getcsr()

        self.assertEqual('Neither -i nor -s was provided.', str(caught.exception))

    def test_both_identity_and_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.getcsr('-s', 'server_standard', '-i', 'some/identity')

        self.assertEqual('User either -i or -s but not both.', str(caught.exception))

    @patch.object(sap.rfc.strust.SSLCertStorage, 'get_csr', autospec=True)
    def test_storage_ok_get(self, fake_get_csr):
        self.getcsr('-s', 'server_standard')

        fake_get_csr.assert_called_once()

        storage = fake_get_csr.call_args.args[0]
        self.assertEqual(
            storage.identity,
            {
                'PSE_CONTEXT': 'SSLS',
                'PSE_APPLIC': 'DFAULT'
            }
        )

    @patch.object(sap.rfc.strust.SSLCertStorage, 'get_csr', autospec=True)
    def test_identity_ok_get(self, fake_get_csr):
        identity = {
            'PSE_CONTEXT': 'SQRT',
            'PSE_APPLIC': 'DNKROZ'
        }
        identity_arg = '{PSE_CONTEXT}/{PSE_APPLIC}'.format(**identity)

        self.getcsr('-i', identity_arg)

        fake_get_csr.assert_called_once()

        storage = fake_get_csr.call_args.args[0]
        self.assertEqual(
            storage.identity,
            identity
        )


class TestPutPKC(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()

        self.open_mock = patch('sap.cli.strust.open', mock_open(read_data='certificate')).start()

    def putpkc(self, *test_args):
        cmd_args = parse_args('putpkc', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def assert_response_and_storage(self, fake_put_cert, fake_add_file, mocked_input):
        pkc_response = fake_add_file.call_args.args[0]
        fake_add_file.assert_called_once_with(pkc_response, mocked_input)

        storage = fake_put_cert.call_args.args[0]
        self.assertEqual(
            storage.identity,
            {
                'PSE_CONTEXT': 'SSLS',
                'PSE_APPLIC': 'DFAULT'
            }
        )
        fake_put_cert.assert_called_once_with(storage, pkc_response)

    def test_storage_invalid(self):
        with self.assertRaises(SystemExit):
            self.putpkc('-s', 'something', 'certificate_path')

    def test_identity_invalid(self):
        identity = 'something'

        with self.assertRaises(SAPCliError) as caught:
            self.putpkc('-i', identity, 'certificate_path')

        self.assertEqual(f'Invalid identity format: {identity}', str(caught.exception))

    def test_neither_identity_nor_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.putpkc('certificate_path')

        self.assertEqual('Neither -i nor -s was provided.', str(caught.exception))

    def test_both_identity_and_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.putpkc('-s', 'server_standard', '-i', 'some/identity', 'certificate_path')

        self.assertEqual('User either -i or -s but not both.', str(caught.exception))

    def test_putpkc_without_path(self):
        with self.assertRaises(SystemExit):
            self.putpkc('-s', 'server_standard')

    def test_putpkc_unable_to_load(self):
        with self.assertRaises(SAPCliError) as caught:
            with patch('sap.cli.strust.open', mock_open()):
                self.putpkc('-s', 'server_standard', 'certificate_path')

        self.assertEqual('Unable to load certificate from the PATH', str(caught.exception))

    @patch.object(sap.rfc.strust.PKCResponseABAPData, 'add_file', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'put_identity_cert', autospec=True)
    def test_storage_ok_putpkc_read_from_stdin(self, fake_put_cert, fake_add_file):
        with patch('sys.stdin', StringIO('certificate')) as mocked_stdin:
            self.putpkc('-s', 'server_standard', '-')

        self.assert_response_and_storage(fake_put_cert, fake_add_file, mocked_stdin)

    @patch.object(sap.rfc.strust.PKCResponseABAPData, 'add_file', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'put_identity_cert', autospec=True)
    def test_storage_ok_putpkc_read_from_file(self, fake_put_cert, fake_add_file):
        self.putpkc('-s', 'server_standard', 'certificate_path')

        self.assert_response_and_storage(fake_put_cert, fake_add_file, self.open_mock.return_value)

    @patch.object(sap.rfc.strust.PKCResponseABAPData, 'add_file', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'put_identity_cert', autospec=True)
    def test_identity_ok_putpkc_read_from_stdin(self, fake_put_cert, fake_add_file):
        with patch('sys.stdin', StringIO('certificate')) as mocked_stdin:
            self.putpkc('-i', 'SSLS/DFAULT', '-')

        self.assert_response_and_storage(fake_put_cert, fake_add_file, mocked_stdin)

    @patch.object(sap.rfc.strust.PKCResponseABAPData, 'add_file', autospec=True)
    @patch.object(sap.rfc.strust.SSLCertStorage, 'put_identity_cert', autospec=True)
    def test_identity_ok_putpkc_read_from_file(self, fake_put_cert, fake_add_file):
        self.putpkc('-i', 'SSLS/DFAULT', 'certificate_path')

        self.assert_response_and_storage(fake_put_cert, fake_add_file, self.open_mock.return_value)


class TestUpload(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()

        self.pse_file_content = 'data'
        patch('sap.cli.strust.open', mock_open(read_data=self.pse_file_content)).start()

    def upload(self, *test_args):
        cmd_args = parse_args('upload', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def assert_password_and_upload(self, fake_upload, expected_password, replace=False):
        storage = fake_upload.call_args.args[0]
        self.assertEqual(
            storage.identity,
            {
                'PSE_CONTEXT': 'SSLS',
                'PSE_APPLIC': 'DFAULT'
            }
        )
        fake_upload.assert_called_once_with(
            storage, self.pse_file_content, replace=replace, password=expected_password
        )

    def test_storage_invalid(self):
        with self.assertRaises(SystemExit):
            self.upload('-s', 'something', 'pse_path')

    def test_identity_invalid(self):
        identity = 'something'

        with self.assertRaises(SAPCliError) as caught:
            self.upload('-i', identity, 'pse_path')

        self.assertEqual(f'Invalid identity format: {identity}', str(caught.exception))

    def test_neither_identity_nor_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.upload('pse_path')

        self.assertEqual('Neither -i nor -s was provided.', str(caught.exception))

    def test_both_identity_and_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.upload('-s', 'server_standard', '-i', 'some/identity', 'pse_path')

        self.assertEqual('User either -i or -s but not both.', str(caught.exception))

    @patch.object(sap.cli.strust.SSLCertStorage, 'upload', autospec=True)
    def test_upload_ask_password(self, fake_upload):
        with patch('sap.cli.strust.getpass', return_value='password') as fake_getpass:
            self.upload('-s', 'server_standard', '--ask-pse-password', 'pse_path')

        fake_getpass.assert_called_once()

        self.assert_password_and_upload(fake_upload, fake_getpass.return_value)

    @patch.object(sap.cli.strust.SSLCertStorage, 'upload', autospec=True)
    def test_upload_ask_password_with_password(self, fake_upload):
        expected_password = 'password'

        with patch('sap.cli.strust.getpass', return_value='not_used_password') as fake_getpass:
            self.upload('-s', 'server_standard', '--ask-pse-password', '--pse-password', expected_password, 'pse_path')

        fake_getpass.assert_not_called()

        self.assert_password_and_upload(fake_upload, expected_password)

    @patch.object(sap.cli.strust.SSLCertStorage, 'upload', autospec=True)
    def test_upload_overwrite(self, fake_upload):
        expected_password = 'password'
        self.upload('-s', 'server_standard', '--pse-password', expected_password, '--overwrite', 'pse_path')

        self.assert_password_and_upload(fake_upload, expected_password, replace=True)

    @patch.object(sap.cli.strust.SSLCertStorage, 'upload', autospec=True)
    def test_storage_ok_upload(self, fake_upload):
        expected_password = 'password'
        self.upload('-s', 'server_standard', '--pse-password', expected_password, 'pse_path')

        self.assert_password_and_upload(fake_upload, expected_password)

    @patch.object(sap.cli.strust.SSLCertStorage, 'upload', autospec=True)
    def test_identity_ok_upload(self, fake_upload):
        expected_password = 'password'
        self.upload('-i', 'SSLS/DFAULT', '--pse-password', expected_password, 'pse_path')

        self.assert_password_and_upload(fake_upload, expected_password)


class TestListIdentities(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()
        self.expected_identities = [{'PSE_CONTEXT': 'context', 'PSE_APPLIC': 'applic', 'SPRSL': 'sprsl',
                                     'PSE_DESCRIPT': 'description'}]

        self.fake_list_identities = self.patch('sap.cli.strust.list_identities')
        self.fake_list_identities.return_value = self.expected_identities

    def list(self, *test_args):
        cmd_args = parse_args('list', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def test_list_identities_json(self):
        output_format = 'JSON'

        self.list('-f', output_format)

        self.fake_list_identities.assert_called_once_with(self.mock_connection)
        self.assertConsoleContents(self.console, f'{self.expected_identities}\n')

    def test_list_identities_human(self):
        output_format = 'HUMAN'

        self.list('-f', output_format)

        self.fake_list_identities.assert_called_once_with(self.mock_connection)
        self.assertConsoleContents(
            self.console,
            stdout=(
                'PSE Context | PSE Application | SPRSL | PSE Description\n'
                '-------------------------------------------------------\n'
                'context     | applic          | sprsl | description    \n'
            )
        )


class TestGetOwnCertificate(PatcherTestCase, ConsoleOutputTestCase):

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)
        assert self.console is not None
        self.patch_console(console=self.console)

        self.mock_connection = Mock()

    def getowncert(self, *test_args):
        cmd_args = parse_args('getowncert', *test_args)
        cmd_args.execute(self.mock_connection, cmd_args)

    def test_storage_invalid(self):
        with self.assertRaises(SystemExit):
            self.getowncert('-s', 'invalidstorage')

    def test_identity_invalid(self):
        identity = 'foo/bar/blah'

        with self.assertRaises(SAPCliError) as caught:
            self.getowncert('-i', identity)

        self.assertEqual(f'Invalid identity format: {identity}', str(caught.exception))

    def test_neither_identity_nor_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.getowncert()

        self.assertEqual('Neither -i nor -s was provided.', str(caught.exception))

    def test_both_identity_and_storage(self):
        with self.assertRaises(SAPCliError) as caught:
            self.getowncert('-s', 'server_standard', '-i', 'some/identity')

        self.assertEqual('User either -i or -s but not both.', str(caught.exception))

    @patch('sap.rfc.strust.SSLCertStorage.get_own_certificate', return_value=b'test_get_own_certificate')
    def test_get_own_certificate(self, fake_get_own_certificate):
        self.getowncert("-s", "client_anonymous")

        fake_get_own_certificate.assert_called_once()

        self.assertConsoleContents(self.console, stdout='''-----BEGIN CERTIFICATE-----
dGVzdF9nZXRfb3duX2NlcnRpZmljYXRl
-----END CERTIFICATE-----
''')



if __name__ == '__main__':
    unittest.main()
