"""
Management of X.509 Base64 certificates

Module allows to uploads X.509 Base64 certificates into SAP to enable SSL peer verification
of remote servers as well as to list all configured certificates
"""

import logging
import base64
import sys
import warnings

from getpass import getpass

import sap.cli.core
from sap.errors import SAPCliError
from sap.rfc.strust import (
    PKCResponseABAPData,
    SSLCertStorage,
    CLIENT_ANONYMOUS,
    CLIENT_STANDART,
    CLIENT_STANDARD,
    SERVER_STANDARD,
    IDENTITY_MAPPING,
    PSE_ALGORITHM_MAPPING,
    Identity,
    notify_icm_changed_pse,
    iter_storage_certificates,
    list_identities
)
from sap.cli.core import (
    printout,
    get_stdin
)
from sap.cli.helpers import TableWriter


PEM_HEADER = '-----BEGIN CERTIFICATE-----'
PEM_FOOTER = '-----END CERTIFICATE-----'


def storage_deprecation_warning():
    """Raises Deprecation warning when 'client_standart' is used.
    """

    warnings.warn(message='Storage "client_standart" is deprecated and will be removed. Use "client_standard" instead.',
                  category=DeprecationWarning)


def _get_ssl_storage_from_args(connection, args):

    identity = None

    if args.storage and args.identity:
        raise SAPCliError('User either -i or -s but not both.')

    if args.storage:
        if args.storage == CLIENT_STANDART:
            storage_deprecation_warning()

        identity = IDENTITY_MAPPING[args.storage]

    if args.identity:
        try:
            identity = Identity(*args.identity.split('/'))
        except (ValueError, TypeError):
            # pylint: disable=raise-missing-from
            raise SAPCliError(f'Invalid identity format: {args.identity}')

    if identity is None:
        raise SAPCliError('Neither -i nor -s was provided.')

    return SSLCertStorage(connection, identity.pse_context, identity.pse_applic)


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for strust"""

    def __init__(self):
        super().__init__('strust')


@CommandGroup.argument('-f', '--format', choices=['HUMAN', 'JSON'], default='HUMAN')
@CommandGroup.command(cmd_name='list')
def listidentities(connection, args):
    """List existing STRUST identities.
    """

    identities = list_identities(connection)

    if args.format == 'JSON':
        printout(identities)
    else:
        console = sap.cli.core.get_console()
        columns = TableWriter.Columns()
        columns('PSE_CONTEXT', 'PSE Context')('PSE_APPLIC', 'PSE Application')('SPRSL', 'SPRSL')
        columns('PSE_DESCRIPT', 'PSE Description')
        columns = columns.done()

        TableWriter(identities, columns).printout(console)


@CommandGroup.argument('--overwrite', help='Overwrite the existing PSE file', action='store_true', default=False)
@CommandGroup.argument('-l', '--algorithm', type=str, help='PSE file Encryption algorithm', default='RSAwithSHA256',
                       choices=PSE_ALGORITHM_MAPPING.keys())
@CommandGroup.argument('-k', '--key-length', type=int, default=2048, help='Of PSE file')
@CommandGroup.argument('--dn', type=str,
                       help='Distinguished Name (LDAP DN) of PSE file if no other system info provided')
@CommandGroup.argument('-s', '--storage', default=None, help='Mutually exclusive with the option -i',
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', default=None, help='Mutually exclusive with the option -s',)
@CommandGroup.command()
def createpse(connection, args):
    """Creates the specified PSE file.
    """

    ssl_storage = _get_ssl_storage_from_args(connection, args)

    if ssl_storage.exists() and not args.overwrite:
        sap.cli.core.printout(f'Nothing to do - the PSE {ssl_storage.identity} already exists')
        return 0

    ssl_storage.create(
        alg=PSE_ALGORITHM_MAPPING[args.algorithm],
        keylen=args.key_length,
        dn=args.dn,
        replace=args.overwrite
    )

    notify_icm_changed_pse(connection)

    sap.cli.core.printout(f'Done - the PSE {ssl_storage.identity} has been created')
    return 0


@CommandGroup.argument('-s', '--storage', default=None, help='Mutually exclusive with the option -i',
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', default=None, help='Mutually exclusive with the option -s',)
@CommandGroup.command()
def removepse(connection, args):
    """Prints out Certificate Signing Request
    """

    ssl_storage = _get_ssl_storage_from_args(connection, args)

    ssl_storage.remove()

    return 0


@CommandGroup.argument('-s', '--storage', default=None, help='Mutually exclusive with the option -i',
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', default=None, help='Mutually exclusive with the option -s',)
@CommandGroup.command()
def getcsr(connection, args):
    """Prints out Certificate Signing Request
    """

    ssl_storage = _get_ssl_storage_from_args(connection, args)

    csr = ssl_storage.get_csr()

    sap.cli.core.printout(csr)
    return 0


@CommandGroup.argument('path', type=str, nargs='+',
                       help='a file path containing X.509 Base64 certificate and issuer certificates if needed')
@CommandGroup.argument('-s', '--storage', default=None, help='Mutually exclusive with the option -i',
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', default=None, help='Mutually exclusive with the option -s',)
@CommandGroup.command()
def putpkc(connection, args):
    """Uploads Identity Certificate
    """

    pkc_response = PKCResponseABAPData()

    for cert_path in args.path:
        if cert_path == '-':
            pkc_response.add_file(sys.stdin)
        else:
            with open(cert_path, 'rb') as cert_file:
                pkc_response.add_file(cert_file)

    if pkc_response.data == ['']:
        raise SAPCliError('Unable to load certificate from the PATH')

    ssl_storage = _get_ssl_storage_from_args(connection, args)
    ssl_storage.put_identity_cert(pkc_response)

    return 0


@CommandGroup.argument('path', type=str,
                       help='a PSE in the form of PKCS#12 - *.pfx')
@CommandGroup.argument('--overwrite', help='Overwrite the existing PSE file', action='store_true', default=False)
@CommandGroup.argument('--ask-pse-password', help='Ask for PSE export password', action='store_true', default=False)
@CommandGroup.argument('--pse-password', help='PSE export password', default=None)
@CommandGroup.argument('-s', '--storage', default=None, help='Mutually exclusive with the option -i',
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', default=None, help='Mutually exclusive with the option -s',)
@CommandGroup.command()
def upload(connection, args):
    """Uploads complete PSE file
    """

    with open(args.path, 'rb') as pse_file:
        data = pse_file.read()

    pse_password = args.pse_password
    if not pse_password and args.ask_pse_password:
        pse_password = getpass('PSE Export password')

    ssl_storage = _get_ssl_storage_from_args(connection, args)

    logging.info('Uploading PSE ... ')
    ssl_storage.upload(
        data,
        replace=args.overwrite,
        password=pse_password
    )

    logging.info('Notifying ICM ... ')
    notify_icm_changed_pse(connection)

    return 0


@CommandGroup.argument('paths', type=str, nargs='+',
                       help='a file path containing X.509 Base64 certificate or - to read it from STDIN')
@CommandGroup.argument('-l', '--algorithm', type=str, help='R,S,G,H,X - or other if you need, of PSE file', default='R')
@CommandGroup.argument('-k', '--key-length', type=int, default=2048, help='Of PSE file')
@CommandGroup.argument('-d', '--dn', type=str, help='Distinguished Name of PSE file', default=None)
@CommandGroup.argument('-s', '--storage', action='append', default=[],
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', action='append', default=[])
@CommandGroup.command()
def putcertificate(connection, args):
    """Uploads X.509 Base64 certificates into SAP to enable SSL peer verification
       of remote servers

        Exceptions:
            - SAPCliError:
                - when the given storage does not belong to the storage white list
                - when identity argument has invalid format
    """

    ssl_storages = ssl_storages_from_arguments(connection, args)

    for ssl_storage in ssl_storages:

        if not ssl_storage.exists():
            ssl_storage.create(
                alg=args.algorithm,
                keylen=args.key_length,
                dn=args.dn
            )

        logging.debug('SSL Storage is OK: %s', ssl_storage)

    if args.paths[0] == '-':
        certificates = read_certificates()

        for ssl_storage in ssl_storages:
            for idx, cert_content in enumerate(certificates):
                logging.info('Adding the certificate: #%d to %s', idx, ssl_storage)
                logging.info(ssl_storage.put_certificate(cert_content.encode()))
    else:
        for file_path in args.paths:
            logging.info('Processing the file: %s', file_path)
            with open(file_path, 'rb') as cert_file:
                cert_contents = cert_file.read()
                for ssl_storage in ssl_storages:
                    logging.info('Adding the file: %s to %s', file_path, ssl_storage)
                    logging.info(ssl_storage.put_certificate(cert_contents))

    logging.info('Notifying ICM ... ')
    notify_icm_changed_pse(connection)

    for updated_storage in ssl_storages:
        logging.info('Certificates of %s:', str(updated_storage))

        for cert in iter_storage_certificates(updated_storage):
            logging.info('* %s', cert['EV_SUBJECT'])


@CommandGroup.argument('-s', '--storage', default=None, help='Mutually exclusive with the option -i',
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', default=None, help='Mutually exclusive with the option -s',)
@CommandGroup.command()
def getowncert(connection, args):
    """Prints out PEM encoded X.509 certificate of the requested PSE.
    """

    ssl_storage = _get_ssl_storage_from_args(connection, args)

    cert = ssl_storage.get_own_certificate()
    cert_x509 = base64.b64encode(cert).decode('ascii')

    printout(PEM_HEADER)
    printout(cert_x509)
    printout(PEM_FOOTER)


@CommandGroup.argument('-s', '--storage', action='append', default=[],
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', action='append', default=[])
@CommandGroup.command()
def listcertificates(connection, args):
    """Lists X.509 Base64 certificates currently installed in SAP system

        Exceptions:
            - SAPCliError:
                - when the given storage does not belong to the storage white list
                - when identity argument has invalid format
    """

    ssl_storages = ssl_storages_from_arguments(connection, args)

    for ssl_storage in ssl_storages:

        if not ssl_storage.exists():
            raise SAPCliError(f'Storage for identity {ssl_storage.identity} does not exist')

        for cert in ssl_storage.get_certificates():

            cert = ssl_storage.parse_certificate(cert)
            printout('*', cert['EV_SUBJECT'])


@CommandGroup.argument('-s', '--storage', action='append', default=[],
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD, SERVER_STANDARD, ])
@CommandGroup.argument('-i', '--identity', action='append', default=[])
@CommandGroup.command()
def dumpcertificates(connection, args):
    """Dumps X.509 Base64 certificates currently installed in SAP system

        Exceptions:
            - SAPCliError:
                - when the given storage does not belong to the storage white list
                - when identity argument has invalid format
    """

    ssl_storages = ssl_storages_from_arguments(connection, args)

    for ssl_storage in ssl_storages:

        if not ssl_storage.exists():
            raise SAPCliError(f'Storage for identity {ssl_storage.identity} does not exist')

        for cert in ssl_storage.get_certificates():

            c_b64 = base64.b64encode(cert)

            printout('-----BEGIN CERTIFICATE-----')
            printout(c_b64.decode('ascii'))
            printout('-----END CERTIFICATE-----')


def ssl_storages_from_arguments(connection, args):
    """Helper function to build list of storages from cli arguments"""

    identities = []

    for storage in args.storage:
        if storage in (CLIENT_ANONYMOUS, CLIENT_STANDART, CLIENT_STANDARD):
            if storage == CLIENT_STANDART:
                storage_deprecation_warning()

            identities.append(IDENTITY_MAPPING[storage])
        else:
            raise SAPCliError(f'Unknown storage: {storage}')

    for identity in args.identity:
        try:
            identities.append(Identity(*identity.split('/')))
        except (ValueError, TypeError):
            # pylint: disable=raise-missing-from
            raise SAPCliError(f'Invalid identity format: {identity}')

    ssl_storages = []
    for identity in identities:
        ssl_storage = SSLCertStorage(connection, identity.pse_context, identity.pse_applic)
        ssl_storages.append(ssl_storage)

    return ssl_storages


def read_certificates():
    """Helper function to build list of certificates from stdin"""

    cert_input = get_stdin().read()

    return [crt.strip() + '\n' + PEM_FOOTER + '\n' for crt in cert_input.split(PEM_FOOTER) if len(crt.strip()) > 0]
