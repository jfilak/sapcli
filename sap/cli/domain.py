"""Command line interface for Domain ADT object."""

import json
import sap.adt
import sap.cli.object
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

        # Type Information
        console.printout('    Type Information:')
        console.printout(f'        Datatype: {obj.content.type_information.datatype}')
        length = int(obj.content.type_information.length) if obj.content.type_information.length else 0
        console.printout(f'        Length: {length}')

        # Output Information
        console.printout('    Output Information:')
        out_length = int(obj.content.output_information.length) if obj.content.output_information.length else 0
        console.printout(f'        Length: {out_length}')

        # Value Information
        console.printout('    Value Information:')
        if obj.content.value_information.value_table_ref and obj.content.value_information.value_table_ref.name:
            console.printout(f'        Table Reference: {obj.content.value_information.value_table_ref.name}')

        if obj.content.value_information.fix_values:
            console.printout('        Fix Values:')
            for fix_value in obj.content.value_information.fix_values:
                console.printout(f'            - {fix_value.low}: {fix_value.text}')

    def _print_abap_format(self, console, obj):
        """Print Domain details in ABAP-compatible JSON format"""

        output = {
            'formatVersion': '1',
            'header': {
                'description': obj.description or '',
                'originalLanguage': obj._metadata.master_language.lower() if obj._metadata.master_language else ''
            },
            'format': {
                'dataType': obj.content.type_information.datatype or '',
                'length': int(obj.content.type_information.length) if obj.content.type_information.length else 0
            },
            'outputCharacteristics': {
                'length': int(obj.content.output_information.length) if obj.content.output_information.length else 0
            }
        }

        # Add fixed values if they exist
        if obj.content.value_information.fix_values:
            output['fixedValues'] = []
            for fix_value in obj.content.value_information.fix_values:
                output['fixedValues'].append({
                    'fixedValue': fix_value.low or '',
                    'description': fix_value.text or ''
                })

        console.printout(json.dumps(output, indent=2))
