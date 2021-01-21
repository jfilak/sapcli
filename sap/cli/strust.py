"""
Uploads X.509 Base64 certificates into SAP to enable SSL peer verification
of remote servers
"""

import logging

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


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for strust"""

    def __init__(self):
        super().__init__('strust')


@CommandGroup.argument('paths', type=str, nargs='+',
                       help='a file path containing X.509 Base64 certificate')
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
            raise SAPCliError('Invalid identity format')

    ssl_storages = []
    for identity in identities:
        ssl_storage = SSLCertStorage(connection, identity.pse_context, identity.pse_applic)
        ssl_storage.sanitize()
        logging.debug('SSL Storage is OK: %s', ssl_storage)
        ssl_storages.append(ssl_storage)

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
