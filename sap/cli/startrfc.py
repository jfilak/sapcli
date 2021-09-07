"""Simple RFC runner"""

import sys
import json
import pprint

# pylint: disable=import-error
import pyrfc

import sap.cli.core
from sap.errors import SAPCliError


FORMATTERS = {
    'human': pprint.PrettyPrinter(indent=2).pformat,
    'json': json.dumps
}


def startrfc(connection, args):
    """Run whatever RFC enabled Function Module users want"""

    if args.JSON_PARAMETERS == '-':
        rfc_params = json.load(sys.stdin)
    else:
        rfc_params = json.loads(args.JSON_PARAMETERS)

    for param_str in args.param_str or []:
        name_value = param_str.split(':', 1)

        if len(name_value) != 2:
            raise SAPCliError(f'Invalid parameter {param_file}.'
                               ' String parameter must be NAME:VALUE.')

        rfc_params[name_value[0].upper()] = name_value[1]

    for param_int in args.param_int or []:
        name_value = param_int.split(':', 1)

        if len(name_value) != 2:
            raise SAPCliError(f'Invalid parameter {param_file}.'
                               ' Integer parameter must be NAME:VALUE.')

        rfc_params[name_value[0].upper()] = name_value[1]

    for param_file in args.param_file:
        name_path = param_file.split(':', 1)

        if len(name_path) != 2:
            raise SAPCliError(f'Invalid parameter {param_file}.'
                               ' File parameter must be NAME:PATH.')

        try:
            with open(name_path[1], 'rb') as file_obj:
                rfc_params[name_path[0].upper()] = file_obj.read()
        except OSError as ex:
            raise SAPCliError(f'Cannot read the file param {param_file}: {str(ex)}')

    console = sap.cli.core.get_console()

    try:
        resp = connection.call(args.RFC_FUNCTION_MODULE.upper(), **rfc_params)
    # pylint: disable=protected-access
    except pyrfc._exception.RFCLibError as ex:
        console.printerr(f'{args.RFC_FUNCTION_MODULE} failed:')
        console.printerr(str(ex))
        return 1
    else:
        console.printout(FORMATTERS[args.output](resp))
        return 0


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for calling RFC Function Modules"""

    def __init__(self):
        super().__init__('startrfc')

    def install_parser(self, arg_parser):
        """Just use the command group"""

        arg_parser.add_argument('-o', '--output', choices=FORMATTERS.keys(), default=next(iter(FORMATTERS.keys())),
                                help='Output format')
        arg_parser.add_argument('RFC_FUNCTION_MODULE')
        arg_parser.add_argument('JSON_PARAMETERS', nargs='?', default='{}',
                                help='JSON string or - for reading the parameters from stdin')
        arg_parser.add_argument('-I', '--param-int', type=int, action='append',
                                help='For number parameters PARAM_NAME:VALUE')
        arg_parser.add_argument('-S', '--param-str', type=str, action='append',
                                help='For string parameters PARAM_NAME:VALUE')
        arg_parser.add_argument('-F', '--param-file', type=str, action='append',
                                help='For parameters containing an entire file. Pass it in the form "PARAM_NAME:FILE_PATH"')
        arg_parser.set_defaults(execute=startrfc)

        # Intentionally return None as this command groups does not support
        # sub-parsers.
