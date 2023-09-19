"""ADT proxy for ABAP DDIC Data Element"""

from sap.errors import SAPCliError
import sap.adt
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

    console = sap.cli.core.get_console()

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
        sap.cli.object.activate_object_list(activator, ((args.name, dataelement),), count=1)
