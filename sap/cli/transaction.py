"""ADT proxy for ABAP Transaction"""

import sap.adt
import sap.cli.object
import sap.cli.wb
from sap.errors import SAPCliError


def _collect_optional_args(args, arg_names):
    """Collects non-None CLI args into a dict using the given name mapping.

       arg_names is a dict mapping CLI arg name -> factory kwarg name.
    """

    result = {}
    for cli_name, kwarg_name in arg_names.items():
        value = getattr(args, cli_name, None)
        if value is not None and value is not False:
            result[kwarg_name] = value
    return result


_REQUIRED_ARGS_MAP = {
    'report': [('report_name', '--report-name'), ('report_dynnr', '--report-dynnr')],
    'parameter': [('parent_transaction', '--parent-transaction')],
    'dialog': [('program_name', '--program-name'), ('program_dynnr', '--program-dynnr')],
    'oo': [('class_name', '--class-name'), ('method_name', '--method-name')],
    'variant': [('parent_transaction', '--parent-transaction')],
}


def _validate_create_args(args):
    """Validates that required type-specific flags are provided for the given transaction type."""

    required = _REQUIRED_ARGS_MAP.get(args.type, [])
    missing = [flag for attr, flag in required if not getattr(args, attr, None)]

    if missing:
        raise SAPCliError(
            f'Missing required flag(s) for type \'{args.type}\': {", ".join(missing)}'
        )


_TYPE_ARGS_MAP = {
    'report': {
        'report_name': 'report_name',
        'report_dynnr': 'report_dynnr',
        'report_variant_name': 'report_variant_name',
    },
    'parameter': {
        'parent_transaction': 'par_parent_transaction_code',
    },
    'dialog': {
        'program_name': 'program_name',
        'program_dynnr': 'program_dynnr',
    },
    'oo': {
        'class_name': 'class_name',
        'method_name': 'method_name',
        'class_program_name': 'class_program_name',
        'local_in_program': 'local_in_program',
        'oo_transaction_model': 'oo_transaction_model',
    },
    'variant': {
        'parent_transaction': 'var_parent_transaction_code',
        'cross_client': 'transaction_variant_cross_client',
        'transaction_variant_name': 'transaction_variant_name',
    },
}


def _build_factory_kwargs(args):
    """Builds keyword arguments for the Transaction factory method from CLI args."""

    kwargs = {
        'abap_language_version_text': args.abap_language_version,
        'update_mode': args.update_mode,
    }

    type_args = _TYPE_ARGS_MAP.get(args.type, {})
    kwargs.update(_collect_optional_args(args, type_args))

    return kwargs


class CommandGroup(sap.cli.object.CommandGroupObjectMaster):
    """Adapter converting command line parameters to sap.adt.Transaction methods
       calls.
    """

    def __init__(self):
        super().__init__('transaction')

        self.define()

    def instance(self, connection, name, args, metadata=None):
        package = None
        if hasattr(args, 'package'):
            package = args.package

        return sap.adt.Transaction(connection, name.upper(), package=package, metadata=metadata)

    def define_create(self, commands):
        """Extends the inherited create command with type-specific arguments."""

        create_cmd = super().define_create(commands)

        create_cmd.append_argument(
            '-t', '--type', required=True,
            choices=['report', 'parameter', 'dialog', 'oo', 'variant'],
            type=str, help='Transaction type')
        create_cmd.append_argument(
            '--abap-language-version', default='Standard ABAP',
            type=str, help='ABAP language version')
        create_cmd.append_argument(
            '--update-mode', default='notSet',
            choices=['notSet', 'asynchronous', 'synchronous', 'local'],
            type=str, help='Update mode')
        create_cmd.append_argument(
            '--report-name', default=None, type=str,
            help='Report name (report type)')
        create_cmd.append_argument(
            '--report-dynnr', default=None, type=str,
            help='Screen number (report type)')
        create_cmd.append_argument(
            '--report-variant-name', default=None, type=str,
            help='Variant name (report type)')
        create_cmd.append_argument(
            '--parent-transaction', default=None, type=str,
            help='Parent transaction code (parameter/variant type)')
        create_cmd.append_argument(
            '--program-name', default=None, type=str,
            help='Program name (dialog type)')
        create_cmd.append_argument(
            '--program-dynnr', default=None, type=str,
            help='Dynpro number (dialog type)')
        create_cmd.append_argument(
            '--class-name', default=None, type=str,
            help='Class name (oo type)')
        create_cmd.append_argument(
            '--method-name', default=None, type=str,
            help='Method name (oo type)')
        create_cmd.append_argument(
            '--class-program-name', default=None, type=str,
            help='Program name (oo type)')
        create_cmd.append_argument(
            '--local-in-program', action='store_true', default=False,
            help='Local class in program (oo type)')
        create_cmd.append_argument(
            '--oo-transaction-model', action='store_true', default=False,
            help='OO transaction model (oo type)')
        create_cmd.append_argument(
            '--cross-client', action='store_true', default=False,
            help='Cross-client variant (variant type)')
        create_cmd.append_argument(
            '--transaction-variant-name', default=None, type=str,
            help='Transaction variant name (variant type)')

        return create_cmd

    def create_object(self, connection, args):
        """Creates the given transaction"""

        _validate_create_args(args)

        metadata = self.build_new_metadata(connection, args)
        metadata.description = args.description

        factory_method = getattr(sap.adt.Transaction, args.type)
        factory_kwargs = _build_factory_kwargs(args)

        transaction = factory_method(
            connection, args.name.upper(),
            description=args.description,
            package=args.package.upper(),
            metadata=metadata,
            **factory_kwargs,
        )

        transaction.create(corrnr=args.corrnr)
