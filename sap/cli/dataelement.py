"""ADT proxy for ABAP DDIC Data Element"""

import json
from sap.errors import SAPCliError
import sap.adt
import sap.adt.domain
import sap.cli.domain_formatter
from sap.adt.dataelement import DataElementValidationIssues
from sap.adt.errors import ExceptionResourceAlreadyExists
import sap.cli.object
import sap.cli.wb
import sap.cli.core


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.DataElement methods
       calls.
    """

    def __init__(self):
        super().__init__('dataelement')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.DataElement(connection, name.upper(), package=package, metadata=metadata)

    def define_read(self, commands):
        """Add the argument --format=ABAP|HUMAN to the read command to allow users to choose the output format."""

        read_cmd = super().define_read(commands)
        read_cmd.append_argument(
            '--format',
            choices=['ABAP', 'HUMAN'],
            default='HUMAN',
            help='Output format for the Data Element details'
        )
        return read_cmd

    def read_object_text(self, connection, args):
        """Retrieves the Data Element and prints its details"""

        console = args.console_factory()
        obj = self.instance(connection, args.name, args)
        obj.fetch()

        if args.format == 'ABAP':
            self._print_abap_format(console, obj)
        else:
            # Print the details of the Data Element in a human-readable format
            self._print_human_format(console, obj, connection)

    def _print_human_format(self, console, obj, connection):
        """Print Data Element details in human-readable format"""

        console.printout(f'Data Element: {obj.name}')
        console.printout(f'Description: {obj.description}')
        console.printout(f'Package: {obj.coredata.package_reference.name}')
        console.printout('')
        console.printout('Definition:')

        # Type information with new nested structure
        console.printout('  Type')
        console.printout(f'    Kind: {obj.definition.typ or ""}')

        if obj.definition.typ == 'domain':
            console.printout(f'    Name: {obj.definition.typ_name or ""}')

            # Always fetch and display domain details for domain-based elements in HUMAN format
            if obj.definition.typ_name:
                self._print_domain_inline(connection, obj.definition.typ_name, console)
        elif obj.definition.typ == 'predefinedAbapType':
            console.printout(f'    Name: {obj.definition.data_type or ""}')
            console.printout(f'    Length: {obj.definition.data_type_length or "0"}')
            console.printout(f'    Decimals: {obj.definition.data_type_decimals or "0"}')

        # Labels
        console.printout('')
        console.printout('  Labels:')
        console.printout(f'    Short: {obj.definition.label_short or ""}')
        console.printout(f'    Medium: {obj.definition.label_medium or ""}')
        console.printout(f'    Long: {obj.definition.label_long or ""}')
        console.printout(f'    Heading: {obj.definition.label_heading or ""}')

        # Additional properties
        if obj.definition.search_help:
            console.printout('')
            console.printout('  Additional Properties:')
            console.printout(f'    Search Help: {obj.definition.search_help}')
            if obj.definition.search_help_parameter:
                console.printout(f'    Search Help Parameter: {obj.definition.search_help_parameter}')

    def _print_abap_format(self, console, obj):
        """Print Data Element details in ABAP-compatible JSON format"""

        output = {
            'formatVersion': '1',
            'header': {
                'description': obj.description or '',
                'originalLanguage': obj.coredata.master_language.lower()
                if obj.coredata.master_language else ''
            },
            'definition': {
                'typeKind': obj.definition.typ or ''
            }
        }

        # Add type-specific information
        if obj.definition.typ == 'domain':
            output['definition']['domainName'] = obj.definition.typ_name or ''
        elif obj.definition.typ == 'predefinedAbapType':
            output['definition']['dataType'] = obj.definition.data_type or ''
            output['definition']['length'] = int(obj.definition.data_type_length) \
                if obj.definition.data_type_length else 0
            output['definition']['decimals'] = int(obj.definition.data_type_decimals) \
                if obj.definition.data_type_decimals else 0

        # Add labels
        output['labels'] = {
            'short': obj.definition.label_short or '',
            'medium': obj.definition.label_medium or '',
            'long': obj.definition.label_long or '',
            'heading': obj.definition.label_heading or ''
        }

        # Add search help if present
        if obj.definition.search_help:
            output['searchHelp'] = {
                'name': obj.definition.search_help,
                'parameter': obj.definition.search_help_parameter or ''
            }

        console.printout(json.dumps(output, indent=2))

    def _print_domain_inline(self, connection, domain_name, console):
        """Print domain information inline under Type section

        Args:
            connection: ADT connection
            domain_name: Name of domain to fetch
            console: Console for output
        """

        domain = sap.adt.Domain(connection, domain_name.upper())
        try:
            domain.fetch()
        except SAPCliError as ex:
            console.printerr(f'    Warning: Could not fetch domain {domain_name}: {str(ex)}')
            return

        console.printout(f'    Description: {domain.description}')
        console.printout('')

        # Use shared formatter with indentation to align under Type section
        sap.cli.domain_formatter.format_domain_human(console, domain, indent='    ')


@CommandGroup.argument_corrnr()
@CommandGroup.argument('--no-error-existing', action='store_true', default=False,
                       help='Do not fail if data element already exists')
@CommandGroup.argument('-a', '--activate', action='store_true', default=False, help='Activate after modification')
@CommandGroup.argument('-t', '--type', required=True, choices=['domain', 'predefinedAbapType'],
                       type=str, help='Type kind')
@CommandGroup.argument('-d', '--domain_name', default=None, type=str, help='Domain name')
@CommandGroup.argument('-dt', '--data_type', default=None, type=str, help='Data type')
@CommandGroup.argument('-dtl', '--data_type_length', default='0', type=str, help='Data type length')
@CommandGroup.argument('-dtd', '--data_type_decimals', default='0', type=str, help='Data type decimals')
@CommandGroup.argument('-ls', '--label_short', default='', type=str, help='Short label')
@CommandGroup.argument('-lm', '--label_medium', default='', type=str, help='Medium label')
@CommandGroup.argument('-ll', '--label_long', default='', type=str, help='Long label')
@CommandGroup.argument('-lh', '--label_heading', default='', type=str, help='Heading label')
@CommandGroup.argument('package', help='Package assignment')
@CommandGroup.argument('description', help='Data element description')
@CommandGroup.argument('name', help='Data element name')
@CommandGroup.command()
# pylint: disable=too-many-branches
def define(connection, args):
    """Changes attributes of the given Data Element"""

    console = args.console_factory()

    metadata = sap.adt.ADTCoreData(language='EN', master_language='EN', responsible=connection.user,
                                   description=args.description)

    dataelement = sap.adt.DataElement(connection, args.name.upper(), args.package, metadata=metadata)

    # Create Data Element
    console.printout(f'Creating data element {args.name}')
    try:
        dataelement.create(args.corrnr)
    except ExceptionResourceAlreadyExists as error:
        # Date Element already exists
        console.printout(f'Data element {args.name} already exists')
        if not args.no_error_existing:
            raise error

    # Fetch data element's content
    dataelement.fetch()

    if hasattr(args, 'type'):
        dataelement.set_type(args.type)

    if hasattr(args, 'domain_name'):
        dataelement.set_type_name(args.domain_name)

    if hasattr(args, 'data_type'):
        dataelement.set_data_type(args.data_type)

    if hasattr(args, 'data_type_length'):
        dataelement.set_data_type_length(args.data_type_length)

    if hasattr(args, 'data_type_decimals'):
        dataelement.set_data_type_decimals(args.data_type_decimals)

    if hasattr(args, 'label_short'):
        dataelement.set_label_short(args.label_short)

    if hasattr(args, 'label_medium'):
        dataelement.set_label_medium(args.label_medium)

    if hasattr(args, 'label_long'):
        dataelement.set_label_long(args.label_long)

    if hasattr(args, 'label_heading'):
        dataelement.set_label_heading(args.label_heading)

    dataelement.normalize()

    validation_issue_key = dataelement.validate()

    match validation_issue_key:
        case DataElementValidationIssues.MISSING_DOMAIN_NAME:
            console.printerr(
                'Domain name must be provided (--domain_name) if the type (--type) is "domain"')

        case DataElementValidationIssues.MISSING_TYPE_NAME:
            console.printerr(
                'Data type name must be provided (--data_type) if the type (--type) is "predefinedAbapType"')

        case DataElementValidationIssues.NO_ISSUE:
            pass

        case _:
            raise SAPCliError(
                f'BUG: please report a forgotten case DataElementValidationIssues({validation_issue_key})')

    if validation_issue_key != DataElementValidationIssues.NO_ISSUE:
        return 1

    # Push Data Element changes
    console.printout(f'Data element {args.name} setup performed')
    with dataelement.open_editor(corrnr=args.corrnr) as editor:
        editor.push()

    # Activate Data Element
    if args.activate:
        console.printout(f'Data element {args.name} activation performed')
        activator = sap.cli.wb.ObjectActivationWorker()
        sap.cli.object.activate_object_list(activator, ((args.name, dataelement),), 1, console)
