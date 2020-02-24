"""Simple RFC runner"""

import sys
import json

import sap.cli.core


def startrfc(connection, args):
    """Run whatever RFC enabled Function Module users want"""

    if args.JSON_PARAMETERS == '-':
        rfc_params = json.load(sys.stdin)
    else:
        rfc_params = json.loads(args.JSON_PARAMETERS)

    resp = connection.call(args.RFC_FUNCTION_MODULE, **rfc_params)

    sap.cli.core.printout(resp)

    return 0


class CommandGroup(sap.cli.core.CommandGroup):
    """Commands for exporting ADT objects"""

    def __init__(self):
        super(CommandGroup, self).__init__('startrfc')

    def install_parser(self, arg_parser):
        """Just use the command group"""

        arg_parser.add_argument('RFC_FUNCTION_MODULE')
        arg_parser.add_argument('JSON_PARAMETERS', nargs='?', default='{}',
                                help='JSON string or - for reading the parameters from stdin')
        arg_parser.set_defaults(execute=startrfc)

        # Intentionally return None as this command groups does not support
        # sub-parsers.
