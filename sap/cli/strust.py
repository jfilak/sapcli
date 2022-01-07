"""
Management of X.509 Base64 certificates

Module allows to uploads X.509 Base64 certificates into SAP to enable SSL peer verification
of remote servers as well as to list all configured certificates
"""

import logging
import base64

import sap.cli.core
from sap.errors import SAPCliError
from sap.rfc.strust import (
    SSLCertStorage,
    CLIENT_ANONYMOUS,
    CLIENT_STANDART,
    IDENTITY_MAPPING,
    Identity,
    notify_icm_changed_pse,
    iter_storage_certificates
)
from sap.cli.core import printout


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for strust"""

    def __init__(self):
        super().__init__('strust')


@CommandGroup.argument('paths', type=str, nargs='+',
                       help='a file path containing X.509 Base64 certificate')
@CommandGroup.argument('-l', '--algorithm', type=str, help='R,S,G,H,X - or other if you need, of PSE file', default='R')
@CommandGroup.argument('-k', '--key-length', type=int, default=2048, help='Of PSE file')
@CommandGroup.argument('-d', '--dn', type=str, help='Distinguished Name of PSE file', default=None)
@CommandGroup.argument('-s', '--storage', action='append', default=[],
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, ])
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


@CommandGroup.argument('-s', '--storage', action='append', default=[],
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, ])
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
                       choices=[CLIENT_ANONYMOUS, CLIENT_STANDART, ])
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
        if storage in (CLIENT_ANONYMOUS, CLIENT_STANDART):
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
