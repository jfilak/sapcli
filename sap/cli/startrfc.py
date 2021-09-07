"""Simple RFC runner"""

import sys
import json
import pprint

# pylint: disable=import-error
import pyrfc

import sap.cli.core
from sap.cli.core import InvalidCommandLineError


FORMATTERS = {
    'human': pprint.PrettyPrinter(indent=2).pformat,
    'json': json.dumps
}


def _parse_args_rfc_param(param_type_name, args_rfc_param, type_conv=None):
    name_value = args_rfc_param.split(':', 1)

    if len(name_value) != 2:
        raise InvalidCommandLineError(
            f'Invalid parameter {args_rfc_param}.'
            f' {param_type_name} parameter must be NAME:VALUE.')

    name_value[0] = name_value[0].upper()

    if type_conv is None:
        return name_value

    try:
        return (name_value[0], type_conv(name_value[1]))
    except ValueError as ex:
        raise InvalidCommandLineError(
            f'Cannot process the parameter {args_rfc_param}: {str(ex)}') from ex


def _process_args_rfc_params(args_rfc_params, call_rfc_params, param_type_name, type_conv=None):
    if not args_rfc_params:
        return

    for param_str in args_rfc_params:
        name_value = _parse_args_rfc_param(param_type_name,
                                           param_str,
                                           type_conv=type_conv)
        call_rfc_params[name_value[0]] = name_value[1]


def _read_file(args_rfc_param_value):
    try:
        with open(args_rfc_param_value, 'rb') as file_obj:
            return file_obj.read()
    except OSError as ex:
        raise ValueError(
            f'Failed to open/read: {str(ex)}') from ex


def _get_call_rfc_params_from_args(args):
    if args.JSON_PARAMETERS == '-':
        rfc_params = json.load(sys.stdin)
    else:
        rfc_params = json.loads(args.JSON_PARAMETERS)

    _process_args_rfc_params(args.param_string, rfc_params, 'String')
    _process_args_rfc_params(args.param_integer, rfc_params, 'Integer', type_conv=int)
    _process_args_rfc_params(args.param_file, rfc_params, 'File', type_conv=_read_file)

    return rfc_params


def startrfc(connection, args):
    """Run whatever RFC enabled Function Module users want"""

    console = sap.cli.core.get_console()

    try:
        rfc_params = _get_call_rfc_params_from_args(args)
    except InvalidCommandLineError as ex:
        console.printerr('Error: ' + str(ex))
        console.printerr('Exiting with error code because of invalid command line parameters.')
        return 1

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
        arg_parser.add_argument('-I', '--param-integer', type=str, action='append',
                                help='For number parameters PARAM_NAME:VALUE')
        arg_parser.add_argument('-S', '--param-string', type=str, action='append',
                                help='For string parameters PARAM_NAME:VALUE')
        arg_parser.add_argument('-F', '--param-file', type=str, action='append',
                                help='For parameters containing an entire file.'
                                     ' Pass it in the form "PARAM_NAME:FILE_PATH"')
        arg_parser.set_defaults(execute=startrfc)

        # Intentionally return None as this command groups does not support
        # sub-parsers.
