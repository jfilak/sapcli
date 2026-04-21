"""CLI mixin for API Release state management (list, set)"""

import sys

import sap.adt.apirelease
import sap.cli.core
from sap.adt.apirelease import ContractKey
from sap.cli.core import InvalidCommandLineError
from sap.errors import SAPCliError


CONTRACT_LABELS = {
    ContractKey.C0: 'Extended (Contract C0)',
    ContractKey.C1: 'Use System-Internally (Contract C1)',
    ContractKey.C2: 'Use as Remote API (Contract C2)',
    ContractKey.C3: 'Contract C3',
    ContractKey.C4: 'Contract C4',
}

YES_NO_MAP = {'yes': 'true', 'no': 'false'}


def _normalize_yes_no(value, option_name):
    """Convert a user-provided Yes/No string to 'true'/'false'.

    Raises SAPCliError if the value is not 'yes' or 'no' (case-insensitive).
    """

    lowered = value.lower()
    if lowered not in YES_NO_MAP:
        raise SAPCliError(f'Invalid value for {option_name}: "{value}" (expected Yes or No)')
    return YES_NO_MAP[lowered]


def _parse_contract_key(value):
    """Parse a string contract level into a ContractKey enum member.

    Raises InvalidCommandLineError for unknown values.
    """

    try:
        return ContractKey(value.lower())
    except ValueError as ex:
        raise InvalidCommandLineError(f'Unknown contract level: {value}') from ex


def _format_yes_no(value):
    """Convert 'true'/'false' string to 'Yes'/'No'"""

    if value is None:
        return ''
    return 'Yes' if value.lower() == 'true' else 'No'


def _is_not_set(contract):
    """Check if a contract is effectively not set (None, no contract attr, or NOT_RELEASED)"""

    if contract is None or contract.contract is None:
        return True

    if contract.status and contract.status.state == 'NOT_RELEASED':
        return True

    return False


def _format_enabled_disabled(value):
    """Convert 'true'/'false' string to 'enabled'/'disabled'"""

    if value is None:
        return ''
    return 'enabled' if value.lower() == 'true' else 'disabled'


def _print_contract(console, label, contract):
    """Print a single contract's details"""

    if _is_not_set(contract):
        console.printout(f'{label}: not set')
        return

    state = contract.status.state_description if contract.status and contract.status.state_description else ''
    if not state and contract.status:
        state = contract.status.state or ''

    comment = contract.comment if contract.comment is not None else ''
    cloud_dev = _format_yes_no(contract.use_in_sap_cloud_platform)
    key_user = _format_yes_no(contract.use_in_key_user_apps)
    auth_values = _format_enabled_disabled(contract.create_auth_values)

    console.printout(f'{label}:')
    console.printout(f'  Release State: {state}')
    console.printout(f'  Local Comment: {comment}')
    console.printout(f'  Use in Cloud Development: {cloud_dev}')
    console.printout(f'  Use in Key User Apps: {key_user}')
    console.printout(f'  Authorization Default Value: {auth_values}')


def apistate_list(command_group, connection, args):
    """List API release states for all contracts of the given object"""

    obj = command_group.instance(connection, args.name, args)
    api_release = sap.adt.apirelease.get_api_release(connection, obj.full_adt_uri)

    console = args.console_factory()

    for key in ContractKey:
        _print_contract(console, CONTRACT_LABELS[key], api_release.get_contract(key))

    return 0


def _validate_set_args(args) -> ContractKey:
    """Validate apistate set arguments, return ContractKey"""

    contract_key = _parse_contract_key(args.contract)

    if not any([args.state, args.comment is not None, args.cloud_dev, args.key_user_apps]):
        raise InvalidCommandLineError(
            'at least one of --state, --comment, --cloud-dev, --key-user-apps is required'
        )

    return contract_key


def _check_behaviour(api_release, contract_key, args):
    """Check behaviour flags and raise on unsupported or read-only attributes"""

    if api_release.behaviour is None:
        raise SAPCliError('Object does not support API release management')

    contract_behaviour = api_release.get_contract_behaviour(contract_key)
    if contract_behaviour is None:
        raise SAPCliError(
            f'Contract level {contract_key.value.upper()} is not supported for this object type'
        )

    if args.key_user_apps and contract_behaviour.use_in_key_user_apps_read_only == 'true':
        raise SAPCliError('Use in Key User Apps is read-only for this contract')

    if args.cloud_dev and contract_behaviour.use_in_sap_cloud_platform_read_only == 'true':
        raise SAPCliError('Use in Cloud Development is read-only for this contract')


def _apply_args_to_contract(target, args):
    """Apply user-provided options to the target contract"""

    if args.state:
        if target.status is None:
            target.status = sap.adt.apirelease.ContractStatus()
        target.status.state = args.state.upper()
        target.status.state_description = None

    if args.comment is not None:
        target.comment = args.comment

    if args.cloud_dev:
        target.use_in_sap_cloud_platform = _normalize_yes_no(args.cloud_dev, '--cloud-dev')

    if args.key_user_apps:
        target.use_in_key_user_apps = _normalize_yes_no(args.key_user_apps, '--key-user-apps')


def _build_payload(api_release, contract_key, args):
    """Build the ApiRelease payload for validate/update"""

    target = api_release.copy_contract(contract_key)
    if target.status is None:
        target.status = sap.adt.apirelease.ContractStatus()
    target.status.state_description = None

    _apply_args_to_contract(target, args)

    payload = sap.adt.apirelease.ApiRelease()
    setattr(payload, contract_key.attr_name, target)

    if api_release.api_catalog_data is not None:
        payload.api_catalog_data = api_release.api_catalog_data

    return payload


def _handle_validation(console, validation, force):
    """Process validation messages. Returns 0 to proceed, 1 to abort."""

    if not validation.validation_messages:
        return 0

    messages = list(validation.validation_messages)
    errors = [m for m in messages if m.typ == 'E']
    warnings = [m for m in messages if m.typ == 'W']

    if errors:
        for msg in errors:
            console.printerr(f'Error: {msg.text}')
        return 1

    if warnings:
        for msg in warnings:
            console.printerr(f'Warning: {msg.text}')

        if not force:
            if not sys.stdin.isatty():
                console.printerr('Warnings found and --force not set. Aborting.')
                return 1

            try:
                answer = input('Continue despite warnings? [y/N] ')
            except EOFError:
                answer = ''

            if answer.lower() != 'y':
                return 1

    return 0


def apistate_set(command_group, connection, args):
    """Set API release state for a contract of the given object"""

    contract_key = _validate_set_args(args)

    obj = command_group.instance(connection, args.name, args)
    api_release = sap.adt.apirelease.get_api_release(connection, obj.full_adt_uri)

    _check_behaviour(api_release, contract_key, args)

    payload = _build_payload(api_release, contract_key, args)

    console = args.console_factory()
    validation = sap.adt.apirelease.validate_api_release(
        connection, obj.full_adt_uri, contract_key, payload
    )

    result = _handle_validation(console, validation, args.force)
    if result != 0:
        return result

    updated = sap.adt.apirelease.set_api_release(
        connection, obj.full_adt_uri, contract_key, payload, corrnr=args.corrnr
    )

    _print_contract(console, CONTRACT_LABELS[contract_key], updated.get_contract(contract_key))

    return 0


def enhance_command_group(command_group):
    """Enhance a CommandGroupObjectMaster with apistate subcommands.

    This wraps install_parser to add an 'apistate' subparser group
    with 'list' and 'set' commands.
    """

    original_install_parser = command_group.install_parser

    def enhanced_install_parser(arg_parser):
        command_args = original_install_parser(arg_parser)

        apistate_parser = command_args.add_parser('apistate', help='API Release state management')
        apistate_subparsers = apistate_parser.add_subparsers()

        # list command
        list_parser = apistate_subparsers.add_parser('list', help='List API release states')
        list_parser.add_argument('name')
        list_parser.set_defaults(
            execute=lambda conn, args: apistate_list(command_group, conn, args),
            console_factory=sap.cli.core.get_console
        )

        # set command
        set_parser = apistate_subparsers.add_parser('set', help='Set API release state')
        set_parser.add_argument('contract', help='Contract level: c0, c1, c2, c3, c4')
        set_parser.add_argument('name', help='Object name')
        set_parser.add_argument('--state', default=None, help='Release state value')
        set_parser.add_argument('--comment', default=None, help='Free-text comment')
        set_parser.add_argument('--cloud-dev', default=None, dest='cloud_dev',
                                help='Use in Cloud Development: Yes or No')
        set_parser.add_argument('--key-user-apps', default=None, dest='key_user_apps',
                                help='Use in Key User Apps: Yes or No')
        set_parser.add_argument('--corrnr', default=None, help='Transport request number')
        set_parser.add_argument('--force', action='store_true', default=False,
                                help='Skip confirmation on validation warnings')
        set_parser.set_defaults(
            execute=lambda conn, args: apistate_set(command_group, conn, args),
            console_factory=sap.cli.core.get_console
        )

        return command_args

    command_group.install_parser = enhanced_install_parser
