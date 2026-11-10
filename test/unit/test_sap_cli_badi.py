#!/usr/bin/env python3

from io import StringIO
import unittest
import json
from unittest.mock import MagicMock, patch, Mock, PropertyMock, mock_open, call

import sap.cli.badi
import sap.cli.core
from sap.rest.errors import HTTPRequestError

from mock import (
    Connection,
    Request,
    Response,
    ConsoleOutputTestCase,
    PatcherTestCase,
)

from fixtures_adt import (
    EMPTY_RESPONSE_OK,
    LOCK_RESPONSE_OK,
)

from fixtures_adt_enhancement_implementation import (
    ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4,
)

from fixtures_sap_adt_enhancement_spot import FIXTURE_ADT_ENHANCEMENT_SPOT

from infra import generate_parse_args


parse_args = generate_parse_args(sap.cli.badi.CommandGroup())

OK_ENHO_RESPONSE = Response(
    status_code=200,
    text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4,
    content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
)

BADI_LIST_TABLE = (
    'Name             | Active | Class                | Definition      | Customizing | Default | Example | Short Text \n'
    '------------------------------------------------------------------------------------------------------------------\n'
    'SAPCLI_BADI_IMPL | true   | ZCL_SAPCLI_BADI_IMPL | SAPCLI_BADI_DEF |             | false   | false   | SAPCLI badi\n'
)

OK_ENHS_RESPONSE = Response(
    status_code=200,
    text=FIXTURE_ADT_ENHANCEMENT_SPOT.replace('SSAMPLE_ENHS', 'SAPCLI_ENH_SPOT'),
    content_type='application/vnd.sap.adt.enh.enhs.v2+xml'
)


def get_argument_help(command_group, handler, argument):
    declaration = command_group.get_command_declaration(handler)
    return next(kwargs['help'] for args, kwargs in declaration.arguments if argument in args)


class TestBadiEnhImplListHelp(unittest.TestCase):

    def test_list_columns_help(self):
        self.assertEqual(
            get_argument_help(sap.cli.badi.CommandGroup, sap.cli.badi.list_badis, '--columns'),
            'Comma separated list of visible columns: name, active, implementing_class.name, '
            'badi_definition.name, customizing_lock, default, example, short_text')


class TestBadiEnhImplRequired(ConsoleOutputTestCase):

    def test_list_without_enhancement_implementation(self):
        with patch('sys.stderr', new_callable=StringIO) as fake_stderr:
            with self.assertRaises(SystemExit):
                parse_args('list')

        self.assertIn('the following arguments are required: -i/--enhancement-implementation',
                      fake_stderr.getvalue())

    def test_default_action_without_enhancement_implementation(self):
        with patch('sys.stderr', new_callable=StringIO) as fake_stderr:
            with self.assertRaises(SystemExit):
                parse_args()

        self.assertIn('the following arguments are required: -i/--enhancement-implementation',
                      fake_stderr.getvalue())


class TestBadiEnhImplList(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)

    def default_action(self, *args, **kwargs):
        return parse_args(*args, **kwargs)

    def list(self, enhimpl, *args, **kwargs):
        return parse_args('-i', enhimpl, 'list', *args, **kwargs)

    def set_active(self, enhimpl, badi, active, *args, **kwargs):
        value = 'true' if active else 'false'
        return parse_args('-i', enhimpl, 'set-active', '-b', badi, value, *args, **kwargs)

    def test_list_all_badis(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.list('SAPCLI_ENH_IMPL')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(self.console, stdout=BADI_LIST_TABLE)

    def test_list_lower_case_enhancement_implementation(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.list('sapcli_enh_impl')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(self.console, stdout=BADI_LIST_TABLE)

    def test_list_long_option_with_dash(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = parse_args('--enhancement-implementation', 'SAPCLI_ENH_IMPL', 'list')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(self.console, stdout=BADI_LIST_TABLE)

    def test_list_long_option_with_underscore(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = parse_args('--enhancement_implementation', 'SAPCLI_ENH_IMPL', 'list')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(self.console, stdout=BADI_LIST_TABLE)

    def test_default_action_all_badis(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.default_action('-i', 'SAPCLI_ENH_IMPL')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(self.console, stdout=BADI_LIST_TABLE)

    def test_list_noheadings(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.list('SAPCLI_ENH_IMPL', '--noheadings')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(
            self.console,
            stdout='SAPCLI_BADI_IMPL | true | ZCL_SAPCLI_BADI_IMPL | SAPCLI_BADI_DEF |  | false | false | SAPCLI badi\n')

    def test_list_columns(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.list('SAPCLI_ENH_IMPL', '--columns', 'name,implementing_class.name')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(
            self.console,
            stdout='Name             | Class               \n'
                   '---------------------------------------\n'
                   'SAPCLI_BADI_IMPL | ZCL_SAPCLI_BADI_IMPL\n')

    def test_list_columns_noheadings(self):
        conn = Connection([OK_ENHO_RESPONSE])

        list_cmd = self.list('SAPCLI_ENH_IMPL', '--columns', 'implementing_class.name,name', '--noheadings')
        list_cmd.execute(conn, list_cmd)

        self.assertConsoleContents(self.console, stdout='SAPCLI_BADI_IMPL | ZCL_SAPCLI_BADI_IMPL\n')

    def test_set_active_no_change(self):
        with patch('sap.cli.badi._get_enhancement_implementation') as mock_getter:
            mock_badi = MagicMock()
            type(mock_badi).is_active_implementation = PropertyMock(return_value=True)

            mock_implementation_obj = MagicMock()
            mock_implementation_obj.__getitem__.return_value = mock_badi

            mock_implementations = PropertyMock(return_value=mock_implementation_obj)

            mock_badis_obj = Mock()
            type(mock_badis_obj).implementations = mock_implementations

            mock_badis = PropertyMock(return_value=mock_badis_obj)

            mock_spec_obj = Mock()
            type(mock_spec_obj).badis = mock_badis

            mock_specific = PropertyMock(return_value=mock_spec_obj)

            mock_enho_obj = MagicMock()
            type(mock_enho_obj).specific = mock_specific

            mock_getter.return_value = mock_enho_obj

            set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True)
            set_active_cmd.execute(None, set_active_cmd)

            mock_getter.assert_called_once_with(None, set_active_cmd)

            mock_implementation_obj.__getitem__.assert_called_once_with('SAPCLI_BADI_IMPL')

        self.assertConsoleContents(self.console, stdout='''Nothing to do! The BAdI SAPCLI_BADI_IMPL\'s Active is already: true
''')


    def test_set_active_false(self):
        ok_active_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="false"', 'enho:active="true"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        conn = Connection([ok_active_enho_response, LOCK_RESPONSE_OK, OK_ENHO_RESPONSE, EMPTY_RESPONSE_OK])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', False)
        set_active_cmd.execute(conn, set_active_cmd)

        self.assertIn('enho:active="false"', conn.execs[2].body.decode('utf8'))

        self.assertConsoleContents(self.console, stdout='''Updating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_IMPL
''')

    def test_set_active_true(self):
        ok_inactive_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="true"', 'enho:active="false"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        conn = Connection([ok_inactive_enho_response, LOCK_RESPONSE_OK, OK_ENHO_RESPONSE, EMPTY_RESPONSE_OK])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True)
        set_active_cmd.execute(conn, set_active_cmd)

        self.assertIn('enho:active="true"', conn.execs[2].body.decode('utf8'))

        self.assertConsoleContents(self.console, stdout='''Updating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_IMPL
''')

    def test_set_active_invalid(self):
        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True)
        set_active_cmd.active = 'foo'

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            set_active_cmd.execute(None, set_active_cmd)

        self.assertEqual(str(caught.exception), 'BUG: unexpected value of the argument active: foo')

    def test_set_active_unknown_badi(self):
        conn = Connection([OK_ENHO_RESPONSE, LOCK_RESPONSE_OK, OK_ENHO_RESPONSE, EMPTY_RESPONSE_OK])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'UKNONWN_BADI', True)

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            set_active_cmd.execute(conn, set_active_cmd)

        self.assertEqual(str(caught.exception), 'The BAdI UKNONWN_BADI not found in the enhancement implementation SAPCLI_ENH_IMPL')

    def test_set_active_with_activation(self):
        ok_inactive_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="true"', 'enho:active="false"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        ok_active_enho_response = Response(
            status_code=200,
            text=ADT_XML_ENHANCEMENT_IMPLEMENTATION_V4.replace('enho:active="false"', 'enho:active="true"'),
            content_type='application/vnd.sap.adt.enh.enhoxhb.v4+xml'
        )

        conn = Connection([
            ok_inactive_enho_response, # GET original object
            LOCK_RESPONSE_OK,  # POST lock
            OK_ENHO_RESPONSE,  # PUT updated
            EMPTY_RESPONSE_OK, # POST unlock
            EMPTY_RESPONSE_OK, # POST activate
            ok_active_enho_response, # GET the object again
        ])

        set_active_cmd = self.set_active('SAPCLI_ENH_IMPL', 'SAPCLI_BADI_IMPL', True, '-a')
        set_active_cmd.execute(conn, set_active_cmd)

        self.assertConsoleContents(self.console, stdout='''Updating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_IMPL
Activating:
* SAPCLI_ENH_IMPL
Activation has finished
Warnings: 0
Errors: 0
''')


class TestBadiCreate(ConsoleOutputTestCase, PatcherTestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        PatcherTestCase.__init__(self)

    def tearDown(self):
        try:
            PatcherTestCase.unpatch_all(self)
        finally:
            super().tearDown()

    def setUp(self):
        super().setUp()
        ConsoleOutputTestCase.setUp(self)

        assert self.console is not None

        self.patch_console(console=self.console)

    def create(self, *args):
        return parse_args('-i', 'sapcli_enh_impl', 'create', *args)

    def test_create_without_class(self):
        with patch('sys.stderr', new_callable=StringIO) as fake_stderr:
            with self.assertRaises(SystemExit):
                self.create('-b', 'SAPCLI_BADI_NEW', '-d', 'SAPCLI_BADI_DEF')

        self.assertIn('the following arguments are required: -c/--implementing-class', fake_stderr.getvalue())

    def test_create(self):
        conn = Connection([OK_ENHO_RESPONSE, OK_ENHS_RESPONSE, LOCK_RESPONSE_OK, OK_ENHO_RESPONSE, EMPTY_RESPONSE_OK])

        create_cmd = self.create('-b', 'sapcli_badi_new', '-d', 'sample_enhs', '-c', 'zcl_sapcli_badi_new',
                                 '--corrnr', '420')
        create_cmd.execute(conn, create_cmd)

        self.assertEqual([(e.method, e.adt_uri) for e in conn.execs], [
            ('GET', '/sap/bc/adt/enhancements/enhoxhb/sapcli_enh_impl'),
            ('GET', '/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot'),
            ('POST', '/sap/bc/adt/enhancements/enhoxhb/sapcli_enh_impl'),
            ('PUT', '/sap/bc/adt/enhancements/enhoxhb/sapcli_enh_impl'),
            ('POST', '/sap/bc/adt/enhancements/enhoxhb/sapcli_enh_impl'),
        ])

        self.assertEqual(conn.execs[3].params['corrNr'], '420')
        self.assertIn('''<enho:badiImplementation enho:name="SAPCLI_BADI_NEW" enho:active="true" enho:customizingLock="">
<enho:enhancementSpot adtcore:uri="/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot" adtcore:type="ENHS/XSB" adtcore:name="SAPCLI_ENH_SPOT"/>
<enho:badiDefinition adtcore:uri="/sap/bc/adt/enhancements/enhsxsb/sapcli_enh_spot#type=enhs%2fxb;name=sample_enhs" adtcore:type="ENHS/XB" adtcore:name="SAMPLE_ENHS"/>
<enho:implementingClass adtcore:uri="/sap/bc/adt/oo/classes/zcl_sapcli_badi_new" adtcore:type="CLAS/OC" adtcore:name="ZCL_SAPCLI_BADI_NEW"/>
</enho:badiImplementation>''', conn.execs[3].body.decode('utf-8'))

        self.assertConsoleContents(self.console, stdout='''Creating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_NEW
''')

    def test_create_with_activation(self):
        conn = Connection([
            OK_ENHO_RESPONSE,   # GET the enhancement implementation
            OK_ENHS_RESPONSE,   # GET the enhancement spot
            LOCK_RESPONSE_OK,   # POST lock
            OK_ENHO_RESPONSE,   # PUT updated
            EMPTY_RESPONSE_OK,  # POST unlock
            EMPTY_RESPONSE_OK,  # POST activate
            OK_ENHO_RESPONSE,   # GET the object again
        ])

        create_cmd = self.create('-b', 'SAPCLI_BADI_NEW', '-d', 'SAMPLE_ENHS', '-c', 'ZCL_SAPCLI_BADI_NEW', '-a')
        create_cmd.execute(conn, create_cmd)

        self.assertConsoleContents(self.console, stdout='''Creating:
* SAPCLI_ENH_IMPL/SAPCLI_BADI_NEW
Activating:
* SAPCLI_ENH_IMPL
Activation has finished
Warnings: 0
Errors: 0
''')

    def test_create_existing_badi(self):
        conn = Connection([OK_ENHO_RESPONSE])

        create_cmd = self.create('-b', 'SAPCLI_BADI_IMPL', '-d', 'SAMPLE_ENHS', '-c', 'ZCL_SAPCLI_BADI_NEW')

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            create_cmd.execute(conn, create_cmd)

        self.assertEqual(str(caught.exception),
                         'The BAdI SAPCLI_BADI_IMPL already exists in the enhancement implementation SAPCLI_ENH_IMPL')
        self.assertEqual(len(conn.execs), 1)

    def test_create_unknown_badi_definition(self):
        conn = Connection([OK_ENHO_RESPONSE, OK_ENHS_RESPONSE])

        create_cmd = self.create('-b', 'SAPCLI_BADI_NEW', '-d', 'UNKNOWN_DEF', '-c', 'ZCL_SAPCLI_BADI_NEW')

        with self.assertRaises(sap.errors.SAPCliError) as caught:
            create_cmd.execute(conn, create_cmd)

        self.assertEqual(str(caught.exception),
                         'The BAdI Definition UNKNOWN_DEF not found in the enhancement spot SAPCLI_ENH_SPOT;'
                         ' available BAdI Definitions: SAMPLE_ENHS')
        self.assertEqual(len(conn.execs), 2)
