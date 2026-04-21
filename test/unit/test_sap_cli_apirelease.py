#!/usr/bin/env python3

"""Tests for sap.cli.apirelease"""

import unittest
from unittest.mock import Mock, patch
from argparse import ArgumentParser

import sap.cli.apirelease
import sap.cli.object
import sap.adt
import sap.adt.apirelease
import sap.errors
from sap.adt.marshalling import Marshal
from sap.adt.apirelease import ContractKey

from mock import Connection, Response, BufferConsole
from fixtures_adt_apirelease import (
    API_RELEASE_RESPONSE_XML,
    VALIDATION_RESPONSE_INFO_XML,
    VALIDATION_RESPONSE_ERROR_XML,
    VALIDATION_RESPONSE_WARNING_XML,
    SET_API_RELEASE_RESPONSE_XML,
)

RELEASE_CT = 'application/vnd.sap.adt.apirelease.v11+xml'
VALIDATION_CT = 'application/vnd.sap.adt.apireleasecontractvalidation.v2+xml'

# Response XML with no contracts set (only c1 behaviour)
API_RELEASE_NO_CONTRACTS_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:behaviour ars:create="true" ars:commentEnabled="true">' \
    '<ars:c1Release ars:create="true" ars:read="true" ars:update="true" ars:delete="true"' \
    ' ars:useInKeyUserAppsDefault="false" ars:useInKeyUserAppsReadOnly="false"' \
    ' ars:useInSAPCloudPlatformDefault="false" ars:useInSAPCloudPlatformReadOnly="false"' \
    ' ars:authValuesEnabled="true"/>' \
    '</ars:behaviour>' \
    '<ars:apiCatalogData ars:isAnyAssignmentPossible="false" ars:isAnyContractReleased="false"/>' \
    '</ars:apiRelease>'

# Response with key_user_apps and cloud_dev read-only for c0
API_RELEASE_READONLY_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '<ars:behaviour ars:create="true" ars:commentEnabled="true">' \
    '<ars:c0Release ars:create="true" ars:read="false" ars:update="true" ars:delete="false"' \
    ' ars:useInKeyUserAppsDefault="false" ars:useInKeyUserAppsReadOnly="true"' \
    ' ars:useInSAPCloudPlatformDefault="true" ars:useInSAPCloudPlatformReadOnly="true"' \
    ' ars:authValuesEnabled="false"/>' \
    '</ars:behaviour>' \
    '<ars:c0Release xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' ars:contract="C0" ars:useInKeyUserApps="false" ars:useInSAPCloudPlatform="false"' \
    ' ars:comment="" ars:featureToggle="" ars:createAuthValues="false">' \
    '<ars:status ars:state="NOT_RELEASED" ars:stateDescription="Not Released"/>' \
    '</ars:c0Release>' \
    '<ars:apiCatalogData ars:isAnyAssignmentPossible="false" ars:isAnyContractReleased="false"/>' \
    '</ars:apiRelease>'

NO_BEHAVIOUR_XML = '<?xml version="1.0" encoding="UTF-8"?>' \
    '<ars:apiRelease xmlns:ars="http://www.sap.com/adt/ars">' \
    '<ars:releasableObject xmlns:adtcore="http://www.sap.com/adt/core"' \
    ' adtcore:uri="/sap/bc/adt/ddic/ddl/sources/i_statisticalkeyfigurecat"' \
    ' adtcore:type="DDLS/DF"' \
    ' adtcore:name="I_STATISTICALKEYFIGURECAT"/>' \
    '</ars:apiRelease>'


def _resp(xml, content_type=RELEASE_CT):
    return Response(text=xml, status_code=200, content_type=content_type)


def _val_resp(xml):
    return Response(text=xml, status_code=200, content_type=VALIDATION_CT)


def _make_group():
    """Create a fresh command group with apistate enhanced"""

    class TestCommandGroup(sap.cli.object.CommandGroupObjectMaster):
        def __init__(self):
            super().__init__('ddl', description='CDS views')
            self.define()
            sap.cli.apirelease.enhance_command_group(self)

        def instance(self, connection, name, args, metadata=None):
            return sap.adt.DataDefinition(connection, name.upper(), package=None, metadata=metadata)

    return TestCommandGroup()


def _parse(group, *argv):
    parser = ArgumentParser()
    group.install_parser(parser)
    return parser.parse_args(argv)


class TestApiStateList(unittest.TestCase):

    def test_list_with_contracts(self):
        conn = Connection([_resp(API_RELEASE_RESPONSE_XML)])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'list', 'I_STATISTICALKEYFIGURECAT')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 0)
        out = console.capout
        # C0 is NOT_RELEASED -> "not set"
        self.assertIn('Extended (Contract C0): not set', out)
        # C1 is RELEASED -> details shown
        self.assertIn('Use System-Internally (Contract C1):', out)
        self.assertIn('  Release State: Released', out)
        self.assertIn('  Use in Key User Apps: Yes', out)
        self.assertIn('  Use in Cloud Development: No', out)
        self.assertIn('  Authorization Default Value: disabled', out)
        self.assertIn('Contract C3: not set', out)
        self.assertIn('Contract C4: not set', out)

    def test_list_no_contracts(self):
        conn = Connection([_resp(API_RELEASE_NO_CONTRACTS_XML)])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'list', 'I_STATISTICALKEYFIGURECAT')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 0)
        out = console.capout
        self.assertIn('Extended (Contract C0): not set', out)
        self.assertIn('Use System-Internally (Contract C1): not set', out)
        self.assertIn('Use as Remote API (Contract C2): not set', out)
        self.assertIn('Contract C3: not set', out)
        self.assertIn('Contract C4: not set', out)


class TestApiStateSet(unittest.TestCase):

    def test_set_success_with_info(self):
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_INFO_XML),
            _resp(SET_API_RELEASE_RESPONSE_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released', '--corrnr', 'C50K000061')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 0)
        self.assertIn('Use System-Internally (Contract C1):', console.capout)
        self.assertIn('  Release State: Released', console.capout)
        self.assertEqual(len(conn.execs), 3)
        self.assertEqual(conn.execs[0].method, 'GET')
        self.assertEqual(conn.execs[1].method, 'POST')
        self.assertEqual(conn.execs[2].method, 'PUT')

    def test_set_validation_error_aborts(self):
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_ERROR_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 1)
        self.assertIn('Error: Contract C1 cannot be released.', console.caperr)
        self.assertEqual(len(conn.execs), 2)

    def test_set_warning_with_force(self):
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_WARNING_XML),
            _resp(SET_API_RELEASE_RESPONSE_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released', '--force')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 0)
        self.assertIn('Warning: Object has open changes.', console.caperr)
        self.assertEqual(len(conn.execs), 3)

    @patch('sys.stdin')
    def test_set_warning_no_tty_no_force_aborts(self, mock_stdin):
        mock_stdin.isatty.return_value = False
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_WARNING_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 1)
        self.assertIn('Warnings found and --force not set. Aborting.', console.caperr)
        self.assertEqual(len(conn.execs), 2)

    @patch('builtins.input', return_value='y')
    @patch('sys.stdin')
    def test_set_warning_tty_user_confirms(self, mock_stdin, mock_input):
        mock_stdin.isatty.return_value = True
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_WARNING_XML),
            _resp(SET_API_RELEASE_RESPONSE_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 0)
        self.assertEqual(len(conn.execs), 3)

    @patch('builtins.input', return_value='n')
    @patch('sys.stdin')
    def test_set_warning_tty_user_declines(self, mock_stdin, mock_input):
        mock_stdin.isatty.return_value = True
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_WARNING_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 1)
        self.assertEqual(len(conn.execs), 2)

    @patch('builtins.input', side_effect=EOFError)
    @patch('sys.stdin')
    def test_set_warning_tty_eoferror(self, mock_stdin, mock_input):
        mock_stdin.isatty.return_value = True
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_WARNING_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 1)
        self.assertEqual(len(conn.execs), 2)

    def test_set_unknown_contract(self):
        group = _make_group()
        args = _parse(group, 'apistate', 'set', 'c9', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=BufferConsole())

        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as cm:
            args.execute(Mock(), args)
        self.assertIn('Unknown contract level: c9', str(cm.exception))

    def test_set_no_flags_error(self):
        group = _make_group()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT')
        args.console_factory = Mock(return_value=BufferConsole())

        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as cm:
            args.execute(Mock(), args)
        self.assertIn('at least one of --state, --comment, --cloud-dev, --key-user-apps is required',
                       str(cm.exception))

    def test_set_contract_not_supported(self):
        conn = Connection([_resp(API_RELEASE_NO_CONTRACTS_XML)])
        group = _make_group()
        args = _parse(group, 'apistate', 'set', 'c0', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=BufferConsole())

        with self.assertRaises(sap.errors.SAPCliError) as cm:
            args.execute(conn, args)
        self.assertIn('not supported', str(cm.exception))

    def test_set_key_user_apps_read_only(self):
        conn = Connection([_resp(API_RELEASE_READONLY_XML)])
        group = _make_group()
        args = _parse(group, 'apistate', 'set', 'c0', 'I_STATISTICALKEYFIGURECAT',
                       '--key-user-apps', 'Yes')
        args.console_factory = Mock(return_value=BufferConsole())

        with self.assertRaises(sap.errors.SAPCliError) as cm:
            args.execute(conn, args)
        self.assertIn('Key User Apps is read-only', str(cm.exception))

    def test_set_cloud_dev_read_only(self):
        conn = Connection([_resp(API_RELEASE_READONLY_XML)])
        group = _make_group()
        args = _parse(group, 'apistate', 'set', 'c0', 'I_STATISTICALKEYFIGURECAT',
                       '--cloud-dev', 'Yes')
        args.console_factory = Mock(return_value=BufferConsole())

        with self.assertRaises(sap.errors.SAPCliError) as cm:
            args.execute(conn, args)
        self.assertIn('Cloud Development is read-only', str(cm.exception))

    def test_set_new_contract(self):
        conn = Connection([
            _resp(API_RELEASE_NO_CONTRACTS_XML),
            _val_resp(VALIDATION_RESPONSE_INFO_XML),
            _resp(SET_API_RELEASE_RESPONSE_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released', '--cloud-dev', 'No', '--key-user-apps', 'Yes')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 0)
        self.assertEqual(len(conn.execs), 3)

    def test_set_with_comment_only(self):
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_INFO_XML),
            _resp(SET_API_RELEASE_RESPONSE_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--comment', 'Some comment')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)
        self.assertEqual(result, 0)

    def test_set_with_empty_comment(self):
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_INFO_XML),
            _resp(SET_API_RELEASE_RESPONSE_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--comment', '')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)
        self.assertEqual(result, 0)

    def test_set_without_corrnr(self):
        conn = Connection([
            _resp(API_RELEASE_RESPONSE_XML),
            _val_resp(VALIDATION_RESPONSE_INFO_XML),
            _resp(SET_API_RELEASE_RESPONSE_XML),
        ])
        group = _make_group()
        console = BufferConsole()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=console)

        result = args.execute(conn, args)

        self.assertEqual(result, 0)
        self.assertIsNone(conn.execs[2].params)

    def test_set_no_behaviour(self):
        conn = Connection([_resp(NO_BEHAVIOUR_XML)])
        group = _make_group()
        args = _parse(group, 'apistate', 'set', 'c1', 'I_STATISTICALKEYFIGURECAT',
                       '--state', 'Released')
        args.console_factory = Mock(return_value=BufferConsole())

        with self.assertRaises(sap.errors.SAPCliError) as cm:
            args.execute(conn, args)
        self.assertIn('does not support API release management', str(cm.exception))


class TestEnhanceCommandGroup(unittest.TestCase):

    def test_enhance_adds_apistate_subcommand(self):
        group = _make_group()
        parser = ArgumentParser()
        group.install_parser(parser)

        args = parser.parse_args(['apistate', 'list', 'MYOBJECT'])
        self.assertEqual(args.name, 'MYOBJECT')
        self.assertTrue(hasattr(args, 'execute'))

        args = parser.parse_args(['apistate', 'set', 'c1', 'MYOBJECT', '--state', 'Released'])
        self.assertEqual(args.name, 'MYOBJECT')
        self.assertEqual(args.contract, 'c1')
        self.assertEqual(args.state, 'Released')


class TestFormatHelpers(unittest.TestCase):

    def test_format_yes_no_true(self):
        self.assertEqual(sap.cli.apirelease._format_yes_no('true'), 'Yes')

    def test_format_yes_no_false(self):
        self.assertEqual(sap.cli.apirelease._format_yes_no('false'), 'No')

    def test_format_yes_no_none(self):
        self.assertEqual(sap.cli.apirelease._format_yes_no(None), '')

    def test_format_yes_no_case_insensitive(self):
        self.assertEqual(sap.cli.apirelease._format_yes_no('TRUE'), 'Yes')
        self.assertEqual(sap.cli.apirelease._format_yes_no('False'), 'No')

    def test_format_enabled_disabled_true(self):
        self.assertEqual(sap.cli.apirelease._format_enabled_disabled('true'), 'enabled')

    def test_format_enabled_disabled_false(self):
        self.assertEqual(sap.cli.apirelease._format_enabled_disabled('false'), 'disabled')

    def test_format_enabled_disabled_none(self):
        self.assertEqual(sap.cli.apirelease._format_enabled_disabled(None), '')

    def test_format_enabled_disabled_case_insensitive(self):
        self.assertEqual(sap.cli.apirelease._format_enabled_disabled('TRUE'), 'enabled')
        self.assertEqual(sap.cli.apirelease._format_enabled_disabled('False'), 'disabled')


class TestPrintContract(unittest.TestCase):

    def test_print_contract_none(self):
        console = BufferConsole()
        sap.cli.apirelease._print_contract(console, 'Test Label', None)
        self.assertEqual(console.capout, 'Test Label: not set\n')

    def test_print_contract_no_contract_attr(self):
        contract = sap.adt.apirelease.Contract()
        console = BufferConsole()
        sap.cli.apirelease._print_contract(console, 'Test Label', contract)
        self.assertEqual(console.capout, 'Test Label: not set\n')

    def test_print_contract_not_released(self):
        """NOT_RELEASED state shows as not set"""
        contract = sap.adt.apirelease.Contract()
        contract.contract = 'C0'
        contract.status = sap.adt.apirelease.ContractStatus()
        contract.status.state = 'NOT_RELEASED'
        contract.status.state_description = 'Not Released'

        console = BufferConsole()
        sap.cli.apirelease._print_contract(console, 'My Label', contract)
        self.assertEqual(console.capout, 'My Label: not set\n')

    def test_print_contract_with_state_only(self):
        """state_description is None but state is set"""
        contract = sap.adt.apirelease.Contract()
        contract.contract = 'C1'
        contract.status = sap.adt.apirelease.ContractStatus()
        contract.status.state = 'RELEASED'
        contract.use_in_key_user_apps = 'true'
        contract.use_in_sap_cloud_platform = 'false'
        contract.comment = 'my comment'
        contract.create_auth_values = 'true'

        console = BufferConsole()
        sap.cli.apirelease._print_contract(console, 'My Label', contract)

        self.assertIn('My Label:', console.capout)
        self.assertIn('  Release State: RELEASED', console.capout)
        self.assertIn('  Local Comment: my comment', console.capout)
        self.assertIn('  Use in Cloud Development: No', console.capout)
        self.assertIn('  Use in Key User Apps: Yes', console.capout)
        self.assertIn('  Authorization Default Value: enabled', console.capout)

    def test_print_contract_no_status(self):
        """status is None"""
        contract = sap.adt.apirelease.Contract()
        contract.contract = 'C1'

        console = BufferConsole()
        sap.cli.apirelease._print_contract(console, 'My Label', contract)

        self.assertIn('  Release State: ', console.capout)


class TestHelperFunctions(unittest.TestCase):

    def test_apply_args_state_with_no_existing_status(self):
        """Cover line 142: target.status is None when applying state"""
        target = sap.adt.apirelease.Contract()
        target.contract = 'C1'
        # status is None - no existing status
        args = Mock(state='Released', comment=None, cloud_dev=None, key_user_apps=None)
        sap.cli.apirelease._apply_args_to_contract(target, args)
        self.assertEqual(target.status.state, 'RELEASED')

    def test_handle_validation_no_messages(self):
        """Cover line 176: no validation messages"""
        console = BufferConsole()
        validation = Mock()
        validation.validation_messages = None
        result = sap.cli.apirelease._handle_validation(console, validation, False)
        self.assertEqual(result, 0)

    def test_parse_contract_key_valid(self):
        from sap.adt.apirelease import ContractKey
        self.assertEqual(sap.cli.apirelease._parse_contract_key('c1'), ContractKey.C1)
        self.assertEqual(sap.cli.apirelease._parse_contract_key('C1'), ContractKey.C1)

    def test_parse_contract_key_invalid(self):
        with self.assertRaises(sap.cli.core.InvalidCommandLineError) as cm:
            sap.cli.apirelease._parse_contract_key('c9')
        self.assertIn('Unknown contract level: c9', str(cm.exception))

    def test_normalize_yes_no_valid(self):
        self.assertEqual(sap.cli.apirelease._normalize_yes_no('Yes', '--cloud-dev'), 'true')
        self.assertEqual(sap.cli.apirelease._normalize_yes_no('no', '--cloud-dev'), 'false')
        self.assertEqual(sap.cli.apirelease._normalize_yes_no('YES', '--key-user-apps'), 'true')

    def test_normalize_yes_no_invalid(self):
        from sap.errors import SAPCliError
        with self.assertRaises(SAPCliError) as cm:
            sap.cli.apirelease._normalize_yes_no('maybe', '--cloud-dev')
        self.assertIn('Invalid value for --cloud-dev: "maybe"', str(cm.exception))

    def test_apply_args_invalid_cloud_dev(self):
        from sap.errors import SAPCliError
        target = sap.adt.apirelease.Contract()
        target.contract = 'C1'
        args = Mock(state=None, comment=None, cloud_dev='invalid', key_user_apps=None)
        with self.assertRaises(SAPCliError):
            sap.cli.apirelease._apply_args_to_contract(target, args)

    def test_build_payload_existing_contract_no_status(self):
        """_build_payload must not crash when copy_contract returns status=None"""
        api_release = sap.adt.apirelease.ApiRelease()
        Marshal.deserialize(API_RELEASE_RESPONSE_XML, api_release)
        # Force status to None on the existing contract
        api_release.c1_release.status = None

        args = Mock(state='Released', comment=None, cloud_dev=None, key_user_apps=None)
        payload = sap.cli.apirelease._build_payload(api_release, ContractKey.C1, args)

        contract = payload.get_contract(ContractKey.C1)
        self.assertIsNotNone(contract.status)
        self.assertEqual(contract.status.state, 'RELEASED')
        self.assertIsNone(contract.status.state_description)


if __name__ == '__main__':
    unittest.main()
