"""Simple RFC runner"""

import sys
import json
import pprint

# pylint: disable=import-error
import pyrfc

import sap.cli.core


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

    console = sap.cli.core.get_console()

    try:
        resp = connection.call(args.RFC_FUNCTION_MODULE, **rfc_params)
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
        arg_parser.set_defaults(execute=startrfc)

        # Intentionally return None as this command groups does not support
        # sub-parsers.
