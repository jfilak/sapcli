"""Command line interface for Authorization Field ADT object."""

import sap.adt
import sap.cli.object
from sap.errors import SAPCliError


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.AuthorizationField calls."""

    def __init__(self):
        super().__init__('authorizationfield')
        self.define()

    def instance(self, connection, name, args, metadata=None):
        """Creates an instance of the Authorization Field ADT object based on the provided parameters."""

        return sap.adt.AuthorizationField(connection, name.upper(), metadata=metadata)

    def define_read(self, commands):
        """Add the argument --format=ABAP|HUMAN to the read command to allow users to choose the output format."""

        read_cmd = super().define_read(commands)
        read_cmd.append_argument(
            '--format',
            choices=['ABAP', 'HUMAN'],
            default='HUMAN',
            help='Output format for the Authorization Field details'
        )
        return read_cmd

    def create_object(self, connection, args):
        """Create is not supported for Authorization Fields"""
        raise SAPCliError('Create Authorization Field is not implemented yet.')

    def delete_object(self, connection, args):
        """Delete is not supported for Authorization Fields"""
        raise SAPCliError('Delete Authorization Field is not implemented yet.')

    def write_object_text(self, connection, args):
        """Write is not supported for Authorization Fields"""
        raise SAPCliError('Write Authorization Field is not implemented yet.')

    def read_object_text(self, connection, args):
        """Retrieves the Authorization Field and prints its details"""

        console = args.console_factory()
        obj = self.instance(connection, args.name, args)
        obj.fetch()

        if args.format == 'ABAP':
            raise SAPCliError('ABAP format output is not implemented yet. Please use --format=HUMAN for now.')

        # Print the details of the Authorization Field in a human-readable format
        console.printout(f'Authorization Field: {obj.name}')
        console.printout(f'Description: {obj.description}')
        console.printout(f'Package: {obj.reference.name}')
        console.printout(f'Responsible: {obj.responsible}')
        console.printout(f'Master Language: {obj.master_language}')
        console.printout('')
        console.printout('Content:')
        console.printout(f'  Field Name: {obj.content.field_name or ""}')
        console.printout(f'  Roll Name: {obj.content.roll_name or ""}')
        console.printout(f'  Check Table: {obj.content.check_table or ""}')
        console.printout(f'  Exit FB: {obj.content.exit_fb or ""}')
        console.printout(f'  Domain Name: {obj.content.domname or ""}')
        console.printout(f'  Output Length: {obj.content.outputlen or ""}')
        console.printout(f'  Conversion Exit: {obj.content.convexit or ""}')
        console.printout(f'  Search: {obj.content.search or ""}')
        console.printout(f'  Object Exit: {obj.content.objexit or ""}')
        console.printout(f'  Org Level Info: {obj.content.orglvlinfo or ""}')
        console.printout(f'  Collective Search Help: {obj.content.col_searchhelp or ""}')
        console.printout(f'  Collective Search Help Name: {obj.content.col_searchhelp_name or ""}')
        console.printout(f'  Collective Search Help Description: {obj.content.col_searchhelp_descr or ""}')
