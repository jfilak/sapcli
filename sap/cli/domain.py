"""Command line interface for Domain ADT object."""

import json
import sap.adt
import sap.cli.object
import sap.cli.domain_formatter
from sap.errors import SAPCliError


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Domain calls."""

    def __init__(self):
        super().__init__('domain')
        self.define()

    def instance(self, connection, name, args, metadata=None):
        """Creates an instance of the Domain ADT object based on the provided parameters."""

        return sap.adt.Domain(connection, name.upper(), metadata=metadata)

    def define_read(self, commands):
        """Add the argument --format=ABAP|HUMAN to the read command to allow users to choose the output format."""

        read_cmd = super().define_read(commands)
        read_cmd.append_argument(
            '--format',
            choices=['ABAP', 'HUMAN'],
            default='ABAP',
            help='Output format for the Domain details'
        )
        return read_cmd

    def create_object(self, connection, args):
        """Create is not supported for Domains"""
        raise SAPCliError('Create Domain is not supported.')

    def delete_object(self, connection, args):
        """Delete is not supported for Domains"""
        raise SAPCliError('Delete Domain is not supported.')

    def write_object_text(self, connection, args):
        """Write is not supported for Domains"""
        raise SAPCliError('Write Domain is not supported.')

    def read_object_text(self, connection, args):
        """Retrieves the Domain and prints its details"""

        console = args.console_factory()
        obj = self.instance(connection, args.name, args)
        obj.fetch()

        if args.format == 'HUMAN':
            self._print_human_format(console, obj)
        else:  # ABAP format
            self._print_abap_format(console, obj)

    def _print_human_format(self, console, obj):
        """Print Domain details in human-readable format"""

        console.printout(f'Domain: {obj.name}')
        console.printout(f'Description: {obj.description}')
        console.printout(f'Package: {obj.coredata.package_reference.name}')
        console.printout('')
        console.printout('Content:')

        # Delegate to shared formatter
        sap.cli.domain_formatter.format_domain_human(console, obj, indent='    ')

    def _print_abap_format(self, console, obj):
        """Print Domain details in ABAP-compatible JSON format"""

        output = sap.cli.domain_formatter.format_domain_abap(obj)
        console.printout(json.dumps(output, indent=2))
