"""Simple RFC runner"""

import sys
import json
import pprint
import base64
from os import path

import sap.cli.core
from sap.cli.core import InvalidCommandLineError
import sap.rfc.bapi
from sap.rfc.core import try_pyrfc_exception_type


class BytesBase64Encoder(json.JSONEncoder):
    """Bytes to Base64 encoder"""

    def default(self, o):
        if isinstance(o, bytes):
            return base64.b64encode(o).decode('ascii')

        return json.JSONEncoder.default(self, o)


def json_format(obj):
    """Serialize obj to JSON formatted str"""

    return json.dumps(obj, cls=BytesBase64Encoder)


FORMATTERS = {
    'human': pprint.PrettyPrinter(indent=2).pformat,
    'json': json_format
}

RESULT_CHECKER_RAW = 'raw'
RESULT_CHECKER_BAPI = 'bapi'
RESULT_CHECKERS = [RESULT_CHECKER_RAW, RESULT_CHECKER_BAPI]


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
    # pylint: disable=too-many-return-statements

    console = args.console_factory()

    # we required new file to avoid security problems if executed
    # under a user with escalated privileges
    if args.response_file and path.exists(args.response_file):
        console.printerr(f'The response file must not exist: {args.response_file}')
        return 1

    try:
        rfc_params = _get_call_rfc_params_from_args(args)
    except InvalidCommandLineError as ex:
        console.printerr('Error: ' + str(ex))
        console.printerr('Exiting with error code because of invalid command line parameters.')
        return 1

    pyrfc_exception_type = try_pyrfc_exception_type()

    try:
        resp = connection.call(args.RFC_FUNCTION_MODULE.upper(), **rfc_params)
    # pylint: disable=protected-access
    except pyrfc_exception_type as ex:
        console.printerr(f'{args.RFC_FUNCTION_MODULE} failed:')
        console.printerr(str(ex))
        return 1

    try:
        # rfc call passed, it is time for analysis of the returned response
        response_formatted = FORMATTERS[args.output](resp)
    except TypeError as exc:
        console.printerr('Could not JSON serialize call response.')
        console.printerr(exc)
        return 1

    # if the response file is given
    if args.response_file:
        try:
            # try to dump the formatted response into a completely new file
            with open(args.response_file, 'x', encoding='utf-8') as file_obj:
                file_obj.write(response_formatted)
        except FileExistsError:
            console.printerr(f'Could not create and open the file: {args.response_file}')
            console.printerr(response_formatted)
            return 1
        except (OSError, IOError) as ex:
            console.printerr(f'Could not open the file {args.response_file}: {str(ex)}')
            console.printerr(response_formatted)
            return 1

    # if bapi checker  is enabled
    if args.result_checker == RESULT_CHECKER_BAPI:
        # first check of the response to be sure it fits to BAPI response structure
        try:
            return_value = resp['RETURN']
        except KeyError:
            console.printerr(f"It was requested to evaluate response from {args.RFC_FUNCTION_MODULE} "
                             "as bapi result, but response does not contain required key RETURN. "
                             "Raw response:")
            console.printerr(response_formatted)
            return 1

        # try to parse response as "bapi return value"
        try:
            bapi_return = sap.rfc.bapi.BAPIReturn(return_value)
        except ValueError as ex:
            console.printerr(f'Parsing BAPI response returned from {args.RFC_FUNCTION_MODULE} failed:')
            console.printerr(str(ex))
            console.printerr("Raw response:")
            console.printerr(response_formatted)
            return 1

        # Print out all messages because we can have more Errors
        # and Non-Error messages can help reades to understand
        # error messages better.
        all_message_lines = "\n".join(bapi_return.message_lines())

        if bapi_return.is_error:
            console.printerr(all_message_lines)
            return 1

        console.printout(all_message_lines)
        return 0

    # if result_checker == RESULT_CHECKER_RAW:
    #   IOW no response analysis performed by 'sapcli startrfc'
    console.printout(response_formatted)
    return 0


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for calling RFC Function Modules"""

    def __init__(self):
        super().__init__('startrfc')

    def install_parser(self, arg_parser):
        """Just use the command group"""

        arg_parser.add_argument('-o', '--output', choices=FORMATTERS.keys(), default=next(iter(FORMATTERS.keys())),
                                help='Output format')
        arg_parser.add_argument('-R', '--response-file', type=str, default=None,
                                help=('Dump the entire response to the given file ',
                                      'which must not exist. The content format '
                                      'matches the paramter --output.'))
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
        arg_parser.add_argument('-c', '--result-checker', choices=RESULT_CHECKERS, default=RESULT_CHECKER_RAW,
                                help='Result checker')
        arg_parser.set_defaults(execute=startrfc)

        # Intentionally return None as this command groups does not support
        # sub-parsers.
